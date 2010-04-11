# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera import replyobj
from chimera.baseDialog import ModelessDialog
import Tkinter, Pmw
from OpenSave import OpenModeless
from AddAttr import addAttributes

class AddAttrDialog(OpenModeless):
	title = "Define Attribute"
	provideStatus = True
	name = "add/change attrs"
	help = "ContributedSoftware/defineattrib/defineattrib.html"

	def __init__(self):
		OpenModeless.__init__(self, clientPos='s', clientSticky='nsew',
			historyID="AddAttr")

	def Apply(self):
		mols = self.molListBox.getvalue()
		if not mols:
			self.enter()
			replyobj.error("No models chosen in dialog\n")
			return
		for path in self.getPaths():
			setAttrs = addAttributes(path, models=mols,
					log=self.doLog.get(),
					raiseAttrDialog=self.openDialog.get())
			if setAttrs == []:
				replyobj.error("No attributes were set from"
					" file %s\n" % path)

	def fillInUI(self, parent):
		OpenModeless.fillInUI(self, parent)
		from chimera.widgets import MoleculeScrolledListBox
		self.molListBox = MoleculeScrolledListBox(self.clientArea,
				listbox_selectmode="extended",
				labelpos="w", label_text="Restrict to models:")
		self.molListBox.grid(row=0, column=0, sticky="nsew")
		self.clientArea.rowconfigure(0, weight=1)
		self.clientArea.columnconfigure(0, weight=1)

		checkButtonFrame = Tkinter.Frame(self.clientArea)
		checkButtonFrame.grid(row=1, column=0)

		self.openDialog = Tkinter.IntVar(parent)
		self.openDialog.set(True)
		Tkinter.Checkbutton(checkButtonFrame, variable=self.openDialog,
			text="Open Render/Select by Attribute").grid(
			row=0, column=0, sticky='w')

		self.doLog = Tkinter.IntVar(parent)
		self.doLog.set(False)
		Tkinter.Checkbutton(checkButtonFrame,
			text="Send match info to Reply Log",
			variable=self.doLog).grid(row=1, column=0, sticky='w')

from chimera import dialogs
dialogs.register(AddAttrDialog.name, AddAttrDialog)
