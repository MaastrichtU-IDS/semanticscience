# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: analysis.py 26655 2009-01-07 22:02:30Z gregc $

from chimera import UserError, selection

def analysisAtoms(movie, useSel, ignoreBulk, ignoreHyds):
	mol = movie.model.Molecule()
	if useSel:
		selAtoms = selection.currentAtoms()
		if selAtoms:
			# reduce to just ours
			sel1 = selection.ItemizedSelection()
			sel1.add(selAtoms)
			sel2 = selection.ItemizedSelection()
			sel2.add(mol.atoms)
			sel1.merge(selection.INTERSECT, sel2)
			atoms = sel1.atoms()
			if not atoms:
				raise UserError("No selected atoms in"
							" trajectory!")
		else:
			atoms = mol.atoms
	else:
		atoms = mol.atoms

	if ignoreBulk:
		bulkSel = selection.OSLSelection("@/surfaceCategory="
				"solvent or surfaceCategory=ions")
		atomSel = selection.ItemizedSelection()
		atomSel.add(atoms)
		atomSel.merge(selection.REMOVE, bulkSel)
		atoms = atomSel.atoms()
		if not atoms:
			raise UserError("No atoms remaining after ignoring"
							" solvent/ions")
	if ignoreHyds:
		atoms = [a for a in atoms if a.element.number != 1]
		if not atoms:
			raise UserError("No atoms remaining after ignoring"
							" hydrogens")
	return atoms
