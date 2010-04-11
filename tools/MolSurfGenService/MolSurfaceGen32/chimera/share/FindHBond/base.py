# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: base.py 28847 2009-09-23 18:54:45Z pett $

"""Hydrogen bond detection based on criteria in "Three-dimensional
	hydrogen-bond geometry and probability information from a
	crystal survey", J. Computer-Aided Molecular Design, 10 (1996),
	607-622
"""
verbose = False

from acceptorGeom import accSynAnti, accPhiPsi, accThetaTau, accGeneric
from donorGeom import donThetaTau, donUpsilonTau, donGeneric, donWater
from commonGeom import ConnectivityError, AtomTypeError
from math import pi
from ChemGroup import findGroup
from CGLutil.AdaptiveTree import AdaptiveTree
from hydpos import hydPositions
from chimera.idatm import typeInfo, tetrahedral, planar, linear, single
from chimera import Element, replyobj, UserError
from miscFind import *
import copy

from ChemGroup import H, N, C, O, R
Tet = {'geometry':tetrahedral}
SingleBond = ({'geometry':tetrahedral}, {'geometry':single})
NonO3minusSB = ({'geometry':tetrahedral, 'notType': ['O3-']},
							{'geometry':single})
NonSacPacHSB = ({'geometry':tetrahedral, 'notType': ['Sac', 'Pac']},
				{'geometry':single, 'notType': ['H', 'D']})

# recommended distance and angle constraint relaxations for biomolecules
recDistSlop = 0.4
recAngleSlop = 20.0

"""layout is:
	name or spec of acceptor group,
	tuple indicating index of acceptor or acceptors in group,
	function to determine if acceptor satisfied,
	tuple of arguments to give to that function

	in argument tuple, conversions will occur before function gets called.
	namely:
		floats are assumed to be distances, and will be squared
		integers are assumed to be angles in degrees, and will be
			converted to radians
		integer/None tuples are assumed to refer to other atoms in
			the group, and will be replaced by them.  None remains
			None.  '-1' means the other acceptor of the group.
			
"""
acceptorParams = [
	# phosphodiester-like (negative oxygens) [3+ O-]
	[[['Pac', ['O3-', 'O3-', 'O3-', SingleBond]], [1,1,1,1,0]],
		(1,), accSynAnti, ((2, 0), 3.03, 110, 145, 3.03, 110, 135)],
	# phosphodiester-like (negative oxygens) [2 O-]
	[[['Pac', ['O3-', 'O3-', NonO3minusSB, NonO3minusSB]], [1,1,1,0,0]],
		(1, 2), accSynAnti, ((-1, 0), 3.03, 110, 145, 3.03, 110, 135)],
	# carboxylate
	[[['Cac', ['O2-', 'O2-', SingleBond]], [1,1,1,0]], (1, 2), accSynAnti,
		((-1, 0), 3.17, 90, 145, 3.17, 110, 145)],
	["thiocarbonyl", (0,), accPhiPsi, ((1, None), 3.73, 90, 145)],
	# carboxylic acid
	[[[C, [['O2', []], ['O3', [H]], SingleBond]],[1,1,1,0,0]], (1,),
		accSynAnti, ((2, 0), 3.17, 110, 130, 3.17, 110, 135)],
	# amide
	[[['C2', ['O2', 'Npl',  SingleBond]], [1,1,1,0]], (1,), accSynAnti,
		((2, 0), 3.30, 110, 135, 3.30, 110, 130)],
	# ketone/aldehyde carbonyl
	[[['C2', ['O2', C, R]], [1,1,0,0]],
		(1,), accPhiPsi, ((0, None), 3.30, 110, 130)],
	# ester carbonyl
	[[['C2', ['O2', ['O3', [Tet]], C]], [1,1,0,0,0]],
		(1,), accPhiPsi, ((0, None), 3.17, 110, 135)],
	# nitro group
	[[['Ntr', ['O2-', 'O2-', SingleBond]], [1,1,1,0]], (1, 2), accSynAnti,
		((-1, 0), 3.42, 90, 145, 3.53, 110, 130)],
	# sulfone
	[[['Son', ['O2', 'O2', SingleBond, SingleBond]], [1,1,1,0,0]], (1, 2), accSynAnti,
		((-1, 0), 3.30, 110, 130, 3.30, 120, 135)],
	# phosphones
	[[['Pac', ['O3', 'O3-', 'O3-', SingleBond]], [1,1,0,0,0]],
		(1,), accThetaTau, ((0,), 3.03, 103, -146, 145)],
	[[['O2', ['Pox']], [1,1]],
		(0,), accThetaTau, ((1,), 3.03, 109, -180, 145)],
	# sulfoxide
	[[['O2', ['Sxd']], [1,1]],
		(0,), accThetaTau, ((1,), 3.03, 100, -180, 145)],
	# non-protonated aliphatic primary amine
	[[['N3', [Tet, H, H]], [1,1,0,0]],
		(0,), accThetaTau, ((1,), 3.03, 103, -180, 155)],
	# non-phenol hydroxyl
	[[['O3', [NonSacPacHSB, H]], [1,1,1]],
		(0,), accThetaTau, ((1,), 3.03, 100, -161, 145)],
	[[['Sac', ['O3-', 'O3-', ['O3', [{'default': True, 'notType': ['Pac']}]], SingleBond]], [1,1,1,1,0,0]],
		(3,), accThetaTau, ((0,), 3.17, 103, -180, 150)],
	# non-protonated aliphatic tertiary amine
	[[['N3', [Tet, Tet, Tet]], [1,1,1,1]],
		(0,), accThetaTau, (None, 3.17, 153, -180, 145)],
	# nitrile
	[[['N1', ['C1']], [1,1]],
		(0,), accThetaTau, ((1,), 3.30, 153, -180, 150)],
	# non-protonated aliphatic secondary amine
	[[['N3', [Tet, Tet, H]], [1,1,1,0]],
		(0,), accThetaTau, (None, 3.30, 153, -180, 150)],
	# phenol
	[[['O3', ['Car', H]], [1,1,0]],
		(0,), accThetaTau, ((1,), 3.17, 100, -153, 150)],
	# anilene
	[[[('Npl', 'N3'), ['Car', H, H]], [1,1,1,1]],
		(0,), accThetaTau, ((1,), 3.42, 90, -137, 140)],
	# waddah
	[[[O, [H, H]], [1,0,0]], (0,), accPhiPsi,
				((None, None), 3.03, 120, 145)],
	# non-ring ether
	[[acycEther, None], (0,), accPhiPsi, ((1, 2), 3.42, 140, 140)],
	# secondary amine not in a ring system
	[[nonringN2, None], (0,), accPhiPsi, ((1, 2), 3.42, 140, 140)],

	# check ring systems last, since conflicts of ring systems with
	# non-ring systems are not considered to be a problem (non-ring
	# "wins") and the code that checks the conflict assumes this order

	# nitrogen in symmetric 6-member ring
	[[symHet6N, None], (0,), accPhiPsi, ((1, 2), 3.17, 150, 145)],
	# nitrogen in symmetric 5-member ring
	[[symHet5N, None], (0,), accPhiPsi, ((1, 2), 3.30, 140, 155)],
	# nitrogen in asymmetric 6-member ring
	[[asymHet6N, None], (0,), accPhiPsi, ((1, 2), 3.30, 140, 140)],
	# nitrogen in asymmetric 5-member ring
	[[asymHet5N, None], (0,), accPhiPsi, ((1, 2), 3.30, 150, 135)],
	# oxygen in 5-member ring
	[[het5O, None], (0,), accPhiPsi, ((1, 2), 3.42, 150, 135)]
]
processedAcceptorParams = {}

"""layout somewhat similar to acceptorParams:
	name or spec of donor group,
	index of donor in group,
	type of donor geometry
	degree of tau symmetry
	argument tuple used when geometry-check function is called

	in argument tuple, conversions will occur before function gets called.
	namely:
		positive floats are assumed to be distances, and will be squared
		integers are assumed to be angles in degrees, and will be
			converted to radians
"""
_het5NH = lambda mols: hetNH(mols, 5)
_hetAro6NH = lambda mols: hetNH(mols, 6, aromaticOnly=1)
water = intern("water")
thetaTau = intern('thetaTau')
upsilonTau = intern('upsilonTau')
OHbondDist = Element.bondLength(Element(Element.O), Element(1))
donorParams = [
	# neutral carboxylic acid
	[[['O3', ['Cac', H]], [1,1,0]],
		0, upsilonTau, 2,
		(2.87, 103, -128, 140, -30,
		 2.87, 103, -128, 155, -30, 150,
		 2.87, 103, -128, 140, -30, 150)],
	# protonated nitrogen double-bonded to carbon
	[[['Npl', [['C2', [SingleBond, SingleBond]], H, H]], [1,1,0,0,0,0]],
		0, upsilonTau, 4,
		(3.17,  90, -146, 140, -30,
		 3.17,  90, -146, 140, -22.5, 150,
		 # next line extrapolated
		 3.17, 113, -161, 125, None, 140)],
	[[['Ng+', ['C2', H, H]], [1,1,0,0]],
		0, upsilonTau, 4,
		(3.17,  90, -146, 140, -30,
		 3.17,  90, -146, 140, -22.5, 150,
		 # next line extrapolated
		 3.17, 113, -161, 125, None, 140)],
	# protonated primary amine
	[[['N3+', [Tet, H, H, H]], [1,1,0,0,0]],
		0, upsilonTau, 6,
		(3.17,  90, -136, 140, 20,
		 3.17,  90, -132, 150, 25, 130,
		 3.17,  90, -124, 155, 15, 150)],
	# hydroxyl
	[[['O3', [Tet, H]], [1,1,0]],
		0, upsilonTau, 6,
		(3.17,  90, -141, 130, None,
		 3.03,  90, -141, 135, None, 140,
		 3.03, 100, -132, 145, None, 150)],
	# amide (two hydrogens)
	#   though the paper gives the tau symmetry as '2', we use '4' since
	#   we aren't distinguishing between the carbonyl oxygen and the
	#   other bonded substituent
	[[['C2', ['O2', [N, [H, H]], SingleBond]], [1,1,1,0,0,0]],
		2, upsilonTau, 4,
		(3.30, 103, -153, 135, -45,
		 3.30, 109, -141, 140, -30, 140,
		 3.30, 113, -161, 125, -30, 145)],
	# aniline-like
	["aromatic primary amine",
		0, upsilonTau, 4,
		(3.30, 100, -146, 145, -37.5,
		 3.30, 103, -146, 140, -37.5, 130,
		 # estimated
		 3.42,  90,  161, 125, None, 140)],
	# phenol-like
	[[['O3', ['Car', H]], [1,0,0]],
		0, upsilonTau, 4,
		(3.03, 103, -136, 145, -37.5,
		 3.03, 103, -136, 150, -45.0, 140,
		 2.87, 109, -128, 145, -52.5, 150)],
	# neutral primary aliphatic amine
	[[['N3', [Tet, H, H]], [1,0,1,1]],
		0, upsilonTau, 6,
		(3.30, 90, -128, 150, 30,
		 3.42, 90, -124, 155, 25, 130,
		 3.42, 90, -132, 155, 20, 140)],
	# planar charged nitrogen with one hydrogen
	[[['Npl', [Tet, [{'geometry':planar}, [(Tet,H), (Tet,H)]], H]], [1,0,0,0,0,0]],
		0, thetaTau, 4,
		(1.92, 146, 1.92, 153, 150, 2.48, 141, 145)],
	# sp3 charged nitrogen with 2 hydrogens
	[[['N3+', [Tet, Tet, H, H]], [1,0,0,1,1]],
		0, thetaTau, 2,
		(2.09, 141, 2.09, 141, 155, 2.48, 141, 145)],
	# waddah
	[[[O, [H, H]], [1,0,0]],
		0, water, 2,
		(2.36, 2.36 + OHbondDist, 146,
		2.23, 2.23 + OHbondDist, 146, 140,
		2.23, 2.23 + OHbondDist, 146, 150)],
	# amide (one hydrogen)
	[[['C2', ['O2', [N, [Tet, H]], SingleBond]], [1,1,1,0,0,0]],
		2, thetaTau, 2,
		(2.23, 146, 2.23, 146, 140, 2.36, 141, 145)],
	# aliphatic tertiary amine
	[[['N3+', [Tet, Tet, Tet, H]], [1,0,0,0,1]],
		0, thetaTau, 6,
		(1.92, 146, 2.09, 146, 140, 2.48, 141, 145)],
	# double-bonded nitrogen
	[[['N2', [{'geometry':planar}, H]], [1,1,0]],
		0, thetaTau, 2,
		(2.23, 132, 2.36, 146, 140, 2.48, 141, 145)],
	# secondary amine
	[[['N3', [Tet, Tet, H]], [1,0,0,1]],
		0, thetaTau, 2,
		(2.36, 141, 2.48, 146, 150, 2.48, 153, 155)],

	# check ring systems last, since conflicts of ring systems with
	# non-ring systems are not considered to be a problem (non-ring
	# "wins") and the code that checks the conflict assumes this order

	# nitrogen in 5-member ring
	[[_het5NH, None],
		0, thetaTau, 4,
		(2.09, 146, 2.09, 141, 140, 2.48, 141, 145)],
	# nitrogen in aromatic 6-member ring
	[[_hetAro6NH, None],
		0, thetaTau, 2,
		(2.23, 136, 2.23, 141, 150, 2.48, 141, 145)],
	# need below to cause check for generic donors
	[None, 0, 'generic', 0, (3.73, 3.73, 3.73)]
]
processedDonorParams = {}
def flushCache():
	global _Dcache, _Acache, _prevLimited
	_prevLimited = _Dcache = _Acache = None
flushCache()
	
_problem = None
_ringFuncs = [asymHet5N, asymHet6N, het5O, hetNH,
				symHet5N, symHet6N, _het5NH, _hetAro6NH]

def findHBonds(models, intermodel=True, intramodel=True, donors=None,
				acceptors=None, distSlop=0.0, angleSlop=0.0,
				interSubmodel=False, cacheDA=False):
	# to restrict to specific donor/acceptor atoms, 'donors' and/or
	# acceptors should be atom lists (or dictionaries with atom keys)
	# 
	# 'cacheDA' allows donors/acceptors in molecules to be cached if
	# it is anticipated that the same structures will be examined for
	# H-bonds repeatedly (e.g. a dynamics trajectory).

	if donors and not isinstance(donors, (dict, set)):
		limitedDonors = set(donors)
	else:
		limitedDonors = donors
	if acceptors and not isinstance(acceptors, (dict, set)):
		limitedAcceptors = set(acceptors)
	else:
		limitedAcceptors = acceptors
	global _Dcache, _Acache, _prevLimited
	if cacheDA:
		if limitedDonors:
			dIDs = [id(d) for d in limitedDonors]
			dIDs.sort()
		else:
			dIDs = None
		if limitedAcceptors:
			aIDs = [id(a) for a in limitedAcceptors]
			aIDs.sort()
		else:
			aIDs = None
		key = (dIDs, aIDs)
		if _prevLimited and _prevLimited != key:
			flushCache()
		_prevLimited = key
		from weakref import WeakKeyDictionary
		if _Dcache is None:
			_Dcache = WeakKeyDictionary()
			_Acache = WeakKeyDictionary()
	else:
		flushCache()
	global donorParams, acceptorParams
	global processedDonorParams, processedAcceptorParams
	global _computeCache
	global verbose
	global _problem
	_problem = None

	badConnectivities = 0

	# Used as necessary to cache expensive calculations (by other
	# functions also)
	_computeCache = {}

	processKey = (distSlop, angleSlop)
	if processKey not in processedAcceptorParams:
		# copy.deepcopy() refuses to copy functions (even as
		# references), so do this instead...
		aParams = []
		for p in acceptorParams:
			aParams.append(copy.copy(p))

		for i in range(len(aParams)):
			aParams[i][3] = _processArgTuple(aParams[i][3],
							distSlop, angleSlop)
		processedAcceptorParams[processKey] = aParams
	else:
		aParams = processedAcceptorParams[processKey]

	# compute some info for generic acceptors/donors
	genericAccInfo = {}
	# oxygens...
	genericOAccArgs = _processArgTuple([3.53, 90], distSlop,
							angleSlop)
	genericAccInfo['miscO'] = (accGeneric, genericOAccArgs)
	# dictionary based on bonded atom's geometry...
	genericAccInfo['O2-'] = {
		single: (accGeneric, genericOAccArgs),
		linear: (accGeneric, genericOAccArgs),
		planar: (accPhiPsi, _processArgTuple([3.53, 90, 130],
						distSlop, angleSlop)),
		tetrahedral: (accGeneric, genericOAccArgs)
	}
	genericAccInfo['O3-'] = genericAccInfo['O2-']
	genericAccInfo['O2'] = {
		single: (accGeneric, genericOAccArgs),
		linear: (accGeneric, genericOAccArgs),
		planar: (accPhiPsi, _processArgTuple([3.30, 110, 130],
						distSlop, angleSlop)),
		tetrahedral: (accThetaTau, _processArgTuple(
			[3.03, 100, -180, 145], distSlop, angleSlop))
	}
	# list based on number of known bonded atoms...
	genericAccInfo['O3'] = [
		(accGeneric, genericOAccArgs),
		(accThetaTau, _processArgTuple([3.17, 100, -161, 145],
						distSlop, angleSlop)),
		(accPhiPsi, _processArgTuple([3.42, 120, 135],
						distSlop, angleSlop))
	]
	# nitrogens...
	genericNAccArgs = _processArgTuple([3.42, 90], distSlop,
							angleSlop)
	genericAccInfo['miscN'] = (accGeneric, genericNAccArgs)
	genericAccInfo['N2'] = (accPhiPsi, _processArgTuple([3.42, 140, 135],
						distSlop, angleSlop))
	# tuple based on number of bonded heavy atoms...
	genericN3MultHeavyAccArgs = _processArgTuple([3.30, 153, -180, 145],
						distSlop, angleSlop)
	genericAccInfo['N3'] = (
		(accGeneric, genericNAccArgs),
		# only one example to draw from; weaken by .1A, 5 degrees
		(accThetaTau, _processArgTuple([3.13, 98, -180, 150],
						distSlop, angleSlop)),
		(accThetaTau, genericN3MultHeavyAccArgs),
		(accThetaTau, genericN3MultHeavyAccArgs)
	)
	# one example only; weaken by .1A, 5 degrees
	genericAccInfo['N1'] = (accThetaTau, _processArgTuple(
				[3.40, 136, -180, 145], distSlop, angleSlop))
	# sulfurs...
	# one example only; weaken by .1A, 5 degrees
	genericAccInfo['S2'] = (accPhiPsi, _processArgTuple([3.83, 85, 140],
						distSlop, angleSlop))
	genericAccInfo['Sar'] = genericAccInfo['S3-'] = (accGeneric,
			_processArgTuple([3.83, 85], distSlop, angleSlop))
	# now the donors...
	
	# planar nitrogens
	genDonNpl1HParams = (donThetaTau, _processArgTuple([2.23, 136,
		2.23, 141, 140, 2.46, 136, 140], distSlop, angleSlop))
	genDonNpl2HParams = (donUpsilonTau, _processArgTuple([3.30, 90, -153,
		135, -45, 3.30, 90, -146, 140, -37.5, 130, 3.40, 108, -166, 125,
		-35, 140], distSlop, angleSlop))
	genDonODists = [2.41, 2.28, 2.28, 3.27, 3.14, 3.14]
	genDonOParams = (donGeneric, _processArgTuple(
					genDonODists, distSlop, angleSlop))
	genDonNDists = [2.36, 2.48, 2.48, 3.30, 3.42, 3.42]
	genDonNParams = (donGeneric, _processArgTuple(
					genDonNDists, distSlop, angleSlop))
	genDonSDists = [2.42, 2.42, 2.42, 3.65, 3.65, 3.65]
	genDonSParams = (donGeneric, _processArgTuple(
					genDonSDists, distSlop, angleSlop))
	genericDonInfo = {
		'O': genDonOParams,
		'N': genDonNParams,
		'S': genDonSParams
	}

	accTrees = {}
	hbonds = []
	hasSulfur = {}
	for model in models:
		replyobj.status("Finding acceptors in model '%s'\n"
						% model.name, blankAfter=0)
		if cacheDA \
		and _Acache.has_key(model) \
		and _Acache[model].has_key((distSlop, angleSlop)):
			accAtoms = []
			accData = []
			for accAtom, data in _Acache[model][(distSlop,
							angleSlop)].items():
				if not accAtom.__destroyed__:
					accAtoms.append(accAtom)
					accData.append(data)
		else:
			accAtoms, accData = _findAcceptors(model, aParams,
					limitedAcceptors, genericAccInfo)
			if cacheDA:
				cache = WeakKeyDictionary()
				for i in range(len(accAtoms)):
					cache[accAtoms[i]] = accData[i]
				if not _Acache.has_key(model):
					_Acache[model] = {}
				_Acache[model][(distSlop, angleSlop)] = cache
		xyz = []
		hasSulfur[model] = False
		for accAtom in accAtoms:
			c = accAtom.xformCoord()
			xyz.append([c.x, c.y, c.z])
			if accAtom.element.number == Element.S:
				hasSulfur[model] = True
		replyobj.status("Building search tree of acceptor atoms\n",
								blankAfter=0)
		accTrees[model] = AdaptiveTree(xyz, accData, 3.0)
	
	if processKey not in processedDonorParams:
		# find max donor distances before they get squared..

		# copy.deepcopy() refuses to copy functions (even as
		# references), so do this instead...
		dParams = []
		for p in donorParams:
			dParams.append(copy.copy(p))

		for di in range(len(dParams)):
			geomType = dParams[di][2]
			argList = dParams[di][4]
			donRad = Element.bondRadius(Element(Element.N))
			if geomType == thetaTau:
				maxDist = max((argList[0], argList[2],
								argList[5]))
			elif geomType == upsilonTau:
				maxDist = max((argList[0], argList[5],
								argList[11]))
			elif geomType == water:
				maxDist = max((argList[1], argList[4],
								argList[8]))
			else:
				maxDist = max(genDonODists
						+ genDonNDists + genDonSDists)
				donRad = Element.bondRadius(Element(Element.S))
			dParams[di].append(maxDist + distSlop + donRad
				+ Element.bondRadius(Element(Element.H)))

		for i in range(len(dParams)):
			dParams[i][4] = _processArgTuple(dParams[i][4],
							distSlop, angleSlop)
		processedDonorParams[processKey] = dParams
	else:
		dParams = processedDonorParams[processKey]
		
	genericWaterParams = _processArgTuple([2.36, 2.36 + OHbondDist, 146],
							distSlop, angleSlop)
	genericThetaTauParams = _processArgTuple([2.48, 132],
							distSlop, angleSlop)
	genericUpsilonTauParams = _processArgTuple([3.42, 90, -161, 125],
							distSlop, angleSlop)
	genericGenericParams = _processArgTuple([2.48, 3.42, 130, 90],
							distSlop, angleSlop)
	for dmi in range(len(models)):
		model = models[dmi]
		replyobj.status("Finding donors in model '%s'\n" % model.name,
								blankAfter=0)
		if cacheDA \
		and _Dcache.has_key(model) \
		and _Dcache[model].has_key((distSlop, angleSlop)):
			donAtoms = []
			donData = []
			for donAtom, data in _Dcache[model][(distSlop,
							angleSlop)].items():
				if not donAtom.__destroyed__:
					donAtoms.append(donAtom)
					donData.append(data)
		else:
			donAtoms, donData = _findDonors(model, dParams,
					limitedDonors, genericDonInfo)
			if cacheDA:
				cache = WeakKeyDictionary()
				for i in range(len(donAtoms)):
					cache[donAtoms[i]] = donData[i]
				if not _Dcache.has_key(model):
					_Dcache[model] = {}
				_Dcache[model][(distSlop, angleSlop)] = cache

		replyobj.status("Matching donors in model '%s' to acceptors\n"
						% model.name, blankAfter=0)
		for i in range(len(donAtoms)):
			donorAtom = donAtoms[i]
			geomType, tauSym, argList, testDist = donData[i]
			donorHyds = hydPositions(donorAtom)
			coord = donorAtom.xformCoord()
			for accModel in models:
				if accModel == model and not intramodel\
				or accModel != model and not intermodel:
					continue
				if accModel.id == model.id \
				   and not interSubmodel \
				   and accModel.subid != model.subid:
					continue
				if hasSulfur[accModel]:
					from commonGeom import SULFUR_COMP
					td = testDist + SULFUR_COMP
				else:
					td = testDist
				accs = accTrees[accModel].searchTree(
					[coord.x, coord.y, coord.z], td)
				if verbose:
					replyobj.message("Found %d possible acceptors for donor %s:\n" % (len(accs), donorAtom.oslIdent()))
					for accData in accs:
						replyobj.message("\t%s\n" % accData[0].oslIdent())
				for accAtom, geomFunc, args in accs:
					if accAtom == donorAtom:
						# e.g. hydroxyl
						if verbose:
							print "skipping: donor == acceptor"
						continue
					# exclude hbonding between
					# differing alt locations of
					# same residue
					if accAtom.altLoc.isalnum() and donorAtom.altLoc.isalnum() and accAtom.residue == donorAtom.residue and accAtom.altLoc != donorAtom.altLoc:
						continue
					try:
						if not apply(geomFunc,
						(donorAtom, donorHyds) + args):
							continue
					except ConnectivityError, v:
						replyobj.message("Skipping possible acceptor with bad geometry: %s\n%s\n\n" % (accAtom.oslIdent(), v))
						badConnectivities += 1
						continue
					if verbose:
						replyobj.message("\t%s satisfies acceptor criteria\n" % accAtom.oslIdent())
					if geomType == upsilonTau:
						donorFunc = donUpsilonTau
						addArgs = genericUpsilonTauParams + [tauSym]
					elif geomType == thetaTau:
						donorFunc = donThetaTau
						addArgs = genericThetaTauParams
					elif geomType == water:
						donorFunc = donWater
						addArgs = genericWaterParams
					else:
						if donorAtom.idatmType in ["Npl", "N2+"]:
							heavys = 0
							for bonded in donorAtom.primaryNeighbors():
								if bonded.element.number > 1:
									heavys += 1
							if heavys > 1:
								info = genDonNpl1HParams
							else:
								info = genDonNpl2HParams
						else:
							info = genericDonInfo[donorAtom.element.name]
						donorFunc, argList = info
						addArgs = genericGenericParams
						if donorFunc == donUpsilonTau:
							# tack on generic
							# tau symmetry
							addArgs = genericUpsilonTauParams + [4]
						elif donorFunc == donThetaTau:
							addArgs = genericThetaTauParams
					try:
						if not apply(donorFunc,
						(donorAtom, donorHyds, accAtom)
						+ tuple(argList + addArgs)):
							continue
					except ConnectivityError, v:
						replyobj.message("Skipping possible donor with bad geometry: %s\n%s\n\n" % (donorAtom.oslIdent(), v))
						badConnectivities += 1
						continue
					except AtomTypeError, v:
						_problem = ("atom type",
							donorAtom, v, None)
						continue
					if verbose:
						replyobj.message("\t%s satisfies donor criteria\n" % donorAtom.oslIdent())
					hbonds.append((donorAtom, accAtom))
	if badConnectivities:
		replyobj.warning("Skipped %d atom(s) with bad connectivities; see reply log for details\n" % badConnectivities);
	if _problem:
		if not chimera.nogui:
			da, atom, grp1, grp2 = _problem
			from BugReport import bugNotify
			resAtoms = atom.residue.oslChildren()
			def resAtomRep(a):
				try:
					i = resAtoms.index(a)
				except ValueError:
					return "other %s" % a.element.name
				return "%2d" % (i+1)
			if da in ["donor", "acceptor"]:
				descript = "geometry class 1: %s\n\n" \
						"geometry class 2: %s" % (
						repr(grp1), repr(grp2))
			else:
				descript = "problem: %s" % grp1
			bugNotify(
"""At least one atom was classified into more than one acceptor or donor
geometry class or had a bad atom type.  This indicates a problem in the
classification/atom-typing mechanism and we would appreciate it if you
would use the bug-report button below to send us the information that
will allow us to improve the classification/atom-typing code.
""",
"""residue name: %s

problem %s atom: %d

residue atoms:
	%s

residue bonds:
	%s

%s
""" % (atom.residue.type, da, resAtoms.index(atom)+1,
"\n\t".join(["%2d %-4s %-s (%s)" % (en[0]+1, en[1].name, en[1].idatmType, str(en[1].coord())) for en in enumerate(resAtoms)]),
"\n\t".join(["%s <-> %-s" % (resAtomRep(b.atoms[0]), resAtomRep(b.atoms[1])) for b in chimera.misc.bonds(resAtoms, internal=False)]),
descript)
)
		_problem = None
	return hbonds

def _processArgTuple(argTuple, distSlop, angleSlop):
	newArgs = []
	for arg in argTuple:
		if isinstance(arg, (int, float)):
			if arg > 0.0 and arg < 7.5:
				# square distances
				arg = arg + distSlop
				newArgs.append(arg * arg)
			else:
				if arg < 0.0:
					arg = arg - angleSlop
					if arg < -180.0:
						arg = -180.0
					# can't convert to positive value
					# here because some constraints vary
					# between "greater than" and "less than"
				else:
					arg = arg - angleSlop
					if arg < 0.0:
						arg = 0.0
				newArgs.append(arg)
		else:
			newArgs.append(arg)
	return newArgs  # returns list

def _findAcceptors(model, aParams, limitedAcceptors, genericAccInfo):
	global _problem
	accAtoms = []
	accData = []
	stdAcceptors = {}
	for ap in aParams:
		groupKey, accIndices, geomFunc, argList = ap
		groups = findGroup(groupKey, [model])
		for group in groups:
			for i in range(len(accIndices)):
				accAtom = group[accIndices[i]]
				if limitedAcceptors \
				and accAtom not in limitedAcceptors:
					continue
				if accAtom in stdAcceptors:
					if groupKey != stdAcceptors[accAtom] \
					and not (
					# conflicts of non-ring groups with
					# ring groups not considered a problem
					# (non-ring groups "win")
					groupKey[0] in _ringFuncs
					and stdAcceptors[accAtom][0]
					not in _ringFuncs):
						_problem = ("acceptor", accAtom,
							stdAcceptors[accAtom],
							groupKey)
					continue
				stdAcceptors[accAtom] = groupKey

				args = [accAtom]
				if isinstance(argList[0], tuple):
					for index in argList[0]:
						if index is None:
							args.append(None)
						elif index < 0:
							args.append(group[
							   accIndices[1-i]])
						else:
							args.append(
								group[index])
					args = args + argList[1:]
				else:
					args = args + argList
				
				accAtoms.append(accAtom)
				accData.append([accAtom, geomFunc, tuple(args)])
	# find acceptors not covered by above
	for atom in model.atoms:
		if atom in stdAcceptors:
			continue
		if limitedAcceptors and atom not in limitedAcceptors:
			continue
		if atom.idatmType in genericAccInfo:
			accInfo = genericAccInfo[atom.idatmType]
			if isinstance(accInfo, dict):
				try:
					bondedGeom = typeInfo[atom
						.primaryNeighbors()[0]
						.idatmType].geometry
				except KeyError:
					bondedGeom = single
				accFunc, args = accInfo[bondedGeom]
			elif isinstance(accInfo, list):
				try:
					accFunc, args = accInfo[
						len(atom.primaryBonds())]
				except IndexError:
					_problem = ("connectivity", atom,
						"bad number of bonds (%d)" %
						len(atom.primaryBonds()), None)
					continue
			elif isinstance(accInfo, tuple) \
			and isinstance(accInfo[0], tuple):
				accFunc, args = accInfo[len(filter(lambda a:
						a.element.number > 1,
						atom.primaryNeighbors()))]
			else:
				accFunc, args = accInfo
			if accFunc == accPhiPsi:
				bonded = atom.primaryNeighbors()
				args = bonded + [None] * (2-len(bonded)) + args
			elif accFunc == accThetaTau:
				bonded = atom.primaryNeighbors()
				if len(bonded) > 1:
					args = [None] + args
				else:
					args = bonded + args
		else:
			atomicNumber = atom.element.number
			if atomicNumber == 8:
				# oxygen
				accFunc, args = genericAccInfo['miscO']
			elif atomicNumber == 7:
				# nitrogen
				if atom.idatmType not in ['N2', 'N3']:
					continue
				accFunc, args = genericAccInfo['miscN']
			else:
				continue
			if verbose:
				print "miscellaneous generic acceptor:", \
								atom.oslIdent()
		accAtoms.append(atom)
		accData.append([atom, accFunc, tuple([atom] + args)])
	return accAtoms, accData

def _findDonors(model, dParams, limitedDonors, genericDonInfo):
	donAtoms = []
	donData = []
	stdDonors = {}
	for dp in dParams:
		groupKey, donorIndex, geomType, tauSym, argList, testDist = dp

		if groupKey:
			groups = findGroup(groupKey, [model])
		else:
			# generic donors
			groups = []
			for atom in model.atoms:
				if atom in stdDonors:
					continue
				if atom.element.number not in [7,8,16]:
					continue
				if limitedDonors \
				and atom not in limitedDonors:
					continue
				# oxygen, nitrogen, or sulfur
				try:
					expectBonds = typeInfo[
					  atom.idatmType].substituents
				except KeyError:
					expectBonds = 0
				numBonds = len(atom.primaryBonds())
				# screen out the partial terminal N that
				# AddH can leave, since the geometry is
				# problematic and the H direction isn't
				# really determined
				if atom.idatmType == "Npl" \
				and numBonds == 2 and 1 in [n.element.number
				for n in atom.primaryNeighbors()]:
					continue
				if numBonds < expectBonds:
					groups.append([atom])
					continue
				for bonded in atom.primaryNeighbors():
					if bonded.element.number == 1:
						groups.append([atom])
						break
			if verbose:
				for g in groups:
					print "generic donor:", g[0].oslIdent()
				
		if groups and geomType == thetaTau:
			# extend probe distance by H-bond length
			# so that all relevant acceptors will be found
			testDist = testDist + Element.bondLength(
					groups[0][donorIndex].element,
					Element(1))
		for group in groups:
			donorAtom = group[donorIndex]
			if limitedDonors \
			and donorAtom not in limitedDonors:
				continue
			if donorAtom in stdDonors:
				if groupKey != stdDonors[donorAtom] and not (
				# conflicts of non-ring groups with ring
				# groups not considered a problem (non-ring
				# groups "win")
				groupKey[0] in _ringFuncs and
				stdDonors[donorAtom][0] not in _ringFuncs):
					global _problem
					_problem = ("donor", donorAtom,
						stdDonors[donorAtom], groupKey)
				continue
			stdDonors[donorAtom] = groupKey
			donAtoms.append(donorAtom)
			donData.append((geomType, tauSym, argList, testDist))
	return donAtoms, donData

from chimera.selection import currentAtoms, currentMolecules

def createHBonds(models=None, intramodel=True, intermodel=True, relax=True,
	distSlop=recDistSlop, angleSlop=recAngleSlop, twoColors=False,
	selRestrict=None, lineWidth=1.0, saveFile=None, batch=False,
	interSubmodel=False, makePseudobonds=True, retainCurrent=False,
	reveal=False, namingStyle=None, log=False, cacheDA=None,
	color=(0.0, 0.8, 0.9, 1.0), slopColor=(0.95, 0.5, 0.0, 1.0)):

	"""Wrapper to be called by gui and command line.

	   Use findHBonds for other programming applications.
	"""

	inColors = (color, slopColor)
	outColors = []
	for c in inColors:
		if isinstance(c, basestring):
			from chimera.colorTable import getColorByName
			try:
				outColors.append(getColorByName(c))
			except KeyError:
				raise "No known color named '%s'" % c
		elif isinstance(c, tuple):
			oc = chimera.MaterialColor()
			oc.ambientDiffuse = c[:3]
			if len(c) > 3:
				oc.opacity = c[-1]
			outColors.append(oc)
		else:
			outColors.append(c)
	bondColor, slopColor = outColors

	donors = acceptors = None
	if selRestrict is not None:
		selAtoms = currentAtoms(asDict=True)
		if not selAtoms:
			if batch:
				return
			raise UserError("No atoms in selection.")
		if (not intermodel or selRestrict == "both") and models is None:
			# intramodel only or both ends in selection
			models = currentMolecules()
		if selRestrict == "both":
			# both ends in selection
			donors = acceptors = selAtoms

	if models is None:
		models = chimera.openModels.list(modelTypes=[chimera.Molecule])

	if not relax:
		distSlop = angleSlop = 0.0

	if cacheDA == None:
		# cache trajectories by default
		cacheDA = len(models) == 1 and len(models[0].coordSets) > 1

	hbonds = findHBonds(models, intermodel=intermodel,
		intramodel=intramodel, distSlop=distSlop,
		angleSlop=angleSlop, donors=donors, acceptors=acceptors,
		interSubmodel=interSubmodel, cacheDA=cacheDA)
	if selRestrict and donors == None:
		hbonds = _filterBySel(hbonds, selAtoms, selRestrict)
	
	outputInfo = (intermodel, intramodel, relax, distSlop, angleSlop,
							models, hbonds)
	if log:
		import sys
		# provide a separator from other output
		print>>sys.stdout, ""
		_fileOutput(sys.stdout, outputInfo, namingStyle)
	if saveFile == '-':
		from MolInfoDialog import SaveMolInfoDialog
		SaveMolInfoDialog(outputInfo, _fileOutput,
					initialfile="hbond.info",
					title="Choose H-Bond Save File",
					historyID="H-bond info")
	elif saveFile is not None:
		_fileOutput(saveFile, outputInfo, namingStyle)

	replyobj.status("%d hydrogen bonds found\n"
				% len(hbonds), log=1, blankAfter=120)
	if not makePseudobonds:
		return

	if twoColors:
		# color relaxed constraints differently
		precise = findHBonds(models,
			intermodel=intermodel, intramodel=intramodel,
			donors=donors, acceptors=acceptors,
			interSubmodel=interSubmodel, cacheDA=cacheDA)
		if selRestrict and donors == None:
			precise = _filterBySel(precise, selAtoms, selRestrict)
		# give another opportunity to read the result...
		replyobj.status("%d hydrogen bonds found\n" % len(hbonds),
								blankAfter=120)

	from chimera.misc import getPseudoBondGroup
	pbg = getPseudoBondGroup("hydrogen bonds", issueHint=True)
	if not retainCurrent:
		pbg.deleteAll()
	pbg.lineWidth = lineWidth

	for don, acc in hbonds:
		if don.associated(acc, "hydrogen bonds"):
			continue
		pb = pbg.newPseudoBond(don, acc)
		if twoColors:
			if (don, acc) in precise:
				color = bondColor
			else:
				color = slopColor
		else:
			color = bondColor
		pb.color = color
		if reveal:
			for end in [don, acc]:
				if end.display:
					continue
				for ea in end.residue.oslChildren():
					ea.display = True

def _filterBySel(hbonds, selAtoms, selRestrict):
	filtered = []
	selBoth = selRestrict == "both"
	selCross = selRestrict == "cross"
	for d, a in hbonds:
		d_in =  d in selAtoms
		a_in =  a in selAtoms
		num = a_in + d_in
		if num == 0:
			continue
		if num == 1:
			if selBoth:
				continue
		elif selCross:
			continue
		filtered.append((d, a))
	return filtered

def _fileOutput(fileName, outputInfo, namingStyle):
	intermodel, intramodel, relaxConstraints, \
			distSlop, angleSlop, modelList, hbonds = outputInfo
	from OpenSave import osOpen
	outFile = osOpen(fileName, 'w')
	if intermodel:
		outFile.write("Finding intermodel H-bonds\n")
	if intramodel:
		outFile.write("Finding intramodel H-bonds\n")
	if relaxConstraints:
		outFile.write("Constraints relaxed by %g angstroms"
			" and %d degrees\n" % (distSlop, angleSlop))
	else:
		outFile.write("Using precise constraint criteria\n")
	outFile.write("Models used:\n")
	for model in modelList:
		outFile.write("\t%s %s\n" % (model.oslIdent(), model.name))
	outFile.write("\nH-bonds (donor, acceptor, hydrogen, D..A dist, D-H..A dist):\n")
	# want the bonds listed in some kind of consistent
	# order...
	hbonds.sort(_oslSort)

	# figure out field widths to make things line up
	dwidth = awidth = hwidth = 0
	labels = {}
	from chimera.misc import chimeraLabel
	for don, acc in hbonds:
		labels[don] = chimeraLabel(don, style=namingStyle)
		labels[acc] = chimeraLabel(acc, style=namingStyle)
		dwidth = max(dwidth, len(labels[don]))
		awidth = max(awidth, len(labels[acc]))
		da = don.xformCoord().distance(acc.xformCoord())
		dha = None
		for h in don.primaryNeighbors():
			if h.element.number != 1:
				continue
			d = h.xformCoord().distance(acc.xformCoord())
			if dha is None or d < dha:
				dha = d
				hyd = h
		if dha is None:
			dhaOut = "N/A"
			hydOut = "no hydrogen"
		else:
			dhaOut = "%5.3f" % dha
			hydOut = chimeraLabel(hyd, style=namingStyle)
		hwidth = max(hwidth, len(hydOut))
		labels[(don, acc)] = (hydOut, da, dhaOut)
	for don, acc in hbonds:
		hydOut, da, dhaOut = labels[(don, acc)]
		outFile.write("%*s  %*s  %*s  %5.3f  %s\n" % (
			0-dwidth, labels[don], 0-awidth, labels[acc],
			0-hwidth, hydOut, da, dhaOut))
	if outFile != fileName:
		# we opened it, so close it...
		outFile.close()

def _oslSort(hb1, hb2):
	from chimera.misc import oslCmp
	don1, acc1 = hb1
	don2, acc2 = hb2

	sval = oslCmp(don1.oslIdent(), don2.oslIdent())
	if sval == 0:
		return oslCmp(acc1.oslIdent(), acc2.oslIdent())
	return sval
