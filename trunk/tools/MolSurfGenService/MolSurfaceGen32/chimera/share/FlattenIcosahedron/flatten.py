# ----------------------------------------------------------------------------
# Code to take an icosahedrol multiscale model and move subunits to
# create a flat layout, flipping out the 10 triangles around two opposite
# 5-fold vertices (to look like spiked crowns) and then unwrapping the
# resulting cylinder.  Assume VIPER icosahedral coordinate system.
#

# ----------------------------------------------------------------------------
#
def flatten_icosahedron(multiscale_models, radius):

  clist = chains(multiscale_models)

  it = icosahedron_triangles(radius)
  itc = map(center, it)

  centers = map(chain_center, clist)
  ci = map(lambda c: closest_point_index(c, itc), centers)
  
  fit = flattened_icosahedron_triangles(radius)

  xforms = map(triangle_transformation, it, fit)

  for k in range(len(clist)):
    c = clist[k]
    c.unflatten_xform = c.xform
    import chimera
    xf = chimera.Xform()
    xf.multiply(c.xform)
    xf.premultiply(xforms[ci[k]])
    c.set_xform(xf)

# ----------------------------------------------------------------------------
#
def unflatten_icosahedron(multiscale_models):

  clist = chains(multiscale_models)
  for c in clist:
    if hasattr(c, 'unflatten_xform'):
      c.set_xform(c.unflatten_xform)
      delattr(c, 'unflatten_xform')

# ----------------------------------------------------------------------------
#
def model_radius(multiscale_models):

  clist = chains(multiscale_models)
  if clist:
    r = max(map(chain_radial_size, clist))
  else:
    r = None
  return r
    
# ----------------------------------------------------------------------------
#
def icosahedron_triangles(radius):

  import Icosahedron
  vlist, tlist = Icosahedron.icosahedron_geometry(orientation = '222')
  from numpy import array
  varray = array(vlist)
  varray *= radius
  triangles = triangle_list(varray, tlist)
  return triangles

# ----------------------------------------------------------------------------
#
def flattened_icosahedron_triangles(radius):

  varray, tarray = flattened_icosahedron_geometry(radius)
  tlist = triangle_list(varray, tarray)
  return tlist

# ----------------------------------------------------------------------------
#
def flattened_icosahedron_geometry(radius):

  from math import sin, acos, pi, sqrt

  # Angle spanned by edge from center
  a = 2*acos(.5/sin(pi/5))
  e = 2*radius*sin(a/2)              # edge length
  h = e*sqrt(3)/2             # height of triangle, equals grid spacing

  #
  # Vertex numbering.
  #
  #    0   1   2   3   4
  #  5   6   7   8   9   10
  #    11  12  13  14  15  16
  #      17  18  19  20  21
  #
  varray = ((-2.25, 1.5, 0), (-1.25, 1.5, 0), (-0.25, 1.5, 0),
            (0.75, 1.5, 0), (1.75, 1.5, 0),
            (-2.75, 0.5, 0), (-1.75, 0.5, 0), (-0.75, 0.5, 0),
            (0.25, 0.5, 0), (1.25, 0.5, 0), (2.25, 0.5, 0),
            (-2.25, -0.5, 0), (-1.25, -0.5, 0), (-0.25, -0.5, 0),
            (0.75, -0.5, 0), (1.75, -0.5, 0), (2.75, -0.5, 0),
            (-1.75, -1.5, 0), (-0.75, -1.5, 0),
            (0.25, -1.5, 0), (1.25, -1.5, 0), (2.25, -1.5, 0))
  from numpy import array, single as floatc, intc
  varray = array(varray, floatc)
  varray[:,0] *= array(e, floatc)
  varray[:,1] *= array(h, floatc)

  # Triangle order matches Icosahedron/__init__.py icosahedron_geometry().
  tarray = ((0,5,6), (1,6,7), (2,7,8), (3,8,9), (4,9,10),
            (18,13,12), (17,12,11), (21,16,15), (20,15,14), (19,14,13),
            (5,11,6), (6,11,12), (6,12,7), (7,12,13), (7,13,8),
            (8,13,14), (8,14,9), (9,14,15), (9,15,10), (10,15,16))
  tarray = array(tarray, intc)
  
  return varray, tarray
    
# ----------------------------------------------------------------------------
# Make list of triangles, each triangle being an array of 3 vertex positions.
#
def triangle_list(varray, tarray):
  
  tlist = []
  for v1, v2, v3 in tarray:
    from numpy import array
    t = array((varray[v1], varray[v2], varray[v3]))
    tlist.append(t)
  return tlist

# ----------------------------------------------------------------------------
# Find transform mapping one triangle to another.  Triangles are specified
# by 3 vertices.
#
def triangle_transformation(t1, t2):

  tf1 = triangle_frame(t1)
  tf2 = triangle_frame(t2)
  xf = frame_transform(tf1, tf2)
  c1 = center(t1)
  from chimera import Xform
  xf.multiply(Xform.translation(-c1[0], -c1[1], -c1[2]))
  c2 = center(t2)
  xf.premultiply(Xform.translation(c2[0], c2[1], c2[2]))
  return xf

# ----------------------------------------------------------------------------
# Return two triangle edge vectors and normal.
#
def triangle_frame(t):

  v0, v1, v2 = t
  e1 = map(lambda a,b: a-b, v1, v0)
  e2 = map(lambda a,b: a-b, v2, v0)
  n = (e1[1]*e2[2]-e1[2]*e2[1],
       -e1[0]*e2[2]+e1[2]*e2[0],
       e1[0]*e2[1]-e1[1]*e2[0])
  f = (e1, e2, n)
  return f

# ----------------------------------------------------------------------------
#
def frame_transform(f1, f2):

  from numpy import transpose, dot as matrix_multiply
  ft1 = transpose(f1)
  ft2 = transpose(f2)
  from numpy.linalg import inv as inverse
  ft1_inv = inverse(ft1)
  r = matrix_multiply(ft2, ft1_inv)
  import chimera
  xf = chimera.Xform.xform(r[0][0], r[0][1], r[0][2],  0,
                           r[1][0], r[1][1], r[1][2],  0,
                           r[2][0], r[2][1], r[2][2],  0,
                           orthogonalize = True)
  return xf
    
# ----------------------------------------------------------------------------
#
def chains(multiscale_models):

  import MultiScale
  clist = MultiScale.find_pieces(multiscale_models, MultiScale.Chain_Piece)
  return clist
    
# ----------------------------------------------------------------------------
#
def multiscale_models():

  import MultiScale
  d = MultiScale.multiscale_model_dialog()
  if d:
    return d.models
  return []

# ----------------------------------------------------------------------------
#
def chain_center(chain):

  xyz = chain.lan_chain.source_atom_xyz()
  sc = center(xyz)
  from Matrix import apply_matrix, xform_matrix
  c = apply_matrix(xform_matrix(chain.xform), sc)
  return c

# ----------------------------------------------------------------------------
#
def chain_radial_size(chain):

  xyz = chain.lan_chain.source_atom_xyz()
  from numpy import array, multiply, sum
  xyzc = array(xyz)
  from Matrix import xform_matrix
  import _contour
  _contour.affine_transform_vertices(xyzc, xform_matrix(chain.xform))
  multiply(xyzc, xyzc, xyzc)
  r2 = sum(xyzc, axis=1)
  r2max = max(r2)
  import math
  r = math.sqrt(r2max)
  return r

# ----------------------------------------------------------------------------
#
def closest_point_index(p, points):

  dmin = None
  kmin = None
  for k in range(len(points)):
    d = distance2(p, points[k])
    if dmin == None or d < dmin:
      dmin = d
      kmin = k
  return kmin

# ----------------------------------------------------------------------------
#
def center(xyz):

  from numpy import sum
  c = sum(xyz, axis = 0) / len(xyz)
  return c

# ----------------------------------------------------------------------------
#
def length(v):

  import math
  d = math.sqrt(v[0]*v[0]+v[1]*v[1]+v[2]*v[2])
  return d

# ----------------------------------------------------------------------------
#
def distance2(u,v):

  dx, dy, dz = map(lambda a,b: a-b, u, v)
  d2 = dx*dx + dy*dy + dz*dz
  return d2
