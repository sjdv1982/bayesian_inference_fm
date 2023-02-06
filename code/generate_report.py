from activepapers.contents import open_documentation, code
from literate_python import lpy2md

with open_documentation('report.md', 'w') as f:
    f.write('''
---
title:
   Supplementary material for "A multiscale Bayesian inference approach
   to analyzing subdiffusion in particle trajectories"
author: K. Hinsen and G.R. Kneller
note: To generate a PDF file, use "pandoc -N --variable=urlcolor:blue -o report.pdf report.md"
---

''')

    f.write('# Parameter choices\n')
    f.write('\n')
    f.write(lpy2md(code['set_parameters']))
    f.write('\n')

    f.write('# Preliminaries\n')
    f.write('\n')
    f.write(lpy2md(code['python-packages/reproducible_random_numbers']))
    f.write('\n')
    f.write(lpy2md(code['python-packages/gaussian_processes']))
    f.write('\n')

    f.write('# Parameter inference for fractional Brownian Motion\n')
    f.write('\n')
    f.write(lpy2md(code['python-packages/fbm']))
    f.write('\n')
    f.write(lpy2md(code['python-packages/inference']))
    f.write('\n')
    f.write(lpy2md(code['inference_convergence']))
    f.write('\n')

    f.write('# Impact of short-time deviations from fBM\n')
    f.write('\n')
    f.write(lpy2md(code['short_time_modification']))
    f.write('\n')

    f.write('# Subdiffusion in lipid bilayers\n')
    f.write('\n')
    f.write(lpy2md(code['python-packages/lipid_analysis_common_code']))
    f.write('\n')
    f.write(lpy2md(code['lipid_analysis_l=10']))
    f.write('\n')
    f.write(lpy2md(code['lipid_analysis_l=50']))
    f.write('\n')
    f.write(lpy2md(code['lipid_analysis_l=100']))
    f.write('\n')
    f.write(lpy2md(code['lipid_analysis_l=200']))
    f.write('\n')

    f.write('# Unit tests\n')
    f.write('```\n')
    f.write(open_documentation('test_log.txt').read())
    f.write('```\n')
