# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: misc.py 27782 2009-06-08 22:08:20Z gregc $

import chimera
from string import digits
import operator
import os, os.path

def getPseudoBondGroup(category, modelID=-1, associateWith=[], hidden=1,
							issueHint=False):
	"""get a pseudobond group regardless of whether it already exists

	   This is utility function to perform the commonly-desired task
	   of getting a pseudobond group whether or not it already exists.
	   If the group does exist, that group is returned.  Otherwise,
	   the group is created, added to the open models, and returned.

	   'modelID' is the model ID to open the group in.  If you use a
	      negative number other than '-1', then the PseudoBondGroup
	      panel will not allow that group to be closed.
	   'associateWith' is a list of models that the pseudobond group
	      is closely associated with.  If any of those models are closed,
	      then the pseudobond group will also be closed.
	   'hidden' indicates that the group shouldn't normally appear in
	      the list of open models (and Model Panel; will still appear
	      in Pseudobond Panel)
	   'issueHint' controls whether a hint about usage of the Pseudobond
	      panel will appear in the status line after the group is created
	"""

	mgr = chimera.PseudoBondMgr.mgr()
	group = mgr.findPseudoBondGroup(category)
	if not group:
		group = mgr.newPseudoBondGroup(category)
		if len(associateWith) == 1:
			addKw = { 'sameAs': associateWith[0] }
		else:
			addKw = { 'baseId': modelID }
		chimera.openModels.add([group], hidden=hidden, **addKw)
		for model in associateWith:
			model.addAssociatedModel(group)
		if not chimera.nogui and issueHint:
			def f(c = category):
				import replyobj
				from tkgui import app
				words = c.split()
				firstWords = " ".join([w for w in words[:2]])
				if len(words) > 2:
					phrase = firstWords + "..."
				else:
					phrase = firstWords
				app.after(10000, lambda r=replyobj, c=c:
					r.status('Control "%s" pseudobonds'
					" with Pseudobond Panel (in Tools..."
					"General Controls)" % phrase))
			chimera.registerPostGraphicsFunc(f)
	return group


def chimeraLabel(item, showModel=None, modelName=False, style=None,
						diffWith=None, bondSep="-"):
	"""Return preferred chimera label for atom/bond/residue/molecule

	   'showModel' controls whether the model ID is part of the label
	   If the value type is boolean, then the model is shown if the value
	   is true.  If the value is None, then the model is shown if there
	   are multiple models, otherwise the model is omitted.

	   'modelName' controls whether the model name is part of the label.
	   Has no effect if atom specs are being returned.

	   'diffWith' can either be a string or of the same type as 'item';
	   the returned label will not include any leading components that
	   are the same as those in 'diffWith'

	   'style' controls whether the label uses atom specs, quasi-
	   English-like contents, or serial numbers.  It is either 'simple',
	   'command'/'command-line'/'osl', 'serial number', or None.
	   If None, then the user's preferences controls the contents.

	   'bondSep' controls the text separator between parts of a bond
	   when using English-like contents.
	"""

	if diffWith and not isinstance(diffWith, basestring):
		diffWith = chimeraLabel(diffWith, showModel, modelName, style)

	if not style:
		if chimera.nogui:
			style = "osl"
		else:
			import preferences
			from tkgui import GENERAL, ATOMSPEC_CONTENTS, \
					ATOMSPEC_SERIAL, ATOMSPEC_SIMPLE
			preferred = preferences.get(GENERAL, ATOMSPEC_CONTENTS)
			if preferred == ATOMSPEC_SERIAL:
				style = "serial number"
			elif preferred == ATOMSPEC_SIMPLE:
				style = "simple"
			else:
				# ATOMSPEC_MIDAS doesn't match value used
				# in NamingStyleOption, so make this the
				# 'else' case
				style = "osl"
	if style.startswith('command'):
		style = "osl"
	elif style.startswith('serial'):
		# command keyword values might only be 'serial'
		style = "serial number"

	if style == "serial number" and (not isinstance(item,  chimera.Atom)
				or not hasattr(item, 'serialNumber')):
		style = "simple"

	if isinstance(item, chimera.Bond) \
	or isinstance(item, chimera.PseudoBond):
		l1 = chimeraLabel(item.atoms[0], showModel, modelName,
								style, diffWith)
		l2 = chimeraLabel(item.atoms[1], showModel,
							modelName, style, l1)
		if not l2:
			l2 = item.atoms[1].name
		return l1 + bondSep + l2

	doShowModel = False
	if showModel:
		doShowModel = True
	if not doShowModel and isinstance(item, chimera.Model):
		doShowModel = True
	if not doShowModel and showModel == None \
	and len(chimera.openModels.list()) > 1:
		doShowModel = True
	if style == "osl":
		return chimeraOslLabel(item, diffWith, doShowModel)

	components = []
	if doShowModel:
		if hasattr(item, 'molecule') and item.molecule:
			mol = item.molecule
		else:
			mol = item

		if showModel or not modelName:
			components.append(mol.oslIdent())
		if modelName:
			if doShowModel:
				components.append("%s(%s)" % (mol.name,
							mol.oslIdent()))
			else:
				components.append(mol.name)
	if style == "serial number":
		if components and diffWith and diffWith.startswith(
							components[0] + " "):
			components = []
		return " ".join(components + [str(item.serialNumber)])
	res = None
	if isinstance(item, chimera.Residue):
		res = item
	elif isinstance(item, chimera.Atom):
		res = item.residue
	if res:
		components.append("%s %s" % (res.type, res.id))

	if isinstance(item, chimera.Atom):
		components.append(item.oslIdent(chimera.SelAtom)[1:])

	if len(components) == 0:
		retVal = chimeraOslLabel(item)	# Non-molecular object
	else:
		retVal = " ".join(components)
	full = retVal
	if diffWith:
		if full == diffWith:
			return ""
		for i in range(len(components)):
			if diffWith.startswith(" ".join(components[:i+1])+" "):
				retVal = " ".join(components[i+1:])
	return retVal

def chimeraOslLabel(item, diffWith=None, showModel=True):
	"""Return chimera osl label text for a selectable item"""

	baseVal = item.oslIdent()
	if not showModel and ':' in baseVal:
		baseVal = baseVal[baseVal.index(':'):]
	if not diffWith:
		return baseVal
	elif baseVal == diffWith:
		return ""
	retVal = baseVal
	for i in range(len(diffWith)):
		if diffWith[i] in [':', '@']:
			if baseVal[:i] == diffWith[:i]:
				retVal = baseVal[i+1:]
	return retVal

def isProtein(model):
	"""Is the given model a protein?"""

	if not hasattr(model, 'residues'):
		return 0

	for res in model.residues:
		resAtoms = res.atomsMap
		if resAtoms.has_key('CA') \
		and resAtoms.has_key('O') \
		and resAtoms.has_key('N') \
		and resAtoms.has_key('C'):
			return 1
	return 0

def simplifyPath(path):
	curdir = os.getcwd() + os.sep
	homedir = os.path.expanduser("~") + os.sep
	if homedir == "~":
		homedir = None
	if path.startswith(curdir):
		return path[len(curdir):]
	if homedir and path.startswith(homedir):
		return "~" + os.sep + path[len(homedir):]
	return path

def principalAtom(res):
	"""return the 'chain trace' atom of a residue, if any
	
	   normally returns the C4' from a nucleic acid since that is
	   always present, but in the case of P-only traces it returns
	   the P
	"""

	atomsMap = res.atomsMap
	if "CA" in atomsMap and "N" in atomsMap and "C" in atomsMap:
		CA = atomsMap["CA"][0]
		if CA.element.name == "C":
			return CA
	elif "C3'" in atomsMap and "C4'" in atomsMap \
	and "C5'" in atomsMap and "O5'" in atomsMap:
		return atomsMap["C4'"][0]
	elif len(atomsMap) == 1:
		if "CA" in atomsMap:
			CA = atomsMap["CA"][0]
			if CA.element.name == "C":
				return CA
		elif "P" in atomsMap:
			from resCode import nucleic3to1
			if res.type in nucleic3to1:
				P = atomsMap["P"][0]
				if P.element.name == "P":
					return P
	return None

def displayResPart(residues, trace=0, backbone=0, other=0, side=0, add=0,
								skipIsolated=1):
	stdChainRoots = {}
	nonstdRoots = {}
	for res in residues:
		if skipIsolated:
			resAtom = res.atoms[0]
			root = resAtom.molecule.rootForAtom(resAtom, 1)
			if root.size.numAtoms == res.numAtoms():
				continue
		atomsMap = res.atomsMap
		if atomsMap.has_key("CA") \
		and atomsMap.has_key("N") \
		and atomsMap.has_key("C"):
			CA = atomsMap["CA"][0]
			N = atomsMap["N"][0]
			C = atomsMap["C"][0]
			if CA.element.name != "C":
				continue
			traceAtom = CA
			stdChainRoots[traceAtom.rootAtom(1)] = 1
			bothAtom = CA
			backboneAtoms = {N:1, CA:1, C:1}
			otherAtoms = {}
			for otherName in ["O", "OXT"]:
				try:
					otherAtoms[atomsMap[otherName][0]] = 1
				except KeyError:
					continue
		elif atomsMap.has_key("O3'") \
		and atomsMap.has_key("C3'") \
		and atomsMap.has_key("C4'") \
		and atomsMap.has_key("C5'") \
		and atomsMap.has_key("O5'"):
			traceAtom = atomsMap["C4'"][0]
			stdChainRoots[traceAtom.rootAtom(1)] = 1
			bothAtom = None
			backboneAtoms = {
				atomsMap["O3'"][0]:1,
				atomsMap["C3'"][0]:1,
				atomsMap["C4'"][0]:1,
				atomsMap["C5'"][0]:1,
				atomsMap["O5'"][0]:1
			}
			try:
				backboneAtoms[atomsMap["P"][0]] = 1
			except KeyError:
				pass
			
			otherAtoms = {}
			for otherName in ["O1P", "O2P", "O2'",
							"C2'", "O4'", "C1'"]:
				try:
					otherAtoms[atomsMap[otherName][0]] = 1
				except KeyError:
					continue
		else:
			atom = res.atoms[0]
			try:
				nonstdRoots[atom.rootAtom(1)].append(res)
			except KeyError:
				nonstdRoots[atom.rootAtom(1)] = [res]
			continue
		for a in res.atoms:
			if not add:
				a.display = 0
			if a.element.number == 1:
				if len(a.bonds) != 1:
					a.display = 1
					continue
				if not side:
					continue
				bonded = a.neighbors[0]
				if not backboneAtoms.has_key(bonded) \
				and not otherAtoms.has_key(bonded):
					a.display = 1
				continue
			if a == traceAtom:
				if trace:
					a.molecule.autochain = 1
					a.display = 1
					continue
			if backboneAtoms.has_key(a):
				if backbone:
					a.display = 1
				elif a != bothAtom:
					continue
			if otherAtoms.has_key(a):
				if other:
					a.display = 1
				continue
			if side:
				a.molecule.autochain = add
				a.display = 1
	if not side:
		# turn off weird parts of chain
		for chainRoot in stdChainRoots.keys():
			try:
				weirdos = nonstdRoots[chainRoot]
			except KeyError:
				continue
			for res in weirdos:
				for a in res.atoms:
					a.display = 0

def bonds(atomIter, internal=True):
	"""Return set of bonds [internal] to given atoms"""
	bd = set()
	ibd = set()
	for a in atomIter:
		for b in a.bonds:
			if b in bd:
				ibd.add(b)
			else:
				bd.add(b)
	if internal:
		return ibd
	return bd

def oslCmp(osl1, osl2):
	"""Compare two full OSL identifiers"""
	if not isinstance(osl1, basestring):
		# so we can compare tuples/lists with leading OSLs
		osl1 = osl1[0]
		osl2 = osl2[0]
	if ':' in osl1:
		(model1, rem1) = osl1.split(":")
	else:
		model1, rem1 = osl1, None
	if ':' in osl2:
		(model2, rem2) = osl2.split(":")
	else:
		model2, rem2 = osl2, None
	
	modelCmp = oslModelCmp(model1, model2)
	if modelCmp != 0:
		return modelCmp
	
	if rem1 is None or rem2 is None:
		return 0
	return oslResAtomCmp(rem1, rem2)

def oslModelCmp(model1, model2):
	"""Compare two model-part-only OSL identifiers"""
	if not isinstance(model1, basestring):
		# so we can compare tuples/lists with leading OSLs
		model1 = model1[0]
		model2 = model2[0]
	dotIndex = model1.find(".")
	if dotIndex >= 0:
		mID1 = int(model1[1:dotIndex])
		subID1 = int(model1[dotIndex+1:])
	else:
		mID1 = int(model1[1:])
		subID1 = 0
	
	dotIndex = model2.find(".")
	if dotIndex >= 0:
		mID2 = int(model2[1:dotIndex])
		subID2 = int(model2[dotIndex+1:])
	else:
		mID2 = int(model2[1:])
		subID2 = 0
	
	if mID1 != mID2:
		return cmp(mID1, mID2)
	return cmp(subID1, subID2)
	
def oslResAtomCmp(ra1, ra2):
	"""Compare two residue-and-atom OSL identifiers"""
	if not isinstance(ra1, basestring):
		# so we can compare tuples/lists with leading OSLs
		ra1 = ra1[0]
		ra2 = ra2[0]
	if '@' in ra1:
		(res1, atom1) = ra1.split("@")
	else:
		res1, atom1 = ra1, None
	if '@' in ra2:
		(res2, atom2) = ra2.split("@")
	else:
		res2, atom2 = ra2, None

	resCmp = oslResCmp(res1, res2)
	if resCmp != 0:
		return resCmp
	
	if atom1 is None or atom2 is None:
		return 0
	return oslAtomCmp(atom1, atom2)

def oslResCmp(res1, res2):
	"""Compare two residue-only OSL identifiers"""
	if not isinstance(res1, basestring):
		# so we can compare tuples/lists with leading OSLs
		res1 = res1[0]
		res2 = res2[0]
	resSeq1, insert1, chain1 = parseResID(res1)
	resSeq2, insert2, chain2 = parseResID(res2)

	if chain1 != chain2:
		return cmp(chain1, chain2)
	if insert1 != insert2:
		return cmp(insert1, insert2)
	return cmp(resSeq1, resSeq2)
	
def oslAtomCmp(atom1, atom2):
	"""Compare two atom-only OSL identifiers"""
	if not isinstance(atom1, basestring):
		# so we can compare tuples/lists with leading OSLs
		atom1 = atom1[0]
		atom2 = atom2[0]
	if atom1[0] == '@':
		atom1 = atom1[1:]
		atom2 = atom2[1:]
	dotIndex = atom1.find(".")
	if dotIndex >= 0:
		atomName1 = atom1[:dotIndex]
		alt1 = atom1[dotIndex+1:]
	else:
		atomName1 = atom1
		alt1 = " "

	dotIndex = atom2.find(".")
	if dotIndex >= 0:
		atomName2 = atom2[:dotIndex]
		alt2 = atom2[dotIndex+1:]
	else:
		atomName2 = atom2
		alt2 = " "

	if atomName1 != atomName2:
		return cmp(atomName1, atomName2)
	return cmp(alt1, alt2)

def parseResID(resID):
	"""Break a residue ID into sequence/insert code/chain"""

	if resID[0] == ':':
		resID = resID[1:]

	dotIndex = resID.find(".")
	if dotIndex >= 0:
		if resID[dotIndex-1] in digits:
			resSeq = int(resID[:dotIndex])
			insert = " "
		else:
			resSeq = int(resID[:dotIndex-1])
			insert = resID[dotIndex-1]
		chain = resID[dotIndex+1:]
	else:
		if resID[-1] in digits:
			resSeq = int(resID)
			insert = " "
		else:
			resSeq = int(resID[:-1])
			insert = resID[-1]
		chain = " "
	return resSeq, insert, chain

def getAtoms(atomContainer):
	"""polymorphic function to get an atom list from various things"""
	from chimera.Sequence import StructureSequence
	if isinstance(atomContainer, chimera.Molecule):
		return atomContainer.atoms
	elif isinstance(atomContainer, chimera.Residue):
		return atomContainer.oslChildren()
	elif isinstance(atomContainer, StructureSequence):
		return [ a for r in atomContainer.residues
						for a in r.oslChildren()]
	elif atomContainer and not isinstance(atomContainer[0], chimera.Atom):
		# list/tuple of Molecules, Sequences, etc.
		return [ a for ac in atomContainer for a in getAtoms(ac) ]
	return atomContainer

def atomSearchTree(atomContainer, sepVal=5.0):
	"""return an AdaptiveTree for spatially searching for atoms
	
	   'atomContainer' is a Molecule, Residue, Sequence, or list of atoms

	   'sepVal' is the 'sepVal' parameter passed to the AdaptiveTree
	   constructor (see CGLutil.AdaptiveTree)

	   returns the populated AdaptiveTree
	"""
	from CGLutil.AdaptiveTree import AdaptiveTree
	atoms = getAtoms(atomContainer)
	return AdaptiveTree([a.xformCoord().data() for a in atoms],
								atoms, sepVal)

def stringToAttr(string, prefix="", style="underscore", collapse=True):
	"""convert an arbitrary string into a legal Python identifier

	   'string' is the string to convert

	   'prefix' is a string to prepend to the result (the 'style' will
	     control whether the prefix is followed by an underscore or
	     capital letter)

	   'style' controls the handling of illegal characters:
	   	'underscore':  replace them with underscores
		'caps':  omit them and capitalize the next letter
	   
	   if style is 'underscore', then 'collapse' controls whether
	   consecutive underscores are collapsed into one

	   if there is no prefix and the string begins with a digit, an
	     underscore will be prepended
	"""
	attrName = prefix
	illegal = prefix
	for c in string:
		if not c.isalnum():
			illegal = True
			if style == "underscore" and illegal and not collapse:
				attrName += "_"
			continue
		if illegal:
			if style == "underscore":
				attrName += "_" + c
			else:
				attrName += c.upper()
		else:
			attrName += c
		illegal = False
	if illegal and style == "underscore":
		attrName += "_"
	if attrName[0].isdigit():
		attrName = "_" + attrName
	return attrName

class KludgeWeakWrappyDict(dict):
	"""kludge until wrappy types implement weak-reference methods.
	   Will go away when wrappy does implement those methods (then
	   use weakref.WeakKeyDictionary)
	
	   A problem with this kludge is that due to the trigger mechanism
	   holding a reference to a instance method, an instance will never
	   be garbage collected
	"""

	def __init__(self, typeName, *args, **kw):
		from chimera import triggers
		triggers.addHandler(typeName, self._trigCB, None)
		dict.__init__(self, *args, **kw)

	def _trigCB(self, trigName, myData, trigData):
		for inst in trigData.deleted:
			if inst in self:
				del self[inst]

def isInformativeName(name):
	nm = name.strip().lower()
	if "unknown" in nm:
		return False

	for c in nm:
		if c.isalnum():
			return True
	return False
