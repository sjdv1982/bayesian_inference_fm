# ## %T %n: Fractional Brownian Motion

# ### Prelude

# Import common scientific libraries

import numpy as np
import numpy.linalg as la

# Import modules from ActivePapers

import gaussian_processes as gp
from unit_tests import test

# ### Discretely sampled fractional Brownian motion

# Fractional Brownian Motion (fBM) is continuous Gaussian stochastic
# process for a position coordinate. Its main parameter, $\alpha$,
# takes values between 0 and 2. For $\alpha = 1$, fBM describes
# standard Brownian motion.  For $\alpha < 1$, an fBM process exhibits
# subdiffusion, and for $\alpha > 1$ superdiffusion. A second
# parameter, $D$, defines the scale of the position coordinate. For
# $\alpha=1$, $D$ is the standard diffusion constant. The code in this
# module assumes $D=1$ for simplicity. Input data with $D \neq 1$ must
# be scaled appropriately.

# fBM can be sampled at arbitrary time points, but the code in this
# module assumes sampling on a equidistant time grid. Moreover, the
# position at time 0 is assumed to be 0 and thus not a random
# variable. An $l$-step process is then fully defined by the
# covariance matrix for the $l$ positions at the end of each step:

def sigma_p(alpha):
    def fn(l):
        i = 1+np.arange(l, dtype=np.float64)[:, np.newaxis]
        j = 1+np.arange(l, dtype=np.float64)[np.newaxis, :]
        return 0.5*(i**alpha + j**alpha - np.fabs(i-j)**alpha)
    return fn

# It is also useful to look at the increments of a sampled fBM
# process, which are defined as the differences between the positions
# at consecutive time steps. The increments are a stationary Gaussian
# process, fully defined by their covariance matrix:

def sigma_i_off_diagonal(alpha, k):
    return 0.5*((k+1)**alpha - 2.*k**alpha + (k-1)**alpha)

def sigma_i(alpha):
    def fn(l):
        m = np.eye(l, dtype=np.float64)
        for k in range(1, l):
            d = np.diag(sigma_i_off_diagonal(alpha, k)*np.ones((l-k,)), k=k)
            m += d
            m += d.T
        return m
    return fn

# These two covariance matrices are equivalent in that they
# can be computed from each other:

@test
def test_equivalence():
    for alpha in [0.3, 0.5, 0.7]:
        for l in [10, 50, 100]:
            s_p = sigma_p(alpha)(l)
            s_i = sigma_i(alpha)(l)
            assert np.fabs( gp.sigma_i_to_sigma_p(s_i) - s_p ).max() < 1.e-13

# Moreover, both covariance matrices are symmetric and positive
# definite, as required for a Gaussian stochastic process:

@test
def test_covariance():
    for alpha in [0.3, 0.5, 0.7]:
        for l in [10, 50, 100]:
            for s in [sigma_p(alpha)(l), sigma_i(alpha)(l)]:
                assert np.fabs( s - s.T ).max() < 1.e-15
                assert la.slogdet(s)[0] >= 0

# ### fBM with modified short-time behavior

# Being a scale-free model, fBM cannot be correct for short time
# scales, where the underlying microscopic dynamics become
# apparent. To explore the impact of non-fBM short-time dynamics on
# the inference scheme, we use a modified fBM in which the increment
# covariance matrix is changed by replacing its first two time steps
# by their average.

def mod_sigma_i(alpha):
    fbm_sigma_i = sigma_i(alpha)
    def fn(l):
        cv1 = sigma_i_off_diagonal(alpha, 1)
        cv2 = sigma_i_off_diagonal(alpha, 2)
        mean = 0.5*(cv1+cv2)
        d = np.diag((mean-cv1)*np.ones((l-1,)), k=1) \
          + np.diag((mean-cv2)*np.ones((l-2,)), k=2)
        return fbm_sigma_i(l) + d + d.T
    return fn

# The corresponding change to the process covariance matrix affects nearly
# all elements.

def mod_diff_p(l):
    m = np.zeros((l, l), dtype=np.int)
    m[0, 0] = -1
    m[1:, 1:] = np.ones((l-1, l-1), dtype=np.int)
    d = np.diag(np.ones((l,), dtype=np.int))
    d1 = np.diag(np.ones((l-1,), dtype=np.int), k = 1)
    return m + d + d1 + d1.T

def mod_sigma_p(alpha):
    diff = 0.5*(sigma_i_off_diagonal(alpha, 1) - sigma_i_off_diagonal(alpha, 2))
    def fn(l):
        return sigma_p(alpha)(l) - diff*mod_diff_p(l)
    return fn

# Again these two covariance matrices are equivalent in that they can
# be computed from each other:

@test
def test_equivalence_mod():
    for alpha in [0.3, 0.5, 0.7]:
        for l in [10, 50, 100]:
            s_p = mod_sigma_p(alpha)(l)
            s_i = mod_sigma_i(alpha)(l)
            assert np.fabs( gp.sigma_i_to_sigma_p(s_i) - s_p ).max() < 1.e-13

# ### Different sampling time steps

# Given the covariance matrix for an fBM process (or our modified fBM
# process) sampled with time step $\Delta t$, construct the covariance
# matrix for the same process sampled at $s \Delta t$, scaled to make
# the diffusion constant 1 again.

def subsample_sigma(sigma, s):
    return sigma[s-1::s, s-1::s]/sigma[s-1, s-1]

# For $s=1$, the input matrix is returned unchanged ($D=1$ is
# guaranteed by `sigma_p`):

@test
def test_subsampling():
    sigma = sigma_p(0.5)(10)
    assert (subsample_sigma(sigma, 1) == sigma).all()

# Plain fBM being a scale-free process, subsampling simply creates a
# shorter fBM process:

@test
def test_scale_freeness():
    l = 10
    sigma = sigma_p(0.5)(l)
    assert np.fabs(subsample_sigma(sigma, 2)
                   - sigma[:l//2, :l//2]).max() < 1.e-10
    assert np.fabs(subsample_sigma(sigma, 5)
                   - sigma[:l//5, :l//5]).max() < 1.e-10
