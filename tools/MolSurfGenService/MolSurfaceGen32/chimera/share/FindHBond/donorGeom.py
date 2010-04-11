# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: donorGeom.py 26655 2009-01-07 22:02:30Z gregc $

"""donor geometry testing functions"""

from chimera.idatm import typeInfo, planar, tetrahedral
from chimera import angle, sqdistance
from chimera.bondGeom import bondPositions
import base
from commonGeom import AtomTypeError, getPhiPlaneParams, \
				testPhi, project, testTheta, sulphurCompensate
from hydpos import hydPositions
from math import sqrt

def donThetaTau(donor, donorHyds, acceptor,
					sp2Orp2, sp2Otheta,
					sp3Orp2, sp3Otheta, sp3Ophi,
					sp3Nrp2, sp3Ntheta, sp3Nupsilon,
					genRp2, genTheta,
					isWater=0):
					# 'isWater' only for hydrogenless water
	if base.verbose:
		print "donThetaTau"
	if len(donorHyds) == 0 and not isWater:
		if base.verbose:
			print "No hydrogens; default failure"
		return 0
	ap = acceptor.xformCoord()
	dp = donor.xformCoord()

	accType = acceptor.idatmType
	if not typeInfo.has_key(accType):
		if base.verbose:
			print "Unknown acceptor type failure"
		return 0
	
	geom = typeInfo[accType].geometry
	element = acceptor.element.name
	if element == 'O' and geom == planar:
		if base.verbose:
			print "planar O"
		for hydPos in donorHyds:
			if sqdistance(hydPos, ap) <= sp2Orp2:
				break
		else:
			if not isWater:
				if base.verbose:
					print "dist criteria failed (all > %g)"\
						% sqrt(sp2Orp2)
				return 0
		theta = sp2Otheta
	elif element == 'O' and geom == tetrahedral \
	or element == 'N' and geom == planar:
		if base.verbose:
			print "planar N or tet O"
		for hydPos in donorHyds:
			if sqdistance(hydPos, ap) <= sp3Orp2:
				break
		else:
			if not isWater:
				if base.verbose:
					print "dist criteria failed (all > %g)"\
						% sqrt(sp3Orp2)
				return 0
		theta = sp3Otheta
		
		# only test phi for acceptors with two bonded atoms
		if len(acceptor.primaryBonds()) == 2:
			if base.verbose:
				print "testing donor phi"
			bonded = acceptor.primaryNeighbors()
			phiPlane, basePos = getPhiPlaneParams(acceptor,
							bonded[0], bonded[1])
			if not testPhi(donor.xformCoord(), ap, basePos,
							phiPlane, sp3Ophi):
				return 0

	elif element == 'N' and geom == tetrahedral:
		if base.verbose:
			print "tet N"
		for hydPos in donorHyds:
			if sqdistance(hydPos, ap) <= sp3Nrp2:
				break
		else:
			if not isWater:
				if base.verbose:
					print "dist criteria failed (all > %g)"\
						% sqrt(sp3Nrp2)
				return 0
		theta = sp3Ntheta

		# test upsilon against lone pair directions
		bondedPos = []
		for bonded in acceptor.primaryNeighbors():
			bondedPos.append(bonded.xformCoord())
		lpPos = bondPositions(ap, geom, 1.0, bondedPos)
		if lpPos:
			# fixed lone pair positions
			for lp in bondPositions(ap, geom, 1.0, bondedPos):
				# invert position so that we are
				# measuring angles correctly
				ang = angle(dp, ap, ap - (lp - ap))
				if ang > sp3Nupsilon:
					if base.verbose:
						print "acceptor upsilon okay"\
							" (%g > %g)" % (
							ang, sp3Nupsilon)
					break
			else:
				if base.verbose:
					print "all acceptor upsilons failed"\
						" (< %g)" % sp3Nupsilon
				return 0
		# else: indefinite lone pair positions; default okay
	else:
		if base.verbose:
			print "generic acceptor"
		if acceptor.element.name == "S":
			genRp2 = sulphurCompensate(genRp2)
		for hydPos in donorHyds:
			if sqdistance(hydPos, ap) <= genRp2:
				break
		else:
			if base.verbose:
				print "dist criteria failed (all > %g)" % sqrt(
								genRp2)
			return 0
		theta = genTheta
	if base.verbose:
		print "dist criteria OK"

	return testTheta(dp, donorHyds, ap, theta)


def donUpsilonTau(donor, donorHyds, acceptor,
  sp2Or2, sp2OupsilonLow, sp2OupsilonHigh, sp2Otheta, sp2Otau,
  sp3Or2, sp3OupsilonLow, sp3OupsilonHigh, sp3Otheta, sp3Otau, sp3Ophi,
  sp3Nr2, sp3NupsilonLow, sp3NupsilonHigh, sp3Ntheta, sp3Ntau, sp3NupsilonN,
  genR2, genUpsilonLow, genUpsilonHigh, genTheta, tauSym):

	if base.verbose:
		print "donUpsilonTau"

	accType = acceptor.idatmType
	if not typeInfo.has_key(accType):
		return 0
	
	geom = typeInfo[accType].geometry
	element = acceptor.element.name
	if element == 'O' and geom == planar:
		if base.verbose:
			print "planar O"
		return testUpsilonTauAcceptor(donor, donorHyds, acceptor,
			sp2Or2, sp2OupsilonLow, sp2OupsilonHigh, sp2Otheta,
			sp2Otau, tauSym)
	elif element == 'O' and geom == tetrahedral \
	or element == 'N' and geom == planar:
		if base.verbose:
			print "planar N or tet O"
		return testUpsilonTauAcceptor(donor, donorHyds, acceptor,
			sp3Or2, sp3OupsilonLow, sp3OupsilonHigh, sp3Otheta,
			sp3Otau, tauSym)
	elif element == 'N' and geom == tetrahedral:
		if base.verbose:
			print "tet N"
		# test upsilon at the N
		# see if lone pairs point at the donor
		bondedPos = []
		for bonded in acceptor.primaryNeighbors():
			bondedPos.append(bonded.xformCoord())
		if len(bondedPos) > 1:
			ap = acceptor.xformCoord()
			dp = donor.xformCoord()
			lonePairs = bondPositions(ap, tetrahedral, 1.0,
								bondedPos)
			for lp in lonePairs:
				upPos = ap - (lp - ap)
				ang = angle(upPos, ap, dp)
				if ang >= sp3NupsilonN:
					if base.verbose:
						print "upsilon(N) okay" \
							" (%g >= %g)" % (ang,
							sp3NupsilonN)
					break
			else:
				if base.verbose:
					print "all upsilon(N) failed (< %g)" % (
								sp3NupsilonN)
				return 0
		elif base.verbose:
			print "lone pair positions indeterminate at N;" \
						"upsilon(N) default okay"
		return testUpsilonTauAcceptor(donor, donorHyds, acceptor,
			sp3Nr2, sp3NupsilonLow, sp3NupsilonHigh, sp3Ntheta,
			sp3Ntau, tauSym)
	else:
		if base.verbose:
			print "generic acceptor"
		if acceptor.element.name == "S":
			genR2 = sulphurCompensate(genR2)
		return testUpsilonTauAcceptor(donor, donorHyds, acceptor,
			genR2, genUpsilonLow, genUpsilonHigh, genTheta,
			None, None)
	if base.verbose:
		print "failed criteria"
	return 0

def testUpsilonTauAcceptor(donor, donorHyds, acceptor, r2, upsilonLow,
					upsilonHigh, theta, tau, tauSym):
	dc = donor.xformCoord()
	ac = acceptor.xformCoord()

	D2 = dc.sqdistance(ac)
	if D2 > r2:
		if base.verbose:
			print "dist criteria failed (%g > %g)" % (sqrt(D2),
								sqrt(r2))
		return 0

	upsilonHigh = 0 - upsilonHigh
	heavys = filter(lambda a: a.element.number > 1,
						donor.primaryNeighbors())
	if len(heavys) != 1:
		raise AtomTypeError("upsilon tau donor (%s) not bonded to"
			" exactly one heavy atom" % donor.oslIdent())
	ang = angle(heavys[0].xformCoord(), dc, ac)
	if ang < upsilonLow or ang > upsilonHigh:
		if base.verbose:
			print "upsilon criteria failed (%g < %g or %g > %g)" % (
				ang, upsilonLow, ang, upsilonHigh)
		return 0
	if base.verbose:
		print "upsilon criteria OK (%g < %g < %g)" % (upsilonLow, ang,
								upsilonHigh)

	dp = dc
	ap = ac

	if not testTheta(dp, donorHyds, ap, theta):
		return 0
	
	if tau is None:
		if base.verbose:
			print "tau test irrelevant"
		return 1

	# sulfonamides and phosphonamides can have bonded NH2 groups that
	# are planar enough to be declared Npl, so use the hydrogen
	# positions to determine planarity if possible
	if tauSym == 4:
		bondedPos = hydPositions(donor)
	else:
		# since we expect tetrahedral hydrogens to be oppositely
		# aligned from the attached tetrahedral center, 
		# we can't use their positions for tau testing
		bondedPos = []
	if 2 * len(bondedPos) != tauSym:
		bondedPos = hydPositions(heavys[0], includeLonePairs=True)
		donorEquiv = donor.allLocations()
		for b in heavys[0].primaryNeighbors():
			if b in donorEquiv or b.element.number < 2:
				continue
			bondedPos.append(b.xformCoord())
		if not bondedPos:
			if base.verbose:
				print "tau indeterminate; default okay"
			return 1

	if 2 * len(bondedPos) != tauSym:
		raise AtomTypeError("Unexpected tau symmetry (%d,"
				" should be %d) for donor %s" % (
				2 * len(bondedPos), tauSym, donor.oslIdent()))

	normal = heavys[0].xformCoord() - dp
	normal.normalize()

	if tau < 0.0:
		test = lambda ang, t=tau: ang <= 0.0 - t
	else:
		test = lambda ang, t=tau: ang >= t
	
	projAccPos = project(ap, normal, 0.0)
	projDonPos = project(dp, normal, 0.0)
	for bpos in bondedPos:
		projBpos = project(bpos, normal, 0.0)
		ang = angle(projAccPos, projDonPos, projBpos)
		if test(ang):
			if tau < 0.0:
				if base.verbose:
					print "tau okay (%g < %g)" % (ang, -tau)
				return 1
		else:
			if tau > 0.0:
				if base.verbose:
					print "tau too small (%g < %g)" % (ang,
									tau)
				return 0
	if tau < 0.0:
		if base.verbose:
			print "all taus too big (> %g)" % -tau
		return 0
	
	if base.verbose:
		print "all taus acceptable (> %g)" % tau
	return 1

def donGeneric(donor, donorHyds, acceptor, sp2Orp2, sp3Orp2, sp3Nrp2,
	sp2Or2, sp3Or2, sp3Nr2, genRp2, genR2, minHydAngle, minBondedAngle):
	if base.verbose:
		print "donGeneric"
	dc = donor.xformCoord()
	ac = acceptor.xformCoord()

	accType = acceptor.idatmType
	if not typeInfo.has_key(accType):
		return 0

	geom = typeInfo[accType].geometry
	element = acceptor.element.name
	if element == 'O' and geom == planar:
		if base.verbose:
			print "planar O"
		r2 = sp2Or2
		rp2 = sp2Orp2
	elif element == 'O' and geom == tetrahedral \
	or element == 'N' and geom == planar:
		if base.verbose:
			print "planar N or tet O"
		r2 = sp3Or2
		rp2 = sp3Orp2
	elif element == 'N' and geom == tetrahedral:
		if base.verbose:
			print "tet N"
		r2 = sp3Nr2
		rp2 = sp3Nrp2
	else:
		if base.verbose:
			print "generic acceptor"
		if acceptor.element.name == "S":
			r2 = sulphurCompensate(genR2)
			minBondedAngle = minBondedAngle - 9
		r2 = genR2
		rp2 = genRp2

	ap = acceptor.xformCoord()
	dp = donor.xformCoord()
	if len(donorHyds) == 0:
		D2 = dc.sqdistance(ac)
		if D2 > r2:
			if base.verbose:
				print "dist criteria failed (%g > %g)" % (
							sqrt(D2), sqrt(r2))
			return 0
	else:
		for hydPos in donorHyds:
			if sqdistance(hydPos, ap) < rp2:
				break
		else:
			if base.verbose:
				print "hyd dist criteria failed (all >= %g)" % (
								sqrt(rp2))
			return 0
		
	if base.verbose:
		print "dist criteria OK"

	for bonded in donor.primaryNeighbors():
		if bonded.element.number <= 1:
			continue
		bp = bonded.xformCoord()
		ang = angle(bp, dp, ap)
		if ang < minBondedAngle:
			if base.verbose:
				print "bonded angle too sharp (%g < %g)" % (
						ang, minBondedAngle)
			return 0
		
	if len(donorHyds) == 0:
		if base.verbose:
			print "No specific hydrogen positions; default accept"
		return 1

	for hydPos in donorHyds:
		ang = angle(dp, hydPos, ap)
		if ang >= minHydAngle:
			if base.verbose:
				print "hydrogen angle okay (%g >= %g)" % (
						ang, minHydAngle)
			return 1
	if base.verbose:
		print "hydrogen angle(s) too sharp (< %g)" % minHydAngle
	return 0

def donWater(donor, donorHyds, acceptor,
					sp2Orp2, sp2Or2, sp2Otheta,
					sp3Orp2, sp3Or2, sp3Otheta, sp3Ophi,
					sp3Nrp2, sp3Nr2, sp3Ntheta, sp3Nupsilon,
					genRp2, genR2, genTheta):
	if base.verbose:
		print "donWater"
	if len(donorHyds) > 0:
		# hydrogens explicitly present,
		# can immediately call donThetaTau
		return donThetaTau(donor, donorHyds, acceptor, sp2Orp2,
			sp2Otheta, sp3Orp2, sp3Otheta, sp3Ophi, sp3Nrp2,
			sp3Ntheta, sp3Nupsilon, genRp2, genTheta)

	ap = acceptor.xformCoord()
	dp = donor.xformCoord()

	accType = acceptor.idatmType
	if not typeInfo.has_key(accType):
		if base.verbose:
			print "Unknown acceptor type failure"
		return 0
	
	geom = typeInfo[accType].geometry
	element = acceptor.element.name
	if element == 'O' and geom == planar:
		if base.verbose:
			print "planar O"
		sq = sqdistance(dp, ap)
		if sq > sp2Or2:
			if base.verbose:
				print "dist criteria failed (%g > %g)" % (
						sqrt(sq), sqrt(sp2Or2))
			return 0
	elif element == 'O' and geom == tetrahedral \
	or element == 'N' and geom == planar:
		if base.verbose:
			print "planar N or tet O"
		sq = sqdistance(dp, ap)
		if sq > sp3Or2:
			if base.verbose:
				print "dist criteria failed (%g > %g)" % (
						sqrt(sq), sqrt(sp3Or2))
			return 0
	elif element == 'N' and geom == tetrahedral:
		if base.verbose:
			print "tet N"
		sq = sqdistance(dp, ap)
		if sq > sp3Nr2:
			if base.verbose:
				print "dist criteria failed (%g > %g)" % (
						sqrt(sq), sqrt(sp3Nr2))
			return 0
	else:
		if base.verbose:
			print "generic acceptor"
		sq = sqdistance(dp, ap)
		if sq > genR2:
			if base.verbose:
				print "dist criteria failed (%g > %g)" % (
						sqrt(sq), sqrt(genR2))
			return 0
	if base.verbose:
		print "dist criteria OK"

	return donThetaTau(donor, donorHyds, acceptor, sp2Orp2,
		sp2Otheta, sp3Orp2, sp3Otheta, sp3Ophi, sp3Nrp2,
		sp3Ntheta, sp3Nupsilon, genRp2, genTheta, isWater=1)
