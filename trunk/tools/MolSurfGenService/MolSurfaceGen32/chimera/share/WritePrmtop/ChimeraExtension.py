import chimera.extension

class WritePrmtopEMO(chimera.extension.EMO):
	def name(self):
		return 'Write Prmtop'
	def description(self):
		return 'write Amber prmtop format and xyz format'
	def categories(self):
		return ['Amber']
	def icon(self):
		#return self.path('rainbow.png')
		return None
	def activate(self):
		from chimera.dialogs import display
		display(self.module('gui').WritePrmtopDialog.name)
		return None

chimera.extension.manager.registerExtension(WritePrmtopEMO(__file__))
