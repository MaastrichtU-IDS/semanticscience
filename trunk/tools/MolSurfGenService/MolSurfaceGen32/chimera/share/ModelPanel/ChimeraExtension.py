# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class ModelPanelEMO(chimera.extension.EMO):
	def name(self):
		return 'Model Panel'
	def description(self):
		return 'allows inspection and actions on open models'
	def categories(self):
		return ['General Controls']
	def icon(self):
		return self.path('modelpanel.png')
	def activate(self):
		from chimera.dialogs import display
		display(self.module('base').ModelPanel.name)
		return None

chimera.extension.manager.registerExtension(ModelPanelEMO(__file__))

class RainbowEMO(chimera.extension.EMO):
	def name(self):
		return 'Rainbow'
	def description(self):
		return 'rainbow-color model(s)'
	def categories(self):
		return ['Depiction']
	def icon(self):
		return self.path('rainbow.png')
	def activate(self):
		from chimera.dialogs import display
		display(self.module('rainbow').RainbowDialog.name)
		return None

chimera.extension.manager.registerExtension(RainbowEMO(__file__))

class SeqPickerEMO(chimera.extension.EMO):
	def name(self):
		return 'Sequence'
	def description(self):
		return 'show sequence of model(s)'
	def categories(self):
		return ['Sequence']
	def icon(self):
		return None
	def activate(self):
		import chimera
		mols = chimera.openModels.list(modelTypes=[chimera.Molecule])
		self.module('base').seqCmd(mols)
		return None

chimera.extension.manager.registerExtension(SeqPickerEMO(__file__))
