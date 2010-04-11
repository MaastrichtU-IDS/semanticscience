# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: MMTKNetcdf.py 26655 2009-01-07 22:02:30Z gregc $

# much of this code is based on sample code provided by Walter Scott

import chimera
from chimera import replyobj
import os

class MMTKNetcdf:

	def __init__(self, netcdfPath, startFrame, endFrame):
		from MMTK.Trajectory import Trajectory
		replyobj.status("Reading NetCDF file\n", blankAfter=0)
		try:
			self.trajectory = Trajectory(None, netcdfPath)
		finally:
			replyobj.status("Done reading NetCDF file\n")

		replyobj.status("Processing trajectory\n", blankAfter=0)

		self.atomNames = []
		self.elements = []
		self.resNames = []
		self.atomIndices = {}
		self.bonds = []
		self.ipres = [1]

		from chimera import Element
		univ = self.trajectory.universe
		for i, a in enumerate(univ.atomList()):
			self.atomIndices[a] = i
			self.atomNames.append(a.name)
			self.elements.append(Element(a.getAtomProperty(a,
								"symbol")))
		for obj in univ:
			self._processObj(obj)
		delattr(self, "atomIndices")
		self.ipres.pop()
		
		self.startFrame = startFrame
		self.endFrame = endFrame

		self.name = os.path.basename(netcdfPath)

		replyobj.status("Done processing trajectory\n")

	def _processObj(self, obj):
		if not hasattr(obj, 'bonds'):
			subobjs = obj.bondedUnits()
			if subobjs == [obj]:
				if hasattr(obj, "atoms") and obj.atoms:
					raise ValueError("Don't know how to"
						" handle MMTK object %s"
						% str(obj))
				replyobj.warning("Skipping unknown MMTK object:"
					" %s\n" % str(obj))
				return
			for so in subobjs:
				self._processObj(so)
			return

		if hasattr(obj, 'residues'):
			residues = obj.residues()
			resNames = [r.name[:3] for r in residues]
		else:
			residues = [obj]
			resNames = ["UNK"]

		self.resNames.extend(resNames)
		self.bonds.extend([(self.atomIndices[b.a1],
				self.atomIndices[b.a2]) for b in obj.bonds])
		for res in residues:
			self.ipres.append(self.ipres[-1] + len(res.atoms))

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
		cnf =  self.trajectory[i-1]['configuration']
		cnf.scaleBy(10)
		return [a.position(cnf)
				for a in self.trajectory.universe.atomList()]

	def __len__(self):
		return len(self.trajectory)
