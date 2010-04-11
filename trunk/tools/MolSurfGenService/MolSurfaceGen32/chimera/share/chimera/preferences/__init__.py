import os
import chimera
from chimera import tkoptions
from base import Preferences, Category, Option, HiddenCategory

PreferenceFile = 'preferences'

#
# Create Preferences singleton instance and add some
# global functions for backwards compatibility
#
preferences = Preferences()
setFilename = preferences.setFilename
setReadonly = preferences.setReadonly
load = preferences.load
save = preferences.save
makeCurrentSaved = preferences.makeCurrentSaved
register = preferences.register
deregister = preferences.deregister
set = preferences.set
get = preferences.get
getOption = preferences.getOption
setOrder = preferences.setOrder
addCategory = preferences.addCategory

#
# Find a preferences file and load it
#
if chimera.preferencesFile is not None:
	pf = None
	if os.access(chimera.preferencesFile, os.R_OK):
		filename = chimera.preferencesFile
		preferences.load(filename)
	else:
		from chimera import replyobj
		replyobj.error("File \"%s\" is not readable\n" %
				chimera.preferencesFile)
		filename = None
else:
	pf = chimera.pathFinder()
	files = pf.allExistingFiles("", PreferenceFile)
	if files:
		for filename in files:
			try:
				preferences.load(filename)
			except IOError:
				continue
			except Exception, e:
				from chimera import replyobj
				replyobj.error(
					'%s: %s.\n'
					'Using factory default preference '
					'settings.\n'
					'The settings in the current '
					'preferences file cannot be\n'
					'applied until the file has been '
					'repaired and Chimera restarted.\n' %
					(filename, e))
				preferences.setReadonly(True)
				break
			else:
				break
	else:
		filename = None
	del files

#
# If no preferences file was found, we try to find
# a writable directory and put the preferences
# file there
#

def _canWrite(path):
	while path:
		if os.access(path, os.W_OK):
			return 1
		if os.path.exists(path):
			return 0
		newPath = os.path.dirname(path)
		if newPath == path:
			break
		else:
			path = newPath
	return 0

if filename:
	if not preferences.isReadonly() and not _canWrite(filename):
		preferences.setReadonly(True)
		def f(filename=filename):
			from chimera import replyobj
			replyobj.warning('Using read-only preferences file.  '
					'Change access permission for "%s" '
					'to enable saving preferences.\n'
					% filename)
		chimera.registerPostGraphicsFunc(f)
else:
	if pf is None:
		pf = chimera.pathFinder()
	pList = pf.pathList("", PreferenceFile, 0, pf.packageDotDefault,
				pf.packageHomeDefault)
	pList.reverse()
	for p in pList:
		if _canWrite(p):
			filename = os.path.normpath(p)
			break

if filename:
	preferences.setFilename(os.path.realpath(filename))

#
# Create a category in preferences so user can
# reset/restore preferences
#

class _PrefFileOption(tkoptions.Option):
	"""Specialization for immutable preferences file name"""
	def _addOption(self, row, col, **kw):
		import Tkinter
		opts = {
			'relief': Tkinter.GROOVE,
			'borderwidth': 2,
			'anchor': Tkinter.W,
		}
		if self._label:
			opts['width'] = 10
		opts.update(kw)
		self._option = Tkinter.Label(self._master, **opts)
		if row == -1:
			if self._label:
				self._option.pack(side=Tkinter.RIGHT)
			else:
				self._option.pack(fill=Tkinter.X)
		else:
			self._option.grid(row=row, column=col, sticky='ew')

	def set(self, value):
		self._option.config(text=value)


PREF_LOCATION = 'Preferences file'
PREF_READONLY = 'Read-only'
PREF_RESTORE  = 'Restore to saved settings'
PREF_RESET    = 'Reset to factory defaults'
PREF_SAVE     = 'Save'

class _PrefCategory(Category):
	def __init__(self, master=None, *args, **kw):
		from chimera.tkoptions import BooleanOption
		Category.__init__(self, master, *args, **kw)
		
		showName = preferences.filename()
		if showName is None:
			showName = "[ No writable preferences file ]"
		readonly = preferences.isReadonly()
		self._options = {
			# last argument to Option is:
			#	[ tkoption, display name, dialog callback ]
                        PREF_LOCATION: Option(self, showName, None,
					      [_PrefFileOption, PREF_LOCATION,
					      None]),
                        PREF_READONLY: Option(self, readonly, self._readonlyCB,
					      [BooleanOption, PREF_READONLY,
					      None]),
			}

	def load(self, *args, **kw):
		"preferences location is not loaded"
		pass

	def save(self, *args, **kw):
		"preferences location is not saved"
		pass
	
	def ui(self, master):
		if self._ui:
			return self._ui

		import Tkinter
		self._ui = Tkinter.Frame(master)

		self.log_state = self._add_opt(PREF_LOCATION, self._ui, 0)
		self.readonly = self._add_opt(PREF_READONLY, self._ui, 1)

		self.restore_button = Tkinter.Button(self._ui, text=PREF_RESTORE,
						     command = self.restoreAll )
		self.reset_button   = Tkinter.Button(self._ui, text=PREF_RESET,
						     command = self.resetAll )
		self.save_button    = Tkinter.Button(self._ui, text=PREF_SAVE,
						     command = self.saveAll )
		self.actions_lbl    = Tkinter.Label(self._ui, text="All categories: ")

		Tkinter.Frame(self._ui, height=10).grid(row=2, column=0, sticky='ew')
		self.restore_button.grid(row=3, column=1, sticky='w')
		self.actions_lbl.grid(row=3,column=0,sticky = 'e')
		self.reset_button.grid(row=4,column=1, sticky='w')
		self.save_button.grid(row=5, column=1, sticky='w')
		
		self._ui.columnconfigure(1, weight=1)
		self._ui.rowconfigure(0, weight=1)
		self._ui.rowconfigure(1, weight=1)
		self._ui.rowconfigure(2, weight=2)
		self._ui.rowconfigure(3, weight=1)
		self._ui.rowconfigure(4, weight=1)
		self._ui.rowconfigure(5, weight=1)
		return self._ui

	def restoreAll(self):
		""" to last save """
		preferences._uiPanel.RestoreAll()
	def resetAll(self):
		""" to factory defaults """
		preferences._uiPanel.ResetAll()
	def saveAll(self):
		""" save all """
		preferences._uiPanel.SaveAll()

	def _add_opt(self, attribute, master, row):
		opt = self._options[attribute]
		closure = opt.closure()
		def cb(tkopt, o=opt, tkcb=closure[2]):
			o.set(tkopt.get())
			if tkcb:
				tkcb(tkopt)
		initialValue = opt.get()
		if closure[1] is not None:
			name = closure[1]
		else:
			name = attribute
		tkOpt = closure[0](master, row, name, opt.defaultValue(), cb,
			attribute=attribute, **opt.UIkw())
		tkOpt.set(initialValue)
		opt.setUI(tkOpt)
		return tkOpt

	def _readonlyCB(self, opt):
		prefFile = preferences.filename()
		if not prefFile:
			# If no file name, changes make no difference.
			return
		newState = opt.get()
		if ((newState and preferences.isReadonly())
		or (not newState and not preferences.isReadonly())):
			# No change in state
			return
		if newState:
			# Make readonly.  This is always okay.
			preferences.setReadonly(True)
		else:
			# Make not readonly.  See if the file is
			# writable.  If not, ask the user if he wants
			# to change permission.
			if not _canWrite(prefFile):
				from chimera.baseDialog import AskYesNoDialog
				d = AskYesNoDialog("File is not writable."
						"  Try changing permissions?")
				answer = d.run(self._ui)
				if answer == "no":
					opt.ui().set(1)
					return
				try:
					sbuf = os.stat(prefFile)
					import stat
					mode = sbuf.st_mode | stat.S_IWRITE
					os.chmod(prefFile, mode)
				except os.error, s:
					opt.ui().set(1)
					raise chimera.UserError(
							"cannot make %s "
							"writable: %s" %
							(prefFile, s))
			preferences.setReadonly(False)

	def add(self, name, defaultValue, callback, closure, notifyUI=1):
		raise RuntimeError, "not applicable"
	def remove(self, name, notifyUI=1):
		raise RuntimeError, "not applicable"
	def destroy(self, notifyUI=1):
		raise RuntimeError, "not applicable"
	def _destroyUI(self, notifyUI):
		raise RuntimeError, "not applicable"	
		
preferencesCategory = preferences.addCategory('Preferences', _PrefCategory)

#
# If in GUI mode, register a function for creating
# the UI panel
#
def showPreferencesPanel():
	from panel import PreferencesPanel
	return PreferencesPanel(preferences)
def registerPanel():
	from panel import PreferencesPanel
	chimera.dialogs.register(PreferencesPanel.name, showPreferencesPanel)

#
# Clean up temporaries
#
del pf
del filename


#
# Testing code below
#
def test():
	from chimera import tkoptions
	from chimera.tkgui import app

	GENERAL = "General"
	CONFIRM_EXIT = "Confirm exit"
	SHOW_REPLIES = "Show replies at startup"
	TOOLBAR_SIDE = "Toolbar side"
	TOOLBAR_VISIBLE = "Toolbar visible"
	BALLOON_HELP = "Show balloon help"

	order = [
			CONFIRM_EXIT, BALLOON_HELP, SHOW_REPLIES
		]
	generalPreferences = {
		BALLOON_HELP:
			(tkoptions.BooleanOption, 1,
					lambda o, a=app: a._setBalloon(o)),
		SHOW_REPLIES:
			(tkoptions.BooleanOption, 0, None),
		CONFIRM_EXIT:
			(tkoptions.BooleanOption, 1, None),
	}
	register(GENERAL, generalPreferences)
	preferences.setOrder(GENERAL, order)

	class _MouseCategory(Category):
		"Mouse modes category has its own interface"

		def ui(self, master):
			if self._ui:
				return self._ui
			import Tkinter
			self._ui = Tkinter.Frame(master)
			from chimera import mousemodes
			mousemodes.MouseTable(self._ui)
			return self._ui

		def buttons(self, buttons, modifiers):
			self._buttons = buttons
			self._modifiers = modifiers

		def load(self, optDict, notifyUI=1):
			from chimera import mousemodes
			for (b, m), f in optDict.items():
				mousemodes.setFunction(b, m, f)
			if notifyUI:
				self._pref.notifyUI()

		def save(self):
			optDict = {}
			for b in self._buttons:
				self._saveButton(optDict, b, (),
							self._modifiers)
			return optDict

		def _saveButton(self, optDict, button, modifiers, remainder):
			from chimera import mousemodes
			if not remainder:
				f = mousemodes.getFunction(button, modifiers)
				optDict[(button, modifiers)] = f
				return
			self._saveButton(optDict, button,
						modifiers,
						remainder[1:])
			self._saveButton(optDict, button,
						modifiers + (remainder[0],),
						remainder[1:])

	cat = preferences.addCategory('Mouse', _MouseCategory)
	cat.buttons(('1', '2', '3'), ('Ctrl',))

#if not chimera.nogui:
#	test()
