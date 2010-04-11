# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: bondGeom.py 26655 2009-01-07 22:02:30Z gregc $

"""Bond geometry utilities"""

from chimera import distance, cross, Atom
from chimera import Point, Vector, Plane, Xform
from math import pi, sin, cos

tetrahedral = Atom.Tetrahedral #sp3
planar = Atom.Planar #sp2
linear = Atom.Linear #sp
single = Atom.Single #s
ion = Atom.Ion

geometryName = ['ion', 'single', 'linear', 'trigonal', 'tetrahedral']

sin5475 = sin(pi * 54.75 / 180.0)
cos5475 = cos(pi * 54.75 / 180.0)
cos705 = cos(pi * 70.5 / 180.0)

def bondPositions(bondee, geom, bondLen, bonded, coPlanar=None,
			toward=None, away=None, toward2=None, away2=None):
	"""Return a list of possible bond partner positions for 'bondee' that
	   satisfy geometry 'geom' and are of length 'bondLen'.  'bonded' are
	   positions of already-bonded substituents to 'bondee'.

	   'bondee' is a Point and 'bonded' is a list of Points.  The return
	   value is a list of Points.

	   For planar geometries, 'coPlanar' can be a list of one or two
	   points that the bond positions should be coplanar with.

	   For rotamers, if 'toward' is specified then one bond position of
	   the rotamer will be as close as possible to the 'toward' point.
	   Conversely, if 'away' is specified, then all bond positions will
	   be as far as possible from the 'away' point.  'toward' has
	   precedence over 'away'.  If this doesn't completely determine
	   the bond positions (i.e. no initial bonded substituents), then
	   'toward2' and 'away2' will be considered in a similar manner to
	   determine the remaining positions.
	"""

	if toward and away or toward2 and away2:
		raise ValueError, "Cannot specify both toward and away," \
					" or both toward2 and away2"
	if geom == single:
		if len(bonded) > 0:
			return []
		return [singlePos(bondee, bondLen, toward, away)]
	
	if geom == linear:
		if len(bonded) > 1:
			return []
		return linearPos(bondee, bonded, bondLen, toward, away)
	
	if geom == planar:
		if len(bonded) > 2:
			return []
		return planarPos(bondee, bonded, bondLen, coPlanar,
						toward, away, toward2, away2)
	
	if geom == tetrahedral:
		if len(bonded) > 3:
			return []
		return tetraPos(bondee, bonded, bondLen,
						toward, away, toward2, away2)

	raise ValueError, "Unknown geometry type '%s'" % geom
		

def singlePos(bondee, bondLen, toward=None, away=None):
	if toward:
		v = toward - bondee
		v.normalize()
		return bondee + v * bondLen
	elif away:
		v = bondee - away
		v.normalize()
		return bondee + v * bondLen
	return Point(bondee.x + bondLen, bondee.y, bondee.z)

def linearPos(bondee, bonded, bondLen, toward=None, away=None):
	newBonded = []
	curBonded = bonded[:]
	if len(bonded) == 0:
		if away:
			# need 90 angle, rather than directly away
			# (since otherwise second added position will then be
			# directly towards)
			ninety = rightAngle(away - bondee)
			away = bondee + ninety
		pos = singlePos(bondee, bondLen, toward, away)
		newBonded.append(pos)
		curBonded.append(pos)
	
	if len(curBonded) == 1:
		bondedDist = distance(bondee, curBonded[0])
		bondVec = bondee - curBonded[0]
		bondVec.length = bondLen
		newBonded.append(bondee + bondVec)
	return newBonded

def planarPos(bondee, bonded, bondLen, coPlanar=None, toward=None, away=None,
						toward2=None, away2=None):
	newBonded = []
	curBonded = bonded[:]
	if len(curBonded) == 0:
		pos = singlePos(bondee, bondLen, toward, away)
		toward = away = None
		newBonded.append(pos)
		curBonded.append(pos)
	
	if len(curBonded) == 1:
		# add at 120 degree angle, co-planar if required
		if not coPlanar:
			if toward or toward2:
				coPlanar = [toward or toward2]
			elif away or away2:
				ninety = rightAngle((away or away2) - bondee)
				coPlanar = [bondee + ninety]
		pos = anglePos(bondee, curBonded[0], bondLen, 120.0, coPlanar)
		newBonded.append(pos)
		curBonded.append(pos)
	
	if len(curBonded) == 2:
		# position along anti-bisector of current bonds
		v1 = curBonded[0] - bondee
		v2 = curBonded[1] - bondee
		v1.normalize()
		v2.normalize()
		antiBi = v1 + v2
		antiBi.negate()
		antiBi.length = bondLen
		newBonded.append(bondee + antiBi)
	return newBonded

def tetraPos(bondee, bonded, bondLen, toward=None, away=None,
						toward2=None, away2=None):
	newBonded = []
	curBonded = bonded[:]
	if len(curBonded) == 0:
		pos = singlePos(bondee, bondLen, toward, away)
		toward = toward2
		away = away2
		newBonded.append(pos)
		curBonded.append(pos)
	
	if len(curBonded) == 1:
		# add at 109.5 degree angle
		coplanar = toward or away
		if coplanar:
			coplanar = [coplanar]
		else:
			coplanar = None
		pos = anglePos(bondee, curBonded[0], bondLen, 109.5,
							coplanar=coplanar)
		if toward or away:
			# find the other 109.5 position in the toward/away
			# plane and the closer/farther position as appropriate
			old = bondee - curBonded[0]
			old.normalize()
			new = pos - bondee
			midpoint = bondee + old * new.length * cos705
			otherPos = pos + (midpoint - pos) * 2
			d1 = (pos - (toward or away)).sqlength()
			d2 = (otherPos - (toward or away)).sqlength()
			if toward:
				if d2 < d1:
					pos = otherPos
			elif away and d2 > d1:
				pos = otherPos

		newBonded.append(pos)
		curBonded.append(pos)
	
	if len(curBonded) == 2:
		# add along anti-bisector of current bonds and raised up
		# 54.75 degrees from plane of those bonds (half of 109.5)
		v1 = curBonded[0] - bondee
		v2 = curBonded[1] - bondee
		v1.normalize()
		v2.normalize()
		antiBi = v1 + v2
		antiBi.negate()
		antiBi.normalize()
		# in order to stabilize the third and fourth tetrahedral
		# positions, cross the longer vector by the shorter
		if v1.sqlength() > v2.sqlength():
			crossV = cross(v1, v2)
		else:
			crossV = cross(v2, v1)
		crossV.normalize()

		antiBi = antiBi * cos5475 * bondLen
		crossV = crossV * sin5475 * bondLen

		pos = bondee + antiBi + crossV
		if toward or away:
			otherPos = bondee + antiBi - crossV
			d1 = (pos - (toward or away)).sqlength()
			d2 = (otherPos - (toward or away)).sqlength()
			if toward:
				if d2 < d1:
					pos = otherPos
			elif away and d2 > d1:
				pos = otherPos
		newBonded.append(pos)
		curBonded.append(pos)
	
	if len(curBonded) == 3:
		unitized = []
		for cb in curBonded:
			v = cb - bondee
			v.normalize()
			unitized.append(bondee + v)
		pl = Plane(unitized)
		norm = pl.normal
		# if normal on other side of plane from bondee, we need to
		# invert the normal;  the (signed) distance from bondee
		# to the plane indicates if it is on the same side
		# (positive == same side)
		d = pl.distance(bondee)
		if d < 0.0:
			norm.negate()
		newBonded.append(bondee + norm * bondLen)
	return newBonded

		
def anglePos(atomPos, bondPos, bondLength, degrees, coplanar=None):
	if coplanar:
		# may have one or two coplanar positions specified,
		# if two, compute both resultant positions and average
		# (the up vector has to be negated for the second one)
		xforms = []
		if len(coplanar) > 2:
			raise ValueError, \
				"More than 2 coplanar positions specified!"
		for cpos in coplanar:
			up = cpos - atomPos
			if xforms:
				up.negate()
			xform = Xform.lookAt(atomPos, bondPos, up)
			# lookAt puts ref point opposite that of zAlign, so 
			# rotate 180 degrees around y axis
			xform.premultiply(Xform.yRotation(180))
			xforms.append(xform)

	else:
		xforms = [Xform.zAlign(atomPos, bondPos)]
	points = []
	for xform in xforms:
		radians = pi * degrees / 180.0
		angle = Point(0.0, bondLength * sin(radians),
						bondLength * cos(radians))
		xform.invert()
		points.append(xform.apply(angle))
	
	if len(points) > 1:
		midpoint = points[0] + (points[1] - points[0]) / 2.0
		v = midpoint - atomPos
		v.length = bondLength
		return atomPos + v

	return points[0]

def rightAngle(orig):
	if orig[0] == 0.0:
		return Vector(0.0, 0 - orig[2], orig[1])
	return Vector(0.0 - orig[1], orig[0], 0.0)
