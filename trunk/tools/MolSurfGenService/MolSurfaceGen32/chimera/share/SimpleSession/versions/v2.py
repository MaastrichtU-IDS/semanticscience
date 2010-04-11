# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v2.py 26655 2009-01-07 22:02:30Z gregc $

from v1 import init, beginRestore, endRestore, updateOSLmap, getOSL, \
	oslMap, registerAfterModelsCB, reportRestoreError, makeAfterModelsCBs, \
	makeOslMappings, findFile, oslLookup, restoreSurfaces, getColor, \
	restoreColors, restoreWindowSize, restoreOpenStates, restoreLabels, \
	restoreVdw, restoreMiscAttrs, \
	restorePseudoBondGroups, weedOSLlist, weedOSLdict, restoreSelections, \
	restoreOpenModelsAttrs, restoreCamera, RemapDialog

def restoreDrawModes(reprDict):
	from chimera import Residue
	for item, style in weedOSLdict(reprDict).items():
		if isinstance(item, Residue):
			item.ribbonDrawMode = style
		else:
			item.drawMode = style

def restoreDispChanged(dispChanged):
	import chimera
	for dc in weedOSLlist(dispChanged):
		if isinstance(dc, chimera.Residue):
			dc.ribbonDisplay = 1 - dc.ribbonDisplay
		else:
			dc.display = 1 - dc.display

