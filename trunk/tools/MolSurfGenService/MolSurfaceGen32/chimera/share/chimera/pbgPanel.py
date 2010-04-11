# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: pbgPanel.py 27381 2009-04-23 23:09:16Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import preferences, help
import Tix
import Pmw
import Tkinter
from copy import deepcopy
from chimera import tkoptions
from chimera.tkoptions import getOptionsForClass, optionSortFunc, \
							AttributeHeader
from chimera.tkoptions import PseudoBondGroupColorOption, \
	BondDrawModeOption, BondDisplayModeOption, HalfbondOption, \
	AtomBondColorOption, AtomBondLabelColor

_buttonInfo = {}
_pbgp = None

def addButton(name, callback, minGroups=1, maxGroups=None, balloon=None):
	"""Add a button to the 'Group Actions' button list.

	   'name' is the button name (duh).  'callback' is the
	   function to call when the button is pressed.  The arg to
	   'callback' will be a list of groups.  'min/maxGroups'
	   indicate how many groups have to be selected in the
	   browser for the button to be active ('None' indicates no
	   limit).

	   This is a module function so that it can be called even if
	   the group panel has not yet been created.
	"""

	if _buttonInfo.has_key(name):
		raise KeyError, \
			"Button named '%s' already exists" % name
	_buttonInfo[name] = (callback, minGroups, maxGroups, balloon)

	if _pbgp:
		_pbgp._showButton(name)
		_pbgp._confDialog.newButton(name, balloon=balloon)

_columnNames = []
_valueTypes = []
_valueFuncs = []
_defaultShows = []
def addColumns(columnInfo, defaultShown=1):
	"""Add columns to the groups table.

	   'columnInfo' is a list of 3-tuples, one for each column
	   to add.  The tuple consists of (column name, value type,
	   value-fetch function).  The value type should be 'text',
	   'image', or 'imagetext'.  The value-fetch function takes
	   one argument (a pseudobond group) and should return the
	   value to display in the table cell (which for imagetext
	   is an (image, text) tuple).  The value of an image is
	   the name of the image (the Tix name, e.g. 'tick' for
	   tickmark).  A value of None for image or text will leave
	   a blank cell.

	   'defaultShown' controls whether the column is shown in
	   the group table or not as long as the user has not yet
	   expressed a preference in the Configuration panel about it.
	"""

	noneShown = 1
	for name,type,func in columnInfo:
		if name in _columnNames:
			raise ValueError, "Duplicate pseudobond group"\
					" panel column name: %s" % name
		_columnNames.append(name)
		_valueTypes.append(type)
		_valueFuncs.append(func)
		_defaultShows.append(defaultShown)
		if _pbgp:
			try:
				shown = _pbgp._confDialog.prefs[
							'shownColumns'][name]
			except KeyError:
				shown = defaultShown
			_pbgp.shownColumns.append(shown)
			if shown:
				noneShown = 0
			_pbgp._confDialog.newColumn(name, shown)

	if not noneShown:
		_pbgp._buildTable()

def _mapName(pbg):
	if isinstance(pbg, chimera.ChainTrace):
		if len(pbg.pseudoBonds) > 0:
			return "model %s: chain" % (
						pbg.pseudoBonds[0].atoms[0]
						.molecule.oslIdent()[1:],)
	return pbg.category or "unknown"

addColumns([
	('Name', 'text', _mapName),
	('Shown', 'toggle', lambda g: (g.display, lambda g, b: setattr(g, 'display', b)))
])

class PseudoBondGroupPanel(ModelessDialog):
	title="PseudoBondGroup Panel"
	buttons=('Close','Configure...')
	name="pseudobondgroup panel"
	help="UsersGuide/pbpanel.html"

	groupsTableHelp = "click to select pseudobond groups;"\
			"\nright-hand action buttons work on selected groups;"\
			"\ndouble-click to perform default action on group"\
			"\n(see 'Configure...' for default action info)"
	def fillInUI(self, parent):
		global _pbgp
		_pbgp = self

		self.parent = parent

		# group table
		self.shownButtons = []
		self._getConfig()
		chimera.triggers.addHandler('PseudoBondGroup',
							self._fillTable, None)

		# action buttons
		self.buttonScroll = Pmw.ScrolledFrame(self.parent,
					hscrollmode='none',
					horizflex='shrink', usehullsize=1,
					hull_width=150, hull_height=1)
		self.buttonScroll.grid(row=10, column=20, sticky='nsew')
		self.actionButtons = Pmw.ButtonBox(self.buttonScroll.interior(),
						orient='vertical', pady=0)
		self.actionButtons.pack()
		self._addColumns()
		# add buttons from other extensions...
		self._addButtons()

		addButton("close", self.closeCmd,
					balloon="close pseudobond groups")
		addButton("hide", lambda m, f='display', v=0,
			sgf=setGroupField: sgf(m, f, v),
			balloon="hide selected groups; undo with 'show'")
		addButton("attributes...", attributesCmd,
			balloon="inspect/modify group attributes")
		addButton("select", selectCmd,
			balloon="incorporate groups into graphics window"
			"\nselection using current selection mode"
			"\n(see graphics window Selection menu)")
		addButton("select bonded", selectBondedCmd,
			balloon="incorporate bonded atoms into graphics window"
			"\nselection using current selection mode"
			"\n(see graphics window Selection menu)")
		addButton("show", lambda m, f='display', v=1,
			sgf=setGroupField: sgf(m, f, v),
			balloon="unhide selected groups")
		addButton("show only", lambda m, f='display',
			sgfo=setGroupFieldOnly: sgfo(m, f),
			balloon="show selected groups and hide all others")
		maxWidth = 0
		for i in range(self.actionButtons.numbuttons()):
			w = self.actionButtons.button(i).winfo_reqwidth()
			if w > maxWidth:
				maxWidth = w
		self.buttonScroll.component('clipper').configure(
						width=maxWidth+2, height='2i')
	
	def closeCmd(self, groups):
		for group in groups:
			if group.id != -1 and group.id < 0:
				import Pmw
				dialog = Pmw.MessageDialog(self.parent,
					buttons=('OK', 'Close'),
					defaultbutton='OK',
					title='Delete %s' % group.category,
					message_text="Cannot delete '%s'\n"
					"Remove all bonds instead?"
					% group.category)
				def cb(but, group=group, dialog=dialog):
					if but == 'OK':
						group.deleteAll()
					dialog.destroy()
				dialog.configure(command=cb)
				continue
			chimera.openModels.close(group)

	def Configure(self):
		"""configure action buttons"""
		self._confDialog.enter()

	def see(self, buttonName):
		scroller = self.buttonScroll.component("vertscrollbar")
		scroller.update_idletasks() # get things mapped
		if not scroller.winfo_ismapped():
			return
		curTop, curBottom = scroller.get()
		numButtons = self.actionButtons.numbuttons()
		thisButton = self.actionButtons.index(buttonName)
		newPos = (thisButton + 0.5) / numButtons
		newTop = newPos - (curBottom - curTop) / 2
		if newTop < 0:
			newTop = 0
		scroller.tk.call(scroller.cget("command"), "moveto", newTop)
		scroller.after(999, self.actionButtons.button(buttonName).flash)

	def selected(self):
		"""Return a list of the selected pseudobond groups"""

		selected = []
		for gi in self.groupsTable.hlist.info_selection():
			selected.append(self.groups[int(gi)])
		return selected

	def selectionChange(self, groups, extend=0):
		"""set (or extend) the selection to contain the given groups"""

		if not extend:
			self.groupsTable.hlist.selection_clear()

		if groups:
			groups = filter(lambda pbg, pbgs=self.groups:
							pbg in pbgs, groups)
		
		for group in groups:
			self.groupsTable.hlist.selection_set(
						self.groups.index(group))
		self._selChangeCB()

	def _addButtons(self):
		"""Add buttons to interface that were requested before
		   panel was created.
		"""

		for name, info in _buttonInfo.items():
			cb, minGrp, maxGrp, balloon = info
			self._showButton(name)
			self._confDialog.newButton(name, balloon=balloon)

	def _addColumns(self):
		"""Process column information"""
		self.shownColumns = []

		for i in range(len(_columnNames)):
			name = _columnNames[i]
			try:
				shown = self._confDialog.prefs['shownColumns'
									][name]
			except KeyError:
				shown = _defaultShows[i]
			self.shownColumns.append(shown)
			self._confDialog.newColumn(name, shown)
		self._buildTable()

	def _buildTable(self):
		if hasattr(self, 'groupsTable'):
			# can't dynamically add columns to Tix widget;
			# destroy and recreate
			selected = self.selected()
			self.groupsTable.grid_forget()
			self.groupsTable.destroy()
		else:
			selected = None

		self.groupsTable = Tix.ScrolledHList(self.parent,
			width="%d" % self.parent.winfo_pixels("3i"),
			options="""hlist.columns %d
			hlist.background #0000bfffffff
			hlist.header 1
			hlist.selectMode extended
			hlist.indicator 0"""
			% len(filter(lambda s: s == 1, self.shownColumns)))
		help.register(self.groupsTable, balloon=self.groupsTableHelp)
		self.groupsTable.hlist.config(browsecmd=self._selChange,
							command=self._dblClick)
		self.textStyle = Tix.DisplayStyle("text",
				background="#0000bfffffff",
				refwindow=self.groupsTable)
		# get a style for checkbutton columns...
		self.checkButtonStyle = Tix.DisplayStyle("window",
				background="#0000bfffffff",
				refwindow=self.groupsTable, anchor="center")
		colNum = 0
		self.columnMap = []
		for index in range(len(_columnNames)):
			if not self.shownColumns[index]:
				continue
			self.columnMap.append(index)
			self.groupsTable.hlist.header_create(colNum,
						itemtype='text',
						text=_columnNames[index])
			colNum = colNum + 1
			
		self.parent.columnconfigure(10, weight=1)
		self.parent.rowconfigure(10, weight=1)
		self.groupsTable.grid(row=10, column=10, sticky='nsew')
		self._fillTable(selected=selected, fromScratch=1)
	
	def _cmpName(self, g1, g2):
		"""compare two groups by name"""

		mapName1 = _mapName(g1)
		mapName2 = _mapName(g2)
		if isinstance(g1, chimera.ChainTrace) \
		and isinstance(g2, chimera.ChainTrace):
		   	from chimera.misc import oslModelCmp
			return oslModelCmp(g1.pseudoBonds[0].atoms[0].oslIdent(
				end=chimera.SelMolecule),
				g2.pseudoBonds[0].atoms[0].oslIdent(
				end=chimera.SelMolecule))
		return cmp(mapName1, mapName2)
		   	
	def _dblClick(self, item):
		"""user has double-clicked on groups table entry"""

		# if the state of the action buttons is due to change,
		# execute that change before calling the double-click routine
		if hasattr(self, '_selChangeIdle') and self._selChangeIdle:
			self.parent.after_cancel(self._selChangeIdle)
			self._selChangeCB()

		self._confDialog.dblClick()

	def _fillTable(self, *triggerArgs, **kw):
		hlist = self.groupsTable.hlist
		defaultable = 0
		if kw.has_key('selected') and kw['selected'] != None:
			selected = kw['selected']
		else:
			selected = self.selected()
			defaultable = 1
		rebuild = 0
		if kw.has_key('fromScratch') and kw['fromScratch']:
			rebuild =1
		else:
			prevGroups = self.groups
		self.groups = chimera.PseudoBondMgr.mgr().pseudoBondGroups
		# filter out autochain groups with no bonds...
		self.groups = filter(lambda g: len(g.pseudoBonds) > 0
			or not isinstance(g, chimera.ChainTrace), self.groups)
		self.groups.sort(lambda g1, g2, f=self._cmpName: f(g1, g2))
		if not rebuild and self.groups != prevGroups:
			rebuild = 1
		if rebuild:
			self._prevValues = {}
			hlist.delete_all()
			vf = _valueFuncs[self.columnMap[0]]
			for gi in range(len(self.groups)):
				g = self.groups[gi]
				apply(hlist.add, (gi,), self._hlistKw(g, 0))
				self._prevValues[(gi, 0)] = vf(g)
			for ci in range(1, len(self.columnMap)):
				vf = _valueFuncs[self.columnMap[ci]]
				for gi in range(len(self.groups)):
					g = self.groups[gi]
					apply(hlist.item_create, (gi, ci),
							self._hlistKw(g, ci))
					self._prevValues[(gi, ci)] = vf(g)
		else:
			for ci in range(len(self.columnMap)):
				vf = _valueFuncs[self.columnMap[ci]]
				for gi in range(len(self.groups)):
					g = self.groups[gi]
					curVal = vf(g)
					prevVal = self._prevValues[(gi, ci)]
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
					self._prevValues[(gi, ci)] = curVal
					apply(hlist.item_configure, (gi, ci),
							self._hlistKw(g, ci))
		# if only one group, select it
		if defaultable and len(self.groups) == 1:
			selected = self.groups
		for g in selected:
			if g not in self.groups:
				continue
			hlist.selection_set(self.groups.index(g))
		self._selChange(None)
	
	def _getConfig(self):
		"""retrieve configuration preferences"""

		# set up configuration dialog
		self._confDialog = _ConfDialog(self)
		self._confDialog.Close()

	def _hideButton(self, butName):
		self.shownButtons.remove(butName)
		self.actionButtons.delete(butName)

	def _hlistKw(self, group, colNum):
		vt = _valueTypes[self.columnMap[colNum]]
		vf = _valueFuncs[self.columnMap[colNum]]
		kw = {'itemtype': vt}
		txt = None
		img = None
		if vt == 'text':
			txt = vf(group)
			kw['style'] = self.textStyle
		elif vt == 'image':
			img = vf(group)
		elif vt == 'imagetext':
			img, txt = vf(group)
		else:
			kw['itemtype'] = 'window'
			bool, cb = vf(group)
			togKw = {'command':
				lambda cb=cb, g=group, b=not bool: cb(g, b),
				'indicatoron': 0,
				'borderwidth': 0} 
			if bool:
				togKw['image'] = self.groupsTable.tk.call(
					'tix', 'getimage', 'ck_on')
			else:
				togKw['image'] = self.groupsTable.tk.call(
					'tix', 'getimage', 'ck_off')
			toggle = Tkinter.Checkbutton(
						self.groupsTable.hlist, **togKw)
			kw['window'] = toggle
			kw['style'] = self.checkButtonStyle
		
		if txt != None:
			kw['text'] = str(txt)
		if img != None:
			kw['image'] = self.groupsTable.tk.call(
							'tix', 'getimage', img)
		return kw
	
	def _selChange(self, item):
		# slow browse callback interferes with double-click detection,
		# so delay callback enough to allow most double-clicks to work
		if hasattr(self, '_selChangeIdle') and self._selChangeIdle:
			self.parent.after_cancel(self._selChangeIdle)
		self._selChangeIdle = self.parent.after(300, self._selChangeCB)

	def _selChangeCB(self):
		numSel = len(self.selected())
		for b in self.shownButtons:
			state = 'normal'
			callback, minGroups, maxGroups, balloon = _buttonInfo[b]
			if minGroups and numSel < minGroups \
			or maxGroups != None and numSel > maxGroups:
				state = 'disabled'
			self.actionButtons.button(b).config(state=state)
		self._selChangeIdle = None

	def _showButton(self, name):
		callback, minGroups, maxGroups, balloon = _buttonInfo[name]

		kw = {}
		numSelected = len(self.groupsTable.hlist.info_selection())
		state = 'normal'
		if minGroups and numSelected < minGroups \
		or maxGroups != None and numSelected > maxGroups:
			state = 'disabled'
		kw['state'] = state
		kw['pady'] = 0
		kw['command'] = lambda cb=callback, s=self: apply(cb,
							(s.selected(),))
		# determine where to add the button...
		self.shownButtons.append(name)
		self.shownButtons.sort()
		index = self.shownButtons.index(name)
		if index == len(self.shownButtons)-1:
			addFunc = self.actionButtons.add
		else:
			addFunc = self.actionButtons.insert
			kw['beforeComponent'] = self.shownButtons[index+1]
		
		but = apply(addFunc, (name,), kw)
		but.config(default='disabled')
		if balloon:
			help.register(but, balloon=balloon)
import dialogs
dialogs.register(PseudoBondGroupPanel.name, PseudoBondGroupPanel)

# functions used in groups panel buttons; could be called directly also
def setGroupField(groups, field, value):
	for m in groups:
		setattr(m, field, value)

def setGroupFieldOnly(groups, field, onVal=1, offVal=0):
	for group in chimera.PseudoBondMgr.mgr().pseudoBondGroups:
		if group in groups:
			setattr(group, field, onVal)
		else:
			setattr(group, field, offVal)

def toggleModelField(groups, field, onVal=1, offVal=0):
	for group in groups:
		if getattr(group, field) == onVal:
			setattr(group, field, offVal)
		else:
			setattr(group, field, onVal)

_inspectors = {}
def attributesCmd(groups):
	global _inspectors, _groupTrigger
	if len(_inspectors) == 0:
		# should be no trigger active; start one
		_groupTrigger = chimera.triggers.addHandler(
				'PseudoBondGroup', _groupTriggerCB, None)
	for group in groups:
		if not _inspectors.has_key(group):
			_inspectors[group] = _GroupInspector(group)
		_inspectors[group].enter()

def _groupTriggerCB(trigName, myArg, groupsChanges):
	global _inspectors
	for group in groupsChanges.deleted:
		if _inspectors.has_key(group):
			_deleteAttrInspector(group)
			
def _deleteAttrInspector(group):
	_inspectors[group].destroy()
	del _inspectors[group]
	if len(_inspectors) == 0:
		# no inspectors; drop trigger
		chimera.triggers.deleteHandler('PseudoBondGroup',
							_groupTrigger)
def selectCmd(groups):
	sel = chimera.selection.ItemizedSelection()
	for group in groups:
		sel.add(group.pseudoBonds)
	chimera.tkgui.selectionOperation(sel)

def selectBondedCmd(groups):
	sel = chimera.selection.ItemizedSelection()
	atoms = []
	for group in groups:
		for pb in group.pseudoBonds:
			atoms.extend(pb.atoms)
	sel.add(atoms)
	chimera.tkgui.selectionOperation(sel)
	
class _ConfDialog(ModelessDialog):
	title = 'Configure Pseudobond Group Panel'
	buttons = ('OK',)
	help = "UsersGuide/pbpanel.html#configuration"

	def __init__(self, groupPanel):
		self.groupPanel = groupPanel
		options = {
			"shownButs": {},
			"executionList": ['attributes...'],
			"shownColumns": {}
		}
		self.prefs = preferences.addCategory("Pseudobond Group Panel",
						preferences.HiddenCategory,
						optDict=options)
		ModelessDialog.__init__(self)
	
	def dblClick(self):
		"""execute double-click-related commands"""
		for cmd in self.dblCommandsList.get(None):
			cb = _buttonInfo[cmd][0]
			cb(self.groupPanel.selected())

	def enter(self):
		if self.computePageSize:
			self.noteBook.setnaturalsize()
			self.computePageSize = 0
		ModelessDialog.enter(self)
		
	def fillInUI(self, parent):
		self.computePageSize = 1
		self.buttonInfo = {}
		self.columnInfo = {}

		self.noteBook = Pmw.NoteBook(parent)
		buts = self.noteBook.add("Buttons")
		help.register(self.noteBook.tab("Buttons"),
			balloon='configure action buttons')
		cols = self.noteBook.add("Columns")
		help.register(self.noteBook.tab("Columns"),
			balloon='configure groups table columns')
		dbl = self.noteBook.add("Double Click")
		help.register(self.noteBook.tab("Double Click"), balloon=
			'select actions for double click in groups table')
		self.noteBook.pack(expand='yes', fill='both')
		
		# fill in 'Buttons' page
		Tkinter.Label(buts, text='Checked buttons will be shown'
			' in group panel').grid(row=0, column=0, columnspan=3)
		
		# fill in 'Columns' page
		Tkinter.Label(cols, text='Checked columns will be shown'
			' in groups table').grid(row=0, column=0, columnspan=4)

		# fill in 'Double Click' page
		dbl.rowconfigure(0, weight=1)
		dbl.columnconfigure(0, weight=1)
		dbl.columnconfigure(1, weight=1)
		self.dblCommandsList = Pmw.ScrolledListBox(dbl,
			hscrollmode='none', labelpos='nw',
			label_text="Execution list",
			items=self.prefs['executionList'],
			selectioncommand=self._removeDblCmdCB)
		self.dblCommandsList.grid(row=0, column=0, sticky='nsew')
		help.register(self.dblCommandsList,
			balloon='list of functions to execute when group\n'
				'is double-clicked in group panel;\n'
				'click on function to remove from list')
		self.dblCommandMenu = Pmw.ScrolledListBox(dbl,
					hscrollmode='none', labelpos='nw',
					label_text='Function menu',
					selectioncommand=self._addDblCmdCB)
		self.dblCommandMenu.grid(row=0, column=1, sticky='nsew')
		help.register(self.dblCommandMenu,
			balloon='click on function to add to execution list')
	
	def newButton(self, butName, balloon=None):
		self.computePageSize = 1

		# 'Buttons' tab...
		for bn in self.buttonInfo.keys():
			self.buttonInfo[bn]['widget'].grid_forget()
		
		butPage = self.noteBook.page("Buttons")
		bdict = {}
		v = Tkinter.IntVar(butPage)
		if not self.prefs['shownButs'].has_key(butName):
			self.prefs['shownButs'][butName] = 1
		elif not self.prefs['shownButs'][butName]:
			# take button out of list
			self.groupPanel._hideButton(butName)
		v.set(self.prefs['shownButs'][butName])
		bdict['variable'] = v
		bdict['widget'] = Tkinter.Checkbutton(butPage, variable=v,
			command=lambda s=self, b=butName: s._butChangeCB(b),
			text=butName)
		self.buttonInfo[butName] = bdict
		if balloon:
			help.register(bdict['widget'], balloon=balloon)

		numButs = len(self.buttonInfo)
		# figure out size of columns [3 columns]
		third = numButs / 3.0
		if third > int(third):
			third = int(third) + 1
		
		row = 1
		col = 0
		keys = self.buttonInfo.keys()
		keys.sort()
		for bn in keys:
			self.buttonInfo[bn]['widget'].grid(row=row, column=col,
								sticky='w')
			row = row + 1
			if row > third:
				col = col + 1
				row = 1
		
		# 'Double Click' tab...
		(callback, minGroups, maxGroups, balloon) = _buttonInfo[butName]
		if minGroups is None or minGroups < 2:
			if maxGroups is None or maxGroups > 0:
				cmds = list(self.dblCommandMenu.get(None))
				cmds.append(butName)
				cmds.sort()
				self.dblCommandMenu.setlist(cmds)

	def newColumn(self, colName, shown):
		self.computePageSize = 1

		for cn in self.columnInfo.keys():
			self.columnInfo[cn]['widget'].grid_forget()
		
		page = self.noteBook.page("Columns")
		cdict = {}
		v = Tkinter.IntVar(page)
		v.set(shown)
		cdict['variable'] = v
		cdict['widget'] = Tkinter.Checkbutton(page, variable=v,
			command=lambda s=self, c=colName: s._colChangeCB(c),
			text=colName)
		self.columnInfo[colName] = cdict

		numCols = len(self.columnInfo)
		# figure out size of columns [4 columns]
		fourth = numCols / 4.0
		if fourth > int(fourth):
			fourth = int(fourth) + 1
		
		row = 1
		col = 0
		keys = self.columnInfo.keys()
		keys.sort()
		for cn in keys:
			self.columnInfo[cn]['widget'].grid(row=row, column=col,
								sticky='w')
			row = row + 1
			if row > fourth:
				col = col + 1
				row = 1
		
	def _addDblCmdCB(self):
		"""callback from 'command menu' listbox"""
		cmdList = list(self.dblCommandsList.get(None))
		cmdList.append(self.dblCommandMenu.getcurselection()[0])
		self.dblCommandsList.setlist(cmdList)
		self.dblCommandMenu.selection_clear()

		self.prefs['executionList'] = cmdList
		preferences.save()
		
	def _butChangeCB(self, butName):
		butInfo = self.buttonInfo[butName]
		if butInfo['variable'].get() == 0:
			# don't show button
			self.groupPanel._hideButton(butName)
			self.prefs['shownButs'][butName] = 0
		else:
			# show button
			self.groupPanel._showButton(butName)
			self.prefs['shownButs'][butName] = 1
		preferences.save()
	
	def _colChangeCB(self, colName):
		gp = self.groupPanel
		colInfo = self.columnInfo[colName]
		if colInfo['variable'].get() == 0:
			# don't show column
			if gp.shownColumns.count(1) == 1:
				# can't hide _all_ columns
				colInfo['variable'].set(1)
				raise ValueError, "Can't hide all columns!"
			gp.shownColumns[_columnNames.index(colName)] = 0
			self.prefs['shownColumns'][colName] = 0
		else:
			# show column
			gp.shownColumns[_columnNames.index(colName)] = 1
			self.prefs['shownColumns'][colName] = 1
		preferences.save()
		gp._buildTable()
	
	def _removeDblCmdCB(self):
		"""callback from 'dbl-click commands' listbox"""
		cmdList = list(self.dblCommandsList.get(None))
		del cmdList[int(self.dblCommandsList.curselection()[0])]
		self.dblCommandsList.setlist(cmdList)

		self.prefs['executionList'] = cmdList
		preferences.save()

class _GroupInspector(ModelessDialog):
	buttons = ('Close',)
	help = "UsersGuide/pbattrib.html"

	def __init__(self, group):
		self.group = group
		self.setInCallback = 0
		if group.category:
			self.title = "%s attributes" % _mapName(group)
		self.triggers = [
			('PseudoBondGroup',
				chimera.triggers.addHandler('PseudoBondGroup',
					self._refreshCB, None)),
			('PseudoBond',
				chimera.triggers.addHandler('PseudoBond',
					self._refreshCB, None))
		]
		self.refreshFuncs = {}
		self.refreshFuncs['PseudoBondGroup'] = []
		self.refreshFuncs['PseudoBond'] = []
		ModelessDialog.__init__(self)
	
	def fillInUI(self, parent):
		self.parent = parent
		self.contents = Tkinter.Frame(parent)
		self._fillInContents()
		self.contents.pack(expand=1, fill='both')

	def destroy(self):
		for trigName, trigHandler in self.triggers:
			chimera.triggers.deleteHandler(trigName, trigHandler)
		self._toplevel.destroy()

	def _refreshCB(self, trigName, myData, changes):
		if self.setInCallback:
			self.setInCallback = 0
			return
		if self.group.__destroyed__:
			return
		for rf in self.refreshFuncs[trigName]:
			rf(self.group)
	
	def setAttr(self, attr, val):
		self.setInCallback = 1
		setattr(self.group, attr, val)

	def setSubattribute(self, items, attr, mode):
		self.setInCallback = 1
		for i in getattr(self.group, items):
			setattr(i, attr, mode)

	def setColor(self, attr, color):
		if self.colorOverwrite.get():
			for pb in self.group.pseudoBonds:
				pb.color = None
		self.setAttr(attr, color)

	def _addGroupOpt(self, opt, header, **kw):
		if kw.has_key('optlabel'):
			label = kw['optlabel']
			del kw['optlabel']
		else:
			label = None
		if kw.has_key('master'):
			master = kw['master']
			del kw['master']
		else:
			master = self.contents
		if opt == PseudoBondGroupColorOption:
			sa = self.setColor
		elif hasattr(opt, 'callback'):
			sa = opt.callback
		else:
			sa = self.setAttr
		doRefresh = True
		try:
			value = getattr(self.group, opt.attribute)
		except AttributeError:
			value = opt.default
			doRefresh = False
		widget = header.addOption(opt, label, value,
				lambda o, f=sa: f(o.attribute, o.get()))
		if hasattr(opt, 'storeAs'):
			setattr(self, opt.storeAs, widget)
		if doRefresh:
			func = lambda g, w=widget: w.display([g])
			self.refreshFuncs['PseudoBondGroup'].append(func)

	def _addAggregateOpt(self, opt, aggAttr, aggClass, header, **kw):
		if kw.has_key('optlabel'):
			label = kw['optlabel']
			del kw['optlabel']
		else:
			label = None
		if kw.has_key('master'):
			master = kw['master']
			del kw['master']
		else:
			master = self.contents
		if kw.has_key('sa'):
			sa = kw['sa']
			del kw['sa']
		else:
			sa = self.setSubattribute
		widget = header.addOption(opt, label, None,
					lambda o, f=sa, a=aggAttr, kw=kw: 
					f(a, o.attribute, o.get(), **kw))
		self.refreshFuncs[aggClass].append(
			lambda g, w=widget, a=aggAttr: w.display(getattr(g, a)))
		widget.display(getattr(self.group, aggAttr))

	def _fillInContents(self):
		mainHeader = AttributeHeader(self.contents,
						klass=self.group.__class__)
		mainHeader.grid(row=0, column=0, sticky='ew')
		row = 1

		widget = mainHeader.addWidget(Tkinter.Label, justify='center')
		self.refreshFuncs['PseudoBondGroup'].append(
			lambda g, w=widget: w.config(
			text="%d pseudobonds in group" % len(g.pseudoBonds)))
		self.refreshFuncs['PseudoBondGroup'][-1](self.group)

		options = getOptionsForClass(self.group.__class__)
		class GroupColorOverride(tkoptions.BooleanOption):
			name = "changing group color\nremoves individual colors"
			default = True
			storeAs = "colorOverwrite"
			balloon = "if true, individual bond colors will be\n" \
				"removed when group color is set"
			sorting = PseudoBondGroupColorOption.name + " 1"
		options.append(GroupColorOverride)
		options.sort(optionSortFunc)

		for opt in options:
			self._addGroupOpt(opt, mainHeader)

		self.contents.rowconfigure(row, minsize="0.1i")
		row += 1
		header = AttributeHeader(self.contents,
				klass=chimera.PseudoBond, composite=True)
		header.grid(row=row, column=0, sticky='ew')
		row += 1
		opts = [BondDrawModeOption, BondDisplayModeOption,
			AtomBondLabelColor, HalfbondOption, AtomBondColorOption]
		opts.sort(optionSortFunc)
		for opt in opts:
			self._addAggregateOpt(opt, "pseudoBonds",
						"PseudoBond", header)

	def Close(self):
		ModelessDialog.Close(self)
		_deleteAttrInspector(self.group)
