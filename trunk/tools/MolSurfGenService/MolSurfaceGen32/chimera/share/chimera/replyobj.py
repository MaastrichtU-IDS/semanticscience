# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: replyobj.py 29014 2009-10-08 18:30:10Z gregc $

"""
Reply Object -- python interface to manage reply log
"""
import sys
import Tkinter
import tkMessageBox
import statusline
Tk = Tkinter

import chimera
from chimera import baseDialog

# tag names -- normal is not really used as a tag
NORMAL = "Normal"
COMMAND = "Command"
STATUS = "Status"
WARNING = "Warning"
WARN = WARNING
ERROR = "Error"
SHOW_STATUS_LINE = "Show status line"
STATUS_CLEARING = "Clear status line after"

DisplayReplyLog = "reply log only"
DisplayDialog = "dialog"

REPLY_PREFERENCES = "Messages"

origStdout = sys.stdout
origStderr = sys.stderr

replyDialog = None

lastTracebackMsg  = ''
uncaughtExc       = False
helpInfo          = None

class MicrosoftSEDialog(baseDialog.ModalDialog):

	buttons = ("Report Bug", baseDialog.Cancel)
	default = baseDialog.Cancel
	help = "http://www.cgl.ucsf.edu/chimera/graphics/graphicsbugs.html"
	title = 'Chimera Error'

	def fillInUI(self, master):
		self.icon = Tk.Label(master, bitmap="error", width=20)
		self.icon.pack(side=Tk.LEFT)
		self.message = Tk.Label(master, text=
			'\n'
			'error: Microsoft SE exception C0000005\n'
			'\n'
			'This error frequently means that your graphics/video'
			' driver is out-of-date.'
			'  Please verify that you are using the latest driver.'
			'  If you have updated your driver'
			' and are still seeing this bug,'
			' please report it.'
			'\n',
			wraplength=400, justify=Tk.LEFT)
		self.message.pack(fill=Tk.BOTH, expand=Tk.TRUE)
		self.message.bind("<Configure>", self.msgConfig)
		self.reconfig = True

	def msgConfig(self, event):
		if not self.reconfig:
			# only reconfigure once to avoid configure loops
			return
		self.message.config(wraplength=event.width)
		self.reconfig = False

	def ReportBug(self):
		baseDialog.ModalDialog.Cancel(self, value='yes')

class ReplyDialog(baseDialog.ModelessDialog):

	buttons = ("Report Bug", "Open Reply Log", baseDialog.Close)
	default = baseDialog.Close

	def fillInUI(self, master):
		self.icon = Tk.Label(master, bitmap="info", width=20)
		self.icon.pack(side=Tk.LEFT)
		self.message = Tk.Label(master, text="Reply Dialog",
					wraplength=400, justify=Tk.LEFT)
		self.message.pack(fill=Tk.BOTH, expand=Tk.TRUE)
		self.message.bind("<Configure>", self.msgConfig)
		self.reconfig = True

	def msgConfig(self, event):
		if not self.reconfig:
			# only reconfigure once to avoid configure loops
			return
		self.message.config(wraplength=event.width)
		self.reconfig = False

	def setMessage(self, msg):
		self.message.config(text='\n' + msg.strip() + '\n')
		self.reconfig = True

	def setTitle(self, title):
		self.message.winfo_toplevel().title(title)
		self.reconfig = True

	def setIcon(self, icon):
		self.icon.config(bitmap=icon)
		self.reconfig = True

	def OpenReplyLog(self):
		from chimera import dialogs, tkgui
		dialogs.display(tkgui._ReplyDialog.name)
		self.Close()

	def enter(self):
		if uncaughtExc:
			self.buttonWidgets['Report Bug'].pack(anchor='se',
					side='right', padx='1p', pady='4p')
		else:
			self.buttonWidgets['Report Bug'].pack_forget()
		global helpInfo
		if helpInfo:
			self.buttonWidgets['Help'].config(state="normal")
			import help
			help.register(self._toplevel, helpInfo)
		else:
			self.buttonWidgets['Help'].config(state="disabled")
		self.help = helpInfo
		helpInfo = None

		baseDialog.ModelessDialog.enter(self)

	def ReportBug(self):
		if 'Microsoft SE exception C0000005' in lastTracebackMsg:
			yes = MicrosoftSEDialog().run(self._toplevel)
			if not yes:
				return
		import BugReport
		br_gui = BugReport.displayDialog()
		if not br_gui:
			return

		bug_report = BugReport.BugReport(info=lastTracebackMsg)
		br_gui.setBugReport(bug_report)

ModeBitmap = {
	NORMAL:		"info",
	COMMAND:	"info",
	STATUS:		"info",
	WARNING:	"warning",
	ERROR:		"error"
}

def showDialog(title="missing title", message="missing message", mode=NORMAL):
	if not message:
		return
	global replyDialog
	if replyDialog is None:
		replyDialog = ReplyDialog()
	replyDialog.setTitle(title)
	replyDialog.setMessage(message)
	replyDialog.setIcon(ModeBitmap[mode])
	replyDialog.enter()

def registerPreferences():
	import tkoptions
	class ReplyDisplayOption(tkoptions.EnumOption):
		"""Specialization of EnumOption Class for side"""
		values = (DisplayReplyLog, DisplayDialog)
	class StatusClearingOption(tkoptions.SymbolicEnumOption):
		values = [5, 10, 20, 30, 60, 0]
		labels = ["5 seconds", "10 seconds", "20 seconds",
			"30 seconds", "1 minute", "never"]
	ReplyPreferences = {
		SHOW_STATUS_LINE: (tkoptions.BooleanOption, Tk.YES,
				   _showStatusLine),
		STATUS_CLEARING:(StatusClearingOption, 30, None),
		COMMAND:	(ReplyDisplayOption, DisplayReplyLog, None),
		WARNING:	(ReplyDisplayOption, DisplayDialog, None),
		ERROR:		(ReplyDisplayOption, DisplayDialog, None)
	}
	ReplyPreferencesOrder = [
		SHOW_STATUS_LINE, STATUS_CLEARING,
		COMMAND, WARNING, ERROR
	]

	import preferences
	preferences.register(REPLY_PREFERENCES, ReplyPreferences)
	preferences.setOrder(REPLY_PREFERENCES, ReplyPreferencesOrder)

	chimera.triggers.addHandler('status line', _statusLineShownCB, None)

class Reply:
	"""A reply window widget.

	The reply window widget acts like a write-only Python file object.
	Primary usage is through instance methods, but "write" statements
	to the instance can have special meaning.

	Example:
		sys.stdout = Reply(master)

		...
		sys.stdout.write("<ERROR>\n")
		traceback.print_exc()
		sys.stdout.write("</ERROR>\n")
	"""
	encoding = 'utf-8'
	softspace = 0
	tagInfo = {
		NORMAL: {
			"icon": None, "text": None,
			"font": "Helvetica 12", "relief":Tk.FLAT
		},
		COMMAND: {
			"icon": None, "text": None,
			"font": "Helvetica 12", "relief":Tk.RIDGE
		},
		STATUS: {
			"icon": None, "text": None,
			"color": "#3300c3",
			"font": "Helvetica 12", "relief":Tk.FLAT
		},
		WARNING: {
			"icon": None, "text": None,
			"color": "#0033d3",
			"font": "Helvetica 12 italic", "relief":Tk.FLAT
		},
		ERROR: {
			"icon": None, "text": None,
			"color": "#c12300",
			"font": "Helvetica 12 bold", "relief":Tk.FLAT
		}
	}

	def __init__(self, widget):
		# TODO: assert widget is a Text widget
		self._widget = widget
		self._widget.config(state=Tk.DISABLED)
		# TODO: text background is read-only color
		ti = Reply.tagInfo[NORMAL]
		ti["color"] = self._widget["foreground"]
		self._widget.config(font=ti["font"], foreground=ti["color"])
		keys = Reply.tagInfo.keys()
		keys.remove(NORMAL)
		for k in keys:
			ti = Reply.tagInfo[k]
			if not ti.has_key("color"):
				ti["color"] = self._widget["foreground"]
			self._widget.tag_configure(k,
				font=ti["font"], foreground=ti["color"],
				relief=ti["relief"], borderwidth=2)
		self._mode = [ NORMAL ]
		self._messages = []

	def write(self, s):
		"""Write string to reply window.

		widget.write(string) => None
		"""
		if s == "</NORMAL>\n" \
		or s == "</COMMAND>\n" \
		or s == "</STATUS>\n" \
		or s == "</WARNING>\n" \
		or s == "</ERROR>\n":
			self.popMode()
		elif s == "<COMMAND>\n":
			self.pushMode(COMMAND)
		elif s == "<STATUS>\n":
			self.pushMode(STATUS)
		elif s == "<WARNING>\n":
			self.pushMode(WARNING)
		elif s == "<ERROR>\n":
			self.pushMode(ERROR)
		else:
			self.message(s)

	def message(self, s):
		"""Display a message in current message mode"""
		mode = self._mode[0]
		if mode == STATUS:
			self._messages[0].append(s)
			return
		self._widget.config(state=Tk.NORMAL)
		if mode == NORMAL:
			while 1:
				i = s.find('\r')
				if i == -1:
					break
				if i + 1 < len(s) and s[i + 1] == '\n':
					self._widget.insert(Tk.END, s[:i] + '\n')
					s = s[i + 2:]
					continue
				# TODO: would like to overwrite last line
				# instead of deleting it
				self._widget.delete('end-1c linestart', Tk.END)
				self._widget.insert(Tk.END, '\n')
				s = s[i + 1:]
			if s:
				self._widget.insert(Tk.END, s)
		else:
			self._widget.insert(Tk.END, s, mode)
			self._messages[0].append(s)
		self._widget.config(state=Tk.DISABLED)
		self._widget.see(Tk.END)

	def pushMode(self, mode):
		"""Enter a message mode (NORMAL, WARNING, ERROR, etc.)"""
		if mode != NORMAL:
			self._messages.insert(0, [])
		self._mode.insert(0, mode)
		self._setMode(mode)

	def popMode(self, log=0, **kw):
		"""Exit a message mode"""
		if len(self._mode) == 1:
			return
		if self._mode[0] == STATUS:
			if log:
				info("".join(self._messages[0]))
				if 'followWith' not in kw:
					kw['followWith'] = \
				"Previous message also written to reply log\n"
			self._showStatus(**kw)
			del self._messages[0]
		elif self._mode[0] != NORMAL:
			import preferences
			p = preferences.get(REPLY_PREFERENCES, self._mode[0])
			if p == DisplayDialog:
				self._showDialog()
			del self._messages[0]
		del self._mode[0]
		self._setMode(self._mode[0])

	def _setMode(self, mode):
		self._widget.config(state=Tk.NORMAL)
		ti = Reply.tagInfo[mode]
		if ti["icon"]:
			win = Label(self._widget, bitmap=ti["icon"],
					foreground=ti["color"])
			self._widget.window_create(Tk.END, window=win,
					align=TOP, padx=2, pady=2)
			self._widget.tag_add(mode, 'end - 2c', 'end - 1c')
		if ti["text"]:
			self._widget.insert(Tk.END, ti["text"], mode)
		if ti["icon"] or ti["text"]:
			self._widget.insert(Tk.END, '\n')
		self._widget.config(state=Tk.DISABLED)

	def _showDialog(self):
		showDialog(title="Chimera %s" % self._mode[0],
				message="".join(self._messages[0]),
				mode=self._mode[0])

	def _showStatus(self, **kw):
		msg = "".join(self._messages[0])
		statusline.show_message(msg, **kw)

	def clear(self):
		"""Clear contents of reply window.

		widget.clear() => None
		"""
		if hasattr(self._widget, 'clear'):
			self._widget.clear()
		else:
			self._widget.config(state=Tk.NORMAL)
			self._widget.delete(1.0, Tk.END)
			self._widget.config(state=Tk.DISABLED)

	def flush(self):
		"""Flush output to reply window.

		widget.flush() => None
		"""
		self._widget.update_idletasks()

	def command(self, s):
		"""Log a command string"""
		self.pushMode(COMMAND)
		self.message(s)
		self.popMode()

	def status(self, s, **kw):
		"""Log a status string"""
		self.pushMode(STATUS)
		self.message(s)
		self.popMode(**kw)

	def info(self, s):
		"""Log an informational message"""
		self.pushMode(NORMAL)
		self.message(s)
		self.popMode()

	def warning(self, s):
		"""Log a warning string"""
		self.pushMode(WARNING)
		self.message(s)
		self.popMode()

	def error(self, s):
		"""Log an error string"""
		self.pushMode(ERROR)
		self.message(s)
		self.popMode()

class SplashReply:
	"""A splash window status widget.

	The splay reply window widget updates a label widget with
	status messages.
	"""
	# Currently, we expect that sys.stdout and sys.stderr are not
	# redirected to us, so we can print to them.
	# TODO: save stdout and stderr output and display it when the
	# SplashReply is removed.
	def __init__(self, widget):
		self.widget = widget

	def write(self, s):
		"""Write string to reply window."""
		sys.stdout.write(s)

	def message(self, s):
		"""Display a message in current message mode"""
		sys.stdout.write(s)

	def pushMode(self, mode):
		"""Enter a message mode (NORMAL, WARNING, ERROR, etc.)"""
		pass

	def popMode(self):
		"""Exit a message mode"""
		pass

	def clear(self):
		"""Clear contents of reply window."""
		if hasattr(self.widget, 'clear'):
			self.widget.clear()
		else:
			self.widget.config(text="")

	def flush(self):
		"""Flush output to reply window."""
		self.widget.update_idletasks()

	def command(self, s):
		"""Log a command string"""
		sys.stdout.write(s)

	def status(self, s, **kw):
		"""Log a status string"""
		if chimera.debug:
			sys.stderr.write(s)
			sys.stderr.write('\n')
		self.widget.config(text=s)
		self.flush()

	def info(self, s):
		"""Log an informational message"""
		self.widget.config(text=s)

	def warning(self, s):
		"""Log a warning string"""
		sys.stderr.write(s)

	def error(self, s):
		"""Log an error string"""
		sys.stderr.write(s)

def nogui_pushMode(mode):
	"""Enter a message mode"""
	pass

def nogui_popMode():
	"""Exit a message mode"""
	pass

def nogui_message(s):
	"""Show a message"""
	if not chimera.silent:
		sys.stdout.write(s)

def nogui_command(s):
	"""Log a command string"""
	if not chimera.silent:
		sys.stdout.write(s)

def nogui_status(s, **kw):
	"""Log a status string"""
	if not chimera.nostatus:
		sys.stdout.write(s)

def nogui_info(s):
	"""Log an informational message"""
	if not chimera.silent:
		sys.stdout.write(s)

def nogui_warning(s):
	"""Log a warning string"""
	if not chimera.silent:
		sys.stdout.write(s)

def nogui_error(s):
	"""Log an error string"""
	sys.stdout.flush()
	sys.stderr.write(s)

def nogui_clear():
	"""Clear output window"""
	pass

def _showStatusLine(option):
	statusline.show_status_line(option.get())

def _statusLineShownCB(trigName, x, shown):
	import preferences
	preferences.set(REPLY_PREFERENCES, SHOW_STATUS_LINE, shown)

def noop(*args, **kw):
	pass

def _setFunctions(reply):
	global pushMode
	global popMode
	global message
	global command
	global status
	global info
	global warning
	global error
	global clear
	def wrapped(rawFunc):
		def x(msg, func=rawFunc, help=None):
			global helpInfo
			helpInfo = help
			func(msg)
		return x
			
	if reply:
		pushMode = reply.pushMode
		popMode = reply.popMode
		message = reply.message
		command = reply.command
		if chimera.nostatus:
			status = noop
		else:
			if not statusline.status_line():
				status = reply.status
		if chimera.silent:
			info = noop
			warning = noop
		else:
			info = wrapped(reply.info)
			warning = wrapped(reply.warning)
		error = wrapped(reply.error)
		clear = reply.clear
	else:
		pushMode = nogui_pushMode
		popMode = nogui_popMode
		message = nogui_message
		command = nogui_command
		if chimera.nostatus:
			status = noop
		else:
			if not statusline.status_line():
				status = nogui_status
		if chimera.silent:
			info = noop
			warning = noop
		else:
			info = wrapped(nogui_info)
			warning = wrapped(nogui_warning)
		error = wrapped(nogui_error)
		clear = nogui_clear

_replyStack = []
_setFunctions(None)

class ReplyItem:
	def __init__(self, reply, stdout, stderr):
		self.reply = reply
		self.stdout = stdout
		self.stderr = stderr

def pushReply(reply, takeStdout=1, takeStderr=1):
	_setFunctions(reply)
	if takeStdout:
		if reply:
			sys.stdout = reply
		else:
			sys.stdout = origStdout
	if takeStderr:
		if reply:
			sys.stderr = reply
		else:
			sys.stderr = origStderr
	s = ReplyItem(reply, takeStdout and sys.stdout,
			takeStderr and sys.stderr)
	_replyStack.insert(0, s)
	return s

def popReply(stackObj):
	global origStdout, origStderr
	if not _replyStack:
		raise IndexError, 'no reply object on stack'
	n = _replyStack.index(stackObj)
	del _replyStack[n]
	if not _replyStack:
		# Popped off only item
		_setFunctions(None)
		sys.stdout = origStdout
		sys.stderr = origStderr
		return
	for replyItem in _replyStack:
		if replyItem.stdout is stackObj.reply:
			replyItem.stdout = None
		if replyItem.stderr is stackObj.reply:
			replyItem.stderr = None

	if n == 0:
		_setFunctions(_replyStack[0].reply)
	for replyItem in _replyStack:
		if replyItem.stdout:
			sys.stdout = replyItem.stdout
			break
	else:
		sys.stdout = origStdout
	for replyItem in _replyStack:
		if replyItem.stderr:
			sys.stderr = replyItem.stderr
			break
	else:
		sys.stderr = origStderr

def clearReplyStack():
	while _replyStack:
		popReply(_replyStack[0])

def reportException(description=None, fullDescription=None):
	"""Report the current exception, prepending 'description'.

	A 'fullDescription' overrides the description and traceback
	information."""

	from chimera import NotABug, CancelOperation
	from traceback import format_exception_only, format_exception, format_tb
	ei = sys.exc_info()
	if description:
		preface = "%s:\n" % description
	else:
		preface = ""

	exception_type  = ei[0]
	exception_value = ei[1]

	if isinstance(exception_value, NotABug):
		error(u"%s%s\n" % (preface, exception_value))
	elif isinstance(exception_value, CancelOperation):
		pass	# Cancelled operations are not reported.
	else:
		global uncaughtExc
		uncaughtExc=True

		if fullDescription:
			tb_msg = fullDescription
		else:
			tb = format_exception(ei[0], ei[1], ei[2])
			tb_msg = "".join(tb)
			message(tb_msg)
		global lastTracebackMsg
		lastTracebackMsg=tb_msg

		if fullDescription:
			error(fullDescription)
		else:
			err = "".join(format_exception_only(ei[0], ei[1]))
			loc = ''.join(format_tb(ei[2])[-1:])
			error(u'%s%s\n%s\n' % (preface, err, loc)
				+ u"See reply log for Python traceback.\n\n")
		uncaughtExc=False

def handlePdbErrs(identifyAs, errs):
	prep = "The following problems occurred while reading PDB file for %s"\
							% identifyAs
	info("\n".join([prep, errs]))

class PdbErrsDialog(baseDialog.ModelessDialog):
	oneshot = True
	title = "Errors in PDB File"
	buttons = ('OK',)
	
	def __init__(self, prep, errs):
		self.info = (prep, errs)
		baseDialog.ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		prep, errs = self.info
		import Tkinter, Pmw
		Tkinter.Label(parent, text=prep).grid(row=0)
		scrolled = Pmw.ScrolledText(parent)
		scrolled.settext(errs)
		scrolled.component('text').configure(state='disabled')
		scrolled.grid(row=1, sticky='nsew')

