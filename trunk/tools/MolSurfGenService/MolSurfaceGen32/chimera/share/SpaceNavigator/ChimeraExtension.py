from SpaceNavigator import sn

from Accelerators import add_accelerator
add_accelerator('nd', 'Space navigator only translate/rotate', 
                sn.toggle_dominant_mode)
add_accelerator('nz', 'Toggle space navigator zoom mode', 
                sn.toggle_zoom_mode)
add_accelerator('na', 'Space navigator moves inactive models',
                sn.toggle_all_models)
add_accelerator('nf', 'Toggle space navigator fly through mode',
                sn.toggle_fly_mode)

