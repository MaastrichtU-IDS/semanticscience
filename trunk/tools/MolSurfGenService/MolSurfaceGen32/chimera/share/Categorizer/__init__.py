# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 26841 2009-01-30 22:58:24Z pett $

"""
Categorize atoms into solvent, ligand, etc. categories

The categories and criteria are:

	solvent -- The most numerous "small" (10 atom or less) single-residue
		chain that isn't a singleton atom of atomic number 9 or more
		(florine or heavier) and that occurs at least 10 times.
		Also, all singleton atoms of atomic number 8 or less.

	ions --  Singleton atoms not categorized as solvent.

	ligand --  Chains smaller than 1/4 the longest chain of the model that
		aren't solvent or ions and less than 10 residues long.

	main --  Remainder of chains.
"""
categories = set([
	intern("solvent"), intern("ions"), intern("ligand"), intern("main")
])
_models = {}
def categorize(trigger, justdoit, bonds):
	# can't get the molecule attribute of deleted bonds,
	# so have to be tricky
	createModels = {}
	for b in bonds.created:
		createModels[b.molecule] = 1
	changeModels = createModels.keys()
	for prevModel, prevBonds in _models.items():
		if createModels.has_key(prevModel):
			continue
		try:
			curBonds = len(prevModel.bonds)
		except:
			# molecule probably deleted
			del _models[prevModel]
			continue
		if curBonds != prevBonds:
			changeModels.append(prevModel)

	for model in changeModels:
		_models[model] = len(model.bonds)
		solvents = {}
		roots = model.roots(1)

		# for efficiency, segregate roots into small solvents/other
		smallSolvents = []
		rootDict = {}
		for root in roots:
			if root.size.numAtoms < 4 \
			and root.atom.residue.type in ("HOH", "WAT", "DOD"):
				smallSolvents.append(root)
			elif root.size.numAtoms == 1 \
			and 5 < root.atom.element.number < 9 \
			and root.size.numAtoms == len(root.atom.residue.atoms):
				smallSolvents.append(root)
			else:
				rootDict[root] = 1

		# assign solvent
		if smallSolvents:
			solvents["small solvents"] = smallSolvents
		for root in rootDict.keys():
			if root.size.numAtoms > 10:
				continue
			if root.size.numAtoms != len(root.atom.residue.atoms):
				continue
			
			# potential solvent
			resID = root.atom.residue.type
			if solvents.has_key(resID):
				solvents[resID].append(root)
			else:
				solvents[resID] = [root]
		
		solvent = []
		for resID in solvents.keys():
			if len(solvents[resID]) < 10:
				continue
			if len(solvents[resID]) < len(solvent):
				continue
			solvent = solvents[resID]
		
		if solvent:
			for root in solvent:
				for atom in model.traverseAtoms(root):
					curCat = atom.surfaceCategory
					if not curCat or curCat in categories:
						atom.surfaceCategory = "solvent"
		if solvent != smallSolvents:
			for root in smallSolvents:
				for atom in model.traverseAtoms(root):
					curCat = atom.surfaceCategory
					if not curCat or curCat in categories:
						atom.surfaceCategory = "solvent"
			for root in solvent:
				del rootDict[root]
			
		# assign ions
		ions = []
		for root in rootDict.keys():
			if root.size.numAtoms == 1 \
			and root.atom.element.number > 1:
				ions.append(root)
		
		# possibly expand to remainder of residue (coordination complex)
		for root in ions[:]:
			if root.size.numAtoms == len(root.atom.residue.atoms):
				continue
			seenRoots = set([root])
			for a in root.atom.residue.atoms:
				rt = model.rootForAtom(a, True)
				if rt in seenRoots:
					continue
				seenRoots.add(rt)
			# add segments of less than 5 heavy atoms
			for rt in seenRoots:
				if rt in ions:
					continue
				if len([a for a in model.traverseAtoms(rt)
						if a.element.number > 1]) < 5:
					ions.append(rt)
		for root in ions:
			del rootDict[root]
			for atom in model.traverseAtoms(root):
				curCat = atom.surfaceCategory
				if not curCat or curCat in categories:
					atom.surfaceCategory = "ions"
		
		if len(rootDict) == 0:
			continue

		# assign ligand

		# find longest chain
		longest = None
		for root in rootDict.keys():
			if not longest \
			or root.size.numAtoms > longest.size.numAtoms:
				longest = root
		
		ligands = []
		ligandCutoff = min(longest.size.numAtoms/4, 250)
		for root in rootDict.keys():
			if root.size.numAtoms < ligandCutoff:
				# fewer than 10 residues?
				if len(dict.fromkeys([a.residue for a in
				model.traverseAtoms(root)])) < 10:
					ligands.append(root)
		
		for root in ligands:
			del rootDict[root]
			for atom in model.traverseAtoms(root):
				curCat = atom.surfaceCategory
				if not curCat or curCat in categories:
					atom.surfaceCategory = "ligand"
			
		# remainder in "main" category
		for root in rootDict.keys():
			for atom in model.traverseAtoms(root):
				curCat = atom.surfaceCategory
				if not curCat or curCat in categories:
					atom.surfaceCategory = "main"


# make these available as selectors
from chimera.selection.manager import selMgr
selectorTemplate = """\
sel.merge(selection.REPLACE, selection.OSLSelection("@/surfaceCategory=%s"))
sel.addImplied(vertices=0)
"""
for cat in categories:
	selMgr.addSelector("surface categorizer", [selMgr.STRUCTURE,
		cat], selectorTemplate % cat)
selMgr.makeCallbacks()
