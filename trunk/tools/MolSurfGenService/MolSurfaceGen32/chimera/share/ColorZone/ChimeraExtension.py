import chimera.extension

# -----------------------------------------------------------------------------
#
class Color_Zone_EMO(chimera.extension.EMO):

  def name(self):
    return 'Color Zone'
  def description(self):
    return 'Color piece of surface near selected atoms'
  def categories(self):
    return ['Volume Data', 'Depiction']
  def icon(self):
    return None
  def activate(self):
    self.module('gui').show_color_zone_dialog()
    return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Color_Zone_EMO(__file__))

# ---------------------------------------------------------------------------
#
def split_map():
  import ColorZone
  ColorZone.split_volume_by_color_zone()
    
from Accelerators import add_accelerator
add_accelerator('sm', 'Split volume by color zones.', split_map)
