import chimera.extension

# -----------------------------------------------------------------------------
#
class Flatten_Icosahedron_EMO(chimera.extension.EMO):

	def name(self):
		return 'Flatten Icosahedron'
	def description(self):
		return 'Flatten icosahedral multiscale model'
	def categories(self):
		return ['Higher-Order Structure']
	def icon(self):
		return None
	def activate(self):
		self.module('gui').show_flatten_icosahedron_dialog()
		return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Flatten_Icosahedron_EMO(__file__))
