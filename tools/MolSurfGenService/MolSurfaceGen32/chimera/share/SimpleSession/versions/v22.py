# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v22.py 26655 2009-01-07 22:02:30Z gregc $

from v20 import reportRestoreError, restoreWindowSize, init, \
	restoreOpenModelsAttrs, RemapDialog, \
	sessionID, registerAfterModelsCB, makeAfterModelsCBs, findFile, \
	idLookup, getColor, restoreVRML, restoreSurfaces, \
	restoreOpenStates, restoreColors, restoreVdw, restoreCamera, \
	restoreDispChanged, restoreSelections, restoreDrawModes, \
	restorePseudoBondGroups, \
	noAutoRestore, autoRestorable, beginRestore, \
	endRestore, restoreSecondaryStructure, restoreMiscAttrs

import globals # so that various version files can easily access same variables
import chimera

def restoreModelClip(clipInfo):
	for modelID, info in clipInfo.items():
		model = idLookup(modelID)
		originData, normalData, useThickness, thickness = info
		cp = model.clipPlane
		cp.origin = chimera.Point(*originData)
		cp.normal = chimera.Vector(*normalData)
		model.clipPlane = cp
		model.useClipPlane = True
		model.clipThickness = thickness
		model.useClipThickness = useThickness

def restoreLabels(labels):
	from chimera.bgprefs import BACKGROUND, LABEL_FONT
	from chimera import preferences
	preferences.getOption(BACKGROUND, LABEL_FONT).set(
						labels.pop('labelInfo'))
	for itemID, labelInfo in labels.items():
		item = idLookup(itemID)
		item.label = labelInfo

def restoreMolecules(srcMolInfo, defRadii, radiiExceptions):
	from tempfile import mktemp
	import os
	from SimpleSession import modelMap, modelOffset
	for mid, subid, name, fileContents in srcMolInfo:
		fname = mktemp()
		f = file(fname, "w")
		f.write(fileContents)
		f.close() # force a flush
		mols = chimera.openModels.open(fname, type="session PDB",
                        baseId=mid+modelOffset, subid=subid, identifyAs=name)
		os.unlink(fname)
			
		if mols:
			globals.atomIDs.update(mols[0].sessionIDs)
			delattr(mols[0], 'sessionIDs')
			modelMap.setdefault((mid, subid), []).extend(mols)


	for mList in modelMap.values():
		for m in mList:
			for a in m.atoms:
				try:
					a.radius = defRadii[a.idatmType]
				except KeyError:
					continue
	for aID, rad in radiiExceptions:
		idLookup(aID).radius = float(rad)
