# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: miscFind.py 26655 2009-01-07 22:02:30Z gregc $

import chimera

def hetNH(molecules, ringSize, aromaticOnly=0):
	"""unfused trigonal planar nitrogens in 'ringSize'-member rings"""
	from chimera.idatm import typeInfo
	groups = []
	for molecule in molecules:
		for atom in molecule.atoms:
			if atom.idatmType not in ["Npl", "N2+"]:
				continue
			neighbors = atom.primaryNeighbors()
			if len(neighbors) == 3 \
			and 1 not in [n.element.number for n in neighbors]:
				continue
			minRings = atom.minimumRings()
			if len(minRings) != 1:
				continue
			ring = minRings[0]
			if len(ring.bonds) != ringSize:
				continue
			if aromaticOnly and not ring.aromatic():
				continue
			bondedInRing = filter(lambda a, ra=ring.atoms: a in ra,
								neighbors)
			groups.append([atom] + bondedInRing)
	return groups

def symHet5N(molecules):
	"""unfused planar acceptor nitrogen in symmetric 5-member ring"""
	groups = []
	for molecule in molecules:
		for atom in molecule.atoms:
			if atom.idatmType != "N2":
				continue
			rings = atom.minimumRings()
			if len(rings) != 1:
				continue
			ring = rings[0]
			if len(ring.bonds) != 5:
				continue
			bonded1, bonded2 = filter(lambda a, ra=ring.atoms:
					a in ra, atom.primaryNeighbors())
			if bonded1.element != bonded2.element:
				continue
			possibleGroup = [atom, bonded1, bonded2]
			remain1, remain2 = filter(lambda a, pg=possibleGroup:
							a not in pg, ring.atoms)
			if remain1.element == remain2.element:
				groups.append(possibleGroup)
	return groups

def symHet6N(molecules):
	"""unfused planar acceptor nitrogen in symmetric 6-member ring"""
	groups = []
	for molecule in molecules:
		for atom in molecule.atoms:
			if atom.idatmType != "N2":
				continue
			rings = atom.minimumRings()
			if len(rings) != 1:
				continue
			ring = rings[0]
			if len(ring.bonds) != 6:
				continue
			bonded1, bonded2 = filter(lambda a, ra=ring.atoms:
					a in ra, atom.primaryNeighbors())
			if bonded1.element != bonded2.element:
				continue
			possibleGroup = [atom, bonded1, bonded2]
			remainRing = filter(lambda a, pg=possibleGroup:
							a not in pg, ring.atoms)
			nextTo1 = bonded1.primaryNeighbors()
			nextTo2 = bonded2.primaryNeighbors()
			n1, n2 = filter(lambda a, n1=nextTo1,
				n2=nextTo2: a in n1 or a in n2, remainRing)
			if n1.element == n2.element:
				groups.append(possibleGroup)
	return groups

def asymHet5N(molecules):
	"""unfused planar acceptor nitrogen in asymmetric 5-member ring"""
	groups = []
	for molecule in molecules:
		for atom in molecule.atoms:
			if atom.idatmType != "N2":
				continue
			rings = atom.minimumRings()
			if len(rings) != 1:
				continue
			ring = rings[0]
			if len(ring.bonds) != 5:
				continue
			bonded1, bonded2 = filter(lambda a, ra=ring.atoms:
					a in ra, atom.primaryNeighbors())
			possibleGroup = [atom, bonded1, bonded2]
			if bonded1.element != bonded2.element:
				groups.append(possibleGroup)
				continue
			remain1, remain2 = filter(lambda a, pg=possibleGroup:
							a not in pg, ring.atoms)
			if remain1.element != remain2.element:
				groups.append(possibleGroup)
	return groups

def asymHet6N(molecules):
	"""unfused planar acceptor nitrogen in asymmetric 6-member ring"""
	groups = []
	for molecule in molecules:
		for atom in molecule.atoms:
			if atom.idatmType != "N2":
				continue
			rings = atom.minimumRings()
			if len(rings) != 1:
				continue
			ring = rings[0]
			if len(ring.bonds) != 6:
				continue
			bonded1, bonded2 = filter(lambda a, ra=ring.atoms:
					a in ra, atom.primaryNeighbors())
			possibleGroup = [atom, bonded1, bonded2]
			if bonded1.element != bonded2.element:
				groups.append(possibleGroup)
				continue
			remainRing = filter(lambda a, pg=possibleGroup:
							a not in pg, ring.atoms)
			nextTo1 = bonded1.primaryNeighbors()
			nextTo2 = bonded2.primaryNeighbors()
			n1, n2 = filter(lambda a, n1=nextTo1,
				n2=nextTo2: a in n1 or a in n2, remainRing)
			if n1.element != n2.element:
				groups.append(possibleGroup)
	return groups

def het5O(molecules):
	"""oxygen in 5-member ring"""
	import chimera
	O = chimera.Element.O

	groups = []
	for molecule in molecules:
		for atom in molecule.atoms:
			if atom.element.number != O:
				continue
			for ring in atom.minimumRings():
				if len(ring.bonds) == 5:
					groups.append([atom]
						+ atom.primaryNeighbors())
	return groups

def nonringN2(molecules):
	"""RNR (N double-bonded to an R)"""
	C = chimera.Element.C

	groups = []
	for molecule in molecules:
		for atom in molecule.atoms:
			if atom.idatmType != "N2":
				continue
			if atom.minimumRings():
				continue
			bonded = atom.primaryNeighbors()
			if len(bonded) != 2:
				continue
			if bonded[0].element.number != C \
			or bonded[1].element.number != C:
				continue
			groups.append([atom] + atom.primaryNeighbors())
	return groups

def acycEther(molecules):
	"""ether oxygen not in a ring system"""
	C = chimera.Element.C

	groups = []
	for molecule in molecules:
		for atom in molecule.atoms:
			if atom.idatmType != "O3":
				continue
			if atom.minimumRings():
				continue
			bondedElements = map(lambda a: a.element.number,
						atom.primaryNeighbors())
			if bondedElements.count(C) != 2:
				continue
			if len(bondedElements) == 2:
				groups.append([atom] + atom.primaryNeighbors())
	return groups

