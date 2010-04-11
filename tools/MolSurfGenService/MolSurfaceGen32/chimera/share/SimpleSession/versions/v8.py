# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v8.py 26655 2009-01-07 22:02:30Z gregc $

from v7 import reportRestoreError, restoreWindowSize, init, \
	restoreOpenModelsAttrs, RemapDialog, beginRestore, endRestore, \
	sessionID, registerAfterModelsCB, makeAfterModelsCBs, findFile, \
	idLookup, restoreSurfaces, getColor, restoreMiscAttrs, \
	restoreOpenStates, restoreLabels, restoreColors, restoreVdw, \
	restoreDrawModes, restoreDispChanged, restoreSelections, \
	restorePseudoBondGroups, restoreCamera
from v7 import restoreMolecules as v7restoreMolecules

import globals # so that various version files can easily access same variables
import chimera

from weakref import WeakKeyDictionary
_skipRestore = WeakKeyDictionary()

def noAutoRestore(mol):
	"""Don't automatically save/restore this molecule"""
	_skipRestore[mol] = True

def autoRestorable(mol):
	# 'in' doesn't seem to work for WeakKeyDictionarys
	return not _skipRestore.has_key(mol)

def restoreMolecules(srcMolMap):
	v7restoreMolecules(srcMolMap)

	# restore pre-1.2038 radii
	from SimpleSession import modelMap
	for mList in modelMap.values():
		for m in mList:
			allAtom = False
			for a in m.atoms:
				if a.element.number == 1:
					allAtom = True
					break
			if not allAtom:
				# radii already the same
				continue
			for a in m.atoms:
				eName = a.element.name
				if eName == "S" or eName == "P":
					a.radius = 1.7
				elif eName == "O":
					a.radius = 1.35
				elif a.name == "NE2" \
				and a.residue.type == "GLN":
					a.radius = 1.45
				elif a.name in ["N","N4","ND2",
							"NE","NH1","NH2"]:
					a.radius = 1.45
				elif eName == "N":
					a.radius = 1.7
				elif a.name == "CG" \
				and a.residue.type in ["HIS","PHE","TRP","TYR"]:
					a.radius = 1.7
				elif a.name == "CD2" \
				and a.residue.type == "LEU":
					a.radius = 1.25
				elif a.name == "CD1" \
				and a.residue.type in ["ILE", "LEU"]:
					a.radius = 1.25
				elif a.name in ["CD1", "C2", "C4", "C5", "C6",
						"C8", "CD2", "CE1", "CE2",
						"CE3", "CH2", "CZ2", "CZ3"]:
					a.radius = 1.7

				elif a.name == "CZ":
					if a.residue.type == "ARG":
						a.radius = 1.5
					else:
						a.radius = 1.7
				elif a.name == "CG" \
				and a.residue.type in ["ASN", "ASP"]:
					a.radius = 1.5
				elif a.name == "CD" \
				and a.residue.type in ["GLN", "GLU"]:
					a.radius = 1.5
				elif a.name == "C":
					a.radius = 1.5
				elif eName == "C":
					a.radius = 1.25
				elif eName == "H":
					a.radius = 1
				else:
					a.radius = 2
