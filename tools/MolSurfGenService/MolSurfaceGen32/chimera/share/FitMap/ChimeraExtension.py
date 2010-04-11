# -----------------------------------------------------------------------------
#
import chimera.extension

# -----------------------------------------------------------------------------
#
class Fit_Map_EMO(chimera.extension.EMO):

    def name(self):
        return 'Fit in Map'
    def description(self):
        return 'Move atomic model or map to best fit locations in a map'
    def categories(self):
        return ['Volume Data']
    def icon(self):
        return None
    def activate(self):
        self.module('gui').show_fit_map_dialog()
        return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Fit_Map_EMO(__file__))

# -----------------------------------------------------------------------------
#
def fit_map_cb():
    import FitMap
    FitMap.move_selected_atoms_to_maximum()
def fit_map_rotation_only_cb():
    import FitMap
    FitMap.move_selected_atoms_to_maximum(optimize_translation = False)
def fit_map_shift_only_cb():
    import FitMap
    FitMap.move_selected_atoms_to_maximum(optimize_rotation = False)
def move_atoms_to_maxima():
    import FitMap
    FitMap.move_atoms_to_maxima()
	
# -----------------------------------------------------------------------------
#
from Accelerators import add_accelerator
add_accelerator('ft', 'Move model to maximize density at selected atoms',
                fit_map_cb)
add_accelerator('fr', 'Rotate model to maximize density at selected atoms',
                fit_map_rotation_only_cb)
add_accelerator('fs', 'Shift model to maximize density at selected atoms',
                fit_map_shift_only_cb)
add_accelerator('mX', 'Move selected atoms to local maxima',
                move_atoms_to_maxima)
