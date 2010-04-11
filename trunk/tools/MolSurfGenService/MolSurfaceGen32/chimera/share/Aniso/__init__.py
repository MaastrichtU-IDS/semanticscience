# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2009 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: copyright 26655 2009-01-07 22:02:30Z gregc $


from chimera import replyobj, selection, Molecule, openModels, \
					triggers, Vector, Atom

_mgr = None
def mgr():
	global _mgr
	if _mgr == None:
		_mgr = AnisoManager()
	return _mgr

class AnisoManager:
	def removeAniso(self, targets):
		if isinstance(targets, dict):
			molMap = targets
		else:
			molMap = self._makeMolMap(targets)
		someShowing = bool(self._surfMap)
		for m, atoms in molMap.items():
			if m not in self._surfMap:
				continue
			surfMap = self._surfMap[m]
			for a in atoms:
				try:
					pieceInfo = surfMap[a]
				except KeyError:
					continue
				if not a.__destroyed__:
					a.labelOffset = None
				for key, pieces in pieceInfo.items():
					if key == "anisoParams" or not pieces:
						continue
					for piece in pieces:
						piece.model.removePiece(piece)
				del surfMap[a]
				del self._atomMolLookup[a]
			if len(surfMap) == 1:
				openModels.close([surfMap.pop("model")])
				del self._surfMap[m]
		if someShowing and not self._surfMap:
			triggers.deleteHandler('Atom', self._handlerID)


	def showAniso(self, targets, color=None, scale=1.0, smoothing=1,
				showEllipsoid=True, ellipsoidTransparency=None,
				axisColor=None, axisFactor=None, axisThickness=0.01,
				ellipseColor=None, ellipseFactor=None, ellipseThickness=0.02):
		"""targets can be an iterable of atoms or molecules

		   color of None means match the atom color.
		   showing outer ellipsoid controlled with 'showEllipsoid'
		   if 'ellipsoidTransparency' is not None, then the color's
		     transparency is set to that fraction.
		   'axisFactor' is a multiplicative factor of how long the displayed
		     axes lengths are versus the ellipsoid axes.  If 'axisFactor'
			 is None then no axes are displayed.
		   'ellipseFactor' is similar to 'axisFactor', but for the major
		     ellipses.
		"""
		molMap = self._makeMolMap(targets)
		self.removeAniso(molMap)
		noneShowing = not self._surfMap
		newlyShown = 0
		for m, atoms in molMap.items():
			if not m.display:
				continue
			surfMap = self._surfMap.setdefault(m, {})
			if surfMap:
				model = surfMap["model"]
			else:
				import _surface
				model = _surface.SurfaceModel()
				surfMap["model"] = model
				openModels.add([model], sameAs=m, hidden=True)
			for a in atoms:
				if not a.display or a.hide:
					continue
				if not hasattr(a, "anisoU"):
					continue
				noneColor = a.color
				if noneColor is None:
					noneColor = a.molecule.color
				if showEllipsoid:
					if color is None:
						_ellipsoidColor = noneColor
					else:
						_ellipsoidColor = color
				else:
					_ellipsoidColor = None
				if axisFactor is None:
					_axisColor = None
				elif axisColor is None:
					_axisColor = noneColor
				else:
					_axisColor = axisColor
				if ellipseFactor is None:
					_ellipseColor = None
				elif ellipseColor is None:
					_ellipseColor = noneColor
				else:
					_ellipseColor = ellipseColor
				surfMap[a] = self._makePieces(model, a, (_ellipsoidColor,
					_axisColor, _ellipseColor), ellipsoidTransparency, scale,
					smoothing, axisFactor, ellipseFactor, axisThickness,
					ellipseThickness)
				newlyShown += 1
				# can't look up 'molecule' in deleted atoms,
				# so remember it...
				self._atomMolLookup[a] = a.molecule
		if noneShowing and self._surfMap:
			self._handlerID = triggers.addHandler('Atom',
							self._atomCB, None)
		return newlyShown

	def __init__(self):
		self._surfMap = {}
		self._atomMolLookup = {}
		self._cylinderCache = {}
		from SimpleSession import SAVE_SESSION
		triggers.addHandler(SAVE_SESSION, self._sessionSaveCB, None)

	def _atomCB(self, trigName, myData, trigData):
		if trigData.deleted:
			self.removeAniso(trigData.deleted)

	def _makeMolMap(self, targets):
		molMap = {}
		for target in targets:
			if isinstance(target, Molecule):
				molMap.setdefault(target, []).extend(
								target.atoms)
			else:
				if target.__destroyed__:
					try:
						m = self._atomMolLookup[target]
					except KeyError:
						# no surface for destroyed
						# atom
						continue
				else:
					m = target.molecule
				molMap.setdefault(m, []).append(target)
		return molMap

	def _makePieces(self, model, atom, colors, ellipsoidTransparency,
					scale, smoothing, axisFactor, ellipseFactor,
					axisThickness, ellipseThickness):
		rgbas = []
		for color in colors:
			if color is None:
				rgba = None
			elif hasattr(color, 'rgba'):
				rgba = color.rgba()
			else:
				rgba = color
			rgbas.append(rgba)
		ellipsoidColor, axisColor, ellipseColor = rgbas
		if ellipsoidTransparency is not None and ellipsoidColor:
			ellipsoidColor = ellipsoidColor[:-1] + (1.0-ellipsoidTransparency,)

		from numpy.linalg import svd
		ignore, lengths, axes = svd(atom.anisoU)
		from numpy import dot, sqrt
		lengths2 = sqrt(lengths)
		lengths2 *= scale

		pieceInfo = {"anisoParams": (scale, smoothing,
				axisFactor, ellipseFactor, axisThickness, ellipseThickness)}

		if ellipsoidColor is None:
			pieceInfo["ellipsoid"] = None
		else:
			from Icosahedron import icosahedron_triangulation
			varray, tarray = icosahedron_triangulation(
				subdivision_levels = smoothing, sphere_factor = 1.0)
			ee = varray * lengths2
			ev = dot(ee, axes)
			ev += atom.coord()
			piece = model.addPiece(ev, tarray, ellipsoidColor)
			pieceInfo["ellipsoid"] = [piece]

		if axisColor is None:
			pieceInfo["axes"] = None
		else:
			pieceInfo["axes"] = pieces = []
			for axis in range(3):
				from numpy import array
				axisFactors = array([axisThickness]*3)
				axisFactors[axis] = axisFactor * lengths2[axis]
				ee = cubeVertices * axisFactors
				ev = dot(ee, axes)
				ev += atom.coord()
				pieces.append(model.addPiece(ev, cubeTriangles, axisColor))

		if ellipseColor is None:
			pieceInfo["ellipses"] = None
		else:
			pieceInfo["ellipses"] = pieces = []
			if smoothing not in self._cylinderCache:
				from Shape.shapecmd import cylinder_divisions, cylinder_geometry
				nz, nc = cylinder_divisions(1.0, 1.0,
												9 * (2**smoothing))
				self._cylinderCache[smoothing] = cylinder_geometry(
										1.0, 1.0, nz, nc, True)
			ellipseVertices, ellipseTriangles = self._cylinderCache[smoothing]
			for axis in range(3):
				from numpy import array
				verts = ellipseVertices.copy()
				if axis < 2:
					verts[:,axis], verts[:,2] = \
							ellipseVertices[:,2], ellipseVertices[:,axis]
				ellipseLengths = lengths2.copy() * ellipseFactor
				ellipseLengths[axis] = ellipseThickness
				ee = verts * ellipseLengths
				ev = dot(ee, axes)
				ev += atom.coord()
				pieces.append(
					model.addPiece(ev, ellipseTriangles, ellipseColor))

		long = max(lengths2)
		atom.labelOffset = (long, 0.0, 0.0)
		return pieceInfo

	def _restoreSession(self, targetMap, version=1):
		from SimpleSession import idLookup
		if version == 1:
			for info, atomIDs in targetMap.items():
				rgba, anisoParams = info
				scale, smoothing = anisoParams
				self.showAniso([idLookup(atomID) for atomID in atomIDs],
					color=rgba, scale=scale, smoothing=smoothing)
			return
		if version == 2:
			for info, atomIDs in targetMap.items():
				anisoParams, colors = info
				scale, smoothing, axisFactor = anisoParams
				ellipsoidColor, axisColor, ellipseColor = colors
				if ellipseColor:
					ellipseFactor = 1.0
				else:
					ellipseFactor = None
				self.showAniso([idLookup(atomID) for atomID in atomIDs],
					color=ellipsoidColor, showEllipsoid=ellipsoidColor,
					axisColor=axisColor, axisFactor=axisFactor,
					ellipseColor=ellipseColor, ellipseFactor=ellipseFactor,
					scale=scale, smoothing=smoothing)
			return
		if version == 3:
			for info, atomIDs in targetMap.items():
				anisoParams, colors = info
				scale, smoothing, axisFactor, ellipseFactor = anisoParams
				ellipsoidColor, axisColor, ellipseColor = colors
				self.showAniso([idLookup(atomID) for atomID in atomIDs],
					color=ellipsoidColor, showEllipsoid=ellipsoidColor,
					axisColor=axisColor, axisFactor=axisFactor,
					ellipseColor=ellipseColor, ellipseFactor=ellipseFactor,
					scale=scale, smoothing=smoothing)
			return
		for info, atomIDs in targetMap.items():
			anisoParams, colors = info
			scale, smoothing, axisFactor, ellipseFactor, \
				axisThickness, ellipseThickness = anisoParams
			ellipsoidColor, axisColor, ellipseColor = colors
			self.showAniso([idLookup(atomID) for atomID in atomIDs],
				color=ellipsoidColor, showEllipsoid=ellipsoidColor,
				axisColor=axisColor, axisFactor=axisFactor,
				axisThickness=axisThickness, ellipseColor=ellipseColor,
				ellipseFactor=ellipseFactor, ellipseThickness=ellipseThickness,
				scale=scale, smoothing=smoothing)
			
	def _sessionSaveCB(self, trigName, myData, sessionFile):
		from SimpleSession import sesRepr, sessionID
		targetMap = {}
		for surfMap in self._surfMap.values():
			for atom, pieceMap in surfMap.items():
				if not isinstance(atom, Atom):
					continue
				colors = []
				for geom in ["ellipsoid", "axes", "ellipses"]:
					if pieceMap.get(geom, None):
						color = pieceMap[geom][0].color
					else:
						color = None
					colors.append(color)
				targetMap.setdefault((pieceMap["anisoParams"],
					tuple(colors)), []).append(sessionID(atom))
		print>>sessionFile, "targetMap = %s" % sesRepr(targetMap)
		print>>sessionFile, """
try:
	import Aniso
	Aniso.mgr()._restoreSession(targetMap, version=4)
except:
	reportRestoreError("Error restoring thermal ellipsoids")
"""


def aniso(targets=None, color=None, smoothing=3, scale=1.0,
		showEllipsoid=True, transparency=None,
		axisFactor=None, axisColor=None, axisThickness=0.01,
		ellipseFactor=None, ellipseColor=None, ellipseThickness=0.02):
	from Midas import MidasError
	if targets is None:
		targets = openModels.list(modelTypes=[Molecule])
	if smoothing < 1:
		raise MidasError("'smoothing' must be at least 1")
	if transparency is not None:
		try:
			transparency /= 100.0
			if transparency < 0.0 or transparency > 1.0:
				raise TypeError("out of range")
		except TypeError:
			raise MidasError(
				"transparency must be a number between zero and one")
	numShown = mgr().showAniso(targets, color=color,
		smoothing=smoothing, scale=scale,
		showEllipsoid=showEllipsoid, ellipsoidTransparency=transparency,
		axisFactor=axisFactor, axisColor=axisColor, axisThickness=axisThickness,
		ellipseColor=ellipseColor, ellipseFactor=ellipseFactor,
		ellipseThickness=ellipseThickness)
	if not numShown:
		raise MidasError("No atoms chosen or none had anisotropic"
							" information")


def unaniso(targets=None):
	if targets is None:
		targets = openModels.list(modelTypes=[Molecule])
	mgr().removeAniso(targets)

def prob2scale(prob):
	if prob < 0.0 or prob >= 1.0:
		raise ValueError("probability must be >= 0.0 and < 1.0")
	if prob == 0.0:
		return 0.0
	return _prob2scale(prob)

from math import pi, sqrt, exp
def integrand(val):
	val2 = val * val
	return val2 * exp(-val2/2.0)

def integral(val, constant=sqrt(2.0/pi)):
	from CGLutil.integral import simpson
	return constant * simpson(integrand, 0, val, n=70)

def _prob2scale(targetProb, lowBound=None, highBound=None, converge=0.0001):
	if lowBound == None and highBound == None:
		val = 1.0
	elif lowBound == None:
		val = highBound / 2.0
	elif highBound == None:
		val = lowBound * 2.0
	else:
		val = (lowBound + highBound) / 2.0
	prob = integral(val)
	if prob < targetProb:
		lowBound = val
	else:
		highBound = val
	if lowBound and highBound and highBound - lowBound < converge:
		return (highBound + lowBound) / 2.0
	return _prob2scale(targetProb, lowBound, highBound, converge)

from numpy import array, single, intc
cubeVertices = array([
	(1.0, 1.0, 1.0), (1.0, 1.0, -1.0),
	(1.0, -1.0, 1.0), (1.0, -1.0, -1.0),
	(-1.0, 1.0, 1.0), (-1.0, 1.0, -1.0),
	(-1.0, -1.0, 1.0), (-1.0, -1.0, -1.0)], single)

# counter-clockwise == normals face out
cubeTriangles = array([
	(2,1,0), (3,1,2), (0,1,5), (0,5,4), (0,4,2), (2,4,6),
	(1,3,5), (3,7,5), (3,2,7), (2,6,7), (4,5,7), (4,7,6)], intc)
