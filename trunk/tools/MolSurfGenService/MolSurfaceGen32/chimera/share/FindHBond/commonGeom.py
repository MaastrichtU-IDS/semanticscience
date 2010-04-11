# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: commonGeom.py 26655 2009-01-07 22:02:30Z gregc $

from chimera import cross, angle, Vector, Point
import base

SULFUR_COMP = 0.35

class ConnectivityError(ValueError):
	pass

class AtomTypeError(ValueError):
	pass

def testPhi(dp, ap, bp, phiPlane, phi):
	if phiPlane:
		normal = cross(phiPlane[1] - phiPlane[0],
						phiPlane[2] - phiPlane[1])
		normal.normalize()
		D = normal * phiPlane[1].toVector()
		bproj = project(bp, normal, D)
		aproj = project(ap, normal, D)
		dproj = project(dp, normal, D)
		
		ang = angle(bproj, aproj, dproj)
		if ang < phi:
			if base.verbose:
				print "phi criteria failed (%g < %g)" % (ang, phi)
			return 0
		if base.verbose:
			print "phi criteria OK (%g >= %g)" % (ang, phi)
	else:
		if base.verbose:
			print "phi criteria irrelevant"
	return 1

def getPhiPlaneParams(acceptor, bonded1, bonded2):
	ap = acceptor.xformCoord()
	if bonded2:
		# two principal bonds
		phiPlane = [ap]
		midPoint = Vector(0.0, 0.0, 0.0)
		for bonded in [bonded1, bonded2]:
			pt = bonded.xformCoord()
			phiPlane.append(pt)
			midPoint = midPoint + pt.toVector()
		midPoint = midPoint / 2.0
		phiBasePos = Point(midPoint.x, midPoint.y, midPoint.z)
	elif bonded1:
		# one principal bond
		phiBasePos = bonded1.xformCoord()
		grandBonded = bonded1.primaryNeighbors()
		for al in acceptor.allLocations():
			if al in grandBonded:
				grandBonded.remove(al)
				break
		else:
			raise ValueError("No locations of acceptor %s found"
				" in bond list of %s" % (acceptor, bonded1))
		if len(grandBonded) == 1:
			phiPlane = [ap, bonded1.xformCoord(),
						grandBonded[0].xformCoord()]
		elif len(grandBonded) == 2:
			phiPlane = [ap]
			for gb in grandBonded:
				phiPlane.append(gb.xformCoord())
		elif len(grandBonded) == 0:
			# e.g. O2
			phiPlane = None
		else:
			raise ConnectivityError("Wrong number of grandchild"
					" atoms for phi/psi acceptor %s"
					% acceptor.oslIdent())
	else:
		return None, None
	return phiPlane, phiBasePos

def project(point, normal, D):
	# project point into plane defined by normal and D.
	return point - normal * (normal * point.toVector() - D)

def testTheta(dp, donorHyds, ap, theta):
	if len(donorHyds) == 0:
		if base.verbose:
			print "no hydrogens for theta test; default accept"
		return 1
	for hydPos in donorHyds:
		ang =  angle(ap, hydPos, dp)
		if ang >= theta:
			if base.verbose:
				print "theta okay (%g >= %g)" % (ang, theta)
			return 1
		if base.verbose:
			print "theta failure (%g < %g)" % (ang, theta)

	return 0

def sulphurCompensate(baseR2):
	from base import _computeCache
	try:
		return _computeCache[baseR2]
	except KeyError:
		pass
	import math
	r = math.sqrt(baseR2)
	r = r + SULFUR_COMP
	newR2 = r * r
	_computeCache[baseR2] = newR2
	return newR2
