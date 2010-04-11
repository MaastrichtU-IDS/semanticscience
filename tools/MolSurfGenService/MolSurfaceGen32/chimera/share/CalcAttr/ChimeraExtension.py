import chimera.extension

class CalcAttrEMO(chimera.extension.EMO):

	def name(self):
		return "Attribute Calculator"
	def description(self):
		return "compute new attributes from existing attribute values"
	def categories(self):
		return ["Structure Analysis"]
	def activate(self):
		self.module().run()
		return None

emo = CalcAttrEMO(__file__)
chimera.extension.manager.registerExtension(emo)
