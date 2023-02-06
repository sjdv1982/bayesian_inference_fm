# ## %T %n: Convergence of the Bayesian inference method

# ### Prelude

# Make matplotlib produce PDF files for figures

import matplotlib
matplotlib.use('PDF')
del matplotlib

# Import common scientific libraries

import numpy as np
import matplotlib.pyplot as plt
from activepapers.contents import data, open_documentation

# Import modules from this ActivePaper

from gaussian_processes import make_trajectories
from fbm import sigma_p, mod_sigma_p, subsample_sigma
from inference import merge_grids, max_lh_estimate, plot_convergence

# Use the global parameters

parameters = data['parameters']
alpha_in = parameters['alpha_in'][...]
alpha_grid = parameters['alpha_grid'][...]
trajectory_lengths = parameters['trajectory_lengths'][...]
n_traj_convergence = int(parameters['n_traj_convergence'][...])

### Convergence for different lengths of input trajectories

# Produce a convergence plot for 1000 trajectories for each trajectory
# length.

for l in trajectory_lengths:
    plot_convergence(make_trajectories(sigma_p(alpha_in)(l),
                                       n_traj_convergence),
                     sigma_p, alpha_grid, r"$\alpha$", alpha_in)
    plt.suptitle(r"fBM trajectories, $L = %d$" % l, fontsize=20)
    fname = 'inference_convergence/convergence_fbm_l=%d.pdf' % l
    plt.savefig(open_documentation(fname, 'w'))

#@image inference_convergence/convergence_fbm_l=10.pdf

#@image inference_convergence/convergence_fbm_l=100.pdf
