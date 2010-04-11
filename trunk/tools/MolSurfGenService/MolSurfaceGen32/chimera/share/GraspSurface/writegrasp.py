# -----------------------------------------------------------------------------
# Write a GRASP format surface file.
#
def grasp_surface_file(vertices, triangles, normals):

    gridsize = 65
    reciplattice = 1

    if len(vertices) > 0:
        from numpy import sum
        midpoint = tuple(sum(vertices, axis=0) / len(vertices))
    else:
        midpoint = (0,0,0)

    ftriangles = triangles + 1          # Fortran indices start at 1
    
    records = (
        fortran_record('format=2', 80),
        fortran_record('vertices,normals,triangles', 80),
        fortran_record('', 80),
        fortran_record('%6d%6d%6d%12.6f' %
                       (len(vertices), len(triangles), gridsize, reciplattice),
                       80),
        fortran_record('%12.6f%12.6f%12.6f' % midpoint, 80),
        fortran_record(vertices.tostring()),
        fortran_record(normals.tostring()),
        fortran_record(ftriangles.tostring())
        )
    f = ''.join(records)
    return f

# -----------------------------------------------------------------------------
#
def fortran_record(string, length = None):

    if length == None:
        length = len(string)
        
    from numpy import array, int32
    rl = array(length, int32).tostring()

    pad = length - len(string)
    if pad > 0:
        string = string + (' '*pad)

    record = ''.join((rl, string[:length], rl))
    return record

# -----------------------------------------------------------------------------
# Write Chimera displayed SurfaceModels as a GRASP surface file.
#
def write_grasp_surface_file():

    from chimera import openModels
    from _surface import SurfaceModel
    mlist = openModels.list(modelTypes = [SurfaceModel])

    if len(mlist) == 0:
        from chimera import replyobj
        replyobj.status('No displayed surfaces')
        return

    varray, tarray, narray = surface_geometry(mlist)
    if len(tarray) == 0:
        from chimera import replyobj
        replyobj.status('No displayed triangles')
        return
    
    def save_geometry(okay, d, varray=varray, tarray=tarray, narray=narray):
        if not okay:
            return          # User canceled action.
        path = d.getPaths()[0]
        f = grasp_surface_file(varray, tarray, narray)
        file = open(path, 'wb')
        file.write(f)
        file.close()

    from OpenSave import SaveModeless
    SaveModeless(title = "Save Surface",
                 filters = [('GRASP surface', ['*.srf'], '.srf')],
                 command = save_geometry)
    
# -----------------------------------------------------------------------------
#
def surface_geometry(model_list):
    
    geomlist = []
    for m in model_list:
        if m.display:
            for p in m.surfacePieces:
                if p.display:
                    varray, tarray = p.maskedGeometry(p.Solid)
                    narray = p.normals
                geomlist.append((varray, tarray, narray))
    geom = append_geometries(geomlist)
    return geom
    
# -----------------------------------------------------------------------------
#
def append_geometries(geomlist):

    if len(geomlist) == 1:
        return geomlist[0]
    elif len(geomlist) == 0:
        from numpy import zeros, float32, int32
        return (zeros((0,3), float32),
                zeros((0,3), int32),
                zeros((0,3), float32))

    vc = tc = 0
    for v, t, n in geomlist:
        vc += len(v)
        tc += len(t)

    from numpy import zeros, float32, int32
    varray = zeros((vc,3), float32)
    tarray = zeros((tc,3), int32)
    narray = zeros((vc,3), float32)

    vc = tc = 0
    for v, t, n in geomlist:
        varray[vc:vc+len(v),:] = v
        tarray[tc:tc+len(t),:] = t + vc
        narray[vc:vc+len(v),:] = n
        vc += len(v)
        tc += len(t)

    return varray, tarray, narray
