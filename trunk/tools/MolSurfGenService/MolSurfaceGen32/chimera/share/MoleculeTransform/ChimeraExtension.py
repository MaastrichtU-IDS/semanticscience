import chimera.extension

# -----------------------------------------------------------------------------
#
class Molecule_Transform_EMO(chimera.extension.EMO):

	def name(self):
		return 'Transform Molecule Coordinates'
	def description(self):
		return 'Apply a rotation and translation to atom coordinates'
	def categories(self):
		return ['Movement']
	def icon(self):
		return None
	def activate(self):
		self.module('gui').show_molecule_transform_dialog()
		return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Molecule_Transform_EMO(__file__))
