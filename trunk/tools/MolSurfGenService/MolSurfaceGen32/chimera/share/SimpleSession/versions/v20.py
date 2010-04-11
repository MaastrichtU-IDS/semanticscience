# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v20.py 26655 2009-01-07 22:02:30Z gregc $

from v19 import reportRestoreError, restoreWindowSize, init, \
	restoreOpenModelsAttrs, RemapDialog, restoreLabels, \
	sessionID, registerAfterModelsCB, makeAfterModelsCBs, findFile, \
	idLookup, getColor, restoreVRML, restoreSurfaces, \
	restoreOpenStates, restoreColors, restoreVdw, restoreCamera, \
	restoreDispChanged, restoreSelections, restoreDrawModes, \
	restorePseudoBondGroups, \
	noAutoRestore, autoRestorable, restoreModelClip, beginRestore, \
	endRestore, restoreSecondaryStructure, restoreMiscAttrs
from v19 import restoreMolecules as v19restoreMolecules

import globals # so that various version files can easily access same variables
import chimera

def restoreMolecules(srcMolMap, defRadii, radiiExceptions):
	v19restoreMolecules(srcMolMap)

	from SimpleSession import modelMap
	for mList in modelMap.values():
		for m in mList:
			for a in m.atoms:
				try:
					a.radius = defRadii[a.idatmType]
				except KeyError:
					continue
	for aID, rad in radiiExceptions:
		idLookup(aID).radius = float(rad)
