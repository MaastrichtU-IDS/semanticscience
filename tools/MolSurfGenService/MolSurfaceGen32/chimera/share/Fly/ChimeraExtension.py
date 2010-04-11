# -----------------------------------------------------------------------------
# Register fly command.
#
def fly_cmd(cmdname, args):
  import Fly
  Fly.fly_command(cmdname, args)
from Midas.midas_text import addCommand
addCommand('fly', fly_cmd, help = True)
