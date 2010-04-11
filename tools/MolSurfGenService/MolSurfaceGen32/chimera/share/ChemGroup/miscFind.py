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

import ChemGroup

# find aromatic ring groups
def findAromatics(molecules):
	groups = []
	for molecule in molecules:
		rings = molecule.minimumRings()
		for ring in rings:
			if ring.aromatic():
				groups.append(ring.atoms)
	return groups

def findAliAmines(molecules):
	# find aliphatic amines
	return ChemGroup.findGroup("aliphatic primary amine", molecules) \
	     + ChemGroup.findGroup("aliphatic secondary amine", molecules) \
	     + ChemGroup.findGroup("aliphatic tertiary amine", molecules) \
	     + ChemGroup.findGroup("aliphatic quaternary amine", molecules)

def findAroAmines(molecules, order):
	# aromatic amines of given order (1 = primary, 2 = secondary, etc.)
	# order == 0 ==> all

	amines = []
	for molecule in molecules:
		Npls = {} # key is nitrogen, value is amine
		for atom in molecule.atoms:
			if atom.idatmType != 'Npl':
				continue
			boundCarbons = 0
			boundAro = False
			amine = [atom]
			for bonded in atom.neighbors:
				if bonded.element.number == ChemGroup.H:
					amine.append(bonded)
					continue
				if bonded.element.number == ChemGroup.C:
					boundCarbons = boundCarbons + 1
					if bonded.idatmType == 'Car':
						boundAro = True
						continue
					if bonded.idatmType == 'C3':
						continue
				# something non-amine-like is bonded...
				boundAro = False
				break
			if not boundAro:
				continue
			if order and boundCarbons != order:
				continue
			Npls[atom] = amine

		for ring in molecule.minimumRings():
			if not ring.aromatic():
				continue
			for atom in ring.atoms:
				if Npls.has_key(atom):
					del Npls[atom]
		amines = amines + Npls.values()

	return amines
