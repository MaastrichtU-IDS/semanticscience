# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v6.py 27509 2009-05-05 22:13:18Z pett $

from v5 import init, beginRestore, endRestore, updateOSLmap, getOSL, \
	oslMap, registerAfterModelsCB, reportRestoreError, makeAfterModelsCBs, \
	findFile, oslLookup, restoreSurfaces, getColor, restoreMiscAttrs, \
	restoreWindowSize, restoreOpenStates, restoreLabels, restoreColors, \
	makeOslMappings, restoreVdw, restoreDrawModes, restoreDispChanged, \
	weedOSLlist, weedOSLdict, restoreSelections, restorePseudoBondGroups, \
	restoreOpenModelsAttrs, RemapDialog

def restoreCamera(detail, fogColor, viewerBG, viewerHL,
					viewerLB, viewerAttrs, cameraAttrs):
	import chimera
	chimera.LODControl.get().quality = detail
	def delay(fogColor=fogColor, viewerBG=viewerBG, viewerHL=viewerHL,
			viewerAttrs=viewerAttrs, cameraAttrs=cameraAttrs):
		viewer = chimera.tkgui.app.viewer
		viewer.depthCueColor = getColor(fogColor)
		viewer.background = getColor(viewerBG)
		viewer.highlightColor = getColor(viewerHL)
		import v1
		v1.fixViewerAttrs(viewerAttrs)
		for attr, val in viewerAttrs.items():
			if attr == "showBBox":
				# not strictly necessary, but cleaner
				continue
			try:
				setattr(viewer, attr, val)
			except ValueError:
				# ignore highlight errors
				if attr != 'highlight':
					raise
		camera = viewer.camera
		if hasattr(cameraAttrs, "near"):
			# session from before nearFar attribute
			cameraAttrs["nearFar"] = (cameraAttrs["near"],
							cameraAttrs["far"])
			del cameraAttrs["near"]
			del cameraAttrs["far"]
		for attr, val in cameraAttrs.items():
			setattr(camera, attr, val)
	chimera.tkgui.app.after_idle(delay)
