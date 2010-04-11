# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 29584 2009-12-10 22:30:41Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import UserError, replyobj
from prefs import prefs, defaults, SHOWN_COLS, DO_SELECT, DO_COLOR, \
	POCKET_COLOR, NONPOCKET_COLOR, DO_SURFACE, DO_ZOOM, EXCLUDE_MOUTH

def processCastpID(castpID):
	castpID = castpID.strip()
	if len(castpID) > 4:
		dir = "sccast"
	else:
		dir = "cast"
	castpID = castpID[:4].lower() + castpID[4:]
	baseUrl = "http://sts.bioengr.uic.edu/castp/%s/%s/" % (dir, castpID[1:3])
	pdb = fetchCastpFile(castpID, baseUrl, ".pdb")
	mouthAtoms = fetchCastpFile(castpID, baseUrl, ".mouth")
	mouthInfo = fetchCastpFile(castpID, baseUrl, ".mouthInfo")
	pocketAtoms = fetchCastpFile(castpID, baseUrl, ".poc")
	pocketInfo = fetchCastpFile(castpID, baseUrl, ".pocInfo")

	from CASTp import processCastpFiles
	structure, cavities = processCastpFiles(pdb, mouthAtoms, mouthInfo,
				pocketAtoms, pocketInfo, identifyAs=castpID)
	CastpDialog(castpID, cavities)
	return [structure]

def fetchCastpFile(castpID, baseUrl, suffix):
	filename = castpID + suffix
	from chimera import fetch
	path = fetch.fetch_local_file('CASTp', filename)
	if path:
		return path
	from urllib2 import urlopen
	try:
		file = urlopen(baseUrl + filename)
	except:
		raise UserError("ID %s not in CASTp database" % castpID)
	data = file.read()
	file.close()
	spath = fetch.save_fetched_data(data, 'CASTp', filename)
	if spath:
		return spath
	from StringIO import StringIO
	sfile = StringIO(data)
	return sfile

def openCastp(pocketPath):
	import os.path
	base, suffix = os.path.splitext(pocketPath)
	if suffix != ".poc":
		raise UserError(
			"CASTp pocket-atoms file must end in .poc, not %s\n"
			"(file: %s)" % (suffix, pocketPath))
	paths = []
	for suffix, description in [(".pdb", "PDB"), (".mouth", "mouth-atoms"),
					(".mouthInfo", "mouth-measurements"),
					(".poc", "pocket-atoms"),
					(".pocInfo", "pocket-measurements")]:
		path = base + suffix
		if not os.path.exists(path):
			raise UserError("CASTp %s file does not exist!\n"
				"(file: %s)" % (description, path))
		paths.append(path)
	from CASTp import processCastpFiles
	structure, cavities = processCastpFiles(*tuple(paths))
	name = os.path.basename(base)
	structure.name = name
	CastpDialog(name, cavities)
	return [structure]
			
class CastpDialog(ModelessDialog):
	help = "UsersGuide/castp.html"
	buttons = ("Quit", "Hide")
	def __init__(self, name, cavities, sessionData=None):
		self.title = "CASTp: %s" % name
		self.cavities = cavities
		from weakref import proxy
		def wrapper(s=proxy(self)):
			s._cavityChangeCB()
		for cav in cavities:
			cav.pocketInfo["atoms"].selChangedCB = wrapper
			cav.mouthInfo["atoms"].selChangedCB = wrapper
		if sessionData:
			self.tableData = sessionData
		else:
			self.tableData = None
		ModelessDialog.__init__(self)
		chimera.extension.manager.registerInstance(self)

	def fillInUI(self, parent):
		from sys import getrefcount
		import Tkinter, Pmw
		top = parent.winfo_toplevel()
		menubar = Tkinter.Menu(top, type="menubar", tearoff=False)
		top.config(menu=menubar)

		self.columnMenu = Tkinter.Menu(menubar)
		menubar.add_cascade(label="Columns", menu=self.columnMenu)

		from chimera.tkgui import aquaMenuBar
		aquaMenuBar(menubar, parent, row = 0)

		row = 1

		from CGLtk.Table import SortableTable
		self.cavityTable = SortableTable(parent, menuInfo=
				(self.columnMenu, prefs, dict.fromkeys(
				defaults[SHOWN_COLS], True), False))
		if not self.tableData:
			from CASTp import mouthFieldNames, pocketFieldNames
			# add preferred columns first
			shownCols = prefs[SHOWN_COLS]
			for fn in ("ID", "MS volume", "SA volume",
					"pocket MS area", "pocket SA area",
					"# openings"):
				if fn[0] == '#' or fn == "ID":
					kw = {'format': "%d"}
				else:
					kw = {'format': "%6.1f", 'font': "TkFixedFont"}
				self.cavityTable.addColumn(fn, "lambda c: "
					"c.pocketInfo['%s']" % fn, **kw)
			for fn in ("mouth MS area", "mouth SA area",
					"MS circumference sum",
					"SA circumference sum"):
				self.cavityTable.addColumn(fn, "lambda c: "
					"c.mouthInfo['%s']" % fn,
					format="%6.1f", font='TkFixedFont')
			for fieldNames, attrName in [
					(pocketFieldNames, "pocketInfo"),
					(mouthFieldNames, "mouthInfo")]:
				for fn in fieldNames:
					if fn[0] == '#' or fn == "ID":
						kw = {'format': "%d"}
					else:
						kw = {'format': "%6.1f", 'font': "TkFixedFont"}
					c = self.cavityTable.addColumn(fn,
						"lambda c: "
						"getattr(c, '%s')['%s']" %
						(attrName, fn), **kw)
					if fn == "ID":
						self.cavityTable.sortBy(c)
						self.cavityTable.sortBy(c)
		self.cavityTable.setData(self.cavities)
		self.cavityTable.launch(browseCmd=self._selCavityCB,
						restoreInfo=self.tableData)
		self.cavityTable.grid(row=row, column=0, sticky="nsew")
		parent.rowconfigure(row, weight=1)
		parent.columnconfigure(0, weight=1)
		row += 1

		grp = Pmw.Group(parent,
				tag_text="Treatment of Chosen Pocket Atoms")
		grp.grid(row=row)
		checkFrame = grp.interior()
		from CGLtk import Hybrid
		def buttonCB(s=self):
			self._selCavityCB(self.cavityTable.selected())
		self.doSelect = Hybrid.Checkbutton(checkFrame, "Select",
							prefs[DO_SELECT])
		self.doSelect.variable.add_callback(buttonCB)
		self.doSelect.button.grid(row=0, sticky='w')
		f = Tkinter.Frame(checkFrame)
		f.grid(row=1, sticky='w')
		self.doColor = Hybrid.Checkbutton(f, "Color",
							prefs[DO_COLOR])
		self.doColor.variable.add_callback(buttonCB)
		self.doColor.button.grid(row=0, column=0)
		from CGLtk.color.ColorWell import ColorWell
		self.pocketColor = ColorWell(f, color=prefs[POCKET_COLOR],
							noneOkay=True)
		self.pocketColor.grid(row=0, column=1)
		Tkinter.Label(f, text=" (and color all other atoms ").grid(
			row=0, column=2)
		self.nonpocketColor = ColorWell(f, color=prefs[NONPOCKET_COLOR],
							noneOkay=True)
		self.nonpocketColor.grid(row=0, column=3)
		Tkinter.Label(f, text=")").grid(row=0, column=4)
		self.doSurface = Hybrid.Checkbutton(checkFrame, "Surface",
							prefs[DO_SURFACE])
		self.doSurface.variable.add_callback(buttonCB)
		self.doSurface.button.grid(row=2, sticky='w')
		self.doZoom = Hybrid.Checkbutton(checkFrame, "Zoom in on",
							prefs[DO_ZOOM])
		self.doZoom.variable.add_callback(buttonCB)
		self.doZoom.button.grid(row=3, sticky='w')
		self.excludeMouth = Hybrid.Checkbutton(checkFrame,
				"Exclude mouth atoms", prefs[EXCLUDE_MOUTH])
		self.excludeMouth.variable.add_callback(buttonCB)
		self.excludeMouth.button.grid(row=4, sticky='w')
		row += 1

	def destroy(self):
		if self.cavities:
			cav1 = self.cavities[0]
			atoms = (cav1.mouthInfo["atoms"].atoms()
				or cav1.pocketInfo["atoms"].atoms())
			if atoms:
				# close surface too...
				from chimera import openModels
				mol = atoms[0].molecule
				openModels.close(openModels.list(
						id=mol.id, subid=mol.subid))
		for chk in [self.doSelect, self.doColor, self.doSurface,
						self.doZoom, self.excludeMouth]:
			chk.destroy()
		chimera.extension.manager.deregisterInstance(self)
		ModelessDialog.destroy(self)

	def emHide(self):
		"""Extension manager method"""
		self.Close()
	Hide = emHide

	def emName(self):
		"""Extension manager method"""
		return self.title

	def emQuit(self):
		"""Extension manager method"""
		self.destroy()
	Quit = emQuit

	def emRaise(self):
		"""Extension manager method"""
		self.enter()

	def _cavityChangeCB(self):
		newCavities = [cav for cav in self.cavities
					if len(cav.mouthInfo["atoms"]) > 0
					or len(cav.pocketInfo["atoms"]) > 0]
		if len(newCavities) == len(self.cavities):
			return
		
		if not newCavities:
			self.destroy()
			return

		self.cavities = newCavities
		self.cavityTable.setData(self.cavities)

	def _colDispChange(self, col):
		self.cavityTable.columnUpdate(col, display=not col.display)
		prefs[SHOWN_COLS] = [c.title for c in self.cavityTable.columns
								if c.display]

	def _selCavityCB(self, tableSel):
		prefs[EXCLUDE_MOUTH] = self.excludeMouth.variable.get()
		from chimera.selection import ItemizedSelection, mergeCurrent, \
								EXTEND, REMOVE
		cavitySel = ItemizedSelection()
		for cavity in tableSel:
			cavitySel.merge(EXTEND, cavity.pocketInfo["atoms"])
			if prefs[EXCLUDE_MOUTH]:
				cavitySel.merge(REMOVE,
						cavity.mouthInfo["atoms"])
		cavitySel.addImplied()
		# might be no cavities selected...
		cav1 = self.cavities[0]
		someA = (cav1.mouthInfo["atoms"].atoms()
			or cav1.pocketInfo["atoms"].atoms())[0]
		if someA.__destroyed__:
			return
		mol = someA.molecule
		cavitySet = set(cavitySel.atoms())
		from chimera import selectionOperation
		doSelect = self.doSelect.variable.get()
		if doSelect != prefs[DO_SELECT]:
			#if not doSelect:
			#	mergeCurrent(REMOVE, cavitySel)
			prefs[DO_SELECT] = doSelect
		doColor = self.doColor.variable.get()
		if doColor != prefs[DO_COLOR]:
			if not doColor and hasattr(self, '_prevColors'):
				for a, c, sc in self._prevColors:
					if a.__destroyed__:
						continue
					a.color = c
					a.surfaceColor = sc
				delattr(self, '_prevColors')
			prefs[DO_COLOR] = doColor
		if doColor:
			prefs[POCKET_COLOR] = self.pocketColor.rgba
			prefs[NONPOCKET_COLOR] = self.nonpocketColor.rgba
		doSurface = self.doSurface.variable.get()
		if doSurface != prefs[DO_SURFACE]:
			if not doSurface:
				for a in cavitySet:
					a.surfaceDisplay = False
			prefs[DO_SURFACE] = doSurface
		doZoom = self.doZoom.variable.get()
		if doZoom != prefs[DO_ZOOM]:
			if not doZoom:
				from Midas import focus, uncofr
				focus([mol])
				uncofr()
			prefs[DO_ZOOM] = doZoom

		if doSelect:
			selectionOperation(cavitySel)
		if doColor:
			if prefs[POCKET_COLOR] == None:
				pocketColor = None
			else:
				pocketColor = chimera.MaterialColor(
							*prefs[POCKET_COLOR])
			if prefs[NONPOCKET_COLOR] == None:
				nonpocketColor = None
			else:
				nonpocketColor = chimera.MaterialColor(
							*prefs[NONPOCKET_COLOR])
			if not hasattr(self, '_prevColors'):
				self._prevColors = [(a, a.color, a.surfaceColor)
							for a in mol.atoms]
			for a in mol.atoms:
				if a in cavitySet:
					a.surfaceColor = a.color = pocketColor
				else:
					a.surfaceColor = a.color = nonpocketColor
		if doSurface:
			for a in mol.atoms:
				a.surfaceDisplay = a in cavitySet
			surfs = chimera.openModels.list(mol.id, mol.subid,
					modelTypes=[chimera.MSMSModel])
			catsurfs = [s for s in surfs if s.category == "main"]
			if not catsurfs:
				from Midas import surfaceNew
				surfaceNew("main", models=[mol])

		if doZoom and tableSel:
			from Midas import align, focus
			align(cavitySel, mol.atoms)
			focus(cavitySel)
