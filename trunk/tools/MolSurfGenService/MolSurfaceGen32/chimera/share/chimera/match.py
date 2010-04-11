#!/usr/local/bin/python
# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: match.py 26655 2009-01-07 22:02:30Z gregc $

import sys
import math
import numpy
from numpy import linalg

import chimera

#
# Computes rotation and translation to align one set of atoms with another.
# The sum of the squares of the distances between corresponding atoms is
# minimized.  Returns Chimera Xform and rms value.
#
def matchAtoms(fixedAtoms, movableAtoms, fCoordSet=None, mCoordSet=None):
	mArray = chimera.numpyArrayFromAtoms(movableAtoms, mCoordSet)
	fArray = chimera.numpyArrayFromAtoms(fixedAtoms, fCoordSet)
	return matchPositions(fArray, mArray)

def _coordArray(aList, coordSet=None):
	if coordSet:
		return numpy.array([a.coord(coordSet).data() for a in aList])
	return numpy.array([a.coord().data() for a in aList])

#
# Computes rotation and translation to align one set of positions with another.
# The sum of the squares of the distances between corresponding positions is
# minimized.  The xyz positions are specified as n by 3 numpy arrays.
# Returns Chimera Xform and rms value.
#
def matchPositions(fixedPositions, movablePositions):
	m = Match(fixedPositions, movablePositions)
	mat = m.matrix()
	rot = chimera.Xform.xform(mat[0, 0], mat[0, 1], mat[0, 2], 0,
				  mat[1, 0], mat[1, 1], mat[1, 2], 0,
				  mat[2, 0], mat[2, 1], mat[2, 2], 0, True)
	fC = m.center(fixedPositions)
	fT = chimera.Xform.translation(chimera.Vector(fC[0], fC[1], fC[2]))
	mC = m.center(movablePositions)
	mT = chimera.Xform.translation(chimera.Vector(-mC[0], -mC[1], -mC[2]))
	xform = chimera.Xform()
	xform.multiply(fT)
	xform.multiply(rot)
	xform.multiply(mT)
	return xform, m.rms

#
# XXX: This does not need to be a class.  A function which does it
# will be best.   It does need a class for the transformation
#
class Match:
	def __init__(self, fixed, movable, wantRMS=1):
		self.fixedCenter = self.center(fixed)
		self.movableCenter = self.center(movable)
		Sj = numpy.subtract(fixed, self.fixedCenter)
		Si = numpy.subtract(movable, self.movableCenter)
		M = chimera.RMSD_fillMatrix(eigenMatrix(), Si, Sj)
		MT = M.transpose()
		trM = eigenMatrix((0.0, 0.0, 0.0, M.trace()))
		P = M + MT - 2 * trM
		P[3, 0] = P[0, 3] = M[1, 2] - M[2, 1]
		P[3, 1] = P[1, 3] = M[2, 0] - M[0, 2]
		P[3, 2] = P[2, 3] = M[0, 1] - M[1, 0]
		P[3, 3] = 0.0

		"""
		Find the eigenvalues and eigenvectors
		"""
		evals, evecs = linalg.eig(P)
		evecs = evecs.transpose()	# numpy returns columns
		largest_ev = evecs[evals.argmax()]
		self.eigenMatrix = eigenMatrix(largest_ev)

		if wantRMS:
			#
			# Compute RMS
			#
			result = numpy.inner(Si, self.matrix())
			d = numpy.subtract(result, Sj)
			dsq = numpy.multiply(d, d)		# square errors
			add_elements = numpy.add.reduce
			sum = add_elements(add_elements(dsq))	# sum of sqs
			self.rms = math.sqrt(sum / len(Si))

	def center(self, v):
		avg = numpy.add.reduce(v) / len(v)
		return avg

	def quaternion(self):
		return self.eigenMatrix[:,3]

	def matrix(self):
		return chimera.RMSD_matrix(*self.quaternion())

	def printCoords(self, v):
		for i in range(len(v)):
			print '\t', v[i]


#
# Return the matrix form of an eigenvector, q.  If q,
# is not specified, return a zero matrix
#
def eigenMatrix(q=None):
	if q is not None:
		return chimera.eigenMatrix(*q)

	return numpy.zeros((4, 4), numpy.float)

if __name__ == '__main__':
	from rawdata import fixed, movable
	m = Match(fixed, movable)
	q = m.quaternion()
	print 'quaternion =', q
	print 'length =', math.sqrt(numpy.dot(q, q))
	print 'angle =', math.acos(q[3]) * 2 / math.pi * 180
	print 'rms =', m.rms
	print 'matrix:'
	print m.matrix()
