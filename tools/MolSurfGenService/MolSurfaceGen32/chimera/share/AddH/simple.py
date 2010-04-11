from chimera import Coord, Point
from chimera.bondGeom import tetrahedral, planar, linear, single, bondPositions
from chimera.idatm import *
from AddH import newHydrogen, findNearest, roomiest, bondWithHLength, \
							findRotamerNearest
from math import sin, cos, pi, sqrt
from chimera import Element
Element_H = Element(1)

sin5475 = sin(pi * 54.75 / 180.0)
cos5475 = cos(pi * 54.75 / 180.0)

def addHydrogens(atom, bondingInfo, namingSchema, totalHydrogens, idatmType,
							invert, coordinations):
	away = away2 = planar = None
	geom = bondingInfo.geometry
	substs = bondingInfo.substituents
	curBonds = len(atom.primaryBonds())
	needed = substs - curBonds
	if needed <= 0:
		return
	atPos = atom.xformCoord()
	exclude = coordinations + atom.primaryNeighbors()
	if geom == 3 and curBonds == 1:
		bonded = atom.primaryNeighbors()[0]
		grandBonded = bonded.primaryNeighbors()
		grandBonded.remove(atom)
		if len(grandBonded) < 3:
			planar = [a.xformCoord() for a in grandBonded]
	if geom == 4 and not exclude:
		away, d, natom = findNearest(atPos, atom, exclude, 3.5)
		if away:
			away2, d2, natom2 = findRotamerNearest(atPos,
				idatmType[atom], atom, natom, 3.5)
	elif geom == 4 and len(exclude) == 1:
		away, d, natom = findRotamerNearest(atPos,
				idatmType[atom], atom, exclude[0], 3.5)
	else:
		away, d, natom = findNearest(atPos, atom, exclude, 3.5)

	bondedPos = []
	for bonded in atom.primaryNeighbors():
		bondedPos.append(bonded.xformCoord())

	if coordinations:
		toward = coordinations[0].xformCoord()
		away2 = away
		away = None
	else:
		toward = None
	positions = bondPositions(atPos, geom, bondWithHLength(atom, geom),
		bondedPos, toward=toward, coPlanar=planar, away=away, away2=away2)
	if coordinations:
		coordPos = None
		for pos in positions:
			d = pos.sqdistance(toward)
			if coordPos is None or d < lowest:
				coordPos = pos
				lowest = d
		positions.remove(coordPos)
	if len(positions) > needed:
		positions = roomiest(positions, atom, 3.5)[:needed]
	for i, pos in enumerate(positions):
		newHydrogen(atom, i+1, totalHydrogens, namingSchema,
							invert.apply(pos))
