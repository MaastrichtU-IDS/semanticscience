# -----------------------------------------------------------------------------
# Molecule utility functions.
#
          
# -----------------------------------------------------------------------------
#
def atom_positions(atoms, xform = None):

    import _multiscale
    xyz = _multiscale.get_atom_coordinates(atoms, transformed = True)
    if xform:
        from Matrix import xform_matrix
        tf = xform_matrix(xform.inverse())
        from _contour import affine_transform_vertices
        affine_transform_vertices(xyz, tf)
    return xyz
  
# -----------------------------------------------------------------------------
# Move atoms in molecule coordinate system using a 3 by 4 matrix.
#
def transform_atom_positions(atoms, tf, from_atoms = None):

    if from_atoms is None:
        from_atoms = atoms
    import _multiscale
    xyz = _multiscale.get_atom_coordinates(from_atoms, transformed = False)
    from _contour import affine_transform_vertices
    affine_transform_vertices(xyz, tf)
    from chimera import Point
    for i,a in enumerate(atoms):
        a.setCoord(Point(*xyz[i]))

# -----------------------------------------------------------------------------
#
def atom_rgba(a):

    c = a.color
    if c is None:
        c = a.molecule.color
    return c.rgba()

# -----------------------------------------------------------------------------
#
def bond_rgba(b):

    c = b.color
    if c is None:
        c = b.molecule.color
    return c.rgba()

# -----------------------------------------------------------------------------
#
def molecule_center(molecule):

  from _multiscale import get_atom_coordinates
  xyz = get_atom_coordinates(molecule.atoms)
  if len(xyz) == 0:
    return (0,0,0)
  c = tuple(xyz.mean(axis = 0))
  return c

# -----------------------------------------------------------------------------
# Return cell size and angles (a, b, c, alpha, beta, gamma).
# Angles are in degrees.
#
def unit_cell_parameters(molecule):

    if not hasattr(molecule, 'pdbHeaders'):
        return None
    from PDBmatrices import crystal_parameters
    cp = crystal_parameters(molecule.pdbHeaders)
    if cp is None:
        return None
    return cp[:6]
