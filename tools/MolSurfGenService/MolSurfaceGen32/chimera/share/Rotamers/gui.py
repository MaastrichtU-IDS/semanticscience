# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 29586 2009-12-10 22:38:08Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import UserError, replyobj
from prefs import prefs, LIBRARY
from SimpleSession import SAVE_SESSION, registerAttribute

class RotamerDialog(ModelessDialog):
	buttons = ('OK', 'Apply', 'Close',)
	oneshot = True
	help = "ContributedSoftware/rotamers/rotamers.html#rotamerlist"

	def __init__(self, residue, resType, lib, sessionData=None):
		self._sesHandlerID = chimera.triggers.addHandler(SAVE_SESSION,
							self._sessionCB, None)
		self.residue = residue
		self.lib = lib
		self.resType = resType
		self.title = "%s Side-Chain Rotamers" % residue
		if sessionData:
			self.bbdep, self.rotamers, self.tableData = sessionData
		else:
			from Rotamers import getRotamers
			self.bbdep, self.rotamers = getRotamers(residue,
					log=True, lib=lib, resType=resType)
			from Midas import linewidth, color
			linewidth(2, self.rotamers)
			color('byhet', self.rotamers)
			chimera.openModels.add(self.rotamers,
					sameAs=residue.molecule, hidden=True, noprefs=True)
			registerAttribute(chimera.Molecule, "chis")
			registerAttribute(chimera.Molecule, "rotamerProb")
			self.tableData = None
		self.resHandlerID = chimera.triggers.addHandler(
					'Residue', self._resChangeCB, None)
		self.dependentDialogInfo = [('Clashes', 'clash'),
				('H-Bonds', 'hbond'), ('Density', 'volume')]
		for label, ddn in self.dependentDialogInfo:
			setattr(self, ddn + "Dialog", None)
		ModelessDialog.__init__(self)
	
	def fillInUI(self, parent):
		import Tkinter, Pmw, Tix
		top = parent.winfo_toplevel()
		menubar = Tkinter.Menu(top, type="menubar", tearoff=False)
		top.config(menu=menubar)

		selectMenu = Tkinter.Menu(menubar)
		menubar.add_cascade(label="Select", menu=selectMenu)
		selectMenu.add_command(label="Current Rotamers",
						command=self._selCurCB)
		selectMenu.add_command(label="All Rotamers",
						command=self._selAllCB)

		self.columnMenu = Tkinter.Menu(menubar)
		menubar.add_cascade(label="Columns", menu=self.columnMenu)

		self.addColumnMenu = Tkinter.Menu(self.columnMenu)
		self.columnMenu.add_cascade(label="Add",
						menu=self.addColumnMenu)
		for label, ddn in self.dependentDialogInfo:
			self.addColumnMenu.add_command(label=label + "...",
					command=lambda name=ddn+"Dialog":
					self._showDialog(name))
		self.columnMenu.add_separator()

		from chimera.tkgui import aquaMenuBar
		aquaMenuBar(menubar, parent, row = 0)

		self.numChis = len(self.rotamers[0].chis)
		row = 1
		Tkinter.Label(parent, text="%s %s rotamers" %
				(self.lib.displayName, self.resType)).grid(
				row=row, column=0)
		row += 1

		self.buttonWidgets['OK'].config(state="disabled")
		self.buttonWidgets['Apply'].config(state="disabled")
		from CGLtk.Table import SortableTable
		self.rotTable = SortableTable(parent,
				menuInfo=(self.columnMenu, prefs, {}, True))
		if not self.tableData:
			for i in range(self.numChis):
				self.rotTable.addColumn("Chi %d" % (i+1),
						"lambda r: r.chis[%d]" % i,
						format="%6.1f")
			self.rotTable.addColumn("Probability", "rotamerProb",
							format="%.6f", font='TkFixedFont')
		self.rotTable.setData(self.rotamers)
		self.rotTable.launch(browseCmd=self._selRotamerCB,
						restoreInfo=self.tableData)
		delattr(self, 'tableData')
		parent.rowconfigure(row, weight=1)
		for tableColumn in range(1):
			parent.columnconfigure(tableColumn, weight=1)
		self.rotTable.grid(row=row, column=0, sticky="nsew")
		row += 1

	def addClashColumn(self, *args):
		from Rotamers import processClashes
		format = processClashes(self.residue, self.rotamers, *args)
		self.rotTable.addColumn("Clashes", "clashScore", format=format,
								display=True)
		registerAttribute(chimera.Molecule, "clashScore")

	def addHbondColumn(self, *args):
		from Rotamers import processHbonds
		processHbonds(self.residue, self.rotamers, *args)
		self.rotTable.addColumn("H-Bonds", "numHbonds", format="%d",
								display=True)
		registerAttribute(chimera.Molecule, "numHbonds")

	def addVolumeColumn(self, columnName, *args):
		from Rotamers import processVolume
		format = processVolume(self.rotamers, columnName, *args)
		self.rotTable.addColumn(columnName,
			"lambda r: r.volumeScores[%s]" % repr(columnName),
			format=format, display=True)
		registerAttribute(chimera.Molecule, "volumeScores")

	def Apply(self):
		from Rotamers import useRotamer
		useRotamer(self.residue, self.rotamerSel, log=True)

	def destroy(self):
		chimera.triggers.deleteHandler('Residue', self.resHandlerID)
		chimera.triggers.deleteHandler(SAVE_SESSION, self._sesHandlerID)
		chimera.openModels.close(self.rotamers)
		for label, ddn in self.dependentDialogInfo:
			dd = getattr(self, ddn + 'Dialog', None)
			if dd:
				dd.destroy()
		ModelessDialog.destroy(self)

	def selectRotamers(self, rotamers):
		from chimera import selectionOperation
		from chimera.selection import ItemizedSelection
		rotSel = ItemizedSelection()
		rotSel.add(rotamers)
		selectionOperation(rotSel)

	def _resChangeCB(self, trigName, myData, trigData):
		if self.residue in trigData.deleted:
			self.destroy()

	def _selAllCB(self):
		self.selectRotamers(self.rotamers)

	def _selCurCB(self):
		self.selectRotamers([r for r in self.rotamers if r.display])

	def _selRotamerCB(self, tableSel):
		tableSet = set(tableSel)
		if tableSet == set([r for r in self.rotamers if r.display]):
			return
		self.rotamerSel = tableSel
		for rot in self.rotamers:
			rot.display = rot in tableSet
		if len(tableSel) > 0:
			state = 'normal'
		else:
			state = 'disabled'
		self.buttonWidgets['OK'].config(state=state)
		self.buttonWidgets['Apply'].config(state=state)

	def _sessionCB(self, trigName, myData, sesFile):
		from SimpleSession import sessionID
		data = (1, sessionID(self.residue), self.resType,
			[sessionID(rot) for rot in self.rotamers], self.bbdep,
			self.lib.displayName, self.rotTable.getRestoreInfo())
		print>>sesFile, """
try:
	from Rotamers.gui import sessionRestore
	sessionRestore(%s)
except:
	reportRestoreError('Error restoring Rotamers')
""" % repr(data)

	def _showDialog(self, dialogName):
		d = getattr(self, dialogName, None)
		if d:
			d.enter()
		else:
			importName = dialogName[0].upper() + dialogName[1:]
			exec("from %s import %s" % (importName, importName))
			exec("self.%s = %s(self)" % (dialogName, importName))

def sessionRestore(sessionData):
	from SimpleSession import idLookup
	version, resID, resType, rotIDs, bbdep, libName, tableInfo = sessionData
	from Rotamers import libraries
	for lib in libraries:
		if lib.displayName == libName:
			break
	else:
		raise ValueError("Cannot find library")
	sesData = (bbdep, [idLookup(rot) for rot in rotIDs], tableInfo)
	RotamerDialog(idLookup(resID), resType, lib, sessionData=sesData)

_PRD = None
def _prd():
	global _PRD
	if not _PRD:
		_PRD = PrepRotamersDialog()
	_PRD.enter()

amino20 = ["ALA", "ARG", "ASN", "ASP", "CYS", "GLN", "GLU", "GLY", "HIS", "ILE",
	"LEU", "LYS", "MET", "PHE", "PRO", "SER", "THR", "TRP", "TYR", "VAL"]
class PrepRotamersDialog(ModelessDialog):
	title = "Choose Rotamer Parameters"
	oneshot = True
	help = "ContributedSoftware/rotamers/framerot.html"

	def fillInUI(self, parent):
		from chimera.tkoptions import EnumOption
		import Tkinter, Pmw
		row = 0
		Tkinter.Label(parent, text=
			"Show rotamers for selected residues..."
			).grid(row=row, column=0, columnspan=2)
		row += 1

		resTypes = set()
		for sr in chimera.selection.currentResidues():
			resTypes.add(sr.type)
		if len(resTypes) == 1:
			defaultType = resTypes.pop()
			if defaultType not in amino20:
				defaultType = amino20[0]
		else:
			defaultType = amino20[0]
		class ResTypeOption(EnumOption):
			values = amino20
		self.resType = ResTypeOption(parent, row, "Rotamer type",
			defaultType, None)
		row += 1

		self.rotLib = RotLibOption(parent, row, "Rotamer library",
			defaultLib(), self._libChangeCB)
		row += 1

		self.libDescription = Tkinter.Label(parent)
		self.libDescription.grid(row=row, column=0, columnspan=2)
		row += 1

		self.citationRow = row
		self.citationWidgets = {}
		self._libChangeCB(self.rotLib)

	def destroy(self):
		global _PRD
		_PRD = None
		ModelessDialog.destroy(self)

	def Apply(self):
		selectedResidues = chimera.selection.currentResidues()
		if not selectedResidues:
			self.enter()
			raise UserError("No residues selected")
		if len(selectedResidues) > 10:
			from chimera.baseDialog import AskYesNoDialog
			numSel = len(selectedResidues)
			if AskYesNoDialog("You have %d residues selected which"
					" could bring up %d rotamer dialogs.\n"
					"Continue?" % (numSel, numSel)).run(
					chimera.tkgui.app) == "no":
				self.enter()
				return
		resType = self.resType.get()
		lib = self.rotLib.get()
		from Rotamers import NoResidueRotamersError
		try:
			for sr in selectedResidues:
				RotamerDialog(sr, resType, lib)
		except NoResidueRotamersError:
			from SwapRes import swap
			for sr in selectedResidues:
				replyobj.info("Swapping %s to %s\n"
							% (sr, resType))
				swap(sr, resType, bfactor=None)
			replyobj.status("Swapped %d residue(s)\n"
						% len(selectedResidues))
	def _libChangeCB(self, opt):
		lib = opt.get()
		if 'showing' in self.citationWidgets:
			self.citationWidgets['showing'].grid_forget()
			del self.citationWidgets['showing']
		if lib not in self.citationWidgets:
			if lib.citation:
				from CGLtk.Citation import Citation
				citationWidget = Citation(self.uiMaster(),
					lib.citation, prefix="Publications"
					" using %s rotamers should cite:"
					% lib.citeName)
			else:
				citationWidget = None
			self.citationWidgets[lib] = citationWidget
		else:
			citationWidget = self.citationWidgets[lib]
		if citationWidget:
			citationWidget.grid(row=self.citationRow, column=0,
							columnspan=2)
			self.citationWidgets['showing'] = citationWidget
		if lib.description:
			ld = lib.description
		else:
			ld = ""
		self.libDescription.configure(text=ld)

def defaultLib():
	libraries = RotLibOption.values
	default = libraries[0]
	for lib in libraries:
		if lib.importName == prefs[LIBRARY]:
			default = lib
			break
	return default

from Rotamers import libraries
libraries.sort(lambda a, b: cmp(a.displayName, b.displayName))
from chimera.tkoptions import SymbolicEnumOption
class RotLibOption(SymbolicEnumOption):
	labels = [lib.displayName for lib in libraries]
	values = libraries
del libraries, SymbolicEnumOption
