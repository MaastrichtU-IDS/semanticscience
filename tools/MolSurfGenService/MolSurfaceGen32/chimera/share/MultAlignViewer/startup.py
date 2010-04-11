# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: startup.py 26655 2009-01-07 22:02:30Z gregc $

from parse import extensions
from MAViewer import MAViewer

_openDialog = None

def startExtension():
	filters = []
	fileTypes = extensions.keys()
	fileTypes.sort(lambda a, b: cmp(a.lower(), b.lower()))
	for fileType in fileTypes:
		exts = extensions[fileType]
		filters.append((fileType, map(lambda x: '*' + x, exts)))
	global _openDialog
	if not _openDialog:
		from OpenSave import OpenModeless
		_openDialog = OpenModeless(title="Open Sequence Alignment File",
		    help="ContributedSoftware/multalignviewer/framemav.html",
		    command=_openFile, filters=filters,
		    historyID="MultAlign open file")
	_openDialog.enter()

def _openFile(okayed, dialog):
	if not okayed:
		return

	for path, fileType in dialog.getPathsAndTypes():
		MAViewer(path, fileType)
