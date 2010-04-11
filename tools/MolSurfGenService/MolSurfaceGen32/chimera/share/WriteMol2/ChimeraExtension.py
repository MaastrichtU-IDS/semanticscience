import chimera.extension

class WriteMol2EMO(chimera.extension.EMO):
	def name(self):
		return 'Write Mol2'
	def description(self):
		return 'write mol2 file'
	def categories(self):
		return ['Utilities']
	def icon(self):
		#return self.path('rainbow.png')
		return None
	def activate(self):
		from chimera.dialogs import display
		display(self.module('gui').WriteMol2Dialog.name)
		return None

# it's in the File menu, so no need to make it a tool...
#chimera.extension.manager.registerExtension(WriteMol2EMO(__file__))
