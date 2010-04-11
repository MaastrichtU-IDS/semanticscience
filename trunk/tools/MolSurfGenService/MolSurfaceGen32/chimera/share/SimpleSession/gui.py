# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 27719 2009-06-01 23:18:11Z pett $

from OpenSave import SaveModeless, OpenModeless
from save import saveSession
from chimera import replyobj, dialogs
import chimera

def _saveCB(okayed, dialog):
	if not okayed:
		return
	paths = dialog.getPaths()
	if not paths:
		replyobj.warning("No save file selected; aborting save.\n")
		return
	saveSession(paths[0])
	chimera.setLastSession(paths[0])

class SaveSessionDialog(SaveModeless):
	name = "Save Session"
	title = "Choose Session Save File"

	def __init__(self):
		SaveModeless.__init__(self, command=_saveCB,
				filters=[("Chimera session", ["*.py"], ".py")],
				historyID="SimpleSession", compressed=True)
dialogs.register(SaveSessionDialog.name, SaveSessionDialog)

def _openCB(okayed, dialog):
	if not okayed:
		return
	for path in dialog.getPaths():
		chimera.openModels.open(path, type="Python")
		chimera.setLastSession(path)

class OpenSessionDialog(OpenModeless):
	name = "Open Session"
	title = "Choose Previously Saved Chimera Session File"

	def __init__(self):
		OpenModeless.__init__(self, command=_openCB,
				filters=[("Chimera session", ["*.py"])],
				defaultFilter="Chimera session", addAll=False,
				historyID="SimpleSession")
dialogs.register(OpenSessionDialog.name, OpenSessionDialog)
