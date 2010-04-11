# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: DelSeqsGapsDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import replyobj
from MAViewer import MOD_ALIGN

class DelSeqsGapsDialog(ModelessDialog):
	"""Delete sequences and/or gaps"""

	buttons = ("OK", "Apply", "Close")
	default = "OK"
	help = "ContributedSoftware/multalignviewer/multalignviewer.html#delete"
	
	def __init__(self, mav, *args, **kw):
		self.mav = mav
		self.title = "Delete Sequences/Gaps of %s" % (mav.title,)
		self.handlerID = self.mav.triggers.addHandler(MOD_ALIGN,
						self._alignMod, None)
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		import Pmw, Tkinter
		self.seqList = Pmw.ScrolledListBox(parent, labelpos='nw',
			label_text="Delete selected sequences (if any):",
			listbox_selectmode="extended",
			items=[s.name for s in self.mav.seqs])
		self.seqList.grid(row=0, column=0, sticky="nsew")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)

		self.delGapsVar = Tkinter.IntVar(parent)
		self.delGapsVar.set(True)
		Tkinter.Checkbutton(parent, variable=self.delGapsVar,
			text="Delete all-gap columns").grid(row=1, column=0)

	def destroy(self):
		self.mav.triggers.deleteHandler(MOD_ALIGN, self.handlerID)
		self.mav = None
		ModelessDialog.destroy(self)

	def Apply(self):
		delSeqs = [self.mav.seqs[int(i)]
					for i in self.seqList.curselection()]
		if delSeqs:
			self.mav.deleteSeqs(delSeqs)
		if self.delGapsVar.get():
			self.mav.deleteAllGaps()

	def _alignMod(self, trigName, myData, newSeqs):
		self.seqList.setlist([s.name for s in newSeqs])

