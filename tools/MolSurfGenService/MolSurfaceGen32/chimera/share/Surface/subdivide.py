# -----------------------------------------------------------------------------
# Refine surface meshes.
#
def subdivide(surface_piece, spacing, surface_model):

    p = surface_piece
    varray, tarray = p.geometry
    narray = p.normals
    va, ta, na = subdivided_geometry(varray, tarray, narray, spacing)
    if surface_model is None:
        p.geometry = va, ta
        p.normals = na
        np = p
    else:
        pos = p.model.openState
        mos = surface_model.openState
        if pos != mos:
            pxf, mxf = pos.xform, mos.xform
            import Matrix
            Matrix.xform_points(va, pxf, mxf)
            Matrix.xform_vectors(na, pxf, mxf)
        np = surface_model.addPiece(va, ta, p.color)
        np.normals = na
        np.displayStyle = p.displayStyle
    return np

# -----------------------------------------------------------------------------
# Try subdividing to obtain a specific edge length and minimize skinny
# triangles.
#
def subdivided_geometry(varray, tarray, narray, elength):

    from _surface import subdivide_mesh
    va, ta, na = subdivide_mesh(varray, tarray, narray, elength)
    return va, ta, na

# -----------------------------------------------------------------------------
#
def test():
    from numpy import array, float32, int32
    varray = array(((0,0,0),(5.1,0,0),(5.1,8.5,0)), float32)
    narray = array(((0,0,1),(0,0,1),(0,0,1)), float32)
    tarray = array(((0,1,2),), int32)
    elength = 1
    va, ta = subdivided_geometry(varray, tarray, narray, elength)
    import _surface
    s = _surface.SurfaceModel()
    color = (1,1,1,1)
    p = s.addPiece(va,ta,color)
    p.displayStyle = p.Mesh
    from chimera import openModels as om
    om.add([s])

#test()
