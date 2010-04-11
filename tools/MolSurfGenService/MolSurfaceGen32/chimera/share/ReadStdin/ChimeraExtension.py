import chimera.extension

class ReadStdinEMO(chimera.extension.EMO):

	def name(self):
		return "ReadStdin"
	def description(self):
		return "read Chimera commands from standard input"
	def categories(self):
		return ["Utilities"]
	def activate(self):
		self.module().run()
		return None

emo = ReadStdinEMO(__file__)
chimera.extension.manager.registerExtension(emo)
