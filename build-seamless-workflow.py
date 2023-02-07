import seamless
seamless.database_cache.connect()

from seamless.highlevel import Context, Cell, DeepFolderCell, Module, Transformer
ctx = Context()

#########################################################
# Set up input data folder as a deep folder cell
# TODO: filter out data items that are outputs or parameters
#########################################################

data_folder = {}
with open("data-checksums.list") as f:
    for l in f:
        if not len(l.strip()):
            continue
        filename, checksum = l.split()
        data_folder[filename] = checksum
        
ctx.data_folder = Cell("plain").set(data_folder)
ctx.compute()
data_folder_checksum = ctx.data_folder.checksum
ctx.data = DeepFolderCell()
ctx.data.checksum = data_folder_checksum
ctx.compute()

#########################################################
# Set up simple parameters, editable as YAML by the user
#########################################################

# We have to convert them twice:
# - once to plain (JSON), as simple_parameters2
# - then to a structured cell, so that we can access subcells
#
# The structured cell allows fine-grained dependency tracking:
# transformers can depend on a single parameter instead of on all parameters,
# so changing a single parameter will not recompute everything
# 
# If we were building a web interface, we wouldn't bother with YAML
# we would store the parameters as JSON 
# and expose that directly to HTTP 

ctx.simple_parameters = Cell("yaml")
ctx.simple_parameters.mount("simple-parameters.yaml")
ctx.simple_parameters2 = Cell("plain")
ctx.simple_parameters2 = ctx.simple_parameters
ctx.simple_parameters3 = ctx.simple_parameters2
ctx.translate()


#########################################################
# Organize Python code
#########################################################

# "modules" for python packages
# "code" for transformer code
# "transformers" for the transformers themselves
ctx.modules = Context()
ctx.code = Context()
ctx.transformers = Context()

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
tf.alpha_in = ctx.simple_parameters3.alpha_in
ctx.alpha_grid = tf.result
ctx.alpha_grid.celltype = "binary"
ctx.translate()