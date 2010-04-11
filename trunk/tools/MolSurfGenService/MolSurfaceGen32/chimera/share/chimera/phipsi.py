class AtomsMissingError(ValueError):
	pass

def getPhi(res):
	try:
		prevC, n, ca, c = phiAtoms(res)
	except AtomsMissingError:
		return None
	from chimera import dihedral
	return dihedral(prevC.coord(), n.coord(), ca.coord(), c.coord())

def getPsi(res):
	try:
		n, ca, c, nextN = psiAtoms(res)
	except AtomsMissingError:
		return None
	from chimera import dihedral
	return dihedral(n.coord(), ca.coord(), c.coord(), nextN.coord())

def getChi1(res):
	return getChi(res, 1)

def getChi2(res):
	return getChi(res, 2)

def getChi3(res):
	return getChi(res, 3)

def getChi4(res):
	return getChi(res, 4)

def getChi(res, chiNum):
	try:
		atoms = chiAtoms(res, chiNum)
	except AtomsMissingError:
		return None
	from chimera import dihedral
	return dihedral(*tuple([a.coord() for a in atoms]))

def phiAtoms(res):
	try:
		n = res.atomsMap['N'][0]
		ca = res.atomsMap['CA'][0]
		c = res.atomsMap['C'][0]
	except KeyError:
		raise AtomsMissingError("Missing backbone atom")
	for nb in n.neighbors:
		if nb.residue == res:
			continue
		if nb.name == 'C':
			prevC = nb
			break
	else:
		raise AtomsMissingError("No C in previous residue")
	return prevC, n, ca, c

def psiAtoms(res):
	try:
		n = res.atomsMap['N'][0]
		ca = res.atomsMap['CA'][0]
		c = res.atomsMap['C'][0]
	except KeyError:
		raise AtomsMissingError("Missing backbone atom")
	for nb in c.neighbors:
		if nb.residue == res:
			continue
		if nb.name == 'N':
			nextN = nb
			break
	else:
		raise AtomsMissingError("No N in next residue")
	return n, ca, c, nextN

def chiAtoms(res, chiNum):
	from Rotamers.data import chiInfo
	from resCode import protein3to1, protein1to3
	try:
		# 'standardize' modified residue types registered
		# through MODRES records
		resType = protein1to3[protein3to1[res.type]]
		atomNames = chiInfo[resType][chiNum-1]
		atoms = [res.atomsMap[an][0] for an in atomNames]
	except (KeyError, IndexError):
		raise AtomsMissingError("Missing backbone atom")
	return atoms

def setPhi(res, phi):
	try:
		n, ca = res.atomsMap['N'][0], res.atomsMap['CA'][0]
		bond = n.bondsMap[ca]
		_setAngle(bond, phi, getPhi(res))
	except (KeyError, AtomsMissingError):
		# to allow inspectors to work
		return

def setPsi(res, psi):
	try:
		ca, c = res.atomsMap['CA'][0], res.atomsMap['C'][0]
		bond = ca.bondsMap[c]
		_setAngle(bond, psi, getPsi(res))
	except (KeyError, AtomsMissingError):
		# to allow inspectors to work
		return

def setChi1(res, chi):
	setChi(res, chi, 1)

def setChi2(res, chi):
	setChi(res, chi, 2)

def setChi3(res, chi):
	setChi(res, chi, 3)

def setChi4(res, chi):
	setChi(res, chi, 4)

def setChi(res, chi, chiNum):
	try:
		a1, a2, a3, a4 = chiAtoms(res, chiNum)
		bond = a2.bondsMap[a3]
		_setAngle(bond, chi, getChi(res, chiNum))
	except (KeyError, AtomsMissingError):
		# to allow inspectors to work
		return

def _setAngle(bond, newAngle, curAngle):
	from BondRotMgr import bondRotMgr
	br = bondRotMgr.rotationForBond(bond, create=False)
	if br:
		br.increment(newAngle - curAngle)
	else:
		from chimera import BondRot
		br = BondRot(bond)
		br.angle = (newAngle - curAngle, br.biggerSide())
		br.destroy()
	res = bond.atoms[0].residue
	from chimera import TrackChanges
	track = TrackChanges.get()
	track.addModified(res, "attribute set")
