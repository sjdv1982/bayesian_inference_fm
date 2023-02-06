# ## %T %n: Bayesian inference for parameters of Gaussian stochastic processes

# ### Prelude

# Import from Python standard library

import itertools as it

# Import common scientific libraries

import numpy as np
import numpy.linalg as la
import matplotlib.pyplot as plt

# ### Inference

# All probability densities are evaluated for specific values of model
# parameters. The inference code expects a grid of parameter values to
# be passed in. It is often useful to use non-uniform grids that are
# more closely spaced in the most interesting parameter regions.
# They are most easily made by merging different uniform grids.

def merge_grids(*grids):
    def d(grid):
        return grid[1:]-grid[:-1]
    def spacing(grid):
        return d(grid).min()
    min_spacing = min(*[spacing(g) for g in grids])
    merged = np.sort(np.concatenate(grids))
    return merged.repeat(np.concatenate([d(merged) > 0.5*min_spacing, [1]]))

# Compute the logarithmic likelihood of a set of trajectories
# for multiple values of a parameter of the model for the covariance matrix.

def log_likelihood(trajectories, sigma_fn, parameter_grid):
    log_lh = np.zeros((len(parameter_grid),), np.float64)
    for i, p in enumerate(parameter_grid):
        s = sigma_fn(p)(len(trajectories[0]))
        sign_det, log_det = la.slogdet(s)
        assert sign_det > 0
        for t in trajectories:
            log_lh[i] -= 0.5*(np.dot(t, la.solve(s, t)) + log_det)
    return log_lh

# The generalization to covariance matrices that that depend on
# several parameters is straightforward thanks to Python's itertools
# module.

def log_likelihood_nd(trajectories, sigma_fn, *parameter_grids):
    log_lh = np.zeros(tuple([len(pg) for pg in parameter_grids]), np.float64)
    param_iter = it.product(*parameter_grids)
    index_iter = it.product(*[range(len(k)) for k in parameter_grids])
    for i, p in zip(index_iter, param_iter):
        s = sigma_fn(*p)(len(trajectories[0]))
        sign_det, log_det = la.slogdet(s)
        assert sign_det > 0
        for t in trajectories:
            log_lh[i] -= 0.5*(np.dot(t, la.solve(s, t)) + log_det)
    return log_lh

# For a simple graphical representation of a logarithmic probability
# distribution, extract three characteristic values:
#
#  1. the parameter value with the largest likelihood
#  2. the smallest parameter value whose likelihood is larger
#     than $1/2$ the maximum
#  3. the largest parameter value whose likelihood is larger
#     than $1/2$ the maximum

def spread(parameter_grid, log_p):
    ipeak = np.argmax(log_p)
    p_range = np.log(2.)
    interval = np.repeat(parameter_grid, log_p >= log_p[ipeak]-p_range)
    return parameter_grid[ipeak], interval[0], interval[-1]

# Compute the maximum-likelihood estimate for a parameter of the
# covariance matrix function.

def max_lh_estimate(trajectories, sigma_fn, parameter_grid):
    log_lh = log_likelihood(trajectories, sigma_fn, parameter_grid)
    return parameter_grid[np.argmax(log_lh)]

# ### Plotting

# Make a plot showing the convergence of the inference procedure
# as more and more trajectories are added.

def plot_convergence(trajectories, sigma_fn, parameter_grid,
                     parameter_label, parameter_reference=None):

    sum_log_lh = 0
    peak_and_limits = []
    cumulative_peak_and_limits = []
    for t in trajectories:
        log_lh = log_likelihood(t[np.newaxis, :], sigma_fn, parameter_grid)
        sum_log_lh += log_lh
        peak_and_limits.append(spread(parameter_grid, log_lh))
        cumulative_peak_and_limits.append(spread(parameter_grid, sum_log_lh))

    peak_and_limits = np.array(peak_and_limits)
    cumulative_peak_and_limits = np.array(cumulative_peak_and_limits)

    fig, axes = plt.subplots(1, 2, figsize = (12, 5))
    bars = peak_and_limits[:50]
    n = 1+np.arange(len(bars))
    peak = bars[:, 0]
    err_lower = peak - bars[:, 1]
    err_upper = bars[:, 2] - peak
    axes[0].errorbar(n, bars[:, 0], xerr=0,
                     yerr=np.array([err_lower, err_upper]),
                     fmt='.')
    for index, points in [(0, cumulative_peak_and_limits[:len(bars)]),
                          (1, cumulative_peak_and_limits)]:
        n = 1+np.arange(len(points))
        axes[index].plot(n, points[:, 0], color='red', linewidth=3)
        axes[index].plot(n, points[:, 1], color='red')
        axes[index].plot(n, points[:, 2], color='red')
        if parameter_reference is not None:
            axes[index].plot([0, n[-1]], 2*[parameter_reference], 'g--', linewidth=3)
        if cumulative_peak_and_limits.max() > 1.:
            axes[index].set_ylim((0., 2.))
        else:
            axes[index].set_ylim((0., 1.))
        axes[index].set_xlabel("Number of trajectories")
        axes[index].set_ylabel(parameter_label)
