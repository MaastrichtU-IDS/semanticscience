# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 29647 2009-12-18 00:44:25Z pett $

ADD_ATOMS = "Add Atoms"
CHANGE_ATOM = "Modify Atom"
ADD_DEL_BONDS = "Add/Delete Bonds"
SET_BOND_LEN = "Set Bond Length"
pageNames = [ADD_ATOMS, CHANGE_ATOM, ADD_DEL_BONDS, SET_BOND_LEN]

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import UserError, selection
from BuildStructure import setBondLength, placeHelium, changeAtom, ParamError, \
	placeFragment, placePeptide, elementRadius, addDihedralBond

class BuildStructureDialog(ModelessDialog):
	title = "Build Structure"
	name = "build structure"
	help = "ContributedSoftware/editing/editing.html"
	buttons = ("Close",)
	provideStatus = True
	statusPosition = "left"

	RES_NOOP = 0
	RES_RENAME = 1
	RES_MAKENEW = 2

	PLACE_ATOM = "atom"
	PLACE_FRAGMENT = "fragment"
	PLACE_SMILES = "SMILES string"
	PLACE_PUBCHEM = "PubChem CID"
	PLACE_PEPTIDE = "peptide sequence"
	PLACE_NUCLEIC = "nucleic sequence"

	def fillInUI(self, parent):
		import Pmw, Tkinter
		self.notebook = Pmw.NoteBook(parent, raisecommand=self._raiseCB)
		self.notebook.grid(sticky="nsew")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)

		for pn in pageNames:
			self.notebook.add(pn)

		self.resNameVar = Tkinter.StringVar(parent)
		self.resNameVar.set("UNK")
		self.chainNameVar = Tkinter.StringVar(parent)
		self.colorByElementVar = Tkinter.IntVar(parent)
		self.colorByElementVar.set(True)
		self._fillPlaceAtomPage()
		self._fillBondLenPage()
		self._fillChangeAtomPage()
		self._fillAddDelBondsPage()
		self.notebook.setnaturalsize()

		self.buttonWidgets['Help'].config(state='normal',
							command=self.Help)

	def _addBonds(self):
		atoms = selection.currentAtoms()
		if len(atoms) < 2:
			raise UserError("Must have at least 2 atoms selected")
		doAll = self.addBondsMenu.getvalue() != "reasonable"
		bondLength = chimera.Element.bondLength
		from chimera.molEdit import addBond
		for i, a1 in enumerate(atoms):
			for a2 in atoms[i+1:]:
				if a1.molecule != a2.molecule:
					continue
				if a2 in a1.bondsMap:
					continue
				if a1.altLoc and a2.altLoc \
				and a1.altLoc != a2.altLoc:
					continue
				if not doAll:
					if a1.xformCoord().distance(
					a2.xformCoord()) - bondLength(
					a1.element, a2.element) > 0.4:
						continue
				addBond(a1, a2)

	def _addParamBond(self):
		a1, a2 = selection.currentAtoms()
		side = self._apbSideMenu.getvalue()
		from chimera.misc import chimeraLabel
		sides = [chimeraLabel(a) for a in (a1, a2)]
		movingSide = sides.index(side)
		moving = (a1, a2)[movingSide]
		nonMoving = (a1, a2)[1-movingSide]
		args = [nonMoving, moving, self._apbLength.get()]
		for enumFunc, menu, option in [
				(self._enumerateAngles, self._apbAngleMenu, self._apbAngle),
				(self._enumerateDihedrals, self._apbDihedralMenu,
														self._apbDihedral)]:
			choice = menu.getvalue()
			for name, atoms in zip(*enumFunc(a1, a2)):
				if name == choice:
					args.append((atoms, option.get()))
					break
			else:
				args.append(None)
			
		addDihedralBond(*tuple(args))

	def _apbConfig(self, *args):
		selAtoms = selection.currentAtoms()
		twoOkayAtoms = False
		if not hasattr(self, "_apbBondHandler"):
			self._apbBondHandler = None
		if len(selAtoms) == 2:
			if not self._apbBondHandler:
				self._apbBondHandler = \
						chimera.triggers.addHandler(
						"Bond", self._apbConfig, None)
			a1, a2 = selAtoms
			if a1.oslIdent() > a2.oslIdent():
				a1, a2 = a2, a1
			rootA1 = a1.molecule.rootForAtom(a1, True)
			rootA2 = a2.molecule.rootForAtom(a2, True)
			if rootA1 != rootA2:
				twoOkayAtoms = True
		elif self._apbBondHandler:
			chimera.triggers.deleteHandler("Bond",
							self._apbBondHandler)
			self._apbBondHandler = None
			
		if twoOkayAtoms:
			osls = [a1.oslIdent(), a2.oslIdent()]
			if not hasattr(self, "_apbPrevAtoms"):
				self._apbPrevAtoms = None
			self._apbPrevAtoms = osls
			self._addParamBondButton.config(state="normal")
			self._apbLabel.config(fg="black")
			if self._apbPrevAtoms != osls:
				self._apbLength.set(elementRadius[a1.element] +
						elementRadius[a2.element])
			for enumFunc, menu in [
			(self._enumerateAngles, self._apbAngleMenu),
			(self._enumerateDihedrals, self._apbDihedralMenu)]:
				names, atoms = enumFunc(a1, a2)
				prevName = menu.getvalue()
				kw = {}
				if prevName in names:
					kw['index'] = prevName
				menu.setitems(names, **kw)
			kw = {}
			prevSide = self._apbSideMenu.getvalue()
			from chimera.misc import chimeraLabel
			sides = [chimeraLabel(a) for a in (a1, a2)]
			if prevSide in sides:
				kw['index'] = prevSide
			else:
				if rootA1.size.numAtoms < rootA2.size.numAtoms:
					kw['index'] = sides[0]
				else:
					kw['index'] = sides[1]
			self._apbSideMenu.setitems(sides, **kw)
		else:
			self._addParamBondButton.config(state="disabled")
			self._apbLabel.config(fg="red")
			self._apbAngleMenu.setitems([])
			self._apbDihedralMenu.setitems([])
			self._apbSideMenu.setitems([])
		if self._addParamBondButton.winfo_ismapped():
			self.notebook.setnaturalsize()
		
	def _changeAtom(self):
		selAtoms = selection.currentAtoms()
		if len(selAtoms) > 4:
			from chimera.baseDialog import AskYesNoDialog
			if AskYesNoDialog("Really change %d atoms?" %
			len(selAtoms)).run(self.uiMaster()) == 'no':
				self.enter()
				return
		if self.retainAtomNamesVar.get():
			for atom in selAtoms:
				if not self._changeSingleAtom(atom, atom.name):
					break
		elif self.atomNameInfo.get():
			assert(len(self._atomNameCache) == len(selAtoms))
			for atom, name in zip(selAtoms, self._atomNameCache):
				if not self._changeSingleAtom(atom, name):
					break
		else:
			for atom in selAtoms:
				if not self._changeSingleAtom(atom):
					break

	def _changeSingleAtom(self, atom, name=None):
		resMode = self.newresVar.get()
		if resMode == self.RES_MAKENEW:
			newResName = self._getResName()
			if newResName == None:
				return False
			oldRes = atom.residue
			oldRes.removeAtom(atom)
			chain = self.chainNameVar.get()
			oldID = oldRes.id
			if len(atom.bonds) > 0 and oldID == chain:
				pos = oldID.position + 1
			else:
				pos = 1
			while True:
				mid = chimera.MolResId(chain, pos)
				if not atom.molecule.findResidue(mid):
					break
				pos += 1
			newRes = atom.molecule.newResidue(newResName,
							chain, pos, ' ')
			newRes.addAtom(atom)
			if not oldRes.atoms:
				atom.molecule.deleteResidue(oldRes)
			chimera.selection._currentSelection._cache = {}
		elif resMode == self.RES_RENAME:
			newResName = self._getResName()
			if newResName == None:
				return False
			from BuildStructure import changeResidueType
			changeResidueType(atom.residue, newResName)
		numBonds = int(self.bondsMenu.getvalue())
		elementVal = self.elementMenu.getvalue()
		if type(elementVal) == str:
			element = chimera.Element(elementVal)
		else:
			element = chimera.Element(elementVal[-1])
		if numBonds < 2:
			if element.number > 2:
				geom = 4
			else:
				geom = 1
		else:
			import Pmw
			geom = self.geometryMenu.index(Pmw.SELECT) + numBonds
		if name == None:
			name=self.atomNameOption.get()
		try:
			changed = changeAtom(atom, element, geom, numBonds,
				autoClose=self.autocloseVar.get(), name=name)
		except ParamError, v:
			raise UserError(str(v))

		if self.autoFocusVar.get():
			from Midas import focus
			focus(atom.residue.atoms)
		if self.colorByElementVar.get():
			from Midas import color
			color("byelement", changed)
		return True

	def _delBonds(self):
		bonds = selection.currentBonds()
		if not bonds:
			raise UserError("Select at least one bond")
		for bond in bonds:
			bond.molecule.deleteBond(bond)

	def _drawFragment(self, frag):
		self.fragCanvas.delete("all")
		self.fragmentLookup[frag[-1]].depict(self.fragCanvas, scale=15)
		left, top, right, bottom = self.fragCanvas.bbox("all")
		self.fragCanvas.configure(width=right-left, height=bottom-top,
			scrollregion=(left, top, right, bottom))
		self.notebook.setnaturalsize()

	def _enumerateAngles(self, a1, a2):
		names, atoms = [], []
		from chimera.misc import chimeraLabel
		for na1 in a1.neighbors:
			names.append(u"%s\u2194%s\u2194%s" % (
					chimeraLabel(na1),
					chimeraLabel(a1, diffWith=na1),
					chimeraLabel(a2, diffWith=a1)))
			atoms.append((na1, a1, a2))
		for na2 in a2.neighbors:
			names.append(u"%s\u2194%s\u2194%s" % (
					chimeraLabel(a1),
					chimeraLabel(a2, diffWith=a1),
					chimeraLabel(na2, diffWith=a2)))
			atoms.append((a1, a2, na2))
		return names, atoms

	def _enumerateDihedrals(self, a1, a2):
		names, atoms = [], []
		from chimera.misc import chimeraLabel
		for na1 in a1.neighbors:
			for na2 in a2.neighbors:
				names.append(u"%s\u2194%s\u2194%s\u2194%s" % (
					chimeraLabel(na1),
					chimeraLabel(a1, diffWith=na1),
					chimeraLabel(a2, diffWith=a1),
					chimeraLabel(na2, diffWith=a2)))
				atoms.append((na1, a1, a2, na2))
		return names, atoms

	def _fillPlaceAtomPage(self):
		import Pmw, Tkinter
		atomPage = self.notebook.page(ADD_ATOMS)
		self.placeTypeVar = Tkinter.StringVar(atomPage)
		self.apGroups = {}
		for row, val in enumerate([self.PLACE_ATOM, self.PLACE_FRAGMENT,
				self.PLACE_SMILES, self.PLACE_PUBCHEM,
				self.PLACE_PEPTIDE, self.PLACE_NUCLEIC]):
			rb = Tkinter.Radiobutton(atomPage, text=val,
				value=val, variable=self.placeTypeVar,
				command=lambda val=val:
				self._showPlaceGroup(val, 0))
			rb.grid(row=row, column=1, sticky="w")
			if row > 4:
				rb.config(state="disabled")
			self.apGroups[val] = Pmw.Group(atomPage, tag_text=
				" ".join([x[1:].islower() and x.capitalize()
				or x for x in (val + " parameters").split()]))
		Tkinter.Button(atomPage, text="Add", command=self._placeAtoms
			).grid(row=0, column=0, rowspan=len(self.apGroups))
		f = Tkinter.Frame(atomPage)
		f.grid(row=len(self.apGroups), column=0, columnspan=3)
		from chimera.widgets import NewMoleculeOptionMenu
		self.molMenu = NewMoleculeOptionMenu(f, labelpos='w',
			label_text="Put atoms in", command=self._molMenuCB)
		self.molMenu.grid(row=0, column=0, sticky='e')
		from chimera.tkoptions import StringOption
		self.molName = StringOption(f, 0, "named", "scratch", None,
							startCol=2)
		self._molMenuCB()
		Tkinter.Checkbutton(atomPage, variable=self.colorByElementVar,
			text="Color new atoms by element"
			).grid(row=len(self.apGroups)+1, column=0, columnspan=3)


		atomGroup = self.apGroups[self.PLACE_ATOM]
		Tkinter.Label(atomGroup.interior(), text=
			"Place helium atom in center of view.\n"
			"Use '%s' tab to change element type\n"
			"and add bonded atoms." % CHANGE_ATOM).grid()
		self.placeTypeVar.set("atom")
		lw = Pmw.LabeledWidget(atomGroup.interior(), labelpos='w',
			label_text="Residue name:")
		lw.grid(row=1)
		Tkinter.Entry(lw.interior(), width=4,
					textvariable=self.resNameVar).grid()
		self.autoselAtomVar = Tkinter.IntVar(atomGroup.interior())
		self.autoselAtomVar.set(True)
		Tkinter.Checkbutton(atomGroup.interior(),
			variable=self.autoselAtomVar, text="Select placed atom"
			).grid()
		self._showPlaceGroup("atom", 0)

		fragmentGroup = self.apGroups[self.PLACE_FRAGMENT]
		from Fragment import fragments, RING6
		menuItems, self.fragmentLookup = self._processFragments(
								fragments)
		from CGLtk.optCascade import CascadeOptionMenu
		self.fragMenu = CascadeOptionMenu(fragmentGroup.interior(),
			labelpos="w", label_text="Fragment", items=menuItems,
			buttonStyle="final", command=self._drawFragment)
		self.fragMenu.grid(row=1, column=0)
		self.fragCanvas = Tkinter.Canvas(fragmentGroup.interior())
		self.fragCanvas.grid(row=1, column=1)
		self.fragMenu.invoke([RING6, "benzene"])
		lw = Pmw.LabeledWidget(fragmentGroup.interior(), labelpos='w',
			label_text="Residue name:")
		lw.grid(row=2, columnspan=2)
		Tkinter.Entry(lw.interior(), width=4,
					textvariable=self.resNameVar).grid()

		smilesGroup = self.apGroups[self.PLACE_SMILES]
		from chimera.tkoptions import StringOption
		self.smilesEntry = StringOption(smilesGroup.interior(), 0,
			"SMILES string", "", None, width=25)
		smilesGroup.interior().columnconfigure(1, weight=1)
		StringOption(smilesGroup.interior(), 1, "Residue name",
						self.resNameVar.get(), None,
						textvariable=self.resNameVar)
		from chimera.HtmlText import HtmlText
		plainTexts = [ "SMILES support courtesy of ", "cheminformatics@iu",
							" ", "web services" ]
		urls = [ '<a href="http://cheminfo.wikispaces.com">',
		'</a>',
		'<a href="http://cheminfo.wikispaces.com/Web+service+infrastructure">',
		'</a>' ]
		html = HtmlText(smilesGroup.interior(),
				width=len("".join(plainTexts)), height=1, bd=0)
		for plain, url in zip(plainTexts, urls):
			html.insert("end", plain+url)
		html.tag_add("center", "0.0", "end")
		html.tag_configure("center", justify="center")
		html.configure(state="disabled")
		html.grid(row=2, column=0, columnspan=2)

		pubChemGroup = self.apGroups[self.PLACE_PUBCHEM]
		from chimera.tkoptions import StringOption
		self.pubChemEntry = StringOption(pubChemGroup.interior(), 0,
			"PubChem CID", "", None, width=6)
		pubChemGroup.interior().columnconfigure(1, weight=1)
		StringOption(pubChemGroup.interior(), 1, "Residue name",
						self.resNameVar.get(), None,
						textvariable=self.resNameVar)
		from chimera.HtmlText import HtmlText
		plainTexts = [ "PubChem CID support courtesy of ",
					"cheminformatics@iu", " ", "web services" ]
		html = HtmlText(pubChemGroup.interior(),
				width=len("".join(plainTexts)), height=1, bd=0)
		for plain, url in zip(plainTexts, urls):
			html.insert("end", plain+url)
		html.tag_add("center", "0.0", "end")
		html.tag_configure("center", justify="center")
		html.configure(state="disabled")
		html.grid(row=2, column=0, columnspan=2)

		peptideGroup = self.apGroups[self.PLACE_PEPTIDE]
		pgi = peptideGroup.interior()
		self.peptideSequence = Pmw.ScrolledText(pgi,
			text_height=2, text_width=30, text_wrap='char',
			labelpos='n', label_text="Peptide Sequence")
		self.peptideSequence.grid(row=1, sticky='nsew')
		Tkinter.Label(pgi, text=u"'Add' button will bring up dialog"
			u" for setting \u03A6/\u03A8 angles").grid(row=2,
			column=0)

	def _fillBondLenPage(self):
		import Pmw, Tkinter
		blPage = self.notebook.page(SET_BOND_LEN)
		self.blEntry = Pmw.EntryField(blPage, validate={'min': 0.001,
				'minstrict': False, 'validator': 'real'},
				value='1.0', entry_width=5, labelpos='w',
				command=self._setBondLength,
				label_text="Set length of selected bonds to:")
		self.blEntry.grid(row=0, column=0)

		sideFrame = Tkinter.Frame(blPage)
		sideFrame.grid(row=1, column=0)
		Tkinter.Label(sideFrame, text="Move atoms on").grid(row=0,
						column=0, rowspan=2, sticky='e')
		self.blSideVar = Tkinter.StringVar(blPage)
		for row, val in enumerate(["smaller side", "larger side"]):
			Tkinter.Radiobutton(sideFrame, text=val, value=val,
				variable=self.blSideVar).grid(row=row,
				column=1, sticky='w')
		self.blSideVar.set("smaller side")
			
	def _fillChangeAtomPage(self):
		import Tkinter, Pmw
		caPage = self.notebook.page(CHANGE_ATOM)
		
		row = 0
		Tkinter.Button(caPage, text="Change", command=self._changeAtom
			).grid(row=row, column=0, sticky='e')
		Tkinter.Label(caPage, text="selected atoms to...").grid(row=0,
			column=1, sticky='w')
		row += 1

		paramFrame = Tkinter.Frame(caPage, bd=1, relief='solid')
		paramFrame.grid(row=row, column=0, columnspan=2)
		row += 1

		from chimera.selection.element \
				import frequentElements, elementRanges
		elementNames = chimera.elements.name[:]
		elementNames.remove("LP")
		elementNames.sort()
		menuItems = frequentElements[:]
		subItems = []
		for start, end in elementRanges:
			subItems.append(("%s-%s" % (start, end),
				elementNames[elementNames.index(start):
					elementNames.index(end)+1]))
		menuItems.append(("other", subItems))
		from CGLtk.optCascade import CascadeOptionMenu
		self.elementMenu = CascadeOptionMenu(paramFrame, labelpos="n",
				label_text="Element", items=menuItems,
				command=lambda *args: self._genAtomNameCB(),
				initialitem=["C"], buttonStyle="final")
		self.elementMenu.grid(row=0, column=0)

		self.bondsMenu = Pmw.OptionMenu(paramFrame, labelpos="n",
			label_text="Bonds", command=self._newBonds,
			items=[str(x) for x in range(5)], initialitem=4)
		self.bondsMenu.grid(row=0, column=1)

		from chimera.bondGeom import geometryName
		self.geometryMenu = Pmw.OptionMenu(paramFrame, labelpos="n",
			label_text="Geometry",
			items=geometryName[4:], initialitem=geometryName[4])
		self.geometryMenu.grid(row=0, column=2)

		nameFrame = Tkinter.Frame(paramFrame)
		nameFrame.grid(row=1, column=0, columnspan=3)
		self.retainAtomNamesVar = Tkinter.IntVar(nameFrame)
		self.retainAtomNamesVar.set(True)
		self.retainAtomNameButton = Tkinter.Radiobutton(nameFrame,
			text="Retain current atom names",
			variable=self.retainAtomNamesVar, value=True)
		self.retainAtomNameButton.grid(row=0, sticky='w')
		customNameFrame = Tkinter.Frame(nameFrame)
		customNameFrame.grid(row=1, sticky='w')
		self.customAtomNameButton = Tkinter.Radiobutton(customNameFrame,
			text="Set atom names to:",
			variable=self.retainAtomNamesVar, value=False)
		self.customAtomNameButton.grid(row=0, sticky='w')
		from chimera.tkoptions import StringOption
		self.atomNameOption = StringOption(customNameFrame, 0, "", "",
			lambda opt: self._genAtomNameCB(infoOnly=True),
			startCol=1, width=4)
		self.atomNameInfo = Tkinter.StringVar(paramFrame)
		self.atomNameInfo.set("")
		Tkinter.Label(customNameFrame, textvariable=self.atomNameInfo
						).grid(row=0, column=3)
		self.newresVar = Tkinter.IntVar(caPage)
		self.newresVar.set(self.RES_RENAME)
		self._genAtomNameCB()
		chimera.triggers.addHandler('selection changed',
				lambda *args: self._genAtomNameCB(), None)

		paramFrame.columnconfigure(0, pad="0.1i")
		paramFrame.columnconfigure(1, pad="0.1i")
		paramFrame.columnconfigure(2, pad="0.1i")

		cbFrame = Tkinter.Frame(caPage)
		cbFrame.grid(row=row, column=0, columnspan=2)
		row += 1

		self.autocloseVar = Tkinter.IntVar(caPage)
		self.autocloseVar.set(True)
		Tkinter.Checkbutton(cbFrame, variable=self.autocloseVar,
			text="Connect to pre-existing atoms if appropriate"
			).grid(row=0, column=0, sticky='w')
		self.autoFocusVar = Tkinter.IntVar(caPage)
		self.autoFocusVar.set(False)
		Tkinter.Checkbutton(cbFrame, variable=self.autoFocusVar,
			text="Focus view on modified residue"
			).grid(row=1, column=0, sticky='w')
		Tkinter.Checkbutton(cbFrame, variable=self.colorByElementVar,
			text="Color new atoms by element"
			).grid(row=2, column=0, sticky='w')
		resGroup = Pmw.Group(cbFrame, tag_text="Residue Name")
		resGroup.grid(row=3, column=0)
		rgFrame = resGroup.interior()
		Tkinter.Radiobutton(rgFrame, variable=self.newresVar,
			text="Leave unchanged", value=self.RES_NOOP).grid(
			row=0, sticky='w')
		f1 = Tkinter.Frame(rgFrame)
		f1.grid(row=1, sticky='w')
		Tkinter.Radiobutton(f1, variable=self.newresVar,
			text="Change modified residue's name to",
			command=self._genAtomNameCB, value=self.RES_RENAME
			).grid(row=0, column=0, sticky='w')
		Tkinter.Entry(f1, width=4, textvariable=self.resNameVar
			).grid(row=0, column=1, sticky='w')
		f2 = Tkinter.Frame(rgFrame)
		f2.grid(row=2, sticky='w')
		Tkinter.Radiobutton(f2, variable=self.newresVar,
			text="Put just changed atoms in new residue named",
			command=self._genAtomNameCB, value=self.RES_MAKENEW
			).grid(row=0, column=0, sticky='w')
		Tkinter.Entry(f2, width=4, textvariable=self.resNameVar
			).grid(row=0, column=1, sticky='w')
		Tkinter.Label(f2, text="in chain").grid(row=0, column=2)
		Tkinter.Entry(f2, width=3, textvariable=self.chainNameVar
			).grid(row=0, column=4)

	def _fillAddDelBondsPage(self):
		import Pmw, Tkinter
		adbPage = self.notebook.page(ADD_DEL_BONDS)

		Tkinter.Button(adbPage, text="Delete", command=self._delBonds
					).grid(row=0, column=0, sticky="e")
		Tkinter.Label(adbPage, text="selected bonds").grid(row=0,
							column=1, sticky='w')
		f = Tkinter.Frame(adbPage)
		f.grid(row=1, column=0, columnspan=2)
		Tkinter.Button(f, text="Add", command=self._addBonds).grid(
							row=0, column=0)
		self.addBondsMenu = Pmw.OptionMenu(f, initialitem=
			"reasonable", items=["reasonable", "all possible"],
			labelpos='e', label_text="bonds between selected atoms")
		self.addBondsMenu.grid(row=0, column=1)

		"""
		row2 = Tkinter.Frame(adbPage)
		row2.grid(row=2, column=0, columnspan=2)
		f = Tkinter.Frame(row2)
		f.grid(row=0, column=0)
		self._addParamBondButton = Tkinter.Button(f, text="Add",
						command=self._addParamBond)
		self._addParamBondButton.grid(row=0, column=0)
		Tkinter.Label(f, text="bond between ").grid(row=0, column=1)
		self._apbLabel = Tkinter.Label(f, text="2 selected atoms")
		self._apbLabel.grid(row=0, column=2)
		Tkinter.Label(f, text=" in different models using below criteria"
			).grid(row=0, column=3, columnspan=3)
		apbGroup = Pmw.Group(row2, tag_text="Bond Criteria")
		apbGroup.grid(row=1, column=0)
		interior = apbGroup.interior()
		from chimera.tkoptions import FloatOption
		Tkinter.Label(interior, text="length:").grid(row=0, column=0,
								sticky='e')
		self._apbLength = FloatOption(interior, 0, "", 1.54, None,
							min=0.0, startCol=1)
		f = Tkinter.Frame(interior)
		f.grid(row=1, column=0, sticky='e')
		self._apbAngleMenu = Pmw.OptionMenu(f)
		self._apbAngleMenu.grid(row=0, column=0)
		Tkinter.Label(f, text=" angle:").grid(row=0, column=1)
		self._apbAngle = FloatOption(interior, 1, "", 120.0, None,
								startCol=1)
		f = Tkinter.Frame(interior)
		f.grid(row=2, column=0, sticky='e')
		self._apbDihedralMenu = Pmw.OptionMenu(f)
		self._apbDihedralMenu.grid(row=0, column=0)
		Tkinter.Label(f, text=" dihedral:").grid(row=0, column=1)
		self._apbDihedral = FloatOption(interior, 2, "", 180.0, None,
							startCol=1)
		f = Tkinter.Frame(interior)
		f.grid(row=3, column=0, columnspan=3)
		Tkinter.Label(f, text="Move atoms on").grid(row=0, column=0)
		self._apbSideMenu = Pmw.OptionMenu(f)
		self._apbSideMenu.grid(row=0, column=1)
		Tkinter.Label(f, text="side").grid(row=0, column=2)

		chimera.triggers.addHandler("selection changed",
							self._apbConfig, None)
		self._apbConfig()
		"""

	def _finishPlace(self, atoms):
		for a in atoms:
			a.drawMode = chimera.Atom.Ball
			for b in a.bonds:
				b.drawMode = chimera.Bond.Stick
		if self.colorByElementVar.get():
			from Midas import color
			color("byelement", atoms)
		
	def _genAtomNameCB(self, infoOnly=False):
		selResidues = chimera.selection.currentResidues()
		selAtoms = chimera.selection.currentAtoms()
		atomName = element = self.elementMenu.getvalue()[-1].upper()
		if not infoOnly:
			for a in selAtoms:
				if a.element.name != element:
					self.retainAtomNamesVar.set(False)
					self.retainAtomNameButton.configure(
							state="disabled")
					break
			else:
				self.retainAtomNameButton.configure(
							state="normal")
				self.retainAtomNamesVar.set(True)
		self.atomNameInfo.set("")
		if self.newresVar.get() == self.RES_MAKENEW:
			atomName += "1"
		elif len(selAtoms) == 1 \
		and selAtoms[0].name.startswith(atomName):
			atomName = selAtoms[0].name
		elif len(selResidues) == 1:
			from chimera.molEdit import genAtomName
			if infoOnly:
				atomName = self.atomNameOption.get()
			else:
				atomName = genAtomName(element, selResidues[0])
			if len(selAtoms) > 1:
				if atomName == element:
					atomName += "1"
				self._atomNameCache = [atomName]
				rem = atomName[len(element):]
				try:
					num = int(rem)
				except ValueError:
					pass
				else:
					needed = len(selAtoms) - 1
					selSet = set(selAtoms)
					remResAtoms = set(selResidues[0].atoms
								) - selSet
					remNames = set([a.name
							for a in remResAtoms])
					while needed:
						num += 1
						while element + str(num) \
								in remNames:
							num += 1
						self._atomNameCache.append(
							"%s%d" % (element, num))
						needed -= 1
					self.atomNameInfo.set("through %s%d"
							% (element, num))
		if infoOnly:
			return
					
		self.atomNameOption.set(atomName)
		chains = set([r.id.chainId for r in selResidues])
		if len(chains) != 1:
			self.chainNameVar.set("het")
		else:
			chain = chains.pop()
			if chain == "water":
				self.chainNameVar.set("het")
			else:
				self.chainNameVar.set(chain)

	def _getMol(self):
		m = self.molMenu.getvalue()
		if type(m) == str:
			m = self.molName.get()
		return m

	def _getResName(self):
		rn = self.resNameVar.get().strip()
		if not rn:
			self.enter()
			raise UserError("Must specify a residue name")
		if len(rn) > 4 or not rn.isalnum():
			from chimera.baseDialog import AskYesNoDialog
			if AskYesNoDialog(
			"Residue names longer than 4 characters\n"
			"or containing non-alphanumeric characters\n"
			"can be problematic when saving to certain\n"
			"file formats (e.g. PDB).\n"
			"\n"
			"Really use residue name '%s'?" % rn).run(
			self.uiMaster()) == 'no':
				self.enter()
				return None
		return rn

	def Help(self):
		chimera.help.display("ContributedSoftware/editing/editing.html#"
			+ "setbond")

	def _molMenuCB(self, val=None):
		val = self.molMenu.getvalue()
		if type(val) == str:
			self.molName.gridManage()
		else:
			self.molName.gridUnmanage()

	def _newBonds(self, val):
		numBonds = int(val)
		mb = self.geometryMenu.component('menubutton')
		if numBonds < 2:
			mb.configure(state="normal")
			self.geometryMenu.setvalue("N/A")
			mb.configure(state="disabled")
			return
		mb.configure(state="normal")
		from chimera.bondGeom import geometryName
		availGeoms = geometryName[numBonds:]
		self.geometryMenu.setitems(availGeoms, index=availGeoms[0])
			
	def _placeAtoms(self):
		placeType = self.placeTypeVar.get()

		if placeType in [self.PLACE_ATOM, self.PLACE_FRAGMENT,
				self.PLACE_SMILES, self.PLACE_PUBCHEM]:
			resName = self._getResName()
			if resName is None:
				return
		m = self._getMol()
		if placeType == self.PLACE_ATOM:
			h = placeHelium(resName, model=m)
			if self.autoselAtomVar.get():
				chimera.selection.setCurrent(h)
			atoms = [h]
		elif placeType in [self.PLACE_FRAGMENT, self.PLACE_SMILES,
						self.PLACE_PUBCHEM]:
			if placeType == self.PLACE_FRAGMENT:
				frag = self.fragmentLookup[
						self.fragMenu.getvalue()[-1]]
				r = placeFragment(frag, resName, model=m)
			elif placeType == self.PLACE_SMILES:
				from Smiles import openSmiles
				m = openSmiles(self.smilesEntry.get(),
							resName=resName)
				r = m.residues[0]
			else:
				from PubChem import openPubChem
				m = openPubChem(self.pubChemEntry.get(),
							resName=resName)
				r = m.residues[0]
			atoms = r.atoms
		else:
			seq = self.peptideSequence.get().strip()
			PeptideDialog(seq, self._placePeptideCB)
			return

		self._finishPlace(atoms)

	def _placePeptideCB(self, seq, phiPsis, chainID, libName):
		try:
			residues = placePeptide(seq, phiPsis, rotlib=libName,
				model=self._getMol(), chainID=chainID)
		except ValueError, v:
			raise UserError(v)
		atoms = []
		for r in residues:
			atoms.extend(r.atoms)

		self._finishPlace(atoms)

	def _processFragments(self, fragments):
		menuItems = []
		lookup = {}
		for item in fragments:
			if type(item) == list:
				# submenu
				subitems, sublookup = self._processFragments(
								item[1])
				menuItems.append([item[0], subitems])
				lookup.update(sublookup)
			else:
				# Fragment
				menuItems.append(item.name)
				lookup[item.name] = item
		return menuItems, lookup

	def _raiseCB(self, pageName):
		if pageName == SET_BOND_LEN:
			bonds = selection.currentBonds()
			if len(bonds) == 1:
				self.blEntry.setvalue("%.3f"
							% bonds[0].length())
	def _setBondLength(self):
		self.status("")
		if not self.blEntry.valid():
			raise UserError("Invalid bond length specified")
		bondLength = float(self.blEntry.getvalue())

		cbs = selection.currentBonds()
		if not cbs:
			raise UserError("No bonds selected")

		side = self.blSideVar.get()
		for bond in cbs:
			setBondLength(bond, bondLength, movingSide=side,
							status=self.status)
	def _showPlaceGroup(self, val, row):
		for group in self.apGroups.values():
			group.grid_forget()
		self.apGroups[val].grid(row=row, column=2,
						rowspan=len(self.apGroups))
		self.notebook.setnaturalsize()

class PeptideDialog(ModelessDialog):
	oneshot = True
	title = "Add Peptide Sequence"
	help = "ContributedSoftware/editing/editing.html#peptide-angles"

	def __init__(self, seq, cb):
		self.seq = seq
		self.cb = cb
		ModelessDialog.__init__(self)
	
	def fillInUI(self, parent):
		from CGLtk.Table import SortableTable
		table = self.table = SortableTable(parent,
							allowUserSorting=False)
		table.addColumn("Res", "code")
		table.addColumn(u"\u03A6", "phi", format="%g")
		table.addColumn(u"\u03A8", "psi", format="%g")
		class ResData:
			pass
		self.data = data = []
		for c in self.seq:
			rd = ResData()
			rd.code = c
			rd.phi, rd.psi = PhiPsiOption.values[0]
			data.append(rd)
		table.setData(data)
		table.launch()
		table.grid(row=0, column=0, sticky="nsew", columnspan=6)
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(5, weight=1)
		import Tkinter
		Tkinter.Button(parent, text="Set", command=self._setPhiPsi,
			pady=0, padx=0).grid(row=1, column=0)
		Tkinter.Label(parent, text="selected rows to").grid(row=1,
								column=1)
		from chimera.tkoptions import FloatOption
		self.phi = FloatOption(parent, 1, u"\u03A6", 0.0, None, width=6,
							sticky='w', startCol=2)
		self.psi = FloatOption(parent, 1, u"\u03A8", 0.0, None, width=6,
							sticky='w', startCol=4)
		f = Tkinter.Frame(parent)
		f.grid(row=2, columnspan=6)
		self._seedPhiPsi(
			PhiPsiOption(f, 0, u"Seed above \u03A6/\u03A8 with"
					u" values for", PhiPsiOption.values[0],
					self._seedPhiPsi))
		from Rotamers.gui import RotLibOption, defaultLib
		f2 = Tkinter.Frame(parent)
		f2.grid(row=3, columnspan=6)
		self.rotlib = RotLibOption(f2, 0, "Rotamer library",
							defaultLib(), None)
		from chimera.tkoptions import StringOption
		self.chainID = StringOption(f2, 0, "chain ID", "A", None,
							width=1, startCol=2)

	def Apply(self):
		self.cb(self.seq, [(d.phi, d.psi) for d in self.data],
			self.chainID.get(), self.rotlib.get().importName)

	def _seedPhiPsi(self, opt):
		phi, psi = opt.get()
		self.phi.set(phi)
		self.psi.set(psi)

	def _setPhiPsi(self):
		residues = self.table.selected()
		if not residues:
			raise UserError("No table rows selected")
		phi = self.phi.get()
		psi = self.psi.get()
		for r in residues:
			r.phi = phi
			r.psi = psi
		self.table.refresh()

from chimera.tkoptions import SymbolicEnumOption
class PhiPsiOption(SymbolicEnumOption):
	values = ((-57, -47),
		(-139, 135),
		(-119, 113),
		(-49, -26),
		(-57, -70))
	## Tk 8.4 rendering of Unicode pretty yucky
	#labels = ("alpha helix", "3/10 helix",
	#	"pi helix", "parallel beta strand",
	#	"anti-parallel beta strand")
	# but Tk 8.5 rendering is okay
	labels = (u"\u03B1 helix",
		u"antiparallel \u03B2 strand",
		u"parallel \u03B2 strand",
		# subscripts look shitty and subscript zero doesn't even work,
		# so instead of using:
		#u"3\u2081\u2080 helix",
		# use:
		"3/10 helix",
		u"\u03C0 helix")

from chimera.dialogs import register
register(BuildStructureDialog.name, BuildStructureDialog)
