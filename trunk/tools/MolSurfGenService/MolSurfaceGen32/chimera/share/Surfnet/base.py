# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import _surfnet
import Midas
import chimera

def model_surfnet(mol, useMesh=True, interval=1.0, cutoff=10,
		  density='Gaussian', color=None):
	surfmol = _surfnet.model_surfnet(mol, cutoff=cutoff, threshold=interval)
	print '%d spheres' % len(surfmol.atoms)
	mList = show_surfnet(surfmol, useMesh, interval,
			     density, color, sameAs=mol)
	for m in mList:
		m.name = 'Surfnet for %s' % mol.name
	surfmol.destroy()
	return None

def atoms_surfnet(osl, useMesh=True, interval=1.0, cutoff=10,
			density='Gaussian', color=None):
	try:
		atomList = Midas._selectedAtoms(osl)
	except (Midas.MidasError, chimera.oslParser.OSLSyntaxError), e:
		return str(e)
	if not atomList:
		return 'No atoms selected'
	try:
		modelList = Midas._selectedModels(osl)
	except (Midas.MidasError, chimera.oslParser.OSLSyntaxError), e:
		return str(e)
	xformed = len(modelList) > 1
	surfmol = _surfnet.atoms_surfnet(atomList, xformed,
					cutoff=cutoff, threshold=interval)
	print '%d spheres' % len(surfmol.atoms)
	if xformed:
		sameAs = None
	else:
		sameAs = modelList[0]
	mList = show_surfnet(surfmol, useMesh, interval,
			     density, color, sameAs=sameAs)
	for m in mList:
		m.name = 'Surfnet for "%s"' % osl
	surfmol.destroy()
	return None

def interface_surfnet(receptorOSL, ligandsOSL, useMesh=True,
			interval=1.0, cutoff=10, density='Gaussian',
			color=None):
	try:
		receptorAtomList = Midas._selectedAtoms(receptorOSL)
	except (Midas.MidasError, chimera.oslParser.OSLSyntaxError), e:
		return str(e)
	if not receptorAtomList:
		return 'No receptor atoms selected'
	try:
		ligandsAtomList = Midas._selectedAtoms(ligandsOSL)
	except (Midas.MidasError, chimera.oslParser.OSLSyntaxError), e:
		return str(e)
	if not ligandsAtomList:
		return 'No ligand atoms selected'
	surfmol = _surfnet.interface_surfnet(receptorAtomList,
						ligandsAtomList,
						True,
						cutoff=cutoff,
						threshold=interval)
	print '%d spheres' % len(surfmol.atoms)
	mList = show_surfnet(surfmol, useMesh, interval, density, color)
	for m in mList:
		m.name = 'Surfnet for "%s" - "%s"' % (receptorOSL, ligandsOSL)
	surfmol.destroy()
	return None

def show_surfnet(surfmol, useMesh, interval, density, color, sameAs=None):

	# Create volume
	q = density == 'Quadratic'
	grid, origin = _surfnet.compute_volume(surfmol, interval, False, q)

	# Contour volume
	from _contour import surface, affine_transform_vertices
	varray, tarray, narray = surface(grid, 100, cap_faces = True,
					 calculate_normals = True)

	# Hide triangle edges to show square mesh
	from _surface import principle_plane_edges
	hidden_edges = principle_plane_edges(varray, tarray)

	# Scale and shift vertices
	tf = ((interval, 0, 0, origin[0]),
	      (0, interval, 0, origin[1]),
	      (0, 0, interval, origin[2]))
	affine_transform_vertices(varray, tf)

	# Create surface/mesh model.
	from _surface import SurfaceModel
	sm = SurfaceModel()
	
	if color is None:
		rgba = (1,1,1,1)
	else:
		rgba = color.rgba()
	p = sm.addPiece(varray, tarray, rgba)
	p.normals = narray
	if useMesh:
		p.displayStyle = p.Mesh
	p.smoothLines = True
	p.setEdgeMask(hidden_edges)

        chimera.openModels.add([sm], shareXform=False, sameAs=sameAs)
	return [sm]
