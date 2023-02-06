Porting of:

[Hinsen, Konrad; Kneller, Gerald R., "A multiscale Bayesian inference approach to analyzing subdiffusion in particle trajectories"](https://zenodo.org/record/162171#.Y90FvNLMJkg)

from an ActivePaper to a Seamless workflow.

Author: Sjoerd de Vries, except for the code/ subdirectory.

Copyright: 2023, CNRS, except for the code/ subdirectory.

License: MIT license, except for the code/ subdirectory.

To the code/ subdirectory, the original license of the ActivePapers applies. This license is Creative Commons Attribution 4.0 International.
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

Note that this repo contains a tag "initial" where code-ORIGINAL/ was copied to code/ . Note that all subsequent commits modify this code in order to port it to Seamless. Therefore, you can always do `git diff initial [files]` in order to see the code modification.

## Initial population of the Seamless database

This requires Seamless to be installed in the default manner, with the `seamless` conda environment activated (`conda activate seamless`)

Run `seamless-populate-db.sh` . This will destroy the current Seamless database dir (if any), create a new one, and populate it with the contents of `data/`. Hard links are used, so no extra disk space will be used.