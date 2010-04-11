# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v38.py 28951 2009-10-02 23:48:12Z goddard $

from v37 import RemapDialog, reportRestoreError, restoreWindowSize, \
	restoreOpenModelsAttrs, noAutoRestore, autoRestorable, \
	registerAfterModelsCB, makeAfterModelsCBs, restoreModelClip, \
	restoreSelections, getColor, findFile, restorePseudoBondGroups, \
	sessionID, idLookup, init, restoreCamera, endRestore, \
	beginRestore, endRestore, restoreColors, restoreVRML, \
	restoreOpenStates, restoreFontInfo, setSessionIDparams, \
	restoreMolecules, expandSummary, expandSequentialSummary, \
        restoreSurfaces

import globals # so that various version files can easily access same variables
import chimera

def checkVersion(releaseNum):
        from chimera import version
        if version.newer(releaseNum, version.releaseNum):
                msg = '''\
This session file was written by a newer version of Chimera (%s)
than you are currently running (%s).  Restoring it may fail or
produce errors during later operations.

Continue opening session?
''' % (version.buildVersion(releaseNum),
       version.buildVersion(version.releaseNum))
                from chimera import baseDialog, tkgui, CancelOperation
                dlg = baseDialog.AskYesNoDialog(msg, justify="left",
                                                default="No", help=False)
                if dlg.run(tkgui.app) == "no":
                        raise CancelOperation()

def restoreViewer(viewerInfo):
	import SimpleSession 
	if SimpleSession.preexistingModels:
		return	# Don't use session viewer/camera settings.
	vi = viewerInfo
	restoreCamera(vi['detail'], vi['viewerFog'], vi['viewerBG'],
		      vi['viewerHL'], vi['viewerLB'], vi['viewerAttrs'],
		      vi['cameraAttrs'], vi['cameraMode'])
