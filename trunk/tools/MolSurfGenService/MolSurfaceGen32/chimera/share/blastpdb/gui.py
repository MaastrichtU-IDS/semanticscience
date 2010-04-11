# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id:$

import chimera
from chimera.baseDialog import ModalDialog, ModelessDialog
from chimera import UserError, replyobj
from SimpleSession import SAVE_SESSION, registerAttribute
from chimera import Molecule
from chimera.Sequence import StructureSequence

class BlastParameters(object):

	def addParametersUI(self, master):
		import Tkinter
		import Pmw
		f = Tkinter.Frame(master)
		f.grid(row=1, column=0, sticky="nsew")
		f.columnconfigure(1, weight=1)
		row = 0

		self.wProgram = Pmw.OptionMenu(f,
					labelpos="w",
					label_text="Program:",
					initialitem="blast",
					items=[ "blast", "psiblast" ],
					command=self._programChanged)
		self.wProgram.grid(column=0, row=row, sticky="ew")
		row += 1

		self.wDb = Pmw.OptionMenu(f,
					labelpos="w",
					label_text="Database:",
					initialitem="pdb",
					items=[ "pdb", "nr" ])
		self.wDb.grid(column=0, row=row, sticky="ew")
		row += 1

		self.wEvalue = Pmw.EntryField(f,
					labelpos="w",
					label_text="E-value (1e-X):",
					value=3,
					validate = {'validator':'integer',
							'min':1,
							'max':200})
		self.wEvalue.grid(column=0, row=row, sticky="ew")
		row += 1

		self.wMatrix = Pmw.OptionMenu(f,
					labelpos="w",
					label_text="Matrix:",
					initialitem="BLOSUM62",
					items=[ "BLOSUM45",
						"BLOSUM62",
						"BLOSUM80",
						"PAM30",
						"PAM70", ])
		self.wMatrix.grid(column=0, row=row, sticky="ew")
		row += 1

		self.wPasses = Pmw.EntryField(f,
					labelpos="w",
					label_text="Passes:",
					label_state="disabled",
					entry_state="disabled",
					value=1,
					validate = {'validator':'integer',
							'min':1,
							'max':10})
		self.wPasses.grid(column=0, row=row, sticky="ew")
		row += 1

		Pmw.alignlabels([ self.wProgram, self.wDb, self.wEvalue,
					self.wMatrix, self.wPasses ], sticky="e")

		self.showOneVar = Tkinter.IntVar(master)
		self.showOneVar.set(1)
		self.showOne = Tkinter.Checkbutton(f,
						text="List only best-matching "
						"chain per PDB entry",
						variable=self.showOneVar)
		self.showOne.grid(column=0, row=row, sticky="w")
		row += 1

	def _programChanged(self, wProg):
		sel = self.wProgram.getcurselection()
		if sel == "blast":
			self.wPasses.configure(entry_state="disabled",
						label_state="disabled")
		else:
			self.wPasses.configure(entry_state="normal",
						label_state="normal")

	def checkParameters(self):
		if not self.wEvalue.valid():
			replyobj.error("Blast: invalid e-value\n")
			return None
		if not self.wPasses.valid():
			replyobj.error("Blast: invalid number of passes\n")
			return None
		prog = self.wProgram.getcurselection()
		db = self.wDb.getcurselection()
		evalue = "1e-" + self.wEvalue.get()
		matrix = self.wMatrix.getcurselection()
		passes = self.wPasses.get()
		showOne = self.showOneVar.get()
		return (prog, db, evalue, matrix, passes, showOne)

class BlastChainDialog(ModelessDialog, BlastParameters):

	name = "blast chain"
	title = "Blast Protein"
	buttons = ("OK", "Apply", "Cancel")
	help = "UsersGuide/blast.html"

	def fillInUI(self, master):
		import Pmw
		self.notebook = nb = Pmw.NoteBook(master)
		nb.grid(column=0, row=0, sticky="ew")

		chainPage = nb.add("From Structure")
		from chimera.widgets import MoleculeChainOptionMenu
		def proteinOnly(s):
			return s.hasProtein()
		self.chainOptionMenu = MoleculeChainOptionMenu(chainPage,
						filtFunc=proteinOnly)
		self.chainOptionMenu.grid(row=0, column=0)

		textPage = nb.add("Plain Text")
		self.seqText = Pmw.ScrolledText(textPage, labelpos="nw",
					label_text="Sequence")
		self.seqText.grid(row=0, column=0, sticky="nsew")
		textPage.rowconfigure(0, weight=1)
		textPage.columnconfigure(0, weight=1)

		self.addParametersUI(master)

	def Apply(self):
		args = self.checkParameters()
		if args is None:
			return
		if self.notebook.getcurselection() == "Plain Text":
			bases = [ c for c in self.seqText.getvalue().upper()
					if c.isalpha() ]
			if not bases:
				replyobj.error(
					"Must supply contents of sequence\n")
				return
			seq = ''.join(bases)
			BlastResultsDialog(seq=seq, blastData=args)
		else:
			chain = self.chainOptionMenu.getvalue()
			if chain is None:
				replyobj.error("No molecule chain selected\n")
				return
			BlastResultsDialog(mol=chain, blastData=args)

class BlastDialog(ModalDialog, BlastParameters):

	name = "blast parameters"
	title = "Blast Parameters"
	buttons = ("OK", "Cancel")
	help = "UsersGuide/blast.html"

	def fillInUI(self, master):
		self.addParametersUI(master)

	def OK(self):
		args = self.checkParameters()
		if args is None:
			return
		self.Cancel(value=args)

def blastprotein(mol, *args):
	BlastResultsDialog(mol=mol, blastData=args)

class BlastResultsDialog(ModelessDialog):

	buttons = ( "Show in MAV", "Load Structure", "Hide", "Quit" )
	help = "UsersGuide/blast.html#results"

	def __init__(self, mol=None, seq=None, blastData=None, sessionData=None):
		self.loaded = {}
		self.reference = mol
		if isinstance(self.reference, StructureSequence):
			self.molecule = self.reference.molecule
		elif isinstance(self.reference, Molecule):
			self.molecule = self.reference
		self.sequence = seq	# for session data only
		if seq is None:
			self.seq, self.refResList = self._makeSeq(mol)
		else:
			self.seq = seq
			if self.reference:
				seq, resList = self._makeSeq(mol)
				self.refResList = self._getResidues(self.seq,
								seq, resList)
		if blastData:
			self.initBlast(*blastData)
		else:
			self.initSession(*sessionData)
		self.title = "Blast: %s" % self.basename
		ModelessDialog.__init__(self)
		if not blastData:
			self._updateLoadButton()
		if self.molecule:
			self.closeHandler = chimera.openModels.addRemoveHandler(
						self._modelClosedCB, None)
		else:
			self.closeHandler = None
		self.sesHandler = chimera.triggers.addHandler(
						SAVE_SESSION,
						self._sessionCB, None)
		chimera.extension.manager.registerInstance(self)

	def _makeSeq(self, mol):
		if isinstance(mol, StructureSequence):
			if not mol.hasProtein():
				raise UserError("No protein sequence found "
						"in %s %s\n" % (
							mol.molecule.name,
							mol.name))
			return ''.join(mol.sequence), mol.residues
		elif isinstance(mol, Molecule):
			from chimera import resCode
			seq = []
			refResList = []
			for r in mol.residues:
				try:
					seq.append(resCode.protein3to1[r.type])
				except KeyError:
					pass
				else:
					refResList.append(r)
			if len(seq) == 0:
				raise UserError("No protein sequence "
						"found in %s\n" % mol.name)
			return ''.join(seq), refResList
		else:
			raise ValueError("Blast Protein not called with "
						"molecule or chain\n")
	
	def initBlast(self, prog, db, evalue, matrix, passes, showOne):
		import os.path
		self.program = prog
		if self.molecule is not None:
			base = os.path.basename(self.molecule.name)
		else:
			try:
				base = self.seq.name
			except AttributeError:
				base = "query"
		self.basename = base.replace(' ', '_')
		self.showOne = showOne
		self.parser = None
		from Parser import BlastproteinService
		self.service = BlastproteinService(self._finish, params=(
							prog, db,
							self.basename,
							self.seq, evalue,
							matrix, passes))
		self.tableData = None

	def initSession(self, program, name, showOne, parserData,
						serviceData, tableData):
		self.basename = name
		self.program = program
		self.showOne = showOne
		if parserData:
			from Parser import restoreParser
			self.parser = restoreParser(parserData)
		else:
			self.parser = None
		if serviceData:
			from Parser import BlastproteinService
			self.service = BlastproteinService(self._finish,
							sessionData=serviceData)
		else:
			self.service = None
		self.tableData = tableData

	def fillInUI(self, parent):
		from CGLtk.Table import SortableTable
		self.blastTable = SortableTable(parent)
		if not self.tableData:
			self._addColumn("GI", "lambda m: m.gi",
					format="%s ", anchor="w")
			self._addColumn("PDB", "lambda m: m.pdb or '-'",
					format="%s ", anchor="w")
			self._addColumn("Evalue", "lambda m: m.evalue",
					format="%s")
			self._addColumn("Score", "lambda m: m.score",
					format="%s")
			self._addColumn("Description",
					"lambda m: m.description",
					format=" %s", anchor="w")
		if self.parser:
			self.blastTable.setData(self.parser.matches)
		else:
			self.blastTable.setData([])
		self.blastTable.launch(browseCmd=self._selectHitCB,
					restoreInfo=self.tableData)
		self.blastTable.pack(expand=True, fill="both")
		bw = self.buttonWidgets
		bw["Show in MAV"].config(state="disabled")
		bw["Load Structure"].config(state="disabled")
		bw["Quit"].config(state="disabled")

	def _finish(self, results):
		if self.blastTable is None:
			# We already quit, so UI is gone
			return
		from Parser import Parser
		import os.path
		try:
			self.parser = Parser(self.basename, results,
						self.program == "psiblast")
		except SyntaxError, s:
			replyobj.error("BLAST error: %s\n" % s)
			return
		except:
			replyobj.reportException("BLAST error")
			return
		self.service = None
		if self.showOne:
			matches = []
			seen = set()
			for m in self.parser.matches:
				if m.pdb is not None:
					parts = m.pdb.split('_')
					pdb = parts[0]
					if pdb in seen:
						continue
					seen.add(pdb)
				matches.append(m)
			self.parser.matches = matches
		self.blastTable.setData(self.parser.matches)
		self._updateLoadButton()

	def _updateLoadButton(self):
		bw = self.buttonWidgets
		if self.parser is None:
			bw["Quit"].config(state="disabled")
			bw["Load Structure"].config(state="disabled")
			bw["Show in MAV"].config(state="disabled")
			return
		sel = self.blastTable.selected()
		if not sel:
			sel = self.parser.matches
		state = "disabled"
		for m in sel:
			if m.pdb is not None:
				state = "normal"
		self.buttonWidgets["Load Structure"].config(state=state)
		bw["Show in MAV"].config(state="normal")
		bw["Quit"].config(state="normal")

	def _addColumn(self, title, attrFetch, **kw):
		if title in [c.title for c in self.blastTable.columns]:
			return
		c = self.blastTable.addColumn(title, attrFetch, **kw)
		self.blastTable.columnUpdate(c)

	def _selectHitCB(self, tableSel):
		self._updateLoadButton()

	def _modelClosedCB(self, trigger, closure, mols):
		self.loaded = dict([ item for item in self.loaded.items()
					if item[1] not in mols ])
		if self.molecule not in mols:
			return
		if not self.loaded:
			self.reference = None
			self.molecule = None
			self.refResList = None
		else:
			match, mol = self.loaded.popitem()
			self._setReference(match, mol)

	def _sessionCB(self, trigger, myData, sesFile):
		import SimpleSession
		if self.reference:
			if isinstance(self.reference, StructureSequence):
				mid = None
				ss = self.reference.saveInfo()
			elif isinstance(self.reference, Molecule):
				mid = SimpleSession.sessionID(self.reference)
				ss = None
			else:
				mid = None
				ss = None
		else:
			mid = None
			ss = None
		if self.parser:
			parserData = self.parser.sessionData()
		else:
			parserData = None
		if self.service:
			serviceData = self.service.sessionData()
		else:
			serviceData = None
		data = (3,					# version
			mid,					# molecule
			ss,					# StructureSeq
			self.sequence,				# input seq
			self.program,				# program
			self.basename,				# name
			self.showOne,				# one hit per PDB
			parserData,				# parser
			serviceData,				# service
			self.blastTable.getRestoreInfo())	# GUI
		print >> sesFile, """
try:
	from blastpdb.gui import sessionRestore
	sessionRestore(%s)
except:
	reportRestoreError("Error restoring Blast dialog")
""" % SimpleSession.sesRepr(data)

	def exit(self):
		if self.closeHandler:
			chimera.openModels.deleteRemoveHandler(
							self.closeHandler)
			self.closeHandler = None
		if self.sesHandler:
			chimera.triggers.deleteHandler(SAVE_SESSION,
							self.sesHandler)
			self.sesHandler = None
		chimera.extension.manager.deregisterInstance(self)
		self.destroy()
		self.blastTable = None

	def ShowinMAV(self):
		from cStringIO import StringIO
		s = StringIO()
		sel = self.blastTable.selected()
		if not sel:
			sel = self.parser.matches
		self.parser.writeMSF(s, matches=sel)
		s.seek(0)
		from MultAlignViewer.parsers import readMSF
		seqs, fileType, markups = readMSF.parse(s)
		from MultAlignViewer import MAViewer
		mav = MAViewer.MAViewer(seqs, fileType=fileType)
		mav.deleteAllGaps()
		mav._edited = False	# don't bother user with question
					# about alignment being edited

	def LoadStructure(self):
		sel = self.blastTable.selected()
		if not sel:
			sel = self.parser.matches
		sel = [ m for m in sel if m.pdb ]
		if len(sel) > 5:
			from chimera.baseDialog import AskYesNoDialog
			from chimera import tkgui
			d = AskYesNoDialog("This will load %d models."
					"  Proceed?" % len(sel),
					default="Yes")
			if d.run(self.uiMaster().winfo_toplevel()) != "yes":
				return
		mList = []
		for m in sel:
			if not m.pdb:
				continue
			parts = m.pdb.split('_')
			pdb = parts[0]
			mol = chimera.openModels.open(pdb, type="PDBID")[0]
			mList.append((m, mol))
		if self.reference is None:
			# Make the first model loaded the reference model
			# so others align to it.
			m, mol = mList[0]
			self._setReference(m, mol)
		for m, mol in mList:
			if mol is self.molecule:
				continue
			resList = self._getMatchResidues(m, mol)
			if resList:
				self._match(mol, m, resList)

	def _setReference(self, match, mol):
		# refMatch and match are already aligned
		refMatch = self.parser.matches[0]
		if len(refMatch.sequence) != len(match.sequence):
			raise ValueError("Blast: alignment length mismatch\n")
		resList = self._getMatchResidues(match, mol)
		rIndex = 0
		self.reference = mol
		if isinstance(self.reference, StructureSequence):
			self.molecule = self.reference.molecule
		elif isinstance(self.reference, Molecule):
			self.molecule = self.reference
		self.refResList = []
		for i, ms in enumerate(match.sequence):
			rs = refMatch.sequence[i]
			if rs == '-':
				if ms != '-':
					rIndex += 1
			else:
				if ms == '-':
					self.refResList.append(None)
				else:
					self.refResList.append(resList[rIndex])
					rIndex += 1

	def _getMatchResidues(self, match, mol):
		# Since the match sequence may be a subset of the
		# entire PDB structure, we cannot do the same thing
		# as for the reference model where we created the
		# match sequence from the structure.  Instead, we
		# find the best match of match sequence to
		# structure sequence using Needleman&Wunsch, and
		# then pull the residues corresponding to the
		# match sequence.
		matchSeq = [ s for s in match.sequence if s != '-' ]
		parts = match.pdb.split('_')
		try:
			chain = parts[1]
		except IndexError:
			chain = ' '
		seq = None
		for s in mol.sequences():
			if s.chain == chain or chain is None:
				seq = s
				break
		else:
			replyobj.error("%s: chain '%s' not found\n"
					% (match.pdb, chain))
			return None
		self.loaded[match] = mol
		return self._getResidues(matchSeq, seq.sequence, seq.residues)

	def _getResidues(self, matchSeq, molSeq, molRes):
		from NeedlemanWunsch import nw
		score, matchList = nw(matchSeq, molSeq)
		matchMap = dict(matchList)
		resList = []
		for mi in range(len(matchSeq)):
			try:
				si = matchMap[mi]
			except KeyError:
				r = None
			else:
				r = molRes[si]
			resList.append(r)
		return resList

	def _match(self, tmol, tm, tres):
		rmol = self.molecule
		rm = self.parser.matches[0]
		rres = self.refResList

		rs = rm.sequence	# reference sequence
		ri = 0			# reference residue index
		rAtoms = []		# reference atom list
		ts = tm.sequence	# t = target
		ti = 0
		tAtoms = []
		# Find corresponding residue pairs and add
		# CA to each atom list
		if len(rm.sequence) != len(tm.sequence):
			replyobj.error("sequence length mismatch: %s and %s\n"
					% (rm.pdb, tm.pdb))
			return
		for si in range(len(rm.sequence)):
			if rs[si] == '-':
				rr = None
			else:
				rr = rres[ri]
				ri += 1
			if ts[si] == '-':
				tr = None
			else:
				tr = tres[ti]
				ti += 1
			if rr is None or tr is None:
				continue
			ra = rr.findAtom("CA")
			ta = tr.findAtom("CA")
			if ra is not None and ta is not None:
				rAtoms.append(ra)
				tAtoms.append(ta)

		from chimera import match
		xform, rmsd = match.matchAtoms(rAtoms, tAtoms)
		xf = rmol.openState.xform
		xf.multiply(xform)
		tmol.openState.xform = xf
		replyobj.info("RMSD between %s and %s over %d residues "
				"is %.3f angstroms\n"
				% (rmol.name, tm.name(), len(rAtoms), rmsd))

	def emName(self):
		return self.title

	def emRaise(self):
		self.enter()

	def emHide(self):
		self.Close()
	Hide = emHide

	def emQuit(self):
		self.exit()
	Quit = emQuit

def sessionRestore(sessionData):
	from SimpleSession import idLookup
	version = sessionData[0]
	if version == 1:
		(v, mid, program, name, parserData, serviceData,
							tableData) = sessionData
		mol = idLookup(mid)
		seq = None
		showOne = False
	elif version == 2:
		(v, mid, seq, program, name, parserData, serviceData,
							tableData) = sessionData
		mol = idLookup(mid)
		showOne = False
	elif version == 3:
		(v, mid, ss, seq, program, name, showOne,
				parserData, serviceData, tableData) = sessionData
		if mid is not None:
			mol = idLookup(mid)
		elif ss is not None:
			mol = chimera.Sequence.restoreSequence(ss)
		else:
			mol = None
	else:
		raise ValueError("unknown blastpdb version: %s" % str(version))
	BlastResultsDialog(mol=mol, seq=seq, sessionData=(program, name,
								showOne,
								parserData,
								serviceData,
								tableData))

from chimera import dialogs
dialogs.register(BlastChainDialog.name, BlastChainDialog)
dialogs.register(BlastDialog.name, BlastDialog)
