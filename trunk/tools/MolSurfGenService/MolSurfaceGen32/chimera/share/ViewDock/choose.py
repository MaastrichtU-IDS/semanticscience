# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import base

Filters = [
	("Dock 4, 5 or 6", ["*.pdb", "*.mol2"]),
	("Dock 3.5.x search", ["*.pdb"]),
	("Dock 3.5.x single", ["*.pdb"]),
	("Dock 3 or 3.5", ["*.pdb"]),
	("Mordor", ["*.ind"]),
]

def ViewDockCB():
	from OpenSave import OpenModeless
	OpenModeless(command=_openVDCB, title="Open Dock Results",
		filters=Filters, dialogKw={'oneshot': 1}, historyID="ViewDock")

def _openVDCB(okayed, dialog):
	if not okayed:
		return
	for path, type in dialog.getPathsAndTypes():
		base.ViewDock(path, type)

def HearDockCB():
	from OpenSave import OpenModeless
	OpenModeless(command=_openHDCB, title="Open Dock Results",
		filters=Filters, dialogKw={'oneshot': 1}, historyID="ViewDock")

def _openHDCB(okayed, dialog):
	if not okayed:
		return
	for path, type in dialog.getPathsAndTypes():
		base.HearDock(path, type)
