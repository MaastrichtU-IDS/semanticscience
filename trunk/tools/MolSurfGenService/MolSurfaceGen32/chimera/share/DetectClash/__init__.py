# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29458 2009-11-26 01:01:32Z pett $

import chimera
attrName = "overlap"
groupName = "contacts"
from prefs import defaults, CLASH_THRESHOLD, HBOND_ALLOWANCE, BOND_SEPARATION
clashDef = defaults[CLASH_THRESHOLD]
hbondDef = defaults[HBOND_ALLOWANCE]
bondSepDef = defaults[BOND_SEPARATION]

def detectClash(testAtoms, test="others", clashThreshold=clashDef,
		hbondAllowance=hbondDef, assumedMaxVdw=2.1,
		bondSeparation=bondSepDef, intraRes=False, interSubmodel=False):
	"""Detect steric clashes

	   'testAtoms' should be a list of atoms.

	   If 'test' is 'others' then non-bonded clashes between atoms in
	   'testAtoms' and non-'testAtoms' atoms will be found.  If 'test'
	   is 'model' then the same clashes as 'others' will be found, but
	   inter-model clashes will be eliminated.  If 'test' is 'self'
	   then non-bonded clashes within 'testAtoms' atoms will be found.
	   Otherwise 'test' should be a list of atoms to test against.
	   The "clash value" is the sum of the VDW radii minus the distance,
	   keeping only the maximal clash (which must exceed 'clashThreshold').

	   'hbondAllowance' is how much the clash value is reduced if one
	   atom is a donor and the other an acceptor.

	   Atom pairs are eliminated from consideration if they are less than
	   or equal to 'bondSeparation' bonds apart.

	   Intra-residue clashes are ignored unless intraRes is True.
	   Inter-submodel clashes are ignored unless interSubmodel is True.

	   Returns a dictionary keyed on atoms, with values that are
	   dictionaries keyed on clashing atom with value being the clash value.
	"""

	# use the fast _closepoints module to cut down candidate atoms if we
	# can (since _closepoints doesn't know about "non-bonded" it isn't as
	# useful as it might otherwise be)
	if test in ("others", "model"):
		mList = chimera.openModels.list(modelTypes=[chimera.Molecule])
		testSet = set(testAtoms)
		from numpy import array
		testList = array(testAtoms)
		otherAtoms = [a for m in mList for a in m.atoms
							if a not in testSet]
		otherAtoms = array(otherAtoms)
		if len(otherAtoms) == 0:
			from chimera import UserError
			raise UserError("All atoms are in test set: no others"
				" available to test against")
		from _multiscale import get_atom_coordinates
		tPoints = get_atom_coordinates(testList, transformed = True)
		oPoints = get_atom_coordinates(otherAtoms, transformed = True)
		cutoff = 2.0 * assumedMaxVdw - clashThreshold
		from _closepoints import find_close_points, BOXES_METHOD
		tClose, oClose = find_close_points(BOXES_METHOD,
						tPoints, oPoints, cutoff)
		testAtoms = testList.take(tClose)
		searchAtoms = otherAtoms.take(oClose)
	elif not isinstance(test, basestring):
		searchAtoms = test
	else:
		searchAtoms = testAtoms

	from chimera.misc import atomSearchTree
	tree = atomSearchTree(list(searchAtoms))
	clashes = {}
	for a in testAtoms:
		cutoff = a.radius + assumedMaxVdw - clashThreshold
		nearby = tree.searchTree(a.xformCoord().data(), cutoff)
		if not nearby:
			continue
		needExpansion = a.allLocations()
		exclusions = set(needExpansion)
		for i in range(bondSeparation):
			nextNeed = []
			for expand in needExpansion:
				for n in expand.neighbors:
					if n in exclusions:
						continue
					exclusions.add(n)
					nextNeed.append(n)
			needExpansion = nextNeed
		for nb in nearby:
			if nb in exclusions:
				continue
			if not intraRes and a.residue == nb.residue:
				continue
			if a in clashes and nb in clashes[a]:
				continue
			if not interSubmodel \
			and a.molecule.id == nb.molecule.id \
			and a.molecule.subid != nb.molecule.subid:
				continue
			if test == "model" and a.molecule != nb.molecule:
				continue
			clash = a.radius + nb.radius - a.xformCoord().distance(
							nb.xformCoord())
			if hbondAllowance:
				if (_donor(a) and _acceptor(nb)) or (
				_donor(nb) and _acceptor(a)):
					clash -= hbondAllowance
			if clash < clashThreshold:
				continue
			clashes.setdefault(a, {})[nb] = clash
			clashes.setdefault(nb, {})[a] = clash
	return clashes

hyd = chimera.Element(1)
negative = set([chimera.Element(sym) for sym in ["N", "O", "S"]])
from chimera.idatm import typeInfo
def _donor(a):
	if a.element == hyd:
		if a.neighbors and a.neighbors[0].element in negative:
			return True
	elif a.element in negative:
		try:
			if len(a.bonds) < typeInfo[a.idatmType].substituents:
				# implicit hydrogen
				return True
		except KeyError:
			pass
		for nb in a.neighbors:
			if nb.element == hyd:
				return True
	return False

def _acceptor(a):
	try:
		info = typeInfo[a.idatmType]
	except KeyError:
		return False
	return info.substituents < info.geometry

from chimera.colorTable import getColorByName
from prefs import defaults, CLASH_THRESHOLD, HBOND_ALLOWANCE, BOND_SEPARATION, \
	IGNORE_INTRA_RES, ACTION_SELECT, ACTION_COLOR, CLASH_COLOR, \
	NONCLASH_COLOR, ACTION_PSEUDOBONDS, PB_COLOR, PB_WIDTH, ACTION_ATTR, \
	ACTION_REPLYLOG
defColors = {}
for color in [CLASH_COLOR, NONCLASH_COLOR, PB_COLOR]:
	val = defaults[color]
	if val is not None:
		val = getColorByName(val)
	defColors[color] = val
_continuousID = None
def cmdDetectClash(testAtoms, overlapCutoff=defaults[CLASH_THRESHOLD],
		hbondAllowance=defaults[HBOND_ALLOWANCE], test="others",
		setAttrs=defaults[ACTION_ATTR], selectClashes=
		defaults[ACTION_SELECT], colorClashes=defaults[ACTION_COLOR],
		clashColor=defColors[CLASH_COLOR], nonclashColor=
		defColors[NONCLASH_COLOR], makePseudobonds=
		defaults[ACTION_PSEUDOBONDS], pbColor=defColors[PB_COLOR],
		lineWidth=defaults[PB_WIDTH], bondSeparation=
		defaults[BOND_SEPARATION], saveFile=None, namingStyle=None,
		ignoreIntraRes=defaults[IGNORE_INTRA_RES], interSubmodel=False,
		log=defaults[ACTION_REPLYLOG], summary=True,
		continuous=False):
	global _continuousID
	from Midas import MidasError
	if continuous:
		if setAttrs or saveFile != None or log:
			raise MidasError("log/setAttrs/saveFile not allowed"
				" with continuous detection")
		if _continuousID == None:
			from inspect import getargvalues, currentframe
			argNames, fArgs, fKw, frameDict = getargvalues(
								currentframe())
			callData = [frameDict[an] for an in argNames]
			def preCB(trigName, myData, changes):
				if 'transformation change' in changes.reasons:
					return _motionCB(myData)
			_continuousID = chimera.triggers.addHandler(
						'OpenState', preCB, callData)
	elif _continuousID != None:
		chimera.triggers.deleteHandler('OpenState', _continuousID)
		_continuousID = None
	if isinstance(test, basestring):
		if test.startswith("other"):
			test = "others"
		elif test not in ('self', 'model'):
			# atom spec
			from chimera.specifier import evalSpec
			try:
				test = evalSpec(test).atoms()
			except:
				raise MidasError("Could not parse atom spec '%s'" % test)
	clashes = detectClash(testAtoms, test=test,
		hbondAllowance=hbondAllowance, clashThreshold=overlapCutoff,
		bondSeparation=bondSeparation, intraRes=not ignoreIntraRes,
		interSubmodel=interSubmodel)
	if selectClashes:
		chimera.selection.setCurrent(clashes.keys())
	if test == "self":
		outputGrouping = set()
	else:
		outputGrouping = testAtoms
	info = (overlapCutoff, hbondAllowance, bondSeparation, ignoreIntraRes,
							clashes, outputGrouping)
	if log:
		import sys
		# put a separator in the Reply Log
		print>>sys.stdout, ""
		_fileOutput(sys.stdout, info, namingStyle=namingStyle)
	if saveFile == '-':
		from FindHBond.MolInfoDialog import SaveMolInfoDialog
		SaveMolInfoDialog(info, _fileOutput, initialfile="overlaps",
				title="Choose Overlap Info Save File",
				historyID="Overlap info")
	elif saveFile is not None:
		_fileOutput(saveFile, info, namingStyle=namingStyle)
	if summary == True:
		def _summary(msg):
			from chimera import replyobj
			replyobj.status(msg + '\n')
			replyobj.info(msg + '\n')
		summary = _summary
	if summary:
		if clashes:
			total = 0
			for clashList in clashes.values():
				total += len(clashList)
			summary("%d contacts" % (total/2))
		else:
			summary("No contacts")
	if not (setAttrs or colorClashes or makePseudobonds):
		nukeGroup()
		return clashes
	if test in ("others", "model"):
		atoms = [a for m in chimera.openModels.list(
			modelTypes=[chimera.Molecule]) for a in m.atoms]
	else:
		atoms = testAtoms
	if setAttrs:
		# delete the attribute in _all_ atoms...
		for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
			for a in m.atoms:
				if hasattr(a, attrName):
					delattr(a, attrName)
		for a in atoms:
			if a in clashes:
				clashVals = clashes[a].values()
				clashVals.sort()
				setattr(a, attrName, clashVals[-1])
	if colorClashes:
		for a in atoms:
			a.surfaceColor = None
			if a in clashes:
				a.color = clashColor
			else:
				a.color = nonclashColor
	if makePseudobonds:
		from chimera.misc import getPseudoBondGroup
		pbg = getPseudoBondGroup(groupName)
		pbg.deleteAll()
		pbg.lineWidth = lineWidth
		pbg.color = pbColor
		seen = set()
		for a in atoms:
			if a not in clashes:
				continue
			seen.add(a)
			for clasher in clashes[a].keys():
				if clasher in seen:
					continue
				pbg.newPseudoBond(a, clasher)
	else:
		nukeGroup()
	return clashes

def nukeGroup():
	mgr = chimera.PseudoBondMgr.mgr()
	group = mgr.findPseudoBondGroup(groupName)
	if group:
		chimera.openModels.close([group])

def _fileOutput(fileName, info, namingStyle):
	overlapCutoff, hbondAllowance, bondSeparation, ignoreIntraRes, \
						clashes, outputGrouping = info
	from OpenSave import osOpen
	outFile = osOpen(fileName, 'w')
	print>>outFile, "Allowed overlap: %g" % overlapCutoff
	print>>outFile, "H-bond overlap reduction: %g" % hbondAllowance
	print>>outFile, "Ignore contacts between atoms separated by %d bonds" \
		" or less" % bondSeparation
	if ignoreIntraRes:
		print>>outFile, "Ignore intra-residue contacts"
	else:
		print>>outFile, "Detect intra-residue contacts also"
	seen = set()
	data = []
	from chimera.misc import chimeraLabel
	for a, aclashes in clashes.items():
		for c, val in aclashes.items():
			if (c, a) in seen:
				continue
			seen.add((a, c))
			if a in outputGrouping:
				out1, out2 = a, c
			else:
				out1, out2 = c, a
			l1, l2 = chimeraLabel(out1, style=namingStyle), \
					chimeraLabel(out2, style=namingStyle)
			data.append((val, l1, l2, out1.xformCoord().distance(
							out2.xformCoord())))
	data.sort()
	data.reverse()
	print>>outFile, "\n%d contacts" % len(data)
	print>>outFile, "atom1  atom2  overlap  distance"
	if data:
		fieldWidth1 = max([len(l1) for v, l1, l2, d in data])
		fieldWidth2 = max([len(l2) for v, l1, l2, d in data])
		for v, l1, l2, d in data:
			print>>outFile, "%*s  %*s  %5.3f  %5.3f" % (
				0-fieldWidth1, l1, 0-fieldWidth2, l2, v, d)
	if fileName != outFile:
		# only close file if we opened it...
		outFile.close()

def _motionCB(callData):
	# if all molecule activities are the same (i.e. no possible
	# relative motion), do nothing
	activity = None
	for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
		if activity is None:
			activity = m.openState.active
		elif activity != m.openState.active:
			callData[0] = [a for a in callData[0]
							if not a.__destroyed__]
			if not callData[0]:
				global _continuousID
				_continuousID = None
				from chimera.triggerSet import ONESHOT
				return ONESHOT
			cmdDetectClash(*tuple(callData))
			return
