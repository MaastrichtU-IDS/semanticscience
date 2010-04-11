# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ChimeraExtension.py 26655 2009-01-07 22:02:30Z gregc $

import chimera.extension

class ShowAttrEMO(chimera.extension.EMO):
	help = "color or change depiction of atoms/residues\nbased on attribute values"
	def name(self):
		return 'Render by Attribute'
	def description(self):
		return self.help
	def categories(self):
		return ['Depiction', 'Structure Analysis']
	def activate(self):
		from chimera import dialogs
		dialogs.display(self.module().ShowAttrDialog.name).configure(
								mode="Render")
		return None

chimera.extension.manager.registerExtension(ShowAttrEMO(__file__))

def showDialog(models, mode):
	import ShowAttr
	from chimera import dialogs
	d = dialogs.display(ShowAttr.ShowAttrDialog.name)
	d.configure(models=models, mode=mode)

def showSaveAttr():
	import ShowAttr
	return ShowAttr.SaveAttrDialog()
from chimera import dialogs
dialogs.register("SaveAttrDialog", showSaveAttr)

import ModelPanel
ModelPanel.addButton("render/sel by attr...", lambda models, sd=showDialog:
			sd(models, "Render"), balloon=ShowAttrEMO.help)
