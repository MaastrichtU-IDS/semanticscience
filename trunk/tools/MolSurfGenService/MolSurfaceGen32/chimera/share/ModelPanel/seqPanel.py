# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: seqPanel.py 28051 2009-07-09 20:25:53Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
import Tkinter
import Pmw

class SeqPickerDialog(ModelessDialog):
	title = 'Show Model Sequence'
	buttons = ('Show', 'Close')
	default = 'Show'
	keepShown = 'Show'
	name = "model sequence chooser"
	help = "ContributedSoftware/multalignviewer/multalignviewer.html#individual"

	def fillInUI(self, parent):
		from chimera.widgets import MoleculeChainScrolledListBox
		self.molListBox = MoleculeChainScrolledListBox(parent,
			listbox_selectmode="extended", labelpos="w",
			# some fancy footwork so that double click honors
			# the "keep shown" dialog setting
			dblclickcommand=lambda *args: getattr(self, 'Show')(),
			label_text="Show sequence for:")
		self.molListBox.grid(row=0, column=0, sticky="news")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)

	def Apply(self):
		from base import seqCmd
		seqCmd(self.molListBox.getvalue())
		
from chimera import dialogs
dialogs.register(SeqPickerDialog.name, SeqPickerDialog)
