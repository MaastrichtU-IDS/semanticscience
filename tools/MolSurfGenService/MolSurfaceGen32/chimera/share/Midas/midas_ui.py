# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: midas_ui.py 28946 2009-10-02 21:44:22Z goddard $

import chimera
import Tkinter
import Pmw
import os
from chimera import help
from chimera.baseDialog import ModelessDialog
from OpenSave import SaveModeless
from chimera import preferences, tkoptions, selection
import Midas
import time
import midas_text
from chimera.oslParser import OSLSyntaxError

ui = None
uiActive = 0

STARTUP_FILES = "Files to read at startup"
SES_MEMORY = "Number of commands to\nremember between sessions"
MIDAS_CATEGORY = "Command Line"
preferences.register(MIDAS_CATEGORY, {
	STARTUP_FILES: (tkoptions.OrderedFileListOption,
		["~/.chimera/midasrc", ".chmidasrc"], None, {'height': 4}),
	SES_MEMORY: (tkoptions.IntOption, 60, None, {'min': 0})
}, aliases=["Midas"])

PREV_COMMANDS = "remembered commands"
prefs = preferences.addCategory("command line gui", preferences.HiddenCategory,
					optDict={PREV_COMMANDS: []})

triggerName = "typed Midas command"
chimera.triggers.addTrigger(triggerName)

class MidasUI:
	"Class for presenting a Midas command line"

	recordLabel = "Command History..."
	hideLabel = "Hide Command Line"

	def __init__(self):
		from chimera import tkgui
		self.frame = Tkinter.Frame(tkgui.app)
		self.frame.columnconfigure(1, weight=1)
		help.register(self.frame,
				"UsersGuide/chimerawindow.html#emulator")

		sep = Tkinter.Frame(self.frame, relief='sunken', bd=2)
		sep.grid(row=0, column=0, columnspan=3, sticky='ew')

		self.histDialog = HistoryDialog(self)
		listbox = self.histDialog.listbox.component('listbox')
		import tkFont
		font = tkFont.Font(font=listbox.cget('font'))
		pixels = font.metrics('linespace')
		self.cmd = Pmw.ComboBox(self.frame, fliparrow=True,
			history=False, labelpos='w', label_text="Command:",
			listheight=10*(pixels+4), entry_exportselection=False,
			selectioncommand=self._selCmdCB,
			scrolledlist_items=[self.recordLabel, self.hideLabel])
		self.cmd.grid(row=1, column=0, columnspan=3, sticky='ew')
		self.histDialog.populate()

		chimera.tkgui.addKeyboardFunc(self.graphicsKeyboardCB)

		entry = self.cmd.component('entry')
		entry.bind('<Up>', self.histDialog.up)
		entry.bind('<Control-p>', self.histDialog.up)
		entry.bind('<Down>', self.histDialog.down)
		entry.bind('<Control-n>', self.histDialog.down)
		entry.bind('<Map>', self.monitorSel)
		entry.bind('<Unmap>', self.unmonitorSel)
		entry.bind('<Control-u>', self.cmdClear)
		entry.bind('<Return>', self.processCommand)

		self.vars = []
		self.buttons = []
		buttonFrame = Tkinter.Frame(self.frame)
		buttonFrame.grid(row=2, column=0, columnspan=3, sticky='ew')
		Tkinter.Label(buttonFrame, text="Active models: ").pack(
								side='left')
		for id in range(10):
			state = 'disabled'
			active = 0
			models = chimera.openModels.list(id)
			models = filter(lambda m: not isinstance(m,
					chimera.PseudoBondGroup), models)
			if models:
				state = 'normal'
				if models[0].openState.active:
					active = 1

			var = Tkinter.IntVar(self.frame)
			self.vars.append(var)
			var.set(active)
			selButton = Tkinter.Checkbutton(buttonFrame,
				variable=var, state=state, text="%d" % id,
				command=lambda x=id, s=self: s.selButtonPush(x))
			selButton.pack(side='left')
			self.buttons.append(selButton)
		self.allVar = Tkinter.IntVar(self.frame)
		self.allVar.set(0)
		self.allButton = Tkinter.Checkbutton(buttonFrame, text="All",
			variable=self.allVar, command=self.allButtonPush)
		self.allButton.pack(side='left')
			
		chimera.triggers.addHandler('OpenState', self.activeHandler,
									None)
		chimera.triggers.addHandler('OpenModels', self.activeHandler,
									None)

		self.show()

		# read startup files
		global ui
		ui = self
		for sf in preferences.get(MIDAS_CATEGORY, STARTUP_FILES):
			from OpenSave import tildeExpand
			sf = tildeExpand(sf)
			if os.path.exists(sf):
				midas_text.message(
				   "Processing Midas start-up file %s" % sf)
				midas_text.processCommandFile(sf)

	def graphicsKeyboardCB(self, event):
		cmd = self.cmd.component('entry')
		index = cmd.index
		char = event.char
		if not char:
			sym = event.keysym
			if sym == "Up":
				self.histDialog.up()
			elif sym == "Down":
				self.histDialog.down()
			elif sym == "Left":
				cmd.icursor(index("insert")-1)
			elif sym == "Right":
				cmd.icursor(index("insert")+1)
			else:
				return
		elif char == '\r':
			self.processCommand(None)
		elif char == '\b':
			if cmd.selection_present():
				cmd.delete(index("sel.first"),
							index("sel.last"))
			else:
				cmd.delete(index("insert")-1)
		elif char == '\016': # control-n
			self.histDialog.down()
		elif char == '\020': # control-p
			self.histDialog.up()
		else:
			if cmd.selection_present():
				cmd.delete(index("sel.first"),
							index("sel.last"))
			cmd.insert("insert", char)
		cmd.focus()

	def activeHandler(self, triggerName, myData, trigData):
		if 'active change' not in trigData.reasons \
		and 'model list change' not in trigData.reasons:
			return
		models = chimera.openModels.list()
		visited = {}
		for model in models:
			if visited.has_key(model.id) \
			or model.id not in range(10) \
			or isinstance(model, chimera.PseudoBondGroup):
				continue
			visited[model.id] = ()
			self.buttons[model.id]['state'] = 'normal'
			self.vars[model.id].set(model.openState.active)
		for id in range(10):
			if visited.has_key(id):
				continue
			self.vars[id].set(0)
			self.buttons[id]['state'] = 'disabled'

	def allButtonPush(self):
		from midas_text import allModelSelect
		if self.allVar.get():
			allModelSelect(True, ids="all")
		else:
			allModelSelect(False, ids="all")
				
	def selButtonPush(self, which):
		# used to just emulate 'select' command, but select won't
		# operate on non-molecule models, so changed it.
		from midas_text import allModelSelect
		allModelSelect(self.vars[which].get() == 1, id=which)

	def hide(self):
		global uiActive
		if not uiActive:
			return
		uiActive = 0
		self.frame.pack_forget()

	def show(self):
		global uiActive
		if uiActive:
			return
		uiActive = 1
		from chimera import tkgui
		self.frame.pack(expand=False, side='bottom', fill='x',
						before=tkgui.app.toolbar)
		self.cmd.component('entry').focus()

	def monitorSel(self, event):
		self._msHandler = chimera.triggers.addHandler(
				"selection changed", self._selChanged, None)

	def unmonitorSel(self, event):
		chimera.triggers.deleteHandler("selection changed",
							self._msHandler)

	def _selChanged(self, trigName, myData, trigData):
		ats = selection.currentAtoms()
		if len(ats) != 1:
			return
		entry = self.cmd.component('entry')
		text = entry.get()
		pre = True
		for i in range(len(text)):
			c = text[i]
			if c == '+' and pre and (i == len(text)-1
							or text[i+1].isspace()):
				break
			pre = c.isspace()
		else:
			return
		entry.delete(i)
		entry.insert(i, ats[0].oslIdent())

	def _selCmdCB(self, sel):
		if sel == self.recordLabel:
			self.histDialog.enter()
			self.cmd.setentry("")
		elif sel == self.hideLabel:
			self.hide()
			self.cmd.setentry("")

	def processCommand(self, event):
		self.cmd.selection_range('0', 'end')
		text = self.cmd.get()
		midas_text.clearError()

		self.histDialog.add(text)
		try:
			midas_text.makeCommand(text)
			chimera.triggers.activateTrigger(triggerName, text)
		except (Midas.MidasError, OSLSyntaxError), v:
			# when Python 2.5.3 is out, replace the workaround
			# below with:
			# midas_text.error(unicode(v))
			midas_text.error(unicode(v.message).encode('utf-8'))

	def cmdClear(self, event=None):
		self.cmd.component('entry').delete('0', 'end')

	def cmdReplace(self, cmd):
		entry = self.cmd.component('entry')
		entry.delete('0', 'end')
		entry.insert('0', cmd)

class HistoryDialog(ModelessDialog):
	title = "Command History"
	buttons = ("Record...", "Execute", "Delete", "Close")
	help = "UsersGuide/history.html"

	def __init__(self, controller):
		# make dialog hidden initially
		self.controller = controller
		ModelessDialog.__init__(self)
		self.Close()

	def fillInUI(self, parent):
		self.listbox = Pmw.ScrolledListBox(parent,
				dblclickcommand= self.execute,
				selectioncommand=self.select,
				listbox_exportselection=0,
				listbox_selectmode='extended')
		self.listbox.pack(expand='yes', fill='both')
		self.listbox.select_set('end')
		self.recordDialog = None

	def _focusCB(self, event=None):
		self.controller.cmd.focus()
		self._toplevel.tkraise()

	def add(self, item):
		self.listbox.insert('end', item)
		self.listbox.see('end')
		self.listbox.select_clear(0, 'end')
		self.listbox.select_set('end')
		commands = list(self.listbox.get())
		last9 = commands[-9:]
		last9.reverse()
		c = self.controller
		c.cmd.setlist(last9+[c.recordLabel, c.hideLabel])
		numRemember = preferences.get(MIDAS_CATEGORY, SES_MEMORY)
		if numRemember:
			prefs[PREV_COMMANDS] = commands[-numRemember:]
		else:
			prefs[PREV_COMMANDS] = []

	def populate(self):
		# not done during __init__ to avoid callback to ComboBox
		# which hasn't been initialized yet (uses our font metrics!)
		prevCommands = prefs[PREV_COMMANDS]
		self.listbox.setlist(prevCommands)
		self.listbox.select_set('end')
		self.select()
		self.controller.cmd.selection_range('0', 'end')
		last9 = prevCommands[-9:]
		last9.reverse()
		c = self.controller
		c.cmd.setlist(last9+[c.recordLabel, c.hideLabel])
		cursel = self.listbox.curselection()
		if cursel:
			self.listbox.see(cursel)

	def select(self):
		sels = self.listbox.getcurselection()
		if len(sels) != 1:
			return
		self.controller.cmdReplace(sels[0])

	def delete(self):
		sel = set([int(i) for i in self.listbox.curselection()])
		prevCommands = prefs[PREV_COMMANDS]
		prefs[PREV_COMMANDS] = [prevCommands[i]
			for i in range(len(prevCommands)) if i not in sel]
		self.populate()

	Delete = delete

	def execute(self):
		for cmd in self.listbox.getcurselection():
			self.controller.cmdReplace(cmd)
			self.controller.processCommand(None)

	Execute = execute

	def record(self):
		if not self.recordDialog:
			self.recordDialog = RecordDialog(self)
		self.recordDialog.enter()

	Record = record

	def up(self, event=None):
		sels = self.listbox.curselection()
		if len(sels) != 1:
			return
		sel = sels[0]
		if isinstance(sel, basestring):
			sel = int(sel)
		if sel == 0:
			return
		self.listbox.select_clear(0, 'end')
		self.listbox.select_set(sel - 1)
		self.controller.cmdReplace(self.listbox.get(sel - 1))

	def down(self, event=None):
		sels = self.listbox.curselection()
		if len(sels) != 1:
			return
		sel = sels[0]
		if isinstance(sel, basestring):
			sel = int(sel)
		if sel == self.listbox.index('end') - 1:
			return
		self.listbox.select_clear(0, 'end')
		self.listbox.select_set(sel + 1)
		self.controller.cmdReplace(self.listbox.get(sel + 1))

class RecordDialog(SaveModeless):
	title = "Command Recording"
	buttons = ("OK", "Cancel")

	def __init__(self, histDialog):
		# make dialog hidden initially
		self.histDialog = histDialog
		SaveModeless.__init__(self, clientPos='s', clientSticky="ew",
						initialfile="chimera.cmd")

	def fillInUI(self, parent):
		SaveModeless.fillInUI(self, parent)
		self.clientArea.columnconfigure(0, weight=1)
		self.clientArea.columnconfigure(1, weight=1)
		self.amount = Pmw.RadioSelect(self.clientArea,
			orient='vertical', buttontype='radiobutton',
			labelpos='w', pady=0, label_text="Record")
		self.amount.add("selected commands")
		self.amount.add("all commands")
		self.amount.invoke(1)
		self.amount.grid(row=0, column=0)
		self.commandStyle = Pmw.RadioSelect(self.clientArea,
			orient='vertical', command=self._adjustFileName,
			buttontype='radiobutton', labelpos='w', pady=0,
			label_text="Record as")
		self.commandStyle.add("Chimera commands")
		self.commandStyle.add("Python commands")
		self.commandStyle.invoke(0)
		self.commandStyle.grid(row=1, column=0)
		self.appending = Tkinter.IntVar(parent)
		self.appending.set(0)
		Tkinter.Checkbutton(self.clientArea, variable=self.appending,
			text="Append to file").grid(row=0, column=1, rowspan=2)

	def Apply(self, event=None):
		paths = self.getPaths()
		if not paths:
			raise ValueError, "No filename given for recording"
		fname = paths[0]
		if self.appending.get():
			mode = "a"
		else:
			mode = "w"
		from OpenSave import osOpen
		file = osOpen(fname, mode)
		writePython = self.commandStyle.getvalue()[:6]=="Python"
		if writePython:
			file.write("from chimera import runCommand\n")
		if self.amount.getvalue()[:3] == "all":
			cmds = self.histDialog.listbox.get()
		else:
			cmds = self.histDialog.listbox.getvalue()
		for cmd in cmds:
			if writePython:
				file.write("runCommand(" + repr(cmd) + ")\n")
			else:
				file.write(cmd + "\n")
		file.close()

	def _adjustFileName(self, butName):
		if butName == "Chimera commands":
			want = ".cmd"
			alt = ".py"
		else:
			want = ".py"
			alt = ".cmd"
		entered = self.millerBrowser.fileFaves.get().strip()
		if entered.endswith(alt):
			new = entered[:0-len(alt)] + want
			self.millerBrowser.fileFaves.component(
						'entryfield').setentry(new)

def createUI():
	global ui
	if ui:
		ui.show()
	else:
		MidasUI()

def hideUI():
	if ui:
		ui.hide()
