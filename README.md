Porting of:

[Hinsen, Konrad; Kneller, Gerald R., "A multiscale Bayesian inference approach to analyzing subdiffusion in particle trajectories"](https://zenodo.org/record/162171#.Y90FvNLMJkg)

from an ActivePaper to a Seamless workflow.

Instructions:

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
