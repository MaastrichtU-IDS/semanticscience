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

class AddAttrEMO(chimera.extension.EMO):
	help = "add/change attributes of atoms/residues/models"
	def name(self):
		return 'Define Attribute'
	def description(self):
		return self.help
	def categories(self):
		return ['Structure Analysis']
	def activate(self):
		from chimera import dialogs
		dialogs.display(self.module('gui').AddAttrDialog.name)
		return None

chimera.extension.manager.registerExtension(AddAttrEMO(__file__))

def cmdAddAttr(cmdName, args):
	from AddAttr import addAttributes
	from Midas.midas_text import doExtensionFunc
	doExtensionFunc(addAttributes, args,
				specInfo=[("spec", "models", "molecules")])

from Midas.midas_text import addCommand
addCommand("defattr", cmdAddAttr, help=True, changesDisplay=False)

