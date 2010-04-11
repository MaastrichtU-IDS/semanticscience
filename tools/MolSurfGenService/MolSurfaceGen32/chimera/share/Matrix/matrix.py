# -----------------------------------------------------------------------------
#
def apply_matrix(tf, points):

  from numpy import array, transpose, add
  from numpy import dot as matrix_multiply
  tf = array(tf)
  r = matrix_multiply(points, transpose(tf[:,:3]))
  add(r, tf[:,3], r)
  return r

# -----------------------------------------------------------------------------
#
def apply_matrix_without_translation(tf, v):

  from numpy import array, transpose, add
  from numpy import dot as matrix_multiply
  tf = array(tf)
  r = matrix_multiply(v, transpose(tf[:,:3]))
  return r
  
# -----------------------------------------------------------------------------
#
def apply_inverse_matrix(tf, *xyz_list):

  import chimera
  if isinstance(tf, chimera.Xform):
    tf = xform_matrix(tf)
  inv_tf = invert_matrix(tf)

  inv_tf_xyz_list = []
  for xyz in xyz_list:
    inv_tf_xyz = apply_matrix(inv_tf, xyz)
    inv_tf_xyz_list.append(inv_tf_xyz)

  if len(xyz_list) == 1:
    return inv_tf_xyz_list[0]
  
  return inv_tf_xyz_list
    
# -----------------------------------------------------------------------------
#
def zero_translation(tf):

    return ((tf[0][0], tf[0][1], tf[0][2], 0),
            (tf[1][0], tf[1][1], tf[1][2], 0),
            (tf[2][0], tf[2][1], tf[2][2], 0))
  
# -----------------------------------------------------------------------------
#
def translation_matrix(shift):

  from numpy import array
  tf = array(((1.0, 0, 0, shift[0]),
              (0, 1.0, 0, shift[1]),
              (0, 0, 1.0, shift[2])))
  return tf
  
# -----------------------------------------------------------------------------
#
def identity_matrix():

  return ((1.0,0,0,0), (0,1.0,0,0), (0,0,1.0,0))
  
# -----------------------------------------------------------------------------
#
def is_identity_matrix(tf, tolerance = 1e-6):

  # Matrix argument may be a NumPy array or a tuple.
  # Need to be careful in how comparison is done.  Comparing a NumPy array
  # to a tuple gives an array of element wise comparisons.
  id = ((1,0,0,0), (0,1,0,0), (0,0,1,0))
  for r in range(3):
    for c in range(4):
      if abs(tf[r][c] - id[r][c]) > tolerance:
        return False
  return True

# -----------------------------------------------------------------------------
#
def multiply_matrices(*tf_list):

  if len(tf_list) == 2:
    tf1, tf2 = tf_list
    r1 = tf1[:,:3]
    t1 = tf1[:,3]
    r2 = tf2[:,:3]
    t2 = tf2[:,3]
    from numpy import zeros, float, add
    from numpy import dot as matrix_multiply
    tf = zeros((3,4), float)
    r = tf[:,:3]
    t = tf[:,3]
    r[:] = matrix_multiply(r1, r2)
    t[:] = add(t1, matrix_multiply(r1, t2))
  else:
    tf = multiply_matrices(*tf_list[1:])
    tf = multiply_matrices(tf_list[0], tf)
  return tf

# -----------------------------------------------------------------------------
#
def invert_matrix(tf):

    from numpy import array, zeros, float, linalg
    tf = array(tf)
    r = tf[:,:3]
    t = tf[:,3]
    tfinv = zeros((3,4), float)
    rinv = tfinv[:,:3]
    tinv = tfinv[:,3]
    from numpy.linalg import inv as matrix_inverse
    from numpy import dot as matrix_multiply
    rinv[:,:] = matrix_inverse(r)
    tinv[:] = matrix_multiply(rinv, -t)
    return tfinv

# -----------------------------------------------------------------------------
# Transpose the rotation part.
#
def transpose_matrix(tf):

  return ((tf[0][0], tf[1][0], tf[2][0], tf[0][3]),
          (tf[0][1], tf[1][1], tf[2][1], tf[1][3]),
          (tf[0][2], tf[1][2], tf[2][2], tf[2][3]))
        
# -----------------------------------------------------------------------------
#
def matrix_products(mlist1, mlist2):

  plist = []
  for m1 in mlist1:
    for m2 in mlist2:
      m1xm2 = multiply_matrices(m1, m2)
      plist.append(m1xm2)
  return plist
        
# -----------------------------------------------------------------------------
#
def multiply_matrices(*mlist):

  if len(mlist) == 2:
    m1, m2 = mlist
    p = [[0,0,0,0],
         [0,0,0,0],
         [0,0,0,0]]
    for r in range(3):
      for c in range(4):
        p[r][c] = m1[r][0]*m2[0][c] + m1[r][1]*m2[1][c] + m1[r][2]*m2[2][c]
        p[r][3] += m1[r][3]
    p = tuple(map(tuple, p))
  else:
    p = multiply_matrices(*mlist[1:])
    p = multiply_matrices(mlist[0], p)
  return p

# -----------------------------------------------------------------------------
#
def chimera_xform(matrix):

  m = matrix
  import chimera
  xf = chimera.Xform.xform(m[0][0], m[0][1], m[0][2], m[0][3],
                           m[1][0], m[1][1], m[1][2], m[1][3],
                           m[2][0], m[2][1], m[2][2], m[2][3],
                           orthogonalize = 1)
  return xf

# -----------------------------------------------------------------------------
#
def same_xform(xf1, xf2, angle_tolerance = 0, shift_tolerance = 0):

  if angle_tolerance == 0 and shift_tolerance == 0:
    return xf1.getOpenGLMatrix() == xf2.getOpenGLMatrix()
  from chimera import Xform
  xf = Xform()
  xf.multiply(xf1)
  xf.multiply(xf2.inverse())
  trans = xf.getTranslation()
  axis, angle = xf.getRotation()
  if (abs(angle) > angle_tolerance or trans.length > shift_tolerance):
    return False
  return True

# -----------------------------------------------------------------------------
#
def determinant(tf):

  return (tf[0][0]*(tf[1][1]*tf[2][2] - tf[1][2]*tf[2][1]) +
          tf[0][1]*(tf[1][2]*tf[2][0] - tf[1][0]*tf[2][2]) +
          tf[0][2]*(tf[1][0]*tf[2][1] - tf[1][1]*tf[2][0]))
  
# -----------------------------------------------------------------------------
#
def xform_matrix(xform):

  rx, ry, rz, t = xform.getCoordFrame()
  return ((rx[0], ry[0], rz[0], t[0]),
          (rx[1], ry[1], rz[1], t[1]),
          (rx[2], ry[2], rz[2], t[2]))

# -----------------------------------------------------------------------------
# Angle is in degrees.
#
def rotation_from_axis_angle(axis, angle):

  from chimera import Xform, Vector
  r = Xform.rotation(Vector(*axis), angle)
  m = r.getOpenGLMatrix()
  rm = ((m[0], m[4], m[8]),
        (m[1], m[5], m[9]),
        (m[2], m[6], m[10]))
  return rm
    
# -----------------------------------------------------------------------------
#
def rotation_axis_angle(r):

    from chimera import Xform
    xf = Xform.xform(r[0][0], r[0][1], r[0][2], 0,
                     r[1][0], r[1][1], r[1][2], 0,
                     r[2][0], r[2][1], r[2][2], 0)
    axis, angle = xf.getRotation()
    return tuple(axis.data()), angle
    
# -----------------------------------------------------------------------------
#
def orthogonalize(r):

    from chimera import Xform
    xf = Xform.xform(r[0][0], r[0][1], r[0][2], 0,
                     r[1][0], r[1][1], r[1][2], 0,
                     r[2][0], r[2][1], r[2][2], 0,
                     orthogonalize = True)
    ro = xform_matrix(xf)
    ro33 = tuple([row[:3] for row in ro])
    return ro33
    
# -----------------------------------------------------------------------------
#
def cell_angles(axes):

  ca = [vector_angle(axes[(a+1)%3], axes[(a+2)%3]) for a in (0,1,2)]
  return ca

# -----------------------------------------------------------------------------
#
def cell_angles_and_rotation(axes):

  ca = cell_angles(axes)
  ska = skew_axes(ca)
  na = [normalize_vector(v) for v in axes]
  from numpy.linalg import inv as matrix_inverse
  from numpy import dot as matrix_multiply
  r = matrix_multiply(matrix_inverse(ska), na).transpose()
  return ca, r

# -----------------------------------------------------------------------------
# Return axes corresponding to cell_angles given in degrees.
#
def skew_axes(cell_angles):

  # Convert to radians
  from math import pi
  alpha, beta, gamma = map(lambda a: a * pi / 180, cell_angles)
  
  from math import sin, cos, sqrt
  cg = cos(gamma)
  sg = sin(gamma)
  cb = cos(beta)
  ca = cos(alpha)
  c1 = (ca - cb*cg)/sg
  c2 = sqrt(1 - cb*cb - c1*c1)

  axes = ((1, 0, 0), (cg, sg, 0), (cb, c1, c2))
  return axes

# -----------------------------------------------------------------------------
#
def transpose(m):

  r,c = len(m), len(m[0])
  mt = tuple([tuple([m[a][b] for a in range(r)]) for b in range(c)])
  return mt

# -----------------------------------------------------------------------------
#
def orthonormal_frame(zaxis):

  z = normalize_vector(zaxis)
  if z[2] != 0 or z[0] != 0:
    x = (z[2], 0, -z[0])
  else:
    x = (0,0,1)
  y = cross_product(z,x)
  return (x,y,z)

# -----------------------------------------------------------------------------
#
def vector_rotation_transform(u,v):

  cuv = cross_product(u,v)
  axis = normalize_vector(cuv)
  from math import atan2, pi
  from numpy import dot as inner_product
  angle = atan2(norm(cuv),inner_product(u,v)) * 180/pi
  r = rotation_transform(axis, angle, (0,0,0))
  return r
  
# -----------------------------------------------------------------------------
#
def cross_product(u,v):

  return (u[1]*v[2]-u[2]*v[1], u[2]*v[0]-u[0]*v[2], u[0]*v[1]-u[1]*v[0])
        
# -----------------------------------------------------------------------------
#
def cross_products(u, v):

    n = len(u)
    from numpy import zeros, multiply, subtract
    cp = zeros((n,3), u.dtype)
    temp = zeros((n,), u.dtype)
    for a, i, j in ((0, 1, 2), (1, 2, 0), (2, 0, 1)):
        multiply(u[:,i], v[:,j], cp[:,a])
        multiply(u[:,j], v[:,i], temp)
        subtract(cp[:,a], temp, cp[:,a])
    return cp

# -----------------------------------------------------------------------------
#
def cross_product_transform(u):

    return ((0, -u[2], u[1], 0),
            (u[2], 0, -u[0], 0),
            (-u[1], u[0], 0, 0))

# -----------------------------------------------------------------------------
# Angle between vectors u and v in degrees.
#
def vector_angle(u,v):

  uv = length(u) * length(v)
  if uv == 0:
    return 0.0
  from math import acos, pi
  a = acos(sum([u[i]*v[i] for i in range(len(u))]) / uv)
  deg = a * 180.0 / pi
  return deg
  
# -----------------------------------------------------------------------------
#
def normalize_vector(v):

  d = length(v)
  if d == 0:
    d = 1
  return tuple([e/d for e in v])
  
# -----------------------------------------------------------------------------
#
def normalize_vectors(v):

  if len(v) == 0:
    return v
  from numpy import multiply, sum, sqrt
  norms = sqrt(sum(multiply(v, v), axis = 1))
  if not norms.all():
    # Don't divide by zero for zero length vectors.  Would produce NaN values.
    norms += (norms == 0)
  for a in range(len(v[0])):
    v[:,a] /= norms

# -----------------------------------------------------------------------------
#
def length(v):

  from math import sqrt
  d = sqrt(sum([e*e for e in v]))
  return d
  
# -----------------------------------------------------------------------------
#
def distance(u,v):

  duv = map(lambda a,b: a-b, u, v)
  return length(duv)
  
# -----------------------------------------------------------------------------
#
def sign(x):

  if x >= 0:
    return 1
  return -1

# -----------------------------------------------------------------------------
# Angle is in degrees.
#
def rotation_transform(axis, angle, center = (0,0,0)):

    axis = normalize_vector(axis)

    from math import pi, sin, cos

    arad = angle*pi/180.0
    sa = sin(arad)
    ca = cos(arad)
    k = 1 - ca
    ax, ay, az = axis
    tf = ((1 + k*(ax*ax-1), -az*sa+k*ax*ay, ay*sa+k*ax*az, 0),
          (az*sa+k*ax*ay, 1 + k*(ay*ay-1), -ax*sa+k*ay*az, 0),
          (-ay*sa+k*ax*az, ax*sa+k*ay*az, 1 + k*(az*az-1), 0))
    cx, cy, cz = center
    c_tf = ((1,0,0,cx), (0,1,0,cy), (0,0,1,cz))
    inv_c_tf = ((1,0,0,-cx), (0,1,0,-cy), (0,0,1,-cz))
    from Matrix import multiply_matrices
    rtf = multiply_matrices(c_tf, tf, inv_c_tf)
    return rtf

# -----------------------------------------------------------------------------
# Determine the rotation axis, point on axis, rotation angle, and shift along
# the rotation axis that describes a transform.
#
def axis_center_angle_shift(tf):

    from Matrix import chimera_xform
    axis, angle = chimera_xform(tf).getRotation()
    axis = axis.data()
    t = map(lambda r: r[3], tf)
    axt = cross_product(axis, t)
    axaxt = cross_product(axis, axt)
    from math import pi, cos, sin
    a2 = 0.5 * angle * pi / 180         # Half angle in radians
    try:
        ct2 = cos(a2) / sin(a2)
    except:
        ct2 = None    # Identity rotation
    if ct2 == None:
        axis_point = (0,0,0)
    else:
        axis_point = tuple(map(lambda a,b: .5*ct2*a - .5*b, axt, axaxt))
    from numpy import dot as inner_product
    shift = inner_product(axis, t)

    return axis, axis_point, angle, shift

# -----------------------------------------------------------------------------
# Return new axis point on axis with coordinate equal to zero for the largest
# magnitude component of the axis vector.  This makes it easier for users to
# use the axis point as an offset to describe symmetry axis locations.
#
def axis_point_adjust(axis_point, axis):

    # Find position of largest magnitude axis component.
    a = sorted(map(lambda c,k: (abs(c),k), axis, range(3)))[-1][1]
    f = -axis_point[a]/axis[a]
    ap = tuple(map(lambda b,c: b+f*c, axis_point, axis))
    return ap

# -----------------------------------------------------------------------------
#
def project_to_axis(p, axis, axis_point):

  from numpy import array, dot
  p, axis, axis_point = array(p), array(axis), array(axis_point)
  pp = axis_point + dot(p - axis_point, axis) * axis
  return pp

# -----------------------------------------------------------------------------
#
def shift_and_angle(tf, center):

    from Matrix import chimera_xform, apply_matrix
    moved_center = apply_matrix(tf, center)
    shift_vector = map(lambda a,b: a-b, moved_center, center)
    shift = norm(shift_vector)
    axis, angle = chimera_xform(tf).getRotation()
    return shift, angle
        
# -----------------------------------------------------------------------------
#
def maximum_norm(v):

    from numpy import maximum
    d2 = maximum.reduce(v[:,0]*v[:,0] + v[:,1]*v[:,1] + v[:,2]*v[:,2])
    import math
    d = math.sqrt(d2)
    return d

# -----------------------------------------------------------------------------
#
def norm(u):

    import math
    n = math.sqrt(u[0]*u[0] + u[1]*u[1] + u[2]*u[2])
    return n

# -----------------------------------------------------------------------------
#
def transformation_description(tf):

  import Matrix
  axis, axis_point, angle, axis_shift = Matrix.axis_center_angle_shift(tf)
  axis_point = Matrix.axis_point_adjust(axis_point, axis)

  message = ('  Matrix rotation and translation\n' +
             '   %12.8f %12.8f %12.8f %12.8f\n' % tf[0] +
             '   %12.8f %12.8f %12.8f %12.8f\n' % tf[1] +
             '   %12.8f %12.8f %12.8f %12.8f\n' % tf[2] +
             '  Axis %12.8f %12.8f %12.8f\n' % axis +
             '  Axis point %12.8f %12.8f %12.8f\n' % axis_point +
             '  Rotation angle (degrees) %12.8f\n' % (angle,) +
             '  Shift along axis %12.8f\n' % (axis_shift,))
  return message

# -----------------------------------------------------------------------------
#
def xforms_differ(xf1, xf2, angle_limit = 0.1, translation_limit = 0.01):

  xf = xf1.inverse()
  xf.multiply(xf2)
  axis, angle = xf.getRotation()
  trans = xf.getTranslation()
  differ = (angle > angle_limit or trans.length > translation_limit)
  return differ

# -----------------------------------------------------------------------------
# Rotation applied first, then translation.
#
def euler_xform(euler_angles, translation):

    xf = euler_rotation(*euler_angles)
    from chimera import Xform
    xf.premultiply(Xform.translation(*translation))
    return xf
                    
# -----------------------------------------------------------------------------
# Convert Euler angles to an equivalent Chimera transformation matrix.
#
# Angles must be in degrees, not radians.
#
# Uses the most common Euler angle convention z-x-z (the chi-convention)
# described at
#
#   http://mathworld.wolfram.com/EulerAngles.html
#
def euler_rotation(phi, theta, psi):

    from chimera import Xform, Vector
    xf1 = Xform.rotation(Vector(0,0,1), phi)    # Rotate about z-axis
    xp = xf1.apply(Vector(1,0,0))               # New x-axis
    xf2 = Xform.rotation(xp, theta)             # Rotate about new x-axis
    zp = xf2.apply(Vector(0,0,1))               # New z-axis
    xf3 = Xform.rotation(zp, psi)               # Rotate about new z-axis

    xf = Xform()
    xf.premultiply(xf1)
    xf.premultiply(xf2)
    xf.premultiply(xf3)

    return xf

# -----------------------------------------------------------------------------
# Returned angles in degrees in z-x-z convention.
#
def euler_angles(tf):

  z1, z2, z3 = [tf[a][2] for a in (0,1,2)]
  from math import atan2, sqrt, pi
  z12 = sqrt(z1*z1 + z2*z2)
  beta = atan2(z12, z3)
  if z12 < 1e-6:
    # Pure z rotation.
    x1, x2 = tf[0][0], tf[1][0]
    alpha = atan2(x2, x1)
    gamma = 0
  else:
    alpha = atan2(z1, -z2)
    x3 = tf[2][0]
    y3 = tf[2][1]
    gamma = atan2(x3, y3)
  return (alpha*180/pi, beta*180/pi, gamma*180/pi)

# -----------------------------------------------------------------------------
#
def xform_xyz(xyz, from_xform, to_xform):

  from chimera import Point
  p = apply(Point, xyz)
  p1 = from_xform.apply(p)
  to_xform.invert()
  p2 = to_xform.apply(p1)
  to_xform.invert()
  return (p2.x, p2.y, p2.z)

# -----------------------------------------------------------------------------
#
def xform_points(points, xf, to_xf):

  txf = to_xf.inverse()
  txf.multiply(xf)
  tf = xform_matrix(txf)
  from _contour import affine_transform_vertices
  affine_transform_vertices(points, tf)

# -----------------------------------------------------------------------------
# Applies only rotation.
#
def xform_vectors(vectors, xf, to_xf):

  txf = to_xf.inverse()
  txf.multiply(xf)
  tf = zero_translation(xform_matrix(txf))
  from _contour import affine_transform_vertices
  affine_transform_vertices(vectors, tf)
