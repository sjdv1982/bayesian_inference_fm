from activepapers.contents import data
import logging

import MMTK
import MMTK.Trajectory
import numpy as np
import immutable.np as IN

import mosaic.immutable_model as M
from mosaic.h5md import Trajectory
from mosaic.hdf5 import HDF5Store

trfile = '~/Trajectories/lipids/POPC_martini/15.nvt_600ns_2/POPC_martini_600ns_2_320K_nvt_CM_traj.nc'
group = data.create_group('POPC_martini_nvt')

logging.info("Importing %s" % trfile)
mmtk_trajectory = MMTK.Trajectory.Trajectory(None, trfile)
mmtk_universe = mmtk_trajectory.universe
# In the following, we assume an OrthorhombicPeriodicUniverse, so
# let's make sure we have one.
assert type(mmtk_universe) == MMTK.Universe.OrthorhombicPeriodicUniverse

# The trajectory frames are sampled with a constant time step, but
# time labels may not be contiguous, so we re-generate a time axis.
time = mmtk_trajectory.time
dt = time[1]-time[0]
time = dt*np.arange(len(mmtk_trajectory))

# Each particle in the MMTK universe corresponds to the
# center-of-mass of a lipid.
atom = M.atom(M.cgparticle("COM"))
natoms = mmtk_universe.numberOfAtoms()
fragment = M.fragment("lipid", (), (("center-of-mass", atom),), ())
universe = M.universe('cuboid',
                      [(fragment, "lipids", natoms)])

# Use MMTK's readParticleTrajectory to remove the jumps caused
# by periodic boundary conditions. The trajectory is small enough
# to fit into memory, so this is the simplest way to proceed.
logging.info("Reading particle trajectories")
pt = [mmtk_trajectory.readParticleTrajectory(com).array
      for com in mmtk_universe]

# Create the H5MD/MOSAIC trajectory
with Trajectory(group, universe) as trajectory:
    pos = np.zeros((natoms, 3), np.float32)
    for i in range(len(mmtk_trajectory)):
        logging.info("Writing step %d" % i)
        box = mmtk_trajectory.box_size[i]
        for j, ptj in enumerate(pt):
            pos[j, :] = ptj[i]
        conf = M.Configuration(universe, IN.array(pos), IN.array(box))
        trajectory.write_step(i, time[i], conf)
