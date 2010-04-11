# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: base.py 29771 2010-01-13 22:09:36Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import help, openModels
import Tix
import Tkinter
import CGLtk
import os

_buttonInfo = {}
_mp = None

def addButton(name, callback, minModels=1, maxModels=None,
			moleculesOnly=True, balloon=None, defaultFrequent=True):
	"""Add a button to the 'Model Actions' button list.

	   'name' is the button name (duh).  'callback' is the
	   function to call when the button is pressed.  The arg to
	   'callback' will be a list of models.  'min/maxModels'
	   indicate how many models have to be selected in the
	   browser for the button to be active ('None' indicates no
	   limit).  if 'moleculesOnly' is True, then those models have
	   to be Molecules.

	   This is a module function so that it can be called even if
	   the model panel has not yet been created.
	"""

	if _buttonInfo.has_key(name):
		raise KeyError, \
			"Button named '%s' already exists" % name
	_buttonInfo[name] = (callback, minModels, maxModels,
					moleculesOnly, balloon, defaultFrequent)

	if _mp:
		_mp._showButton(name)
		_mp._confDialog.newButton(name, balloon=balloon,
					defaultFrequent=defaultFrequent)

_columnNames = []
_valueTypes = []
_valueFuncs = []
_defaultShows = []
def addColumns(columnInfo, defaultShown=1):
	"""Add columns to the model table.

	   'columnInfo' is a list of 3-tuples, one for each column
	   to add.  The tuple consists of (column name, value type,
	   value-fetch function).  The value type should be 'text',
	   'image', 'imagetext', or 'toggle'.  The value-fetch function
	   takes one argument (a model) and (for 'image' and 'text')
	   should return the value to display in the table cell.  For
	   'imagetext' the return value should be an (image, text)
	   tuple.  'toggle' shows a toggle button and the return value
	   should be a (boolean, callback) tuple.  If the boolean is
	   true, a check will be shown on the toggle button; otherwise
	   the button is blank.  The callback is invoked when the
	   toggle is pressed, with the model and the new boolean as
	   arguments.  The value of an image is the name of the image
	   (the Tix name, e.g. 'tick' for tickmark).  A value of None
	   for image or text will leave a blank cell.

	   'defaultShown' controls whether the column is shown in
	   the model table or not as long as the user has not yet
	   expressed a preference in the Configuration panel about it.
	"""

	noneShown = 1
	for name,type,func in columnInfo:
		if name in _columnNames:
			raise ValueError, "Duplicate model panel"\
						"column name: %s" % name
		_columnNames.append(name)
		_valueTypes.append(type)
		_valueFuncs.append(func)
		_defaultShows.append(defaultShown)
		if _mp:
			try:
				shown = _mp._confDialog.prefs[
							'shownColumns'][name]
			except KeyError:
				shown = defaultShown
			_mp.shownColumns.append(shown)
			if shown:
				noneShown = 0
			_mp._confDialog.newColumn(name, shown)

	if not noneShown:
		_mp._buildTable()

def readableName(model):
	import string
	if model.name:
		for char in model.name:
			if ord(char) < 32:
				break
		else:
			return model.name
	if isinstance(model, chimera.Molecule):
		return "unknown Molecule"
	if isinstance(model, chimera.MSMSModel):
		return "unknown MSMS surface"
	if isinstance(model, chimera.VRMLModel):
		return "unknown VRML object"
	return "unknown"

def inputPath(model):
	if not hasattr(model, 'openedAs') or '\n' in model.openedAs[0]:
		return readableName(model)
	path = model.openedAs[0]
	curdir = os.getcwd() + os.sep
	if path.startswith(curdir):
		return path[len(curdir):]
	return path

def getPhysicalChains(model):
	# return chains of physically connected residues as list of lists;
	# single-residue "chains" collated into first list
	from operator import add
	physical = [[]]
	seen = {}

	for root in model.roots(1):
		resAtoms = root.atom.residue.atoms
		numRootAtoms = root.size.numAtoms

		if numRootAtoms < len(resAtoms):
			# disconnected residue; continue only if this is
			# the largest fragment of the residue
			largestFrag = 1
			for atom in resAtoms:
				if atom.rootAtom == root.atom:
					continue
				if atom.molecule.rootForAtom(atom, 1).size\
						.numAtoms > numRootAtoms:
					largestFrag = 0
					break
			if not largestFrag:
				continue

		if numRootAtoms <= len(resAtoms):
			curPhysical = physical[0]
		else:
			curPhysical = []
			physical.append(curPhysical)
		for atom in model.traverseAtoms(root):
			res = atom.residue
			if seen.has_key(res):
				continue
			seen[res] = 1

			curPhysical.append(res)
	
	return physical

def nameColumn(m):
	if _mp and _mp._confDialog.showColorVar.get():
		bcolor = isinstance(m, chimera.Molecule) and m.color or None
		return readableName(m), bcolor
	return readableName(m)
	
addColumns([
	('ID', 'text', lambda m: m.oslIdent()[1:]),
	('', 'well', lambda m: (isinstance(m, chimera.Molecule) and m.color, True, True, lambda m, c: setattr(m, 'color', c))),
	('Active', 'toggle', lambda m: (m.openState.active, lambda m, b: setattr(m.openState, 'active', b))),
	('Shown', 'toggle', lambda m: (m.display, lambda m, b: setattr(m, 'display', b))),
	('Name', 'text', nameColumn)
])
addColumns([
	('Note', 'text', lambda m: (hasattr(m, 'note') and m.note or '')),
	('Input file', 'text', inputPath)
], defaultShown=False)

class ModelPanel(ModelessDialog):
	title="Model Panel"
	buttons=('Close','Configure...')
	name="model panel"
	help="UsersGuide/modelpanel.html"

	modelTableHelp = "click to select models;"\
			"\nright-hand action buttons work on selected models;"\
			"\ndouble-click to perform default action on model"\
			"\n(see 'Configure...' for default action info)"
	def fillInUI(self, parent):
		global _mp
		_mp = self

		self.parent = parent

		# model table
		self.frequentButtons = []
		self.infrequentButtons = []
		self._getConfig()

		import Pmw
		# action buttons
		self.buttonScroll = Pmw.ScrolledFrame(self.parent,
							hscrollmode='none')
		self.buttonScroll.grid(row=10, column=20, sticky='nsew')
		self.freqActionButtons = Pmw.ButtonBox(
			self.buttonScroll.interior(), orient='vertical', pady=0)
		self.freqActionButtons.pack()
		self._shownActions = self.freqActionButtons
		self.infreqActionButtons = Pmw.ButtonBox(
			self.buttonScroll.interior(), orient='vertical', pady=0)
		self._freqToggle = Pmw.OptionMenu(self.parent,
				command=self._freqToggleCB,
				items=["frequently used", "infrequently used"],
				initialitem="frequently used")
		self._freqToggle.grid(row=20, column=20)

		self._addColumns()
		# add buttons from other extensions...
		self._addButtons()

		# add standard buttons
		addButton("add/edit note...", noteCmd, balloon="add notation"
			" that will be displayed in model table")
		addButton("activate", lambda m, f='active', v=1,
			smf=setModelField: smf(m, f, v, openState=1),
			moleculesOnly=False, defaultFrequent=False,
			balloon="make selected models active"
			"\n(responsive to mouse motions)")
		addButton("activate all", lambda m, f=activateAllCmd: f(),
			minModels = 0, moleculesOnly=False,
			balloon="activate all models;\n"
			"restore previous active states with this same button")
		addButton("activate only", lambda m, f='active',
			smfo=setModelFieldOnly: smfo(m, f, openState=1),
			moleculesOnly=False,
			balloon="make selected models active"
			"\n(responsive to mouse motions);\ndeactivate others")
		addButton("attributes...", attributesCmd,
			moleculesOnly=False,
			balloon="inspect/modify model attributes")
		def runClipping(models):
			import ModelClip
			cd = chimera.dialogs.display(ModelClip.ClipDialog.name)
			cd.setModel(models[0])
		addButton("clipping...", runClipping, moleculesOnly=False,
			balloon="adjust per-model clipping plane")
		addButton("close", openModels.close, moleculesOnly=False,
			balloon="close models")
		addButton("deactivate", lambda m, f='active', v=0,
			smf=setModelField: smf(m, f, v, openState=1),
			moleculesOnly=False, defaultFrequent=False,
			balloon="make selected models inactive"
			"\n(insensitive to mouse motions)")
		addButton("focus", focusCmd, moleculesOnly=False,
			balloon="bring selected models fully into view"
			"\nin main graphics window")
		addButton("hide", lambda m, f='display', v=0,
			smf=setModelField: smf(m, f, v),
			moleculesOnly=False, defaultFrequent=False,
			balloon="hide selected models; undo with 'show'")
		def showRainbowDialog(models):
			from chimera import dialogs
			from rainbow import RainbowDialog
			if len(models) > 1:
				target = "models"
			else:
				target = "residues"
			dialogs.display(RainbowDialog.name).configure(
						models=models, target=target)
		addButton("rainbow...", showRainbowDialog,
			balloon="rainbow-color residues or chains")
		addButton("rename...", renameCmd, moleculesOnly=False,
								maxModels=1)
		addButton("select", selectCmd, moleculesOnly=False,
			balloon="incorporate models into graphics window"
			"\nselection using current selection mode"
			"\n(see graphics window Selection menu)")
		from chainPicker import ChainPicker
		addButton("select chain(s)...", lambda m,
			cp=ChainPicker: cp(m).enter(),
			balloon="select some/all chains\n"
			"(using current selection\n"
			"mode from Selection menu)")
		addButton("sequence...", seqCmd,
			balloon="inspect molecule sequence")
		addButton("show", lambda m, f='display', v=1,
			smf=setModelField: smf(m, f, v),
			moleculesOnly=False, defaultFrequent=False,
			balloon="unhide selected models")
		addButton("show all atoms", showAllAtomsCmd,
			balloon="show all atoms"
			" (but use 'show' to undo 'hide')")
		addButton("show only", lambda m, f='display',
			smfo=setModelFieldOnly: smfo(m, f), moleculesOnly=False,
			balloon="show selected models and hide all others")
		addButton("surface main", lambda m, c="main", sc=surfCmd:
			sc(m, c),
			balloon="surface non-ligand portion of models")
		def showTileDialog(models):
			from chimera import dialogs
			from EnsembleMatch.choose import TileStructuresCB
			dialogs.display(TileStructuresCB.name).configure(
								models=models)
		addButton("tile...", showTileDialog, minModels=2,
			moleculesOnly=False,
			balloon="arrange selected models into a"
			"\nrectangular grid and focus on them")
		addButton("toggle active", lambda m, f='active',
			tmf=toggleModelField: tmf(m, f, openState=1),
			moleculesOnly=False,
			balloon="invert active states of selected models")
		addButton("trace backbones", lambda m, bc=backboneCmd:
			bc(m, resTrace=0),
			balloon="show backbone atom trace for protein"
			"\nor nucleic acid; undo with 'show all atoms'")
		addButton("trace chains", backboneCmd,
			balloon="show residue connectivity trace for protein"
			"\nor nucleic acid; undo with 'show all atoms'")
		from transformDialog import TransformDialog
		addButton("transform as...", TransformDialog,
			moleculesOnly=False,
			balloon="rotate/translate models same as another model")
		from writePDBdialog import WritePDBdialog
		addButton("write PDB", lambda mols: chimera.dialogs.display(
			WritePDBdialog.name).configure(mols, selOnly=False),
			balloon="write molecule as PDB file")
		from ksdsspDialog import KsdsspDialog
		addButton("compute SS", KsdsspDialog,
			balloon="compute secondary structure elements"
			"\nusing Kabsch and Sander algorithm")
		
		maxWidth = 0
		for actionButtons in [self.freqActionButtons,
						self.infreqActionButtons]:
			for i in range(actionButtons.numbuttons()):
				w = actionButtons.button(i).winfo_reqwidth()
				if w > maxWidth:
					maxWidth = w
		self.buttonScroll.component('clipper').configure(
						width=maxWidth+2, height='2i')

		# add these last, since if they somehow fire before the
		# constructor is complete then an exception will occur
		chimera.triggers.addHandler('Model', self._fillTable, None)
		chimera.triggers.addHandler('OpenState', self._fillTable, None)
	
	def Configure(self):
		"""configure action buttons"""
		self._confDialog.enter()

	def see(self, buttonName):
		if buttonName in self.frequentButtons:
			actionButtons = self.freqActionButtons
		else:
			actionButtons = self.infreqActionButtons
		self._showActions(actionButtons)
		scroller = self.buttonScroll.component("vertscrollbar")
		scroller.update_idletasks() # get things mapped
		if not scroller.winfo_ismapped():
			return
		curTop, curBottom = scroller.get()
		numButtons = actionButtons.numbuttons()
		thisButton = actionButtons.index(buttonName)
		newPos = (thisButton + 0.5) / numButtons
		newTop = newPos - (curBottom - curTop) / 2
		if newTop < 0:
			newTop = 0
		scroller.tk.call(scroller.cget("command"), "moveto", newTop)
		scroller.after(999, actionButtons.button(buttonName).flash)

	def selected(self, moleculesOnly=False):
		"""Return a list of the selected models"""

		selected = []
		for mi in self.modelTable.hlist.info_selection():
			model = self.models[int(mi)]
			if moleculesOnly \
			and model.__class__ != chimera.Molecule:
				continue
			selected.append(model)
		return selected

	def selectionChange(self, models, extend=0):
		"""set (or extend) the selection to contain the given models
		
		   'models' can be Models or oslIdents"""

		if not extend:
			self.modelTable.hlist.selection_clear()

		if models:
			if isinstance(models[0], basestring):
				# presumably oslIdent
				models = filter(lambda m, ms=models:
						m.oslIdent() in ms, self.models)
			else:
				models = filter(lambda m, ms=self.models:
								m in ms, models)
		
		for model in models:
			self.modelTable.hlist.selection_set(
						self.models.index(model))
		self._selChangeCB()

	def _addButtons(self):
		"""Add buttons to interface that were requested before
		   panel was created.
		"""

		for name, info in _buttonInfo.items():
			balloon, defaultFrequent = info[-2:]
			self._showButton(name)
			self._confDialog.newButton(name, balloon=balloon,
						defaultFrequent=defaultFrequent)

	def _addColumns(self):
		"""Process column information"""
		self.shownColumns = []

		for i in range(len(_columnNames)):
			name = _columnNames[i]
			if name == "Note":
				shown = False
				for m in openModels.list():
					if hasattr(m, 'note') and m.note:
						shown = True
						break
			else:
				try:
					shown = self._confDialog.prefs[
							'shownColumns'][name]
				except KeyError:
					shown = _defaultShows[i]
			self.shownColumns.append(shown)
			self._confDialog.newColumn(name, shown)
		self._buildTable()

	def _buildTable(self):
		if hasattr(self, 'modelTable'):
			# can't dynamically add columns to Tix widget;
			# destroy and recreate
			selected = self.selected()
			self.modelTable.grid_forget()
			self.modelTable.destroy()
		else:
			selected = None

		self.modelTable = Tix.ScrolledHList(self.parent,
			width="%d" % self.parent.winfo_pixels("3i"),
			options="""hlist.columns %d
			hlist.header 1
			hlist.selectMode extended
			hlist.indicator 0"""
			% len(filter(lambda s: s == 1, self.shownColumns)))
		help.register(self.modelTable, balloon=self.modelTableHelp)
		self.modelTable.hlist.config(browsecmd=self._selChange,
							command=self._dblClick)
		self.textStyle = Tix.DisplayStyle("text",
				refwindow=self.modelTable)
		# get a style for checkbutton columns...
		self.checkButtonStyle = Tix.DisplayStyle("window",
				refwindow=self.modelTable, anchor="center")
		self.colorWellStyle = Tix.DisplayStyle("window",
				refwindow=self.modelTable, anchor="center")
		colNum = 0
		self.columnMap = []
		showFullTitles = False
		last = self._confDialog.prefs["lastUse"]
		from time import time
		now = self._confDialog.prefs["lastUse"] = time()
		if last is None or now - last > 777700: # about 3 months
			showFullTitles = True
		for index in range(len(_columnNames)):
			if not self.shownColumns[index]:
				continue
			self.columnMap.append(index)
			text = _columnNames[index]
			if _valueTypes[index] == 'toggle' \
			and not showFullTitles:
				text = text[:1]
			self.modelTable.hlist.header_create(colNum,
						itemtype='text', text=text)
			colNum = colNum + 1
			
		self.parent.columnconfigure(10, weight=1)
		self.parent.rowconfigure(10, weight=1)
		self.modelTable.grid(row=10, column=10, sticky='nsew',
								rowspan=11)
		self._fillTable(selected=selected, fromScratch=1)
	
	def _buttonFrequency(self, button, frequent=1):
		"""set button frequency"""
		if frequent:
			buttons = self.frequentButtons
			otherButtons = self.infrequentButtons
			otherActions = self.infreqActionButtons
		else:
			buttons = self.infrequentButtons
			otherButtons = self.frequentButtons
			otherActions = self.freqActionButtons
		if button in otherButtons:
			otherButtons.remove(button)
			otherActions.delete(button)
		if button not in buttons:
			self._showButton(button)


	def _dblClick(self, item):
		"""user has double-clicked on model table entry"""

		# if the state of the action buttons is due to change,
		# execute that change before calling the double-click routine
		if hasattr(self, '_selChangeIdle') and self._selChangeIdle:
			self.parent.after_cancel(self._selChangeIdle)
			self._selChangeCB()

		self._confDialog.dblClick()

	def _fillTable(self, *triggerArgs, **kw):
		if len(triggerArgs) > 0 and triggerArgs[0] == 'OpenState':
			if 'active change' not in triggerArgs[-1].reasons:
				return
		hlist = self.modelTable.hlist
		defaultable = 0
		if kw.has_key('selected') and kw['selected'] != None:
			selected = kw['selected']
		else:
			selected = self.selected()
			defaultable = 1
		rebuild = 0
		if kw.has_key('fromScratch') and kw['fromScratch']:
			rebuild = 1
		else:
			prevModels = self.models

		self.models = openModels.list()
		self.models.sort(self._modelSort)
		if not rebuild and self.models != prevModels:
			rebuild = 1
		if rebuild:
			self._prevValues = {}
			hlist.delete_all()
			vf = _valueFuncs[self.columnMap[0]]
			for mi in range(len(self.models)):
				m = self.models[mi]
				apply(hlist.add, (mi,), self._hlistKw(m, 0))
				self._prevValues[(mi, 0)] = vf(m)
			for ci in range(1, len(self.columnMap)):
				vf = _valueFuncs[self.columnMap[ci]]
				for mi in range(len(self.models)):
					m = self.models[mi]
					apply(hlist.item_create, (mi, ci),
							self._hlistKw(m, ci))
					self._prevValues[(mi, ci)] = vf(m)
		else:
			for ci in range(len(self.columnMap)):
				vf = _valueFuncs[self.columnMap[ci]]
				for mi in range(len(self.models)):
					m = self.models[mi]
					curVal = vf(m)
					prevVal = self._prevValues[(mi, ci)]
					if isinstance(curVal, tuple):
						for vi in range(len(curVal)):
							valItem = curVal[vi]
							if callable(valItem):
								continue
							if valItem != prevVal[
									vi]:
								break
						else:
							# equal
							continue
					elif curVal == prevVal:
						continue
					self._prevValues[(mi, ci)] = curVal
					apply(hlist.item_configure, (mi, ci),
							self._hlistKw(m, ci))
		# if only one model, select it
		if defaultable and len(self.models) == 1:
			selected = self.models
		for m in selected:
			if m not in self.models:
				continue
			hlist.selection_set(self.models.index(m))
		self._selChange(None)
	
	def _freqToggleCB(self, label):
		if label.startswith("freq"):
			self._showActions(self.freqActionButtons)
		else:
			self._showActions(self.infreqActionButtons)

	def _getConfig(self):
		"""retrieve configuration preferences"""

		# set up configuration dialog
		from confDialog import ConfDialog
		self._confDialog = ConfDialog(self)
		self._confDialog.Close()

	def _hlistKw(self, model, colNum):
		vt = _valueTypes[self.columnMap[colNum]]
		vf = _valueFuncs[self.columnMap[colNum]]
		kw = {'itemtype': vt}
		txt = None
		img = None
		if vt == 'text':
			txt = vf(model)
			if not isinstance(txt, basestring):
				txt, bcolor = txt
				if bcolor is not None:
					if not isinstance(bcolor, basestring):
						if hasattr(bcolor, 'rgba'):
							rgba = bcolor.rgba()
						else:
							rgba = bcolor
						from CGLtk.color import rgba2tk
						bcolor = rgba2tk(rgba)
						fcolor = CGLtk.textForeground(
							bcolor, self.modelTable)
					kw['style'] = Tix.DisplayStyle("text",
						refwindow=self.modelTable,
						background=bcolor,
						foreground=fcolor,
						selectforeground=bcolor)
			else:
				kw['style'] = self.textStyle
		elif vt == 'image':
			img = vf(model)
		elif vt == 'imagetext':
			img, txt = vf(model)
		elif vt == 'toggle':
			kw['itemtype'] = 'window'
			bool, cb = vf(model)
			togKw = {'command':
				# avoid holding references to model
				lambda cb=cb, i=self.models.index(model),
					b=not bool: cb(self.models[i], b),
				'indicatoron': 0,
				'borderwidth': 0}
			if bool:
				togKw['image'] = self.modelTable.tk.call(
					'tix', 'getimage', 'ck_on')
			else:
				togKw['image'] = self.modelTable.tk.call(
					'tix', 'getimage', 'ck_off')
			toggle = Tkinter.Checkbutton(
						self.modelTable.hlist, **togKw)
			kw['window'] = toggle
			kw['style'] = self.checkButtonStyle
		elif vt == 'well':
			color, noneOkay, alphaOkay, cb = vf(model)
			if color is False:
				kw['itemtype'] = 'text'
				txt = ""
			else:
				kw['itemtype'] = 'window'
				if isinstance(color, chimera.MaterialColor):
					color = color.rgba()
				def wellCB(clr, cb=cb, mdl=model):
					if clr is not None:
						clr = chimera.MaterialColor(
									*clr)
					cb(mdl, clr)
				from CGLtk.color.ColorWell import ColorWell
				kw['window'] = ColorWell(self.modelTable.hlist,
					color, callback=wellCB,
					width=18, height=18,
					noneOkay=noneOkay, wantAlpha=alphaOkay)
				kw['style'] = self.colorWellStyle
		else:
			raise ValueError("Unknown column type: '%s'" % vt)
		
		if txt != None:
			kw['text'] = str(txt)
		if img != None:
			kw['image'] = self.modelTable.tk.call(
							'tix', 'getimage', img)
		return kw
	
	def _modelSort(self, m1, m2):
		if m1.id < m2.id:
			return -1
		if m1.id > m2.id:
			return 1
		if m1.subid < m2.subid:
			return -1
		if m1.subid > m2.subid:
			return 1
		return 0

	def _selChange(self, item):
		# slow browse callback interferes with double-click detection,
		# so delay callback enough to allow most double-clicks to work
		if hasattr(self, '_selChangeIdle') and self._selChangeIdle:
			self.parent.after_cancel(self._selChangeIdle)
		self._selChangeIdle = self.parent.after(300, self._selChangeCB)

	def _selChangeCB(self):
		numSel = len(self.modelTable.hlist.info_selection())
		for buttons, actionButtons in [
				(self.frequentButtons, self.freqActionButtons),
				(self.infrequentButtons,
						self.infreqActionButtons)]:
			for b in buttons:
				state = 'normal'
				callback, minModels, maxModels, moleculesOnly, \
					balloon, defaultFrequent \
							= _buttonInfo[b]
				if self._shouldDisable(minModels, maxModels,
								moleculesOnly):
					state = 'disabled'
				actionButtons.button(b).config(state=state)
		self._selChangeIdle = None

	def _shouldDisable(self, minModels, maxModels, moleculesOnly):
		if moleculesOnly:
			numSel = len(self.selected(moleculesOnly=True))
		else:
			numSel = len(self.modelTable.hlist.info_selection())
		if minModels != None and numSel < minModels \
		or maxModels != None and numSel > maxModels:
			return 1
		return 0

	def _showActions(self, actionButtons):
		if actionButtons == self._shownActions:
			return
		if actionButtons == self.freqActionButtons:
			self.infreqActionButtons.pack_forget()
		else:
			self.freqActionButtons.pack_forget()
		actionButtons.pack()
		self._shownActions = actionButtons

	def _showButton(self, name):
		callback, minModels, maxModels, moleculesOnly, balloon, \
					defaultFrequent = _buttonInfo[name]

		kw = {}
		state = 'normal'
		if self._shouldDisable(minModels, maxModels, moleculesOnly):
			state = 'disabled'
		kw['state'] = state
		kw['pady'] = 0
		# if you click a button fast enough, you can get around it's
		# upcoming disabling...
		def cmd(cb=callback, s=self, mo=moleculesOnly, minm=minModels,
				maxm=maxModels):
			if not s._shouldDisable(minm, maxm, mo):
				cb(s.selected(moleculesOnly=mo))
		kw['command'] = cmd
		# determine where to add the button...
		freqPrefs = self._confDialog.prefs['freqButs']
		if freqPrefs.has_key(name):
			isFrequent = freqPrefs[name]
		else:
			isFrequent = defaultFrequent
		if isFrequent:
			buttons = self.frequentButtons
			actionButtons = self.freqActionButtons
		else:
			buttons = self.infrequentButtons
			actionButtons = self.infreqActionButtons
		buttons.append(name)
		buttons.sort(lambda a, b: cmp(a.lower(), b.lower()))
		index = buttons.index(name)
		if index == len(buttons)-1:
			addFunc = actionButtons.add
		else:
			addFunc = actionButtons.insert
			kw['beforeComponent'] = buttons[index+1]
		
		but = apply(addFunc, (name,), kw)
		but.config(default='disabled')
		if balloon:
			help.register(but, balloon=balloon)

from chimera import dialogs
dialogs.register(ModelPanel.name, ModelPanel)

def _setAttr(m, field, value, openState=0):
	if openState:
		setattr(m.openState, field, value)
	else:
		setattr(m, field, value)

# functions used in model panel button; could be called directly also
def setModelField(models, field, value, openState=0):
	for m in models:
		_setAttr(m, field, value, openState)

def setModelFieldOnly(models, field, onVal=1, offVal=0, openState=0):
	# turn off first, then on, so that models not in the models list
	# that nonetheless have shared openStates get the 'on' value
	for m in openModels.list():
		_setAttr(m, field, offVal, openState)
	for m in models:
		_setAttr(m, field, onVal, openState)

def toggleModelField(models, field, onVal=1, offVal=0, openState=0):
	openStates = {}
	for m in models:
		if openState:
			openStates[m.openState] = 1
			continue
		if curval == onVal:
			_setAttr(m, field, offVal, openState)
		else:
			_setAttr(m, field, onVal, openState)
	for os in openStates.keys():
		if getattr(os, field) == onVal:
			setattr(os, field, offVal)
		else:
			setattr(os, field, onVal)

_prevActivities = None
def activateAllCmd():
	"""Activate all models.  Restore previous activities if called again."""

	global _prevActivities
	if _prevActivities:
		for m in openModels.list():
			if _prevActivities.has_key(m.openState):
				m.openState.active = _prevActivities[
								m.openState]
		_prevActivities = None
		if _mp:
			if 'activate all' in _mp.frequentButtons:
				actionButtons = _mp.freqActionButtons
			else:
				actionButtons = _mp.infreqActionButtons
			actionButtons.component('activate all').config(
							text='activate all')
	else:
		_prevActivities = {}
		for m in openModels.list():
			if _prevActivities.has_key(m.openState):
				continue
			_prevActivities[m.openState] = m.openState.active
			m.openState.active = 1
		if _mp:
			if 'activate all' in _mp.frequentButtons:
				actionButtons = _mp.freqActionButtons
			else:
				actionButtons = _mp.infreqActionButtons
			actionButtons.component('activate all').config(
						text='restore activities')
_attrInspectors = {}
_headers = {}
_seqInspectors = {}
_inspectors = [_attrInspectors, _headers] # _seqInspectors is per chain

def _checkTrigger():
	global _modelTrigger
	for inspDict in _inspectors:
		if len(inspDict) > 0:
			break
	else:
		# should be no trigger active; start one
		_modelTrigger = chimera.triggers.addHandler(
						'Model', _modelTriggerCB, None)

def attributesCmd(models):
	global _attrInspectors
	_checkTrigger()
	for model in models:
		if not _attrInspectors.has_key(model):
			from modelInspector import ModelInspector
			_attrInspectors[model] = ModelInspector(model)
		_attrInspectors[model].enter()

def seqCmd(items):
	global _seqInspectors
	todo = []
	for item in items:
		if not _seqInspectors.has_key(item):
			from chimera.Sequence import StructureSequence
			if isinstance(item, StructureSequence):
				from MultAlignViewer.MAViewer import MAViewer
				copySeq = StructureSequence.__copy__(item)
				copySeq.name = item.fullName()
				_addSeqInspector(item, mavSeq=copySeq)
			else:
				todo.extend(item.sequences())
				continue
		_seqInspectors[item].enter()
	if todo:
		if len(todo) > 1:
			from seqPanel import SeqPickerDialog
			from chimera import dialogs
			d = dialogs.display(SeqPickerDialog.name)
			d.molListBox.setvalue(todo)
		else:
			seqCmd(todo)

def _addSeqInspector(item, mavSeq=None, mav=None):
	global _seqInspectors, _saveSessionTrigger
	if not _seqInspectors:
		from SimpleSession import SAVE_SESSION
		_saveSessionTrigger = chimera.triggers.addHandler(
				SAVE_SESSION, _saveSessionCB, None)
	trigMav = []
	hid = item.triggers.addHandler(item.TRIG_DELETE,
			lambda tn, md, td: md[0].Quit(), trigMav)
	def quitCB(mav, i=item, h=hid):
		del _seqInspectors[i]
		i.triggers.deleteHandler(i.TRIG_DELETE, h)
		if not _seqInspectors:
			from SimpleSession import SAVE_SESSION
			chimera.triggers.deleteHandler(SAVE_SESSION, _saveSessionTrigger)
	if mav:
		mav.quitCB = quitCB
	else:
		from MultAlignViewer.MAViewer import MAViewer
		mav = MAViewer([mavSeq], title=mavSeq.name, quitCB=quitCB,
						autoAssociate=None, sessionSave=False)
	_seqInspectors[item] = mav
	trigMav.append(mav)

def _modelTriggerCB(trigName, myArg, modelsChanges):
	for model in modelsChanges.deleted:
		for inspDict in _inspectors:
			if inspDict.has_key(model):
				_deleteInspector(model, inspDict)

def _saveSessionCB(trigName, myArg, session):
	from SimpleSession import sessionID, sesRepr
	info = []
	for seq, mav in _seqInspectors.items():
		info.append((seq.name, sessionID(seq.molecule),
			[seq.saveInfo() for seq in mav.seqs], mav.saveInfo()))
	print>>session, """
try:
	from ModelPanel import restoreSeqInspectors
	restoreSeqInspectors(%s)
except:
	reportRestoreError("Error restoring sequence viewers")
""" % sesRepr(info)

def restoreSeqInspectors(info):
	global _seqInspectors
	from SimpleSession import idLookup
	for seqName, molID, seqsInfo, mavInfo in info:
		mol = idLookup(molID)
		for seq in mol.sequences():
			if seq.name == seqName:
				break
		else:
			continue
		if seq in _seqInspectors:
			continue

		from MultAlignViewer.MAViewer import restoreMAV
		from chimera.Sequence import restoreSequence
		mav = restoreMAV([restoreSequence(seqInfo)
						for seqInfo in seqsInfo], mavInfo)
		_addSeqInspector(seq, mav=mav)

def _deleteInspector(model, dict):
	inspector = dict[model]
	del dict[model]
	for inspDict in _inspectors:
		if len(inspDict) > 0:
			break
	else:
		# no inspectors; drop triggers
		chimera.triggers.deleteHandler('Model', _modelTrigger)
	if hasattr(inspector, 'destroy'):
		inspector.destroy()
	else:
		inspector._toplevel.destroy()

def backboneCmd(models, resTrace=1):
	from chimera.misc import displayResPart
	for m in models:
		if not hasattr(m, 'residues'):
			continue
		if resTrace:
			displayResPart(m.residues, trace=1)
		else:
			displayResPart(m.residues, backbone=1)

def focusCmd(models):
	from chimera import openModels, viewer, update
	shown = {}
	for m in openModels.list():
		shown[m] = m.display
		if m in models:
			m.display = 1
		else:
			m.display = 0
	update.checkForChanges()
	viewer.viewAll()
	if chimera.openModels.cofrMethod != chimera.OpenModels.Independent:
		openModels.cofrMethod = openModels.CenterOfView
		viewer.clipping = True

	for m,disp in shown.items():
		m.display = disp
	update.checkForChanges()

def noteCmd(models):
	from noteDialog import NoteDialog
	NoteDialog(models)

def renameCmd(models):
	from renameDialog import RenameDialog
	RenameDialog(models[0])

def selectCmd(models):
	sel = chimera.selection.ItemizedSelection()
	sel.add(models)
	chimera.tkgui.selectionOperation(sel)
	
def showAllAtomsCmd(models):
	for m in models:
		if not hasattr(m, 'atoms') or not hasattr(m, 'bonds'):
			continue
		m.display = 1
		for a in m.atoms:
			a.display = 1

def surfCmd(models, category):
	import Midas
	mols = filter(lambda m: isinstance(m, chimera.Molecule), models)
	Midas.surfaceNew(category, models=mols)
	for m in mols:
		for a in m.atoms:
			if a.surfaceCategory == category:
				a.surfaceDisplay = 1
