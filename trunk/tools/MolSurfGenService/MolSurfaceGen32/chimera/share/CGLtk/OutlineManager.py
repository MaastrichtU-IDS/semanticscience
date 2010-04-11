# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: OutlineManager.py 26655 2009-01-07 22:02:30Z gregc $

import OutlineLayout

class Entry:
	"""Entry represents a single item in an outline

	This class defines the protocol used by the OutlineManager to
	communicate with entries"""

	def __init__(self):
		self.reset()

	def name(self):
		"Return display name for this entry"
		return 'ExtensionManagementObject'

	def description(self):
		"Return short description (appropriate for balloon help)"
		return 'No description available'

	def reset(self):
		self._category = None
		self._oEntry = None

	def _setCategory(self, cat):
		self._category = cat
		sortedEntries = cat.sortedEntries()
		if sortedEntries[-1] is self:
			before = None
		else:
			n = sortedEntries.index(self)
			before = sortedEntries[n + 1]._oEntry
		self._oEntry = cat._oEntry.addEntry(self.name(),
					self.description(), self, before=before)

class Category:
	"""Category instance tracks set of related entries"""

	def __init__(self, name, desc=None):
		"Initialize an empty category"

		self.catName = name
		self.desc = desc
		self.order = {}
		self.entryList = []
		self._sorted = None
		self.reset()

	def name(self):
		"Return name of category"

		return self.catName

	def description(self):
		"Return short description of category"

		return self.desc

	def setOrder(self, order):
		"Set preferred order of entry presentation"

		self.order = order
		if self._oEntry:
			sorted = map(lambda e: e._oEntry, self.sortedEntries())
			self._oEntry.entries = sorted
			self._oEntry.displaySelf()

	def sortByName(self):
		"Sort entries alphabetically by name"

		nameList = map(lambda e: e.name(), self.entryList)
		nameList.sort()
		order = {}
		for i in range(len(nameList)):
			order[nameList[i]] = i
		self.setOrder(order)

	def addEntry(self, entry):
		"Add an entry to category"

		self._sorted = None
		self.entryList.append(entry)
		if self._oEntry:
			entry._setCategory(self)

	def removeEntry(self, entry):
		"Remove an entry from a category"

		self.entryList.remove(entry)
		self._sorted = None
		if self._oEntry:
			self._oEntry.removeEntry(entry._oEntry)
		entry.reset()

	def moveEntry(self, entry, before):
		"Move an entry to before another entry"

		order = self.sortedEntries()
		order.remove(entry)
		if before:
			order.insert(order.index(before), entry)
		else:
			order.append(entry)
		for i in range(len(order)):
			self.order[order[i]] = i
		if entry._oEntry:
			if before:
				e = before._oEntry
			else:
				e = None
			self._oEntry.moveEntry(entry._oEntry, e)

	def sortedEntries(self):
		"Return entry list sorted by preferred then alphabetical order"

		if self._sorted is not None:
			return self._sorted
		known = []
		unknown = []
		for entry in self.entryList:
			name = entry.name()
			try:
				known.append((self.order[name], entry))
			except KeyError:
				unknown.append((name, entry))
		known.sort()
		known = map(lambda t: t[1], known)
		unknown.sort()
		unknown = map(lambda t: t[1], unknown)
		return known + unknown

	def reset(self):
		for e in self.entryList:
			e.reset()
		self._manager = None
		self._oEntry = None

	def _setManager(self, manager):
		self._manager = manager
		sortedCat = manager.sortedCategories()
		if sortedCat[-1] is self:
			before = None
		else:
			n = sortedCat.index(self)
			before = sortedCat[n + 1]._oEntry
		self._oEntry = manager.outline.addEntry(self.name(),
					self.description(), self, before=before)
		for e in self.sortedEntries():
			e._setCategory(self)

class Manager:
	"""Manager keeps track of available entries by category"""

	def __init__(self):
		"Initialize manager with no entries"

		self.categories = {}
		self.order = {}
		self.outline = None
		self._sorted = None

	def makeOutline(self, master=None, **kw):
		import Tkinter
		import Pmw
		self.frame = Tkinter.Frame(master)
		self.buttonBox = Pmw.ButtonBox(self.frame)
		self.buttonBox.pack(side=Tkinter.BOTTOM)
		self._startButton = self.buttonBox.add('Start',
					state=Tkinter.DISABLED,
					command=self._start)
		self._deleteButton = self.buttonBox.add('Delete',
					state=Tkinter.DISABLED,
					command=self._delete)
		self._infoButton = self.buttonBox.add('Info...',
					state=Tkinter.DISABLED,
					command=self._describe)
		self.buttonBox.alignbuttons()

		self.optionFrame = Tkinter.Frame(master)
		self.optionFrame.pack(side=Tkinter.TOP, fill=Tkinter.X)

		self.outline = apply(OutlineLayout.OutlineLayout,
					(self, self.frame), kw)
		self.outline.pack(side=Tkinter.TOP, fill=Tkinter.BOTH,
					expand=Tkinter.TRUE)

		self.showDescVar = Tkinter.IntVar(self.optionFrame)
		self.showDescVar.set(0)
		b = Tkinter.Checkbutton(self.optionFrame,
					padx=0, pady=0,
					highlightthickness=0,
					text='Show descriptions',
					variable=self.showDescVar,
					command=lambda o=self.outline,
						v=self.showDescVar:
						o.setShowHelp(v.get()))
		b.pack(fill=Tkinter.X)

		for cat in self.sortedCategories():
			cat._setManager(self)
		return self.frame

	def findCategory(self, catName):
		return self.categories[catName]

	def addCategory(self, cat):
		self._sorted = None
		self.categories[cat.name()] = cat
		if self.outline:
			cat._setManager(self)

	def removeCategory(self, cat):
		if cat._oEntry:
			self.outline.removeEntry(cat._oEntry)
			cat.reset()
		del self.categories[cat.name()]
		self._sorted = None

	def moveCategory(self, cat, before):
		"Move a category to before another category"

		order = self.sortedCategories()
		order.remove(cat)
		if before:
			order.insert(order.index(before), cat)
		else:
			order.append(cat)
		for i in range(len(order)):
			self.order[order[i]] = i
		if cat._oEntry:
			if before:
				e = before._oEntry
			else:
				e = None
			self.outline.moveEntry(cat._oEntry, e)

	def sortedCategories(self):
		"Return category list sorted by preferred order"

		if self._sorted is not None:
			return self_sorted
		known = []
		unknown = []
		for name, cat in self.categories.items():
			try:
				known.append((self.order[name], cat))
			except KeyError:
				unknown.append((name, cat))
		known.sort()
		known = map(lambda t: t[1], known)
		unknown.sort()
		unknown = map(lambda t: t[1], unknown)
		return known + unknown

	def outlineSelect(self, oEntry):
		if self.outline:
			if oEntry:
				self._startButton.config(state='normal')
				try:
					state = oEntry.obj.documentation() \
						and 'normal' or 'disabled'
				except AttributeError:
					state = 'disabled'
				self._infoButton.config(state=state)
			else:
				self._startButton.config(state='disabled')
				self._infoButton.config(state='disabled')

	def outlineActivate(self, oEntry):
		pass

	def outlineDND(self, src, dst, before):
		if not isinstance(src, OutlineLayout.OutlineEntry):
			return
		where = before and "before" or "after"
		print '"%s" dropped %s "%s"' % \
			(src.desc, where, dst.desc)

	def outlineDescribe(self, oEntry):
		print 'Describe selected entry'

	def outlineDisplayed(self, oEntry, text, descTag, iconTag):
		pass

	def _start(self):
		self.outlineActivate(self.outline.selected)

	def _delete(self):
		print 'Delete selected entry'

	def _describe(self):
		self.outlineDescribe(self.outline.selected)

if __name__ == '__main__':
	import Tkinter
	class FakeEntry(Entry):
		def __init__(self, name, desc):
			self._name = name
			self._desc = desc
		def name(self):
			return self._name
		def description(self):
			return self._desc
	m = Manager()

	app = Tkinter.Frame()
	app.pack(fill='both', expand=1)
	layout = m.makeOutline(app)
	layout.pack(fill='both', expand=1)
	first = Category('Hello world', 'Help for Hello world')
	m.addCategory(first)
	plugh = FakeEntry('Plugh', 'Help for Plugh')
	first.addEntry(plugh)
	xyzzy = FakeEntry('Xyzzy', None)
	first.addEntry(xyzzy)
	second = Category('Second entry', 'Help for Second')
	m.addCategory(second)

	b = Tkinter.Button(app, text='Remove Plugh',
				command=lambda e=first, s=plugh:
					e.removeEntry(s))
	b.pack(fill='x')
	b = Tkinter.Button(app, text='Remove Second',
				command=lambda m=m, s=second:
					m.removeCategory(s))
	b.pack(fill='x')
	b = Tkinter.Button(app, text='Move Xyzzy',
				command=lambda e=first, x=xyzzy, p=plugh:
					e.moveEntry(x, p))
	b.pack(fill='x')
	b = Tkinter.Button(app, text='Move Second',
				command=lambda m=m, f=first, s=second:
					m.moveCategory(s, f))
	b.pack(fill='x')
	v = Tkinter.IntVar(app)
	v.set(0)
	b = Tkinter.Checkbutton(app, text='Display help text', variable=v,
				command=lambda m=m, v=v:
					m.outline.setShowHelp(v.get()))
	b.pack(fill='x')

	app.mainloop()
