# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: noteDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog

class RenameDialog(ModelessDialog):
	oneshot = True
	title = "Rename Model"
	buttons = ("OK", "Cancel")
	default = "OK"

	def __init__(self, model):
		self.model = model
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		import Tkinter
		Tkinter.Label(parent, text="Rename %s to:" % self.model.name
						).grid(row=0, sticky='w')
		self.nameVar = Tkinter.StringVar(parent)
		self.nameVar.set(self.model.name)
		entry = Tkinter.Entry(parent, exportselection=False,
						textvariable=self.nameVar)
		entry.focus_set()
		entry.selection_range(0, Tkinter.END)
		entry.icursor(Tkinter.END)
		entry.grid(row=1, sticky='ew')

	def Apply(self):
		if self.model.__destroyed__:
			return
		self.model.name = self.nameVar.get()
