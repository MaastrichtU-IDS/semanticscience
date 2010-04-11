# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: OutlineLayout.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter
import Tkdnd
import os.path

CLOSED = 0
OPEN = 1

class OutlineEntry:
	"OutlineEntry contains one point (and all its sub-points)"

	def __init__(self, parent, root, desc, help, obj, depth, dnd):
		self.depth = depth	# Distance to root
		self.dnd = dnd		# allow drag-and-drop
		self.parent = parent	# Entry containing this one
		self.root = root	# Root entry (also manager)
		self.isVisible = 0	# is the description visible?
		self.state = CLOSED	# are sub-entries displayed?
		self.desc = desc	# textual description
		self.help = help	# balloon help
		self.obj = obj		# associated object (opaque)
		self.entries = []	# list of sub-entries
		self.textMark = 'mark%x' % abs(id(self))
					# text mark preceding description
		self.iconTag = 'icon%x' % abs(id(self))
					# text tag covering state icon
		self.descTag = 'desc%x' % abs(id(self))
					# text tag covering description
		self.descStart = self.descTag + '.first'
		self.descEnd = self.descTag + '.last'
		self.root._register(self)

	def addEntry(self, desc, help, obj, before=None):
		"Add a sub-entry to current entry"

		e = OutlineEntry(self, self.root, desc, help, obj,
					self.depth + 1, self.dnd)
		if before:
			try:
				n = self.entries.index(before)
				self.entries.insert(n, e)
			except ValueError:
				self.entries.append(e)
		else:
			self.entries.append(e)
		self.state = OPEN
		self.displaySelf()
		return e

	def removeEntry(self, e):
		"Remove a sub-entry to this entry"

		try:
			self.entries.remove(e)
			if self.root.selected is e:
				self.root._deselect()
			e.undisplaySelf()
			if not self.entries:
				self.displaySelf()
		except ValueError:
			pass

	def moveEntry(self, e, before=None, after=None):
		"Move a sub-entry before or after another"

		e.undisplaySelf()
		self.entries.remove(e)
		if before is None and after is None:
			self.entries.append(e)
		elif before is not None:
			self.entries.insert(self.entries.index(before), e)
		else:
			self.entries.insert(self.entries.index(after) + 1, e)
		e.displaySelf()

	def findEntry(self, desc):
		"Find an entry by its description"

		for e in self.entries:
			if e.desc == desc:
				return e
		return None

	def setState(self, state):
		"Set the current open/close state of entry"

		if self.state == state:
			return
		if state == OPEN and len(self.entries) == 0:
			return
		self.state = state
		if state == OPEN:
			self.displayEntries()
		else:
			self.undisplayEntries()
		self.displaySelf()

	def toggleState(self, event=None):
		"Toggle the current open/close state of entry"

		if self.state == OPEN:
			self.state = CLOSED
			self.undisplayEntries()
		else:
			self.state = OPEN
			self.displayEntries()
		self.displaySelf()

	def displaySelf(self):
		"Redisplay description for this entry"

		self.root.unlock()
		if self.isVisible:
			# Old text is already visible, just replace it.
			self.root.text.mark_set(self.textMark, self.descStart)
			self.root.text.delete(self.descStart, self.descEnd)
		else:
			# To place the text in the appropriate position,
			# we need to locate the previous entry (either
			# the older sibling or the parent), which _must_
			# be displayed already due to the order in which
			# we display entries.  We then insert our text
			# after the end of the previous entry.
			prev = self.parent._findPrevious(self)
			self.root.text.mark_set(self.textMark, prev.descEnd)
		self.root.text.insert(self.textMark, self.depth * '\t',
					self.descTag)
		self.root.text.image_create(self.textMark, image=self._image())
		self.root.text.tag_add(self.descTag, self.textMark + '-1c')
		self.root.text.tag_add(self.iconTag, self.textMark + '-1c')
		if self.root.showHelp and self.help:
			textList = [ self.desc + '\n' ]
			helpList = self.help.strip().split('\n')
			for h in helpList:
				textList.append(((self.depth + 1) * '\t') +
						h + '\n')
			text = ''.join(textList)
		else:
			text = self.desc + '\n'
		self.root.text.insert(self.textMark, text, self.descTag)
		if self.root.selected is self:
			color = 'red'
		else:
			color = 'black'
		self.root.text.tag_configure(self.descTag, foreground=color)
		self.root.text.mark_unset(self.textMark)
		self.root.manager.outlineDisplayed(self, self.root.text,
						self.descTag, self.iconTag)
		self.isVisible = 1
		if self.state == OPEN:
			for e in self.entries:
				e.displaySelf()
		self.root.lock()

	def undisplaySelf(self):
		"Undisplay description for this entry"

		if not self.isVisible:
			return
		self.root.unlock()
		if self.state == OPEN:
			for e in self.entries:
				e.undisplaySelf()
		self.root.text.delete(self.descStart, self.descEnd)
		self.root.lock()
		self.isVisible = 0

	def displayEntries(self):
		"Redisplay description for all sub-entries"

		for e in self.entries:
			e.displaySelf()

	def undisplayEntries(self):
		"Undisplay description for all sub-entries"

		for e in self.entries:
			e.undisplaySelf()

	def _bindEvents(self):
		#self.root.text.tag_bind(self.iconTag, '<Enter>',
		#			self._enter, add=1)
		#self.root.text.tag_bind(self.iconTag, '<Leave>',
		#			self._leave, add=1)
		self.root.text.tag_bind(self.iconTag,
					'<ButtonPress-1><ButtonRelease-1>',
					self.toggleState, add=1)
		#self.root.text.tag_bind(self.descTag, '<Enter>',
		#			self._enter, add=1)
		#self.root.text.tag_bind(self.descTag, '<Leave>',
		#			self._leave, add=1)
		self.root.text.tag_bind(self.descTag, '<ButtonPress-1>',
					self._descPress, add=1)
		self.root.text.tag_bind(self.descTag, '<Double-ButtonPress-1>',
					self._descDoublePress, add=1)
		self.root.text.tag_bind(self.descTag, '<Triple-ButtonPress-1>',
					self._descTriplePress, add=1)

	def _findPrevious(self, e):
		n = self.entries.index(e)
		if n == 0:
			return self
		else:
			e = self.entries[n - 1]
			if e.state == OPEN and e.entries:
				return e.entries[-1]
			else:
				return e

	def _image(self):
		if len(self.entries) == 0:
			return self.root.LeafImage
		elif self.state == OPEN:
			return self.root.MinusImage
		else:
			return self.root.PlusImage

	def _enter(self, event):
		self.root.tag_configure(self.descTag, foreground='red')

	def _leave(self, event):
		self.root.tag_configure(self.descTag, foreground='black')

	def _descPress(self, event):
		self.root.balloon.withdraw()
		self.root._select(self)
		if self.dnd:
			Tkdnd.dnd_start(self, event)
			event.widget.bind('<Leave>', self._ignore, add=1)
			event.widget.bind('<Motion>', self._ignore, add=1)
		return 'break'

	def _descDoublePress(self, event):
		self.root._activate(self)
		return 'break'

	def _descTriplePress(self, event):
		return 'break'

	def _ignore(self, event):
		return 'break'

	def dnd_commit(self, source, event):
		if source is self:
			return
		index = '@%d,%d' % (event.x, event.y)
		bbox = self.root.text.bbox(index)
		dy = event.y - bbox[1]
		hh = bbox[3] / 2
		before = dy < hh
		self.root._dnd(source, self, before)

	def dnd_enter(self, source, event):
		pass

	def dnd_leave(self, source, event):
		pass

	def dnd_motion(self, source, event):
		pass

	def dnd_end(self, source, event):
		pass

class OutlineLayout(Tkinter.Frame, OutlineEntry):
	"OutlineLayout is a hierarchical text widget (similar to tree widget)"

	def __init__(self, manager, master=None, dnd=1, **kw):
		self.selected = None
		self.showHelp = 0	# Show help text in widget
		self.entryMap = {}
		self.manager = manager
		import Pmw
		self.balloon = Pmw.Balloon(master, label_fg='black')
		self.setAllowBalloons(1)
		Tkinter.Frame.__init__(self, master)
		self.scrolledText = Pmw.ScrolledText(self,
						text_wrap='none',
						text_tabs='18p',
						text_exportselection=0,
						text_foreground='black',
						text_background='gray')
		self.scrolledText.pack(fill=Tkinter.BOTH, expand=Tkinter.TRUE)
		self.text = self.scrolledText.component('text')
		OutlineEntry.__init__(self, None, self, '', None, None, -1, dnd)
		try:
			dir = os.path.dirname(__file__)
		except NameError:
			dir = ''
		self.PlusImage = Tkinter.BitmapImage(master=self,
					file=os.path.join(dir, 'plus.bm'))
		self.MinusImage = Tkinter.BitmapImage(master=self,
					file=os.path.join(dir, 'minus.bm'))
		self.LeafImage = Tkinter.BitmapImage(master=self,
					file=os.path.join(dir, 'leaf.bm'))
		self.descStart = '1.0'
		self.descEnd = '1.0'
		self.unlockCount = 0
		self.text.config(state=Tkinter.DISABLED)
		self.text.dnd_accept = self._dndAccept
		self.text.config(kw)
		self.text.bind('<ButtonPress>', self._deselect)
		self.text.bind('<Double-ButtonPress>', self._ignore)
		self.text.bind('<Triple-ButtonPress>', self._ignore)
		self.text.bind('<Motion>', self._ignore)
		self._justSelected = 0

	def displaySelf(self):
		for e in self.entries:
			e.displaySelf()

	def setAllowBalloons(self, allow):
		# allow/disallow balloon help completely
		if not allow:
			self.balloon.configure(state='none')
		elif not self.showHelp:
			# balloons on if widget help strings hidden
			self.balloon.configure(state='both')
		self.allowBalloons = allow

	def setShowHelp(self, state):
		# show help strings in widget, else in balloon
		if self.showHelp != state:
			self.showHelp = state
			self.displaySelf()
			if state:
				self.balloon.configure(state='none')
			elif self.allowBalloons:
				self.balloon.configure(state='both')

	def setSelected(self, who):
		if self.selected is who:
			return
		old = self.selected
		self.selected = who
		if old:
			old.displaySelf()
		if who:
			who.displaySelf()

	def unlock(self):
		if self.unlockCount == 0:
			self.text.config(state=Tkinter.NORMAL)
		self.unlockCount = self.unlockCount + 1

	def lock(self):
		self.unlockCount = self.unlockCount - 1
		if self.unlockCount == 0:
			self.text.config(state=Tkinter.DISABLED)

	def _ignore(self, event):
		return 'break'

	def _deselect(self, event=None):
		if not self._justSelected:
			self._select(None)
		else:
			self._justSelected = 0

	def _register(self, who):
		self.entryMap[str(id(who))] = who
		if who.help:
			self.balloon.tagbind(self.text, who.descTag, who.help)
		who._bindEvents()

	def _select(self, who):
		self.setSelected(who)
		self.manager.outlineSelect(who)
		self._justSelected = 1

	def _activate(self, who):
		self.manager.outlineActivate(who)

	def _dnd(self, src, dst, before):
		self.manager.outlineDND(src, dst, before)

	def _dndAccept(self, source, event):
		index = '@%d,%d' % (event.x, event.y)
		tags = self.text.tag_names(index)
		obj = None
		for t in tags:
			if t[:4] != 'desc':
				continue
			try:
				obj = self.entryMap[t[4:]]
				break
			except KeyError:
				pass
		return obj

if __name__ == '__main__':
	class Manager:
		def outlineDisplayed(self, oEntry, text, descTag, iconTag):
			print 'outlineDisplayed'

		def outlineSelect(self, entry):
			print 'select', entry.obj

		def outlineActivate(self, entry):
			print 'activate', entry.obj

		def outlineDND(self, src, dst, before):
			if not isinstance(src, OutlineEntry):
				return
			where = before and "before" or "after"
			print '"%s" dropped %s "%s"' % \
				(src.desc, where, dst.desc)

	app = Tkinter.Frame()
	app.pack(fill='both', expand=1)

	m = Manager()
	layout = OutlineLayout(m, app, dnd=0)
	layout.pack(fill='both', expand=1)
	first = layout.addEntry('Hello world', 'Help for Hello world', 'first')
	plugh = first.addEntry('Plugh', 'Help for Plugh', 'plugh')
	xyzzy = first.addEntry('Xyzzy', None, 'xyzzy')
	second = layout.addEntry('Second entry', 'Help for Second', 'second')

	b = Tkinter.Button(app, text='Remove Plugh',
				command=lambda e=first, s=plugh:
					e.removeEntry(s))
	b.pack(fill='x')
	b = Tkinter.Button(app, text='Remove Xyzzy',
				command=lambda e=first, s=xyzzy:
					e.removeEntry(s))
	b.pack(fill='x')
	b = Tkinter.Button(app, text='Move Xyzzy',
				command=lambda e=first, x=xyzzy, p=plugh:
					e.moveEntry(x, p))
	b.pack(fill='x')
	v = Tkinter.IntVar(app)
	v.set(0)
	b = Tkinter.Checkbutton(app, text='Display help text', variable=v,
				command=lambda l=layout, v=v:
					l.setShowHelp(v.get()))
	b.pack(fill='x')

	app.mainloop()
