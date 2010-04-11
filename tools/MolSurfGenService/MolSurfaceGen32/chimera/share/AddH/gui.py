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
from chimera.baseDialog import ModelessDialog, ModalDialog
from prefs import prefs, HBOND_GUIDED

class AddHDialog(ModelessDialog):
	name = "add hydrogens"
	help = "ContributedSoftware/addh/addh.html"
	buttons = ('OK', 'Close')
	default = 'OK'

	def __init__(self, title="Add Hydrogens", models=None,
						useHBonds=None, cb=None, **kw):
		self.title = title
		self.cb = cb
		self.startModels = models
		if useHBonds is None:
			self.startUseHBonds = prefs[HBOND_GUIDED]
		else:
			self.startUseHBonds = useHBonds
		ModelessDialog.__init__(self, **kw)

	def fillInUI(self, parent):
		import Pmw, Tkinter
		from chimera.widgets import MoleculeScrolledListBox
		self.molList = MoleculeScrolledListBox(parent, labelpos='w',
					label_text="Add hydrogens to:",
					listbox_selectmode='extended',
					selectioncommand=self._updateHisListing)
		if self.startModels:
			self.molList.setvalue(self.startModels)
		self.molList.grid(row=0, column=0, sticky="news")
		parent.columnconfigure(0, weight=1)
		parent.rowconfigure(0, weight=1)

		grp = Pmw.Group(parent, tag_text="Method", hull_padx=2)
		grp.grid(row=1, column=0, sticky="ew")
		self.useHBondsVar = Tkinter.IntVar(parent)
		self.useHBondsVar.set(self.startUseHBonds)
		Tkinter.Radiobutton(grp.interior(), variable=self.useHBondsVar,
				value=False, text="steric only"
				).grid(row=0, sticky='w')
		Tkinter.Radiobutton(grp.interior(), variable=self.useHBondsVar,
			value=True, text="also consider H-bonds (slower)"
			).grid(row=1, sticky='w')

		self.hisGroup = Pmw.Group(parent, hull_padx=2,
					tag_text="Histidine Protonation")
		self.hisGroup.grid(row=2, column=0, sticky="nsew")
		self.hisProtVar = Tkinter.StringVar(parent)
		self.hisProtVar.set("name")
		interior = self.hisGroup.interior()
		Tkinter.Radiobutton(interior, variable=self.hisProtVar,
			value="name", text="Residue-name-based\n"
			"(HIS/HID/HIE/HIP = unspecified/delta/epsilon/both)",
			command=self._switchHisList, justify="left").grid(
			row=0, sticky='w')
		self._pickText = Tkinter.StringVar(parent)
		self._pickText.set("Specified individually...")
		Tkinter.Radiobutton(interior, variable=self.hisProtVar,
				value="pick", textvariable=self._pickText,
				command=self._switchHisList,
				).grid(row=1, sticky='w')
		Tkinter.Radiobutton(interior, variable=self.hisProtVar,
				value="default", command=self._switchHisList,
				text="Unspecified (determined by method)"
				).grid(row=3, sticky='w')

	def _clearAll(self):
		for v, cmd in self._vars:
			if v.get():
				v.set(0)
				cmd()

	def _selectAll(self):
		for v, cmd in self._vars:
			if not v.get():
				v.set(1)
				cmd()

	def _switchHisList(self):
		if not hasattr(self, 'hisListing'):
			if self.hisProtVar.get() != "pick":
				return
			self.hisListingData = {}
			import Tix, Tkinter
			self.hisFrame = Tkinter.Frame(self.hisGroup.interior())
			Tkinter.Label(self.hisFrame, text="If neither delta"
				" nor epsilon is selected\nthen chosen method"
				" determines protonation").grid(row=0,
				column=0, columnspan=2)
			self.hisListing = Tix.ScrolledHList(self.hisFrame,
						width="3i",
						options="""hlist.columns 4
						hlist.header 1
						hlist.indicator 1""")
			self.hisListing.hlist.configure(
				selectbackground=self.hisListing['background'],
				selectborderwidth=0)
			self.hisListing.grid(row=1, column=0, columnspan=2,
								sticky="nsew")
			self.hisFrame.rowconfigure(1, weight=1)
			self.hisFrame.columnconfigure(0, weight=1)
			self.hisFrame.columnconfigure(1, weight=1)
			hlist = self.hisListing.hlist
			hlist.header_create(0, itemtype="text", text="Model")
			hlist.header_create(1, itemtype="text", text="Residue")
			hlist.header_create(2, itemtype="text", text="Delta")
			hlist.header_create(3, itemtype="text", text="Epsilon")
			self._checkButtonStyle = Tix.DisplayStyle("window",
				background=hlist['background'],
				refwindow=self.hisListing, anchor='center')
			self._updateHisListing()

			Tkinter.Button(self.hisFrame, text="Select All",
				pady=0, highlightthickness=0,
				command=self._selectAll).grid(row=2, column=0)
			Tkinter.Button(self.hisFrame, text="Clear All",
				pady=0, highlightthickness=0,
				command=self._clearAll).grid(row=2, column=1)

		if self.hisProtVar.get() == "pick":
			self._pickText.set("Individually chosen:")
			self.hisFrame.grid(row=2, sticky="nsew")
			interior = self.hisGroup.interior()
			interior.columnconfigure(0, weight=1)
			interior.rowconfigure(2, weight=1)
			self.uiMaster().rowconfigure(2, weight=4)
		else:
			self._pickText.set("Individually chosen...")
			self.hisFrame.grid_forget()
			interior = self.hisGroup.interior()
			interior.columnconfigure(0, weight=0)
			interior.rowconfigure(2, weight=0)
			self.uiMaster().rowconfigure(2, weight=0)

	def _toggleDelta(self, res):
		old = self.hisListingData[res]
		if old == "HIS":
			new = "HID"
		elif old == "HID":
			new = "HIS"
		elif old == "HIE":
			new = "HIP"
		else:
			new = "HIE"
		self.hisListingData[res] = new

	def _toggleEpsilon(self, res):
		old = self.hisListingData[res]
		if old == "HIS":
			new = "HIE"
		elif old == "HID":
			new = "HIP"
		elif old == "HIE":
			new = "HIS"
		else:
			new = "HID"
		self.hisListingData[res] = new

	def _updateHisListing(self):
		if not hasattr(self, 'hisListing'):
			return
		self._updateHisListingData()
		hlist = self.hisListing.hlist
		on = self.hisListing.tk.call('tix', 'getimage', 'ck_on')
		off = self.hisListing.tk.call('tix', 'getimage', 'ck_off')
		hlist.delete_all()
		import Tkinter
		row = 0
		self._vars = []
		for m in self.molList.getvalue():
			for r in m.residues:
				if r.type not in ["HIS", "HIE", "HIP", "HID"]:
					continue
				try:
					hisType = self.hisListingData[r]
				except KeyError:
					self.hisListingData[r] = hisType = "HIS"
				hlist.add(row, itemtype="text", text="%s (%s)"
						% (m.name, m.oslIdent()))
				hlist.item_create(row, 1, itemtype="text",
						text=r.oslIdent(
						start=chimera.SelResidue))
				var = Tkinter.IntVar(hlist)
				var.set(hisType in ["HID", "HIP"])
				cmd = lambda r=r: self._toggleDelta(r)
				self._vars.append((var, cmd))
				toggle = Tkinter.Checkbutton(hlist, command=cmd,
					variable=var, image=off, selectimage=on,
					selectcolor="", indicatoron=False,
					borderwidth=0)
				hlist.item_create(row, 2, itemtype="window",
					window=toggle,
					style=self._checkButtonStyle)
				var = Tkinter.IntVar(hlist)
				var.set(hisType in ["HIE", "HIP"])
				cmd = lambda r=r: self._toggleEpsilon(r)
				self._vars.append((var, cmd))
				toggle = Tkinter.Checkbutton(hlist, command=cmd,
					variable=var, image=off, selectimage=on,
					selectcolor="", indicatoron=False,
					borderwidth=0)
				hlist.item_create(row, 3, itemtype="window",
					window=toggle,
					style=self._checkButtonStyle)
				row += 1

	def _updateHisListingData(self):
		newData = {}
		for m in self.molList.getvalue():
			for r in m.residues:
				if r.type not in ["HIS", "HIE", "HIP", "HID"]:
					continue
				try:
					newData[r] = self.hisListingData[r]
				except KeyError:
					newData[r] = r.type
		self.hisListingData = newData

	def Apply(self):
		from chimera import openModels, Molecule
		from AddH import simpleAddHydrogens, hbondAddHydrogens
		from unknownsGUI import initiateAddHyd
		prefs[HBOND_GUIDED] = self.useHBondsVar.get()
		method = [simpleAddHydrogens, hbondAddHydrogens][
							prefs[HBOND_GUIDED]]
		if self.hisProtVar.get() == "name":
			hisScheme = None
		elif self.hisProtVar.get() == "pick":
			hisScheme = self.hisListingData
		else:
			hisScheme = {}
		initiateAddHyd(self.molList.getvalue(), addFunc=method,
					hisScheme=hisScheme, okCB=self.cb)

def checkNoHyds(mols, cb, process):
	noHyds = []
	for mol in mols:
		for a in mol.atoms:
			if a.element.number == 1:
				break
		else:
			noHyds.append(mol)
	if not noHyds:
		cb()
		return
	from chimera.baseDialog import AskYesNoDialog
	msg = "Hydrogens must be present for %s to work correctly.\n" % process
	if type(mols[0]) == chimera.Residue:
		objDesc = "residue"
		attrName = "type"
		noHydModels = list(set([r.molecule for r in noHyds]))
	else:
		objDesc = "model"
		attrName = "name"
		noHydModels = noHyds
	if len(mols) == len(noHyds):
		msg += "No %ss have hydrogens.\n" % objDesc
	else:
		msg += "The following %ss have no hydrogens:\n" % objDesc
		for nh in noHyds:
			msg += "\t%s (%s)\n" % (getattr(nh, attrName),
								nh.oslIdent())
	msg += "You can add hydrogens using the AddH tool.\n"
	msg += "What would you like to do?"
	userChoice = NoHydsDialog(msg).run(chimera.tkgui.app)
	if userChoice == "add hydrogens":
		AddHDialog(title="Add Hydrogens for %s" % process.title(),
			models=noHydModels, useHBonds=True, oneshot=True, cb=cb)
	elif userChoice == "continue":
		cb()

class NoHydsDialog(ModalDialog):
	title = "No Hydrogens..."
	help = "UsersGuide/midas/addcharge.html#needH"
	buttons = ('Abort', 'Add Hydrogens', 'Continue Anyway')
	default = 'Add Hydrogens'
	oneshot = True

	def __init__(self, msg):
		self.msg = msg
		ModalDialog.__init__(self)

	def fillInUI(self, parent):
		import Tkinter
		message = Tkinter.Label(parent, text=self.msg)
		message.grid(sticky='nsew')

	def Abort(self):
		self.Cancel("cancel")

	def AddHydrogens(self):
		self.Cancel("add hydrogens")

	def ContinueAnyway(self):
		self.Cancel("continue")

from chimera import dialogs
dialogs.register(AddHDialog.name, AddHDialog)
