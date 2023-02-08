# ## %T %n: Support code for working with Gaussian stochastic processes

# ### Prelude

# Import common scientific libraries

import numpy as np

# Import modules from ActivePapers

# from unit_tests import test # missing

# ### Various utility functions

# Convert between the covariance matrix for a Gaussian stochastic
# process and the covariance matrix for its increments.

def sigma_i_to_sigma_p(m):
    return np.add.accumulate(np.add.accumulate(m, axis=0), axis=1)

def sigma_p_to_sigma_i(m):
    l = m.shape[0]
    m = np.vstack([np.zeros((1, l+1), np.int),
                   np.hstack([np.zeros((l, 1), np.int), m])])
    m = m[1:, :] - m[:-1, :]
    m = m[:, 1:] - m[:, :-1]
    return m

# These two functions are inverses of each other for any matrix, not
# just for valid covariance matrices.

'''
# unit_tests.py is missing
@test
def sigma_conversion_test():
    m = np.arange(16).reshape((4, 4))
    assert (sigma_p_to_sigma_i(sigma_i_to_sigma_p(m)) == m).all()
    assert (sigma_i_to_sigma_p(sigma_p_to_sigma_i(m)) == m).all()
'''

# Generate n trajectories of length l, given a covariance matrix sigma
# of size l x l.

def make_trajectories(sigma, n):
    from .reproducible_random_numbers import multivariate_normal
    l = sigma.shape[0]
    m = np.zeros((l,), dtype=np.float64)
    return multivariate_normal(m, sigma, n)

'''
# unit_tests.py is missing
@test
def trajectory_generation_test():
    s = np.eye(10)
    t = make_trajectories(s, 100)
    assert t.shape == (100, 10)
'''
