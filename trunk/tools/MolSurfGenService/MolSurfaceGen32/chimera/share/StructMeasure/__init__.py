# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 28114 2009-07-15 23:12:35Z pett $

"""Interface to structure measurements (e.g. distances, angles)"""

def axis(coords, findBounds=False, findRadius=False, iterate=True,
								weights=None):
	"""Compute an axis given an Nx3 Numpy array.

	   Returns a Point (centroid) and a Vector (unit direction vector).
	   If 'findBounds' is True, returns two additional floating point
	   values -- the scaling factors for the vector to reach the
	   approximate bounds of the axis defined by the array values.
	   If 'findRadius' is True, returns yet another floating-point
	   value: the average coord-axis distance.
	   'weights' is a numpy array used to weight the 'coords'; typicaly used
	   for mass weighting.

	   Tip: you generally generate the input Numpy array with 
	   numpyArrayFromAtoms()
	"""

	if weights != None and iterate:
		raise ValueError("'iterate' does not consider 'weights'")
	import numpy
	from chimera import Point, Vector
	def reshapeTo(source, target):
		scalings = numpy.repeat(source, 3)
		scalings.shape = len(target), 3
		return scalings
	pt, longVec, centroid, normLineVec, centered, vals, vecs = bestLine(
						coords, weights=weights)

	# for short helices, best axis not necessarily longest
	normLineVec = vecs[numpy.argmin([axisEval(v, centered) for v in vecs])]
	vec = Vector(*normLineVec)

	best = None
	while iterate:
		# nearest point on line
		ts = numpy.tensordot(normLineVec, centered, (0, 1)) \
					/ numpy.dot(normLineVec, normLineVec)
		linePts = numpy.outer(ts, normLineVec)

		# distance
		temp = (centered - linePts)
		dists = numpy.sqrt((temp * temp).sum(-1))
		avgDist = dists.mean(0)
		diffs = dists - avgDist
		val = (diffs * diffs).sum()
		if best == None or val < best:
			best = val
			oldPt = pt
			oldVec = vec
			oldCentered = centered
			oldLineVec = normLineVec
		else:
			pt = oldPt
			vec = oldVec
			centered = oldCentered
			normLineVec = oldLineVec
			break

		# find the point that is 1/3 from the current distance to
		# the average distance and correct line and centroid based
		# on that point
		nonzero = dists > 0.0001
		if not len(nonzero):
			break
		nzCentered = centered.compress(nonzero, 0)
		nzLinePts = linePts.compress(nonzero, 0)
		nzDists = dists.compress(nonzero, 0)
		correctionTargets = linePts + (nzCentered - linePts) * reshapeTo((2 + avgDist / nzDists) / 3.0, nzCentered)

		# centroid motion
		#centroid += (correctionTargets - nzLinePts).mean(0)

		# vector correction
		corrVecs = correctionTargets
		dots = (corrVecs * normLineVec).sum(1)
		corrVecs[dots<0] *= -1
		normLineVec = corrVecs.mean(0)
		normLineVec /= numpy.sqrt((normLineVec * normLineVec).sum())
		centered = coords - centroid
		pt = Point(*centroid)
		vec = Vector(*normLineVec)
	retVals = (pt, vec)
	if findBounds:
		dotted = numpy.dot(centered, normLineVec)
		retVals += (dotted.min(), dotted.max())
	if findRadius:
		dists = axisDists(normLineVec, centered)
		retVals += (dists.mean(0),)
	return retVals

def plane(coords, findBounds=False):
	"""Compute a plane given an Nx3 Numpy array.

	   Returns a Plane whose origin is the centroid of the coords.
	   If 'findBounds' is True, returns an additional Point (the
	   furthest point projected into plane) and an additional
	   floating-point number (distance from origin to that point).
	   
	   Tip: you generally generate the input Numpy array with 
	   numpyArrayFromAtoms()
	"""
	import numpy
	from numpy.linalg import eig, svd, eigh
	centroid = coords.mean(0)
	centered = coords - centroid
	ignore, vals, vecs = svd(centered)
	normal = vecs[numpy.argmin(vals)]
	from chimera import Point, Plane, Vector
	origin = Point(*centroid)
	plane = Plane(origin, Vector(*normal))
	if findBounds:
		maxSqDist = None
		for coord in coords:
			projected = plane.nearest(Point(*coord))
			sqDist = origin.sqdistance(projected)
			if maxSqDist == None or sqDist > maxSqDist:
				maxSqDist = sqDist
				furthest = projected
		from math import sqrt
		return plane, projected, sqrt(maxSqDist)
	return plane

def axisEval(v, centered):
	dists = axisDists(v, centered)
	avgDist = dists.mean(0)
	diffs = dists - avgDist
	return (diffs * diffs).sum()

def axisDists(v, centered):
	import numpy
	ts = numpy.tensordot(v, centered, (0, 1)) / numpy.dot(v, v)
	linePts = numpy.outer(ts, v)

	# distance
	temp = (centered - linePts)
	return numpy.sqrt((temp * temp).sum(-1))

def bestLine(coords, weights=None):
	import numpy
	from numpy.linalg import eig, svd, eigh
	if weights != None:
		n = len(coords)
		matWeights = weights.reshape((n,1))
		wcoords = matWeights * coords
		wsum = weights.sum()
		centroid = wcoords.sum(0) / wsum
		centered = coords - centroid
		# Tom Goddard's method too subtle for me!
		#v33 = numpy.dot(coords.transpose(), wcoords) / wsum \
		#			- numpy.outer(centroid, centroid)
		#vals, vecs = eigh(v33)
		ignore, vals, vecs = svd(matWeights * centered)
	else:
		centroid = coords.mean(0)
		centered = coords - centroid
		ignore, vals, vecs = svd(centered)
	normLineVec = vecs[numpy.argmax(vals)]

	from chimera import Point, Vector
	return Point(*centroid), Vector(*normLineVec), centroid, normLineVec, \
							centered, vals, vecs

def matchStructureColor(atoms):
	# try to use ribbon color if appropriate
	displayedRgbas = []
	undisplayedRgbas = []
	for a in atoms:
		if a.hide:
			# ribbon showing
			r = a.residue
			if r.ribbonDisplay:
				if r.ribbonColor:
					rgba = r.ribbonColor.rgba()
				else:
					rgba = r.molecule.color.rgba()
			else:
				rgba = r.molecule.color.rgba()
		else:
			if a.color:
				rgba = a.color.rgba()
			else:
				rgba = a.molecule.color.rgba()
		if (a.hide and r.ribbonDisplay) or a.display:
			displayedRgbas.append(rgba)
		else:
			undisplayedRgbas.append(rgba)
	if displayedRgbas:
		rgbas = displayedRgbas
	else:
		rgbas = undisplayedRgbas
	import numpy
	avgRgba = numpy.mean(numpy.array(rgbas), 0)
	import chimera
	return chimera.MaterialColor(*tuple(avgRgba))

if __name__ == "chimeraOpenSandbox":
	import numpy
	testData = [
		[0, 1, 0], [1, 0, -1], [2, -1, 0], [3, 0,  1],
		[4, 1, 0], [5, 0, -1], [6, -1, 0], [7, 0,  1]
	]
	axis(numpy.array(testData))
