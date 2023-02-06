# ## %T %n: Random numbers with reproducible initialization

# All code in the ActivePaper using random numbers should import this module
# instead of `numpy.random` in order to ensure that the random number generator
# gets initialized with a unique reproducible seed.

from numpy.random import *
seed(0)
