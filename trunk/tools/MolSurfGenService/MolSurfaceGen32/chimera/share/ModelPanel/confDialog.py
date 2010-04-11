# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: confDialog.py 26773 2009-01-15 22:41:16Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import preferences, help
import Pmw
import Tkinter
from copy import deepcopy
from base import _buttonInfo, _columnNames

class ConfDialog(ModelessDialog):
	title = 'Configure Model Panel'
	buttons = ('OK',)
	help="UsersGuide/modelpanel.html#configuration"

	def __init__(self, modelPanel):
		self.modelPanel = modelPanel
		options = {
			"freqButs": {},
			"executionList": ['attributes...'],
			"shownColumns": {},
			"showColor": False,
			"lastUse": None
		}
		self.prefs = preferences.addCategory("Model Panel",
						preferences.HiddenCategory,
						optDict=options)
		ModelessDialog.__init__(self)
	
	def dblClick(self):
		"""execute double-click-related commands"""
		for cmd in self.dblCommandsList.get(None):
			cb, minModels, maxModels, moleculesOnly \
							= _buttonInfo[cmd][0:4]
			sel = self.modelPanel.selected(
						moleculesOnly=moleculesOnly)
			if len(sel) < minModels:
				continue
			cb(sel)

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
			balloon='configure model table columns')
		dbl = self.noteBook.add("Double Click")
		help.register(self.noteBook.tab("Double Click"), balloon=
			'select actions for double click in model table')
		self.noteBook.pack(expand='yes', fill='both')
		
		# fill in 'Buttons' page
		Tkinter.Label(buts, text='Checked buttons will be in'
			' frequent-actions list\n'
			'Others will be in infrequent-actions list').grid(
			row=0, column=0, columnspan=3)
		
		# fill in 'Columns' page
		Tkinter.Label(cols, text='Checked columns will be shown'
			' in model table').grid(row=0, column=0, columnspan=4)
		self.showColorVar = Tkinter.IntVar(cols)
		self.showColorVar.set(self.prefs['showColor'])
		self.colDivider = Tkinter.Frame(cols, background='black')
		self.showColorButton = Tkinter.Checkbutton(cols,
				text="Show model color behind model name",
				command=self.modelPanel._buildTable,
				variable=self.showColorVar)

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
			balloon='list of functions to execute when model\n'
				'is double-clicked in model panel;\n'
				'click on function to remove from list')
		self.dblCommandMenu = Pmw.ScrolledListBox(dbl,
					hscrollmode='none', labelpos='nw',
					label_text='Function menu',
					selectioncommand=self._addDblCmdCB)
		self.dblCommandMenu.grid(row=0, column=1, sticky='nsew')
		help.register(self.dblCommandMenu,
			balloon='click on function to add to execution list')
	
	def newButton(self, butName, balloon=None, defaultFrequent=1):
		self.computePageSize = 1

		# 'Buttons' tab...
		for bn in self.buttonInfo.keys():
			self.buttonInfo[bn]['widget'].grid_forget()
		
		butPage = self.noteBook.page("Buttons")
		bdict = {}
		v = Tkinter.IntVar(butPage)
		if not self.prefs['freqButs'].has_key(butName):
			self.setDictPref('freqButs', butName, defaultFrequent)
		v.set(self.prefs['freqButs'][butName])
		bdict['variable'] = v
		bdict['widget'] = Tkinter.Checkbutton(butPage, variable=v,
			command=lambda s=self, b=butName: s._butChangeCB(b),
			text=butName, highlightthickness=0)
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
		keys.sort(lambda a, b: cmp(a.lower(), b.lower()))
		for bn in keys:
			self.buttonInfo[bn]['widget'].grid(row=row, column=col,
								sticky='w')
			row = row + 1
			if row > third:
				col = col + 1
				row = 1
		
		# 'Double Click' tab...
		minModels, maxModels = _buttonInfo[butName][1:3]
		if minModels is None or minModels < 2:
			if maxModels is None or maxModels > 0:
				cmds = list(self.dblCommandMenu.get(None))
				cmds.append(butName)
				cmds.sort()
				self.dblCommandMenu.setlist(cmds)

	def newColumn(self, colName, shown):
		self.computePageSize = 1

		for cn in self.columnInfo.keys():
			self.columnInfo[cn]['widget'].grid_forget()
		self.colDivider.grid_forget()
		self.showColorButton.grid_forget()
		
		page = self.noteBook.page("Columns")
		cdict = {}
		v = Tkinter.IntVar(page)
		v.set(shown)
		cdict['variable'] = v
		if colName:
			text = colName
		else:
			text = "(color)"
		cdict['widget'] = Tkinter.Checkbutton(page, variable=v,
			command=lambda s=self, c=colName: s._colChangeCB(c),
			text=text, highlightthickness=0)
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
		nextRow = int(fourth+1)
		self.colDivider.grid(row=nextRow, column=0, columnspan=4,
								sticky="ew")
		self.showColorButton.grid(row=nextRow+1, column=0,
								columnspan=4)
	def setDictPref(self, pref, key, value):
		from copy import copy
		copyDict = copy(self.prefs[pref])
		copyDict[key] = value
		self.prefs[pref] = copyDict

	def showColumn(self, colName, doShow):
		var = self.columnInfo[colName]['variable']
		if var.get() != doShow:
			var.set(doShow)
			self._colChangeCB(colName)

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
			# make infrequent
			self.setDictPref('freqButs', butName, 0)
			self.modelPanel._buttonFrequency(butName, frequent=0)
		else:
			# make frequent
			self.setDictPref('freqButs', butName, 1)
			self.modelPanel._buttonFrequency(butName, frequent=1)
	
	def _colChangeCB(self, colName):
		mp = self.modelPanel
		colInfo = self.columnInfo[colName]
		if colInfo['variable'].get() == 0:
			# don't show column
			if mp.shownColumns.count(1) == 1:
				# can't hide _all_ columns
				colInfo['variable'].set(1)
				raise ValueError, "Can't hide all columns!"
			mp.shownColumns[_columnNames.index(colName)] = 0
			self.setDictPref('shownColumns', colName, 0)
		else:
			# show column
			mp.shownColumns[_columnNames.index(colName)] = 1
			self.setDictPref('shownColumns', colName, 1)
		mp._buildTable()
	
	def _removeDblCmdCB(self):
		"""callback from 'dbl-click commands' listbox"""
		cmdList = list(self.dblCommandsList.get(None))
		del cmdList[int(self.dblCommandsList.curselection()[0])]
		self.dblCommandsList.setlist(cmdList)

		self.prefs['executionList'] = cmdList
