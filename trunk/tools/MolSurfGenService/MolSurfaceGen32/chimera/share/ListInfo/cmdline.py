# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

def process(cmdName, args):
	from Midas.midas_text import doExtensionFunc
	try:
		func, kwargs = _cmdTable[cmdName]
	except KeyError:
		# We only get here if the command was registered
		# in ChimeraExtension.py but is not in our command table.
		# Assume that registration is correct and that we
		# just haven't implemented the function yet.
		import chimera
		raise chimera.UserError("%s: unimplemented command" % cmdName)
	doExtensionFunc(func, args, **kwargs)

def attrString(obj, attr):
	s = getattr(obj, attr)
	import chimera
	if isinstance(s, chimera.Color):
		r, g, b, a = s.rgba()
		if s.isTranslucent():
			return "%.3f,%.3f,%.3f,%.3f" % (r, g, b, a)
		else:
			return "%.3f,%.3f,%.3f" % (r, g, b)
	v = str(s)
	l = [ '"' ]
	needQuotes = False
	for c in v:
		if c in '"\\':
			l.append('\\')
		elif c in ' \t':
			needQuotes = True
		l.append(c)
	if needQuotes:
		l.append('"')
		return ''.join(l)
	else:
		return v

def listm(models=None, type="any", attribute="name"):
	import chimera
	if models is None:
		models = chimera.openModels.list()
	wantedType = type.lower()
	keep = []
	for m in models:
		molType = m.__class__.__name__
		if wantedType != "any" and wantedType != molType.lower():
			continue
		keep.append(m)
	_reportModels(keep, attribute)

def _reportModels(models, attribute):
	from chimera import replyobj
	for m in models:
		try:
			attrValue = attrString(m, attribute)
		except AttributeError:
			continue
		molType = m.__class__.__name__
		info = "model id %s type %s" % (m.oslIdent(), molType)
		info += " %s %s" % (attribute, attrValue)
		info += '\n'
		replyobj.info(info)

def listc(models=None, attribute="chain"):
	import chimera
	if models is None:
		models = chimera.openModels.list(modelTypes=[chimera.Molecule])
	chains = []
	for m in models:
		chains += m.sequences()
	_reportChains(chains, attribute)

def _reportChains(chains, attribute):
	from chimera import replyobj
	for seq in chains:
		try:
			attrValue = attrString(seq, attribute)
		except AttributeError:
			continue
		info = "chain id %s:.%s" % (seq.molecule.oslIdent(), seq.chain)
		info += " %s %s" % (attribute, attrValue)
		info += '\n'
		replyobj.info(info)

def listr(residues=None, attribute="type"):
	import chimera
	if residues is None:
		residues = []
		for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
			residues += m.residues
	_reportResidues(residues, attribute)

def _reportResidues(residues, attribute):
	from chimera import replyobj
	for r in residues:
		try:
			attrValue = attrString(r, attribute)
		except AttributeError:
			continue
		info = "residue id %s" % r.oslIdent()
		info += " %s %s" % (attribute, attrValue)
		info += '\n'
		replyobj.info(info)

def lista(atoms=None, attribute="idatmType"):
	import chimera
	from chimera import replyobj
	if atoms is None:
		atoms = []
		for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
			atoms += m.atoms
	_reportAtoms(atoms, attribute)

def _reportAtoms(atoms, attribute):
	from chimera import replyobj
	for a in atoms:
		try:
			attrValue = attrString(a, attribute)
		except AttributeError:
			continue
		info = "atom id %s" % a.oslIdent()
		info += " %s %s" % (attribute, attrValue)
		info += '\n'
		replyobj.info(info)

def lists(level="atom", mode="any", attribute=None):
	import chimera
	from chimera import replyobj, selection
	mode = findBestMatch(mode, ["any", "all"])
	level = findBestMatch(level, ["atom", "residue", "chain", "molecule"])
	if level == "atom":
		if attribute is None:
			attribute = "idatmType"
		_reportAtoms(selection.currentAtoms(), attribute)
	elif level == "residue":
		if mode == "any":
			residues = selection.currentResidues()
		else:
			rMap = {}
			for a in selection.currentAtoms():
				l = rMap.setdefault(a.residue, [])
				l.append(a)
			residues = []
			for r, aList in rMap.iteritems():
				if len(r.atoms) == len(aList):
					residues.append(r)
		if attribute is None:
			attribute = "type"
		_reportResidues(residues, attribute)
	elif level == "chain":
		if mode == "any":
			chains = selection.currentChains()
		else:
			rcMap = {}
			cached = set([])
			cMap = {}
			for r in selection.currentResidues():
				if r.molecule not in cached:
					cached.add(r.molecule)
					for seq in r.molecule.sequences():
						for res in seq.residues:
							rcMap[res] = seq
				try:
					seq = rcMap[r]
				except KeyError:
					pass
				else:
					l = cMap.setdefault(seq, [])
					l.append(r)
			chains = []
			for seq, rList in cMap.iteritems():
				if len(seq) == len(rList):
					chains.append(seq)
		if attribute is None:
			attribute = "chain"
		_reportChains(chains, attribute)
	elif level == "molecule":
		if mode == "any":
			molecules = selection.currentMolecules()
		else:
			mMap = {}
			for a in selection.currentAtoms():
				l = mMap.setdefault(a.molecule, [])
				l.append(a)
			molecules = []
			for m, aList in mMap.iteritems():
				if len(m.atoms) == len(aList):
					molecules.append(m)
		if attribute is None:
			attribute = "name"
		_reportModels(molecules, attribute)
	else:
		raise chimera.UserError("\"%s\": unknown listselection level"
					% level)

modelHandler = None
def _alertModel(trigger, prefix, molecules):
	from chimera import replyobj
	import sys
	r = replyobj.pushReply(None)
	for m in molecules:
		print "%s: model %s" % (prefix, m.oslIdent())
	sys.stdout.flush()
	replyobj.popReply(r)

selectionHandler = None
def _alertSelection(trigger, prefix, curSel):
	from chimera import replyobj
	import sys
	r = replyobj.pushReply(None)
	print "%s: selection changed" % prefix
	sys.stdout.flush()
	replyobj.popReply(r)

def listen(mode, what, prefix=None):
	from chimera import replyobj
	mode = findBestMatch(mode, ["start", "stop"])
	what = findBestMatch(what, ["models", "selection"])
	if what == "models":
		from chimera import openModels
		global modelHandler
		if mode == "start":
			if modelHandler is not None:
				msg = "already listening for models\n"
			else:
				if prefix is None:
					prefix = "ModelChanged"
				modelHandler = openModels.addAddHandler(
						_alertModel, prefix)
				msg = "listening for models\n"
		else:
			if modelHandler is None:
				msg = "not listening for models\n"
			else:
				openModels.deleteAddHandler(modelHandler)
				modelHandler = None
				msg = "stopped listening for models\n"
		replyobj.info(msg)
	elif what == "selection":
		import chimera
		global selectionHandler
		if mode == "start":
			if selectionHandler is not None:
				msg = "already listening for selection\n"
			else:
				if prefix is None:
					prefix = "SelectionChanged"
				selectionHandler = chimera.triggers.addHandler(
						"selection changed",
						_alertSelection, prefix)
				msg = "listening for selection\n"
		else:
			if selectionHandler is None:
				msg = "not listening for selection\n"
			else:
				chimera.triggers.deleteHandler(
						"selection changed",
						selectionHandler)
				selectionHandler = None
				msg = "stopped listening for selection\n"
		replyobj.info(msg)

def showSeq(molecules):
	from ModelPanel.base import seqCmd
	seqCmd(molecules)

_cmdTable = {
	"listmodels":	( listm, { "specInfo":
					[("spec", "models", "models")] }),
	"listchains":	( listc, { "specInfo":
					[("spec", "models", "models")] }),
	"listresidues":	( listr, { "specInfo":
					[("spec", "residues", "residues")] }),
	"listatoms":	( lista, { "specInfo":
					[("spec", "atoms", "atoms")] }),
	"listselection":( lists, {} ),
	"listen":	( listen, {} ),
	"sequence":	( showSeq, { "specInfo":
					[("spec", "molecules", "molecules")] }),
}

def findBestMatch(input, choices):
	bestMatch = None
	for choice in choices:
		if choice.startswith(input):
			if bestMatch is not None:
				raise ValueError("\"%s\" is ambiguous" % input)
			else:
				bestMatch = choice
	if bestMatch is None:
		raise ValueError("\"%s\" does not match any available choice"
				% input)
	return bestMatch
