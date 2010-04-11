# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 29667 2009-12-18 23:13:40Z pett $

from chimera.baseDialog import ModelessDialog, ModalDialog
from chimera import openModels, Molecule, replyobj, UserError
import chimera
from chimera.widgets import MoleculeScrolledListBox, \
			MoleculeChainScrolledListBox, MoleculeChainOptionMenu
import Pmw, Tkinter
import NeedlemanWunsch
import SmithWaterman

from MatchMaker import align, match, CP_SPECIFIC_SPECIFIC, CP_SPECIFIC_BEST, \
	CP_BEST, SA_NEEDLEMAN_WUNSCH, SA_SMITH_WATERMAN
from prefs import prefs, defaults, CHAIN_PAIRING, SEQUENCE_ALGORITHM, \
	SHOW_SEQUENCE, MATRIX, GAP_OPEN, GAP_EXTEND, USE_SS, SS_MIXTURE, \
	SS_SCORES, ITERATE, ITER_CUTOFF, HELIX_OPEN, STRAND_OPEN, OTHER_OPEN, \
	COMPUTE_SS

class MatchMaker(ModelessDialog):
	name = "match structures"
	buttons = ('OK', 'Apply', 'Cancel')
	title = "MatchMaker"
	help = 'ContributedSoftware/matchmaker/matchmaker.html'

	def __init__(self, **kw):
		ModelessDialog.__init__(self, **kw)

	def Apply(self):
		cp = self.chainMatchVar.get()
		alg = self.seqAlgorithmMenu.getvalue()
		showSeq = self.showSeqVar.get()
		iterate = self.iterVar.get()
		computeSS = self.computeSSVar.get()
		for entry in self._entries:
			entry.invoke()
		if iterate:
			iterArg = float(self.iterEntry.getvalue())
		else:
			iterArg = None
		helixOpen, strandOpen, otherOpen = self.ssParams.getGaps()
		matrix = self.matrixMenu.getvalue()
		gapOpen = float(self.gapOpenEntry.getvalue())
		gapExtend = float(self.gapExtendEntry.getvalue())

		pairings = {}
		if cp == CP_SPECIFIC_SPECIFIC:
			matchItems = []
			for ref, menu in self.matchChainList.menus.items():
				matchItems.append((ref, menu.getvalue()))
		elif cp == CP_SPECIFIC_BEST:
			# specific chain in reference;
			# best seq-aligning chain in match model(s)
			ref = self.refChainList.getvalue()
			if not ref:
				raise UserError("Must choose a reference chain")
			matches = [ x for x in self.matchMolList.getvalue()
				if x != ref.molecule ]
			matchItems = [ref, matches]
		elif cp == CP_BEST:
			# best seq-aligning pair of chains between
			# reference and match structure(s)
			ref = self.refMolList.getvalue()
			matches = [ x for x in self.matchMolList.getvalue()
				if x != ref ]
			matchItems = [ref, matches]

		if self.ssParams.useSSVar.get():
			ssFraction = self.ssParams.ssMixture.get()
			ssMatrix = self.ssParams.getMatrix()
		else:
			ssMatrix = ssFraction = None
		alignKw = { 'ssFraction': ssFraction, 'ssMatrix': ssMatrix,
					'computeSS': computeSS }
		try:
			matchInfo = match(cp, matchItems, matrix, alg, gapOpen,
				gapExtend, align=self._align,
				iterate=iterArg, gapOpenHelix=helixOpen,
				gapOpenStrand=strandOpen,
				gapOpenOther=otherOpen,
				showAlignment=showSeq, **alignKw)
		except UserError:
			self.enter()
			raise

		if not self.structSeqVar.get():
			return
		chains = set()
		for matchAtoms, refAtoms, rmsd in matchInfo:
			for r in (matchAtoms[0].residue, refAtoms[0].residue):
				for mchain in  r.molecule.sequences():
					if r in mchain.resMap:
						chains.add(mchain)
						break
		from StructSeqAlign import Match2Align
		m2a = Match2Align()
		m2a.chainList.setvalue(chains)

	def fillInUI(self, parent):
		self.refMolList = MoleculeScrolledListBox(parent,
				autoselect="single", labelpos="nw",
				label_text="Reference structure:")
		self.refChainList = MoleculeChainScrolledListBox(parent,
			labelpos="nw", label_text="Reference chain:",
			listbox_selectmode='extended')

		self.matchMolList = MoleculeScrolledListBox(parent,
			labelpos="nw", label_text="Structure(s) to match:",
			listbox_selectmode='extended')
		self.matchChainList = ChainMenus(parent)
		def doSync():
			if self.chainMatchVar.get() != CP_SPECIFIC_SPECIFIC:
				return
			self.matchChainList.syncUp(self.refChainList)
		self.refChainList.configure(selectioncommand=doSync)
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)
		parent.columnconfigure(1, weight=1)

		seqFrame = Tkinter.Frame(parent)
		seqFrame.grid(row=1, column=0, columnspan=2, sticky="nsew")
		seqFrame.columnconfigure(0, weight=1)
		seqFrame.columnconfigure(1, weight=1)

		pairingGroup = Pmw.Group(seqFrame, tag_text="Chain pairing")
		pairingGroup.grid(row=0, column=0, columnspan=2, sticky="w",
								padx=2)
		pairingGroup.interior().columnconfigure(0, weight=1)

		self.chainMatchVar = Tkinter.StringVar(parent)
		self.chainMatchVar.set(prefs[CHAIN_PAIRING])

		radiobuttonInfo = [
			(CP_BEST, "Best-aligning pair of chains\n\tbetween reference and match structure"),
			(CP_SPECIFIC_BEST, "Specific chain in reference structure\n\twith best-aligning chain in match structure"),
			(CP_SPECIFIC_SPECIFIC, "Specific chain(s) in reference structure\n\twith specific chain(s) in match structure"),
		]
		for i in range(len(radiobuttonInfo)):
			val, text = radiobuttonInfo[i]
			radio = Tkinter.Radiobutton(pairingGroup.interior(),
					command=self._chainMatchCB, text=text,
					justify='left',
					value=val, variable=self.chainMatchVar)
			radio.grid(row=i, column=0, sticky='w')
		self._chainMatchCB()

		self.seqAlgorithmMenu = Pmw.OptionMenu(seqFrame,
			initialitem=prefs[SEQUENCE_ALGORITHM], labelpos='w',
			label_text="Alignment algorithm:",
			items=[SA_NEEDLEMAN_WUNSCH, SA_SMITH_WATERMAN])
		self.seqAlgorithmMenu.grid(row=1, column=0, sticky='w')

		matrixNames = SmithWaterman.matrices.keys()
		matrixNames.sort()
		if prefs[MATRIX] in SmithWaterman.matrices:
			initialMatrix = prefs[MATRIX]
		else:
			if defaults[MATRIX] in SmithWaterman.matrices:
				initialMatrix = defaults[MATRIX]
			else:
				initialMatrix = matrixNames[0]
			prefs[MATRIX] = initialMatrix
		self.matrixMenu = Pmw.OptionMenu(seqFrame,
			initialitem=initialMatrix, labelpos='w',
			label_text="Matrix:", items=matrixNames)
		self.matrixMenu.grid(row=1, column=1, sticky='w')

		gapFrame = Tkinter.Frame(seqFrame)
		gapFrame.grid(row=2, column=0, columnspan=2, sticky='ew')
		gapFrame.columnconfigure(0, weight=1)
		gapFrame.columnconfigure(1, weight=1)
		self.gapOpenEntry = Pmw.EntryField(gapFrame, labelpos='w',
			label_text="Gap opening penalty", validate='real',
			entry_width=2,
			entry_justify='right', value="%g"%(prefs[GAP_OPEN]))
		self.gapOpenEntry.grid(row=0, column=0)
		self.gapExtendEntry = Pmw.EntryField(gapFrame, labelpos='w',
			label_text="Gap extension penalty", validate='real',
			entry_width=2,
			entry_justify='right', value="%g"%(prefs[GAP_EXTEND]))
		self.gapExtendEntry.grid(row=0, column=1)
		self._entries = [self.gapOpenEntry, self.gapExtendEntry]

		self.ssParams = SSParams(seqFrame, prefs, useSSCB=self._useSSCB)
		self.ssParams.grid(row=3, column=0, columnspan=2, sticky='ew')
		self.computeSSVar = Tkinter.IntVar(parent)
		self.computeSSVar.set(prefs[COMPUTE_SS])
		self._computeSSButton = Tkinter.Checkbutton(seqFrame,
			text="Compute secondary structure assignments",
			variable=self.computeSSVar)
		self._computeSSGridArgs = { 'row': 4, 'sticky': 'w',
							'columnspan': 2 }
		if self.ssParams.useSSVar.get():
			self._computeSSButton.grid(**self._computeSSGridArgs)

		self.showSeqVar = Tkinter.IntVar(parent)
		self.showSeqVar.set(prefs[SHOW_SEQUENCE])
		Tkinter.Checkbutton(seqFrame, text="Show pairwise alignment(s)",
				variable=self.showSeqVar).grid(
				row=5, column=0, sticky='w', columnspan=2)

		matchGroup = Pmw.Group(parent, tag_text="Matching")
		matchGroup.grid(row=2, column=0, columnspan=2, sticky="nsew",
								padx=2)
		matchGroup.interior().columnconfigure(0, weight=1)
		self.iterVar = Tkinter.IntVar(parent)
		self.iterVar.set(prefs[ITERATE])
		Tkinter.Checkbutton(matchGroup.interior(), justify="left",
			text="Iterate by pruning long atom pairs"
			" until no pair exceeds:", variable=self.iterVar).grid(
			row=0, column=0, sticky='w')
		self.iterEntry = Pmw.EntryField(matchGroup.interior(),
			validate='real', entry_width=3, entry_justify="right",
			value="%.1f" % prefs[ITER_CUTOFF], labelpos='e',
			label_text="angstroms")
		self.iterEntry.grid(row=1, column=0)
		self._entries.append(self.iterEntry)

		self.structSeqVar = Tkinter.IntVar(parent)
		self.structSeqVar.set(False)
		Tkinter.Checkbutton(parent, text="After superposition, compute"
			" structure-based multiple sequence alignment",
			variable=self.structSeqVar).grid(row=3, sticky='w',
			columnspan=2)

		f = Tkinter.Frame(parent)
		f.grid(row=4, column=0, columnspan=2, sticky='ew')
		from chimera import help
		b = Tkinter.Button(f, text="Save settings", pady=0,
						command=self._saveSettings)
		b.grid(row=0, column=0)
		help.register(b, balloon="Save current settings")
		b = Tkinter.Button(f, text="Reset to defaults", pady=0,
						command=self._restoreSettings)
		b.grid(row=0, column=1)
		help.register(b, balloon="Reset dialog to factory defaults")
		f.columnconfigure(0, weight=1)
		f.columnconfigure(1, weight=1)

		# set up state of gap-open entry
		self._useSSCB()

	def _align(self, ref, match, matrix, alg, gapOpen, gapExtend,
							ksdsspCache, **alignKw):
		replyobj.status("test match %s %s to %s %s" % (
					ref.molecule.name, ref.name,
					match.molecule.name, match.name))
		return align(ref, match, matrix, alg, gapOpen, gapExtend,
							ksdsspCache, **alignKw)

	def _chainMatchCB(self):
		matching = self.chainMatchVar.get()
		if matching == CP_SPECIFIC_SPECIFIC:
			ref = self.refChainList
			match = self.matchChainList
			ref.component("listbox").config(selectmode="extended")
			self.matchChainList.syncUp(self.refChainList)
		elif matching == CP_SPECIFIC_BEST:
			ref = self.refChainList
			match = self.matchMolList
			ref.component("listbox").config(selectmode="browse")
		else:
			ref = self.refMolList
			match = self.matchMolList
		for slave in self.uiMaster().grid_slaves(row=0):
			slave.grid_forget()
		ref.grid(row=0, column=0, sticky="nsew")
		match.grid(row=0, column=1, sticky="nsew")

	def _restoreSettings(self):
		self.ssParams.resetParams()
		self.chainMatchVar.set(defaults[CHAIN_PAIRING])
		self._chainMatchCB()
		self.seqAlgorithmMenu.setvalue(defaults[SEQUENCE_ALGORITHM])
		self.showSeqVar.set(defaults[SHOW_SEQUENCE])
		self.iterVar.set(defaults[ITERATE])
		self.computeSSVar.set(defaults[COMPUTE_SS])
		for entry in self._entries:
			entry.invoke()
		self.iterEntry.setvalue(str(defaults[ITER_CUTOFF]))
		self.ssParams.useSSVar.set(defaults[USE_SS])
		self.matrixMenu.setvalue(defaults[MATRIX])
		self.gapOpenEntry.setvalue(str(defaults[GAP_OPEN]))
		self.gapExtendEntry.setvalue(str(defaults[GAP_EXTEND]))
		self.structSeqVar.set(False)

	def _saveSettings(self):
		prefs[CHAIN_PAIRING] = self.chainMatchVar.get()
		prefs[SEQUENCE_ALGORITHM] = self.seqAlgorithmMenu.getvalue()
		prefs[SHOW_SEQUENCE] = self.showSeqVar.get()
		prefs[ITERATE] = self.iterVar.get()
		prefs[COMPUTE_SS] = self.computeSSVar.get()
		for entry in self._entries:
			entry.invoke()
		prefs[ITER_CUTOFF] = float(self.iterEntry.getvalue())
		prefs[HELIX_OPEN], prefs[STRAND_OPEN], prefs[OTHER_OPEN] = \
						self.ssParams.getGaps()
		prefs[USE_SS] = self.ssParams.useSSVar.get()
		prefs[SS_MIXTURE] = self.ssParams.ssMixture.get()
		ssMatrix = self.ssParams.getMatrix()
		if ssMatrix != prefs[SS_SCORES]:
			prefs[SS_SCORES] = ssMatrix
		prefs[MATRIX] = self.matrixMenu.getvalue()
		prefs[GAP_OPEN] = float(self.gapOpenEntry.getvalue())
		prefs[GAP_EXTEND] = float(self.gapExtendEntry.getvalue())

	def _useSSCB(self):
		if self.ssParams.useSSVar.get():
			state = 'disabled'
			self._computeSSButton.grid(**self._computeSSGridArgs)
		else:
			state = 'normal'
			self._computeSSButton.grid_forget()
		self.gapOpenEntry.configure(label_state=state,entry_state=state)

class ChainMenus(Tkinter.Frame):
	def __init__(self, master, **kw):
		self.menus = {}
		Tkinter.Frame.__init__(self, master, **kw)
		self.labeledFrame = Pmw.LabeledWidget(self, labelpos="nw",
					label_text="Chain(s) to match:")
		self.labeledFrame.grid(row=0, column=0, sticky="nsew")
		self.rowconfigure(0, weight=1)
		self.columnconfigure(0, weight=1)
		self.emptyLabel = Tkinter.Label(self.labeledFrame.interior(),
				text="Choose reference chain(s)")
		self.emptyLabel.grid()

	def syncUp(self, refChains):
		if not self.menus:
			self.emptyLabel.grid_forget()
		row = 0
		newMenus = {}
		for rc in refChains.getvalue():
			if rc in self.menus:
				menu = self.menus[rc]
				menu.grid_forget()
				del self.menus[rc]
			else:
				menu = MoleculeChainOptionMenu(
					self.labeledFrame.interior(),
					labelpos='nw', label_text="ref: %s"
					% refChains.valueMap[rc])
			newMenus[rc] = menu
			menu.grid(row=row, column=0)
			self.labeledFrame.interior().rowconfigure(row, weight=1)
			row += 1
		oldValues = []
		for old in self.menus.values():
			old.grid_forget()
			oldValues.append(old.getvalue())
		self.menus = newMenus
		if not self.menus:
			self.emptyLabel.grid()
		elif len(oldValues) == len(self.menus) == 1:
			# ref chain switched, try to retain match chain value if possible
			try:
				self.menus.values()[0].setvalue(oldValues[0])
			except:
				pass

class SSParams(Tkinter.Frame):
	def __init__(self, parent, prefs, useSSCB=None):
		Tkinter.Frame.__init__(self, parent)
		self.columnconfigure(1, weight=1)
		self.useSSVar = Tkinter.IntVar(parent)
		self.useSSVar.set(prefs[USE_SS])
		self._ssTextVar = Tkinter.StringVar(parent)
		Tkinter.Checkbutton(self, textvariable=self._ssTextVar,
				command=useSSCB, variable=self.useSSVar
				).grid(row=0, column=0)
		self._ssButTexts = [ "Show parameters", "Hide parameters" ]
		self._ssParamButton = Tkinter.Button(self,
					text=self._ssButTexts[0], pady=0,
					command=self._hideShowSSParams)
		self._ssParamButton.grid(row=0, column=1, sticky='w')
		self._ssParamFrame = Tkinter.Frame(self)
		self.ssMixture = Tkinter.Scale(self._ssParamFrame, from_=0.0,
			to_=1.0, orient="horizontal", command=self._ssSetText,
			resolution=0.01, showvalue=True)
		self.ssMixture.set(prefs[SS_MIXTURE])
		self._ssSetText(self.ssMixture.get())
		self.ssMixture.grid(row=0, column=0, columnspan=2, sticky='sew')
		self._ssParamFrame.columnconfigure(0, weight=1)
		Tkinter.Label(self._ssParamFrame, text="Residue\nSimilarity",
			justify="left").grid(row=1, column=0, sticky='nw')
		Tkinter.Label(self._ssParamFrame, text="Secondary\nStructure",
			justify="right").grid(row=1, column=1, sticky='ne')
		ssMatrixGroup = Pmw.Group(self._ssParamFrame,
						tag_text="Scoring matrix")
		ssMatrixGroup.grid(row=0, column=2, rowspan=2)
		labels = ("Helix", "Strand", "Other")
		interior = ssMatrixGroup.interior()
		for i, text in enumerate(labels):
			Tkinter.Label(interior, text=text).grid(row=i+1,
							column=0, sticky='e')
			Tkinter.Label(interior, text=text[0]).grid(row=0,
								column=i+1)
		ssMatrix = prefs[SS_SCORES]
		self._entryMatrix = {}
		for r, rtext in enumerate(labels):
			for c, ctext in enumerate(labels):
				if c > r:
					Tkinter.Label(interior, text="-").grid(
							row=r+1, column=c+1)
					continue
				rlet = rtext[0]
				clet = ctext[0]
				entry = Pmw.EntryField(interior,
					validate='real', entry_width=3,
					entry_justify='right',
					value="%g" % (ssMatrix[(rlet, clet)]))
				entry.grid(row=r+1, column=c+1)
				self._entryMatrix[(rlet, clet)] = entry
				self._entryMatrix[(clet, rlet)] = entry

		gapOpenFrame = Tkinter.Frame(self._ssParamFrame)
		gapOpenFrame.grid(row=2, column=0, columnspan=3, sticky='ew')

		Tkinter.Label(gapOpenFrame, text="Gap opening penalties:").grid(
						row=0, column=0, sticky='w')
		self._hgapEntry = Pmw.EntryField(gapOpenFrame, validate='real',
			entry_width=2, value="%g" % prefs[HELIX_OPEN],
			labelpos='w', label_text="Intra-helix:")
		self._hgapEntry.grid(row=1, column=0)
		self._sgapEntry = Pmw.EntryField(gapOpenFrame, validate='real',
			entry_width=2, value="%g" % prefs[STRAND_OPEN],
			labelpos='w', label_text="Intra-strand:")
		self._sgapEntry.grid(row=1, column=1)
		self._ogapEntry = Pmw.EntryField(gapOpenFrame, validate='real',
			entry_width=2, value="%g" % prefs[OTHER_OPEN],
			labelpos='w', label_text="Any other:")
		self._ogapEntry.grid(row=1, column=2)
		for col in range(3):
			gapOpenFrame.columnconfigure(col, weight=1)

		Tkinter.Button(self._ssParamFrame, text="Reset secondary"
			" structure scoring parameters to defaults", pady=0,
			command=self.resetParams).grid(row=3, column=0,
							columnspan=3)
	def getGaps(self):
		vals = []
		for entry in (self._hgapEntry, self._sgapEntry,
							self._ogapEntry):
			entry.invoke()
			vals.append(float(entry.getvalue()))
		return vals

	def getMatrix(self):
		ssMatrix = {}
		for key, entry in self._entryMatrix.items():
			entry.invoke()
			v = float(entry.getvalue())
			ssMatrix[key] = v
			ssMatrix[(key[1], key[0])] = v
		return ssMatrix

	def resetParams(self):
		self.ssMixture.set(defaults[SS_MIXTURE])
		self._ssSetText(self.ssMixture.get())
		for key, value in defaults[SS_SCORES].items():
			self._entryMatrix[key].setvalue(str(value))
		self._hgapEntry.setvalue(str(defaults[HELIX_OPEN]))
		self._sgapEntry.setvalue(str(defaults[STRAND_OPEN]))
		self._ogapEntry.setvalue(str(defaults[OTHER_OPEN]))

	def _hideShowSSParams(self):
		if self._ssParamFrame.winfo_ismapped():
			self._ssParamFrame.grid_forget()
			self._ssParamButton.configure(text=self._ssButTexts[0])
		else:
			self._ssParamFrame.grid(row=1, column=0, columnspan=2,
							sticky='ew')
			self._ssParamButton.configure(text=self._ssButTexts[1])

	def _ssSetText(self, val):
		self._ssTextVar.set("Include secondary structure score"
					" (%d%%)" % int(100 * float(val)))


from chimera import dialogs
dialogs.register(MatchMaker.name, MatchMaker)
