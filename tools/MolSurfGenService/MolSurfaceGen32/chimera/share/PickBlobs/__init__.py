# -----------------------------------------------------------------------------
#
def picked_surface_component(surface_models, xyz_in, xyz_out):

    d, p, t = closest_surface_intercept(surface_models, xyz_in, xyz_out)
    if p == None:
        return None, None, None

    varray, tarray = p.maskedGeometry(p.Solid)
    vlist, tlist = connected_component(tarray, t)
    return p, vlist, tlist

# -----------------------------------------------------------------------------
#
def connected_component(tarray, t):

    import _surface
    tlist = _surface.connected_triangles(tarray, t)
    vlist = _surface.triangle_vertices(tarray, tlist)
    return vlist, tlist

# -----------------------------------------------------------------------------
#
def closest_surface_intercept(surface_models, xyz_in, xyz_out):

    pilist = []
    for m in surface_models:
        if m.display:
            from VolumeViewer import slice as s
            planes = s.per_model_clip_planes(m)
            xyz1, xyz2, f1, f2 = s.clip_segment_with_planes(xyz_in, xyz_out,
                                                            planes)
            from Matrix import apply_inverse_matrix
            sxyz1, sxyz2 = apply_inverse_matrix(m.openState.xform, xyz1, xyz2)
            for p in m.surfacePieces:
                if p.display and not hasattr(p, 'outline_box'):
                    tri, fs = closest_piece_intercept(p, sxyz1, sxyz2)
                    if not tri is None:
                        f = f1 + fs*(f2-f1)
                        pilist.append((f, p, tri))
    pilist.sort()
    if len(pilist) == 0:
        return None, None, None
    return pilist[0]

# -----------------------------------------------------------------------------
#
def closest_piece_intercept(surface_piece, xyz_in, xyz_out):

    p = surface_piece
    varray, tarray = p.maskedGeometry(p.Solid)
    t, f = closest_geometry_intercept(varray, tarray, xyz_in, xyz_out)
    return t, f

# -----------------------------------------------------------------------------
#
def closest_geometry_intercept(varray, tarray, xyz_in, xyz_out):

    import _surface
    fmin, tmin = _surface.closest_geometry_intercept(varray, tarray,
                                                     xyz_in, xyz_out)
    return tmin, fmin

# -----------------------------------------------------------------------------
#
def color_blob(surface_piece, vlist, rgba):

    p = surface_piece
    vc = p.vertexColors
    if vc == None:
        varray, tarray = p.maskedGeometry(p.Solid)
        n = len(varray)
        from numpy import zeros, single as floatc
        vc = zeros((n, 4), floatc)
        color = p.color
        for k,c in enumerate(color):
            vc[:,k] = c

    vc[vlist,:] = rgba

    p.vertexColors = vc

# -----------------------------------------------------------------------------
#
def blob_geometry(surface_piece, vlist, tlist):

    p = surface_piece
    varray, tarray = p.maskedGeometry(p.Solid)
    
    vbarray = varray.take(vlist, axis=0)
    tbarray = tarray.take(tlist, axis=0)

    # Remap vertex indices in triangle array to use new vertex list.
    from numpy import zeros, intc, arange
    vmap = zeros(varray.shape[0], intc)
    vmap[vlist] = arange(len(vlist), dtype = intc)
    tbarray[:,:] = vmap[tbarray]
        
    return vbarray, tbarray

# -----------------------------------------------------------------------------
#
def surface_models():

  import chimera
  import _surface
  mlist = chimera.openModels.list(modelTypes = [_surface.SurfaceModel])
  import SurfaceCap
  mlist = filter(lambda m: not SurfaceCap.is_surface_cap(m), mlist)

  return mlist
