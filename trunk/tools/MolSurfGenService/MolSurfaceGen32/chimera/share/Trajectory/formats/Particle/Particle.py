# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2009 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: copyright 26655 2009-01-07 22:02:30Z gregc $

class ParticleTraj():
	def __init__(self, fileName, ncInfo):
		from chimera import UserError, Molecule, Element, openModels, replyobj
		from chimera import Coord, connectMolecule
		self.name = "Particle trajectory from %s" % fileName
		self.molecule = m = Molecule()
		self.isRealMolecule = False
		try:
			m.name = ncInfo.title
		except AttributeError:
			m.name = fileName
		tc = Element("Tc")
		coords = ncInfo.variables['coordinates']
		try:
			pnames = ncInfo.variables['particle_names']
		except KeyError:
			pnames = ["prt"] * len(coords)
		try:
			radii = ncInfo.variables['radii']
		except KeyError:
			radii = [1.0] * len(coords)
		try:
			mnames = ncInfo.variables['molecule_names']
			mnumbers = ncInfo.variables['molecule_numbers']
		except KeyError:
			mnames = ["PRT"]
			mnumbers = [1] * len(coords)
		serial = 1
		atoms = []
		residues = {}
		for name, radius, crd, mnumber in zip(
					pnames[:], radii[:], coords[0][:], mnumbers[:]):
			try:
				r = residues[mnumber]
			except KeyError:
				r = m.newResidue(string(mnames[mnumber-1]), " ", mnumber, " ")
			name = string(name)
			a = m.newAtom(name, tc)
			atoms.append(a)
			a.radius = radius
			r.addAtom(a)
			a.setCoord(Coord(*tuple(crd)))
			a.serialNumber = serial
			serial += 1
		try:
			connections = ncInfo.variables['connections']
		except KeyError:
			connections = []
		for i1, i2 in connections[:]:
			m.newBond(atoms[i1-1], atoms[i2-1])
		csNum = 1
		for crds in coords[1:]:
			cs = m.newCoordSet(csNum)
			for a, crd in zip(atoms, crds):
				a.setCoord(Coord(*tuple(crd)), cs)
			csNum += 1

	def __len__(self):
		return len(self.molecule.coordSets)

def string(name):
	if isinstance(name, basestring):
		return name
	return "".join(name).strip()
