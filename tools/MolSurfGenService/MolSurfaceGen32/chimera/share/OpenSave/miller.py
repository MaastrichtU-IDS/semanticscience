# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: miller.py 29504 2009-12-02 22:02:54Z pett $

import Tkinter
import Pmw
import os, sys
import os.path
import re
from chimera import replyobj

# some code to allow sys admins (particularly on Windows) to restrict
# where the browser can go [since Python knows nothing about Windows
# "security" policies].
#
# To enable it, remove the initial "return True" line from the allowed()
# function below.  Then change the list of allowed folders to what you want
# (initially the user's home directory and "/usr/tmp").  Note that
# "DefaultDir" is where the browser will home to when an illegal folder
# access is attempted.
from OpenSave import tildeExpand
DefaultDir = tildeExpand("~")
def allowed(checkPath):
	return True
	for adir in [DefaultDir, "/usr/tmp"]:
		if checkPath.startswith(adir) or adir.startswith(checkPath):
			return True
	return False

class MillerBrowser(Tkinter.Frame):
	"""Miller-column file system browser

	   'style' can be 'open' or 'save'

	   selections are always a list, even if 'multiple' is 0

	   'initialdir' is where the browser points to at start

	   'initialfile' is the file/directory name that will initially
	   appear in the type-in widget.

	   'dirsOnly' controls whether the browser shows files or not.

	   'filters' is a (possibly empty) list of tuples:  (type
	   description, glob(s)) [for 'open' panels] or (type description,
	   glob(s), extension) [for 'save' panels].  The 'type description'
	   is used in the interface to describe the filtering (should be
	   something like "PDB") and is returned when the 'type' method is
	   called.  'glob(s)' can be either a single glob string or a list
	   of such strings.  The glob(s) are used to filter the files
	   (directories if 'dirOnly' is true) shown in the browser.
	   If 'dirsOnly' is true, globs will have '/' appended if they
	   don't already end in '/'.  Glob matching is always case-
	   insensitive.  By default, 'extension' will be appended to the
	   save file name if no extension is specified (and therefore
	   typically begins with a '.').  The user can override this 
	   behavior.  'extension' can be None.  'filters' can be an
	   empty tuple if no filtering is needed.

	   'defaultFilter' controls what filter is initially on.  It is
	   an index into the filters list.  Can be one of the filter
	   descriptions or a menu index.  Negative indices count from the
	   end of the menu.

	   'addAll' controls whether an 'all files (or directories)'
	   choice will be added to the list of filters (only will be
	   added if list of filters is non-empty)

	   'historyID' is used to keep a per-dialog file history list.
	   It should be a string that differs between browsers that
	   open/save different files.  For example, "main chimera file
	   open" or "FindHBond file save".

	   'compressed' controls whether compressed files are shown in
	   the browser.  By default, compressed files are shown in
	   browsers whose 'style' is 'open'.  Files are considered to
	   be compressed if they have a suffix in compressSuffixes.

	   'kw' are passed to the Tkinter.Frame constructor
	"""

	allAskLabel = "all (ask type)"
	allGuessLabel = "all (guess type)"
	allFirst = True

	addExtFmt = "Add %s suffix if none given"

	def __init__(self, parent=None, style='open', multiple=0,
			initialdir=None, initialfile=None, dirsOnly=0,
			filters=[], defaultFilter=None, addAll=1,
			readyCommand=None, dblClickCommand=None,
			setFilterCommand=None, fileEntryCommand=None,
			historyID="", compressed=None, **kw):
		if parent is None:
			parent = Tkinter.Tk()
		Tkinter.Frame.__init__(self, parent, **kw)

		global _rememberer
		if _rememberer == None:
			_rememberer = _Rememberer()
		_rememberer.register(self)

		self.style = style
		self.dirsOnly = dirsOnly
		self.addAll = addAll
		self.multiple = multiple
		self.readyCommand = readyCommand
		self.dblClickCommand = dblClickCommand
		self.setFilterCommand = setFilterCommand
		self.historyID = historyID
		self.compressed = compressed

		self.scrolledFrame = Pmw.ScrolledFrame(self, vertflex='elastic')
		self._lastFrameWidth = None
		self.scrolledFrame.interior().bind('<Configure>',
						self.columnChange, add=1)

		if initialdir is None:
			for faveDir in _rememberer.faveDirs():
				if self.pathExists(faveDir):
					initialdir = faveDir
					break
			else:
				initialdir = os.getcwd()
		if not allowed(initialdir):
			initialdir = DefaultDir
		self.scrolledFrame.grid(row=1, column=0,
						columnspan=2, sticky='nsew')
		self.rowconfigure(1, weight=1)
		self.columnconfigure(1, weight=1)

		self.dirFaves = Pmw.ComboBox(self, fliparrow=1, history=0,
			labelpos='w', selectioncommand=lambda d, s=self:
			s.setPath(d), entryfield_command=lambda s=self:
			s.setPath(s.dirFaves.get()), label_text="Folder:")
		self.dirFaves.grid(row=0, column=0, columnspan=2, sticky='ew')
		self.defaultSelectColor = self.dirFaves.component(
					'entry').cget('selectbackground')

		# eat Return from dirFaves so toplevel binding can work for rest
		entry = self.dirFaves.component('entryfield').component('entry')
		# taken from chimera.baseDialog.Dialog.preventDefault(entry)
		tags = list(entry.bindtags())
		top = tags.index(str(entry.winfo_toplevel()))
		tags.insert(top, str(self.dirFaves))
		entry.bindtags(tuple(tags))
		self.dirFaves.bind('<Return>', lambda e: 'break')

		if style == 'save':
			self.folderButton = Tkinter.Button(self,
				text="New folder...", command=self.newFolder)
			self.folderButton.grid(row=4, column=1)
			justFilters = []
			self.saveExtension = {}
			for filt in filters:
				d, globs, ext = filt
				justFilters.append((d, globs))
				self.saveExtension[d] = ext
			filters = justFilters
			if filters:
				self.addExtVar = Tkinter.IntVar(self)
				self.addExtVar.set(1)
				self.addExtCheck = Tkinter.Checkbutton(self,
						variable=self.addExtVar)

		if self.dirsOnly:
			labelName = "Folder name:"
		else:
			labelName = "File name:"
		self.fileFaves = Pmw.ComboBox(self, fliparrow=1, history=0,
			labelpos='w', selectioncommand=lambda f, s=self:
			s.setPath(f), entryfield_command=fileEntryCommand,
			label_text=labelName)
		self.fileFaves.grid(row=2, column=0, columnspan=2, sticky='ew')
		self.makeFaveFiles()
		self.bind("<Map>", self._mapCB)
		if initialfile:
			self.fileFaves.component('entryfield').setentry(
								initialfile)
		if self.pathExists(initialdir):
			try:
				self.makeMainColumn(initialdir, firstTime=True)
			except IOError:
				# NFS/Samba timeout/hang
				inCommon = os.path.commonprefix([initialdir,
							os.getcwd()])
				if not inCommon:
					inCommon = os.getcwd()
					errorPart = None
				else:
					errorPart = initialdir[len(inCommon):]
				if not os.path.isdir(inCommon):
					inCommon = os.path.dirname(inCommon)
				initialdir = inCommon
				self.makeMainColumn(initialdir,
					errorPath=errorPart, firstTime=True)
		else:
			self.makeMainColumn(os.getcwd(), firstTime=True)
			# can't change to initialdir until filters exist...

		# if there's a default filter, we need the main column
		# to already exist...
		if filters:
			self._makeFiltersButton(filters[:], defaultFilter)
		else:
			self.filters = []
		# also need a main column for this...
		self.makeFaveDirs()
		
		if not self.pathExists(initialdir):
			self.setPath(initialdir)

		# avoid early _readyCB() calls
		# [main column has to have been made for _readyCB() to work]
		self.fileFaves.component('entryfield').configure(
						modifiedcommand=self._readyCB)
		self._readyCB()

	def destroy(self):
		_rememberer.deregister(self)
		Tkinter.Frame.destroy(self)

	def setPath(self, path):
		"""Set the path shown in the browser

		   One normally use the 'initialdir' keyword to __init__ to
		   set up the initial browser path.  'setPath' is used if
		   the path must be changed programatically after that.
		"""
		if path is None:
			# combobox can return this!
			return
		if not allowed(path):
			replyobj.warning("Accessing %s not allowed\n" % path)
			self.browser.setPath(DefaultDir)
			return
		if not self.pathExists(path):
			if self.style != "save":
				replyobj.error("'%s' does not exist.\n" % path)
			unc = ""
			if hasattr(os.path, 'splitunc'):
				unc, path = os.path.splitunc(path)
				if unc:
					if not self.pathExists(unc):
						replyobj.error(
"""Cannot access network share %s
If it is password protected, you should access
it first via Network Neighborhood and try again\n""" % unc)
					return
				elif path[:2] == r'\\':
					err = "Bad network share name '%s'\n" \
						% path
					if path.count('\\') < 3:
						err += "Must consist of at " \
						r'least \\hostname\mount' + "\n"
					replyobj.error(err)
					return
			errorPart = ""
			while 1:
				(head, tail) = os.path.split(path)
				if head == path:
					if unc:
						path = unc
					break
				if errorPart:
					errorPart = os.path.join(tail,
								errorPart)
				else:
					errorPart = tail
				path = head
				fullPath = os.path.join(unc, path)
				if self.pathExists(fullPath):
					path = fullPath
					break
			if not self.pathExists(path):
				path = self.mainColumn.path
		else:
			errorPart = None
		self.mainColumn.remove()
		self.makeMainColumn(path, errorPath=errorPart)
		if self.filters:
			self.setFilter(self.getFilter())

	def pathExists(self, path):
		"""Due to the vagaries of Windows network shares,
		   must use this instead of os.path.exists"""

		if hasattr(os.path, 'splitunc'):
			unc, rem = os.path.splitunc(path)
			if unc and not rem:
				# on Windows, 'stat' of a mount point (which
				# os.path.exists uses) only works if the
				# mount point has a trailing '\'.  And of 
				# course, 'stat' on non-mount points only
				# works if there is no trailing '\'.  So
				# Python magically strips a trailing '\'
				# from paths unless they look like
				# [drive letter]:\
				# Since UNC mount points don't look like
				# that, we add _two_ '\'s so that one
				# remains after stripping
				return os.path.exists(unc + r'\\')
		ope = os.path.exists(path)
		if ope:
			# on Windows, removable-media drives can "exist"
			# and still be inaccessible
			drive, rem = os.path.splitdrive(path)
			if drive:
				curdir = os.getcwd()
				try:
					os.chdir(drive)
				except:
					ret = False
				else:
					ret = True
				os.chdir(curdir)
				return ret
			return True
		return False

	def _getPaths(self, remember):
		paths = self.mainColumn.getPaths()
		typed = self.fileFaves.get().strip()
		if typed:
			if os.path.isabs(typed):
				if remember:
					self.setPath(typed)
				paths = [typed]
			else:
				for i in range(len(paths)):
					path = paths[i]
					if os.path.isdir(path):
						path = os.path.join(path, typed)
					else:
						head, tail = os.path.split(path)
						path = os.path.join(head, typed)
					paths[i] = path
		if self.dirsOnly:
			filtFunc = os.path.isdir
		else:
			filtFunc = lambda p, os=os: not os.path.isdir(p)
		paths = filter(lambda p, f=filtFunc: f(p), paths)
		saveTypes = [None] * len(paths)
		if self.style == 'save':
			saveTypes = self._getTypes(paths)
			if saveTypes == self:
				return [], []
			for i in range(len(paths)):
				if saveTypes[i] == None:
					continue
				ext = self.saveExtension[saveTypes[i]]
				if ext and self.addExtVar.get():
					dirs, fname = os.path.split(paths[i])
					if '.' not in fname:
						paths[i] += ext
		if remember:
			self.rememberDir(paths)
			self.rememberFile(paths)
		for i in range(len(paths)):
			path = paths[i]
			if isinstance(path, unicode) \
			and not os.path.supports_unicode_filenames:
				paths[i] = path.encode('utf8')
		return paths, saveTypes

	def _getTypes(self, paths):
		if len(self.filters) > 0:
			filtType = self.getFilter()
			if self.addAll and len(self.filters) == 3:
				if self.allFirst:
					return [self.filters[-1][0]]*len(paths)
				else:
					return [self.filters[0][0]]*len(paths)
		else:
			return [None] * len(paths)
		if filtType == self.allAskLabel and self.addAll:
			return self._getTypesFromUser(paths)
		if not self.addAll or filtType != self.allGuessLabel:
			return [filtType] * len(paths)

		# okay, we're guessing the types
		types = []
		unknownPaths = []

		for path in paths:
			matched = self._filterMatch(path)
			if len(matched) == 1:
				types.append(matched[0])
			else:
				types.append(None)
				unknownPaths.append(path)
		if unknownPaths:
			userTypes = self._getTypesFromUser(unknownPaths,
							partiallyKnown=1)
			if userTypes == self:
				return userTypes
			utIndex = 0
			for i in range(len(types)):
				if types[i] is None:
					types[i] = userTypes[utIndex]
					utIndex += 1
		return types

	def _filterMatch(self, path):
		if self.addAll:
			if self.allFirst:
				realFilters = self.filters[2:]
			else:
				realFilters = self.filters[:-2]
		else:
			realFilters = self.filters
		matched = []
		for d, globs in realFilters:
			for glob in globs:
				if fileGlobMatch(self.allowingCompressed(),
								path, glob):
					matched.append(d)
					break
		return matched

	def getPaths(self, remember=1):
		"""Get the path(s) indicated in the browser.

		   Returns a (possibly empty) list of paths.  If 'remember'
		   is true, then the paths will be remembered in the list
		   of file and directory favorites.
		"""
		paths = self._getPaths(remember)[0]
		if self.style == 'open':
			paths = [p for p in paths if os.path.exists(p)]
		return paths
	
	def getPathsAndTypes(self, remember=1):
		"""Get the path(s) indicated in the browser, and their types.

		   Returns a (possibly empty) list of path/type two-tuples.
		   If 'remember' is true, then the paths will be remembered
		   in the list of file and directory favorites.  Note that
		   the list can't be empty if used from one of the OpenSave
		   classes, since those classes will not enable the Open/
		   Save button unless the path is valid.

		   Since this method may query the user for types, it should
		   only be called once per dialog use
		"""
		paths, saveTypes = self._getPaths(remember=remember)
		if self.style == 'open':
			p = []
			st = []
			for i in range(len(paths)):
				if os.path.exists(paths[i]):
					p.append(paths[i])
					st.append(saveTypes[i])
			paths = p
			saveTypes = st
		if not paths:
			return []

		returnTypes = saveTypes
		if self.style == 'open':
			returnTypes = self._getTypes(paths)
			if returnTypes == self:
				return []
		return map(None, paths, returnTypes)

	def setFilter(self, descript, filt=None):
		"""Set the file filtering in the browser.

		   The 'defaultFilter' keyword of __init__ is normally
		   used to set up initial filtering, so this is only used
		   if the filtering must be changed programatically after
		   that.

		   'descript' is the type description associated with
		   the filter.  'filt' is for internal use only.
		"""
		if not filt:
			for d, f in self.filters:
				if d == descript:
					filt = f
					break
			else:
				raise KeyError, "No filter named '%s'" % (
								descript)
		pattern = self._menuPattern(descript)
		try:
			index = self.filtMenu.index(pattern)
		except Tkinter.TclError:
			index = self.filtMenu.index(pattern + " \[*")
		menuText = self.filtMenu.entrycget(index, 'label')
		self.filtButton.config(text=menuText)
		if hasattr(self, 'addExtCheck'):
			saveExt = self.saveExtension[descript]
			if not saveExt:
				self.addExtCheck.grid_forget()
			else:
				self.addExtCheck.grid(row=3, column=0,
								columnspan=2)
				self.addExtCheck.config(
						text=self.addExtFmt % saveExt)
		self.mainColumn.filter(filt)
		if self.setFilterCommand:
			self.setFilterCommand(descript)
		_rememberer.rememberFilter(descript, self)

	def getFilter(self):
		"""Get the type description associated with the current filter.
		"""
		filtLabel = self.filtButton.cget('text')
		if filtLabel[-1] == ']':
			return filtLabel[:filtLabel.rindex('[')-1]
		return filtLabel

	def addFilter(self, filterInfo, index=-1):
		"""Add the given filter to the list of filters.

		   'filterInfo' is the same format as a single entry of
		   the 'filters' keyword of __init__.  'index' is where
		   in the list of filter to insert the new filter.
		"""
		if self.style == 'save':
			d, globs, ext = filterInfo
			self.saveExtension[d] = ext
			filterInfo = (d, globs)
		if not hasattr(self, 'filters'):
			self._makeFiltersButton([filterInfo], None)
			return
		if self.addAll:
			if self.allFirst:
				if index >= 0:
					index += 2
			elif index < 0:
				index -= 2
		self.filters.insert(index, filterInfo)
		self.makeFilterMenu()
		
	def columnChange(self, event):
		w = self.scrolledFrame.interior().winfo_width()
		if self._lastFrameWidth == w:
			return
		self._lastFrameWidth = w
		# have to delay querying scrolled frame so that new
		# columns can get mapped
		def updateScroll(*args):
			visLeft, visRight = self.scrolledFrame.xview()
			validRight = self.mainColumn.validRight()
			if visRight < validRight:
				self.scrolledFrame.xview(mode="moveto",
						value=validRight-(visRight-visLeft))
		self.scrolledFrame.after(100, updateScroll)
	
	def makeFaveDirs(self):
		self.dirFaves.clear()
		self.dirFaves.setlist(_rememberer.faveDirs())
		self._setDirEntry(self.mainColumn.getDirPath())

	def makeFaveFiles(self):
		curFave = self.fileFaves.get()
		self.fileFaves.clear()
		self.fileFaves.setlist(_rememberer.faveFiles(self))
		self.fileFaves.component('entryfield').setentry(curFave)

	def makeFilterMenu(self):
		self.filtMenu = Tkinter.Menu(self.filtButton, tearoff=0)
		for filtNum, info in enumerate(self.filters):
			descript, filt = info
			if not isinstance(filt, (list, tuple)):
				filt = [filt]
			suffixes = []
			for i in range(len(filt)):
				if self.dirsOnly and filt[i][-1] != os.sep:
					filt[i] += os.sep
				if filt[i].startswith("*."):
					suffixes.append(filt[i][1:])
			label = descript
			if suffixes:
				label += " [" + ", ".join(suffixes) + "]"
			newColumn = (filtNum % 20 == 0) and filtNum > 0 \
					and filtNum < len(self.filters) - 1
			self.filtMenu.add_command(label=label,
				columnbreak=newColumn, command=lambda s=self,
				f=filt, d=descript: s.setFilter(d, f))
		self.filtButton.config(menu=self.filtMenu)

	def makeMainColumn(self, path, errorPath=None, firstTime=False):
		path = os.path.abspath(tildeExpand(path))
		self.mainColumn = MillerColumn(self.scrolledFrame.interior(),
				self, None, path, self.dirsOnly, self.multiple,
				self._selectionCB, self.dblClickCommand,
				titleMode=None, firstTime=firstTime)
		faveDir = path
		if not os.path.isdir(path):
			faveDir, file = os.path.split(path)
		self._setDirEntry(path, errorPath)

	def makeVisible(self, column):
		leftEdge, rightEdge = self.scrolledFrame.xview()
		tot = 0
		curColumn = self.mainColumn
		while curColumn:
			if column == curColumn:
				colLeft = tot
			tot += curColumn.winfo_width()
			if column == curColumn:
				colRight = tot
			curColumn = curColumn.nextColumn
		colLeft /= float(tot)
		colRight /= float(tot)
		if colLeft < leftEdge:
			self.scrolledFrame.xview('moveto', colLeft)
		elif colRight > rightEdge:
			self.scrolledFrame.xview('moveto',
					leftEdge + (colRight - rightEdge))
	def _readyCB(self):
		if self.readyCommand:
			self.readyCommand(self.getPaths(remember=False))

	def _selectionCB(self):
		# arrange to have entries track file name / path
		# as they get clicked
		paths = self.mainColumn.getPaths()
		fileEntry = self.fileFaves.component('entryfield')
		if len(paths) == 1 and not os.path.isdir(paths[0]):
			head, tail = os.path.split(paths[0])
			fileEntry.setentry(tail)
		elif self.style == 'open':
			fileEntry.setentry("")
		if len(paths) == 1 and os.path.isdir(paths[0]):
			self._setDirEntry(paths[0])
		self._readyCB()

	def _setDirEntry(self, path, errorPath=None):
		if errorPath:
			path = os.path.join(path, errorPath)
		entryfield = self.dirFaves.component('entryfield')
		entryfield.setentry(path)
		
		entry = entryfield.component('entry')
		if errorPath:
			entry.selection_range(len(path) - len(errorPath),
								len(path))
			entry.config(selectbackground='pink')
		else:
			entry.config(selectbackground=self.defaultSelectColor)

	def newFolder(self):
		self.folderPromptDialog = Pmw.PromptDialog(self,
			buttons=('Cancel', 'OK'), command=self.newFolderCB,
			defaultbutton='OK', title="New Folder",
			entryfield_labelpos='w', label_text="New folder name:")
		self.folderPromptDialog.activate()
	
	def newFolderCB(self, button):
		self.folderPromptDialog.deactivate()
		if button == None or button == 'Cancel':
			return
		folder = self.folderPromptDialog.get()
		if not folder:
			raise UserError(
				"You didn't provide a name for the new folder")
		self.mainColumn.newFolder(folder)
		self._setDirEntry(self.mainColumn.getPaths()[0])

	def rememberDir(self, dirName):
		"""Put a directory in the list of directory favorites"""
		_rememberer.rememberDir(dirName)

	def rememberFile(self, fileName):
		"""Put a file in the list of file favorites"""
		_rememberer.rememberFile(fileName, self)

	def _getTypesFromUser(self, paths, partiallyKnown=0):
		if self.addAll:
			if self.allFirst:
				realFilters = self.filters[2:]
			else:
				realFilters = self.filters[:-2]
		else:
			realFilters = self.filters
		types = []
		for d, globs in realFilters:
			types.append(d)
		types.sort(lambda a, b: cmp(a.lower(), b.lower()))
		self._userTypes = []
		self._runTypesQuery(paths, types, partiallyKnown)
		return self._userTypes

	def _menuPattern(self, source):
		pattern = ""
		for c in source:
			if c in '*?\\[]':
				pattern += '\\' + c
			else:
				pattern += c
		return pattern

	def _runTypesQuery(self, paths, types, partiallyKnown):
		if self.dirsOnly:
			realm = "folder"
		else:
			realm = "file"
		# for some reason on Windows, inheriting simply from self
		# results in the activated dialog not being shown...
		self._typeDialog = Pmw.SelectionDialog(
			self.winfo_toplevel().master, defaultbutton='OK',
			buttons=('OK', 'Cancel'), command=self._setUserType, 
			title="Type Selection", scrolledlist_labelpos='n',
			label_text="Please designate %s type for\n%s" %
			(realm, paths[0]), scrolledlist_items=types)
		self._typeDialog.rtqData = (paths, types, partiallyKnown)
		if len(paths) > 1:
			if not hasattr(self, 'rtqApplyAllVar'):
				self.rtqApplyAllVar = Tkinter.IntVar(self)
			self.rtqApplyAllVar.set(0)
			if partiallyKnown:
				text = "Use this type for remainder\n" \
					"of unknown selected %ss" % realm
			else:
				text = "Use this type for remainder\n" \
					"of selected %ss" % realm
			Tkinter.Checkbutton(
				self._typeDialog.component("dialogchildsite"),
				variable=self.rtqApplyAllVar, text=text
				).pack()
		self._typeDialog.activate()

	def _setUserType(self, but):
		self._typeDialog.deactivate()
		if but != 'OK':
			self._userTypes = self
			return
		sels = self._typeDialog.getcurselection()
		paths, types, partiallyKnown = self._typeDialog.rtqData
		self._typeDialog.destroy()
		try:
			userType = sels[0]
		except IndexError:
			replyobj.error("No type selected for %s!\n" % paths[0])
			self._userTypes = self
			return
		self._userTypes.append(userType)
		if len(paths) == 1:
			return
		if self.rtqApplyAllVar.get():
			self._userTypes.extend([userType] * (len(paths) - 1))
			return
		self._runTypesQuery(paths[1:], types, partiallyKnown)
			
	def _makeFiltersButton(self, filters, defaultFilter):
		if self.dirsOnly:
			ltext = 'Folder type:'
		else:
			ltext = 'File type:'
		widget = Pmw.LabeledWidget(self, labelpos='w', label_text=ltext)
		widget.grid(row=4, column=0, sticky='w')

		if self.addAll:
			if self.allFirst:
				filters.insert(0, (self.allAskLabel, '*'))
				filters.insert(0, (self.allGuessLabel, '*'))
				if defaultFilter == None:
					defaultFilter = 0
				elif isinstance(defaultFilter, int) \
				and defaultFilter >= 0:
					defaultFilter += 2
			else:
				filters.append((self.allGuessLabel, '*'))
				filters.append((self.allAskLabel, '*'))
				filters.insert(0, (self.allGuessLabel, '*'))
				if defaultFilter == None:
					defaultFilter = -1
				elif isinstance(defaultFilter, int) \
				and defaultFilter < 0:
					defaultFilter -= 2
			if self.style == 'save':
				self.saveExtension[self.allAskLabel] = None
				self.saveExtension[self.allGuessLabel] = None
		elif defaultFilter == None:
			defaultFilter = 0
		self.filters = filters
		self.filtButton = Tkinter.Menubutton(widget.interior(), pady=0,
						indicatoron=1, relief='raised')
		self.makeFilterMenu()
		if isinstance(defaultFilter, int):
			defaultFilter = filters[defaultFilter][0]
		self.filtButton.grid(row=0, column=0)
		initialFilter = _rememberer.lastFilter(self)
		if initialFilter:
			for descript, globs in self.filters:
				if descript == initialFilter:
					break
			else:
				initialFilter = defaultFilter
		else:
			initialFilter = defaultFilter
		self.setFilter(initialFilter)
		Pmw.alignlabels([widget, self.fileFaves], sticky='e')

	def allowingCompressed(self):
		if self.compressed is None:
			return self.style == 'open'
		return self.compressed

	def _mapCB(self, event=None):
		self.fileFaves.component('entry').focus_set()
		self.mainColumn.refresh()
		if not self.mainColumn.valid:
			# can happen if last browse was removable media
			self.setPath(os.getcwd())
			

class MillerColumn(Pmw.ScrolledListBox):
	def __init__(self, parent, browser, initHead, initTail, dirsOnly,
			multiple, selectionCommand=None, dblClickCommand=None,
			titleMode='tail', column=0, firstTime=False):
		self.parent = parent
		self.browser = browser
		self.dirsOnly = dirsOnly
		self.multiple = multiple
		self.titleMode = titleMode
		self.column = column
		self.selectionCommand = selectionCommand
		self.dblClickCommand = dblClickCommand
		self.filt = None
		rowspan = 3
		needUp = needDrive = 0
		compact = self.isCompact()
		if initHead is None:
			# we da man; figure out path stuff
			splitPath = []
			if hasattr(os.path, 'splitunc'):
				unc, head = os.path.splitunc(initTail)
			else:
				unc = ""
				head = initTail
			while(1):
				nextHead, tail = os.path.split(head)
				if nextHead == head:
					break
				splitPath.append(tail)
				head = nextHead
			if unc:
				# since splitpath of '\pdb' yields '\', 'pdb'
				# just forget head (i.e. '\') here
				head = unc
			splitPath.reverse()
			if compact and len(splitPath) > 1:
				needUp = 1
			if hasattr(os.path, 'splitunc'):
			#if len(head) == 3 and head[1:] == ':\\' \
			#or compact and os.sep == '\\':
				needDrive = 1
			
			if needDrive:
				upRow = 1
			else:
				upRow = 2
			if needUp:
				rowspan = upRow
			elif needDrive:
				rowspan = 2
				
			if needDrive:
				# a windows drive identifier
				self.driveButton = Tkinter.Menubutton(parent,
						text="Change drive",
						indicatoron=1, relief='raised')
				self.driveButton.grid(row=2, column=column)
				self.drives = []
				self.driveMenu = Tkinter.Menu(self.driveButton,
					postcommand=self._drivePost, tearoff=0)
				self.driveButton.configure(menu=self.driveMenu)

			if compact:
				head = [head] + splitPath[:-1]
				tail = splitPath[-1:]
			else:
				head = [head]
				tail = splitPath
			parent.rowconfigure(0, weight=1)
		else:
			head = initHead
			tail = initTail
		self.head = head
		self.path = os.path.join(*tuple(head))

		if needUp:
			# go up a directory
			self.upButton = Tkinter.Button(parent,
				text="<- parent directory",
				command=lambda sp=self.browser.setPath,
				path=self.path: sp(path))
			self.upButton.grid(row=upRow, column=column)
		
		items = self._getItems(firstTime, tail)
		
		labelKW = {}
		if titleMode == 'tail':
			labelKW['labelpos'] = 'n'
			labelKW['label_text'] = self.head[-1]
			
		if multiple:
			selectMode = 'extended'
		else:
			selectMode = 'browse'
		Pmw.ScrolledListBox.__init__(self, parent, items=items,
					selectioncommand=self.singleClickCB,
					dblclickcommand=self.dblClickCommand,
					listbox_selectmode=selectMode,
					listbox_exportselection=0, **labelKW)
		self.column, self.rowspan = column, rowspan
		self.grid(row=0, column=column, rowspan=rowspan, sticky='nsew')
		self.configure(vscrollmode='dynamic')
		parent.columnconfigure(column, weight=1)

		self.nextColumn = None
		self.valid = True
		if tail:
			isDir = 1
			normItems = map(os.path.normcase, items)
			try:
				index = normItems.index(
					os.path.normcase(tail[0] + os.sep))
			except ValueError:
				try:
					index = normItems.index(
						os.path.normcase(tail[0]))
				except ValueError:
					# path doesn't exist anymore; stop here
					return
				isDir = 0
			self.select_set(index)
			self.see(index)
			if isDir:
				self.nextColumn = MillerColumn(parent,
					self.browser,
					head + tail[:1], tail[1:], dirsOnly,
					multiple, selectionCommand,
					dblClickCommand, titleMode, column+1,
					firstTime)

	def singleClickCB(self):
		self.newSelection()
	
	def changeDrive(self, drive):
		self.browser.setPath(drive)

	def remove(self):
		if self.nextColumn:
			self.nextColumn.remove()
			self.nextColumn = None
		self.grid_forget()
		Pmw.ScrolledListBox.destroy(self)
	
	def clear(self):
		if not self.valid:
			return
		if self.nextColumn:
			self.nextColumn.clear()
		Pmw.ScrolledListBox.clear(self)
		self.valid = False

	def hide(self):
		if self.nextColumn:
			self.nextColumn.hide()
		self.grid_forget()

	def revive(self, head):
		self.head = head
		self.path = os.path.join(*tuple(head))
		self.setlist(self._getItems())
		self.grid(row=0, column=self.column, rowspan=self.rowspan,
							sticky='nsew')
		self.valid = True
		self.browser.makeVisible(self)
		
	def validRight(self):
		validWidth = invalidWidth = 0
		col = self
		while True:
			width = col.component('hull').winfo_width()
			if col.valid:
				validWidth += width
			else:
				invalidWidth += width
			if col.nextColumn:
				col = col.nextColumn
			else:
				break
		return validWidth / float(validWidth + invalidWidth)

	def isCompact(self):
		from chimera.tkgui import GENERAL, COMPACT_OPENSAVE
		from chimera.preferences import preferences
		return preferences.get(GENERAL, COMPACT_OPENSAVE)

	def filter(self, filt):
		if not self.valid:
			return
		if isinstance(filt, basestring):
			filt = [filt]
		self.filt = filt
		self._refresh()
		if self.nextColumn:
			self.nextColumn.filter(filt)
	
	def getDirPath(self):
		# return the path being shown in the browser,
		# which is not necessarily the current selection
		if self.nextColumn and self.nextColumn.valid:
			return self.nextColumn.getDirPath()
		return self.path

	def getDrives(self):
		drives = []
		curdir = os.getcwd()
		for drive in 'CDEFGHIJKLMNOPQRSTUVWXYZ':
			try:
				os.chdir(drive + ':')
			except:
				continue
			drives.append(drive + ':\\')
		os.chdir(curdir)
		return drives
				
	def getPaths(self):
		if self.nextColumn and self.nextColumn.valid:
			return self.nextColumn.getPaths()
		selections = self.getcurselection()
		paths = []
		for sel in selections:
			paths.append(os.path.join(self.path, sel))
		if not paths:
			return [self.path]
		return paths

	def itemSort(self, a, b):
		aDir = (a[-1] == os.sep)
		bDir = (b[-1] == os.sep)
		if aDir == bDir:
			aUni = isinstance(a, unicode)
			bUni = isinstance(b, unicode)
			if aUni == bUni:
				return cmp(a.lower(), b.lower())
			return cmp(bUni, aUni)
		if aDir:
			return -1
		return 1

	def newFolder(self, folderName):
		if self.nextColumn and self.nextColumn.valid:
			self.nextColumn.newFolder(folderName)
			return
		folderPath = os.path.join(self.path, folderName)
		if os.path.exists(folderPath):
			from chimera import UserError
			raise UserError("Cannot create folder named '%s'"
				" because a file or folder with that name"
				" already exists" % folderName)
		# catch "permission denied" so that we don't get bug reports 
		# from morons
		try:
			os.mkdir(folderPath)
		except (OSError, IOError), val:
			from OpenSave import userIOErrors
			if hasattr(val, "errno") and val.errno in userIOErrors:
				from chimera import UserError
				raise UserError(val)
			raise
		self.select_clear(0)
		self._refresh()
		self.select_set(list(self.get()).index(folderName + os.sep))
		self.newSelection()
		
	def newSelection(self):
		selected = self.getcurselection()
		if self.nextColumn:
			self.nextColumn.clear()
		if len(selected) == 1 and selected[0][-1] == os.sep:
			checkPath = os.path.join(self.path, selected[0])
			if not allowed(checkPath):
				replyobj.warning("Accessing %s not allowed\n"
								% checkPath)
				self.browser.setPath(DefaultDir)
				return
			if self.isCompact() and not self.nextColumn:
				self.browser.setPath(os.path.join(self.path,
								selected[0]))
				return
			newPath = self.head + [selected[0][:-1]]
			try:
				if self.nextColumn:
					self.nextColumn.revive(newPath)
				else:
					self.nextColumn = MillerColumn(
						self.parent, self.browser,
						newPath, [], self.dirsOnly,
						self.multiple,
						self.selectionCommand,
						self.dblClickCommand,
						self.titleMode, self.column+1)
			except IOError, v:
				from chimera import UserError
				raise UserError(v)
			if self.filt:
				self.nextColumn.filter(self.filt)
		if self.selectionCommand:
			self.selectionCommand()
	
	def refresh(self):
		if not self.valid:
			return
		prevsel = self.getcurselection()
		self._refresh()
		if not self.valid:
			return
		if prevsel != self.getcurselection():
			self.newSelection()
		elif self.nextColumn:
			self.nextColumn.refresh()

	def _drivePost(self):
		# drives menu about to post
		drives = self.getDrives()
		if drives == self.drives:
			return
		self.driveMenu.delete(0, 'end')
		for drive in drives:
			self.driveMenu.add_command(label=drive, command=lambda
				s=self, d=drive: s.changeDrive(d))
		self.drives = drives

	def _getItems(self, firstTime=False, tail=None):
		try:
			dirList = listDir(self.path)
		except:
			# some WindowsErrors ("The device is not ready")
			# should really be IOErrors
			raise IOError(sys.exc_info()[1])
		items = []
		started = []
		doneExamining = []
		def _examineDir():
			started.append(1)
			for item in dirList:
				if item.startswith(".") and (
				not tail or tail[0] != item):
					# don't put "dot" files in list
					# unless we # are trying to show
					# a path containing them
					continue
				path = os.path.join(self.path, item)
				if os.path.isdir(path):
					items.append(item + os.sep)
				elif not self.dirsOnly:
					items.append(item)
			doneExamining.append(1)
		if firstTime:
			# during initial browser setup, use threads to
			# detect hanging NFS mounts.  Due to thread 
			# overhead, only do this during setup.
			from threading import Thread
			thread = Thread(target=_examineDir)
			thread.setDaemon(True)
			thread.start()
			thread.join(15.0)
			if not started:
				_examineDir()
			elif not doneExamining:
				path = self.path
				if isinstance(path, unicode):
					path = path.encode('utf8')
				from chimera import NonChimeraError
				raise NonChimeraError(
"""Listing the contents of %s is taking a long time.
This probably due to a hanging NFS/Samba mount.  You might want to change
your preferences to use a "short" (two-column) browser.  This is in
the 'General' preferences category.  Also, in the same category make
sure the "starts in directory from last session" is false. Restart Chimera
after making these changes.

If you do the above and still get hanging behavior, make sure you
start Chimera from a directory where you can list the contents without a hang,
and where you can list the contents of the parent directory without a hang.
""" % path)
		else:
			_examineDir()
		items.sort(self.itemSort)

		return items

	def _refresh(self):
		if not self.browser.pathExists(self.path):
			self.clear()
			return
		cursel = self.getcurselection()
		dirList = listDir(self.path)
		files = []
		dirs = []
		for item in dirList:
			path = os.path.join(self.path, item)
			if os.path.isdir(path):
				dirs.append(item + os.sep)
			elif not self.dirsOnly:
				files.append(item)
		if self.filt:
			matched = {}
			if self.dirsOnly:
				unfiltered = dirs
			else:
				for d in dirs:
					matched[d] = 1
				unfiltered = files
			for filt in self.filt:
				for fn in unfiltered:
					if fileGlobMatch(self.browser.
							allowingCompressed(),
							fn, filt):
						matched[fn] = 1
			items = matched.keys()
		else:
			items = dirs + files
		items = filter(lambda i: not i.startswith(".") or i in cursel,
									items)
		items.sort(self.itemSort)
		self.setlist(items)
		for s in cursel:
			try:
				i = items.index(s)
			except ValueError:
				continue
			self.select_set(i)
			self.see(i)

from chimera import preferences

_prefs = {"dirHistory": [], "fileHistory": {}, "lastFilter": {}}
class _MillerPrefs(preferences.Category):
	def hidden(self):
		return 1
	
	def ui(self, master=None):
		return None
	
	def load(self, optDict, notifyUI=1):
		_prefs.update(optDict)
		if notifyUI:
			self._pref.notifyUI()
	def save(self):
		return _prefs

preferences.addCategory("miller browser", _MillerPrefs)

class _Rememberer:
	def __init__(self):
		self._instances = []

		# add home and startup dir to favorites...
		if sys.platform == "win32":
			home = tildeExpand("~/Desktop")
		else:
			home = tildeExpand("~")
		if home[0] != "~":
			self._remember(home, place="dirs", raiseUp=0)

		from chimera.tkgui import GENERAL, STARTUP_DIRECTORY
		from chimera.preferences import preferences
		add_startup = not preferences.get(GENERAL, STARTUP_DIRECTORY)
		if add_startup:
			self._remember(os.getcwd(), place="dirs")

	def _remember(self, name, place="dirs", raiseUp=1, instance=None):
		global _prefs

		if not isinstance(name, basestring):
			for n in name:
				self._remember(n, place=place, raiseUp=raiseUp,
					instance=instance)
			return

		name = handleAccented(name)
		if place == "dirs":
			hist = _prefs['dirHistory']
			if not os.path.isdir(name):
				name, tail = os.path.split(name)
		else:
			try:
				hist = _prefs['fileHistory'][instance.historyID]
			except KeyError:
				hist = []
		hist = [handleAccented(x) for x in hist]
		

		if hist and hist[0] == name:
			return
		
		if name in hist:
			hist.remove(name)
		if raiseUp:
			newHist = [name] + hist[:9]
		else:
			newHist = hist[:9] + [name]
		if place == "dirs":
			_prefs["dirHistory"] = newHist
		else:
			_prefs["fileHistory"][instance.historyID] = newHist
		preferences.save()
	
	def register(self, instance):
		self._instances.append(instance)

	def deregister(self, instance):
		self._instances.remove(instance)

	def rememberDir(self, name):
		self._remember(name, place="dirs")
		for inst in self._instances:
			inst.makeFaveDirs()

	def rememberFile(self, name, instance):
		self._remember(name, place="files", instance=instance)
		instance.makeFaveFiles()

	def rememberFilter(self, filt, instance):
		global _prefs
		if instance.historyID:
			_prefs["lastFilter"][instance.historyID] = filt
			preferences.save()

	def faveDirs(self):
		return _prefs["dirHistory"]

	def faveFiles(self, instance):
		try:
			return _prefs["fileHistory"][instance.historyID]
		except KeyError:
			return []

	def lastFilter(self, instance):
		try:
			return _prefs["lastFilter"][instance.historyID]
		except KeyError:
			return None

_rememberer = None

def fileGlobMatch(allowingCompressed, fn, glob):
	from fnmatch import fnmatch
	downglob = glob.lower()
	downfn = fn.lower()
	if fnmatch(downfn, downglob):
		return True
	if allowingCompressed:
		from OpenSave import compressSuffixes
		for cs in compressSuffixes:
			if fnmatch(downfn, downglob + cs.lower()):
				return True
	return False

def handleAccented(path):
	if not isinstance(path, unicode):
		try:
			unicode(path)
		except UnicodeDecodeError:
			return unicode(path, "latin1")
	return path

def listDir(path):
	# screen out weird names that can't be decoded since they
	# throw exceptions with os.path.join
	return [i for i in os.listdir(unicode(path))
					if isinstance(i, unicode)]

