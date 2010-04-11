# ----------------------------------------------------------------------------
# Code to take an icosahedrol multiscale model and move subunits to
# create a flat layout, flipping out the 10 triangles around two opposite
# 5-fold vertices (to look like spiked crowns) and then unwrapping the
# resulting cylinder.  Assume VIPER icosahedral coordinate system.
#
from flatten import flatten_icosahedron, unflatten_icosahedron
from flatten import flattened_icosahedron_geometry
from flatten import multiscale_models, model_radius
