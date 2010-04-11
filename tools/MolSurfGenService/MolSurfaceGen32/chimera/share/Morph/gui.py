# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera
from chimera.baseDialog import ModelessDialog
from Interpolate import InterpolationMap, RateMap

MethodChoices = InterpolationMap.keys()
MethodChoices.sort()
RateChoices = RateMap.keys()
RateChoices.sort()

ActionNone = "none"
ActionShowModelPanel = "show Model Panel"
ActionHideConformations = "hide Conformations"

class MorphDialog(ModelessDialog):
	title = "Morph Conformations"
	help = "ContributedSoftware/morph/morph.html"
	buttons = ("Create", "Hide", "Quit")
	keepShown = "Create"

	def __init__(self, *args, **kw):
		self.addDialog = None
		self.state = State(self)
		ModelessDialog.__init__(self, *args, **kw)
		import chimera
		chimera.extension.manager.registerInstance(self)

	def fillInUI(self, parent):
		# Create conformation ordering frame
		import Pmw, Tkinter
		g = Pmw.Group(parent, hull_padx=2, tag_text="Conformations")
		g.pack(fill="both", expand=True)
		gf = g.interior()
		self.confBox = Pmw.ScrolledListBox(gf, listbox_height=4,
					selectioncommand=self._confChoose)
		self.confBox.pack(fill="both", expand=True)
		buttonBox = Pmw.ButtonBox(gf)
		buttonBox.pack(side="bottom")
		buttonBox.add("add", text="Add...", command=self._confAdd)
		buttonBox.add("remove", text="Remove", command=self._confRemove)
		buttonBox.add("up", text="Up", command=self._confUp)
		buttonBox.add("down", text="Down", command=self._confDown)
		buttonBox.alignbuttons()
		self.buttonBox = buttonBox
		# Create options frame
		self.methodMenu = Pmw.OptionMenu(parent,
					hull_padx=2,
					labelpos="w",
					label_text="Interpolation method:",
					items=MethodChoices,
					command=self._setOptions)
		self.methodMenu.pack(fill="x")
		self.rateMenu = Pmw.OptionMenu(parent,
					hull_padx=2,
					labelpos="w",
					label_text="Interpolation rate:",
					items=RateChoices,
					command=self._setOptions)
		self.rateMenu.pack(fill="x")
		self.framesCounter = Pmw.Counter(parent,
					hull_padx=2,
					labelpos="w",
					label_text="Interpolation steps:",
					increment=5,
					entryfield_value=20,
					entryfield_validate={
						"validator": "integer",
						"min": 1,
						"max": 10000,
					},
					entryfield_modifiedcommand=self._setOptions)
		self.framesCounter.pack(fill="x")
		Pmw.alignlabels([ self.framesCounter,
					self.rateMenu,
					self.methodMenu ], sticky="e")
		w = Pmw.LabeledWidget(parent, labelpos="w",
					label_text="Force Cartesian intermediates")
		w.pack(fill="x")
		self.cartesianVar = Tkinter.IntVar()
		self.cartesianVar.set(0)
		self.cartesianButton = Tkinter.Checkbutton(w.interior(),
					variable=self.cartesianVar,
					command=self._setOptions)
		self.cartesianButton.pack(side=Tkinter.LEFT)

		f = Tkinter.Frame(parent, height=2, bd=1, relief=Tkinter.GROOVE)
		f.pack(fill="x", pady=3)

		# Create minimization frame
		self.minimizeVar = Tkinter.IntVar()
		self.minimizeVar.set(0)
		g = Pmw.Group(parent, hull_padx=2,
				tag_text="Minimize",
				tag_pyclass=Tkinter.Checkbutton,
				tag_variable=self.minimizeVar,
				tag_command=self._setOptions)
		g.pack(fill="both")
		gf = g.interior()
		self.stepsCounter = Pmw.Counter(gf,
					labelpos="w",
					label_text="Minimization steps:",
					increment=5,
					entryfield_value=60,
					entryfield_validate={
						"validator": "integer",
						"min": 1,
						"max": 10000,
					},
					entryfield_modifiedcommand=self._setOptions)
		self.stepsCounter.pack()

		# Create "Action on Create" menu
		self.createActionMenu = Pmw.OptionMenu(parent,
					hull_padx=2,
					labelpos="w",
					label_text="Action on Create:",
					items=[ ActionNone,
						ActionShowModelPanel,
						ActionHideConformations ])
		self.createActionMenu.pack(fill="x")

		self.updateOptions()
		self.updateButtons()

	def _confChoose(self, *args):
		selected = [ int(x) for x
			in self.confBox.component("listbox").curselection() ]
		self.state.setSelected(selected)
		self.updateOptions()
		self.updateButtons()

	def _confAdd(self, *args):
		if self.addDialog is None:
			self.addDialog = MorphAddDialog(self,
							master=self.uiMaster())
		else:
			self.addDialog.enter()

	def _confRemove(self, *args):
		self.state.removeSelected()
		self.updateConformations()
		self.updateButtons()

	def _confUp(self, *args):
		self.state.moveSelectedUp()
		self.updateConformations()
		self.updateButtons()

	def _confDown(self, *args):
		self.state.moveSelectedDown()
		self.updateConformations()
		self.updateButtons()

	def _setOptions(self, *args):
		self.state.setOptions(self.getCurrentOptions())

	def updateButtons(self):
		import Tkinter
		selected = self.state.selected
		numItems = len(self.confBox.get())
		if not selected:
			state = Tkinter.DISABLED
		else:
			state = Tkinter.NORMAL
		self.buttonBox.button("remove").config(state=state)
		if 0 in selected:
			state = Tkinter.DISABLED
		else:
			state = Tkinter.NORMAL
		self.buttonBox.button("up").config(state=state)
		if (numItems - 1) in selected:
			state = Tkinter.DISABLED
		else:
			state = Tkinter.NORMAL
		self.buttonBox.button("down").config(state=state)
		if not selected or (len(selected) == 1 and 0 in selected):
			state = Tkinter.DISABLED
		else:
			state = Tkinter.NORMAL
		self.framesCounter.configure(entryfield_entry_state=state,
						uparrow_state=state,
						downarrow_state=state)
		self.rateMenu.configure(menubutton_state=state)
		self.methodMenu.configure(menubutton_state=state)
		self.cartesianButton.configure(state=state)

	def updateConformations(self):
		self.confBox.setlist(self.state.labels())
		listbox = self.confBox.component("listbox")
		for sel in self.state.selected:
			listbox.selection_set(sel)

	def updateOptions(self, *args):
		opts = self.state.getOptions()
		self.methodMenu.setvalue(opts["method"])
		self.rateMenu.setvalue(opts["rate"])
		ef = self.framesCounter.component("entryfield")
		ef.setvalue(opts["frames"])
		self.cartesianVar.set(opts["cartesian"])

	def getCurrentOptions(self):
		opts = {}
		value = self.methodMenu.getvalue()
		if value in MethodChoices:
			opts["method"] = value
		value = self.rateMenu.getvalue()
		if value in RateChoices:
			opts["rate"] = value
		ef = self.framesCounter.component("entryfield")
		if ef.valid():
			value = int(ef.getvalue())
			if value > 0:
				opts["frames"] = value
		opts["cartesian"] = self.cartesianVar.get()
		return opts

	def addConformation(self, mols):
		"Add give conformations to conformation listbox"
		self.state.addAction(mols, self.getCurrentOptions())
		self.updateConformations()
		self.updateButtons()

	#
	# Button callback routines
	#
	def Apply(self):
		minimize = self.minimizeVar.get()
		steps = 60
		ef = self.stepsCounter.component("entryfield")
		if ef.valid():
			value = int(ef.getvalue())
			if value > 0:
				steps = value
		self.state.makeMovie(minimize=minimize, steps=steps)
		action = self.createActionMenu.getvalue()
		if action == ActionShowModelPanel:
			from ModelPanel import ModelPanel
			from chimera import dialogs
			dialogs.display(ModelPanel.name)
		elif action == ActionHideConformations:
			self.state.hideConformations()

	def Hide(self):
		self.emHide()

	def Quit(self):
		self.emQuit()

	#
	# Extension manager callback routines
	#
	def emName(self):
		return self.title

	def emRaise(self):
		self.enter()

	def emHide(self):
		self.Close()

	def emQuit(self):
		import chimera
		if self.addDialog:
			self.addDialog.destroy()
			self.addDialog = None
		chimera.extension.manager.deregisterInstance(self)
		self.state._closeDialog()
		self.destroy()

class State:

	DefaultOpts = {
		"method": "corkscrew",
		"rate": "linear",
		"frames": 20,
		"cartesian": False,
	}

	def __init__(self, morphDialog):
		self.dialog = morphDialog
		self.script = None
		self.selected = []

	def setSelected(self, sel):
		self.selected = sel
		self.selected.sort()

	def addAction(self, mol, opts):
		if self.script is None:
			from base import Script
			self.script = Script(mol, closeCB=self._closeCB, **opts)
			self.selected = [ 0 ]
		else:
			if self.selected:
				where = max(self.selected)
			else:
				where = None
			place = self.script.addAction(mol, after=where, **opts)
			self.selected = [ place ]

	def _closeDialog(self):
		self.dialog = None

	def _closeCB(self, script):
		if not script.actions:
			self.script.finish()
			self.script = None
		if self.dialog:
			self.dialog.updateConformations()

	def moveSelectedUp(self):
		if not self.script:
			return
		if 0 in self.selected:
			from chimera import UserError
			raise UserError("cannot move first item upwards")
		for sel in self.selected:
			self.script.moveActionUp(sel)
		self.selected = [ sel - 1 for sel in self.selected ]

	def moveSelectedDown(self):
		if not self.script:
			return
		if (len(self.script.actions) - 1) in self.selected:
			from chimera import UserError
			raise UserError("cannot move last item down")
		for sel in self.selected[::-1]:
			self.script.moveActionUp(sel + 1)
		self.selected = [ sel + 1 for sel in self.selected ]

	def removeSelected(self):
		if not self.script:
			return
		if not self.selected:
			from chimera import UserError
			raise UserError("no items selected")
		if len(self.script.actions) == 1:
			self.script.finish()
			self.script = None
			self.selected = []
		else:
			for sel in self.selected[::-1]:
				self.script.removeAction(sel)
			last = self.selected[-1] - len(self.selected) + 1
			if last >= len(self.script.actions):
				last = len(self.script.actions) - 1
			self.selected = [ last ]

	def getOptions(self):
		import copy
		if not self.selected:
			return self.DefaultOpts
		multiple = "multiple values"
		methodVal = None
		rateVal = None
		framesVal = None
		cartesianVal = None
		for sel in self.selected:
			mol, opts = self.script.actions[sel]
			val = opts.get("method", None)
			if val is not None:
				if methodVal is None:
					methodVal = val
				elif methodVal != val:
					methodVal = multiple
			val = opts.get("rate", None)
			if val is not None:
				if rateVal is None:
					rateVal = val
				elif rateVal != val:
					rateVal = multiple
			val = opts.get("frames", 0)
			if val is not None:
				if framesVal is None:
					framesVal = val
				elif framesVal != val:
					framesVal = 0
			val = opts.get("cartesian", None)
			if val is not None:
				if cartesianVal is None:
					cartesianVal = val
				elif cartesianVal != val:
					cartesianVal = multiple
		opts = {
			"method": methodVal,
			"rate": rateVal,
			"frames": framesVal,
			"cartesian": cartesianVal,
		}
		return opts

	def setOptions(self, opts):
		if not self.script:
			return
		if not self.selected:
			from chimera import UserError
			raise UserError("no items selected")
		for sel in self.selected:
			self.script.setOptions(sel, **opts)

	def labels(self):
		if not self.script:
			return []
		labels = []
		for mol, opts in self.script.actions:
			labels.append("%s (%s)" % (mol.name, mol.oslIdent()))
		return labels

	def makeMovie(self, **kw):
		if not self.script:
			from chimera import UserError
			raise UserError("No conformations selected")
		self.script.updateMovieDialog(True, **kw)

	def hideConformations(self):
		if not self.script:
			return
		for mol, opts in self.script.actions:
			mol.display = False

class MorphAddDialog(ModelessDialog):
	title = "Add Morph Conformation"
	buttons = ("Add", "Close")
	default = "Add"
	help = "ContributedSoftware/morph/morph.html#addmodels"

	def __init__(self, morph, *args, **kw):
		self.morph = morph
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		from chimera import widgets
		self.molBox = widgets.MoleculeScrolledListBox(parent,
						listbox_selectmode="extended",
						dblclickcommand=self.Add,
						autoselect=None)
		self.molBox.pack(expand=True, fill="both")

	def Add(self):
		mols = self.molBox.getvalue()
		if not mols:
			from chimera import UserError
			raise UserError("Please select conformation to add")
		for mol in mols:
			self.morph.addConformation(mol)
