# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 27727 2009-06-02 02:39:43Z pett $

def writeDMS(surf, fileName, writeNormals=True, displayedOnly=True):
	from OpenSave import osOpen
	from chimera import UserError, replyobj
	m = surf.molecule
	if not m:
		raise UserError("No molecule for surface")
	out = osOpen(fileName, "wb")
	vMap = {}
	for i, a in enumerate(surf.atomMap):
		vMap.setdefault(a, []).append(i)
	for i, a in enumerate(m.atoms):
		atomPart = atomFormat(a)
		crd = a.coord()
		print>>out, "%s%8.3f %8.3f %8.3f A" % (atomPart, crd.x,
								crd.y, crd.z)
		if displayedOnly and not a.surfaceDisplay:
			continue
		vertices = surf.surface_piece.geometry[0]
		normals = surf.surface_piece.normals
		vtypes = surf.triData[1][:,2]
		# vtypes (according to MSMS man page):
		#   1 == toric reentrant
		#   2 == inside reentrant
		#   3 == inside contact
		vses = surf.triData[0][:,6]
		for vi in vMap.get(a, []):
			v = vertices[vi]
			vtype = vtypes[vi]
			try:
				dmsType = ('S', 'R', 'C')[vtype-1]
			except IndexError:
				raise ValueError("Vertex type (%d) not in"
						" range 1-3" % vtype)
			ses = vses[vi]
			line = "%s%8.3f %8.3f %8.3f S%s0 %6.3f" % (atomPart,
					v[0], v[1], v[2], dmsType, ses)
			if writeNormals:
				line += " %6.3f %6.3f %6.3f" \
							% tuple(normals[vi])
			print>>out, line
	out.close()

def atomFormat(a):
	r = a.residue
	if r.id.insertionCode == ' ':
		insert = ""
	else:
		insert = r.id.insertionCode
	if len(r.id.chainId) > 1:
		chainId = "*"
	else:
		chainId = r.id.chainId
	resseq = str(r.id.position) + insert + chainId
	return "%3s %4s %4.4s" % (r.type, resseq, a.name)
