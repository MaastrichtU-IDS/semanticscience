import chimera
from chimera import replyobj

process = "charge addition"
ATTR_SET = "attribute set"

class ChargeError(RuntimeError):
	pass

AMBER99SB = "AMBER ff99SB"
AMBER99bsc0 = "AMBER ff99bsc0"
AMBER02pol_r1 = "AMBER ff02pol.r1"
AMBER03ua = "AMBER ff03ua"
AMBER03 = "AMBER ff03"
AMBER03_r1 = "AMBER ff03.r1"
defaultChargeModel = AMBER99SB
knownChargeModels = [AMBER99SB, AMBER99bsc0, AMBER02pol_r1, AMBER03ua,
							AMBER03, AMBER03_r1]

def initiateAddCharges(models=None, method=None, gaffType=True, status=None,
			cb=None, nogui=False, amberNucleicPhosphorylation=None,
			chargeModel=None, labelStandard=False, labelNonstandard=False):
	"""add AMBER/GAFF charges to models

	   'models' and 'status' are the same as the arguments for
	   addStandardCharges.  'cb' is a callback function to call
	   when charges have been added.  It will be called with two
	   dictionary arguments which are the same format as the return
	   value of addStandardCharges. 'method' is either "am1-bcc" or
	   "gasteiger" and specifies the charge method used by antechamber
	   (None = specified by user).  'amberNucleicPhosphorylation'
	   controls whether chain-terminal nucleic-acid phosphorylation will
	   be changed to that expected by AMBER charge files (3' phosphorylated,
	   5' not); if the value is None then the user will be queried 
	   (unless in nogui mode, in which case it is treated as True).
	   'chargeModel' controls what iteration of the AMBER force field
	   the charges are taken from (if None, use defaultChargeModel).
	   'labelStandard/Nonstandard' controls whether atomic label showing
	   charges will be added after assignment for residues of the
	   appropriate type.

	   Hydrogens need to be present.

	   In nogui mode, this calls addStandardCharges() and
	   then addNonstandardResCharges() for each residue type without
	   charges (using a guesstimated net charge) and then the cb()
	   function.  If the proper net charges are known, it is
	   probably better just to call addStandardCharges() and then
	   addNonstandardResCharges() directly.

	   In gui mode, addStandardCharges() will be run and then for
	   any unknown residues the user will be queried for the net
	   charge and addNonstandardResCharges() will be invoked for
	   those residues.  Then the 'cb' function will be called.
	"""
	def doneCB(ur, ua, cb=cb, status=status, models=models):
		if status:
			status("Done adding charges\n")
		if models is None:
			models = chimera.openModels.list(
						modelTypes=[chimera.Molecule])
		warnMsg = ""
		if ur:
			warnMsg += "Correct charges are unknown for %d"\
				" non-standard residue types\n\n" % len(ur)
			replyobj.info("Non-standard residue types:\n")
			for t, rs in ur.items():
				info = ", ".join([str(r)
						for r in rs[:3]])
				if len(rs) > 3:
					info += " + %d others" % (
						len(rs) - 3)
				replyobj.info("\t%s (%s)\n" % (t, info))
		warnMsg = unchargedAtomsWarning(ua, warning=warnMsg)
		if warnMsg:
			warnMsg += "Charges of 0.0 were assigned to the" \
							" unknown atoms\n\n"
		nonIntegral = []
		from math import floor
		numNImodels = 0
		def isNonIntegral(val):
			return abs(floor(val+0.5) - val) > 0.0005
		for m in models:
			totCharge = 0.0
			for r in m.residues:
				resCharge = 0.0
				for a in r.atoms:
					resCharge += getattr(a, 'charge', 0.0)
				totCharge += resCharge
				if isNonIntegral(resCharge):
					nonIntegral.append((r, resCharge))
			tChargeMsg = "Total charge for %s: %.4f\n" % (str(m),
								totCharge)
			replyobj.info(tChargeMsg)
			if status:
				status(tChargeMsg)
			if isNonIntegral(totCharge):
				numNImodels += 1
		if nonIntegral:
			if numNImodels:
				warnMsg += "%d model(s) had non-integral total"\
						" charge\n" % numNImodels
			replyobj.info("The following residues had non-integral"
							" charges:\n")
			for r, charge in nonIntegral:
				replyobj.info("\t%s %g\n" % (str(r), charge))
		if warnMsg:
			warnMsg += "Details in reply log\n"
			replyobj.warning(warnMsg, help="ContributedSoftware/addcharge/addcharge.html#warnings")
		if cb:
			cb(ur, ua)

	unchargedResidues, unchargedAtoms = addStandardCharges(models=models,
		status=status, phosphorylation=amberNucleicPhosphorylation,
		chargeModel=chargeModel, nogui=nogui, showCharges=labelStandard)
	if not unchargedResidues:
		doneCB(unchargedResidues, unchargedAtoms)
		return

	for residues in unchargedResidues.values():
		for r in residues:
			for a in r.atoms:
				a.charge = None # in case dialog is cancelled
				if labelStandard: # undo labelling
					a.label = ""
	if nogui or chimera.nogui:
		if method is None:
			from prefs import prefs, CHARGE_METHOD
			method = prefs[CHARGE_METHOD].lower()
		for resType, residues in unchargedResidues.items():
			try:
				addNonstandardResCharges(residues,
					estimateNetCharge(residues[0].atoms),
					gaffType=gaffType, showCharges=labelNonstandard,
					method=method, status=status)
			except ChargeError:
				continue
			else:
				del unchargedResidues[resType]
		doneCB(unchargedResidues, unchargedAtoms)
	else:
		from gui import NonstandardChargeDialog
		NonstandardChargeDialog(doneCB, unchargedResidues,
				unchargedAtoms, method, status, gaffType,
				showCharges=labelNonstandard)

def addStandardCharges(models=None, status=None, phosphorylation=None,
				chargeModel=None, nogui=False, showCharges=False):
	"""add AMBER charges to well-known residues

	   'models' restricts the addition to the specified models

	   'status' is where status messages go (e.g. replyobj.status)

	   'phosphorylation' controls whether chain-terminal nucleic acids
	   will have their phosphorylation state changed to correspond to
	   AMBER charge files (3' phosphorylated, 5' not).  A value of None
	   means that the user will be queried if possible [treated as True
	   if not possible].

	   'showCharges' controls whether atoms get labeled with their charge.

	   The return value is a 2-tuple of dictionaries:  the first of which
	   details the residues that did not receive charges [key: residue
	   type, value: list of residues], and the second lists remaining
	   uncharged atoms [key: (residue type, atom name), value: list of
	   atoms]

	   Hydrogens need to be present.
	"""

	from AddAttr import addAttributes
	import os.path
	attrFile = os.path.join(os.path.split(__file__)[0],
						"amberName.defattr")
	if status:
		status("Defining AMBER residue types\n")
	addAttributes(attrFile, models=models, raiseAttrDialog=False)

	if models is None:
		mols = chimera.openModels.list(modelTypes=[chimera.Molecule])
	else:
		mols = models

	if phosphorylation != False:
		if status:
			status("Checking phosphorylation of chain-terminal"
							" nucleic acids\n")
		likeAmber = True
		deletes = []
		for m in mols:
			for r in m.residues:
				amberName = getattr(r, 'amberName', "UNK")
				if len(amberName) != 2 \
				or amberName[0] not in 'DR' \
				or amberName[1] not in 'ACGTU' \
				or 'P' not in r.atomsMap:
					continue
				p = r.atomsMap['P'][0]
				for nb in p.neighbors:
					if nb.residue != r:
						break
				else:
					# trailing phosphate
					deletes.append(r)
		if deletes:
			if phosphorylation is None:
				if nogui or chimera.nogui:
					phosphorylation = True
				else:
					from gui import PhosphorylateDialog
					phosphorylation = PhosphorylateDialog(
							).run(chimera.tkgui.app)
			if phosphorylation:
				_phosphorylate(mols, status, deletes)
	if status:
		status("Adding standard charges\n")
	unchargedResTypes = {}
	unchargedAtoms = {}
	unchargedResidues = set()
	from dict import ffChargeTypeData
	from SimpleSession import registerAttribute
	registerAttribute(chimera.Molecule, "chargeModel")
	registerAttribute(chimera.Atom, "gaffType")
	if chargeModel == None:
		chargeModel = defaultChargeModel
	replyobj.info("Charge model: %s\n" % chargeModel)
	chargeTypeData = ffChargeTypeData[chargeModel]
	track = chimera.TrackChanges.get()
	for m in mols:
		m.chargeModel = chargeModel
		track.addModified(m, ATTR_SET)
		for r in m.residues:
			if getattr(r, '_solvateCharged', False):
				continue
			if not hasattr(r, 'amberName'):
				unchargedResidues.add(r)
				unchargedResTypes.setdefault(r.type,
								[]).append(r)
		for a in m.atoms:
			if getattr(a.residue, '_solvateCharged', False):
				continue
			a.charge = 0.0
			track.addModified(a, ATTR_SET)
			if a.residue.type in unchargedResTypes:
				if showCharges:
					a.label = str(a.charge)
				continue
			atomKeys = [a.name.lower()]
			if a.element.number == 1 and a.name.lower()[0] in "dt":
				atomKeys.append('h' + a.name.lower()[1:])
			atomKeys.append(a.element)
			for ak in atomKeys:
				key = (a.residue.amberName, ak)
				try:
					a.charge, a.gaffType = chargeTypeData[
									key]
				except KeyError:
					continue
				if showCharges:
					a.label = "%+g" % a.charge
				break
			else:
				unchargedAtoms.setdefault((a.residue.type,
							a.name), []).append(a)
	# merge connected non-standard residues into a "mega" residue.
	# also any standard residues directly connected
	for urt, urs in unchargedResTypes.items():
		for ur in urs[:]:
			if urt not in unchargedResTypes:
				break
			if ur not in unchargedResTypes[urt]:
				# connected to residue of same type and
				# previously removed
				continue
			connected = [ur]
			queue = [ur]
			while queue:
				curRes = queue.pop(0)
				neighbors = set()
				stdConnects = {}
				for a in curRes.atoms:
					for na in a.neighbors:
						naRes = na.residue
						if naRes == curRes \
						or naRes in connected:
							continue
						# don't add standard residue
						# if connected through chain
						# bond
						if naRes not in unchargedResidues:
							from chimera.misc \
							import principalAtom
							pa = principalAtom(
									naRes)
							if pa != None:
								if pa.name == 'CA':
									testNames = ['N', 'C']
								else:
									testNames = ['P', "O3'"]
								if na.name in testNames and na.name not in stdConnects.get(naRes, set()):
									stdConnects.setdefault(naRes, set()).add(na.name)
									continue
						neighbors.add(naRes)
				neighbors = list(neighbors)
				neighbors.sort(lambda r1, r2:
							cmp(r1.type, r2.type))
				connected.extend(neighbors)
				queue.extend([nb for nb in neighbors
						if nb in unchargedResidues])
			# avoid using atom names with the trailing "-number"
			# distinguisher if possible...
			if len(connected) > 1:
				fr = FakeRes(connected)
			else:
				fr = connected[0]
			unchargedResTypes.setdefault(fr.type, []).append(fr)
			for cr in connected:
				if cr in unchargedResidues:
					unchargedResTypes[cr.type].remove(cr)
					if not unchargedResTypes[cr.type]:
						del unchargedResTypes[cr.type]
					continue
				# remove standard-residue atoms from
				# uncharged list
				for ca in cr.atoms:
					uas = unchargedAtoms.get((cr.type,
								ca.name), [])
					if ca not in uas:
						continue
					uas.remove(ca)
					if not uas:
						del unchargedAtoms[(cr.type,
								ca.name)]

	# split isolated atoms (e.g. metals) into separate "residues"
	for resType, residues in unchargedResTypes.items():
		bondResidues = residues
		brType = resType
		while True:
			if len(bondResidues[0].atoms) == 1:
				break
			for a in bondResidues[0].atoms:
				if a.bonds:
					continue
				hasIso = [r for r in bondResidues
							if a.name in r.atomsMap]
				if len(hasIso) == len(bondResidues):
					rem = []
				else:
					rem = [r for r in bondResidues
							if r not in hasIso]
				iso = []
				nonIso = rem
				isoType = "%s[%s]" % (resType, a.name)
				brType = "%s[non-%s]" % (brType, a.name)
				for r in hasIso:
					isoRes = FakeRes(isoType, [fa
						for fa in r.atoms
						if fa.name == a.name])
					iso.append(isoRes)
					nonIsoAtoms = [fa for fa in r.atoms
						if fa.name != a.name]
					if not nonIsoAtoms:
						brType = None
						continue
					nonIsoRes = FakeRes(brType, nonIsoAtoms)
					nonIso.append(nonIsoRes)
				unchargedResTypes[isoType] = iso
				bondResidues = nonIso
			else:
				# no isolated atoms
				break
		if brType != resType:
			del unchargedResTypes[resType]
			if brType != None:
				unchargedResTypes[brType] = bondResidues

	# despite same residue type, residues may still differ -- particularly
	# terminal vs. non-terminal...
	for resType, residues in unchargedResTypes.items():
		if len(residues) < 2:
			continue
		varieties = {}
		for r in residues:
			key = tuple([a.name for a in r.oslChildren()])
			varieties.setdefault(key, []).append(r)
		if len(varieties) == 1:
			continue
		# in order to give the varieties distinguishing names, 
		# find atoms in common
		keys = varieties.keys()
		common = set(keys[0])
		for k in keys[1:]:
			common = common.intersection(set(k))
		uncommon = set()
		for k in keys:
			uncommon = uncommon.union(set(k) - common)
		del unchargedResTypes[resType]
		for k, residues in varieties.items():
			names = set(k)
			more = names - common
			less = uncommon - names
			newKey = resType
			if more:
				newKey += " (w/%s)" % ",".join(list(more))
			if less:
				newKey += " (wo/%s)" % ",".join(list(less))
			unchargedResTypes[newKey] = residues
	if status:
		status("Standard charges added\n")
	return unchargedResTypes, unchargedAtoms


ionTypes = {
	"Ca": "C0", "Cl": "IM", "Na": "IP", "Mg": "MG",
	"Li": "Li", "K": "K", "Rb": "Rb", "Cs": "Cs", "Zn": "Zn"
}
def addNonstandardResCharges(residues, netCharge, method="am1-bcc",
					gaffType=True, status=None, showCharges=False):
	"""Add Antechamber charges to non-standard residue
	
	   'residues' is a list of residues of the same type.  The first
	   residue in the list will be used as an exemplar for the whole
	   type for purposes of charge determination, but charges will be
	   added to all residues in the list.

	   'netCharge' is the net charge of the residue type.

	   'method' is either 'am1-bcc' or 'gasteiger'

	   'gaffType' is a boolean that determines whether GAFF
	   atom types are assigned to atoms in non-standard residues

	   'status' is where status messages go (e.g. replyobj.status)

	   'showCharges' controls whether atom labels are displayed
	   showing the charge values

	   Hydrogens need to be present.
	"""

	# special case for single-atom residues...
	r = residues[0]
	replyobj.info("Assigning partial charges to residue %s (net charge %+d)"
			" with %s method\n" % (r.type, netCharge, method))
	track = chimera.TrackChanges.get()
	if len(r.atoms) == 1:
		for r in residues:
			a = r.atoms[0]
			a.charge = netCharge
			if showCharges:
				a.label = "%+g" % a.charge
			track.addModified(a, ATTR_SET)
			if gaffType:
				if a.element.name in ionTypes:
					a.gaffType = ionTypes[a.element.name]
				else:
					replyobj.info("Could not determine"
						" GAFF type for atom %s\n" % a)
		return True

	# detect tautomers by checking bonds
	varieties = {}
	for r in residues:
		atomMap = {}
		for i, a in enumerate(r.oslChildren()):
			atomMap[a] = i
		bonds = []
		for a in r.atoms:
			i1 = atomMap[a]
			for n in a.neighbors:
				i2 = atomMap.get(a, None)
				if i1 < i2:
					bonds.append((i1, i2))
				else:
					bonds.append((i2, i1))
		bonds.sort()
		varieties.setdefault(tuple(bonds), []).append(r)
	if len(varieties) > 1:
		replyobj.info("%d tautomers of %s; charging separately\n"
					% (len(varieties), r.type))
	for tautomerResidues in varieties.values():
		_nonStdCharge(tautomerResidues, netCharge, method, gaffType,
								status, showCharges)

def _nonStdCharge(residues, netCharge, method, gaffType, status, showCharges):
	r = residues[0]
	if status:
		status("Copying residue %s\n" % r.type)

	# create a fake Molecule that we can write to a Mol2 file
	nm = chimera.Molecule()
	nm.name = r.type

	# write out the residue's atoms first, since those are the
	# ones we will be caring about
	nr = nm.newResidue(r.type, ' ', 1, ' ')
	from chimera.molEdit import addAtom
	atomMap = {}
	atomNames = set()
	ratoms = r.atoms
	# use same ordering of atoms as they had in input, to improve
	# consistency of antechamber charges
	ratoms.sort(lambda a1, a2: cmp(a1.coordIndex, a2.coordIndex))
	for a in ratoms:
		atomMap[a] = addAtom(a.name, a.element, nr, a.coord())
		atomNames.add(a.name)

	# add the intraresidue bonds and remember the interresidue ones
	nearby = set()
	for a in ratoms:
		na = atomMap[a]
		for n in a.neighbors:
			if n.residue != r:
				nearby.add(n)
				continue
			nn = atomMap[n]
			if nn in na.bondsMap:
				continue
			nm.newBond(na, nn)
	from chimera.idatm import typeInfo
	extras = set()
	while nearby:
		nb = nearby.pop()
		aname = _getAName(str(nb.element), atomNames)
		na = addAtom(aname, nb.element, nr, nb.coord())
		atomMap[nb] = na
		extras.add(na)
		for nbn in nb.neighbors:
			if nbn in atomMap:
				nm.newBond(na, atomMap[nbn])
			else:
				try:
					ti = typeInfo[nbn.idatmType]
				except KeyError:
					fc = 0
					geom = 4
				else:
					fc = estimateNetCharge([nbn])
					geom = ti.geometry
				if fc or geom != 4:
					nearby.add(nbn)
				else:
					extras.update(
						_methylate(na, nbn, atomNames))
	totalNetCharge = netCharge + estimateNetCharge(extras)

	from tempfile import mkdtemp
	import os, os.path
	tempDir = mkdtemp()
	def _clean():
		for fn in os.listdir(tempDir):
			os.unlink(os.path.join(tempDir, fn))
		os.rmdir(tempDir)

	from WriteMol2 import writeMol2
	anteIn = os.path.join(tempDir, "ante.in.mol2")
	writeMol2([nm], anteIn, status=status)

	chimeraRoot = os.environ["CHIMERA"]
	anteHome = os.path.join(chimeraRoot, 'bin', 'antechamber')
	anteOut = os.path.join(tempDir, "ante.out.mol2")
	if method.lower().startswith("am1"):
		mth = "bcc"
	elif method.lower().startswith("gas"):
		mth = "gas"
	else:
		_clean()
		raise ValueError("Unknown charge method: %s" % method)

	command = [os.path.join(anteHome, "exe", "antechamber"),
		"-i", anteIn,
		"-fi", "mol2",
		"-o", anteOut,
		"-fo", "mol2",
		"-c", mth,
		"-nc", str(totalNetCharge),
		"-df", "0",
		"-j", "5",
		"-s", "2"]
	if status:
		status("Running ANTECHAMBER for residue %s\n" % r.type)
	from subprocess import Popen, STDOUT, PIPE
	# For some reason on Windows, if shell==False then antechamber
	# cannot run bondtype via system().
	import sys
	if sys.platform == "win32":
		shell = True
	else:
		shell = False
	replyobj.info("Running ANTECHAMBER command: %s\n" % " ".join(command))
	import os
	os.environ['ACHOME'] = anteHome
	anteMessages = Popen(command, stdin=PIPE, stdout=PIPE, stderr=STDOUT,
			cwd=tempDir, shell=shell, bufsize=1).stdout
	while True:
		line = anteMessages.readline()
		if not line:
			break
		replyobj.status("(%s) %s" % (r.type, line), log=True)
	if not os.path.exists(anteOut):
		_clean()
		raise ChargeError("Failure running ANTECHAMBER for residue %s\n"
			"Check reply log for details\n" % r.type)
	if status:
		status("Reading ANTECHAMBER output for residue %s\n" % r.type)
	from chimera import Mol2io, defaultMol2ioHelper
	mol2io = Mol2io(defaultMol2ioHelper)
	mols = mol2io.readMol2file(anteOut)
	if not mol2io.ok():
		_clean()
		raise IOError(mol2io.error())
	if not mols:
		_clean()
		raise RuntimeError("No molecules in ANTECHAMBER output for"
			" residue %s" % r.type)
	chargedAtoms = mols[0].atoms
	if len(chargedAtoms) != len(nm.atoms):
		_clean()
		raise RuntimeError("Wrong number of atoms (%d, should be %d)"
			" in ANTECHAMBER output for residue %s"
			% (r.type, len(chargedAtoms), len(nm.atoms)))
	if status:
		status("Assigning charges for residue %s\n" % r.type)
	# put charges in template 
	templateAtoms = nm.atoms
	# can't rely on order...
	templateAtoms.sort(lambda a1, a2: cmp(a1.serialNumber, a2.serialNumber))
	nonZero = False
	addedChargeSum = 0.0
	_totalCharge = 0.0
	for ta, ca in zip(templateAtoms, chargedAtoms):
		_totalCharge += ca.charge
		if ta in extras:
			addedChargeSum += ca.charge
			continue
		if ca.charge:
			nonZero = True
	if not nonZero:
		_clean()
		raise ChargeError("Failure running ANTECHAMBER for residue %s\n"
			"Check reply log for details\n" % r.type)

	# adjust charges to compensate for added atoms...
	adjustment = (addedChargeSum - (totalNetCharge - netCharge)) / (
					len(templateAtoms) - len(extras))
	for ta, ca in zip(templateAtoms, chargedAtoms):
		if ta in extras:
			continue
		ta.charge = ca.charge + adjustment
		if gaffType:
			ta.gaffType = ca.mol2type
	# map template charges onto first residue
	track = chimera.TrackChanges.get()
	for fa, ta in atomMap.items():
		if ta in extras:
			continue
		fa.charge = ta.charge
		if showCharges:
			fa.label = "%+g" % fa.charge
		track.addModified(fa, ATTR_SET)
		if gaffType:
			fa.gaffType = ta.gaffType
	# map charges onto remaining residues
	for rr in residues[1:]:
		for fa, ra in zip(r.oslChildren(), rr.oslChildren()):
			ra.charge = fa.charge
			if showCharges:
				ra.label = "%+g" % ra.charge
			track.addModified(ra, ATTR_SET)
			if gaffType:
				ra.gaffType = fa.gaffType
	_clean()
	if status:
		status("Charges for residue %s determined\n" % r.type)
	replyobj.info("Charges for residue %s determined\n" % r.type)
	return True

def estimateNetCharge(atoms):
	mols = set([a.molecule for a in atoms])
	if len(mols) == 1:
		# weed out altlocs
		primary = set(mols.pop().primaryAtoms())
		atoms = [a for a in atoms if a in primary]
	chargeInfo = {
		'Cac': 2,
		'N3+': 2,
		'N2+': 2,
		'N1+': 2,
		'Nox': 2,
		'Ntr': 4,
		'Ng+': _ngCharge,
		'O2-': -2,
		'O3-': -2,
		'S3-': -2,
		'S3+': 2,
		'Sac': 4,
		'Son': 4,
		'Sxd': 2,
		'Pac': 2,
		'Pox': 2,
		'P3+': 2,
	}
	chargeTotal = 0
	rings = set()
	subs = {}
	for a in atoms:
		if len(a.bonds) == 0:
			from chimera.elements \
					import metals, halides, alkaliMetals
			if a.element in alkaliMetals:
				chargeTotal += 2
				continue
			if a.element in metals:
				chargeTotal += 4
				continue
			if a.element in halides:
				chargeTotal -= 2
				continue
		from chimera.idatm import typeInfo
		try:
			subs[a] = typeInfo[a.idatmType].substituents
		except KeyError:
			pass
		else:
			# missing/additional protons
			chargeTotal += 2 * (len(a.primaryNeighbors()) - subs[a])
		aRings = a.minimumRings()
		rings.update([ar for ar in aRings if ar.aromatic()])
		if a.idatmType == "C2" and not aRings:
			for nb in a.neighbors:
				nbRings = nb.minimumRings()
				if not nbRings or not nbRings[0].aromatic():
					break
			else:
				# all neighbors in aromatic rings
				chargeTotal += 2
		try:
			info = chargeInfo[a.idatmType]
		except KeyError:
			continue
		if type(info) == int:
			chargeTotal += info
		else:
			chargeTotal += info(a)
	for ring in rings:
		# since we are only handling aromatic rings, any non-ring
		# bonds are presumably single bonds (or matched aromatic bonds)
		electrons = 0
		for a in ring.atoms:
			if a in subs:
				electrons += a.element.number + subs[a] - 2
			else:
				electrons += a.element.number + \
							len(a.neighbors) - 2
			if a.idatmType[-1] in "+-":
				electrons += 1
		if electrons % 2 == 1:
			chargeTotal += 2
	return chargeTotal/2
estimateFormalCharge = estimateNetCharge # for backwards compatibility

def _getAName(base, knownNames):
	anum = 1
	while True:
		name = "%s%d" % (base, anum)
		if name not in knownNames:
			knownNames.add(name)
			break
		anum += 1
	return name

def _methylate(na, n, atomNames):
	added = []
	aname = _getAName("C", atomNames)
	from chimera.molEdit import addAtom
	nn = addAtom(aname, chimera.Element('C'), na.residue, n.coord())
	added.append(nn)
	na.molecule.newBond(na, nn)
	from chimera.bondGeom import bondPositions
	for pos in bondPositions(nn.coord(), 4, 1.1, [na.coord()]):
		hname = _getAName("H", atomNames)
		nh = addAtom(hname, chimera.Element('H'), na.residue, pos)
		added.append(nh)
		na.molecule.newBond(nn, nh)
	return added

def _ngCharge(atom):
	heavys = 0
	for nb in atom.neighbors:
		if nb.element.number > 1:
			heavys += 1
	if heavys > 1:
		return 0
	return 1

def _phosphorylate(mols, status, deletes):
	replyobj.info("Deleting 5' phosphates from: %s\n" %
					", ".join([str(r) for r in deletes]))
	from chimera.molEdit import addAtom
	for r in deletes:
		r.amberName += "5"
		for p in r.atomsMap['P']:
			o = None
			for nb in p.neighbors:
				for nnb in nb.neighbors:
					if nnb == p:
						continue
					if nnb.element.number > 1:
						o = nb
						continue
					r.molecule.deleteAtom(nnb)
				if nb != o:
					r.molecule.deleteAtom(nb)
			v = p.coord() - o.coord()
			sn = getattr(p, "serialNumber", None)
			r.molecule.deleteAtom(p)
			v.length = 0.96
			addAtom("H5T", chimera.Element('H'), r, o.coord() + v,
						serialNumber=sn, bondedTo=o)

def cmdAddStdCharge(molecules=None, chargeModel=None):
	chargeModel = _cmdChargeModel(chargeModel)
	if molecules is None:
		molecules = chimera.openModels.list(
						modelTypes=[chimera.Molecule])
	def warnAddStd(mols, cm):
		ur, ua = addStandardCharges(models=mols, chargeModel=cm,
						status=replyobj.status)
		warning = unchargedAtomsWarning(ua)
		if warning:
			replyobj.warning(warning)
	if not chimera.nogui:
		from AddH.gui import checkNoHyds
		checkNoHyds(molecules, lambda mols=molecules, cm=chargeModel:
					warnAddStd(mols, cm), process)
		return
	warnAddStd(molecules, chargeModel)

def cmdAddNonstdCharge(residues, netCharge, method="am1", gaffType=True):
	from Midas.midas_text import MidasError
	if not residues:
		raise MidasError("No such residues")
	resName, numAtoms = residues[0].type, len(residues[0].atoms)
	for r in residues[1:]:
		if r.type != resName:
			raise MidasError("Residues not all the same type"
				" (%s != %s)" % (resName, r.type))
		if numAtoms != len(r.atoms):
			raise MidasError("Residues have differing number of"
				" atoms (%d != %d)" % (numAtom, len(r.atoms)))
	if not chimera.nogui:
		from AddH.gui import checkNoHyds
		checkNoHyds(residues, lambda residues=residues, nc=netCharge,
			method=method, gt=gaffType, status=replyobj.status:
			addNonstandardResCharges(residues, nc, method=method,
			gaffType=gt, status=status), process)
		return
	try:
		addNonstandardResCharges(residues, netCharge, method=method,
				gaffType=gaffType, status=replyobj.status)
	except ChargeError, v:
		replyobj.error(str(v))
	except ValueError, v:
		raise MidasError(str(v))

def cmdAddAllCharge(molecules=None, method="am1", chargeModel=None,
							gaffType=True):
	from Midas.midas_text import MidasError
	if molecules is None:
		molecules = chimera.openModels.list(
						modelTypes=[chimera.Molecule])
	elif not molecules:
		raise MidasError("Atom specifier does not select any models")

	chargeModel = _cmdChargeModel(chargeModel)
	if not chimera.nogui:
		from AddH.gui import checkNoHyds
		checkNoHyds(molecules, lambda mols=molecules, gt=gaffType,
			method=method, cm=chargeModel: initiateAddCharges(
			models=mols, chargeModel=cm, status=replyobj.status,
			gaffType=gt, method=method), process)
		return
	initiateAddCharges(models=molecules, chargeModel=chargeModel,
		status=replyobj.status, gaffType=gaffType, method=method)

def _cmdChargeModel(chargeModel):
	from Midas.midas_text import MidasError
	if chargeModel:
		cm = str(chargeModel).lower()
		if cm in ["99sb", "ff99sb"]:
			chargeModel = AMBER99SB
		elif cm in ["99bsc0", "ff99bsc0"]:
			chargeModel = AMBER99bsc0
		elif cm in ["02pol.r1", "ff02pol.r1"]:
			chargeModel = AMBER02pol_r1
		elif cm in ["03ua", "ff03ua"]:
			chargeModel = AMBER03ua
		elif cm in ["3", "ff03"]:
			chargeModel = AMBER03
		elif cm in ["03.r1", "ff03.r1"]:
			chargeModel = AMBER03_r1
		else:
			raise MidasError("Unknown charge model: '%s'; must be"
				" one of 99sb, 99bsc0, 02pol.r1, 03ua, 03, or"
				" 03.r1" % chargeModel)
	return chargeModel

def unchargedAtomsWarning(ua, warning=""):
	if ua:
		warning += "Correct charges are unknown for %d"\
			" non-standard atom names in otherwise"\
			" standard residues\n\n" % len(ua)
		replyobj.info("Non-standard atom names:\n")
		for k, atoms in ua.items():
			t, n = k
			info = ", ".join([str(a)
					for a in atoms[:3]])
			if len(atoms) > 3:
				info += " + %d others" % (
					len(atoms) - 3)
			replyobj.info("\t%s %s (%s)\n"
						% (t, n, info))
	return warning

class FakeAtom:
	def __init__(self, atom, res, nameMod=0):
		if isinstance(atom, FakeAtom):
			self.fa_atom = atom.fa_atom
		else:
			self.fa_atom = atom
		self.fa_res = res
		self.fa_nameMod = nameMod

	def __eq__(self, other):
		if isinstance(other, chimera.Atom):
			return self.fa_atom == other
		return other is self

	def __getattr__(self, attrName):
		if attrName == "name" and self.fa_nameMod:
			return "%s-%d" % (getattr(self.fa_atom, attrName),
							self.fa_nameMod)
		if attrName == "residue":
			return self.fa_res
		if attrName == "neighbors":
			realNeighbors = getattr(self.fa_atom, "neighbors")
			lookup = {}
			for fa in self.fa_res.atoms:
				lookup[fa.fa_atom] = fa
			return [lookup.get(x, x) for x in realNeighbors]
		return getattr(self.fa_atom, attrName)

	def __setattr__(self, name, val):
		if name.startswith("fa_"):
			self.__dict__[name] = val
		else:
			setattr(self.fa_atom, name, val)

class FakeRes:
	def __init__(self, name, atoms=None):
		if atoms == None:
			# mega residue
			residues = name
			name = "+".join([r.type for r in residues])
			atoms = [FakeAtom(a, self, i+1)
					for i, r in enumerate(residues)
						for a in r.atoms]
		else:
			atoms = [FakeAtom(a, self) for a in atoms]
		self.type = name
		self.atoms = atoms
		self.atomsMap = {}
		for a in atoms:
			self.atomsMap.setdefault(a.name, []).append(a)

	def oslChildren(self):
		return self.atoms
