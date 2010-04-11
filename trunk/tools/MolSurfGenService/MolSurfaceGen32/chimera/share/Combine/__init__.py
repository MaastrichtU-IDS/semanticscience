# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 27885 2009-06-19 20:19:43Z pett $

class CombineError(ValueError):
	pass

def combine(mols, refMol, newChainIDs=True, log=False, returnMapping=False):
	from chimera import replyobj

	# figure out residue chain/number remapping
	origChainIDs = {}
	numChains = 0
	minNums = {}
	maxNums = {}
	for m in mols:
		seenIDs = set()
		for r in m.residues:
			chainID = r.id.chainId
			num = r.id.position
			key = (m, chainID)
			if key in minNums:
				if num > maxNums[key]:
					maxNums[key] = num
				elif num < minNums[key]:
					minNums[key] = num
			else:
				minNums[key] = maxNums[key] = num
			if chainID in seenIDs:
				continue
			numChains += 1
			seenIDs.add(chainID)
			origChainIDs.setdefault(chainID, []).append(m)
	resMap = {}
	if newChainIDs:
		if numChains > 62:
			raise CombineError("More than 62 chains; cannot"
				" uniquely identify with single characters")
		from string import uppercase, lowercase, digits
		possibleIDs = uppercase + lowercase + digits
		usedChainIDs = set(origChainIDs.keys())
		chainIDmap = {}
		for chainID, idMols in origChainIDs.items():
			if len(chainID) > 1:
				continue
			chainIDmap[(idMols[0], chainID)] = chainID
			usedChainIDs.add(chainID)
			for m in idMols[1:]:
				for c in possibleIDs:
					if c not in usedChainIDs:
						break
				if log:
					replyobj.info("Remapping %s chain %s"
						" to %s\n" % (m, chainID, c))
				usedChainIDs.add(c)
				chainIDmap[(m, chainID)] = c
		for m in mols:
			for r in m.residues:
				chainID = r.id.chainId
				if len(chainID) > 1:
					continue
				resMap[r] = (chainIDmap[(m, chainID)],
								r.id.position)
	# handle renumbering for all chains if newChainIDs False,
	# otherwise just water/het chains
	offsets = {}
	for chainID, idMols in origChainIDs.items():
		if newChainIDs and len(chainID) < 2:
			continue
		minMaxs = []
		for m in idMols:
			mmin = minNums[(m, chainID)]
			mmax = maxNums[(m, chainID)]
			for omin, omax in minMaxs:
				if omin < mmin < omax or omin < mmax < omax:
					gmax = max([mm[1] for mm in minMaxs])
					offset = gmax - mmin + 1
					break
			else:
				offset = 0
			offsets[(m, chainID)] = offset
			minMaxs.append((mmin+offset, mmax+offset))
			if log and offset:
				replyobj.info("Adding %d to %s chain %s"
					" numbering\n" % (offset, m, chainID))
	for m in mols:
		for r in m.residues:
			chainID = r.id.chainId
			try:
				offset = offsets[(m, chainID)]
			except KeyError:
				continue
			resMap[r] = (chainID, r.id.position + offset)

	# combine...
	from chimera import Atom, Bond, Residue, Molecule
	combined = Molecule()
	combined.name = "combination"
	from SimpleSession.save import optionalAttributes
	from chimera.molEdit import addAtom
	atomAttrs = optionalAttributes[Atom].keys() + ['color', 'vdwColor',
		'labelColor', 'surfaceColor', 'drawMode', 'display', 'label',
		'radius', 'surfaceDisplay', 'surfaceCategory', 'surfaceOpacity',
		'vdw']
	bondAttrs = optionalAttributes[Bond].keys() + ['drawMode', 'display',
		'radius']
	resAttrs = optionalAttributes[Residue].keys() + ['ribbonColor',
		'labelColor', 'isHelix', 'isSheet', 'isTurn', 'ribbonDrawMode',
		'ribbonDisplay', 'label', 'isHet']
	serial = 1
	atomMap = {}
	for m in mols:
		if m.openState == refMol.openState:
			xform = None
		else:
			xform = refMol.openState.xform
			xform.invert()
		for r in m.residues:
			chainID, pos = resMap[r]
			nr = combined.newResidue(r.type, chainID, pos,
							r.id.insertionCode)
			for attrName in resAttrs:
				try:
					setattr(nr, attrName,
							getattr(r, attrName))
				except AttributeError:
					continue
			ratoms = r.atoms
			ratoms.sort(lambda a1, a2:
					cmp(a1.coordIndex, a2.coordIndex))
			for a in ratoms:
				if xform is None:
					crd = a.coord()
				else:
					crd = xform.apply(a.xformCoord())
				na = addAtom(a.name, a.element, nr, crd,
							serialNumber=serial)
				na.altLoc = a.altLoc
				atomMap[a] = na
				serial += 1
				for attrName in atomAttrs:
					try:
						setattr(na, attrName,
							getattr(a, attrName))
					except AttributeError:
						continue
		for b in m.bonds:
			a1, a2 = b.atoms
			nb = combined.newBond(atomMap[a1], atomMap[a2])
			for attrName in bondAttrs:
				try:
					setattr(nb, attrName,
						getattr(b, attrName))
				except AttributeError:
					continue
	consensusAttrs = ['color', 'display', 'lineWidth', 'pointSize',
		'stickScale', 'surfaceOpacity', 'ballScale', 'vdwDensity',
		'autochain', 'ribbonHidesMainchain']
	for attrName in consensusAttrs:
		consensusVal = None
		for m in mols:
			val = getattr(m, attrName)
			if consensusVal == None:
				consensusVal = val
			elif val != consensusVal:
				break
		else:
			setattr(combined, attrName, consensusVal)

	associatedModels = set()
	for m in mols:
		associatedModels.update(m.associatedModels())
	from chimera import PseudoBondMgr
	for opbg in PseudoBondMgr.mgr().pseudoBondGroups:
		if opbg in associatedModels:
			if opbg.category.startswith("internal-chain-"):
				continue
			assert(opbg.category.startswith("coordination complex"))
			from chimera.misc import getPseudoBondGroup
			pbg = getPseudoBondGroup("coordination complexes of %s"
				% combined.name, associateWith=[combined])
			for attrName in ['color', 'showStubBonds', 'lineWidth',
						'stickScale', 'lineType']:
				setattr(pbg, attrName, getattr(opbg, attrName))
		else:
			pbg = opbg
		for opb in opbg.pseudoBonds:
			oa1, oa2 = opb.atoms
			na1 = atomMap.get(oa1, oa1)
			na2 = atomMap.get(oa2, oa2)
			if oa1 == na1 and oa2 == na2:
				continue
			pb = pbg.newPseudoBond(na1, na2)
			for attrName in ['drawMode', 'display', 'halfbond',
					'label', 'color', 'labelColor']:
				setattr(pb, attrName, getattr(opb, attrName))
		
	if returnMapping:
		return atomMap, combined
	return combined

def cmdCombine(mols, name="combination", newChainIDs=True, log=True,
				close=False, modelId=None, refMol=None):
	from chimera.misc import oslModelCmp
	mols.sort(lambda m1, m2: oslModelCmp(m1.oslIdent(), m2.oslIdent()))

	from Midas import MidasError
	if not mols:
		raise MidasError("No molecules specified")
	if refMol == None:
		refMol = mols[:1]
	if len(refMol) == 0:
		raise MidasError("No reference molecule specified")
	elif len(refMol) > 1:
		raise MidasError("Multiple reference molecules specified")
	refMol = refMol[0]
	if modelId is not None and type(modelId) != int:
		try:
			modelId = int(modelId[1:])
		except:
			raise MidasError("modelId value must be integer")
	from chimera import suppressNewMoleculeProcessing, \
					restoreNewMoleculeProcessing
	suppressNewMoleculeProcessing()
	try:
		m = combine(mols, refMol, newChainIDs=newChainIDs, log=log)
	except CombineError, v:
		restoreNewMoleculeProcessing()
		raise MidasError(v)
	from chimera import openModels
	m.name = name
	kw = {'shareXform': False}
	if modelId != None:
		kw['baseId'] = modelId
	openModels.add([m], **kw)
	m.openState.xform = refMol.openState.xform
	restoreNewMoleculeProcessing()
	if close:
		openModels.close(mols)
