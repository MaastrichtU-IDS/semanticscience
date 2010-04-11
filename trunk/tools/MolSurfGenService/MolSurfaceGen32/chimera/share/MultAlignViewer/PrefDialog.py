from chimera.baseDialog import ModelessDialog
from prefs import SINGLE_PREFIX
from prefs import WRAP, WRAP_IF, LINE_WIDTH, WRAP_THRESHOLD, BLOCK_SPACE
from prefs import FONT_SIZE, FONT_NAME, BOLD_ALIGNMENT
from prefs import COLUMN_SEP, LINE_SEP, TEN_RES_GAP
from prefs import SEQ_NAME_ELLIPSIS, REGION_NAME_ELLIPSIS
from prefs import LOAD_PDB_NAME_EXACT, LOAD_PDB_NAME_START, \
	LOAD_PDB_NAME_NCBI, LOAD_PDB_NAME_VARSTART, LOAD_SCOP, \
	LOAD_PDB_NAME_VARSTART_VAL, \
	LOAD_PDB_AUTO, LOAD_PDB_DO_LIMIT, LOAD_PDB_LIMIT, \
	ASSOC_ERROR_RATE, \
	SHOW_SEL, SEL_REGION_BORDER, SEL_REGION_INTERIOR, \
	NEW_REGION_BORDER, NEW_REGION_INTERIOR, \
	SHOW_CONSERVATION_AT_STARTUP, SHOW_CONSENSUS_AT_STARTUP, \
	SHOW_RULER_AT_STARTUP, \
	MATCH_REG_ACTIVE, MATCH_REG_EDGE, MATCH_REG_FILL, \
	ERROR_REG_ACTIVE, ERROR_REG_EDGE, ERROR_REG_FILL, \
	GAP_REG_ACTIVE, GAP_REG_EDGE, GAP_REG_FILL
from prefs import CONSERVATION_STYLE, CSV_PERCENT
from prefs import CONSENSUS_STYLE, CSN_MAJ_GAP
from prefs import RESIDUE_COLORING, RC_BLACK, RC_CLUSTALX, RC_RIBBON, \
	RC_CUSTOM_SCHEMES
from chimera import replyobj, tkoptions, UserError
import Tkinter
import Pmw
import os.path

class PrefDialog(ModelessDialog):

	help = \
	"ContributedSoftware/multalignviewer/multalignviewer.html#mavprefs"
	tabs = ["Appearance", "Structure", "Headers", "Regions"]
	provideStatus = True
	statusPosition = "left"

	def __init__(self, mav):
		self.mav = mav
		self.title = "Preferences for %s" % mav.title
		ModelessDialog.__init__(self)
	
	def fillInUI(self, parent):
		self.Close()

		self._entryWidgets = []

		self.notebook = Pmw.NoteBook(parent)
		for tab in self.tabs:
			page = self.notebook.add(tab)
			from chimera.baseDialog import buttonFuncName
			exec("self._add%sPage(page)" % buttonFuncName(tab))
		self.notebook.grid(row=0, column=0, sticky="nsew")
		self.notebook.setnaturalsize()

	def Apply(self):
		for entryWidget in self._entryWidgets:
			if entryWidget.valid():
				entryWidget.invoke()
		ModelessDialog.Apply(self)

	def addColorScheme(self, colorFile, makeDefault):
		if colorFile not in self.mav.prefs[RC_CUSTOM_SCHEMES]:
			self.mav.prefs[RC_CUSTOM_SCHEMES] = \
				self.mav.prefs[RC_CUSTOM_SCHEMES] + [colorFile]
			self._resColorOpt.values.append(colorFile)
			self._resColorOpt.labels.append(
						os.path.basename(colorFile))
			self._resColorOpt.remakeMenu()
		if makeDefault and len(self.mav.seqs) > 1:
			self.mav.prefs[RESIDUE_COLORING] = colorFile
			self._resColorOpt.set(colorFile)

	def _newRegionEllipsis(self, opt):
		newVal = opt.get()
		if newVal == self.mav.prefs[REGION_NAME_ELLIPSIS]:
			return
		self.mav.prefs[REGION_NAME_ELLIPSIS] = newVal
		rb = self.mav.regionBrowser
		rb._rebuildListing(rb.selected())

	def _newSeqEllipsis(self, opt):
		newVal = opt.get()
		if newVal == self.mav.prefs[SEQ_NAME_ELLIPSIS]:
			return
		self.mav.prefs[SEQ_NAME_ELLIPSIS] = newVal
		self.mav.seqCanvas._reformat()

	def _addAppearancePage(self, page):
		page.columnconfigure(3, weight=1)
		page.columnconfigure(1, minsize='0.05i')
		page.rowconfigure(1, weight=1)

		alignmentGroup = Pmw.Group(page, tag_text="Multiple alignments")
		alignmentGroup.grid(row=0, column=0, sticky='n')
		agFrame = alignmentGroup.interior()
		WrapGroup(agFrame, self, "", self.mav.seqCanvas._newWrap).grid(
								row=0, column=0, sticky="nsew")

		FontGroup(agFrame, self, "", self.mav.seqCanvas._newFont).grid(
								row=1, column=0, sticky="nsew")

		SpacingGroup(agFrame, self, "", self.mav.seqCanvas._reformat).grid(
								row=2, column=0, sticky="nsew")

		ResColoringGroup(agFrame, self, "", self.mav.seqCanvas.setColorFunc
						).grid(row=3, column=0, sticky='nsew')

		singleSeqGroup = Pmw.Group(page, tag_text="Single sequences")
		singleSeqGroup.grid(row=0, column=2, sticky='n')
		ssgFrame = singleSeqGroup.interior()
		WrapGroup(ssgFrame, self, SINGLE_PREFIX, self.mav.seqCanvas._newWrap
			).grid(row=0, column=0, sticky="nsew")

		FontGroup(ssgFrame, self, SINGLE_PREFIX, self.mav.seqCanvas._newFont
			).grid(row=1, column=0, sticky="nsew")

		SpacingGroup(ssgFrame, self, SINGLE_PREFIX, self.mav.seqCanvas._reformat
			).grid(row=2, column=0, sticky="nsew")

		ResColoringGroup(ssgFrame, self, SINGLE_PREFIX,
			self.mav.seqCanvas.setColorFunc).grid(
			row=3, column=0, sticky='nsew')

		seqNameGroup = Pmw.Group(page, tag_text="Sequence names")
		seqNameGroup.grid(row=1, column=0, columnspan=3)
		tkoptions.IntOption(seqNameGroup.interior(), 0,
			"Use ellipsis for names longer than",
			self.mav.prefs[SEQ_NAME_ELLIPSIS], self._newSeqEllipsis,
			width=3, min=4)

	def _addRegionsPage(self, page):
		def showSelChange(opt):
			self.mav.prefs[SHOW_SEL] = opt.get()
			self.mav.regionBrowser._showSelCB()

		tkoptions.BooleanOption(page, 0,
					"Show Chimera selection as region",
					self.mav.prefs[SHOW_SEL], showSelChange)

		def selColorChange(opt, prefName):
			val = opt.get()
			self.mav.prefs[prefName] = val
			from RegionBrowser import SEL_REGION_NAME
			selRegion = self.mav.regionBrowser.getRegion(
								SEL_REGION_NAME)
			if selRegion:
				if prefName == SEL_REGION_BORDER:
					selRegion.setBorderRGBA(val)
				else:
					selRegion.setInteriorRGBA(val)
				
		tkoptions.RGBAOption(page, 1,
			"Chimera selection region border color",
			self.mav.prefs[SEL_REGION_BORDER],
			lambda o: selColorChange(o, SEL_REGION_BORDER))
		tkoptions.RGBAOption(page, 2,
			"Chimera selection region interior color",
			self.mav.prefs[SEL_REGION_INTERIOR],
			lambda o: selColorChange(o, SEL_REGION_INTERIOR))

		tkoptions.RGBAOption(page, 3, "New region border color",
			self.mav.prefs[NEW_REGION_BORDER], lambda o:
			self.mav.prefs.update({NEW_REGION_BORDER: o.get()}))
		tkoptions.RGBAOption(page, 4, "New region interior color",
			self.mav.prefs[NEW_REGION_INTERIOR], lambda o:
			self.mav.prefs.update({NEW_REGION_INTERIOR: o.get()}))
		tkoptions.IntOption(page, 5,
			"Use ellipsis for names longer than",
			self.mav.prefs[REGION_NAME_ELLIPSIS],
			self._newRegionEllipsis,
			width=3, min=4)

		widgetData = [
			("successful matches",
				MATCH_REG_ACTIVE,MATCH_REG_EDGE,MATCH_REG_FILL),
			("mismatches",
				ERROR_REG_ACTIVE,ERROR_REG_EDGE,ERROR_REG_FILL),
			("structure gaps",
				GAP_REG_ACTIVE, GAP_REG_EDGE, GAP_REG_FILL)
		]
		assocGroup = Pmw.Group(page, tag_text="Structure association")
		assocGroup.grid(row=6, column=0, columnspan=2)
		from CGLtk.color.ColorWell import ColorWell
		inside = assocGroup.interior()
		inside.columnconfigure(0, weight=1)
		inside.columnconfigure(3, weight=1)
		for i, regPrefs in enumerate(widgetData):
			descript, activePref, edgePref, fillPref = regPrefs
			rv = Tkinter.IntVar(inside)
			rv.set(self.mav.prefs[activePref])
			Tkinter.Checkbutton(inside, variable=rv,
				text="Draw region depicting %s" % descript,
				command=lambda var=rv, prefName=activePref:
				self.mav.prefs.update({prefName: var.get()})
				).grid(row=2*i, column=0, columnspan=4,
				sticky='w')
			Tkinter.Label(inside, text="Border:").grid(
				row=2*i+1, column=0, sticky='e')
			ColorWell(inside, color=self.mav.prefs[edgePref],
				noneOkay=True, wantAlpha=False,
				callback=lambda c, prefName=edgePref:
				self.mav.prefs.update({prefName: c})).grid(
				row=2*i+1, column=1, sticky='w')
			Tkinter.Label(inside, text=" Interior:").grid(
				row=2*i+1, column=2, sticky='e')
			ColorWell(inside, color=self.mav.prefs[fillPref],
				noneOkay=True, wantAlpha=False,
				callback=lambda c, prefName=fillPref:
				self.mav.prefs.update({prefName: c})).grid(
				row=2*i+1, column=3, sticky='w')

	def _addStructurePage(self, page):
		page.columnconfigure(1, weight=1)
		loadGroup = Pmw.Group(page, tag_text="Structure loading")
		loadGroup.grid(row=1, column=0, sticky="nsew")
		loadGroup.interior().columnconfigure(1, weight=1)

		self.loadScopVar = Tkinter.IntVar(loadGroup.interior())
		self.loadScopVar.set(self.mav.prefs[LOAD_SCOP])
		ck = Tkinter.Checkbutton(loadGroup.interior(), text=
			"Load SCOP file for each unassociated sequence"
			"\nwhose name appears to be a SCOP ID (sid)",
			variable=self.loadScopVar, command=lambda
			pr=self.mav.prefs, p=LOAD_SCOP, v=self.loadScopVar:
			pr.update({p: v.get()}))
		ck.grid(row=0, column=0, columnspan=2, sticky='w')

		lab = Tkinter.Label(loadGroup.interior(), text="Load PDB file "
				"for each unassociated sequence whose name...")
		lab.grid(row=1, column=0, columnspan=2, sticky='w')

		nameButtons = Tkinter.Frame(loadGroup.interior())
		nameButtons.grid(row=2, column=0, columnspan=2)
		self.loadNameVars = {}
		row = 0
		for nameStyle, descript in [
			(LOAD_PDB_NAME_EXACT,
				"""is <pdb code>\n   (e.g. "1gcn")"""),
			(LOAD_PDB_NAME_START,
				"""starts with <pdb code>\n   """
				"""(e.g. "1k6w_A")"""),
			(LOAD_PDB_NAME_NCBI,
				"""contains "pdb|" + <pdb code>\n   """
				"""(NCBI-style; e.g. "gi|1421399|pdb|1FTZ")"""),
			(LOAD_PDB_NAME_VARSTART, "starts with")
		]:
			var = Tkinter.IntVar(nameButtons)
			var.set(self.mav.prefs[nameStyle])
			if nameStyle == LOAD_PDB_NAME_VARSTART:
				buttonMaster = Tkinter.Frame(nameButtons)
				buttonMaster.grid(row=row, column=0, sticky='w')
			else:
				buttonMaster = nameButtons
			ck = Tkinter.Checkbutton(buttonMaster, text=descript,
				variable=var, justify='left', command=lambda
				pr=self.mav.prefs, ns=nameStyle, v=var:
				pr.update({ns: v.get()}))
			if nameStyle == LOAD_PDB_NAME_VARSTART:
				ck.grid(row=0, column=0, sticky='e')
				self.varStartEntry = Pmw.EntryField(
					buttonMaster, command=lambda:
					self.mav.prefs.update({
						LOAD_PDB_NAME_VARSTART_VAL:
						self.varStartEntry.get()}),
					labelpos='e',
					label_text=" + <pdb code>",
					entry_width=5,
					value=self.mav.prefs[LOAD_PDB_NAME_VARSTART_VAL])
				self.varStartEntry.grid(row=0, column=1,
								sticky='w')
				self._entryWidgets.append(self.varStartEntry)
			else:
				ck.grid(row=row, column=0, sticky='w')
			row += 1
			self.loadNameVars[nameStyle] = var
		
		self.autoloadVar = Tkinter.IntVar(loadGroup.interior())
		self.autoloadVar.set(self.mav.prefs[LOAD_PDB_AUTO])
		ck = Tkinter.Checkbutton(loadGroup.interior(), text=
			"Automatically load structures",
			variable=self.autoloadVar, command=lambda
			pr=self.mav.prefs, p=LOAD_PDB_AUTO, v=self.autoloadVar:
			pr.update({p: v.get()}))
		ck.grid(row=3, column=0, columnspan=2, sticky='w')

		self.dolimitVar = Tkinter.IntVar(loadGroup.interior())
		self.dolimitVar.set(self.mav.prefs[LOAD_PDB_DO_LIMIT])
		ck = Tkinter.Checkbutton(loadGroup.interior(), text=
			"Do not autoload if more than",
			variable=self.dolimitVar, command=lambda
			pr=self.mav.prefs, p=LOAD_PDB_DO_LIMIT,
			v=self.dolimitVar: pr.update({p: v.get()}))
		ck.grid(row=4, column=0)
		self.loadLimitEntry = Pmw.EntryField(loadGroup.interior(),
			command=self._loadLimitCB, labelpos='e',
			entry_justify='right', label_text=
			"structures would load", validate='numeric',
			value=str(self.mav.prefs[LOAD_PDB_LIMIT]),
			entry_width=3)
		self.loadLimitEntry.grid(row=4, column=1, sticky='w')
		self._entryWidgets.append(self.loadLimitEntry)

		# sequence association...
		assocGroup = Pmw.Group(page, tag_text="Auto-association")
		assocGroup.grid(row=0, column=0, sticky="nsew")
		assocGroup.interior().columnconfigure(1, weight=1)

		lw = Pmw.LabeledWidget(assocGroup.interior(), labelpos='w',
			label_text="Allow one mismatch per")
		lw.grid(row=0, column=0, sticky='w')
		self.errorRateEntry = Pmw.EntryField(lw.interior(),
			command=self._errorRateCB, labelpos='e',
			entry_justify='right', label_text=
			"structure residues", validate='numeric',
			value=str(self.mav.prefs[ASSOC_ERROR_RATE]),
			entry_width=3)
		self.errorRateEntry.grid(row=0, column=0, sticky='w')
		self._entryWidgets.append(self.errorRateEntry)

	def _errorRateCB(self):
		if not self.errorRateEntry.valid():
			replyobj.error(
				"Bad auto-association error rate value.\n")
			return
		self.mav.prefs[ASSOC_ERROR_RATE] = int(
						self.errorRateEntry.get())

	def _loadLimitCB(self):
		if not self.loadLimitEntry.valid():
			replyobj.error("Bad load limit value.\n")
			return
		self.mav.prefs[LOAD_PDB_LIMIT] = int(self.loadLimitEntry.get())

	def _addHeadersPage(self, page):
		from chimera.tkoptions import EnumOption, IntOption, FloatOption
		from prefs import consensusStyles
		default = self.mav.prefs[CONSENSUS_STYLE]
		if default not in consensusStyles:
			default = CSN_MAJ_GAP
			self.mav.prefs[CONSENSUS_STYLE] = default
		class ConsensusOption(EnumOption):
			values = consensusStyles
		ConsensusOption(page, 0, "Consensus style", default,
			self._csnChange, balloon="what to show in the"
			" 'Consensus'\nline of the alignment")

		from prefs import conservationStyles
		default = self.mav.prefs[CONSERVATION_STYLE]
		if default not in conservationStyles:
			default = CSV_PERCENT
			self.mav.prefs[CONSERVATION_STYLE] = default
		class ConservationOption(EnumOption):
			values = conservationStyles
		ConservationOption(page, 2, "Conservation style", default,
				self._csvChange, balloon="what to show in the"
				" 'Conservation'\nline of the alignment")

		tkoptions.BooleanOption(page, 3, "Show numbering initially",
			self.mav.prefs[SHOW_RULER_AT_STARTUP], lambda opt:
			self.mav.prefs.update({SHOW_RULER_AT_STARTUP: opt.get()}))
		tkoptions.BooleanOption(page, 4, "Show consensus initially",
			self.mav.prefs[SHOW_CONSENSUS_AT_STARTUP], lambda opt:
			self.mav.prefs.update({SHOW_CONSENSUS_AT_STARTUP: opt.get()}))
		tkoptions.BooleanOption(page, 5, "Show conservation initially",
			self.mav.prefs[SHOW_CONSERVATION_AT_STARTUP], lambda opt:
			self.mav.prefs.update({SHOW_CONSERVATION_AT_STARTUP: opt.get()}))

		self.al2coGroup = grp = Pmw.Group(page,
						tag_text="AL2CO parameters")
		from prefs import CSV_AL2CO
		grp.gridArgs = { 'row': 6, 'column': 0,
						'columnspan': 2, 'sticky': 'w' }
		if self.mav.prefs[CONSERVATION_STYLE] == CSV_AL2CO:
			grp.grid(**grp.gridArgs)
		ingrp = grp.interior()
		from prefs import al2coFrequencies, al2coConservations, \
			al2coTransforms, AL2CO_FREQ, AL2CO_CONS, AL2CO_WINDOW, \
			AL2CO_GAP, AL2CO_MATRIX, AL2CO_TRANSFORM
		class Al2coFrequencyOption(EnumOption):
			values = al2coFrequencies
		Al2coFrequencyOption(ingrp, 0, "Frequency estimation method",
			al2coFrequencies[self.mav.prefs[AL2CO_FREQ]],
			self._al2coFreqChange, balloon="Method"
			" to estimate position-specific amino acid frequencies")
		class Al2coConservationOption(EnumOption):
			values = al2coConservations
		Al2coConservationOption(ingrp, 1, "Conservation measure",
			al2coConservations[self.mav.prefs[AL2CO_CONS]],
			self._al2coConsChange,
			balloon="Conservation calculation strategy")
		class Al2coWindowOption(IntOption):
			min = 1
		Al2coWindowOption(ingrp, 2, "Averaging window",
			self.mav.prefs[AL2CO_WINDOW], self._al2coWindowChange,
			balloon="Window size for conservation averaging",
			sticky='w', width=2)
		class Al2coGapOption(FloatOption):
			min = 0
			max = 1
		Al2coGapOption(ingrp, 3, "Gap fraction",
			self.mav.prefs[AL2CO_GAP], self._al2coGapChange,
			sticky='w', width='4',
			balloon="Conservations are computed for columns only\n"
			"if the fractions of gaps is less than this value")
		from SmithWaterman import matrixFiles
		# AL2CO doesn't play nice with non-protein matrices
		matrixNames = [m for m in matrixFiles.keys()
				if matrixFiles[m].endswith(".matrix")]
		matrixNames.append("identity")
		matrixNames.sort(lambda a, b: cmp(a.lower(), b.lower()))
		class Al2coMatrixOption(EnumOption):
			values = matrixNames
		self.al2coMatrixOpt = Al2coMatrixOption(ingrp, 4,
			"Sum-of-pairs matrix", self.mav.prefs[AL2CO_MATRIX],
			self._al2coMatrixChange, balloon="Similarity matrix"
			" used by sum-of-pairs measure")
		class Al2coTransformOption(EnumOption):
			values = al2coTransforms
		self.al2coTransformOpt = Al2coTransformOption(ingrp, 5,
			"Matrix transformation",
			al2coTransforms[self.mav.prefs[AL2CO_TRANSFORM]],
			self._al2coTransformChange, balloon="Transform applied"
			" to similarity matrix as follows:\n"
			"\t%s: identity subtitutions have same value\n"
			"\t%s: adjustment so that 2-sequence alignment yields\n"
			"\t\tsame score as in original matrix" % tuple(
			al2coTransforms[1:]))
		if self.mav.prefs[AL2CO_CONS] != 2:
			self.al2coMatrixOpt.disable()
			self.al2coTransformOpt.disable()
		from CGLtk.Citation import Citation
		Citation(ingrp, "Pei, J. and Grishin, N.V. (2001)\n"
			"AL2CO: calculation of positional conservation in a"
			" protein sequence alignment\n"
			"Bioinformatics, 17, 700-712.", prefix="Publications"
			" using AL2CO conservation measures should cite:"
			).grid(row=6, column=0, columnspan=2)

	def _al2coConsChange(self, opt):
		from prefs import al2coConservations, AL2CO_CONS
		self.mav.prefs[AL2CO_CONS] = al2coConservations.index(opt.get())
		if self.mav.prefs[AL2CO_CONS] == 2:
			self.al2coMatrixOpt.enable()
			self.al2coTransformOpt.enable()
		else:
			self.al2coMatrixOpt.disable()
			self.al2coTransformOpt.disable()
		self._al2coRefresh()

	def _al2coFreqChange(self, opt):
		from prefs import al2coFrequencies, AL2CO_FREQ
		self.mav.prefs[AL2CO_FREQ] = al2coFrequencies.index(opt.get())
		self._al2coRefresh()

	def _al2coGapChange(self, opt):
		from prefs import AL2CO_GAP
		val = opt.get()
		if val <= 0.0 or val > 1.0:
			opt.set(self.mav.prefs[AL2CO_GAP])
			raise UserError("Gap fraction must be greater than"
				" zero and no greater than one")
		self.mav.prefs[AL2CO_GAP] = val
		self._al2coRefresh()
	
	def _al2coMatrixChange(self, opt):
		from prefs import AL2CO_MATRIX
		self.mav.prefs[AL2CO_MATRIX] = opt.get()
		self._al2coRefresh()

	def _al2coTransformChange(self, opt):
		from prefs import AL2CO_TRANSFORM, al2coTransforms
		self.mav.prefs[AL2CO_TRANSFORM] = al2coTransforms.index(
								opt.get())
		self._al2coRefresh()

	def _al2coWindowChange(self, opt):
		from prefs import AL2CO_WINDOW
		self.mav.prefs[AL2CO_WINDOW] = opt.get()
		self._al2coRefresh()
	
	def _al2coRefresh(self):
		from prefs import CSV_AL2CO
		if self.mav.prefs[CONSERVATION_STYLE] != CSV_AL2CO:
			return
		self.status("Computing conservation...")
		seqCanvas = self.mav.seqCanvas
		seqCanvas.conservation.reevaluate()
		seqCanvas.refresh(seqCanvas.conservation)
		self.status("Conservation computed.")

	def _csnChange(self, opt):
		self.mav.prefs[CONSENSUS_STYLE] = opt.get()
		seqCanvas = self.mav.seqCanvas
		seqCanvas.consensus.reevaluate()
		seqCanvas.refresh(seqCanvas.consensus)

	def _csvChange(self, opt):
		self.mav.prefs[CONSERVATION_STYLE] = opt.get()
		from prefs import CSV_AL2CO
		if self.mav.prefs[CONSERVATION_STYLE] == CSV_AL2CO:
			self.al2coGroup.grid(**self.al2coGroup.gridArgs)
		else:
			self.al2coGroup.grid_forget()
		self.notebook.setnaturalsize()
		seqCanvas = self.mav.seqCanvas
		seqCanvas.conservation.reevaluate()
		seqCanvas.refresh(seqCanvas.conservation)

class WrapGroup(Pmw.Group):
	def __init__(self, parent, dialog, prefPrefix, callback):
		Pmw.Group.__init__(self, parent, tag_text="Line wrapping")
		self.__callback = callback
		self.__dialog = dialog
		self.__prefPrefix = prefPrefix

		self.__wrapVar = Tkinter.IntVar(dialog.uiMaster())
		if dialog.mav.prefs[prefPrefix + WRAP_IF]:
			self.__wrapVar.set(2)
		elif dialog.mav.prefs[prefPrefix + WRAP]:
			self.__wrapVar.set(0)
		else:
			self.__wrapVar.set(1)

		row=0
		f = Tkinter.Frame(self.interior())
		f.grid(row=row, column=0, columnspan=2, sticky="w")
		b = Tkinter.Radiobutton(f, text="Wrap to new line every ",
			variable=self.__wrapVar, value=0, command=self.__newWrap)
		b.grid(row=0, column=0, sticky="e")
		self.__lineWidthEntry = Pmw.EntryField(f, command=self.__newWrap,
				labelpos="e", label_text="0 residues", entry_width=2,
				entry_justify='right', validate='numeric',
				value=dialog.mav.prefs[prefPrefix + LINE_WIDTH]/10)
		self.__lineWidthEntry.grid(row=0, column=1, sticky="w")
		dialog._entryWidgets.append(self.__lineWidthEntry)
		row += 1

		if not prefPrefix:
			f = Tkinter.Frame(self.interior())
			f.grid(row=row, column=0, columnspan=2, sticky="w")
			b = Tkinter.Radiobutton(f, text="Wrap if ",
				variable=self.__wrapVar, value=2, command=self.__newWrap)
			b.grid(row=0, column=0, sticky="e")
			self.__wrapThresholdEntry = Pmw.EntryField(f,
					command=self.__newWrap, labelpos="e", entry_width=2,
					validate='numeric', entry_justify='center',
					label_text=" or fewer sequences",
					value=dialog.mav.prefs[prefPrefix + WRAP_THRESHOLD])
			self.__wrapThresholdEntry.grid(row=0, column=1, sticky="w")
			dialog._entryWidgets.append(self.__wrapThresholdEntry)
			row += 1

		b = Tkinter.Radiobutton(self.interior(), text="Never wrap",
			variable=self.__wrapVar, value=1, command=self.__newWrap)
		b.grid(row=row, column=0, columnspan=2, sticky="w")
		row += 1

		from chimera.tkoptions import BooleanOption
		BooleanOption(self.interior(), row, "Space between wrapped blocks",
			dialog.mav.prefs[prefPrefix + BLOCK_SPACE], self.__blockSpace)

	def __blockSpace(self, opt):
		mav, prefPrefix = self.__dialog.mav, self.__prefPrefix
		mav.prefs[prefPrefix + BLOCK_SPACE] = opt.get()
		if (len(mav.seqs) == 1) == bool(prefPrefix):
			mav.seqCanvas._reformat()

	def __newWrap(self):
		mav, prefPrefix = self.__dialog.mav, self.__prefPrefix
		if self.__wrapVar.get() == 0:
			mav.prefs[prefPrefix + WRAP_IF] = 0
			mav.prefs[prefPrefix + WRAP] = 1
		elif self.__wrapVar.get() == 1:
			mav.prefs[prefPrefix + WRAP_IF] = 0
			mav.prefs[prefPrefix + WRAP] = 0
		else:
			mav.prefs[prefPrefix + WRAP_IF] = 1

		valid = 0
		if self.__lineWidthEntry.valid():
			lineWidth = 10 * int(self.__lineWidthEntry.get())
			if lineWidth > 0:
				valid = 1
				mav.prefs[prefPrefix + LINE_WIDTH] = lineWidth
		if not valid:
			replyobj.error("Line width must be positive integer\n")

		if not prefPrefix:
			valid = 0
			if self.__wrapThresholdEntry.valid():
				threshold = int(self.__wrapThresholdEntry.get())
				if threshold > 0:
					valid = 1
					mav.prefs[prefPrefix + WRAP_THRESHOLD] = threshold
			if not valid:
				replyobj.error("'Number of sequences for line wrapping'"
					" must be positive integer\n")
		if (len(mav.seqs) == 1) == bool(prefPrefix):
			self.__callback()

class FontGroup(Pmw.Group):
	def __init__(self, parent, dialog, prefPrefix, callback):
		Pmw.Group.__init__(self, parent, tag_text="Font")
		self.__callback = callback
		self.__dialog = dialog
		self.__prefPrefix = prefPrefix

		prefs = dialog.mav.prefs
		self.__fontSizeEntry = Pmw.EntryField(self.interior(),
			command=self.__newFont, labelpos='w', label_text="Use",
			entry_width=2, entry_justify='center',
			validate='numeric', value=prefs[prefPrefix + FONT_SIZE])
		self.__fontSizeEntry.grid(row=0, column=0, sticky='e')
		dialog._entryWidgets.append(self.__fontSizeEntry)

		self.__fontMenu = Pmw.OptionMenu(self.interior(), labelpos='w',
			command=self.__newFont, initialitem=prefs[prefPrefix + FONT_NAME],
			items=['Courier', 'Helvetica', 'Times'], label_text='point')
		self.__fontMenu.grid(row=0, column=1, sticky='w')

		self.__boldVar = Tkinter.IntVar(parent)
		self.__boldVar.set(prefs[prefPrefix + BOLD_ALIGNMENT])
		Tkinter.Checkbutton(self.interior(), variable=self.__boldVar,
			text="Bold", command=self.__newFont).grid(row=0, column=2)

	def __newFont(self, fontName=None):
		mav, prefPrefix = self.__dialog.mav, self.__prefPrefix

		# can't ask prefs for these values, since some other
		# MAV may have changed them out from under us
		curFontName = mav.seqCanvas.font.cget("family").capitalize()
		curFontSize = int(mav.seqCanvas.font.cget("size"))
		valid = 0
		if self.__fontSizeEntry.valid():
			fontSize = int(self.__fontSizeEntry.get())
			if fontSize > 0:
				if fontSize > 20:
					import tkMessageBox
					if not tkMessageBox.askokcancel(title="Very Big Font",
							message="Really use %d-point font?" % fontSize):
						self.__fontSizeEntry.setvalue(curFontSize)
						return

				valid = 1
				mav.prefs[prefPrefix + FONT_SIZE] = fontSize
		if not valid:
			replyobj.error("Font size must be positive integer\n")

		actualChange = False
		if fontName:
			mav.prefs[prefPrefix + FONT_NAME] = fontName
			if fontName != curFontName:
				actualChange = True
		if curFontSize != mav.prefs[prefPrefix + FONT_SIZE]:
			actualChange = True
		if self.__boldVar.get() != mav.prefs[prefPrefix + BOLD_ALIGNMENT]:
			mav.prefs[prefPrefix + BOLD_ALIGNMENT] = self.__boldVar.get()
			actualChange = True

		if actualChange and (len(mav.seqs) == 1) == bool(prefPrefix):
			self.__callback()

class SpacingGroup(Pmw.Group):
	def __init__(self, parent, dialog, prefPrefix, callback):
		Pmw.Group.__init__(self, parent, tag_text="Spacing")
		self.__callback = callback
		self.__dialog = dialog
		self.__prefPrefix = prefPrefix

		prefs = dialog.mav.prefs
		self.__columnSepEntry = Pmw.EntryField(self.interior(),
			command=self.__newColSep, labelpos='w',
			label_text="Column separation (pixels)", entry_width=2,
			entry_justify='center', validate='integer',
			value=prefs[prefPrefix + COLUMN_SEP])
		self.__columnSepEntry.grid(row=0, column=0, columnspan=2, sticky='e')
		dialog._entryWidgets.append(self.__columnSepEntry)

		self.__lineSepEntry = Pmw.EntryField(self.interior(),
			command=self.__newLineSep, labelpos='w',
			label_text="Line separation (pixels)", entry_width=2,
			entry_justify='center', validate='integer',
			value=prefs[prefPrefix + LINE_SEP])
		self.__lineSepEntry.grid(row=1, column=0, columnspan=2, sticky='e')
		dialog._entryWidgets.append(self.__lineSepEntry)

		from chimera.tkoptions import BooleanOption
		BooleanOption(self.interior(), 2, "Space after every 10 residues",
			prefs[prefPrefix + TEN_RES_GAP], self.__resGap)

	def __newLineSep(self):
		mav, prefPrefix = self.__dialog.mav, self.__prefPrefix
		# can't use pref for cur value: pref may have been changed
		# by another MAV instance
		if self.__lineSepEntry.valid():
			newLineSep = int(self.__lineSepEntry.get())
			mav.prefs[prefPrefix + LINE_SEP] = newLineSep
			if (len(mav.seqs) == 1) == bool(prefPrefix):
				curLineSep = mav.seqCanvas.leadBlock.letterGaps[1]
				if newLineSep != curLineSep:
					self.__callback()

	def __newColSep(self):
		mav, prefPrefix = self.__dialog.mav, self.__prefPrefix
		# can't use pref for cur value: pref may have been changed
		# by another MAV instance
		if self.__columnSepEntry.valid():
			newColSep = int(self.__columnSepEntry.get())
			mav.prefs[prefPrefix + COLUMN_SEP] = newColSep
			if (len(mav.seqs) == 1) == bool(prefPrefix):
				curColSep = mav.seqCanvas.leadBlock.letterGaps[0]
				if newColSep != curColSep:
					self.__callback()

	def __resGap(self, opt):
		mav, prefPrefix = self.__dialog.mav, self.__prefPrefix
		mav.prefs[prefPrefix + TEN_RES_GAP] = opt.get()
		if (len(mav.seqs) == 1) == bool(prefPrefix):
			self.__callback()

class ResColoringGroup(Pmw.Group):
	def __init__(self, parent, dialog, prefPrefix, callback):
		Pmw.Group.__init__(self, parent, tag_text="Residue letter coloring")
		self.__callback = callback
		self.__dialog = dialog
		self.__prefPrefix = prefPrefix

		from prefs import builtinResidueColorings
		prefs = dialog.mav.prefs
		default = prefs[prefPrefix + RESIDUE_COLORING]
		allColorings = builtinResidueColorings + prefs[RC_CUSTOM_SCHEMES]
		if default not in allColorings:
			default = RC_CLUSTALX
			prefs[prefPrefix + RESIDUE_COLORING] = default
		from chimera.tkoptions import SymbolicEnumOption
		class ResidueColoringOption(SymbolicEnumOption):
			values = allColorings
			labels = builtinResidueColorings + [os.path.basename(x)
				for x in prefs[RC_CUSTOM_SCHEMES]]
		self._resColorOpt = ResidueColoringOption(self.interior(), 0,
			"Color scheme", default, self.__rcChange,
			balloon="how to color alignment residue letters")

	def __rcChange(self, opt):
		mav, prefPrefix = self.__dialog.mav, self.__prefPrefix
		coloring = opt.get()
		mav.prefs[prefPrefix + RESIDUE_COLORING] = coloring
		if (len(mav.seqs) == 1) != bool(prefPrefix):
			return
		if coloring in [RC_BLACK, RC_RIBBON]:
			self.__callback(coloring)
			return
		self.__callback(RC_CLUSTALX)
		from clustalX import clustalInfo
		if coloring == RC_CLUSTALX:
			args = clustalInfo()
		else:
			try:
				args = clustalInfo(coloring)
			except UserError, v:
				replyobj.error("Error reading %s: %s\nUsing"
						" ClustalX coloring instead\n"
						% (coloring, str(v)))
				args = clustalInfo()
				self.__removeColorScheme(coloring)
		mav.seqCanvas.setClustalParams(*args)

	def __removeColorScheme(self, colorFile):
		mav, prefPrefix = self.__dialog.mav, self.__prefPrefix
		schemes = mav.prefs[RC_CUSTOM_SCHEMES]
		if colorFile not in schemes:
			return
		schemes.remove(colorFile)
		mav.prefs[RC_CUSTOM_SCHEMES] = schemes[:]
		if mav.prefs[prefPrefix + RESIDUE_COLORING] == colorFile:
			self._resColorOpt.set(RC_CLUSTALX)
			mav.prefs[prefPrefix + RESIDUE_COLORING] = RC_CLUSTALX
		self._resColorOpt.values.remove(colorFile)
		self._resColorOpt.labels.remove(os.path.basename(colorFile))
		self._resColorOpt.remakeMenu()
