# -----------------------------------------------------------------------------
# Joins a set of one-dimensional paths to make a surface.  The paths can be
# closed loops (last point same as first point) or have distinct end points.
# Each path is a sequence of xyz point positions.
#
def stitch_curves(curves, varray, caps):

    if len(curves) == 0:
        from numpy import zeros, intc
        tarray = zeros((0,3), intc)
        return tarray
    elif len(curves) == 1:
        tarray = polygon_triangulation(curves[0], varray)
        return tarray

    triangles = []
    if caps:
        c0 = curves[0]
        if len(c0) > 1 and c0[-1] == c0[0]:
            triangles.extend(polygon_triangulation(c0, varray, reverse = True))
    for c,c0 in enumerate(curves[:-1]):
        c1 = curves[c+1]
        if all_open_or_closed((c0,c1)):
            triangles.extend(triangle_strip(c0, c1, varray))
    if caps and len(c1) > 1 and c1[-1] == c1[0]:
        triangles.extend(polygon_triangulation(c1, varray))

    from numpy import array, intc
    tarray = array(triangles, intc)

    return tarray

# -----------------------------------------------------------------------------
#
def all_open_or_closed(clist):

  opened = closed = 0
  for c in clist:
    if len(c) > 1:
      if c[-1] == c[0]:
        closed += 1
      else:
        opened += 1
      if opened > 0 and closed > 0:
        return False
  return True

# -----------------------------------------------------------------------------
#
def triangle_strip(curve1, curve2, varray):

    triangles = []
    v = varray
    n1 = curve_length(curve1)
    n2 = curve_length(curve2)
    p1 = len(curve1)
    p2 = len(curve2)
    i1 = i2 = 0
    while i1 < p1-1 or i2 < p2-1:
        if i1 < p1-1:
            d1 = distance2(v[curve1[i1+1]], v[curve2[i2]])
        else:
            d1 = None
        if i2 < p2-1:
            d2 = distance2(v[curve1[i1]], v[curve2[i2+1]])
        else:
            d2 = None
        if d2 == None or (d1 != None and d1 < d2):
            triangles.append((curve1[i1%n1], curve1[(i1+1)%n1], curve2[i2%n2]))
            i1 += 1
        else:
            triangles.append((curve1[i1%n1], curve2[(i2+1)%n2], curve2[i2%n2]))
            i2 += 1
    return triangles

# -----------------------------------------------------------------------------
# Number of points in closed or open curve.
#
def curve_length(curve):

    n = len(curve)
    if n > 1 and curve[-1] == curve[0]:
        return n-1
    return n
    
# -----------------------------------------------------------------------------
#
def distance2(p1, p2):

    d2 = 0
    for k in range(len(p1)):
        d = p2[k] - p1[k]
        d2 += d*d
    return d2

# -----------------------------------------------------------------------------
# Adjust ordering of points in curves for stitching.
# For closed loops choose first point as one with maximum x value and choose
# order of points for counter-clockwise traversal.  For open curves choose
# vectors between end points of successive curves to have positive inner
# product.
#
def order_points_for_stitching(curves, varray, axis):

    if len(curves) == 0:
        return curves

    from Matrix import orthonormal_frame
    axes = orthonormal_frame(axis)

    from numpy import dot, transpose, subtract, argmax, inner
    xyz = dot(varray, transpose(axes))

    c0 = curves[0]
    loop = (len(c0) > 1 and c0[0] == c0[-1])
    gap = subtract(xyz[c0[-1]], xyz[c0[0]])

    colist = []
    for c in curves:
        if loop:
            i = argmax([x for x,y,z in xyz[c]])
            ci = list(c[i:]+c[1:i+1])
            if center_and_normal(c, xyz)[1][2] < 0:
                ci.reverse()
            colist.append(ci)
        else:
            gapc = subtract(xyz[c[-1]],xyz[c[0]])
            if inner(gapc, gap) >= 0:
                colist.append(c)
                gap = gapc
            else:
                colist.append(c[::-1])
                gap = -gapc

    return colist

# -----------------------------------------------------------------------------
# Take a list of chains (given by indices) and put the chains in order for
# stitching a surface.  Use average normal to determine axis.
#
# Might issue warning if two chain are within 10**-4 * (normal extent)
# along normal to catch common case of multiple chains in a single plane.
#
def order_chains(curves, varray):

  n = len(curves)
  if n <= 1:
    return curves, (0,0,1)

  # Determine projection axis
  sclist = list(curves)
  sclist.sort(lambda a,b: -cmp(len(a),len(b)))
  cn = [center_and_normal(c,varray) for c in sclist]
  nlist = [normal for center, normal in cn]
  nsum = nlist[0]
  from numpy import dot, sqrt
  for n in nlist[1:]:
    if dot(n, nsum) >= 0: nsum += n
    else:                 nsum -= n
  norm = sqrt(dot(nsum,nsum))
  if norm > 0:
    axis = nsum / norm
  else:
    axis = (0,0,1)

  # Sort by position of chain centers along axis.
  pos = [dot(axis,center) for center, normal in cn]
  oclist = [c for p, c in sorted(zip(pos,sclist))]
  return oclist, axis

# -----------------------------------------------------------------------------
#
def center_and_normal(curve, varray):

    if len(curve) >= 2 and curve[-1] == curve[0]:
        curve = curve[:-1]

    xyz = varray[curve]
    n = len(curve)
    center = xyz.sum(axis = 0) / n
    p = xyz - center
    from numpy import cross
    normal = cross(p[-1],p[0])
    for i in range(n-1):
        normal += cross(p[i],p[i+1])
    return center, normal

# -----------------------------------------------------------------------------
#
def triangle_normal(t, varray):

    v1, v2, v3 = t
    from numpy import cross
    normal = cross(varray[v2]-varray[v1], varray[v3]-varray[v1])
    return normal

# -----------------------------------------------------------------------------
#
def polygon_triangulation(curve, varray, reverse = False):

    if len(curve) >= 2 and curve[-1] == curve[0]:
        curve = curve[:-1]

    tarray = nonconvex_polygon_triangulation(curve, varray, reverse)
    if len(tarray) > 0:
        return tarray

    n = len(curve)
    from numpy import zeros, intc
    tarray = zeros((max(0,n-2),3), intc)
    if n >= 3:
        tarray[:,0] = curve[0]
        if reverse:
            tarray[:,1] = curve[2:]
            tarray[:,2] = curve[1:-1]
        else:
            tarray[:,1] = curve[1:-1]
            tarray[:,2] = curve[2:]
    return tarray

# -----------------------------------------------------------------------------
#
def nonconvex_polygon_triangulation(curve, varray, reverse):

    c, normal = center_and_normal(curve, varray)
    v = varray.take(curve, axis = 0)
    if reverse:
        v = v[::-1,:]
        normal = -normal
    loops = ((0,len(v)-1),)
    from _surfacecap import triangulate_polygon
    t = triangulate_polygon(loops, normal, v)
    from numpy import array
    tarray = array(curve)[t]
    return tarray
