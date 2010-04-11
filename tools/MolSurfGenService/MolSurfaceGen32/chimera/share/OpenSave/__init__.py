# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29504 2009-12-02 22:02:54Z pett $

"""Standard open/save panels for Chimera

   The classes that are designed for developer use are SaveModal, SaveModeless,
   OpenModal, and OpenModeless.  Initializer keywords that aren't directly
   understood by these classes are passed on to the initializer of the 
   MillerBrowser (self.millerBrowser).  See the MillerBrowser class (in
   miller.py) for documentation on those keywords.  The 'parent',
   'fileEntryCommand', 'style', and 'readyCommand' keywords of the
   MillerBrowser should never be supplied by the developer as the open/save
   classes supply these.

   If the developer doesn't explicitly supply values for the 'addAll' or
   'multiple' keywords, then the dialog will supply a value.  For open
   dialogs, addAll and multiple will be true, whereas for save dialogs
   they will be false.

   If the developer needs to place additional widgets in the dialog, then
   they should supply a 'clientPos' keyword specifying what side of the 
   dialog to place the widgets ('n', 's', 'e', or 'w').  If 'clientPos'
   is specified, a Frame will be placed on the appropriate side of the
   dialog (self.clientArea) with the grid() method and a "stickiness"
   given by the 'clientSticky' keyword (if provided).  The developer
   should populate the client area by overriding the 'fillInUI' method,
   calling the parent fillInUI() method and then creating widgets with
   self.clientArea as a parent.
   
   The 'command' keyword can be used to supply a function to call when 'Apply',
   'OK', or 'Close' are invoked in Modeless dialogs.  The two arguments
   given to the function are a boolean and the dialog instance.  The boolean
   is 1 if 'Apply' or 'OK' were chosen, 0 otherwise.  It is expected that if
   'command' is supplied, then the developer will not be overriding the
   Apply method.

   The 'title' keyword allows the developer to supply a title without having
   to subclass.  The subclassing method still works (though the keyword has
   precedence if supplied).  Similarly, the 'help' keyword can provide a
   help URL if something other than the generic open/save help is desired.

   In open dialogs, the 'sample' keyword (or self.sample class attribute)
   allows a path to a directory containing sample data to be specified.
   If 'sample' is provided, a "Sample" button will be added to the dialog.

   The "public" MillerBrowser methods are accepted by the dialog instance
   directly and forwarded to self.millerBrowser.  They are:

	setPath getPaths getPathsAndTypes getFilter setFilter addFilter
	rememberDir rememberFile
   [see MillerBrowser class for more info]

   The most frequently used of these is 'getPaths'/'getPathsAndTypes'
   to find out the path name(s) chosen by the user.

   These paths should be opened with this module's osOpen function, which
   will handle compressed files transparently.  Check the osOpen function's
   doc string for details on it's use.

   The 'extraButtons' (sub)class attribute can be used to obtain additional
   bottom-row action buttons.
"""

from chimera.baseDialog import ModalDialog, ModelessDialog, AskYesNoDialog
import chimera
import Tkinter

class OpenSaveBase:
	help = "UsersGuide/opensave.html"
	def __init__(self, clientPos=None, clientSticky=None, command=None,
				help=None, title=None, dialogKw={}, **kw):
		extraButtons = getattr(self, 'extraButtons', ())
		self.buttons = tuple(extraButtons)+(self.default, self.dismiss)
		self.clientPos = clientPos
		self.clientSticky = clientSticky
		self.command = command
		if title:
			self.title = title
		if help:
			self.help = help
		try:
			self.userDblClickCommand = kw["dblClickCommand"]
		except KeyError:
			self.userDblClickCommand = None
		kw["dblClickCommand"] = self._millerDblClick
		kw["readyCommand"] = self._millerReady
		self.millerKw = kw
		self.dialogKw = dialogKw

	def fillInUI(self, parent):
		self.millerBrowser = MillerBrowser(parent, **self.millerKw)
		self.millerBrowser.grid(row=1, column=1, sticky='nsew')
		self.setPath = self.millerBrowser.setPath
		self.getPaths = self.millerBrowser.getPaths
		self.getPathsAndTypes = self.millerBrowser.getPathsAndTypes
		self.getFilter = self.millerBrowser.getFilter
		self.setFilter = self.millerBrowser.setFilter
		self.addFilter = self.millerBrowser.addFilter
		self.rememberDir = self.millerBrowser.rememberDir
		self.rememberFile = self.millerBrowser.rememberFile
		parent.rowconfigure(1, weight=1)
		parent.columnconfigure(1, weight=1)
		self.clientArea = None
		if self.clientPos:
			self.clientArea = Tkinter.Frame(parent)
			row, column = [(0,1), (2,1), (1,2), (1,0)][
						'nsew'.index(self.clientPos)]
			self.clientArea.grid(row=row, column=column,
						sticky=self.clientSticky)
			if self.clientSticky:
				if 'n' in self.clientSticky \
				or 's' in self.clientSticky:
					parent.rowconfigure(row, weight=1)
				if 'e' in self.clientSticky \
				or 'w' in self.clientSticky:
					parent.columnconfigure(column, weight=1)
	
	def _millerDblClick(self):
		if not self.millerBrowser.getPaths(remember=False):
			return
		if self.userDblClickCommand:
			self.userDblClickCommand()
		from chimera.baseDialog import buttonFuncName
		getattr(self, buttonFuncName(self.default))()

	def _millerReady(self, paths):
		if paths:
			state = 'normal'
		else:
			state = 'disabled'
		self.buttonWidgets[self.default].config(state=state)

class ModalBase(ModalDialog):
	dismiss = 'Cancel'
	def OK(self):
		self.returnValue = self.millerBrowser.getPathsAndTypes()
		self.Cancel(self.returnValue)

class ModelessBase(ModelessDialog):
	dismiss = 'Close'
	provideStatus = True
	statusPosition = 'left'
	def __init__(self, *args, **kw):
		ModelessDialog.__init__(self, *args, **kw)
		self.status("Triangle buttons reveal\n"
					"   recently-used folders/files")

	def Apply(self):
		ModelessDialog.Apply(self)
		if self.command:
			self.command(1, self)
	def Cancel(self):
		ModelessDialog.Cancel(self)
		if self.command:
			self.command(0, self)

class OpenBase(OpenSaveBase):
	default = 'Open'
	sample = None
	title = 'Open File in Chimera'
	def __init__(self, **kw):
		self.sample = kw.pop('sample', self.sample)
		# avoid overridding subclass-defined default...
		if 'default' in kw:
			self.default = kw.pop('default')
			# also, if using keyword default presumably
			# simply replacing Open
			def _open(*args, **kw):
				# Open not available at this point...
				self.Open(*args, **kw)
			from chimera.baseDialog import buttonFuncName
			setattr(self, buttonFuncName(self.default), _open)
		OpenSaveBase.__init__(self, **kw)
		if self.sample:
			self.buttons = tuple(self.buttons) + ('Sample',)
		self.millerKw['style'] = 'open'
		if not self.millerKw.has_key('addAll'):
			self.millerKw['addAll'] = 1
		if not self.millerKw.has_key('multiple'):
			self.millerKw['multiple'] = 1

	def Sample(self):
		self.millerBrowser.setPath(self.sample)
	
class SaveBase(OpenSaveBase):
	default = 'Save'
	title = 'Save File in Chimera'
	def __init__(self, **kw):
		# avoid overridding subclass-defined default...
		if 'default' in kw:
			self.default = kw.pop('default')
			# also, if using keyword default presumably
			# simply replacing Save
			def _save(*args, **kw):
				# Save not available at this point...
				self.Save(*args, **kw)
			from chimera.baseDialog import buttonFuncName
			setattr(self, buttonFuncName(self.default), _save)
		OpenSaveBase.__init__(self, **kw)
		self.millerKw['style'] = 'save'
		if not self.millerKw.has_key('addAll'):
			self.millerKw['addAll'] = 0
		if not self.millerKw.has_key('multiple'):
			self.millerKw['multiple'] = 0

	def Save(self):
		from chimera.tkgui import GENERAL, CONFIRM_OVERWRITE
		from chimera.preferences import preferences
		if preferences.get(GENERAL, CONFIRM_OVERWRITE):
			for path in self.millerBrowser.getPaths():
				import os
				if (os.path.exists(path) and
				    not os.path.isdir(path)):
					dlg = AskYesNoDialog("Overwrite %s?"
									% path)
					if dlg.run(self.uiMaster()) == "no":
						self.enter()
						return
		getattr(self, self.keepEquiv())()

class OpenModal(OpenBase, ModalBase):
	Open = ModalBase.OK
	def __init__(self, **kw):
		OpenBase.__init__(self, **kw)
		ModalBase.__init__(self, **self.dialogKw)

class OpenModeless(OpenBase, ModelessBase):
	keepShown = OpenBase.default
	def __init__(self, **kw):
		OpenBase.__init__(self, **kw)
		ModelessBase.__init__(self, **self.dialogKw)

class SaveModal(SaveBase, ModalBase):
	def __init__(self, **kw):
		SaveBase.__init__(self, **kw)
		ModalBase.__init__(self, **self.dialogKw)

class SaveModeless(SaveBase, ModelessBase):
	def __init__(self, **kw):
		SaveBase.__init__(self, **kw)
		ModelessBase.__init__(self, **self.dialogKw)

compressSuffixes = ['.gz']
import subprocess
try:
	subprocess.call(["gzip", "-V"],
			stderr=subprocess.PIPE, stdout=subprocess.PIPE)
except:
	from chimera import replyobj
	replyobj.info("Cannot execute 'gzip':"
				" no automatic decompression of .Z files\n")
else:
	compressSuffixes.append('.Z')

import errno
userIOErrors = set([
		errno.EACCES, errno.EDQUOT,
		errno.EFAULT, errno.EISDIR,
		errno.ELOOP, errno.ENAMETOOLONG,
		errno.ENOENT, errno.ENOSPC,
		errno.ENOTDIR, errno.ENXIO,
		errno.EOPNOTSUPP, errno.EROFS,
])
def osOpen(fileName, *args, **kw):
	"""Open a file/URL with or without compression
	
	   Takes the same arguments as built-in open and returns a file-like
	   object.  However, "fileName" can also be a file-like object
	   itself, in which case it is simply returned.  Also, if "fileName"
	   is a string that begins with "http:" then it is interpreted as
	   an URL.

	   If the file is opened for input, compression is checked for and
	   handled automatically.  If the file is opened for output, the
	   'compress' keyword can be used to force or suppress compression.
	   If the keyword is not given, then compression will occur if the
	   file name ends in '.gz' [case independent].  If compressing,
	   you can supply 'args' compatible with gzip.open().

	   '~' is expanded unless the 'expandUser' keyword is specified as
	   False.

	   Uncompressed non-binary files will be opened for reading with
	   universal newline support.
	"""

	# catch "permission denied" so that we don't get bug reports 
	# from morons
	try:
		return _osOpen(fileName, *args, **kw)
	except IOError, val:
		if hasattr(val, "errno") and val.errno in userIOErrors:
			from chimera import UserError
			raise UserError(val)
		raise

GZIP_MAGIC = '\037\213'
LZW_MAGIC = '\037\235'
def _osOpen(fileName, *args, **kw):
	if not isinstance(fileName, basestring):
		# a "file-like" object -- just return it after making
		# sure that .close() will work
		if not hasattr(fileName, "close") \
		or not callable(fileName.close):
			fileName.close = lambda: False
		return fileName
	if fileName.startswith("http:"):
		import urllib2
		return urllib2.urlopen(fileName)
	if 'expandUser' in kw:
		expandUser = kw['expandUser']
	else:
		expandUser = True
	if expandUser:
		fileName = tildeExpand(fileName)
	import gzip
	if args and 'r' not in args[0]:
		# output
		if 'compress' in kw:
			compress = kw['compress']
		else:
			compress = False
			for cs in compressSuffixes:
				if fileName.lower().endswith(cs):
					compress = True
					break
		if compress:
			return gzip.open(fileName, *args)
		return open(fileName, *args)
	if not args or args[0] == "r":
		args = ("rU",) + args[1:]
	f = open(fileName, *args)
	magic = f.read(2)
	if magic == GZIP_MAGIC:
		# gzip compressed
		f.close()
		f = gzip.open(fileName)
	elif magic == LZW_MAGIC:
		# LZW compressed
		f.close()
		return open(osUncompressedPath(fileName), *args)
	else:
		f.seek(0)
	return f


def osUncompressedPath(inPath, expandUser=True):
	"""Return a path to an uncompressed version of a file

	   If 'inPath' is already uncompressed, it is simply returned.
	   If if is compressed, a temp uncompressed file is created and
	   the path to it is returned.  The temp file is automatically
	   deleted at APPQUIT

	   '~' is expanded unless expandUser is False.

	   This routine is typically used to give uncompressed file
	   paths to C++ functions.
	"""
	import os
	if inPath.startswith("http:"):
		allExts = ""
		base = inPath
		while True:
			base, ext = os.path.splitext(base)
			if ext:
				allExts = ext + allExts
			else:
				break
		localName = osTemporaryFile(suffix=allExts)
		import urllib
		retrieved = urllib.urlretrieve(inPath, localName)
		return osUncompressedPath(localName, expandUser=False)

	if expandUser:
		inPath = tildeExpand(inPath)
	try:
		f = open(inPath)
	except IOError, val:
		if hasattr(val, "errno") and val.errno in userIOErrors:
			from chimera import UserError
			raise UserError(val)
		raise
	magic = f.read(2)
	if magic not in [GZIP_MAGIC, LZW_MAGIC]:
		f.close()
		return inPath
	if magic == LZW_MAGIC and '.Z' not in compressSuffixes:
		from chimera import LimitationError
		raise LimitationError(
			"Cannot uncompress .Z files [cannot find gzip]")
	# gzip compressed
	f.close()

	from os.path import splitext
	from tempfile import mktemp
	lead, suffix = splitext(inPath)
	if suffix in compressSuffixes:
		lead, suffix = splitext(lead)
	tempPath = osTemporaryFile(suffix=suffix)
	outFile = open(tempPath, 'w')
	if magic == GZIP_MAGIC:
		import gzip
		decomp = gzip.open(inPath)
	else:
		from subprocess import Popen, PIPE
		decomp = Popen(["gzip", "-cd", inPath], stdout=PIPE).stdout
	outFile.write(decomp.read())
	outFile.close()

	return tempPath

_tempDir = None
def osTemporaryFile(**args):
	"Return a path to a file that will be deleted when Chimera exits."
	import os
	from tempfile import mkstemp, mkdtemp
	global _tempDir
	if _tempDir == None:
		_tempDir = mkdtemp()
		def rmTemp(trigName, path, trigData):
			try:
				for fn in os.listdir(path):
					os.remove(os.path.join(path, fn))
				os.rmdir(path)
			except:
				pass
		import chimera
		chimera.triggers.addHandler(chimera.APPQUIT, rmTemp, _tempDir)
	args['dir'] = _tempDir
	f, tempPath = mkstemp(**args)
	os.close(f)
	return tempPath

def tildeExpand(path):
	import sys, os.path
	if sys.platform == "win32" and path[:2] in ('~/', '~\\'):
		# Use the user's profile directory on Windows.
		# This directory contains Desktop, Documents, Pictures folders.
		import _winreg
		try:
			h = _winreg.OpenKeyEx(_winreg.HKEY_CURRENT_USER,
        "SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders",
                                        0, _winreg.KEY_QUERY_VALUE)
			v = _winreg.QueryValueEx(h, "Desktop")
			desktop = v[0].encode('mbcs')
			p = os.path.join(os.path.dirname(desktop), path[2:])
		except WindowsError:
			p = path
	else:
		p = os.path.expanduser(path)
	return p

# Only import miller after tildeExpand() is defined.
if not chimera.nogui:
	from miller import MillerBrowser
