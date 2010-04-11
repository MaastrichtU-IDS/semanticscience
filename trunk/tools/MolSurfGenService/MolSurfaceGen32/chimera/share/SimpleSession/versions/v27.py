# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v27.py 26655 2009-01-07 22:02:30Z gregc $

from v26 import RemapDialog, reportRestoreError, restoreWindowSize, \
	restoreOpenModelsAttrs, noAutoRestore, autoRestorable, \
	registerAfterModelsCB, makeAfterModelsCBs, restoreModelClip, \
	restoreSelections, getColor, findFile, restoreMolecules, \
	sessionID, idLookup, expandSummary, init, restoreCamera, \
	beginRestore, endRestore, restoreColors, restoreSurfaces, restoreVRML, \
	restoreOpenStates, restoreFontInfo

import globals # so that various version files can easily access same variables
import chimera

def setSessionIDparams(molecules, residues, atoms, bonds, surfaces, vrmls,
								pseudobonds):
	# during session save, 'sessionMap' is item->index
	# during restore, index->item
	sessionMap = {}
	for i, item in enumerate(molecules+residues+atoms+bonds
						+surfaces+vrmls+pseudobonds):
		sessionMap[item] = i
	globals.sessionMap = sessionMap

def restorePseudoBondGroups(pbInfo):
	from chimera.misc import getPseudoBondGroup
	mgr = chimera.PseudoBondMgr.mgr()
	sm = globals.sessionMap
	for category, id, color, showStubBonds, lineWidth, stickScale, \
	wireStipple, bondInfo in zip(
				pbInfo['category'],
				pbInfo['id'],
				expandSummary(pbInfo['color']),
				expandSummary(pbInfo['showStubBonds']),
				expandSummary(pbInfo['lineWidth']),
				expandSummary(pbInfo['stickScale']),
				expandSummary(pbInfo['wireStipple']),
				pbInfo['bondInfo']
				):
		g = getPseudoBondGroup(category, id)
		g.color = getColor(color)
		g.showStubBonds = showStubBonds
		g.lineWidth = lineWidth
		g.stickScale = stickScale
		if wireStipple[0]:
			g.lineType = chimera.Dash
		for atoms, drawMode, display, halfbond, label, color, \
		labelColor in zip(
					bondInfo['atoms'],
					expandSummary(bondInfo['drawMode']),
					expandSummary(bondInfo['display']),
					expandSummary(bondInfo['halfbond']),
					expandSummary(bondInfo['label']),
					expandSummary(bondInfo['color']),
					expandSummary(bondInfo['labelColor'])
					):
			a1, a2 = [idLookup(a) for a in atoms]
			pb = g.newPseudoBond(a1, a2)
			pb.drawMode = drawMode
			pb.display = display
			pb.halfbond = halfbond
			pb.label = label
			pb.color = getColor(color)
			pb.labelColor = getColor(labelColor)
			sm[len(sm)] = pb
