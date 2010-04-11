# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v38.py,v 1.1 2008-11-11 01:04:35 goddard Exp $

from v40 import RemapDialog, reportRestoreError, restoreWindowSize, \
	restoreOpenModelsAttrs, noAutoRestore, autoRestorable, \
	registerAfterModelsCB, makeAfterModelsCBs, restoreModelClip, \
	restoreSelections, getColor, findFile, restorePseudoBondGroups, \
	sessionID, idLookup, init, restoreCamera, endRestore, \
	beginRestore, endRestore, restoreColors, restoreVRML, \
	restoreOpenStates, restoreFontInfo, setSessionIDparams, \
	restoreMolecules, expandSummary, expandSequentialSummary, \
        checkVersion, restoreModelAssociations, restoreSurfaces

import globals # so that various version files can easily access same variables
import chimera

def restoreViewer(viewerInfo):
	import SimpleSession 
	if SimpleSession.preexistingModels:
		return	# Don't use session viewer/camera settings.
	vi = viewerInfo
	restoreCamera(vi['detail'], vi['viewerFog'], vi['viewerBG'],
		      vi['viewerHL'], vi['viewerAttrs'],
		      vi['cameraAttrs'], vi['cameraMode'])

def restoreCamera(detail, fogColor, viewerBG, viewerHL,
					viewerAttrs, cameraAttrs, cameraMode):
	import chimera
	chimera.LODControl.get().quality = detail
	# globals.colorMap is deleted by end of session so look up colors now
	fogColor = getColor(fogColor)
	viewerBG = getColor(viewerBG)
	viewerHL = getColor(viewerHL)
	for va, val in viewerAttrs.items():
		if va.endswith("Color"):
			viewerAttrs[va] = getColor(val)
	def delay(arg1, arg2, arg3, fogColor=fogColor, viewerBG=viewerBG,
			viewerHL=viewerHL, viewerAttrs=viewerAttrs,
			cameraAttrs=cameraAttrs):
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
		# can't reliably transit to/from stereo...
		if not chimera.stereo and cameraMode != "sequential stereo":
			camera.setMode(cameraMode, viewer)
		from chimera.triggerSet import ONESHOT
		return ONESHOT
	from SimpleSession import END_RESTORE_SESSION
	chimera.triggers.addHandler(END_RESTORE_SESSION, delay, None)
