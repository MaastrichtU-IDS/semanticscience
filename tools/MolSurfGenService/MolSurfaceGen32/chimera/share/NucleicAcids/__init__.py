# --- UCSF Chimera Copyright ---
# Copyright (c) 2004 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# Base slabs -- approximate purine and pyrimidine bases
#
# Written by Greg Couch, UCSF Computer Graphics Lab, April 2004
# with help from Nikolai Ulyanov.

import chimera
from CGLutil import vrml
import math
from chimera.resCode import nucleic3to1
import re
import weakref
import SimpleSession
import default

_SQRT2 = math.sqrt(2)

# _data holds all of the nucleotide data.  It is keyed on Molecules,
# and the values are WeakKeyDictionaries with Residue and string keys
# (like 'VRML' for a link to the associated VRML model).  And the Residue
# values are parameters needed to recreate the depiction and associated
# VRML node data.

_data = weakref.WeakKeyDictionary()
_molHandler = None
_rebuildHandler = None
_needRebuild = weakref.WeakKeyDictionary()
_rebuilding = False
_block = 0
VRML = 'VRML'
RESIDUES = 'residues'

SideOptions = [ 'orient', 'fill/slab', 'tube/slab', 'ladder' ]

BackboneRE = re.compile("^(C[345]'|O[35]'|P|OP[12])$", re.I)
BackboneSugarRE = re.compile("^(C[12345]'|O[2345]'|P|OP[12])$", re.I)
BaseAtomsRE = re.compile("^(C[245678]|C5M|N[1234679]|O[246])$", re.I)
BaseExceptRE = re.compile("^C1'$", re.I)
SugarAtomsRE = re.compile("^(C[1234]|O[24])'$", re.I)
SugarExceptRE = re.compile("^(C5|N[19]|C5'|O3')$", re.I)
SugarAtomsNoRibRE = re.compile("^(C[12]|O[24])'$", re.I)
SugarExceptNoRibRE = re.compile("^(C5|N[19]|C[34]')$", re.I)
class AlwaysRE:
	def match(self, text):
		return True
AlwaysRE = AlwaysRE()
class NeverRE:
	def match(self, text):
		return False
NeverRE = NeverRE()

## clockwise rings
#purine = ("N9", "C8", "N7", "C5", "C4")	# + pyrimidine
#pyrimidine = ("N1", "C6", "C5", "C4", "N3", "C2")
# counterclockwise rings
_purine = ("N9", "C4", "C5", "N7", "C8")	# without reversed pyrimidine
_full_purine = ("N9", "C4", "N3", "C2", "N1", "C6", "C5", "N7", "C8")
_full_purine_1 = (0, 1, 6, 7, 8)
_full_purine_2 = (1, 2, 3, 4, 5, 6)
_pyrimidine = ("N1", "C2", "N3", "C4", "C5", "C6")
_pyrimidine_1 = (0, 1, 2, 3, 4, 5)
_sugar = ("C1'", "C2'", "C3'", "C4'", "O4'")

ANCHOR = 'anchor'
BASE = 'base'
SUGAR = 'sugar'
PURINE = 'purine'
PYRIMIDINE = 'pyrimidine'
PSEUDO_PYRIMIDINE = 'pseudo-pyrimidine'

# Standard base geometries with C1'
#
# From "A Standard Reference Frame for the Description of Nucleic Acid
# Base-pair Geometry", Olsen et. al., J. Mol. Biol. (2001) V. 313, pp.
# 229-237.  A preliminary version is available for free at
# <http://ndbserver.rutgers.edu/archives/report/tsukuba/tsukuba.pdf>.
standard_bases = {
	'A': {
		"type":	PURINE,
		"ring atom names": _full_purine,
		"NDB color": "red",
		"C1'":	(-2.479, 5.346, 0.000),
		"N9":	(-1.291, 4.498, 0.000),
		"C8":	( 0.024, 4.897, 0.000),
		"N7":	( 0.877, 3.902, 0.000),
		"C5":	( 0.071, 2.771, 0.000),
		"C6":	( 0.369, 1.398, 0.000),
		"N6":	( 1.611, 0.909, 0.000),
		"N1":	(-0.668, 0.532, 0.000),
		"C2":	(-1.912, 1.023, 0.000),
		"N3":	(-2.320, 2.290, 0.000),
		"C4":	(-1.267, 3.124, 0.000),
		"other bonds": (("C1'", "N9"), ("C4", "C5"), ("C6", "N6"))
	},
	'C': {
		"type":	PYRIMIDINE,
		"ring atom names": _pyrimidine,
		"NDB color": "yellow",
		"C1'":	(-2.477, 5.402, 0.000),
		"N1":	(-1.285, 4.542, 0.000),
		"C2":	(-1.472, 3.158, 0.000),
		"O2":	(-2.628, 2.709, 0.001),
		"N3":	(-0.391, 2.344, 0.000),
		"C4":	( 0.837, 2.868, 0.000),
		"N4":	( 1.875, 2.027, 0.001),
		"C5":	( 1.056, 4.275, 0.000),
		"C6":	(-0.023, 5.068, 0.000),
		"other bonds": (("C1'", "N1"), ("O2", "C2"), ("C4", "N4"))
	},
	'G': {
		"type":	PURINE,
		"ring atom names": _full_purine,
		"NDB color": "green",
		"C1'":	(-2.477, 5.399, 0.000),
		"N9":	(-1.289, 4.551, 0.000),
		"C8":	( 0.023, 4.962, 0.000),
		"N7":	( 0.870, 3.969, 0.000),
		"C5":	( 0.071, 2.833, 0.000),
		"C6":	( 0.424, 1.460, 0.000),
		"O6":	( 1.554, 0.955, 0.000),
		"N1":	(-0.700, 0.641, 0.000),
		"C2":	(-1.999, 1.087, 0.000),
		"N2":	(-2.949, 0.139,-0.001),
		"N3":	(-2.342, 2.364, 0.001),
		"C4":	(-1.265, 3.177, 0.000),
		"other bonds": (("C1'", "N9"), ("C4", "C5"), ("C6", "O6"), ("N2", "C2"))
	},
	'I': {
		# inosine (NOS) -- like G, but without the N2
		# taken from RNAView, ndbserver.rutgers.edu
		"type":	PURINE,
		"ring atom names": _full_purine,
		"NDB color": "dark green",
		"C1'":	(-2.477, 5.399, 0.000),
		"N9":	(-1.289, 4.551, 0.000),
		"C8":	( 0.023, 4.962, 0.000),
		"N7":	( 0.870, 3.969, 0.000),
		"C5":	( 0.071, 2.833, 0.000),
		"C6":	( 0.424, 1.460, 0.000),
		"O6":	( 1.554, 0.955, 0.000),
		"N1":	(-0.700, 0.641, 0.000),
		"C2":	(-1.999, 1.087, 0.000),
		"N3":	(-2.342, 2.364, 0.001),
		"C4":	(-1.265, 3.177, 0.000),
		"other bonds": (("C1'", "N9"), ("C4", "C5"), ("C6", "O6"))
	},
	'P': {
		# pseudouridine (PSU) -- like U with the base ring flipped
		# (C1'->C5 not N1)
		# taken from RNAView, ndbserver.rutgers.edu
		"type":	PSEUDO_PYRIMIDINE,
		"ring atom names": _pyrimidine,
		"NDB color": "light gray",
		"C1'":	(-2.506, 5.371, 0.000),
		"N1":	( 1.087, 4.295, 0.000),
		"C2":	( 1.037, 2.915, 0.000),
		"O2":	( 2.036, 2.217, 0.000),
		"N3":	(-0.229, 2.383, 0.000),
		"C4":	(-1.422, 3.076, 0.000),
		"O4":	(-2.485, 2.453, 0.000),
		"C5":	(-1.284, 4.500, 0.000),
		"C6":	(-0.064, 5.048, 0.000),
		"other bonds": (("C1'", "C5"), ("O2", "C2"), ("C4", "O4"))
	},
	'T': {
		"type":	PYRIMIDINE,
		"ring atom names": _pyrimidine,
		"NDB color": "blue",
		"C1'":	(-2.481, 5.354, 0.000),
		"N1":	(-1.284, 4.500, 0.000),
		"C2":	(-1.462, 3.135, 0.000),
		"O2":	(-2.562, 2.608, 0.000),
		"N3":	(-0.298, 2.407, 0.000),
		"C4":	( 0.994, 2.897, 0.000),
		"O4":	( 1.944, 2.119, 0.000),
		"C5":	( 1.106, 4.338, 0.000),
		"C5M":	( 2.466, 4.961, 0.001),	# PDB V2
		"C7":	( 2.466, 4.961, 0.001),	# PDB V3
		"C6":	(-0.024, 5.057, 0.000),
		"other bonds": (("C1'", "N1"), ("O2", "C2"), ("C4", "O4"), ("C5", "C5M"), ("C5", "C7"))
	},
	'U': {
		"type":	PYRIMIDINE,
		"ring atom names": _pyrimidine,
		"NDB color": "cyan",
		"C1'":	(-2.481, 5.354, 0.000),
		"N1":	(-1.284, 4.500, 0.000),
		"C2":	(-1.462, 3.131, 0.000),
		"O2":	(-2.563, 2.608, 0.000),
		"N3":	(-0.302, 2.397, 0.000),
		"C4":	( 0.989, 2.884, 0.000),
		"O4":	( 1.935, 2.094,-0.001),
		"C5":	( 1.089, 4.311, 0.000),
		"C6":	(-0.024, 5.053, 0.000),
		"other bonds": (("C1'", "N1"), ("O2", "C2"), ("C4", "O4"))
	},
}
# map pyrminidine anchors to pseudopryimidine ones
pseudopyrimidine_anchor_map = {
	"C1'": "C1'",
	"N1": "C5",
	"C2": "C4",
	"O2": "C4",
	"N3": "N3",
	"C4": "C2",
	"O4": "C2",
	"C5": "N1",
	"C6": "C6",
}

# precompute bounding boxes
purine_min = purine_max = None
pyrimidine_min = pyrimidine_max = None
for b in standard_bases.values():
	min = max = None
	for coord in b.values():
		if len(coord) != 3 or not isinstance(coord[0], float):
			continue
		if min is None:
			min = list(coord)
			max = list(coord)
			continue
		if min[0] > coord[0]:
			min[0] = coord[0]
		elif max[0] < coord[0]:
			max[0] = coord[0]
		if min[1] > coord[1]:
			min[1] = coord[1]
		elif max[1] < coord[1]:
			max[1] = coord[1]
		if min[2] > coord[2]:
			min[2] = coord[2]
		elif max[2] < coord[2]:
			max[2] = coord[2]
	b['min coord'] = min
	b['max coord'] = max
	if b['type'] == PURINE:
		if purine_min is None:
			purine_min = list(min)
			purine_max = list(max)
		else:
			if purine_min[0] > min[0]:
				purine_min[0] = min[0]
			if purine_min[1] > min[1]:
				purine_min[1] = min[1]
			if purine_min[2] > min[2]:
				purine_min[2] = min[2]
			if purine_max[0] < max[0]:
				purine_max[0] = max[0]
			if purine_max[1] < max[1]:
				purine_max[1] = max[1]
			if purine_max[2] < max[2]:
				purine_max[2] = max[2]
	elif b['type'] == PYRIMIDINE:
		if pyrimidine_min is None:
			pyrimidine_min = min[:]
			pyrimidine_max = max[:]
		else:
			if pyrimidine_min[0] > min[0]:
				pyrimidine_min[0] = min[0]
			if pyrimidine_min[1] > min[1]:
				pyrimidine_min[1] = min[1]
			if pyrimidine_min[2] > min[2]:
				pyrimidine_min[2] = min[2]
			if pyrimidine_max[0] < max[0]:
				pyrimidine_max[0] = max[0]
			if pyrimidine_max[1] < max[1]:
				pyrimidine_max[1] = max[1]
			if pyrimidine_max[2] < max[2]:
				pyrimidine_max[2] = max[2]
pu = (purine_max[1] - purine_min[1])
py = (pyrimidine_max[1] - pyrimidine_min[1])
purine_pyrimidine_ratio = pu / (pu + py)
del b, coord, min, max, pu, py

# precompute z-plane rotation correction factor
zAxis = chimera.Vector(0, 0, 1)
for b in standard_bases.values():
	pts = [chimera.Point(*b[n]) for n in b["ring atom names"][0:2]]
	yAxis = pts[0] - pts[1]
	yAxis.normalize()
	yAxis.z = 0.0	# should be zero already
			# insurance, so yAxis is perpendicular to zAxis
	xAxis = chimera.cross(yAxis, zAxis)
	xf = chimera.Xform.xform(
		xAxis[0], yAxis[0], zAxis[0], 0.0,
		xAxis[1], yAxis[1], zAxis[1], 0.0,
		xAxis[2], yAxis[2], zAxis[2], 0.0,
		orthogonalize=True
	)
	# we can work in 2d because we know atoms are in z=0 plane
	#coords = [b[a][0:2] for a in atoms]
	#yAxis = [coords[0][0] - coords[1][0], coords[0][1] - coords[1][1]]
	#len = math.sqrt(yAxis[0] * yAxis[0] + yAxis[1] * yAxis[1])
	#yAxis[0] /= len
	#yAxis[1] /= len
	## x axis is perpendicular to y axis
	#xf = chimera.Xform.xform(
	#	yAxis[1], yAxis[0], 0.0, 0.0,
	#	-yAxis[0], yAxis[1], 0.0, 0.0,
	#	0.0, 0.0, 1.0, 0.0
	#)
	xf.invert()
	#axis, angle = xf.getRotation()
	#print "axis = %s, angle = %s" % (axis, angle)
	b["adjust"] = xf
del b, pts, xAxis, yAxis, zAxis, xf

SystemStyles = {
	# predefined styles in local coordinate frame
	# note: (0,0) corresponds to position of C1'
	'skinny': {
		ANCHOR: BASE,
		PURINE: ((0.0, -4.0), (2.1, 0.0)),
		PYRIMIDINE: ((0.0, -2.1), (2.1, 0.0)),
		PSEUDO_PYRIMIDINE: ((0.0, -2.1), (2.1, 0.0)),
	},
	'long': {
		ANCHOR: BASE,
		PURINE: ((0.0, -5.0), (2.1, 0.0)),
		PYRIMIDINE: ((0.0, -3.5), (2.1, 0.0)),
		PSEUDO_PYRIMIDINE: ((0.0, -3.5), (2.1, 0.0)),
	},
	'fat': {
		ANCHOR: SUGAR,
		PURINE: ((0.0, -4.87), (3.3, 0.0)),
		PYRIMIDINE: ((0.0, -2.97), (3.3, 0.0)),
		PSEUDO_PYRIMIDINE: ((0.0, -2.97), (3.3, 0.0)),
	},
	'big': {
		ANCHOR: SUGAR,
		PURINE: ((0.0, -5.47), (4.4, 0.0)),
		PYRIMIDINE: ((0.0, -3.97), (4.4, 0.0)),
		PSEUDO_PYRIMIDINE: ((0.0, -3.97), (4.4, 0.0)),
	},
}

_BaseAnchors = {
	PURINE: 'N9',
	PYRIMIDINE: 'N1',
	PSEUDO_PYRIMIDINE: 'C5'
}

def anchor(sugarOrBase, type):
	if sugarOrBase == SUGAR:
		return "C1'"
	return _BaseAnchors[type]

userStyles = {}
prefStyles = {}

pref = None
PREF_CATEGORY = "Nucleotides"
PREF_SLAB_STYLES = "slab styles"
TRIGGER_SLAB_STYLES = "SlabStyleChanged"

def findStyle(name):
	try:
		return userStyles[name]
	except KeyError:
		return SystemStyles.get(name, None)

def addStyle(name, info):
	exists = name in userStyles
	if exists and userStyles[name] == info:
		return
	userStyles[name] = info
	if not name:
		return
	prefStyles[name] = info
	from chimera import preferences
	preferences.save()
	chimera.triggers.activateTrigger(TRIGGER_SLAB_STYLES, name)

def removeStyle(name):
	del userStyles[name]
	del prefStyles[name]
	from chimera import preferences
	preferences.save()
	chimera.triggers.activateTrigger(TRIGGER_SLAB_STYLES, name)

def listStyles():
	return userStyles.keys() + SystemStyles.keys()

def initialize():
	global pref, userStyles, prefStyles
	from chimera import preferences
	pref = preferences.addCategory(PREF_CATEGORY,
						preferences.HiddenCategory)
	prefStyles = pref.setdefault(PREF_SLAB_STYLES, {})
	import copy
	userStyles = copy.deepcopy(prefStyles)
	chimera.triggers.addTrigger(TRIGGER_SLAB_STYLES)
initialize()

def NDBColors(residues):
	import Midas
	color_names = set(std['NDB color'] for std in standard_bases.values())
	colors = {}
	for n in color_names:
		colors[n] = []
	for r in residues:
		try:
			info = standard_bases[nucleic3to1[r.type]]
		except KeyError:
			continue
		color = info['NDB color']
		colors[color].append(r)
	for color, residues in colors.items():
		if residues:
			Midas.color(color, residues)
			Midas.ribcolor(color, residues)

def _molDict(mol):
	global _molHandler, _rebuildHandler
	try:
		# expect this to succeed most of the time
		return _data[mol]
	except KeyError:
		md = _data[mol] = {}
		md[RESIDUES] = weakref.WeakKeyDictionary()
		md[VRML] = None
		if _molHandler is None:
			_molHandler = chimera.triggers.addHandler('Model',
							_trackMolecules, None)
			_rebuildHandler = chimera.triggers.addHandler(
					'monitor changes', _rebuild, None)
		return md

from contextlib import contextmanager

@contextmanager
def blockUpdates():
	global _block
	_block += 1 
	yield
	_block -= 1

def _trackMolecules(triggerName, closure, changes):
	"""Model trigger handler""" 
	# Track when Molecules and VRML models are deleted to see if
	# they are ones that we're interested in.
	if _rebuilding:
		# don't care about molecule changes while we're rebuilding
		# the VRML models
		return
	if not changes:
		return
	if 'major' in changes.reasons:
		for mol in changes.modified:
			try:
				md = _data[mol]
			except KeyError:
				continue
			_needRebuild[mol] = None
	deleted = changes.deleted
	if not deleted:
		return
	# First remove all Molecules.  With weak dictionaries
	# most of this cleanup should be unnecessary.
	for mol in list(deleted):
		try:
			md = _data[mol]
		except KeyError:
			continue
		try:
			vrml = md[VRML]
			# our VRML models are always associated with mol,
			# so they should always be on the deleted list.
			deleted.remove(vrml)
		except KeyError:
			pass
		deleted.remove(mol)
		del _data[mol]
	# Now look for VRML models whose molecule still exists
	# so we can remove the nucleotides data and unhide any hidden atoms
	foundVRML = False
	for v in deleted:
		if not isinstance(v, chimera.VRMLModel):
			continue
		# find the parent molecule
		for mol in _data:
			try:
				if _data[mol][VRML] == v:
					break
			except KeyError:
				continue
		else:
			continue
		residues = _data[mol][RESIDUES].keys()
		del _data[mol]
		# unhide any atoms we would have hidden
		setHideAtoms(False, AlwaysRE, BackboneRE, residues)
		foundVRML = True
	# Since changing hide bits doesn't cause a rebuilding
	# of the molecule's display list, rebuild them all!
	if foundVRML:
		chimera.viewer.invalidateCache()
	if _data:
		return
	global _molHandler, _rebuildHandler
	chimera.triggers.deleteHandler('Model', _molHandler)
	_molHandler = None
	chimera.triggers.deleteHandler('monitor changes', _rebuildHandler)
	_rebuildHandler = None
	_needRebuild.clear()

def _rebuild(triggerName, closure, changes):
	"""'monitor changes' trigger handler""" 
	global _rebuilding
	if _block or not _needRebuild or _rebuilding:
		return
	_rebuilding = True
	for mol in _needRebuild:
		md = _molDict(mol)
		try:
			if md[VRML]:
				v = md[VRML]
				md[VRML] = None
				chimera.openModels.close(v)
		except (KeyError, chimera.error):
			# Either there's no previous VRML
			# model to close or it has already
			# been closed.
			pass
		# figure out which residues are of which type because
		# ladder needs knowledge about the whole molecule
		rds = md[RESIDUES]
		sides = {}
		for k in SideOptions:
			sides[k] = []
		for r in rds.keys():
			if r.__destroyed__:
				# Sometimes the residues are gone,
				# but there's a still reference to them.
				del rds[r]
				continue
			sides[rds[r]['side']].append(r)
		if not rds:
			# no residues to track in molecule
			v = md[VRML]
			if v:
				chimera.openModels.close(v)
			del _data[mol]
			continue
		allResidues = set(rds.keys())
		# make new VRML nodes
		hideSugars = set()
		hideBases = set()
		residues = sides['ladder']
		if not residues:
			md.pop('ladder params', None)
		else:
			# redo all ladder nodes
			hideSugars.update(residues)
			hideBases.update(residues)
			make_ladder(mol, residues, rds, **md['ladder params'])
		residues = sides['fill/slab']
		if residues:
			hideBases.update(make_slab(mol, residues, rds))
		residues = sides['tube/slab']
		if residues:
			hideSugars.update(residues)
			make_tube(mol, residues, rds)
			hideBases.update(make_slab(mol, residues, rds))
		residues = sides['orient']
		if residues:
			make_orient(mol, residues, rds)
		# make sure sugar/base atoms are hidden/shown
		showSugars = allResidues - hideSugars
		showBases = allResidues - hideBases
		showResidues = showSugars - hideBases
		showSugars.difference_update(showResidues)
		showBases.difference_update(showResidues)
		setHideAtoms(False, AlwaysRE, NeverRE, showResidues)
		setHideAtoms(False, BackboneSugarRE, NeverRE, showSugars)
		nonRibbonSugars = [r for r in hideSugars
				if not r.ribbonDisplay or not r.hasRibbon()]
		setHideAtoms(False, BackboneRE, NeverRE, nonRibbonSugars)
		setHideAtoms(False, BaseAtomsRE, BaseExceptRE, showBases)

		# open VRML model
		nodes = sum((rds[r][SUGAR] + rds[r][BASE] for r in rds), [])
		if nodes:
			vrml = nodesToVRML(nodes)
			vList = chimera.openModels.open(vrml, type='VRML',
				sameAs=mol, hidden=True,
				identifyAs='%s - Nucleotides' % mol.name)
			assert(len(vList) == 1)
			v = vList[0]
			mol.addAssociatedModel(v)
			md[VRML] = v
			SimpleSession.noAutoRestore(v)
	_needRebuild.clear()
	# Since changing hide bits doesn't cause a rebuilding
	# of the molecule's display list, rebuild them all!
	chimera.viewer.invalidateCache()
	_rebuilding = False

def setHideAtoms(hide, AtomsRE, exceptRE, residues):
	# Hide that atoms match AtomsRE and associated hydrogens.  If
	# a hidden atom is bonded to a displayed atom, then bring it back
	# except for the ones in exceptRE.  If a hidden atom is pseudobonded
	# to another atom, then hide the pseudobond.
	H = chimera.Element.H
	Smart = chimera.Bond.Smart
	Never = chimera.Bond.Never
	Always = chimera.Bond.Always
	for r in residues:
		atoms = []
		for a in r.oslChildren():
			if AtomsRE.match(a.name):
				atoms.append(a)
				continue
			if a.element.number != H:
				continue
			b = a.neighbors
			if not b:
				continue
			if AtomsRE.match(b[0].name):
				atoms.append(a)
		if not atoms:
			continue

		for ra in atoms:
			ra.hide = hide

		# set hide bit for atoms that bond to non-hidden atoms
		for ra in atoms:
			bondsMap = ra.bondsMap
			for a in bondsMap:
				if a in atoms:
					continue
				if exceptRE.match(a.name):
					continue
				b = bondsMap[a]
				d = b.display
				if d == Never:
					continue
				if d == Always or a.display:
					# bring back atom
					ra.hide = False

def _atom_color(atom):
	kwds = {}
	color = atom.color
	if not color:
		color = atom.molecule.color
	try:
		material = color.material
		kwds['specularColor'] = material.specular
		kwds['shininess'] = material.shininess / 128
	except AttributeError:
		pass
	color = color.rgba()
	kwds['color'] = color[:3]
	kwds['transparency'] = 1 - color[3]
	return kwds

def _ribbon_color(residue):
	kwds = {}
	color = residue.ribbonColor
	if not color:
		color = residue.molecule.color
	try:
		material = color.material
		kwds['specularColor'] = material.specular
		kwds['shininess'] = material.shininess / 128
	except AttributeError:
		pass
	color = color.rgba()
	kwds['color'] = color[:3]
	kwds['transparency'] = 1 - color[3]
	return kwds

cylAxis = chimera.Vector(0, 1, 0)
def drawCylinder(radius, ep0, ep1, **kw):
	t = vrml.Transform()
	t.translation = chimera.Point([ep0, ep1]).data()
	delta = ep1 - ep0
	height = delta.length
	axis = chimera.cross(cylAxis, delta)
	cos = (cylAxis * delta) / height
	angle = math.acos(cos)
	t.rotation = (axis[0], axis[1], axis[2], angle)
	c = vrml.Cylinder(radius=radius, height=height, **kw)
	t.addChild(c)
	return t

def skipNonStandardResidue(r):
	if r.type not in rescode.nucleic3to1:
		return True
	# confirm that residue is displayed
	c5p = r.findAtom("C5'")
	return not c5p or not c5p.display

def getRing(r, baseRing):
	"""Return atoms in nucleotide residue named by baseRing.

	All of the atoms must be present and displayed."""
	atoms = []
	for name in baseRing:
		a = r.findAtom(name)
		if a and a.display:
			atoms.append(a)
		else:
			return []
	# confirm they are in a ring
	# Use minimumRings because that will reuse cached ring information
	# from asking for atom radii.
	for a in atoms:
		if len(a.minimumRings()) == 0:
			return []		# not in a ring
	return atoms
	# this code checks that the atoms are in the same ring
	# use 9 since that is the maximun size we're interested in
	rings = atoms[0].allRings(sizeThreshold=9)
	for r in rings:
		ringAtoms = r.atoms
		if len(ringAtoms) != len(atoms):
			continue
		for a in atoms[1:]:
			if a not in ringAtoms:
				return []
		return atoms
	return []

def drawSlab(residue, style, thickness, orient, shape, showGly):
	try:
		t = residue.type
		if t in ('PSU', 'P'):
			n = 'P'
		elif t in ('NOS', 'I'):
			n = 'I'
		else:
			n = nucleic3to1[t]
	except KeyError:
		return None
	standard = standard_bases[n]
	ring_atom_names = standard["ring atom names"]
	atoms = getRing(residue, ring_atom_names)
	if not atoms:
		return None
	plane = chimera.Plane([a.coord() for a in atoms])
	info = findStyle(style)
	type = standard['type']
	slab_corners = info[type]
	origin = residue.findAtom(anchor(info[ANCHOR], type)).coord()
	origin = plane.nearest(origin)

	pts = [plane.nearest(a.coord()) for a in atoms[0:2]]
	yAxis = pts[0] - pts[1]
	yAxis.normalize()
	xAxis = chimera.cross(yAxis, plane.normal)
	xf = chimera.Xform.xform(
		xAxis[0], yAxis[0], plane.normal[0], origin[0],
		xAxis[1], yAxis[1], plane.normal[1], origin[1],
		xAxis[2], yAxis[2], plane.normal[2], origin[2]
	)
	xf.multiply(standard["adjust"])

	color_kwds = _atom_color(atoms[0])

	na = vrml.Transform()
	na.translation = xf.getTranslation().data()
	axis, angle = xf.getRotation()
	na.rotation = (axis[0], axis[1], axis[2], math.radians(angle))
	#xf.invert()	# invert so xf maps residue space to standard space

	halfThickness = thickness / 2.0

	t = vrml.Transform()
	na.addChild(t)
	llx, lly = slab_corners[0]
	urx, ury = slab_corners[1]
	t.translation = (llx + urx) / 2.0, (lly + ury) / 2.0, 0
	if shape == 'box':
		b = vrml.Box(size=(urx - llx, ury - lly, 2.0 * halfThickness),
				**color_kwds)
	elif shape == 'tube':
		radius = (urx - llx) / 2
		t.scale = 1, 1, halfThickness / radius
		b = vrml.Cylinder(radius=radius, height=(ury - lly),
				**color_kwds)
	elif shape == 'ellipsoid':
		# need to reach anchor atom
		t.scale = ((urx - llx) / 20 * _SQRT2, (ury - lly) / 20 * _SQRT2,
							.1 * halfThickness)
		b = vrml.Sphere(radius=10, **color_kwds)
	t.addChild(b)

	if showGly:
		c1p = residue.findAtom("C1'")
		ba = residue.findAtom(anchor(info[ANCHOR], type))
		if c1p and ba:
			c1p.hide = False
			ba.hide = False

	if not orient:
		return na

	# show slab orientation by putting "bumps" on surface
	if standard['type'] == PYRIMIDINE:
		t = vrml.Transform()
		na.addChild(t)
		t.translation = (llx + urx) / 2.0, (lly + ury) / 2, halfThickness
		t.addChild(vrml.Sphere(radius=halfThickness, **color_kwds))
	else:
		# purine
		t = vrml.Transform()
		na.addChild(t)
		t.translation = (llx + urx) / 2.0, lly + (ury - lly) / 3, halfThickness
		t.addChild(vrml.Sphere(radius=halfThickness, **color_kwds))
		t = vrml.Transform()
		na.addChild(t)
		t.translation = (llx + urx) / 2.0, lly + (ury - lly) * 2 / 3, halfThickness
		t.addChild(vrml.Sphere(radius=halfThickness, **color_kwds))
	return na

def slabNodes(residue, style=default.STYLE, thickness=default.THICKNESS,
		hide=default.HIDE, orient=default.ORIENT, shape=default.SHAPE,
		showGly=default.GLYCOSIDIC):
	node = drawSlab(residue, style, thickness, orient, shape, showGly)
	if node:
		return [node]
	return []

def bondsBetween(atoms):
	bonds = []
	for i in range(len(atoms) - 1):
		a = atoms[i]
		bondMap = a.bondsMap
		otherAtoms = atoms[i + 1:]
		for oa in otherAtoms:
			if oa in bondMap:
				bonds.append(bondMap[oa])
	return bonds

def orientPlanarRing(atoms, ringIndices=[], convex=True):
	r = atoms[0].residue
	if not r.fillDisplay or r.fillMode != chimera.Residue.Thick:
		# can't show orientation of thin nor aromatic ring
		return []
	pts = [a.coord() for a in atoms]
	bonds = bondsBetween(atoms)
	if chimera.Bond.Wire in [b.drawMode for b in bonds]:
		radius = 0
	else:
		radius = min([b.radius for b in bonds])
		radius *= atoms[0].molecule.stickScale
	color_kwds = _atom_color(atoms[0])
	if radius == 0:
		# can't show orientation of thin ring
		return []

	# non-zero radius
	planeEq = chimera.Plane(pts)
	offset = planeEq.normal * radius
	result = []
	for r in ringIndices:
		center = chimera.Point([pts[i] for i in r]) + offset
		t = vrml.Transform()
		t.translation = center.data()
		s = vrml.Sphere(radius=radius, **color_kwds)
		t.addChild(s)
		result.append(t)
	return result

class TriangleNode(vrml._Node):
	def __init__(self, **kw):
		self.coordList = []
		self.coordIndices = []
		self.colorList = []
		self.colorIndices = []
		vrml._Node.__init__(self, **kw)

	def writeNode(self, f, prefix=''):
		f.write('%sShape {\n' % prefix)
		self.writeAppearance(f, prefix)
		f.write('%s%sgeometry IndexedFaceSet {\n' % (prefix, vrml.Indent))
		p = prefix + vrml.Indent + vrml.Indent
		self.writeBooleanAttribute(f, p, 'ccw', 'ccw %s')
		self.writeBooleanAttribute(f, p, 'convex', 'convex %s')
		self.writeBooleanAttribute(f, p, 'solid', 'solid %s')
		self.writeAttribute(f, p, 'creaseAngle', 'creaseAngle %g')
		self.writeCoords(f, p)
		self.writeBooleanAttribute(f, p, 'normalPerVertex',
							'normalPerVertex %s')
		self.writeColors(f, p)
		self.writeBooleanAttribute(f, p, 'colorPerVertex',
							'colorPerVertex %s')
		f.write('%s%s}\n' % (prefix, vrml.Indent))
		f.write('%s}\n' % prefix)

	def writeCoords(self, f, prefix):
		if not self.coordList:
			return
		f.write(prefix)
		f.write('coord Coordinate { point [\n')
		p = prefix + vrml.Indent
		f.write(p)
		f.write((',\n' + p).join(["%g %g %g" % c for c in self.coordList]))
		f.write('\n')
		f.write(prefix)
		f.write('] }\n')

		if not self.coordIndices:
			return
		f.write(prefix)
		f.write('coordIndex [\n')
		f.write(p)
		f.write((' -1\n' + p).join(["%d %d %d" % i for i in self.coordIndices]))
		f.write('\n')
		f.write(prefix)
		f.write(']\n')

	def writeColors(self, f, prefix):
		if not self.colorList:
			return
		f.write(prefix)
		f.write('color Color { color [\n')
		p = prefix + vrml.Indent
		f.write(p)
		f.write((',\n' + p).join(["%g %g %g" % c for c in self.colorList]))
		f.write('\n')
		f.write(prefix)
		f.write('] }\n')

		if not self.colorIndices:
			return
		f.write(prefix)
		f.write('colorIndex [\n')
		f.write(p)
		f.write(('\n' + p).join(["%d" % i for i in self.colorIndices]))
		f.write('\n')
		f.write(prefix)
		f.write(']\n')

# Use planar_cutoff instead of zero, both to workaround floating
# point limitations and for meager data.
planar_cutoff = 0.1
# Use envelope_ratio to decide which forms should be shown as
# envelopes.  This is used in lieu of doing the full envelope
# calculation.
envelope_ratio = 3

def fill5Ring(atoms, c5p=None):
	pts = [a.coord() for a in atoms]
	bonds = bondsBetween(atoms)
	if chimera.Bond.Wire in [b.drawMode for b in bonds]:
		radius = 0
	else:
		radius = min([b.radius for b in bonds])
		radius *= atoms[0].molecule.stickScale
	color_kwds = _atom_color(atoms[0])

	# see how planar ring is
	indices = (0, 1, 2, 3, 4, 0, 1, 2, 3, 4)
	distC5p = None
	fake_bonds = [(0, 5), (1, 5), (2, 5), (3, 5), (4, 5)]
	for i in range(5):
		atoms[i].pucker = 'plane'

	# Find twist plane.  Note: due to floating point limitations,
	# dist3 and dist4 will virtually never be zero.
	for i in range(5):
		planeEq = chimera.Plane([pts[indices[j]] for j in range(i, i + 3)])
		dist3 = planeEq.distance(pts[indices[i + 3]])
		dist4 = planeEq.distance(pts[indices[i + 4]])
		if c5p:
			distC5p = planeEq.distance(c5p.coord())
		if dist3 == 0 or dist4 == 0 \
		or (dist3 < 0 and dist4 > 0) or (dist3 > 0 and dist4 < 0):
			break

	abs_dist3 = abs(dist3)
	abs_dist4 = abs(dist4)
	if abs_dist3 < planar_cutoff and abs_dist4 < planar_cutoff:
		# planar, new_vertex is centroid of pts
		new_vertex = chimera.Point(pts)
	elif abs_dist3 < abs_dist4 and abs_dist4 / abs_dist3 >= envelope_ratio:
		# envelope, new_vertex is mid-point of separating edge
		new_vertex = chimera.Point([pts[indices[i]], pts[indices[i + 3]]])
		atoms[indices[i + 4]].pucker = 'envelope'
		del fake_bonds[indices[i + 4]]
	elif abs_dist4 < abs_dist3 and abs_dist3 / abs_dist4 >= envelope_ratio:
		# envelope, new_vertex is mid-point of separating edge
		new_vertex = chimera.Point([pts[indices[i + 2]], pts[indices[i + 4]]])
		atoms[indices[i + 3]].pucker = 'envelope'
		del fake_bonds[indices[i + 3]]
	else: # if (dist3 < 0 and dist4 > 0) or (dist3 > 0 and dist4 < 0):
		# twist, new_vertex is placed in twist plane near twist pts
		centroid = chimera.Point([
			pts[indices[i + 1]],
			pts[indices[i + 3]],
			pts[indices[i + 4]]
		])
		new_vertex = planeEq.nearest(centroid)
		del fake_bonds[indices[i + 1]]
		if cmp(dist3, 0) == cmp(distC5p, 0):
			atoms[indices[i + 3]].pucker = 'endo'
		else:
			atoms[indices[i + 3]].pucker = 'exo'
		if cmp(dist4, 0) == cmp(distC5p, 0):
			atoms[indices[i + 4]].pucker = 'endo'
		else:
			atoms[indices[i + 4]].pucker = 'exo'
	pts.append(new_vertex)		# new_vertex has index 5
	triangles = ((0, 1, 5), (1, 2, 5), (2, 3, 5), (3, 4, 5), (4, 0, 5))

	if radius == 0:
		f = TriangleNode(solid=False,
			coordList=[p.data() for p in pts],
			coordIndices=triangles,
			colorPerVertex=False, **color_kwds
		)
		return [f]

	# non-zero radius
	f = vrml.Faces(**color_kwds)
	for t in triangles:
		# t is a list of 3 indices
		t = [pts[i] for i in t]
		# t is a list of 3 Points
		planeEq = chimera.Plane(t)
		offset = planeEq.normal * radius
		top = [(p + offset).data() for p in t]
		bot = [(p - offset).data() for p in t]
		f.addFace(top)
		if 1:
			# STL wants manifold objects
			for i in range(len(t) - 1):
				f.addFace([top[i], bot[i], bot[i + 1], top[i + 1]])
			f.addFace([top[-1], bot[-1], bot[0], top[0]])
		bot.reverse()
		f.addFace(bot)
	result = [f]
	for b in fake_bonds:
		node = drawCylinder(radius, pts[b[0]], pts[b[1]], **color_kwds)
		result.append(node)
	t = vrml.Transform()
	t.translation = pts[5].data()
	s = vrml.Sphere(radius=radius, **color_kwds)
	t.addChild(s)
	result.append(t)
	return result


def drawOrientation(residue):
	c5p = residue.findAtom("C5'")
	if not c5p:
		return []
	ring = getRing(residue, _full_purine)
	if ring:
		indices = [_full_purine_1, _full_purine_2]
		ringNodes = orientPlanarRing(ring, indices, convex=False)
		return ringNodes
	ring = getRing(residue, _pyrimidine)
	if ring:
		indices = [_pyrimidine_1]
		ringNodes = orientPlanarRing(ring, indices)
		return ringNodes
	return []

def sugarTube(residue, anchor=SUGAR, showGly=False):
	if anchor is SUGAR:
		showGly = False
	if anchor is SUGAR or showGly:
		aname = "C1'"
	else:
		try:
			t = residue.type
			if t in ('PSU', 'P'):
				n = 'P'
			elif t in ('NOS', 'I'):
				n = 'I'
			else:
				n = nucleic3to1[t]
			type = standard_bases[n]['type']
		except KeyError:
			return []
		aname = _BaseAnchors[type]
		if not aname:
			return []
	a = residue.findAtom(aname)
	if not a or not a.display:
		return []
	ep0 = a.coord()
	radius = a.molecule.stickScale * chimera.Molecule.DefaultBondRadius
	color_kwds = _atom_color(a)

	# calculate position between C3' and C4' on ribbon
	hasRibbon = residue.ribbonDisplay and residue.hasRibbon()
	if hasRibbon:
		rrc = residue.ribbonResidueClass
		found, o3pPos = rrc.position("O3'")
		if not found:
			return []
		found, c5pPos = rrc.position("C5'")
		if not found:
			return []
		s = chimera.Spline(chimera.Spline.BSpline,
						residue.ribbonCenters())
		ep1 = s.coordinate((o3pPos + c5pPos) / 2)
	else:
		c3p = residue.findAtom("C3'")
		if not c3p:
			return []
		c4p = residue.findAtom("C4'")
		if not c4p:
			return []
		ep1 = chimera.Point([c3p.coord(), c4p.coord()])

	node = drawCylinder(radius, ep0, ep1, **color_kwds)

	setHideAtoms(True, SugarAtomsRE, SugarExceptRE, [residue])
	return [node]

def _c3pos(residue):
	c3p = residue.findAtom("C3'")
	if not c3p:
		return None
	if residue.ribbonDisplay and residue.hasRibbon():
		rrc = residue.ribbonResidueClass
		found, o3pPos = rrc.position("O3'")
		if found:
			found, c5pPos = rrc.position("C5'")
			if found:
				s = chimera.Spline(chimera.Spline.BSpline,
						residue.ribbonCenters())
				return c3p, s.coordinate((o3pPos + c5pPos) / 2)
	return c3p, c3p.coord()

def set_normal(molecules, residues):
	rds = {}
	for m in molecules:
		md = _molDict(m)
		rds[m] = md[RESIDUES]
	changed = set()
	for r in residues:
		if rds[r.molecule].pop(r, None) is not None:
			changed.add(r)
			_needRebuild[r.molecule] = None
	setHideAtoms(False, AlwaysRE, BackboneRE, changed)

def set_orient(molecules, residues):
	mds = {}
	for m in molecules:
		md = _molDict(m)
		mds[m] = md
	for r in residues:
		rd = mds[r.molecule][RESIDUES].setdefault(r, {})
		cur_side = rd.get('side', None)
		if cur_side == 'orient':
			continue
		_needRebuild[r.molecule] = None
		rd.pop('slab params', None)
		rd.pop('tube params', None)
		rd['side'] = 'orient'
		rd[SUGAR] = []
		rd[BASE] = []

def make_orient(mol, residues, rds):
	for r in residues:
		rds[r][BASE] = drawOrientation(r)

def set_slab(side, molecules, residues, **slab_params):
	if not side.startswith('tube'):
		tube_params = None
	else:
		info = findStyle(slab_params.get('style', default.STYLE))
		tube_params = {
			'showGly': slab_params.get('showGly', default.GLYCOSIDIC),
			ANCHOR: info[ANCHOR],
		}
	mds = {}
	for m in molecules:
		md = _molDict(m)
		mds[m] = md
	for r in residues:
		rd = mds[r.molecule][RESIDUES].setdefault(r, {})
		cur_side = rd.get('side', None)
		if cur_side == side:
			cur_params = rd.get('slab params', None)
			if cur_params == slab_params:
				continue
		_needRebuild[r.molecule] = None
		rd['slab params'] = slab_params
		if not tube_params:
			rd.pop('tube params', None)
		else:
			rd['tube params'] = tube_params
		rd['side'] = side
		rd[SUGAR] = []
		rd[BASE] = []

def make_slab(mol, residues, rds):
	hideBases = set()
	for r in residues:
		params = rds[r]['slab params']
		if params.get('hide', default.HIDE):
			hideBases.add(r)
			setHideAtoms(True, BaseAtomsRE, BaseExceptRE, [r])
		vrml = rds[r][BASE] = slabNodes(r, **params)
		if not vrml:
			hideBases.discard(r)
	return hideBases

def make_tube(mol, residues, rds):
	# should be called before make_slab
	for r in residues:
		rds[r][SUGAR] = sugarTube(r, **rds[r]['tube params'])

def set_ladder(molecules, residues, **ladder_params):
	mds = {}
	for m in molecules:
		md = _molDict(m)
		mds[m] = md
		cur_params = md.get('ladder params', None)
		if cur_params is not None:
			if cur_params == ladder_params:
				continue
			_needRebuild[m] = None
		md['ladder params'] = ladder_params
	for r in residues:
		rd = mds[r.molecule][RESIDUES].setdefault(r, {})
		cur_side = rd.get('side', None)
		if cur_side == 'ladder':
			continue
		_needRebuild[r.molecule] = None
		rd.pop('slab params', None)
		rd.pop('tube params', None)
		rd['side'] = 'ladder'
		rd[SUGAR] = []
		rd[BASE] = []

def make_ladder(mol, residues, rds, **ladder_params):
	info = ladder([mol], residues, **ladder_params)
	for r, node in info.items():
		rds[r][BASE] = node
	setHideAtoms(True, AlwaysRE, BackboneRE, residues)

def ladder(molecules, residues, rungRadius=0, showStubs=True, skipNonBaseHBonds=False, useExisting=False, distSlop=0.0, angleSlop=0.0):
	"""generate links between residues that are hydrogen bonded together"""
	result = {}
	# create list of atoms from residues for donors and acceptors
	atoms = set()
	for r in residues:
		atoms.update(r.atoms)
	if useExisting:
		mgr = chimera.PseudoBondMgr.mgr()
		pbg = mgr.findPseudoBondGroup("hydrogen bonds")
		if not pbg:
			bonds = ()
		else:
			bonds = (p.atoms for p in pbg.pseudoBonds)
	else:
		import FindHBond
		bonds = FindHBond.findHBonds(molecules, intermodel=False,
				donors=atoms, acceptors=atoms,
				distSlop=distSlop, angleSlop=angleSlop)
	matchedResidues = set()
	for a0, a1 in bonds:
		nonBase = (BackboneSugarRE.match(a0.name),
					BackboneSugarRE.match(a1.name))
		nonBaseBaseHBond = any(nonBase)
		if skipNonBaseHBonds and nonBaseBaseHBond:
			continue
		r0 = a0.residue
		r1 = a1.residue
		if chimera.bondsBetween(r0, r1, onlyOne=True):
			# skip covalently bonded residues
			continue
		c3p0 = _c3pos(r0)
		if not c3p0:
			continue
		c3p1 = _c3pos(r1)
		if not c3p1:
			continue
		if not nonBaseBaseHBond and rungRadius:
			radius = rungRadius
		elif r0.ribbonDisplay and r1.ribbonDisplay:
			style = r0.ribbonFindStyle()
			radius = min(style.width(.5), style.thickness(.5))
		else:
			radius = a0.molecule.stickScale \
					* chimera.Molecule.DefaultBondRadius
		r0color_kwds = _ribbon_color(r0)
		r1color_kwds = _ribbon_color(r1)
		# choose mid-point to make purine larger
		try:
			isPurine0 = standard_bases[nucleic3to1[r0.type]]['type'] == PURINE
			isPurine1 = standard_bases[nucleic3to1[r1.type]]['type'] == PURINE
		except KeyError:
			isPurine0 = False
			isPurine1 = False
		if nonBaseBaseHBond or isPurine0 == isPurine1:
			mid = 0.5
		elif isPurine0:
			mid = purine_pyrimidine_ratio
		else:
			mid = 1.0 - purine_pyrimidine_ratio
		midpt = chimera.lerp(c3p0[1], c3p1[1], mid)
		nodes = [
			drawCylinder(radius, c3p0[1], midpt, **r0color_kwds),
			drawCylinder(radius, midpt, c3p1[1], **r1color_kwds)
		]
		if r0 in result:
			result[r0].extend(nodes)
		else:
			result[r0] = nodes
		if not nonBase[0]:
			matchedResidues.add(r0)
		if not nonBase[1]:
			matchedResidues.add(r1)
	if not showStubs:
		return result
	# draw stubs for unmatched nucleotide residues
	for r in residues:
		if r in matchedResidues:
			continue
		c3p = _c3pos(r)
		if not c3p:
			continue
		ep0 = c3p[1]
		color_kwds = _ribbon_color(r)
		# find farthest atom from C3'
		dist_atom = (0, None)
		for a in r.atoms:
			dist = ep0.sqdistance(a.coord())
			if dist > dist_atom[0]:
				dist_atom = (dist, a)
		ep1 = dist_atom[1].coord()
		node = drawCylinder(rungRadius, ep0, ep1, **color_kwds)
		if r in result:
			result[r].append(node)
		else:
			result[r] = [node]
	return result

def nodesToVRML(nodes):
	return vrml.vrml(nodes)

def save_session(trigger, closure, file):
	"""convert data to session data"""
	if not _data:
		return
	# molecular data
	mdata = {}
	for m in _data:
		md = _data[m]
		mid = SimpleSession.sessionID(m)
		smd = mdata[mid] = {}
		for k in md:
			if k.endswith('params'):
				smd[k] = md[k]
		rds = md[RESIDUES]
		srds = smd[RESIDUES] = {}
		for r in rds:
			rid = SimpleSession.sessionID(r)
			rd = rds[r]
			srd = srds[rid] = {}
			for k in rd:
				if k.endswith('params'):
					srd[k] = rd[k]
			srd['side'] = rd['side']
	# save restoring code in session
	restoring_code = (
"""
def restoreNucleotides():
	import NucleicAcids as NA
	NA.restoreState(%s, %s)
try:
	restoreNucleotides()
except:
	reportRestoreError('Error restoring Nucleotides')
""")
	file.write(restoring_code % (
		SimpleSession.sesRepr(mdata),
		SimpleSession.sesRepr(userStyles)
	))

def restoreState(mdata, sdata={}):
	for name, info in sdata.items():
		addStyle(name, info)
	for mid in mdata:
		m = SimpleSession.idLookup(mid)
		md = _molDict(m)
		smd = mdata[mid]
		for k in smd:
			if k.endswith('params'):
				md[k] = smd[k]
		rds = md[RESIDUES]
		srds = smd[RESIDUES]
		for rid in srds:
			r = SimpleSession.idLookup(rid)
			rd = rds[r] = srds[rid]
			rd[SUGAR] = []
			rd[BASE] = []
		_needRebuild[m] = None

chimera.triggers.addHandler(SimpleSession.SAVE_SESSION, save_session, None)

if __name__ == "__main__":
	mols = chimera.openModels.list(modelTypes=[chimera.Molecule])
	vrmlModels = []
	for m in mols:
		nodes = vrml.Group()
		for r in m.residues:
			node = drawSlab(r, 'big', 0.5, True, True)
			if node:
				nodes.addChild(node)
		if nodes.children:
			vrmlModels.append((m, nodes))

	if vrmlModels:
		for m, nodes in vrmlModels:
			v = vrml.vrml(nodes)
			#print v
