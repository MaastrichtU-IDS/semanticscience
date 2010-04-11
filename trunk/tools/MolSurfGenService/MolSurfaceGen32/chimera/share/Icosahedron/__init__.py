# -----------------------------------------------------------------------------
#
from icosahedron import icosahedron_geometry, icosahedron_edge_length
from icosahedron import icosahedral_symmetry_matrices, coordinate_system_names

# -----------------------------------------------------------------------------
#
def make_icosahedron_surface(radius = 1, orientation = '222',
                             subdivision_levels = 0, sphere_factor = 0,
                             style = 'mesh', color_rgba = (.7,.7,.7,1),
                             surface_model = None):

    varray, tarray, iradii = \
        icosahedron_triangulation(radius, subdivision_levels, sphere_factor,
                                  orientation, return_radii = True)

    if surface_model == None:
        import _surface
        surface_model = _surface.SurfaceModel()
        import chimera
        chimera.openModels.add([surface_model])
    p = surface_model.addPiece(varray, tarray, color_rgba)
    if style == 'mesh':
        p.displayStyle = p.Mesh
    p.icosahedral_radii = iradii

    return p

# -----------------------------------------------------------------------------
#
def icosahedron_triangulation(radius = 1, subdivision_levels = 0,
                              sphere_factor = 0, orientation = '222',
                              return_radii = False):

    vlist, tlist = icosahedron_geometry(orientation)
    from numpy import array, single as floatc, intc
    varray = array(vlist, floatc)
    tarray = array(tlist, intc)
    import _surface
    for level in range(subdivision_levels):
        varray, tarray = _surface.subdivide_triangles(varray, tarray)
    icosahedral_radii = radii(varray)
    if sphere_factor != 0:
        interpolate_radii(varray, icosahedral_radii, 1, sphere_factor)
    scale_radii(varray, radius)

    if return_radii:
        return varray, tarray, icosahedral_radii

    return varray, tarray

# -----------------------------------------------------------------------------
#
def interpolate_icosahedron_with_sphere(surface_piece, radius, sphere_factor):

    p = surface_piece
    varray, tarray = p.geometry
    interpolate_radii(varray, p.icosahedral_radii, 1, sphere_factor)
    scale_radii(varray, radius)
    p.geometry = varray, tarray

# -----------------------------------------------------------------------------
#
def interpolate_radii(varray, radii_0, radii_1, f):

    rarray = radii(varray)
    scale = radii_0 * (1-f) + radii_1 * f
    from numpy import divide, multiply
    divide(scale, rarray, scale)
    for a in range(3):
        multiply(varray[:,a], scale, varray[:,a])

# -----------------------------------------------------------------------------
#
def scale_radii(varray, scale):

    from numpy import multiply
    for a in range(3):
        multiply(varray[:,a], scale, varray[:,a])

# -----------------------------------------------------------------------------
#
def radii(points):

    from numpy import sqrt
    r = sqrt(points[:,0]*points[:,0] +
             points[:,1]*points[:,1] +
             points[:,2]*points[:,2])
    return r

# -----------------------------------------------------------------------------
#
def show_icosahedron(radius = 1, orientation = '222',
                     subdivision_levels = 0, sphere_factor = 0,
                     style = 'mesh', color_rgba = (.7,.7,.7,1)):

    import _surface
    surface_model = _surface.SurfaceModel()
    p = make_icosahedron_surface(radius, orientation,
                                 subdivision_levels, sphere_factor,
                                 style, color_rgba, surface_model)
    import chimera
    chimera.openModels.add([surface_model])
    return p

# -----------------------------------------------------------------------------
#
def test():

    radius = 140
    orientation = '2n3'
    subdivision_levels = 4
    sphere_factor = .3
    style = 'mesh'
    surface_piece = show_icosahedron(radius, orientation, subdivision_levels,
                                     0, style)
    # interpolate_icosahedron_with_sphere(surface_piece, radius, sphere_factor)
