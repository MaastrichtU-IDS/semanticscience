# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: element.py 26655 2009-01-07 22:02:30Z gregc $

from manager import selMgr

# register some element type selectors
elementSelCategory = "element"
frequentElements = [ "C", "O", "N", "H", "P", "S" ]
elementRanges = [
  ("Ac", "Ba"), ("Be", "Cl"), ("Cm", "F"), ("Fe", "Hg"), ("Ho", "Lu"),
  ("Md", "Ni"), ("No", "Po"), ("Pr", "S"), ("Sb", "Tc"), ("Te", "Zr")
]
selectorTemplate = """\
selAdd = []
for mol in molecules:
        for atom in mol.atoms:
                if atom.element.name == '%s':
                        selAdd.append(atom)
sel.add(selAdd)
"""
from chimera import elements
for element in frequentElements:
	selMgr.addSelector("element",
			[selMgr.CHEMISTRY, elementSelCategory, element],
			selectorTemplate % (element,))
for element in elements.name:
	if element == "LP":
		# ignore lone pair "element"
		continue
	for range in elementRanges:
		if element < range[0] or element > range[1]:
			continue
		selMgr.addSelector("element", [selMgr.CHEMISTRY,
			elementSelCategory, "other", "%s-%s" % range, element],
			selectorTemplate % (element,))
		break
selMgr.makeCallbacks()
del element, range

