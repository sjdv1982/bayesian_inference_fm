# ## %T %n: Illustrate fBM with modified short-time behavior

# ### Prelude

# Make matplotlib produce PDF files for figures

import matplotlib
matplotlib.use('PDF')
del matplotlib

# Import common scientific libraries

import matplotlib.pyplot as plt
from activepapers.contents import data, open_documentation

# Import modules from this ActivePaper

from fbm import sigma_p, mod_sigma_p, sigma_i, mod_sigma_i

# Use the global parameters

parameters = data['parameters']
alpha_in = parameters['alpha_in'][...]
alpha_grid = parameters['alpha_grid'][...]
trajectory_lengths = parameters['trajectory_lengths'][...]
n_traj_convergence = int(parameters['n_traj_convergence'][...])
n_traj_ml_estimate = int(parameters['n_traj_ml_estimate'][...])

# ### Illustration of the short-time behavior and its impact on
#     parameter inference with the plain fBM model

fig, axes = plt.subplots(1, 3, figsize = (15, 6))
fig.subplots_adjust(wspace=0.4)

ms = 10.
alfs = 20.
for ax in axes:
    ax.tick_params(axis='both', which='major', labelsize=18)

# Plot the increment correlations, which differ only in two points.

axes[0].plot(sigma_i(alpha_in)(11)[0],
             linestyle='', marker='<', markersize=ms,
             markerfacecolor='blue', markeredgecolor='black',
             label=r'fBM $\alpha=%.1f$' % alpha_in)
axes[0].plot(mod_sigma_i(alpha_in)(11)[0],
             linestyle='', marker='>', markersize=ms,
             markerfacecolor='red',  markeredgecolor='black',
             label=r'modified fBM $\alpha=%.1f$' % alpha_in)
axes[0].set_xlim((-1, 11))
axes[0].legend(loc='upper right')
axes[0].set_xlabel(r"$\tau/\delta t$", fontsize=alfs)
axes[0].set_ylabel(r"$<\Delta X(t) \Delta X(t+\tau))> / (D \cdot \delta t^\alpha)$",
                   fontsize=alfs)

# Plot the MSDs, which differ over a much longer time range.

axes[1].loglog(sigma_p(alpha_in)(1000).diagonal(),
               color='blue',
               label=r'fBM $\alpha=%.1f$' % alpha_in)
axes[1].loglog(mod_sigma_p(alpha_in)(1000).diagonal(),
               color='red',
               label=r'modified fBM $\alpha=%.1f$' % alpha_in)
axes[1].legend(loc='upper left')
axes[1].set_xlabel(r"$t/\delta t$", fontsize=alfs)
axes[1].set_ylabel(r"$<X^2(t)> / (D \cdot \delta t^\alpha)$",
                   fontsize=alfs)

# Compute the maximum-likelihood estimates for $\alpha$.
# The trajectories are generated from the modified model, subsampled
# every $s$ steps. The estimation process uses the plain fBM model.
# For each value of $s$, we generate 500 trajectories of 100 steps each.
# With an increasing sampling time step, the estimate for
# $\alpha$ converges to the known input value `alpha_in`.

from gaussian_processes import make_trajectories
from fbm import sigma_p, mod_sigma_p, subsample_sigma
from inference import merge_grids, max_lh_estimate, plot_convergence

l = trajectory_lengths[-1]
ss = [1, 2, 3, 5, 10, 20, 30, 40, 50, 60, 70, 80, 90, 100]

sigma_big = mod_sigma_p(alpha_in)(max(ss)*l)
alphas = []
fname = 'short_time_modification/subsampling_convergence_l=%d.txt' % l
with open_documentation(fname, 'w') as log:
    log.write("  s, alpha\n")
    for s in ss:
        sigma = subsample_sigma(sigma_big[:s*l, :s*l], s)
        t = make_trajectories(sigma, n_traj_ml_estimate)
        assert t.shape[1] == l
        alphas.append(max_lh_estimate(t, sigma_p, alpha_grid))
        log.write("%3d, %f\n" % (s, alphas[-1]))

# Plot the $\alpha$ values.

axes[2].plot(ss, alphas,
             markerfacecolor='red', markeredgecolor='red',
             marker="o", markersize=ms,
             linestyle='--', color='blue')
axes[2].set_xlim((0, max(ss)+2))
axes[2].set_xlabel(r"$s$", fontsize=alfs)
axes[2].set_ylabel(r"$\alpha_{ML}$", fontsize=alfs)

# Combine the three plots into one figure.

plt.savefig(open_documentation('short_time_modification/overview.pdf', 'w'))

#@image short_time_modification/overview.pdf

# ### Convergence of the inference process

# The above plot shows the maximum-likelihood estimates for $\alpha$,
# but it doesn't show that the inference process actually converges
# properly with $500$ trajectories. Here we show the convergence
# profiles for $s=1$ and $s=10$.

for s in [1, 10]:
    l = trajectory_lengths[-1]
    trs = make_trajectories(mod_sigma_p(alpha_in)(l), n_traj_convergence)
    plot_convergence(trs, sigma_p, alpha_grid, r"$\alpha$", alpha_in)
    plt.suptitle(r"fBM with modified short-time behavior, $L = %d$, $s = %d$" % (l, s),
                 fontsize=20)
    fname = 'short_time_modification/convergence_mod_fbm_s=%d.pdf' % s
    plt.savefig(open_documentation(fname, 'w'))

#@image short_time_modification/convergence_mod_fbm_s=1.pdf

#@image short_time_modification/convergence_mod_fbm_s=10.pdf
