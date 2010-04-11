# -----------------------------------------------------------------------------
# Compute inertia tensor principle axes for surface based on area.
# Calculation weights vertices by 1/3 area of adjoining triangles.
#
def surface_inertia(plist):

  vw = []
  from _surface import vertex_areas
  for p in plist:
    varray, tarray = p.geometry
    weights = vertex_areas(varray, tarray)
    from VolumeViewer.volume import transformed_points
    v = transformed_points(varray, p.model.openState.xform)
    vw.append((v, weights))
    
  return moments_of_inertia(vw)

# -----------------------------------------------------------------------------
# Compute inertia tensor principle axes for atoms using atomic mass weights.
# Results are in eye coordinates.
#
def atoms_inertia(atoms):

  from _multiscale import get_atom_coordinates
  xyz = get_atom_coordinates(atoms, transformed = True)
  weights = [a.element.mass for a in atoms]
  return moments_of_inertia([(xyz,weights)])

# -----------------------------------------------------------------------------
# Compute inertia axes and moments for weighted set of points.
# Takes list of paired vertex and weight arrays.
#
def moments_of_inertia(vw):

  from numpy import zeros, float, array, dot, outer, argsort, linalg, identity
  i = zeros((3,3), float)
  c = zeros((3,), float)
  w = 0
  for xyz, weights in vw:
    xyz, weights = array(xyz), array(weights)
    n = len(xyz)
    if n > 0 :
      wxyz = weights.reshape((n,1)) * xyz
      w += weights.sum()
      i += (xyz*wxyz).sum()*identity(3) - dot(xyz.transpose(),wxyz)
      c += wxyz.sum(axis = 0)

  if w == 0:
    return None, None, None      # All weights are zero.

  i /= w
  c /= w                         # Center of vertices
  i -= dot(c,c)*identity(3) - outer(c,c)

  eval, evect = linalg.eigh(i)

  # Sort by eigenvalue size.
  order = argsort(eval)
  seval = eval[order]
  sevect = evect[:,order]

  # Make rows of 3 by 3 matrix the principle axes.
  return sevect.transpose(), seval, c

# -----------------------------------------------------------------------------
#
def ellipsoid_surface(axes, lengths, center, color, surface):

  xf = surface.openState.xform.inverse()
  sa, sc = transform_ellipsoid(axes, center, xf)
  varray, tarray = ellipsoid_geometry(sc, sa, lengths)
  p = surface.addPiece(varray, tarray, color)
  return p

# -----------------------------------------------------------------------------
#
def ellipsoid_geometry(center, axes, axis_lengths):

  from Icosahedron import icosahedron_triangulation
  varray, tarray = icosahedron_triangulation(subdivision_levels = 3,
                                             sphere_factor = 1.0)
  from numpy import dot, multiply, transpose
  es = dot(varray, transpose(axes))
  ee = multiply(es, axis_lengths)
  ev = dot(ee, axes)
  ev += center

  return ev, tarray

# -----------------------------------------------------------------------------
#
def inertia_ellipsoid_size(d2, shell = False):

  if shell:
    # Match inertia of uniform thickness ellipsoidal shell.
    elen = ellipsoid_shell_size_from_moments(d2)
  else:
    # Solid ellipsoid inertia about "a" axis = m*(b*b + c*c)/5
    d2sum = sum(d2)
    from math import sqrt
    elen = [sqrt(5*(0.5*d2sum - d2[a])) for a in range(3)]
  return elen

# -----------------------------------------------------------------------------
# There is probably no simple formula for moments of inertia of a uniform
# thickness ellipsoid shell (likely elliptic integrals).
# A non-uniform thickness shell thicker along longer axes has moment of
# inertia I_a = m*(b*b + c*c)/3.
# This routines uses an iterative method to find ellipsoid axis lengths with
# specified moments for a uniform thickness shell.
#
# TODO: Convergence is poor for long aspect (10:1) ellipsoids.  With 10
#       iterations, sizes in small dimensions off by ~5%.
#
def ellipsoid_shell_size_from_moments(d2):

  d2sum = sum(d2)
  from math import sqrt
  elen = [sqrt(max(0,3*(0.5*d2sum - d2[a]))) for a in range(3)]
  varray, tarray = ellipsoid_geometry(center = (0,0,0),
                                      axes = ((1,0,0),(0,1,0),(0,0,1)),
                                      axis_lengths = elen)
  from _surface import vertex_areas
  for k in range(10):
    weights = vertex_areas(varray, tarray)
    axes, d2e, center = moments_of_inertia([(varray, weights)])
    de = (d2 - d2e) / d2
    escale = 0.25*(-2*de+de.sum()) + 1
    for a in range(3):
      varray[:,a] *= escale[a]
    elen = [elen[a]*escale[a] for a in range(3)]
  return elen

# -----------------------------------------------------------------------------
#
def print_axes(axes, d2, elen, name, xform = None):

  if xform:
    import Matrix as m
    axes = m.apply_matrix_without_translation(m.xform_matrix(xform), axes)
  from math import sqrt
  paxes = ['\tv%d = %6.3f %6.3f %6.3f   %s = %6.3f   r%d = %6.3f' %
           (a+1, axes[a][0], axes[a][1], axes[a][2],
            ('a','b','c')[a], elen[a], a+1, sqrt(d2[a]))
           for a in range(3)]
  from chimera.replyobj import info
  info('Inertia axes for %s\n%s\n' % (name, '\n'.join(paxes)))
  from Accelerators.standard_accelerators import show_reply_log
  show_reply_log()

# -----------------------------------------------------------------------------
# Inertia of uniform thickness surface.  Uniform ellipsoidal shell with
# matching inertia per area shown.
#
def surface_inertia_ellipsoid(plist, show = True, color = None, surface = None):

  if len(plist) == 0:
    return

  axes, d2, center = surface_inertia(plist)
  elen = inertia_ellipsoid_size(d2, shell = True)

  p0 = plist[0]
  xf = p0.model.openState.xform
  name = surface_name(plist)
  print_axes(axes, d2, elen, name, xf.inverse())

  if show:
    surface = surface_model(surface, xf, 'ellipsoid ' + name)
    if color is None:
      color = p0.color
    p = ellipsoid_surface(axes, elen, center, color, surface)

# -----------------------------------------------------------------------------
#
def surface_name(plist):

  if len(plist) == 1:
    p = plist[0]
    if p.oslName == '?':
      name = p.model.name
    else:
      name = '%s %s' % (p.model.name, p.oslName)
  else:
    slist = set([p.model for p in plist])
    if len(slist) == 1:
      s = slist.pop()
      if len(plist) == len(s.surfacePieces):
        name = s.name
      else:
        name = '%s %d surface pieces' % (s.name, len(plist))
    else:
      name = '%d surface pieces' % len(plist)
  return name

# -----------------------------------------------------------------------------
#
def atoms_inertia_ellipsoid(atoms, show = True, color = None, surface = None):

  if len(atoms) == 0:
    return

  axes, d2, center = atoms_inertia(atoms)
  elen = inertia_ellipsoid_size(d2)

  a0 = atoms[0]
  xf = a0.molecule.openState.xform
  name = atoms_name(atoms)
  print_axes(axes, d2, elen, name, xf.inverse())

  if show:
    surface = surface_model(surface, xf, 'ellipsoid ' + name)
    if color is None:
      c = a0.color
      if c is None:
        c = a0.molecule.color
      color = c.rgba()
    p = ellipsoid_surface(axes, elen, center, color, surface)
    return p

# -----------------------------------------------------------------------------
#
def atoms_name(atoms):

  mlist = set([a.molecule for a in atoms])
  if len(mlist) == 1:
    m = mlist.pop()
    if len(atoms) == len(m.atoms):
      name = m.name
    else:
      name = '%s %d atoms' % (m.name, len(atoms))
  else:
    name = '%d atoms' % len(atoms)
  return name

# -----------------------------------------------------------------------------
#
def transform_ellipsoid(axes, center, xform):

  import Matrix as m
  tf = m.xform_matrix(xform)
  axes = m.apply_matrix_without_translation(tf, axes)
  center = m.apply_matrix(tf, center)
  return axes, center

# -----------------------------------------------------------------------------
#
def surface_model(surface, xf, name):

  if surface is None:
    import _surface
    s = _surface.SurfaceModel()
    s.name = name
    from chimera import openModels as om
    om.add([s])
    s.openState.xform = xf
    return s
  return surface

