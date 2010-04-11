# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: LoadHeaderDialog.py 29125 2009-10-22 23:49:08Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from OpenSave import OpenModeless
from chimera import replyobj

class LoadHeaderDialog(OpenModeless):
	"""Dialog to load custom header lines"""

	def __init__(self, mav):
		self.mav = mav
		self.title = "Load Header Line for %s" % mav.title
		OpenModeless.__init__(self, historyID="mav header")

	def destroy(self):
		self.mav = None
		ModelessDialog.destroy(self)

	def Apply(self):
		if not self.getPaths():
			replyobj.error("No file specified.\n")
			self.enter()
			return
		for path in self.getPaths():
			self.mav.readHeaderFile(path)
