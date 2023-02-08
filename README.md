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

This will generate the following directories:

- data: containing the ActivePaper datasets in .npy format
- documentation-ORIGINAL: the original ActivePaper documentation
- code-ORIGINAL: the original ActivePaper code (calclets and modules)

Note that this Git repo contains a tag "initial" where code-ORIGINAL/ was copied to code/ . Subsequent Git commits modify this code in order to port it to Seamless. Therefore, you can do `git diff initial [files]` in order to see the code modification.

## Initial population of the Seamless database

This requires Seamless to be installed in the default manner, with the `seamless` conda environment activated (`conda activate seamless`)

Run `seamless-populate-db.sh` . This will destroy the current Seamless database dir (if any), create a new one, and populate it with the contents of `data/`. Hard links are used, so no extra disk space will be used.

## Optional: import the database archive

The database archive contains all transformations and their results...
TODO

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

NOTE: the script to build the workflow is not necessarily reproducible. However, the workflow itself(`bayesian_inference.seamless`) is strongly reproducible, since it contains the checksums of all code and data.

In the current script, the workflow is being run while it is being built. The workflow computations are significant, taking ~XXX hours on all cores of a laptop. Note that all results are saved into the Seamless database. Therefore, the script can be interrupted and re-launched at will, and the computations that have been done will not be repeated. If all computations have already been done (or the database archive has been imported in the previous step), the script will complete within seconds.

At the end of the script, the IPython shell will start where the workflow can be interactively modified. The workflow remains running in the background, with its file mounts in full effect. This means that `parameters.yaml` and any file in the `code/` subdirectory can be modified, and all affected computations will be re-executed as soon as the file is saved. Remove the '-i' flag from ipython (or run with `seamless-run python`) if you wish to run the script strictly in batch mode.

In principle, instead of running the workflow as it is being built and then saving the graph, the workflow could also be saved as a graph of computations-to-run. (Seamless does not make any fundamental difference, it is just that the checksums of the result cells would be missing.) Commenting out the designated `ctx.compute(...)` expressions will achieve this. This is not done by default, because as of Seamless 0.10, meta-info regarding CPU core usage is not being taken into account. In other words, loading an unfinished graph will instantly run all computations in parallel (since there are few internal dependencies in this workflow), which will flood a local computer unless Seamless job delegation has been set up.

## Optional: build the database archive

TODO

## Optional: deployment

TODO
seamless-serve-graph --database
In a new directory, seamless-new-project => copy the .seamless file into the graphs/ directory => seamless-add-vault vault/ => modify load-project.py to use a database instead of a vault. Uncomment in load_database, comment out ctx.load_vault, ctx.save_vault.
Gain status graph, web interface.