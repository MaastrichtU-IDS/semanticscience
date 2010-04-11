# -----------------------------------------------------------------------------
#
def bond_points_and_colors(bonds, xform_to_surface, bond_point_spacing):
  
    if bond_point_spacing == None and use_bond_zone():
        bond_point_spacing = bond_zone_point_spacing()

    if bond_point_spacing == None:
        return None, None

    bpoints = bond_points(bonds, xform_to_surface, bond_point_spacing)
    bcolors = bond_point_colors(bonds, bond_point_spacing)

    return bpoints, bcolors

# -----------------------------------------------------------------------------
# Interpolate points along bonds.  The spacing is relative to bond radius.
#
def bond_points(bonds, xform, bond_point_spacing):
  
    if bond_point_spacing == None and use_bond_zone():
        bond_point_spacing = bond_zone_point_spacing()

    if bond_point_spacing == None:
        return []

    xyz_list = []
    for b in bonds:
        c = bond_point_count(b, bond_point_spacing)
        if c > 0:
            xyz1, xyz2 = map(lambda a: a.xformCoord().data(), b.atoms)
            for k in range(c):
                fb = float(k+1) / (c+1)
                fa = 1-fb
                xyz = map(lambda a,b: fa*a + fb*b, xyz1, xyz2)
                xyz_list.append(xyz)

    from numpy import array, single as floatc, zeros
    if len(xyz_list) > 0:
        points = array(xyz_list, floatc)
        from Matrix import xform_matrix
        import _contour
        _contour.affine_transform_vertices(points, xform_matrix(xform))
    else:
        points = zeros((0,3), floatc)
    
    return points
    
# -----------------------------------------------------------------------------
#
def bond_point_colors(bonds, bond_point_spacing):

    rgba_list = []
    for b in bonds:
        c = bond_point_count(b, bond_point_spacing)
        if c > 0:
            if b.halfbond:
                rgba1, rgba2 = half_bond_rgba(b)
                rgba_list.extend([rgba1]*(c/2))
                rgba_list.extend([rgba2]*(c-c/2))
            else:
                rgba_list.extend([bond_rgba(b)]*c)
    return rgba_list

# -----------------------------------------------------------------------------
#
def bond_point_count(bond, bond_point_spacing):

    r = bond.radius
    if r > 0 and bond_point_spacing > 0:
        from math import floor
        c = int(floor(bond.length() / (bond_point_spacing * r)))
        return c
    return 0
    
# -----------------------------------------------------------------------------
#
def bond_rgba(bond):

    c = bond.color
    if c == None:
        c = bond.molecule.color
    rgba = c.rgba()
    return rgba
    
# -----------------------------------------------------------------------------
#
def half_bond_rgba(bond):

    return [atom_rgba(a) for a in bond.atoms]

# -----------------------------------------------------------------------------
#
def atom_rgba(atom):

    c = atom.color
    if c == None:
        c = atom.molecule.color
    rgba = c.rgba()
    return rgba

# -----------------------------------------------------------------------------
#
from chimera.preferences import addCategory, HiddenCategory
bzone_prefs = addCategory('BondZone', HiddenCategory,
                          optDict={'active': False, 'spacing': 1.0})

# -----------------------------------------------------------------------------
#
def use_bond_zone(use = None, bond_point_spacing = None):

    if use == None:
        return bzone_prefs['active']
    
    bzone_prefs['active'] = use

    if bond_point_spacing != None:
        bzone_prefs['spacing'] = bond_point_spacing

# -----------------------------------------------------------------------------
#
def bond_zone_point_spacing():

    return bzone_prefs['spacing']

# -----------------------------------------------------------------------------
#
def concatenate_points(points1, points2):

    n1 = len(points1)
    n2 = len(points2)
    from numpy import zeros, single as floatc
    p = zeros((n1+n2, 3), floatc)
    if n1 > 0:
        p[:n1] = points1
    if n2 > 0:
        p[n1:] = points2
    return p

# -----------------------------------------------------------------------------
#
def bondzone_command(cmdname, args):

    from Midas.midas_text import error
    fields = args.split()
    if len(fields) > 1:
        error('Syntax error: %s [relative_point_spacing]' % cmdname)
        return
    elif len(fields) == 1:
        try:
            spacing = float(fields[0])
        except ValueError:
            error('Error: %s illegal point spacing "%s"' % (cmdname, fields[0]))
            return
        use_bond_zone(True, spacing)
    else:
        use_bond_zone(True)

# -----------------------------------------------------------------------------
#
def no_bondzone_command(cmdname, args):

    from Midas.midas_text import error
    fields = args.split()
    if len(fields) > 1:
        error('Syntax error: %s [relative_point_spacing]' % cmdname)
        return

    use_bond_zone(False)
