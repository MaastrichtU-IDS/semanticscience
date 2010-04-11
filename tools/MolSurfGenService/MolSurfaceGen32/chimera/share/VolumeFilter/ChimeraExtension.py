# -----------------------------------------------------------------------------
#
from chimera.extension import EMO, manager
class Volume_Filter_EMO(EMO):
  def name(self):
    return 'Volume Filter'
  def description(self):
    return 'Filter volume data'
  def categories(self):
    return ['Volume Data']
  def icon(self):
    return None
  def activate(self):
    self.module('gui').show_volume_filter_dialog()
    return None

manager.registerExtension(Volume_Filter_EMO(__file__))

# -----------------------------------------------------------------------------
# Register vop command.
#
def vop_cmd(cmdname, args):
    from VolumeFilter.vopcommand import vop_command
    vop_command(cmdname, args)
from Midas.midas_text import addCommand
addCommand('vop', vop_cmd, help = True)

# ---------------------------------------------------------------------------
# Register keyboard shortcuts for filtering.
#
def fourier():
  from VolumeFilter import fourier_transform
  fourier_transform()
def laplace():
  from VolumeFilter import laplacian
  laplacian()

from Accelerators import add_accelerator
add_accelerator('FT', 'Fourier transform active volume', fourier)
add_accelerator('LT', 'Calculate Laplacian active volume', laplace)
from median import make_test_volume
add_accelerator('tv', 'Make test volume', make_test_volume)
