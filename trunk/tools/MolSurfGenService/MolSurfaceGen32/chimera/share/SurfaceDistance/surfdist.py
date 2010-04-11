# -----------------------------------------------------------------------------
#
def selection_surface_distance():

    from chimera import selection
    alist = selection.currentAtoms()
    if len(alist) == 0:
        from chimera.replyobj import status
        status('No atoms or markers selected')
        return

    from chimera import openModels
    from _surface import SurfaceModel
    smlist = openModels.list(modelTypes = [SurfaceModel])

    write_surface_distances(alist, smlist)
    
# -----------------------------------------------------------------------------
#
def write_surface_distances(atoms, surfaces):

    sdisp = [s for s in surfaces if s.display]
    dshown = False
    for s in sdisp:
        xyz = atom_coordinates(atoms, s.openState.xform)
        dist = distance_to_surface(xyz, s)
        for a,d in enumerate(dist):
            print ('Distance from %s to surface %s'
                   % (atoms[a].oslIdent(), s.name))
            print (' d = %.5g, surface point (%.5g, %.5g, %.5g), side %.0f'
                   % tuple(d))
            from chimera.replyobj import status
            status('d = %.5g' % d[0])
            dshown = True
#        show_line_segments(xyz, dist[1:4])

    if not dshown:
        from chimera.replyobj import status
        status('No displayed surfaces')
        return
    
# -----------------------------------------------------------------------------
#
def atom_coordinates(atoms, xform):

    from _multiscale import get_atom_coordinates
    xyz = get_atom_coordinates(atoms, transformed = True)
    from Matrix import xform_matrix
    tf = xform_matrix(xform.inverse())
    from _contour import affine_transform_vertices
    affine_transform_vertices(xyz, tf)
    return xyz
    
# -----------------------------------------------------------------------------
#
def distance_to_surface(xyz, smodel):

    from _surface import surface_distance
    dist = None
    for p in smodel.surfacePieces:
        if p.display:
            varray, tarray = p.maskedGeometry(p.Solid)
            dist = surface_distance(xyz, varray, tarray, dist)
    return dist
    
# -----------------------------------------------------------------------------
# Compute the closest distance from a point to a surface.  The surface is
# represented as a list of triangles.  The distance, closest point, and
# side of the closest triangle that the given point lies on is returned.
# Side +1 is the right-handed normal clockwise vertex traversal, while -1
# indicates the opposite side.  This is for determining if the given point
# is inside or outside the surface.
#
def surface_distance(xyz, surf_vertex_xyz, surf_triangles, dist = None):

    if dist is None:
        from numpy import zeros, single as floatc
        dist = zeros((len(xyz),5), floatc)
        dist[:,0] = 1e38

    for i,p in enumerate(xyz):
        di = dist[i,:]
        for vertex_indices in surf_triangles:
            t = [surf_vertex_xyz[v] for v in vertex_indices]
            d, txyz, tside = triangle_distance(p, t)
            if d != None and d < di[0]:
                di[0] = d
                di[1:4] = txyz
                di[4] = tside

    return dist

# -----------------------------------------------------------------------------
# Returns distance, triangle point, and side (1 or -1) of triangle.
#
def triangle_distance(xyz, triangle_vertices):

    # Check if point projects to triangle interior
    va, vb, vc = triangle_vertices
    vab = subtract(vb, va)
    vac = subtract(vc, va)
    vbc = subtract(vc, vb)
    n = normalize(cross(vab, vac))
    if n == None:
        return None, None, None         # degenerate triangle

    v = subtract(xyz, va)
    nv = dot(n, v)
    vt = subtract(v, multiply(nv, n))
    if (dot(cross(n, vab), vt) >= 0 and
        dot(cross(vac, n), vt) >= 0 and
        dot(cross(n, vbc), subtract(vt, vab)) >= 0):
        sxyz = add(va, vt)
        d = distance(xyz, sxyz)
        return d, sxyz, sign(nv)

    # Check if point projects onto any edge
    d = None
    for (v1, v2) in ((va, vb), (va, vc), (vb, vc)):
        v12 = subtract(v2, v1)
        v12n2 = dot(v12,v12)
        v = subtract(xyz, v1)
        vv12 = dot(v,v12)
        if vv12 >= 0 and vv12 <= v12n2:
            exyz = add(v1, multiply(vv12/v12n2, v12))
            de = distance(xyz, exyz)
            if d is None or de < d:
                d = de
                sxyz = exyz

    # Check the closest triangle vertex
    vdist = [(distance(xyz, tv), tuple(tv)) for tv in triangle_vertices]
    vdist.sort()
    dv, v = vdist[0]
    if d is None or dv < d:
        d = dv
        sxyz = v

    return d, sxyz, sign(nv)

# -----------------------------------------------------------------------------
#
def distance(u,v):
    w0, w1, w2 = u[0]-v[0], u[1]-v[1], u[2]-v[2]
    import math
    return math.sqrt(w0*w0+w1*w1+w2*w2)

# -----------------------------------------------------------------------------
#
def dot(u,v):
    return u[0]*v[0]+u[1]*v[1]+u[2]*v[2]

# -----------------------------------------------------------------------------
#
def add(u,v):
    return (u[0]+v[0], u[1]+v[1], u[2]+v[2])

# -----------------------------------------------------------------------------
#
def subtract(u,v):
    return (u[0]-v[0], u[1]-v[1], u[2]-v[2])

# -----------------------------------------------------------------------------
#
def multiply(a,v):
    return (a*v[0], a*v[1], a*v[2])

# -----------------------------------------------------------------------------
#
def cross(u,v):
    return (u[1]*v[2]-u[2]*v[1],
            u[2]*v[0]-u[0]*v[2],
            u[0]*v[1]-u[1]*v[0])

# -----------------------------------------------------------------------------
#
def normalize(v):
    import math
    n = math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2])
    if n == 0:
        return None
    return (v[0]/n, v[1]/n, v[2]/n)

# -----------------------------------------------------------------------------
#
def sign(x):
    if x >= 0:
        return 1
    return -1
    
# -----------------------------------------------------------------------------
#
def show_line_segments(v1, v2, color = (1,1,1,1), surface_model = None):

    n = len(v1)
    from numpy import empty, single as floatc, intc, arange
    varray = empty((2*n,3), floatc)
    tarray = empty((n,3), intc)
    varray[:n,:] = v1
    varray[n:,:] = v2
    tarray[:,0] = tarray[:,2] = arange(n)
    tarray[:,1] = tarray[:,0] + n

    create_model = (surface_model is None)
    if create_model:
        from _surface import SurfaceModel
        surface_model = SurfaceModel()

    p = surface_model.addPiece(varray, tarray, color)
    p.displayStyle = p.Mesh

    if create_model:
        from chimera import openModels as om
        om.add([surface_model])

    return p
