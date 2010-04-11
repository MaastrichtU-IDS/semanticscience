# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: chain.py 26655 2009-01-07 22:02:30Z gregc $

from manager import selMgr

# register some element type selectors
selectorTemplate = """\
selAdd = []
minimal = %(minimal)d
backbone = %(backbone)d
fullSide = %(fullSide)d
protMinbbAtoms = {"CA":1, "C":1, "N":1}
protMaxbbAtoms = {"O":2, "OXT":2}
protMaxbbAtoms.update(protMinbbAtoms)
nucMinbbAtoms = {"O3'":1, "C3'":1, "C4'":1, "C5'":1, "O5'":1, "P":0}
nucMaxbbAtoms = {"O1P":2, "O2P":2, "O2'":2, "C2'":2, "O4'":2, "C1'":2}
nucMaxbbAtoms.update(nucMinbbAtoms)

if fullSide and not backbone:
	del protMaxbbAtoms["CA"]
	del nucMaxbbAtoms["C1'"]

for mol in molecules:
        for res in mol.residues:
		# isolated residues don't participate
		children = res.oslChildren()
		if len(children) == children[0].molecule.rootForAtom(
					children[0], True).size.numAtoms:
			continue
		atoms = res.atomsMap
		for protName, testable in protMinbbAtoms.items():
			if not testable:
				continue
			if not atoms.has_key(protName):
				protein = 0
				break
		else:
			protein = 1
		
		if not protein:
			for nucName, testable in nucMinbbAtoms.items():
				if not testable:
					continue
				if not atoms.has_key(nucName):
					nucleic = 0
					break
			else:
				nucleic = 1
			if not nucleic:
				continue
		
		if protein:
			if minimal and backbone:
				bbAtoms = protMinbbAtoms
			else:
				bbAtoms = protMaxbbAtoms
		else:
			if minimal and backbone:
				bbAtoms = nucMinbbAtoms
			else:
				bbAtoms = nucMaxbbAtoms
		
		if backbone:
			for bbAtom in bbAtoms.keys():
				try:
					selAdd.extend(atoms[bbAtom])
				except KeyError:
					pass
		else:
			for name, atomList in atoms.items():
				if not bbAtoms.has_key(name):
					selAdd.extend(atomList)
sel.add(selAdd)
sel.addImplied(vertices=0)
"""
chainInfo = {
	"minimal":
		{ "backbone": 1, "minimal": 1, "fullSide": 0 },
	"full":
		{ "backbone": 1, "minimal": 0, "fullSide": 0 },
	"with CA/C1'":
		{ "backbone": 0, "minimal": 0, "fullSide": 1 },
	"without CA/C1'":
		{ "backbone": 0, "minimal": 0, "fullSide": 0 }
}
for chainType, infoDict in chainInfo.items():
	if infoDict["backbone"]:
		subCat = "backbone"
	else:
		subCat = "side chain/base"
	selMgr.addSelector("main/side chain", [selMgr.STRUCTURE,
		subCat, chainType], selectorTemplate % infoDict)
selMgr.makeCallbacks()
del chainType, infoDict

