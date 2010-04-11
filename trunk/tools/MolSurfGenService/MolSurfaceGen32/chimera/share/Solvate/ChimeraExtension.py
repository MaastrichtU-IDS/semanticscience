# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera

class SolvateEMO(chimera.extension.EMO):
	def name(self):
		return 'Solvate'
	def description(self):
		return 'Solvate molecule'
	def categories(self):
		return ['Amber', 'Structure Editing']
	def activate(self):
		import chimera.dialogs
		chimera.dialogs.display(
				self.module('gui').SolvateDialog.name)
		return None

chimera.extension.manager.registerExtension(SolvateEMO(__file__))

def cmdSolvate(cmdName, args):
	from Midas.midas_text import doExtensionFunc, MidasError
	from Solvate import ValidSolventShapes, ValidSolventModels, initiateSolvate

	fields = args.split(" ")

	if len(fields) < 2:
		raise MidasError(
			"Solvent shape/model arguments required for solvate.")

	shape = fields[0]
	if not( shape in ValidSolventShapes ):
		raise MidasError("Unknown solvent shape: " + fields[1])

	model = fields[1]
        if not( model in ValidSolventModels ):
		raise MidasError("Unknown solvent model: " + fields[2])

	if shape=="cap":
		if len(fields) != 4:
			raise MidasError("Syntax for solvate cap: solvate cap solvent_model center radius")
		center = fields[2]
		extent = fields[3]
	else:
		center = ""
		extent = fields[2]

	import chimera
        mols = chimera.openModels.list(modelTypes=[chimera.Molecule])
	if not chimera.nogui:
		from AddH.gui import checkNoHyds
		checkNoHyds(mols, lambda mols=mols, shape=shape, model=model,
			extent=extent, center=center, status=
			chimera.replyobj.status: initiateSolvate(mols, shape,
			model, extent, center, status), process="solvation")
		return
	initiateSolvate( mols, shape, model, extent, center, chimera.replyobj.status)
        


from Midas.midas_text import addCommand
addCommand("solvate", cmdSolvate, help=True)

