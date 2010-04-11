# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Gromacs.py 26931 2009-02-18 01:49:08Z pett $

import os
import sys
import chimera
from chimera import elements, replyobj

class Gromacs:
	def __init__(self, topology, trajectory, startFrame, endFrame):
		self.elements = None
		self.name = os.path.basename(trajectory)
		from chimera import replyobj
		replyobj.status("Reading Gromacs topology\n", blankAfter=0)
		try:
			#self.topology = TopTopology(topology)
			self.topology = TprTopology(topology)
		finally:
			replyobj.status("Done reading Gromacs topology\n")
		replyobj.status("Reading Gromacs trajectory", blankAfter=0)
		try:
			self.trajectory = Trajectory(self.topology, trajectory)
		finally:
			replyobj.status("Done reading Gromacs trajectory\n")
		self.startFrame = startFrame
		self.endFrame = endFrame

	def GetDict(self, i):
		if i == "numatoms":
			return len(self.topology.atomNames)
		if i == "atomnames":
			return self.topology.atomNames
		if i == "resnames":
			return self.topology.resNames
		if i == "ipres":
			return self.topology.resIndices
		if i == "bonds":
			return self.topology.bonds
		if i == "elements":
			return self.topology.elements
		raise KeyError, "Can't GetDict() for '%s'" % i

## Wrapped access to trajectory data
	def __getitem__(self, i):
		return self.trajectory[i-1]

	def __len__(self):
		return len(self.trajectory)

class TprTopology:
	funcNames = [
		"bonds", "g96bonds", "morse", "cubicbonds", "connbonds",
		"harmonic", "fenebonds", "tabbonds", "tabbondsnc",
		"angles", "g96angles", "cross_bond_bond",
		"cross_bond_angle", "urey_bradley", "qangles",
		"tabangles", "pdihs", "rbdihs", "fourdihs", "idihs",
		"pidihs", "tabdihs", "lj14", "coul14", "ljc14_q",
		"ljc_nb", "lj_sr", "bham", "lj_lr", "bham_lr",
		"dispcorr", "coul_sr", "coul_lr", "rf_excl",
		"coul_recip", "dpd", "polarization", "waterpol",
		"thole", "posres", "disres", "drviol", "orires",
		"ordev", "angres", "angresz", "dihres", "dihviol",
		"constr", "constrnc", "settle", "vsite2", "vsite3",
		"vsite3fd", "vsite3fad", "vsite3out", "vsite4fd",
		"vsite4fdn", "vsiten", "com_pull", "eqm", "epot",
		"ekin", "etot", "econs", "temp", "pres", "dv/dl",
		"dk/dl", "dg/dl_con"
	]
	def __init__(self, topology):
		from OpenSave import osOpen
		topFile = osOpen(topology, 'rb')
		import os
		self.topFileSize = os.stat(topology).st_size
		from xdrlib import Unpacker
		self.fileString = FileString(topFile, 0, self.topFileSize)
		self.xdr = Unpacker(self.fileString)
		version = self._readHeader()
		self._readTopology(version)

	def _do_block(self, version):
		if version < 44:
			for i in range(256):
				self.xdr.unpack_uint()
		blockNR = self.xdr.unpack_uint()
		if version < 51:
			blockNRA = self.xdr.unpack_uint()
		for i in range(blockNR + 1):
			self.xdr.unpack_uint()
		if version < 51:
			for i in range(blockNRA):
				self.xdr.unpack_uint()

	def _do_blocka(self, version):
		if version < 44:
			for i in range(256):
				self.xdr.unpack_uint()
		blockNR = self.xdr.unpack_uint()
		blockNRA = self.xdr.unpack_uint()
		for i in range(blockNR + blockNRA + 1):
			self.xdr.unpack_uint()

	def _do_ffparams(self, version):
		self.funcNumber = {}
		for i, fn in enumerate(self.funcNames):
			self.funcNumber[fn] = i
		self.funcNumberUpdate = [
			(20, "cubicbonds"), (20, "connbonds"), (20, "harmonic"),
			(34, "fenebonds"), (43, "tabbonds"),
			(43, "tabbondsnc"), (30, "cross_bond_bond"),
			(30, "cross_bond_angle"), (30, "urey_bradley"),
			(34, "qangles"), (43, "tabangles"),
			(26, "fourdihs"), (26, "pdihs"), (43, "tabdihs"),
			(41, "ljc14_q"), (41, "ljc_nb"),
			(32, "bham_lr"), (32, "rf_excl"), (32, "coul_recip"),
			(46, "dpd"), (30, "polarization"), (36, "thole"),
			(22, "drviol"), (22, "orires"), (22, "ordev"),
			(26, "dihres"), (26, "dihviol"),
			(49, "vsite4fdn"), (50, "vsiten"), (46, "com_pull"),
			(20, "eqm"), (46, "econs"), (54, "dg/dl_con")
		]
		self.xdr.unpack_uint()
		if version < 57:
			self.xdr.unpack_uint()
		ntypes = self.xdr.unpack_uint()

		functions = []
		for i in range(ntypes):
			fnum = self.xdr.unpack_uint()
			for vn, funcName in self.funcNumberUpdate:
				if version < vn \
				and fnum >= self.funcNumber[funcName]:
					fnum += 1
			funcName = self.funcNames[fnum]
			functions.append(funcName)
		if version >= 57:
			self.unpackFloatFunc()
		for i, funcName in enumerate(functions):
			if funcName in ["angles", "g96angles", "bonds",
					"g96bonds", "harmonic", "idihs",
					"cross_bond_angle", "urey_bradley",
					"thole", "lj14", "ljc_nb"]:
				floatInts = "rrrr"
			elif funcName in ["fenebonds", "lj_sr", "constr",
					"constrnc", "settle", "vsite3",
					"vsite3fd", "vsite3fad"]:
				floatInts = "rr"
			elif funcName in ["cross_bond_bond", "bham", "morse",
					"cubic_bonds", "vsite3out", "vsite4fd",
					"vsite4fdn"]:
				floatInts = "rrr"
			elif funcName in ["qangles", "waterpol"]:
				floatInts = "rrrrrr"
			elif funcName in ["connbonds"]:
				floatInts = ""
			elif funcName in ["polarization", "vsite2"]:
				floatInts = "r"
			elif funcName in ["pdihs", "pidihs"]:
				floatInts = "rrrri"
			elif funcName in ["disres"]:
				floatInts = "iirrrr"
			elif funcName in ["orires"]:
				floatInts = "iiirrr"
			elif funcName in ["dihres"]:
				floatInts = "iirrr"
			elif funcName in ["posres"]:
				if version < 27:
					floatInts = "rrrrrr"
				else:
					floatInts = "rrrrrrrrrrrr"
			elif funcName in ["rbdihs"]:
				if version >= 25:
					floatInts = "rrrrrrrrrrrr"
				else:
					floatInts = "rrrrrr"
			elif funcName in ["fourdihs"]:
				floatInts = "rrrrrrrrrrrr"
			elif funcName in ["tabbonds", "tabbondsnc", "tabangles",
					"tabdihs"]:
				floatInts = "rir"
			elif funcName in ["ljc14_q"]:
				floatInts = "rrrrr"
			elif funcName in ["angres", "angresz"]:
				if version < 42:
					floatInts = "rrrr"
				else:
					floatInts = "rrrri"
			elif funcName in ["vsiten"]:
				floatInts = "ir"
			else:
				raise ValueError("Don't know correct"
						" parameters for '%s' function"
						% funcName)
			for fi in floatInts:
				if fi == 'r':
					t = self.unpackFloatFunc()
				else:
					t = self.xdr.unpack_uint()

	def _do_ilists(self, version):
		# bonds is first func, at least
		seen = set()
		self.bonds = []
		checklist = set()
		def addBond(a1, a2):
			if (a1, a2) in checklist:
				return
			self.bonds.append((a1, a2))
			checklist.add((a1, a2))
			checklist.add((a2, a1))
			seen.add(a1)
			seen.add(a2)
		for fname in self.funcNames:
			for uv, uname in self.funcNumberUpdate:
				if version < uv and fname == uname:
					skip = True
					break
			else:
				skip = False
			if skip:
				continue
			if version < 44:
				for i in range(256):
					self.xdr.unpack_uint()
			nr = self.xdr.unpack_uint()
			if fname == "bonds":
				for i in range(nr/3):
					self.xdr.unpack_uint()
					a1index = self.xdr.unpack_uint()
					a2index = self.xdr.unpack_uint()
					addBond(a1index, a2index)
			elif fname in ["angles", "g96angles"]:
				for i in range(nr/4):
					self.xdr.unpack_uint()
					a1index = self.xdr.unpack_uint()
					a2index = self.xdr.unpack_uint()
					a3index = self.xdr.unpack_uint()
					addBond(a1index, a2index)
					addBond(a2index, a3index)
			else:
				for i in range(nr):
					self.xdr.unpack_uint()
		# okay, the above doesn't hook up water (and maybe methane?)...
		hyds = {}
		heavys = {}
		for i, element in enumerate(self.elements):
			if i in seen:
				continue
			key = self.resNums[i]
			if element.number == 1:
				hyds.setdefault(key, []).append(i)
			else:
				heavys.setdefault(key, []).append(i)
		for i, heavysList in heavys.items():
			if len(heavysList) != 1 or i not in hyds:
				# beats me what to do
				continue
			heavy = heavysList[0]
			for hyd in hyds[i]:
				self.bonds.append((heavy, hyd))
		self.molInfo.append((self.atomNames, self.resNames,
				self.resIndices, self.bonds, self.elements))
		
	def _readHeader(self):
		# version string
		replyobj.info("%s\n" % self._readString())
		realSize = self.xdr.unpack_uint()
		if realSize == 4:
			self.unpackFloatFunc = self.xdr.unpack_float
			replyobj.info("using floats\n")
		elif realSize == 8:
			self.unpackFloatFunc = self.xdr.unpack_double
			replyobj.info("using doubles\n")
		else:
			raise ValueError("Floating-point values in .tpr file"
				" are not the same as either single-precision"
				" or double-precision floating point on this"
				" machine")
		version = self.xdr.unpack_uint()
		if version >= 26:
			generation = self.xdr.unpack_uint()
		else:
			generation = 0
		replyobj.info("version %d, generation %d\n"
						% (version, generation))
		natoms = self.xdr.unpack_uint()
		replyobj.info("%d atoms\n" % natoms)
		if version >= 28:
			tempCouplingGroups = self.xdr.unpack_uint()
		curStep = self.xdr.unpack_uint()
		curTime = self.unpackFloatFunc()
		curLambda = self.unpackFloatFunc()
		hasInputRec = self.xdr.unpack_uint()
		hasTopology = self.xdr.unpack_uint()
		if not hasTopology:
			raise ValueError(
				".tpr file does not have topology section")

		hasCoord = self.xdr.unpack_uint()
		hasVelocities = self.xdr.unpack_uint()
		hasForces = self.xdr.unpack_uint()
		hasBbox = self.xdr.unpack_uint()

		if hasBbox:
			for i in range(9):
				self.unpackFloatFunc()
			if version >= 51:
				for i in range(9):
					self.unpackFloatFunc()
			if version >= 28:
				for i in range(9):
					self.unpackFloatFunc()
				if version < 56:
					for i in range(9):
						self.unpackFloatFunc()

		if version >= 28 and tempCouplingGroups > 0:
			for i in range(tempCouplingGroups):
				self.unpackFloatFunc()
				self.unpackFloatFunc()

		if version < 26 and hasInputRec:
			raise ValueError("Cannot read version 26 or earlier"
				" .tpr files")

		return version

	def _readString(self):
		strlen = self.xdr.unpack_uint()
		self.xdr.unpack_uint()
		return self.xdr.unpack_fstring(strlen-1)

	def _readTopology(self, version):
		self.molInfo = []
		numStrings = self.xdr.unpack_uint()
		symbols = []
		for i in range(numStrings):
			symbols.append(self._readString())
		name = symbols[self.xdr.unpack_uint()]
		replyobj.info("%s\n" % name)

		if version >= 57:
			self._do_ffparams(version)
			numMolTypes = self.xdr.unpack_uint()
		else:
			numMolTypes = 1

		from Trajectory import determineElementFromMass
		for i in range(numMolTypes):
			if version >= 57:
				molName = symbols[self.xdr.unpack_uint()]
				replyobj.info("mol name: %s\n" % molName)
				

			numAtoms = self.xdr.unpack_uint()
			replyobj.info("%d atoms\n" % numAtoms)
			numResidues = self.xdr.unpack_uint()
			replyobj.info("%d residues\n" % numResidues)
			if version < 57:
				numGroupNames = self.xdr.unpack_uint()
				if version < 23:
					numGroups = 8
				elif version < 39:
					numGroups = 9
				else:
					numGroups = 10
			self.elements = []
			self.resNums = []
			for i in range(numAtoms):
				mass = self.unpackFloatFunc()
				self.elements.append(
						determineElementFromMass(mass))
				charge = self.unpackFloatFunc()
				self.unpackFloatFunc()
				self.unpackFloatFunc()
				for j in range(3):
					self.xdr.unpack_uint()
				resNum = self.xdr.unpack_uint()
				self.resNums.append(resNum)
				if version >= 52:
					self.xdr.unpack_uint()
				if version < 57:
					for j in range(numGroups):
						self.xdr.unpack_uint()
			self.atomNames = [symbols[self.xdr.unpack_uint()]
						for i in range(numAtoms)]
			for i in range(numAtoms*2):
				self.xdr.unpack_uint()
			self.resNames = [symbols[self.xdr.unpack_uint()]
						for i in range(numResidues)]
			self.resIndices = []
			curResNum = None
			for i, rn in enumerate(self.resNums):
				if curResNum != rn:
					self.resIndices.append(i+1)
					curResNum = rn
			
			if version < 57:
				# group names
				for i in range(numGroupNames):
					gn = symbols[self.xdr.unpack_uint()]

				# group contents
				for i in range(numGroups):
					grpN = self.xdr.unpack_uint()
					for j in range(grpN):
						self.xdr.unpack_uint()

			if version >= 57:
				self._do_ilists(version)
				self._do_block(version)

			self._do_blocka(version)

		if version >= 57:
			self.atomNames = []
			self.resNames = []
			self.resIndices = []
			self.bonds = []
			self.elements = []
		
			numMolBlocks = self.xdr.unpack_uint()
			for i in range(numMolBlocks):
				self.xdr.unpack_uint()
				repeat = self.xdr.unpack_uint()
				self.xdr.unpack_uint()
				# position restraints
				for j in range(2):
					npr = self.xdr.unpack_uint()
					for k in range(npr):
						self.unpackFloatFunc()
						self.unpackFloatFunc()
						self.unpackFloatFunc()
				atomNames, resNames, resIndices, bonds, \
						elements = self.molInfo[i]
				for j in range(repeat):
					aBase = len(self.atomNames)
					self.atomNames.extend(atomNames)
					self.resNames.extend(resNames)
					for ri in resIndices:
						self.resIndices.append(
								aBase + ri)
					for a1, a2 in bonds:
						self.bonds.append((aBase + a1,
								aBase + a2))
					self.elements.extend(elements)
		
			self.xdr.unpack_uint()

		# atom types
		if version > 25:
			nr = self.xdr.unpack_uint()
			# radii
			for i in range(nr):
				self.unpackFloatFunc()
			# volume
			for i in range(nr):
				self.unpackFloatFunc()
			# surface tension
			for i in range(nr):
				self.unpackFloatFunc()
			if version >= 40:
				# atom number
				for i in range(nr):
					self.xdr.unpack_uint()

		if version < 57:
			self._do_ffparams(version)
			if version >= 54:
				self.unpackFloatFunc()
			self._do_ilists(version)

class TopTopology:
	def __init__(self, topology):
		from OpenSave import osOpen
		self.atomNames = []
		self.resNames = []
		self.resIndices = []
		self.bonds = []
		self.elements = []
		self.molInfo = {}

		topFile = osOpen(topology)
		while self._readLine(topFile):
			pass
		topFile.close()

	def _readLine(self, topFile):
		# skip comments/includes/blank lines and handle continuations
		finalLine = ""
		line = topFile.readline()
		while line:
			line = line.strip()
			if line and line[-1] == '\\':
				finalLine = " ".join([finalLine,
							line[:-1]]).strip()
			else:
				finalLine = " ".join([finalLine, line]).strip()
				if not finalLine or finalLine[0] in ';#':
					finalLine = ""
				else:
					break
			line = topFile.readline()
		if finalLine:
			if finalLine[0] == '[' and finalLine[-1] == ']':
				methodName = "_process%s" % (
					finalLine[1:-1].strip().capitalize())
				if hasattr(self, methodName):
					return eval("self.%s(topFile)" % (
								methodName))
				else:
					# skip section
					while self._readLine(topFile):
						pass
			else:
				return finalLine
		return False

	def _processAtoms(self, topFile):
		from Trajectory import determineElementFromMass
		curMoleculeType = self.curMoleculeType
		atoms = []
		atomMap = {}
		resNames = []
		resMap = {}
		self.molInfo[self.curMoleculeType] = [atoms, atomMap,
							resNames, resMap]
		line = self._readLine(topFile)
		while line:
			fields = line.split()
			try:
				atomNum = int(fields[0])
				resNum = int(fields[2])
				resName = fields[3]
				atomName = fields[4]
				mass = float(fields[7])
			except ValueError:
				raise ValueError("Bad line in 'atoms' section"
					" of topology file: %s" % line)
			atomMap[atomNum] = len(atoms)
			atoms.append((atomName,
				determineElementFromMass(mass), resNum))
			if resNum not in resMap:
				resMap[resNum] = len(resNames)
				resNames.append(resName)
			line = self._readLine(topFile)
		return False

	def _processBonds(self, topFile):
		bonds = []
		self.molInfo[self.curMoleculeType].append(bonds)
		line = self._readLine(topFile)
		while line:
			try:
				bonds.append([int(an)
						for an in line.split()[:2]])
			except ValueError:
				raise ValueError("Bad line in 'bonds' section"
					" of topology file: %s" % line)
			line = self._readLine(topFile)
		return False

	def _processMolecules(self, topFile):
		molInfo = {
			'SOL': [
				# atoms
				[('OW', chimera.Element('O'), 1),
				('HW1', chimera.Element('H'), 1),
				('HW2', chimera.Element('H'), 1)],

				# atom map
				{ 0:0, 1:1, 2:2},

				# res names
				['SOL'],

				# res map
				{ 1:0 },

				# bonds
				[ [0, 1], [0, 2] ]
			]
		}
		molInfo.update(self.molInfo)
		curRes = None
		line = self._readLine(topFile)
		while line:
			molType, num = line.split()
			num = int(num)
			try:
				atoms, atomMap, resNames, resMap, bonds = \
							molInfo[molType]
			except KeyError:
				raise ValueError("Unknown molecule type: %s"
								% molType)
			for i in range(num):
				resBase = len(self.resNames)
				atomBase = len(self.atomNames)
				self.resNames.extend(resNames)
				for atomName, element, resLookup in atoms:
					self.atomNames.append(atomName)
					resIndex = resBase + resMap[resLookup]
					if resIndex != curRes:
						self.resIndices.append(
							len(self.atomNames))
						curRes = resIndex
					self.elements.append(element)
				for a1, a2 in bonds:
					i1, i2 = atomMap[a1], atomMap[a2]
					self.bonds.append(
						(atomBase+i1, atomBase+i2))
			line = self._readLine(topFile)
		return False

	def _processMoleculetype(self, topFile):
		self.curMoleculeType = self._readLine(topFile).split()[0]
		return True

	def _processSystem(self, topFile):
		self.name = self._readLine(topFile)
		return True

class Trajectory:
	def __init__(self, topology, trajFileName):
		# since we need to be able to do seeks, can't use osOpen
		# which might return an unseekable stream
		self.topology = topology
		from OpenSave import osUncompressedPath
		path = osUncompressedPath(trajFileName)
		import os
		self.trajFileSize = os.stat(path).st_size
		self.traj = open(path, "rb")
		from xdrlib import Unpacker
		self.fileString = FileString(self.traj, 0, self.trajFileSize)
		self.xdr = Unpacker(self.fileString)
		self.crdStarts = []
		while True:
			replyobj.status("Reading frame %d header\n" % (
						len(self.crdStarts) + 1))
			try:
				crdStart, endFrame = self._readHeader()
			except ValueError, e:
				raise ValueError("Frame %d: %s" %
					(len(self.crdStarts) + 1, str(e)))
			if endFrame > self.trajFileSize:
				if not self.crdStarts:
					raise ValueError("Computed size of"
						" first frame (%d) greater than"
						" trajectory file size (%s)" %
						(endFrame, self.trajFileSize))
				replyobj.warning("Truncated trajectory file;"
					" skipping last partial frame.\n")
			else:
				self.crdStarts.append(crdStart)
			if endFrame == self.trajFileSize:
				break
			self.xdr.set_position(endFrame)

	def _readHeader(self):
		xdr = self.xdr
		if xdr.unpack_int() != 1993:
			raise ValueError("Bad magic number in trajectory file")
		strlen = xdr.unpack_uint()
		xdr.unpack_uint()
		# version string
		xdr.unpack_fstring(strlen-1)
		precoordSize = 0
		# ir_size
		# e_size
		# box_size
		# vir_size
		# pres_size
		# top_size
		# sym_size
		for i in range(7):
			precoordSize += xdr.unpack_uint()
		# x_size
		x_size = xdr.unpack_uint()
		frameSize = precoordSize + x_size
		# v_size
		# f_size
		for i in range(2):
			frameSize += xdr.unpack_uint()
		natoms = xdr.unpack_uint()
		if natoms != len(self.topology.atomNames):
			raise ValueError("Number of atoms in trajectory (%d)"
				" not the same as in topology (%d)" %
				(natoms, len(self.topology.atomNames)))
		# step
		# nre
		for i in range(2):
			xdr.unpack_uint()
		if x_size / (3 * natoms) == 4:
			self.unpackFloatFunc = xdr.unpack_float
		elif x_size / (3 * natoms) == 8:
			self.unpackFloatFunc = xdr.unpack_double
		else:
			raise ValueError("Coordinate size not a multiple of"
						" float or double size")
		# t
		# lambda
		for i in range(2):
			self.unpackFloatFunc()
		headerPos = xdr.get_position()
		return headerPos + precoordSize, headerPos + frameSize

	def __len__(self):
		return len(self.crdStarts)

	def __getitem__(self, i):
		numAtoms = len(self.topology.atomNames)
		from numpy import float32, float64, fromstring, array, dtype
		import struct

		self.fileString.setStartPos(self.crdStarts[i])
		if self.unpackFloatFunc == self.xdr.unpack_float:
			fmt = ">%df" % (3 * numAtoms)
			size = 12 * numAtoms
			ntype = float32
		else:
			fmt = ">%dd" % (3 * numAtoms)
			size = 24 * numAtoms
			ntype = float64
		coords = fromstring(self.fileString[:size], ntype)
		if dtype(ntype).str[0] == '<': # little endian
			coords.byteswap(True)
		coords *= 10.0
		coords.shape = (numAtoms, 3)
		return coords

class FileString:
	def __init__(self, xdrFile, startPos, fileSize):
		self.startPos = startPos
		self.xdrFile = xdrFile
		self.fileSize = fileSize
		self.getbuffer()

	def fillBuffer(self, pos):
		blen = len(self.buffer)
		while pos >= blen:
			self.getbuffer(2 * blen)
			nlen = len(self.buffer)
			if nlen <= blen:
				raise ValueError("Unexpected end in trajectory"
								" file")
			blen = nlen

	def getbuffer(self, reqSize=262144):
		self.xdrFile.seek(self.startPos)
		self.buffer = self.xdrFile.read(reqSize)

	def setStartPos(self, newPos):
		self.startPos = newPos
		self.getbuffer()

	def __getitem__(self, i):
		self.fillBuffer(i)
		return self.buffer[i]

	def __getslice__(self, i, j):
		self.fillBuffer(j-1)
		return self.buffer[i:j]
	
	def __len__(self):
		# __len__ apparently has to return an int, not a long
		return int(self.fileSize - self.startPos)
