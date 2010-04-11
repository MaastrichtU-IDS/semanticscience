# -----------------------------------------------------------------------------
#
from Crystal import space_group_matrices, unit_cell_axes, unit_cell_skew
from Crystal import unit_cell_to_xyz_matrix, cell_origin, cell_center
from Crystal import close_packing_matrices

# -----------------------------------------------------------------------------
# To get all the transformations needed to build the unit cell, multiply all
# SMTRY (crystallographic symmetry) matrices by all MTRIX (non-crystallographic
# symmetry) matrices.
#
def pdb_unit_cell_matrices(pdb_headers):

  slist = crystal_symmetry_matrices(pdb_headers)
  import parsepdb
  mlist = parsepdb.pdb_mtrix_matrices(pdb_headers)

  if slist and mlist:
    from Matrix import matrix_products
    smlist = matrix_products(slist, mlist)
    return smlist
  elif slist:
    return slist
  elif mlist:
    return mlist

  from Matrix import identity_matrix
  return [identity_matrix()]

# -----------------------------------------------------------------------------
#
def pdb_3x3x3_unit_cell_matrices(pdb_headers):

  cell_axes = pdb_unit_cell_axes(pdb_headers)
  mlist = translation_matrices(cell_axes, ((-1,1), (-1,1), (-1,1)))
  clist = pdb_unit_cell_matrices(pdb_headers)
  from Matrix import matrix_products
  plist = matrix_products(mlist, clist)
  
  return plist

# -----------------------------------------------------------------------------
# Identity matrix is first in list.
#
def translation_matrices(cell_axes, tranges):

  from Matrix import translation_matrix
  (xmin, xmax), (ymin, ymax), (zmin, zmax) = tranges
  mlist = []
  for z in range(zmin, zmax+1):
    for y in range(ymin, ymax+1):
      for x in range(xmin, xmax+1):
        t = [0,0,0]
        for a in range(3):
          t[a] = x*cell_axes[0][a] + y*cell_axes[1][a] + z*cell_axes[2][a]
        m = translation_matrix(t)
        if (x,y,z) == (0,0,0):
          # Put the 0 translation first in the list.
          mlist.insert(0, m)
        else:
          mlist.append(m)
  return mlist

# -----------------------------------------------------------------------------
#
def unit_cell_translations(uc, nc, tflist):

  ranges = [(0,n-1) for n in nc]
  cell_axes = unit_cell_axes(*uc)
  mlist = translation_matrices(cell_axes, ranges)
  from Matrix import matrix_products
  tlist = matrix_products(mlist, tflist)
  return tlist

# -----------------------------------------------------------------------------
# Use SMTRY matrices if available, otherwise use space group matrices.
#
def crystal_symmetry_matrices(pdb_headers):

  import parsepdb
  slist = parsepdb.pdb_smtry_matrices(pdb_headers)
  if len(slist) == 0:
    slist = pdb_space_group_matrices(pdb_headers)
  return slist

# -----------------------------------------------------------------------------
#
def pdb_space_group_matrices(pdb_headers):

  cp = crystal_parameters(pdb_headers)
  if cp == None:
    return []
  a, b, c, alpha, beta, gamma, space_group, zvalue = cp
  sgt = space_group_matrices(space_group, a, b, c, alpha, beta, gamma)
  return sgt

# -----------------------------------------------------------------------------
# Angle arguments must be in radians.
#
def space_group_matrices(space_group, a, b, c, alpha, beta, gamma):

    import space_groups
    sgtable = space_groups.space_group_symmetry_table()
    if not sgtable.has_key(space_group):
        return []
    unit_cell_matrices = sgtable[space_group]
    
    r2r_symops = []
    u2r = unit_cell_to_xyz_matrix(a, b, c, alpha, beta, gamma)
    from Matrix import invert_matrix, multiply_matrices
    r2u = invert_matrix(u2r)

    for u2u in unit_cell_matrices:
        r2u_sym = multiply_matrices(u2u, r2u)
        r2r = multiply_matrices(u2r, r2u_sym)
        r2r_symops.append(r2r)

    return r2r_symops

# -----------------------------------------------------------------------------
#
def pdb_cryst1_symmetry_matrices(cryst1_line):

    a, b, c, alpha, beta, gamma, space_group, zvalue = \
       pdb_cryst1_parameters(cryst1_line)

    matrices = symmetry_matrices(space_group, a, b, c, alpha, beta, gamma)
    return matrices

# -----------------------------------------------------------------------------
#
def crystal_parameters(pdb_headers):

  cryst1_line = cryst1_pdb_record(pdb_headers)
  if not cryst1_line:
    return None
    
  cp = pdb_cryst1_parameters(cryst1_line)
  return cp

# -----------------------------------------------------------------------------
#
def cryst1_pdb_record(pdb_headers):

  h = pdb_headers
  if not h.has_key('CRYST1') or len(h['CRYST1']) != 1:
    return None

  line = h['CRYST1'][0]
  return line
    
# -----------------------------------------------------------------------------
#
def pdb_cryst1_parameters(cryst1_line):

  line = cryst1_line

  a = float(line[6:15])
  b = float(line[15:24])
  c = float(line[24:33])
  import math
  degrees_to_radians = math.pi / 180
  alpha = degrees_to_radians * float(line[33:40])
  beta = degrees_to_radians * float(line[40:47])
  gamma = degrees_to_radians * float(line[47:54])
  space_group = line[55:66].strip()
  zstr = line[66:70].strip()
  if zstr == '':
    zvalue = None
  else:
    zvalue = int(zstr)

  return a, b, c, alpha, beta, gamma, space_group, zvalue

# -----------------------------------------------------------------------------
#
def pdb_unit_cell_axes(pdb_headers):

  line = cryst1_pdb_record(pdb_headers)
  if line == None:
    return ((1,0,0), (0,1,0), (0,0,1))

  a, b, c, alpha, beta, gamma, space_group, zvalue = pdb_cryst1_parameters(line)
  axes = unit_cell_axes(a, b, c, alpha, beta, gamma)
  return axes

# -----------------------------------------------------------------------------
# Return a list of symmetry matrices by adding translations to tflist matrices
# so that they map ref_point into the unit cell box containing ref_point.
# The origin of the unit cell grid is given by grid_origin.
#
def pack_matrices(pdb_headers, grid_origin, ref_point, tflist):

    cp = crystal_parameters(pdb_headers)
    if cp is None:
      return tflist
    return pack_unit_cell(cp[:6], grid_origin, ref_point, tflist)

# -----------------------------------------------------------------------------
# Return a list of symmetry matrices by adding translations to tflist matrices
# so that they map ref_point into the unit cell box containing ref_point.
# The origin of the unit cell grid is given by grid_origin.
#
def pack_unit_cell(uc, grid_origin, ref_point, tflist):

    a, b, c, alpha, beta, gamma = uc
    axes = unit_cell_axes(a, b, c, alpha, beta, gamma)
    center = cell_center(grid_origin, axes, ref_point)
    tflist = close_packing_matrices(tflist, ref_point, center,
                                    a, b, c, alpha, beta, gamma)
    return tflist
