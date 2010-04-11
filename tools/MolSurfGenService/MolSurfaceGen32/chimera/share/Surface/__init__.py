from actions import surface_models
from actions import surface_pieces, selected_surface_pieces, all_surface_pieces
from actions import show_surfaces, hide_surfaces
from actions import color_surfaces, delete_surfaces
from actions import show_surfaces_as_mesh, show_surfaces_filled
from actions import split_surfaces, split_selected_surfaces
from actions import toggle_surface_selectability

from sphere import surface_sphere

# -----------------------------------------------------------------------------
# Used by methods that color a surface and automatically update the coloring.
# Calling this routine turns off the previous auto-coloring code.
#
def set_coloring_method(name, model, stop_cb = None):

    if hasattr(model, 'coloring_method'):
        cname, cb = model.coloring_method
        if name != cname:
            if cb:
                cb(model)
    model.coloring_method = (name, stop_cb)

# -----------------------------------------------------------------------------
# Used by methods that adjust surface visibility automatically.
# Calling this routine turns off the previous visibility-adjusting code.
#
def set_visibility_method(name, model, stop_cb = None):

    if hasattr(model, 'visibility_method'):
        cname, cb = model.visibility_method
        if name != cname:
            if cb:
                cb(model)
    model.visibility_method = (name, stop_cb)
