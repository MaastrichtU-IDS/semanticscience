# -----------------------------------------------------------------------------
# Command to create standard geometric shapes as surfaces primarily for
# masking volume data.
#
#   Syntax: shape cylinder|icosahedron|sphere|tube
#               [radius <r>|<rx,ry,rz>]
#               [divisions <d>]
#               [height <h>]
#               [center <x,y,z>|spec]
#               [rotation <ax,ay,az,a>]
#               [qrotation <qx,qy,qz,qw>]
#               [caps true|false]
#               [coordinateSystem <modelid>]
#               [color <cname>]
#               [mesh true|false]
#               [linewidth <w>]
#               [sphereFactor <f>]
#               [orientation <o>]
#               [lattice <h,k>]
#               [slab <width>|<d1,d2>]
#               [segmentSubdivisions <n>]
#               [followBonds true|false]
#               [bandLength <l>]
#               [modelName <name>]
#               [modelId <modelid>]
#
# where orientation applies only to icosahedron and can be one of
# 222, 2n5, n25, 2n3 or any of those with r appended.  The lattice parameter
# is two non-negative integers separated by a comma and controls the
# layout of hexagons for an icosahedron.
#
from Commands import CommandError, check_number, parse_floats, parse_model_id
def shape_command(cmdname, args):

    vspec = ('atomSpec','atoms','atoms')
    shapes = {
        'cylinder': (cylinder_shape, []),
        'ellipsoid': (sphere_shape, []),
        'icosahedron': (icosahedron_shape, []),
        'sphere': (sphere_shape, []),
        'tube': (tube_shape, [vspec]),
        }
    snames = shapes.keys()

    sa = args.split(None, 1)
    if len(sa) < 1:
        raise CommandError, 'shape requires at least 1 argument: shape <name>'

    from Commands import parse_enumeration
    shape = parse_enumeration(sa[0], snames)
    if shape is None:
        raise CommandError, 'Unknown shape: %s' % sa[0]

    func, specs = shapes[shape]
    from Commands import doExtensionFunc
    fargs = ' '.join(sa[1:])
    doExtensionFunc(func, fargs, specInfo = specs)

# -----------------------------------------------------------------------------
#
def cylinder_shape(radius = 10.0, height = 40.0,
                   center = None, rotation = None, qrotation = None,
                   coordinateSystem = None,
                   divisions = 72, color = (.745,.745,.745,1),
                   mesh = False, linewidth = 1,
                   caps = False, slab = None,
                   modelName = 'cylinder', modelId = None):

    check_number(radius, 'radius', nonnegative = True)
    check_number(height, 'height', nonnegative = True)
    check_number(divisions, 'divisions', positive = True)
    check_number(linewidth, 'linewidth', nonnegative = True)
    model_id = parse_model_id(modelId)

    nz, nc = cylinder_divisions(radius, height, divisions)
    varray, tarray = cylinder_geometry(radius, height, nz, nc, caps)
    edge_mask = None

    show_surface(varray, tarray, edge_mask, color, mesh, linewidth,
                 center, rotation, qrotation, coordinateSystem,
                 slab, model_id, modelName)

# -----------------------------------------------------------------------------
#
def cylinder_divisions(radius, height, divisions):

    from math import ceil, pi, sqrt
    nc = max(3, int(ceil(divisions)))
    nz = max(2, int(ceil(nc * height / (sqrt(3)*pi*radius))))
    return nz, nc

# -----------------------------------------------------------------------------
#
def cylinder_geometry(radius, height, nz, nc, caps):

    varray, tarray = tube_geometry(nz, nc)
    varray[:,0] *= radius
    varray[:,1] *= radius
    varray[:,2] *= height
   
    if not caps:
        return varray, tarray

    vc = varray.shape[0]
    varray.resize((vc+2,3))
    varray[vc,:] = (0,0,-0.5*height)
    varray[vc+1,:] = (0,0,0.5*height)

    tc = tarray.shape[0]
    tarray.resize((tc+2*nc,3))
    for i in range(nc):
        tarray[tc+i,:] = (vc,(i+1)%nc,i)
        tarray[tc+nc+i,:] = (vc+1,vc-nc+i,vc-nc+(i+1)%nc)

    return varray, tarray

# -----------------------------------------------------------------------------
# Build a hexagonal lattice tube
#
def tube_geometry(nz, nc):

    from numpy import zeros, single as floatc, arange, cos, sin, intc, pi
    vc = nz*nc
    tc = (nz-1)*nc*2
    varray = zeros((vc,3), floatc)
    tarray = zeros((tc,3), intc)

    v = varray.reshape((nz,nc,3))
    angles = (2*pi/nc)*arange(nc)
    v[::2,:,0] = cos(angles)
    v[::2,:,1] = sin(angles)
    angles += pi/nc
    v[1::2,:,0] = cos(angles)
    v[1::2,:,1] = sin(angles)
    for z in range(nz):
        v[z,:,2] = float(z)/(nz-1) - 0.5
    t = tarray.reshape((nz-1,nc,6))
    c = arange(nc)
    c1 = (c+1)%nc
    t[:,:,0] = t[1::2,:,3] = c
    t[::2,:,1] = t[::2,:,3] = t[1::2,:,1] = c1
    t[::2,:,4] = t[1::2,:,2] = t[1::2,:,4] = c1+nc
    t[::2,:,2] = t[:,:,5] = c+nc
    for z in range(1,nz-1):
        t[z,:,:] += z*nc

    return varray, tarray

# -----------------------------------------------------------------------------
#
def icosahedron_shape(radius = 10.0, center = None, rotation = None,
                      qrotation = None, coordinateSystem = None,
                      divisions = 72,
                      color = (.745,.745,.745,1), mesh = None, linewidth = 1,
                      sphereFactor = 0.0, orientation = '222', lattice = None,
                      slab = None, modelName = 'icosahedron', modelId = None):

    check_number(radius, 'radius', nonnegative = True)
    check_number(divisions, 'divisions', positive = True)
    check_number(linewidth, 'linewidth', nonnegative = True)
    check_number(sphereFactor, 'sphereFactor')
    model_id = parse_model_id(modelId)

    if orientation == 222:
        orientation = '222'
    from Icosahedron import coordinate_system_names as csnames
    if not orientation in csnames:
        raise CommandError, ('Unknown orientation "%s", use %s'
                             % (orientation, ', '.join(csnames)))
    if not lattice is None and mesh is None:
        mesh = True

    from Commands import parse_ints
    hk = parse_ints(lattice, 'lattice', 2)

    if hk is None:
        varray, tarray = icosahedral_geometry(radius, divisions,
                                              sphereFactor, orientation)
        edge_mask = None
    else:
        varray, tarray, edge_mask = hk_icosahedral_geometry(radius, hk,
                                                            sphereFactor,
                                                            orientation)
    show_surface(varray, tarray, edge_mask, color, mesh, linewidth,
                 center, rotation, qrotation, coordinateSystem,
                 slab, model_id, modelName)

# -----------------------------------------------------------------------------
#
def icosahedral_geometry(radius, divisions, sphere_factor = 0,
                         orientation = '222'):

    from math import pi, log
    from Icosahedron import icosahedron_edge_length, icosahedron_triangulation
    d = divisions * (icosahedron_edge_length() / (2*pi))
    subdivision_levels = max(0, int(round(log(d)/log(2))))
    varray, tarray = icosahedron_triangulation(radius, subdivision_levels,
                                               sphere_factor, orientation)
    return varray, tarray

# -----------------------------------------------------------------------------
#
def hk_icosahedral_geometry(radius, hk, sphere_factor = 0, orientation = '222'):

    h,k = hk
    from IcosahedralCage import cages
    varray, tarray, hex_edges = cages.hk_icosahedron_lattice(h, k, radius,
                                                             orientation)
    cages.interpolate_with_sphere(varray, radius, sphere_factor)
    return varray, tarray, hex_edges

# -----------------------------------------------------------------------------
# Makes sphere or ellipsoid if radius is given as 3 values.
#
def sphere_shape(radius = 10.0, center = None, rotation = None,
                 qrotation = None, coordinateSystem = None,
                 divisions = 72,
                 color = (.745,.745,.745,1), mesh = False, linewidth = 1,
                 slab = None, modelName = None, modelId = None):

    try:
        r = parse_floats(radius, 'radius', 3)
    except CommandError:
        check_number(radius, 'radius', nonnegative = True)
        r = (radius, radius, radius)
    check_number(divisions, 'divisions', positive = True)
    check_number(linewidth, 'linewidth', nonnegative = True)
    model_id = parse_model_id(modelId)

    varray, tarray = icosahedral_geometry(1.0, divisions, sphere_factor = 1)
    for a in range(3):
        varray[:,a] *= r[a]
    edge_mask = None

    if modelName is None:
        modelName = 'sphere' if r[1] == r[0] and r[2] == r[0] else 'ellipsoid'

    show_surface(varray, tarray, edge_mask, color, mesh, linewidth,
                 center, rotation, qrotation, coordinateSystem,
                 slab, model_id, modelName)

# -----------------------------------------------------------------------------
#
def show_surface(varray, tarray, edge_mask, color, mesh, linewidth,
                 center, rotation, qrotation, coordinate_system,
                 slab, model_id, shape_name):

    from Commands import parse_rgba
    rgba = parse_rgba(color)

    if coordinate_system:
        from Commands import openStateFromSpec
        os = openStateFromSpec(coordinate_system, 'coordinateSystem')
        cxf = os.xform
    else:
        cxf = None
        
    s = surface_model(model_id, shape_name, cxf)
    sxf = s.openState.xform
    sxfinv = sxf.inverse()

    if cxf is None:
        cxf = sxf

    axis, angle = parse_rotation(rotation, qrotation)
    if axis:
        from chimera import Vector
        csaxis = cxf.apply(Vector(*axis)).data()
        from Matrix import rotation_transform
        saxis = sxfinv.apply(Vector(*csaxis)).data()
        rtf = rotation_transform(saxis, angle)
        from _contour import affine_transform_vertices
        affine_transform_vertices(varray, rtf)

    if center:
        from Commands import parseCenterArg
        center, csys = parseCenterArg(center, 'shape')
        if csys:
            center = csys.xform.apply(center)
        else:
            center = cxf.apply(center)
        scenter = sxfinv.apply(center)
        varray += scenter.data()
        
    if not slab is None:
        if isinstance(slab, (float,int)):
            pad = (-0.5*slab, 0.5*slab)
        else:
            pad = parse_floats(slab, 'slab', 2)
        import _surface
        narray = _surface.calculate_vertex_normals(varray, tarray)
        from Mask import depthmask
        varray, tarray = depthmask.slab_surface(varray, tarray, narray, pad)

    p = s.addPiece(varray, tarray, rgba)
    if mesh:
        p.displayStyle = p.Mesh
    if not edge_mask is None:
        p.setEdgeMask(edge_mask)    # Hide spokes of hexagons.
    p.lineThickness = linewidth
    p.save_in_session = True

# -----------------------------------------------------------------------------
#
def surface_model(model_id, shape_name, coord_xform = None):

    s = find_surface_model(model_id)
    if s is None:
        from _surface import SurfaceModel
        s = SurfaceModel()
        s.name = shape_name
        from chimera import openModels as om
        if model_id is None:
            model_id = (om.Default, om.Default)
        om.add([s], baseId = model_id[0], subid = model_id[1])
        if coord_xform:
            s.openState.xform = coord_xform
    return s

# -----------------------------------------------------------------------------
#
def find_surface_model(model_id):

    from chimera import openModels as om
    if model_id is None or model_id == (om.Default, om.Default):
        return

    from _surface import SurfaceModel
    id, subid = model_id
    slist = om.list(id = id, subid = subid, modelTypes = [SurfaceModel])
    if len(slist) > 1:
        raise CommandError, 'multiple surfaces with model id %d' % model_id
    if len(slist) == 1:
        return slist[0]
    return None

# -----------------------------------------------------------------------------
#
def tube_shape(atoms, radius = 1.0, bandLength = 0.0, followBonds = False,
               divisions = 15, segmentSubdivisions = 10,
               color = (.745,.745,.745,1), mesh = None, linewidth = 1,
               modelName = 'tube', modelId = None):

    if len(atoms) == 0:
        raise CommandError, 'No atoms specified'
    check_number(radius, 'radius', nonnegative = True)
    check_number(bandLength, 'bandLength', nonnegative = True)
    check_number(divisions, 'divisions', positive = True)
    check_number(divisions, 'segmentSubdivisions', positive = True)
    check_number(linewidth, 'linewidth', nonnegative = True)
    from Commands import parse_rgba
    rgba = parse_rgba(color)
    model_id = parse_model_id(modelId)

    s = find_surface_model(model_id)
    from VolumePath import tube
    s,plist = tube.tube_through_atoms(atoms, radius, bandLength,
                                      segmentSubdivisions, divisions,
                                      followBonds, rgba, s, model_id)
    for p in plist:
        if mesh:
            p.displayStyle = p.Mesh
        p.lineThickness = linewidth
        p.save_in_session = True
    if s:
        s.name = modelName

# -----------------------------------------------------------------------------
#
def parse_rotation(rotation, qrotation):

    if rotation:
        aa = parse_floats(rotation, 'rotation', 4)
        axis, angle = aa[:3], aa[3]
    elif qrotation:
        q = parse_floats(qrotation, 'qrotation', 4)
        from Matrix import norm
        from math import atan2, pi
        angle = (360/pi)*atan2(norm(q[:3]), q[3])
        axis = q[:3]
    else:
        axis = angle = None
    if axis and tuple(axis) == (0,0,0):
        axis = angle = None
    return axis, angle
