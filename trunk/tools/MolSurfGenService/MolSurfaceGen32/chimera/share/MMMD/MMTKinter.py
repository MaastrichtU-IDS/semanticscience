def simpleNormalizeName(name):
	return name.strip()

class Unimplemented(ValueError):
	pass

class MMTKinter:

	def __init__(self, mols, nogui=False, addhyd=True,
			ljOptions=None, esOptions=None, callback=None):
		# MMTK lengths are in nm while Chimera ones are in Angstroms
		# so we need a scale factor when converting
		if not mols:
			raise ValueError("No molecules specified")
		self.tempDir = None
		self.molId = 0
		self.ljOptions = ljOptions
		self.esOptions = esOptions
		self.callback = callback
		self.mols = mols
		self._getParameters(mols, nogui, addhyd)

	def _finishInit(self):
		timestamp("_finishInit")
		self.molecules = []
		self.atomMap = {}
		try:
			for m in self.mols:
				self.molecules.append(self._makeMolecule(m))
			self._makeUniverse()
			if self.callback:
				self.callback(self)
				del self.callback
		finally:
			self._removeTempDir()

	def _makeUniverse(self):
		import os.path
		parmDir = os.path.dirname(__file__)
		timestamp("_makeUniverse")
		from MMTK import InfiniteUniverse
		from MMTK.ForceFields.Amber import AmberData
		from MMTK.ForceFields.Amber.AmberForceField import readAmber99
		from MMTK.ForceFields.MMForceField import MMForceField
		#
		# GAFF uses lower case atom types to distinguish
		# from Amber atom types.  MMTK, however, normalizes
		# all atom types to upper case.  So we hack MMTK
		# and temporarily replace _normalizeName function
		# with ours while reading our parameter files.
		# (We have to reread the parameter file each time
		# because we potentially have different frcmod files
		# for the different universes.)
		#
		saveNormalizeName = AmberData._normalizeName
		AmberData._normalizeName = simpleNormalizeName
		modFiles = [ m.frcmod for m in self.molecules
				if m.frcmod is not None]
		parameters = readAmber99(os.path.join(parmDir,
							"parm", "gaff.dat"),
						modFiles)
		self._mergeAmber99(parameters)
		bondedScaleFactor = 1.0
		ff = MMForceField("Amber99/GAFF", parameters, self.ljOptions,
					self.esOptions, bondedScaleFactor)
		AmberData._normalizeName = saveNormalizeName

		timestamp("Made forcefield")
		self.universe = InfiniteUniverse(ff)
		timestamp("Made universe")
		for mm in self.molecules:
			self.universe.addObject(mm)
			timestamp("Added model %s" % mm.name)
		timestamp("end _makeUniverse")

	def _getParameters(self, mols, nogui, addhyd):
		timestamp("_getParameters")
		import DockPrep
		import chimera
		self.originalAtoms = set([])
		for m in mols:
			self.originalAtoms.update(m.atoms)
		from AddCharge import AMBER99SB
		kw = { "doneCB": self._finishDockPrep, "gaffType": True,
			"chargeModel": AMBER99SB }
		if nogui or chimera.nogui:
			if not addhyd:
				kw["addHFunc"] = None
			DockPrep.prep(mols, nogui=nogui, **kw)
		else:
			from DockPrep.gui import DockPrepDialog
			from chimera import dialogs
			d = dialogs.display(DockPrepDialog.name, wait=True)
			d.addHydVar.set(addhyd)
			d.applyKeywords = kw
			d.molListBox.setvalue(mols)
			d.writeMol2Var.set(False)
		"""
		d = DockPrep.memoryPrep("Minimize", "use", mols, nogui=nogui, **kw)
		if d:
			d.addHydVar.set(addhyd)
			d.writeMol2Var.set(False)
		"""


	def _finishDockPrep(self):
		timestamp("end _getParameters")
		from chimera import selection
		selectedAtoms = set(selection.currentAtoms())
		addSelected = []
		numAdded = 0
		for m in self.mols:
			for a in m.atoms:
				if a in self.originalAtoms:
					continue
				numAdded += 1
				# This atom was added.  If it was added to
				# a selected atom, then we add this atom
				# into the current selection as well.
				for b in a.bonds:
					oa = a.bonds[0].otherAtom(a)
					if oa in selectedAtoms:
						addSelected.append(a)
						break
		del self.originalAtoms
		if addSelected:
			selection.addCurrent(addSelected)
		#from chimera import replyobj
		#replyobj.info("%d atoms added, %d selected\n"
		#		% (numAdded, len(addSelected)))
		self._finishInit()

	def _mergeAmber99(self, parm):
		"Merge MMTK Amber99 parameters into our parameters"
		from MMTK.ForceFields.Amber.AmberForceField import readAmber99
		parm99 = readAmber99()
		parm.atom_types.update(parm99.atom_types)
		parm.bonds.update(parm99.bonds)
		parm.bond_angles.update(parm99.bond_angles)
		parm.dihedrals.update(parm99.dihedrals)
		parm.dihedrals_2.update(parm99.dihedrals_2)
		parm.impropers.update(parm99.impropers)
		parm.impropers_1.update(parm99.impropers_1)
		parm.impropers_2.update(parm99.impropers_2)
		parm.hbonds.update(parm99.hbonds)
		parm.lj_equivalent.update(parm99.lj_equivalent)
		for name, ljpar_set99 in parm99.ljpar_sets.iteritems():
			try:
				ljpar_set = parm.ljpar_sets[name]
			except KeyError:
				parm.ljpar_sets[name] = ljpar_set99
			else:
				if ljpar_set.type != ljpar_set99.type:
					print "incompatible ljpar_set"
					print " GAFF type:", ljpar_set.type
					print " AMBER99 type:", ljpar_set99.type
				ljpar_set.entries.update(ljpar_set99.entries)

	def _makeMolecule(self, m):
		timestamp("_makeMolecule %s" % m.name)
		mm = MMTKChimeraModel(m, self.molId, self)
		self.molId += 1
		timestamp("end _makeMolecule")
		return mm

	def setFixed(self, which):
		from chimera import selection
		if which == "none" or selection.currentEmpty():
			for ma in self.universe.atomList():
				ma.fixed = False
		elif which == "selected":
			import chimera
			for ma in self.universe.atomList():
				ma.fixed = False
			for a in selection.currentAtoms():
				if a.molecule in self.mols:
					ma = self.atomMap[a]
					ma.fixed = True
		else:
			import chimera
			for ma in self.universe.atomList():
				ma.fixed = True
			for a in selection.currentAtoms():
				if a.molecule in self.mols:
					ma = self.atomMap[a]
					ma.fixed = False

	def loadMMTKCoordinates(self):
		"Load MMTK coordinates from Chimera models"
		import chimera
		from Scientific.Geometry import Vector
		from MMTK import Units
		s = Units.Ang
		for ma in self.universe.atomList():
			try:
				ca = ma.getAtomProperty(ma, "chimera_atom")
			except AttributeError:
				pass
			else:
				c = ca.coord()
				p = Vector(c[0] * s, c[1] * s, c[2] * s)
				ma.setPosition(p)

	def saveMMTKCoordinates(self):
		"Save MMTK coordinates into Chimera models"
		import chimera
		from chimera import Coord
		from MMTK import Units
		s = Units.Ang
		sum = 0.0
		count = 0
		for ma in self.universe.atomList():
			if ma.fixed:
				continue
			ca = ma.getAtomProperty(ma, "chimera_atom")
			p = ma.position()
			c = Coord(p[0] / s, p[1] / s, p[2] / s)
			dsq = (c - ca.coord()).sqlength()
			ca.setCoord(c)
			#print "%.6f" % dsq
			sum += dsq
			count += 1
		import math
		if count > 0:
			print "Updated", count, "atoms.  RMSD: %.6f" \
				% math.sqrt(sum / count)
		else:
			print "No atoms updated."

	def minimize(self, nsteps, stepsize=0.02,
			interval=None, action=None, **kw):
		from chimera import replyobj
		timestamp("_minimize")
		from MMTK import Units
		from MMTK.ForceFields.Amber import AmberData
		from MMTK.Minimization import SteepestDescentMinimizer
		from MMTK.Trajectory import LogOutput
		import sys
		if not interval:
			actions = []
		else:
			actions = [ LogOutput(sys.stdout, ["energy"],
						interval, None, interval) ]
		kw["step_size"] = stepsize * Units.Ang
		minimizer = SteepestDescentMinimizer(self.universe,
							actions=actions, **kw)
		if action is None or not interval:
			interval = None
		msg = "Initial energy: %f" % self.universe.energy()
		replyobj.status(msg)
		replyobj.info(msg)
		saveNormalizeName = AmberData._normalizeName
		AmberData._normalizeName = simpleNormalizeName
		remaining = nsteps
		while remaining > 0:
			timestamp(" minimize interval")
			if interval is None:
				realSteps = remaining
			else:
				realSteps = min(remaining, interval)
			minimizer(steps=realSteps)
			remaining -= realSteps
			if action is not None:
				action(self)
			timestamp(" finished %d steps" % realSteps)
			msg = "Finished %d of %d minimization steps" % (
						nsteps - remaining, nsteps)
			replyobj.status(msg)
			replyobj.info(msg)
		replyobj.info("\n")
		AmberData._normalizeName = saveNormalizeName
		timestamp("end _minimize")

	def getTempDir(self):
		if self.tempDir:
			return self.tempDir
		from tempfile import mkdtemp
		self.tempDir = mkdtemp()
		#self.tempDir = "."
		return self.tempDir

	def _removeTempDir(self):
		if not self.tempDir:
			return
		if True:
			import os, os.path
			for filename in os.listdir(self.tempDir):
				os.remove(os.path.join(self.tempDir, filename))
			os.rmdir(self.tempDir)
		else:
			print "Did not clean up temp dir", self.tempDir
		self.tempDir = None


from MMTK import ChemicalObjects
class MMTKChimeraModel(ChemicalObjects.Molecule):

	def __init__(self, m, ident, owner):
		from MMTK import Bonds
		self.chimeraMolecule = m
		self.needParmchk = set([])
		self.frcmod = None
		self.atomMap = owner.atomMap

		self.name = m.name
		self.parent = None
		self.type = None
		self.groups = []
		for r in m.residues:
			v = self._findStandardResidue(r)
			if v is None:
				self._makeNonStandardResidue(r)
			else:
				self._makeStandardResidue(r, *v)
		atoms = []
		bonds = []
		for g in self.groups:
			atoms.extend(g.atoms)
			bonds.extend(g.bonds)
		from chimera import Bond
		for b in m.bonds:
			if b.display == Bond.Never:
				continue
			a0, a1 = b.atoms
			if a0.residue is a1.residue:
				continue
			mb = Bonds.Bond((self.atomMap[a0], self.atomMap[a1]))
			bonds.append(mb)
		self.atoms = atoms
		self.bonds = Bonds.BondList(bonds)
		if self.needParmchk:
			self._runParmchk(ident, owner.getTempDir())

	def _findStandardResidue(self, r):
		try:
			amberName = r.amberName
		except AttributeError:
			pass
		else:
			try:
				blueprint = ResidueNameMap[amberName]
			except KeyError:
				pass
			else:
				from MMTK.ChemicalObjects import Group
				return Group(blueprint), amberName
		try:
			blueprint = MoleculeNameMap[r.type]
		except KeyError:
			return None
		else:
			from MMTK.ChemicalObjects import Molecule
			return Molecule(blueprint), r.type

	def _makeStandardResidue(self, r, mg, blueprint):
		#print "makeStandardResidue", r.oslIdent(), r.amberName, blueprint
		chimera2mmtk = self._mapStandardAtoms(r, mg)
		if (len(chimera2mmtk) == len(mg.atomList())
		and len(chimera2mmtk) == len(r.atoms)):
			self._addStandardResidue(mg, chimera2mmtk)
			return

		# Some atoms were not used.
		# If residue is a histidine, try other protonation forms.
		resType = blueprint[-3:]
		hisList = [ "HIE", "HID", "HIP", "HIS" ]
		if resType in hisList:
			prefix = blueprint[:-3]
			from MMTK.ChemicalObjects import Group
			from chimera import LimitationError
			for hisType in hisList:
				if hisType == resType:
					continue
				newType = prefix + hisType
				mg = Group(ResidueNameMap[newType])
				try:
					chimera2mmtk = self._mapStandardAtoms(r, mg)
				except LimitationError:
					# Must have hit a Chimera atom with
					# no corresponding MMTK atom when
					# using the wrong blueprint
					continue
				if (len(chimera2mmtk) == len(mg.atomList())
				and len(chimera2mmtk) == len(r.atoms)):
					break
			from chimera import replyobj
			replyobj.warning("histidine %s reclassified "
						"from AMBER type %s to %s\n" %
						(r.oslIdent(), blueprint,
						newType))
			self._addStandardResidue(mg, chimera2mmtk)
			return

		# There is an irreconcilable atom mismatch.
		allMMTKAtoms = set(mg.atomList())
		allChimeraAtoms = set(r.atoms)
		usedMMTKAtoms = set(chimera2mmtk.itervalues())
		usedChimeraAtoms = set(chimera2mmtk.iterkeys())
		extra = [ a.name
			for a in allChimeraAtoms - usedChimeraAtoms ]
		if extra:
			extraAtoms = " has extra " + makeAtomList(extra)
		else:
			extraAtoms = None
		missing = [ ma.name
			for ma in allMMTKAtoms - usedMMTKAtoms ]
		if missing:
			missingAtoms = " is missing " + makeAtomList(missing)
		else:
			missingAtoms = None
		if extra and missing:
			msg = extraAtoms + " and" + missingAtoms
		elif extra:
			msg = extraAtoms
		else:
			msg = missingAtoms
		from chimera import LimitationError
		raise LimitationError("Residue %s (%s/%s) %s"
					% (r.oslIdent(), r.type, mg.name, msg))

	def _mapStandardAtoms(self, r, mg):
		pdbmap = {}
		altmap = {}
		self._getMaps(mg, pdbmap, altmap)
		try:
			subgroups = mg.groups
		except AttributeError:
			pass
		else:
			for subg in mg.groups:
				self._getMaps(subg, pdbmap, altmap)
		used = {}
		chimera2mmtk = {}
		for a in r.atoms:
			aname = self.getMMTKname(a.name, r.type, pdbmap, altmap)
			ma = mg.getAtom(aname)
			if ma in used:
				from chimera import LimitationError
				raise LimitationError("Residue %s (%s/%s) should have either atom %s "
							"or %s, but not both" % (r.oslIdent(),
							r.type, mg.name, used[ma], a.name))
			chimera2mmtk[a] = ma
			used[ma] = a.name
		return chimera2mmtk

	def getMMTKname(self, aname, rtype, pdbmap, altmap):
		# If the name does not start with an alphabetic
		# character, try rotating it until it does.  This works
		# for hydrogens in amino acids.
		letters = "abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
		n = aname
		while n[0] not in letters:
			n = n[1:] + n[0]
		n = altmap.get(n, n)
		if pdbmap.has_key(n):
			return pdbmap[n]
		# Nope.  If the name contains a ', try replacing it with
		# a *.  This works for hydrogens in nucleotides.
		n = aname.replace("'", '*')
		n = altmap.get(n, n)
		if pdbmap.has_key(n):
			return pdbmap[n]
		#print pdbmap.keys()
		#print altmap.keys()
		from chimera import LimitationError
		raise LimitationError("No MMTK name for atom \"%s\" "
					"in standard residue \"%s\""
					% (aname, rtype))

	def _getMaps(self, obj, pdbmap, altmap):
		try:
			pm = obj.pdbmap
		except AttributeError:
			pass
		else:
			for item in pm:
				for name, ref in item[1].iteritems():
					atom = obj.getAtom(ref)
					pdbmap[name] = atom
		try:
			am = obj.pdb_alternative
		except AttributeError:
			pass
		else:
			altmap.update(am)

	def _addStandardResidue(self, mg, chimera2mmtk):
		for a, ma in chimera2mmtk.iteritems():
			ma.addProperties({"chimera_atom": a})
			a.gaffType = mg.getAtomProperty(ma, "amber_atom_type")
			self.atomMap[a] = ma
		mg.parent = self
		self.groups.append(mg)

	def _makeNonStandardResidue(self, r):
		#print "makeNonstandardResidue", r.oslIdent(), r.type
		mg = MMTKChimeraGroup(r, self.atomMap)
		mg.parent = self
		self.groups.append(mg)
		self.needParmchk.add(r)

	def _runParmchk(self, ident, tempDir):
		import os, os.path, sys
		from subprocess import Popen, STDOUT, PIPE
		from chimera import replyobj
		parmDir = os.path.dirname(__file__)
		if not parmDir:
			parmDir = os.getcwd()
		parmchkIn = os.path.join(tempDir, "parmchk.in.%d" % ident)
		self._writeParmchk(parmchkIn)

		self.frcmod = os.path.join(tempDir, "frcmod.%d" % ident)
		chimeraRoot = os.environ["CHIMERA"]
		anteHome = os.path.join(chimeraRoot, "bin", "antechamber")
		command = [
			os.path.join(anteHome, "exe", "parmchk"),
			"-i", parmchkIn,
			"-f", "mol2",
			"-o", self.frcmod,
			"-p", os.path.join(parmDir, "parm", "gaff.dat")
		]
		replyobj.status("Running PARMCHK for %s\n" %
				self.chimeraMolecule.name, log=True)
		replyobj.info("command: %s\n" % " ".join(command))
		p = Popen(command, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
				cwd=tempDir, shell=False,
				env={"ACHOME": anteHome},
				bufsize=1).stdout
		while True:
			line = p.readline()
			if not line:
				break
			replyobj.info("(parmchk) %s\n" % line.rstrip())
		if not os.path.exists(self.frcmod):
			from chimera import LimitationError
			raise LimitationError("Unable to compute partial "
					"charges: PARMCHK failed.\n"
					"Check reply log for details.\n")
			self.frcmod = None
		replyobj.status("Finished PARMCHK for %s\n" %
				self.chimeraMolecule.name, log=True)

	def _writeParmchk(self, filename):
		# generate Mol2 input file for parmchk
		import WriteMol2
		from chimera.selection import ItemizedSelection
		from chimera import Bond
		rSet = set(self.needParmchk)
		for b in self.chimeraMolecule.bonds:
			if b.display == Bond.Never:
				continue
			a0, a1 = b.atoms
			r0 = a0.residue
			r1 = a1.residue
			if (r0 in self.needParmchk
			and r1 not in self.needParmchk):
				rSet.add(r1)
			elif (r0 not in self.needParmchk
			and r1 in self.needParmchk):
				rSet.add(r0)
		sel = ItemizedSelection()
		sel.add(rSet)
		WriteMol2.writeMol2(sel, filename, gaffType=True)


from MMTK import Biopolymers
class MMTKChimeraGroup(Biopolymers.Residue):

	def __init__(self, r, atomMap):
		import chimera
		from MMTK.ChemicalObjects import Atom
		from MMTK.Bonds import Bond
		self.type = None
		self.parent = None
		self.name = r.oslIdent()
		atoms = []
		c2m = {}
		residueBonds = set([])
		for a in r.atoms:
			try:
				ma = Atom(a.element.name)
			except IOError:
				from chimera import LimitationError
				raise LimitationError("Atom type \"%s\" "
					"is not supported by MMTK" %
					a.element.name)
			ma.parent = self
			try:
				charge = a.charge
			except AttributeError:
				from chimera import LimitationError
				raise LimitationError("Unable to find "
					"partial charge for %s" % a.oslIdent())
			try:
				gaffType = a.gaffType
			except AttributeError:
				from chimera import LimitationError
				raise LimitationError("Element %s (atom "
					"%s) is not currently supported"
					% (a.element.name, a.oslIdent()))
			properties = {
				"amber_charge": charge,
				"amber_atom_type": gaffType,
				"chimera_atom": a,
			}
			ma.addProperties(properties)
			atoms.append(ma)
			c2m[a] = ma
			for b in a.bonds:
				if b.display == chimera.Bond.Never:
					continue
				other = b.otherAtom(a)
				if other.residue == r:
					residueBonds.add(b)
			atomMap[a] = ma
		bonds = []
		for b in residueBonds:
			a0, a1 = b.atoms
			ma0 = c2m[a0]
			ma1 = c2m[a1]
			mb = Bond((ma0, ma1))
			mb.parent = self
			bonds.append(mb)
		self.atoms = atoms
		self.bonds = bonds

def _dumpChain(obj):
	while obj is not None:
		print "object", obj
		_dumpDataAttributes(obj)
		obj = getattr(obj, "parent", None)

def _dumpDataAttributes(mg):
	for attr in dir(mg):
		if attr.startswith("__"):
			continue
		val = getattr(mg, attr)
		if callable(val):
			continue
		print " ", attr, val

def makeAtomList(names):
	# Assume names is not empty
	if len(names) == 1:
		return "atom %s" % names[0]
	else:
		return "atoms %s and %s" % (", ".join(names[:-1]), names[-1])

def timestamp(s):
	pass
	#import time
	#print "%s: %s" % (time.ctime(time.time()), s)

ResidueNameMap = {
	"ACE":	"ace_beginning_nt",
	"NME":	"methyl",

	"ALA":	"alanine",
	"ARG":	"arginine",
	"ASP":	"aspartic_acid",
	"ASN":	"asparagine",
	"CYS":	"cysteine",
	"CYX":	"cystine_ss",
	"GLU":	"glutamic_acid",
	"GLN":	"glutamine",
	"GLY":	"glycine",
	"HIS":	"histidine",
	"HID":	"histidine_deltah",
	"HIE":	"histidine_epsilonh",
	"HIP":	"histidine_plus",
	"ILE":	"isoleucine",
	"LEU":	"leucine",
	"LYS":	"lysine",
	"MET":	"methionine",
	"PHE":	"phenylalanine",
	"PRO":	"proline",
	"SER":	"serine",
	"NA":	"sodium",
	"THR":	"threonine",
	"TRP":	"tryptophan",
	"TYR":	"tyrosine",
	"VAL":	"valine",
	"CALA":	"alanine_ct",
	"CARG":	"arginine_ct",
	"CASP":	"aspartic_acid_ct",
	"CASN":	"asparagine_ct",
	"CCYS":	"cysteine_ct",
	"CCYX":	"cystine_ss_ct",
	"CGLU":	"glutamic_acid_ct",
	"CGLN":	"glutamine_ct",
	"CGLY":	"glycine_ct",
	"CHIS":	"histidine_ct",
	"CHID":	"histidine_deltah_ct",
	"CHIE":	"histidine_epsilonh_ct",
	"CHIP":	"histidine_plus_ct",
	"CILE":	"isoleucine_ct",
	"CLEU":	"leucine_ct",
	"CLYS":	"lysine_ct",
	"CMET":	"methionine_ct",
	"CPHE":	"phenylalanine_ct",
	"CPRO":	"proline_ct",
	"CSER":	"serine_ct",
	"CNA":	"sodium_ct",
	"CTHR":	"threonine_ct",
	"CTRP":	"tryptophan_ct",
	"CTYR":	"tyrosine_ct",
	"CVAL":	"valine_ct",
	"NALA":	"alanine_nt",
	"NARG":	"arginine_nt",
	"NASP":	"aspartic_acid_nt",
	"NASN":	"asparagine_nt",
	"NCYS":	"cysteine_nt",
	"NCYX":	"cystine_ss_nt",
	"NGLU":	"glutamic_acid_nt",
	"NGLN":	"glutamine_nt",
	"NGLY":	"glycine_nt",
	"NHIS":	"histidine_nt",
	"NHID":	"histidine_deltah_nt",
	"NHIE":	"histidine_epsilonh_nt",
	"NHIP":	"histidine_plus_nt",
	"NILE":	"isoleucine_nt",
	"NLEU":	"leucine_nt",
	"NLYS":	"lysine_nt",
	"NMET":	"methionine_nt",
	"NPHE":	"phenylalanine_nt",
	"NPRO":	"proline_nt",
	"NSER":	"serine_nt",
	"NNA":	"sodium_nt",
	"NTHR":	"threonine_nt",
	"NTRP":	"tryptophan_nt",
	"NTYR":	"tyrosine_nt",
	"NVAL":	"valine_nt",

	"A":	"adenine",
	"C":	"cytosine",
	"G":	"guanine",
	"T":	"thymine",
	"U":	"uracil",
	"DA":	"d-adenosine",
	"DC":	"d-cytosine",
	"DG":	"d-guanosine",
	"DT":	"d-thymine",
	"RA":	"r-adenosine",
	"RC":	"r-cytosine",
	"RG":	"r-guanosine",
	"RU":	"r-uracil",
	"DA3":	"d-adenosine_3ter",
	"DC3":	"d-cytosine_3ter",
	"DG3":	"d-guanosine_3ter",
	"DT3":	"d-thymine_3ter",
	"RA3":	"r-adenosine_3ter",
	"RC3":	"r-cytosine_3ter",
	"RG3":	"r-guanosine_3ter",
	"RU3":	"r-uracil_3ter",
	"DA5":	"d-adenosine_5ter",
	"DC5":	"d-cytosine_5ter",
	"DG5":	"d-guanosine_5ter",
	"DT5":	"d-thymine_5ter",
	"RA5":	"r-adenosine_5ter",
	"RC5":	"r-cytosine_5ter",
	"RG5":	"r-guanosine_5ter",
	"RU5":	"r-uracil_5ter",
	"DAN":	"d-adenosine_5ter_3ter",
	"DCN":	"d-cytosine_5ter_3ter",
	"DGN":	"d-guanosine_5ter_3ter",
	"DTN":	"d-thymine_5ter_3ter",
	"RAN":	"r-adenosine_5ter_3ter",
	"RCN":	"r-cytosine_5ter_3ter",
	"RGN":	"r-guanosine_5ter_3ter",
	"RUN":	"r-uracil_5ter_3ter",
}

MoleculeNameMap = {
	"HOH":	"water",
	"WAT":	"water",
}

if __name__ == "__main__" or __name__ == "chimeraOpenSandbox":
	def minimize(mi):
		def update(mi):
			import chimera
			mi.saveMMTKCoordinates()
			chimera.runCommand("wait")
		mi.loadMMTKCoordinates()
		mi.minimize(nsteps=100, interval=10, action=update)

	def test():
		import chimera
		# Standard residues only
		#mList = chimera.openModels.open("testdata/small2.pdb")
		#mList = chimera.openModels.open("testdata/1gcn.pdb")
		# Non-standard residues only
		#mList = chimera.openModels.open("testdata/gdp.pdb")
		# Both standard and non-standard residues
		mList = chimera.openModels.open("testdata/3fx2.pdb")
		mi = MMTKinter(mList, callback=minimize)

	test()
