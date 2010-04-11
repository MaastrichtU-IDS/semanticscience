# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera

class AddChargeEMO(chimera.extension.EMO):
	def name(self):
		return 'Add Charge'
	def description(self):
		return 'Add partial charges to atoms'
	def icon(self):
		return self.path('charge.png')
	def categories(self):
		return ['Structure Editing', 'Structure Analysis']
	def activate(self):
		import chimera.dialogs
		chimera.dialogs.display(
				self.module('gui').AddChargesDialog.name)
		return None

chimera.extension.manager.registerExtension(AddChargeEMO(__file__))

def cmdAddCharge(cmdName, args):
	from AddCharge import cmdAddStdCharge, \
					cmdAddNonstdCharge, cmdAddAllCharge
	from Midas.midas_text import doExtensionFunc, MidasError
	if not args:
		mode = 'a'
	else:
		fields = args.split(None, 1)
		if len(fields) > 1:
			fullMode, args = fields
		else:
			fullMode = fields[0]
			args = ""
		mode = fullMode[0].lower()

	if mode == 's':
		func = cmdAddStdCharge
		specInfo = [("spec", "molecules", "molecules")]
	elif mode == 'n':
		func = cmdAddNonstdCharge
		specInfo = [("resSpec", "residues", "residues")]
	elif mode == 'a':
		func = cmdAddAllCharge
		specInfo = [("spec", "molecules", "molecules")]
	else:
		raise MidasError("Unknown mode for %s: %s" % (cmdName,fullMode))
	doExtensionFunc(func, args, specInfo=specInfo)

from Midas.midas_text import addCommand
addCommand("addcharge", cmdAddCharge, help=True, changesDisplay=False)

