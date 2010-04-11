# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 26655 2009-01-07 22:02:30Z gregc $

def readSDF(fileName, identifyAs=None):
	from OpenSave import osOpen
	from chimera import UserError, Molecule, Element, openModels, replyobj
	from chimera import Coord
	state = "init"
	f = osOpen(fileName)
	mols = []
	nonblank = False
	for l in f:
		line = l.strip()
		nonblank = nonblank or line
		if state == "init":
			state = "post header 1"
			molName = line
		elif state == "post header 1":
			state = "post header 2"
		elif state == "post header 2":
			state = "counts"
		elif state == "counts":
			if not line:
				break
			state = "atoms"
			serial = 1
			anums = {}
			atoms = []
			try:
				numAtoms = int(l[:3].strip())
				numBonds = int(l[3:6].strip())
			except ValueError:
				raise UserError("Atom/bond counts line of"
					" MOL/SDF file '%s' is botched: '%s'"
					% (fileName, l))
			m = Molecule()
			mols.append(m)
			if identifyAs:
				m.name = identifyAs
			else:
				from chimera.misc import isInformativeName
				mn = molName.strip()
				if isInformativeName(mn):
					m.name = mn
				else:
					import os.path
					m.name = os.path.split(fileName)[-1]
			r = m.newResidue("UNK", " ", 1, " ")
		elif state == "atoms":
			numAtoms -= 1
			if numAtoms == 0:
				if numBonds:
					state = "bonds"
				else:
					state = "properties"
			try:
				x = float(l[:10].strip())
				y = float(l[10:20].strip())
				z = float(l[21:30].strip())
				elem = l[31:34].strip()
			except ValueError:
				raise UserError("Atom line of MOL/SDF file"
					" '%s' is not x y z element...: '%s'"
					% (fileName, l))
			element = Element(elem)
			if element.number == 0:
				# lone pair or somesuch
				atoms.append(None)
				continue
			anum = anums.get(element.name, 0) + 1
			anums[element.name] = anum
			a = m.newAtom("%s%d" % (element.name, anum), element)
			atoms.append(a)
			r.addAtom(a)
			a.setCoord(Coord(x, y, z))
			a.serialNumber = serial
			serial += 1
		elif state == "bonds":
			numBonds -= 1
			if numBonds == 0:
				state = "properties"
			try:
				a1index = int(l[:3].strip())
				a2index = int(l[3:6].strip())
				order = int(l[6:9].strip())
			except ValueError:
				raise UserError("Bond line of MOL/SDF file"
					" '%s' is not a1 a2 order...: '%s'"
					% (fileName, l))
			a1 = atoms[a1index-1]
			a2 = atoms[a2index-1]
			if not a1 or not a2:
				continue
			m.newBond(a1, a2).order = order
		elif state == "properties":
			if not m.atoms:
				raise UserError("No atoms found for compound"
						" '%s' in MOL/SDF file '%s'"
						% (m.name, fileName))
			if line.split() == ["M", "END"]:
				state = "data"
		elif state == "data":
			if line == "$$$$":
				nonblank = False
				state = "init"
	f.close()
	if nonblank and state not in ["data", "init"]:
		if mols:
			replyobj.warning("Extraneous text after final $$$$"
				" in MOL/SDF file '%s'" % fileName)
		else:
			raise UserError("Unexpected end of file (parser state:"
				" %s) in MOL/SDF file '%s'" % (state, fileName))
	return mols
