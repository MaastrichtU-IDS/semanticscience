# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 26655 2009-01-07 22:02:30Z gregc $

from OpenSave import SaveModeless
from chimera import replyobj, preferences, selection, openModels, MSMSModel

class WriteDmsDialog(SaveModeless):
	help = "UsersGuide/dms.html#writedms"
	oneshot = True

	def __init__(self):
		SaveModeless.__init__(self, clientPos='s', clientSticky='ewns',
			filters=[("DMS", "*.dms", ".dms")])

	def fillInUI(self, parent):
		import Pmw, Tkinter
		SaveModeless.fillInUI(self, parent)
		self.clientArea.columnconfigure(0, weight=1)

		row = 0

		from chimera.widgets import ModelOptionMenu
		self.surfList = ModelOptionMenu(self.clientArea,
			labelpos='w', label_text="Save surface:",
			filtFunc=lambda m: isinstance(m, MSMSModel))
		self.surfList.grid(row=row, column=0)
		row += 1

		self.saveNormalsVar = Tkinter.IntVar(self.clientArea)
		self.saveNormalsVar.set(True)
		Tkinter.Checkbutton(self.clientArea, text="Save normals",
			variable=self.saveNormalsVar).grid(row=row)
		row += 1

		self.displayedOnlyVar = Tkinter.IntVar(self.clientArea)
		self.displayedOnlyVar.set(True)
		Tkinter.Checkbutton(self.clientArea, text="Limit output to"
			" displayed surface sections",
			variable=self.displayedOnlyVar).grid(row=row)
		row += 1

	def Apply(self):
		path = self.getPaths()[0]
		surf = self.surfList.getvalue()
		if not surf:
			replyobj.error("No surface chosen to save.\n")
			return
		from WriteDMS import writeDMS
		replyobj.status("Writing DMS surface to %s\n" % path)
		writeDMS(surf, path, writeNormals=self.saveNormalsVar.get(),
			displayedOnly=self.displayedOnlyVar.get())
		replyobj.status("Wrote DMS surface to %s\n" % path)
