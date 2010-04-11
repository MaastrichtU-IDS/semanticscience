# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera

class AddionsEMO(chimera.extension.EMO):
	def name(self):
		return 'Add Ions'
	def description(self):
		return 'Add counter ions to molecule'
	def categories(self):
		return ['Amber', 'Structure Editing']
	def activate(self):
		import chimera.dialogs
		chimera.dialogs.display(
				self.module('gui').AddionsDialog.name)
		return None

chimera.extension.manager.registerExtension(AddionsEMO(__file__))

def cmdAddions(cmdName, args):
	from Midas.midas_text import doExtensionFunc, MidasError
	from Addions import ValidIontypes, initiateAddions

	fields = args.split(" ")

	if len(fields) ==0:
		raise MidasError("No arguments were given for solvate.")

	iontype = fields[0]
	if not( shape in ValidIontypes ):
		raise MidasError("Unknown solvent shape: " + fields[1])

	numion = fields[1]


	import chimera
        mols = chimera.openModels.list(modelTypes=[chimera.Molecule])
	initiateAdions( mols, shape, model, extent, center, chimera.replyobj.status)
        


from Midas.midas_text import addCommand
addCommand("adions", cmdAddions, help=True)

