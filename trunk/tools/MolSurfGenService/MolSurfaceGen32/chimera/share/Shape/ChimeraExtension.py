# -----------------------------------------------------------------------------
# Register shape command.
#
def shape_cmd(cmdname, args):
    from Shape import shape_command
    shape_command(cmdname, args)
from Midas.midas_text import addCommand
addCommand('shape', shape_cmd, help = True)

# -----------------------------------------------------------------------------
# Register surface resize mouse mode keyboard shortcut.
#
def resize_mouse_mode():
    from Shape.resizemode import enable_resize_surface_mouse_mode as e
    e(one_use = True)
from Accelerators import add_accelerator
add_accelerator('sz', 'Resize selected surfaces', resize_mouse_mode)
