# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: drawmode.py 26655 2009-01-07 22:02:30Z gregc $

from manager import selMgr
import chimera

# register some draw mode selectors
dmSelCategory = "Draw Mode"
dmAtomCategory = "atom"
dmBondCategory = "bond"
atomSelectorTemplate = """\
selAdd = []
for mol in molecules:
        for atom in mol.atoms:
                if atom.drawMode == %d:
                        selAdd.append(atom)
sel.add(selAdd)
"""
bondSelectorTemplate = """\
selAdd = []
for mol in molecules:
        for bond in mol.bonds:
                if bond.drawMode == %d:
                        selAdd.append(bond)
sel.add(selAdd)
"""
combinedSelectorTemplate = """\
selAdd = {}
for mol in molecules:
	for atom in mol.atoms:
		if atom.drawMode != %d:
			continue
		addBonds = {}
		for bond in atom.bonds:
			if bond.drawMode == %d:
				addBonds[bond] = 1
		if addBonds or not atom.bonds:
			selAdd.update(addBonds)
			selAdd[atom] = 1
sel.add(selAdd)
"""

comboModes = [
	("wire", chimera.Atom.Dot, chimera.Bond.Wire),
	("stick", chimera.Atom.EndCap, chimera.Bond.Stick),
	("ball and stick", chimera.Atom.Ball, chimera.Bond.Stick),
	("sphere", chimera.Atom.Sphere, chimera.Bond.Wire)
]
registrant = "draw mode"
for name, atomMode, bondMode in comboModes:
	selMgr.addSelector(registrant, [dmSelCategory, name],
			combinedSelectorTemplate % (atomMode, bondMode))
for name, atomMode in [	("dot", chimera.Atom.Dot),
			("endcap (stick)", chimera.Atom.EndCap),
			("ball", chimera.Atom.Ball),
			("sphere", chimera.Atom.Sphere) ]:
	selMgr.addSelector(registrant, [dmSelCategory, dmAtomCategory, name],
					atomSelectorTemplate % atomMode)
for name, bondMode in [	("wire", chimera.Bond.Wire),
			("stick", chimera.Bond.Stick), ]:
	selMgr.addSelector(registrant, [dmSelCategory, dmBondCategory, name],
					bondSelectorTemplate % bondMode)
selMgr.makeCallbacks()
del name, atomMode, bondMode

