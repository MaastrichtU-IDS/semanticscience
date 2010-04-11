# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: AddSeqDialog.py 27358 2009-04-21 00:32:47Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import replyobj
from MAViewer import ADDDEL_SEQS

class BlastPdbDialog(ModelessDialog):
	"""Blast sequence"""

	buttons = ("OK", "Apply", "Close")
	default = "OK"
	title = "Blast Sequence"
	#help = "ContributedSoftware/multalignviewer/multalignviewer.html#blast"
	
	def __init__(self, mav, *args, **kw):
		self.mav = mav
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		import Pmw, Tkinter
		self.menu = Pmw.OptionMenu(parent, labelpos='w',
			label_text="Blast", items=[s.name for s in self.mav.seqs])
		self.menu.grid()
		self.handlerID = self.mav.triggers.addHandler(ADDDEL_SEQS,
						self._seqsChangeCB, None)
	def destroy(self):
		self.mav.triggers.deleteHandler(ADDDEL_SEQS, self.handlerID)
		self.mav = None
		ModelessDialog.destroy(self)

	def Apply(self):
		import Pmw
		index = self.menu.index(Pmw.SELECT)
		seq = self.mav.seqs[index]
		self.mav.blast(seq)

	def _seqsChangeCB(self, trigName, d1, d2):
		curItem = self.menu.getvalue()
		items = [s.name for s in self.mav.seqs]
		if curItem not in items:
			curItem=None
		self.menu.setitems(items, index=curItem)

