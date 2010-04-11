# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import os
import operator
from Tkinter import *

from CGLtk.MultiColumnListbox import MultiColumnListbox
from CGLtk.ModalWindow import ModalWindow
import chimera
from chimera.baseDialog import ModalDialog, OK, Cancel

def chooseModels(master,
	mode=EXTENDED, setupCB=None, finishCB=None, modelTypes=[], *args, **kw):

	"""
	Modal panel for selecting a set of models
	"""

	ml = chimera.openModels.list(modelTypes=modelTypes)
	if len(ml) == 0:
		return []
	ml.sort(_cmpModels)
	cd = ChooserDialog(ml, mode, setupCB, finishCB, *args, **kw)
	return cd.run(master)

def _cmpModels(m0, m1):
	if m0.id < m1.id:
		return -1
	elif m0.id > m1.id:
		return 1
	elif m0.subid < m1.subid:
		return -1
	elif m0.subid > m1.subid:
		return 1
	else:
		return 0


class ChooserDialog(ModalDialog):

	oneshot = True
	title = "Select Models"
	buttons = (OK, Cancel)

	def __init__(self, ml, mode, setupCB, finishCB, *args, **kw):
		self.modelList = ml
		self.mode = mode
		self.setupCB = setupCB
		self.finishCB = finishCB
		ModalDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		self.frame = parent
		self.modelMCL = MultiColumnListbox(parent, scrollbar_width=8)
		self.modelMCL.addListbox(selectmode=self.mode, width=5)
		self.modelMCL.addListbox(selectmode=self.mode)
		self.modelMCL.pack(side=TOP, fill=BOTH, expand=TRUE)
		self._loadModels()
		if self.setupCB:
			self.setupCB(parent)

	def _loadModels(self):
		for where in range(len(self.modelList)):
			m = self.modelList[where]
			try:
				if m.subid <= 0:
					ident = '%d' % m.id
				else:
					ident = '%d.%d' % (m.id, m.subid)
			except AttributeError:
				ident = '<unnamed>'
			self.modelMCL.listbox(0).insert(where, ident)
			self.modelMCL.listbox(1).insert(where, self._source(m))
		if len(self.modelList) == 1:
			self.modelMCL.select_set(0)

	def _source(self, m):
		try:
			return self._fmtSource(m.infoDict["source"])
		except AttributeError, KeyError:
			try:
				return self._fmtSource(m.name)
			except AttributeError:
				return "<unknown source>"

	def _fmtSource(self, s):
		head, tail = os.path.split(s)
		if head:
			return tail + ' - ' + head
		else:
			return tail

	def selectedList(self):
		selectionList = []
		for s in self.modelMCL.curselection():
			selectionList.append(self.modelList[int(s)])
		return selectionList

	def OK(self):
		if self.finishCB:
			self.finishCB(self.frame)
		ModalDialog.Cancel(self, self.selectedList())
