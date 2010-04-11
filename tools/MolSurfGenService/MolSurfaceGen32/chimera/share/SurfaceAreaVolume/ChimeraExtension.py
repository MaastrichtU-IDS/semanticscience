import chimera.extension

class SurfaceAreaVolumeEMO(chimera.extension.EMO):

	def name(self):
		return "Area/Volume from Web"
	def description(self):
		return "compute solvent accessible area/volume for atoms"
	def categories(self):
		return ["Surface/Binding Analysis"]
	def activate(self):
		self.module().run()
		return None
#	def modelPanel(self, molecules):
#		for m in molecules:
#			self.module("SurfaceAreaVolume").modelPanel(m)
#

emo = SurfaceAreaVolumeEMO(__file__)
#import ModelPanel
#ModelPanel.addButton(emo.name(), emo.modelPanel,
#			defaultFrequent=0, balloon=emo.description())
chimera.extension.manager.registerExtension(emo)
