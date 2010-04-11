# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v19.py 26655 2009-01-07 22:02:30Z gregc $

from v18 import reportRestoreError, restoreWindowSize, init, \
	restoreOpenModelsAttrs, RemapDialog, restoreLabels, \
	sessionID, registerAfterModelsCB, makeAfterModelsCBs, findFile, \
	idLookup, getColor, restoreVRML, \
	restoreOpenStates, restoreColors, restoreVdw, restoreCamera, \
	restoreDispChanged, restoreSelections, restoreDrawModes, \
	restorePseudoBondGroups, restoreMolecules, \
	noAutoRestore, autoRestorable, restoreModelClip, beginRestore, \
	endRestore, restoreSecondaryStructure, restoreMiscAttrs

import globals # so that various version files can easily access same variables
import chimera

def restoreSurfaces(surfDisplayed, surfCategories, surfDict, surfOpacity):
	for surfDisp in surfDisplayed:
		idLookup(surfDisp).surfaceDisplay = 1
	for category, atList in surfCategories.items():
		for a in atList:
			idLookup(a).surfaceCategory = category
	for surfID, attrs in surfDict.items():
		molID, category = surfID
		mol = idLookup(molID)
		surf = chimera.MSMSModel(mol, category)
		badCustom = False
		for attr, val in attrs.items():
			if attr == 'customColors':
				val = map(getColor, val)
				if len(val) != len(surf.triangleData()[0]):
					from chimera import replyobj 
					replyobj.error("Number of surface vertices for %s (%s) differs from number of colors.\nCustom color scheme not restored\n" % (mol.oslIdent(), category))
					badCustom = True
					continue
			setattr(surf, attr, val)
		if badCustom:
			surf.colorMode = chimera.MSMSModel.ByAtom
		chimera.openModels.add([surf], sameAs=mol)
		from SimpleSession import modelMap
		modelMap.setdefault((mol.id, mol.subid), []).append(surf)

	for atomID, opacity in surfOpacity.items():
		atom = idLookup(atomID)
		atom.surfaceOpacity = opacity

