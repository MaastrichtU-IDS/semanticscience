# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: HBondDialog.py 26655 2009-01-07 22:02:30Z gregc $


from chimera.baseDialog import ModelessDialog
import Pmw, Tkinter
from Compound import Compound

class HBondDialog(ModelessDialog):
	
	title = "ViewDock HBond Filter"
	help = "ContributedSoftware/viewdock/viewdock.html#hbfilt"

	def __init__(self, callback, *args, **kw):
		self.callback = callback
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		f = Tkinter.Frame(parent)
		f.grid(row=0, column=0, sticky="w")
		self.actionOption = Pmw.OptionMenu(f, 
			initialitem="deleted", items=["viable", "deleted",
			"purged"], labelpos="w", label_text="Mark as")
		self.actionOption.grid(row=0, column=0)

		Tkinter.Label(f, text="compounds without:").grid(row=0,
							column=1)

		self.filterVar = Tkinter.IntVar(parent)
		self.filterVar.set(1)

		f = Tkinter.Frame(parent)
		f.grid(row=1, column=0, sticky="w")
		Tkinter.Radiobutton(f, text="hydrogen bonds to", value=0,
				variable=self.filterVar).grid(row=0, column=0)
		self.criteriaOption = Pmw.OptionMenu(f, initialitem="all",
			items=["all", "any"], labelpos="e",
			label_text="selected receptor heteroatoms")
		self.criteriaOption.grid(row=0, column=1)

		f = Tkinter.Frame(parent)
		f.grid(row=2, column=0, sticky="w")
		Tkinter.Radiobutton(f, value=1, variable=self.filterVar).grid(
								row=0, column=0)
		self.amountOption = Pmw.EntryField(f, labelpos='e',
			label_text="or more hydrogen bonds to receptor",
			entry_width=2, entry_justify='center',
			validate='numeric', value="2")
		self.amountOption.grid(row=0, column=1)

	def Apply(self):
		actionChoice = self.actionOption.getcurselection()
		if actionChoice == "viable":
			action = Compound.Viable
		elif actionChoice == "deleted":
			action = Compound.Deleted
		else:
			action = Compound.Purged

		if self.filterVar.get() == 0:
			filterType = "quality"
			arg = self.criteriaOption.getcurselection()
		else:
			filterType = "quantity"
			if self.amountOption.valid():
				self.amountOption.invoke()
				arg = int(self.amountOption.get())
			else:
				replyobj.error("You must specify an integer "
						"number of hydrogen bonds as "
						"filtering criteria\n")
				return
		self.callback(filterType, action, arg)
