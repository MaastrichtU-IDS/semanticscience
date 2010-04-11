# -----------------------------------------------------------------------------
# Create smooth surfaces surrounding a set of points.
#

# -----------------------------------------------------------------------------
#
def surface_points(xyz_list, resolution, density_threshold,
                   smoothing_factor, smoothing_iterations):

  if len(xyz_list) == 0:
    xyz_min = xyz_max = (0,0,0)
  else:
    import _multiscale
    xyz_min, xyz_max = _multiscale.bounding_box(xyz_list)

  #
  # Need padding of empty cells on border of occupancy map to avoid
  # surface holes.
  #
  xyz_origin = map(lambda x, pad=1.5*resolution: x-pad, xyz_min)
  xyz_step = (resolution, resolution, resolution)
  xyz_size  = map(lambda xmax, xmin: xmax-xmin, xyz_max, xyz_min)
  from math import ceil
  round_up = lambda v, c=ceil: int(c(v))
  isize, jsize, ksize = map(lambda size, r=resolution, rup=round_up:
                            rup(4 + size/r),
                            xyz_size)

  from numpy import zeros, single as floatc
  occup = zeros((ksize, jsize, isize), floatc)
  import _multiscale
  _multiscale.fill_occupancy_grid(xyz_list, xyz_origin, xyz_step, occup)

  occupancy_threshold = density_threshold * (resolution ** 3)
  from _contour import surface, scale_and_shift_vertices, scale_vertices
  varray, tarray, narray = surface(occup, occupancy_threshold,
                                   cap_faces = False, calculate_normals = True)
  scale_and_shift_vertices(varray, xyz_origin, xyz_step)
  scale_vertices(narray, [1.0/s for s in xyz_step])
  from Matrix import normalize_vectors
  normalize_vectors(narray)

  from _surface import smooth_vertex_positions
  smooth_vertex_positions(varray, tarray,
                          smoothing_factor, smoothing_iterations)
  smooth_vertex_positions(narray, tarray,
                          smoothing_factor, smoothing_iterations)
  normalize_vectors(narray)     # Smoothing shortens normals

  return varray, tarray, narray

# -----------------------------------------------------------------------------
#
def solvent_excluded_surface(xyz, r, probe_radius = None,
                             vertex_density = None, all_components = None):

  from chimera.initprefs import SURFACE_DEFAULT, SURF_PROBE_RADIUS, SURF_DENSITY, SURF_DISJOINT
  from chimera.preferences import get as prefget
  if probe_radius is None:
    probe_radius = prefget(SURFACE_DEFAULT, SURF_PROBE_RADIUS)
  if vertex_density is None:
    vertex_density = prefget(SURFACE_DEFAULT, SURF_DENSITY)
  if all_components is None:
    all_components = prefget(SURFACE_DEFAULT, SURF_DISJOINT)

  from numpy import zeros, single as floatc
  xyzr = zeros((len(xyz),4), floatc)
  xyzr[:,:3] = xyz
  xyzr[:,3] = r

  from MoleculeSurface import xyzr_surface_geometry, Surface_Calculation_Error
  try:
    vfloat, vint, tri = xyzr_surface_geometry(xyzr, probe_radius,
                                              vertex_density,
					       all_components)[:3]
  except Surface_Calculation_Error:
    from numpy import zeros, single as floatc, intc
    return zeros((0,3),floatc), zeros((0,3),intc), zeros((0,3),floatc)

  varray = vfloat[:,:3]
  narray = vfloat[:,3:6]
  tarray = tri[:,:3]

  return varray, tarray, narray
