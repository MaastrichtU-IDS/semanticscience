# -----------------------------------------------------------------------------
# Register mask command.
#
def mask_cmd(cmdname, args):
    from Mask.maskcommand import mask_command
    mask_command(cmdname, args)

import Midas.midas_text
Midas.midas_text.addCommand('mask', mask_cmd, help = True)

# -----------------------------------------------------------------------------
# Register contour surface mask shortcut.
#
from Accelerators import add_accelerator
def mask_volume():
    import Mask
    Mask.mask_volume_using_selected_surfaces()
add_accelerator('vm', 'Mask volume using selected surfaces', mask_volume)
