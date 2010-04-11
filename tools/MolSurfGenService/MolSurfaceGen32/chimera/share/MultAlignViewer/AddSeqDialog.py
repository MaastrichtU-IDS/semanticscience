# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: AddSeqDialog.py 29320 2009-11-16 22:49:16Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera import replyobj
from prefs import MATRIX, GAP_OPEN, GAP_EXTEND, \
	USE_SS, SS_MIXTURE, SS_SCORES, HELIX_OPEN, STRAND_OPEN, OTHER_OPEN

class AddSeqDialog(ModelessDialog):
	"""Insert all-gap columns"""

	buttons = ("OK", "Apply", "Close")
	help = "ContributedSoftware/multalignviewer/multalignviewer.html#add"
	
	def __init__(self, mav, *args, **kw):
		self.mav = mav
		self.title = "Add Sequence to %s" % (mav.title,)
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		import Pmw, Tkinter
		self.seqNameEntry = Pmw.EntryField(parent, labelpos='w',
			label_text='Sequence name:', value= "added")
		self.seqNameEntry.grid(row=0, column=0, sticky="ew")

		paramGroup = Pmw.Group(parent, tag_text="Alignment Parameters")
		paramGroup.grid(row=1, column=0)

		import SmithWaterman
		matrixNames = SmithWaterman.matrices.keys()
		matrixNames.sort()
		if self.mav.prefs[MATRIX] in SmithWaterman.matrices:
			initialMatrix = self.mav.prefs[MATRIX]
		else:
			from prefs import defaultMatrix
			if defaultMatrix in SmithWaterman.matrices:
				initialMatrix = defaultMatrix
			else:
				initialMatrix = matrixNames[0]
		self.matrixMenu = Pmw.OptionMenu(paramGroup.interior(),
			command=lambda m: self.mav.prefs.update({MATRIX: m}),
			initialitem=initialMatrix, labelpos='w',
			label_text="Matrix:", items=matrixNames)
		self.matrixMenu.grid(row=0, column=0)

		gapGroup = Pmw.Group(paramGroup.interior(), tag_text="Gaps")
		gapGroup.grid(row=0, column=1)
		self.gapOpenEntry = Pmw.EntryField(gapGroup.interior(),
			labelpos='w', label_text="Opening penalty",
			validate='real', command=lambda : self.mav.prefs.update(
			{GAP_OPEN: float(self.gapOpenEntry.getvalue())}),
			entry_width=2, entry_justify='right',
			value="%g"%(self.mav.prefs[GAP_OPEN]))
		self.gapOpenEntry.grid(row=0, column=0, sticky='w')
		self.gapExtendEntry = Pmw.EntryField(gapGroup.interior(),
			labelpos='w', label_text="Extension penalty",
			validate='real', command=lambda : self.mav.prefs.update(
			{GAP_EXTEND: float(self.gapExtendEntry.getvalue())}),
			entry_width=2, entry_justify='right',
			value="%g"%(self.mav.prefs[GAP_EXTEND]))
		self.gapExtendEntry.grid(row=1, column=0, sticky='w')
		import string
		self.gapCharMenu = Pmw.OptionMenu(gapGroup.interior(), labelpos='w',
			label_text="Character", items=list(string.punctuation),
			initialitem=self.mav.gapChar())
		self.gapCharMenu.grid(row=2, column=0, sticky='w')
		Pmw.alignlabels([self.gapOpenEntry, self.gapExtendEntry,
						self.gapCharMenu], sticky='e')

		Tkinter.Button(paramGroup.interior(), text="Reset to defaults",
			command=self._reset2defaultsCB, pady=0).grid(
			row=1, column=0, columnspan=2)

		self.notebook = nb = Pmw.NoteBook(parent)
		nb.grid(row=2, column=0, sticky="nsew")

		textPage = nb.add("Plain Text")
		self.seqText = Pmw.ScrolledText(textPage, labelpos='nw',
					label_text='Sequence')
		self.seqText.grid(row=0, column=0, sticky="nsew")
		textPage.rowconfigure(0, weight=1)
		textPage.columnconfigure(0, weight=1)

		self.appendVar = Tkinter.IntVar(textPage)
		self.appendVar.set(True)
		Tkinter.Checkbutton(textPage, variable=self.appendVar,
			text="Simply append to alignment if sequence same"
			" length").grid(row=1, column=0)

		structPage = nb.add("From Structure")
		from chimera.widgets import MoleculeChainOptionMenu
		self.chainMenu = MoleculeChainOptionMenu(structPage)
		self.chainMenu.grid(row=0)
		from MatchMaker.gui import SSParams
		self.ssParams = SSParams(structPage, self.mav.prefs,
						useSSCB=self._useSSCB)
		self.ssParams.grid(row=1)
		nb.setnaturalsize()
		nb.configure(raisecommand=self._pageRaised)

	def destroy(self):
		self.mav = None
		ModelessDialog.destroy(self)

	def Apply(self):
		from chimera import UserError
		for entry in [self.seqNameEntry, self.gapOpenEntry,
							self.gapExtendEntry]:
			entry.invoke()
		seqName = self.seqNameEntry.getvalue().strip()
		if not seqName:
			self.enter()
			raise UserError("Must supply a sequence name")
		kw = { 'ssFraction': None, 'ssMatrix': None }
		if self.notebook.getcurselection() == "Plain Text":
			import string
			seqString = "".join([c
					for c in self.seqText.getvalue().upper()
					if c not in string.whitespace])
			if not seqString:
				self.enter()
				raise UserError(
					"Must supply contents of sequence")

			seq = chimera.Sequence.Sequence(seqName)
			seq.extend(seqString)
			if self.appendVar.get() \
			and len(seq) == len(self.mav.seqs[0]):
				self.mav.addSeqs([seq])
				return
		else:
			seq = self.chainMenu.getvalue()
			if not seq:
				raise UserError("No structure sequence")
			if self.ssParams.useSSVar.get():
				kw['ssFraction'] = self.ssParams.ssMixture.get()
				kw['ssMatrix'] = self.ssParams.getMatrix()
				hg, sg, og = self.ssParams.getGaps()
				(kw['gapOpenHelix'], kw['gapOpenStrand'],
					kw['gapOpenOther']) = (0-hg, 0-sg, 0-og)
			if seq.molecule in self.mav.associations:
				self.mav.disassociate(seq.molecule)
		self.mav.alignSeq(seq, displayName=seqName,
				matrix=self.mav.prefs[MATRIX],
				gapChar=self.gapCharMenu.getvalue(),
				scoreGapOpen=0-self.mav.prefs[GAP_OPEN],
				scoreGap=0-self.mav.prefs[GAP_EXTEND], **kw)

	def _chainMenuCB(self, chain):
		if chain:
			self.seqNameEntry.setvalue(chain.molecule.name)
		else:
			self.seqNameEntry.setvalue("added")

	def _pageRaised(self, newPage):
		if newPage == "Plain Text":
			self.seqNameEntry.setvalue("added")
			self.chainMenu.configure(command=None)
			self.gapOpenEntry.configure(label_state="normal",
						entry_state="normal")
		else:
			self.chainMenu.configure(command=self._chainMenuCB)
			if self.chainMenu.getvalue():
				self.chainMenu.invoke()
			self._useSSCB()

	def _reset2defaultsCB(self):
		import SmithWaterman
		from prefs import defaults, MATRIX, GAP_OPEN, GAP_EXTEND
		if defaults[MATRIX] in SmithWaterman.matrices:
			self.matrixMenu.setvalue(defaults[MATRIX])
		self.gapOpenEntry.setvalue(str(defaults[GAP_OPEN]))
		self.gapExtendEntry.setvalue(str(defaults[GAP_EXTEND]))
		self.gapCharMenu.setvalue(self.mav.gapChar())

	def _useSSCB(self):
		if self.ssParams.useSSVar.get():
			state = 'disabled'
		else:
			state = 'normal'
		self.gapOpenEntry.configure(label_state=state,entry_state=state)
