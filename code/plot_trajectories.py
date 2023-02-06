import matplotlib
matplotlib.use('PDF')
import matplotlib.pyplot as plt
from mpl_toolkits.mplot3d import Axes3D

from activepapers.contents import data, open_documentation

positions = data['POPC_martini_nvt/particles/universe/position/value']
dt = data['POPC_martini_nvt/particles/universe/position/time'][1]

# Many spaces added to the right of the plot titles,
# to work around a matplotlib bug that shows the title three times.
pad = 100*" "

skip = 1000
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
ax.view_init(elev=10, azim=-70)
points = positions[::skip, :, :]
for i in range(points.shape[1]):
    ax.plot(points[:, i, 0], points[:, i, 1], points[:, i, 2])
ax.set_title(("All lipids, $\\Delta t = %.0f$ ps"+pad) % skip*dt,
             loc='left')
plt.savefig(open_documentation('all_lipids.pdf', 'w'))

skip = 10
fig = plt.figure()
ax = fig.add_subplot(111, projection='3d')
particle = 0
points = positions[::skip, particle, :]
ax.plot(points[:, 0], points[:, 1], points[:, 2])
ax.set_title(("One lipid, $\\Delta t = %.0f$ ps"+pad) % skip*dt,
             loc='left')
plt.savefig(open_documentation('one_lipid.pdf', 'w'))
