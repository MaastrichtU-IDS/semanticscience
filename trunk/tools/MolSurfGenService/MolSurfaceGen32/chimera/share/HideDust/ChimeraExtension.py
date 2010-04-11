from chimera.extension import EMO, manager

# -----------------------------------------------------------------------------
#
class Hide_Dust_EMO(EMO):

	def name(self):
		return 'Hide Dust'
	def description(self):
		return 'Hide small surface pieces'
	def categories(self):
		return ['Volume Data']
	def icon(self):
		return None
	def activate(self):
		self.module('gui').show_dust_dialog()
		return None

# -----------------------------------------------------------------------------
#
manager.registerExtension(Hide_Dust_EMO(__file__))
