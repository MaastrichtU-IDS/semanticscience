# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: residues.py 26655 2009-01-07 22:02:30Z gregc $

from manager import selMgr, SortString

# register residue type selectors
registrant = "existing residues"
# add residue's atoms to addition list (rather than the residue) since
# we are going to addImplied afterward anyway
selectorTemplate = """\
selAdd = []
for mol in molecules:
        for res in mol.residues:
                if res.type == "%s":
                        selAdd.extend(res.oslChildren())
sel.add(selAdd)
sel.addImplied(vertices=0)
"""

groupTemplate = """\
selAdd = []
from chimera.resCode import protein3to1, nucleic3to1, standard3to1
for mol in molecules:
        for res in mol.residues:
                if res.type %sin %s:
                        selAdd.extend(res.oslChildren())
sel.add(selAdd)
sel.addImplied(vertices=0)
"""

import chimera

prevResidues = {}

def updateResidues(trigName, myData, changes):
	if changes and not changes.created and not changes.deleted:
		return
	unseen = prevResidues.copy()
	from chimera.resCode import nucleic3to1, protein3to1
	new = {}
	for mol in chimera.openModels.list(modelTypes=[chimera.Molecule]):
		for res in mol.residues:
			if prevResidues.has_key(res.type):
				if unseen.has_key(res.type):
					del unseen[res.type]
			else:
				# we will add 1 to these numbers when 
				# selectors are registered, so that
				# other residue-menu entries precede these
				# selectors are are separated from them
				# with a menu separator
				if res.type in protein3to1:
					grouping = 2
				elif res.type in nucleic3to1:
					grouping = 1
				else:
					grouping = 0
				new[res.type] = grouping
	if not new and not unseen:
		return
	for newResType, grouping in new.items():
		selMgr.addSelector(registrant, [selMgr.RESIDUE,
			SortString(newResType, cmpVal=1)],
			selectorTemplate % (newResType,), grouping=grouping+1)
	counts = [0] * 3
	for grouping in prevResidues.values():
		counts[grouping] += 1
	prevResidues.update(new)
	for formerResType in unseen.keys():
		selMgr.deleteSelector(registrant,
					[selMgr.RESIDUE, formerResType])
		del prevResidues[formerResType]
	newCounts = [0] * 3
	for grouping in prevResidues.values():
		newCounts[grouping] += 1
	for i, oldCount in enumerate(counts):
		newCount = newCounts[i]
		needOld = oldCount > 1
		needNew = newCount > 1
		if needNew == needOld:
			continue
		groupNames = [
			SortString("all nonstandard", cmpVal=0),
			SortString("standard nucleic acids", cmpVal=0),
			SortString("standard amino acids", cmpVal=0)
		]
		if needNew:
			# add a group entry
			selMgr.addSelector(registrant, [selMgr.RESIDUE,
				groupNames[i]], groupTemplate % [
					("not ", "standard3to1"),
					("", "nucleic3to1"),
					("", "protein3to1")
				][i], grouping=i+1)
		else:
			# delete old group entry
			selMgr.deleteSelector(registrant,
					[selMgr.RESIDUE, groupNames[i]])
	
	selMgr.makeCallbacks()

chimera.triggers.addHandler('Residue', updateResidues, None)

updateResidues(None, None, None)
