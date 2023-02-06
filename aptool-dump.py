# Author: Sjoerd de Vries, CNRS
# license: public domain

import sys
import os
import h5py
import numpy as np

active_paper_file = sys.argv[1]
target_directory = sys.argv[2]
ap = h5py.File(active_paper_file)
apdata = ap["data"]
assert isinstance(apdata, h5py.Group)
datadir = os.path.join(target_directory, "data")
os.makedirs(datadir, exist_ok=True)

def dump(datagroup, targetdir):
    for childname, child in datagroup.items():
        child_target = os.path.join(targetdir, childname)
        if isinstance(child, h5py.Group):
            os.makedirs(child_target, exist_ok=True)
            dump(child, child_target)
        else:
            print("dump", child_target)
            if child.ndim == 0 or not child.dtype.shape:
                child2 = child
            else: #structured data, bugged in h5py
                child2 = np.empty(child.shape, child.dtype)
                for n in range(len(child)):
                    child2[n] = child[n]
            np.save(child_target, child2)

dump(apdata, datadir)