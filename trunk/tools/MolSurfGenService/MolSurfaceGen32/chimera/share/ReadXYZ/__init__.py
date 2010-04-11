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

def readXYZ(fileName):
	from OpenSave import osOpen
	from chimera import UserError, Molecule, Element, openModels, replyobj
	from chimera import Coord, connectMolecule
	state = "init"
	f = osOpen(fileName)
	anums = {}
	for line in f:
		line = line.strip()
		if line.startswith("#"):
			continue
		if state == "init":
			state = "post line 1"
			if line.isdigit():
				numAtoms = int(line)
				continue
			else:
				numAtoms = None
		if state == "post line 1":
			m = Molecule()
			r = m.newResidue("UNK", " ", 1, " ")
			state = "atoms"
			serial = 1
			fields = line.split()
			if len(fields) == 4 and len(fields[0]) < 3:
				# seems to be an atom line
				m.name = "unknown molecule"
			else:
				m.name = line
				continue
		if not line: continue

		try:
			elem, x, y, z = line.split()
		except ValueError:
			try:
				elem, x, y, z = line.split(',')
				
			except ValueError:
				raise UserError("Coordinate line of XYZ file"
					" '%s' is not element,x,y,z: '%s'"
					% (fileName, line))
		try:
			x, y, z = [float(c) for c in [x,y,z]]
		except ValueError:
			raise UserError("Coordinate line of XYZ file '%s'"
				" has non-floating point xyz values: '%s'"
				% (fileName, line))
		if elem.isdigit():
			element = Element(int(elem))
		else:
			element = Element(elem)
		if element.number == 0:
			raise UserError("Coordinate line of XYZ file '%s'"
				" has unrecognizable atomic symbol/number: '%s'"
				% (fileName, line))
		anum = anums.get(element.name, 0) + 1
		anums[element.name] = anum
		a = m.newAtom("%s%d" % (element.name, anum), element)
		r.addAtom(a)
		a.setCoord(Coord(x, y, z))
		a.serialNumber = serial
		serial += 1
	f.close()
	if not r.atoms:
		raise UserError("No atoms in XYZ file '%s'" % fileName)
	connectMolecule(m)
	if numAtoms is not None and len(r.atoms) != numAtoms:
		replyobj.warning("Number of atoms found (%d) not equal to"
			" number of atoms declared (%d) in XYZ file '%s'\n"
			% (len(r.atoms), numAtoms))
	return [m]
