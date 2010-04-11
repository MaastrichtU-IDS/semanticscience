# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: idatm.py 26655 2009-01-07 22:02:30Z gregc $

from bondGeom import tetrahedral, planar, linear, single, geometryName
import chimera

typeInfo = chimera.Atom.getIdatmInfoMap()

registrant = "idatm"
selCategory = 'IDATM type'
try:
	import chimera
	from chimera.selection.manager import selMgr
except ImportError:
	pass
else:
	for idatmType in typeInfo.keys():
		selectorText = """\
selAdd = []
for mol in molecules:
        for atom in mol.atoms:
		if atom.idatmType == '%s':
			selAdd.append(atom)
sel.add(selAdd)
""" % (idatmType,)
		selMgr.addSelector(registrant, [selMgr.CHEMISTRY, selCategory,
			idatmType], selectorText,
			description=typeInfo[idatmType].description)
	selMgr.makeCallbacks()

	del idatmType, selectorText, selMgr
