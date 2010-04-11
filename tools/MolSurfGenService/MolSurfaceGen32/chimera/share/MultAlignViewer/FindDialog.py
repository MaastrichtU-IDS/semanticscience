# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: FindDialog.py 27832 2009-06-12 00:37:28Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import replyobj
import Pmw, Tkinter
from MAViewer import MOD_ALIGN

class BaseFindDialog(ModelessDialog):
	buttons = ("OK", "Apply", "Cancel")
	default = "OK"

	def __init__(self, mav, *args, **kw):
		self.mav = mav
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		parent.columnconfigure(0, weight=1)
		self.seqEntry = Pmw.EntryField(parent, labelpos='w',
			label_text=self.entryLabel, validate=self.validate,
			entry_width=10)
		self.seqEntry.grid(row=0, column=0, sticky='ew')
		items = ['all sequences']
		items.extend([s.name for s in self.mav.seqs])
		self.targetMenu = Pmw.OptionMenu(parent, initialitem=0,
				items=items, labelpos='w', label_text='in')
		self.targetMenu.grid(row=0, column=1, sticky='w')
		self.handlerID = self.mav.triggers.addHandler(MOD_ALIGN,
						self._remakeTargetMenu, None)
		self.upcaseVar = Tkinter.IntVar(parent)
		self.upcaseVar.set(self.upcaseDefault)
			
	def destroy(self):
		self.mav.triggers.deleteHandler(MOD_ALIGN, self.handlerID)
		self.mav = None
		ModelessDialog.destroy(self)

	def Apply(self):
		search = self.seqEntry.get().strip()
		if not search:
			replyobj.error("No search value specified\n")
			return
		if self.upcaseVar.get():
			search = search.upper()
		searchRegion = self.mav.regionBrowser.getRegion("search result",
				outline="dodger blue", fill="white", create=1)
		seqIndex = self.targetMenu.index(Pmw.SELECT)
		if seqIndex == 0:
			seqs = self.mav.seqs
		else:
			seqs = [self.mav.seqs[seqIndex-1]]

		matches = []
		searchType, func = self.searchInfo
		self.mav.status("Searching...", blankAfter=0)
		for seq in seqs:
			if searchType == "self":
				seqMatches = eval("self.%s(seq, search)" % func)
			else:
				seqMatches = eval("seq.%s(search)" % func)
			for start, end in seqMatches:
				matches.append([seq, seq, start, end])

		if not matches:
			replyobj.error("No matches found\n")
			return

		if len(matches) > 1:
			msg = "%d matches found" % len(matches)
		else:
			msg = "1 match found"
		self.mav.status(msg)

		searchRegion.clear()
		searchRegion.addBlocks(matches)

		self.mav.regionBrowser.seeRegion(searchRegion)

	def _remakeTargetMenu(self, *args):
		curval = self.targetMenu.getvalue()
		newItems = ['all sequences'] + [s.name for s in self.mav.seqs]
		try:
			newIndex = newItems.index(curval)
		except ValueError:
			newIndex = 0
		self.targetMenu.setitems(newItems, index=newIndex)

class FindDialog(BaseFindDialog):
	"""Find sequence patterns"""

	help = \
	   "ContributedSoftware/multalignviewer/multalignviewer.html#findsub"
	title = "Find Subsequence"
	validate = 'alphabetic'
	entryLabel = "Find subsequence"
	upcaseDefault = True
	searchInfo = ("self", "_seqMatch")

	def fillInUI(self, parent):
		BaseFindDialog.fillInUI(self, parent)
		from chimera.selection.seq import AmbiguityMenu
		self.ambMenu = AmbiguityMenu(parent)
		self.ambMenu.grid(row=1, column=0, columnspan=2)
		checkbox = Tkinter.Checkbutton(parent, variable=self.upcaseVar,
			text="Convert to uppercase before matching")
		checkbox.grid(row=2, column=0, columnspan=2, sticky='w')

	def _seqMatch(self, seq, subseq):
		pattern = self.ambMenu.text2pattern(subseq)
		import re
		expr = re.compile(pattern)
		return seq.patternMatch(expr)

class PrositeDialog(BaseFindDialog):
	"""Find PROSITE patterns"""

	help = \
	   "ContributedSoftware/multalignviewer/multalignviewer.html#findpro"
	title = "Find PROSITE Pattern"
	validate = None
	entryLabel = "Find PROSITE pattern"
	upcaseDefault = False
	searchInfo = ("seq", "prositeMatch")

