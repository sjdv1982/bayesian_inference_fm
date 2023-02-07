# Author: Sjoerd de Vries, CNRS
# license: public domain

import sys
import os
import h5py
import numpy as np
import traceback

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
            scalar = False
            if child.ndim == 0:
                scalar = True
                child2 = np.empty(1, child.dtype)
                child2[0] = child[()]
            elif not child.dtype.shape:
                child2 = np.empty(child.shape, child.dtype)
                child2[:] = child[:]
            else: #structured data, bugged in h5py
                child2 = np.empty(child.shape, child.dtype)
                for n in range(len(child)):
                    child2[n] = child[n]

            child = child2        
            if child.dtype.fields:
                has_o = False
                dtype = []
                for fieldname, (subdtype, subshape) in child.dtype.fields.items():
                    if subdtype == "O":  # variable byte strings (vlen)
                        has_o = True
                        for n in range(len(child)):
                            assert isinstance(child[n][fieldname], bytes), (n, fieldname) # Python objects must be bytes
                        subdtype = np.array([obj for obj in child[fieldname]]).dtype
                        subshape = ()                    
                    dtype.append((fieldname, (subdtype, subshape)))
                if has_o:
                    newchild = np.empty(child.shape, np.dtype(dtype))
                    for fieldname, (subdtype, subshape) in child.dtype.fields.items():
                        if subdtype == "O":
                            newchild[fieldname] = np.array([obj for obj in child[fieldname]])
                        else:
                            newchild[fieldname] = child[fieldname]
                    child = newchild
            if scalar:
                child = child[0]
            np.save(child_target + ".npy", child)
  
            # Check integrity
            try:
                arr = np.load(child_target + ".npy", allow_pickle=False)
            except Exception:
                print("Integrity check FAILED", file=sys.stderr)
                traceback.print_exc()
  
dump(apdata, datadir)