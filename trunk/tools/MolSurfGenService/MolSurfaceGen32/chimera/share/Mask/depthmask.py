# -----------------------------------------------------------------------------
# Compute a 2-dimensional depth array from a list of triangles.  The
# vertex y and x coordinates are indices into the depth array and the
# z coordinate is the depth.  The depth array should be initialized to
# a desired maximum depth before being passed to this routine.  If a
# "beyond" array is passed it should be the same size as depth and
# only depths beyond its values will be recorded in the depth array.
# This can be used to get the second layer surface depth by passing in
# a "beyond" array that is the depth calculated for the first layer.
#
# Math needs to be done 64-bit to minimize round-off errors leading to
# multiple nearly identical depths at single grid points where there is only
# one surface point coincident with edge or vertex shared by multiple
# triangles.
#
def surface_z_depth(varray, triangles, depth, beyond = None):

  ysize, xsize = depth.shape

  # Record minimum depth for each triangle at array grid points.
  set = False

  from numpy import zeros, float64, array, float32
  tv = zeros((3,3), float64)    # Triangle vertices
  from math import floor, ceil
  for t in triangles:
    tv[0], tv[1], tv[2] = [varray[i] for i in t]
    ixmin, ixmax = tv[:,0].argmin(), tv[:,0].argmax()
    if ixmin == ixmax:
      continue      # Zero area triangle
    ixmid = 3 - (ixmin + ixmax)
    xmin, xmid, xmax = tv[ixmin,0], tv[ixmid,0], tv[ixmax,0]
    for i in range(max(0,int(ceil(xmin))), min(xsize-1,int(floor(xmax)))+1):
      fxa = (i - xmin) / (xmax - xmin)
      ya,za = tv[ixmin,1:]*(1-fxa) + tv[ixmax,1:]*fxa
      if i < xmid:
        fxb = (i - xmin) / (xmid - xmin)
        yb,zb = tv[ixmin,1:]*(1-fxb) + tv[ixmid,1:]*fxb
      else:
        xsep = xmax - xmid
        if xsep == 0:
          fxb = 0
        else:
          fxb = (i - xmid) / xsep
        yb,zb = tv[ixmid,1:]*(1-fxb) + tv[ixmax,1:]*fxb
      if ya < yb:
        ymin,ymax,zmin,zmax = ya,yb,za,zb
      else:
        ymin,ymax,zmin,zmax = yb,ya,zb,za
      ysep = ymax - ymin
      for j in range(max(0,int(ceil(ymin))), min(ysize-1,int(floor(ymax)))+1):
        if ysep == 0:
          fy = 0
        else:
          fy = (j - ymin) / ysep
        z = zmin*(1-fy) + zmax*fy
        if z < depth[j,i]:
          # Have to convert 64-bit z to 32-bit so same point does not appear
          # beyond itself.
          if beyond is None or array((z,),float32)[0] > beyond[j,i]:
            depth[j,i] = z
            set = True
  return set

# -----------------------------------------------------------------------------
#
def surfaces_z_depth(surfaces, depth, triangle_num,
                     beyond, beyond_triangle_num):

  set = False
  toffset = 0
  from _mask import surface_z_depth
  for varray, tarray in surfaces:
    if surface_z_depth(varray, tarray, depth, triangle_num,
                       beyond, beyond_triangle_num, toffset):
      set = True
    toffset += len(tarray)
  return set

# -----------------------------------------------------------------------------
# Vertices must be in volume local coordinates.
#

def masked_volume(volume, surfaces,
                  projection_axis = (0,0,1), full_map = False,
                  sandwich = False, invert_mask = False):

  g = volume.data

  # Determine transform from vertex coordinates to depth array indices
  step = min(g.plane_spacings())
  fx,fy,fz = orthonormal_frame(projection_axis)
  from numpy import array, float32, intc, zeros, subtract
  tf = array(((fx[0], fx[1], fx[2], 0),
              (fy[0], fy[1], fy[2], 0),
              (fz[0], fz[1], fz[2], 0)), float32) / step

  # Transform vertices to depth array coordinates.
  zsurf = []
  tcount = 0
  for vertices, triangles in surfaces:
    varray = vertices.copy()
    apply_transform(tf, varray)
    zsurf.append((varray, triangles))
    tcount += len(triangles)
  if tcount == 0:
    return None
  vmin, vmax = bounding_box(zsurf)
  voffset = -(vmin - 0.5)
  tf[:,3] += voffset
  from _contour import shift_vertices
  for varray, triangles in zsurf:
    shift_vertices(varray, voffset)
  from math import ceil, floor
  dxsize = int(ceil(vmax[0] - vmin[0] + 1))
  dysize = int(ceil(vmax[1] - vmin[1] + 1))

  # Create depth arrays
  depth = zeros((dysize,dxsize), float32)
  tnum = zeros((dysize,dxsize), intc)
  depth2 = zeros((dysize,dxsize), float32)
  tnum2 = zeros((dysize,dxsize), intc)

  # Create minimal size masked volume array and transformation from
  # masked volume indices to depth array indices.
  if full_map or invert_mask:
    from VolumeViewer.volume import full_region
    ijk_min, ijk_max = full_region(g.size)[:2]
  else:
    ijk_min, ijk_max = bounding_box(surfaces, g.xyz_to_ijk_transform)
    ijk_min = [int(floor(i)) for i in ijk_min]
    ijk_max = [int(ceil(i)) for i in ijk_max]
    from VolumeViewer.volume import clamp_region
    ijk_min, ijk_max = clamp_region((ijk_min, ijk_max, (1,1,1)), g.size)[:2]
  ijk_size = map(lambda a,b: a-b+1, ijk_max, ijk_min)
  vol = g.matrix(ijk_min, ijk_size)
  mvol = zeros(vol.shape, vol.dtype)
  from Matrix import translation_matrix, multiply_matrices
  mijk_to_dijk = multiply_matrices(tf, g.ijk_to_xyz_transform,
                                   translation_matrix(ijk_min))

  # Copy volume to masked volume at masked depth intervals.
  max_depth = 1e37
  if sandwich:
    dlimit = .5*max_depth
  else:
    dlimit = 2*max_depth
  beyond = beyond_tnum = None
  max_layers = 200
  for iter in range(max_layers):
    depth.fill(max_depth)
    tnum.fill(-1)
    any = surfaces_z_depth(zsurf, depth, tnum, beyond, beyond_tnum)
    if not any:
      break
    depth2.fill(max_depth)
    tnum2.fill(-1)
    surfaces_z_depth(zsurf, depth2, tnum2, depth, tnum)
    from _mask import copy_slab
    copy_slab(depth, depth2, mijk_to_dijk, vol, mvol, dlimit)
    beyond = depth2
    beyond_tnum = tnum2

  if invert_mask:
    subtract(vol, mvol, mvol)
    
  # Create masked volume grid object.
  from VolumeData import Array_Grid_Data
  from Matrix import apply_matrix
  morigin = apply_matrix(g.ijk_to_xyz_transform, ijk_min)
  m = Array_Grid_Data(mvol, morigin, g.step, cell_angles = g.cell_angles,
                      rotation = g.rotation, name = g.name + ' masked')

  # Create masked volume object.
  from VolumeViewer import volume_from_grid_data
  v = volume_from_grid_data(m, show_data = False)
  v.copy_settings_from(volume, copy_region = False)
  v.show()
  volume.show(show = False)
  
  return v

# -----------------------------------------------------------------------------
#
def copy_slab(depth, depth2, mijk_to_dijk, vol, mvol, dlimit):

  ksize, jsize, isize = mvol.shape
  djsize, disize = depth.shape
  from Matrix import apply_matrix
  for k in range(ksize):
    for j in range(jsize):
      for i in range(isize):
        di,dj,dk = apply_matrix(mijk_to_dijk, (i,j,k))
        if di >= 0 and di < disize-1 and dj >= 0 and dj < djsize-1:
          # Interpolate depths, nearest neighbor
          # TODO: use linear interpolation.
          di = int(di + 0.5)
          dj = int(dj + 0.5)
          d1 = depth[dj,di]
          d2 = depth2[dj,di]
          if dk >= d1 and dk <= d2 and d1 <= dlimit and d2 <= dlimit:
            mvol[k,j,i] = vol[k,j,i]

# -----------------------------------------------------------------------------
#
def orthonormal_frame(zaxis):

  x,y,z = zaxis
  if z == 0:
    xaxis = (-y,x,0)
    yaxis = (0,0,1)
  else:
    xaxis = (z,0,-x)
    yaxis = (0,z,-y)
  from Matrix import normalize_vector
  naxes = [normalize_vector(v) for v in (xaxis,yaxis,zaxis)]
  return naxes

# -----------------------------------------------------------------------------
#
def bounding_box(surfaces, tf = None):

  smin = smax = None
  from numpy import minimum, maximum
  for vertices, triangles in surfaces:
    if len(triangles) == 0:
      continue
    if tf is None:
      v = vertices
    else:
      v = vertices.copy()
      apply_transform(tf, v)
    v = v.take(triangles.ravel(), axis = 0)
    vmin = v.min(axis = 0)
    if smin is None:      smin = vmin
    else:                 smin = minimum(smin, vmin)
    vmax = v.max(axis = 0)
    if smax is None:      smax = vmax
    else:                 smax = maximum(smax, vmax)
  return smin, smax

# -----------------------------------------------------------------------------
#
def apply_transform(tf, v):

  from _contour import affine_transform_vertices
  affine_transform_vertices(v, tf)

# -----------------------------------------------------------------------------
#
def clamp(v, vmin, vmax):

  vc = [min(vmax[i], max(vmin[i], v[i])) for i in range(len(v))]
  return vc

# -----------------------------------------------------------------------------
# Mask active volume using selected surfaces.
#
def mask_volume_using_selected_surfaces(axis = (0,1,0), pad = None):

  from VolumeViewer import active_volume
  v = active_volume()
  if v is None:
    return

  from Surface import selected_surface_pieces
  plist = selected_surface_pieces()
  from Matrix import xform_matrix, invert_matrix
  tf = invert_matrix(xform_matrix(v.model_transform()))
  surfaces = surface_geometry(plist, tf, pad)

  if surfaces:
    masked_volume(v, surfaces, axis)

# -----------------------------------------------------------------------------
# Pad can be one or two values.  If two values then a slab is formed by
# stitching offset copies of the surface at the boundary.
#
def surface_geometry(plist, tf, pad):

  surfaces = []
  for p in plist:
    surfs = []
    va, ta = p.maskedGeometry(p.Solid)
    na = p.normals
    if isinstance(pad, (float,int)) and pad != 0:
      varray, tarray = offset_surface(va, ta, na, pad)
    elif isinstance(pad, (list,tuple)) and len(pad) == 2:
      varray, tarray = slab_surface(va, ta, na, pad)
    else:
      varray, tarray = va, ta

    if not tf is None:
      from Matrix import xform_matrix, multiply_matrices, is_identity_matrix
      vtf = multiply_matrices(tf, xform_matrix(p.model.openState.xform))
      if not is_identity_matrix(vtf):
        apply_transform(vtf, varray)

    surfaces.append((varray, tarray))

  return surfaces

# -----------------------------------------------------------------------------
#
def offset_surface(varray, tarray, narray, pad):

  varray += pad * narray
  return varray, tarray

# -----------------------------------------------------------------------------
#
def slab_surface(va, ta, na, pad):

  nv = len(va)
  nt = len(ta)

  from _surface import boundary_edges
  edges = boundary_edges(ta)
  ne = len(edges)
  from numpy import zeros
  varray = zeros((2*nv,3), va.dtype)
  tarray = zeros((2*nt+2*ne,3), ta.dtype)

  # Two copies of vertices offset along normals by padding values.
  varray[:nv,:] = va + pad[1] * na
  varray[nv:2*nv,:] = va + pad[0] * na

  tarray[:nt,:] = ta
  # Reverse triangle orientation for inner face.
  tarray[nt:2*nt,0] = ta[:,0] + len(va)
  tarray[nt:2*nt,1] = ta[:,2] + len(va)
  tarray[nt:2*nt,2] = ta[:,1] + len(va)

  # Stitch faces with band of triangles, two per boundary edge.
  tarray[2*nt:2*nt+ne,0] = edges[:,0]
  tarray[2*nt:2*nt+ne,1] = edges[:,0] + nv
  tarray[2*nt:2*nt+ne,2] = edges[:,1] + nv
  tarray[2*nt+ne:2*nt+2*ne,0] = edges[:,0]
  tarray[2*nt+ne:2*nt+2*ne,1] = edges[:,1] + nv
  tarray[2*nt+ne:2*nt+2*ne,2] = edges[:,1]

  return varray, tarray
