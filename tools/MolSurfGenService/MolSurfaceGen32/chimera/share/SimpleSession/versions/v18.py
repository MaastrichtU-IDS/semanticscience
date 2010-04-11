# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v18.py 26655 2009-01-07 22:02:30Z gregc $

from v17 import reportRestoreError, restoreWindowSize, init, \
	restoreOpenModelsAttrs, RemapDialog, restoreLabels, \
	sessionID, registerAfterModelsCB, makeAfterModelsCBs, findFile, \
	idLookup, getColor, restoreSurfaces, \
	restoreOpenStates, restoreColors, restoreVdw, restoreCamera, \
	restoreDispChanged, restoreSelections, restoreDrawModes, \
	restorePseudoBondGroups, restoreMolecules, \
	noAutoRestore, autoRestorable, restoreModelClip, beginRestore, \
	endRestore, restoreSecondaryStructure, restoreMiscAttrs

import globals # so that various version files can easily access same variables
import chimera

def restoreVRML(info):
        from SimpleSession import modelOffset
	for idInfo, vrmlString in info.items():
		id, subid, name, display = idInfo
		from SimpleSession import modelMap
		if (id, subid) in modelMap:
			model = modelMap[(id, subid)][0]
			mapId, mapSubid = model.id, model.subid
		else:
			mapId, mapSubid = id+modelOffset, subid
		vrmlModels = chimera.openModels.open(vrmlString, type="VRML",
				baseId=mapId, subid=mapSubid, identifyAs=name)
		for vrml in vrmlModels:
			vrml.display = display
		modelMap.setdefault((id, subid), []).extend(vrmlModels)
