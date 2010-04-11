import chimera.extension

# -----------------------------------------------------------------------------
#
class SurfaceCap_EMO(chimera.extension.EMO):

	def name(self):
		return 'Surface Capping'
	def description(self):
		return 'Draw caps over holes in clipped surfaces'
	def categories(self):
		return ['Depiction', 'Surface/Binding Analysis']
	def icon(self):
		return self.path('groelcap.png')
	def activate(self):
		self.module('gui').show_capper_dialog()
		return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(SurfaceCap_EMO(__file__))

import SurfaceCap
SurfaceCap.enable_capping(True)
