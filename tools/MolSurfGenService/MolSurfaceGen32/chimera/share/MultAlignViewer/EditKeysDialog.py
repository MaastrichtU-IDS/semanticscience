# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: EditKeysDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog
import Pmw, Tkinter

class EditKeysDialog(ModelessDialog):
	title = "Editing Keys"
	buttons = ('Close',)
	help = "ContributedSoftware/multalignviewer/multalignviewer.html#editkeys"

	def fillInUI(self, parent):
		Tkinter.Label(parent, text="Control Key + ...", bd=3,
			relief="ridge").grid(row=0, column=0, sticky="nsew")
		Tkinter.Label(parent, text="Function", bd=3,
			relief="ridge").grid(row=0, column=1, sticky="nsew")
		Tkinter.Label(parent, text="Notes", bd=3,
			relief="ridge").grid(row=0, column=2, sticky="nsew")
		Tkinter.Label(parent, text=u"\u2190 / \u2192", bd=3,
			relief="groove").grid(row=1, column=0, sticky="nsew")
		Tkinter.Label(parent, text="move current region one column"
				" left/right", bd=3, relief="groove"
				).grid( row=1, column=1, sticky="nsew")
		Tkinter.Label(parent, text="1", bd=3,
			relief="groove").grid(row=1, column=2, sticky="nsew")
		Tkinter.Label(parent, text=u"Shift + \u2190 / \u2192", bd=3,
			relief="groove").grid(row=2, column=0, sticky="nsew")
		Tkinter.Label(parent, text="move current region max left/right",
					bd=3, relief="groove").grid(
					row=2, column=1, sticky="nsew")
		Tkinter.Label(parent, text="1,2", bd=3,
			relief="groove").grid(row=2, column=2, sticky="nsew")
		Tkinter.Label(parent, text=u"\u2193", bd=3,
			relief="groove").grid(row=3, column=0, sticky="nsew")
		Tkinter.Label(parent, text="undo", bd=3, relief="groove").grid(
					row=3, column=1, sticky="nsew")
		Tkinter.Label(parent, text="3", bd=3,
			relief="groove").grid(row=3, column=2, sticky="nsew")
		Tkinter.Label(parent, text=u"\u2191", bd=3,
			relief="groove").grid(row=4, column=0, sticky="nsew")
		Tkinter.Label(parent, text="redo", bd=3, relief="groove").grid(
					row=4, column=1, sticky="nsew")
		Tkinter.Label(parent, text=" ", bd=3,
			relief="groove").grid(row=4, column=2, sticky="nsew")
		Tkinter.Label(parent, text=u"Escape", bd=3,
			relief="groove").grid(row=5, column=0, sticky="nsew")
		Tkinter.Label(parent, text="undo all", bd=3, relief="groove"
			).grid(row=5, column=1, sticky="nsew")
		Tkinter.Label(parent, text="3", bd=3,
			relief="groove").grid(row=5, column=2, sticky="nsew")

		Tkinter.Label(parent, text="[1] Must have all gaps in region's"
			" adjacent left/right column").grid(row=6, columnspan=3,
			sticky="w")
		Tkinter.Label(parent, text="[2] Motion stops when next column"
			" is not all gaps").grid(row=7, columnspan=3,
			sticky="w")
		Tkinter.Label(parent, text="[3] Can only undo edits listed"
			" above (e.g. not add/delete sequences)").grid(row=8,
			columnspan=3, sticky="w")
