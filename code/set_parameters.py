# ## %T %n: Define various parameters used in the examples

# ### Prelude

# Import common scientific libraries

import numpy as np
from activepapers.contents import data

# Import modules from this ActivePaper

from inference import merge_grids

# ### Parameter settings

# The following settings apply to the illustrations based on synthetic trajectories,
# i.e. trajectories generated using a random number generator from known probability
# distributions. Our analysis of lipid trajectories uses parameters that were tuned
# to the input data, see the calclet `lipid_analysis` for the details.
#
# To run the computations with different settings, do the following:
#
#  1. Change the settings in this calclet and run it.
#  2. `aptool update`

parameters = data.create_group('parameters')

# The lipid trajectories have $\alpha \approx 0.6$, so we use this
# value for exploring the convergence of the inference scheme.

parameters['alpha_in'] = 0.6

# We construct a grid of $\alpha$ values that covers the whole
# range $0\ldots 2$ but is denser around `alpha_in`. All likelihoods
# and probability distributions for $\alpha$ are computed for the
# values on this grid.

parameters['alpha_grid'] = \
         merge_grids(np.linspace(0.01, 2.-0.01, 200),
                     np.linspace(parameters['alpha_in'][...]-0.3,
                                 parameters['alpha_in'][...]+0.3,
                                 200),
                     np.linspace(parameters['alpha_in'][...]-0.1,
                                 parameters['alpha_in'][...]+0.1,
                                 200))

# We use two different trajectory lengths to illustrate its impact on
# the inference process.

parameters['trajectory_lengths'] = [10, 100]

# For the convergence plots, we use 1000 trajectories. For
# maximum-likelihood estimates, 500 trajectories are sufficient.

parameters['n_traj_convergence'] = 1000
parameters['n_traj_ml_estimate'] = 500
