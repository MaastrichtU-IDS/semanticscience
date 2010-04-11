class MolecularMotion:

	def __init__(self, m, xform, **kw):
		"""Compute a trajectory that transforms molecule conformation
		'm'.  Subsequent calls to interpolate must supply molecules
		that have the exact same set of atoms as 'm'.
		Currently support keyword options are:

			method		string, default "corkscrew"
					Use interpolation method 'method'.
					Known methods are "corkscrew",
					"independent" and "linear".
			rate		string, default "linear"
					Interpolate frames so that the
					trajectory motion appears to be
					"rate": either "linear" (constant
					motion throughout) or "sinusoidal"
					(fast in middle, slow at ends).
			frames		integer, default 20
					Number of intermediate frames to
					generate in trajectory
			minimize	boolean, default False
					Run energy minimization for each
					trajectory frame when it is created.
			steps		integer, default 60
					If "minimize" is True, run "steps"
					steps of minimization for each frame.

		If "minimize" is True, the steepest descent minimizer from
		MMTK is used for minimization with the Amber94 forcefield.
		Non-standard residues are parameterized using DockPrep and
		Parmchk, which generates GAFF parameters.  'mStart' and 'mEnd'
		must have hydrogens already added (this is to provide
		flexibility for caller to control hydrogen addition
		conditions).
		
		Note that this class assumes that the hydrogens have already
		been added.  This is because the hydrogen addition code (AddH)
		may put different number of hydrogens on different conformations
		because they have different hydrogen bonding patterns.  To avoid
		this, all conformations must use the same idatmType for all
		atoms, and there is no way for this class to guarantee for
		that to happen.  So we punt the problem to the caller."""

		#
		# Save reference to molecule for error checking later
		#
		from util import copyMolecule
		self.mol, atomMapMol, residueMapMol = copyMolecule(m)
		self.xform = xform
		self.inverseXform = self.xform.inverse()
		# Fix up some attributes after copying:
		# New trajectory has its own name
		# If reference model was uncolored, default new color to None
		self.mol.name = "Morph - %s" % m.name
		if m.color.name().startswith("_openColor"):
			self.mol.color = None
		self._mi = None
		self._resetOptions(**kw)

	def _resetOptions(self, **kw):
		#
		# Get all the options first
		#
		self.method = kw.get("method", "corkscrew")
		self.rate = kw.get("rate", "linear")
		self.frames = kw.get("frames", 20)
		self.minimize = kw.get("minimize", False)
		self.steps = kw.get("steps", 60)

		#
		# Set up minimization apparatus if needed
		#
		if self.minimize and self._mi is None:
			from MMMD import MMTKinter
			from util import timestamp
			timestamp("Setting up MMTK universe")
			self._mi = MMTKinter.MMTKinter([self.mol], nogui=True,
							ljOptions=10.0,
							esOptions=10.0)
			timestamp("Finished setting up MMTK universe")

	def reset(self, **kw):
		"""Reset interpolation (just remove all but first coordset)"""
		keys = self.mol.coordSets.keys()
		keep = min(keys)
		cs = self.mol.findCoordSet(keep)
		self.mol.activeCoordSet = cs
		for key in keys:
			if key == keep:
				continue
			cs = self.mol.findCoordSet(key)
			self.mol.deleteCoordSet(cs)
		self._resetOptions(**kw)

	def interpolate(self, m, xform, **kw):
		"""Interpolate to new conformation 'm'."""

		#
		# Get all the options
		#
		if kw.has_key("method"):
			self.method = kw["method"]
		if kw.has_key("rate"):
			self.rate = kw["rate"]
		if kw.has_key("frames"):
			self.frames = kw["frames"]
		if kw.has_key("cartesian"):
			self.cartesian = kw["cartesian"]
		if kw.has_key("minimize"):
			self.minimize = kw["minimize"]
		if kw.has_key("steps"):
			self.steps = kw["steps"]
		if self.minimize:
			self.callback = self.minimizeCallback
		else:
			self.callback = self.interpolateCallback

		#
		# Find matching set of residues.  First try for
		# one-to-one residue match, and, if that fails,
		# then finding a common set of residues.
		#
		import Segment
		sm = self.mol
		try:
			results = Segment.segmentHingeExact(sm, m)
		except ValueError:
			results = Segment.segmentHingeApproximate(sm, m)
		segments, atomMap, unusedResidues, unusedAtoms = results
		for r in unusedResidues:
			sm.deleteResidue(r)
		for a in unusedAtoms:
			sm.deleteAtom(a)
		if unusedResidues or unusedAtoms:
			from chimera import Sequence
			Sequence.invalidate(sm)
			if self.minimize:
				from chimera.baseDialog import AskYesNoDialog
				from chimera.tkgui import app
				d = AskYesNoDialog(
					"Cannot minimize with non-identical models.\n"
					"Continue without minimization?",
					default="Yes")
				if d.run(app) != "yes":
					raise ValueError("terminated at user request")
				self.minimize = False
				self.callback = self.interpolateCallback

		#
		# Interpolate between last conformation in trajectory
		# and new conformations
		#
		sm.activeCoordSet = sm.coordSets[max(sm.coordSets.keys())]
		from Interpolate import interpolate
		import chimera
		combinedXform = chimera.Xform(self.inverseXform)
		combinedXform.multiply(xform)
		interpolate(sm, combinedXform,
				segments, atomMap, self.method,
				self.rate, self.frames,
				self.cartesian, self.callback)

	def minimizeCallback(self, mol):
		self._mi.setFixed("none")
		self._mi.loadMMTKCoordinates()
		self._mi.minimize(self.steps, interval=10)
		self._mi.saveMMTKCoordinates()
		self.interpolateCallback(mol)

	def interpolateCallback(self, mol):
		from util import timestamp
		timestamp("Trajectory frame %d generated" % len(mol.coordSets))
		from chimera.replyobj import status
		status("Trajectory frame %d generated" % len(mol.coordSets))

	def trajectory(self):
		return self.mol

if __name__ == "chimeraOpenSandbox":
	def test():
		import chimera
		import AddH

		m0, m1 = chimera.openModels.open("testdata/1dmo.pdb")
		#m0, m1 = chimera.openModels.open("/mol/pdb/mt/pdb1mtx.ent")[:2]
		minimize = True
		if minimize:
			AddH.simpleAddHydrogens([m0, m1])

		m0.color = chimera.Color.lookup("red")
		m1.color = chimera.Color.lookup("green")
		chimera.runCommand("~disp ; ribbon; ribrepr sharp")

		mm = MolecularMotion(m0, minimize=minimize)
		mm.interpolate(m1)
		mm.interpolate(m0)

		from util import runMovie
		runMovie(mm.trajectory())

	test()
