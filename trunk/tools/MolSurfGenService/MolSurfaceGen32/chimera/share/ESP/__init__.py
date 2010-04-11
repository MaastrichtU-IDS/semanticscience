# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 28838 2009-09-21 23:26:17Z pett $

from chimera import replyobj

def colorEsp(surf, colors, vals, dielectric=4.0, distDep=True, surfDist=1.4,
							hisScheme="HID"):
	from chimera import MaterialColor
	if isinstance(colors[0], MaterialColor):
		colors = [mc.rgba() for mc in colors]
	if len(colors) != len(vals) and len(colors) != len(vals)+2:
		raise ValueError("Number of colors (%d) must be the same as"
			" number of values or number of values +2 (%d, %d)"
			% (len(colors), len(vals), len(vals) + 2))
	# are charges available?
	# don't use checkNoCharges() since that may add hydrogens and
	# therefore change surface
	atoms = surf.atoms
	try:
		# are charges missing or None?
		[a.charge + 1.0 for a in atoms]
	except (AttributeError, TypeError):
		_chargeAtoms(atoms, hisScheme)

	replyobj.status("Computing electrostatics")
	from _multiscale import get_atom_coordinates
	coords = get_atom_coordinates(atoms)
	import numpy
	charges = numpy.array([a.charge for a in atoms])
	from _esp import computeEsp
	piece = surf.surface_piece
	vertices, triangles = piece.geometry
	normals = piece.normals
	potentials = computeEsp(vertices, normals, coords, charges,
		dielectric=dielectric, distDep=distDep, surfDist=surfDist)
	belowColor = colors[0]
	aboveColor = colors[-1]
	if len(colors) == len(vals) + 2:
		colors = colors[1:-1]
	from SurfaceColor import interpolate_colormap
	rgbas = interpolate_colormap(potentials, vals, colors, aboveColor,
							belowColor)
        from Surface import set_coloring_method
        set_coloring_method('ESP coloring', surf, None)
	replyobj.status("Coloring surface")
	surf.surface_piece.vertexColors = rgbas
	surf.surface_piece.using_surface_coloring = True
	replyobj.status("Surface colored")

def _chargeAtoms(atoms, hisScheme):
	# add charges to these atoms w/o adding hydrogens directly to them;
	# probably requires copying

	replyobj.status("Copying molecule")
	from Combine import combine
	mol = atoms[0].molecule
	atomMap, copyMol = combine([mol], mol, returnMapping=True)
	copied = set()
	numHyds = 0
	for a in atoms:
		if a.element.number == 1:
			numHyds += 1
		copied.add(atomMap[a])

	replyobj.status("Adding hydrogens to copy")
	from chimera.idatm import typeInfo
	exotic = [a for a in atoms if a.idatmType not in typeInfo]
	unknownsInfo = dict.fromkeys(exotic, {'geometry':0, 'substituents': 0})
	from AddH import simpleAddHydrogens, hbondAddHydrogens
	hbfunc = simpleAddHydrogens
	if type(hisScheme) == dict:
		hisInfo = {}
		for origR, handling in hisScheme.items():
			hisInfo[atomMap[origR.atoms[0]].residue] = handling
	elif hisScheme == None:
		hbfunc = hbondAddHydrogens
		hisInfo = None
	else:
		hisInfo = dict.fromkeys([r for r in copyMol.residues
						if r.type == "HIS"], hisScheme)
	if numHyds * 3 < len(atoms):
		hbfunc([copyMol], unknownsInfo=unknownsInfo, hisScheme=hisInfo)

	replyobj.status ("Adding charges to copy")
	from AddCharge import addStandardCharges, addNonstandardResCharges, \
						estimateNetCharge, ChargeError
	unchargedResidues, unchargedAtoms = addStandardCharges(models=[copyMol],
				status=replyobj.status, phosphorylation=False)
	for uaList in unchargedAtoms.values():
		for ua in uaList:
			if ua in copied:
				ua.charge = 0.0
	if unchargedAtoms:
		replyobj.error("Some atoms were not assigned charges.\n"
			"For more accurate results you should run the Add Charge\n"
			"tool and then rerun this tool.\n")

	for resType, residues in unchargedResidues.items():
		residues = [r for r in residues if r.atoms[0] in copied]
		if not residues:
			continue
		try:
			addNonstandardResCharges(residues, estimateNetCharge(
				residues[0].atoms), status=replyobj.status,
				gaffType=False)
		except ChargeError:
			from chimera import LimitationError
			raise LimitationError("Cannot automatically determine"
				" charges for residue %s;\nRun AddCharge tool"
				" manually to add charges and then rerun ESP"
				% resType)

	replyobj.status("Mapping copy charges back to original")
	chargeSum = 0.0
	for oa in atoms:
		ca = atomMap[oa]
		charge = ca.charge
		for nb in ca.neighbors:
			if len(nb.neighbors) == 1 and nb not in copied:
				charge += nb.charge
		oa.charge = charge
		chargeSum += charge
	mol.chargeModel = copyMol.chargeModel
	copyMol.destroy()
