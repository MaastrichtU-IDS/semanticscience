# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29761 2010-01-13 01:06:30Z pett $

import sys

## "real" ensemble class implements the following: a "GetDict" method
## which handles "atomnames", "renames", "bonds" and "ipres" (residue
## to bond pointers)
## and a "LoadFrame" method which loads the Nth frame.

import chimera

class NoFrameError(ValueError):
	pass

class Ensemble:
    """ 
    Ensemble class
    """
    def __init__(self, ensemble):
        self._ensemble = ensemble
	if hasattr(ensemble, 'molecule'):
		self._mol = ensemble.molecule
	else:
		self._mol = chimera.Molecule()
		self._mol.name = ensemble.name

    def __getattr__(self, attrName):
	"""access as if a molecule model"""
	return getattr(self._mol, attrName)

    def AddMolecule(self, **kw):
	# needs to be here instead of CreateMolecule() because PDB trajectories
	# don't really use CreateMolecule()
	if getattr(self._ensemble, 'isRealMolecule', True):
		from chimera import makePseudoBondsToMetals, makeLongBondsDashed
		makePseudoBondsToMetals([self._mol])
		makeLongBondsDashed([self._mol])
	elif 'noPrefs' not in kw:
		kw['noprefs'] = True
	chimera.openModels.add([self._mol], **kw)

    def DeleteMolecule(self):
        chimera.openModels.close([self._mol])
        
    def Molecule(self):
	return self._mol

    def CreateMolecule(self):
	if hasattr(self._ensemble, "molecule"):
		return
        atomnames = map(str.strip, self._ensemble.GetDict('atomnames'))
        elements = self._ensemble.GetDict('elements')
        resnames = map(str.strip, self._ensemble.GetDict('resnames'))
        bonds = self._ensemble.GetDict('bonds')
        ipres = self._ensemble.GetDict('ipres')

        self.atomMap = [None] * len(atomnames)

        for rnum in range(len(resnames)):
            residue = resnames[rnum]
	    if residue in ["HOH", "WAT", "H2O", "D2O", "SOL"]:
	    	chain = "water"
	    else:
	    	chain = " "
            res = self._mol.newResidue(residue, chain, rnum+1, ' ')
            if rnum != len(resnames)-1:
                a1, a2 = ipres[rnum]-1, ipres[rnum+1]-1
            else:
                a1, a2 = ipres[rnum]-1, len(atomnames)

            for i in range(a1, a2):
                chimera_atom = self._mol.newAtom(atomnames[i], elements[i])
		chimera_atom.serialNumber = i+1
                self.atomMap[i] = chimera_atom
                res.addAtom(chimera_atom)

        for bond in bonds:
            a1, a2 = self.atomMap[bond[0]], self.atomMap[bond[1]]
            self._mol.newBond(a1, a2)

    def LoadFrame(self, frame, makeCurrent=True):
	cs = self._mol.findCoordSet(frame)
	if cs is not None:
		if makeCurrent:
			self._mol.activeCoordSet = cs
		return
        try:
		crds = self._ensemble[frame]
        except:
		if self._ensemble.endFrame == "pipe":
			raise NoFrameError("Couldn't read frame " + str(frame))
		else:
			raise

	numAtoms = len(self._ensemble.GetDict('atomnames'))
        cs = self._mol.newCoordSet(frame, numAtoms)
        coord = chimera.Coord()
	for i, a in enumerate(self.atomMap):
		if a.__destroyed__:
			continue
		coord.x, coord.y, coord.z = crds[i]
		a.setCoord(coord, cs)
        if makeCurrent:
	    self._mol.activeCoordSet = cs
	
	if len(self._mol.coordSets) == 1 and not self._mol.bonds:
		# if no connectivity, create on first coord set
		chimera.connectMolecule(self._mol)
        
def determineElementFromMass(mass, considerHydrogens=True):
	from chimera import Element
	H = Element('H')
	nearest = None
	for high in range(1, 93):
		if Element(high).mass > mass:
			break
	else:
		high = 93

	if considerHydrogens:
		maxHyds = 6
	else:
		maxHyds = 0
	for numHyds in range(maxHyds+1):
		adjMass = mass - numHyds * H.mass
		lowMass = Element(high-1).mass
		while lowMass > adjMass and high > 1:
			high -= 1
			lowMass = Element(high-1).mass
		highMass = Element(high).mass
		lowDiff = abs(adjMass - lowMass)
		highDiff = abs(adjMass - highMass)
		if lowDiff < highDiff:
			diff = lowDiff
			element = high - 1
		else:
			diff = highDiff
			element = high
		if nearest is None or diff < nearest[1]:
			nearest = (element, diff)
	return Element(nearest[0])

class MultiFileTrajectory:
	def __init__(self, addFunc):
		self.addFunc = addFunc
		self.trajs = []

	def addFile(self, trajFile):
		self.trajs.append(self.addFunc(trajFile))

	def __getitem__(self, i):
		# zero based
		for traj in self.trajs:
			if len(traj) > i:
				return traj[i]
			i -= len(traj)
		raise IndexError("No such frame")

	def __len__(self):
		return reduce(lambda x, y: x+y, [len(t) for t in self.trajs], 0)


