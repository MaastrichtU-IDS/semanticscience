# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class AddHEMO(chimera.extension.EMO):
	def name(self):
		return 'AddH'
	def description(self):
		return 'add hydrogens'
	def categories(self):
		return ['Structure Editing']
	def icon(self):
		return self.path('AddH.png')
	def activate(self):
		from chimera.dialogs import display
		display(self.module('gui').AddHDialog.name)
		return None
	def modelPanelCB(self, molecules):
		from chimera.dialogs import display
		d = display(self.module('gui').AddHDialog.name)
		d.molList.setvalue(molecules)

emo = AddHEMO(__file__)
chimera.extension.manager.registerExtension(emo)
import ModelPanel
ModelPanel.addButton("add hydrogens...", emo.modelPanelCB,
						defaultFrequent=False)

def cmdAddH(cmdName, args):
        from Midas.midas_text import doExtensionFunc
	import AddH
        doExtensionFunc(AddH.cmdAddH, args,
                                specInfo=[("spec", "molecules", "molecules")])

from Midas.midas_text import addCommand
addCommand("addh", cmdAddH, help=True)

