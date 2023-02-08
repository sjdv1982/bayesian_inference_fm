# ## %T %n: Convergence of the Bayesian inference method

# Import common scientific libraries

import numpy as np
import matplotlib.pyplot as plt
from io import BytesIO

# Import modules from this ActivePaper

from .gaussian_processes import make_trajectories
from .fbm import sigma_p, mod_sigma_p, subsample_sigma
from .inference import merge_grids, max_lh_estimate, plot_convergence

### Convergence for different lengths of input trajectories

# Produce a convergence plot for 1000 trajectories for each trajectory
# length.

result = {}
for l in trajectory_lengths:
    plot_convergence(make_trajectories(sigma_p(alpha_in)(l),
                                       n_traj_convergence),
                     sigma_p, alpha_grid, r"$\alpha$", alpha_in)
    plt.suptitle(r"fBM trajectories, $L = %d$" % l, fontsize=20)
    fname = 'inference_convergence/convergence_fbm_l=%d.png' % l
    png = BytesIO()
    plt.savefig(png)
    #result[fname] = png.getvalue() # bug in Seamless
    result[fname] = np.array(png.getvalue()) # workaround

#@image inference_convergence/convergence_fbm_l=10.png

#@image inference_convergence/convergence_fbm_l=100.png
