import chimera.extension

# -----------------------------------------------------------------------------
#
class Scale_Bar_EMO(chimera.extension.EMO):

	def name(self):
		return 'Scale Bar'
	def description(self):
		return 'Show length scale in graphics window'
	def categories(self):
		return ['Higher-Order Structure']
	def icon(self):
		return self.path('scalebar.gif')
	def activate(self):
		self.module().show_scale_bar()
		return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Scale_Bar_EMO(__file__))
