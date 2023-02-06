# ## %T %n: Center-of-mass diffusion of lipids in a membrane ($L=50$)

# ### Use the common code for all $L$.

from lipid_analysis_common_code import *

# ### Parameters

l = 50

# ### Convergence

# We illustrate the convergence of the inference procedure for a few
# sampling timesteps for each of the two trajectories.

for label, trajectory, ss in [('st', short_time, [20, 50]),
                              ('lt', long_time, [1, 50, 100])]:
    for s in ss:
        dt, tr = read_trajectory(trajectory, l, s)
        d, tr = estimate_d_and_normalize(tr)
        plot_convergence(tr, sigma_p, alpha_grid, r"$\alpha$")
        plt.suptitle(r"lipid trajectories, $\Delta t = %.2f$ ps" % dt, fontsize=20)
        fname = 'lipid_analysis/convergence_%s_l=%d_s=%d.pdf' % (label, l, s)
        plt.savefig(open_documentation(fname, 'w'))

# #### Short-time trajectory
#
#@image lipid_analysis/convergence_st_l=50_s=20.pdf
#@image lipid_analysis/convergence_st_l=50_s=50.pdf
#
# #### Long-time trajectory
#
#@image lipid_analysis/convergence_lt_l=50_s=1.pdf
#@image lipid_analysis/convergence_lt_l=50_s=50.pdf
#@image lipid_analysis/convergence_lt_l=50_s=100.pdf


# ### Parameter estimation

# For each of the two trajectories, and for several values of the
# sampling step size, we estimate the parameters $\alpha$ and
# $2 D_\alpha \Delta t^{alpha}$. The results are returned and also
# written to a text-format table for easy access.

dts, alphas, ds = estimate_parameters(
    trajectories = [(short_time, [1, 2, 5, 10, 20, 50, 100, 200]),
                    (long_time, [1, 2, 5, 10, 20, 50, 100, 200, 500])],
    l = l,
    table_ds = 'lipid_analysis/sampling_timestep_l=%d.txt' % l)

# All of this data is shown in one complex plot.

plot_parameters(dts, alphas, ds,
                t_max = 10000.,
                pdf_ds = 'lipid_analysis/sampling_timestep_l=%d.pdf' % l)

#@image lipid_analysis/sampling_timestep_l=50.pdf

plot_D(dts, alphas, ds,
       t_max = 10000.,
       pdf_ds = 'lipid_analysis/D_vs_sampling_timestep_l=%d.pdf' % l)

#@image lipid_analysis/D_vs_sampling_timestep_l=50.pdf
