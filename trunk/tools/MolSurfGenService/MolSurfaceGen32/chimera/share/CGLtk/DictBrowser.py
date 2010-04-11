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
# $Id: DictBrowser.py 26655 2009-01-07 22:02:30Z gregc $

import sys
import Tkinter
Tk = Tkinter
from SimpleDialog import SimpleDialog

from AuxWidgets import LabelEntry, LabelText
from Sash import Sash, CollapsiblePane
from MultiColumnListbox import MultiColumnListbox

BrowseFont = ('Helvetica', 12)
EditFont = ('Helvetica', 12)

class DictBrowser(Tk.Frame):
	"""
	DictBrowser is a class for browsing attributes of a single
	dictionary.  The DictBrowser user interface is divided into
	two sections:  the top section is the list of attributes
	(key/value pairs) in the dictionary; the bottom section
	contains two fields for adding/modifying/deleting attributes.
	"""
	def __init__(self, master=None, updateCallback=None, dict=None, **kw):
		self.updateCallback = updateCallback
		kw['master'] = master
		apply(Tk.Frame.__init__, (self,), kw)
		self.sash = Sash(self)
		self.sash.pack(expand=1, fill=Tk.BOTH)

		self.attrPane = CollapsiblePane(self.sash, title='Attributes')
		self.sash.addPane(self.attrPane)
		self.attrListbox = MultiColumnListbox(self.attrPane.frame,
					releaseCallback=self.selectAttr,
					scrollbar_width=8)
		self.attrListbox.addListbox(width=10, font=BrowseFont)
		self.attrListbox.addListbox(width=10, font=BrowseFont)
		self.attrListbox.pack(side=Tk.TOP, fill=Tk.BOTH, expand=1)

		self.editPane = CollapsiblePane(self.sash, title='Edit Panel')
		self.sash.addPane(self.editPane)
		f = Tk.Frame(self.editPane.frame)
		f.pack(side=Tk.BOTTOM, fill=Tk.X, padx=2, pady=2, ipadx=2)
		self.attrUpdate = Tk.Button(f, text='Update')
		self.attrUpdate.pack(side=Tk.RIGHT)
		self.attrRevert = Tk.Button(f, text='Revert')
		self.attrRevert.pack(side=Tk.RIGHT)
		self.attrDelete = Tk.Button(f, text='Delete')
		self.attrDelete.pack(side=Tk.RIGHT)
		f = Tk.Frame(self.editPane.frame)
		f.pack(side=Tk.TOP, expand=Tk.TRUE, fill=Tk.BOTH, padx=2, pady=2)
		self.attrName = LabelEntry(f, label_text='Name', label_width=5,
						width=20, font=EditFont)
		self.attrName.pack(side=Tk.TOP, fill=Tk.X)
		self.attrValue = LabelText(f, label_text='Value', label_width=5,
						height=5, width=20,
						font=EditFont)
		self.attrValue.pack(side=Tk.TOP, expand=1, fill=Tk.BOTH)

		self.attrUpdate['command'] = self.updateAttr
		self.attrRevert['command'] = self.revertAttr
		self.attrDelete['command'] = self.deleteAttr

		self.setDict(dict)

	def setDict(self, dict):
		self.dict = dict
		self._updateAttr(None)

	def selectAttr(self, lb):
		if self.dict == None:
			return
		try:
			i = self._getAttr()
		except ValueError:
			return
		name = self.attrListbox.listbox(0).get(i)
		value = self.attrListbox.listbox(1).get(i)
		self._updateEditPanel(name, value)

	def updateAttr(self):
		if self.dict == None:
			self._complain('No attribute selected')
			return
		name = self.attrName.get()
		value = self.attrValue.get('0.0', Tk.END)
		if callable(self.updateCallback) \
		and not self.updateCallback('update', self.dict, name, value):
			return
		self.dict[name] = value
		self._updateAttr(name)

	def revertAttr(self):
		if self.dict == None:
			self._complain('No attribute selected')
			return
		try:
			i = self._getAttr()
		except ValueError:
			self._complain('No attribute selected')
			return
		name = self.attrListbox.listbox(0).get(i)
		value = self.attrListbox.listbox(1).get(i)
		if callable(self.updateCallback) \
		and not self.updateCallback('revert', self.dict, name, value):
			return
		self._updateEditPanel(name, value)

	def deleteAttr(self):
		if self.dict == None:
			self._complain('No attribute selected')
			return
		name = self.attrName.get()
		if not self.dict.has_key(name):
			self._complain('No such attribute: %s' % name)
			return
		if callable(self.updateCallback) \
		and not self.updateCallback('delete', self.dict, name, None):
			return
		del self.dict[name]
		self._updateAttr(None)

	def _getAttr(self):
		sel = self.attrListbox.curselection()
		if not sel:
			raise ValueError
		return int(sel[0])

	def _updateAttr(self, selectKey):
		self.attrListbox.select_clear(0, Tk.END)
		keyLb = self.attrListbox.listbox(0)
		keyLb.delete(0, Tk.END)
		valueLb = self.attrListbox.listbox(1)
		valueLb.delete(0, Tk.END)
		if self.dict is None or len(self.dict) <= 0:
			self._updateEditPanel('', '')
			return
		keyList = self.dict.keys()
		keyList.sort()
		selectIndex = -1
		for k in keyList:
			if k == selectKey:
				selectIndex = keyList.index(k)
			keyLb.insert(Tk.END, k)
			valueLb.insert(Tk.END, self.dict[k])
		if selectIndex >= 0:
			self.attrListbox.select_set(selectIndex)
			self._updateEditPanel(selectKey, self.dict[selectKey])
		else:
			self._updateEditPanel('', '')

	def _updateEditPanel(self, name, value):
		self.attrName.delete(0, Tk.END)
		self.attrName.insert(Tk.END, name)
		self.attrValue.delete('0.0', Tk.END)
		self.attrValue.insert(Tk.END, value)

	def _complain(self, text):
		d = SimpleDialog(self.winfo_toplevel(), text=text,
					buttons=['Okay'], title='User Error')
		d.go()

if __name__ == '__main__':
	def updateCB(reason, dict, name, value):
		print 'Update:', reason, dict, name, value
		return 1
	dict = {'color':'red', 'size':'large', 'cost':'$1.25'}
	browser = DictBrowser(updateCallback=updateCB, dict=dict)
	browser.pack(fill=Tk.BOTH, expand=Tk.TRUE)
	browser.editPane.hide()
	browser.mainloop()
