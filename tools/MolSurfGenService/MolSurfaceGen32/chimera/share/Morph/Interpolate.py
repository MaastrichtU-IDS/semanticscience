def interpolate(mol, molXform, segments, equivAtoms, method, rMethod,
			frames, cartesian, cb):
	# mol		molecule where new coordinate sets are added
	#		should already have first frame in place
	# molXform	transform to convert atoms from their own
	#		local coordinate system into "mol" local coordinates
	#		(usually [inverse transform of trajectory model] x
	#		[transform of target model])
	# segments	list of 2-tuples of matching residue lists
	# equivAtoms	dictionary of equivalent atoms
	#		key is atom from first frame
	#		value is 2-tuple of atoms from last frame and "mol"
	# method	interpolation method name
	# rMethod	rate profile, e.g., "linear"
	# frames	number of frames to generate in trajectory
	# cartesian	use cartesian coordinate interpolation?
	# cb		function called for every frame generated 

	import InterpResidue
	from util import getAtomList, findBestMatch
	import chimera
	from chimera import match

	method = findBestMatch(method, InterpolationMap.iterkeys())
	interpolateFunction = InterpolationMap[method]
	rMethod = findBestMatch(rMethod, RateMap.iterkeys())
	rateFunction = RateMap[rMethod]
	if cartesian:
		planFunction = InterpResidue.planCartesian
	else:
		planFunction = InterpResidue.planInternal

	rate = rateFunction(frames)
	numFrames = len(rate) + 1
	activeCS = mol.activeCoordSet
	csSize = len(mol.activeCoordSet.coords())
	baseCS = max(mol.coordSets.keys()) + 1
	segMap = {}
	plan = {}
	for seg in segments:
		rList0, rList1 = seg
		aList0 = getAtomList(rList0)
		aList1 = [ equivAtoms[a0] for a0 in aList0 ]
		c1 = chimera.Point([ a.coord() for a in aList1 ])
		segMap[seg] = (aList0, aList1, molXform.apply(c1))
		for r in rList0:
			plan[r] = planFunction(r)

	import numpy
	def coordsToPosition(atoms):
		return numpy.array([a.coord().data() for a in atoms])
	def xformCoordsToPosition(atoms):
		return numpy.array([molXform.apply(a.coord()).data()
							for a in atoms])
	lo = 0.0
	interval = 1.0
	for i in range(len(rate)):
		f = (rate[i] - lo) / interval
		lo = rate[i]
		interval = 1.0 - lo
		cs = mol.newCoordSet(baseCS + i, csSize)
		for seg in segments:
			aList0, aList1, c1 = segMap[seg]
			c = chimera.Point([ a.coord() for a in aList0 ])
			cList0 = coordsToPosition(aList0)
			cList1 = xformCoordsToPosition(aList1)
			xform, rmsd = match.matchPositions(cList1, cList0)
			xf, xf1 = interpolateFunction(xform, c, c1, f)
			xf1.multiply(molXform)
			rList0, rList1 = seg
			for r in rList0:
				InterpResidue.applyPlan(plan[r], r, cs, f,
						equivAtoms, xf, xf1)
		mol.activeCoordSet = cs
		if cb:
			cb(mol)
	cs = mol.newCoordSet(baseCS + len(rate), csSize)
	for a0, a1 in equivAtoms.iteritems():
		a0.setCoord(molXform.apply(a1.coord()), cs)
	mol.activeCoordSet = cs

def interpolateCorkscrew(xf, c0, c1, f):
	"""Interpolate by splitting the transformation into a rotation
	and a translation along the axis of rotation."""
	import chimera, math
	dc = c1 - c0
	vr, a = xf.getRotation()		# a is in degrees
	tra = dc * vr				# magnitude of translation
						# along rotation axis
	vt = dc - tra * vr			# where c1 would end up if
						# only rotation is used
	cm = c0 + vt / 2
	v0 = chimera.cross(vr, vt)
	if v0.sqlength() <= 0.0:
		ident = chimera.Xform.identity()
		return ident, ident
	v0.normalize()
	if a != 0.0:
		l = vt.length / 2 / math.tan(math.radians(a / 2))
		cr = (cm + v0 * l).toVector()
	else:
		cr = chimera.Vector(0.0, 0.0, 0.0)

	Tinv = chimera.Xform.translation(-cr)
	R0 = chimera.Xform.rotation(vr, a * f)
	R1 = chimera.Xform.rotation(vr, -a * (1 - f))
	X0 = chimera.Xform.translation(cr + vr * (f * tra))
	X0.multiply(R0)
	X0.multiply(Tinv)
	X1 = chimera.Xform.translation(cr - vr * ((1 - f) * tra))
	X1.multiply(R1)
	X1.multiply(Tinv)
	return X0, X1

def interpolateIndependent(xf, c0, c1, f):
	"""Interpolate by splitting the transformation into a rotation
	and a translation."""
	import chimera
	vr, a = xf.getRotation()		# a is in degrees
	xt = xf.getTranslation()
	Tinv = chimera.Xform.translation(-xt)
	T = chimera.Xform.translation(xt * f)
	X0 = chimera.Xform(T)
	X0.multiply(chimera.Xform.rotation(vr, a * f))
	X1 = chimera.Xform(T)
	X1.multiply(chimera.Xform.rotation(vr, -a * (1 - f)))
	X1.multiply(Tinv)
	return X0, X1

def interpolateLinear(xf, c0, c1, f):
	"""Interpolate by translating c1 to c0 linearly along with
	rotation about translation point."""
	import chimera
	vr, a = xf.getRotation()		# a is in degrees
	c0v = c0.toVector()
	c1v = c1.toVector()
	Tinv0 = chimera.Xform.translation(-c0v)
	Tinv1 = chimera.Xform.translation(-c1v)
	dt = c1 - c0
	R0 = chimera.Xform.rotation(vr, a * f)
	R1 = chimera.Xform.rotation(vr, -a * (1 - f))
	T = chimera.Xform.translation(c0v + dt * f)
	X0 = chimera.Xform(T)
	X0.multiply(R0)
	X0.multiply(Tinv0)
	X1 = chimera.Xform(T)
	X1.multiply(R1)
	X1.multiply(Tinv1)
	return X0, X1

InterpolationMap = {
	"corkscrew": interpolateCorkscrew,
	"independent": interpolateIndependent,
	"linear": interpolateLinear,
}

def rateLinear(frames):
	"Generate fractions from 0 to 1 linearly (excluding start/end)"
	return [ float(s) / frames for s in range(1, frames) ]

def rateSinusoidal(frames):
	"""Generate fractions from 0 to 1 sinusoidally
	(slow at beginning, fast in middle, slow at end)"""
	import math
	piOverTwo = math.pi / 2
	rate = []
	for s in rateLinear(frames):
		a = math.pi + s * math.pi
		v = math.cos(a)
		r = (v + 1) / 2
		rate.append(r)
	return rate

def rateRampUp(frames):
	"""Generate fractions from 0 to 1 sinusoidally
	(slow at beginning, fast at end)"""
	import math
	piOverTwo = math.pi / 2
	rate = []
	for s in rateLinear(frames):
		a = math.pi + s * piOverTwo
		v = math.cos(a)
		r = v + 1
		rate.append(r)
	return rate

def rateRampDown(frames):
	"""Generate fractions from 0 to 1 sinusoidally
	(fast at beginning, slow at end)"""
	import math
	piOverTwo = math.pi / 2
	rate = []
	for s in rateLinear(frames):
		a = s * piOverTwo
		r = math.sin(a)
		rate.append(r)
	return rate

RateMap = {
	"linear": rateLinear,
	"sinusoidal": rateSinusoidal,
	"ramp up": rateRampUp,
	"ramp down": rateRampDown,
}

if __name__ == "__main__":
	print rateLinear(10)
	print rateGeometric(10)
