import chimera.extension

# -----------------------------------------------------------------------------
#
class Icosahedron_EMO(chimera.extension.EMO):

	def name(self):
		return 'Icosahedron Surface'
	def description(self):
		return 'Make a surface interpolated between an icosahedron and a sphere'
	def categories(self):
		return ['Higher-Order Structure']
	def icon(self):
		return None
	def activate(self):
		self.module('gui').show_icosahedron_dialog()
		return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Icosahedron_EMO(__file__))
