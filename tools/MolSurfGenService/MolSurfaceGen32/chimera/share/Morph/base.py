class Script:

	def __init__(self, mol, closeCB=None, **kw):
		# TODO: grab preferences before initializing default options
		options = {
			"method": "corkscrew",
			"rate": "linear",
			"frames": 20,
		}
		options.update(kw)
		self.actions = [ (mol, options) ]
		self.motion = None
		self.movieDialog = None
		self.closeHandler = None
		self.closeCB = closeCB
		self.addhMap = {}

	def __del__(self):
		if self.movieDialog:
			self.killMovieDialog()
		self.motion = None
		self.actions = []
		self.updateHandler()

	def finish(self):
		# Must be called to get rid of closeHandler before
		# releasing reference to this instance.  Otherwise,
		# instance is not released and bad things happen
		# on callback.
		if self.closeHandler:
			import chimera
			chimera.triggers.deleteHandler("Molecule",
						self.closeHandler)
			self.closeHandler = None

	def addAction(self, mol, after=None, **kw):
		if after is None:
			self.actions.append((mol, kw))
			where = len(self.actions) - 1
		else:
			self.actions.insert(after + 1, (mol, kw))
			where = after + 1
		self.updateHandler()
		return where

	def moveActionUp(self, which):
		mol, opts = self.actions[which]
		prevMol, prevOpts = self.actions[which - 1]
		self.actions[which - 1] = (mol, prevOpts)
		self.actions[which] = (prevMol, opts)

	def removeAction(self, which):
		del self.actions[which]

	def setOptions(self, which, **kw):
		mol, opts = self.actions[which]
		opts.update(kw)

	def makeTrajectory(self, minimize=False, steps=60):
		from chimera import replyobj
		#
		# It's an all-or-nothing deal.  If any step requires
		# minimization, all molecules must have hydrogens
		# because the interpolation routines requires a 1-1
		# atom mapping between the two conformations
		#
		if not minimize:
			molMap = {}
			for mol, options in self.actions:
				molMap[mol] = mol
		else:
			import AddH
			kw = {
				"delSolvent": False,
				"nogui": True,
				"addHFunc": AddH.simpleAddHydrogens,
			}
			import DockPrep
			from util import mapAtoms, copyMolecule
			refMol = None
			for mol, options in self.actions:
				if self.addhMap.has_key(mol):
					refMol = mol
			if refMol is None:
				refMol = self.actions[0][0]
				replyobj.message("Add hydrogens to %s\n"
							% refMol.oslIdent())
				m, aMap, rMap = copyMolecule(refMol)
				DockPrep.prep([m], **kw)
				self.addhMap[refMol] = m
			for mol, options in self.actions:
				if self.addhMap.has_key(mol):
					continue
				amap = mapAtoms(mol, refMol,
						ignoreUnmatched=True)
				for a, refa in amap.iteritems():
					a.idatmType = refa.idatmType
				replyobj.message("Add hydrogens to %s\n"
							% mol.oslIdent())
				m, aMap, rMap = copyMolecule(mol)
				DockPrep.prep([m], **kw)
				self.addhMap[mol] = m
			molMap = self.addhMap

		import copy
		mol, options = self.actions[0]
		initOptions = copy.copy(options)
		if self.motion is None:
			from Motion import MolecularMotion
			self.motion = MolecularMotion(molMap[mol],
							mol.openState.xform,
							minimize=minimize,
							steps=steps,
							**initOptions)
		else:
			self.motion.reset(minimize=minimize, steps=steps,
							**initOptions)
		prevMol = mol
		prevOptions = copy.copy(options)

		for i in range(1, len(self.actions)):
			msg = "Computing interpolation %d\n" % i
			replyobj.message(msg)
			replyobj.status(msg)
			mol, options = self.actions[i]
			prevOptions.update(options)
			try:
				self.motion.interpolate(molMap[mol],
							mol.openState.xform,
							**prevOptions)
			except ValueError, msg:
				from chimera import UserError
				raise UserError("cannot interpolate models: %s"
						% msg)
			prevMol = mol
		return self.motion.trajectory(), self.motion.xform

	def killMovieDialog(self):
		import chimera
		if self.movieDialog in chimera.extension.manager.instances:
			if self.motion:
				m = self.motion.trajectory()
			else:
				m = None
			if m:
				self.movieDialog.Quit(deleteMolecule=False)
				chimera.openModels.remove([m])
			else:
				self.movieDialog.Quit()
		self.movieDialog = None

	def updateMovieDialog(self, always, **kw):
		if self.movieDialog:
			self.killMovieDialog()
			always = True
		if always:
			try:
				traj, xform = self.makeTrajectory(**kw)
			finally:
				for mol, options in self.actions:
					try:
						del mol._primaryAtomSet
					except AttributeError:
						# Already gone, molecule
						# probably used multiple times
						pass
			import util
			self.movieDialog = util.runMovie(traj, xform)
			self.updateHandler()

	def updateHandler(self):
		if self.actions or self.motion:
			if self.closeHandler is None:
				# register molecule close handler
				import chimera
				self.closeHandler = chimera.triggers.addHandler(
							"Molecule",
							self._molChange, None)
		else:
			if self.closeHandler is not None:
				# deregister molecule close handler
				import chimera
				chimera.triggers.deleteHandler("Molecule",
							self.closeHandler)
				self.closeHandler = None

	def _molChange(self, triggerName, dummy, change):
		if (self.motion is not None
		and self.motion.trajectory() in change.deleted):
			self.motion = None
		any = False
		newActions = []
		for mol, options in self.actions:
			if mol in change.deleted:
				any = True
			else:
				newActions.append((mol, options))
		if any:
			self.actions = newActions
			if self.closeCB:
				self.closeCB(self)
		self.updateHandler()
