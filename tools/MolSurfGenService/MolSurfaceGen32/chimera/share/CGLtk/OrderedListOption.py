# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: OrderedListOption.py 27259 2009-03-26 19:41:56Z pett $

import Tkinter

import OutlineLayout

class OrderedListFrame(Tkinter.Frame):
	"""OrderedListFrame keeps track of an ordered list of named items"""

	def __init__(self, master=None, **kw):
		"Initialize manager with no files"

		Tkinter.Frame.__init__(self, master)
		self.outline = apply(OutlineLayout.OutlineLayout,
					(self, self), kw)
		self.outline.pack(side=Tkinter.TOP, fill=Tkinter.BOTH,
					expand=Tkinter.TRUE)

	def items(self):
		return map(lambda e: (e.desc, e.obj), self.outline.entries)

	def _findItem(self, item):
		"Find an item (either by name or value)"

		for e in self.outline.entries:
			if e.desc == item or e.obj == item:
				return e
		return None

	def addItem(self, name, item):
		"Add an item"

		self.outline.addEntry(name, None, item)

	def removeItem(self, item):
		"Remove an item (either by name or value)"

		which = self._findItem(item)
		if which:
			self.outline.removeEntry(which)

	def moveItem(self, item, before):
		"Move an item before another item"

		itemEntry = self._findItem(item)
		if not itemEntry:
			return
		beforeEntry = self._findItem(before)
		if not beforeEntry:
			return
		self.outline.moveEntry(itemEntry, beforeEntry)

	def outlineSelect(self, oEntry):
		pass

	def outlineActivate(self, oEntry):
		pass

	def outlineDND(self, src, dst, before):
		if not isinstance(src, OutlineLayout.OutlineEntry):
			return
		if not isinstance(dst, OutlineLayout.OutlineEntry):
			return
		if before:
			self.outline.moveEntry(src, before=dst)
		else:
			self.outline.moveEntry(src, after=dst)

	def outlineDescribe(self, oEntry):
		pass

	def outlineDisplayed(self, oEntry, text, descTag, iconTag):
		pass

	def add(self):
		pass

	def delete(self):
		self.outline.removeEntry(self.outline.selected)
		self.outlineSelect(self.outline.selected)

	def deleteAll(self):
		for e in self.outline.entries[:]:
			self.outline.removeEntry(e)
		self.outlineSelect(None)
			

class OrderedListOption(OrderedListFrame):
	"""OrderedListFrame with add/delete buttons"""

	def __init__(self, master=None, **kw):
		"Initialize manager with no files"

		# by default, make list small so that packing it
		# doesn't crowd out buttonbox (list will expand and
		# fill, so it won't end up tiny)
		# use '2.5' instead of 2 because of scroller map/unmap
		# problem when using integral line height
		listDict = {'width': 10, 'height':2.5}
		listDict.update(kw)
		apply(OrderedListFrame.__init__, (self, master), listDict)
		import Pmw
		self.buttonBox = Pmw.ButtonBox(self)
		self.buttonBox.pack(side=Tkinter.BOTTOM)
		self._addButton = self.buttonBox.add('Add...',
					state=Tkinter.NORMAL,
					command=self.add)
		self._deleteButton = self.buttonBox.add('Delete',
					state=Tkinter.DISABLED,
					command=self.delete)
		self._deleteAllButton = self.buttonBox.add('Delete All',
					state=Tkinter.NORMAL,
					command=self.deleteAll)
		self.buttonBox.alignbuttons()

	def outlineSelect(self, oEntry):
		if oEntry:
			self._deleteButton.config(state='normal')
		else:
			self._deleteButton.config(state='disabled')

class OrderedFileListOption(OrderedListOption):
	"""OrderedFileListOption keeps track of an ordered list of file names"""

	def __init__(self, *args, **kw):
		self.__pathStyle = kw.pop('pathStyle')
		self.__addKw = kw.pop('addKw', {})
		apply(OrderedListOption.__init__, (self,)+args, kw)

	def add(self):
		try:
			import OpenSave
		except ImportError:
			self._tkAdd()
		else:
			self._chimeraAdd()

	def _tkAdd(self):
		from tkFileDialog import askopenfilename
		filename = askopenfilename()
		if not filename:
			return
		if self.__pathStyle == 'normal':
			self.addItem(filename, filename)
		else:
			import os.path
			dir, name = os.path.split(filename)
			if not dir:
				dir = "(current directory)"
			self.addItem('%s - %s' % (name, dir), filename)

	def _chimeraAdd(self):
		from OpenSave import OpenModeless
		if not hasattr(self, "_addDialog"):
			self._addDialog = OpenModeless(command=self._addCB,
					default='Add', **self.__addKw)
		self._addDialog.enter()

	def _addCB(self, okayed, dialog):
		if not okayed:
			return
		for path in dialog.getPaths():
			if self.__pathStyle == 'normal':
				self.addItem(path, path)
			else:
				import os.path
				dir, name = os.path.split(path)
				if not dir:
					dir = "(current directory)"
				self.addItem('%s - %s' % (name, dir), path)
		

class OrderedDirListOption(OrderedListOption):
	"""OrderedDirListOption keeps track of an ordered list of directory names"""

	def __init__(self, master=None, dirPrompt="Pick a directory",
					startDir=None, hiddenDirs=0, **kw):
		"""as per OrderedListOption, but accepts additional keywords

		'dirPrompt' specifies prompt to use in directory picker
		'startDir' specifies directory to start the picker in
		'hiddenDirs' is boolean indicating whether to show 'hidden' dirs
		"""
		self.dirPrompt = dirPrompt
		self.startDir = startDir
		self.hiddenDirs = hiddenDirs
		apply(OrderedListOption.__init__, (self, master), kw)

	def add(self, *runArgs):
		from DirPick import DirPick

		if not hasattr(self, 'dirPick'):
			self.dirPick = DirPick(
				Tkinter.Toplevel(self.winfo_toplevel()),
				# _not_ Tkinter.Toplevel(self), which somehow
				# confuses the Tix directory picking widget
				# due to the deep widget inheritance 
				# hierarchy of master (-> core dumps)
				query=self.dirPrompt, startDir=self.startDir,
				showHidden=self.hiddenDirs)
		dir = self.dirPick.run(*runArgs)
		if dir:
			self.addItem(dir, dir)

if __name__ == '__main__':
	app = Tkinter.Frame()
	app.pack(fill='both', expand=1)
	option = OrderedFileListOption(app, width=30, height=5)
	option.pack(fill='both', expand=1)
	#
	# TODO: put this in OutlineLayout.py
	#
	option.outline.text.config(wrap='none')

	def printItems(option=option):
		print map(lambda t: t[1], option.items())

	b = Tkinter.Button(app, text='Print Items', command=printItems)
	b.pack(fill='x')
	app.mainloop()
