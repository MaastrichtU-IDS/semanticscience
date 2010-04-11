# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: molEdit.py 26655 2009-01-07 22:02:30Z gregc $

from math import pi, cos, sin
from chimera import cross, Xform, Coord, Point, Atom, Bond

def addAtom(name, element, residue, loc, serialNumber=None, bondedTo=None,
							occupancy=None):
	"""Add an atom at the Point 'loc'
	
	   The atom is added to the given residue (and its molecule).
	   'loc' can be a sequence of Points if there are multiple
	   coordinate sets.

	   If you are adding atoms in bulk, make sure that you provide the
	   optional 'serialNumber' argument, since the code that automatically
	   determines the serial number is slow.

	   'bondedTo' is None or an Atom.  If an Atom, then the new atom 
	   inherits various attributes from that atom and a bond to that
	   Atom is created.

	   If 'occupancy' is not None or the 'bondedTo' atom has an
	   occupancy, the new atom will be given the corresponding occupancy.

	   Returns the new atom.
	"""

	mol = residue.molecule
	newAtom = mol.newAtom(name, element)
	residue.addAtom(newAtom)
	if not mol.coordSets:
		if isinstance(loc, Point):
			mol.newCoordSet(1)
		else:
			for i in range(1, len(loc)+1):
				mol.newCoordSet(i)
		mol.activeCoordSet = mol.findCoordSet(1)
	for i, coordSet in enumerate(mol.coordSets.values()):
		if isinstance(loc, Point):
			newCoord = loc
		else:
			newCoord = loc[i]
		newAtom.setCoord(newCoord, coordSet)
	if serialNumber is None:
		try:
			serialNumber = max(
					[a.serialNumber for a in mol.atoms]) + 1
		except AttributeError:
			serialNumber = len(mol.atoms)
	newAtom.serialNumber = serialNumber
	if occupancy is not None or bondedTo and hasattr(bondedTo, 'occupancy'):
		newAtom.occupancy = getattr(bondedTo, 'occupancy', occupancy)
	if bondedTo:
		newAtom.altLoc = bondedTo.altLoc
		newAtom.display = bondedTo.display
		newAtom.surfaceDisplay = bondedTo.surfaceDisplay
		newAtom.drawMode = bondedTo.drawMode
		addBond(newAtom, bondedTo)
	return newAtom

def addDihedralAtom(name, element, n1, n2, n3, dist, angle, dihed,
		molecule=None, residue=None, bonded=False, occupancy=None):
	"""Add an atom given 3 Atoms/Points and angle/distance constraints
	
	   The atom is added to the given molecule.  If no molecule or
	   residue is specified, then n1/n2/n3 must be Atoms and the new atom
	   is added to n1's molecule and residue.  If just residue is
	   specified, the new atom is added to that residue and its molecule.

	   'n1' marks the position from which 'dist' is measured, and in
	   combination with 'n2' forms 'angle', and then with 'n3' forms
	   'dihed'.

	   if 'bonded' is True then n1 must be an Atom and the new atom will
	   be bonded to it.

	   If 'occupancy' is not None or the 'bonded' is True and n1 has an
	   occupancy, the new atom will be given the corresponding occupancy.

	   Returns the new atom.
	"""

	if bonded:
		bondedTo = n1
	else:
		bondedTo = None
	if n1.__class__ is Atom:
		if not residue:
			molecule = n1.molecule
			residue = n1.residue
		n1 = n1.coord()
		n2 = n2.coord()
		n3 = n3.coord()
	if not molecule:
		molecule = residue.molecule
	
	finalPt = findPt(n1, n2, n3, dist, angle, dihed)

	return addAtom(name, element, residue, finalPt, bondedTo=bondedTo,
							occupancy=occupancy)

def addBond(a1, a2, drawMode=None, halfbond=None, color=None):
	if a1.bonds:
		sampleBond = a1.bonds[0]
	elif a2.bonds:
		sampleBond = a2.bonds[0]
	else:
		sampleBond = None
	if drawMode is None:
		if sampleBond:
			drawMode = sampleBond.drawMode
		elif a1.drawMode == Atom.Dot:
			drawMode = Bond.Wire
		else:
			drawMode = Bond.Stick
	if halfbond is None:
		if sampleBond:
			halfbond = sampleBond.halfbond
		else:
			halfbond = True
	try:
		b = a1.molecule.newBond(a1, a2)
	except TypeError, v:
		if str(v).startswith("Attempt to form duplicate covalent bond"
					) or str(v).startswith("Cannot form"
					" covalent bond joining two molecules"):
			from chimera import UserError
			raise UserError(v)
		else:
			raise
	b.drawMode = drawMode
	b.halfbond = halfbond
	if not halfbond:
		if color is None:
			if sampleBond:
				color = sampleBond.color
			else:
				color = a1.color
		b.color = color
	return b

def findPt(n1, n2, n3, dist, angle, dihed):
	# cribbed from Midas addgrp command
	v12 = n2 - n1
	v13 = n3 - n1
	v12.normalize()
	x = cross(v13, v12)
	x.normalize()
	y = cross(v12, x)
	y.normalize()

	mat = [0.0] * 12
	for i in range(3):
		mat[i*4] = x[i]
		mat[1 + i*4] = y[i]
		mat[2 + i*4] = v12[i]
		mat[3 + i*4] = n1[i]
	
	xform = Xform.xform(*mat)

	radAngle = pi * angle / 180.0
	tmp = dist * sin(radAngle)
	radDihed = pi * dihed / 180.0
	pt = Point(tmp*sin(radDihed), tmp*cos(radDihed), dist*cos(radAngle))
	return xform.apply(pt)

def genAtomName(element, residue):
	n = 1
	while True:
		name = "%s%d" % (str(element).upper(), n)
		if name not in residue.atomsMap:
			break
		n += 1
	return name
