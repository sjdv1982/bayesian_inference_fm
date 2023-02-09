Porting of:

[Hinsen, Konrad; Kneller, Gerald R., "A multiscale Bayesian inference approach to analyzing subdiffusion in particle trajectories"](https://zenodo.org/record/162171#.Y90FvNLMJkg)

from an ActivePaper to a Seamless workflow.

**Author**: Sjoerd de Vries, except for the `code/` subdirectory.

**Copyright**: 2023, CNRS, except for the `code/` subdirectory.

**License**: MIT license, except for the `code/` subdirectory.

The `code/` subdirectory contains the original code from the ActivePapers with (generally light) modifications. The original license of the ActivePapers applies. This license is Creative Commons Attribution 4.0 International.

See the ActivePapers for more information:

- https://zenodo.org/record/162171
- https://zenodo.org/record/61742
- https://zenodo.org/record/61743

# Instructions

## ActivePapers download and extraction

- Create ActivePapers environment with:
`mamba env create --file active-papers.yaml`

- Download and extract Bayesian Inference ActivePaper:

```bash
conda activate active-papers
python3 ap-download-and-extract.py
```

This will download about 1 GB of data. Download is skipped if the corresponding .ap file already exists. You may download these yourself from Zenodo.

The script will generate the following directories:

- `data/`: containing the ActivePaper datasets in .npy format
- `documentation-ORIGINAL/`: the original ActivePaper documentation
- `code-ORIGINAL/`: the original ActivePaper code (calclets and modules)

Note that this Git repo contains a tag "initial" where code-ORIGINAL/ was copied to code/ . Subsequent Git commits modify this code in order to port it to Seamless. Therefore, you can do `git diff initial [files]` in order to see the code modification.

## Initial population of the Seamless database

This requires Seamless to be installed in the default manner, with the `seamless` conda environment activated (`conda activate seamless`)

Run `./seamless-populate-db.sh` . This will destroy the current Seamless database dir (if any), create a new one, and populate it with the contents of `data/`. Hard links are used, so no extra disk space will be used.

## Optional (recommended for a first run): import the database archive

The database archive contains all workflow transformations and their results. 
If you extract this archive, the workflow will retrieve all results from cache and not recompute anything.

NOTE: this should be done while the Seamless database is not running. To stop the database, do:

```bash
docker stop seamless-database-container
docker rm seamless-database-container
```

Then, you can extract the archive as follows:

`tar xvzf seamless-db.tgz`

## Build the Seamless workflow

Seamless workflows can be modified interactively and stored as data.
The build/modification code does not need to be stored.
However, for ease of demonstration, the workflow is here being built from a script instead of simply loaded from a .seamless file.

This is done as:

```bash

conda activate seamless

seamless-database seamless-db  # start the Seamless database

seamless-ipython -i build-seamless-workflow.py
#or: seamless-bash, and then run: ipython -i build-seamless-workflow.py
```

NOTE: the script to build the workflow is not necessarily reproducible. However, the workflow itself(`bayesian_inference_fbm.seamless`) is strongly reproducible, since it contains the checksums of all code and data.

In the current script, the workflow is being run while it is being built. The workflow computations are significant, taking ~XXX hours on all cores of a laptop. Note that all results are saved into the Seamless database. Therefore, the script can be interrupted and re-launched at will, and the computations that have been done will not be repeated. If all computations have already been done (or the database archive has been imported in the previous step), the script will complete within (tens of) seconds.

At the end of the script, the IPython shell will start where the workflow can be interactively modified. The workflow remains running in the background, with its file mounts in full effect. This means that `parameters.yaml` and any file in the `code/` subdirectory can be modified, and all affected computations will be re-executed as soon as the file is saved. Remove the '-i' flag from ipython (or run with `seamless-run python`) if you wish to run the script strictly in batch mode.

In principle, instead of running the workflow as it is being built and then saving the graph, the workflow could also be saved as a graph of computations-to-run. (Seamless does not make any fundamental difference, it is just that the checksums of the result cells would be missing.) Commenting out the designated `ctx.compute(...)` expressions will achieve this. This is not done by default, because as of Seamless 0.10, meta-info regarding CPU core usage is not being taken into account. In other words, loading an unfinished graph will instantly run all computations in parallel (since there are few internal dependencies in this workflow), which will flood a local computer unless Seamless job delegation has been set up.

This applies to interactive modifications in `parameters.yaml`. Seamless will re-launch 
all effected dependencies in parallel. Therefore, be very careful what you modify! Alternatively, you can force Seamless to execute only one transformer at a time by setting `seamless.set_ncores(1)` at the top of the script. This may no longer be necessary in future  Seamless versions.

## Optional: build the database archive from the database contents

This is if you want to re-distribute the results of a modified workflow.

```bash
docker stop seamless-database-container
docker rm seamless-database-container
./create-db-archive.sh data-checksums.list seamless-db.tgz
```

## Optional: re-load the graph for further modification

The Seamless workflow is self-contained in `bayesian_inference_fbm.seamless`. With the checksum buffers (and computation results) provided by the database, the workflow can be re-loaded as follows:

```bash
## If necessary:
# conda activate seamless
# seamless-database seamless-db

seamless-serve-graph-interactive bayesian_inference_fbm.seamless \
      --database --mounts \
      --ncores 1
```

As before, you can modify the graph interactively, either from IPython, or from the mounted files. all dependencies are launched in parallel.

You can force Seamless to execute only one transformer at a time by specifying `--ncores 1`. This may no longer be necessary in future Seamless versions.

### Adding a status visualization graph

```bash
seamless-serve-graph-interactive bayesian_inference_fbm.seamless --database --mounts \
      --status-graph /home/jovyan/software/seamless/graphs/status-visualization.seamless \
      --add-zip /home/jovyan/software/seamless/graphs/status-visualization.zip \
      --ncores 1
```

In that case, open http://localhost:5813/status/index.html