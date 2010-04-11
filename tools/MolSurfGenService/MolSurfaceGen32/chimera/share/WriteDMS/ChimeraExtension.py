import chimera.extension

class WriteDmsEMO(chimera.extension.EMO):
	def name(self):
		return 'Write DMS'
	def description(self):
		return 'write dms file'
	def categories(self):
		return ['Structure Editing']
	def icon(self):
		#return self.path('rainbow.png')
		return None
	def activate(self):
		self.module('gui').WriteDmsDialog()
		return None

chimera.extension.manager.registerExtension(WriteDmsEMO(__file__))
