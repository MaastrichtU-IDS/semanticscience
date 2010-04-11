from __future__ import with_statement

TYPE_PUBLICATION = "publication"
TYPE_INTERACTIVE = "interactive"
Types = [ TYPE_INTERACTIVE, TYPE_PUBLICATION ]

_singleton = None
def init(menu):
	global _singleton
	_singleton = PresetManager(menu)
	return _singleton
def get():
	if _singleton is None:
		init(None)
	return _singleton

class PresetManager:

	def __init__(self, menu):
		self.menu = menu
		self.presets = {}
		for type in Types:
			self.presets[type] = []
		self.addPreset(TYPE_INTERACTIVE,
			"ribbons", 0,
			preset, False)
		self.addPreset(TYPE_INTERACTIVE,
			"all atoms", 4,
			lambda:preset(allAtoms=True), False)
		self.addPreset(TYPE_INTERACTIVE,
			"hydrophobicity surface", 15,
			lambda:preset(surface="hydrophobicity"), False)
		self.addPreset(TYPE_PUBLICATION,
			"silhouette, rounded ribbon, sticks", -3,
			lambda:preset(publication=True, depthCued=False), False)
		self.addPreset(TYPE_PUBLICATION,
			"silhouette, licorice, sticks", -3,
			lambda:preset(publication=True, depthCued=False,
					scalingName="licorice"), False)
		self.addPreset(TYPE_PUBLICATION,
			"depth-cued, rounded ribbon, sticks", -3,
			lambda:preset(publication=True), False)
		self.addPreset(TYPE_PUBLICATION,
			"depth-cued, licorice, sticks", -3,
			lambda:preset(publication=True,
					scalingName="licorice"), False)
		self.updateMenu()

	def updateMenu(self):
		if self.menu is None:
			return
		self.menu.delete(0, "end")
		for type in Types:
			for i, val in enumerate(self.presets[type]):
				desc, underline, func = val
				prefix = "%s %d" % (type.capitalize(), i + 1)
				label = "%s (%s)" % (prefix, desc)
				ul = underline + len(prefix) + 2
				self.menu.add_command(label=label,
							underline=ul,
							command=func)
			if type is not Types[-1]:
				self.menu.add_separator()

	def addPreset(self, type, desc, underline, f, update=True):
		ctype = self._canonicalType(type)
		presetList = self.presets[ctype]
		presetList.append((desc, underline, f))
		if update:
			self.updateMenu()
		return len(presetList)

	def removePreset(self, type, n):
		ctype = self._canonicalType(type)
		try:
			presetList = self.presets[ctype]
			del presetList[n]
		except (KeyError, IndexError):
			raise KeyError("preset \"%s %d\" not found" % (type, n))

	def applyPreset(self, type, n):
		ctype = self._canonicalType(type)
		try:
			presetList = self.presets[ctype]
			desc, underline, func = presetList[n - 1]
			func()
		except (KeyError, IndexError):
			raise KeyError("preset \"%s %d\" not found" % (type, n))

	def listPresets(self, type=None):
		presets = []
		if type is not None:
			ctype = self._canonicalType(type)
			presetList = self.presets[ctype]
			for i, item in enumerate(presetList):
				presets.append((ctype, i + 1, item[0]))
		else:
			for type, presetList in self.presets.iteritems():
				for i, item in enumerate(presetList):
					presets.append((type, i + 1, item[0]))
		return presets

	def _canonicalType(self, type):
		userType = type.lower()
		for t in Types:
			if t.startswith(userType):
				return t
		raise KeyError("unknown preset type \"%s\"" % type)

def preset(surface=None, allAtoms=False, publication=False, depthCued=True,
			scalingName="Chimera default", openedModels=None):
	import chimera
	from chimera import runCommand, viewer, LODControl, ionLike
	from viewing import getQuality, setQuality
	def myRunCommand(*args):
		from Midas import MidasError
		try:
			runCommand(*args)
		except MidasError, v:
			from chimera import replyobj
			replyobj.status(str(v), color="red")

	import NucleicAcids as NA
	from contextlib import nested
	with nested(NA.blockUpdates(), chimera.update.blockFrameUpdates()):
		mat = chimera.Material.lookup("default")
		if publication:
			myRunCommand("set bg_color white; set dc_color none")
			if getQuality() < 5.0:
				setQuality(5.0)
			mat.shininess = 100.0
			mat.specular = 5.0, 5.0, 5.0
			from _surface import SurfaceModel
			for m in chimera.openModels.list(modelTypes=[SurfaceModel]):
				m.material = mat
		elif not openedModels:
			myRunCommand("set bg_color black; set dc_color none")
			setQuality(1.0)
			mat.shininess = 30.0
			mat.specular = 1.0, 1.0, 1.0
		if openedModels:
			from Midas import ribrepr
			ribrepr("smooth", openedModels)
		else:
			if depthCued:
				viewer.depthCue = True
				viewer.showSilhouette = False
			else:
				viewer.depthCue = False
				viewer.showSilhouette = True
				if viewer.silhouetteWidth < 1.5:
					viewer.silhouetteWidth = 1.5
			myRunCommand("ribscale %s" % repr(scalingName))
			myRunCommand("ribrepr smooth")
		ribbonable = set()
		display = set()
		Ball = chimera.Atom.Ball
		Sphere = chimera.Atom.Sphere
		EndCap = chimera.Atom.EndCap
		Stick = chimera.Bond.Stick
		from misc import principalAtom
		from actions import colorAtomByElement
		ribMolecules = []
		interacting = set()
		nucleic = {}
		from elements import metals
		if openedModels:
			models = openedModels
		else:
			models = chimera.openModels.list(modelTypes=[chimera.Molecule])
		for m in models:
			nukes = []
			for a in m.atoms:
				if ionLike(a):
					a.drawMode = Sphere
				else:
					a.drawMode = EndCap
				if publication:
					continue
				a.display = allAtoms
				colorAtomByElement(a, hetero=True)
				if a.element.name == "C":
					a.color = None
			for b in m.bonds:
				b.drawMode = Stick
			if publication:
				continue
			rib = []
			for seq in m.sequences():
				rib.extend([r for r in seq.residues if r])
			if len(rib) <= 10:
				# 10 residues or less is basically 
				# a trivial depiction if ribboned
				display.update(m.residues)
				continue
			ribbonable.update(rib)
			if not openedModels:
				# don't color opened model's ribbon
				ribMolecules.append(m)
			ligand = []
			for r in m.residues:
				r.ribbonDisplay = False
				surfCat = r.atoms[0].surfaceCategory
				if surfCat == "ligand":
					ligand.append(r)
					display.add(r)
					ribbonable.discard(r)
				elif (len(r.atoms) == 1
				and r.atoms[0].element in metals):
					ligand.append(r)
					display.add(r)
				elif getattr(principalAtom(r), "name", None) == "C4'":
					# decide whether to display later
					nukes.append(r)
			if nukes:
				nucleic[m] = nukes

			if allAtoms or not ligand:
				continue
			from numpy import array, float32
			ligPoints = array([a.coord() for r in ligand
						for a in r.atoms], float32)
			atoms = m.atoms
			molPoints = array([a.coord() for a in atoms], float32)
			from _closepoints import find_close_points, BOXES_METHOD
			closeIndices = find_close_points(BOXES_METHOD,
						ligPoints, molPoints, 3.5)[1]
			interacting.update(array(atoms).take(closeIndices))
		if publication:
			for srf in chimera.openModels.list(
						modelTypes=[chimera.MSMSModel]):
				if (srf.colorMode != chimera.MSMSModel.Custom
				and srf.density < 10.0
				and srf.molecule is not None):
					srf.density = 10.0
			return
		if surface:
			if ribMolecules:
				mols = ribMolecules
			else:
				mols = chimera.openModels.list(
						modelTypes=[chimera.Molecule])
			from Midas import surfaceNew
			surfaceNew("main", mols)
			for mol in mols:
				for a in mol.atoms:
					if a.surfaceCategory == "main":
						a.surfaceDisplay = True

			if surface == "hydrophobicity":
				myRunCommand("rangecolor kdHydrophobicity,s"
					" -4.5 dodger blue 0.0 white"
					" 4.5 orange red novalue none")
				myRunCommand("surfcolor byatom")
			else:
				myRunCommand("surfcolor bymodel")
			for srf in chimera.openModels.list(
						modelTypes=[chimera.MSMSModel]):
				if srf.colorMode != chimera.MSMSModel.Custom:
					srf.density = 2.0
		elif not openedModels:
			chimera.openModels.close(chimera.openModels.list(
						modelTypes=[chimera.MSMSModel]))
		if allAtoms:
			if nucleic:
				residues = sum(nucleic.values(), [])
				NA.set_normal(nucleic.keys(), residues)
				for r in residues:
					r.fillDisplay = False
			myRunCommand("repr wire; line 2")
			myRunCommand("rep sphere ions; rep sphere ligand")
			# so that auto-colored carbons are distinguishable
			# from other heteros...
			myRunCommand("modelcolor firebrick #/color=red")
			myRunCommand("modelcolor navy blue #/color=blue")
			return

		from Midas.midas_rainbow import defaultColors, rainbowTexture
		if len(ribMolecules) == 1:
			rainbow = rainbowTexture(defaultColors)
			seqs = ribMolecules[0].sequences()
			if len(seqs) == 1:
				residues = seqs[0].residues
				divisor = float(len(residues) - 1)
				for i, r in enumerate(residues):
					r.ribbonColor = rainbow.color(i/divisor)
			else:
				divisor = float(len(seqs) - 1)
				for i, seq in enumerate(seqs):
					color = rainbow.color(i/divisor)
					for r in seq.residues:
						r.ribbonColor = color
		elif len(ribMolecules) > 1:
			if not [x for x in ribMolecules if x.id != ribMolecules[0].id]:
				# rainbow an NMR ensemble by itself
				rainbow = rainbowTexture(defaultColors)
				divisor = float(len(ribMolecules) - 1)
				for i, rm in enumerate(ribMolecules):
					color = rainbow.color(i/divisor)
					for r in rm.residues:
						r.ribbonColor = color
					for a in rm.atoms:
						a.color = color
			else:
				for rm in ribMolecules:
					for seq in rm.sequences():
						for r in seq.residues:
							r.ribbonColor = None
		from chimera import LONGBOND_PBG_NAME
		for category, group in chimera.PseudoBondMgr.mgr(
						).pseudoBondGroupsMap.items():
			if category == LONGBOND_PBG_NAME:
				for pb in group.pseudoBonds:
					if pb.atoms[0].molecule not in models:
						continue
					for end in pb.atoms:
						end.display = True
						end.color = end.residue.ribbonColor
				continue
			if not category.startswith("coordination complex"):
				continue
			metalResidues = set()
			for pb in group.pseudoBonds:
				if pb.atoms[0].molecule not in models:
					continue
				for end in pb.atoms:
					display.add(end.residue)
					if end.element in metals:
						metalResidues.add(end.residue)
			for mr in metalResidues:
				for a in mr.atoms:
					for nb in a.neighbors:
						if nb.residue != mr:
							display.add(nb.residue)

		for rr in ribbonable:
			rr.ribbonDisplay = True
		for inter in interacting:
			r = inter.residue
			if (r not in ribbonable
			or not r.ribbonResidueClass.hasPosition(inter.name)):
				display.add(r)

		# ring atoms need to be displayed for NucleicAcids to work
		if nucleic:
			for m, residues in nucleic.items():
				if len(residues) < 5:
					continue
				elif len(residues) < 100:
					NA.set_slab('fill/slab', [m], residues,
						orient=True, showGly=True)
					for r in residues:
						r.fillDisplay = True
					display.update(residues)
				elif len(residues) < 500:
					NA.set_slab('tube/slab', [m], residues)
					display.update(residues)

		if not display and not nucleic:
			norib = [r for r in ribbonable if not r.hasRibbon()]
			if len(norib) == len(ribbonable):
				display.update(norib)

		for dr in display:
			for a in dr.atoms:
				if (a.idatmType != "HC"
				or len(a.molecule.residues) == 1):
					a.display = True
