# -----------------------------------------------------------------------------
# Cubic spline through points in 3D.
#

# -----------------------------------------------------------------------------
# Return cubically interpolated point list.  An Overhauser spline
# (aka Catmul-Rom spline) uses cubic segments that join at the given points
# and have continuous tangent vector.  The tangent vector at point i equals
# the difference vector between points i+1 and i-1.
# For the end segments I use a quadratic curve.
#
# It is assumed that the points are objects with operators +, -,
# and * (by float) defined.  For example, NumPy arrays work.
# But points that are lists or tuples will not work.
#
def overhauser_spline_points(points, segment_subdivisions,
                             limit_tangent = None, return_tangents = False):

  n = len(points)
  if isinstance(segment_subdivisions, int) and n > 0:
    segment_subdivisions = [segment_subdivisions] * (n - 1)
  d = segment_subdivisions
  if n == 0:
    pt = []
  if n == 1:
    if return_tangents:
      pt = [(points[0], (0,0,1))]
    else:
      pt = points
  elif n == 2:
    pt = linear_segment_points(points[0], points[1], d[0], return_tangents)
  else:
    p0 = points[2]
    p1 = points[1]
    p2 = points[0]
    t1 = tangent(p0,p1,p2,limit_tangent)
    pt = quadratic_segment_points(p1, t1, p2, d[0], return_tangents)[1:]
    pt.reverse()
    if return_tangents:
      pt = [(p,-t) for p,t in pt]

    for k in range(1, n-2):
      p0 = points[k-1]
      p1 = points[k]
      p2 = points[k+1]
      p3 = points[k+2]
      t1 = tangent(p0,p1,p2,limit_tangent)
      t2 = tangent(p1,p2,p3,limit_tangent)
      pt.extend(cubic_segment_points(p1, t1, p2, t2, d[k], return_tangents)[:-1])

    p0 = points[-3]
    p1 = points[-2]
    p2 = points[-1]
    t1 = tangent(p0,p1,p2,limit_tangent)
    pt.extend(quadratic_segment_points(p1, t1, p2, d[n-2], return_tangents))

  return pt

# -----------------------------------------------------------------------------
#
def tangent(p0, p1, p2, limit_tangent = None):

  t = p2 - p0
  if not limit_tangent is None:
    t01 = (p1 - p0) * (2*limit_tangent)
    t12 = (p2 - p1) * (2*limit_tangent)
    for i in range(len(t)):
      t[i] = clamp(t[i], 0, t01[i])
      t[i] = clamp(t[i], 0, t12[i])
  return t

# -----------------------------------------------------------------------------
#
def clamp(x, x0, x1):

  if x0 < x1:
    cx = min(max(x, x0), x1)
  else:
    cx = min(max(x, x1), x0)
  return cx

# -----------------------------------------------------------------------------
# Return a sequence of points along a cubic starting at p1 with tangent t1
# and ending at p2 with tangent t2.
#
def cubic_segment_points(p1, t1, p2, t2, subdivisions, return_tangents = False):

  s = p2 - p1
  a = t2 + t1 - s * 2
  b = s * 3 - t2 - t1 * 2
  c = t1
  d = p1
  pt = []
  for k in range(subdivisions + 2):
    t = float(k) / (subdivisions + 1)
    p = d + (c + (b + a * t) * t) * t
    if return_tangents:
      tn = c + (2*b + 3*a*t) * t
      pt.append((p,tn))
    else:
      pt.append(p)
  return pt

# -----------------------------------------------------------------------------
# Return a sequence of points along a quadratic starting at p1 with tangent t1
# and ending at p2.
#
def quadratic_segment_points(p1, t1, p2, subdivisions, return_tangents = False):

  a = p2 - p1 - t1
  b = t1
  c = p1
  pt = []
  for k in range(subdivisions + 2):
    t = float(k) / (subdivisions + 1)
    p = c + (b + a * t) * t
    if return_tangents:
      tn = b + (2*t)*a 
      pt.append((p,tn))
    else:
      pt.append(p)
  return pt

# -----------------------------------------------------------------------------
# Return a sequence of points along a linear segment starting at p1 and ending
# at p2.
#
def linear_segment_points(p1, p2, subdivisions, return_tangents = False):

  a = p2 - p1
  b = p1
  pt = []
  for k in range(subdivisions + 2):
    t = float(k) / (subdivisions + 1)
    p = b + a * t
    if return_tangents:
      pt.append((p,a))
    else:
      pt.append(p)
  return pt
  
# -----------------------------------------------------------------------------
# Return a list of arc lengths for a piecewise linear curve specified by
# points.  The points should be objects with operator - defined such as
# NumPy arrays.  There number of arc lengths returned equals the
# number of points, the first arc length being 0.
#
def arc_lengths(points):

  import math
  arcs = [0]
  for s in range(len(points)-1):
    d = points[s+1] - points[s]
    length = math.sqrt(d[0]*d[0] + d[1]*d[1] + d[2]*d[2])
    arcs.append(arcs[s] + length)
  return arcs
