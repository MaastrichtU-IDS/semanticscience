# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v30.py 28949 2009-10-02 23:47:48Z goddard $

from v29 import RemapDialog, reportRestoreError, restoreWindowSize, \
	restoreOpenModelsAttrs, noAutoRestore, autoRestorable, \
	registerAfterModelsCB, makeAfterModelsCBs, restoreModelClip, \
	restoreSelections, getColor, findFile, restorePseudoBondGroups, \
	sessionID, idLookup, init, restoreCamera, \
	beginRestore, endRestore, restoreColors, restoreSurfaces, restoreVRML, \
	restoreOpenStates, restoreFontInfo, setSessionIDparams, \
	restoreMolecules, expandSequentialSummary, expandSummary

import chimera

def restoreWindowSize((width, height)):
	import SimpleSession
	if SimpleSession.preexistingModels:
		return	# Leave window size as is.
	import Midas
	Midas.windowsize((width, height))
