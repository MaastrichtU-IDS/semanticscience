# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v15.py 26655 2009-01-07 22:02:30Z gregc $

from v14 import reportRestoreError, restoreWindowSize, init, \
	restoreOpenModelsAttrs, RemapDialog, restoreLabels, \
	sessionID, registerAfterModelsCB, makeAfterModelsCBs, findFile, \
	idLookup, getColor, restoreVRML, restoreDrawModes, \
	restoreOpenStates, restoreColors, restoreVdw, \
	restoreDispChanged, restoreSelections, \
	restorePseudoBondGroups, restoreCamera, \
	noAutoRestore, autoRestorable, restoreModelClip, beginRestore, \
	endRestore, restoreSecondaryStructure, restoreMiscAttrs
# skip v14 restoreMolecules since that restores 1.1951 radii
from v7 import restoreMolecules

import globals # so that various version files can easily access same variables
import chimera

def restoreSurfaces(surfDisplayed, surfCategories, surfDict, surfOpacity):
	for surfDisp in surfDisplayed:
		idLookup(surfDisp).surfaceDisplay = 1
	for category, atList in surfCategories.items():
		for a in atList:
			idLookup(a).surfaceCategory = category
	for molID, attrs in surfDict.items():
		mol = idLookup(molID)
		surf = chimera.MSMSModel(mol, attrs['category'])
		del attrs['category']
		for attr, val in attrs.items():
			if attr == 'customColors':
				val = map(getColor, val)
			setattr(surf, attr, val)
		chimera.openModels.add([surf], sameAs=mol)
		from SimpleSession import modelMap
		modelMap.setdefault((mol.id, mol.subid), []).append(surf)

	for atomID, opacity in surfOpacity.items():
		atom = idLookup(atomID)
		atom.surfaceOpacity = opacity
