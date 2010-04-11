# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v9.py 26655 2009-01-07 22:02:30Z gregc $

from v8 import reportRestoreError, restoreWindowSize, init, \
	restoreOpenModelsAttrs, RemapDialog, beginRestore, endRestore, \
	sessionID, registerAfterModelsCB, makeAfterModelsCBs, findFile, \
	idLookup, getColor, restoreMiscAttrs, \
	restoreOpenStates, restoreLabels, restoreColors, restoreVdw, \
	restoreDrawModes, restoreDispChanged, restoreSelections, \
	restorePseudoBondGroups, restoreCamera, restoreMolecules, \
	noAutoRestore, autoRestorable

import globals # so that various version files can easily access same variables
import chimera

from v8 import restoreSurfaces as v8restoreSurfaces

def restoreSurfaces(surfDisplayed, surfCategories, surfDict, surfOpacity):
	v8restoreSurfaces(surfDisplayed, surfCategories, surfDict)
	for atomID, opacity in surfOpacity.items():
		atom = idLookup(atomID)
		atom.surfaceOpacity = opacity

def restoreModelClip(clipInfo):
	for modelID, info in clipInfo.items():
		model = idLookup(modelID)
		originData, normalData = info
		cp = model.clipPlane
		cp.origin = chimera.Point(*originData)
		cp.normal = chimera.Vector(*normalData)
		model.clipPlane = cp
		model.useClipPlane = True


