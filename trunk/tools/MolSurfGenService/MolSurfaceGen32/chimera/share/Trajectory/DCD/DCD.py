# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: DCD.py 26655 2009-01-07 22:02:30Z gregc $

# much of this code is based on sample code provided by Walter Scott

import chimera
from chimera import replyobj
import os

class DCD:

	def __init__(self, psfPath, dcdPath, startFrame, endFrame):
		from MDToolsMarch97 import md
		replyobj.status("Reading PSF file\n", blankAfter=0)
		try:
			mdtMol = md.Molecule(psf=psfPath)
		finally:
			replyobj.status("Done reading PSF file\n")
		replyobj.status("Processing PSF file\n", blankAfter=0)
		try:
			mdtMol.buildstructure()
		finally:
			replyobj.status("Processed PSF file\n")

		replyobj.status("Reading DCD header\n", blankAfter=0)
		try:
			self.dcd = md.DCD(dcdPath)
		finally:
			replyobj.status("Done reading DCD header\n")
		if self.dcd.numatoms != len(mdtMol.atoms):
			raise ValueError, "PSF has different number of atoms (%d) than DCD (%d)!" % (len(mdtMol.atoms), self.dcd.numatoms)
		self.startFrame = startFrame
		self.endFrame = endFrame

		self.name = os.path.basename(dcdPath)

		# atom names
		self.atomNames = map(lambda a: a.name, mdtMol.atoms)

		# elements
		from Trajectory import determineElementFromMass
		self.elements = map(lambda a: determineElementFromMass(a.mass),
								mdtMol.atoms)
		# residue names
		self.resNames = []
		for seg in mdtMol.segments:
			for res in seg.residues:
				self.resNames.append(res.name)

		# bonds
		atomIndices = {}
		for i, a in enumerate(mdtMol.atoms):
			atomIndices[a] = i
		self.bonds = map(lambda b: (atomIndices[b[0]],
					atomIndices[b[1]]), mdtMol.bonds)

		# residue composition
		self.ipres = []
		offset = 1
		for seg in mdtMol.segments:
			for res in seg.residues:
				self.ipres.append(offset)
				offset += len(res.atoms)

	def GetDict(self, key):
		if key == "atomnames":
			return self.atomNames
		if key == "elements":
			return self.elements
		if key == "resnames":
			return self.resNames
		if key == "bonds":
			return self.bonds
		if key == "ipres":
			return self.ipres
		raise KeyError, "Unknown GetDict() value: '%s'" % key

	def __getitem__(self, i):
		return self.dcd[i-1]

	def __len__(self):
		return len(self.dcd)
