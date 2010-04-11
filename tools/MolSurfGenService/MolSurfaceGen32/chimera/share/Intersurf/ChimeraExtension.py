import chimera.extension
from Midas import midas_text

class IntersurfEMO(chimera.extension.EMO):
	def name(self):
		return "Intersurf"
	def description(self):
		return "compute interface surface between molecules"
	def categories(self):
		return ["Surface/Binding Analysis"]
	def activate(self):
		self.module().run()
		return None
	def commandLine(self, cmd, args):
		self.module().commandLine(cmd, args)

emo = IntersurfEMO(__file__)
chimera.extension.manager.registerExtension(emo)
midas_text.addCommand("intersurf", emo.commandLine)
