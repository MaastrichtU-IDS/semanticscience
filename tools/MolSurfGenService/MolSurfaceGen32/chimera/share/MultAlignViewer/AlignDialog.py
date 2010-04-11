# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: AlignDialog.py 27358 2009-04-21 00:32:47Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from chimera.misc import oslModelCmp
from chimera import replyobj
import Pmw, Tkinter
from MAViewer import MOD_ASSOC
from prefs import MATCH_CUTOFF

class AlignDialog(ModelessDialog):
	"""Dialog that prompts the user to select a structure
	as the reference, and align all other structures onto
	it, using matching residues from the sequence alignment."""

	buttons = ("OK", "Apply", "Cancel")
	help = "ContributedSoftware/multalignviewer/multalignviewer.html" \
							"#superposition"

	def __init__(self, mav, *args, **kw):
		self.mav = mav
		self.title = "Match Structures by Sequence for %s" % mav.title
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		self.refList = Pmw.ScrolledListBox(parent, items=[],
					labelpos="nw",
					label_text="Reference structure:",
					listbox_exportselection=0)
		self.refList.grid(row=0, column=0, sticky="nsew")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)
		self.alignList = Pmw.ScrolledListBox(parent, items=[],
					labelpos="nw",
					label_text="Structures to match:",
					listbox_exportselection=0,
					listbox_selectmode='extended')
		self.alignList.grid(row=0, column=1, sticky="nsew")
		parent.columnconfigure(1, weight=1)

		f = Tkinter.Frame(parent)
		f.grid(row=1, column=0, columnspan=2)

		self.alignConservedVar = Tkinter.IntVar(parent)
		self.alignConservedVar.set(0)
		b = Tkinter.Checkbutton(f,
				text="Match highly conserved residues only",
				variable=self.alignConservedVar)
		b.grid(row=0, column=0, columnspan=2, sticky="w")

		self.useActiveRegionVar = Tkinter.IntVar(parent)
		self.useActiveRegionVar.set(0)
		b = Tkinter.Checkbutton(f,
				text="Match active region only",
				variable=self.useActiveRegionVar)
		b.grid(row=1, column=0, columnspan=2, sticky="w")

		self.pseudoBondsVar = Tkinter.IntVar(parent)
		self.pseudoBondsVar.set(0)
		b = Tkinter.Checkbutton(f,
				text="Use pseudobonds to show matched atoms",
				variable=self.pseudoBondsVar)
		b.grid(row=2, column=0, columnspan=2, sticky="w")

		self.iterateVar = Tkinter.IntVar(parent)
		self.iterateVar.set(0)
		b = Tkinter.Checkbutton(f,
				text="Iterate by pruning long atom pairs",
				variable=self.iterateVar)
		b.grid(row=3, column=0, sticky="w")
		l = Tkinter.Label(f, text="until no pair exceeds")
		l.grid(row=4, column=0, sticky="e")
		self.iterateCutoff = Pmw.EntryField(f, labelpos='e',
					validate='real', entry_width=3,
					value=str(self.mav.prefs[MATCH_CUTOFF]),
					label_text="angstroms")
		self.iterateCutoff.grid(row=4, column=1, sticky="w")

		self.createRegionVar = Tkinter.IntVar(parent)
		self.createRegionVar.set(0)
		b = Tkinter.Checkbutton(f,
				text="Create region showing matched residues",
				variable=self.createRegionVar)
		b.grid(row=5, column=0, sticky="w")

		self.refresh(initial=1)
		self.assocHandlerID = self.mav.triggers.addHandler(MOD_ASSOC,
							self.refresh, None)

	def destroy(self):
		self.mav.triggers.deleteHandler(MOD_ASSOC, self.assocHandlerID)
		self.mav = None
		ModelessDialog.destroy(self)

	def refresh(self, trig1=None, trig2=None, trig3=None, initial=0):
		self.mols = {}
		sortableNames = []
		for mol in self.mav.associations.keys():
			name = self.mav.molName(mol)
			sortableNames.append((mol.oslIdent(), name))
			self.mols[name] = mol
		if len(sortableNames) < 2:
			self.mav._disableAlignDialog()
			return

		sortableNames.sort(oslModelCmp)
		self.names = []
		for osl, name in sortableNames:
			self.names.append(name)

		if initial:
			self.refList.setlist(self.names)
			self.alignList.setlist(self.names)
			if self.names:
				self.refList.setvalue(self.names[0])
				self.alignList.setvalue(self.names)
		else:
			refsels = self.refList.getcurselection()
			alignsels = self.alignList.getcurselection()
			self.refList.setlist(self.names)
			self.alignList.setlist(self.names)
			for refsel in refsels:
				if self.mols.has_key(refsel):
					self.refList.selection_set(
						self.names.index(refsel))
			for alignsel in alignsels:
				if self.mols.has_key(alignsel):
					self.alignList.selection_set(
						self.names.index(alignsel))

	def Apply(self):
		sels = self.refList.getcurselection()
		if len(sels) != 1:
			replyobj.error(
				'Select exactly one reference structure\n')
			return
		refMol = self.mols[sels[0]]
		sels = self.alignList.getcurselection()
		if len(sels) == 0:
			replyobj.error('No structures to match selected\n')
			return
		matchMols = map(lambda n: self.mols[n], sels)
		iterate = self.iterateVar.get()
		if iterate:
			if not self.iterateCutoff.valid():
				replyobj.error(
					"Iterate cutoff value not valid\n")
				self.enter()
				return
			cutoff = float(self.iterateCutoff.getvalue())
			self.mav.prefs[MATCH_CUTOFF] = cutoff
		else:
			cutoff=None
		self.mav.match(refMol, matchMols,
				createRegion=self.createRegionVar.get(),
				makePseudobonds=self.pseudoBondsVar.get(),
				matchConserved=self.alignConservedVar.get(),
				matchActive=self.useActiveRegionVar.get(),
				iterate=iterate, iterateCutoff=cutoff)

		

