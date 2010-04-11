# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 26839 2009-01-30 20:55:16Z pett $

from chimera.baseDialog import ModelessDialog
from chimera import openModels

class CombineDialog(ModelessDialog):
	title = "Copy/Combine Molecular Models"
	help = "UsersGuide/modelpanel.html#combine"

	def __init__(self, models=None):
		self.initModels = models
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		from chimera.widgets import MoleculeScrolledListBox
		self.molListBox = MoleculeScrolledListBox(parent,
			listbox_selectmode='extended', labelpos='w',
			label_text="Molecules to combine/copy:")
		if self.initModels:
			self.molListBox.setvalue(self.initModels)
		self.molListBox.grid(row=0, column=0, columnspan=2,
							sticky="nsew")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(1, weight=1)
		from chimera.tkoptions import StringOption, IntOption
		self.molNameEntry = StringOption(parent, 1, "New model's"
						" name", "combination", None)

		curIDs = set([i1 for i1, i2 in openModels.listIds()])
		mid = 0
		while mid in curIDs:
			mid += 1
		self.modelID = IntOption(parent, 2, "New model's ID", mid, None)

		from chimera.widgets import MoleculeOptionMenu
		self.refMolMenu = MoleculeOptionMenu(parent, labelpos='w',
			label_text="Coordinate system of:",
			initialitem=self.initModels[0])
		self.refMolMenu.grid(row=3, column=0, columnspan=2, sticky='w')

		import Pmw
		chb = self.chainHandlingButtons = Pmw.RadioSelect(parent,
			buttontype="radiobutton", labelpos='w',
			label_text="If original molecules have duplicate\n"
			"single-letter chain IDs, then:", orient="vertical")
		self.buttonTexts = ["rename them uniquely",
				"retain them (residues may be renumbered)"]
		for bt in self.buttonTexts:
			chb.add(bt)
		chb.setvalue(self.buttonTexts[0])
		chb.grid(row=4, column=0, columnspan=2)

		import Tkinter
		self.closeModelsVar = Tkinter.IntVar(parent)
		self.closeModelsVar.set(False)
		Tkinter.Checkbutton(parent, text="Close source models",
					variable=self.closeModelsVar).grid(
					row=5, column=0, columnspan=2)
			

	def Apply(self):
		mols = self.molListBox.getvalue()
		from chimera import UserError
		if not mols:
			self.enter()
			raise UserError("Must specify at least one molecular"
				" model to combine/copy")
		from chimera import suppressNewMoleculeProcessing, \
						restoreNewMoleculeProcessing
		suppressNewMoleculeProcessing()
		newChainIDs = (self.chainHandlingButtons.getvalue()
						== self.buttonTexts[0])
		refMol = self.refMolMenu.getvalue()
		from Combine import combine, CombineError
		try:
			m = combine(mols, refMol,
					newChainIDs=newChainIDs, log=True)
		except CombineError, v:
			restoreNewMoleculeProcessing()
			self.enter()
			raise UserError(v)
		m.name = self.molNameEntry.get()
		openModels.add([m], baseId=self.modelID.get(), shareXform=False)
		m.openState.xform = refMol.openState.xform
		restoreNewMoleculeProcessing()

		if self.closeModelsVar.get():
			openModels.close(mols)
