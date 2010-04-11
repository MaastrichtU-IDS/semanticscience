# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29196 2009-11-02 18:54:22Z pett $

import chimera
from chimera import LimitationError, replyobj

def getRotamers(res, phi=None, psi=None, cisTrans="trans", resType=None,
						lib="Dunbrack", log=False):
	"""Takes a Residue instance and optionally phi/psi angles  
	   (if different from the Residue), residue type (e.g. "TYR"), and/or  
	   rotamer library name.  Returns a boolean and a list of Molecule  
	   instances.  The boolean indicates whether the rotamers are backbone  
	   dependent.  The Molecules are each a single residue (a rotamer) and  
	   are in descending probability order.  Each has an attribute  
	   "rotamerProb" for the probability and "chis" for the chi angles.
	"""
	# find n/c/ca early to identify swapping non-amino acid before
	# the NoResidueRotamersError gets raised, which will attempt
	# a swap for ALA/GLY (and result in a traceback)
	resAtomsMap = res.atomsMap
	try:
		n = resAtomsMap["N"][0]
		ca = resAtomsMap["CA"][0]
		c = resAtomsMap["C"][0]
	except KeyError:
		raise LimitationError("N, CA, or C missing from %s:"
					" needed to position CB" % res)
	resType = resType or res.type
	if not phi and not psi:
		ignore, phi, psi, cisTrans = extractResInfo(res)
		if log:
			def _info(ang):
				if ang is None:
					return "none"
				return "%.1f" % ang
			replyobj.info("%s: phi %s, psi %s"
					% (res, _info(phi), _info(psi)))
			if cisTrans:
				replyobj.info(" " + cisTrans)
			replyobj.info("\n")
	replyobj.status("Retrieving rotamers from %s library\n"
					% getattr(lib, "displayName", lib))
	bbdep, params = getRotamerParams(resType, phi=phi, psi=psi,
						cisTrans=cisTrans, lib=lib)
	replyobj.status("Rotamers retrieved from %s library\n"
					% getattr(lib, "displayName", lib))

	template = chimera.restmplFindResidue(resType, False, False)
	tmplMap = template.atomsMap
	tmplN = tmplMap["N"]
	tmplCA = tmplMap["CA"]
	tmplC = tmplMap["C"]
	tmplCB = tmplMap["CB"]
	from chimera.molEdit import addAtom, addDihedralAtom, addBond
	from chimera.match import matchPositions, _coordArray
	xform, rmsd = matchPositions(_coordArray([n, ca, c]),
					_coordArray([tmplN, tmplCA, tmplC]))
	ncoord = xform.apply(tmplN.coord())
	cacoord = xform.apply(tmplCA.coord())
	cbcoord = xform.apply(tmplCB.coord())
	from data import chiInfo
	info = chiInfo[resType]
	bondCache = {}
	angleCache = {}
	torsionCache = {}
	from chimera.bondGeom import bondPositions
	mols = []
	middles = {}
	ends = {}
	for i, rp in enumerate(params):
		m = chimera.Molecule()
		mols.append(m)
		m.name = "rotamer %d of %s" % (i+1, res)
		r = m.newResidue(resType, ' ', 1, ' ')
		# can't use a local variable for r.atomsMap since we receive
		# only an unchanging copy of the map
		m.rotamerProb = rp.p
		m.chis = rp.chis
		rotN = addAtom("N", tmplN.element, r, ncoord)
		rotCA = addAtom("CA", tmplCA.element, r, cacoord, bondedTo=rotN)
		rotCB = addAtom("CB", tmplCB.element, r, cbcoord,
							bondedTo=rotCA)
		todo = []
		for i, chi in enumerate(rp.chis):
			n3, n2, n1, new = info[i]
			blen, angle = _lenAngle(new, n1, n2, tmplMap,
							bondCache, angleCache)
			n3 = r.atomsMap[n3][0]
			n2 = r.atomsMap[n2][0]
			n1 = r.atomsMap[n1][0]
			new = tmplMap[new]
			a = addDihedralAtom(new.name, new.element, n1, n2, n3,
						blen, angle, chi, bonded=True)
			todo.append(a)
			middles[n1] = [a, n1, n2]
			ends[a] = [a, n1, n2]

		# if there are any heavy non-backbone atoms bonded to template
		# N and they haven't been added by the above (which is the
		# case for Richardson proline parameters) place them now
		for tnnb in tmplN.bondsMap.keys():
			if tnnb.name in r.atomsMap or tnnb.element.number == 1:
				continue
			tnnbcoord = xform.apply(tnnb.coord())
			addAtom(tnnb.name, tnnb.element, r, tnnbcoord,
								bondedTo=rotN)

		# fill out bonds and remaining heavy atoms
		from chimera.idatm import typeInfo
		from chimera import distance
		done = set([rotN, rotCA])
		while todo:
			a = todo.pop(0)
			if a in done:
				continue
			tmplA = tmplMap[a.name]
			for bonded, bond in tmplA.bondsMap.items():
				if bonded.element.number == 1:
					continue
				try:
					rbonded = r.atomsMap[bonded.name][0]
				except KeyError:
					# use middles if possible...
					try:
						p1, p2, p3 = middles[a]
						conn = p3
					except KeyError:
						p1, p2, p3 = ends[a]
						conn = p2
					t1 = tmplMap[p1.name]
					t2 = tmplMap[p2.name]
					t3 = tmplMap[p3.name]
					xform, rmsd = matchPositions(
						_coordArray([p1,p2,p3]),
						_coordArray([t1,t2,t3]))
					pos = xform.apply(
						tmplMap[bonded.name].coord())
					rbonded = addAtom(bonded.name,
						bonded.element, r, pos,
						bondedTo=a)
					middles[a] = [rbonded, a, conn]
					ends[rbonded] = [rbonded, a, conn]
				if a not in rbonded.bondsMap:
					addBond(a, rbonded)
				if rbonded not in done:
					todo.append(rbonded)
			done.add(a)
	return bbdep, mols
				
def _lenAngle(new, n1, n2, tmplMap, bondCache, angleCache):
	from chimera import distance, angle
	bondKey = (n1, new)
	angleKey = (n2, n1, new)
	try:
		bl = bondCache[bondKey]
		ang = angleCache[angleKey]
	except KeyError:
		n2pos = tmplMap[n2].coord()
		n1pos = tmplMap[n1].coord()
		newpos = tmplMap[new].coord()
		bondCache[bondKey] = bl = distance(newpos, n1pos)
		angleCache[angleKey] = ang = angle(newpos, n1pos, n2pos)
	return bl, ang

class NoResidueRotamersError(ValueError):
	pass

def getRotamerParams(res, phi=None, psi=None, cisTrans="trans", lib="Dunbrack"):
	"""return a list of RotamerParams (in descending probability order).
	   The return value is actually a boolean and a list of RotamerParams.
	   The boolean is True if the RotamerParams are backbone dependent.

	   takes either a Residue instance, or a residue name (e.g. TRP) and
	   phi and psi angles.  If a Residue instance is given, its phi/psi
	   angles will be used.  If phi or psi is None or the residue is
	   chain-terminal, then backbone-independent rotamers are returned.

	   raises NoResidueRotamersError if the residue isn't in the database
	"""
	importName = getattr(lib, "importName", lib)
	exec "import %s as Library" % importName
	if isinstance(res, chimera.Residue):
		resName, phi, psi, cisTrans = extractResInfo(res)
	else:
		resName = res
	if resName in getattr(Library, 'cisTrans', []):
		resName += "-" + cisTrans
	if phi is None or psi is None \
	or not hasattr(Library, "dependentRotamerParams"):
		return False, Library.independentRotamerParams(resName)
	return True, Library.dependentRotamerParams(resName, phi, psi)

class RotamerParams:
	""" 'p' attribute is probability of this rotamer;
	    'chis' is list of chi angles
	"""
	def __init__(self, p, chis):
		self.p = p
		self.chis = chis

def extractResInfo(res):
	"""Takes a Residue instance.  Returns the residue type,  
	   phi, psi, and "cis" or "trans".
	"""
	try:
		n = res.atomsMap["N"][0]
		ca = res.atomsMap["CA"][0]
		c = res.atomsMap["C"][0]
	except KeyError, IndexError:
		return res.type, None, None, "trans"
	from chimera import dihedral
	for nb in n.neighbors:
		if nb.residue != res:
			phi = dihedral(*tuple(
				[x.xformCoord() for x in [nb, n, ca, c]]))
			break
	else:
		phi = None

	for nb in c.neighbors:
		if nb.residue != res:
			psi = dihedral(*tuple(
				[x.xformCoord() for x in [n, ca, c, nb]]))
			break
	else:
		psi = None

	# measure dihedral with previous residue...
	cisTrans = "trans"
	for nnb in n.neighbors:
		if nnb.residue == res or nnb.name != "C":
			continue
		for cnb in nnb.neighbors:
			if cnb.residue == nnb.residue \
			and cnb.name == "CA":
				omega = dihedral(*tuple([x.xformCoord()
					for x in [ca, n, nnb, cnb]]))
				if abs(omega) < 90.0:
					cisTrans = "cis"
					break
		break

	return res.type, phi, psi, cisTrans


def useRotamer(oldRes, rots, log=False):
	"""Takes a Residue instance and a list of one or more rotamers (as
	   returned by getRotamers) and swaps the Residue's side chain with
	   the given rotamers.  If more than one rotamer is in the list,
	   then alt locs will be used to distinguish the different side chains.
	"""
	try:
		oldN = oldRes.atomsMap["N"][0]
		oldCA = oldRes.atomsMap["CA"][0]
		oldC = oldRes.atomsMap["C"][0]
	except KeyError:
		raise LimitationError("N, CA, or C missing from %s:"
			" needed for side-chain pruning algorithm" % oldRes)
	import string
	altLocs = string.ascii_uppercase + string.ascii_lowercase \
				+ string.digits + string.punctuation
	if len(rots) > len(altLocs):
		raise LimitationError("Don't have enough unique alternate "
			"location characters to place %d rotamers." % len(rots))
	rotAnchors = {}
	for rot in rots:
		rotRes = rot.residues[0]
		try:
			rotAnchors[rot] = (rotRes.atomsMap["N"][0],
						rotRes.atomsMap["CA"][0])
		except KeyError:
			raise LimitationError("N or CA missing from rotamer:"
					" cannot matchup with original residue")
	# prune old side chain
	retain = set([oldN, oldCA, oldC])
	deathrow = [nb for nb in oldCA.neighbors if nb not in retain]
	serials = {}
	while deathrow:
		prune = deathrow.pop()
		serials[prune.name] = getattr(prune, "serialNumber", None)
		for nb in prune.neighbors:
			if nb not in deathrow and nb not in retain:
				deathrow.append(nb)
		oldRes.molecule.deleteAtom(prune)

	totProb = sum([r.rotamerProb for r in rots])
	oldAtoms = set([a.name for a in oldRes.atoms])
	for i, rot in enumerate(rots):
		rotRes = rot.residues[0]
		rotN, rotCA = rotAnchors[rot]
		if len(rots) > 1:
			altLoc = altLocs[i]
			extra = " using alt loc %s" % altLoc
		else:
			altLoc = None
			extra = ""
		if log:
			replyobj.info("Applying %s rotamer (chi angles: %s) to"
				" %s%s\n" % (rotRes.type, " ".join(["%.1f" % c
				for c in rot.chis]), oldRes, extra))
		from BuildStructure import changeResidueType
		changeResidueType(oldRes, rotRes.type)
		# add new side chain
		from chimera.molEdit import addAtom, addBond
		sprouts = [rotCA]
		while sprouts:
			sprout = sprouts.pop()
			builtSprout = oldRes.atomsMap[sprout.name][-1]
			for nb, b in sprout.bondsMap.items():
				try:
					builtNBs = oldRes.atomsMap[nb.name]
				except KeyError:
					needBuild = True
				else:
					if nb.name in oldAtoms or len(builtNBs) == i+1:
						needBuild = False
					else:
						needBuild = True
				if needBuild:
					if i == 0:
						serial = serials.get(nb.name,
								None)
					else:
						serial = None
					builtNB = addAtom(nb.name, nb.element,
						oldRes, nb.coord(),
						serialNumber=serial,
						bondedTo=builtSprout)
					if altLoc:
						builtNB.altLoc = altLoc
					builtNB.occupancy = rot.rotamerProb / totProb
					sprouts.append(nb)
				else:
					builtNB = builtNBs[-1]
				if builtNB not in builtSprout.bondsMap:
					addBond(builtSprout, builtNB)

		
class RotamerLibraryInfo:
	"""holds information about a rotamer library:
	   how to import it, what citation to display, etc.
	"""
	def __init__(self, importName):
		self.importName = importName
		exec "import %s as RotLib" % importName
		self.displayName = getattr(RotLib, "displayName", importName)
		self.description = getattr(RotLib, "description", None)
		self.citation = getattr(RotLib, "citation", None)
		self.citeName = getattr(RotLib, "citeName", None)

libraries = []
def registerLibrary(importName):
	"""Takes a string indicated the "import name" of a library
	   (i.e. what name to use in an import statement) and adds a  
	   RotamerLibraryInfo instance for it to the list of known
	   rotamer libraries ("Rotamers.libraries").
	"""
	libraries.append(RotamerLibraryInfo(importName))
registerLibrary("Dunbrack")
registerLibrary("Richardson.mode")
registerLibrary("Richardson.common")

backboneNames = set(['CA', 'C', 'N', 'O'])

def processClashes(residue, rotamers, overlap, hbondAllow, scoreMethod,
				makePBs, pbColor, pbWidth, ignoreOthers):
	testAtoms = []
	for rot in rotamers:
		testAtoms.extend(rot.atoms)
	from DetectClash import detectClash
	clashInfo = detectClash(testAtoms, clashThreshold=overlap,
				interSubmodel=True, hbondAllowance=hbondAllow)
	if makePBs:
		from chimera.misc import getPseudoBondGroup
		from DetectClash import groupName
		pbg = getPseudoBondGroup(groupName)
		pbg.deleteAll()
		pbg.lineWidth = pbWidth
		pbg.color = pbColor
	else:
		import DetectClash
		DetectClash.nukeGroup()
	resAtoms = set(residue.atoms)
	for rot in rotamers:
		score = 0
		for ra in rot.atoms:
			if ra.name in ("CA", "N", "CB"):
				# any clashes of CA/N/CB are already clashes of
				# base residue (and may mistakenly be thought
				# to clash with "bonded" atoms in nearby
				# residues
				continue
			if ra not in clashInfo:
				continue
			for ca, clash in clashInfo[ra].items():
				if ca in resAtoms:
					continue
				if ignoreOthers \
				and ca.molecule.id != residue.molecule.id:
					continue
				if scoreMethod == "num":
					score += 1
				else:
					score += clash
				if makePBs:
					pbg.newPseudoBond(ra, ca)
		rot.clashScore = score
	if scoreMethod == "num":
		return "%2d"
	return "%4.2f"

def processHbonds(residue, rotamers, drawHbonds, bondColor, lineWidth, relax,
			distSlop, angleSlop, twoColors, relaxColor, groupName,
			ignoreOtherModels, cacheDA=False):
	from FindHBond import findHBonds
	if ignoreOtherModels:
		targetModels = [residue.molecule] + rotamers
	else:
		targetModels = chimera.openModels.list(
				modelTypes=[chimera.Molecule]) + rotamers
	if relax and twoColors:
		color = relaxColor
	else:
		color = bondColor
	hbonds = dict.fromkeys(findHBonds(targetModels, intramodel=False,
		distSlop=distSlop, angleSlop=angleSlop, cacheDA=True), color)
	if relax and twoColors:
		hbonds.update(dict.fromkeys(findHBonds(targetModels,
					intramodel=False), bondColor))
	backboneNames = set(['CA', 'C', 'N', 'O'])
	# invalid H-bonds:  involving residue side chain or rotamer backbone
	invalidAtoms = set([ra for ra in residue.atoms
					if ra.name not in backboneNames])
	invalidAtoms.update([ra for rot in rotamers for ra in rot.atoms
					if ra.name in backboneNames])
	rotAtoms = set([ra for rot in rotamers for ra in rot.atoms
					if ra not in invalidAtoms])
	for rot in rotamers:
		rot.numHbonds = 0

	if drawHbonds:
		from chimera.misc import getPseudoBondGroup
		pbg = getPseudoBondGroup(groupName)
		pbg.deleteAll()
		pbg.lineWidth = lineWidth
	elif groupName:
		nukeGroup(groupName)
	for hb, color in hbonds.items():
		d, a = hb
		if (d in rotAtoms) == (a in rotAtoms):
			# only want rotamer to non-rotamer
			continue
		if d in invalidAtoms or a in invalidAtoms:
			continue
		if d in rotAtoms:
			rot = d.molecule
		else:
			rot = a.molecule
		rot.numHbonds += 1
		if drawHbonds:
			pb = pbg.newPseudoBond(d, a)
			pb.color = color

def processVolume(rotamers, columnName, volume):
	import AtomDensity
	sums = []
	for rot in rotamers:
		AtomDensity.set_atom_volume_values(rot, volume, "_vscore")
		scoreSum = 0
		for a in rot.atoms:
			if a.name not in backboneNames:
				scoreSum += a._vscore
			delattr(a, "_vscore")
		if not hasattr(rot, "volumeScores"):
			rot.volumeScores = {}
		rot.volumeScores[columnName] = scoreSum
		sums.append(scoreSum)
	minSum = min(sums)
	maxSum = max(sums)
	absMax = max(maxSum, abs(minSum))
	if absMax >= 100 or absMax == 0:
		return "%d"
	addMinusSign = len(str(int(minSum))) > len(str(int(absMax)))
	if absMax >= 10:
		return "%%%d.1f" % (addMinusSign + 4)
	precision = 2
	while absMax < 1:
		precision += 1
		absMax *= 10
	return "%%%d.%df" % (precision+2+addMinusSign, precision)


def nukeGroup(groupName):
	mgr = chimera.PseudoBondMgr.mgr()
	group = mgr.findPseudoBondGroup(groupName)
	if group:
		chimera.openModels.close([group])

from prefs import defaults, CLASH_METHOD, CLASH_THRESHOLD, HBOND_ALLOWANCE
from FindHBond import recDistSlop, recAngleSlop, flushCache
defaultCriteria = "dchp"
def useBestRotamers(resType, targets, criteria=defaultCriteria, lib="Dunbrack",
		preserve=False,
		# clash options
		overlapCutoff=defaults[CLASH_THRESHOLD],
			hbondAllowance=defaults[HBOND_ALLOWANCE],
			scoreMethod=defaults[CLASH_METHOD],
			ignoreOtherModels=False,
		# H-bond options
		relax=True, distSlop=recDistSlop, angleSlop=recAngleSlop,
		# density options
		density=None, log=True):
	"""implementation of "swapaa" command.  'targets' is a list of Residues."""
	from Midas import midas_text, MidasError
	lib = lib.capitalize()
	rotamers = {}
	toClose = []
	for res in targets:
		if resType == "same":
			rType = res.type
		else:
			rType = resType.upper()
		try:
			bbdep, rots = getRotamers(res, resType=rType, lib=lib,
								log=log)
		except NoResidueRotamersError:
			from SwapRes import swap, BackboneError
			if log:
				replyobj.info("Swapping %s to %s\n"
							% (res, rType))
			try:
				swap(res, rType, bfactor=None)
			except BackboneError, v:
				raise MidasError(str(v))
			continue
		except ImportError:
			raise MidasError("No rotamer library named '%s'" % lib)
		if preserve:
			rots = pruneByChis(rots, res, log=log)
		rotamers[res] = rots
		toClose.extend(rots)

	# this implementation allows tie-breaking criteria to be skipped if
	# there are no ties
	for char in criteria:
		if char == "d":
			# density
			if density == None:
				if criteria is defaultCriteria:
					continue
				raise MidasError("Density criteria requested"
					" but no density model specified")
			from VolumeViewer.volume import Volume
			if isinstance(density, list):
				density = [d for d in density
						if isinstance(d, Volume)]
			else:
				density = [density]
			if not density:
				raise MidasError("No volume models in"
					" specified model numbers")
			if len(density) > 1:
				raise MidasError("Multiple volume models in"
					" specified model numbers")
			allRots = []
			for res, rots in rotamers.values():
				chimera.openModels.add(rots,
					sameAs=res.molecule, hidden=True)
				allRots.extend(rots)
			processVolume(allRots, "cmd", density[0])
			chimera.openModels.remove(allRots)
			fetch = lambda r: r.volumeScores["cmd"]
			test = cmp
		elif char == "c":
			# clash
			for res, rots in rotamers.items():
				chimera.openModels.add(rots,
					sameAs=res.molecule, hidden=True)
				processClashes(res, rots, overlapCutoff,
					hbondAllowance, scoreMethod, False,
					None, None, ignoreOtherModels)
				chimera.openModels.remove(rots)
			fetch = lambda r: r.clashScore
			test = lambda v1, v2: cmp(v2, v1)
		elif char == 'h':
			# H bonds
			for res, rots in rotamers.items():
				chimera.openModels.add(rots,
					sameAs=res.molecule, hidden=True)
				processHbonds(res, rots, False, None, None,
					relax, distSlop, angleSlop, False,
					None, None, ignoreOtherModels,
					cacheDA=True)
				chimera.openModels.remove(rots)
			flushCache()
			fetch = lambda r: r.numHbonds
			test = cmp
		elif char == 'p':
			fetch = lambda r: r.rotamerProb
			test = cmp

		for res, rots in rotamers.items():
			best = None
			for rot in rots:
				val = fetch(rot)
				if best == None or test(val, bestVal) > 0:
					best = [rot]
					bestVal = val
				elif test(val, bestVal) == 0:
					best.append(rot)
			if len(best) > 1:
				rotamers[res] = best
			else:
				useRotamer(res, [best[0]], log=log)
				del rotamers[res]
		if not rotamers:
			break
	for res, rots in rotamers.items():
		if log:
			replyobj.info("%s has %d equal-value rotamers; choosing"
				" one arbitrarily.\n" % (res, len(rots)))
		useRotamer(res, [rots[0]], log=log)
	if toClose:
		chimera.openModels.close(toClose)

branchSymmetry = {
	'ASP': 1,
	'TYR': 1,
	'PHE': 1,
	'GLU': 2
}
def pruneByChis(rots, res, log=False):
	from data import chiInfo
	if res.type not in chiInfo:
		return rots
	info = chiInfo[res.type]
	rotChiInfo = chiInfo[rots[0].residues[0].type]
	if log:
		replyobj.info("Chi angles for %s:" % res)
	for chiNum, resNames in enumerate(info):
		try:
			rotNames = rotChiInfo[chiNum]
		except IndexError:
			break
		atoms = []
		try:
			for name in resNames:
				atoms.append(res.atomsMap[name][0])
		except KeyError:
			break
		from chimera import dihedral
		origChi = dihedral(*tuple([a.coord() for a in atoms]))
		if log:
			replyobj.info(" %.1f" % origChi)
		pruned = []
		nearest = None
		for rot in rots:
			atomsMap = rot.residues[0].atomsMap
			chi = dihedral(*tuple([atomsMap[name][0].coord()
							for name in rotNames]))
			delta = abs(chi - origChi)
			if delta > 180:
				delta = 360 - delta
			if branchSymmetry.get(res.type, -1) == chiNum:
				if delta > 90:
					delta = 180 - delta
			if not nearest or delta < nearDelta:
				nearest = rot
				nearDelta = delta
			if delta > 40:
				continue
			pruned.append(rot)
		if pruned:
			rots = pruned
		else:
			rots = [nearest]
			break
	if log:
		replyobj.info("\n")
	return rots
