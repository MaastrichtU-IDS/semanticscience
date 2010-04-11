def add_accelerators():

  # Avoid importing Surface module unless accelerator is used.
  def cb(function_name, on_selection = True):
    def afunc(fname = function_name, sel = on_selection):
      import Surface
      f = getattr(Surface, fname)
      if sel:
        f(Surface.selected_surface_pieces())
      else:
        f()
    return afunc

  from Accelerators import add_accelerator as aa
  aa('co', 'Color selected surfaces', cb('color_surfaces'))
  aa('Ds', 'Delete selected surfaces', cb('delete_surfaces'))
  aa('fs', 'Show selected surfaces in filled style', cb('show_surfaces_filled'))
  aa('ms', 'Show selected surfaces using mesh style',
     cb('show_surfaces_as_mesh'))
  aa('Sc', 'Split connected surface pieces',
     cb('split_selected_surfaces', False))
  aa('ts', 'Toggle surface selectability',
     cb('toggle_surface_selectability', False))

add_accelerators()

# -----------------------------------------------------------------------------
# Register sop command.
#
def sop_cmd(cmdname, args):
    from Surface.sopcommand import sop_command
    sop_command(cmdname, args)
from Midas.midas_text import addCommand
addCommand('sop', sop_cmd, help = True)

# -----------------------------------------------------------------------------
# Register attributes of SurfaceModel and SurfacePiece.
# TODO:  Make all use of SurfaceModel import Surface instead of _surface.
#
from Surface import inspect

# -----------------------------------------------------------------------------
# Save surfaces in session file.
#
def save_session(trigger, arg, file):
  from Surface import session
  session.save_surface_state(file)
from SimpleSession import SAVE_SESSION
from chimera import triggers as t
t.addHandler(SAVE_SESSION, save_session, None)
