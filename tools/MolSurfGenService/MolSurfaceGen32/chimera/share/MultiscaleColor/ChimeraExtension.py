# -----------------------------------------------------------------------------
#
def msc_command(cmdname, args):
  import MultiscaleColor
  MultiscaleColor.multiscale_color(cmdname, args)

# -----------------------------------------------------------------------------
#
def msc_undo_command(cmdname, args):
  import MultiscaleColor
  MultiscaleColor.multiscale_uncolor(cmdname, args)

# -----------------------------------------------------------------------------
#
import Midas.midas_text
Midas.midas_text.addCommand('msc', msc_command, msc_undo_command, help = True)
