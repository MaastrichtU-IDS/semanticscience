# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29658 2009-12-18 01:41:18Z pett $

import chimera
from chimera import Point, Element

def setBondLength(bond, bondLength, movingSide="smaller side", status=None):
	bond.molecule.idatmValid = False
	try:
		br = chimera.BondRot(bond)
	except ValueError, v:
		if "already used" in str(v):
			if status:
				status("Cannot change length of active"
					" bond rotation\nDeactivate rotation"
					" and try again", color="red")
			return
		if "cycle" not in str(v):
			raise
		if status:
			status("Bond involved in ring/cycle\n"
				"Moved bonded atoms (only) equally",
				color="blue")
		mid = Point([a.coord() for a in bond.atoms])
		for a in bond.atoms:
			v = a.coord() - mid
			v.length = bondLength/2
			a.setCoord(mid+v)
		return
	if movingSide == "smaller side":
		fixed = br.biggerSide()
		moving = bond.otherAtom(fixed)
	else:
		moving = br.biggerSide()
		fixed = bond.otherAtom(moving)
	mp = moving.coord()
	fp = fixed.coord()
	v1 = mp - fp
	v1.length = bondLength
	delta = v1 - (mp - fp)
	moved = set()
	toMove = [moving]
	while toMove:
		mover = toMove.pop()
		if mover in moved:
			continue
		moved.add(mover)
		mover.setCoord(mover.coord() + delta)
		for neighbor, nb in mover.bondsMap.items():
			if nb == bond:
				continue
			toMove.append(neighbor)
	br.destroy()

def placeHelium(resName, model="scratch", position=None):
	"""place a new helium atom

	   'resName' is the name of the new residue that will contain the
	   helium.  (It will be in the 'het' chain.)

	   'model' can either be a chimera.Molecule instance or a string.
	   If the latter, then a new model is created with the string as
	   its .name attribute.

	   'position' can either be a chimera.Point or None.  If None, then
	   the helium is positioned at the center of the view.
	"""

	if isinstance(model, basestring):
		model = _newModel(model)

	r = _newResidue(model, resName)
	if position is None:
		xf = model.openState.xform
		position = xf.inverse().apply(
				Point(*chimera.viewer.camera.center))
	from chimera.molEdit import addAtom
	return addAtom('He1', Element('He'), r, position)

def placeFragment(fragment, resName, model="scratch", position=None):
	"""place a Fragment (see Fragment.py)

	   'resName' is the name of the new residue that will contain the
	   fragment.  (It will be in the 'het' chain.)

	   'model' can either be a chimera.Molecule instance or a string.
	   If the latter, then a new model is created with the string as
	   its .name attribute.

	   'position' can either be a chimera.Point or None.  If None, then
	   the fragment is positioned at the center of the view.
	"""

	if isinstance(model, basestring):
		model = _newModel(model)
	r = _newResidue(model, resName)
	needFocus = False
	if position is None:
		if len(chimera.openModels.list()) == 1:
			needFocus = True
		xf = model.openState.xform
		position = xf.inverse().apply(
				Point(*chimera.viewer.camera.center))
	# find fragment center
	x = y = z = 0.0
	for element, xyz in fragment.atoms:
		x += xyz[0]
		y += xyz[1]
		z += xyz[2]
	numAtoms = len(fragment.atoms)
	fragCenter = Point(x / numAtoms, y / numAtoms, z / numAtoms)
	correction = position - fragCenter

	from chimera.molEdit import addAtom, genAtomName
	atoms = []
	for element, xyz in fragment.atoms:
		atoms.append(addAtom(genAtomName(element, r), Element(element),
						r, Point(*xyz) + correction))
	for indices, depict in fragment.bonds:
		r.molecule.newBond(atoms[indices[0]], atoms[indices[1]])
	if needFocus:
		chimera.runCommand("focus")
	return r

def placePeptide(sequence, phiPsis, model="scratch", position=None,
						rotlib=None, chainID='A'):
	"""place a peptide sequence

	   'sequence' contains the (upper case) sequence

	   'phiPsis' is a list of phi/psi tuples, one per residue

	   'model' can either be a chimera.Molecule instance or a string.
	   If the latter, then a new model is created with the string as
	   its .name attribute.

	   'position' can either be a chimera.Point or None.  If None, then
	   the fragment is positioned at the center of the view.
	"""

	if not sequence:
		raise ValueError("No sequence supplied")
	sequence = sequence.upper()
	if not sequence.isupper():
		raise ValueError("Sequence contains non-alphabetic characters")
	from chimera.resCode import protein1to3
	for c in sequence:
		if c not in protein1to3:
			raise ValueError("Unrecognized protein 1-letter code:"
								" %s" % c)
	if len(sequence) != len(phiPsis):
		raise ValueError("Number of phi/psis not equal to"
							" sequence length")
	if isinstance(model, basestring):
		model = _newModel(model)
	needFocus = False
	if position is None:
		if len(chimera.openModels.list()) == 1:
			needFocus = True
		xf = model.openState.xform
		position = xf.inverse().apply(
				Point(*chimera.viewer.camera.center))
	prev = [None] * 3
	pos = 1
	from Midas.addAA import DIST_N_C, DIST_CA_N, DIST_C_CA, DIST_C_O
	from chimera.molEdit import findPt, addAtom, addDihedralAtom
	serialNumber = None
	residues = []
	for c, phiPsi in zip(sequence, phiPsis):
		phi, psi = phiPsi
		while model.findResidue(chimera.MolResId(chainID, pos)):
			pos += 1
		r = model.newResidue(protein1to3[c], chainID, pos, ' ')
		residues.append(r)
		for backbone, dist, angle, dihed in (
				('N', DIST_N_C, 116.6, psi),
				('CA', DIST_CA_N, 121.9, 180.0),
				('C', DIST_C_CA, 110.1, phi)):
			if prev[0] == None:
				pt = Point(0.0, 0.0, 0.0)
			elif prev[1] == None:
				pt = Point(dist, 0.0, 0.0)
			elif prev[2] == None:
				pt = findPt(prev[0].coord(), prev[1].coord(),
					Point(0.0, 1.0, 0.0), dist, angle, 0.0)
			else:
				pt = findPt(prev[0].coord(), prev[1].coord(),
					prev[2].coord(), dist, angle, dihed)
			a = addAtom(backbone, Element(backbone[0]), r, pt,
				serialNumber=serialNumber, bondedTo=prev[0])
			serialNumber = a.serialNumber + 1
			prev = [a] + prev[:2]
		o = addDihedralAtom("O", Element("O"), prev[0], prev[1],
			prev[2], DIST_C_O, 120.4, 180.0 + psi, bonded=True)
	# C terminus O/OXT at different angle than mainchain O
	model.deleteAtom(o)
	addDihedralAtom("O", Element("O"), prev[0], prev[1],
			prev[2], DIST_C_O, 117.0, 180.0 + psi, bonded=True)
	addDihedralAtom("OXT", Element("O"), prev[0], prev[1], prev[2],
					DIST_C_O, 117.0, psi, bonded=True)
	from Rotamers import useBestRotamers
	# have to process one by one, otherwise side-chain clashes will occur
	kw = {}
	if rotlib:
		kw['lib'] = rotlib
	for r in residues:
		useBestRotamers("same", [r], criteria="cp", log=False, **kw)
				
	# find peptide center
	coords = []
	for r in residues:
		coords.extend([a.coord() for a in r.atoms])
	center = Point(coords)
	correction = position - center
	for r in residues:
		for a in r.atoms:
			a.setCoord(a.coord() + correction)
	from Midas import ksdssp
	ksdssp([model])
	if needFocus:
		chimera.runCommand("focus")
	return residues

from chimera import elements
elementRadius = {}
for i in range(len(chimera.elements.name)):
	element = Element(i)
	elementRadius[element] = 0.985 * Element.bondRadius(element)
elementRadius[elements.C] = 0.7622
elementRadius[elements.H] = 0.1869
elementRadius[elements.N] = 0.6854
elementRadius[elements.O] = 0.6454
elementRadius[elements.P] = 0.9527
elementRadius[elements.S] = 1.0428

class ParamError(ValueError):
	pass

def bondLength(a1, geom, e2, a2info=None):
	if e2.number == 1:
		from AddH import bondWithHLength
		return bondWithHLength(a1, geom)
	e1 = a1.element
	baseLen = elementRadius[e1] + elementRadius[e2]
	if geom == 1:
		return baseLen
	neighbor, numBonds = a2info
	try:
		ngeom = chimera.idatm.typeInfo[neighbor.idatmType].geometry
	except KeyError:
		return baseLen
	if ngeom == 1:
		return baseLen
	if numBonds == 1 or len(neighbor.primaryBonds()) == 1:
		# putative double bond
		return 0.88 * baseLen
	elif geom == 4 or ngeom == 4:
		return baseLen
	return 0.92 * baseLen

def changeAtom(atom, element, geometry, numBonds, autoClose=True, name=None):
	if len(atom.primaryBonds()) > numBonds:
		raise ParamError("Atom already has more bonds than requested.\n"
			"Either delete some bonds or choose a different number"
			" of requested bonds.")
	from chimera.molEdit import addAtom, genAtomName
	changedAtoms = [atom]
	if not name:
		name = genAtomName(element, atom.residue)
	changeAtomName(atom, name)
	atom.element = element
	if hasattr(atom, 'mol2type'):
		delattr(atom, 'mol2type')
		
	# if we only have one bond, correct its length
	if len(atom.primaryBonds()) == 1:
		neighbor = atom.primaryNeighbors()[0]
		newLength = bondLength(atom, geometry, neighbor.element,
						a2info=(neighbor, numBonds))
		setBondLength(atom.primaryBonds()[0], newLength,
					movingSide="smaller side")

	if numBonds == len(atom.primaryBonds()):
		return changedAtoms

	from chimera.bondGeom import bondPositions
	coPlanar = None
	if geometry == 3 and len(atom.primaryBonds()) == 1:
		n = atom.primaryNeighbors()[0]
		if len(n.primaryBonds()) == 3:
			coPlanar = [nn.coord() for nn in n.primaryNeighbors()
								if nn != atom]
	away = None
	if geometry == 4 and len(atom.primaryBonds()) == 1:
		n = atom.primaryNeighbors()[0]
		if len(n.primaryBonds()) > 1:
			nn = n.primaryNeighbors()[0]
			if nn == atom:
				nn = n.primaryNeighbors()[1]
			away = nn.coord()
	hydrogen = Element("H")
	positions = bondPositions(atom.coord(), geometry,
		bondLength(atom, geometry, hydrogen),
		[n.coord() for n in atom.primaryNeighbors()], coPlanar=coPlanar,
		away=away)[:numBonds-len(atom.primaryBonds())]
	if autoClose:
		if len(atom.molecule.atoms) < 100:
			testAtoms = atom.molecule.atoms
		else:
			from CGLutil.AdaptiveTree import AdaptiveTree
			tree = AdaptiveTree([a.coord().data()
						for a in atom.molecule.atoms],
						a.molecule.atoms, 2.5)
			testAtoms = tree.searchTree(atom.coord().data(), 5.0)
	else:
		testAtoms = []
	for pos in positions:
		for ta in testAtoms:
			if ta == atom:
				continue
			testLen = bondLength(ta, 1, hydrogen)
			testLen2 = testLen * testLen
			if (ta.coord() - pos).sqlength() < testLen2:
				bonder = ta
				# possibly knock off a hydrogen to
				# accomodate the bond...
				for bn in bonder.primaryNeighbors():
					if bn.element.number > 1:
						continue
					if chimera.angle(atom.coord()
							- ta.coord(), bn.coord()
							- ta.coord()) > 45.0:
						continue
					if bn in testAtoms:
						testAtoms.remove(bn)
					atom.molecule.deleteAtom(bn)
					break
				break
		else:
			bonder = addAtom(genAtomName(hydrogen, atom.residue),
				hydrogen, atom.residue, pos, bondedTo=atom)
			changedAtoms.append(bonder)
	return changedAtoms

def changeAtomName(atom, name):
	if replaceableLabel(atom.name, atom.label):
		atom.label = atom.label.replace(atom.name, name, 1)
	atom.name = name

def changeResidueType(res, name):
	if replaceableLabel(res.type, res.label):
		res.label = res.label.replace(res.type, name, 1)
	res.type = name

def replaceableLabel(oldName, label):
	stripped = label.strip()
	if stripped == oldName or (stripped.startswith(oldName)
							and not stripped[len(oldName)].isalpha()):
		return True
	return False

def addDihedralBond(a1, a2, length, angleInfo, dihedInfo):
	"""Make bond between two models.

	   The models will be combined and the originals closed.
	   The new model will be opened in the same id/subid as the
	       non-moving model.

	   a1/a2 are atoms in different models.
	   a2 and atoms in its model will be moved to form the bond.
		'length' is the bond length.
		'angleInfo' is a two-tuple of sequence of three atoms and
			an angle that the three atoms should form.
		'dihedInfo' is like 'angleInfo', but 4 atoms.
		angleInfo/dihedInfo can be None if insufficient atoms
	"""

	if a1.molecule == a2.molecule:
		raise ValueError("Atoms to be bonded must be in different models")

	# first, get the distance correct
	from chimera import Xform, cross, angle, Point
	dvector = a1.xformCoord() - a2.xformCoord()
	dvector.length = dvector.length + length
	openState = a2.molecule.openState
	openState.globalXform(Xform.translation(dvector))

	# then angle
	if angleInfo:
		atoms, angleVal = angleInfo
		p1, p2, p3 = [a.xformCoord() for a in atoms]
		axis = cross(p1-p2, p2-p3)
		curAngle = angle(p1, p2, p3)
		delta = angleVal - curAngle
		v2 = p2 - Point(0.0, 0.0, 0.0)
		trans1 = Xform.translation(v2)
		v2.negate()
		trans2 = Xform.translation(v2)
		trans1.multiply(Xform.rotation(axis, delta))
		trans1.multiply(trans2)
		openState.globalXform(trans1)

def _newModel(name):
	m = chimera.Molecule()
	m.name = name
	chimera.openModels.add([m])
	return m

def _newResidue(model, name):
	# find an number unused in both the 'het' and 'water' chains...
	pos = 1
	while model.findResidue(chimera.MolResId('het', pos)) \
	or model.findResidue(chimera.MolResId('water', pos)):
		pos += 1
	return model.newResidue(name, 'het', pos, ' ')
