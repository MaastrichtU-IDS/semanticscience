# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 29590 2009-12-11 00:12:08Z pett $

"""Interface to structure measurements (e.g. distances, angles)"""

import Pmw
import chimera
from chimera import replyobj, selection
from chimera.baseDialog import ModelessDialog
import Tkinter
from DistMonitor import distanceMonitor, addDistance, removeDistance, \
	precision, setPrecision, showUnits
from BondRotMgr import bondRotMgr
from chimera import dihedral, mousemodes
from prefs import prefs, ROT_LABEL, ROT_DIAL_SIZE, ANGLE_PRECISION, \
				TORSION_PRECISION, SHOW_DEGREE_SYMBOL

DISTANCES = "Distances"
BONDROTS = "Adjust Torsions"
ANGLES = "Angles/Torsions"
GEOMETRIES = "Axes/Planes" #/Centroids
CENTROIDS = "Centroids"
METALS = "Metal Geometry"
# add in remaining tabs later
pageNames = [DISTANCES, ANGLES, BONDROTS, GEOMETRIES]
# the follow import needed until there's a ChimeraExtension.py
import Axes, Planes
try:
	import Centroids
except ImportError:
	pass
else:
	pageNames.append(CENTROIDS)

try:
	import Metals
except ImportError:
	pass
else:
	pageNames.append(METALS)

class StructMeasure(ModelessDialog):
	title="Structure Measurements"
	buttons=("Close", "Save")
	name="structure measurements"
	provideStatus = True
	statusPosition = "above"

	dialSizes = [".1i", ".2i", ".3i"]
	def fillInUI(self, parent):
		self.distances = []
		self.angleInfo = []

		self.numMolecules = len(chimera.openModels.list(
						modelTypes=[chimera.Molecule]))
		chimera.triggers.addHandler('Molecule', self._molChange, None)
		chimera.triggers.addHandler('PseudoBond', self._psbChange, None)
		chimera.triggers.addHandler('Atom', self._atomChange, None)
		chimera.triggers.addHandler('Model', self._modelChange, None)
		distanceMonitor.updateCallbacks.append(self._distUpdateCB)

		self.notebook = Pmw.NoteBook(parent,
						raisecommand=self._nbRaiseCB,
						lowercommand=self._nbLowerCB)
		self.notebook.pack(fill='both', expand=1)

		self.interfaces = {}
		for pn in pageNames:
			pageID = pn
			## when more tabs shown, maybe do this...
			#if '/' in pn:
			#	parts = pn.split('/')
			#	pn = "/ ".join(parts)
			#if ' ' in pn:
			#	parts = pn.split(' ')
			#	pn = '\n'.join(parts)
			self.notebook.add(pageID, tab_text=pn)

		dp = self.notebook.page(DISTANCES)
		from CGLtk.Table import SortableTable
		self.distTable = SortableTable(dp)
		self.distTable.grid(row=0, column=0, sticky='nsew', rowspan=7)
		dp.columnconfigure(0, weight=1)
		dp.rowconfigure(4, weight=1)
		dp.rowconfigure(5, weight=1)
		self.distTable.addColumn("ID", "id", format="%d")
		self.distTable.addColumn("Atom 1",
				lambda d, s=self: s.atomLabel(d.atoms[0]))
		self.distTable.addColumn("Atom 2",
				lambda d, s=self: s.atomLabel(d.atoms[1]))
		self.distTable.addColumn("Distance", "distance", font="TkFixedFont")
		self.distTable.setData(self.distances)
		self.distTable.launch(browseCmd=self._distTableSelCB)

		self.distButtons = Pmw.ButtonBox(dp, padx=0)
		self.distButtons.add("Create", command=self._createDistance)
		self.distButtons.add("Remove", command=self._removeDistance)

		# remove the extra space around buttons allocated to indicate
		# which button is the 'default', so that buttons stack closely
		for but in range(self.distButtons.numbuttons()):
			self.distButtons.button(but).config(default='disabled')
		self.distButtons.alignbuttons()
		self.distButtons.grid(row=1, column=1)

		self.distLabelChoice = Pmw.RadioSelect(dp, pady=0,
			buttontype='radiobutton',
			command=self._distLabelModeChange, orient='vertical',
			labelpos='w', label_text="Labels")
		self.distLabelChoice.grid(row=2, column=1)
		self.distLabelChoice.add("None", highlightthickness=0)
		self.distLabelChoice.add("ID", highlightthickness=0)
		self.distLabelChoice.add("Distance", highlightthickness=0)
		self.distLabelChoice.invoke("Distance")

		self.distPrecisionChoice = Pmw.Counter(dp, datatype={
			'counter': self._distPrecisionChange}, labelpos='w',
			label_text="Decimal places", entry_width=1,
			entry_pyclass=PrecisionEntry,
			entryfield_value=str(precision()))
		self.distPrecisionChoice.grid(row=3, column=1)

		self.showUnitsVar = Tkinter.IntVar(dp)
		self.showUnitsVar.set(showUnits())
		Tkinter.Checkbutton(dp, text="Show Angstrom symbol",
			variable=self.showUnitsVar,
			command=self._showUnitsChangeCB).grid(row=4, column=1)

		self.distSelectsAtomsVar = Tkinter.IntVar(dp)
		self.distSelectsAtomsVar.set(False)
		Tkinter.Checkbutton(dp, variable=self.distSelectsAtomsVar,
			text="Choosing in table\nselects atoms\n(and pseudobond)"
			).grid(row=5, column=1)

		from chimera.pbgPanel import attributesCmd
		Tkinter.Button(dp, text="Display options...", command=
			lambda dm=distanceMonitor: attributesCmd([dm])
			).grid(row=6, column=1)

		for d in distanceMonitor.pseudoBonds:
			self.newDistance(d)

		atp = self.notebook.page(ANGLES)
		from CGLtk.Table import SortableTable
		self.angleTable = SortableTable(atp)
		self.angleTable.grid(row=0, column=0, sticky='nsew', rowspan=4)
		atp.columnconfigure(0, weight=1)
		atp.rowconfigure(2, weight=1)
		for i in range(4):
			self.angleTable.addColumn("Atom %d" % (i+1), lambda atoms, s=self,
					i=i: i >= len(atoms) and "N/A" or s.atomLabel(atoms[i]))
		self.angleTable.addColumn("Angle/Torsion",
			lambda atoms, s=self: s._angleLabel(atoms), font="TkFixedFont")
		self.angleTable.setData(self.angleInfo)
		self.angleTable.launch(browseCmd=self._angleTableSelCB)

		self._osHandler = None
		self.angleButtons = Pmw.ButtonBox(atp, padx=0)
		self.angleButtons.add("Create", command=self._createAngle)
		self.angleButtons.add("Remove", command=self._removeAngle,
							state='disabled')
		# remove the extra space around buttons allocated to indicate
		# which button is the 'default', so that buttons stack closely
		for but in range(self.angleButtons.numbuttons()):
			self.angleButtons.button(but).config(default='disabled')
		self.angleButtons.alignbuttons()
		self.angleButtons.grid(row=0, column=1)

		self.anglePrecisionChoice = Pmw.Counter(atp, datatype={
			'counter': self._anglePrecisionChange}, labelpos='w',
			label_text="Decimal places", entry_width=1,
			entry_pyclass=PrecisionEntry,
			entryfield_value=str(prefs[ANGLE_PRECISION]))
		self.anglePrecisionChoice.grid(row=1, column=1)

		self.angleSelectsComponentsVar = Tkinter.IntVar(atp)
		self.angleSelectsComponentsVar.set(True)
		Tkinter.Checkbutton(atp, variable=self.angleSelectsComponentsVar,
			text="Choosing in table selects\ncomponent atoms/bonds"
			).grid(row=3, column=1)

		brp = self.notebook.page(BONDROTS)
		self.rotations = []
		self.rotInfo = {}

		labeledButton = Pmw.LabeledWidget(brp, labelpos="e",
				label_text="selected bond as torsion")
		labeledButton.grid(row=0, column=0, columnspan=2)
		self.createRotButton = Tkinter.Button(labeledButton.interior(),
			text="Activate", command=self._createRotation, pady=0)
		self.createRotButton.grid()

		tableFrame = Tkinter.Frame(brp, pady="0.1i")
		tableFrame.grid(row=1, column=0, columnspan=2, sticky='ns')
		from CGLtk.Table import ScrolledTable
		self.rotTable = ScrolledTable(tableFrame, hscrollmode='none')
		self.rotTable.setColumnTitle(0, "ID")
		self.rotTable.setColumnTitle(1, "Near")
		self.rotTable.setColumnTitle(2, "Bond")
		self.rotTable.setColumnTitle(3, "Far")
		self.angleTitle = Tkinter.StringVar(parent)
		self.angleTitle.set("Torsion")
		self.rotTable.setColumnTitle(4, self.angleTitle,
						pyclass=Tkinter.Button, pady=0,
						command=self._toggleAngleType)
		brp.rowconfigure(1, weight=1)
		brp.columnconfigure(0, weight=1)
		brp.columnconfigure(1, weight=1)
		tableFrame.rowconfigure(0, weight=1)
		tableFrame.columnconfigure(0, weight=1)
		self.rotTable.columnconfigure(4, weight=1)
		self.rotTable.grid(row=0, column=0, sticky='news')

		self.dialSizeLabels = ["small", "medium", "large"]
		Pmw.OptionMenu(tableFrame,
			items=self.dialSizeLabels, labelpos='w',
			initialitem=self.dialSizeLabels[prefs[ROT_DIAL_SIZE]],
			label_text="Dial size:", command=self._dialSizeChangeCB,
			).grid(row=1, column=0, sticky='e')

		f = Tkinter.Frame(brp)
		f.grid(row=2, column=0, columnspan=2)
		self.mouseModeVar = Tkinter.IntVar(f)
		self.mouseModeVar.set(False)
		self.needTorWidgets = []
		self.needTorWidgets.append(Tkinter.Checkbutton(f, text="Rotate",
			variable=self.mouseModeVar, command=self._mouseModeCB))
		self.needTorWidgets[-1].grid(row=0, column=0)
		self.rotModeTorsMenu = Pmw.OptionMenu(f)
		self.rotModeTorsMenu.grid(row=0, column=1)
		self.needTorWidgets.append(self.rotModeTorsMenu)
		self.buttonLabels = []
		self.labelValues = {}
		for mod in ("",) + mousemodes.usedMods:
			for but in mousemodes.usedButtons:
				if mod:
					self.buttonLabels.append(
						mod.lower() + " button " + but)
					self.labelValues[self.buttonLabels[-1]]\
						= (but, (mod,))
				else:
					self.buttonLabels.append("button "+but)
					self.labelValues[self.buttonLabels[-1]]\
						= (but, ())
		self._modeButton = self.buttonLabels[0]
		self.rotModeButMenu = Pmw.OptionMenu(f, labelpos='w',
			command=self._modeButtonCB,
			label_text="using", items=self.buttonLabels)
		self.rotModeButMenu.grid(row=0, column=2)
		self.needTorWidgets.append(self.rotModeButMenu)

		self.rotLabelChoice = Pmw.RadioSelect(brp, pady=0,
			buttontype='radiobutton', hull_pady=".1i",
			command=self._rotLabelModeChange, orient='vertical',
			labelpos='w', label_text="Labels")
		self.rotLabelChoice.grid(row=3, rowspan=2, column=0)
		self.rotLabelChoice.add("None", highlightthickness=0)
		self.rotLabelChoice.add("ID", highlightthickness=0)
		self.rotLabelChoice.add("Name", highlightthickness=0)
		self.rotLabelChoice.add("Angle", highlightthickness=0)
		self.rotLabelChoice.invoke(prefs[ROT_LABEL])

		self.torsionPrecisionChoice = Pmw.Counter(brp, datatype={
			'counter': self._torsionPrecisionChange}, labelpos='w',
			label_text="Decimal places", entry_width=1,
			entry_pyclass=PrecisionEntry,
			entryfield_value=str(prefs[TORSION_PRECISION]))
		self.torsionPrecisionChoice.grid(row=3, column=1)

		self.showDegreeSymbolVar = Tkinter.IntVar(brp)
		self.showDegreeSymbolVar.set(prefs[SHOW_DEGREE_SYMBOL])
		Tkinter.Checkbutton(brp, text="Show degree symbol",
			variable=self.showDegreeSymbolVar,
			command=self._showDegreeSymbolChangeCB).grid(
							row=4, column=1)

		self.setTorWidgetsState("disabled")

		mousemodes.addFunction("rotate bond", (lambda v, e:
			v.recordPosition(e.time, e.x, e.y, "rotate"),
			self._mouseSphere,
			lambda v, e: v.setCursor(None)))

		if GEOMETRIES in pageNames:
			gp = self.notebook.page(GEOMETRIES)
			from Geometry import GeometryInterface
			self.interfaces[GEOMETRIES] = GeometryInterface(gp, self.status)

		if METALS in pageNames:
			mp = self.notebook.page(METALS)
			from Metals import MetalsInterface
			self.interfaces[METALS] = MetalsInterface(mp,
								self.status)
		self.notebook.setnaturalsize()

	def setCategoryMenu(self, category):
		# avoid unnecessary page raises; they interfere with
		# the bond rotation mouse mode (graphics window loses
		# focus)
		if self.notebook.getcurselection() != category:
			self.notebook.selectpage(category)
	
	def atomLabel(self, atom, diffWith=None):
		if self.numMolecules > 1:
			showModel = 1
		else:
			showModel = 0
		
		from chimera.misc import chimeraLabel
		lab = chimeraLabel(atom, showModel=showModel,
							diffWith=diffWith)
		if lab == "":
			lab = atom.name
		return lab

	def _angleLabel(self, atoms):
		pts = tuple([a.xformCoord() for a in atoms])
		if len(pts) == 3:
			val = chimera.angle(*pts)
		else:
			val = chimera.dihedral(*pts)
		return "%.*f" % (prefs[ANGLE_PRECISION], val)

	def _anglePrecisionChange(self, *args):
		newPrecision = self._checkPrecision(*args)
		prefs[ANGLE_PRECISION] = newPrecision
		self.angleTable.refresh()
		return str(newPrecision)

	def _angleTableSelCB(self, selAngles):
		if self.angleSelectsComponentsVar.get():
			select = []
			for atoms in selAngles:
				select.extend(atoms)
				atomSet = set(atoms)
				for a in atoms:
					for b in a.bonds:
						if b.otherAtom(a) in atomSet:
							select.append(b)
			selection.setCurrent(select)

	def _atomChange(self, trigName, myData, trigData):
		if not trigData.deleted:
			return
		remove = []
		for atoms in self.angleInfo:
			for a in atoms:
				if a.__destroyed__:
					remove.append(atoms)
					break
		if remove:
			self._removeAngle(remove=remove)

	def _checkPrecision(self, text, plusMinus, increment):
		newPrecision = int(text) + plusMinus
		if newPrecision < 0:
			raise ValueError("decimal places must be non-negative")
		if newPrecision > 9:
			raise ValueError("9 decimal places is enough")
		return newPrecision

	def _createAngle(self, atoms=None):
		"""'Create angle' callback"""

		if atoms is None:
			atoms = selection.currentAtoms(ordered=True)
		if len(atoms) not in [3,4]:
			replyobj.error("Either three or four atoms must be"
					" selected in graphics window\n")
			return
		if not self.angleInfo:
			from SimpleSession import SAVE_SESSION
			self._angleSesTrigID = chimera.triggers.addHandler(SAVE_SESSION,
												self._sessionAngleSaveCB, None)
		self.angleInfo.append(atoms)
		self.angleTable.setData(self.angleInfo)
		
		self.angleButtons.button("Remove").config(state='normal')

		if self._osHandler is None:
			models = set([a.molecule for a in atoms])
			if len(models) > 1:
				self._osHandler = chimera.triggers.addHandler(
					'OpenState', self._osChange, None)

	def _createDistance(self):
		"""'Create distance' callback"""

		selAtoms = selection.currentAtoms()
		if len(selAtoms) != 2:
			replyobj.error("Exactly two atoms must be selected "
							"in graphics window\n")
			return
		addDistance(*tuple(selAtoms))

	def _createRotation(self):
		selBonds = selection.currentBonds()
		if len(selBonds) == 1:
			addRotation(selBonds[0])
			return
		replyobj.error("Exactly one bond must be selected "
							"in graphics window\n")

	def deadDistances(self):
		"""Remove deleted distances from the table"""

		pre = len(self.distances)
		self.distances = [d for d in self.distances
						if not d.__destroyed__]
		if len(self.distances) != pre:
			self.distTable.setData(self.distances)
			return True
		return False

	def _dialSizeChangeCB(self, dialSizeLabel):
		dialSize = self.dialSizeLabels.index(dialSizeLabel)
		prefs[ROT_DIAL_SIZE] = dialSize
		for info in self.rotInfo.values():
			for angleCounter in info[0][-2:]:
				angleCounter.configure(dial_radius=
						self.dialSizes[dialSize])
		self.notebook.setnaturalsize()

	def dihedEndAtoms(self, br):
		widgets, nearIndex, nearAtoms, farIndex, farAtoms = \
								self.rotInfo[br]
		return nearAtoms[nearIndex], farAtoms[farIndex]
		
	def _distPrecisionChange(self, text, plusMinus, increment):
		setPrecision(int(text) + plusMinus)
		if precision() > 9:
			setPrecision(9)
			raise ValueError, "9 decimal places is enough"
		return str(precision())

	def _distTableSelCB(self, selDists):
		if self.distSelectsAtomsVar.get():
			select = []
			select.extend(selDists)
			for sd in selDists:
				select.extend(sd.atoms)
			selection.setCurrent(select)
		else:
			selection.removeCurrent(self.distances)
			selection.addCurrent(selDists)

	def _distUpdateCB(self):
		"""Distances just updated"""
		self.distTable.refresh()

	def _distLabelModeChange(self, mode):
		if mode == "None":
			distanceMonitor.fixedLabels = 1
			for d in self.distances:
				d.label = ""
		elif mode == "ID":
			distanceMonitor.fixedLabels = 1
			for d in self.distances:
				d.label = "%d" % d.id
		else:
			distanceMonitor.fixedLabels = 0
			for d in self.distances:
				d.label = d.distance

	def Help(self):
		anchor = self.notebook.getcurselection().lower().split()[0]
		if "/" in anchor:
			anchor = anchor.split('/')[0]
		chimera.help.display("ContributedSoftware/structuremeas/"
			"structuremeas.html#" + anchor)

	def _labelRot(self, br, mode=None):
		if mode is None:
			mode = self.rotLabelChoice.getvalue()
		if mode == "None":
			for br in self.rotations:
				br.bond.label = ""
		elif mode == "Name":
			for br in self.rotations:
				br.bond.label = self.rotLabel(br)
		elif mode == "Angle":
			isDihed = self.angleTitle.get() == "Torsion"
			if prefs[SHOW_DEGREE_SYMBOL]:
				suffix = "\260"
			else:
				suffix = ""
			for br in self.rotations:
				if isDihed:
					val = self.dihedral(br)
				else:
					val = br.get()
					while val < -180.0:
						val += 180.0
					while val > 180.0:
						val -= 180.0
				br.bond.label = "%.*f%s" % (
						prefs[TORSION_PRECISION],
						val, suffix)
		elif mode == "ID":
			br.bond.label = str(br.id)

	def _modelChange(self, trigName, myData, trigData):
		if not trigData.modified:
			return
		# both Coord and CoordSet changes fire the Model trigger
		self._updateAngles()

	def _molChange(self, trigName, myData, trigData):
		n = len(chimera.openModels.list(modelTypes=[chimera.Molecule]))
		if n == 1 and self.numMolecules > 1 \
		or n > 1 and self.numMolecules == 1:
			# don't want to remake atom labels right away since
			# some of the distances may have gone away, and that
			# won't get cleaned up until the Pseudobond trigger
			# fires, so register for the monitorChanges trigger and
			# update the labels there
			chimera.triggers.addHandler(
				  'monitor changes', self.monitorCB, None)
		self.numMolecules = n

	def _modeButtonCB(self, but):
		if self.mouseModeVar.get():
			# "manually" turn off, then on with new value
			self.mouseModeVar.set(False)
			self._mouseModeCB()
			self._modeButton = but
			self.mouseModeVar.set(True)
			self._mouseModeCB()
		else:
			self._modeButton = but

	def _mouseModeCB(self):
		but, mods = self.labelValues[self._modeButton]
		if self.mouseModeVar.get():
			self._formerMouseMode = mousemodes.getFuncName(but,mods)
			mousemodes.setButtonFunction(but, mods, "rotate bond")
		else:
			mousemodes.setButtonFunction(but, mods,
							self._formerMouseMode)

	def _mouseSphere(self, viewer, event):
		xf = viewer.vsphere(event.time, event.x, event.y,
							event.state % 2 == 1)
		if xf.isIdentity():
			return
		axis, angle = xf.getRotation()
		br = self.rotations[self.rotModeTorsMenu.index(Pmw.SELECT)]
		rotVec = br.atoms[1].xformCoord() - br.atoms[0].xformCoord()
		axis.normalize()
		rotVec.normalize()
		turn = angle * (axis * rotVec)
		br.set(turn + br.get())

	def newDistance(self, d):
		if self.distances:
			d.id = self.distances[-1].id + 1
		else:
			d.id = 1
		if not hasattr(d, 'distance'):
			d.distance = ""
		self.distances.append(d)
		self.distTable.setData(self.distances)
		
	def monitorCB(self, trigName, myData, trigData):
		from chimera.triggerSet import ONESHOT
		self.mcHandlerID = None
		self.remakeAtomLabels()
		return ONESHOT

	def _nbLowerCB(self, pageName):
		if pageName in self.interfaces:
			interface = self.interfaces[pageName]
			try:
				interface._lowerCmd()
			except AttributeError:
				self.status("")
		else:
			self.status("")

	def _nbRaiseCB(self, pageName):
		if pageName in self.interfaces:
			interface = self.interfaces[pageName]
			try:
				interface._raiseCmd()
			except AttributeError:
				pass

	def _osChange(self, trigName, myData, trigData):
		if 'transformation change' not in trigData.reasons:
			return
		self._updateAngles()

	def _psbChange(self, trigName, myData, trigData):
		"""Callback from PseudoBond trigger"""

		change = False

		# clean up deleted distances
		if trigData.deleted:
			change = self.deadDistances()
		
		# insert new distances
		for psb in trigData.created:
			if psb in distanceMonitor.pseudoBonds:
				self.newDistance(psb)
				change = True
		if change:
			self.notebook.setnaturalsize()
			
	def remakeAtomLabels(self):
		self.distTable.refresh()
		self.angleTable.refresh()
		newLabels = []
		for br in self.rotations:
			newLabels.append(self.rotLabel(br))
			rotMenu = self.rotInfo[br][0][2]
			rotMenu.configure(text=newLabels[-1])
		if newLabels:
			modeTors = self.rotModeTorsMenu.index(Pmw.SELECT)
			if not modeTors:
				modeTors = None
		else:
			modeTors = None
		self.rotModeTorsMenu.setitems(newLabels, index=modeTors)

	def _removeAngle(self, remove=None):
		if len(self.angleInfo) == 0:
			replyobj.error("No angles to remove\n")
			return
		if remove is None:
			if len(self.angleInfo) == 1:
				remove = self.angleInfo
			else:
				remove = self.angleTable.selected()
				if not remove:
					replyobj.error("Must select angle(s) in table\n")
					return
		for rm in remove:
			self.angleInfo.remove(rm)
		self.angleTable.setData(self.angleInfo)

		if len(self.angleInfo) == 0:
			self.angleButtons.button("Remove").config(
							state='disabled')
			from SimpleSession import SAVE_SESSION
			chimera.triggers.deleteHandler(SAVE_SESSION, self._angleSesTrigID)

		if self._osHandler:
			stillNeedHandler = False
			for info in self.angleInfo:
				models = dict.fromkeys([a.molecule
							for a in info[0]])
				if len(models) > 1:
					stillNeedHandler = True
					break
			if not stillNeedHandler:
				chimera.triggers.deleteHandler('OpenState',
								self._osHandler)
				self._osHandler = None

	def _removeDistance(self):
		if len(self.distances) == 1:
			removeDistance(self.distances[0])
			return
		if len(self.distances) == 0:
			replyobj.error("No distances to remove\n")
			return
		if not self.distTable.selected():
			replyobj.error("Must select distance in table\n")
			return
		for d in self.distTable.selected():
			removeDistance(d)

	def rotLabel(self, br):
		return "%s -> %s" % (self.atomLabel(br.atoms[0]),
			self.atomLabel(br.atoms[1], diffWith=br.atoms[0]))

	def _rotLabelModeChange(self, mode):
		prefs[ROT_LABEL] = mode
		for br in self.rotations:
			self._labelRot(br, mode)

	def Save(self):
		"""Save the displayed info to file"""
		if not hasattr(self, '_saveDialog'):
			self._saveDialog = _SaveStructInfo(self, clientPos='s',
				title='Save Structure Measurements')
		self._saveDialog.enter()
	
	def setTorWidgetsState(self, state):
		for w in self.needTorWidgets:
			if isinstance(w, Pmw.OptionMenu):
				if w['labelpos']:
					w.configure(label_state=state)
				w.configure(menubutton_state=state)
			else:
				w.configure(state=state)

	def _showDegreeSymbolChangeCB(self):
		prefs[SHOW_DEGREE_SYMBOL] = self.showDegreeSymbolVar.get()
		if self.rotLabelChoice.getvalue() == "Angle":
			for br in self.rotations:
				self._labelRot(br)

	def _showUnitsChangeCB(self):
		showUnits(self.showUnitsVar.get())

	def _syncUI(self, br, side):
		"""Called from the Bond trigger callback, to correct the
		   dihedral angle menus if possible"""
		start = 1+2*side
		index, atoms = self.rotInfo[br][start:start+2]
		newIndex, newNames, newAtoms = \
			self.dihedChoices(br.atoms[side], br.atoms[1-side])
		if not newAtoms:
			# when gnats 243 is fixed, this bond rotation will
			# already have been destroyed and we won't get here
			return None
		if atoms == newAtoms:
			return None
		atom = atoms[index]
		if atom in newAtoms:
			newIndex = newAtoms.index(atom)
		menu = self.rotInfo[br][0][1+2*side]
		menu.setitems(newNames, newNames[newIndex])
		self.rotInfo[br][start:start+2] = [newIndex, newAtoms]
		return menu
		
	def _torsionPrecisionChange(self, *args):
		newPrecision = self._checkPrecision(*args)
		prefs[TORSION_PRECISION] = newPrecision
		for br in self.rotations:
			self._updateRot(br)
		return str(newPrecision)

	def rotChange(self, trigger, brInfo):
		needResize = False
		if trigger == bondRotMgr.DELETED:
			self._delRots(brInfo)
			needResize = True
		elif trigger == bondRotMgr.CREATED:
			self._addRot(brInfo)
			needResize = True
		elif trigger == bondRotMgr.REVERSED:
			# since the bond has reversed, need to switch
			# near/far labels as well
			widgets, nearIndex, nearAtoms, farIndex, farAtoms = \
							self.rotInfo[brInfo]
			row = self.rotations.index(brInfo)
			self.rotInfo[brInfo] = [widgets, farIndex, farAtoms,
							nearIndex, nearAtoms]
			# swap torsion-end menus
			widgets[1], widgets[3] = widgets[3], widgets[1]
			widgets[2].configure(text=self.rotLabel(brInfo))
			if self.angleTitle.get() == "Torsion":
				widgets[1].grid_forget()
				widgets[3].grid_forget()
				widgets[1].grid(row=row, column=1, sticky='ew')
				widgets[3].grid(row=row, column=3, sticky='ew')
			self.rotModeTorsMenu.setitems([self.rotLabel(r)
				for r in self.rotations],
				index=self.rotModeTorsMenu.index(Pmw.SELECT))
		else:
			self._updateRot(brInfo)
			self._updateAngles()
		if needResize:
			self.notebook.setnaturalsize()
	
	def dihedChoices(self, baseAtom, otherAtom):
		# sort choices so they are always in the same order
		default = None
		info = []
		for a in baseAtom.neighbors:
			if a is otherAtom:
				continue
			name = self.atomLabel(a, diffWith=baseAtom)
			info.append((name, a))
			if a.element.number > 1:
				default = a
		info.sort()
		names = map(lambda items: items[0], info)
		bonded = map(lambda items: items[1], info)
		if default is None:
			default = 0
		else:
			default = bonded.index(default)
		return default, names, bonded

	def dihedral(self, br):
		near, far = self.dihedEndAtoms(br)
		widgets, nearIndex, nearAtoms, farIndex, farAtoms = \
								self.rotInfo[br]
		return dihedral(near.xformCoord(), br.atoms[0].xformCoord(),
				br.atoms[1].xformCoord(), far.xformCoord())

	def _addRot(self, br, row=-1):
		self.setTorWidgetsState("normal")
		if row == -1:
			# by default, append bond rotation
			row = len(self.rotInfo)
		else:
			# insert bond rotation at given row, so make room
			for i in range(len(self.rotations), row, -1):
				nbr = self.rotations[i - 1]
				widgets = self.rotInfo[nbr][0]
				for w in widgets:
					gi = w.grid_info()
					if gi.has_key('column'):
						# otherwise presumably unmapped
						column = gi['column']
						w.grid_forget()
						w.grid(row=i, column=column,
								sticky='ew')

		self.rotations.insert(row, br)
		a1, a2 = br.atoms
		nearIndex, nearNames, nearAtoms = self.dihedChoices(a1, a2)
		farIndex, farNames, farAtoms = self.dihedChoices(a2, a1)
		# need to do this here so that self.dihedral(br) works
		widgets = []
		self.rotInfo[br] = [widgets,
				nearIndex, nearAtoms, farIndex, farAtoms]

		ID = Tkinter.Label(self.rotTable.interior(), text=str(br.id))
		widgets.append(ID)
		ID.grid(row=row, column=0)

		near = Pmw.OptionMenu(self.rotTable.interior(),
				menubutton_highlightthickness=0,
				initialitem=nearIndex, items=nearNames)
		near.configure(command=lambda x, br=br, n=near, s=self:
						s._setDihedEnd(br, n))
		widgets.append(near)
		if self.angleTitle.get() == "Torsion":
			near.grid(row=row, column=1, sticky='ew')
			
		actions = PmwableMenuButton(self.rotTable.interior(),
			text=self.rotLabel(br), indicatoron=1,
			relief='raised', bd=2, justify='right',
			states=['normal', 'normal', 'normal', 'normal'],
			items=['Revert', 'Reverse', 'Deactivate', 'Select'],
			command=lambda c, s=self, br=br: s._menuCB(c, br))
		widgets.append(actions)
		actions.grid(row=row, column=2, sticky='ew')

		far = Pmw.OptionMenu(self.rotTable.interior(),
				menubutton_highlightthickness=0,
				initialitem=farIndex, items=farNames)
		far.configure(command=lambda x, br=br, n=far, s=self:
						s._setDihedEnd(br, n))
		widgets.append(far)
		if self.angleTitle.get() == "Torsion":
			far.grid(row=row, column=3, sticky='ew')
			
		from CGLtk.AngleCounter import AngleCounter
		delta = AngleCounter(self.rotTable.interior(), dialpos='e',
			angle=float("%.*f" % (prefs[TORSION_PRECISION],
			br.get())),
			dial_zeroAxis='y', dial_radius=self.dialSizes[
			prefs[ROT_DIAL_SIZE]], dial_rotDir='clockwise',
			command=lambda d, s=self, br=br: s._deltaCB(br, d))

		dihed = AngleCounter(self.rotTable.interior(), dialpos='e',
			angle=float("%.*f" % (prefs[TORSION_PRECISION],
			self.dihedral(br))),
			dial_zeroAxis='y', dial_radius=self.dialSizes[
			prefs[ROT_DIAL_SIZE]], dial_rotDir='clockwise',
			command=lambda d, s=self, br=br: s._dihedCB(br, d))
		if self.angleTitle.get() == "Delta":
			delta.grid(row=row, column=4, sticky='ew')
			widgets.extend([delta, dihed])
		else:
			dihed.grid(row=row, column=4, sticky='ew')
			widgets.extend([dihed, delta])

		modeTors = self.rotModeTorsMenu.getvalue()
		if not modeTors:
			modeTors = None
		items = map(self.rotLabel, self.rotations)
		self.rotModeTorsMenu.setitems(items, index=modeTors)

		self._labelRot(br)

	def _delRots(self, brs):
		for br in brs:
			row = self.rotations.index(br)
			widgets = self.rotInfo[br][0]
			for w in widgets:
				w.grid_forget()
				w.destroy()
			del self.rotInfo[br]

			for i in range(row + 1, len(self.rotations)):
				nbr = self.rotations[i]
				widgets = self.rotInfo[nbr][0]
				for w in widgets:
					gi = w.grid_info()
					if gi.has_key('column'):
						# otherwise presumably unmapped
						column = gi['column']
						w.grid_forget()
						w.grid(row=i-1, column=column,
								sticky='ew')
			self.rotations.remove(br)

		modeTors = self.rotModeTorsMenu.getvalue()
		items = [self.rotLabel(br) for br in self.rotations]
		if modeTors in items:
			self.rotModeTorsMenu.setitems(items, index=modeTors)
		else:
			self.rotModeTorsMenu.setitems(items)
			if self.mouseModeVar.get():
				self.mouseModeVar.set(False)
				self._mouseModeCB()
			if not items:
				self.setTorWidgetsState("disabled")

	def _updateRot(self, br):
		if self.angleTitle.get() == "Torsion":
			dihed, delta = self.rotInfo[br][0][-2:]
		else:
			delta, dihed = self.rotInfo[br][0][-2:]
		delta.configure(angle = float("%.*f" %
			(prefs[TORSION_PRECISION], br.get())))
		dihed.configure(angle = float("%.*f" %
			(prefs[TORSION_PRECISION], self.dihedral(br))))
		if self.rotLabelChoice.getvalue() == "Angle":
			self._labelRot(br, "Angle")

	def _dihedCB(self, br, degrees):
		# callback from dihedral AngleCounter

		curDihed = self.dihedral(br)
		br.set(br.get() + degrees - curDihed)

	def _counterAngle(self, text, updown, incr, **kw):
		angle = float(text)
		if updown > 0:
			angle = angle + incr
		else:
			angle = angle - incr

		while angle < -180.0:
			angle = angle + 360.0
		while angle > 180.0:
			angle = angle - 360.0
		self._deltaCB(kw['br'], angle=angle)
		return str(angle)
	
	def _deltaCB(self, br, degrees):
		# callback from delta AngleCounter

		br.set(degrees)

	def _menuCB(self, cmdText, br):
		# callback from angle pull-down menu

		if cmdText == "Revert":
			br.set(0)
		elif cmdText == "Deactivate":
			br.bond.label = ""
			br.destroy()
		elif cmdText == "Select":
			selectables = []
			selectables.extend(br.atoms)
			selectables.append(br.bond)
			if self.angleTitle.get() == "Torsion":
				near, far = self.dihedEndAtoms(br)
				selectables.extend([near, far])
				selectables.append(br.atoms[0].bondsMap[near])
				selectables.append(br.atoms[1].bondsMap[far])
			from chimera.tkgui import selectionOperation
			sel = selection.ItemizedSelection()
			sel.add(selectables)
			selectionOperation(sel)
		elif cmdText == "Reverse":
			br.anchorSide = br.bond.otherAtom(br.anchorSide)

	def _sessionAngleSaveCB(self, trigName, myData, sessionFile):
		from SimpleSession import sessionID, sesRepr
		sesData = []
		for atoms in self.angleInfo:
			sesData.append([sessionID(a) for a in atoms])
		print>>sessionFile, "angleInfo = %s" % sesRepr(sesData)
		print>>sessionFile, """
try:
	from StructMeasure.gui import restoreAngles
	restoreAngles(angleInfo)
except:
	reportRestoreError("Error restoring angle monitors in session")
"""

	def _setDihedEnd(self, br, dihedMenu):
		"""callback when a 'near atoms' menu is set"""

		widgets, nearIndex, nearAtoms, farIndex, farAtoms = \
								self.rotInfo[br]
		index = dihedMenu.index(Pmw.SELECT)
		if dihedMenu is widgets[1]:
			nearIndex = index
		else:
			farIndex = index
		self.rotInfo[br] = [widgets, nearIndex, nearAtoms,
							farIndex, farAtoms]
		widgets[4].configure(angle=float("%.*f" %
			(prefs[TORSION_PRECISION], self.dihedral(br))))
		self._labelRot(br)
	
	def _toggleAngleType(self):
		if self.angleTitle.get() == "Torsion":
			self.angleTitle.set("Delta")
			self.rotTable.setColumnTitle(1, None)
			self.rotTable.setColumnTitle(3, None)
			for i in range(len(self.rotations)):
				br = self.rotations[i]
				ID, near, menu, far, dihed, delta = \
							self.rotInfo[br][0]
				dihed.grid_forget()
				near.grid_forget()
				far.grid_forget()
				delta.grid(row=i, column=4, sticky='ew')
				self.rotInfo[br][0][-2:] = delta, dihed
		else:
			self.angleTitle.set("Torsion")
			self.rotTable.setColumnTitle(1, "Near")
			self.rotTable.setColumnTitle(3, "Far")
			for i in range(len(self.rotations)):
				br = self.rotations[i]
				ID, near, menu, far, delta, dihed = \
							self.rotInfo[br][0]
				delta.grid_forget()
				dihed.grid(row=i, column=4, sticky='ew')
				near.grid(row=i, column=1, sticky='ew')
				far.grid(row=i, column=3, sticky='ew')
				self.rotInfo[br][0][-2:] = dihed, delta
		if self.rotLabelChoice.getvalue() == "Angle":
			for br in self.rotations:
				self._labelRot(br, "Angle")
			
	def _updateAngles(self):
		self.angleTable.refresh()

from OpenSave import SaveModeless
class _SaveStructInfo(SaveModeless):
	def __init__(self, structMeasure, **kw):
		self.structMeasure = structMeasure
		SaveModeless.__init__(self, **kw)

	def fillInUI(self, parent):
		SaveModeless.fillInUI(self, parent)
		self.saveTypes = Pmw.RadioSelect(self.clientArea, pady=0,
			buttontype='checkbutton', labelpos='w',
			orient='vertical', label_text="Save:")
		self.saveTypes.grid(row=0, column=0)
		for name in self.structMeasure.notebook.pagenames():
			mode = 'normal'
			if name not in [DISTANCES, ANGLES, BONDROTS, GEOMETRIES]:
				mode = 'disabled'
			self.saveTypes.add(name, state=mode)
			if mode == 'normal':
				self.saveTypes.invoke(name)

	def Apply(self):
		savePaths = self.getPaths()
		if not savePaths:
			replyobj.error("No save file specified\n")
			return
		from OpenSave import osOpen
		saveFile = osOpen(savePaths[0], "w")
		mols = chimera.openModels.list(modelTypes=[chimera.Molecule])
		for mol in mols:
			print>>saveFile, "Model %s is %s" % (mol.oslIdent(),
								mol.name)
		sm = self.structMeasure
		selected = self.saveTypes.getcurselection()
		if DISTANCES in selected:
			print>>saveFile, "\nDistance information"
			output = {}
			for d in sm.distances:
				a1, a2 = d.atoms
				distID = d.id
				if d.distance[-1].isdigit():
					dval = d.distance
				else:
					# omit angstrom character
					dval = d.distance[:-1]
				output[distID] = "%2d  %s <-> %s:  %s" % (
						distID, sm.atomLabel(a1),
						sm.atomLabel(a2), dval)
			ids = output.keys()
			ids.sort()
			for distID in ids:
				print>>saveFile, output[distID]

		if ANGLES in selected:
			print>>saveFile, "\nAngles/Torsions"
			printables = []
			maxLabel = 0
			for atoms in sm.angleInfo:
				labelArgs = tuple([sm.atomLabel(a)
							for a in atoms])
				if len(atoms) == 3:
					label = "%s -> %s -> %s" % labelArgs
					func = chimera.angle
				else:
					label = "%s -> %s -> %s -> %s" \
								% labelArgs
					func = chimera.dihedral
				maxLabel = max(maxLabel, len(label))
				printables.append((label, "%8.3f" %
						func(*tuple([a.xformCoord()
							for a in atoms]))))
			format = "%%%ds: %%s" % maxLabel
			for printArgs in printables:
				print>>saveFile, format % printArgs
				
		if BONDROTS in selected:
			print>>saveFile, "\nBond rotations"
			printables = []
			maxLabel = 0
			for br in sm.rotations:
				na, fa = sm.dihedEndAtoms(br)
				label = "%s -> %s -> %s -> %s" % (
					sm.atomLabel(na),
					sm.atomLabel(br.atoms[0]),
					sm.atomLabel(br.atoms[1]),
					sm.atomLabel(fa))
				maxLabel = max(maxLabel, len(label))
				printables.append((label,
						"%8.3f" % sm.dihedral(br),
						"%8.3f" % br.get()))
			format = "%%%ds: %%s (delta: %%s)" % maxLabel
			for printArgs in printables:
				print>>saveFile, format % printArgs
				
		if GEOMETRIES in selected:
			print>>saveFile, "\nAxes"
			print>>saveFile, "axis name, length, center, direction"
			from Axes import axisManager
			axes = axisManager.axes
			axes.sort(lambda a1, a2: cmp(a1.name, a2.name))
			nameSize = max([0] + [len(a.name) for a in axes])
			from chimera import Point
			for axis in axes:
				ends = [axis.direction * ext + axis.center
						for ext in axis.extents]
				cx, cy, cz = Point(ends)
				dx, dy, dz = axis.direction
				print>>saveFile, "%*s: %6.3f (%7.3f, %7.3f," \
					" %7.3f) (%6.3f, %6.3f, %6.3f)" % (
					nameSize, axis.name,
					abs(axis.extents[0] - axis.extents[1]),
					cx, cy, cz, dx, dy, dz)
			print>>saveFile, "\nPlanes"
			print>>saveFile, "plane name, center, normal, radius"
			from Planes import planeManager
			planes = planeManager.planes
			planes.sort(lambda p1, p2: cmp(p1.name, p2.name))
			nameSize = max([0] + [len(pl.name) for pl in planes])
			for plane in planes:
				ox, oy, oz = plane.plane.origin
				nx, ny, nz = plane.plane.normal
				print>>saveFile, "%*s: (%7.3f, %7.3f, %7.3f)" \
					" (%6.3f, %6.3f, %6.3f) %.3f"  % (nameSize, plane.name,
					ox, oy, oz, nx, ny, nz, plane.radius)
		saveFile.close()

class PmwableMenuButton(Tkinter.Menubutton):
	def __init__(self, *args, **kw):
		try:
			items = kw['items']
			del kw['items']
		except KeyError:
			items = []
		try:
			command = kw['command']
			del kw['command']
		except KeyError:
			command = None
		try:
			states = kw['states']
			del kw['states']
		except KeyError:
			states = ['normal'] * len(items)
		Tkinter.Menubutton.__init__(self, *args, **kw)
		self.menu = Tkinter.Menu(self)
		for i in range(len(items)):
			item = items[i]
			state = states[i]
			if command:
				self.menu.add_command(label=item, state=state,
					command=lambda c=command, i=item: c(i))
			else:
				self.menu.add_command(label=item, state=state)
		self.configure(menu=self.menu)

class PrecisionEntry(Tkinter.Label):
	"""Fake an Entry with a Label to allow making an uneditable Pmw.Counter"""
	def delete(self, *args, **kw):
		pass
	def insert(self, pos, text):
		self['text'] = text
	def get(self):
		return self['text']
	def index(self, *args, **kw):
		return 0
	def selection_present(self):
		return 0
	def xview(self, *args, **kw):
		pass
	def icursor(self, *args, **kw):
		pass

from chimera import dialogs
dialogs.register(StructMeasure.name, StructMeasure)

def addRotation(bond):
	d = dialogs.find(StructMeasure.name)
	import types
	br = bondRotMgr.rotationForBond(bond, create=False)
	if br == None:
		br = bondRotMgr.rotationForBond(bond)
	else:
		d.enter()
		d.setCategoryMenu(BONDROTS)
	return br

def addAngle(atoms):
	d = dialogs.display(StructMeasure.name)
	d._createAngle(atoms)
	d.setCategoryMenu(ANGLES)

def _showBondRotUI(trigger, myData, br):
	if chimera.nogui:
		return
	if trigger == bondRotMgr.CREATED:
		# some window managers are slow to raise windows
		# only auto-raise the dialog if a new rotation is created
		dialogs.display(StructMeasure.name)
	d = dialogs.find(StructMeasure.name)
	d.setCategoryMenu(BONDROTS)
	d.rotChange(trigger, br)
for trigger in bondRotMgr.triggerNames:
	bondRotMgr.triggers.addHandler(trigger, _showBondRotUI, None)

def restoreAngles(angleInfo):
	from SimpleSession import idLookup
	for atomIDs in angleInfo:
		addAngle([idLookup(aID) for aID in atomIDs])
	
# need restoreTorsions for old session files
def restoreTorsions(info):
	from SimpleSession import idLookup
	from BondRotMgr import bondRotMgr
	for bondID, atom1ID, atom2ID in info:
		br = bondRotMgr.rotationForBond(idLookup(bondID))
		br.anchorSide = idLookup(atom1ID)
