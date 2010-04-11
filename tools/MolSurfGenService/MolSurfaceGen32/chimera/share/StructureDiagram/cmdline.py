# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

def run(cmdName, args):
	from Midas.midas_text import doExtensionFunc
	doExtensionFunc(mol2diagram, args,
				specInfo=[("spec", "molecules", "molecules")])

def mol2diagram(molecules):
	from gui import StructureDiagramDialog
	if molecules is None:
		import chimera
		molecules = chimera.openModels.list(
				modelTypes=[chimera.Molecule])
	for m in molecules:
		StructureDiagramDialog(molecule=m)
