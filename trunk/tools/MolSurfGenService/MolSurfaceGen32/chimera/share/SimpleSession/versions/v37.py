# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v37.py 26655 2009-01-07 22:02:30Z gregc $

from v36 import RemapDialog, reportRestoreError, restoreWindowSize, \
	restoreOpenModelsAttrs, noAutoRestore, autoRestorable, \
	registerAfterModelsCB, makeAfterModelsCBs, restoreModelClip, \
	restoreSelections, getColor, findFile, restorePseudoBondGroups, \
	sessionID, idLookup, init, restoreCamera, endRestore, \
	beginRestore, endRestore, restoreColors, restoreVRML, \
	restoreOpenStates, restoreFontInfo, setSessionIDparams, \
	restoreMolecules, expandSummary, expandSequentialSummary

import globals # so that various version files can easily access same variables
import chimera

def restoreSurfaces(surfInfo):
	sm = globals.sessionMap
	for mid, category, colorMode, density, name, drawMode, display, \
	probeRadius, customColorsSummary, allComponents in zip(
					surfInfo['molecule'],
					expandSummary(surfInfo['category']),
					expandSummary(surfInfo['colorMode']),
					expandSummary(surfInfo['density']),
					surfInfo['name'],
					expandSummary(surfInfo['drawMode']),
					expandSummary(surfInfo['display']),
					expandSummary(surfInfo['probeRadius']),
					surfInfo['customColors'],
					expandSummary(surfInfo['allComponents'])
					):
		mol = idLookup(mid)
		s = chimera.MSMSModel(mol, category,
					allComponents=allComponents)
		chimera.openModels.add([s], sameAs=mol)
		s.colorMode = colorMode
		s.density = density
		s.name = name
		s.drawMode = drawMode
		s.display = display
		s.probeRadius = probeRadius
		customColors = expandSummary(customColorsSummary)
		if customColors:
			if len(customColors) != len(s.triangleData()[0]):
				from chimera import replyobj
				replyobj.error("Number of surface vertices for %s (%s) differs from number of colors.\nCustom color scheme not restored\n" % (mol.oslIdent(), category))
				s.colorMode = chimera.MSMSModel.ByAtom
			else:
				s.customColors = [getColor(c)
							for c in customColors]
				# setting custom colors seems to implicitly
				# set the color mode...
				s.colorMode = colorMode
		sm[len(sm)] = s
		from SimpleSession import modelMap
		modelMap.setdefault((mol.id, mol.subid), []).append(s)
