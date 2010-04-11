# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ss.py 26655 2009-01-07 22:02:30Z gregc $

from manager import selMgr

# register some element type selectors
ssSelCategory = "secondary structure"
selectorTemplate = """\
selAdd = []
for mol in molecules:
        for res in mol.residues:
                if res.is%s:
                        selAdd.append(res)
sel.add(selAdd)
sel.addImplied(vertices=0)
"""
for ssType in ["helix", "turn", "strand"]:
	selMgr.addSelector("secondary structure", [selMgr.STRUCTURE,
				ssSelCategory, ssType],
				selectorTemplate % (ssType.capitalize(),))
selMgr.makeCallbacks()
del ssType

