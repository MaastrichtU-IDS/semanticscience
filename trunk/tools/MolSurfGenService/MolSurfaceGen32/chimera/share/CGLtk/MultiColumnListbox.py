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
# $Id: MultiColumnListbox.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter
Tk = Tkinter
from Tkinter import _cnfmerge
from SimpleDialog import SimpleDialog
from AuxWidgets import _splitCnf
from CbListbox import CbListbox
from Sash import Sash

class MultiColumnListbox(Tk.Frame):
	def __init__(self, master=None, titled=Tk.FALSE, releaseCallback=None,
			cnf={}, **kw):
		self.releaseCallback = releaseCallback
		sbCnf, cnf = _splitCnf('scrollbar_', _cnfmerge((cnf, kw)))
		Tk.Frame.__init__(self, master, cnf, cursor='sb_h_double_arrow')
		self.scroll = Tk.Scrollbar(self, sbCnf, cursor='arrow',
					command=self.yview)
		self.scroll.pack(side=Tk.LEFT, fill=Tk.Y)
		self.sash = Sash(self, orient=Tk.HORIZONTAL)
		self.sash.pack(side=Tk.LEFT, fill=Tk.BOTH, expand=Tk.TRUE)
		self.listboxList = []
		self.titled = titled

	def listbox(self, n):
		return self.listboxList[n]

	def addListbox(self, title='', **kw):
		if self.titled:
			frame = Tk.Frame(self.sash)
			label = Tk.Label(frame, text=title, bd=2, relief=Tk.GROOVE)
			label.pack(side=Tk.TOP, fill=Tk.X)
			lb = CbListbox(frame, kw,
					cursor='arrow',
					exportselection=0,
					yscrollcommand=self.scrollSet,
					selectionCallback=self.updateSelection)
			lb.pack(side=Tk.TOP, expand=Tk.TRUE, fill=Tk.BOTH)
			self.sash.addPane(frame)
		else:
			lb = CbListbox(self.sash, kw,
					cursor='arrow',
					exportselection=0,
					yscrollcommand=self.scrollSet,
					selectionCallback=self.updateSelection)
			self.sash.addPane(lb)
		self.listboxList.append(lb)
		if callable(self.releaseCallback):
			lb.setReleaseCallback(self.releaseCB)
		return lb

	def setReleaseCallback(self, cb):
		if not callable(cb):
			cb = None
		self.releaseCallback = cb
		myCB = cb and self.releaseCB or None
		for lb in self.listboxList:
			lb.setReleaseCallback(myCB)

	def releaseCB(self, lb):
		self.releaseCallback(self)

	def updateSelection(self, tlb, reason, before, after):
		for lb in self.listboxList:
			if lb is tlb:
				continue
			lb.select_clear(0, Tk.END)
			for s in after:
				lb.select_set(s)

	def yview(self, *args):
		for lb in self.listboxList:
			apply(lb.yview, args)

	def scrollSet(self, min, max):
		self.scroll.set(min, max)
		for lb in self.listboxList:
			lb.yview('moveto', min)

	def curselection(self):
		return self.listboxList[0].curselection()

	def select_adjust(self, index):
		for lb in self.listboxList:
			lb.select_adjust(index)
			lb.rescanSelection()

	def select_anchor(self, index):
		for lb in self.listboxList:
			lb.select_anchor(index)
			lb.rescanSelection()

	def select_clear(self, first, last=None):
		for lb in self.listboxList:
			lb.select_clear(first, last)
			lb.rescanSelection()

	def select_set(self, first, last=None):
		for lb in self.listboxList:
			lb.select_set(first, last)
			lb.rescanSelection()

	def delete(self, first, last=None):
		for lb in self.listboxList:
			lb.delete(first, last)
			lb.rescanSelection()

if __name__ == '__main__':
	def setSelection(mcl):
		mcl.select_set(2)
	f = Tk.Frame()
	f.pack(fill=Tk.BOTH, expand=Tk.TRUE)
	button = Tk.Button(f, text='Set Selection')
	button.pack(side=Tk.TOP, fill=Tk.BOTH)
	mcl = MultiColumnListbox(f, scrollbar_width=8, titled=Tk.TRUE)
	mcl.pack(side=Tk.TOP, fill=Tk.BOTH, expand=Tk.TRUE)
	lb = mcl.addListbox(title='Hello', width=10, height=3)
	nlb = mcl.addListbox(title='World', width=6, height=3)
	clb = mcl.addListbox(title='Checksum', width=6, height=3)
	wlb = mcl.addListbox(title='Weight', width=6, height=3)
	for i in range(3):
		lb.insert(Tk.END, '%2d: hello world' % i)
		nlb.insert(Tk.END, '%2d: goodbye world' % i)
		clb.insert(Tk.END, '%2d: goodbye world' % i)
		wlb.insert(Tk.END, '%2d: goodbye world' % i)
	button['command'] = lambda mcl=mcl: setSelection(mcl)
	mcl.mainloop()
