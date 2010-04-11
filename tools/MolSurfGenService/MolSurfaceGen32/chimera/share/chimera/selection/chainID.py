# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: chainID.py 28907 2009-09-29 20:29:01Z pett $

from manager import selMgr

# register chain ID selectors
registrant = "chain IDs"

def selector(chainID, mol=None):
	# add residue's atoms to addition list (rather than the residue) since
	# we are going to addImplied afterward anyway
	if mol is None:
		return """\
selAdd = []
for mol in molecules:
	for res in mol.residues:
		if res.id.chainId == "%s":
			selAdd.extend(res.atoms)
sel.add(selAdd)
sel.addImplied(vertices=0)
import chimera 
if not chimera.nogui:
	from chimera.selection.upDown import selChainTrace
	sel.add(selChainTrace(sel))
""" % (chainID,)
	return """\
selAdd = []
for mol in molecules:
	if id(mol) != %d:
		continue
	for res in mol.residues:
		if res.id.chainId == "%s":
			selAdd.extend(res.atoms)
sel.add(selAdd)
sel.addImplied(vertices=0)
import chimera 
if not chimera.nogui:
	from chimera.selection.upDown import selChainTrace
	sel.add(selChainTrace(sel))
""" % (id(mol), chainID)

import chimera

prevChainIDs = {}

def chainIDtoName(chainID):
	if chainID == " ":
		return '(no ID)'
	return chainID

_molNames = {}
def molToName(mol):
	global _molNames
	if mol not in _molNames:
		_molNames[mol] = "%s (%s)" % (mol.name, mol.oslIdent())
	return _molNames[mol]

def updateChains(trigName, myData, changes):
	if changes and not changes.created and not changes.deleted:
		return

	global prevChainIDs
	# would like a two-level shallow copy!
	unseen = {}
	for chainID, prevMols in prevChainIDs.items():
		unseen[chainID] = prevMols.copy()
	nextChainIDs = {}
	new = {}
	for mol in chimera.openModels.list(modelTypes=[chimera.Molecule]):
		for res in mol.residues:
			chainID = res.id.chainId
			if chainID in nextChainIDs:
				if mol in nextChainIDs[chainID]:
					continue
				nextChainIDs[chainID].add(mol)
			else:
				nextChainIDs[chainID] = set([mol])
			if chainID in unseen and mol in unseen[chainID]:
				unseen[chainID].remove(mol)
				if not unseen[chainID]:
					del unseen[chainID]
			if chainID in prevChainIDs \
			and mol in prevChainIDs[chainID]:
				continue
			if chainID in new:
				new[chainID].add(mol)
			else:
				new[chainID] = set([mol])
	if not new and not unseen:
		return
	# if prev and next differ in need for rollover, nuke the old 
	# selectors (put the old ones in 'unseen' and the next ones in 'new')
	for chainID, prevMols in prevChainIDs.items():
		if chainID in nextChainIDs:
			numNext = len(nextChainIDs[chainID])
		else:
			numNext = 0
		if (len(prevMols) <= 1) == (numNext <= 1):
			continue
		unseen.setdefault(chainID, set()).update(prevMols)
		if len(prevMols) > 1:
			selMgr.deleteSelector(registrant, [selMgr.CHAINID,
					chainIDtoName(chainID), "all"])
		if numNext:
			new.setdefault(chainID, set()).update(nextChainIDs[chainID])
	for chainID, mols in unseen.items():
		chainName = chainIDtoName(chainID)
		prevMols = prevChainIDs[chainID]
		if len(prevMols) == 1:
			# non-rollover
			selMgr.deleteSelector(registrant, [selMgr.CHAINID,
							chainName], prune=True)
		else:
			for mol in mols:
				selMgr.deleteSelector(registrant,
						[selMgr.CHAINID, chainName,
						molToName(mol)], prune=True)
	for mols in unseen.values():
		for mol in mols:
			if mol not in _molNames:
				continue
			for nmols in nextChainIDs.values():
				if mol in nmols:
					break
			else:
				del _molNames[mol]
	for chainID, mols in new.items():
		chainName = chainIDtoName(chainID)
		nextMols = nextChainIDs[chainID]
		if len(nextMols) == 1:
			# non-rollover
			selMgr.addSelector(registrant, [selMgr.CHAINID,
						chainName], selector(chainID),
						grouping=0)
		else:
			for mol in mols:
				selMgr.addSelector(registrant, [selMgr.CHAINID,
						chainName, molToName(mol)],
						selector(chainID, mol))
			selMgr.addSelector(registrant, [selMgr.CHAINID,
					chainName, "all"], selector(chainID),
					grouping=1)

	prevChainIDs = nextChainIDs
	selMgr.makeCallbacks()

def prev_updateChains(trigName, myData, changes):
	if changes and not changes.created and not changes.deleted:
		return

	unseen = prevChainIDs.copy()
	new = {}
	for mol in chimera.openModels.list(modelTypes=[chimera.Molecule]):
		for res in mol.residues:
			chainID = res.id.chainId
			if prevChainIDs.has_key(chainID):
				if unseen.has_key(chainID):
					del unseen[chainID]
			else:
				new[chainID] = 1
	if not new and not unseen:
		return
	for newChainID in new.keys():
		selMgr.addSelector(registrant, [selMgr.CHAINID,
					chainIDtoName(newChainID)],
					selectorTemplate % (newChainID,))
	prevChainIDs.update(new)
	for formerChainID in unseen.keys():
		selMgr.deleteSelector(registrant, [selMgr.CHAINID,
					chainIDtoName(formerChainID)])
		del prevChainIDs[formerChainID]
	
	selMgr.makeCallbacks()

chimera.triggers.addHandler('Residue', updateChains, None)

selMgr.addCategory(registrant, [selMgr.CHAINID])
updateChains(None, None, None)
