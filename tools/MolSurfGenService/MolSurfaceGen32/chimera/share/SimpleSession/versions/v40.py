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

from v39 import RemapDialog, reportRestoreError, restoreWindowSize, \
	restoreOpenModelsAttrs, noAutoRestore, autoRestorable, \
	registerAfterModelsCB, makeAfterModelsCBs, restoreModelClip, \
	restoreSelections, getColor, findFile, restorePseudoBondGroups, \
	sessionID, idLookup, init, restoreCamera, endRestore, \
	beginRestore, endRestore, restoreColors, restoreVRML, \
	restoreOpenStates, restoreFontInfo, setSessionIDparams, \
	restoreMolecules, expandSummary, expandSequentialSummary, \
        checkVersion, restoreViewer, restoreModelAssociations

import globals # so that various version files can easily access same variables
import chimera

def restoreSurfaces(surfInfo):
	sm = globals.sessionMap
        si = {}
        for n in ('molecule', 'name', 'customColors'):
            si[n] = surfInfo[n]
        for n in ('category', 'colorMode', 'density', 'drawMode',
                  'display', 'probeRadius', 'allComponents',
                  'lineWidth', 'pointSize', 'useLighting',
                  'twoSidedLighting', 'smoothLines',
                  'transparencyBlendMode', 'oneTransparentLayer'):
            si[n] = expandSummary(surfInfo[n])
        for i, mid in enumerate(si['molecule']):
		mol = idLookup(mid)
		s = chimera.MSMSModel(mol, si['category'][i],
                                      probeRadius = si['probeRadius'][i],
                                      allComponents = si['allComponents'][i],
                                      vertexDensity = si['density'][i])
		chimera.openModels.add([s], sameAs=mol)
                for n in ('name', 'colorMode', 'drawMode', 'display',
                          'lineWidth', 'pointSize', 'useLighting',
                          'twoSidedLighting', 'smoothLines',
                          'transparencyBlendMode', 'oneTransparentLayer'):
                    setattr(s, n, si[n][i])
		customColors = expandSummary(si['customColors'][i])
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
				s.colorMode = si['colorMode'][i]
		sm[len(sm)] = s
		from SimpleSession import modelMap
		modelMap.setdefault((mol.id, mol.subid), []).append(s)
