# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ReorderDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import replyobj
from MAViewer import MOD_ALIGN

class ReorderDialog(ModelessDialog):
	"""Reorder alignment sequences"""

	buttons = ("OK", "Apply", "Close")
	help="ContributedSoftware/multalignviewer/multalignviewer.html#reorder"
	
	def __init__(self, mav, *args, **kw):
		self.mav = mav
		self.title = "Reorder Sequences of %s" % (mav.title,)
		self.handlerID = self.mav.triggers.addHandler(MOD_ALIGN,
						self._alignMod, None)
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		import Pmw, Tkinter
		self.seqs = self.mav.seqs[:]
		self.seqList = Pmw.ScrolledListBox(parent,
					items=[s.name for s in self.seqs])
		self.seqList.setvalue(self.seqs[0].name)
		self.seqList.grid(row=0, column=0, sticky="nsew")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)

		lw = Pmw.LabeledWidget(parent, labelpos='n',
				label_text="Move selected sequence to...")
		bb = lw.interior()
		Tkinter.Button(bb, text="top",
				command=lambda: self.moveSeq("top"), pady=0,
				default='disabled').grid(row=0, column=0)
		Tkinter.Button(bb, text="one higher",
				command=lambda: self.moveSeq("up"), pady=0,
				default='disabled').grid(row=0, column=1)
		Tkinter.Button(bb, text="one lower",
				command=lambda: self.moveSeq("down"), pady=0,
				default='disabled').grid(row=0, column=2)
		Tkinter.Button(bb, text="bottom",
				command=lambda: self.moveSeq("bottom"), pady=0,
				default='disabled').grid(row=0, column=3)
		lw.grid(row=1)

	def destroy(self):
		self.mav.triggers.deleteHandler(MOD_ALIGN, self.handlerID)
		self.mav = None
		ModelessDialog.destroy(self)

	def moveSeq(self, mode):
		index = int(self.seqList.curselection()[0])
		if index == 0 and mode in ['top', 'up'] \
		or index == len(self.seqs) -1 and mode in ['bottom', 'down']:
			return

		if mode == 'top':
			self.seqs = [self.seqs[index]] + self.seqs[:index] \
				+ self.seqs[index+1:]
			newActive = 0
		elif mode == "up":
			self.seqs = self.seqs[:index-1] + [self.seqs[index],
				self.seqs[index-1]] + self.seqs[index+1:]
			newActive = index -1
		elif mode == "down":
			self.seqs = self.seqs[:index] + [self.seqs[index+1],
				self.seqs[index]] + self.seqs[index+2:]
			newActive = index + 1
		else:
			self.seqs = self.seqs[:index] + self.seqs[index+1:] \
				+ [self.seqs[index]]
			newActive = len(self.seqs) - 1

		self.seqList.setlist([s.name for s in self.seqs])
		self.seqList.selection_clear()
		self.seqList.selection_set(newActive)

	def Apply(self):
		self.mav.reorder(self.seqs)

	def _alignMod(self, trigName, myData, newSeqs):
		if self.seqs == newSeqs:
			return
		self.seqs = newSeqs[:]
		self.seqList.setlist([s.name for s in self.seqs])
		self.seqList.setvalue(self.seqs[0].name)

