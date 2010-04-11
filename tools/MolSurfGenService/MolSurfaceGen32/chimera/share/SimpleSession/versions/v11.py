# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v11.py 29038 2009-10-13 18:45:06Z pett $

from v10 import reportRestoreError, restoreWindowSize, init, \
	restoreOpenModelsAttrs, RemapDialog, restoreLabels, \
	sessionID, registerAfterModelsCB, makeAfterModelsCBs, findFile, \
	idLookup, getColor, restoreMiscAttrs, restoreSurfaces, \
	restoreOpenStates, restoreColors, restoreVdw, \
	restoreDrawModes, restoreDispChanged, restoreSelections, \
	restorePseudoBondGroups, restoreCamera, restoreMolecules, \
	noAutoRestore, autoRestorable, restoreModelClip

import globals # so that various version files can easily access same variables
import chimera
from v10 import beginRestore as beginRestore_v10
from v10 import endRestore as endRestore_v10

def beginRestore():
	from SimpleSession import BEGIN_RESTORE_SESSION
	chimera.triggers.activateTrigger(BEGIN_RESTORE_SESSION, None)
	beginRestore_v10()

def endRestore():
	endRestore_v10()
	from SimpleSession import END_RESTORE_SESSION
	chimera.triggers.activateTrigger(END_RESTORE_SESSION, None)
	import SimpleSession
	del SimpleSession.mergedSession

def restoreSecondaryStructure(ssDict):
	for resID, assignments in ssDict.items():
		res = idLookup(resID)
		res.isHelix, res.isStrand, res.isTurn = assignments
