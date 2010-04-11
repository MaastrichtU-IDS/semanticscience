# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29778 2010-01-13 23:28:14Z pett $

"""Add hydrogens to structures"""

import chimera
from chimera.bondGeom import single
from chimera.molEdit import addAtom
from chimera import Element, idatm, replyobj
import operator
from chimera.bondGeom import cos705 as cos70_5
from math import sqrt
sin70_5 = sqrt(1.0 - cos70_5 * cos70_5)

_treeDist = 3.25
_metalDist = 3.6
Hrad = 1.0

from chimera.elements import metals, halides
nonHbinders = metals | halides

class IdatmTypeInfo:
	def __init__(self, geometry, substituents):
		self.geometry = geometry
		self.substituents = substituents
typeInfo = {}
for nonHbinder in nonHbinders:
	typeInfo[nonHbinder.name] = IdatmTypeInfo(single, 0)
typeInfo.update(idatm.typeInfo)

def gatherUnknowns(models, prevUnknowns = []):
	"""Find atoms whose hydrogen-adding geometries are unknown"""
	puDict = {}
	for unk in prevUnknowns:
		puDict[unk] = 1
	newUnknowns = []
	for model in models:
		if not hasattr(model, 'atoms'):
			continue
		for atom in model.atoms:
			if atom.element.number == 0:
				continue
			if typeInfo.has_key(atom.idatmType) \
			or puDict.has_key(atom):
				continue
			newUnknowns.append(atom)
	return newUnknowns
	

def simpleAddHydrogens(models, unknownsInfo={}, hisScheme=None):
	"""Add hydrogens to given models using simple geometric criteria

	Geometric info for atoms whose IDATM types don't themselves provide
	sufficient information can be passed via the 'unknownsInfo' dictionary.
	The keys are atoms and the values are dictionaries specifying the
	geometry and number of substituents (not only hydrogens) for the atom.

	The 'hisScheme' keyword determines how histidines are handled.  If
	it is None then the residue name is expected to be HIE, HID, HIP, or
	HIS indicating the protonation state is epsilon, delta, both, or
	unspecified respectively.  Otherwise the value is a dictionary: the
	keys are histidine residues and the values are HIE/HID/HIP/HIS
	indication of the protonation state.  Histindines not in the
	dictionary will be protonated based on the nitrogens' atom types.

	
	the protonation is determined by the nitrogen atom type.

	This routine adds hydrogens immediately even if some atoms have
	unknown geometries.  To allow the user to intervene to specify
	geometries, use the 'initiateAddHyd' function of the unknownsGUI
	module of this package.
	"""

	from simple import addHydrogens
	atomList, typeInfo4Atom, namingSchemas, idatmType, hydrogenTotals, \
				hisNs, coordinations, fakeN, fakeC = \
				_prepAdd(models, unknownsInfo, hisScheme)
	_makeSharedData()
	invertXforms = {}
	for atom in atomList:
		if not typeInfo4Atom.has_key(atom):
			continue
		bondingInfo = typeInfo4Atom[atom]
		try:
			invert = invertXforms[atom.molecule]
		except KeyError:
			try:
				invert = atom.molecule.openState.xform
			except ValueError:
				invert = chimera.Xform.identity()
			invert.invert()
			invertXforms[atom.molecule] = invert

		addHydrogens(atom, bondingInfo, (namingSchemas[atom.residue],
			namingSchemas[atom.molecule]), hydrogenTotals[atom],
			idatmType, invert, coordinations.get(atom, []))
	postAdd(fakeN, fakeC)
	_deleteSharedData()
	replyobj.info("Hydrogens added\n")

def _prepAdd(models, unknownsInfo, hisScheme, needAll=False):
	global _serial
	_serial = None
	atomList = []
	typeInfo4Atom = {}
	namingSchemas = {}
	idatmType = {} # need this later; don't want a recomp
	hydrogenTotals= {}
	models = [m for m in models if hasattr(m, "atoms")]

	# add missing OXTs of "real" C terminii;
	# delete hydrogens of "fake" N terminii after protonation
	# and add a single "HN" back on, using same dihedral as
	# preceding residue;
	# delete extra hydrogen of "fake" C terminii after protonation
	realN, realC, fakeN, fakeC = determineTerminii(models)
	replyobj.info("Chain-initial residues that are actual N"
		" terminii: %s\n" % ", ".join([str(r) for r in realN]))
	replyobj.info("Chain-initial residues that are not actual N"
		" terminii: %s\n" % ", ".join([str(r) for r in fakeN]))
	replyobj.info("Chain-final residues that are actual C"
		" terminii: %s\n" % ", ".join([str(r) for r in realC]))
	replyobj.info("Chain-final residues that are not actual C"
		" terminii: %s\n" % ", ".join([str(r) for r in fakeC]))
	for rc in realC:
		completeTerminalCarboxylate(rc)
	# ensure that N terminii are protonated as N3+ (since Npl will
	# fail)
	for nter in realN+fakeN:
		try:
			n = nter.atomsMap["N"][0]
		except KeyError:
			continue
		n.idatmType = "N3+"

	coordinations = {}
	for cat, pbg in chimera.PseudoBondMgr.mgr().pseudoBondGroupsMap.items():
		if not cat.startswith("coordination complex"):
			continue
		for pb in pbg.pseudoBonds:
			for a in pb.atoms:
				coordinations.setdefault(a, []).append(pb.otherAtom(a))

	for model in models:
		for atom in model.atoms:
			if atom.element.number == 0:
				res = atom.residue
				model.deleteAtom(atom)
				if not res.atoms:
					model.deleteResidue(res)
		for atom in model.atoms:
			idatmType[atom] = atom.idatmType
			if typeInfo.has_key(atom.idatmType):
				# don't want to ask for idatmType in middle
				# of hydrogen-adding loop (since that will
				# force a recomp), so remember here
				typeInfo4Atom[atom] = typeInfo[atom.idatmType]
				atomList.append(atom)
				# sulfonamide nitrogens coordinating a metal
				# get an additional hydrogen stripped
				if coordinations.get(atom, []) and atom.element.name == "N":
					pns = atom.primaryNeighbors()
					if "Son" in [pn.idatmType for pn in pns]:
						from copy import copy
						ti = copy(typeInfo[atom.idatmType])
						ti.substituents -= 1
						typeInfo4Atom[atom] = ti
				continue
			if unknownsInfo.has_key(atom):
				typeInfo4Atom[atom] = unknownsInfo[atom]
				atomList.append(atom)
				continue
			replyobj.info("AddH: unknown hydridization for atom"
					" (%s) of residue type %s" %
					(atom.name, atom.residue.type))
		
		namingSchemas.update(
				determineNamingSchemas(model, typeInfo4Atom))
	if needAll:
		for model in chimera.openModels.list(
						modelTypes=[chimera.Molecule]):
			if model in models:
				continue
			for atom in model.atoms:
				idatmType[atom] = atom.idatmType
				if typeInfo.has_key(atom.idatmType):
					typeInfo4Atom[atom] = \
						typeInfo[atom.idatmType]
	
	for atom in atomList:
		if not typeInfo4Atom.has_key(atom):
			continue
		bondingInfo = typeInfo4Atom[atom]
		totalHydrogens = bondingInfo.substituents - len(
							atom.primaryBonds())
		for bonded in atom.primaryNeighbors():
			if bonded.element.number == 1:
				totalHydrogens = totalHydrogens + 1
		hydrogenTotals[atom] = totalHydrogens

	if hisScheme is None:
		hisScheme = {}
		for m in models:
			for r in m.residues:
				if r.type in ["HID", "HIE", "HIP"]:
					hisScheme[r] = r.type
	# create dictionary keyed on histidine residue with value of another
	# dictionary keyed on the nitrogen atoms with boolean values: True
	# equals should be protonated
	hisNs = {}
	for r, protonation in hisScheme.items():
		try:
			delta = r.atomsMap["ND1"][0]
			epsilon = r.atomsMap["NE2"][0]
		except KeyError:
			# find the ring, etc.
			rings = r.molecule.minimumRings()
			for ring in rings:
				if ring.atoms.pop().residue == r:
					break
			else:
				continue
			# find CG by locating CB-CG bond
			ringBonds = ring.bonds
			for ra in ring.atoms:
				if ra.element.name != "C":
					continue
				for ba, b in ra.bondsMap.items():
					if ba.element.name == "C" \
					and b not in ringBonds:
						break
				else:
					continue
				break
			else:
				continue
			nitrogens = [a for a in ring.atoms
						if a.element.name == "N"]
			if len(nitrogens) != 2:
				continue
			if ra in nitrogens[0].neighbors:
				delta, epsilon = nitrogens
			else:
				epsilon, delta = nitrogens
		if protonation == "HID":
			hisNs.update({ delta: True, epsilon: False })
		elif protonation == "HIE":
			hisNs.update({ delta: False, epsilon: True })
		elif protonation == "HIP":
			hisNs.update({ delta: True, epsilon: True })
		else:
			continue
	for n, doProt in hisNs.items():
		if doProt:
			typeInfo4Atom[n] = typeInfo["Npl"]
			n.idatmType = idatmType[n] = "Npl"
		else:
			typeInfo4Atom[n] = typeInfo["N2"]
			n.idatmType = idatmType[n] = "N2"

	return atomList, typeInfo4Atom, namingSchemas, idatmType, \
			hydrogenTotals, hisNs, coordinations, fakeN, fakeC

def postAdd(fakeN, fakeC):
	# fix up non-"true" terminal residues (terminal simply because
	# next residue is missing)
	for fn in fakeN:
		try:
			n = fn.atomsMap["N"][0]
			ca = fn.atomsMap["CA"][0]
			c = fn.atomsMap["C"][0]
		except KeyError:
			continue
		dihed = None
		for cnb in c.primaryNeighbors():
			if cnb.name == "N":
				pn = cnb
				break
		else:
			dihed = 0.0
		if dihed is None:
			try:
				pr = pn.residue
				pc = pr.atomsMap["C"][0]
				pca = pr.atomsMap["CA"][0]
				if pr.type == "PRO":
					ph = pr.atomsMap["CD"][0]
				else:
					ph = pr.atomsMap["H"][0]
			except KeyError:
				dihed = 0.0
		for nb in n.primaryNeighbors():
			if nb.element.number == 1:
				nb.molecule.deleteAtom(nb)
		if fn.type == "PRO":
			continue
		if dihed is None:
			dihed = chimera.dihedral(pc.coord(), pca.coord(),
							pn.coord(), ph.coord())
		replyobj.info("Adding 'H' to %s\n" % str(fn))
		from chimera.molEdit import addDihedralAtom, addBond
		h = addDihedralAtom("H", Element(1), n, ca, c, 1.01, 120.0,
							dihed, bonded=True)
		# also need to set N's IDATM type, because if we leave it as
		# N3+ then the residue will be identified by AddCharge as
		# terminal and there will be no charge for the H atom
		n.idatmType = "Npl"

	for fc in fakeC:
		try:
			c = fc.atomsMap["C"][0]
		except KeyError:
			continue
		for nb in c.primaryNeighbors():
			if nb.element.number == 1:
				replyobj.info("Removing spurious proton from"
					" 'C' of %s\n" % str(fc))
				nb.molecule.deleteAtom(nb)
		# the N proton may have been named 'HN'; fix that
		try:
			hn = fc.atomsMap["HN"][0]
		except KeyError:
			continue
		addAtom("H", Element(1), fc, hn.coord(),
			serialNumber=hn.serialNumber, bondedTo=hn.neighbors[0])
		fc.molecule.deleteAtom(hn)


def hbondAddHydrogens(models, unknownsInfo={}, hisScheme=None):
	"""Add hydrogens to given models, trying to preserve H-bonding
	
	   Arguments are similar to simpleAddHydrogens() except that for
	   histidines not in the 'hisScheme' dictionary, the hydrogen-bond
	   interactions determine the histidine protonation.
	"""

	from hbond import addHydrogens

	# since h-bonds may go to other models (e.g. separate receptor/ligand)
	# need info for all models...
	atomList, typeInfo4Atom, namingSchemas, idatmType, hydrogenTotals, \
				hisNs, coordinations, fakeN, fakeC = _prepAdd(
				models, unknownsInfo, hisScheme, needAll=True)
	_makeSharedData()
	addHydrogens(atomList, typeInfo4Atom, namingSchemas, hydrogenTotals,
						idatmType, hisNs, coordinations)
	postAdd(fakeN, fakeC)
	_deleteSharedData()
	replyobj.info("Hydrogens added\n")

def determineNamingSchemas(molecule, typeInfo):
	"""Determine for each residue, method for naming hydrogens

	The possible schemas are:
		1) 'prepend' -- put 'H' in front of entire atom name
		2) a set of hetero atoms that should be prepended (others
		will have the element symbol replaced with 'H')
	
	In both cases, a number will be appended if more than one hydrogen
	is to be added. (Unless the base atom name ends in a prime [']
	character, in which case additional primes will be added as long
	as the resulting name is 4 characters or less)
	
	The "set" is the preferred scheme and is used when the heavy atoms
	have been given reasonably distinctive names.  'Prepend' is used
	mostly in small molecules where the atoms have names such as 'C1',
	'C2', 'C3', 'N1', 'N2', etc. and 'replace' would not work."""

	schemas = {molecule: 3} # default to PDB version 3 naming
	for residue in molecule.residues:
		if schemas[molecule] == 3 and residue.type in ["A", "C", "G",
				"T", "U"] and "O1P" in residue.atomsMap:
			schemas[molecule] = 2 # PDB version 2
		carbons = set()
		hets = set()
		for atom in residue.atoms:
			# skip pre-existing hydrogens
			if atom.element.number == 1:
				if not atom.name[0].isalpha():
					schemas[molecule] = 2 # PDB version 2
				continue
			
			# make sure leading characters are atomic symbol
			# (otherwise use 'prepend')
			symbol = atom.element.name
			if len(atom.name) < len(symbol) or \
			atom.name[0:len(symbol)].upper() != symbol.upper():
				schemas[residue] = 'prepend'
				break
			
			# if this atom won't have hydrogens added,
			# we don't care
			if not typeInfo.has_key(atom):
				continue
			num2add = typeInfo[atom].substituents - len(
							atom.primaryBonds())
			if num2add < 1:
				continue

			# if this atom has explicit naming given, don't
			# enter in identifiers dict
			resName = atom.residue.type
			if namingExceptions.has_key(resName) \
			and namingExceptions[resName].has_key(atom.name):
				continue
			if atom.element.name == "C":
				carbons.add(atom)
			else:
				hets.add(atom)
		else:
			identifiers = set()
			dups = set()
			for c in carbons:

				identifier = c.oslIdent(chimera.SelAtom)[2:]
				if identifier in identifiers:
					schemas[residue] = 'prepend'
					break
				identifiers.add(identifier)

			else:
				hetIdentifiers = set()
				for het in hets:
					identifier = het.oslIdent(
							chimera.SelAtom)[1:][
							len(het.element.name):]
					if identifier in identifiers:
						if identifier in hetIdentifiers:
							schemas[residue] = \
								'prepend'
							break
						else:
							dups.add(het)
							hetIdentifiers.add(
								identifier)
					else:
						identifiers.add(identifier)
				else:
					schemas[residue] = dups
	return schemas

_nucExc = { "O3'": ["H3T"], "O5'": ["H5T"], "O2'": ["2HO'"] }
namingExceptions = {
	"A": _nucExc, "+A": _nucExc,
	"C": _nucExc, "+C": _nucExc,
	"G": _nucExc, "+G": _nucExc,
	"I": _nucExc, "+I": _nucExc,
	"T": _nucExc, "+T": _nucExc,
	"U": _nucExc, "+U": _nucExc
}

def _sameName(resAtoms, altLoc, name):
	try:
		atoms = resAtoms[name]
	except KeyError:
		return False
	for a in atoms:
		if a.altLoc == altLoc:
			return True
	return False

def _Hname(atom, Hnum, totalHydrogens, namingSchema):
	resName = atom.residue.type
	resAtoms = atom.residue.atomsMap

	resSchema, pdbVersion = namingSchema
	if namingExceptions.has_key(resName) \
	and namingExceptions[resName].has_key(atom.name):
		for name in namingExceptions[resName][atom.name]:
			Hname = name
			if not resAtoms.has_key(Hname):
				break
	elif (resSchema == "prepend" or atom in resSchema) \
	or len(atom.name) < len(atom.element.name):
		Hname = "H" + atom.name
	else:
		Hname = "H" + atom.name[len(atom.element.name):]
	
	while len(Hname) + (totalHydrogens>1) > 4:
		if Hname.isalnum():
			Hname = Hname[:-1]
		else:
			Hname = "".join([x for x in Hname if x.isalnum()])

	if pdbVersion == 2:
		if totalHydrogens > 1 \
		or _sameName(resAtoms, atom.altLoc, Hname):
			while _sameName(resAtoms, atom.altLoc, "%d%s"
							% (Hnum, Hname)):
				Hnum += 1
			Hname = "%d%s" % (Hnum, Hname)
	elif Hname[-1] == "'" and len(Hname) + (totalHydrogens-1) <= 4:
		while _sameName(resAtoms, atom.altLoc, Hname):
			Hname += "'"
	elif totalHydrogens > 1 or _sameName(resAtoms, atom.altLoc, Hname):
		if totalHydrogens == 2 and len([nb for nb in
						atom.primaryNeighbors()
						if nb.element.number > 1]) == 2:
			Hnum += 1
		while _sameName(resAtoms, atom.altLoc, "%s%d" % (Hname, Hnum)):
			Hnum += 1
		Hname = "%s%d" % (Hname, Hnum)
	return Hname

def newHydrogen(parentAtom, Hnum, totalHydrogens, namingSchema, pos):
	global _serial, _metals
	nearbyMetals = _metals.searchTree(pos.data(), _metalDist)
	for metal in nearbyMetals:
		if metal.molecule != parentAtom.molecule:
			continue
		metalPos = metal.coord()
		parentPos = parentAtom.coord()
		if metalClash(metalPos, pos, parentPos):
			return
	newH = addAtom(_Hname(parentAtom, Hnum, totalHydrogens, namingSchema),
		Element(1), parentAtom.residue, pos, serialNumber=_serial,
		bondedTo=parentAtom)
	_serial = newH.serialNumber + 1
	from Midas import elementColor
	parentColor = parentAtom.color
	if parentColor == elementColor(parentAtom.element.name):
		newH.color = elementColor("H")
	else:
		newH.color = parentColor

def metalClash(metalPos, pos, parentPos):
	if metalPos.distance(parentPos) > _metalDist:
		return False
	if chimera.angle(parentPos, pos, metalPos) > 135.0:
		return True
	return False

def _byDist(a, b):
	return cmp(a[0].xformCoord().sqdistance(a[1].xformCoord()),
				b[0].xformCoord().sqdistance(b[1].xformCoord()))

def roomiest(positions, attached, checkDist):
	posInfo =[]
	for i in range(len(positions)):
		pos = positions[i]
		if isinstance(attached, list):
			atom = attached[i]
			val = (atom, [pos])
		else:
			atom = attached
			val = pos
		nearPos, nearest, nearA = findNearest(pos, atom, [], checkDist,
								avoidMetal=True)
		if nearest is None:
			nearest = checkDist
		posInfo.append((nearest, val))
	posInfo.sort(lambda a,b: cmp(a[0], b[0]))
	posInfo.reverse()
	# return a list of the values...
	return zip(*posInfo)[1]

def findNearest(pos, atom, exclude, checkDist, avoidMetal=False):
	nearby = searchTree.searchTree(pos.data(), checkDist)
	nearPos = n = nearAtom = None
	# Points don't have a hash function (yet) so use their data()
	excludePos = set([ex.xformCoord().data() for ex in exclude])
	excludePos.add(atom.xformCoord().data())
	for nb in nearby:
		nPos = nb.xformCoord()
		if nPos.data() in excludePos:
			# excludes identical models also...
			continue
		if nb.molecule != atom.molecule and (
				atom.molecule.id < 0 or nb.molecule.id == atom.molecule.id):
			# (1) unopen models only "clash" with themselves
			# (2) don't consider atoms in sibling submodels
			continue
		if nb not in atom.primaryNeighbors():
			if avoidMetal and nb.element in metals \
			and nb.molecule == atom.molecule:
				if metalClash(nb.xformCoord(), pos,
							atom.xformCoord()):
					return nPos, 0.0, nb
			d = (nPos - pos).length - vdwRadius(nb)
			if not nearPos or d < n:
				nearPos = nPos
				n = d
				nearAtom = nb
		# only heavy atoms in tree...
		for nbb in nb.primaryNeighbors():
			if nbb.element.number != 1:
				continue
			if nbb.xformCoord().data() in excludePos:
				continue
			nPos = nbb.xformCoord()
			d = (nPos - pos).length - Hrad
			if not nearPos or d < n:
				nearPos = nPos
				n = d
				nearAtom = nbb
	return nearPos, n, nearAtom

def findRotamerNearest(atPos, idatmType, atom, neighbor, checkDist):
	# find atom that approaches nearest to a methyl-type rotamer
	nPos = neighbor.xformCoord()
	v = atPos - nPos
	bondLen = bondWithHLength(atom, typeInfo[idatmType].geometry)
	v.length = cos70_5 * bondLen
	center = atPos + v
	plane = chimera.Plane(center, v)
	radius = sin70_5 * bondLen
	checkDist += radius

	nearby = searchTree.searchTree(center.data(), checkDist)
	nearPos = n = nearAtom = None
	for nb in nearby:
		if nb.xformCoord() in [atPos, nPos]:
			# exclude atoms from identical-copy molecules also...
			continue
		if nb.molecule != atom.molecule \
		and nb.molecule.id == atom.molecule.id:
			# don't consider atoms in sibling submodels
			continue
		candidates = [(nb, vdwRadius(nb))]
		# only heavy atoms in tree...
		for nbb in nb.primaryNeighbors():
			if nbb.element.number != 1:
				continue
			if nbb == neighbor:
				continue
			candidates.append((nbb, Hrad))

		for candidate, aRad in candidates:
			cPos = candidate.xformCoord()
			# project into plane...
			proj = plane.nearest(cPos)

			# find nearest approach of circle...
			cv = proj - center
			if cv.length == 0.0:
				continue
			cv.length = radius
			app = center + cv
			d = (cPos - app).length - aRad
			if not nearPos or d < n:
				nearPos = cPos
				n = d
				nearAtom = candidate
	return nearPos, n, nearAtom

def vdwRadius(atom):
	return _radii.get(atom, Hrad)

def _makeSharedData():
	from CGLutil.AdaptiveTree import AdaptiveTree
	# since adaptive search tree is static, it will not include
	# hydrogens added after this; they will have to be found by
	# looking off their heavy atoms
	global searchTree, _radii, _metals
	_radii = {}
	xyzs = []
	vals = []
	metalXyzs = []
	metalVals = []
	for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
		for a in m.atoms:
			xyzs.append(a.xformCoord().data())
			vals.append(a)
			_radii[a] = a.radius
			if a.element in metals:
				metalXyzs.append(a.coord().data())
				metalVals.append(a)
	searchTree = AdaptiveTree(xyzs, vals, _treeDist)
	_metals = AdaptiveTree(metalXyzs, metalVals, _metalDist)

def _deleteSharedData():
	global searchTree, _radii, _metals
	searchTree = radii = _metals = None

def cmdAddH(molecules=None, hbond=True, useHisName=True):
	if molecules is None:
		molecules = chimera.openModels.list(
					modelTypes=[chimera.Molecule])
	if hbond:
		addHFunc = hbondAddHydrogens
	else:
		addHFunc = simpleAddHydrogens
	if useHisName:
		hisScheme = None
	else:
		hisScheme = {}
	if chimera.nogui:
		addHFunc(molecules)
	else:
		from unknownsGUI import initiateAddHyd
		initiateAddHyd(molecules, addFunc=addHFunc, hisScheme=hisScheme)

N_H = 1.01
def bondWithHLength(heavy, geom):
	element = heavy.element.name
	if element == "C":
		if geom == 4:
			return 1.09
		if geom == 3:
			return 1.08
		if geom == 2:
			return 1.056
	elif element == "N":
		return N_H
	elif element == "O":
		# can't rely on water being in chain "water" anymore...
		if len(heavy.bonds) == 0 or (len(heavy.bonds) == 2
		and len([nb for nb in heavy.neighbors if nb.element.number > 1]) == 0):
			return 0.9572
		return 0.96
	elif element == "S":
		return 1.336
	return Element.bondLength(heavy.element, Element(1))

def determineTerminii(mols):
	realN = []
	realC = []
	fakeN = []
	fakeC = []
	for m in mols:
		for seq in m.sequences():
			if seq.fromSeqres:
				rn, rc, fn, fc = terminiiFromSeqres(seq)
				replyobj.info("Terminii for %s determined from"
					" SEQRES records\n" % seq.fullName())
			else:
				rn, rc, fn, fc = guessTerminii(seq)
				if seq.fromSeqres == None:
					replyobj.info("No SEQRES records for %s;" % seq.fullName())
				else:
					replyobj.info("SEQRES records don't match %s;" % seq.fullName())
				replyobj.info(" guessing terminii instead\n")
			realN.extend(rn)
			realC.extend(rc)
			fakeN.extend(fn)
			fakeC.extend(fc)
	return realN, realC, fakeN, fakeC

def guessTerminii(seq):
	realN = []
	realC = []
	fakeN = []
	fakeC = []
	residues = seq.residues
	nTerm = residues[0]
	if crossResidue(nTerm, 'N'):
		fakeN.append(nTerm)
	else:
		realN.append(nTerm)
	cTerm = residues[-1]
	if crossResidue(cTerm, 'C'):
		fakeC.append(cTerm)
	else:
		realC.append(cTerm)
	for i, res in enumerate(residues[:-1]):
		nextRes = residues[i+1]
		if chimera.bondsBetween(res, nextRes, onlyOne=True):
			continue
		if res.id.position + 1 < nextRes.id.position:
			fakeC.append(res)
			fakeN.append(nextRes)
	return realN, realC, fakeN, fakeC

def terminiiFromSeqres(seq):
	realN = []
	realC = []
	fakeN = []
	fakeC = []
	if seq.residues[0]:
		realN.append(seq.residues[0])
	if seq.residues[-1]:
		realC.append(seq.residues[-1])

	last = seq.residues[0]
	for res in seq.residues[1:]:
		if res:
			if not last:
				fakeN.append(res)
		else:
			if last:
				fakeC.append(last)
		last = res
	return realN, realC, fakeN, fakeC

def crossResidue(res, atName):
	try:
		a = res.atomsMap[atName][0]
	except KeyError:
		return False
	for bonded in a.bondsMap.keys():
		if bonded.residue != a.residue:
			return True
	return False

def completeTerminalCarboxylate(cter):
	from chimera.bondGeom import bondPositions
	from chimera.molEdit import addAtom
	if "OXT" in cter.atomsMap:
		return
	try:
		cs = cter.atomsMap["C"]
	except KeyError:
		return
	for c in cs: # alt locs are possible
		if len(c.primaryBonds()) != 2:
			return
		loc = bondPositions(c.coord(), 3, 1.229,
				[n.coord() for n in c.primaryNeighbors()])[0]
		oxt = addAtom("OXT", chimera.Element("O"), cter, loc,
								bondedTo=c)
	replyobj.info("Missing OXT added to C-terminal residue %s\n"
								% str(cter))
