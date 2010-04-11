#!/usr/bin/env python

# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import Tkinter
Tk = Tkinter
from Tkinter import _cnfmerge
import sys

from AuxWidgets import _splitCnf

class Entry:
	"""Entry instances are items that go into a EntryList.
	This class should be augmented (probably subclassed)
	to override methods that are called when certain events
	happen (e.g., state change and button clicks)."""

	def __init__(self, text, state=1, isLeaf=Tk.YES, isOpen=Tk.YES):
		self._state = state
		if not isLeaf:
			self._children = []
		self._isOpen = isOpen
		self._text = text
		self._tag = 'tag_%d' % id(self)
		self._parent = None
		self._list = None

	def tag(self):
		return self._tag

	def destroy(self):
		if self._list is not None:
			self.hide(self._list)
		if self._parent:
			self._parent._children.remove(self)

	def addChild(self, child, at=None):
		if not hasattr(self, '_children'):
			self._children = []
			needRedisplay = Tk.YES
		else:
			needRedisplay = Tk.NO
		if at is None:
			at = len(self._children)
		self._children.insert(at, child)
		child._parent = self
		if self._list is None or not self._isOpen:
			return
		if self._parent is not None and needRedisplay:
			self.redisplay()
		#
		# When adding a child, if it is at the top, place it
		# immediately below us.  If it is in the middle, place
		# it above the following entry.  If it is at the end,
		# place it above the entry following us; if there is
		# no following entry, place it at the very end.
		#
		if at == 0:
			if self._parent is None:
				location = '0.0'
			else:
				tag = self._tag
				location = '%s.first + 1 line linestart' % tag
		elif at + 1 < len(self._children):
			tag = self._children[at + 1]._tag
			location = '%s.first linestart' % tag
		else:
			if self._parent is None:
				location = Tk.END + ' - 1 line'
			else:
				children = self._parent._children
				n = children.index(self)
				if n + 1 < len(children):
					tag = children[n + 1]._tag
					location = '%s.first linestart' % tag
				else:
					location = Tk.END + ' - 1 line'
		child.show(self._list, self._list.text.index(location))

	def count(self):
		try:
			return len(self._children)
		except AttributeError:
			return -1

	def child(self, n):
		try:
			return self._children[n]
		except (AttributeError, IndexError):
			return None

	def stateChange(self):
		state = self._stateVar.get()
		if self._state == state:
			return NO
		self._state = state
		return Tk.YES

	def openChange(self):
		isOpen = self._openVar.get()
		if self._isOpen == isOpen:
			return Tk.NO
		self._isOpen = isOpen
		if self._isOpen:
			location = '%s.first + 1 lines linestart' % self._tag
			self._showChildren(self._list, location)
		else:
			self._hideChildren(self._list)
		return Tk.YES

	def selected(self):
		pass

	def deselected(self):
		pass

	def show(self, entryList, at):
		if self._list is None:
			self._setList(entryList)
		self._showChildren(entryList, at)
		if self._parent is None:
			return
		entryList.text['state'] = Tk.NORMAL
		self._showEntry(entryList, at)
		entryList.text['state'] = Tk.DISABLED

	def hide(self, entryList):
		if self._list is None:
			return
		self._hideChildren(entryList)
		if self._parent is None:
			return
		entryList.text['state'] = Tk.NORMAL
		self._hideEntry(entryList)
		self._setList(None)
		entryList.text['state'] = Tk.DISABLED

	def redisplay(self):
		if self._list is None:
			return
		entryList = self._list
		entryList.text['state'] = Tk.NORMAL
		location = entryList.text.index(self._tag + '.first')
		self._hideEntry(entryList)
		self._showEntry(entryList, location)
		entryList.text['state'] = Tk.DISABLED

	#
	# Private methods
	#

	def _setList(self, entryList):
		if entryList is None:
			if self._list:
				self._list.removeTag(self._tag)
			del self._stateButton
			del self._stateVar
			try:
				del self._openButton
				del self._openVar
			except AttributeError:
				pass
		else:
			entryList.addTag(self._tag, self)
			self._stateVar = Tk.IntVar(entryList.text)
			self._stateVar.set(self._state)
			self._stateButton = Tk.Checkbutton(entryList.text,
						variable=self._stateVar)
			self._stateButton['command'] = \
						lambda s=self: s.stateChange()
			if hasattr(self, '_children'):
				self._openVar = Tk.IntVar(entryList.text)
				self._openVar.set(self._isOpen)
				self._openButton = Tk.Checkbutton(
						entryList.text,
						indicatoron=Tk.NO,
						selectcolor='',
						text='. . .',
						variable=self._openVar)
				self._openButton['command'] = \
						lambda s=self: s.openChange()
		self._list = entryList

	def _showChildren(self, entryList, at):
		try:
			for n in range(len(self._children) - 1, -1, -1):
				self._children[n].show(entryList, at)
		except AttributeError:
			pass

	def _hideChildren(self, entryList):
		try:
			for n in range(len(self._children) - 1, -1, -1):
				self._children[n].hide(entryList)
		except AttributeError:
			pass

	def _showEntry(self, entryList, at):
		entryList.text.insert(at, '\n')
		try:
			entryList.text.window_create(at,
					window=self._openButton, padx=2)
		except AttributeError:
			pass
		entryList.text.insert(at, self._text)
		entryList.text.window_create(at, window=self._stateButton)
		entryList.text.insert(at, '  ' * (self._depth() - 1))
		first = '%s linestart' % at
		last = '%s + 1 line linestart' % at
		entryList.text.tag_add(self._tag, first, last)

	def _hideEntry(self, entryList):
		first = '%s.first' % self._tag
		last = '%s.last' % self._tag
		entryList.text.delete(first, last)
		entryList.text.tag_delete(self._tag)

	def _depth(self):
		depth = 0
		entry = self
		while entry._parent:
			entry = entry._parent
			depth = depth + 1
		return depth

class EntryList(Tk.Frame):
	"""EntryList is a list whose items consist of a Checkbutton
	and some text.  Selection is the same as Listbox "Browse" mode."""

	def __init__(self, master=None, cnf={}, **kw):
		sbCnf, cnf = _splitCnf('scrollbar_', _cnfmerge((cnf, kw)))
		textCnf, cnf = _splitCnf('text_', cnf)
		Tk.Frame.__init__(self, master, cnf)
		self.scroll = Tk.Scrollbar(self, sbCnf)
		self.scroll.pack(side=Tk.LEFT, fill=Tk.Y)
		self.text = Tk.Text(self, textCnf)
		self.text.pack(side=Tk.LEFT, expand=Tk.YES, fill=Tk.BOTH)
		self.scroll['command'] = self.text.yview
		self.text['yscrollcommand'] = self.scroll.set
		self.text['state'] = Tk.DISABLED
		self.text.bind('<ButtonPress-1>', self._buttonPress)
		self.text.bind('<ButtonRelease-1>', self._buttonRelease)
		self.text.bind('<B1-Motion>', self._buttonMotion)
		self.text.bind('<Double-ButtonRelease-1>',
				self._buttonDoubleLeft)
		self.text.bind('<Double-ButtonRelease-2>',
				self._buttonDoubleRight)
		self._lastSelected = None
		self._tagDict = {}
		self._entry = Entry('ROOT', isLeaf=Tk.NO)
		self._entry.show(self, '0.0')

	def entry(self):
		return self._entry

	def addTag(self, tag, entry):
		self._tagDict[tag] = entry

	def removeTag(self, tag):
		del self._tagDict[tag]

	def deselect(self, notifyEntry=Tk.YES):
		try:
			self.text.tag_remove(Tk.SEL, Tk.SEL_FIRST, Tk.SEL_LAST)
		except TclError:
			pass
		if notifyEntry:
			self._lastSelected.deselect()
		self._lastSelected = None

	def _buttonPress(self, event):
		sys.stderr.write('buttonPress\n')
		entry = self._findEntry(event.x, event.y)
		sys.stderr.write('buttonPress midway\n')
		self._activateEntry(entry)
		sys.stderr.write('buttonPress done\n')
		return 'break'

	def _buttonRelease(self, event):
		sys.stderr.write('buttonRelease\n')
		entry = self._findEntry(event.x, event.y)
		if entry != self._curEntry:
			self._activateEntry(entry)
		if entry != self._lastSelected:
			if self._lastSelected:
				self._lastSelected.deselected()
			if entry:
				entry.selected()
			self._lastSelected = entry
		return 'break'

	def _buttonMotion(self, event):
		entry = self._findEntry(event.x, event.y)
		if entry != self._curEntry:
			self._activateEntry(entry)
		return 'break'

	def _buttonDoubleLeft(self, event):
		pass
		return 'break'

	def _buttonDoubleRight(self, event):
		pass
		return 'break'

	def _findEntry(self, x, y):
		tagList = self.text.tag_names('@%d,%d' % (x, y))
		entry = None
		for tag in tagList:
			try:
				newEntry = self._tagDict[tag]
			except KeyError:
				continue
			if entry != None:
				raise ValueError, 'Too many tags hit'
			entry = newEntry
		return entry

	def _activateEntry(self, entry):
		self.text.tag_remove(Tk.SEL, '0.0', Tk.END)
		if entry:
			first = '%s.first' % entry.tag()
			last = '%s.first lineend' % entry.tag()
			self.text.tag_add(Tk.SEL, first, last)
		self._curEntry = entry

if __name__ == '__main__':
	global _count
	_count = 0
	def addItem(entryList):
		global _count
		entry = Entry(text='Hello %d' % _count)
		_count = _count + 1
		root = entryList.entry()
		root.addChild(entry)
	def deleteItem(entryList):
		import whrandom
		root = entryList.entry()
		n = int(root.count() * whrandom.random())
		root.child(n).destroy()
	def addChild(entryList):
		import whrandom
		root = entryList.entry()
		n = int(root.count() * whrandom.random())
		entry = root.child(n)
		global _count
		newEntry = Entry(text='Hello %d' % _count)
		_count = _count + 1
		entry.addChild(newEntry)
	f = Tk.Frame()
	f.pack(side=Tk.TOP, expand=Tk.YES, fill=Tk.BOTH)
	el = EntryList(f)
	el.pack(side=Tk.TOP, expand=Tk.YES, fill=Tk.BOTH)
	b = Tk.Button(f, text='Add', command=lambda el=el: addItem(el))
	b.pack(side=Tk.LEFT, expand=Tk.NO, fill=Tk.BOTH)
	b = Tk.Button(f, text='Delete', command=lambda el=el: deleteItem(el))
	b.pack(side=Tk.LEFT, expand=Tk.NO, fill=Tk.BOTH)
	b = Tk.Button(f, text='Add Child', command=lambda el=el: addChild(el))
	b.pack(side=Tk.LEFT, expand=Tk.NO, fill=Tk.BOTH)
	b = Tk.Button(f, text='Quit', command=f.quit)
	b.pack(side=Tk.LEFT, expand=Tk.NO, fill=Tk.BOTH)
	f.mainloop()
