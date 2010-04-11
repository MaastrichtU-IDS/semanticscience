# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: NumberingsDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import replyobj, UserError
from MAViewer import MOD_ALIGN

class NumberingsDialog(ModelessDialog):
	"""Adjust sequence numberings"""

	buttons = ("OK", "Apply", "Close")
	default = "OK"
	help = "ContributedSoftware/multalignviewer/multalignviewer.html#seqnum"
	
	def __init__(self, mav, *args, **kw):
		self.mav = mav
		self.title = "Adjust Numberings of %s" % (mav.title,)
		self.handlerID = self.mav.triggers.addHandler(MOD_ALIGN,
						self._alignMod, None)
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		import Pmw, Tkinter
		seqNames = [s.name for s in self.mav.seqs]
		self.seqList = Pmw.ScrolledListBox(parent, labelpos='nw',
			label_text="Adjust numbering for:",
			listbox_selectmode="extended", items=seqNames,
			listbox_exportselection=0)
		self.seqList.setvalue(seqNames)
		self.seqList.grid(row=0, column=0, sticky="nsew")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)

		self.numberingEntry = Pmw.EntryField(parent, labelpos='w',
			label_text="Start:", validate="integer", value="1")
		self.numberingEntry.grid(row=1, column=0)

	def destroy(self):
		self.mav.triggers.deleteHandler(MOD_ALIGN, self.handlerID)
		self.mav = None
		ModelessDialog.destroy(self)

	def Apply(self):
		self.numberingEntry.invoke()
		if not self.numberingEntry.valid():
			self.enter()
			raise UserError("Starting number must be an integer")
		start = int(self.numberingEntry.getvalue())
		adjSeqs = [self.mav.seqs[int(i)]
					for i in self.seqList.curselection()]
		if not adjSeqs:
			self.enter()
			raise UserError("No sequences selected for adjustment")
		for seq in adjSeqs:
			seq.numberingStart = start
		self.mav.updateNumberings()

	def _alignMod(self, trigName, myData, newSeqs):
		prevSel = set(self.seqList.getvalue())
		self.seqList.setlist([s.name for s in newSeqs])
		self.seqList.setvalue([s.name for s in newSeqs
						if s.name in prevSel])

