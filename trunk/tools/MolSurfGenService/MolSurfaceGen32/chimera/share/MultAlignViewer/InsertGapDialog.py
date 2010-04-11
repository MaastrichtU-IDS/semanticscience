# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: InsertGapDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import replyobj

class InsertGapDialog(ModelessDialog):
	"""Insert all-gap columns"""

	buttons = ("OK", "Apply", "Close")
	help = "ContributedSoftware/multalignviewer/multalignviewer.html#insert"
	
	def __init__(self, mav, *args, **kw):
		self.mav = mav
		self.title = "Insert Gaps in %s" % (mav.title,)
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		import Pmw
		self.amountEntry = Pmw.EntryField(parent, labelpos='w',
			label_text="Insert", validate={ 'validator': 'numeric',
			'min': 1, 'minstrict': False }, value='5',
			entry_width=2, entry_justify='right')
		self.amountEntry.grid(row=0, column=0)

		self.positionEntry = Pmw.EntryField(parent, labelpos='w',
			label_text="-column gap after column", validate={
				'validator': 'numeric', 'minstrict': False
			}, value='0', entry_width=4, entry_justify='left')
		self.positionEntry.grid(row=0, column=1)

		import string
		self.gapCharMenu = Pmw.OptionMenu(parent, initialitem='.',
				items=string.punctuation, labelpos='w',
				label_text="Gap character:")
		self.gapCharMenu.grid(row=1, column=0, columnspan=2)

	def destroy(self):
		self.mav = None
		ModelessDialog.destroy(self)

	def Apply(self):
		for entry in [self.amountEntry, self.positionEntry]:
			entry.invoke()
		if not self.amountEntry.valid():
			self.enter()
			raise UserError("Gap size must be a number greater"
				" than zero")
		if not self.positionEntry.valid():
			self.enter()
			raise UserError("Gap position must be an integer")

		self.mav.insertGap(int(self.amountEntry.getvalue()),
					int(self.positionEntry.getvalue()),
					gapChar=self.gapCharMenu.getvalue())
