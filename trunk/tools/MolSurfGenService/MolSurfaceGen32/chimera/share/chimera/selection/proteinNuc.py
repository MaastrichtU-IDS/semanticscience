# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: proteinNuc.py 26655 2009-01-07 22:02:30Z gregc $

from manager import selMgr

# register some protein/nucleic selectors
selectorTemplate = """\
from chimera.misc import principalAtom
selAdd = []
for mol in molecules:
        for res in mol.residues:
		pa = principalAtom(res)
                if pa and pa.name in %s:
                        selAdd.append(res)
sel.add(selAdd)
sel.addImplied(vertices=0)
"""
for name, pa in [("protein", ["CA"]), ("nucleic acid", ["C4'", "P"])]:
	selMgr.addSelector("protein/nucleic", [selMgr.STRUCTURE, name],
						selectorTemplate % (repr(pa),))
selMgr.makeCallbacks()
del name, pa

