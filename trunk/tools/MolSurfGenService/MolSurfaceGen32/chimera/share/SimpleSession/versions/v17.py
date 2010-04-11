# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v17.py 27509 2009-05-05 22:13:18Z pett $

from v16 import reportRestoreError, restoreWindowSize, init, \
	restoreOpenModelsAttrs, RemapDialog, restoreLabels, \
	sessionID, registerAfterModelsCB, makeAfterModelsCBs, findFile, \
	idLookup, getColor, restoreVRML, restoreSurfaces, \
	restoreOpenStates, restoreColors, restoreVdw, \
	restoreDispChanged, restoreSelections, \
	restorePseudoBondGroups, restoreMolecules, \
	noAutoRestore, autoRestorable, restoreModelClip, beginRestore, \
	endRestore, restoreSecondaryStructure, restoreMiscAttrs

import globals # so that various version files can easily access same variables
import chimera

def restoreDrawModes(reprDict):
	from chimera import Residue
	for itemID, info in reprDict.items():
		item = idLookup(itemID)
		if isinstance(item, Residue):
			item.ribbonDrawMode = info
		else:
			item.drawMode = info

def restoreCamera(detail, fogColor, viewerBG, viewerHL,
					viewerLB, viewerAttrs, cameraAttrs):
	import chimera
	chimera.LODControl.get().quality = detail
	# globals.colorMap is deleted by end of session so look up colors now
	fogColor = getColor(fogColor)
	viewerBG = getColor(viewerBG)
	viewerHL = getColor(viewerHL)
	def delay(arg1, arg2, arg3, fogColor=fogColor, viewerBG=viewerBG,
			viewerHL=viewerHL,
			viewerAttrs=viewerAttrs, cameraAttrs=cameraAttrs):
		viewer = chimera.tkgui.app.viewer
		viewer.depthCueColor = fogColor
		viewer.background = viewerBG
		viewer.highlightColor = viewerHL
		import v1
		v1.fixViewerAttrs(viewerAttrs)
		for attr, val in viewerAttrs.items():
			try:
				setattr(viewer, attr, val)
			except ValueError:
				# ignore highlight errors
				if attr != 'highlight':
					raise
		camera = viewer.camera
		for attr, val in cameraAttrs.items():
			setattr(camera, attr, val)
		camera.fieldOfView = 25
		from chimera.triggerSet import ONESHOT
		return ONESHOT
	from SimpleSession import END_RESTORE_SESSION
	chimera.triggers.addHandler(END_RESTORE_SESSION, delay, None)
