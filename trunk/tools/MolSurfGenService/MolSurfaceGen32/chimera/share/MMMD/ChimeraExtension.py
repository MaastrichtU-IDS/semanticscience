# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class mmmdEMO(chimera.extension.EMO):
	def name(self):
		return 'Minimize Structure'
	def description(self):
		return 'Find local energy minimum of molecules'
	def categories(self):
		return ['Structure Editing']
	#def icon(self):
	#	return self.path("Template.png")
	def activate(self):
		from chimera.dialogs import display
		display(self.module('gui').mmmdDialog.name)
		return None
	def cmdMMMD(self, cmdName, args):
		from Midas.midas_text import doExtensionFunc
		func = getattr(self.module('cmdline'), cmdName)
		doExtensionFunc(func, args,
				specInfo=[("spec", "molecules", "molecules")])
	def modelPanelMM_CB(self, molecules):
		self.module('modelpanel').minimize(molecules)
	def modelPanelMD_CB(self, molecules):
		self.module('modelpanel').dynamics(molecules)

emo = mmmdEMO(__file__)

chimera.extension.manager.registerExtension(emo)

import ModelPanel
ModelPanel.addButton("minimize...", emo.modelPanelMM_CB, defaultFrequent=False)
#ModelPanel.addButton("run MD", emo.modelPanelMD_CB)

from Midas.midas_text import addCommand
addCommand("minimize", emo.cmdMMMD, help=True)
#addCommand("dynamics", emo.cmdMMMD, help=True)
