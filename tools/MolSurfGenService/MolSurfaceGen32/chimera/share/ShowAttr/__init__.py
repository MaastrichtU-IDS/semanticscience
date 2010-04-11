# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29220 2009-11-03 21:21:58Z pett $

import chimera
from chimera import selection
from chimera.baseDialog import ModelessDialog
import Tkinter, Pmw
from prefs import prefs, TARGET, ATTRS_RESIDUES, ATTRS_ATOMS, ATTRS_MODELS, \
	LAST_ATTR, COLORS, COLOR_ATOMS, COLOR_RIBBONS, COLOR_SURFACES, SCALING,\
	ATOM_STYLE, ATOM_RADII, NOVAL_RADIUS, WORM_RADII, NOVAL_WORM, \
	WORM_STYLE, RESTRICT
from CGLtk.optCascade import CascadeOptionMenu

screenedAttrs = {}
screenedAttrs[chimera.Atom] = {
	'name': False, 'idatmIsExplicit': False, 'idatmType': str,
	'drawMode': False, 'hide': False, 'label': False,
	'surfaceDisplay': False, 'vdw': False,
	'selLevel': False, 'surfaceOpacity': False,
	'serialNumber': False, 'defaultRadius': False,
	'radius': False, 'coordIndex': False
}
screenedAttrs[chimera.Residue] = {
	'name': False, 'ribbonDisplay': False, 'isSheet': False,
	'ribbonDrawMode': False, 'selLevel': False, 'ringMode': False,
	'ssId': False, 'fillMode': False, 'fillDisplay': False
}
screenedAttrs[chimera.Model] = {
	'autochain': False, 'ballScale': False, 'lineType': False,
	'lineWidth': False, 'id': False, 'subid': False,
	'pointSize': False, 'ribbonHidesMainchain': False,
	'selLevel': False, 'showStubBonds': False,
	'stickScale': False, 'structureAssigned': False,
	'surfaceOpacity': False, 'vdwDensity': False,
	'clipThickness': False, 'aromaticLines': False,
	'aromaticLineType': False, 'idatmValid': False,
	'lowerCaseChains': False, 'useClipPlane': False,
	'useClipThickness': False, 'aromaticMode': False,
	'aromaticDisplay': False
}

intTypes = [int, long]
floatTypes = [float]
import numpy
for bits in ["16", "32", "64", "128"]:
	for base in ["int", "uint"]:
		try:
			intTypes.append(getattr(numpy, base + bits))
		except AttributeError:
			pass
	try:
		floatTypes.append(getattr(numpy, "float" + bits))
	except AttributeError:
		pass
numericTypes = intTypes + floatTypes

registeredAttrs = {}
registeredAttrs[chimera.Atom] = {}
registeredAttrs[chimera.Residue] = {}
registeredAttrs[chimera.Model] = {}

MODE_RENDER = "Render"
MODE_SELECT = "Select"
Modes = [MODE_RENDER, MODE_SELECT]

attrsLabelMap = {
	ATTRS_ATOMS: "atoms",
	ATTRS_RESIDUES: "residues",
	ATTRS_MODELS: "models"
}
revAttrsLabelMap = {}
for k, v in attrsLabelMap.items():
	revAttrsLabelMap[v] = k
NO_ATTR = "choose attr"
NO_RENDER_DATA = "Choose attribute to show histogram"
NO_SELECT_DATA = "Choose attribute to show histogram/list"
MENU_VALUES_LABEL = "Values"

_LIST_NOVALUE = "(no value)"
class ShowAttrDialog(ModelessDialog):
	title = "Render/Select by Attribute"
	buttons = ('OK', 'Apply', 'Close')
	provideStatus = True
	name = "render/select attrs"
	help = "ContributedSoftware/render/render.html"

	dewormLabel = "non-worm"

	def __init__(self):
		self.models = []
		self.useableTypes = numericTypes
		self.additionalNumericTypes = () # boolean could be here instead
		self.additionalOtherTypes = (bool, basestring)
		self._attrVals = [None] * len(Modes)
		self._minVal = [None] * len(Modes)
		self._maxVal = [None] * len(Modes)
		ModelessDialog.__init__(self)

	def Apply(self):
		prefs[RESTRICT] = self.selRestrictVar.get()
		if self.modeNotebook.getcurselection() == MODE_SELECT:
			self._applySelect()
		else:
			fname = "_apply" + self.renderNotebook.getcurselection()
			getattr(self, fname)()

	def attrVals(self, mode=None):
		if mode is None:
			mode = self.modeNotebook.getcurselection()
		return self._attrVals[Modes.index(mode)]

	def configure(self, models=None, mode=None, attrsOf=None,
					attrName=None, fromMolListBox=False):
		curMenu = self._curAttrMenu()
		curAttr = curMenu.getvalue()
		curMode = self.modeNotebook.getcurselection()
		curTargetLabel = self.targetMenu.getvalue()
		curTarget = revAttrsLabelMap[curTargetLabel]
		if models != self.models and models is not None:
			newModels = None
			if fromMolListBox:
				from sets import Set
				oldSet = Set(self.models)
				newSet = Set(models)
				if newSet >= oldSet:
					newModels = newSet - oldSet
			else:
				self.molListBox.setvalue(models,
							doCallback=False)
			self.models = models
			self._populateAttrsMenus(newModels=newModels)
			if not models or (curAttr is None and attrName is None):
				# _populateAttrsMenu has knocked the menu
				# button off of "choose attr"; arrange for
				# it to be restored...
				attrName = NO_ATTR
			if (mode == curMode or mode is None) \
			and (attrsOf == curTarget or attrsOf is None) \
			and ([attrName] == curAttr or attrName is None):
				# no other changes
				if curAttr is not None:
					try:
						curMenu.invoke(curAttr)
					except ValueError:
						# attribute no longer present
						self._targetCB(curTargetLabel)

		if mode != curMode and mode is not None:
			self.modeNotebook.selectpage(mode)

		if attrsOf != curTarget and attrsOf is not None:
			self.targetMenu.invoke(attrsOf)

		# prevent attr menu winding up on "choose attr"
		# even in attrName specified
		if self._needRefreshAttrs:
			self.refreshAttrs()

		# if an attribute name is specified, probably want an update...
		if attrName is not None:
			if attrName == NO_ATTR:
				self._targetCB(curTargetLabel)
				self.refreshMenu.entryconfigure(
					MENU_VALUES_LABEL, state="disabled")
			else:
				target = attrsOf or curTarget
				if target == "atoms":
					seen = self.seenAtomAttrs
				elif target == "residues":
					seen = self.seenResAttrs
				else:
					seen = self.seenModelAttrs
				if attrName in seen:
					self._curAttrMenu().invoke([attrName])
				else:
					self._targetCB(curTargetLabel)
				self.refreshMenu.entryconfigure(
					MENU_VALUES_LABEL, state="normal")

	def fillInUI(self, parent):
		top = parent.winfo_toplevel()
		menubar = Tkinter.Menu(top, type="menubar", tearoff=False)
		top.config(menu=menubar)

		fileMenu = Tkinter.Menu(menubar)
		menubar.add_cascade(label="File", menu=fileMenu)
		fileMenu.add_command(label="Save Attributes...",
					command=self._saveAttr)
		scalingMenu = Tkinter.Menu(menubar)
		menubar.add_cascade(label="Scaling", menu=scalingMenu)
		self.scalingVar = Tkinter.StringVar(parent)
		self.scalingVar.set(prefs[SCALING])
		scalingMenu.add_radiobutton(label="Logarithmic", value="log",
			command=self._scalingCB, variable=self.scalingVar)
		scalingMenu.add_radiobutton(label="Linear", value="linear",
			command=self._scalingCB, variable=self.scalingVar)

		refreshMenu = Tkinter.Menu(menubar)
		self.refreshMenu = refreshMenu
		menubar.add_cascade(label="Refresh", menu=refreshMenu)
		refreshMenu.add_command(label="Menus",
						command=self.refreshAttrs)
		def _cmdCB():
			menu = self._curAttrMenu()
			menu.invoke(menu.getvalue())
		refreshMenu.add_command(label=MENU_VALUES_LABEL, command=_cmdCB)

		from chimera.tkgui import aquaMenuBar
		aquaMenuBar(menubar, parent, row = 0, columnspan = 2)

		self.targetMenu = Pmw.OptionMenu(parent, command=self._targetCB,
				items=attrsLabelMap.values(), labelpos='w',
				label_text="Attributes of")
		self.targetMenu.grid(row=1, column=0)

		from chimera.widgets import MoleculeScrolledListBox
		self._needRefreshAttrs = True
		self.molListBox = MoleculeScrolledListBox(parent,
				selectioncommand=lambda: self.configure(
				models=self.molListBox.getvalue(),
				fromMolListBox=True),
				listbox_selectmode="extended",
				labelpos="nw", label_text="Models")
		self.molListBox.grid(row=1, column=1, sticky="nsew")

		self.modeNotebook = Pmw.NoteBook(parent)
		self.modeNotebook.add(MODE_RENDER)
		self.modeNotebook.add(MODE_SELECT)
		self.modeNotebook.grid(row=2, column=0, columnspan=2,
								sticky="nsew")
		parent.rowconfigure(2, weight=1)
		parent.columnconfigure(1, weight=1)
		renderFrame = self.modeNotebook.page(MODE_RENDER)
		selectFrame = self.modeNotebook.page(MODE_SELECT)

		self.renderModelAttrsMenu = CascadeOptionMenu(renderFrame,
			command=lambda mi: self._compileAttrVals(ATTRS_MODELS,
			mi), labelpos='w', label_text="Attribute:")
		self.renderResAttrsMenu = CascadeOptionMenu(renderFrame,
			command=lambda mi: self._compileAttrVals(ATTRS_RESIDUES,
			mi), labelpos='w', label_text="Attribute:")
		self.renderAtomAttrsMenu = CascadeOptionMenu(renderFrame,
			command=lambda mi: self._compileAttrVals(ATTRS_ATOMS,
			mi), labelpos='w', label_text="Attribute:")
		self.selectModelAttrsMenu = CascadeOptionMenu(selectFrame,
			command=lambda mi: self._compileAttrVals(ATTRS_MODELS,
			mi), labelpos='w', label_text="Attribute:")
		self.selectResAttrsMenu = CascadeOptionMenu(selectFrame,
			command=lambda mi: self._compileAttrVals(ATTRS_RESIDUES,
			mi), labelpos='w', label_text="Attribute:")
		self.selectAtomAttrsMenu = CascadeOptionMenu(selectFrame,
			command=lambda mi: self._compileAttrVals(ATTRS_ATOMS,
			mi), labelpos='w', label_text="Attribute:")

		from CGLtk.Histogram import MarkedHistogram
		histKw = {
			'statusline': self.status,
			'minlabel': True,
			'maxlabel': True
		}
		if prefs[SCALING] == "log":
			histKw['scaling'] = 'logarithmic'
		else:
			histKw['scaling'] = 'linear'
		self.selFrames = []
		self.selHistFrame = Tkinter.Frame(selectFrame)
		self.selFrames.append(self.selHistFrame)
		self.selHistFrame.grid(row=1, column=0, sticky="nsew")
		self.selHistFrame.rowconfigure(0, weight=1)
		self.selHistFrame.columnconfigure(0, weight=1)
		self.selectHistogram = MarkedHistogram(self.selHistFrame,
			colorwell=False, showmarkerhelp=False, **histKw)
		self.selectHistogram['datasource'] = NO_SELECT_DATA
		self.selectHistogram.grid(row=0, column=0,
						columnspan=2, sticky="nsew")
		histKw['selectcallback'] = self._selMarkerCB
		self.renderHistogram = MarkedHistogram(renderFrame, **histKw)
		self.renderHistogram.grid(row=1, column=0, sticky="nsew")
		self.renderHistogram['datasource'] = NO_RENDER_DATA
		selModeTexts = ["between markers (inclusive)",
					"outside markers", "no value"]
		Tkinter.Label(self.selHistFrame, text="Select:").grid(
			row=1, rowspan=len(selModeTexts), column=0, sticky='e')
		self.selModeVar = Tkinter.IntVar(selectFrame)
		gridKw = { 'column': 1, 'sticky': 'w' }
		for i, text in enumerate(selModeTexts):
			b = Tkinter.Radiobutton(self.selHistFrame, text=text,
				value=i, variable=self.selModeVar)
			gridKw['row'] = i+1
			b.grid(**gridKw)
		self.selNoValueButtonInfo = (b, gridKw)
		self.selModeVar.set(0)

		self.selListFrame = Tkinter.Frame(selectFrame)
		self.selFrames.append(self.selListFrame)
		self.selListFrame.rowconfigure(0, weight=1)
		self.selListFrame.columnconfigure(0, weight=1)
		self.selectListBox = Pmw.ScrolledListBox(self.selListFrame,
					listbox_selectmode="multiple")
		self.selectListBox.grid(row=0, column=0, sticky="nsew")

		self.selBoolFrame = Tkinter.Frame(selectFrame)
		self.selFrames.append(self.selBoolFrame)
		self.selBoolVar = Tkinter.IntVar(selectFrame)
		self.selBoolVar.set(True)
		self.boolButtons = []
		for label in ["False", "True", "No value"]:
			self.boolButtons.append(Tkinter.Radiobutton(
						self.selBoolFrame, text=label,
						value=len(self.boolButtons),
						variable=self.selBoolVar))
			self.boolButtons[-1].grid(row=len(self.boolButtons)-1,
						column=0, sticky='w')

		renderFrame.rowconfigure(1, weight=1)
		renderFrame.columnconfigure(0, weight=1)
		selectFrame.rowconfigure(1, weight=1)
		selectFrame.columnconfigure(0, weight=1)

		self.renderColorMarkers = self.renderHistogram.addmarkers(
					activate=True, coordtype='relative')
		if len(prefs[COLORS]) == 1:
			self.renderColorMarkers.append(
						((0.5, 0.0), prefs[COLORS][0]))
		else:
			self.renderColorMarkers.extend(map(lambda e: ((e[0] /
				float(len(prefs[COLORS]) - 1), 0.0), e[1]),
				enumerate(prefs[COLORS])))
		self.renderRadiiMarkers = self.renderHistogram.addmarkers(
				newcolor='slate gray', activate=False,
				coordtype='relative')
		if len(prefs[ATOM_RADII]) == 1:
			self.renderRadiiMarkers.append(((0.5, 0.0), None))
		else:
			self.renderRadiiMarkers.extend(map(lambda e: ((e[0] /
				float(len(prefs[ATOM_RADII]) - 1), 0.0),
				None), enumerate(prefs[ATOM_RADII])))
		for i, rad in enumerate(prefs[ATOM_RADII]):
			self.renderRadiiMarkers[i].radius = rad
		self.renderWormsMarkers = self.renderHistogram.addmarkers(
			newcolor='pink', activate=False, coordtype='relative')
		if len(prefs[WORM_RADII]) == 1:
			self.renderWormsMarkers.append(((0.5, 0.0), None))
		else:
			self.renderWormsMarkers.extend(map(lambda e: ((e[0] /
				float(len(prefs[WORM_RADII]) - 1), 0.0),
				None), enumerate(prefs[WORM_RADII])))
		for i, rad in enumerate(prefs[WORM_RADII]):
			self.renderWormsMarkers[i].radius = rad
		self.selectMarkers = self.selectHistogram.addmarkers(
				coordtype='relative', minmarks=2, maxmarks=2)
		selMarkerColor = (0.0, 1.0, 0.0)
		self.selectMarkers.extend([((0.333, 0.0), selMarkerColor),
						((0.667, 1.0), selMarkerColor)])

		f = self.renderHistogram.component('widgetframe')
		self.radiusEntry = Pmw.EntryField(f, labelpos='w',
				validate={ 'validator': 'real', 'min': 0.001 },
				entry_width=7, entry_state='disabled')
		self.entryColumn = int(f.grid_size()[1])

		self.renderNotebook = Pmw.NoteBook(renderFrame)
		self.renderNotebook.add("Colors")
		self.renderNotebook.add("Radii")
		self.renderNotebook.add("Worms")
		self.renderNotebook.grid(row=2, column=0)

		self.selRestrictVar = Tkinter.IntVar(parent)
		self.selRestrictVar.set(prefs[RESTRICT])
		srbut = Tkinter.Checkbutton(renderFrame,
			variable=self.selRestrictVar,
			text="Restrict OK/Apply to current selection, if any")
		srbut.grid(row=3, column=0)

		f = self.renderNotebook.page("Colors")
		self.colorAtomsVar = Tkinter.IntVar(f)
		self.colorAtomsVar.set(prefs[COLOR_ATOMS])
		self.colorAtomsButton = Tkinter.Checkbutton(f, pady=0,
			text="Color atoms", variable=self.colorAtomsVar)
		self.colorAtomsButton.grid(row=0, column=0, sticky="w")
		self.opaqueAtomsVar = Tkinter.IntVar(f)
		self.opaqueAtomsVar.set(True)
		self.opaqueAtomsButton = Tkinter.Checkbutton(f, pady=0,
			text="Keep opaque", variable=self.opaqueAtomsVar)
		self.opaqueAtomsButton.grid(row=0, column=1)

		self.colorRibbonsVar = Tkinter.IntVar(f)
		self.colorRibbonsVar.set(prefs[COLOR_RIBBONS])
		self.colorRibbonsButton = Tkinter.Checkbutton(f, pady=0,
			text="Color ribbons", variable=self.colorRibbonsVar)
		self.colorRibbonsButton.grid(row=1, column=0, sticky='w')
		self.opaqueRibbonsVar = Tkinter.IntVar(f)
		self.opaqueRibbonsVar.set(True)
		self.opaqueRibbonsButton = Tkinter.Checkbutton(f, pady=0,
			text="Keep opaque", variable=self.opaqueRibbonsVar)
		self.opaqueRibbonsButton.grid(row=1, column=1)

		self.colorSurfacesVar = Tkinter.IntVar(f)
		self.colorSurfacesVar.set(prefs[COLOR_SURFACES])
		self.colorSurfacesButton = Tkinter.Checkbutton(f, pady=0,
			text="Color surfaces", variable=self.colorSurfacesVar)
		self.colorSurfacesButton.grid(row=2, column=0, sticky='w')

		from CGLtk.color.ColorWell import ColorWell
		self.noValueColorsFrame = Tkinter.Frame(f)
		self.noValueColorsFrame.gridKw = { "row": 3, "column": 0,
							"columnspan": 2 }
		self.noValueColorsFrame.grid(**self.noValueColorsFrame.gridKw)
		Tkinter.Label(self.noValueColorsFrame, text='No-value color:'
					).grid(row=0, column=0, sticky='e')
		self.noValueWell = ColorWell(self.noValueColorsFrame,
								noneOkay=True)
		self.noValueWell.grid(row=0, column=1, sticky='w')

		self.colorKeyButton = Tkinter.Button(f, pady=0, text=
			"Create corresponding color key", state="disabled",
			command=self._colorKeyCB)
		self.colorKeyButton.grid(row=4, column=0, columnspan=2)

		f = self.renderNotebook.page("Radii")
		from chimera.tkoptions import SymbolicEnumOption, \
						FloatOption, BooleanOption
		class AtomStyleOption(SymbolicEnumOption):
			labels = ["ball", "sphere"]
			values = [chimera.Atom.Ball, chimera.Atom.Sphere]
		self.atomStyle = AtomStyleOption(f, 0, "Atom style",
				prefs[ATOM_STYLE], None, balloon=
				"How affected atoms will be depicted")
		self.doNoValueRadii = BooleanOption(f, 1,
			"Affect no-value atoms", False, None, balloon=
			"Set radii for atoms not having this attribute\n"
			"or leave them as is")
		class RadiiOption(FloatOption):
			min = 0.001
		self.noValueRadii = RadiiOption(f, 2, "No-value radius",
			prefs[NOVAL_RADIUS], None, balloon=
			"Atoms without this attribute will be given this radius")

		f = self.renderNotebook.page("Worms")
		self.wormsWarning = Tkinter.Label(f, text=
			"Worms can only be used in\n"
			"conjunction with residue or model\n"
			"attributes.  (Atom attributes are\n"
			"currently selected)")
		self.wormsWarning.grid() # for later setnaturalsize

		self.wormsFrame = Tkinter.Frame(f)
		from chimera.tkoptions import EnumOption
		class WormStyleOption(EnumOption):
			values = ["smooth", "segmented", self.dewormLabel]
		self.wormStyle = WormStyleOption(self.wormsFrame, 0,
			"Worm style", prefs[WORM_STYLE], lambda o:
			self.renderNotebook.setnaturalsize(), balloon=
			"How worm radius changes between residues:\n"
			"   smooth: radius changes smoothly\n"
			"   segmented: radius changes abruptly")
		self.wormStyle.menu.entryconfigure(self.dewormLabel,
							state="disabled")
		self.doNoValueWorm = BooleanOption(self.wormsFrame, 1,
			"Affect no-value residues", False, None, balloon=
			"Change worm representation for residues not having\n"
			"this attribute or leave them as is")
		self.noValueWorm = RadiiOption(self.wormsFrame, 2,
			"No-value worm radius", prefs[NOVAL_WORM], None,
			balloon="Residues without this attribute will\n"
			"be given this radius")
		self.renderNotebook.configure(raisecommand=self._raisePageCB)

		self._wormsOkApply = True
		self._attrOkApply = True
		self.renderNotebook.setnaturalsize()
		self.modeNotebook.setnaturalsize()

		self.targetMenu.invoke(attrsLabelMap[prefs[TARGET]])
		
	def histogram(self, frame=False):
		if self.modeNotebook.getcurselection() == MODE_RENDER:
			return self.renderHistogram
		if frame:
			return self.selHistFrame
		return self.selectHistogram

	def maxVal(self, mode=None):
		if mode is None:
			mode = self.modeNotebook.getcurselection()
		return self._maxVal[Modes.index(mode)]

	def minVal(self, mode=None):
		if mode is None:
			mode = self.modeNotebook.getcurselection()
		return self._minVal[Modes.index(mode)]

	def refreshAttrs(self):
		if not self.uiMaster().winfo_ismapped():
			# model-list widget is sleeping, delay update...
			self._needRefreshAttrs = True
			return
		self._needRefreshAttrs = False
		curMenu = self._curAttrMenu()
		curAttr = curMenu.getvalue()
		self._populateAttrsMenus()
		try:
			curMenu.index(curAttr)
		except ValueError:
			# attribute no longer present
			self._targetCB(self.targetMenu.getvalue())

	def _applyColors(self):
		colorAtoms = self.colorAtomsVar.get()
		opaqueAtoms = self.opaqueAtomsVar.get()
		colorRibbons = self.colorRibbonsVar.get()
		opaqueRibbons = self.opaqueRibbonsVar.get()
		colorSurfaces = self.colorSurfacesVar.get()
		if colorSurfaces:
			from chimera.actions import changeSurfsFromCustom
			changeSurfsFromCustom(self.models)
		target = revAttrsLabelMap[self.targetMenu.getvalue()]
		if not colorAtoms and not colorSurfaces and not (
				colorRibbons and target != ATTRS_ATOMS):
			raise chimera.UserError(
				"Nothing chosen to receive attribute coloring!")
		prefs[COLOR_ATOMS] = colorAtoms
		prefs[COLOR_RIBBONS] = colorRibbons
		prefs[COLOR_SURFACES] = colorSurfaces

		self.status("Coloring atoms/ribbons\n", blankAfter=0)
		def makeColors(rgba):
			c = chimera.MaterialColor(*rgba)
			if rgba[-1] < 1.0:
				orgba = rgba[:3] + [1.0]
				oc = chimera.MaterialColor(*orgba)
			else:
				oc = c
			colors[val] = (c, oc)
			return c, oc
		colors = {}
		restrict = prefs[RESTRICT]
		if restrict:
			if target == ATTRS_ATOMS:
				filterItems = selection.currentAtoms()
			elif target == ATTRS_RESIDUES:
				filterItems = selection.currentResidues()
			else:
				filterItems = selection.currentMolecules(
								asDict=True)
			if not filterItems:
				restrict = False
		from operator import add
		if target == ATTRS_ATOMS:
			attrMenu = self.renderAtomAttrsMenu
			if restrict:
				mDict = {}
				for m in self.models:
					mDict[m] = 1
				items = filter(lambda a: a.molecule in mDict,
								filterItems)
			else:
				items = []
				for model in self.models:
					items.extend(model.atoms)
			def colorItem(c, oc):
				if colorAtoms:
					if opaqueAtoms:
						item.color = oc
					else:
						item.color = c
				if colorSurfaces:
					item.surfaceColor = c
					item.surfaceOpacity = -1
					item.vdwColor = c
		elif target == ATTRS_RESIDUES:
			attrMenu = self.renderResAttrsMenu
			subfunc = lambda r: r.oslChildren()
			if restrict:
				mDict = {}
				for m in self.models:
					mDict[m] = 1
				items = filter(lambda r: r.molecule in mDict,
								filterItems)
			else:
				items = []
				for model in self.models:
					items.extend(model.residues)
			def colorItem(c, oc):
				if colorRibbons:
					if opaqueRibbons:
						item.ribbonColor = oc
					else:
						item.ribbonColor = c
				if colorAtoms or colorSurfaces:
					for a in item.atoms:
						if colorAtoms:
							if opaqueAtoms:
								a.color=oc
							else:
								a.color=c
						if colorSurfaces:
							a.surfaceColor=c
							a.surfaceOpacity = -1
							a.vdwColor=c
		else:
			attrMenu = self.renderModelAttrsMenu
			subfunc = lambda m: m.residues
			if restrict:
				items = filter(lambda m: m in filterItems,
								self.models)
			else:
				items = self.models
			def colorItem(c, oc):
				if colorRibbons:
					for r in item.residues:
						if opaqueRibbons:
							r.ribbonColor = oc
						else:
							r.ribbonColor = c
				if colorAtoms or colorSurfaces:
					for a in item.atoms:
						if colorAtoms:
							if opaqueAtoms:
								a.color = oc
							else:
								a.color = c
						if colorSurfaces:
							a.surfaceColor = c
							a.surfaceOpacity = -1
							a.vdwColor = c
		attrName = attrMenu.getvalue()
		if len(attrName) == 1:
			doSubitems = False
		else:
			doSubitems = True
		attrName = attrName[-1]
		self.renderColorMarkers['coordtype'] = 'absolute'
		noValRgba = self.noValueWell.rgba
		for item in items:
			if doSubitems:
				# an average/sum
				vals = []
				for sub in subfunc(item):
					try:
						val = getattr(sub, attrName)
					except AttributeError:
						continue
					if val is not None:
						vals.append(val)
				if vals:
					val = reduce(add, vals)
					if not summableAttrName(attrName):
						val /= float(len(vals))
				else:
					val = None
			else:
				try:
					val = getattr(item, attrName)
				except AttributeError:
					val = None

			if val is None:
				if noValRgba is not None:
					if None in colors:
						c, oc = colors[None]
					else:
						c, oc = makeColors(noValRgba)
					colorItem(c, oc)
				continue
			if len(self.renderColorMarkers) == 0:
				continue
			for i, marker in enumerate(self.renderColorMarkers):
				if val <= self._markerVal(marker):
					break
			else:
				i = len(self.renderColorMarkers)
			if i == 0:
				val = self._markerVal(
						self.renderColorMarkers[0])
				i = 1
			elif i == len(self.renderColorMarkers):
				val = self._markerVal(
						self.renderColorMarkers[-1])
				i -= 1;
			if val in colors:
				colorItem(*colors[val])
				continue
			if len(self.renderColorMarkers) > 1:
				left, right = map(lambda m:
					(self._markerVal(m), m['rgba']),
					self.renderColorMarkers[i-1:i+1])
				lval, lrgba = left
				rval, rrgba = right
				if rval == lval:
					pos = 0.5
				else:
					pos = (val - lval) / float(rval - lval)
				rgba = map(lambda l, r: l*(1 - pos) + r*pos,
								lrgba, rrgba)
			else:
				rgba = self.renderColorMarkers[0]['rgba']
			c, oc = makeColors(rgba)
			colorItem(c, oc)
		self.renderColorMarkers['coordtype'] = 'relative'
		self.status("Done setting colors\n")

	def _applyRadii(self):
		markers, marker = self.renderHistogram.currentmarkerinfo()
		if marker is not None:
			self._setRadius(marker)
		noValRadius = self.noValueRadii.get()
		doNoVal = self.doNoValueRadii.get()
		prefs[ATOM_RADII] = map(lambda m: m.radius,
						self.renderRadiiMarkers[:])
		prefs[ATOM_STYLE] = self.atomStyle.get()

		target = revAttrsLabelMap[self.targetMenu.getvalue()]

		self.status("Setting atomic radii\n", blankAfter=0)

		restrict = prefs[RESTRICT]
		if restrict:
			curSel = selection.currentAtoms(asDict=True)
			if not curSel:
				restrict = False
		from operator import add
		style = prefs[ATOM_STYLE]
		if target == ATTRS_ATOMS:
			attrMenu = self.renderAtomAttrsMenu
			items = []
			for model in self.models:
				items.extend(model.atoms)
			if restrict:
				def setRad(rad):
					if item in curSel:
						item.radius = rad
						item.drawMode = style
			else:
				def setRad(rad):
					item.radius = rad
					item.drawMode = style
		elif target == ATTRS_RESIDUES:
			attrMenu = self.renderResAttrsMenu
			subfunc = lambda r: r.oslChildren()
			items = []
			for model in self.models:
				items.extend(model.residues)
			if restrict:
				def setRad(rad):
					for a in item.atoms:
						if a in curSel:
							a.radius = rad
							a.drawMode = style
			else:
				def setRad(rad):
					for a in item.atoms:
						a.radius = rad
						a.drawMode = style
		else:
			attrMenu = self.renderModelAttrsMenu
			subfunc = lambda m: m.residues
			if restrict:
				selMols = selection.currentMolecules(
								asDict=True)
				items = filter(lambda m: m in selMols,
								self.models)
				def setRad(rad):
					for a in item.atoms:
						if a in curSel:
							a.radius = rad
							a.drawMode = style
			else:
				items = self.models
				def setRad(rad):
					for a in item.atoms:
						a.radius = rad
						a.drawMode = style
		attrName = attrMenu.getvalue()
		if len(attrName) == 1:
			doSubitems = False
		else:
			doSubitems = True
		attrName = attrName[-1]
		radMarkers = self.renderRadiiMarkers
		radMarkers['coordtype'] = 'absolute'
		for item in items:
			if doSubitems:
				# an average/sum
				vals = []
				for sub in subfunc(item):
					try:
						val = getattr(sub, attrName)
					except AttributeError:
						continue
					if val is not None:
						vals.append(val)
				if vals:
					val = reduce(add, vals)
					if not summableAttrName(attrName):
						val /= float(len(vals))
				else:
					val = None
			else:
				try:
					val = getattr(item, attrName)
				except AttributeError:
					val = None

			if val is None:
				if doNoVal:
					setRad(noValRadius)
				continue
			if len(radMarkers) == 0:
				continue
			for i, marker in enumerate(radMarkers):
				if val <= self._markerVal(marker):
					break
			else:
				i = len(radMarkers)
			if i == 0:
				rad = radMarkers[0].radius
			elif i == len(radMarkers):
				rad = radMarkers[-1].radius
			elif len(radMarkers) > 1:
				left, right = map(self._markerVal,
						radMarkers[i-1:i+1])
				if right == left:
					pos = 0.5
				else:
					pos = (val - left) / float(right - left)
				rad = radMarkers[i-1].radius * (1 -
					pos) + radMarkers[i].radius * pos
			else:
				rad = radMarkers[0].radius
			setRad(rad)
		radMarkers['coordtype'] = 'relative'
		self.status("Done setting radii\n")

	def _applyWorms(self):
		markers, marker = self.renderHistogram.currentmarkerinfo()
		if marker is not None:
			self._setRadius(marker)
		noValRadius = self.noValueWorm.get()
		doNoVal = self.doNoValueWorm.get()
		wormStyleName = self.wormStyle.get()
		prefs[NOVAL_WORM] = noValRadius
		if wormStyleName == self.dewormLabel:
			# revert the style menu to the worm style
			self.wormStyle.set(prefs[WORM_STYLE])
		else:
			prefs[WORM_STYLE] = wormStyleName
		prefs[ATOM_RADII] = map(lambda m: m.radius,
						self.renderWormsMarkers[:])
		self.wormStyle.menu.entryconfigure(self.dewormLabel,
							state="normal")

		target = revAttrsLabelMap[self.targetMenu.getvalue()]

		self.status("Setting worm radii\n", blankAfter=0)

		restrict = prefs[RESTRICT]
		if restrict:
			curSel = selection.currentResidues(asDict=True)
			if not curSel:
				restrict = False
		styles = {}
		def style(rad):
			if wormStyleName == "smooth":
				# can't cache -- each different
				return chimera.RibbonStyleWorm([rad])
			elif wormStyleName == self.dewormLabel:
				return None
			if rad not in styles:
				styles[rad] = chimera.RibbonStyleFixed([rad,
									rad])
			return styles[rad]
		def wormResidue(item, rad):
			if restrict and item not in curSel:
				return
			item.ribbonDrawMode = chimera.Residue.Ribbon_Round
			item.ribbonDisplay = True
			item.ribbonStyle = style(rad)
		def wormModel(item, rad):
			for r in item.residues:
				wormResidue(r, rad)
		from operator import add
		if target == ATTRS_ATOMS:
			raise AssertionError, "Cannot worms with atoms target"
		elif target == ATTRS_RESIDUES:
			attrMenu = self.renderResAttrsMenu
			subfunc = lambda r: r.oslChildren()
			items = []
			for model in self.models:
				items.extend(model.residues)
			wormFunc = wormResidue
		else:
			attrMenu = self.renderModelAttrsMenu
			subfunc = lambda m: m.residues
			wormFunc = wormModel
			items = self.models
		attrName = attrMenu.getvalue()
		if len(attrName) == 1:
			doSubitems = False
		else:
			doSubitems = True
		attrName = attrName[-1]
		radMarkers = self.renderWormsMarkers
		radMarkers['coordtype'] = 'absolute'
		for item in items:
			if doSubitems:
				# an average/sum
				vals = []
				for sub in subfunc(item):
					try:
						val = getattr(sub, attrName)
					except AttributeError:
						continue
					if val is not None:
						vals.append(val)
				if vals:
					val = reduce(add, vals)
					if not summableAttrName(attrName):
						val /= float(len(vals))
				else:
					val = None
			else:
				try:
					val = getattr(item, attrName)
				except AttributeError:
					val = None

			if val is None:
				if doNoVal:
					wormFunc(item, noValRadius)
				continue
			if len(radMarkers) == 0:
				continue
			for i, marker in enumerate(radMarkers):
				if val <= self._markerVal(marker):
					break
			else:
				i = len(radMarkers)
			if i == 0:
				rad = radMarkers[0].radius
			elif i == len(radMarkers):
				rad = radMarkers[-1].radius
			elif len(radMarkers) > 1:
				left, right = map(self._markerVal,
						radMarkers[i-1:i+1])
				if right == left:
					pos = 0.5
				else:
					pos = (val - left) / float(right - left)
				rad = radMarkers[i-1].radius * (1 -
					pos) + radMarkers[i].radius * pos
			else:
				rad = radMarkers[0].radius
			wormFunc(item, rad)
		radMarkers['coordtype'] = 'relative'
		self.status("Done setting radii\n")

	def _applySelect(self):
		self.status("Selecting atoms/residues\n", blankAfter=0)
		from operator import add
		target = revAttrsLabelMap[self.targetMenu.getvalue()]
		if target == ATTRS_ATOMS:
			attrMenu = self.selectAtomAttrsMenu
			items = []
			for model in self.models:
				items.extend(model.atoms)
		elif target == ATTRS_RESIDUES:
			attrMenu = self.selectResAttrsMenu
			subfunc = lambda r: r.oslChildren()
			items = []
			for model in self.models:
				items.extend(model.residues)
		else:
			attrMenu = self.selectModelAttrsMenu
			subfunc = lambda m: m.residues
			items = self.models
		attrName = attrMenu.getvalue()
		if len(attrName) == 1:
			doSubitems = False
		else:
			doSubitems = True
		attrName = attrName[-1]
		usingHist = False
		if self.selHistFrame.winfo_manager():
			usingHist = True
			selMode = self.selModeVar.get()
			self.selectMarkers['coordtype'] = 'absolute'
			if selMode < 2:
				m1, m2 = map(lambda m: self._markerVal(m),
							self.selectMarkers)
				if selMode == 0:
					selFunc = lambda v: v >= m1 and v <= m2
				else:
					selFunc = lambda v: v < m1 or v > m2
			else:
				selFunc = lambda v: False
		elif self.selListFrame.winfo_manager():
			selMode = 0 # i.e. not selecting None
			selValues = {}
			for v in self.selectListBox.getvalue():
				if v == _LIST_NOVALUE:
					selMode = 2 # selecting None
					continue
				selValues[v] = 1
			selFunc = lambda v: v in selValues
		else:
			# since it just so happens that the only relevant
			# value for selMode in the later code is 2...
			selMode = self.selBoolVar.get()
			selFunc = lambda v: v == selMode
		sels = []
		for item in items:
			if doSubitems:
				# an average/sum
				vals = []
				for sub in subfunc(item):
					try:
						val = getattr(sub, attrName)
					except AttributeError:
						continue
					if val is not None:
						vals.append(val)
				if vals:
					val = reduce(add, vals)
					if not summableAttrName(attrName):
						val /= float(len(vals))
				else:
					val = None
			else:
				try:
					val = getattr(item, attrName)
				except AttributeError:
					val = None

			if val is None:
				if selMode == 2:
					sels.append(item)
				continue
			if selFunc(val):
				sels.append(item)
		from chimera.selection import ItemizedSelection
		sel = ItemizedSelection()
		sel.add(sels)
		sel.addImplied()
		from chimera.tkgui import selectionOperation
		selectionOperation(sel)
		if usingHist:
			self.selectMarkers['coordtype'] = 'relative'
		self.status("Done selecting atoms/residues\n")

	def _colorKeyCB(self, *args):
		if len(self.renderColorMarkers) < 2:
			raise chimera.UserError("Need at least two color bars"
				" in histogram to create key")
		prevCoordType = self.renderColorMarkers['coordtype']
		self.renderColorMarkers['coordtype'] = 'absolute'
		from Ilabel.gui import IlabelDialog
		from chimera import dialogs
		d = dialogs.display(IlabelDialog.name)
		d.keyConfigure([(m['rgba'], "%g" % self._markerVal(m))
					for m in self.renderColorMarkers])
		self.renderColorMarkers['coordtype'] = prevCoordType

	def _compileAttrVals(self, targetName, menuItem):
		self.status("Surveying attribute %s\n" % " ".join(menuItem),
								blankAfter=0)
		attrVals = []
		if targetName == ATTRS_MODELS:
			surveyed = self.models
		else:
			surveyed = []
			for m in self.models:
				surveyed.extend(getattr(m, targetName))
		attrName = menuItem[-1]
		hasNone = False
		if len(menuItem) == 1:
			for t in surveyed:
				try:
					val = getattr(t, attrName)
				except AttributeError:
					hasNone = True
					continue
				if val is None or (isinstance(val, basestring)
								and not val):
					hasNone = True
					continue
				attrVals.append(val)
		else:
			# average/sum of atoms/residues
			from operator import add
			if targetName == ATTRS_MODELS:
				subfunc = lambda m: m.residues
			else:
				subfunc = lambda r: r.oslChildren()
			for t in surveyed:
				vals = []
				for sub in subfunc(t):
					try:
						val = getattr(sub, attrName)
					except AttributeError:
						continue
					if val is None \
					or (isinstance(val, basestring)
								and not val):
						continue
					vals.append(val)
				if not vals:
					hasNone = True
					continue
				val = reduce(add, vals)
				if not summableAttrName(attrName):
					val /= float(len(vals))
				attrVals.append(val)
		self.status("Done surveying\n")
		self._attrOkApply = True
		self._setAttrVals(attrVals)
		for frame in self.selFrames:
			frame.grid_forget()
		if attrVals and isinstance(attrVals[0], basestring):
			frame = self.selListFrame
			uniqueVals = {}
			for av in attrVals:
				uniqueVals[av] = 1
			listItems = uniqueVals.keys()
			listItems.sort(lambda a, b: cmp(a.lower(), b.lower()))
			if hasNone:
				listItems.append(_LIST_NOVALUE)
			self.selectListBox.setlist(listItems)
		elif attrVals and isinstance(attrVals[0], bool):
			frame = self.selBoolFrame
			self.boolButtons[-1].grid_forget()
			if hasNone:
				self.boolButtons[-1].grid(
						row=len(self.boolButtons)-1,
						column=0, sticky='w')
			elif self.selBoolVar.get() == 2:
				self.selBoolVar.set(True)
		else:
			frame = self.selHistFrame
			if not attrVals:
				self.histogram()['datasource'] = \
					"No attribute '%s' in any %s" % (
							attrName, targetName)
				self._attrOkApply = False
			elif self.minVal() == self.maxVal():
				self.histogram()['datasource'] = \
					"attribute has only one value: %s" \
							% str(self.minVal())
				self._attrOkApply = False
			else:
				self.histogram()['datasource'] = (self.minVal(),
					self.maxVal(), lambda numBins, mode=
					self.modeNotebook.getcurselection(): self._makeBins(numBins, mode=mode))
			if hasNone:
				but, gridKw = self.selNoValueButtonInfo
				but.grid(**gridKw)
			else:
				self.selNoValueButtonInfo[0].grid_forget()
		if hasNone:
			self.noValueColorsFrame.grid(
					**self.noValueColorsFrame.gridKw)
			self.doNoValueRadii.gridManage()
			self.noValueRadii.gridManage()
			self.doNoValueWorm.gridManage()
			self.noValueWorm.gridManage()
		else:
			self.noValueColorsFrame.grid_forget()
			self.doNoValueRadii.gridUnmanage()
			self.noValueRadii.gridUnmanage()
			self.doNoValueWorm.gridUnmanage()
			self.noValueWorm.gridUnmanage()
		self.renderNotebook.setnaturalsize()
		frame.grid(row=1, column=0, sticky="nsew")
		if self._wormsOkApply and self._attrOkApply:
			self.buttonWidgets['OK'].configure(state='normal')
			self.buttonWidgets['Apply'].configure(state='normal')
			self.colorKeyButton.configure(state='normal')
		else:
			self.buttonWidgets['OK'].configure(state='disabled')
			self.buttonWidgets['Apply'].configure(state='disabled')
			self.colorKeyButton.configure(state='disabled')
		self.refreshMenu.entryconfigure(MENU_VALUES_LABEL,
								state="normal")

	def _composeAttrMenus(self):
		sortFunc = lambda a, b: cmp(a.lower(), b.lower())
		self.useableAtomAttrs.sort(sortFunc)
		self.useableResAttrs.sort(sortFunc)
		self.useableModelAttrs.sort(sortFunc)
		self.renderAtomAttrsMenu.setitems(self.useableAtomAttrs)
		self.renderResAttrsMenu.setitems(_menuItems(
				self.useableResAttrs, self.useableAtomAttrs))
		self.renderModelAttrsMenu.setitems(_menuItems(
				self.useableModelAttrs, self.useableResAttrs))

		# do this in a little bit of a weird order so that the 'average'
		# submenu only contains numeric quantities
		aggAtomAttrs = self.useableAtomAttrs \
					+ self.additionalNumericAtomAttrs
		aggResAttrs = self.useableResAttrs + \
					self.additionalNumericResAttrs
		aggModelAttrs = self.useableModelAttrs + \
					self.additionalNumericModelAttrs + \
					self.additionalOtherModelAttrs
		aggAtomAttrs.sort(sortFunc)
		aggResAttrs.sort(sortFunc)
		aggModelAttrs.sort(sortFunc)
		self.selectModelAttrsMenu.setitems(_menuItems(
						aggModelAttrs, aggResAttrs))
		aggResAttrs.extend(self.additionalOtherResAttrs)
		aggResAttrs.sort(sortFunc)
		self.selectResAttrsMenu.setitems(_menuItems(
						aggResAttrs, aggAtomAttrs))
		aggAtomAttrs.extend(self.additionalOtherAtomAttrs)
		aggAtomAttrs.sort(sortFunc)
		self.selectAtomAttrsMenu.setitems(aggAtomAttrs)

	def _curAttrMenu(self):
		target = revAttrsLabelMap[self.targetMenu.getvalue()]
		if self.modeNotebook.getcurselection() == MODE_RENDER:
			if target == ATTRS_ATOMS:
				return self.renderAtomAttrsMenu
			if target == ATTRS_RESIDUES:
				return self.renderResAttrsMenu
			if target == ATTRS_MODELS:
				return self.renderModelAttrsMenu
		else:
			if target == ATTRS_ATOMS:
				return self.selectAtomAttrsMenu
			if target == ATTRS_RESIDUES:
				return self.selectResAttrsMenu
			if target == ATTRS_MODELS:
				return self.selectModelAttrsMenu

	def _makeBins(self, numBins, mode):
		self.status("Computing histogram bins\n", blankAfter=0)
		minVal, maxVal = self.minVal(mode), self.maxVal(mode)
		if isinstance(minVal, int) and isinstance(maxVal, int) \
		and maxVal - minVal + 1 <= numBins / 3.0:
			# enough room to show bars instead of lines
			numBins = maxVal - minVal + 1
		bins = [0] * numBins
		vrange = maxVal - minVal
		binSize = vrange / float(numBins - 1)
		leftEdge = minVal - 0.5 * binSize
		for val in self.attrVals(mode):
			bin = int((val - leftEdge) / binSize)
			bins[bin] += 1
		self.status("Done computing histogram bins\n")
		return bins

	def _markerVal(self, marker):
		rawVal = marker['xy'][0]
		if isinstance(self.minVal(), int):
			return int(rawVal + 0.5)
		return rawVal

	def _populateAttrsMenus(self, newModels=None):
		self.status("Compiling attribute lists...\n", blankAfter=0)
		if newModels is None or not hasattr(self, 'seenAtomAttrs'):
			self.seenAtomAttrs = screenedAttrs[chimera.Atom].copy()
			self.seenResAttrs = screenedAttrs[chimera.Residue].copy()
			self.seenModelAttrs = screenedAttrs[chimera.Model].copy()
			self.useableAtomAttrs = []
			self.useableResAttrs = []
			self.useableModelAttrs = []
			self.additionalNumericAtomAttrs = []
			self.additionalNumericResAttrs = []
			self.additionalNumericModelAttrs = []
			self.additionalOtherAtomAttrs = []
			self.additionalOtherResAttrs = []
			self.additionalOtherModelAttrs = []
		if newModels is None:
			scanModels = self.models
		else:
			scanModels = newModels

		for m in scanModels:
			self.status("Compiling attribute lists from %s...\n"
					% m.name, blankAfter=0)
			self._reapAttrs(m, self.seenModelAttrs,
					self.useableModelAttrs,
					self.additionalNumericModelAttrs,
					self.additionalOtherModelAttrs)
			for a in m.atoms:
				self._reapAttrs(a, self.seenAtomAttrs,
						self.useableAtomAttrs,
						self.additionalNumericAtomAttrs,
						self.additionalOtherAtomAttrs)
			for r in m.residues:
				self._reapAttrs(r, self.seenResAttrs,
						self.useableResAttrs,
						self.additionalNumericResAttrs,
						self.additionalOtherResAttrs)
		self.status("Updating attribute menus...\n", blankAfter=0)
		self._composeAttrMenus()
		self.status("\n")

	def _raisePageCB(self, page):
		entryFrame = self.renderHistogram.component('widgetframe')
		if page == "Colors":
			markers = self.renderColorMarkers
			self.renderHistogram.configure(colorwell=True)
			self.radiusEntry.grid_forget()
			entryFrame.columnconfigure(self.entryColumn, weight=0)
		else:
			if page == "Radii":
				markers = self.renderRadiiMarkers
				self.radiusEntry.component('label').configure(
							text='Atom radius')
			else:
				markers = self.renderWormsMarkers
				self.radiusEntry.component('label').configure(
							text='Worm radius')
			self.renderHistogram.configure(colorwell=False)
			self.radiusEntry.grid(row=1, column=self.entryColumn)
			entryFrame.columnconfigure(self.entryColumn, weight=2)
		self.renderHistogram.activate(markers)
		self._wormsGUI()

	def _reapAttrs(self, instance, seenAttrs, useableAttrs,
				additionalNumericAttrs, additionalOtherAttrs):
		for attrName in dir(instance):
			attrType = seenAttrs.get(attrName, None)
			if isinstance(attrType, bool):
				continue
			elif attrType is None:
				if attrName[0] == '_' \
				or attrName[0].isupper():  # e.g. 'Ball'
					seenAttrs[attrName] = False
					continue
				attr = getattr(instance, attrName)
				if attr is None or (isinstance(attr, basestring)
								and not attr):
					# defer judgment until
					# we see a real value
					continue
				attrType = type(attr)
			else:
				attr = attrType()
			seenAttrs[attrName] = True
			if attrType in self.useableTypes:
				useableAttrs.append(attrName)
			elif attrType in self.additionalNumericTypes:
				additionalNumericAttrs.append(attrName)
			elif isinstance(attr, self.additionalOtherTypes):
				additionalOtherAttrs.append(attrName)

	def _scalingCB(self):
		scaling = self.scalingVar.get()
		prefs[SCALING] = scaling
		for histogram in [self.renderHistogram, self.selectHistogram]:
			if scaling == "log":
				histogram.configure(scaling="logarithmic")
			else:
				histogram.configure(scaling="linear")

	def _selMarkerCB(self, prevMarkers, prevMarker, markers, marker):
		if prevMarker and prevMarkers != self.renderColorMarkers:
			self._setRadius(prevMarker)
		if markers == self.renderColorMarkers:
			return
		self.radiusEntry.component('entry').configure(state='normal')
		if marker is None:
			self.radiusEntry.clear()
			self.radiusEntry.component('entry').configure(
							state='disabled')
			return
		if not hasattr(marker, "radius"):
			# new marker
			marker.radius = 1.0
		self.radiusEntry.setentry("%g" % marker.radius)

	def _setAttrVals(self, attrVals):
		index = Modes.index(self.modeNotebook.getcurselection())
		self._attrVals[index] = attrVals
		if attrVals and type(attrVals[0]) in numericTypes:
			self._minVal[index] = min(attrVals)
			self._maxVal[index] = max(attrVals)

	def _setRadius(self, marker):
		self.radiusEntry.invoke()
		if not self.radiusEntry.valid():
			self.status("Radius value not valid: '%s'" %
				self.radiusEntry.getvalue(), color='red')
			return
		marker.radius = float(self.radiusEntry.getvalue())

	def _targetCB(self, menuItem):
		self.renderModelAttrsMenu.grid_forget()
		self.renderResAttrsMenu.grid_forget()
		self.renderAtomAttrsMenu.grid_forget()
		self.selectModelAttrsMenu.grid_forget()
		self.selectResAttrsMenu.grid_forget()
		self.selectAtomAttrsMenu.grid_forget()
		self._wormsGUI()
		target = revAttrsLabelMap[menuItem]
		if target == ATTRS_ATOMS:
			menus = [self.renderAtomAttrsMenu,
						self.selectAtomAttrsMenu]
			ribbonState = "disabled"
		elif target == ATTRS_RESIDUES:
			menus = [self.renderResAttrsMenu,
						self.selectResAttrsMenu]
			ribbonState = "normal"
		else:
			menus = [self.renderModelAttrsMenu,
						self.selectModelAttrsMenu]
			ribbonState = "normal"
		for menu in menus:
			menu.grid(row=0, column=0, columnspan=2)
			menu.component('menubutton').config(text=NO_ATTR)
		for frame in self.selFrames:
			frame.grid_forget()
		for hg in [self.renderHistogram, self.selHistFrame]:
			hg.grid(row=1, column=0, sticky="nsew")
		self.renderHistogram['datasource'] = NO_RENDER_DATA
		self.selectHistogram['datasource'] = NO_SELECT_DATA
		self.colorRibbonsButton.config(state=ribbonState)
		self.opaqueRibbonsButton.config(state=ribbonState)
		self._attrOkApply = False
		self.buttonWidgets['OK'].configure(state='disabled')
		self.buttonWidgets['Apply'].configure(state='disabled')
		self.colorKeyButton.configure(state='disabled')

	def _wormsGUI(self):
		page = self.renderNotebook.getcurselection()
		if page == "Worms":
			if revAttrsLabelMap[self.targetMenu.getvalue()] \
								== ATTRS_ATOMS:
				self.wormsFrame.grid_forget()
				self.wormsWarning.grid()
				self._wormsOkApply = False
				self.buttonWidgets['OK'].configure(
							state='disabled')
				self.buttonWidgets['Apply'].configure(
							state='disabled')
				self.colorKeyButton.configure(state='disabled')
				return
		self.wormsWarning.grid_forget()
		self.wormsFrame.grid()
		self.renderNotebook.setnaturalsize()
		self._wormsOkApply = True
		if self._attrOkApply:
			self.buttonWidgets['OK'].configure(state='normal')
			self.buttonWidgets['Apply'].configure(state='normal')
			self.colorKeyButton.configure(state='normal')

	def _saveAttr(self):
		from chimera import dialogs
		d = dialogs.find("SaveAttrDialog", create=True)
		attrList = self._curAttrMenu().getvalue()
		if attrList:
			attrName = attrList[0]
		else:
			attrName = None
		d.configure(models=self.molListBox.getvalue(),
				attrsOf=self.targetMenu.getvalue(),
				attrName=attrName)
		d.enter()

from chimera import dialogs
dialogs.register(ShowAttrDialog.name, ShowAttrDialog)

from OpenSave import SaveModeless
class SaveAttrDialog(SaveModeless):
	title = "Save Attribute"
	name = "SaveAttrDialog"
	help = "ContributedSoftware/render/render.html#saving"

	def __init__(self, *args, **kw):
		self.havePaths = False
		self.models = []
		self.useableTypes = numericTypes
		self.additionalNumericTypes = () # boolean could be here instead
		self.additionalOtherTypes = (bool, basestring)
		SaveModeless.__init__(self, clientPos="s", clientSticky="nsew",
					*args, **kw)

	def fillInUI(self, parent):
		self.targetMenu = None
		self.molListBox = None
		SaveModeless.fillInUI(self, parent)
		g = Pmw.Group(self.clientArea, tag_text="Attribute to Save")
		g.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)

		f = Tkinter.Frame(g.interior())
		f.pack(side=Tkinter.TOP, expand=Tkinter.FALSE, fill=Tkinter.X)
		self.modelAttrsMenu = CascadeOptionMenu(f,
			command=lambda mi: self._compileAttrVals(ATTRS_MODELS, mi),
			labelpos='w', label_text="Attribute:")
		self.resAttrsMenu = CascadeOptionMenu(f,
			command=lambda mi: self._compileAttrVals(ATTRS_RESIDUES,
			mi), labelpos='w', label_text="Attribute:")
		self.atomAttrsMenu = CascadeOptionMenu(f,
			command=lambda mi: self._compileAttrVals(ATTRS_ATOMS,
			mi), labelpos='w', label_text="Attribute:")
		self.atomAttrsMenu.grid(row=0, column=0)
		self.targetMenu = Pmw.OptionMenu(f, command=self._targetCB,
				items=attrsLabelMap.values(), labelpos='w',
				label_text=" of")
		self.targetMenu.grid(row=0, column=1)

		self.includeModelVar = Tkinter.IntVar(g.interior())
		self.includeModelVar.set(0)
		self.includeModelButton = Tkinter.Checkbutton(g.interior(),
			pady=0, text="Include model numbers in output",
			variable=self.includeModelVar)
		self.includeModelButton.pack(side=Tkinter.BOTTOM)

		self.saveSelectionVar = Tkinter.IntVar(g.interior())
		self.saveSelectionVar.set(0)
		self.saveSelectionButton = Tkinter.Checkbutton(g.interior(),
			pady=0,
			text="Restrict save to current selection, if any",
			variable=self.saveSelectionVar)
		self.saveSelectionButton.pack(side=Tkinter.BOTTOM)

		from chimera.widgets import MoleculeScrolledListBox
		self.molListBox = MoleculeScrolledListBox(g.interior(),
				selectioncommand=lambda: self.configure(
				models=self.molListBox.getvalue(),
				fromMolListBox=True),
				listbox_selectmode="extended",
				labelpos="nw", label_text="Models")
		self.molListBox.pack(side=Tkinter.BOTTOM, expand=Tkinter.TRUE,
					fill=Tkinter.BOTH)

		self.targetMenu.invoke(attrsLabelMap[prefs[TARGET]])

	def Apply(self):
		paths = self.getPaths(remember=False)
		filename = paths[0]
		models = self.molListBox.getvalue()
		if not models:
			raise chimera.UserError("No models selected")

		restrict = (self.saveSelectionVar.get()
				and not selection.currentEmpty())
		target = revAttrsLabelMap[self.targetMenu.getvalue()]
		if target == ATTRS_ATOMS:
			menu = self.atomAttrsMenu
			if restrict:
				mset = set(models)
				objList = [ a for a in selection.currentAtoms()
						if a.molecule in mset ]
			else:
				objList = []
				for m in models:
					objList.extend(m.atoms)
		elif target == ATTRS_RESIDUES:
			menu = self.resAttrsMenu
			if restrict:
				mset = set(models)
				objList = [ r for r in
						selection.currentResidues()
						if r.molecule in mset ]
			else:
				objList = []
				for m in models:
					objList.extend(m.residues)
		elif target == ATTRS_MODELS:
			menu = self.modelAttrsMenu
			if restrict:
				mset = set(models)
				objList = [ m for m in
						selection.currentMolecules()
						if m in mset ]
			else:
				objList = models
		if not objList:
			raise chimera.UserError("No items selected")
		attrList = menu.getvalue()
		if not attrList:
			raise chimera.UserError("No attribute selected")
		attrName = attrList[-1]
		if self.includeModelVar.get():
			level = selection.SelGraph
		else:
			level = selection.SelSubgraph
		f = open(filename, "w")
		try:
			if len(attrList) == 1:
				print >> f, "attribute:", attrName
				print >> f, "recipient:", target
				# direct attribute, just print
				for o in objList:
					try:
						val = getattr(o, attrName)
					except AttributeError:
						continue
					if val is not None:
						print >> f, "\t%s\t%s" % (
							o.oslIdent(level),
							repr(val))
			else:
				# averaged attribute, need to be more clever
				print >> f, "attribute:", '_'.join(attrList)
				print >> f, "recipient:", target
				if target == ATTRS_MODELS:
					subfunc = lambda m: m.residues
				else:
					subfunc = lambda r: r.oslChildren()
				from operator import add
				for o in objList:
					vals = []
					for sub in subfunc(o):
						try:
							val = getattr(sub,
								attrName)
						except AttributeError:
							continue
						if val is not None:
							vals.append(val)
					if vals:
						val = reduce(add, vals)
						if not summableAttrName(
								attrName):
							val /= float(len(vals))
						print >> f, "\t%s\t%g" % (
							o.oslIdent(level), val)
		finally:
			f.close()
		msg = "Attribute %s of %s saved in file %s" % (attrName,
								target, filename)
		from chimera import replyobj
		replyobj.status(msg)

	def configure(self, models=None, attrsOf=None, attrName=None,
							fromMolListBox=False):
		curMenu = self._curAttrMenu()
		curAttr = curMenu.getvalue()
		curTargetLabel = self.targetMenu.getvalue()
		curTarget = revAttrsLabelMap[curTargetLabel]
		refreshedAttrs = False
		if models != self.models and models is not None:
			newModels = None
			if fromMolListBox:
				from sets import Set
				oldSet = Set(self.models)
				newSet = Set(models)
				if newSet >= oldSet:
					newModels = newSet - oldSet
			else:
				self.molListBox.setvalue(models,
							doCallback=False)
			self.models = models
			self._populateAttrsMenus(newModels=newModels)
			refreshedAttrs = True
			if not models or (curAttr is None and attrName is None):
				# _populateAttrsMenu has knocked the menu
				# button off of "choose attr"; arrange for
				# it to be restored...
				attrName = NO_ATTR
			if (attrsOf == curTarget or attrsOf is None) \
			and ([attrName] == curAttr or attrName is None):
				# no other changes
				if curAttr is not None:
					try:
						curMenu.invoke(curAttr)
					except ValueError:
						# attribute no longer present
						self._targetCB(curTargetLabel)

		if attrsOf != curTarget and attrsOf is not None:
			self.targetMenu.invoke(attrsOf)

		# if an attribute name is specified, probably want an update...
		if attrName is not None:
			if attrName == NO_ATTR:
				self._targetCB(curTargetLabel)
			else:
				target = attrsOf or curTarget
				if target == "atoms":
					seen = self.seenAtomAttrs
				elif target == "residues":
					seen = self.seenResAttrs
				else:
					seen = self.seenModelAttrs
				if not refreshedAttrs and attrName not in seen:
					self._populateAttrsMenus()
					# 'seen' pointing to old list now...
					if target == "atoms":
						seen = self.seenAtomAttrs
					elif target == "residues":
						seen = self.seenResAttrs
					else:
						seen = self.seenModelAttrs
				if attrName in seen:
					self._curAttrMenu().invoke([attrName])
				else:
					self._targetCB(curTargetLabel)

		self._attrReady()

	def _compileAttrVals(self, targetName, menuItem):
		self.status("Surveying attribute %s\n" % " ".join(menuItem),
								blankAfter=0)
		attrVals = []
		if targetName == ATTRS_MODELS:
			surveyed = self.models
		else:
			surveyed = []
			for m in self.models:
				surveyed.extend(getattr(m, targetName))
		attrName = menuItem[-1]
		hasNone = False
		if len(menuItem) == 1:
			for t in surveyed:
				try:
					val = getattr(t, attrName)
				except AttributeError:
					hasNone = True
					continue
				if val is None or (isinstance(val, basestring)
								and not val):
					hasNone = True
					continue
				attrVals.append(val)
		else:
			# average of atoms/residues
			from operator import add
			if targetName == ATTRS_MODELS:
				subfunc = lambda m: m.residues
			else:
				subfunc = lambda r: r.oslChildren()
			for t in surveyed:
				vals = []
				for sub in subfunc(t):
					try:
						val = getattr(sub, attrName)
					except AttributeError:
						continue
					if val is None \
					or (isinstance(val, basestring)
								and not val):
						continue
					vals.append(val)
				if not vals:
					hasNone = True
					continue
				val = reduce(add, vals)
				if not summableAttrName(attrName):
					val /= float(len(vals))
				attrVals.append(val)
		self.status("Done surveying\n")
		self._attrReady()

	def _composeAttrMenus(self):
		sortFunc = lambda a, b: cmp(a.lower(), b.lower())
		self.useableAtomAttrs.sort(sortFunc)
		self.useableResAttrs.sort(sortFunc)
		self.useableModelAttrs.sort(sortFunc)

		# do this in a little bit of a weird order so that the 'average'
		# submenu only contains numeric quantities
		aggAtomAttrs = self.useableAtomAttrs \
					+ self.additionalNumericAtomAttrs
		aggResAttrs = self.useableResAttrs + \
					self.additionalNumericResAttrs
		aggModelAttrs = self.useableModelAttrs + \
					self.additionalNumericModelAttrs
		aggAtomAttrs.sort(sortFunc)
		aggResAttrs.sort(sortFunc)
		aggModelAttrs.sort(sortFunc)
		self.modelAttrsMenu.setitems(
				_menuItems(aggModelAttrs, aggResAttrs))
		aggResAttrs.extend(self.additionalOtherResAttrs)
		aggResAttrs.sort(sortFunc)
		self.resAttrsMenu.setitems(
				_menuItems(aggResAttrs, aggAtomAttrs))
		aggAtomAttrs.extend(self.additionalOtherAtomAttrs)
		aggAtomAttrs.sort(sortFunc)
		self.atomAttrsMenu.setitems(aggAtomAttrs)

	def _curAttrMenu(self):
		if not self.targetMenu:
			return None
		target = revAttrsLabelMap[self.targetMenu.getvalue()]
		if target == ATTRS_ATOMS:
			return self.atomAttrsMenu
		if target == ATTRS_RESIDUES:
			return self.resAttrsMenu
		if target == ATTRS_MODELS:
			return self.modelAttrsMenu

	def _populateAttrsMenus(self, newModels=None):
		self.status("Compiling attribute lists...\n", blankAfter=0)
		if newModels is None or not hasattr(self, 'seenAtomAttrs'):
			self.seenAtomAttrs = screenedAttrs[chimera.Atom].copy()
			self.seenResAttrs = screenedAttrs[chimera.Residue].copy()
			self.seenModelAttrs = screenedAttrs[chimera.Model].copy()
			self.useableAtomAttrs = []
			self.useableResAttrs = []
			self.useableModelAttrs = []
			self.additionalNumericAtomAttrs = []
			self.additionalNumericResAttrs = []
			self.additionalNumericModelAttrs = []
			self.additionalOtherAtomAttrs = []
			self.additionalOtherResAttrs = []
			self.additionalOtherModelAttrs = []
		if newModels is None:
			scanModels = self.models
		else:
			scanModels = newModels

		for m in scanModels:
			self.status("Compiling attribute lists from %s...\n"
					% m.name, blankAfter=0)
			self._reapAttrs(m, self.seenModelAttrs,
					self.useableModelAttrs,
					self.additionalNumericModelAttrs,
					self.additionalOtherModelAttrs)
			for a in m.atoms:
				self._reapAttrs(a, self.seenAtomAttrs,
						self.useableAtomAttrs,
						self.additionalNumericAtomAttrs,
						self.additionalOtherAtomAttrs)
			for r in m.residues:
				self._reapAttrs(r, self.seenResAttrs,
						self.useableResAttrs,
						self.additionalNumericResAttrs,
						self.additionalOtherResAttrs)
		self.status("Updating attribute menus...\n", blankAfter=0)
		self._composeAttrMenus()
		self.status("\n")

	def _reapAttrs(self, instance, seenAttrs, useableAttrs,
				additionalNumericAttrs, additionalOtherAttrs):
		for attrName in dir(instance):
			attrType = seenAttrs.get(attrName, None)
			if isinstance(attrType, bool):
				continue
			elif attrType is None:
				if attrName[0] == '_' \
				or attrName[0].isupper():  # e.g. 'Ball'
					seenAttrs[attrName] = False
					continue
				attr = getattr(instance, attrName)
				if attr is None or (isinstance(attr, basestring)
								and not attr):
					# defer judgment until
					# we see a real value
					continue
				attrType = type(attr)
			else:
				attr = attrType()
			seenAttrs[attrName] = True
			if attrType in self.useableTypes:
				useableAttrs.append(attrName)
			elif attrType in self.additionalNumericTypes:
				additionalNumericAttrs.append(attrName)
			elif isinstance(attr, self.additionalOtherTypes):
				additionalOtherAttrs.append(attrName)

	def _targetCB(self, menuItem):
		self.modelAttrsMenu.grid_forget()
		self.resAttrsMenu.grid_forget()
		self.atomAttrsMenu.grid_forget()
		target = revAttrsLabelMap[menuItem]
		if target == ATTRS_ATOMS:
			menu = self.atomAttrsMenu
		elif target == ATTRS_RESIDUES:
			menu = self.resAttrsMenu
		else:
			menu = self.modelAttrsMenu
		menu.grid(row=0, column=0)
		menu.component('menubutton').config(text=NO_ATTR)
		SaveModeless._millerReady(self, None)

	def _millerReady(self, paths):
		if not self.molListBox or not self.molListBox.getvalue():
			paths = None
		else:
			menu = self._curAttrMenu()
			if menu:
				attrList = menu.getvalue()
				if not attrList:
					paths = None
			else:
				paths = None
		SaveModeless._millerReady(self, paths)

	def _attrReady(self):
		self._millerReady(self.getPaths(remember=False))

_attrNameAnalysisCache = {}
def summableAttrName(attrName):
	# split camel case and underscored names
	if attrName not in _attrNameAnalysisCache:
		components = []
		start = 0
		for i in range(1, len(attrName)):
			p, c = attrName[i-1:i+1]
			if c == "_":
				if p != "_":
					components.append(
						attrName[start:i].lower())
				start = i+1
			elif p.islower() and c.isupper():
				components.append(attrName[start:i].lower())
				start = i
			elif p.isupper() and c.islower() and start < i-1:
				# only final cap of a stretch is part of the camel case
				components.append(attrName[start:i-1].lower())
				start = i-1
		if start < len(attrName):
			components.append(attrName[start:].lower())
		for summable in ("area", "volume", "charge"):
			if summable in components:
				_attrNameAnalysisCache[attrName] = True
				break
		else:
			_attrNameAnalysisCache[attrName] = False
	return _attrNameAnalysisCache[attrName]
				

def _menuItems(baseItems, subItems):
	items = baseItems
	for summable, label in [(False, "average"), (True, "total")]:
		filtered = [si for si in subItems
				if summableAttrName(si) == summable]
		if filtered:
			items = items + [(label, filtered)]
	return items

