# -----------------------------------------------------------------------------
# Create a tube surface passing through specified atoms.
#
def tube_through_atoms(atoms, radius = 0, band_length = 0,
                       segment_subdivisions = 10, circle_subdivisions = 15,
                       follow_bonds = True, color = None,
                       surface_model = None, model_id = None):

    if len(atoms) == 0:
        return None, []

    if follow_bonds:
        chains = atom_chains(atoms)
    else:
        chains = [(atoms,None)]
        if color is None:
            color = (1,1,1,1)

    s = surface_model
    sxf = (s or atoms[0].molecule).openState.xform
    plist = []
    import Molecule as M
    for atoms, bonds in chains:
        xyz_path = M.atom_positions(atoms, sxf)
        point_colors = [M.atom_rgba(a) for a in atoms]
        if bonds is None:
            segment_colors = [color] * (len(atoms) - 1)
        else:
            segment_colors = [M.bond_rgba(b) for b in bonds]
        p = banded_tube(xyz_path, point_colors, segment_colors, radius,
                        segment_subdivisions, circle_subdivisions,
                        band_length, surface_model = s, model_id = model_id)
        if p:
            plist.append(p)
            s = p.model
    if s:
        s.openState.xform = sxf
    return s, plist
    
# -----------------------------------------------------------------------------
# Return a list of atom chains.  An atom chain is a sequence
# of atoms connected by bonds where all non-end-point atoms have exactly 2
# bonds.  A chain is represented by a 2-tuple, the first element being the
# ordered list of atoms, and the second being the ordered list of bonds.
# In a chain which is a cycle all atoms have 2 bonds and the first and
# last atom in the chain are the same.  Non-cycles have end point atoms
# with more or less than 2 bonds.
#
def atom_chains(atoms):

  used_bonds = {}
  chains = []
  for a in atoms:
    if len(a.bonds) != 2:
      for b in a.bonds:
        if not used_bonds.has_key(b):
          used_bonds[b] = 1
          c = trace_chain(a, b)
          chains.append(c)
          end_bond = c[1][-1]
          used_bonds[end_bond] = 1

  #
  # Pick up cycles
  #
  reached_atoms = {}
  for catoms, bonds in chains:
    for a in catoms:
      reached_atoms[a] = 1

  for a in atoms:
    if not reached_atoms.has_key(a):
      bonds = a.bonds
      if len(bonds) == 2:
        b = bonds[0]
        c = trace_chain(a, b)
        chains.append(c)
        for a in c[0]:
          reached_atoms[a] = 1
      
  return chains
          
# -----------------------------------------------------------------------------
#
def trace_chain(atom, bond):

  atoms = [atom]
  bonds = [bond]

  a = atom
  b = bond
  while 1:
    a = b.otherAtom(a)
    atoms.append(a)
    if a == atom:
      break                     # loop
    blist = a.bonds
    blist.remove(b)
    if len(blist) != 1:
      break
    b = blist[0]
    bonds.append(b)
    
  return (atoms, bonds)

# -----------------------------------------------------------------------------
# Create a tube surface passing through specified points.
#
def banded_tube(xyz_path, point_colors, segment_colors, radius,
                segment_subdivisions, circle_subdivisions,
                band_length, limit_tangent = None,
                surface_model = None, model_id = None):

    if len(xyz_path) <= 1:
        return None             # No tube

    import spline
    ptlist = spline.overhauser_spline_points(xyz_path, segment_subdivisions,
                                             limit_tangent,
                                             return_tangents = True)

    plist = [pt[0] for pt in ptlist]
    pcolors = band_colors(plist, point_colors, segment_colors,
                          segment_subdivisions, band_length)

    p = tube_surface_piece(ptlist, pcolors, radius, circle_subdivisions,
                           surface_model, model_id)
    return p

# -----------------------------------------------------------------------------
#
def tube_surface_piece(ptlist, pcolors, radius, circle_subdivisions,
                       surface_model = None, model_id = None):

    nz = len(ptlist)
    nc = circle_subdivisions
    height = 0
    from Shape.shapecmd import cylinder_geometry
    varray, tarray = cylinder_geometry(radius, height, nz, nc, caps = True)
    tflist = extrusion_transforms(ptlist)
    # Transform circles.
    from _contour import affine_transform_vertices
    for i in range(nz):
        affine_transform_vertices(varray[nc*i:nc*(i+1),:], tflist[i])
    # Transform cap center points
    affine_transform_vertices(varray[-2:-1,:], tflist[0])
    affine_transform_vertices(varray[-1:,:], tflist[-1])

    # Vertex colors.
    from numpy import empty, float32
    carray = empty((nz*nc+2,4), float32)
    for i in range(nz):
        carray[nc*i:nc*(i+1),:] = pcolors[i]
    carray[-2,:] = pcolors[0]
    carray[-1,:] = pcolors[-1]

    if surface_model is None:
        import _surface
        surface_model = _surface.SurfaceModel()
        from chimera import openModels as om
        if model_id is None:
            model_id = (om.Default, om.Default)
        om.add([surface_model], baseId = model_id[0], subid = model_id[1])
    
    p = surface_model.addPiece(varray, tarray, (1,1,1,1))
    p.vertexColors = carray
    if radius == 0:
        p.displayStyle = p.Mesh
        p.useLighting = False
    return p

# -----------------------------------------------------------------------------
# Compute transforms mapping disc in xy plane to given points and normals
# with no twist from disc to disc.
#
def extrusion_transforms(ptlist):

    import Matrix as M
    tflist = []
    tf = M.identity_matrix()
    n0 = (0,0,1)
    for p1,n1 in ptlist:
        tf = M.multiply_matrices(M.vector_rotation_transform(n0,n1), tf)
        tflist.append(M.multiply_matrices(M.translation_matrix(p1),tf))
        n0 = n1
    return tflist

# -----------------------------------------------------------------------------
# Calculate point colors for an interpolated set of points.
# Point colors are extended to interpolated points and segments within
# band_length/2 arc distance.
#
def band_colors(plist, point_colors, segment_colors,
                segment_subdivisions, band_length):
                
  n = len(point_colors)
  pcolors = []
  for k in range(n-1):
    j = k * (segment_subdivisions + 1)
    import spline
    arcs = spline.arc_lengths(plist[j:j+segment_subdivisions+2])
    bp0, mp, bp1 = band_points(arcs, band_length)
    for p in range(bp0):
      pcolors.append(point_colors[k])
    for p in range(mp):
      pcolors.append(segment_colors[k])
    for p in range(bp1-1):
      pcolors.append(point_colors[k+1])
  if band_length > 0:
      last = point_colors[-1]
  else:
      last = segment_colors[-1]
  pcolors.append(last)
  return pcolors
  
# -----------------------------------------------------------------------------
# Count points within band_length/2 of each end of an arc.
#
def band_points(arcs, band_length):
      
  arc = arcs[-1]
  half_length = min(.5 * band_length, .5 * arc)
  bp0 = mp = bp1 = 0
  for p in range(len(arcs)):
    l0 = arcs[p]
    l1 = arc - arcs[p]
    if l0 < half_length:
      if l1 < half_length:
        if l0 <= l1:
          bp0 = bp0 + 1
        else:
          bp1 = bp1 + 1
      else:
        bp0 = bp0 + 1
    elif l1 < half_length:
      bp1 = bp1 + 1
    else:
      mp = mp + 1

  return bp0, mp, bp1
