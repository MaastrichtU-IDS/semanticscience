# -----------------------------------------------------------------------------
# Register measure command.
#
def measure_cmd(cmdname, args):
  import Measure
  Measure.measure_command(cmdname, args)
from Midas.midas_text import addCommand
addCommand('measure', measure_cmd, help = True)
