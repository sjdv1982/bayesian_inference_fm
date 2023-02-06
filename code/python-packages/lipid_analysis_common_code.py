# ## %T %n: Center-of-mass diffusion of lipids in a membrane (common code for all $L$)

# The analysis of the lipid trajectories is repeated for different
# values of the parameter $L$, which is the number of steps in each
# trajectory subsample. Each analysis is a separate calclet, because
# that makes it possible to run it independently. This module contains
# code and parameters common to all these calclets.

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

from fbm import sigma_p
from inference import merge_grids, max_lh_estimate, plot_convergence

# ### I/O and preprocessing

# The trajectories contain the $x$, $y$, $z$ coordinates of the lipid
# centers of masses at each time step. We read only the $x$ and $y$
# coordinates, $z$ being the direction perpendicular to the membrane
# plane. More over, we shift $x$ and $y$ to 0 at $t=0$ and then
# discard the first point, which is no longer of interest. Finally,
# because the $x$ and $y$ trajectories are equivalent, we fuse the
# "molecule number" and "xyz" array axes, returning a 2d array with $2
# N$ single-coordinate trajectories for a system containing $N$
# lipids. We also retrieve the sampling timestep from the trajectory.

def read_trajectory(trajectory, max_steps, sample):
    time = trajectory['particles/universe/position/time'] \
                     [0:2*sample:sample]
    positions = trajectory['particles/universe/position/value'] \
                          [0:sample*(max_steps+1):sample, :, :2]
    data = positions[1:] - positions[0]
    data.shape = (data.shape[0], 2*data.shape[1])
    return time[1]-time[0], data.T

# The fBM inference procedure assumes $2 D_\alpha \Delta t^\alpha=1$
# for simplicity. Therefore we estimate this quantity from the
# increments and divide all coordinates by its square root. Note that
# the variable `D` actually represents $2 D_\alpha \Delta t^\alpha$,
# as everywhere else in the code.

def estimate_d_and_normalize(ts):
    increments = ts[:, 1:] - ts[:, :-1]
    cov = (increments[:, np.newaxis, :]*increments[:, :, np.newaxis]) \
          .mean(axis=0)
    d = cov.diagonal().mean()
    return d, ts/np.sqrt(d)

# ### Data

# We have two trajectories for the same system: a short-time trajectory
# of 300 ps, sampled every 0.03 ps, and a long-time trajectory of 600 ns,
# sampled every 18 ps.

short_time = data['short_time_trajectory']
long_time = data['long_time_trajectory']

# ### Probability densities as a function of $\alpha$

# We construct a grid of the $\alpha$ values that will be used in the
# inference procedure. It covers the whole range $0..2$ but it is
# denser around `alpha_focus`, where the most interesting data will be
# seen. Note that there is no bias towards this `alpha_focus` in the
# inference procedure, the denser grid only makes for more detailed plots
# in this region.

alpha_focus = 0.55

alpha_grid = merge_grids(np.linspace(0.01, 2.-0.01, 200),
                         np.linspace(alpha_focus-0.3, alpha_focus+0.3, 200))

# ### Estimation of $\alpha$

# We compute estimates for $2 D_\alpha \Delta t^{alpha}$, normalize the
# trajectories to $2 D_\alpha \Delta t^{alpha} \to 1$, and then compute
# a maximum-likelihood estimate of $\alpha$. This is done for several
# input rajectories and several sampling step sizes.

def estimate_parameters(trajectories, l, table_ds):

    with open_documentation(table_ds, 'w') as output:

        output.write("dt, alpha, 2 * D * dt^alpha\n")

        dts = []
        alphas = []
        ds = []
        for trajectory, ss in trajectories:
            for s in ss:
                dt, tr = read_trajectory(trajectory, l, s)
                # Make sure we actually got $L$ steps - it might be less.
                assert tr.shape[1] == l
                d, tr = estimate_d_and_normalize(tr)
                alpha = max_lh_estimate(tr, sigma_p, alpha_grid)
                dts.append(dt)
                alphas.append(alpha)
                ds.append(d)
                output.write("%f, %f, %f\n" % (dts[-1], alphas[-1], ds[-1]))

    dts = np.array(dts)
    alphas = np.array(alphas)
    ds = np.array(ds)

    return dts, alphas, ds

# For comparison, we show fBM with the three parameter fits from
# [Stachura & Kneller 2015](http://dx.doi.org/10.1063/1.4936129)
# in our plots. These are the values taken from this paper:

earlier_fits = [('MSD', 'red', 0.516, 0.0555),
                ('WDFT', 'brown', 0.452, 0.0466),
                ('MEE', 'darkcyan', 0.466, 0.0394)]

# The $D_\alpha$ values are in nm$^2$/ns$^\alpha$, contrary to what
# the table caption in the paper says. We need them in
# nm$^2$/ps$^\alpha$, so we do a conversion. We also need to
# correct by a factor 2 for the fact that the literature values
# are for two-dimensional diffusion (in the lipid plane), whereas
# here we look at the $x$ and $y$ coordinates separately.

earlier_fits = \
   [(label, color, alpha_fit, 0.5*d_alpha_fit/1000.**alpha_fit)
    for label, color, alpha_fit, d_alpha_fit in earlier_fits]

# Another interesting comparison is ballistic motion for short
# times, i.e. times smaller than the mean collision times between
# molecules. Ballistic motion is described by fBM in the limit
# $\alpha \to 2$. Its diffusion constant is given by
# $D_2 = <v^2>/2 = k T / 2 m$. 

kT = 2.66 # kJ/mol at T = 320 K
m = 936.  # g/mol
d_2 = 0.5*kT/m


def plot_parameters(dts, alphas, ds, t_max, pdf_ds):

# First, some final computations:
#  - $\alpha$ and $D$ averaged over the asymptoti regime, which 
#    correponds to $\Delta t > 10$
#  - the characteristic diffusion time $\tau$, computed from $D$,
#    $\alpha$, and the diffusion constant of ballistic motion.

    alpha_mean = alphas.repeat(dts > 10.).mean()
    d_mean = (0.5*ds.repeat(dts > 10.)/(dts.repeat(dts > 10.)**alpha_mean)).mean()
    tau = (d_mean/d_2)**(1./(2.-alpha_mean))

# We prepare the plot...

    fig, axs = plt.subplots(2, 1, sharex=True, sharey=False)
    dash_style = [10, 3, 3, 3]

# and first plot the estimate for $\alpha$...

    axs[0].set_xscale('log')
    axs[0].plot(dts, alphas,
             marker="o", markersize=10,
             linestyle='--')
    axs[0].set_ylabel(r"$\alpha_{ML}$")

# next, the asymptotic fBM...

    dt_values = np.array([10., t_max])
    axs[0].plot(dt_values, alpha_mean*np.ones(dt_values.shape),
                label=r"$\alpha=%.2f$" % alpha_mean,
                color='black', linestyle='--', linewidth=2) \
          [0].set_dashes(dash_style)

# followed by the ballistic motion for short times...

    dt_values = np.array([0.01, 0.1])
    axs[0].plot(dt_values, 2.*np.ones(dt_values.shape), label="ballistic",
                color='darkred', linestyle='--', linewidth=2) \
          [0].set_dashes(dash_style)

# and the three fits from the literature.

    dt_values = np.array([1000., t_max])
    for label, color, alpha_fit, d_alpha_fit in earlier_fits:
        axs[0].plot(dt_values, np.ones(dt_values.shape)*alpha_fit,
                    label=label, color=color, linestyle='--', linewidth=2) \
              [0].set_dashes(dash_style)

# We also need to fix some details of the presentation.

    axs[0].legend(loc='upper right')
    axs[0].set_ylim(0.4, 2.05)


# In a second panel, we plot $2 D_\alpha \Delta t^{\alpha}$,
# which is in fact the MSD ...

    axs[1].set_xlabel(r"$\Delta t$ [ps]")
    axs[1].set_xscale('log')
    axs[1].set_yscale('log')

    axs[1].plot(dts, ds,
                marker="s", markersize=10,
                linestyle='--')
    axs[1].set_ylabel(r"$2 D_\alpha \Delta t^{\alpha}$ [nm$^2$]")

# plus the asymptotic fBM...

    dt_values = np.array([0.2*tau, t_max])
    msd_values = 2.*d_mean*dt_values**alpha_mean
    axs[1].plot(dt_values, msd_values,
                label=r"$\alpha=%.2f$" % alpha_mean,
                color='black', linestyle='--', linewidth=2) \
          [0].set_dashes(dash_style)

# the ballistic regime...

    dt_values = np.array([0.01, 5.*tau])
    axs[1].plot(dt_values, 2.*d_2*dt_values**2, label="ballistic",
                color='darkred', linestyle='--', linewidth=2) \
          [0].set_dashes(dash_style)

# a vertial line indicating $\tau$...

    axs[1].plot([tau, tau], [1.e-6, 1.e-1],
                color='black', linewidth=2, linestyle='dotted')
    axs[1].text(1.2*tau, 1.e-6, r"$\tau=%.2f$ ps" % tau, fontsize=18)

# and finally, the fits from the literature...

    dt_values = np.array([10., t_max])
    for label, color, alpha_fit, d_alpha_fit in earlier_fits:
        msd_values = 2.*d_alpha_fit*dt_values**alpha_fit
        axs[1].plot(dt_values, msd_values,
                    label=label, color=color, linestyle='--', linewidth=2) \
              [0].set_dashes(dash_style)

# followed by presentation details.

    axs[1].legend(loc='lower right')

    plt.savefig(open_documentation(pdf_ds, 'w'))


# Another plot shows $D_\alpha$ directly, rather than the combination
# $2 D_\alpha \Delta t^{\alpha}$. Its computation involves the
# estimated $\alpha$, leading to a larger uncertainty than for $2
# D_\alpha \Delta t^{\alpha}$, which is the more fundamental quantity
# from a computational point of view. Note also that the units of
# $D_\alpha$ depend on $\alpha$ and thus vary across the plot!

def plot_D(dts, alphas, ds, t_max, pdf_ds):

# We need to re-do the computation of the averages.

    alpha_mean = alphas.repeat(dts > 10.).mean()
    d_mean = (0.5*ds.repeat(dts > 10.)/(dts.repeat(dts > 10.)**alpha_mean)).mean()
    tau = (d_mean/d_2)**(1./(2.-alpha_mean))

# We start the plot with the valued of $D_\alpha$

    dash_style = [10, 3, 3, 3]
    plt.figure()
    plt.plot(dts, 0.5*ds/(dts**alphas),
             marker="o", markersize=10,
             linestyle='--')
    plt.xscale('log')
    plt.xlabel(r"$\Delta t$ [ps]")
    plt.ylabel(r"$D_\alpha$ [nm$^2$/ps$^\alpha$]")

# Again we add the asymptotic and short-time regimes plus the
# fits from the literature.

    dt_values = np.array([10., t_max])
    plt.plot(dt_values, d_mean*np.ones(dt_values.shape),
             label=r"$D_{%.2f} = %.5f$" % (alpha_mean, d_mean),
             color='black',
             linestyle='--', linewidth=2) \
       [0].set_dashes(dash_style)

    dt_values = np.array([0.01, 0.05])
    plt.plot(dt_values, d_2*np.ones(dt_values.shape),
             label="ballistic", color='darkred',
             linestyle='--', linewidth=2) \
       [0].set_dashes(dash_style)

    dt_values = np.array([1000., t_max])
    for label, color, alpha_fit, d_alpha_fit in earlier_fits:
        plt.plot(dt_values, np.ones(dt_values.shape)*d_alpha_fit,
                 label=label, color=color, linestyle='--', linewidth=2) \
        [0].set_dashes(dash_style)

    plt.legend(loc="upper right")

    plt.savefig(open_documentation(pdf_ds, 'w'))
