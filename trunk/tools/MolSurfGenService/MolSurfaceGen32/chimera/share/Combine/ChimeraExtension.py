# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class CombineEMO(chimera.extension.EMO):
	def name(self):
		return 'Combine Molecular Models'
	def description(self):
		return 'combine molecular models'
	def categories(self):
		return []
	def icon(self):
		return None
	def activate(self):
		#from chimera.dialogs import display
		#display(self.module('gui').AddHDialog.name)
		return None
	def modelPanelCB(self, molecules):
		self.module('gui').CombineDialog(models=molecules)

emo = CombineEMO(__file__)
#chimera.extension.manager.registerExtension(emo)
import ModelPanel
ModelPanel.addButton("copy/combine...", emo.modelPanelCB,
	balloon="Combine molecular models into new model", moleculesOnly=True)

def cmdCombine(cmdName, args):
        from Midas.midas_text import doExtensionFunc
	import Combine
        doExtensionFunc(Combine.cmdCombine, args,
                                specInfo=[("spec", "mols", "molecules"),
					("refSpec", "refMol", "molecules")])

from Midas.midas_text import addCommand
addCommand("combine", cmdCombine, help=True)
