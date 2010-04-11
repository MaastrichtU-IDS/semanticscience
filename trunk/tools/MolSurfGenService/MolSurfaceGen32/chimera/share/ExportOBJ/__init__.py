# -----------------------------------------------------------------------------
# Output displayed _surface.SurfaceModel models in Wavefront OBJ format.
#

# -----------------------------------------------------------------------------
#
def write_surfaces(surface_models, fobj, fmtl):

    from chimera import version
    created_by = '# Created by Chimera %s\n\n' % version.release
    fobj.write(created_by)
    fmtl.write(created_by)

    import os.path
    fobj.write('mtllib %s\n\n' % os.path.basename(fmtl.name))

    voffset = 1
    piece_count = 0
    import _surface
    import chimera
    for m in surface_models:
    	if m.display:
            for p in m.surfacePieces:
                if p.display:
                    piece_count += 1
                    vcount = write_surface_piece(fobj, fmtl, m, p,
                                                 piece_count, voffset)
                    voffset += vcount

# -----------------------------------------------------------------------------
#
def write_surface_piece(fobj, fmtl, m, p, piece_count, voffset):

    # TODO: Apply model xform to vertices and normals
    v, vi = p.geometry
    n = p.normals
    transform_vertices_and_normals(v, n, m.openState.xform)

    pname = p.oslName
    if pname == '?' or pname == '':
        pname = '%d' % piece_count
    piece_name = '%s_%s' % (m.name, pname)
    piece_name = piece_name.replace(' ', '_') 

    material_name = 'm%d' % piece_count

    write_surface(fobj, v, vi, n, voffset, piece_name, material_name)

    # Write material file
    # TODO: Don't know how Wavefront OBJ handles per vertex color
    # vertex_rgba = p.vertexColors
    mat = m.material
    shine = mat.shininess       # 0 - 128 float
    srgb = mat.specular
    rgba = p.color
    write_color(fmtl, material_name, rgba, shine, srgb)

    return len(v)

# -----------------------------------------------------------------------------
#
def transform_vertices_and_normals(v, n, xform):

    from Matrix import xform_matrix, zero_translation
    tf = xform_matrix(xform)
    rot = zero_translation(tf)
    from _contour import affine_transform_vertices
    affine_transform_vertices(v, tf)
    affine_transform_vertices(n, rot)

# -----------------------------------------------------------------------------
#
def write_surface(fobj, v, vi, n, voffset, piece_name, material_name):
    
    fobj.write('# Number of vertices: %d\n' % len(v))
    for k in range(len(v)):
        fobj.write('v %.6g %.6g %.6g\n' % tuple(v[k]))
    fobj.write('\n')

    fobj.write('# Number of normals: %d\n' % len(n))
    for k in range(len(n)):
        fobj.write('vn %.6g %.6g %.6g\n' % tuple(n[k]))
    fobj.write('\n')

    fobj.write('g %s\n' % piece_name)

    fobj.write('usemtl %s\n\n' % material_name)

    fobj.write('# Number of triangles: %d\n' % len(vi))
    for k in range(len(vi)):
        f = vi[k]
        vni = (f[0]+voffset, f[0]+voffset,
               f[1]+voffset, f[1]+voffset,
               f[2]+voffset, f[2]+voffset)
        fobj.write('f %d//%d %d//%d %d//%d\n' % vni)
    fobj.write('\n')

# -----------------------------------------------------------------------------
#
def write_color(fmtl, name, rgba, specular_exponent, specular_rgb):

    fmtl.write('newmtl %s\n' % name)
    fmtl.write('illum 2\n')     # lighting mode with specular highlights
    fmtl.write('Ka %.6g %.6g %.6g\n' % tuple(rgba[:3]))
    fmtl.write('Kd %.6g %.6g %.6g\n' % tuple(rgba[:3]))
    fmtl.write('Ks %.6g %.6g %.6g\n' % tuple(specular_rgb))
    fmtl.write('d %.6g\n' % rgba[3])
    fmtl.write('Tr %.6g\n' % rgba[3])
    fmtl.write('Ns %.6g\n' % specular_exponent)
    fmtl.write('\n')

# -----------------------------------------------------------------------------
#
def surface_models():

    from chimera import openModels
    from _surface import SurfaceModel
    mlist = openModels.list(modelTypes = [SurfaceModel])
    return mlist

# -----------------------------------------------------------------------------
#
def write_surfaces_dialog():

    import os.path
    dir = os.path.dirname(__file__)
    help_path = os.path.join(dir, 'helpdir', 'obj_output.html')
    help_url = 'file://' + help_path
    filters = (('OBJ', ('*.obj',), '.obj'),)

    import OpenSave
    od = OpenSave.SaveModeless(title = 'Save Surfaces as Wavefront OBJ',
                               filters = filters,
                               defaultFilter = 0,
                               command = write_surfaces_cb,
                               multiple = 0,
			       help = help_url)
    od.enter()

# -----------------------------------------------------------------------------
#
def write_surfaces_cb(okayed, dialog):

    if okayed:
        paths = dialog.getPaths()
        if len(paths) == 1:
            write_surfaces_as_wavefront_obj(paths[0])

# -----------------------------------------------------------------------------
#
def write_surfaces_as_wavefront_obj(obj_path):

    mtl_path = mtl_path_from_obj_path(obj_path)
    mlist = surface_models()

    fobj = open(obj_path, 'w')
    fmtl = open(mtl_path, 'w')
    write_surfaces(mlist, fobj, fmtl)
    fobj.close()
    fmtl.close()

# -----------------------------------------------------------------------------
# Strip .obj, .OBJ, or .Obj from path and add .mtl, .MTL, or .Mtl suffix.
#
def mtl_path_from_obj_path(obj_path):

    if obj_path.endswith('.obj'):
        mtl_path = obj_path[:-4] + '.mtl'
    elif obj_path.endswith('.OBJ'):
        mtl_path = obj_path[:-4] + '.MTL'
    elif obj_path.endswith('.Obj'):
        mtl_path = obj_path[:-4] + '.Mtl'
    else:
        mtl_path = obj_path + '.mtl'

    return mtl_path
