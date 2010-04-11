# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: gui.py 29220 2009-11-03 21:21:58Z pett $

from manager import selMgr, ui
import string
import sys
import traceback
from chimera import selection, triggers, openModels, SelVertex, help
from chimera.baseDialog import ModelessDialog
import Tkinter
import tkFont
import Pmw
from CGLtk import optCascade
import os
import chimera
from chimera import specifier, ZoneDialog, Molecule

_selectorString = intern("Selectors")
_selectionString = intern("Selections")
_curSelectedString = intern("Existing Selection")
_wbGroupString = intern("Workbench selector")
_mainMenuString = intern("Main menu")
_newMenuString = intern("New submenu...")
_thisMenuString = intern("Add here")
_showCurSelString = intern("Show current selector contents")
_showWbSelString = intern("Show workbench selector contents")
_atomSpecString = intern("Midas Atom Specifier...")
_wbEmptyString = intern("Workbench empty")

class SelectionPanel(ModelessDialog):
	name = "selector workbench"
	buttons = ("Close",)
	help = "UsersGuide/selectionGUI.html"
	title = "Selector Construction Panel"

	def fillInUI(self, parent):
		# control how selector menu items are sorted
		self._sortFunc = self._sortInterspersed

		# make menubar
		self.menuBar = Tkinter.Menu(parent, type="menubar", tearoff=False)
		#self.menuBar.pack(anchor="nw", expand="no", fill="x")
		parent.winfo_toplevel().config(menu=self.menuBar)
		help.register(self.menuBar, "UsersGuide/selectionGUI.html#menuBar")

		# selector menu
		selMenu = Tkinter.Menu(self.menuBar)
		selMenu.add_command(label="Rename", command=self._rename)
		selMenu.add_command(label="Delete", command=self._delete)
		selMenu.add_command(label="Delete menu",
						command=self._deleteMenu)
		self.menuBar.add_cascade(label="Selector", menu=selMenu)

		# workbench menu
		wbMenu = Tkinter.Menu(self.menuBar)
		wbMenu.add_command(label="Load from current",
						command=self._loadFromCurrent)
		wbMenu.add_command(label="Save...", command=self._saveAs)
		self.menuBar.add_cascade(label="Workbench", menu=wbMenu)

		# panels menu
		self.panelsMenu = Tkinter.Menu(self.menuBar)
		self.showWbTextVar = Tkinter.IntVar(self.menuBar)
		self.showCurTextVar = Tkinter.IntVar(self.menuBar)
		self.showWbTextVar.set(0)
		self.showCurTextVar.set(0)
		self.showWbTextVar.trace('w', self._changeWbSelShow)
		self.showCurTextVar.trace('w', self._changeCurSelShow)
		self.panelsMenu.add_checkbutton(label=_showWbSelString,
		  variable=self.showWbTextVar)
		self.panelsMenu.add_checkbutton(label=_showCurSelString,
		  variable=self.showCurTextVar)
		self.menuBar.add_cascade(label="Panels", menu=self.panelsMenu)

		from chimera.tkgui import aquaMenuBar
		aquaMenuBar(self.menuBar, parent, pack = 'top')

		# make selectors option menu
		# do this before making the function menu so that the function
		# menu can use lambdas that reference the option menu
		self.selectorsMenu = optCascade.CascadeOptionMenu(parent,
				  command=self._setCurSelector, labelpos="n",
				  label_text="Selector list:")
		chimera.tkgui.registerMenuBalloon(
					self.selectorsMenu.component('balloon'))
		self._updateSelectorsMenu(index=_curSelectedString)
		self.selectorsMenu.pack()
		help.register(self.selectorsMenu.component('hull'),
					"UsersGuide/selectionGUI.html#selList")
		
		# make "Select" area
		selArea = Pmw.Group(parent, tag_text="Select")
		Tkinter.Button(selArea.interior(), text="Current",
			command=self._selectCurrent).grid(row=0, column=0)
		Tkinter.Button(selArea.interior(), text="Workbench",
			command=self._selectWorkbench).grid(row=0, column=1)
		Tkinter.Button(selArea.interior(), text="Internal bonds",
			command=lambda s=selection: s.addImpliedCurrent(
					vertices=0)).grid(row=0, column=2)
		selArea.pack(pady=2)

		# operations on work group
		wbArea = Pmw.Group(parent, tag_text="Workbench")
		def zoneCB(s=self):
			zd = chimera.dialogs.display(ZoneDialog.ZoneDialog.name)
			zd.callback = s._insertZone
		Tkinter.Button(wbArea.interior(), text="Zone...",
					command=zoneCB).pack(side="left")
		Tkinter.Button(wbArea.interior(), text="Clear",
					command=self._clear).pack(side="left")
		opMenuButton = Tkinter.Menubutton(wbArea.interior(),
		  indicatoron=1, text="Operations", relief="raised")
		opMenu = Tkinter.Menu(opMenuButton)
		opMenu.add_command(label="Select internal bonds",
						command=self._wbSelBonds)
		opMenu.add_command(label="Intersect with current",
		  command=lambda s=self, a1="Intersect with", a2="INTERSECT":
		  s._doOp(a1,a2))
		opMenu.add_command(label="Workbench + current",
		  command=lambda s=self,
		  a1="Append", a2="EXTEND": s._doOp(a1,a2))
		opMenu.add_command(label="Workbench - current",
		  command=lambda s=self,
		  a1="Subtract away", a2="REMOVE": s._doOp(a1,a2))
		opMenu.add_command(label="Current - workbench",
		  command=lambda s=self,
		  a1="Subtract from", a2="REMOVE": s._doOp(a1,a2,inverse=1))
		opMenuButton['menu'] = opMenu
		opMenuButton.pack(side='left')
		wbArea.pack(pady=2)

		# status area
		statusArea = Pmw.Group(parent, tag_text="Status")
		labelFont = tkFont.Font(size=10, slant='roman', underline=1)
		infoFont = tkFont.Font(size=10, slant='italic')
		wbFont = tkFont.Font(size=8, slant='roman')
		inch = parent.winfo_pixels("1i")
		self.statusLabelFont = labelFont
		self.statusInfoFont = infoFont
		curGroupFrame = Tkinter.Frame(statusArea.interior())
		curGroupFrame.pack(fill='x')
		self.curGroupVar = Tkinter.StringVar(parent)
		Tkinter.Label(curGroupFrame, font=labelFont,
				text="Current selector").pack(side='top')
		Tkinter.Label(curGroupFrame, font=infoFont, height=2,
		  wraplength=2.6*inch, justify='center',
		  textvariable=self.curGroupVar).pack(side='top')
		self.wbContentsVar = Tkinter.StringVar(parent)
		self.wbContentsVar.set(_wbEmptyString)
		Tkinter.Label(curGroupFrame, textvariable=self.wbContentsVar,
				justify='left', font=wbFont).pack(side='left')
		statusArea.pack(padx=2, pady=2, fill='x')

		# ...work group (selector)
		self.wbGroupPanel = Tkinter.Toplevel(parent)
		self.wbGroupPanel.title("Workbench selector")
		self.wbGroupPanel.protocol('WM_DELETE_WINDOW', 
		  lambda s=self: s.showWbTextVar.set(0))
		self.wbGroupPanel.withdraw()
		self.wbGroupPanel.rowconfigure(0, weight=1)
		self.wbGroupPanel.columnconfigure(0, weight=1)
		self.wbGroupDisp = Pmw.ScrolledText(self.wbGroupPanel,
		  text_height=15, text_width=60)
		self.wbGroupDisp.grid(sticky="nsew")

		# ...current group (selector)
		self.curGroupPanel = Tkinter.Toplevel(parent)
		self.curGroupPanel.title("Current selector")
		self.curGroupPanel.protocol('WM_DELETE_WINDOW', 
		  lambda s=self: s.showCurTextVar.set(0))
		self.curGroupPanel.withdraw()
		self.curGroupPanel.rowconfigure(0, weight=1)
		self.curGroupPanel.columnconfigure(0, weight=1)
		self.curGroupDisp = Pmw.ScrolledText(self.curGroupPanel,
		  text_height=15, text_width=60,
		  text_bg = "#c0c0c0", text_state="disabled")
		self.curGroupDisp.grid(sticky="nsew")

		# atom spec dialog
		self.midasSpec = '#'
		self.atomSpecDialog = Pmw.PromptDialog(parent, 
			title='Atom Spec Selector Dialog',
			label_text='Enter Midas atom specifier',
			entryfield_labelpos='n',
			entry_text=self.midasSpec,
			defaultbutton = 0,
			buttons = ('OK', 'Cancel', 'Help'),
			command = self._atomSpecDialogCB)
		self.atomSpecDialog.withdraw()

		self._setCurSelector([_curSelectedString])
		selMgr.addCallback(self.mgrSelectorChange)
	
	def _atomSpecDialogCB(self, button):
		if button is None or button == 'Cancel':
			self.atomSpecDialog.withdraw()
		elif button == 'Help':
			help.display("UsersGuide/midas/atom_spec.html")
		else:
			try:
				specifier.parse(self.atomSpecDialog.get())
			except (SyntaxError, ValueError), errmsg:
				Pmw.MessageDialog(title='Syntax Error',
				  message_text='Syntax error in specifier: %s\n(specifier was "%s")\nPlease retry.' % (errmsg, self.atomSpecDialog.get()))
			else:
				self.midasSpec = self.atomSpecDialog.get()
				self.curGroupVar.set(self._groupAbbr(
							self.curSelectorName))
				self.atomSpecDialog.withdraw()
				self._updateCurGroupArea()
		
	def _buildItems(self, itemsDict = None, addSelected=1, addAtomSpec=1):
		# build a list from a self.selectors()-style dictionary
		# that a cascading option menu can take as an item list

		itemList = []
		if itemsDict == None:
			itemsDict = selMgr.selectorDict()
		if addSelected:
			itemList.append(_curSelectedString)
		if addAtomSpec:
			itemList.append(_atomSpecString)
		for itemName in itemsDict.keys():
			registrant, itemValue = itemsDict[itemName]
			if isinstance(itemValue, dict):
				itemList.append((itemName,
				  self._buildItems(itemValue,
					  addSelected=0, addAtomSpec=0)))
			else:
				itemList.append(itemName)
		itemList.sort(self._sortFunc)
		return itemList

	def _buildMenuChoiceItems(self, itemsDict = None, addMainMenuString=1):
		# build a list from a self.selectors-style dictionary
		# that a cascading option menu can take as an item list
		# ... include only rollover menu titles and add a "main
		# menu" choice at top level and "new submenu" choices at
		# appropriate levels.  Used to select a menu to add items
		# to.

		# wanted to be able to choose non-leaf items of the cascade
		# menu, but adding a "command" to a cascade is not supported
		# on Windoze
		itemList = [_newMenuString]
		if addMainMenuString:
			itemList.append(_mainMenuString)
		else:
			itemList.append(_thisMenuString)
		if itemsDict == None:
			itemsDict = selMgr.selectorDict()
		for itemName in itemsDict.keys():
			registrant, itemValue = itemsDict[itemName]
			if isinstance(itemValue, dict):
				itemList.append((itemName,
				  self._buildMenuChoiceItems(itemValue, 0)))
		itemList.sort(self._sortFunc)
		return itemList

	def _changeCurSelShow(self, var1, var2, mode):
		if self.showCurTextVar.get():
			self.curGroupPanel.deiconify()
		else:
			self.curGroupPanel.withdraw()

	def _changeWbSelShow(self, var1, var2, mode):
		if self.showWbTextVar.get():
			self.wbGroupPanel.deiconify()
		else:
			self.wbGroupPanel.withdraw()

	def _clear(self):
		self.wbGroupDisp.clear()
		self.wbContentsVar.set(_wbEmptyString)
	
	def _confirmDeleteCB(self, rep):
		self._confirmDialog.deactivate()
		if rep is None or rep == 'Cancel':
			return
		selMgr.deleteSelector(ui, self.curSelectorName,
						prune=True, makeCallbacks=True)
		self._saveUIselectors()
		
	def _curSelectorRegistrant(self):
		reg = None
		selDict = selMgr.selectorDict()
		for component in self.curSelectorName:
			try:
				(reg, selDict) = selDict[component]
			except KeyError:
				return None
		return reg

	def _defaultSelectorName(self):
		# when no particular selector is chosen, pick chimera selection
		return [_curSelectedString]

	def __del__(self):
		for baseClass in self.__class__.__bases__:
			baseClass.__del__(self)
		selMgr.removeCallback(self.mgrSelectorChange)

	def _delete(self):
		if self._curSelectorRegistrant() != ui:
			Pmw.MessageDialog(title='Delete Error',
				message_text='You cannot delete a selector\n'
				'that you did not create yourself')
			return
		self._confirmDialog = Pmw.MessageDialog(title='Confirm Delete',
					message_text='Really delete "%s"?' %
					self._groupAbbr(self.curSelectorName),
					buttons=('Cancel', 'OK'),
					command=self._confirmDeleteCB)
		self._confirmDialog.activate()

	def _deleteMenu(self):
		uiMenus = []
		for (cat, info) in selMgr.selectorDict().items():
			reg, catInfo = info
			if not isinstance(catInfo, dict):
				# not a menu
				continue
			uiMenus = uiMenus + self._uiMenus([cat], reg, catInfo)
		if not uiMenus:
			Pmw.MessageDialog(title='Delete Menu Error',
				message_text='No menu has been created by you')
			return
		self._dmenuMap = {}
		for menu in uiMenus:
			self._dmenuMap[self._groupAbbr(menu)] = menu
		items = self._dmenuMap.keys()
		items.sort()
		self._deleteMenuDialog = Pmw.SelectionDialog(
					title='Choose Deletion Menu',
					buttons=('Cancel','OK'),
					defaultbutton='OK',
					scrolledlist_labelpos='s',
					label_text='Choose a menu to delete',
					scrolledlist_items=items,
					command=self._deleteMenuCB)
		self._deleteMenuDialog.show()
	
	def _deleteMenuCB(self, rep):
		self._deleteMenuDialog.withdraw()
		if rep is None or rep == 'Cancel':
			return
		sels = self._deleteMenuDialog.getcurselection()
		if len(sels) == 0:
			return
		dmenu = self._dmenuMap[sels[0]]
		uiSelDict = selMgr.selectors[ui].copy()
		for component in dmenu:
			uiSelDict = uiSelDict[component]
		self._deleteMenuSelectors(dmenu, uiSelDict)
		selMgr.makeCallbacks()
		self._saveUIselectors()
	
	def _deleteMenuSelectors(self, menu, selDict):
		for name, info in selDict.items():
			if isinstance(info, dict):
				# submenu
				self._deleteMenuSelectors(
						menu + [name], selDict[name])
				continue
			selMgr.deleteSelector(ui, menu + [name], prune=True,
							makeCallbacks=False)
			
	def _doOp(self, readableOp, opString, inverse=0):
		# 'workhorse' function for performing a logical operation
		# on two selections

		self.wbGroupDisp.settext(selMgr.doOp(opString,
		  self.wbGroupDisp.get(), self._selectorText(), inverse))
		self.wbContentsVar.set(self.wbContentsVar.get()
			+ "\n  " + readableOp + " " +
			self._groupAbbr(self.curSelectorName, newLine=" "))

	def _groupAbbr(self, groupName, newLine="\n"):
		if groupName[0] == _atomSpecString:
			return _atomSpecString + "%s(%s)" % (newLine,
								self.midasSpec)
		groupAbbr = ""
		if len(groupName) > 2:
			groupAbbr = groupAbbr + "... / "
		if len(groupName) > 1:
			groupAbbr = groupAbbr + groupName[-2] + " / "
		groupAbbr = groupAbbr + groupName[-1]
		return groupAbbr

	def _insertZone(self, zoneDialog):
		from chimera import specifier
		initSel = string.strip(self.wbGroupDisp.get())
		selStr = initSel + "\nfrom chimera import specifier\n" \
		                  "sel.merge(selection.REPLACE, specifier.zone("
		if len(initSel) > 0:
			selStr = selStr + "sel, "
			statusStr = self.wbContentsVar.get() + "\n  Zone "
		else:
			selStr = selStr + "selection.copyCurrent(), "
			statusStr = "Workbench contents:\n  Zone "
		if zoneDialog.doResidues.get():
			selStr = selStr + "specifier.RESIDUE, "
			statusStr = statusStr + "residues "
		else:
			selStr = selStr + "specifier.ATOM, "
			statusStr = statusStr + "atoms "
		if zoneDialog.doFurther.get():
			further = zoneDialog.furtherEntry.get()
			selStr = selStr + further + ", "
			statusStr = statusStr + "> " + further
		else:
			selStr = selStr + "None, "
		if zoneDialog.doCloser.get():
			closer = zoneDialog.closerEntry.get()
			selStr = selStr + closer + ", models))\n"
			statusStr = statusStr + "< " + closer
		else:
			selStr = selStr + "None, models))\n"
		selStr = selStr + "sel.addImplied(vertices=0) # add bonds\n"
		self.wbGroupDisp.settext(selStr)
		self.wbContentsVar.set(statusStr)

	def _loadFromCurrent(self):
		self.wbGroupDisp.settext(self._selectorText())
		if isinstance(self.curSelectorName, basestring):
			selString = self.curSelectorName
		else:
			selString = string.join(self.curSelectorName, "/")
		self.wbContentsVar.set("Workbench contents:\n  "
			+ self._groupAbbr(self.curSelectorName, newLine=" "))
	
	def mgrSelectorChange(self):
		"""called when selectors change in the selection manager"""
		newItems = self._buildItems()
		list = newItems
		curSelectorValid = 1
		for component in self.curSelectorName:
			foundComponent = 0
			for item in list:
				if isinstance(item, basestring):
					if item == component:
						list = []
						foundComponent = 1
						break
				elif item[0] == component:
					list = item[1]
					foundComponent = 1
					break
			if not foundComponent:
				curSelectorValid = 0
				break
		if curSelectorValid and len(list) != 0:
			curSelectorValid = 0

		if not curSelectorValid:
			self.curSelectorName = self._defaultSelectorName()
		
		self._updateSelectorsMenu(index=self.curSelectorName[0])

		if not curSelectorValid:
			self._setCurSelector(self.curSelectorName)

	def _rename(self):
		if self._curSelectorRegistrant() != ui:
			Pmw.MessageDialog(title='Rename Error',
				message_text='You cannot rename a selector\n'
				'that you did not create yourself')
			return
		self._renameFrom = self.curSelectorName
		if not hasattr(self, "_renameDialog"):
			self._renameDialog = MenuPositionDialog(self,
					'Rename to:', self._renameDialogCB)
		self._renameDialog.component('entry').selection_range(0, 'end')
		self._renameDialog.show()
	
	def _renameDialogCB(self, rep):
		self._renameDialog.withdraw()
		if rep is None or rep == 'Cancel':
			return
		groupName = string.strip(
				self._renameDialog.component('entry').get())
		if groupName == "":
			Pmw.MessageDialog(title='Selector Name Error',
				message_text='Empty selector name').show()
			return

		saveDict = selMgr.selectorDict()
		saveDict[_atomSpecString] = None # prevent an overwrite
		saveDict[_curSelectedString] = None # prevent an overwrite
		for component in self._renameDialog.menuTarget:
			registrant, saveDict = saveDict[component]
		
		if groupName in saveDict.keys():
			Pmw.MessageDialog(title='Selector Name Error',
			  message_text='Renaming to existing name').show()
			return
		
		selMgr.addSelector(ui, self._renameDialog.menuTarget +
		  [groupName], self._selectorText(self._renameFrom),
		  makeCallbacks=0)
		selMgr.deleteSelector(ui, self._renameFrom, prune=True,
							makeCallbacks=True)

		self._saveUIselectors()

	def _saveAs(self):
		if not hasattr(self, "_saveAsDialog"):
			self._saveAsDialog = MenuPositionDialog(self,
				'New selector name:', self._saveAsDialogCB)
		self._saveAsDialog.component('entry').selection_range(0, 'end')
		self._saveAsDialog.show()
	
	def _saveAsDialogCB(self, rep):
		self._saveAsDialog.withdraw()
		if rep is None or rep == 'Cancel':
			return
		groupName = string.strip(
				self._saveAsDialog.component('entry').get())
		if groupName == "":
			Pmw.MessageDialog(title='Selector Name Error',
				message_text='Empty selector name').show()
			return

		saveDict = selMgr.selectorDict()
		saveDict[_atomSpecString] = None # prevent an overwrite
		saveDict[_curSelectedString] = None # prevent an overwrite
		for component in self._saveAsDialog.menuTarget:
			registrant, saveDict = saveDict[component]
		
		if groupName in saveDict.keys():
			Pmw.MessageDialog(title='Selector Name Error',
			  message_text='Duplicate selector name').show()
			return
		
		selMgr.addSelector(ui, self._saveAsDialog.menuTarget +
		  [groupName], self.wbGroupDisp.get(), makeCallbacks=1)

		self._saveUIselectors()

	def _saveUIselectors(self):
		saveLoc = chimera.pathFinder().pathList("selectionGUI",
							"selectors", 0, 0, 1)[0]
		if not os.path.exists(saveLoc):
			# try to create
			dirPath, fileName = os.path.split(saveLoc)
			if not os.path.exists(dirPath):
				try:
					os.makedirs(dirPath)
				except:
					Pmw.MessageDialog(title='Save Error',
					  message_text="Cannot create selector save directory '%s'" % (dirPath)).show()
					return
		try:
			saveFile = open(saveLoc, 'w')
		except:
			Pmw.MessageDialog(title='Save Error',
			  message_text="Cannot open save file ('%s')for writing" % (saveLoc)).show()
			return
			
		selDict = selMgr.selectorDict([ui], argDictsOnly=1)
		saveFile.write(repr(selDict))
		saveFile.close()

	def _selectCurrent(self):
		if self.curSelectorName[0] == _atomSpecString:
			selection.setCurrent(specifier.evalSpec(self.midasSpec))
		else:
			selection.setCurrent(
				selMgr.selectionFromText(self._selectorText()))

	def _selectorText(self, selectorName=None):
		if not selectorName:
			selectorName = self.curSelectorName
		if selectorName[0] == _atomSpecString:
			return """from chimera import specifier
sel.merge(selection.REPLACE, specifier.evalSpec("%s"))
sel.addImplied(vertices=0) # add bonds
""" % (self.midasSpec,)

		if selectorName[0] == _curSelectedString:
			return """selection.mergeUsingCurrent(selection.REPLACE, sel)
"""
		dict = selMgr.selectorDict()
		groupName = selectorName
		while len(groupName) > 1:
			registrant, dict = dict[groupName[0]]
			groupName = groupName[1:]
		registrant, value = dict[groupName[0]]
		enumText, grouping, description = value
		return enumText
	
	def _selectWorkbench(self):
		selection.setCurrent(
			  selMgr.selectionFromText(self.wbGroupDisp.get()))
	
	def _setCurSelector(self, groupName):
		self.curSelectorName = groupName

		self.curGroupVar.set(self._groupAbbr(groupName))
		self._updateCurGroupTitle()
		self._updateCurGroupArea()
		if groupName[0] == _atomSpecString:
			self.atomSpecDialog.show()

	def _sortInterspersed(self, item1, item2):
		if not isinstance(item1, basestring):
			item1 = item1[0]
		if not isinstance(item2, basestring):
			item2 = item2[0]
		# case-independent string comparison
		if string.lower(item1) < string.lower(item2):
			return -1
		return 1
	
	def _uiMenus(self, thisMenu, menuRegistrant, menuDict):
		menuDeletable = menuRegistrant == ui
		dmenus = []
		for menu, info in menuDict.items():
			reg, menuInfo = info
			if reg != ui:
				menuDeletable = 0
			if isinstance(menuInfo, dict):
				dmenus = dmenus + self._uiMenus(
					thisMenu + [menu], reg, menuInfo)
		if menuDeletable:
			dmenus.append(thisMenu)
		return dmenus

	def _updateCurGroupArea(self):
		font = tkFont.Font(
			font=self.curGroupDisp.component('text')['font'])
		font.config(slant="roman")
		
		self.curGroupDisp.component('text')['font'] = font
		self.curGroupDisp.settext(self._selectorText())

	def _updateCurGroupTitle(self):
		groupAbbr = ""
		if len(self.curSelectorName) > 2:
			groupAbbr = groupAbbr + ".../"
		if len(self.curSelectorName) > 1:
			groupAbbr = groupAbbr + self.curSelectorName[-2] \
									  + "/"
		groupAbbr = groupAbbr + self.curSelectorName[-1]
		self.curGroupPanel.title("Current selector ("+groupAbbr+")")
	
	def _updateSelectorsMenu(self, *args, **kw):
		sels = selMgr.selectorDict()
		apply(self.selectorsMenu.setitems,
						(self._buildItems(sels),), kw)
		selMgr.registerSelectorBalloons(
			self.selectorsMenu.component('balloon'), sels)

	def _wbSelBonds(self):
		self.wbGroupDisp.component('text').insert('end',
					  "\nsel.addImplied(vertices=0)\n")
from chimera import dialogs
dialogs.register(SelectionPanel.name, SelectionPanel)

class MenuPositionDialog(Pmw.PromptDialog):
	def __init__(self, mainGUI, label_text, command):
		Pmw.PromptDialog.__init__(self, label_text=label_text,
		  entryfield_labelpos='w', buttons=('Cancel','OK'),
		  defaultbutton='OK', separatorwidth = 1, command=command)
		self.menuTarget = []
		self.mainGUI = mainGUI
		menuChoiceFrame = self.component('dialogchildsite')
		self._menuChoiceCascade = optCascade.CascadeOptionMenu(
				menuChoiceFrame, initialitem=_mainMenuString,
				items=mainGUI._buildMenuChoiceItems(),
				command=self._menuChoiceCB)
		chimera.tkgui.registerMenuBalloon(
				self._menuChoiceCascade.component('balloon'))
		self._menuChoiceCascade.pack()
		self._menuChoiceLabelVar = Tkinter.StringVar(menuChoiceFrame)
		self._menuChoiceLabel = Tkinter.Label(menuChoiceFrame,
					textvariable=self._menuChoiceLabelVar)
		self._updateMenuChoiceLabel()
		self._menuChoiceLabel.pack()
		self.initialiseoptions(MenuPositionDialog)

	def _menuChoiceCB(self, choice):
		dict = selMgr.selectorDict()
		self.menuTarget = []
		if choice[0] != _mainMenuString:
			for level in choice:
				if dict.has_key(level):
					registrant, dict = dict[level]
					self.menuTarget.append(level)
					continue
				if level == _thisMenuString:
					break

				# must be "new menu"...
				if not hasattr(self, "_newMenuDialog"):
					self._newMenuDialog = Pmw.PromptDialog(
					  entryfield_labelpos='w',
					  label_text='New menu name:',
					  buttons=('Cancel','OK'),
					  defaultbutton='OK',
					  command=self._newMenuDialogCB)
				self._newMenuDialog.activate()

				if len(self.menuTarget) == len(choice):
					# new submenu successfully added
					dict[self.menuTarget[-1]] = (ui, {})
					selMgr.addCategory(ui, self.menuTarget)
					self._menuChoiceCascade.setitems(
					  self.mainGUI._buildMenuChoiceItems(),
					  index=self.menuTarget[0])
					self.mainGUI._updateSelectorsMenu(index=
						self.mainGUI.selectorsMenu
						.getcurselection())
					break

				# new menu cancelled
				self.menuTarget = choice[0:-1]

		self._updateMenuChoiceLabel()

	def _newMenuDialogCB(self, rep):
		self._newMenuDialog.deactivate()
		if rep is None or rep == 'Cancel':
			return
		menuName = string.strip(
				self._newMenuDialog.component('entry').get())
		if menuName == "":
			Pmw.MessageDialog(title='Menu Name Error',
				message_text='Empty menu name').show()
			return
		
		self.menuTarget.append(menuName)

	def _updateMenuChoiceLabel(self):
		label = "Selector under: "
		if len(self.menuTarget) > 2:
			label = label + ".../"
		if len(self.menuTarget) > 1:
			label = label + self.menuTarget[-2] + "/"
		if len(self.menuTarget) > 0:
			label = label + self.menuTarget[-1]
		else:
			label = label + _mainMenuString
		self._menuChoiceLabelVar.set(label)


class CodeItemizedSelection(selection.CodeSelection):
	"""similar to selection.CodeSelection

	differences are that the code local variables are:

		sel -- empty ItemizedSelection
		models -- reference to chimera.openModels
		molecules -- reference to open models that are molecules
	
	and the code is expected to fill in 'sel' with selected items
	"""

	def apply(self, gFunc = None, sFunc = None, vFunc = None, eFunc = None):
		sel = selection.ItemizedSelection()
		sels = []  # used as a stack when selections get composited
		funcGlobals = {
			"__doc__": None,
			"__name__": "CodeItemizedSelection",
			"__builtins__": __builtins__
		}
		funcLocals = {
			"models": openModels.list(),
			"molecules": openModels.list(modelTypes=[Molecule]),
			"sel": sel,
			"sels": sels,
			"selection": selection
		}

		try:
			exec self.codeObj in funcGlobals, funcLocals
		except:
			sys.stderr.write("<ERROR>\n")
			sys.stderr.write(str(self.name())
					+ " CodeItemizedSelection failed\n")
			traceback.print_exc()
			sys.stderr.write("</ERROR>\n")
		sel.apply(gFunc, sFunc, vFunc, eFunc)
