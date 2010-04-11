# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: specifier.py 26655 2009-01-07 22:02:30Z gregc $

import re
import chimera
from chimera import selection, oslParser

SIMPLE = 'simple'
ZONE = 'zone'
UNION = 'union'
INTERSECT = 'intersect'
COMPLEMENT = 'complement'

RESIDUE = 'residue'
ATOM = 'atom'

zonePat = re.compile('(z[ar]?)\s*([<>])\s*([0-9.]+)', re.I)
pickSynonyms = ['current', 'picked', 'selected', 'selection', 'sel']

def evalSpec(s, models=None):
	"""models arg only actually restricts if spec is an OSL
	   or registered selector
	"""
	if models is None:
		return _evaluate(parse(s), chimera.openModels.list())
	else:
		return _evaluate(parse(s), models)

def parse(s):
	return _splitOnUnion(s.strip())

def _splitOnUnion(s):
	n = s.find('|')
	if n < 0:
		return _splitOnIntersect(s)
	else:
		return [UNION, _splitOnIntersect(s[:n].strip()),
				_splitOnUnion(s[n+1:].strip())]

def _splitOnIntersect(s):
	n = s.find('&')
	if n < 0:
		return _splitOnZones(s)
	else:
		return [INTERSECT, _splitOnZones(s[:n].strip()),
				_splitOnIntersect(s[n+1:].strip())]

def _splitOnZones(s):
	m = zonePat.search(s)
	if m is None:
		return _splitOnComplement(s)
	kind = RESIDUE
	floor = None
	ceiling = None
	if m.group(1) == 'za':
		kind = ATOM
	if m.group(2) == '<':
		ceiling = float(m.group(3))
	else:
		floor = float(m.group(3))
	start = m.start()
	stop = m.end()
	while 1:
		m = zonePat.search(s, m.end())
		if m is None:
			break
		if m.group(2) == '<':
			ceiling = float(m.group(3))
		else:
			floor = float(m.group(3))
		stop = m.end()
	spec = [ZONE, _splitOnComplement(s[:start].strip()),
							kind, floor, ceiling]
	remainder = s[stop:].strip()
	if remainder:
		spec = [UNION, spec, _splitOnZones(remainder)]
	return spec

def _splitOnComplement(s):
	if not s or s[0] != '~':
		retVal = [SIMPLE, s]
	else:
		s = s[1:].strip()
		retVal = [COMPLEMENT, [SIMPLE, s]]
	if knownSelection(s) is None:
		oslParser.Parser(s, None, None, None)
	return retVal

def _evaluate(f, models):
	if f[0] is SIMPLE:
		ks = knownSelection(f[1], models)
		if ks is not None:
			if ks == 1:
				sel = selection.copyCurrent()
			elif isinstance(ks, basestring):
				sel = selection.OSLSelection(ks, models)
			else:
				sel = ks
		else:
			sel = selection.OSLSelection(f[1], models)
	elif f[0] is ZONE:
		sel = zone(_evaluate(f[1], chimera.openModels.list()), f[2], f[3], f[4], models)
	elif f[0] is UNION:
		left = _evaluate(f[1], models)
		right = _evaluate(f[2], models)
		sel = selection.ItemizedSelection()
		sel.merge(selection.REPLACE, left)
		sel.merge(selection.EXTEND, right)
	elif f[0] is INTERSECT:
		left = _evaluate(f[1], models)
		right = _evaluate(f[2], left.graphs())
		sel = selection.ItemizedSelection()
		sel.merge(selection.REPLACE, left)
		sel.merge(selection.INTERSECT, right)
	elif f[0] is COMPLEMENT:
		sel = selection.ItemizedSelection()
		sel.add(models)
		operand =  _evaluate(f[1], models)
		sel.merge(selection.REMOVE, operand)
	else:
		raise ValueError, 'Unknown specifier function: %s' % str(f[0])
	return sel

def zone(sel, kind, floor, ceiling, models):
	if kind is ATOM:
		return _zoneAtom(sel, floor, ceiling, models)
	elif kind is RESIDUE:
		return _zoneResidue(sel, floor, ceiling, models)
	else:
		return sel

def _zoneAtom(orig, floor, ceiling, modelList):
	coordList = _getCoordList(orig)
	if not coordList:
		return orig
	if floor is None:
		fSq = None
		fbbox = None
	else:
		fSq = floor * floor
		valid, fbbox = chimera.find_minimum_bounding_sphere(coordList)
		if valid:
			fbbox.radius += floor
		else:
			fbbox = None
	if ceiling is None:
		cSq = None
		cbbox = None
	else:
		cSq = ceiling * ceiling
		valid, cbbox = chimera.find_minimum_bounding_sphere(coordList)
		if valid:
			cbbox.radius += ceiling
		else:
			cbbox = None
	zone = selection.ItemizedSelection()
	for m in modelList:
		try:
			atomList = m.atoms
		except AttributeError:
			continue
		for a in atomList:
			try:
				c = a.xformCoord()
			except AttributeError:
				continue
			if cbbox and not cbbox.inside(c):
				continue
			if _inZone(c, coordList, fSq, cSq, fbbox) > 0:
				zone.add(a)
	if floor is None:
		zone.merge(selection.EXTEND, orig)
	return zone

def _zoneResidue(orig, floor, ceiling, modelList):
	coordList = _getCoordList(orig)
	if not coordList:
		return orig
	if floor is None:
		fSq = None
		fbbox = None
	else:
		fSq = floor * floor
		valid, fbbox = chimera.find_minimum_bounding_sphere(coordList)
		if valid:
			fbbox.radius += floor
		else:
			fbbox = None
	if ceiling is None:
		cSq = None
		cbbox = None
	else:
		cSq = ceiling * ceiling
		valid, cbbox = chimera.find_minimum_bounding_sphere(coordList)
		if valid:
			cbbox.radius += ceiling
		else:
			cbbox = None
	zone = selection.ItemizedSelection()
	for m in modelList:
		try:
			residueList = m.residues
		except AttributeError:
			continue
		for r in residueList:
			atomList = r.oslChildren()
			keep = ceiling is None
			for a in atomList:
				try:
					c = a.xformCoord()
				except AttributeError:
					continue
				if cbbox and not cbbox.inside(c):
					continue
				isIn = _inZone(c, coordList, fSq, cSq, fbbox)
				if isIn < 0:
					keep = 0
					break
				elif isIn > 0:
					keep = 1
			if keep:
				zone.add(atomList)
	if floor is None:
		zone.merge(selection.EXTEND, orig)
	return zone

def _getCoordList(sel):
	coordList = []
	for v in sel.vertices():
		try:
			coordList.append(v.xformCoord())
		except AttributeError:
			pass
	return coordList

def _inZone(c, cList, fSq, cSq, fbbox):
	if fSq is not None:
		if fbbox and not fbbox.inside(c):
			return 1
		closeEnough = 0
		for c2 in cList:
			dSq = c.sqdistance(c2)
			if dSq < fSq:
				return -1
			if cSq is None or dSq <= cSq:
				closeEnough = 1
		return closeEnough
	else:
		for c2 in cList:
			dSq = c.sqdistance(c2)
			if cSq is None or dSq <= cSq:
				return 1
		return 0

def knownSelection(s, models=None):
	s = s.strip()
	if s in pickSynonyms:
		return 1
	namedSel = s
	if namedSel[:3] == "sel" and '=' in namedSel:
		equal = namedSel.index('=')
		left = namedSel[:equal].strip()
		if left == "sel":
			namedSel = namedSel[equal+1:].strip()
	if selection.savedSels.has_key(namedSel):
		return selection.savedSels[namedSel]

	_initSelections()
	if s in _sels:
		from selection.manager import selMgr
		return selMgr.selectionFromText(_sels[s], models=models)

	from Midas.midas_text import userSurfCategories
	if s in userSurfCategories:
		return "@/surfaceCategory=%s" % s
	return None

_sels = None
def _initSelections():
	if _sels is None:
		from selection.manager import selMgr
		selMgr.addCallback(_updateSels)
		_updateSels()

def _updateSels(prior=None, selDict=None):
	global _sels
	from selection.manager import selMgr
	if prior is None:
		_sels = {}
		prior = ""
		selDict = selMgr.selectorDict()
	skip = [selection.residues.registrant, selection.chainID.registrant]
	lowPriority = [chimera.idatm.registrant, "ChemGroup"]
	for k, v in selDict.items():
		registrant, val = v
		if registrant in skip:
			continue
		if isinstance(val, dict):
			_updateSels(k, val)
		else:
			if registrant not in lowPriority or k not in _sels:
				_sels[k] = val[0]
			_sels[prior + "." + k] = val[0]
