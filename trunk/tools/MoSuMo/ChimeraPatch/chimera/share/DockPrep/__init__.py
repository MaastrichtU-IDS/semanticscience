# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29678 2009-12-23 21:26:15Z pett $

import chimera
from chimera import replyobj
import AddH
from prefs import prefs, defaults, INCOMPLETE_SC, MEMORIZED_SETTINGS

def prep(mols, addHFunc=AddH.hbondAddHydrogens, hisScheme=None,
		mutateMSE=True, mutate5BU=True, mutateUMS=True, mutateCSL=True,
		delSolvent=True, delIons=True, delLigands=True,
		delAltLocs=True, incompleteSideChains="rotamers", nogui=False,
		rotamerLib=defaults[INCOMPLETE_SC], rotamerPreserve=True,
		memorize=False, memorizeName=None, **kw):
	"""For faster hydrogen addition, you would set addHFunc to
	   AddH.simpleAddHydrogens

	   'delIons' will only delete ions not involved in metal complexes
	"""

	if memorizeName:
		if memorize:
			import inspect
			argNames, varargName, varKwName, vals = \
				inspect.getargvalues(inspect.currentframe())
			settingsDict = dict([(n, vals[n]) for n in argNames])
			for n in ['mols', 'addHFunc', 'memorize', 'memorizeName']:
				del settingsDict[n]
			settingsDict['kw'] = kw.copy()
			del settingsDict['kw']['doneCB']
			settings = prefs[MEMORIZED_SETTINGS].copy()
			settings[memorizeName] = settingsDict
			prefs[MEMORIZED_SETTINGS] = settings
		elif memorizeName in prefs[MEMORIZED_SETTINGS]:
			exec "; ".join(["%s = %s" % (k, repr(v))
				for k,v in prefs[MEMORIZED_SETTINGS][memorizeName].items()])
	dels = set()
	if delSolvent:
		dels.add("solvent")
	if delIons:
		dels.add("ions")
	if delLigands:
		dels.add("ligand")
	if dels:
		for m in mols:
			validity = m.idatmValid
			for a in m.atoms:
				if a.surfaceCategory in dels:
					if a.surfaceCategory == "ions" \
					and a.coordination():
						continue
					m.deleteAtom(a)
			for r in m.residues:
				if len(r.atoms) == 0:
					m.deleteResidue(r)
			m.idatmValid = validity
	if delAltLocs:
		for m in mols:
			allAtoms = m.atoms
			primaryAtoms = m.primaryAtoms()
			if len(allAtoms) == len(primaryAtoms):
				continue
			paCheck = set(primaryAtoms)
			delledResidues = {}
			for a in allAtoms:
				if a not in paCheck:
					delledResidues.setdefault(a.residue, set()).add(a.altLoc)
					m.deleteAtom(a)
			replyobj.info("Removed %d alternate locations frogetargvaluesm %s as follows:\n"
				"\tResidue  alt loc(s)\n"
				% (len(allAtoms) - len(primaryAtoms), str(m)))

			altResidues = delledResidues.keys()
			altResidues.sort(lambda r1, r2, cmp=cmp: cmp(r1.id, r2.id))
			for r in altResidues:
				rlocs = delledResidues[r]
				replyobj.info("\t%s  %s\n" % (r, ",".join(list(rlocs))))
	for mutResName in ["MSE", "5BU", "UMS", "CSL"]:
		if eval("mutate%s" % mutResName):
			for m in mols:
				validity = m.idatmValid
				for r in m.residues:
					if r.type == mutResName:
						exec "normalize%s(r)" % mutResName in globals(), locals()
				m.idatmValid = validity

	if incompleteSideChains:
		replyobj.status("Mutating incomplete side chains")
		targets = []
		for m in mols:
			for r in m.residues:
				tmplRes = chimera.restmplFindResidue(r.type,
								False, False)
				if not tmplRes:
					continue
				t_amap = tmplRes.atomsMap
				if 'CA' not in t_amap or 'CB' not in t_amap:
					continue
				r_amap = r.atomsMap
				if 'CA' not in r_amap:
					continue
				todo = ['CB']
				seen = set(['N', 'CA', 'C'])
				incomplete = False
				while todo:
					aname = todo.pop()
					seen.add(aname)
					if aname not in r_amap:
						incomplete = True
						break
					ta = t_amap[aname]
					for n in ta.bondsMap.keys():
						if n.name in seen:
							continue
						if n.element.number == 1:
							continue
						todo.append(n.name)
				if not incomplete:
					continue
				if incompleteSideChains == "rotamers":
					targets.append(r)
					continue
				# mutate to gly/ala
				if 'CB' not in r_amap:
					replyobj.info("Mutating %s (incomplete "
						"side chain) to GLY\n" % str(r))
					r.type = 'GLY'
					continue
				replyobj.info("Mutating %s (incomplete side"
						" chain) to ALA\n" % str(r))
				r.type = 'ALA'
				seen = set()
				for bbName in ['N', 'CA', 'C']:
					try:
						alist = r_amap[bbName]
					except KeyError:
						continue
					for a in alist:
						seen.add(a)
				todo = []
				for cb in r_amap['CB']:
					todo.append(cb)
				deathRow = set()
				while todo:
					a = todo.pop()
					seen.add(a)
					for nb in a.neighbors:
						if nb in seen:
							continue
						if nb.residue != a.residue:
							continue
						todo.append(nb)
						deathRow.add(nb)
				for dr in deathRow:
					dr.molecule.deleteAtom(dr)
		if incompleteSideChains == "rotamers":
			if targets:
				replyobj.info("Residues with incomplete"
							" side chains:\n")
				for t in targets:
					replyobj.info("\t" + str(t) + "\n")
				replyobj.info("Replacing each by 'swapaa"
					" same (residue atom spec)")
				replyobj.info(" lib %s" % rotamerLib)
				replyobj.info(" preserve %s'\n"
							% rotamerPreserve)
				from Rotamers import useBestRotamers
				useBestRotamers("same", targets, lib=rotamerLib,
						preserve=rotamerPreserve)
			else:
				replyobj.info("No incomplete side chains\n")

	if addHFunc:
		replyobj.status("Adding hydrogens")
		if nogui or chimera.nogui:
			addHFunc(mols, hisScheme=hisScheme)
			_postAddPrep(mols, nogui=nogui, **kw)
		else:
			from AddH.gui import AddHDialog
			AddHDialog(title="Add Hydrogens for Dock Prep",
				models=mols, useHBonds=True, oneshot=True,
				cb=lambda pap=_postAddPrep, mols=mols, kw=kw: pap(mols, **kw))
	else:
		_postAddPrep(mols, **kw)

def normalizeMSE(r):
	S = chimera.Element("S")
	from BuildStructure import setBondLength
	for a in r.atoms:
		if a.element.name != "Se":
			continue
		a.element = S
		a.name = "SD"
		a.idatmType = "S3"
		for n, b in a.bondsMap.items():
			if n.name == "CE":
				setBondLength(b, 1.78)
			elif n.name == "CG":
				setBondLength(b, 1.81)
	r.type = "MET"
	replyobj.info("MSE residue %s changed to MET\n" % str(r))

def normalize5BU(r):
	for a in r.atoms:
		if a.element.name == "Br":
			r.molecule.deleteAtom(a)
			break
	r.type = "U"
	replyobj.info("5BU residue %s changed to U\n" % str(r))

def normalizeUMS(r):
	_mutateSugarSe(r)
	r.type = "U"
	replyobj.info("UMS residue %s changed to U\n" % str(r))

def normalizeCSL(r):
	_mutateSugarSe(r)
	r.type = "C"
	replyobj.info("CSL residue %s changed to C\n" % str(r))

def _mutateSugarSe(r):
	for a in r.atoms:
		if a.name == "CA'":
			for nb in a.neighbors:
				if nb.element.number == 1:
					r.molecule.deleteAtom(nb)
			r.molecule.deleteAtom(a)
			break
	O = chimera.Element("O")
	from BuildStructure import setBondLength
	for a in r.atoms:
		if a.element.name != "Se":
			continue
		a.element = O
		a.name = "O2'"
		a.idatmType = "O3"
		for n, b in a.bondsMap.items():
			if n.name == "C2'":
				setBondLength(b, 1.43)

def _postAddPrep(mols, addCharges=False, gaffType=True, nogui=False,
					chargeModel=None, method=None, **kw):
	if addCharges:
		from AddCharge import initiateAddCharges
		initiateAddCharges(models=mols, status=replyobj.status,
			gaffType=gaffType, chargeModel=chargeModel, nogui=nogui,
			method=method, cb=lambda ur, uc, m=mols, kw=kw:
			_chargeCB(ur, uc, m, **kw))
	else:
		_postAddCharge(mols, **kw)

def _chargeCB(unchargedResTypes, unchargedAtoms, mols, **kw):
	_postAddCharge(mols, **kw)

def _postAddCharge(mols, runSaveMol2Dialog=False, doneCB=None):
	if runSaveMol2Dialog:
		from WriteMol2.gui import WriteMol2Dialog
		wmDlg = chimera.dialogs.display(WriteMol2Dialog.name)
		wmDlg.saveRelativeVar.set(True)
		wmDlg.rigidVar.set(True)
		wmDlg.multiSaveMenu.invoke(wmDlg.labelMap["combined"])
	replyobj.status("Dock prep finished")
	if doneCB:
		doneCB()

def memoryPrep(toolName, memFunc, mols, nogui=False, **kw):
	"""For calling prep() from a tool, possibly using memorized settings"""
	kw = kw.copy()
	if memFunc == "set":
		kw['memorize'] = True
		kw['memorizeName'] = toolName
	elif memFunc == "use":
		if toolName not in prefs[MEMORIZED_SETTINGS]:
			return memoryPrep(toolName, "set", mols, nogui=nogui, **kw)
		kw['memorize'] = False
		kw['memorizeName'] = toolName
		prep(mols, **kw)
		return None
	return _prepDialog(nogui, mols, **kw)

def _prepDialog(nogui, mols, **kw):
	if nogui or chimera.nogui:
		prep(mols, **kw)
		return None
	from gui import DockPrepDialog
	from chimera import dialogs
	d = dialogs.display(DockPrepDialog.name, wait=True)
	d.applyKeywords = kw
	d.molListBox.setvalue(mols)
	return d

