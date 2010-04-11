# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import numpy
from numpy import linalg
import math
import operator

import chimera
from CGLutil import vrml

#
# initialize and deinitialize are called before
# and after calls to displayHelices, displayStrands
# and displayTurns.  displayTurns should be called
# last because it uses data populated by the first
# two routines.
#
def initialize():
	global ssMap
	ssMap = {}

def deinitialize():
	global ssMap
	ssMap = {}

#
# Calculate orthonormal basis vectors via principal component analysis
#
def findAxes(resList, atomNames):
	coords = []
	for r in resList:
		for atomName in atomNames:
			a = r.findAtom(atomName)
			if not a:
				continue
			c = a.coord()
			coords.append((c.x, c.y, c.z))
	coordinates = numpy.array(coords)
	centroid = coordinates.mean(0)
	ignore, vals, vecs = linalg.svd(coordinates - centroid)

	return coordinates, centroid, vecs.take(vals.argsort()[::-1], 1)

def _normalize(v):
	length = _length(v)
	for i in range(len(v)):
		v[i] = v[i] / length

def _cross(a, b):
	return numpy.array([
		a[1] * b[2] - a[2] * b[1],
		a[2] * b[0] - a[0] * b[2],
		a[0] * b[1] - a[1] * b[0] ])

def _subtract(a, b):
	return [a[0] - b[0], a[1] - b[1], a[2] - b[2]]

def _length(v):
	return math.sqrt(numpy.dot(v, v))

#
# Chimera is very picky about its matrices
# 
# Routine below normalizes a 3x3 matrix to the acceptable tolerance
# 
def matrixNormalize(m):
	det = determinant(m)
	for i in range(3):
		for j in range(3):
			m[i][j] = m[i][j] / det

def determinant(mat):
	return mat[0][0] * _minor(mat, 1, 2, 1, 2) \
		- mat[0][1] * _minor(mat, 1, 2, 0, 2) \
		+ mat[0][2] * _minor(mat, 1, 2, 0, 1)

def _minor(mat, r0, r1, c0, c1):
	return mat[r0][c0] * mat[r1][c1] - mat[r1][c0] * mat[r0][c1]

#
# Compute the parametric variables from "base" to "c" using orthonormal
# bases of "axes"
#
def parametricVars(base, axes, c):
	matrix = numpy.array([
				[axes[0][0], axes[1][0], axes[2][0]],
				[axes[0][1], axes[1][1], axes[2][1]],
				[axes[0][2], axes[1][2], axes[2][2]] ])
	vector = c - base
	return linalg.solve(matrix, vector)

#
# Split a list of residues by finding the pair that has
# the most divergent axes
#
def splitResidues(residues, atomNames):
	for i in range(3, len(residues) - 3):
		front = residues[:i + 1]
		fcrd, fc, fa = findAxes(front, atomNames)
		back = residues[i:]
		bcrd, bc, ba = findAxes(back, atomNames)
		angle = numpy.dot(fa[0], ba[0])
		try:
			if angle < bestAngle:
				best = (front, back)
				bestAngle = angle
		except NameError:
			best = (front, back)
			bestAngle = angle
	try:
		return best
	except NameError:
		return [residues, []]

#
# Find helices and sheets in model
#
def findHelices(mol):
	helices = []
	helix = []
	for r in mol.residues:
		if r.isHelix:
			if helix and not chimera.bondsBetween(r, helix[-1]):
				helices.append(helix)
				helix = []
			helix.append(r)
		elif helix:
			helices.append(helix)
			helix = []
	if helix:
		helices.append(helix)
	return helices

def findStrands(mol):
	strands = []
	strand = []
	for r in mol.residues:
		if r.isSheet:
			if strand and not chimera.bondsBetween(r, strand[-1]):
				strands.append(strand)
				strand = []
			strand.append(r)
		elif strand:
			strands.append(strand)
			strand = []
	if strand:
		strands.append(strand)
	return strands

def findTurns(mol):
	# We actually include the previous and next residues
	# around the turn because we want the secondary structures
	# to connect when displayed
	turns = []
	turn = []
	prev = None
	for r in mol.residues:
		if r.isHet:
			if turn:
				turns.append(turn)
				turn = []
			prev = None
		elif r.isSheet or r.isHelix:
			if turn:
				turn.append(r)
				turns.append(turn)
				turn = []
			prev = r
		else:
			if not turn and prev:
				turn.append(prev)
			turn.append(r)
			prev = r
	if turn:
		turns.append(turn)
	return turns

#
# Create a VRML node representing a helix
#
def showHelix(helix, color, fixedRadius, radius, split, splitRatio):
	if len(helix) < 3:
		return []

	# Find cylinder axes, length and radius
	coords, centroid, axes = findAxes(helix, ['CA'])
	for c in coords:
		s, t, u = parametricVars(centroid, axes, c)
		d = math.sqrt(t * t + u * u)
		try:
			minS = min(s, minS)
			maxS = max(s, maxS)
			minD = min(d, minD)
			maxD = max(d, maxD)
			sumD = sumD + d
		except NameError:
			minS = maxS = s
			minD = maxD = d
			sumD = d
	if split and maxD / minD > splitRatio:
		front, back = splitResidues(helix, ['CA'])
		if back:	# successful split
			return showHelix(front, color, fixedRadius, radius,
						split, splitRatio) \
				+ showHelix(back, color, fixedRadius, radius,
						split, splitRatio)
	if not fixedRadius:
		radius = sumD / len(coords)
	axisLength = maxS + -minS
	halfLength = axisLength / 2
	center = (maxS + minS) / 2 * axes[0] + centroid
	s, t, u = parametricVars(center, axes, coords[0])
	if maxS - s < s - minS:
		ssMap[helix[0]] = ( center + halfLength * axes[0],
					axes[0], axes[1], axes[2] )
		ssMap[helix[-1]] = ( center - halfLength * axes[0],
					-axes[0], axes[1], axes[2] )
	else:
		ssMap[helix[0]] = ( center - halfLength * axes[0],
					-axes[0], axes[1], axes[2] )
		ssMap[helix[-1]] = ( center + halfLength * axes[0],
					axes[0], axes[1], axes[2] )

	mat = [		# Note that the Y axis is mapped onto major axis
		[ axes[1][0],	axes[0][0],	axes[2][0]	],
		[ axes[1][1],	axes[0][1],	axes[2][1]	],
		[ axes[1][2],	axes[0][2],	axes[2][2]	]
	]
	matrixNormalize(mat)
	xf = chimera.Xform.xform(mat[0][0], mat[0][1], mat[0][2], 0,
				mat[1][0], mat[1][1], mat[1][2], 0,
				mat[2][0], mat[2][1], mat[2][2], 0)
	rotAxis, angle = xf.getRotation()
	angle = angle / 180.0 * math.pi

	transform = vrml.Transform()
	trans = vrml.Transform(
			translation=(center[0], center[1], center[2]))
	transform.addChild(trans)
	rot = vrml.Transform(
			rotation=(rotAxis.x, rotAxis.y, rotAxis.z, angle))
	trans.addChild(rot)
	rgba = color.get().rgba()
	cylinder = vrml.Cylinder(radius=radius, height=axisLength,
					color=rgba[:3])
	if rgba[3] < 1.0:
		cylinder.transparency = 1.0 - rgba[3]
	rot.addChild(cylinder)
	return [ transform ]

def displayHelices(mol, color, fixedRadius, radius, split, splitRatio):
	nodes = []
	for helix in findHelices(mol):
		helices = showHelix(helix, color, fixedRadius, radius,
					split, splitRatio)
		nodes = nodes + helices
	return nodes
#
# Create a VRML node representing a sheet
#
def showStrand(strand, color, fixedWidth, width, fixedThickness, thickness,
		split, splitRatio):
	if len(strand) < 3:
		return []
	# Find box axes, length, width and thickness
	coords, centroid, axes = findAxes(strand, ['O'])
	for c in coords:
		s, t, u = parametricVars(centroid, axes, c)
		t = math.fabs(t)
		u = math.fabs(u)
		try:
			minS = min(s, minS)
			maxS = max(s, maxS)
			sumT = sumT + t
			minU = min(u, minU)
			maxU = max(u, maxU)
			sumU = sumU + u
		except NameError:
			minS = maxS = s
			sumT = t
			minU = maxU = u
			sumU = u
	if split and maxU / minU > splitRatio:
		front, back = splitResidues(strand, ['O'])
		if back:	# successful split
			return showStrand(front, color, fixedWidth, width,
						fixedThickness, thickness,
						split, splitRatio) \
				+ showStrand(back, color, fixedWidth, width,
						fixedThickness, thickness,
						split, splitRatio)
	length = maxS + -minS
	center = (maxS + minS) / 2 * axes[0] + centroid
	if not fixedWidth:
		width = sumT / len(coords) * 2
	if not fixedThickness:
		thickness = sumU / len(coords) * 2
	hl = length / 2
	s, t, u = parametricVars(center, axes, coords[0])
	if maxS - s > s - minS:
		ssMap[strand[0]] = ( center - hl * axes[0],
					-axes[0], axes[1], axes[2] )
		ssMap[strand[-1]] = ( center + hl * axes[0],
					axes[0], axes[1], axes[2] )
	else:
		ssMap[strand[0]] = ( center + hl * axes[0],
					axes[0], axes[1], axes[2] )
		ssMap[strand[-1]] = ( center - hl * axes[0],
					-axes[0], axes[1], axes[2] )

	mat = [		# Note that the X axis is mapped onto length axis
			# ... and Y is mapped onto width axis 
		[ axes[0][0],	axes[1][0],	axes[2][0]	],
		[ axes[0][1],	axes[1][1],	axes[2][1]	],
		[ axes[0][2],	axes[1][2],	axes[2][2]	]
	]
	matrixNormalize(mat)
	xf = chimera.Xform.xform(mat[0][0], mat[0][1], mat[0][2], 0,
				mat[1][0], mat[1][1], mat[1][2], 0,
				mat[2][0], mat[2][1], mat[2][2], 0)
	rotAxis, angle = xf.getRotation()
	angle = angle / 180.0 * math.pi

	transform = vrml.Transform()
	trans = vrml.Transform(
			translation=(center[0], center[1], center[2]))
	transform.addChild(trans)
	rot = vrml.Transform(
			rotation=(rotAxis.x, rotAxis.y, rotAxis.z, angle))
	trans.addChild(rot)
	rgba = color.get().rgba()
	box = vrml.Box(size=(length, width, thickness), color=rgba[:3])
	if rgba[3] < 1.0:
		box.transparency = 1.0 - rgba[3]
	rot.addChild(box)
	return [ transform ]

def displayStrands(mol, color, fixedWidth, width, fixedThickness, thickness,
			split, splitRatio):
	nodes = []
	for strand in findStrands(mol):
		nodes = nodes + showStrand(strand, color,
						fixedWidth, width,
						fixedThickness, thickness,
						split, splitRatio)
	return nodes
#
# Create a VRML node representing a turn
#
def showTurn(turn, color, width, thickness):
	pt = []
	for r in turn:
		a = r.findAtom('CA')
		if not a:
			continue
		pt.append(a.coord())
	size = max(width, thickness)
	try:
		c, d, n, b = ssMap[turn[0]]
		cv = chimera.Point(c[0], c[1], c[2])
		dv = chimera.Vector(d[0], d[1], d[2])
		nv = chimera.Vector(n[0], n[1], n[2])
		bv = chimera.Vector(b[0], b[1], b[2])
		startDir = dv
		startNormals = (nv, bv)
		pt.insert(0, cv)
	except KeyError:
		startDir = None
		startNormals = None
	try:
		c, d, n, b = ssMap[turn[-1]]
		cv = chimera.Point(c[0], c[1], c[2])
		dv = chimera.Vector(d[0], d[1], d[2])
		nv = chimera.Vector(n[0], n[1], n[2])
		bv = chimera.Vector(b[0], b[1], b[2])
		endDir = -dv
		endNormals = (nv, bv)
		pt.append(cv)
	except KeyError:
		endDir = None
		endNormals = None
	if len(pt) < 3:
		return []
	if len(pt) == 3:
		# need at least 4 points for vrml.Extrustion
		if startDir:
			pt.insert(1, chimera.Point(pt[:2]))
		if endDir:
			pt.insert(-1, chimera.Point(pt[-2:]))
	dir = []
	if startDir is None:
		dir.append(pt[1] - pt[0])
	else:
		dir.append(startDir)
	for i in range(1, len(pt) - 1):
		dir.append(pt[i + 1] - pt[i - 1])
	if endDir is None:
		dir.append(pt[-1] - pt[-2])
	else:
		dir.append(endDir)
	offsets = [ [0.0, thickness], [width, 0.0],
			 [0.0, -thickness], [-width, 0.0] ]
	edges = []
	for i in offsets:
		edges.append([])
	if startNormals is not None:
		normal, binormal = startNormals
	else:
		normal, binormal = getEndNormals(pt[0], pt[1], pt[2])
	addEdges(edges, offsets, pt[0], normal, binormal)
	for i in range(1, len(pt) - 1):
		try:
			n, b = getInteriorNormals(pt[i], pt[i - 1], pt[i + 1])
			normal, binormal = minimizeTwist(dir[i], n, b,
							normal, binormal)
		except ValueError:
			# This can happen if the three points are linear
			# We just inherit the normals from the previous triple
			pass
		addEdges(edges, offsets, pt[i], normal, binormal)
	if endNormals is not None:
		n, b = endNormals
	else:
		n, b = getEndNormals(pt[-1], pt[-3], pt[-2])
	normal, binormal = minimizeTwist(dir[-1], n, b,
						normal, binormal)
	addEdges(edges, offsets, pt[-1], normal, binormal)
	rgba = color.get().rgba()
	ext = vrml.Extrusion(color=rgba[:3], edges=edges)
	if rgba[3] < 1.0:
		ext.transparency = 1.0 - rgba[3]
	return [ ext ]

def getEndNormals(c0, c1, c2):
	v1 = c1 - c0
	v2 = c2 - c0
	binormal = chimera.cross(v1, v2)
	binormal.normalize()
	normal = chimera.cross(binormal, v1)
	normal.normalize()
	return normal, binormal

def getInteriorNormals(c0, cb, ca):
	vb = cb - c0
	va = ca - c0
	vab = ca - cb
	binormal = chimera.cross(va, vb)
	binormal.normalize()
	normal = chimera.cross(binormal, vab)
	normal.normalize()
	return normal, binormal

def minimizeTwist(d, nn, nb, on, ob):
	# To minimize twisting, we use the ribbon direction
	# (approximated by the vector from the previous residue
	# to the next residue) as the axis and project the normal
	# and binormal both for this (n) and previous (o) residue.
	# We don't care about maintaining handedness (defined by
	# direction, normal and binormal) or about orientation
	# (binormal and normal may be swapped).  So we find whether
	# which two vectors (one from this and one from previous
	# residue) match best.  That determines whether we match
	# normal to normal or normal to binormal.  Once we decide
	# that, we can flip normal and binormal so that they never
	# rotate more than 90 degrees.
	nn0 = chimera.cross(nn, d)
	nn0.normalize()
	on0 = chimera.cross(on, d)
	on0.normalize()
	nb0 = chimera.cross(nb, d)
	nb0.normalize()
	ob0 = chimera.cross(ob, d)
	ob0.normalize()
	ndotn = nn0 * on0
	bdotb = nb0 * ob0
	matchBest = max(abs(ndotn), abs(bdotb))
	ndotb = nn0 * ob0
	bdotn = nb0 * on0
	swapBest = max(abs(ndotb), abs(bdotn))
	if matchBest >= swapBest:
		# We match normal to normal, binormal to binormal
		if ndotn < 0:
			normal = -nn
		else:
			normal = nn
		if bdotb < 0:
			binormal = -nb
		else:
			binormal = nb
	else:
		# We match normal to binormal, binormal to normal
		if ndotb < 0:
			binormal = -nn
		else:
			binormal = nn
		if bdotn < 0:
			normal = -nb
		else:
			normal = nb
	return normal, binormal

def addEdges(edges, offsets, coord, normal, binormal):
	for i in range(len(offsets)):
		n, b = offsets[i]
		c = []
		for j in range(3):
			c.append(coord[j] + n * normal[j] + b * binormal[j])
		edges[i].append(c)

def displayTurns(mol, color, width, thickness):
	nodes = []
	for turn in findTurns(mol):
		nodes = nodes + showTurn(turn, color, width, thickness)
	return nodes
