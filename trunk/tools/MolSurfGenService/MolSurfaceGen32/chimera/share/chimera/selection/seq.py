import string
import re
import Pmw
import Tkinter
from chimera.baseDialog import ModelessDialog
from chimera import resCode
import chimera

class AmbiguityMenu(Tkinter.Frame):
	NONE = "none"
	PROTEIN = "protein"
	NUCLEIC = "nucleic acid"
	ambiguity = [NONE, PROTEIN, NUCLEIC]

	class PatternError(ValueError):
		pass

	def __init__(self, parent):
		Tkinter.Frame.__init__(self, parent)
		self.menu = Pmw.OptionMenu(self, items=self.ambiguity,
			label_text="Ambiguity codes:", labelpos='w',
			command=self._configureInfo)
		self.menu.grid(row=0)

		self.label = Tkinter.Label(self, bd=0, padx=0, pady=0)
		from tkFont import Font
		font = Font(font=self.label.cget('font'))
		font.config(size=int(0.75*float(font.cget('size'))+0.5),
							weight="normal")
		self.label.config(font=font)
		self.label.grid(row=1)

	def getvalue(self):
		return self.menu.getvalue()

	def invoke(self, val):
		self.menu.invoke(val)

	def text2pattern(self, text):
		ambiguity = self.getvalue()
		pattern = ""
		for letter in text:
			if not letter.isalpha():
				raise self.PatternError("Non-alphabetic"
					" character in probe sequence: '%s'"
					% letter)
			if letter == "J":
				raise self.PatternError("Unknown one-letter"
					" code: 'J'")
			
			if ambiguity == self.PROTEIN:
				if letter == "B":
					pattern += "[BDN]"
				elif letter == "Z":
					pattern += "[EQZ]"
				elif letter in "DN":
					pattern += "[B%s]" % letter
				elif letter in "EQ":
					pattern += "[%sZ]" % letter
				else:
					pattern += letter
			elif ambiguity == self.NUCLEIC:
				if letter == "R":
					pattern += "[AG]"
				elif letter == "Y":
					pattern += "[CTU]"
				elif letter == "N":
					pattern += "[ACGTU]"
				else:
					pattern += letter
			else:
				pattern += letter
		return pattern
		
	def _configureInfo(self, item):
		if item == self.NONE:
			self.label.configure(text="")
		elif item == self.PROTEIN:
			self.label.configure(text="(B = D/N, Z = E/Q)")
		else:
			self.label.configure(text=
					"(R = A/G, Y = C/T/U, N = A/C/G/T/U)")

class SeqSearchFrame(Tkinter.Frame):
	SUBSEQUENCE = "Subsequence"
	PROSITE = "PROSITE pattern"
	styles = [SUBSEQUENCE, PROSITE]
	prefStyle = "search style"

	from chimera import preferences
	prefs = preferences.addCategory("sequence search UI",
		preferences.HiddenCategory,
		optDict={ prefStyle: SUBSEQUENCE })

	def __init__(self, parent, seqsCB, **kw):
		self.seqsCB = seqsCB

		Tkinter.Frame.__init__(self, parent)
		self.columnconfigure(0, weight=1)

		self.grouping = Pmw.Group(self, tag_text="Find", **kw)
		self.grouping.grid(row=0, column=0, sticky="nsew")
		self.grouping.interior().columnconfigure(0, weight=1)

		self.notebook = Pmw.NoteBook(self.grouping.interior())
		self.notebook.grid(row=0, column=0, sticky='ewns')
			
		self.pages = {}
		for style in self.styles:
			self.pages[style] = self.notebook.add(style)
			self._fillPage(style)
		self.notebook.setnaturalsize()
		self.notebook.selectpage(self.prefs[self.prefStyle])

		self.forceInterpVar = Tkinter.IntVar(parent)
		fiFrame = Tkinter.Frame(self.grouping.interior())
		fiFrame.grid(row=1, sticky='ew')
		fiCheckbox = Tkinter.Checkbutton(fiFrame,
			text="Force interpretation as",
			variable=self.forceInterpVar)
		self.forceInterpVar.set(0)
		fiCheckbox.grid(row=0, column=0, sticky="e")
		self.fiOptMenu = Pmw.OptionMenu(fiFrame, initialitem="protein",
				items=["nucleic acid", "protein"],
				label_text="sequence", labelpos='e')
		self.fiOptMenu.grid(row=0, column=1, sticky='w')

	def _fillPage(self, pageName):
		page = self.pages[pageName]
		page.columnconfigure(0, weight=1)
		if pageName == self.SUBSEQUENCE:
			self.seqEntry = Pmw.EntryField(page,
					command=self.findSubseq, labelpos='w',
					label_text='Sequence:')
			self.seqEntry.grid(row=0, sticky='ew')

			self.ambMenu = AmbiguityMenu(page)
			self.ambMenu.grid(row=1, column=0)
		else:
			self.prositeEntry = Pmw.EntryField(page,
					command=self.findProsite, labelpos='w',
					label_text='Pattern:')
			self.prositeEntry.grid(row=0, sticky='ew')

	def entry(self):
		if self.notebook.getcurselection() == self.SUBSEQUENCE:
			return self.seqEntry
		return self.prositeEntry

	def findSubseq(self):
		self.prefs[self.prefStyle] = self.SUBSEQUENCE
		try:
			probeSeq = self.ambMenu.text2pattern(self.seqEntry
					.component('entry').get().upper())
		except AmbiguityMenu.PatternError, v:
			raise chimera.UserError(str(v))
			
		if not probeSeq:
			return

		expr = re.compile(probeSeq)

		resAdd = []
		for seq in self._getSeqs():
			matches = seq.patternMatch(expr)
			for start, end in matches:
				resAdd.extend(seq.residues[
					seq.gapped2ungapped(start):
					seq.gapped2ungapped(end+1)])
		self._selResidues(resAdd)

	def findProsite(self):
		self.prefs[self.prefStyle] = self.PROSITE
		resAdd = []
		prositePattern = self.prositeEntry.component('entry').get()
		for seq in self._getSeqs():
			for start, end in seq.prositeMatch(prositePattern):
				resAdd.extend(seq.residues[start:end+1])
		self._selResidues(resAdd)

	def _getSeqs(self):
		if self.forceInterpVar.get():
			if self.fiOptMenu.getvalue() == "protein":
				return filter(lambda s: s.hasProtein(),
								self.seqsCB())
			else:
				return filter(lambda s: not s.hasProtein(),
								self.seqsCB())
		return self.seqsCB()
		
	def _selResidues(self, residues):
		from chimera.selection import ItemizedSelection
		from chimera.tkgui import selectionOperation
		sel = ItemizedSelection()
		sel.add(residues)
		sel.addImplied(vertices=0)
		selectionOperation(sel)

class SeqSelDialog(ModelessDialog):
	"""Assist user to select sequence"""

	name = 'Select sequence'
	title = 'Select Sequence'
	help = 'UsersGuide/findseq.html'
	buttons = ('OK', 'Apply', 'Cancel')
	default = 'OK'

	def fillInUI(self, parent):
		self.searchFrame = SeqSearchFrame(parent, self.getSeqs)
		self.searchFrame.grid(row=0, column=0, sticky='ew')
	
	def Apply(self):
		self.searchFrame.entry().invoke()

	def getSeqs(self):
		seqs = []
		for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
			seqs.extend(m.sequences())
		return seqs

