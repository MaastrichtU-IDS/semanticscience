# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 27633 2009-05-21 20:00:36Z pett $

import chimera
from chimera import replyobj

class CastpCavity:
	def __init__(self, mouthInfo, pocketInfo):
		self.mouthInfo = mouthInfo
		self.pocketInfo = pocketInfo

mouthFieldNames = ("ID", "# openings", "mouth SA area", "mouth MS area",
	"SA circumference sum", "MS circumference sum", "# triangles")
pocketFieldNames = ("ID", "# openings", "pocket SA area", "pocket MS area",
		"SA volume", "MS volume", "sum arc length", "# corner points")

def processCastpFiles(pdb, mouthAtoms, mouthInfo, pocketAtoms, pocketInfo,
							identifyAs=None):
	from OpenSave import osOpen
	if not identifyAs:
		identifyAs = pdb[:-4]
	pdb = osOpen(pdb)
	mouthAtoms = osOpen(mouthAtoms)
	mouthInfo = osOpen(mouthInfo)
	pocketAtoms = osOpen(pocketAtoms)
	pocketInfo = osOpen(pocketInfo)
	from chimera import PDBio
	pdbio = PDBio()
	molList = pdbio.readPDBstream(pdb, "CASTp PDB", 0)[0]
	pdb.close()
	if not pdbio.ok():
		raise IOError(pdbio.error())
	if not molList:
		raise ValueError("No structures in CASTp PDB file?!?")
	elif len(molList) > 1:
		raise ValueError("Multiple structures in CASTp PDB file?!?")
	structure = molList[0]
	structure.name = identifyAs
	mouthInfoDicts = processMouthInfoFile(mouthInfo)
	pocketInfoDicts = processPocketInfoFile(pocketInfo)
	mouthInfo.close()
	pocketInfo.close()
	if len(mouthInfoDicts) != len(pocketInfoDicts):
		raise ValueError("Number of mouths (%d) does not match number"
				" of pockets (%d)." % (len(mouthInfoDicts),
				len(pocketInfoDicts)))
	bySerial = {}
	for a in structure.atoms:
		bySerial[a.serialNumber] = a
	gatherAtoms(bySerial, "mouth", mouthAtoms, mouthInfoDicts)
	gatherAtoms(bySerial, "pocket", pocketAtoms, pocketInfoDicts)
	mouthAtoms.close()
	pocketAtoms.close()
	cavities = []
	for mid, pid in zip(mouthInfoDicts, pocketInfoDicts):
		cavities.append(CastpCavity(mid, pid))

	#chimera.openModels.add([structure])
	return structure, cavities

def processMouthInfoFile(mi):
	return processInfoFile(mi, "mouth", mouthFieldNames)

def processPocketInfoFile(pi):
	return processInfoFile(pi, "pocket", pocketFieldNames)

def processInfoFile(f, label, fields):
	infos = []
	header = True
	for line in f:
		if header:
			header = False
			continue
		info = {}
		infos.append(info)
		cols = line.split()
		firstField = 0 - len(fields)
		if int(cols[firstField]) != len(infos):
			raise ValueError("%s info header missing or"
				" IDs not consecutive" % label.capitalize())
		for i, field in enumerate(fields):
			if field[0] == '#' or field == "ID":
				val = int(cols[firstField+i])
			else:
				val = float(cols[firstField+i])
			info[field] = val
	return infos

def gatherAtoms(bySerial, label, f, dicts):
	for line in f:
		line = line.strip()
		if not line:
			continue
		# ignore altloc column...
		if line.startswith("HETATM"):
			# guarantee that atom serial number splits off...
			line = "ATOM  " + line[6:]
		fields = line[:16].strip().split() + line[17:].split()
		serial = int(fields[1])
		try:
			atom = bySerial[serial]
		except KeyError:
			raise ValueError("Non-existent serial number (%d) found"
					" in %s file" % (serial, label))
		from chimera.misc import chimeraLabel
		if atom.name != fields[2] \
		and atom.name != fields[2].replace("*", "'"):
			raise ValueError("Atom with serial number %d (%s) does"
				" not match name in %s file (%s)" % (serial,
				chimeraLabel(atom, showModel=False,
				modelName=False), label, fields[2]))
		if atom.residue.type != fields[3]:
			raise ValueError("Atom with serial number %d (%s) does"
				" not match residue type in %s file (%s)" %
				(serial, chimeraLabel(atom, showModel=False,
				modelName=False), label, fields[3]))
		id = int(fields[-2])
		if id > len(dicts):
			raise ValueError("%s ID (%d) in %s file greater than"
				" number of %ss (%d) in %s info file" %
				(label.capitalize(), id, label, label,
				len(dicts), label))
		dicts[id-1].setdefault("atoms", []).append(atom)
	from chimera.selection import ItemizedSelection
	for d in dicts:
		sel = ItemizedSelection()
		sel.add(d.get("atoms", []))
		d["atoms"] = sel
