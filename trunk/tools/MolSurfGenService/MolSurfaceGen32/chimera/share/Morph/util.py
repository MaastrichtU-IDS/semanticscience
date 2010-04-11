PreferredAtoms = [
	"CA",
	"P",
	"N",
	"C",
	"O5'",
	"O3'",
]

def getAtomList(rList):
	"""Construct a list of CA/P atoms from residue list (ignoring
	residues that do not have either atom)"""
	aList = []
	if len(rList) > 2:
		atomsPerResidue = 1
	elif len(rList) > 1:
		atomsPerResidue = 2
	else:
		atomsPerResidue = 3
	for r in rList:
		atoms = set([])
		failed = False
		while len(atoms) < atomsPerResidue:
			for aname in PreferredAtoms:
				a = findPrimaryAtom(r, aname)
				if a is None or a in atoms:
					continue
				atoms.add(a)
				break
			else:
				for a in residuePrimaryAtoms(r):
					if a not in atoms:
						atoms.add(a)
						break
				else:
					failed = True
			if failed:
				break
		aList.extend(atoms)
	#print "%d residues -> %d atoms" % (len(rList), len(aList))
	return aList

def findPrimaryAtom(r, aname):
	pAtomSet = primaryAtomSet(r.molecule)
	try:
		for a in r.atomsMap[aname]:
			if a in pAtomSet:
				return a
	except KeyError:
		return None

def residuePrimaryAtoms(r):
	return set(r.atoms).intersection(primaryAtomSet(r.molecule))

def primaryAtomSet(m):
	try:
		return m.primaryAtomSet
	except AttributeError:
		m._primaryAtomSet = set(m.primaryAtoms())
		return m._primaryAtomSet

from chimera.baseDialog import ModalDialog
class WaitForInputDialog(ModalDialog):

	buttons = ( "Okay" )
	oneshot = True
	
	def fillInUI(self, parent):
		import Tkinter
		l = Tkinter.Label(parent, text="Click Okay to continue")
		l.grid(row=0, column=0, sticky="nsew")
		
	def Okay(self):
		ModalDialog.Cancel(self)
		
def waitForInput():
	"""Pop up a dialog and way for user to click okay"""
	from chimera.tkgui import app
	app.update_idletasks()
	WaitForInputDialog().run(app)

_MoleculeAttrList = [
	"autochain",
	"ballScale",
	"color",
#	"display",
	"lineWidth",
	"name",
	"openedAs",
	"pointSize",
	"ribbonHidesMainchain",
	"stickScale",
	"surfaceColor",
	"surfaceOpacity",
	"vdwDensity",
	"wireStipple",
]
_ResidueAttrList = [
	"isHelix",
	"isHet",
	"isSheet",
	"isTurn",
	"label",
	"labelColor",
	"labelOffset",
	"ribbonColor",
	"ribbonDisplay",
	"ribbonDrawMode",
	"ribbonResidueClass",
	"ribbonStyle",
	"ribbonXSection",
]
_AtomAttrList = [
# Don't copy altLoc since we're only using primary locations
#	"altLoc",
	"bfactor",
	"color",
	"display",
	"drawMode",
	"label",
	"labelColor",
	"labelOffset",
	"occupancy",
	"radius",
	"serialNumber",
	"surfaceCategory",
	"surfaceColor",
	"surfaceDisplay",
	"surfaceOpacity",
	"vdw",
	"vdwColor",
]
_BondAttrList = [
	"color",
	"display",
	"drawMode",
	"halfbond",
	"label",
	"labelColor",
	"labelOffset",
	"radius",
]

def _copyAttributes(f, t, attrList):
	for attr in attrList:
		try:
			value = getattr(f, attr)
		except AttributeError:
			pass
		else:
			setattr(t, attr, value)

def copyMolecule(m, copyXformCoords=False):
	"""Copy molecule and return both copy and map of corresponding atoms"""
	# Copied from PDBmatrices.copy_molecule
	import chimera
	cm = chimera.Molecule()
	cs = cm.newCoordSet(1)
	cm.activeCoordSet = cs
	_copyAttributes(m, cm, _MoleculeAttrList)
	try:
		headers = getattr(m, "pdbHeaders")
	except AttributeError:
		pass
	else:
		cm.setAllPDBHeaders(headers)

	residueMap = {}
	for r in m.residues:
		cr = cm.newResidue(r.type, r.id)
		_copyAttributes(r, cr, _ResidueAttrList)
		residueMap[r] = cr

	atomMap = {}
	for a in primaryAtomSet(m):
		ca = cm.newAtom(a.name, a.element)
		if copyXformCoords:
			ca.setCoord(a.xformCoord())
		else:
			ca.setCoord(a.coord())
		_copyAttributes(a, ca, _AtomAttrList)
		atomMap[a] = ca
		residueMap[a.residue].addAtom(ca)

	for b in m.bonds:
		a1, a2 = b.atoms
		try:
			na1 = atomMap[a1]
			na2 = atomMap[a2]
		except KeyError:
			# At least one of the atom was not mapped,
			# so don't bother creating the bond
			pass
		else:
			cb = cm.newBond(na1, na2)
			_copyAttributes(b, cb, _BondAttrList)

	return cm, atomMap, residueMap

def mapAtoms(m0, m1, ignoreUnmatched=False):
	atomMap = {}
	residueMap = mapResidues(m0, m1)
	for a0 in primaryAtomSet(m0):
		r0 = a0.residue
		r1 = residueMap[r0]
		try:
			if r1 is None:
				raise ValueError("no residue corresponds to %s"
							% r0.oslIdent())
			a1 = findPrimaryAtom(r1, a0.name)
			if a1 is None:
				raise ValueError("no atom corresponds to %s"
							% a0.oslIdent())
			atomMap[a0] = a1
		except ValueError:
			if not ignoreUnmatched:
				raise
	return atomMap

def mapResidues(m0, m1):
	residueMap = {}
#	for r0 in m0.residues:
#		r1 = m1.findResidue(r0.id)
#		if r1 is None:
#			raise ValueError("no residue corresponds to %s"
#						% r0.oslIdent())
#		residueMap[r0] = r1
	residueMap.update(zip(m0.residues, m1.residues))
	return residueMap

def runMovie(m, xform):
	class MorphTraj:
		def __len__(self):
			return len(self.molecule.coordSets)
		def __getitem__(self, key):
			print "getitem", key
			return None
	ensemble = MorphTraj()
	ensemble.name = "Molecular Movement of %s" % m.name
	keys = m.coordSets.keys()
	# Assume that keys is contiguous block of integers
	ensemble.startFrame = min(keys)
	ensemble.endFrame = max(keys)
	ensemble.molecule = m
	import chimera
	# Trajectory insists on adding molecules to Chimera list,
	# so we remove it first to avoid a duplication error
	chimera.openModels.remove([m])
	from Movie.gui import MovieDialog
	d = MovieDialog(ensemble, shareXform=False)
	m.openState.xform = xform
	return d

def timestamp(s):
	import time
	print "%s: %s" % (time.ctime(time.time()), s)

def findBestMatch(input, choices):
	bestMatch = None
	for choice in choices:
		if choice.startswith(input):
			if bestMatch is not None:
				raise ValueError("\"%s\" is ambiguous" % input)
			else:
				bestMatch = choice
	if bestMatch is None:
		raise ValueError("\"%s\" does not match any available choice"
				% input)
	return bestMatch
