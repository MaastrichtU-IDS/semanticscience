# -----------------------------------------------------------------------------
# Find points under the specified window position intersecting surface of
# a box.  The box is specified as (xyz_min, xyz_max).  The returned points
# are in box coordinates.  The segment inside the box is clipped by near
# and far clip planes.  It is also clipped by per-model clip planes if
# the clip_plane_model is provided.
#
def box_intercepts(window_x, window_y, box_to_screen_transform, box,
                   clip_plane_model = None):

  from Matrix import invert_matrix
  box_transform = invert_matrix(box_to_screen_transform)
  line = line_perpendicular_to_screen(window_x, window_y, box_transform)
  xyz_in, xyz_out = box_line_intercepts(line, box)
  if xyz_in == None or xyz_out == None:
    return xyz_in, xyz_out
  
  planes = clip_planes(box_transform, clip_plane_model)
  xyz_in, xyz_out, f1, f2 = clip_segment_with_planes(xyz_in, xyz_out, planes)
  
  return xyz_in, xyz_out

# -----------------------------------------------------------------------------
# Returned line is transformed from screen coordinates using the given
# transform
#
def line_perpendicular_to_screen(window_x, window_y, transform):

  xyz_near, xyz_far = clip_plane_points(window_x, window_y)
  from Matrix import apply_matrix
  xyz_near = apply_matrix(transform, xyz_near)
  xyz_far = apply_matrix(transform, xyz_far)
  dir = map(lambda a,b: a-b, xyz_far, xyz_near)
  line = (xyz_near, dir)
  return line

# -----------------------------------------------------------------------------
# Returned planes are transformed from screen coordinates using the given
# transform.  Plane normals point toward unclipped half-space.
#
def clip_planes(transform, clip_plane_model = None):

  xyz_near, xyz_far = clip_plane_points(0, 0)
  dir = (0,0,-1)
  neg_dir = (0,0,1)
  planes = [(dir, inner_product(xyz_near, dir)),
            (neg_dir, inner_product(xyz_far, neg_dir))]

  # Include per-model clip planes
  planes.extend(per_model_clip_planes(clip_plane_model))

  tplanes = map(lambda p: transform_plane(p, transform), planes)

  return tplanes

# -----------------------------------------------------------------------------
# Returned planes are in screen coordinates.
# Normal points toward unclipped half-space.
#
def per_model_clip_planes(clip_plane_model):
  
  if clip_plane_model == None or not clip_plane_model.useClipPlane:
    return []
  
  p = clip_plane_model.clipPlane
  plane = (p.normal.data(), -p.offset())
  planes = [plane]

  # Handle slab clipping mode.
  if clip_plane_model.useClipThickness:
    normal = map(lambda x: -x, p.normal.data())
    offset = p.offset() - clip_plane_model.clipThickness
    plane = (normal, offset)
    planes.append(plane)

  from Matrix import xform_matrix
  model_to_screen = xform_matrix(clip_plane_model.openState.xform)
  tplanes = map(lambda p: transform_plane(p, model_to_screen), planes)

  return tplanes

# -----------------------------------------------------------------------------
# The transform need not be orthogonal.
#
def transform_plane(plane, transform):

  from Matrix import invert_matrix, transpose_matrix
  from Matrix import apply_matrix_without_translation, apply_matrix
  inv_tf = invert_matrix(transform)
  inv_tf_transpose = transpose_matrix(inv_tf)
  normal, offset = plane
  n = apply_matrix_without_translation(inv_tf_transpose, normal)
  o = offset - inner_product(normal, apply_matrix(inv_tf, (0,0,0)))
  return (n, o)
  
# -----------------------------------------------------------------------------
# Find points on near and far clip planes under the specified window position.
# The returned points are in eye coordinates.
#
def clip_plane_points(window_x, window_y):

  import chimera
  c = chimera.viewer.camera

  #
  # This is for mono display.
  # Will use single eye in stereo mode.
  #
  view = 0

  #
  # Window coordinates, y = 0 at bottom
  #
  llx, lly, width, height = c.viewport(view)
  xw = window_x
  yw = height - 1 - window_y

  #
  # Normalized device coordinates range from -1 to 1
  #
  xn = 2 * float(xw - llx)/width - 1
  yn = 2 * float(yw - lly)/height - 1

  #
  # Eye coordinates.
  #
  # Projection matrix from glFrustum() or glOrtho() maps window lower left
  # and upper right corners to near clip plane corners
  # (left, bottom, -znear), (right, top, -znear).
  #
  left, right, bottom, top, znear, zfar, f = c.window(view)

  xe1 = .5 * (left + right) + .5 * xn * (right - left)
  ye1 = .5 * (top + bottom) + .5 * yn * (top - bottom)
  ze1 = -znear

  if c.ortho:
    xe2 = xe1
    ye2 = ye1
  else:
    zratio = zfar / znear
    xe2 = zratio * xe1
    ye2 = zratio * ye1
  ze2 = -zfar

  #
  # Shift by eye position.
  #
  ex, ey, ez = c.eyePos(view)

  xs1 = xe1 + ex
  ys1 = ye1 + ey
  zs1 = ze1 + ez

  xs2 = xe2 + ex
  ys2 = ye2 + ey
  zs2 = ze2 + ez

  xyz_near = (xs1, ys1, zs1)
  xyz_far = (xs2, ys2, zs2)

  return xyz_near, xyz_far

# -----------------------------------------------------------------------------
#
def box_line_intercepts(line, xyz_region):

  xyz_in = box_entry_point(line, xyz_region)
  xyz_out = box_entry_point(oppositely_directed_line(line), xyz_region)
  return xyz_in, xyz_out

# -----------------------------------------------------------------------------
#
def oppositely_directed_line(line):
  
  point, direction = line
  neg_direction = map(lambda a: -a, direction)
  neg_line = (point, neg_direction)
  return neg_line

# -----------------------------------------------------------------------------
# Place where directed line enters box, or None if no intersection.
#
def box_entry_point(line, xyz_region):

  p, d = line
  xyz_min, xyz_max = xyz_region
  planes = (((1,0,0), xyz_min[0]), ((-1,0,0), -xyz_max[0]),
            ((0,1,0), xyz_min[1]), ((0,-1,0), -xyz_max[1]),
            ((0,0,1), xyz_min[2]), ((0,0,-1), -xyz_max[2]))
  for n, c in planes:
    nd = inner_product(n, d)
    if nd > 0:
      t = (c - inner_product(n,p)) / nd
      xyz = tuple(map(lambda a, b, t=t: a + t*b, p, d))
      outside = False
      for n2, c2 in planes:
        if n2 != n or c2 != c:
          if inner_product(xyz, n2) < c2:
            outside = True
            break
      if not outside:
        return xyz

  return None
  
# -----------------------------------------------------------------------------
# Plane normals point towards unclipped half-space.
#
def clip_segment_with_planes(xyz_1, xyz_2, planes):

  f1 = 0
  f2 = 1
  for normal, offset in planes:
    c1 = inner_product(normal, xyz_1) - offset
    c2 = inner_product(normal, xyz_2) - offset
    if c1 < 0 and c2 < 0:
      return None, None, None, None     # All of segment is clipped
    if c1 >= 0 and c2 >= 0:
      continue                          # None of segment is clipped
    f = c1 / (c1 - c2)
    if c1 < 0:
      f1 = max(f1, f)
    else:
      f2 = min(f2, f)

  if f1 == 0 and f2 == 1:
    return xyz_1, xyz_2, f1, f2

  if f1 > f2:
    return None, None, None, None

  i1 = map(lambda a,b: (1-f1)*a + f1*b, xyz_1, xyz_2)      # Intercept point
  i2 = map(lambda a,b: (1-f2)*a + f2*b, xyz_1, xyz_2)      # Intercept point
  return i1, i2, f1, f2

# -----------------------------------------------------------------------------
#
def inner_product(u, v):

  sum = 0
  for a in range(len(u)):
    sum = sum + u[a] * v[a]
  return sum

# -----------------------------------------------------------------------------
# Return intercept under mouse position with volume in volume xyz coordinates.
#
def volume_plane_intercept(window_x, window_y, volume, k):

  from Matrix import multiply_matrices, xform_matrix, invert_matrix
  ijk_to_screen = multiply_matrices(xform_matrix(volume.model_transform()),
                                    volume.data.ijk_to_xyz_transform)
  screen_to_ijk = invert_matrix(ijk_to_screen)
  line = line_perpendicular_to_screen(window_x, window_y, screen_to_ijk)
  p,d = line
  if d[2] == 0:
    return None
  t = (k - p[2]) / d[2]
  ijk = (p[0]+t*d[0], p[1]+t*d[1], k)
  xyz = volume.data.ijk_to_xyz(ijk)
  return xyz

# -----------------------------------------------------------------------------
#
def volume_segment(volume, pointer_x, pointer_y):

  xyz_in = xyz_out = None
  from VolumeViewer import selectregion
  box, tf, xform = selectregion.box_transform_and_xform(volume)
  shown = (box != None)
  if shown:
    transform = selectregion.box_to_eye_transform(tf, xform)
    mlist = filter(lambda m: m.display, volume.models())
    if mlist:
      clipping_model = mlist[0]
    else:
      clipping_model = None
    ijk_in, ijk_out = box_intercepts(pointer_x, pointer_y,
                                     transform, box, clipping_model)
    if ijk_in != None and ijk_out != None:
      from Matrix import apply_matrix
      xyz_in = apply_matrix(tf, ijk_in)
      xyz_out = apply_matrix(tf, ijk_out)

  return xyz_in, xyz_out, shown
