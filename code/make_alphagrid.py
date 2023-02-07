import numpy as np
from .inference import merge_grids

# We construct a grid of $\alpha$ values that covers the whole
# range $0\ldots 2$ but is denser around `alpha_in`. All likelihoods
# and probability distributions for $\alpha$ are computed for the
# values on this grid.

alpha_grid = \
         merge_grids(np.linspace(0.01, 2.-0.01, 200),
                     np.linspace(alpha_in-0.3,
                                 alpha_in+0.3,
                                 200),
                     np.linspace(alpha_in-0.1,
                                 alpha_in+0.1,
                                 200))

result = alpha_grid
