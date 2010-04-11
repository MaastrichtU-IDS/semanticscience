# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import Tkinter
import Pmw
import Tix
from sets import Set

import chimera
import SimpleSession
from chimera import tkgui, selection, replyobj, triggerSet
from chimera.baseDialog import ModelessDialog, ModalDialog
import Compound

RestoreCode = """
import SimpleSession
try:
	import ViewDock
except ImportError:
	# No ViewDock module, don't bother restoring
	pass
else:
	SimpleSession.registerAfterModelsCB(lambda cb=ViewDock.restoreSession,
						k=ViewDock.%s, d=%s: cb(k, d))
"""

def restoreSession(klass, data):
	try:
		m = __import__(data.ResultsModule)
		for name in data.ResultsModule.split('.')[1:]:
			m = getattr(m, name)
		Results = getattr(m, data.ResultsClass)
		klass(data.file, data.type, Results=Results,
				sessionData=data.resultsData,
				uiData=data.uiData,
				*data.args, **data.kw)
	except:
		print "Restoring ViewDock extension failed"
		import traceback, sys
		traceback.print_exc(file=sys.stdout)

class ViewDock(ModelessDialog):

	help = "ContributedSoftware/viewdock/framevd.html"
	buttons = ( "Hide", "Quit" )

	Ignore = -1
	Identify = 0
	Prune = 1

	SELECTION_CHANGED = "ViewDockSelectionChanged"
	COMPOUND_STATE_CHANGED = "ViewDockCompoundStateChanged"
	COLUMN_ADDED = "ViewDockColumnAdded"
	COLUMN_DELETED = "ViewDockColumnDeleted"
	COLUMN_UPDATED = "ViewDockColumnUpdated"
	EXIT = "ViewDockExited"

	def __init__(self, file, type, Results=Compound.Results,
			sessionData=None, uiData=None, *args, **kw):
		#
		# GUI-independent initialization
		#
		self.filetype = type
		self.moleculeTrigger = None
		self.sessionHandler = None
		self.closeHandler = None
		self._uiData = uiData
		self.results = Results(file, type, self._showCompounds,
						self._setChanged, sessionData)
		if len(self.results.compoundList) == 0:
			raise IOError, 'no compounds found in %s' % file
		self.filterSet = None
		self.diagramDialog = None
		self.changed = False

		#
		# Create trigger set for others to register handler
		#
		self.triggers = triggerSet.TriggerSet()
		self.triggers.addTrigger(self.SELECTION_CHANGED)
		self.triggers.addTrigger(self.COMPOUND_STATE_CHANGED)
		self.triggers.addTrigger(self.COLUMN_ADDED)
		self.triggers.addTrigger(self.COLUMN_DELETED)
		self.triggers.addTrigger(self.COLUMN_UPDATED)
		self.triggers.addTrigger(self.EXIT)

		#
		# Create framework
		#
		self.title = 'ViewDock - %s' % file
		ModelessDialog.__init__(self, *args, **kw)
		chimera.extension.manager.registerInstance(self)

		#
		# Monitor molecule and exit when closed
		#
		self.moleculeTrigger = chimera.openModels.addRemoveHandler(
					self._molChange, None)

		#
		# Exit when session is closed
		#
		self.closeHandler = chimera.triggers.addHandler(
						chimera.CLOSE_SESSION,
						self.closeSession, None)

		#
		# Get ready to save data in session
		#
		self._sessionData = (file, type, args, kw)
		self.sessionHandler = chimera.triggers.addHandler(
						SimpleSession.SAVE_SESSION,
						self.saveSession, None)

	def fillInUI(self, root):
		self.app = root
		self.moviePanel = None
		self.filterPanel = None
		self.handler = None
		self.hbondHandler = None
		self.movieAfterId = None
		self.interval = 1000

		#
		# Create Tk variables
		#
		if self._uiData is not None:
			(initListViable, initListDeleted, initListPurged,
				initPickMode) = self._uiData
		else:
			initListViable = 1
			initListDeleted = 0
			initListPurged = 0
			initPickMode = ViewDock.Ignore
		self.listViable = Tkinter.IntVar(root)
		self.listViable.set(initListViable)
		self.listDeleted = Tkinter.IntVar(root)
		self.listDeleted.set(initListDeleted)
		self.listPurged = Tkinter.IntVar(root)
		self.listPurged.set(initListPurged)
		self.pickMode = Tkinter.IntVar(root)
		self.pickMode.set(initPickMode)
		self.compoundState = Tkinter.StringVar(root)
		self.compoundState.set(Compound.Compound.Undefined)

		#
		# Create menu bar
		#
		menubar = Pmw.MainMenuBar(root, hull_bd=2,
					hull_relief=Tkinter.RAISED)
		root.winfo_toplevel().config(menu=menubar)
		self.menubar = menubar
		menubar.addmenu('File', 'Save data')
		menubar.addmenuitem('File', 'command', label='Save',
					command=self.save)
		menubar.addmenuitem('File', 'command', label='Save As ...',
					command=self.saveAs)
		menubar.addmenuitem('File', 'command', label='Rewrite ...',
					command=self.rewrite)
		menubar.addmenuitem('File', 'command', label='Close',
					command=self.exit)
		menubar.addmenu('Compounds',
					'Choose compounds to show')
		menubar.addmenuitem('Compounds', 'checkbutton',
					label='List Viable',
					onvalue=1,
					offvalue=0,
					variable=self.listViable,
					command=self._reloadCompounds)
		menubar.addmenuitem('Compounds', 'checkbutton',
					label='List Deleted',
					onvalue=1,
					offvalue=0,
					variable=self.listDeleted,
					command=self._reloadCompounds)
		menubar.addmenuitem('Compounds', 'checkbutton',
					label='List Purged',
					onvalue=1,
					offvalue=0,
					variable=self.listPurged,
					command=self._reloadCompounds)
		menubar.addmenuitem('Compounds', 'command',
					label='List Chosen Only',
					command=self.hideCB)
		menubar.addmenuitem('Compounds', 'command',
					label='List All',
					command=self.unhideCB)
		menubar.addmenuitem('Compounds', 'command',
					label='Invert Choices',
					command=self.invertCB)
		menubar.addmenuitem('Compounds', 'command',
					label='Choose by Value...',
					command=self.filterCB)
		menubar.addmenu('Column', 'Display data column')
		self.remakeColumnMenus(firstTime=True)
		menubar.addmenu('Selection', 'Choose action on selection')
		menubar.addmenuitem('Selection', 'radiobutton',
					label='Ignore',
					value=ViewDock.Ignore,
					variable=self.pickMode,
					command=self.setPickMode)
		menubar.addmenuitem('Selection', 'radiobutton',
					label='Identify',
					value=ViewDock.Identify,
					variable=self.pickMode,
					command=self.setPickMode)
		menubar.addmenuitem('Selection', 'radiobutton',
					label='Prune',
					value=ViewDock.Prune,
					variable=self.pickMode,
					command=self.setPickMode)
		menubar.addmenu('Chimera', 'Display or hide compounds')
		menubar.addmenuitem('Chimera', 'command',
					label='Hide All',
					command=self.results.hideAll)
		menubar.addmenuitem('Chimera', 'command',
					label='Hide All Viable',
					command=self.results.hideViable)
		menubar.addmenuitem('Chimera', 'command',
					label='Hide All Deleted',
					command=self.results.hideDeleted)
		menubar.addmenuitem('Chimera', 'command',
					label='Hide All Purged',
					command=self.results.hidePurged)
		menubar.addmenuitem('Chimera', 'command',
					label='Show All',
					command=self.results.displayAll)
		menubar.addmenuitem('Chimera', 'command',
					label='Show All Viable',
					command=self.results.displayViable)
		menubar.addmenuitem('Chimera', 'command',
					label='Show All Deleted',
					command=self.results.displayDeleted)
		menubar.addmenuitem('Chimera', 'command',
					label='Show All Purged',
					command=self.results.displayPurged)
		menubar.addmenu('HBonds', 'Manage compounds by hydrogen-bond count')
		menubar.addmenuitem('HBonds', 'command',
					label='Add Count to Entire Receptor',
					command=self.hbondToReceptor)
		menubar.addmenuitem('HBonds', 'command',
					label='Add Count to Selected Atoms',
					command=self.hbondToSelectedAtoms)
		menubar.addmenuitem('HBonds', 'command',
					label='Change Compound State...',
					command=self.hbondCB)
		self.hbondColName = None
		self.hbondSelectedAtoms = None
		self.hbondPBGCount = -1
		menubar.addmenu('Movie', 'Display compounds sequentially')
		menubar.addmenuitem('Movie', 'command',
					label='Play',
					command=self.moviePlay)
		menubar.addmenuitem('Movie', 'command',
					label='Stop',
					state=Tkinter.DISABLED,
					command=self.movieStop)
		menubar.addmenuitem('Movie', 'command',
					label='Options ...',
					command=self.movieOptions)
		if self.filetype == "Mordor":
			menubar.addmenu('Mordor', 'Mordor format commands')
			self.results.mordorSetMenubar(menubar)
			self.results.mordorRemakeMenu()

		from chimera.tkgui import aquaMenuBar
		aquaMenuBar(menubar.component('hull'), root, pack = True)

		#
		# Create PanedWidget for rest of interface
		#
		pw = Pmw.PanedWidget(root, hull_width=600, hull_height=400)
		pw.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)
		topPane = pw.add('top', size=0.5, min=0.2)
		bottomPane = pw.add('bottom', size=0.5, min=0.2)

		#
		# Create button box
		#
		fontfamily = root.tk.call('tix', 'option', 'get', 'textfamily')
		fontsize = root.tk.call('tix', 'option', 'get', 'fontsize')
		fontsize = int(1.1 * int(fontsize))
		label_font = (fontfamily, fontsize, 'bold')
		radio = Pmw.RadioSelect(bottomPane, buttontype='radiobutton',
					command=self._setCompoundState,
					labelpos=Tkinter.N,
					label_anchor=Tkinter.W,
					label_font=label_font,
					label_text='Change Compound State',
					selectmode='single')
		radio.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
		radio.add('Viable', variable=self.compoundState,
					value=Compound.Compound.Viable)
		radio.add('Deleted', variable=self.compoundState,
					value=Compound.Compound.Deleted)
		radio.add('Purged', variable=self.compoundState,
					value=Compound.Compound.Purged)
		radio.configure(Purged_state=Tkinter.DISABLED,
				Deleted_state=Tkinter.DISABLED,
				Viable_state=Tkinter.DISABLED)
		self.stateRadio = radio

		#
		# Create info text box and label
		#
		fixed_font = root.tk.call('tix', 'option', 'get', 'fixed_font')
		self.textBox = Pmw.ScrolledText(bottomPane, labelpos=Tkinter.N,
					text_font=fixed_font,
					label_anchor=Tkinter.W,
					label_font=label_font,
					text_width=65,
					text_height=8)
		self.textBox.pack(side=Tkinter.BOTTOM, fill=Tkinter.BOTH,
					expand=Tkinter.TRUE)
		self.textLabel = self.textBox.component('label')
		self.textLabel.config(text='No compound chosen')

		#
		# Create listbox
		#
		self.results.setCompoundsFrame(topPane)
		self._reloadCompounds()

	def remakeColumnMenus(self, firstTime=False):
		if not firstTime:
			self.menubar.deletemenu('Show')
			self.menubar.deletemenu('Hide')
			end = self.menubar.component("Column").index("end")
			self.menubar.deletemenuitems('Column', 0, end)
		self.menubar.addcascademenu('Column', 'Show')
		self.menubar.addcascademenu('Column', 'Hide')
		self.menubar.addmenuitem('Column', 'command', label='Read...',
						command=self.readColumnOrder)
		self.menubar.addmenuitem('Column', 'command', label='Diagram...',
						command=self.updateDiagram)
		fnum = 0
		for f in self.results.fields:
			def showCB(name=f):
				self.addColumn(name)
			def hideCB(name=f):
				self.deleteColumn(name)
			if fnum % 15 == 0:
				cbreak = 1
			else:
				cbreak = 0
			self.menubar.addmenuitem('Show', 'command', label=f,
							columnbreak=cbreak,
							command=showCB)
			self.menubar.addmenuitem('Hide', 'command', label=f,
							columnbreak=cbreak,
							command=hideCB)
			fnum = fnum + 1

	def save(self):
		self.results.save()

	def saveAs(self):
		if hasattr(self, '_saveAsDialog'):
			self._saveAsDialog.enter()
			return
		from OpenSave import SaveModeless
		self._saveAsDialog = SaveModeless(command=self._saCB,
			title='Save ViewDock File', historyID='ViewDock',
			filters=[("DOCK", ["*" + self.results.format],
			self.results.format)])

	def _saCB(self, okayed, dialog):
		if not okayed:
			return
		for path in dialog.getPaths():
			self.results.save(path)

	def rewrite(self):
		if hasattr(self, '_rewriteDialog'):
			self._rewriteDialog.enter()
			return
		from OpenSave import SaveModeless
		self._rewriteDialog = SaveModeless(command=self._rwCB,
			title='Rewrite ViewDock File (remove purged)',
			filters=[("DOCK", ["*" + self.results.format],
			self.results.format)], historyID='ViewDock')

	def _rwCB(self, okayed, dialog):
		if not okayed:
			return
		for path in dialog.getPaths():
			self.results.save(path, skipPurged=1)

	def exit(self, forceExit=False):
		shouldExit = True
		if self.changed:
			self.enter()
			d = YesNoCancel(title="Close ViewDock",
				text="Do you wish to save your changes?",
				master=self.app)
			status = d.run(self.app)
			if status == 'yes':
				self.saveAs()
			elif status == 'cancel':
				shouldExit = False
		if shouldExit or forceExit:
			molList = [ c.chimeraModel
					for c in self.results.compoundList
					if c.chimeraModel is not None ]
			chimera.openModels.close(molList)
			if self.moviePanel:
				self.moviePanel.destroy()
			if self.filterPanel:
				self.filterPanel.destroy()
			if self.diagramDialog:
				self.diagramDialog.destroy()
			if self.hbondHandler:
				chimera.triggers.deleteHandler("PseudoBond",
							self.hbondHandler)
				self.hbondHandler = None
			if self.handler:
				chimera.triggers.deleteHandler(
							'selection changed',
							self.handler)
				self.handler = None
			if self.sessionHandler:
				chimera.triggers.deleteHandler(
							SimpleSession.SAVE_SESSION,
							self.sessionHandler)
			self.destroy()
			chimera.extension.manager.deregisterInstance(self)
			if self.moleculeTrigger:
				chimera.openModels.deleteRemoveHandler(
							self.moleculeTrigger)
			if self.closeHandler:
				chimera.triggers.deleteHandler(
							chimera.CLOSE_SESSION,
							self.closeHandler)

	def setPickMode(self):
		if self.pickMode.get() == ViewDock.Ignore:
			if self.handler is not None:
				chimera.triggers.deleteHandler(
					'selection changed', self.handler)
				self.handler = None
		else:
			if self.handler is None:
				self.handler = chimera.triggers.addHandler(
						'selection changed',
						self._selectionChanged, None)

	def addColumn(self, col):
		if self.results.addColumn(col):
			self._reloadCompounds()
		self.triggers.activateTrigger(self.COLUMN_ADDED, col)

	def deleteColumn(self, col):
		if self.results.deleteColumn(col):
			self._reloadCompounds()
		self.triggers.activateTrigger(self.COLUMN_DELETED, col)

	def readColumnOrder(self):
		from OpenSave import OpenModal
		d = OpenModal(title="Read Column Order", multiple=False)
		pathsAndTypes = d.run(self.app)
		if not pathsAndTypes:
			return
		filename = pathsAndTypes[0][0]
		try:
			f = open(filename)
		except IOError, msg:
			from chimera import UserError
			raise UserError("%s: %s" % (filename, msg))
		try:
			order = [ s.strip() for s in f.readlines() ]
		finally:
			f.close()
		for col in order:
			if col not in self.results.fields:
				from chimera import UserError
				raise UserError("%s is not valid column name"
						% col)
		oldOrder = set(self.results.columnKeys)
		self.results.setCompoundsKeys(order)
		self._reloadCompounds()
		newOrder = set(self.results.columnKeys)
		for col in (oldOrder - newOrder):
			self.triggers.activateTrigger(self.COLUMN_DELETED, col)
		for col in (newOrder - oldOrder):
			self.triggers.activateTrigger(self.COLUMN_ADDED, col)

	def updateDiagram(self):
		if self.diagramDialog is None:
			self.diagramDialog = DiagramDialog(self)
		else:
			self.diagramDialog.enter()

	def showDiagram(self, display, width, height):
		self.results.showDiagram(display, width, height)

	def hideCB(self):
		self.filterSet = Set(self.results.selected)
		self._reloadCompounds()

	def unhideCB(self):
		self.filterSet = None
		self._reloadCompounds()

	def invertCB(self):
		self.results.invertSelected()

	def filterCB(self):
		if self.filterPanel is None:
			from FilterDialog import FilterDialog
			self.filterPanel = FilterDialog(self)
		self.filterPanel.enter()

	def hbondCB(self):
		from HBondDialog import HBondDialog
		HBondDialog(self.startHBondFilter, oneshot=1)

	def startHBondFilter(self, *args):
		mgr = chimera.PseudoBondMgr.mgr()
		pbg = mgr.findPseudoBondGroup("hydrogen bonds")
		from FindHBond import gui as findHBondGui
		findHBondGui.showUI(lambda hbf=self.hbondFilter,
						args=args: hbf(*args))

	def hbondFilter(self, filterType, action, arg):
		filterable = []
		molDict = {}
		hbondCount = {}
		for compound in self.results.compoundList:
			molDict[compound.chimeraModel] = compound
			hbondCount[compound.chimeraModel] = 0

		if filterType == "quality":
			criteria = arg

			numSelAtoms = 0
			for atom in selection.currentAtoms():
				mol = atom.molecule
				if molDict.has_key(mol):
					continue
				if len(atom.residue.atoms) == mol.rootForAtom(
							atom, 1).size.numAtoms:
					# isolated residue (water?)
					continue
				if atom.element.number in [0, 1, 6]:
					# exclude carbon, hydrogen and funky
					continue
				numSelAtoms += 1
				seen = []
				for hbond in atom.associations(
							"hydrogen bonds", None):
					otherMol = hbond.otherAtom(
								atom).molecule
					if not molDict.has_key(otherMol):
						continue
					if otherMol in seen:
						continue
					seen.append(otherMol)
					hbondCount[otherMol] += 1

			if numSelAtoms == 0:
				replyobj.error(
					"No heteroatoms selected in receptor\n")
				return 

			for mol, count in hbondCount.items():
				if criteria == "all" and count < numSelAtoms:
					filterable.append(mol)
				elif criteria == "any" and count == 0:
					filterable.append(mol)
		else:
			numNeeded = arg

			from chimera.misc import getPseudoBondGroup
			hbgrp = getPseudoBondGroup("hydrogen bonds")
			for hb in hbgrp.pseudoBonds:
				a1, a2 = hb.atoms
				mol1 = a1.molecule
				mol2 = a2.molecule
				islig1 = molDict.has_key(mol1)
				islig2 = molDict.has_key(mol2)
				if islig1 + islig2 != 1:
					# need one end on ligand and one on
					# receptor
					continue
				if islig1:
					receptAtom = a2
					receptMol = mol2
					ligMol = mol1
				else:
					receptAtom = a1
					receptMol = mol1
					ligMol = mol2
				if len(receptAtom.residue.atoms) == \
						receptMol.rootForAtom(
						receptAtom, 1).size.numAtoms:
					# isolated residue (water?)
					continue
				hbondCount[ligMol] += 1
			for mol, count in hbondCount.items():
				if count < numNeeded:
					filterable.append(mol)

		for mol in filterable:
			molDict[mol].state = action
		self._reloadCompounds()

	def hbondToSelectedAtoms(self):
		selected = selection.currentAtoms()
		if not selected:
			replyobj.error("No atoms selected")
		else:
			sd = {}
			for a in selected:
				sd[a] = 1
			self._addHbondColumn(sd)

	def hbondToReceptor(self):
		self._addHbondColumn(None)

	def _addHbondColumn(self, selectedAtoms):
		# Create pseudobond monitor
		if not self.hbondHandler:
			self.hbondHandler = chimera.triggers.addHandler(
						"PseudoBond",
						self._addHbondColumnCB, None)
		self.hbondSelectedAtoms = selectedAtoms
		mgr = chimera.PseudoBondMgr.mgr()
		pbg = mgr.findPseudoBondGroup("hydrogen bonds")
		from FindHBond import gui as findHBondGui
		findHBondGui.showUI()

	def _addHbondColumnCB(self, trigger, ignore, atoms):
		if trigger != None:
			mgr = chimera.PseudoBondMgr.mgr()
			pbg = mgr.findPseudoBondGroup("hydrogen bonds")
			if pbg is None:
				return
			if len(pbg.pseudoBonds) != self.hbondPBGCount:
				needUpdate = True
			else:
				for b in atoms.created:
					if b.category == "hydrogen bonds":
						needUpdate = True
						break
				else:
					needUpdate = False
			if not needUpdate:
				return
		selectedAtoms = self.hbondSelectedAtoms
		molDict = {}
		hbondCount = {}
		ligandAtoms = {}
		receptorAtoms = {}
		for compound in self.results.compoundList:
			molDict[compound.chimeraModel] = compound
			hbondCount[compound.chimeraModel] = 0
			ligandAtoms[compound.chimeraModel] = {}
			receptorAtoms[compound.chimeraModel] = {}
		from chimera.misc import getPseudoBondGroup
		hbgrp = getPseudoBondGroup("hydrogen bonds")
		for hb in hbgrp.pseudoBonds:
			a1, a2 = hb.atoms
			if (selectedAtoms
			and a1 not in selectedAtoms
			and a2 not in selectedAtoms):
				continue
			mol1 = a1.molecule
			mol2 = a2.molecule
			islig1 = molDict.has_key(mol1)
			islig2 = molDict.has_key(mol2)
			if islig1 + islig2 != 1:
				# need one end on ligand and one on
				# receptor
				continue
			if islig1:
				receptAtom = a2
				receptMol = mol2
				ligAtom = a1
				ligMol = mol1
			else:
				receptAtom = a1
				receptMol = mol1
				ligAtom = a2
				ligMol = mol2
			if len(receptAtom.residue.atoms) == \
					receptMol.rootForAtom(
					receptAtom, 1).size.numAtoms:
				# isolated residue (water?)
				continue
			hbondCount[ligMol] += 1
			ligandAtoms[ligMol][ligAtom] = 1
			receptorAtoms[ligMol][receptAtom] = 1
		if selectedAtoms:
			labelHB = "HBonds (sel)"
		else:
			labelHB = "HBonds (all)"
		labelLA = "HBond Ligand Atoms"
		labelRA = "HBond Receptor Atoms"
		for compound in self.results.compoundList:
			cm = compound.chimeraModel
			compound.fields[labelHB] = hbondCount[cm]
			compound.fields[labelLA] = len(ligandAtoms[cm])
			compound.fields[labelRA] = len(receptorAtoms[cm])
		shownColumns = self.results.getColumns()
		self._hbondShowColumn(labelHB, shownColumns, self.hbondColName)
		self.hbondColName = labelHB
		self._hbondShowColumn(labelLA, shownColumns)
		self._hbondShowColumn(labelRA, shownColumns)
		self.remakeColumnMenus()

	def _hbondShowColumn(self, colName, shownColumns, replacing=None):
		state = self.results.createColumn(colName, "number", replacing)
		if state == "created":
			self.addColumn(colName)
		elif state == "renamed":
			self._reloadCompounds()
			self.triggers.activateTrigger(self.COLUMN_DELETED,
							replacing)
			self.triggers.activateTrigger(self.COLUMN_ADDED,
							colName)
		if colName in shownColumns:
			self._reloadCompounds()
			self.triggers.activateTrigger(self.COLUMN_UPDATED,
							colName)

	def _setCompoundState(self, buttonName):
		self.results.setSelectedState(self.compoundState.get())
		self._reloadCompounds()

	def _reloadCompounds(self):
		show = {
			Compound.Compound.Viable: self.listViable.get(),
			Compound.Compound.Deleted: self.listDeleted.get(),
			Compound.Compound.Purged: self.listPurged.get(),
		}
		self.results.updateCompounds(show, self.filterSet)
		if self.movieAfterId is not None:
			if not self.results.movieSetup():
				self.app.after_cancel(self.movieAfterId)
				self.movieAfterId = None

	def filter(self, filterSet):
		if filterSet is not None:
			filterSet = list(filterSet)
		self.results.setSelected(filterSet)

	def _showCompounds(self, compounds):
		if len(compounds) == 1:
			c = compounds[0]
			self.textLabel.config(text=c.label)
			self.textBox.settext(c.text)
			self.stateRadio.configure(Purged_state=Tkinter.NORMAL,
						Deleted_state=Tkinter.NORMAL,
						Viable_state=Tkinter.NORMAL)
			self.compoundState.set(c.state)
		elif len(compounds) == 0:
			self.textLabel.config(text='No compound chosen')
			self.textBox.settext('')
			self.compoundState.set(Compound.Compound.Undefined)
			self.stateRadio.configure(Purged_state=Tkinter.DISABLED,
						Deleted_state=Tkinter.DISABLED,
						Viable_state=Tkinter.DISABLED)
		else:
			self.textLabel.config(
				text='Multiple compounds chosen')
			self.textBox.settext('')
			self.stateRadio.configure(Purged_state=Tkinter.NORMAL,
						Deleted_state=Tkinter.NORMAL,
						Viable_state=Tkinter.NORMAL)
			state = compounds[0].state
			for c in compounds[1:]:
				if c.state != state:
					state = Compound.Compound.Undefined
					break
			self.compoundState.set(state)
		self.triggers.activateTrigger(self.SELECTION_CHANGED, compounds)

	def _setChanged(self, compounds):
		self.changed = True
		self.triggers.activateTrigger(self.COMPOUND_STATE_CHANGED,
						compounds)

	def _selectionChanged(self, name, closure, select):
		molList = select.graphs()
		if self.pickMode.get() == ViewDock.Prune:
			self.results.pruneModels(molList)
			self._reloadCompounds()
		else:
			self.results.selectModels(molList, update=False)
			self._reloadCompounds()
			self._showCompounds(self.results.selected)

	def moviePlay(self):
		if self.moviePanel:
			self.moviePanel.configure(
				buttonbox_Play_state=Tkinter.DISABLED,
				buttonbox_Stop_state=Tkinter.NORMAL)
		menu = self.menubar.component('Movie')
		menu.entryconfigure('Play', state=Tkinter.DISABLED)
		menu.entryconfigure('Stop', state=Tkinter.NORMAL)
		if not self.results.movieSetup():
			return
		if self.movieAfterId is None:
			self.movieAfterId = self.app.after(self.interval,
								self._movieStep)

	def movieStop(self):
		self.results.movieStop()
		if self.moviePanel:
			self.moviePanel.configure(
				buttonbox_Stop_state=Tkinter.DISABLED,
				buttonbox_Play_state=Tkinter.NORMAL)
		menu = self.menubar.component('Movie')
		menu.entryconfigure('Stop', state=Tkinter.DISABLED)
		menu.entryconfigure('Play', state=Tkinter.NORMAL)
		if self.movieAfterId is not None:
			self.app.after_cancel(self.movieAfterId)
			self.movieAfterId = None

	def movieOptions(self):
		if self.moviePanel is None:
			self._makeMoviePanel()
		self.moviePanel.show()

	def _makeMoviePanel(self):
		self.moviePanel = Pmw.CounterDialog(title='Movie Options',
					counter_datatype='real',
					counter_increment=0.1,
					counter_labelpos=Tkinter.N,
					label_text='Step Interval (sec)',
					entryfield_validate={
						'validator':'real',
						'min':0.1,
						'minstrict':0,
						'max':60.0
					},
					entryfield_value=self.interval/1000.0,
					entryfield_modifiedcommand=
						self._movieIntervalChanged,
					buttons = ('Play', 'Stop'),
					command=self._movieButtonClicked)
		if self.movieAfterId is not None:
			self.moviePanel.configure(
				buttonbox_Play_state=Tkinter.DISABLED,
				buttonbox_Stop_state=Tkinter.NORMAL)
		else:
			self.moviePanel.configure(
				buttonbox_Stop_state=Tkinter.DISABLED,
				buttonbox_Play_state=Tkinter.NORMAL)
		self.movieEntry = self.moviePanel.component('entry')

	def _movieButtonClicked(self, buttonName):
		if buttonName is None:
			self.moviePanel.withdraw()
		elif buttonName == 'Play':
			self.moviePlay()
		else:
			self.movieStop()

	def _movieIntervalChanged(self):
		try:
			interval = int(float(self.movieEntry.get()) * 1000)
		except ValueError:
			return
		if interval > 0:
			self.interval = interval

	def _movieStep(self):
		if not self.results.movieStep():
			self.movieAfterId = None
			return
		self.movieAfterId = self.app.after(self.interval,
							self._movieStep)

	def _molChange(self, trigger, myData, closed):
		for c in self.results.compoundList:
			if c.chimeraModel in closed:
				c.closeChimeraModel()

	def emRaise(self):
		self.enter()

	def emHide(self):
		self.Close()

	def emQuit(self):
		self.exit()

	def Hide(self):
		self.emHide()

	def Quit(self):
		self.emQuit()

	def closeSession(self, trigger, data, ignore):
		self.exit(forceExit=True)

	def saveSession(self, trigger, data, f):
		dataVar = "viewDockData"
		className = self.__class__.__name__
		print >> f, "# restore %s extension" % className
		print >> f, "class ViewDockData: pass"
		print >> f, "%s = ViewDockData()" % dataVar
		file, type, args, kw = self._sessionData
		print >> f, "%s.file = %s" % (dataVar, repr(file))
		print >> f, "%s.type = %s" % (dataVar, repr(type))
		print >> f, "%s.args = %s" % (dataVar, repr(args))
		print >> f, "%s.kw = %s" % (dataVar, repr(kw))
		rc = self.results.__class__
		print >> f, "%s.ResultsClass = %s" % (dataVar,
							repr(rc.__name__))
		print >> f, "%s.ResultsModule = %s" % (dataVar,
							repr(rc.__module__))
		print >> f, "%s.resultsData = %s" % (dataVar,
					repr(self.results.saveSession()))
		if self.app:
			uiData = (self.listViable.get(),
					self.listDeleted.get(),
					self.listPurged.get(),
					self.pickMode.get())
		else:
			uiData = None
		print >> f, "%s.uiData = %s" % (dataVar, repr(uiData))
		f.write(RestoreCode % (className, dataVar))

class YesNoCancel(ModalDialog):

	buttons = ( "Yes", "No", "Cancel" )

	def __init__(self, title, text, *args, **kw):
		self.text = text
		self.title = title
		ModalDialog.__init__(self, oneshot=1, *args, **kw)

	def fillInUI(self, parent):
		l = Tkinter.Label(parent, text=self.text)
		l.pack()

	def Yes(self):
		ModalDialog.Cancel(self, value="yes")

	def No(self):
		ModalDialog.Cancel(self, value="no")

	def Cancel(self):
		ModalDialog.Cancel(self, value="cancel")

class DiagramDialog(ModelessDialog):

	help = "ContributedSoftware/viewdock/viewdock.html#diagram"
	title = "Display 2D Diagrams"
	buttons = ("Show", "Hide", "Cancel")

	def __init__(self, viewdock, *args, **kw):
		self.viewdock = viewdock
		self.width = 96
		self.height = 96
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		import Tkinter
		from chimera.tkoptions import BooleanOption, IntOption
		l = Tkinter.Label(parent, text="Conversion from structure to "
						"diagram\n"
						"is provided using the\n"
						"GIF Creator for "
						"Chemical Structures\n"
						"(courtesy of "
						"Dr. W.D. Ihlenfeldt)")
		l.grid(row=0, column=0, columnspan=2, ipady=3)
		self.diagramWidth = IntOption(parent, 1,
					"Diagram width", self.width, None)
		self.diagramHeight = IntOption(parent, 2,
					"Diagram height", self.height, None)

	def Show(self):
		self.Apply(True)
	def Hide(self):
		self.Apply(False)
	def Apply(self, display):
		w = self.diagramWidth.get()
		h = self.diagramHeight.get()
		from chimera import UserError
		if w < 32 or h < 32:
			raise UserError("Width and height must be 32 or greater")
		if w > 1024 or h > 1024:
			raise UserError("Width and height must be 1024 or less")
		self.viewdock.showDiagram(display, w, h)
		self.width = w
		self.height = h

class HearDock(ViewDock):

	def __init__(self, file, type, *args, **kw):
		import Hear
		ViewDock.__init__(self, file, type, Results=Hear.HearResults,
					*args, **kw)

		import Sonify
		self.sonify = Sonify.Sonify(self.app, self.results.midi)
		self.results.setSonify(self.sonify)

		menubar = self.menubar
		menubar.addmenu('Sonify', 'Sonify Scoring Terms')
		for f in self.results.sonifyFields:
			menubar.addmenuitem('Sonify', 'command', label=f,
					command=lambda s=self.sonify, f=f:
					s.soundOptions(f))
