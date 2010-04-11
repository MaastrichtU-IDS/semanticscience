import chimera.extension

# -----------------------------------------------------------------------------
#
class Blob_Picker_EMO(chimera.extension.EMO):

	def name(self):
		return 'Measure and Color Blobs'
	def description(self):
		return 'Measure and color connected parts of a surface'
	def categories(self):
		return ['Volume Data', 'Surface/Binding Analysis']
	def icon(self):
		return None
	def activate(self):
		self.module('gui').show_blob_picker_dialog()
		return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Blob_Picker_EMO(__file__))
