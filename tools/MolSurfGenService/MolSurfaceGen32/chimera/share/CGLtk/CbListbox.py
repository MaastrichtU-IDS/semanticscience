#!/usr/bin/env python

# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: CbListbox.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter

class CbListbox(Tkinter.Listbox):
	"""
	CbListbox is simply a Listbox that invokes callbacks
	whenever its selection changes
	"""

	def __init__(self, master=None, cnf={}, **kw):
		try:
			cb = kw['selectionCallback']
			del kw['selectionCallback']
		except KeyError:
			cb = None
		try:
			self.releaseCallback = kw['releaseCallback']
			del kw['releaseCallback']
		except KeyError:
			self.releaseCallback = None
		self.selectionCallback = None
		apply(Tkinter.Listbox.__init__, (self, master, cnf), kw)
		self.setSelectionCallback(cb)
		#
		# Swap the class and window callback execution order
		# so that when our callback is invoked, the selection
		# has already been updated
		#
		bt = self.bindtags()
		bt = (bt[1], bt[0]) + bt[2:]
		self.bindtags(bt)

	def setSelectionCallback(self, cb):
		if cb == None:
			if self.selectionCallback != None:
				self.selectionCallback = None
				self.unbind('<ButtonRelease-1>')
				self.unbind('<ButtonPress-1>')
				self.unbind('<B1-Enter>')
				self.unbind('<B1-Leave>')
		else:
			if self.selectionCallback == None:
				self.bind('<ButtonRelease-1>', self._release)
				self.bind('<ButtonPress-1>', self._press)
				self.bind('<B1-Enter>', self._enter)
				self.bind('<B1-Leave>', self._leave)
				self._afterId = None
		self.selectionCallback = cb
		self._selection = self.curselection()

	def setReleaseCallback(self, cb):
		self.releaseCallback = cb

	def rescanSelection(self):
		self._selection = self.curselection()

	def _release(self, event):
		#print 'ButtonRelease-1'
		self.unbind('<B1-Motion>')
		if self._afterId != None:
			self.after_cancel(self._afterId)
			self._afterId = None
		self._checkSelection('release')
		if callable(self.releaseCallback):
			self.releaseCallback(self)

	def _press(self, event):
		#print 'ButtonPress-1'
		self.bind('<B1-Motion>', self._motion)
		self._checkSelection('press')

	def _motion(self, event):
		#print 'Motion'
		self._checkSelection('motion')

	def _enter(self, event):
		#print 'B1-Enter'
		if self._afterId != None:
			self.after_cancel(self._afterId)
			self._afterId = None
		self._checkSelection('enter')

	def _leave(self, event):
		#print 'B1-Leave'
		self._checkSelection('leave')
		self._afterId = self.after(50, self._autoscan)

	def _autoscan(self):
		#print 'autoscan'
		self._checkSelection('autoscan')
		self._afterId = self.after(50, self._autoscan)

	def _checkSelection(self, reason):
		if self.selectionCallback != None:
			sel = self.curselection()
			if sel != self._selection:
				self.selectionCallback(self, reason,
							self._selection, sel)
				self._selection = sel

if __name__ == '__main__':
	def printSelection(w, reason, prev, cur):
		print 'Listbox:', w
		print 'Reason:', reason
		print 'Previous selection:', prev
		print 'New selection:', cur

	nlb = CbListbox(selectionCallback=printSelection)
	nlb.pack(expand=1, fill='both')
	for i in range(50):
		nlb.insert('end', '%2d: hello world' % i)
	nlb.mainloop()
