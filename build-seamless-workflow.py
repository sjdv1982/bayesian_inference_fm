import os
import seamless
seamless.database_cache.connect()
seamless.database_sink.connect()

from seamless.highlevel import Context, Cell, FolderCell, DeepFolderCell, Module, Transformer
ctx = Context()

#########################################################
# Set up input data folder as a deep folder cell
#########################################################

data_folder = {}
with open("data-checksums.list") as f:
    for l in f:
        if not len(l.strip()):
            continue
        filename, checksum = l.split()
        data_folder[filename] = checksum
        
ctx.data_TEMP = Cell("plain").set(data_folder)
ctx.compute()
data_folder_checksum = ctx.data_TEMP.checksum
ctx.data = DeepFolderCell()
ctx.data.checksum = data_folder_checksum
del ctx.data_TEMP
ctx.compute()

#########################################################
# Set up simple parameters, editable as YAML by the user
#########################################################

# We have to convert them twice:
# - once to plain (JSON), as parameters2
# - then to a structured cell, so that we can access subcells
#
# The structured cell allows fine-grained dependency tracking:
# transformers can depend on a single parameter instead of on all parameters,
# so changing a single parameter will not recompute everything
# 
# If we were building a web interface, we wouldn't bother with YAML
# we would store the parameters as JSON 
# and expose that directly to HTTP 

ctx.parameters = Cell("yaml")
ctx.parameters.mount("parameters.yaml")
ctx.parameters2 = Cell("plain")
ctx.parameters2 = ctx.parameters
ctx.parameters3 = ctx.parameters2
ctx.translate()

#########################################################
# Organize workflow
#########################################################

# "modules" for Python packages
# "code" for transformer code
# "transformers" for the transformers themselves
# "results" for the transformer results

ctx.modules = Context()
ctx.code = Context()
ctx.transformers = Context()
ctx.results = Context()

#########################################################
# make_alphagrid (previously: set_parameters)
#########################################################

ctx.modules.inference = Module()
ctx.modules.inference.mount("code/python-packages/inference.py")

ctx.code.make_alphagrid = Cell("code")
ctx.code.make_alphagrid.mount("code/make_alphagrid.py")

tf = ctx.transformers.make_alphagrid = Transformer()
tf.code = ctx.code.make_alphagrid

tf.inference = ctx.modules.inference

tf.alpha_in = ctx.parameters3.alpha_in

ctx.alpha_grid = tf.result
ctx.alpha_grid.celltype = "binary"
ctx.translate()

#########################################################
# inference_convergence
#   runs in 20-30 mins on a laptop
#########################################################

ctx.code.inference_convergence = Cell("code")
ctx.code.inference_convergence.mount("code/inference_convergence.py")

tf = ctx.transformers.inference_convergence = Transformer()
tf.code = ctx.code.inference_convergence

tf.inference = ctx.modules.inference

ctx.modules.gaussian_processes = Module()
ctx.modules.gaussian_processes.mount("code/python-packages/gaussian_processes.py")
tf.gaussian_processes = ctx.modules.gaussian_processes

ctx.modules.reproducible_random_numbers = Module()
ctx.modules.reproducible_random_numbers.mount("code/python-packages/reproducible_random_numbers.py")
tf.reproducible_random_numbers = ctx.modules.reproducible_random_numbers

ctx.modules.fbm = Module()
ctx.modules.fbm.mount("code/python-packages/fbm.py")
tf.fbm = ctx.modules.fbm

tf.alpha_in = ctx.parameters3.alpha_in
tf.alpha_grid = ctx.alpha_grid
tf.trajectory_lengths = ctx.parameters3.trajectory_lengths
tf.n_traj_convergence = ctx.parameters3.n_traj_convergence
tf.meta = {"ncores": -1} # uses all cores of the machine. Not used in Seamless at the moment.

ctx.translate()

# Seamless can run computations in parallel, but that would flood the local machine
# Disable if a Seamless job manager has been set up
ctx.compute(report=30)

os.makedirs("results/inference_convergence", exist_ok=True)
ctx.results.inference_convergence = FolderCell()
ctx.results.inference_convergence = tf.result
ctx.results.inference_convergence.mount("results/inference_convergence", "w")
ctx.compute()

#########################################################
# short_time_modification
#   runs in ~45 mins on a laptop
#########################################################

ctx.code.short_time_modification = Cell("code")
ctx.code.short_time_modification.mount("code/short_time_modification.py")

tf = ctx.transformers.short_time_modification = Transformer()
tf.code = ctx.code.short_time_modification

tf.fbm = ctx.modules.fbm
tf.inference = ctx.modules.inference
tf.gaussian_processes = ctx.modules.gaussian_processes
tf.reproducible_random_numbers = ctx.modules.reproducible_random_numbers

tf.alpha_in = ctx.parameters3.alpha_in
tf.alpha_grid = ctx.alpha_grid
tf.trajectory_lengths = ctx.parameters3.trajectory_lengths
tf.n_traj_convergence = ctx.parameters3.n_traj_convergence
tf.n_traj_ml_estimate = ctx.parameters3.n_traj_ml_estimate
tf.meta = {"ncores": -1} # uses all cores of the machine. Not used in Seamless at the moment.

ctx.translate()

# Seamless can run computations in parallel, but that would flood the local machine
# Disable if a Seamless job manager has been set up
ctx.compute(report=30)

os.makedirs("results/short_time_modification", exist_ok=True)
ctx.results.short_time_modification = FolderCell()
ctx.results.short_time_modification = tf.result
ctx.results.short_time_modification.mount("results/short_time_modification", "w")
ctx.compute()

#########################################################
# lipid analysis
#########################################################

ctx.code.lipid_analysis = Cell("code")
ctx.code.lipid_analysis.mount("code/lipid_analysis.py")

ctx.short_time_trajectory_times = ctx.data["data/short_time_trajectory/particles/universe/position/time.npy"]
ctx.short_time_trajectory_positions = ctx.data["data/short_time_trajectory/particles/universe/position/value.npy"]
ctx.long_time_trajectory_times = ctx.data["data/long_time_trajectory/particles/universe/position/time.npy"]
ctx.long_time_trajectory_positions = ctx.data["data/long_time_trajectory/particles/universe/position/value.npy"]

#########################################################
# lipid analysis, l=10
#   runs in ~30 mins on a laptop
#
# lipid analysis, l=50
#   runs in ~2h on a laptop
#
# lipid analysis, l=100
#   DISABLED: runs in >7h on a laptop
#
# lipid analysis, l=200
#   DISABLED
#
#########################################################

# By default, only l=10 and l=50 are run because of CPU time
# Remove the [:2] in the next line to enable them.
for analysis_index, l in enumerate([10, 50, 100, 200][:2]):
    attr = "lipid_analysis_l_{}".format(l)
    tf = ctx.transformers[attr] = Transformer()
    tf.code = ctx.code.lipid_analysis

    tf.fbm = ctx.modules.fbm
    tf.inference = ctx.modules.inference
    tf.lipid_analysis_parameters = ctx.parameters3.lipid_analysis[analysis_index]
    tf.short_time_trajectory_times = ctx.short_time_trajectory_times
    tf.short_time_trajectory_positions = ctx.short_time_trajectory_positions
    tf.long_time_trajectory_times = ctx.long_time_trajectory_times
    tf.long_time_trajectory_positions = ctx.long_time_trajectory_positions

    tf.meta = {"ncores": -1} # uses all cores of the machine. Not used in Seamless at the moment.

    # This will print the progress of the calculation, but it will also force 
    #   local execution (no job delegation to a cluster)
    # Note that debug settings are not stored in the workflow
    tf.debug.direct_print = True 

    ctx.translate()

    # Seamless can run computations in parallel, but that would flood the local machine
    # Disable if a Seamless job manager has been set up
    print(attr)
    ctx.compute(report=30)
    print(tf.logs)
    print()
    
    result_dir = os.path.join("results", attr)
    os.makedirs(result_dir, exist_ok=True)
    ctx.results[attr] = FolderCell()
    ctx.results[attr] = tf.result
    ctx.results[attr].mount(result_dir, "w")
    ctx.translate()

ctx.save_graph("bayesian_inference_fbm.seamless")