# This module defines some geometrical objects in 3D-space.
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

"""This module defines several elementary geometrical objects, which
can be useful in the construction and analysis of molecular systems.
There are essentially two kinds of geometrical objects: shape objects
(spheres, planes, etc.), from which intersections can be calculated,
and lattice objects, which define a regular arrangements of points.
"""

from Scientific.Geometry import Vector
from Scientific import N

# Error type
class GeomError(Exception):
    pass

# Small number
eps = 1.e-16

#
# The base class
#
class GeometricalObject3D:

    """3D shape object

    This is an Glossary:abstract-base-class. To create 3D objects,
    use one of its subclasses.
    """
    
    def intersectWith(self, other):
        """Return a 3D object that represents the intersection with |other|
        (another 3D object)."""
	if self.__class__ > other.__class__:
	    self, other = other, self
	try:
	    f, switch = _intersectTable[(self.__class__, other.__class__)]
	    if switch:
		return f(other, self)
	    else:
		return f(self, other)
	except KeyError:
	    raise GeomError("Can't calculate intersection of " +
			     self.__class__.__name__ + " with " +
			     other.__class__.__name__)

    def hasPoint(self, point):
	return self.distanceFrom(point) < eps

    # subclasses that enclose a volume should override this method
    # a return value of None indicates "don't know", "can't compute",
    # or "not implemented (yet)".
    def enclosesPoint(self, point):
        return None

_intersectTable = {}

#
# Boxes
#
class Box(GeometricalObject3D):

    """Box

    A Glossary:Subclass of Class:MMTK.Geometry.GeometricalObject3D.

    Constructor: Box(|corner1|, |corner2|)

    Arguments:

    |corner1|, |corner2| -- diagonally opposite corner points
    """

    def __init__(self, corner1, corner2):
        c1 = N.minimum(corner1.array, corner2.array)
        c2 = N.maximum(corner1.array, corner2.array)
        self.corners = c1, c2

    def __repr__(self):
        return 'Box(' + `Vector(self.corners[0])` + ', ' \
               + `Vector(self.corners[1])` + ')'

    __str__ = __repr__

    def volume(self):
        c1, c2 = self.corners
        return N.multiply.reduce(c2-c1)

    def hasPoint(self, point):
        c1, c2 = self.corners
        min1 = N.minimum.reduce(N.fabs(point.array-c1))
        min2 = N.minimum.reduce(N.fabs(point.array-c2))
        return min1 < eps or min2 < eps

    def enclosesPoint(self, point):
        c1, c2 = self.corners
        out1 = N.logical_or.reduce(N.less(point.array-c1, 0))
        out2 = N.logical_or.reduce(N.less_equal(c2-point.array, 0))
        return not (out1 or out2)

    def cornerPoints(self):
        (c1x, c1y, c1z), (c2x, c2y, c2z) = self.corners
        return [Vector(c1x, c1y, c1z),
                Vector(c1x, c1y, c2z),
                Vector(c1x, c2y, c1z),
                Vector(c2x, c1y, c1z),
                Vector(c2x, c2y, c1z),
                Vector(c2x, c1y, c2z),
                Vector(c1x, c2y, c2z),
                Vector(c2x, c2y, c2z)]

#
# Spheres
#
class Sphere(GeometricalObject3D):

    """Sphere

    A Glossary:Subclass of Class:MMTK.Geometry.GeometricalObject3D.

    Constructor: Sphere(|center|, |radius|)

    Arguments:

    |center| -- the center of the sphere (a vector)

    |radius| -- the radius of the sphere (a number)
    """

    def __init__(self, center, radius):
	self.center = center
	self.radius = radius

    def __repr__(self):
        return 'Sphere(' + `self.center` + ', ' + `self.radius` + ')'
    __str__ = __repr__

    def volume(self):
	return (4.*N.pi/3.) * self.radius**3

    def hasPoint(self, point):
        return N.fabs((point-self.center).length()-self.radius) < eps

    def enclosesPoint(self, point):
        return (point - self.center).length() < self.radius

##      def coordList(self, no_nulls = 0):
##          result = []
##          from Scientific.N import arange
##          for normal in [Vector(1,0,0), Vector(0,1,0), Vector(0,0,1),\
##                         Vector(1,1,1)]:
##              v0 = normal.cross(randomDirection())
##              if result and not no_nulls:
##                  result.append(None)
##              for u in arange(0, 2*N.pi, N.pi/8):
##                  v = rotateDirection(v0, normal, u)
##                  result.append(self.center + self.radius*v.normal())
##          return result

##  class Prism(GeometricalObject3D):

##      """Prism must be constructed from a convex Polygon which is a sequence of
##       coplanar points, ordered clockwise as seen from inside prism."""

##      def __init__(self, polygon, height):
##         self.polygon = polygon
##         self.height = height
##         self.vector = height*polygon.normal

##      def volume(self):
##         raise 'not implemented'

##      def __repr__(self):
##         return 'Prism(' + `self.polygon` + ', ' + `self.height` + ')'
##      __str__ = __repr__

##      def enclosesPoint(self, point):
##         return 0#??

##      def coordList(self):
##         result = polygon[:]
##         result.append(polygon[0])
##         for pt in polygon:
##             result.append(pt + self.vector)
##             result.append(pt)
##             result.append(pt + self.vector)
##         result.append(polygon[0] + self.vector)
##         return result

#
# Cylinders
#
class Cylinder(GeometricalObject3D):

    """Cylinder

    A Glossary:Subclass of Class:MMTK.Geometry.GeometricalObject3D.

    Constructor: Cylinder(|center1|, |center2|, |radius|)

    Arguments:

    |center1| -- the center of the bottom circle (a vector)

    |center2| -- the center of the top circle (a vector)

    |radius| -- the radius (a number)
    """

    def __init__(self, center1, center2, radius):
       self.center1 = center1            # center of base
       self.center2 = center2            # center of top
       self.radius = radius
       self.height = (center2-center1).length()

    def volume(self):
       return N.pi*self.radius*self.radius*self.height

    def __repr__(self):
       return 'Cylinder(' + `self.center1` + ', ' + `self.center2` + \
              ', ' + `self.radius` + ')'
    __str__ = __repr__

    def hasPoint(self, point):
       center_line = LineSegment(self.center1, self.center2)
       pt = center_line.projectionOf(point)
       if pt is None:
           return 0
       return N.fabs((point - pt).length() - self.radius) < eps

    def enclosesPoint(self, point):
       center_line = LineSegment(self.center1, self.center2)
       pt = center_line.projectionOf(point)
       if pt is None:
           return 0
       return (point - pt).length() < self.radius

##      def coordList(self):
##         axis = self.center2-self.center1
##         return Circle(self.center1, axis, self.radius).coordList() + \
##                Circle(self.center2, axis, self.radius).coordList()


##  #
##  # All but last point of pyramid must be coplanar
##  #

##  class Pyramid(GeometricalObject3D):

##      def __init__(self, points):
##         self.points = points

##      def center(self):
##         return reduce(__add__, self.points) / len(self.points)

##      def boundingBox(self):
##         min = self.points[0].array
##         max = min
##         for pt in self.points[1:]:
##             r = pt.array
##             min = N.minimum(min, r)
##             max = N.maximum(max, r)
##         return Vector(min), Vector(max)

##      def volume(self):
##         base = Polygon(self.points[0:-1])
##         return base.area() * base.planeOf().distanceFrom(self.points[-1])\
##                / (len(self.points) - 1)


#
# Planes
#
class Plane(GeometricalObject3D):

    """2D plane in 3D space

    A Glossary:Subclass of Class:MMTK.Geometry.GeometricalObject3D.

    Constructor: Plane(|point|, |normal|)
                 or Plane(|point1|, |point2|, |point3|)

    Arguments:

    |point| -- any point in the plane

    |normal| -- the normal vector of the plane

    |point1|, |point2|, |point3| -- three points in the plane that
                                    are not collinear.
    """

    def __init__(self, *args):
	if len(args) == 2:   # point, normal
	    self.normal = args[1].normal()
	    self.distance_from_zero = self.normal*args[0]
	else:                # three points
	    v1 = args[1]-args[0]
	    v2 = args[2]-args[1]
	    self.normal = (v1.cross(v2)).normal()
	    self.distance_from_zero = self.normal*args[1]

    def __repr__(self):
        return 'Plane(' + str(self.normal*self.distance_from_zero) + \
               ', ' + str(self.normal) + ')'
    __str__ = __repr__

    def distanceFrom(self, point):
	return abs(self.normal*point-self.distance_from_zero)

    def projectionOf(self, point):
        return point - (self.normal*point-self.distance_from_zero)*self.normal

    def rotate(self, axis, angle):
	point = rotatePoint(self.distance_from_zero*self.normal, axis, angle)
	normal = rotateDirection(self.normal, axis, angle)
	return Plane(point, normal)

    def volume(self):
	return 0.

#
# Infinite cones
#
class Cone(GeometricalObject3D):

    """Cone

    A Glossary:Subclass of Class:MMTK.Geometry.GeometricalObject3D.

    Constructor: Cone(|center|, |axis|, |angle|)

    Arguments:

    |center| -- the center (tip) of the cone (a vector)

    |axis| -- the direction of the axis of rotational symmetry (a vector)

    |angle| -- the angle between any straight line on the cone surface and
               the axis of symmetry (a number)
    """

    def __init__(self, center, axis, angle):
	self.center = center
	self.axis = axis.normal()
	self.angle = angle

    def __repr__(self):
        return 'Cone(' + `self.center` + ', ' + `self.axis` + ',' + \
               `self.angle` + ')'
    __str__ = __repr__

    def volume(self):
	return None

#
# Circles
#
class Circle(GeometricalObject3D):

    """2D circle in 3D space

    A Glossary:Subclass of Class:MMTK.Geometry.GeometricalObject3D.

    Constructor: Circle(|center|, |normal|, |radius|)

    Arguments:

    |center| -- the center of the circle (a vector)

    |normal| -- the normal vector of the plane of the sphere (vector)

    |radius| -- the radius of the circle (a number)
    """

    def __init__(self, center, normal, radius):
	self.center = center
	self.normal = normal
	self.radius = radius

    def planeOf(self):
        return Plane(self.center, self.normal)

    def __repr__(self):
        return 'Circle(' + `self.center` + ', ' + `self.normal` + \
               ', ' + `self.radius` + ')'
    __str__ = __repr__

    def volume(self):
        return 0.

    def distanceFrom(self, point):
        plane = self.planeOf()
        project_on_plane = plane.projectionOf(point)
        center_to_projection = project_on_plane - self.center
        if center_to_projection.length() < eps:
            return 0
        closest_point = self.center + self.radius*center_to_projection.normal()
        return (point - closest_point).length()

##      def coordList(self):
##          result = []
##          from Scientific.N import arange
##          v0 = self.normal.cross(randomDirection())
##          for u in arange(0, 2*N.pi, N.pi/64):
##              v = rotateDirection(v0, self.normal, u)
##              result.append(self.center + self.radius*v.normal())
##          return result

##  class Polygon(GeometricalObject3D):

##      def __init__(self, pt_list):
##          assert(len(pt_list) >= 3)
##          self.points = pt_list
##          v1 = pt_list[2] - pt_list[1]
##          self.normal = v1.cross(pt_list[1] - pt_list[0]).normal()

##      def planeOf(self):
##          return Plane(self.points[0], self.normal)

##      def __repr__(self):
##          points_repr = `self.points[0]`
##          for pt in self.points[1:]:
##              points_repr = points_repr + ', ' + `pt`
##          return 'Polygon(' + points_repr + ')'
##      __str__ = __repr__

##      def __getitem__(self, index):
##          return self.points[index]

##      def center(self):
##          sum = Vector(0,0,0)
##          for pt in self.points:
##              sum = sum + pt
##          return sum / len(self.points)

##      def area(self):
##          assert(len(self.points) <= 4)
##          if len(self.points) == 4:
##              return (self.points[1] - self.points[0]).length() *\
##                     (self.points[2] - self.points[1]).length()
##          v = self.points[1] - self.points[0]
##          side1 = Line(self.points[0], v)
##          ht = side1.distanceFrom(self.points[2])
##          return 0.5 * v.length() * ht

##       def volume(self):
##           return 0.
 
##      # assumes convex polygon
##      def pointNearest(self, point, proj_only = 0):
##          plane = self.planeOf()
##          project_on_plane = plane.projectionOf(point)
##          n = len(self.points)
##          is_inside = 1
##          nearest_dist = 1.e9
##          for i in range(n):
##              edge = LineSegment(self.points[i], self.points[(i + 1) % n])
##              v = project_on_plane - self.points[i]
##              if v.cross(edge.direction) * self.normal < 0:
##                  is_inside = 0
##              near_pt = edge.pointNearest(point)
##              d = (near_pt - point).length()
##              if d < nearest_dist:
##                  nearest_dist = d
##                  nearest_point = near_pt
##          if is_inside:
##              return project_on_plane
##          if proj_only:
##              return None
##          return nearest_point

##      def projectionOf(self, point):
##          return self.pointNearest(point, 1)

##      def distanceFrom(self, point):
##          return (point - self.pointNearest(point)).length()

##      def coordList(self):
##          return self.points

##      def edgeVectors(self):
##          edges = [self.points[0] - self.points[-1]]
##          for i in range(1, len(self.points)):
##              edges.append(self.points[i] - self.points[i-1])
##          return edges

#
# Lines
#
class Line(GeometricalObject3D):

    """Line

    A Glossary:Subclass of Class:MMTK.Geometry.GeometricalObject3D.

    Constructor: Line(|point|, |direction|)

    Arguments:

    |point| -- any point on the line (a vector)

    |direction| -- the direction of the line (a vector)
    """

    def __init__(self, point, direction):
	self.point = point
	self.direction = direction.normal()

    def distanceFrom(self, point):
        "Returns the smallest distance of |point| from the line."
	d = self.point-point
	d = d - (d*self.direction)*self.direction
	return d.length()

    def projectionOf(self, point):
        "Returns the orthogonal projection of |point| onto the line."
	d = self.point-point
	d = d - (d*self.direction)*self.direction
	return point+d

    def perpendicularVector(self, plane):
        return self.direction.cross(plane.normal)

    def __repr__(self):
        return 'Line(' + `self.point` + ', ' + `self.direction` + ')'
    __str__ = __repr__

##      def Is_Infinite(self):
##          return 1

##      def asVector(self):
##          return self.point2 - self.point

    def volume(self):
	return 0.

##      def segmentNear(self, other):      # for use by intersection code only
##          pt1 = self.projectionOf(other.point)
##          v = pt1 - other.point
##          if v.length() < min_meaningfull_distance:
##              angle1 = 0
##          else:
##              angle1 = v.angle(other.direction)
##              if abs(angle1 - N.pi/2) < eps_radians:
##                  return None
##          if angle1 > N.pi/2:
##              angle1 = N.pi - angle1
##          d = self.direction * (0.1 + N.tan(angle1) * v.length())
##          return LineSegment(pt1 - d, pt1 + d)


class LineSegment(Line):

    def __init__(self, point1, point2):
        Line.__init__(self, point1, point2 - point1)
        self.point2 = point2

    def __repr__(self):
        return 'LineSegment(' + `self.point` + ', ' + `self.point2` + ')'
    __str__ = __repr__

##      def BisectPoint(self):
##          return (self.point + self.point2)/2

##      def PerpBisector(self, plane):
##          return Line(self.BisectPoint(), self.perpendicularVector(plane))

##      def Is_Infinite(self):
##          return 0

##      def pointNearest(self, point):
##          pt = self.projectionOf(point)
##          if pt is not None:
##              return pt
##          d1 = (self.point - point).length()
##          d2 = (self.point2 - point).length()
##          if d1 < d2:
##              return self.point
##          return self.point2

    def distanceFrom(self, point):
        pt = self.projectionOf(point)
        if pt is not None:
            return (pt - point).length()
        d1 = (self.point - point).length()
        d2 = (self.point2 - point).length()
        return min(d1, d2)

    def projectionOf(self, point):
        d = self.point-point
        d = d - (d*self.direction)*self.direction
        pt = point+d
        if self.isWithin(pt):
            return pt
        return None

    def isWithin(point):
        v1 = point - self.point
        v2 = point - self.point2
        if abs(v1 * v2) < eps:
            return 0
        return not Same_Dir(v1, v2)

##      def asVector(self):
##          return self.point2 - self.point

#
# Intersection calculations
#
def _addIntersectFunction(f, class1, class2):
    switch = class1 > class2
    if switch:
	class1, class2 = class2, class1
    _intersectTable[(class1, class2)] = (f, switch)


#
# a number of routines used by _intersectLineLine
#

##  def LinePointColinear(line, pt):
##      return line.distanceFrom(pt) < eps

##  def Same_Dir(dir1, dir2):
##      # for 2 colinear vectors, FALSE if in opposite dir, else TRUE 
##      return (dir1[0] >= 0) == (dir2[0] >= 0)\
##             and (dir1[1] >= 0) == (dir2[1] >= 0)\
##             and (dir1[2] >= 0) == (dir2[2] >= 0)

##  def Overlap(l1, l2): # expects colinear lines
##      if l1.Is_Infinite(): return l2
##      if l2.Is_Infinite(): return l1
##      if Same_Dir(l1.direction, l2.direction):
##          l0 = l1
##      else:
##          l0 = LineSegment(l1.point2, l1.point)
##      in1 = l0.isWithin(l2.point)
##      if in1:
##          p1 = l2.point
##      else:
##          p1 = l0.point
##      in2 = l0.isWithin(l2.point2)
##      if (not in1) and (not in2):
##          if l2.isWithin(l0.point):
##              return l1
##         # no overlap; do they touch?
##         if (l0.point - l2.point).length() <= eps or\
##            (l0.point - l2.point2).length() <= eps:
##             return l0.point
##         if (l0.point2 - l2.point).length() <= eps or\
##            (l0.point2 - l2.point2).length() <= eps:
##             return l0.point2
##         return None
##      if in2:
##          p2 = l2.point2
##      else:
##          p2 = l0.point2
##      return LineSegment(p1, p2)

##  def _intersectLineLine(l1, l2):
##      if LinePointColinear(l1, l2.point) \
##         and N.sin(l1.direction.angle(l2.direction)) < eps_radians:
##          return Overlap(l1, l2)
##      if l2.Is_Infinite():
##          l2 = l2.segmentNear(l1)
##          if not l2:
##              return l2
##      if l1.Is_Infinite():
##          l1 = l1.segmentNear(l2)
##          if not l1:
##              return l1
##      x11 = l1.point[0]
##      y11 = l1.point[1]
##      x21 = l2.point[0]
##      y21 = l2.point[1]
##      v1 = l1.asVector()
##      x12 = float(v1[0])
##      y12 = float(v1[1])
##      v2 = l2.asVector()
##      x22 = v2[0]
##      y22 = v2[1]
##      num = x12*(y11 - y21) + y12*(x21 - x11);
##      denom = x12*y22 - y12*x22;
##      if abs(denom*1.01) > abs(num):
##          u = num/denom
##      elif abs(num) < eps:       # (?) XY Perpendicular, using XZ projection num
##          z11 = l1.point[2]
##          z21 = l2.point[2]
##          z12 = float(v1[2])
##          z22 = v2[2]
##          num = x12*(z11 - z21) + z12*(x21 - x11)
##          denom = x12*z22 - z12*x22
##          if abs(denom*1.01) > abs(num):
##              u = num/denom
##          elif abs(num) < eps:    # XZ Perpendicular, using YZ projection
##              num = y12*(z11 - z21) + z12*(y21 - y11)
##              denom = y12*z22 - z12*y22
##              if abs(denom*1.01) > abs(num):
##                  u = num/denom
##              else:
##                  u = 1.01
##         else: u = 1.01
##      else: u = 1.01
##      if u < 0 or u > 1:
##          return None
##      z12 = float(v1[2])
##      # set t to parametric distance along l1
##      if abs(y12) >= eps:
##          t = (y21 - y11 + u*y22)/y12
##      elif abs(x12) >= eps:
##          t = (x21 - x11 + u*x22)/x12
##      elif abs(z12) >= eps:
##          t = (l2.point[2] - l1.point[2] + u*v2[2])/z12
##      else: t = 0                # can l1 be a meaningfull line if this happens?
##      #print 'parametric dists %e %e %.2f %.2f %.2f' % (t,u,y12,y21,y11)
##      if not l1.Is_Infinite() and (t < 0 or t > 1):
##          return None
##      pt_from1 = l1.point + t*v1
##      pt_from2 = l2.point + u*v2
##      if (pt_from1 - pt_from2).length() < min_meaningfull_distance:
##          return pt_from1
##      else:
##          return None

##  _addIntersectFunction(_intersectLineLine, Line, Line)
##  _addIntersectFunction(_intersectLineLine, Line, LineSegment)
##  _addIntersectFunction(_intersectLineLine, LineSegment, Line)
##  _addIntersectFunction(_intersectLineLine, LineSegment, LineSegment)

##  def _intersectLinePolygon(line, poly):
##      pt = line.intersectWith(poly.planeOf())
##      if pt is not None and poly.pointNearest(pt, proj_only = 1) is not None:
##          return pt
##      return None

##  _addIntersectFunction(_intersectLinePolygon, LineSegment, Polygon)

##  def _intersectLinePlane(line, plane):
##      v = vectorFromPointToPlane(line.point, plane)
##      if v.length() < eps:
##          return line.point
##      angle = v.angle(line.asVector())
##      if abs(angle - N.pi/2) < eps:
##          return None
##      proj1 = line.point + v
##      proj2 = plane.projectionOf(line.point + line.direction)
##      x = proj1 + N.tan(angle)*(proj2 - proj1)
##      if line.__class__ is LineSegment and not line.isWithin(x):
##          return None
##      return x

##  _addIntersectFunction(_intersectLinePlane, LineSegment, Plane)

# Box with box

def _intersectBoxBox(box1, box2):
    c1 = N.maximum(box1.corners[0], box2.corners[0])
    c2 = N.minimum(box1.corners[1], box2.corners[1])
    if N.logical_or.reduce(N.greater_equal(c1, c2)):
        return None
    return Box(Vector(c1), Vector(c2))

_addIntersectFunction(_intersectBoxBox, Box, Box)

# Sphere with sphere

def _intersectSphereSphere(sphere1, sphere2):
    r1r2 = sphere2.center-sphere1.center
    d = r1r2.length()
    if d > sphere1.radius+sphere2.radius:
	return None
    if d+min(sphere1.radius, sphere2.radius) < \
                             max(sphere1.radius, sphere2.radius):
	return None
    x = 0.5*(d**2 + sphere1.radius**2 - sphere2.radius**2)/d
    h = N.sqrt(sphere1.radius**2-x**2)
    normal = r1r2.normal()
    return Circle(sphere1.center + x*normal, normal, h)

_addIntersectFunction(_intersectSphereSphere, Sphere, Sphere)

# Sphere with cone

def _intersectSphereCone(sphere, cone):
    if sphere.center != cone.center:
	raise GeomError("Not yet implemented")
    from_center = sphere.radius*N.cos(cone.angle)
    radius = sphere.radius*N.sin(cone.angle)
    return Circle(cone.center+from_center*cone.axis, cone.axis, radius)

_addIntersectFunction(_intersectSphereCone, Sphere, Cone)

#
# Sphere - Line intersection returns None or tuple of 2 points. The  
# 2 points can be identical.
#
##  def _intersectSphereLine(sphere, line):
##      r = sphere.radius
##      dist = line.distanceFrom(sphere.center)
##      if dist > r:
##          return None
##      projection = line.projectionOf(sphere.center)
##      drop_normal = projection - sphere.center
##      if drop_normal.length() < 1.e-9*r: # line goes through center
##          return (sphere.center + r*line.direction,\
##                  sphere.center - r*line.direction)
##      scale = N.sqrt(r*r - drop_normal.length()*drop_normal.length())
##      normal2 = scale*line.direction
##      return (sphere.center + (projection + normal2),
##              sphere.center + (projection - normal2))


##  _addIntersectFunction(_intersectSphereLine, Sphere, Line)

##  # Circle with Circle

##  def vectorsAreParallel(v1,v2):
##      return v1.cross(v2).length() < eps

##  def Circle_Intersect_2point(c1,c2,d):
##      # must have c1.radius >= c2.Radius; must have d > 0
##      dr2 = (c1.radius - c2.radius)*(c1.radius + c2.radius) # r1*r1-r2*r2
##      d1 = dr2/(2*d) + d/2
##      v = (c2.center-c1.center)  # direction from center to c2
##      v1 = (d1/d)*v
##      # p is projection of intersections onto line connecting centers
##      # Point p(c1.center + v)
##      scale = N.sqrt((c1.radius-d1)*(c1.radius+d1))
##      v2 = v.cross(c1.normal).normal()
##      return (c1.center + (v1 + scale*v2), c1.center + (v1 - scale*v2))

##  def Circle_Intersect_Noncoplanar(c1, c2):
##      plane1 = c1.planeOf()
##      plane2 = c2.planeOf()
##      intersect_line = plane1.intersectWith(plane2)
##      if intersect_line is None:
##          return None
##      assert(intersect_line.__class__ is Line)
##      proj1 = intersect_line.projectionOf(c1.center)
##      dist_proj1 = (proj1 - c1.center).length()
##      scale = N.sqrt(c1.radius*c1.radius - dist_proj1*dist_proj1)
##      pt1 = proj1 + scale * intersect_line.direction
##      pt2 = proj1 - scale * intersect_line.direction
##      intersect_pt1 = abs((pt1 - c2.center).length() - c2.radius) \
##                      < min_meaningfull_distance
##      intersect_pt2 = abs((pt2 - c2.center).length() - c2.radius) \
##                      < min_meaningfull_distance
##      if intersect_pt1 and intersect_pt2:
##          return (pt1, pt2)
##      if intersect_pt1:
##          return pt1
##      if intersect_pt2:
##          return pt2
##      return None

##  def _intersectCircleCircle(c1, c2):
##      if not vectorsAreParallel(c1.normal,c2.normal):
##          return Circle_Intersect_Noncoplanar(c1, c2)
##      d = (c1.center - c2.center).length()
##      r2 = c1.radius+c2.radius
##      r0 = abs(c1.radius-c2.radius)
##      if d/c1.radius < eps and d/c2.radius < eps:
##          if r0 <= d:
##              return c1 # same circles
##          return None
##      if d < r0:
##          return None      # 1 circle entirely inside other
##      if abs(r2/d - 1) < eps:    # single point intersection
##          pt = c1.center + c1.radius/d*(c2.center - c1.center);
##          return (pt,pt)
##      if r2 < d:
##          return None
##      # if get to this point then should intersect at 2 points
##      if c1.radius > c2.radius:
##          return Circle_Intersect_2point(c1,c2,d)
##      else:
##          return Circle_Intersect_2point(c2,c1,d)

##  _addIntersectFunction(_intersectCircleCircle, Circle, Circle)

##  def vectorFromPointToPlane(point, plane):
##      d = (plane.normal*plane.distance_from_zero - point) * plane.normal
##      return d * plane.normal

##  def distanceFromPointToPlane(point, plane):
##      return vectorFromPointToPlane(point,plane).length()

##  def _intersectSphereCircle(sphere, circle):
##      vector_to_circle = vectorFromPointToPlane(sphere.center, circle.planeOf())
##      projection = sphere.center + vector_to_circle
##      d2 = vector_to_circle.length()
##      if sphere.radius < d2 + eps:
##          if abs(sphere.radius - d2) <= eps:
##              return projection
##          return None
##      radius2 = N.sqrt(sphere.radius*sphere.radius - d2*d2)
##      circle2 = Circle(projection, circle.normal, radius2)
##      return _intersectCircleCircle(circle, circle2)

##  _addIntersectFunction(_intersectSphereCircle, Sphere, Circle)

##  def arbitraryNormal(v):
##      if abs(v[0]) < eps:
##          return v.cross(Vector(1,0,0))
##      if abs(v[1]) < eps:
##          return v.cross(Vector(0,1,0))
##      return v.cross(Vector(0,0,1))

# Plane with plane

def _intersectPlanePlane(plane1, plane2):
    if abs(abs(plane1.normal*plane2.normal)-1.) < eps:
	if abs(plane1.distance_from_zero-plane2.distance_from_zero) < eps:
	    return plane1
	else:
            return None
    else:
	direction = plane1.normal.cross(plane2.normal)
	point_in_1 = plane1.distance_from_zero*plane1.normal
	point_in_both = point_in_1 - (point_in_1*plane2.normal -
				      plane2.distance_from_zero)*plane2.normal
	return Line(point_in_both, direction)

_addIntersectFunction(_intersectPlanePlane, Plane, Plane)

# Circle with plane

def _intersectCirclePlane(circle, plane):
    if abs(abs(circle.normal*plane.normal)-1.) < eps:
	if plane.hasPoint(circle.center):
	    return circle
	else:
	    return None
    else:
	line = plane.intersectWith(Plane(circle.center, circle.normal))
	x = line.distanceFrom(circle.center)
	if x > circle.radius:
	    return None
	else:
	    angle = N.arccos(x/circle.radius)
	    along_line = N.sin(angle)*circle.radius
	    normal = circle.normal.cross(line.direction)
	    if line.distanceFrom(circle.center+normal) > x:
		normal = -normal
	    return (circle.center+x*normal-along_line*line.direction,
		    circle.center+x*normal+along_line*line.direction)
	    
_addIntersectFunction(_intersectCirclePlane, Circle, Plane)

# Cone with Cone - special purpose routine, returns 0 to 2 vectors

##  def _intersectConeCone(cone1, cone2):
##      if (cone1.center - cone2.center).length() > eps:
##          raise GeomError("Not yet implemented")
##      if cone1.angle + cone2.angle < cone1.axis.angle(cone2.axis):
##          return None
##                 # intersection is a line?
##      if abs(cone1.angle + cone2.angle - cone1.axis.angle(cone2.axis)) <= eps:
##          normal = Line(cone.center,cone1.axis.cross(cone2.axis))
##          return rotateDirection(cone1.axis,normal, cone1.angle)
##      if abs(cone1.angle - N.pi/2) <= eps:
##          if abs(cone2.angle - N.pi/2) <= eps:
##              return _intersectPlanePlane(Plane(cone1.center, cone1.axis),
##                                          Plane(cone2.center, cone2.axis))
##          return _intersectConeCone(cone2, cone1)
##      cos1 = N.cos(cone1.angle)
##      radius1 = cos1*N.tan(cone1.angle)
##      circle = Circle(cone1.center + cos1*cone1.axis, cone1.axis, radius1)
##      plane = Plane(cone2.center + N.cos(cone2.angle)*cone2.axis,
##                    cone2.axis)
##      result = _intersectCirclePlane(circle, plane)
##      if type(result) is type(()) and len(result) == 2:
##          r = (result[0] - cone1.center, result[1] - cone1.center)
##          if r[0].angle(r[1]) < eps_radians:
##              return Line(cone1.center, r[0])
##          return r
##      return result

#
# Rotation
#
def rotateDirection(vector, axis, angle):
    s = N.sin(angle)
    c = N.cos(angle)
    c1 = 1-c
    try:
        axis = axis.direction
    except AttributeError:
        pass
    return s*axis.cross(vector) + c1*(axis*vector)*axis + c*vector

def rotatePoint(point, axis, angle):
    return axis.point + rotateDirection(point-axis.point, axis, angle)

##  #
##  # Find the angle by which one would have to rotate vector v1 about axis
##  # so that when projected on to the plane to which axis is normal, it
##  # would be colinear to v2. Mainly for comparing two bonds that you are
##  # trying to position about the same atom.
##  #
##  def findRotationAngle(axis, v1, v2):
##      plane1 = Plane(Vector(0,0,0), axis)
##      p1 = plane1.projectionOf(v1)
##      p2 = plane1.projectionOf(v2)
##      angle = p1.angle(p2)
##      if p1.cross(p2)*axis < 0:
##          angle = -angle
##      return angle

##  #
##  # find difference between 2 directions. With default, result is -180 to +180
##  # degrees. Use modulo = pi to produce a -90 to +90 range for undirected lines.
##  #
##  def angleBetweenDirections(angle1, angle2, modulo = 2*N.pi):
##      r = angle1 - angle2
##      while r > modulo/2: r = r - modulo
##      while r < -modulo/2: r = r + modulo
##      return r

#
# Lattices
#

#
# Lattice base class
#
class Lattice:

    """General lattice

    Lattices are special sequence objects that contain vectors
    (points on the lattice) or objects that are constructed as
    functions of these vectors. Lattice objects behave like
    lists, i.e. they permit indexing, length inquiry, and iteration
    by 'for'-loops. See also the example Example:Miscellaneous:lattice.py.

    This is an Glossary:abstract-base-class. To create lattice objects,
    use one of its subclasses.
    """

    def __init__(self, function):
	if function is not None:
	    self.elements = map(function, self.elements)

    def __getitem__(self, item):
	return self.elements[item]

    def __setitem__(self, item, value):
	self.elements[item] = value

    def __len__(self):
	return len(self.elements)

#
# General rhombic lattice
#
class RhombicLattice(Lattice):

    """Rhombic lattice

    A Glossary:Subclass of Class:MMTK.Geometry.Lattice.

    Constructor: RhombicLattice(|elementary_cell|, |lattice_vectors|,
                                |cells|, |function|='None')

    Arguments:

    |elementary_cell| -- a list of points (vectors) in the elementary cell

    |lattice_vectors| -- a list of lattice vectors. Each lattice
                         vector defines a lattice dimension (only values
                         from one to three make sense) and indicates the
                         displacement along this dimension from one
                         cell to the next.

    |cells| -- a list of integers, whose length must equal the number
               of dimensions. Each entry specifies how often a cell is
               repeated along this dimension.

    |function| -- a function that is called for every lattice point with
                  the vector describing the point as argument. The return
                  value of this function is stored in the lattice object.
                  If the function is 'None', the vector is directly stored
                  in the lattice object.

    The number of objects in the lattice is equal to the product of the
    values in |cells| times the number of points in |elementary_cell|.
    """

    def __init__(self, elementary_cell, lattice_vectors, cells,
                 function=None, base=None):
	if len(lattice_vectors) != len(cells):
	    raise TypeError('Inconsistent dimension specification')
        if base is None:
            base = Vector(0, 0, 0)
	self.dimension = len(lattice_vectors)
	self.elements = []
	self.makeLattice(elementary_cell, lattice_vectors, cells, base)
	Lattice.__init__(self, function)

    def makeLattice(self, elementary_cell, lattice_vectors, cells, base):
	if len(cells) == 0:
	    for p in elementary_cell:
		self.elements.append(p+base)
	else:
	    for i in range(cells[0]):
		self.makeLattice(elementary_cell, lattice_vectors[1:],
				 cells[1:], base+i*lattice_vectors[0])
	    
#
# Bravais lattice
#
class BravaisLattice(RhombicLattice):

    """Bravais lattice

    A Glossary:Subclass of Class:MMTK.Geometry.Lattice.

    A Bravais lattice is a special case of a general rhombic lattice
    in which the elementary cell contains only one point.

    Constructor: BravaisLattice(|lattice_vectors|,
                                |cells|, |function|='None')

    Arguments:

    |lattice_vectors| -- a list of lattice vectors. Each lattice
                         vector defines a lattice dimension (only values
                         from one to three make sense) and indicates the
                         displacement along this dimension from one
                         cell to the next.

    |cells| -- a list of integers, whose length must equal the number
               of dimensions. Each entry specifies how often a cell is
               repeated along this dimension.

    |function| -- a function that is called for every lattice point with
                  the vector describing the point as argument. The return
                  value of this function is stored in the lattice object.
                  If the function is 'None', the vector is directly stored
                  in the lattice object.

    The number of objects in the lattice is equal to the product of the
    values in |cells|.
    """

    def __init__(self, lattice_vectors, cells, function=None, base=None):
	cell = [Vector(0,0,0)]
	RhombicLattice.__init__(self, cell, lattice_vectors, cells,
                                function, base)

#
# Simple cubic lattice
#
class SCLattice(BravaisLattice):

    """Simple Cubic lattice

    A Glossary:Subclass of Class:MMTK.Geometry.Lattice.

    A Simple Cubic lattice is a special case of a Bravais lattice
    in which the elementary cell is a cube.

    Constructor: SCLattice(|cell_size|, |cells|, |function|='None')

    Arguments:

    |cell_size| -- the edge length of the elementary cell

    |cells| -- a list of integers, whose length must equal the number
               of dimensions. Each entry specifies how often a cell is
               repeated along this dimension.

    |function| -- a function that is called for every lattice point with
                  the vector describing the point as argument. The return
                  value of this function is stored in the lattice object.
                  If the function is 'None', the vector is directly stored
                  in the lattice object.

    The number of objects in the lattice is equal to the product of the
    values in |cells|.
    """

    def __init__(self, cellsize, cells, function=None, base=None):
	lattice_vectors = (cellsize*Vector(1., 0., 0.),
                           cellsize*Vector(0., 1., 0.),
                           cellsize*Vector(0., 0., 1.))
	if type(cells) != type(()):
	    cells = 3*(cells,)
	BravaisLattice.__init__(self, lattice_vectors, cells, function, base)

#
# Body-centered cubic lattice
#
class BCCLattice(RhombicLattice):

    """Body-Centered Cubic lattice

    A Glossary:Subclass of Class:MMTK.Geometry.Lattice.

    A Body-Centered Cubic lattice has two points per elementary cell.

    Constructor: BCCLattice(|cell_size|, |cells|, |function|='None')

    Arguments:

    |cell_size| -- the edge length of the elementary cell

    |cells| -- a list of integers, whose length must equal the number
               of dimensions. Each entry specifies how often a cell is
               repeated along this dimension.

    |function| -- a function that is called for every lattice point with
                  the vector describing the point as argument. The return
                  value of this function is stored in the lattice object.
                  If the function is 'None', the vector is directly stored
                  in the lattice object.

    The number of objects in the lattice is equal to the product of the
    values in |cells|.
    """

    def __init__(self, cellsize, cells, function=None, base=None):
        cell = [Vector(0,0,0), cellsize*Vector(0.5,0.5,0.5)]
	lattice_vectors = (cellsize*Vector(1., 0., 0.),
                           cellsize*Vector(0., 1., 0.),
                           cellsize*Vector(0., 0., 1.))
	if type(cells) != type(()):
	    cells = 3*(cells,)
	RhombicLattice.__init__(self, cell, lattice_vectors, cells,
                                function, base)

#
# Face-centered cubic lattice
#
class FCCLattice(RhombicLattice):

    """Face-Centered Cubic lattice

    A Glossary:Subclass of Class:MMTK.Geometry.Lattice.

    A Face-Centered Cubic lattice has four points per elementary cell.

    Constructor: FCCLattice(|cell_size|, |cells|, |function|='None')

    Arguments:

    |cell_size| -- the edge length of the elementary cell

    |cells| -- a list of integers, whose length must equal the number
               of dimensions. Each entry specifies how often a cell is
               repeated along this dimension.

    |function| -- a function that is called for every lattice point with
                  the vector describing the point as argument. The return
                  value of this function is stored in the lattice object.
                  If the function is 'None', the vector is directly stored
                  in the lattice object.

    The number of objects in the lattice is equal to the product of the
    values in |cells|.
    """

    def __init__(self, cellsize, cells, function=None, base=None):
        cell = [Vector(0,0,0),
                cellsize*Vector(  0,0.5,0.5),
                cellsize*Vector(0.5,  0,0.5),
                cellsize*Vector(0.5,0.5,  0)]
	lattice_vectors = (cellsize*Vector(1., 0., 0.),
                           cellsize*Vector(0., 1., 0.),
                           cellsize*Vector(0., 0., 1.))
	if type(cells) != type(()):
	    cells = 3*(cells,)
	RhombicLattice.__init__(self, cell, lattice_vectors, cells,
                                function, base)
