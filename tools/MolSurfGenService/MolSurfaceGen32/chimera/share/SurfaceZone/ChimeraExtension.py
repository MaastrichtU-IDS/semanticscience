import chimera.extension

# -----------------------------------------------------------------------------
#
class Surface_Zone_EMO(chimera.extension.EMO):

	def name(self):
		return 'Surface Zone'
	def description(self):
		return 'Show piece of surface near selected atoms'
	def categories(self):
		return ['Surface/Binding Analysis']
	def icon(self):
		return self.path('surfzone.png')
	def activate(self):
		self.module('gui').show_surface_zone_dialog()
		return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Surface_Zone_EMO(__file__))

# -----------------------------------------------------------------------------
# Add bondzone command.
#
def bzone(cmdname, args):
  from SurfaceZone import bondzone
  bondzone.bondzone_command(cmdname, args)
def no_bzone(cmdname, args):
  from SurfaceZone import bondzone
  bondzone.no_bondzone_command(cmdname, args)
import Midas.midas_text
Midas.midas_text.addCommand('bondzone', bzone, no_bzone, help = True, changesDisplay=False)
