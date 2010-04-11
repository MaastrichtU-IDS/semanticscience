# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Gromos.py 26655 2009-01-07 22:02:30Z gregc $

# much of this code is based on sample code provided by Walter Scott

import chimera
from chimera import replyobj

class Gromos:

	def __init__(self, topologyPath, coordinatesPath, promdPath,
					scaleFactor, startFrame, endFrame):
		scaleFactor = float(scaleFactor) # might be a string
		replyobj.status("Reading Gromos topology\n", blankAfter=0)
		try:
			self.topology = Gromos96Topology(topologyPath)
		finally:
			replyobj.status("Done reading Gromos topology\n")
		replyobj.status("Reading Gromos PROMD\n", blankAfter=0)
		try:
			self.promd = Gromos96Promd(promdPath)
		finally:
			replyobj.status("Done reading Gromos PROMD\n")
		replyobj.status("Reading Gromos coordinates\n", blankAfter=0)
		try:
			self.coordinates = Gromos96Coordinates(coordinatesPath,
						scaleFactor, self.promd.steps)
		finally:
			replyobj.status("Done reading Gromos coordinates\n")
		self.startFrame = startFrame
		self.endFrame = endFrame
		self.scaleFactor = scaleFactor

		self.name = self.topology.title[0].strip()

		soluteNames = []
		soluteTypes = []
		curResNum = None
		for i, aInfo in enumerate(self.topology.solute):
			topNum, resNum, name, aType, mass = aInfo
			soluteNames.append(name)
			soluteTypes.append((self.topology.atomTypeNames[aType],
									mass))
			if curResNum is None:
				curResNum = resNum
				resAtomStart = [1]
				continue
			if resNum != curResNum:
				curResNum += 1
				if resNum != curResNum:
					raise ValueError, \
						"Atoms not in residue order"
				resAtomStart.append(i+1)

		if len(resAtomStart) != len(self.topology.soluteResNames):
			raise ValueError, "Number of residues in atom list" \
				" (%d) not equal to number of named residues"\
				" (%d)" % (len(resAtomStart),
				len(self.topology.soluteResNames))

		solventNames = []
		solventTypes = []
		for aInfo in self.topology.solvent:
			topNum, name, aType, mass = aInfo
			solventNames.append(name)
			solventTypes.append((self.topology.atomTypeNames[aType],
									mass))
		# atom names
		self.atomNames = soluteNames * self.promd.NPM \
				+ solventNames * self.promd.NSM

		# elements
		solventElements = determineElements(solventTypes)
		self.elements = determineElements(soluteTypes) * self.promd.NPM\
					+ solventElements * self.promd.NSM

		# residue names
		solventResName = "SLV"
		if solventTypes and len(solventTypes) == 3:
			# possibly water
			if solventElements.count(O) == 1 \
			and solventElements.count(H) in [0,2]:
				solventResName = "HOH"
		self.resNames = self.topology.soluteResNames * self.promd.NPM +[
					solventResName] * self.promd.NSM

		# bonds
		self.bonds = []
		for n in range(self.promd.NPM):
			offset = n * len(self.topology.solute) - 1
			for a1, a2 in self.topology.soluteBonds:
				self.bonds.append((a1+offset, a2+offset))
		if len(self.topology.solvent) - solventElements.count(H) > 1:
			raise ValueError, \
				"Cannot determine connectivity of solvent"
		Hs = []
		for i, e in enumerate(solventElements):
			if e == H:
				Hs.append(i)
			else:
				heavy = i
		baseOffset = self.promd.NPM * len(self.topology.solute)
		for n in range(self.promd.NSM):
			offset = baseOffset + n * len(self.topology.solvent)
			for i in Hs:
				self.bonds.append((heavy+offset, i+offset))

		# residue composition
		self.ipres = []
		for i in range(0, self.promd.NPM):
			offset = i * len(self.topology.solute)
			for index in resAtomStart:
				self.ipres.append(offset + index)
		baseOffset = self.promd.NPM * len(self.topology.solute) + 1
		self.ipres.extend(list(range(baseOffset, baseOffset
				+ self.promd.NSM * len(self.topology.solvent),
				len(self.topology.solvent))))

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
		return self.coordinates[i-1]

	def __len__(self):
		return self.promd.steps
			
TITLE = 'TITLE\n'
END = 'END\n'

class Gromos96Topology:
	"""store the topology information needed for visualisation"""
	def __init__(self, fname):
		sf = SkipCommentsFile(fname)

		# read the topology title
		sf.skipUntil(TITLE)
		self.title = sf.readUntil(END)

		# read the atom type names
		sf.skipUntil('ATOMTYPENAME\n')
		self.atomTypeNames = map(lambda at: at.strip(),
							sf.readUntil(END))

		# read the residue names
		sf.skipUntil('RESNAME\n')
		self.soluteResNames = map(lambda rn: rn.strip(),
							sf.readUntil(END))[1:]

		# read the solute atom information
		sf.skipUntil('SOLUTEATOM\n')
		self.solute = self.readSolute(sf.readUntil(END))
		
		# read bond info
		sf.skipUntil('BONDH\n')
		bndh = self.readBonds(sf.readUntil(END))
		sf.skipUntil('BOND\n' )
		bnd = self.readBonds(sf.readUntil(END))
		self.soluteBonds = bndh + bnd

		# read solvent atom information
		sf.skipUntil('SOLVENTATOM\n')
		self.solvent = self.readSolvent(sf.readUntil(END))

	def readBonds(self, lines):
		nb = int(lines[0]);
		bonds = []
		for line in lines[1:]:
			cols = map(int, line.split())
			bonds.append((cols[0], cols[1]))
		if len(bonds) != nb:
			raise ValueError, "Number of bonds (%d) not " \
				"equal to NB (%d)" % (len(bonds), nb)
		return bonds;

	def readSolute(self, lines):
		self.NRP = int(lines[0])
		i = 1
		n = len(lines)
		atoms = []
		while i < n:
			# the begining of an atom line
			cols = lines[i].split()
			i += 1
			# columns:
			# atom sequence number
			# residue number
			# atom name
			# atom type (int)
			# mass
			# charge
			# charge group code (boolean)
			# number of exclusions (?)
			num, resnum, name, iac, mass, ine = (int(cols[0]),
					int(cols[1]), cols[2], int(cols[3]),
					float(cols[4]), int(cols[7]))
			atoms.append((num, resnum, name, iac, mass))
			# we are not interested in actually reading the
			# exclusion or 1-4 interaction lists. Just skip them.
			# The exclusion list may extend to following lines...
			ineGot = len(cols) - 8
			while (ineGot < ine):
				ineGot += len(lines[i].split())
				i += 1;
			# now 1-4 interactions
			cols = lines[i].split()
			i += 1
			ine14 = int(cols[0])
			ine14got = len(cols)-1
			while(ine14got < ine14):
				ine14got += len(lines[i].split())
				i += 1
		if len(atoms) != self.NRP:
			raise ValueError, "Number of solute atoms (%d) not " \
				"equal to NRP (%d)" % (len(atoms), self.NRP)
		return atoms

	def readSolvent(self, lines):
		self.NRAM = int(lines[0])
		atoms = []
		for line in lines[1:]:
			cols = line.split()
			num, name, iacs, mass = (int(cols[0]), cols[1],
					int(cols[2]), float(cols[3]))
			atoms.append((num, name, iacs, mass))
		if self.NRAM != len(atoms):
			raise ValueError, "Number of solvent atoms (%d) not " \
				"equal to NRAM (%d)" % (len(atoms), self.NRAM)

		return atoms

class Gromos96Promd:
	def __init__(self, fname):
		sf = SkipCommentsFile(fname)

		# read the topology title
		sf.skipUntil(TITLE)
		self.title = sf.readUntil(END)

		# system block
		sf.skipUntil('SYSTEM\n')
		lst = map(int, sf.gimmeLine().split())
		self.NPM, self.NSM = lst[0], lst[1]
		print "system is ",lst

		# step block
		sf.skipUntil("STEP\n")
		computedSteps = int(sf.gimmeLine().split()[0])

		# boundary block
		sf.skipUntil('BOUNDARY\n')
		lst = sf.gimmeLine().split()
		self.NTB, self.BOXX, self.BOXY, self.BOXZ = (int(lst[0]),
				float(lst[1]), float(lst[2]), float(lst[3]))
		self.BETA, self.NRDBOX = float(lst[4]), int(lst[5])
		print "boundary is",lst

		sf.skipUntil('WRITE\n')
		self.steps = computedSteps/abs(int(sf.gimmeLine().split()[0]))
		print "#steps is", self.steps

class Gromos96Coordinates:
	"read in a formatted file containing coordinates"
	def __init__(self, fname, scaleFactor, steps):
		self.sf = SkipCommentsFile(fname)
		self.scaleFactor = scaleFactor
		self.positions = [None] * steps
		self.nextPos = 0

		return
		# the way I used to read this file follows...

		sf = SkipCommentsFile(fname)

		# read the trajectory title
		try:
			sf.skipUntil(TITLE)
			self.title = sf.readUntil(END)
		except IOError:
			# no TITLE section
			import os.path
			sf.rewind()
			self.title = os.path.split(fname)[-1]

		self.info = info = {}
		line = sf.gimmeLine()
		while line:
			if (line =='POSITION\n'):
				info.setdefault('positions', []).append(
					[map(lambda c: scaleFactor * float(c),
					l[24:].split()) for l in
					sf.readUntil(END)])
			elif (line=='POSITIONRED\n'):
				info.setdefault('positions', []).append(
					[map(lambda c: scaleFactor * float(c),
					l.split()) for l in sf.readUntil(END)])
			elif (line=='BOX\n'):
				info.setdefault('boxes', []).append(
					[map(lambda b: scaleFactor * float(b),
					l.split()) for l in sf.readUntil(END)])
			elif (line=='TIMESTEP\n'):
				ll = sf.readUntil(END)
				ll = ll[0].split()
				info.setdefault('timesteps', []).append(
						[int(ll[0]), float(ll[1])])
			else:
				sf.skipUntil(END)
			line = sf.gimmeLine()
		if 'positions' in info:
			print len(info['positions']), "coordinate positions, each of length", len(info['positions'][0])
		if 'positions' not in info:
			raise ValueError, "No coordinates in coordinate file!"
		if 'boxes' in info:
			print len(info['boxes']), "boxes"
		else:
			print "no box info in file"
		if 'timesteps' in info:
			print len(info['timesteps']), "timesteps"
		else:
			print "no timestep info in file"

	def __getitem__(self, i):
		pos = self.positions[i]
		if pos is None:
			sf = self.sf
			scaleFactor = self.scaleFactor
			while self.nextPos <= i:
				line = sf.gimmeLine()
				while line:
					if (line =='POSITION\n'):
						pos = [map(lambda c:
							scaleFactor * float(c),
							l[24:].split()) for l in
							sf.readUntil(END)]
						break
					elif (line=='POSITIONRED\n'):
						pos = [map(lambda c:
							scaleFactor * float(c),
							l.split()) for l in
							sf.readUntil(END)]
						break
					line = sf.gimmeLine()
				if not line:
					raise ValueError("Missing coordinates"
						" for frame %d" % (i+1))
				self.positions[self.nextPos] = pos
				self.nextPos += 1
		return pos

class SkipCommentsFile:
	"""File that skips over comments automatically"""
	def __init__(self, fname):
		self.f = open(fname,'r')

	def gimmeLine(self):
		rdline = self.f.readline
		line = rdline()
		while (line and line[0]=='#'):
			line = rdline()
		return line

	def skipUntil(self, marker):
		"""skip lines until we encounter the markerstring"""
		gl = self.gimmeLine
		line = gl()
		while line != marker:
			line = gl()
			if not line:
				raise IOError, "EOF while skipping to marker"\
					" '%s'"% marker

	def readUntil(self, marker):
		"""return a list of lines read from where we are in the file
		   until we reach the markerstring. That line is discarded."""
		gl = self.gimmeLine
		line = gl()
		retList = []
		while line != marker:
			retList.append(line)
			line = gl()
			if not line:
				raise IOError, "EOF while reading to marker"\
					" '%s'"% marker
		return retList

	def rewind(self):
		self.f.seek(0)

from chimera import Element
O = Element('O')
N = Element('N')
C = Element('C')
H = Element('H')
S = Element('S')
Cu = Element('Cu')
Fe = Element('Fe')
Zn = Element('Zn')
Mg = Element('Mg')
Ca = Element('Ca')
Ar = Element('Ar')
F = Element('F')
Cl = Element('Cl')
Br = Element('Br')
Na = Element('Na')
Si = Element('Si')
AtomTypeToElement = {
	'O': O, 	'OM': O, 	'OA': O, 	'OW': O,
	'N': N,		'NT': N,	'NL': N,	'NR': N,
	'NZ': N,	'NE': N,	'C': C,		'CH1': C,
	'CH2': C,	'CH3': C,	'CH4': C,	'CR1': C,
	'HC': H,	'H': H,		'S': S,		'CU1+': Cu,
	'CU2+': Cu,	'FE': Fe,	'ZN2+': Zn,	'MG2+': Mg,
	'CA2+': Ca,	'AR': Ar,	'F': F,		'CL': Cl,
	'BR': Br,	'CMET': C,	'OMET': O,	'NA+': Na,
	'CL-': Cl,	'CCHL': C,	'CLCHL': Cl,	'HCHL': H,
	'SDMSO': S,	'CDMSO': C,	'ODMSO': O,	'CCL4': C,
	'CLCL4': Cl
}

def determineElements(typeInfo):
	elements = []
	for at, mass in typeInfo:
		if at in AtomTypeToElement:
			elements.append(AtomTypeToElement[at])
			continue
		from Trajectory import determineElementFromMass
		elements.append(determineElementFromMass(mass))
		print "Estimating atom type '%s' with mass %g to be %s" % (
			at, mass, elements[-1].name)
		if at != "P,SI":
			AtomTypeToElement[at] = elements[-1]

	return elements
