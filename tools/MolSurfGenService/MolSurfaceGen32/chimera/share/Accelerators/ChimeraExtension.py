import chimera.extension

class Accelerator_Browser_EMO(chimera.extension.EMO):
  def name(self):
    return 'Keyboard Shortcuts'
  def description(self):
    return 'Shows dialog listing keyboard shortcuts.'
  def categories(self):
    return ['General Controls']
  def icon(self):
    return None
  def activate(self):
    self.module().show_accelerator_dialog()
    return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Accelerator_Browser_EMO(__file__))
    
# ----------------------------------------------------------------------------
# Add 'ac' Midas command to turn on accelerators.
#
def accel_cmd(cmdname, args):
  from Accelerators import accelerator_command
  accelerator_command(cmdname, args)
from Midas.midas_text import addCommand
addCommand('ac', accel_cmd, None, help = True, changesDisplay = True)

# ----------------------------------------------------------------------------
# Check for auto-start
#
import Accelerators
Accelerators.autostart_accelerators()
