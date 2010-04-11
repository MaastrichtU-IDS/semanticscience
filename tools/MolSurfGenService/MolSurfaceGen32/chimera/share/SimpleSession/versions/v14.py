# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v14.py 26655 2009-01-07 22:02:30Z gregc $

from v13 import reportRestoreError, restoreWindowSize, init, \
	restoreOpenModelsAttrs, RemapDialog, restoreLabels, \
	sessionID, registerAfterModelsCB, makeAfterModelsCBs, findFile, \
	idLookup, getColor, restoreVRML, restoreMolecules, \
	restoreOpenStates, restoreColors, restoreVdw, \
	restoreDispChanged, restoreSelections, \
	restorePseudoBondGroups, restoreSurfaces, restoreCamera, \
	noAutoRestore, autoRestorable, restoreModelClip, beginRestore, \
	endRestore, restoreSecondaryStructure, restoreMiscAttrs

import globals # so that various version files can easily access same variables
import chimera

def restoreDrawModes(reprDict, xSections, ribScalings):
	from chimera import Residue
	crossSections = []
	for outline, a1, a2, a3 in xSections:
		cx = chimera.RibbonXSection(a1, a2, a3)
		cx.outline = outline
		crossSections.append(cx)
	for itemID, style in reprDict.items():
		item = idLookup(itemID)
		if isinstance(item, Residue):
			style, xsi = style
			item.ribbonDrawMode = style
			if xsi is not None:
				item.ribbonXSection = crossSections[xsi]
				
		else:
			if item is None:
				print itemID, map(lambda i: globals.atomIDs[i].oslIdent(), itemID[1])
			item.drawMode = style
	scalings = map(chimera.Residue.getDefaultRibbonStyle, [
		chimera.Residue.RS_TURN, chimera.Residue.RS_HELIX,
		chimera.Residue.RS_SHEET, chimera.Residue.RS_ARROW,
		chimera.Residue.RS_NUCLEIC])
	for i, rs in enumerate(scalings):
		width, thickness = ribScalings[i]
		if i == 3:
			arrowSW, arrowST = width, thickness
			continue
		rs.size = [width, thickness]
	# arrow has two sets...
	arrowEW, arrowET = ribScalings[-1]
	arrow = scalings[3]
	arrow.size = [arrowSW, arrowST, arrowEW, arrowET]
