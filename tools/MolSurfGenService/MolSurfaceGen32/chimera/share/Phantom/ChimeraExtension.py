import chimera.extension

# -----------------------------------------------------------------------------
#
class Phantom_Cursor_EMO(chimera.extension.EMO):

	def name(self):
		return 'Phantom Force Feedback'
	def description(self):
		return 'Use Phantom force feedback device with volume data'
	def categories(self):
		return ['Volume Data']
	def icon(self):
		return self.path('phantom.gif')
	def activate(self):
		self.module().show_phantom_dialog()
		return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Phantom_Cursor_EMO(__file__))
