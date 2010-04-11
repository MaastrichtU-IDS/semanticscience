# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: acceptorGeom.py 26655 2009-01-07 22:02:30Z gregc $

"""acceptor geometry testing functions"""

from chimera import Xform, sqdistance, distance, angle, Vector, cross
from chimera.bondGeom import bondPositions
from chimera.idatm import tetrahedral
import base
from commonGeom import testPhi, getPhiPlaneParams, testTheta, sulphurCompensate
from hydpos import hydPositions
from math import sqrt

def accSynAnti(donor, donorHyds, acceptor, synAtom, planeAtom, synR2, synPhi,
		synTheta, antiR2, antiPhi, antiTheta):
	"""'planeAtom' (in conjunction with acceptor, and with 'synAtom'
	    defining the 'up' direction) defines a plane.  If donor is on
	    the same side as 'synAtom', use syn params, otherwise anti params.
	"""

	if base.verbose:
		print "accSynAnti"
	dc = donor.xformCoord()
	dp = dc
	ac = acceptor.xformCoord()
	ap = ac
	pp = planeAtom.xformCoord()
	sp = synAtom.xformCoord()

	synXform = Xform.lookAt(ap, pp, sp - pp)
	xdp = synXform.apply(dp)

	phiBasePos = pp
	phiPlane = [ap, pp, sp]

	if xdp.y > 0.0:
		if base.verbose:
			print "Syn"
		if donor.element.name == "S":
			# increase distance cutoff to allow for larger
			# vdw radius of sulphur (which isn't considered
			# considered as a donor in original paper)
			synR2 = sulphurCompensate(synR2)
		return testPhiPsi(dp, donorHyds, ap, phiBasePos, phiPlane,
						synR2, synPhi, synTheta)
	if base.verbose:
		print "Anti"
	if donor.element.name == "S":
		# increase distance to compensate for sulphur radius
		antiR2 = sulphurCompensate(antiR2)
	return testPhiPsi(dp, donorHyds, ap, phiBasePos, phiPlane,
						antiR2, antiPhi, antiTheta)

def accPhiPsi(donor, donorHyds, acceptor, bonded1, bonded2, r2, phi, theta):
	if base.verbose:
		print "accPhiPsi"

	# when acceptor bonded to one heavy atom
	if not bonded1:
		# water
		bonded = acceptor.primaryNeighbors()
		if len(bonded) > 0:
			bonded1 = bonded[0]
			if len(bonded) > 1:
				bonded2 = bonded[1]
		
	phiPlane, phiBasePos = getPhiPlaneParams(acceptor, bonded1, bonded2)
	if donor.element.name == "S":
		r2 = sulphurCompensate(r2)
	return testPhiPsi(donor.xformCoord(), donorHyds,
		acceptor.xformCoord(), phiBasePos, phiPlane, r2, phi, theta)

def testPhiPsi(dp, donorHyds, ap, bp, phiPlane, r2, phi, theta):
	if base.verbose:
		print "distance: %g, cut off: %g" % (distance(dp, ap), sqrt(r2))
	if sqdistance(dp, ap) > r2:
		if base.verbose:
			print "dist criteria failed"
		return 0
	if base.verbose:
		print "dist criteria OK"

	if not testPhi(dp, ap, bp, phiPlane, phi):
		return 0

	return testTheta(dp, donorHyds, ap, theta)
	
def accThetaTau(donor, donorHyds, acceptor, upsilonPartner, r2,
						upsilonLow, upsilonHigh, theta):
	if base.verbose:
		print "accThetaTau"
	dp = donor.xformCoord()
	ap = acceptor.xformCoord()

	if donor.element.name == "S":
		r2 = sulphurCompensate(r2)
	if base.verbose:
		print "distance: %g, cut off: %g" % (distance(dp, ap), sqrt(r2))
	if sqdistance(dp, ap) > r2:
		if base.verbose:
			print "dist criteria failed"
		return 0
	if base.verbose:
		print "dist criteria okay"
	
	if upsilonPartner:
		upPos = upsilonPartner.xformCoord()
	else:
		# upsilon measured from "lone pair" (bisector of attached
		# atoms)
		bondedPos = []
		for bonded in acceptor.primaryNeighbors():
			bondedPos.append(bonded.xformCoord())
		lonePairs = bondPositions(ap, tetrahedral, 1.0, bondedPos)
		bisectors = []
		for lp in lonePairs:
			bisectors.append(ap - (lp - ap))
		upPos = bisectors[0]
		for bs in bisectors[1:]:
			if base.verbose:
				print "Testing 'extra' lone pair"
			if testThetaTau(dp, donorHyds, ap, bs,
						upsilonLow, upsilonHigh, theta):
				return 1
	return testThetaTau(dp, donorHyds, ap, upPos,
						upsilonLow, upsilonHigh, theta)

def testThetaTau(dp, donorHyds, ap, pp, upsilonLow, upsilonHigh, theta):
	if pp:
		upsilonHigh = 0 - upsilonHigh
		upsilon = angle(pp, ap, dp)
		if upsilon < upsilonLow or upsilon > upsilonHigh:
			if base.verbose:
				print "upsilon (%g) failed (%g-%g)" % (
					upsilon, upsilonLow, upsilonHigh)
			return 0
	else:
		if base.verbose:
			print "can't determine upsilon; default okay"
	if base.verbose:
		print "upsilon okay"
	return testTheta(dp, donorHyds, ap, theta)

def accGeneric(donor, donorHyds, acceptor, r2, minAngle):
	if base.verbose:
		print "generic acceptor"
	dp = donor.xformCoord()
	ap = acceptor.xformCoord()
	if donor.element.name == "S":
		r2 = sulphurCompensate(r2)
	if base.verbose:
		print "distance: %g, cut off: %g" % (distance(dp, ap), sqrt(r2))
	if sqdistance(dp, ap) > r2:
		if base.verbose:
			print "dist criteria failed"
		return 0
	if base.verbose:
		print "dist criteria okay"
	 
	ap = acceptor.xformCoord()
	dp = donor.xformCoord()
	for bonded in acceptor.primaryNeighbors():
		bp = bonded.xformCoord()
		if base.verbose:
			print "angle: %g" % angle(bp, ap, dp)
		ang = angle(bp, ap, dp)
		if ang < minAngle:
			if base.verbose:
				print "angle too sharp (%g < %g)" % (ang,
								minAngle)
			return 0
	if base.verbose:
		print "angle(s) okay (all > %g)" % minAngle
	return 1
