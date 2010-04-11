# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: AssocInfoDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog
from OpenSave import SaveModeless
from chimera import replyobj
import Pmw, Tkinter
import os.path

class AssocInfoDialog(SaveModeless):
	"""Dialog to allow the user to save associated residue correspondence"""

	def __init__(self, mav):
		self.mav = mav
		self.title = "Save Association Info of %s" % mav.title
		defaultFile = os.path.splitext(self.mav.title or "alignment")[0]
		SaveModeless.__init__(self, clientPos='s',
					initialfile=defaultFile+".asc")

	def fillInUI(self, parent):
		SaveModeless.fillInUI(self, parent)
		from chimera.tkoptions import NamingStyleOption
		self.namingStyle = NamingStyleOption(self.clientArea, 0,
					"Residue naming style", "simple", None)
	def destroy(self):
		self.mav = None
		ModelessDialog.destroy(self)

	def Apply(self):
		if not self.getPaths():
			replyobj.error("No EPS save file specified.\n")
			self.enter()
			return
		self.mav.saveAssocInfo(self.getPaths()[0],
					namingStyle=self.namingStyle.get())
