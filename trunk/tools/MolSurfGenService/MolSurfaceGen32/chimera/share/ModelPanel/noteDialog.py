# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: noteDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog

class NoteDialog(ModelessDialog):
	oneshot = True
	buttons = ("OK", "Cancel")

	def __init__(self, models):
		self.models = models
		if len(models) > 1:
			self.title = "Add Note to %d Models" % (len(models))
		else:
			self.title = "Add Note to %s" % models[0].name
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		import Pmw
		self.text = Pmw.ScrolledText(parent,
						text_height=3, text_width=25)
		self.text.grid(sticky="nsew")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)
		initialNote = None
		for m in self.models:
			if hasattr(m, 'note'):
				if initialNote:
					if m.note != initialNote:
						initialNote = None
						break
				elif m.note:
					initialNote = m.note
				else:
					break
			elif initialNote:
				initialNote = None
				break
			else:
				break
		if initialNote:
			self.text.setvalue(initialNote)
		self.text.focus_set()

	def Apply(self):
		liveModels = [m for m in self.models if not m.__destroyed__]
		if not liveModels:
			return
		note = self.text.getvalue().strip()
		track = chimera.TrackChanges.get()
		for m in liveModels:
			if note:
				m.note = note
			elif hasattr(m, "note"):
				delattr(m, "note")
			track.addModified(m, "note changed")
		if note:
			from SimpleSession import registerAttribute
			registerAttribute(chimera.Molecule, "note")
			from base import _mp
			_mp._confDialog.showColumn("Note", True)

