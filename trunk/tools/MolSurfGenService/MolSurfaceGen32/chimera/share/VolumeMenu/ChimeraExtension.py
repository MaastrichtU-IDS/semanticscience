import chimera.extension

# -----------------------------------------------------------------------------
#
class Volume_Menu_EMO(chimera.extension.EMO):

  def name(self):
    return 'Volume Menu on Menubar'
  def description(self):
    return 'Place a copy of the volume menu on the main window menu bar'
  def categories(self):
    return ['Volume Data']
  def icon(self):
    return None
  def activate(self):
    self.module().toplevel_volume_menu('toggle')
    return None

# -----------------------------------------------------------------------------
#
emo = Volume_Menu_EMO(__file__)
chimera.extension.manager.registerExtension(emo)

# -----------------------------------------------------------------------------
#
import chimera
if not chimera.nogui:
  import VolumeMenu
  if VolumeMenu.volume_menu_shown_preference():
    VolumeMenu.toplevel_volume_menu('show-delayed')
