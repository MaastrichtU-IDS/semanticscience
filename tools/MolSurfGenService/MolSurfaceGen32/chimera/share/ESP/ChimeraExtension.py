import chimera.extension

class EspEMO(chimera.extension.EMO):
	def name(self):
		return 'Coulombic Surface Coloring'
	def description(self):
		return 'color surface by Coulombic potential'
	def categories(self):
		return ['Surface/Binding Analysis']
	def icon(self):
		return self.path('icon.png')
		return None
	def activate(self):
		from chimera.dialogs import display
		display(self.module('gui').EspDialog.name)
		return None

chimera.extension.manager.registerExtension(EspEMO(__file__))
