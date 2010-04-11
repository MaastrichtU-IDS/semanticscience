# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 29426 2009-11-24 01:28:29Z pett $

""" Emulate UCSF Midas command set """

import sys
import math
import tempfile
import os

import chimera
if not chimera.nogui:
	import chimera.tkgui
from chimera import selection, dialogs
from chimera import elements
from chimera import replyobj
from chimera import misc
from chimera.colorTable import getColorByName
from StructMeasure import DistMonitor

class MidasError(Exception):
	pass

def _showStatus(s, **kw):
	if "log" not in kw:
		kw['log'] = True
	replyobj.status('%s\n' % s, **kw)

def evalSpec(spec):
	try:
		from chimera import specifier
		return specifier.evalSpec(spec)
	except:
		raise MidasError, "mangled atom specifier"

#
# Internal functions that return items of interest
#
def _selectedModels(sel, modType=chimera.Molecule):
	if isinstance(sel, basestring):
		sel = evalSpec(sel)
	elif isinstance(sel, (list, tuple, set)):
		return sel
	graphs = sel.graphs()
	return filter(lambda g, t=modType: isinstance(g, t), graphs)

def _selectedResidues(sel):
	if isinstance(sel, basestring):
		sel = evalSpec(sel)
	elif isinstance(sel, (list, tuple)):
		if sel:
			if isinstance(sel[0], chimera.Molecule):
				nsel = []
				for m in sel:
					nsel.extend(m.residues)
				sel = nsel
			elif isinstance(sel[0], chimera.Atom):
				residues = set()
				for a in sel:
					residues.add(a.residue)
				sel = list(residues)
		return sel
	elif isinstance(sel, set):
		return sel
	return sel.residues()

def _selectedAtoms(sel, ordered=False, asDict=False):
	if isinstance(sel, basestring):
		sel = evalSpec(sel)
	elif isinstance(sel, (list, tuple)):
		if sel and isinstance(sel[0],
					(chimera.Molecule, chimera.Residue)):
			nsel = []
			for m in sel:
				nsel.extend(m.atoms)
			sel = nsel
		if asDict:
			return dict.fromkeys(sel)
		return sel
	elif isinstance(sel, set):
		return sel
	if isinstance(sel, selection.ItemizedSelection):
		return sel.atoms(ordered=ordered, asDict=asDict)
	return sel.atoms(asDict=asDict)

def _selectedBonds(sel, internal=True):
	return misc.bonds(_selectedAtoms(sel), internal=internal)

def _selectedPseudobonds(sel):
	seenOnce = set()
	seenTwice = set()
	for a in _selectedAtoms(sel):
		pbs = set(a.pseudoBonds)
		seenTwice |= (seenOnce & pbs)
		seenOnce |= pbs
	return seenTwice

def _selectedPseudobondGroups(sel):
	groups = set()
	for pb in _selectedPseudobonds(sel):
		groups.add(pb.pseudoBondGroup)
	return groups

def _selectedSurfacePieces(sel):
	if isinstance(sel, (list, tuple, set)):
		nsel = []
		from _surface import SurfacePiece, SurfaceModel
		for s in sel:
			if isinstance(s, SurfacePiece):
				nsel.append(s)
			elif isinstance(s, SurfaceModel):
				nsel.extend(s.surfacePieces)
		return nsel
	if isinstance(sel, basestring):
		sel = evalSpec(sel)
	if isinstance(sel, selection.Selection):
		import Surface
		return Surface.selected_surface_pieces(sel)
	return []

#
# Internal functions that operate on given selection
#
def _editAtom(sel, funcs):
	atoms = _selectedAtoms(sel)
	if isinstance(funcs, (list, tuple)):
		for a in atoms:
			for f in funcs:
				f(a)
	else:
		for a in atoms:
			funcs(a)
	return atoms

def _editAtomBond(sel, aFunc, bFunc, internal=False):
	atoms = _selectedAtoms(sel)
	if aFunc:
		for a in atoms:
			aFunc(a)
	if bFunc:
		for b in misc.bonds(atoms, internal=internal):
			bFunc(b)

def _editResidue(sel, func):
	residues = _selectedResidues(sel)
	for res in residues:
		func(res)

def _editMolecule(sel, func):
	graphs = _selectedModels(sel)
	for g in graphs:
		func(g)

def _editModel(sel, func):
	graphs = _selectedModels(sel, modType=object)
	for g in graphs:
		func(g)

#
# Internal functions that support motion commands
#
_motionHandlers = []
def _addMotionHandler(func, param):
	if not isinstance(param['frames'], int):
		raise MidasError("'frames' must be an integer")
	h = chimera.triggers.addHandler('new frame', func, param)
	param['handler'] = h
	_motionHandlers.append(param)

def _removeMotionHandler(param):
	try:
		_motionHandlers.remove(param)
		chimera.triggers.deleteHandler('new frame', param['handler'])
		param['handler'] = None  # break cycle
	except KeyError:
		pass

def _clearMotionHandlers():
	global _motionHandlers
	for param in _motionHandlers:
		chimera.triggers.deleteHandler('new frame', param['handler'])
		param['handler'] = None  # break cycle
	_motionHandlers = []

def _motionRemaining():
	frames = 0
	for param in _motionHandlers:
		f = param['frames']
		if f > 0 and f > frames:
			frames = f
	return frames

def _tickMotionHandler(param):
	if param['frames'] > 0:
		param['frames'] = param['frames'] - 1
		if param['frames'] == 0:
			_removeMotionHandler(param)
	elif not chimera.openModels.list():
		_removeMotionHandler(param)

def _movement(trigger, param, triggerData):
	if trigger:
		_tickMotionHandler(param)
	_moveModels(param['xform'], param.get('coordinateSystem',None),
		    param.get('models',None), param.get('center',None))

def _flight(trigger, param, triggerData):
	if trigger:
		_tickMotionHandler(param)
	counter = param['counter']
	xfList = param['xformList']
	_moveModels(xfList[counter], param.get('coordinateSystem',None),
		    param.get('models',None), param.get('center',None))
	counter = counter + param['direction']
	if counter < 0 or counter >= len(xfList):
		mode = param['mode']
		if mode == 'cycle':
			counter = 0
		elif mode == 'bounce':
			if counter < 0:
				counter = 1
				param['direction'] = 1
			else:
				counter = len(xfList) - 2
				param['direction'] = -1
		else:
			_removeMotionHandler(param)
	param['counter'] = counter

def _moveModels(xf, coordsys_open_state, models, center):
	if coordsys_open_state:
		cxf = coordsys_open_state.xform
		from chimera import Xform
		rxf = Xform.translation(-cxf.getTranslation())
		rxf.multiply(cxf)
		axf = Xform()
		for x in (rxf, xf, rxf.inverse()):
			axf.multiply(x)
		# Reorthogonalize for stability when coordinate frame rotating
		axf.makeOrthogonal(True)
		xf = axf
		if center:
			center = cxf.apply(center)
	from chimera import openModels as om
	if models is None and center is None:
		om.applyXform(xf)
	else:
		if models is None:
			models = [m for m in om.list() if m.openState.active]
		for os in set([m.openState for m in models
			       if not m.__destroyed__]):
			_moveOpenState(os, xf, center)

def _moveOpenState(os, xf, center):
	# Adjust transform to act about center of rotation.
	from chimera import openModels as om, Xform
	if center:
		c = center
	elif om.cofrMethod == om.Independent:
		c = os.xform.apply(os.cofr)
	else:
		c = om.cofr
	cxf = Xform.translation(c.x, c.y, c.z)
	cxf.multiply(xf)
	cxf.multiply(Xform.translation(-c.x, -c.y, -c.z))
	os.globalXform(cxf)

def _clip(trigger, param, triggerData):
	if trigger:
		_tickMotionHandler(param)
	delta = param['delta']
	v = chimera.viewer
	camera = v.camera
	if param['plane'][0] == 'h':
		dnear, dfar = (delta, 0)
	elif param['plane'][0] == 'y':
		dnear, dfar = (0, delta)
	elif param['plane'][0] == 't':
		dnear, dfar = (delta, -delta)
	elif param['plane'][0] == 's':
		dnear, dfar = (delta, delta)
	v.clipping = True
	oldnear, oldfar = getattr(camera, 'nearFar')
	if oldnear + dnear <= oldfar + dfar:
		raise MidasError('Near clip plane moved behind (%.3g) far clip plane (%.3g).' % (oldnear + dnear, oldfar + dfar))
	camera.nearFar = (oldnear + dnear, oldfar + dfar)

def _rotation(trigger, param, triggerData):
	if trigger:
		_tickMotionHandler(param)
	rot = param['rot']
	if rot.bondRot.__destroyed__:
		return
	rot.increment(param['adjust'])

def _scale(trigger, param, triggerData):
	if trigger:
		_tickMotionHandler(param)
	viewer = chimera.viewer
	try:
		viewer.scaleFactor = viewer.scaleFactor * param['scaleFactor']
	except ValueError:
		raise chimera.LimitationError("refocus to continue scaling")

def _wait(trigger, param, triggerData):
	_tickMotionHandler(param)

def _degrees(a):
	return a / math.pi * 180

def _axis(a):
	if isinstance(a, basestring):
		if a == 'x':
			return chimera.Vector(1, 0, 0)
		elif a == 'y':
			return chimera.Vector(0, 1, 0)
		elif a == 'z':
			return chimera.Vector(0, 0, 1)
	elif isinstance(a, (list, tuple)):
		if len(a) == 3:
			return chimera.Vector(a[0], a[1], a[2])
	return a

#
# Miscellaneous internal functions
#

def _centerOf(aList):
	pts = [a.xformCoord() for a in aList]
	valid, sph = chimera.find_bounding_sphere(pts)
	return sph.center

def _crossProduct(a, b):
	x = a[1] * b[2] - a[2] * b[1]
	y = a[2] * b[0] - a[0] * b[2]
	z = a[0] * b[1] - a[1] * b[0]
	return [x, y, z]

def _dotProduct(a, b):
	return a[0] * b[0] + a[1] * b[1] + a[2] * b[2]

def _normalize(a):
	l = _dotProduct(a, a)
	if l > 0:
		l = math.sqrt(l)
		a[0] = a[0] / l
		a[1] = a[1] / l
		a[2] = a[2] / l

_labelInfo = "name"

_colorEditorSynonyms = ['colorpanel', 'fromeditor', 'editor']
def convertColor(color):
	if isinstance(color, basestring):
		if color in _colorEditorSynonyms:
			from CGLtk.color import ColorWell
			if not ColorWell._colorPanel:
				from chimera import UserError
				dialogs.display("color editor")
				raise UserError('Choose color in panel first')
			c = chimera.MaterialColor()
			rgba = ColorWell.colorPanel().rgba
			c.ambientDiffuse = rgba[:-1]
			c.opacity = rgba[-1]
		elif color.lower() == "none":
			c = None
		elif color.lower() == "byatom":
			c = "byatom"
		else:
			try:
				# Chimera color name.
				c = getColorByName(color)
			except KeyError:
				try:
					# Tk color name.
					from chimera.tkgui import app
					rgb16 = app.winfo_rgb(color)
					rgb = [c/65535.0 for c in rgb16]
					c = chimera.MaterialColor(*rgb)
				except:
					try:
						# Comma separated list of rgb or rgba float values.
						rgba = [float(c) for c in color.split(',')]
						c = chimera.MaterialColor(*rgba)
					except:
						from chimera import UserError
						raise UserError('Color "%s" is undefined'
								% color)
	elif color is None or isinstance(color, chimera.Color):
		c = color
	else:
		raise RuntimeError, 'need a color'
	return c

ColorSuffixes = (',a', ',b', ',r', ',f', ',s', ',v', ',l', ',la', ',al', ',lr', ',rl')

def _colorSplit(color):
	ci = min([color.find(r) for r in ColorSuffixes if r in color] + [len(color)])
	cname = color[:ci]
	if color[ci+1:]:
		citems = color[ci+1:].split(",")
	else:
		citems = []
	atomItems, resItems = _colorItems(citems)
	return cname, atomItems, resItems

def _colorItems(parts):
	if not parts:
		return (["color", "labelColor", "vdwColor", "surfaceColor"],
				["labelColor", "ribbonColor", "fillColor"])

	atomItems = []
	resItems = []
	for itemChar in parts:
		if itemChar == "s":
			atomItems.append("surfaceColor")
		elif itemChar == "l":
			atomItems.append("labelColor")
			resItems.append("labelColor")
		elif itemChar in "ab":
			atomItems.append("color")
		elif itemChar == "v":
			atomItems.append("vdwColor")
		elif itemChar =="r":
			resItems.append("ribbonColor")
		elif itemChar =="f":
			resItems.append("fillColor")
		elif itemChar in ["al", "la"]:
			atomItems.append("labelColor")
		elif itemChar in ["rl", "lr"]:
			resItems.append("labelColor")
		elif itemChar == "c":
			raise MidasError(
				'Color wheel interpolations not supported')
		else:
			raise MidasError('Unknown color specifier "%s"'
						' encountered' % itemChar)
	return atomItems, resItems

def _savePosition():
	from chimera import openModels as om, viewer
	xforms = {}
	for molId in om.listIds():
		xforms[molId] = om.openState(*molId).xform
	from chimera.misc import KludgeWeakWrappyDict
	clips = KludgeWeakWrappyDict("Model")
	for m in om.list():
		clips[m] = (m.useClipPlane, m.clipPlane, m.useClipThickness,
							m.clipThickness)
	if om.cofrMethod == om.Independent:
		cofr = (0, 0, 0)
	else:
		cofr = tuple(om.cofr)
	cam = viewer.camera
	return (
		viewer.scaleFactor,
		viewer.viewSize,
		cam.center,
		cam.nearFar,
		cam.focal,
		xforms,
		clips,
		om.cofrMethod,
		cofr,
		viewer.clipping
	)

def _restorePosition(trigger, param, triggerData):
	if trigger:
		_tickMotionHandler(param)
	pos = param['position']
	cofrMethod = None
	clips = {}
	clipping = True
	if len(pos) == 10:
		scale, view, center, nearFar, focal, xforms, clips, \
					cofrMethod, cofr, clipping = pos
	elif len(pos) == 9:
		scale, view, center, nearFar, focal, xforms, clips, \
					cofrMethod, cofr = pos
	elif len(pos) == 7:
		scale, view, center, nearFar, focal, xforms, clips = pos
	else:
		scale, view, center, nearFar, focal, xforms = pos

	v = chimera.viewer
	cam = v.camera
	from chimera import openModels as om
	# have currently open models not in the position keep their
	# orientation relative to the lowest open model...
	missing = []
	fromXF = toXF = lowID = None
	for molID in om.listIds():
		if molID in xforms:
			if lowID == None or molID < lowID:
				lowID = molID
				fromXF = om.openState(*molID).xform
				toXF = xforms[molID]
		else:
			missing.append(molID)
	if missing and fromXF:
		for molID in missing:
			xf = om.openState(*molID).xform
			xf.multiply(fromXF.inverse())
			xf.multiply(toXF)
			xforms[molID] = xf

	if param['frames'] == 0:
		# make sure we finish
		# (should be the same as setting the rate to 1)
		if cofrMethod != None:
			om.cofrMethod = cofrMethod
			if om.cofrMethod == chimera.OpenModels.Independent:
				om.cofr = chimera.Point(*cofr)
		v.scaleFactor = scale
		v.viewSize = view
		v.clipping = clipping
		cam.center = center
		cam.nearFar = nearFar
		cam.focal = focal
		for molId, xf in xforms.items():
			try:
				om.openState(*molId).xform = xf
			except ValueError:
				# model's gone, oh well...
				continue
		for m, clipInfo in clips.items():
			useClip, plane, useThickness, thickness = clipInfo
			m.useClipPlane = useClip
			m.clipPlane = plane
			m.useClipThickness = useThickness
			m.clipThickness = thickness
		return
	mode = param['mode']
	if mode == 'geometric':
		# TODO: revise so we don't over/under shoot 1
		duration = param['duration']
		rate = .5 / pow(duration, 1./duration)
	elif mode == 'halfstep':
		rate = .5
	else:
		# mode == 'linear' (default)
		rate = 1.0 / (param['frames'] + 1)
	if cofrMethod == om.cofrMethod \
	and om.cofrMethod != chimera.OpenModels.Independent:
		cofrPoint = chimera.Point(*cofr)
		curCofr = om.cofr
		newCofr = curCofr + (cofrPoint - curCofr) * rate
		om.cofr = chimera.Point(*newCofr)
	v.scaleFactor += (scale - v.scaleFactor) * rate
	v.viewSize += (view - v.viewSize) * rate
	curCenter = chimera.Point(*cam.center)
	center = chimera.Point(*center)
	newCenter = curCenter + (center - curCenter) * rate
	cam.center = tuple(newCenter)
	if v.clipping or clipping:
		v.clipping = True
		near, far = cam.nearFar
		cam.nearFar = near + (nearFar[0] - near) * rate, \
					far + (nearFar[1] - far) * rate
	cam.focal += (focal - cam.focal) * rate
	for m, clipInfo in clips.items():
		useClip, plane, useThickness, thickness = clipInfo
		if useClip and m.useClipPlane:
			# avoid modifying copy of clip plane...
			curPlane = m.clipPlane
			curPlane.origin += (plane.origin - curPlane.origin)*rate
			curPlane.normal += (plane.normal - curPlane.normal)*rate
			m.clipPlane = curPlane
			if m.useClipThickness == useThickness:
				m.clipThickness += (thickness
						- m.clipThickness) * rate
			else:
				m.useClipThickness = useThickness
				m.clipThickness = thickness
		else:
			m.useClipPlane = useClip
			m.clipPlane = plane
			m.useClipThickness = useThickness
			m.clipThickness = thickness
	_moveModelsPartWay(xforms, rate)

def _moveModelsPartWay(xforms, rate):
	for openState, xform, c in _motionCenters(xforms):
		# Determine translation
		xf = openState.xform
		r = xf.inverse()
		r.premultiply(xform)
		curCofr = c
		finalCofr = r.apply(c)
		wantCofr = curCofr + (finalCofr - curCofr) * rate
		td = chimera.Xform.translation(wantCofr - curCofr)

		# Determine rotation
		axis, angle = r.getRotation()
		rd = chimera.Xform.rotation(axis, angle * rate)

		cv = chimera.Xform.translation(curCofr - chimera.Point())
		cvi = chimera.Xform.translation(chimera.Point() - curCofr)

		nextXf = chimera.Xform.identity()
		nextXf.multiply(xf)	# Apply start transform
		nextXf.premultiply(cvi)	# Shift to put cofr at origin
		nextXf.premultiply(rd)	# Apply fractional rotation
		nextXf.premultiply(cv)	# Shift cofr back
		nextXf.premultiply(td)	# Apply fractional translation

		openState.xform = nextXf

#
# Group openStates that require the same xform to get to their destination.
# Compute center of bounding sphere for each group.
#
def _motionCenters(xforms):
	xox = {}
	oxc = []
	for molId, xform in xforms.items():
		try:
			os = chimera.openModels.openState(*molId)
		except ValueError:
			continue			# deleted model
		xf = os.xform.inverse()
		xf.premultiply(xform)
		for x in xox.keys():
			if _closeXforms(x,xf):
				xf = x
				break
		if xf in xox:
			xox[xf].append((os,xform))
		else:
			xox[xf] = [(os,xform)]
	for osxlist in xox.values():
		gs = None
		for os, xform in osxlist:
			have, s = os.bsphere()
			if have:
				s.xform(os.xform)
				if gs is None:
					gs = s
				else:
					gs.merge(s)
		if not gs is None:
			c = gs.center
			oxc.extend([(os, xform, c) for os, xform in osxlist])
	return oxc

def _closeXforms(xf1, xf2, angleTol = 0.1, shiftTol = 0.001):
	xf = chimera.Xform()
	xf.premultiply(xf1)
	xf.premultiply(xf2.inverse())
	axis, angle = xf.getRotation()
	close = (xf.getTranslation().length <= shiftTol and
		 angle <= angleTol)
	return close
	
#
# Actual exported functions (in alphabetical order)
#

def addaa(args):
	"""add an amino acid to the last residue in a chain"""
	import addAA
	from addAA import addAA, AddAAError

	arg_list = args.split(" ", 1)

	if not len(arg_list) == 2:
		raise MidasError, "Invalid number of arguments."
		
	rest_of_args = arg_list[0]

	## atom spec of residue to which new residue will be appended
	res_spec = arg_list[1]
	residues = _selectedResidues(res_spec)
	if len(residues) != 1:
		raise MidasError, "Exactly one residue must be selected. " \
		      "'%s' specifies %d residues." % (res_spec, len(residues))
		
	else:
		(last_residue,) = residues
	
	some_args = rest_of_args.split(",")
	if len(some_args) < 2:
		raise MidasError, "Not enough arguments. " \
		      "Require at least 'residue type' and 'residue sequence'"

	else:
		if not some_args[0].isalpha():
			raise MidasError,"Missing residue type argument"
		else:
			res_type = str(some_args[0])

		res_seq = some_args[1]
		if res_seq.isalpha():
			raise MidasError,"Missing residue sequence argument"
	        
		if len(some_args)  == 2:
			conf = None
		elif len(some_args) == 3:
			conf = some_args[2]
		elif len(some_args) == 4:
			phi,psi = some_args[2:4]
			if (phi.isalpha() or psi.isalpha()):
				raise MidasError, "Require either both phi and psi arguments or neither"
			conf = (phi,psi)
		elif len(some_args) > 4:
			raise MidasError, "Too many arguments"
	
	try:
		addAA(res_type, res_seq, last_residue, conformation=conf)
	except AddAAError, what:
		raise MidasError, "%s" % what
	else:
		_showStatus("Successfully added new amino acid \"%s\"" % res_type)


def align(sel, sel2=None):
	if sel2 == None:
		try:
			atoms = _selectedAtoms(sel, ordered=True)
		except MidasError:
			# sel might be two specs instead of one...
			if sel.count(' ') == 1:
				sel1, sel2 = sel.split(' ')
		else:
			if len(atoms) == 2:
				frontPt = atoms[0].xformCoord()
				backPt = atoms[1].xformCoord()
				centering = atoms[:1]
			elif sel.count(' ') == 1:
				sel1, sel2 = sel.split(' ')
		if sel2 == None and len(atoms) != 2:
			raise MidasError('Exactly two atoms must be selected'
				' by atom spec or two atom specs provided.')
	else:
		sel1 = sel
	if sel2 != None:
		atoms1 = _selectedAtoms(sel1)
		atoms2 = _selectedAtoms(sel2)
		if not atoms1:
			raise MidasError("Left atom spec (%s) selects no atoms"
								% sel1)
		if not atoms2:
			raise MidasError("Right atom spec (%s) selects no atoms"
								% sel2)
		frontPt = chimera.Point([a.xformCoord() for a in atoms1])
		backPt = chimera.Point([a.xformCoord() for a in atoms2])
		centering = atoms1
	xf = chimera.Xform.zAlign(backPt, frontPt)
	for molId in chimera.openModels.listIds():
		openState = chimera.openModels.openState(*molId)
		if openState.active:
			openState.globalXform(xf)
	cp = chimera.Point([a.xformCoord() for a in centering])
	v = chimera.viewer
	camera = v.camera
	nearFar = camera.nearFar
	halfSize = abs(nearFar[0] - nearFar[1]) / 2.0
	v.clipping = True
	camera.nearFar = cp.z + halfSize, cp.z - halfSize
	camera.focal = cp.z
	camera.center = (cp.x, cp.y, cp.z)

def angle(sel='sel', objIDs=None):
	"""Report angle between three or four atoms, or two objects"""
	if objIDs:
		from StructMeasure.Geometry import geomManager
		items = geomManager.items
		objs = []
		for objID in objIDs:
			try:
				objs.append([item for item in items if item.id == objID][0])
			except IndexError:
				raise MidasError("No such object: %s" % objID)

		val = geomManager.angle(objs)
		name1, name2 = [obj.id for obj in objs]
		_showStatus("Angle between %s and %s is %.3f" % (name1, name2, val))
		return val
	atoms = _selectedAtoms(sel, ordered=True)
	osl = ' '.join(map(lambda a: a.oslIdent(), atoms))
	points = tuple(map(lambda a: a.xformCoord(), atoms))
	if len(points) == 3:
		from chimera import angle
		val = angle(*points)
		_showStatus("Angle %s: %g" % (osl, val))
		return val
	if len(points) == 4:
		from chimera import dihedral
		val = dihedral(*points)
		_showStatus("Dihedral %s: %g" % (osl, val))
		return val
	raise MidasError('Three or four atoms must be selected.  You '
			'selected %d.' % len(atoms))

def aromatic(style=None, sel='sel'):
	molecules = _selectedModels(sel)
	if style is None:
		for m in molecules:
			m.aromaticDisplay = True
		return
	if style == 'off':
		return unaromatic(sel)
	if style == 'circle':
		mode = chimera.Molecule.Circle
	elif style == 'disk':
		mode = chimera.Molecule.Disk
	elif style not in (chimera.Molecule.Circle, chimera.Molecule.Disk):
		raise MidasError('unknown aromatic representation ("%s")' % style)
	for m in molecules:
		m.aromaticDisplay = True
		m.aromaticMode = mode

def unaromatic(sel='sel'):
	molecules = _selectedModels(sel)
	for m in molecules:
		m.aromaticDisplay = False

def _attrSelFunc(level):
	if level[0] == 'a':
		return _selectedAtoms
	elif level[0] == 'r':
		return _selectedResidues
	elif level[0] == 's':
		from chimera import MSMSModel
		return lambda sel, mt=MSMSModel: _selectedModels(sel,modType=mt)
	elif level[0] == 'm':
		return _selectedModels
	elif level[0] == 'b':
		return _selectedBonds
	elif level[0] == 'p':
		return _selectedPseudobonds
	elif level[0] == 'g':
		return _selectedPseudobondGroups
	raise MidasError("Attribute level must be [a]tom, [r]esidue,"
			" [m]olecule, [b]ond, [s]urface, [p]seudobond,"
			" or [g]roup")
def bond(sel='sel'):
	bonded = _selectedAtoms(sel)
	if len(bonded) != 2:
		raise MidasError("Choose only 2 atoms to bond (%d chosen)"
								% len(bonded))
	from chimera.molEdit import addBond
	return addBond(*bonded)
	
def bondcolor(color, sel='sel'):
	try:
		c = convertColor(color)
	except RuntimeError, e:
		raise MidasError(e)
	atoms = _selectedAtoms(sel)
	for b in misc.bonds(atoms, internal=True):
		b.color = c
		b.halfbond = False
bondcolour = bondcolor

def bonddisplay(mode, sel='sel'):
	atoms = _selectedAtoms(sel)
	for b in misc.bonds(atoms, internal=True):
		b.display = mode

def bondrepr(style, sel='sel'):
	if style == "stick":
		bondMode = chimera.Bond.Stick
	elif style == "wire":
		bondMode = chimera.Bond.Wire
	else:
		raise MidasError('Unknown representation style "%s"' % style)
	atoms = _selectedAtoms(sel)
	for b in misc.bonds(atoms, internal=True):
		b.drawMode = bondMode

def center(sel='sel'):
	aList = _selectedAtoms(sel)
	if len(aList) == 0:
		raise MidasError('No atoms selected')
	chimera.viewer.camera.center = _centerOf(aList).data()
centre = center

def chimeraSelect(sel='sel'):
	if sel in ['up', 'down']:
		from chimera.selection.upDown import selUp, selDown
		if sel == 'up':
			selUp()
		else:
			selDown()
		return
	if sel.startswith("invert"):
		from chimera.selection import invertCurrent
		if sel.endswith("sel"):
			invertCurrent(allModels=False)
		else:
			invertCurrent(allModels=True)
		return
	if not isinstance(sel, selection.Selection):
		sel = evalSpec(sel)
	if not hasattr(sel, 'addImplied'):
		newSel = selection.ItemizedSelection()
		newSel.merge(selection.REPLACE, sel)
		sel = newSel
	sel.addImplied(vertices=0)
	from chimera import selectionOperation
	selectionOperation(sel)

def chirality(sel='sel'):
	import chiral
	class ChiralError(ValueError, MidasError):
		pass
	chiralities = []
	for a in _selectedAtoms(sel):
		try:
			start = chimera.idatm.typeInfo[a.idatmType]
		except KeyError:
			raise ChiralError(
				"Unknown hybridization state for atom %s"
								% a.oslIdent())
		if start.geometry != 4:
			raise ChiralError("%s is not tetrahedral"
								% a.oslIdent())
		if start.substituents != 4:
			raise ChiralError("%s bonds to less than 4 atoms"
								% a.oslIdent())
		chirality = chiral.init(a)	  
		chirMsg = chirality
		if chirality is None:
			chirMsg = "no"
		else:
			chirMsg = chirality
		_showStatus('%s has %s chirality' % (a.oslIdent(), chirMsg))
		chiralities.append(chirality)
	if not chiralities:
		raise ChiralError("No atoms specified")
	return chiralities

def clip(plane, delta, frames=None):
	param = {'command':'clip', 'plane':plane,
					  'delta':delta, 'frames':frames}
	if frames is None:
		_clip(None, param, None)
	else:
		_addMotionHandler(_clip, param)

def close(model, subid=None):
	if model == "all":
		models = chimera.openModels.list()
	elif model == "session":
		chimera.closeSession()
		return
	else:
		if subid is None:
			models = chimera.openModels.list(model)
		else:
			models = chimera.openModels.list(model, subid)
	chimera.openModels.close(models)

def cofr(where='report'):
	from chimera import openModels as om
	methods = { 'view': om.CenterOfView,
		    'front': om.FrontCenter,
		    'models': om.CenterOfModels,
		    'independent': om.Independent,
		    'fixed':om.Fixed}
	if where in methods:
		om.cofrMethod = methods[where]
	elif isinstance(where, chimera.Point):
		om.cofr = where
		om.cofrMethod = om.Fixed
	elif where != 'report':
		sph = boundingSphere(where)
		if sph is None:
			raise MidasError('No atoms or surfaces selected')
		om.cofr = sph.center
		om.cofrMethod = om.Fixed
	if om.cofrMethod != om.Independent:
		_showStatus('Center of rotation: ' + str(om.cofr))

def color(color, sel='sel'):
	"""Change atom color"""
	color, atomItems, resItems = _colorSplit(color)
				
	colorFunc = None
	if color in ['byatom', 'byelement']:
		# always atom-level only
		resItems = []
		def _colorByAtom(a, items):
			c = elementColor(a.element)
			for item in items:
				setattr(a, item, c)
		colorFunc = _colorByAtom
	elif color in ['byhet', 'byhetero']:
		# always atom-level only
		resItems = []
		def _colorByHet(a, items):
			if a.element.number == elements.C.number:
				return
			c = elementColor(a.element)
			for item in items:
				setattr(a, item, c)
		colorFunc = _colorByHet
	else:
		try:
			c = convertColor(color)
		except RuntimeError, e:
			raise MidasError(e)

	if colorFunc == None:
		def _color(thing, items, color=c):
			for item in items:
				setattr(thing, item, color)
		colorFunc = _color

	if atomItems:
		# change surfaces from custom coloring if appropriate...
		if 'surfaceColor' in atomItems:
			from chimera import MSMSModel
			mols = {}
			for m in _selectedModels(sel):
				mols[m] = None
			for surf in chimera.openModels.list(
							modelTypes=[MSMSModel]):
				if surf.colorMode != MSMSModel.Custom:
					continue
				if surf.molecule in mols:
					surf.colorMode = MSMSModel.ByAtom
				
		_editAtom(sel, lambda a, items=atomItems: colorFunc(a, items))

	if resItems:
		_editResidue(sel, lambda a, items=resItems: colorFunc(a, items))
colour = color

def colordef(color, target):
	"""Define RGB(A) color"""
	if isinstance(color, basestring):
		if color in _colorEditorSynonyms:
			raise MidasError("Cannot define a color named '%s'"
								% color)
		c = chimera.Color.lookup(color)
		if c is None:
			if target is None:
				raise MidasError("Unknown color named '%s'"
								% color)
			c = chimera.MaterialColor()
			c.save(color)
		if target is None:
			_showStatus('color %s is %g %g %g %g' % (
							(color,) + c.rgba()))
			return
	else:
		c = color
		if target is None:
			raise MidasError("print it out yourself!")

	if isinstance(target, tuple):
		# argument is RGB or RGBA tuple
		c.ambientDiffuse =  target[:3]
		if len(target) > 3:
			c.opacity = target[-1]
		else:
			c.opacity = 1.0
	else:
		# argument is other color
		try:
			nc = convertColor(target)
		except:
			raise MidasError('Color "%s" is undefined' % target)
		c.ambientDiffuse = tuple(nc.ambientDiffuse)
		c.opacity = nc.opacity
colourdef = colordef

def copy(printer=None, file=None, format=None, supersample=None,
			raytrace=False, rtwait=None, rtclean=None,
			width=None, height=None):
	import chimera.printer as cp
	if raytrace:
		format = 'PNG'
	if not format:
		if file:
			format = deduceFileFormat(file, cp.FilenameFilters)
			if not format:
				format = deduceFileFormat(file,
						cp.StereoFilenameFilters)
		if not format:
			format = 'PS'
	printMode = None
	if format in (f[0] for f in cp.StereoFilenameFilters):
		printMode = 'stereo pair'
	if not printer and not file:
		if chimera.nogui:
			raise MidasError('need filename in nogui mode')
		file = '-'
	if printer and not file:
		saveFile = tempfile.mktemp()
		format = 'TIFF'
	elif file and file != '-':
		from OpenSave import tildeExpand
		saveFile = tildeExpand(file)
	else:
		saveFile = None
	if rtclean is None:
		keepInput = None
	else:
		keepInput = not rtclean
	if width is not None and height is None:
		w, h = chimera.viewer.windowSize
		scale = float(width) / w
		height = int(h * scale + .5)
	elif width is None and height is not None:
		w, h = chimera.viewer.windowSize
		scale = float(height) / h
		width = int(w * scale + .5)
	image = cp.saveImage(saveFile, format=format, supersample=supersample,
				raytrace=raytrace, raytraceWait=rtwait,
				raytraceKeepInput=keepInput,
				width=width, height=height, printMode=printMode)

	if printer is None:
		return

	if raytrace:
		from PIL import Image
		image = Image.open(saveFile)

	if not saveFile or format not in ('TIFF', 'TIFF-fast'):
		printSource = tempfile.mktemp()
		image.save(printSource, 'TIFF')
	else:
		printSource = saveFile
	
	
	if printer != "-":
		printArg = "-P" + printer
	else:
		printArg = ""

	itops = os.path.join(os.environ["CHIMERA"], "bin", "itops")
	os.system('"' + itops + '" -a -r %s | lpr %s' % (printSource, printArg))
	if file and format not in ('TIFF', 'TIFF-fast'):
		os.unlink(printSource)

def define(geom, sel='sel', **kw):
	name = kw.pop("name", geom)
	if geom == "axis":
		plural = "Axes"
		if kw.pop("perHelix", False):
			from StructMeasure.Axes import createHelices
			axes = []
			for m in _selectedModels(sel):
				axes.extend(createHelices(m, **kw))
			return axes
	else:
		plural = geom.capitalize() + "s"
	exec("from StructMeasure.%s import %sManager as mgr" % (plural, geom))
	atoms = _selectedAtoms(sel)
	return eval("mgr.create%s(name, atoms, **kw)" % geom.capitalize())

def undefine(geomIDs, axes=False, planes=False):
	if axes:
		from StructMeasure.Axes import axisManager
		geomIDs.extend([a.id for a in axisManager.axes])
	if planes:
		from StructMeasure.Planes import planeManager
		geomIDs.extend([p.id for p in planeManager.planes])
	lookup = set(geomIDs)
	from StructMeasure.Geometry import geomManager
	geomManager.removeItems([i for i in geomManager.items if i.id in lookup])

def delete(sel='sel'):
	"""Delete atoms"""
	deleteAtomsBonds(_selectedAtoms(sel))

def display(sel='sel'):
	"""Display atoms

	Atoms specification may come from either a selection or
	an osl string.  If no atom specification is supplied,
	the current selection is displayed."""
	def _atomDisplay(atom):
		atom.display = 1
	_editAtomBond(sel, _atomDisplay, None)

def distance(sel='sel', objIDs=[], **kw):
	"""Monitor distance between exactly two items"""
	if len(objIDs) < 2:
		atoms = _selectedAtoms(sel)
	else:
		atoms = []
	if len(atoms) + len(objIDs) != 2:
		raise MidasError('Exactly two atoms/axes/planes must be selected.'
			'  You selected %d.' % (len(atoms) + len(objIDs)))
	if len(atoms) == 2:
		try:
			DistMonitor.addDistance(atoms[0], atoms[1])
		except ValueError, s:
			raise MidasError('Error adding distance: %s.' % s)
		return atoms[0].xformCoord().distance(atoms[1].xformCoord())

	from StructMeasure.Geometry import geomManager
	items = geomManager.items
	objs = []
	for objID in objIDs:
		try:
			objs.append([item for item in items if item.id == objID][0])
		except IndexError:
			raise MidasError("No such object: %s" % objID)

	if len(atoms) == 1:
		try:
			dist = objs[0].pointDistances([atom.xformCoord()
				for atom in atoms], **kw)[0]
		except TypeError:
			if 'signed' in kw:
				raise MidasError("'signed' keyword only supported for"
					" atom-to-plane distances")
			raise
		name1 = str(atoms[0])
		name2 = objs[0].id
	else:
		dist = geomManager.distance(objs)
		name1, name2 = [obj.id for obj in objs]
	_showStatus("Distance from %s to %s is %.3f" % (name1, name2, dist))
	return dist

def export(filename=None, format=None, list=False):
	DEFAULT_FORMAT = 'X3D'
	from chimera import exports
	exportInfo = exports.getFilterInfo()
	if list:
		_showStatus("Export formats: " + ", ".join([x[0] for x in exportInfo]))
		return

	if format:
		for name, glob, suffix in exportInfo:
			if name.lower() == format.lower():
				format = name
				break
		else:
			raise MidasError('Unknown export format: %s' % format)

	if not filename:
		if chimera.nogui:
			raise ValueError(
			"Cannot use argless 'export' command in nogui mode")
		from chimera import exportDialog
		d = dialogs.display(exportDialog.name)
		if d and format:
			d.setFilter(format)
		return

	from OpenSave import compressSuffixes
	compress = False
	for cs in compressSuffixes:
		if filename.endswith(cs):
			compress = True
			break
	if compress:
		replyobj.warning("file not saved: compressed files are not supported yet\n")
		return

	if not format:
		format = deduceFileFormat(filename, exportInfo)
		if not format:
			format = DEFAULT_FORMAT

	from OpenSave import tildeExpand
	filename = tildeExpand(filename)

	exports.doExportCommand(format, filename)

def focus(sel='sel'):
	"""Window/cofr about displayed part of selection"""
	if sel == '#':
		dsel = sel
	else:
		disped = [a for a in _selectedAtoms(sel) if a.shown()]
		disped.extend([r for r in _selectedResidues(sel)
			       if r.ribbonDisplay and r.molecule.rootForAtom(r.atoms[0], True).size.numAtoms != len(r.atoms)])
		disped.extend([p for p in _selectedSurfacePieces(sel)
			       if p.display and p.model.display])
		if not disped:
			raise MidasError("No displayed atoms/ribbons/surfaces specified")

		from chimera.selection import ItemizedSelection
		dsel = ItemizedSelection()
		dsel.add(disped)
	window(dsel)
	from chimera import openModels as om
	if om.cofrMethod != om.Independent:
		if sel == '#':
			from chimera import viewing
			om.cofrMethod = viewing.defaultCofrMethod
		else:
			om.cofrMethod = om.CenterOfView
			cofr('report')

def unfocus(sel='sel'):
	"""Window/cofr about all displayed models"""
	focus('#')

def freeze():
	"""Stop all motion"""
	_clearMotionHandlers()
	if not chimera.nogui:
		chimera.tkgui.stopSpinning()

def getcrd(sel='sel'):
	"""Print the coordinates of selected atoms"""
	def _getcrd(a):
		_showStatus('Atom %s - %s' % (a.oslIdent(),
				'%.3f %.3f %.3f' % a.coord().data()))
	_editAtom(sel, _getcrd)

def ksdssp(sel='sel', energy=None, helixLen=None, strandLen=None, infoFile=None):
	kw = {}
	reportEnergy = reportHelix = reportStrand = "<default>"
	if energy is not None:
		kw['energyCutoff'] = energy
		reportEnergy = "%g" % energy
	if helixLen is not None:
		kw['minHelixLength'] = helixLen
		reportHelix = "%g" % helixLen
	if strandLen is not None:
		kw['minStrandLength'] = strandLen
		reportStrand = "%g" % strandLen
	if infoFile is not None:
		kw['info'] = infoFile
	
	mols = _selectedModels(sel)
	if mols:
		replyobj.info(
"""Computing secondary structure assignments for model(s) %s
using ksdssp (Kabsch and Sander Define Secondary Structure
of Proteins) with the parameters:
  energy cutoff %s
  minimum helix length %s
  minimum strand length %s
""" % (", ".join([m.oslIdent() for m in mols]), reportEnergy, reportHelix, reportStrand))
		for mol in mols:
			mol.computeSecondaryStructure(**kw)
			mol.updateRibbonData()

def label(sel='sel', offset=None, warnLarge=False):
	"""Add label to selected atoms"""
	if offset == 'default':
		offset = chimera.Vector(chimera.Molecule.DefaultOffset, 0, 0)
	def _label(thing, offset=offset):
		if _labelInfo == "name":
			thing.label = thing.oslIdent(chimera.SelAtom)[1:]
		elif _labelInfo == "idatm":
			thing.label = thing.idatmType
		elif _labelInfo == "element":
			thing.label = thing.element.name
		else:
			thing.label = str(getattr(thing, _labelInfo, "none"))
		if offset is not None:
			thing.labelOffset = offset
	if warnLarge and not chimera.nogui:
		numAffected = len([a for a in _selectedAtoms(sel) if a.display])
		if numAffected > 100:
			# is it also more than one label per residue?
			# (use 1.5 per residue to allow for alt atom locs)
			if numAffected > 1.5 * len(_selectedResidues(sel)):
				from chimera.tkgui import LabelWarningDialog
				LabelWarningDialog(numAffected,
							lambda : label(sel))
				return
	_editAtom(sel, _label)

def labelopt(opt, value):
	"""change label display options"""
	if opt == "info":
		global _labelInfo
		_labelInfo = value

def linewidth(width, sel='sel'):
	models = _selectedModels(sel)
	for model in models:
		model.lineWidth = width

def longbond(ratio=2.5, length=None, sel='sel'):
	from chimera import LONGBOND_PBG_NAME
	from chimera.misc import getPseudoBondGroup
	pbg = getPseudoBondGroup(LONGBOND_PBG_NAME)
	if pbg.display:
		raise MidasError("Missing segments already shown."
				" Use ~longbond to hide them.")
	pbg.display = True

class TooFewAtomsError(MidasError):
	pass

def match(f, t, selected=False, iterate=None, minPoints=1, showMatrix=False,
														move=True):
	"""Superposition the two specified sets of atoms ("from" and "to")

	   if 'selected' is True, transform all active models, not just
	   the 'from' model.

	   if 'iterate' is not None, the matching will iterate
	   (pruning poorly-matching atom pairs at each pass) until no pair
	   distance exceeds the value assigned to 'iterate'

	   'minPoints' is the minimum number of points from each model to
	   match.  If fewer are specified (or, due to 'iterate', you go
	   below the number), then TooFewAtomsError is raised.

	   if 'showMatrix' is True, report the transformation matrix to
	   the Reply Log.

	   if 'move' is True, superimpose the models.
	"""
	if iterate is not None and not move:
		raise MidasError("Cannot iterate if 'move' is false")
	mobileAtoms, refAtoms, mobileMol, refMol = _atomSpecErrorCheck(f, t)
	xfrel = mobileMol.openState.xform.inverse()
	xfrel.multiply(refMol.openState.xform)
	import chimera.match
	firstPass = 1
	while 1:
		if len(refAtoms) < minPoints:
			raise TooFewAtomsError("Too few corresponding atoms"
				" (%d) to match models\n" % len(refAtoms))

		xform, rmsd = chimera.match.matchAtoms(refAtoms, mobileAtoms)
		if move:
			xf = refMol.openState.xform
			xf.multiply(xform)
			mobileMol.openState.xform = xf
			if selected:
				# transform all active models
				tfIds = [(refMol.id, refMol.subid),
						(mobileMol.id, mobileMol.subid)]
				for id, subid in chimera.openModels.listIds():
					openState = chimera.openModels.openState(id, subid)
					if openState.active and (id, subid) not in tfIds:
						openState.xform = xf
		if iterate is None:
			break
		elif iterate < 0.0:
			raise MidasError("Iteration cutoff must be positive")

		pairings = []
		for i in range(len(refAtoms)):
			ref = refAtoms[i]
			mobile = mobileAtoms[i]
			pairings.append((ref.xformCoord().sqdistance(
				mobile.xformCoord()), ref, mobile))
		pairings.sort()

		if firstPass:
			firstPass = 0
			cutoff = iterate * iterate

		if pairings[-1][0] <= cutoff:
			break

		# cull 10% or...
		index1 = int(len(refAtoms) * 0.9)

		for i in range(len(refAtoms)-1, -1, -1):
			if pairings[i][0] <= cutoff:
				break

		# cull half the long pairings
		index2 = int((i + len(refAtoms)) / 2)

		# whichever is fewer
		index = max(index1, index2)

		refAtoms = []
		mobileAtoms = []
		for i in range(index):
			dist, ref, mobile = pairings[i]
			refAtoms.append(ref)
			mobileAtoms.append(mobile)

	if len(refAtoms) < 3:
		replyobj.warning("This superposition uses less than 3 pairs of"
			" atoms is therefore not unique.\n")
	if showMatrix:
		# even when iterating, only last transformation computed matters
		from Matrix import transformation_description, xform_matrix
		tf = transformation_description(xform_matrix(xform))
		xfrel.premultiply(xform)
		tl = transformation_description(xform_matrix(xfrel))
		msg = ('Motion from original file coordinates\n%s' % tf +
		       'Motion from last position\n%s' % tl)
		replyobj.info(msg)
	_showStatus('RMSD between %d atom pairs is %.3f angstroms'
						% (len(refAtoms), rmsd))
	return mobileAtoms, refAtoms, rmsd

#
# Copies the f model transform to the t models.
#
# If the moving argument is provided (a list of models) then those
# models are carried along by the transform that takes f to t and the
# t model(s) are not changed (unless they are in the moving list).
#
def matrixcopy(f, t, moving = None):
	try:
		xform = f.openState.xform
	except AttributeError:
		fList = _getModelsFromId(f)
		src = None
		for mod in fList:
			if not src:
				src = mod.openState
			elif src != mod.openState:
				raise MidasError(
					'Too many source models selected.')
		if not src:
			raise MidasError('No source models selected.')
		xform = src.xform
			
	try:
		dests = [t.openState]
	except AttributeError:
		try:
			dests = [m.openState for m in t]
		except AttributeError:
			dests = [x.openState for x in _getModelsFromId(t)]
	if len(dests) == 0:
		raise MidasError('No destination model(s) selected.')
	if moving is None:
		for dest in dests:
			dest.xform = xform
	else:
		xform.multiply(dests[0].xform.inverse())
		for os in set([m.openState for m in moving]):
			os.globalXform(xform)


def matrixget(fileName):
	if fileName == "-":
		f = sys.stdout
	else:
		f = file(fileName, 'w')
	for mid in chimera.openModels.listIds():
		print>>f, "Model %d.%d" % mid
		os = chimera.openModels.openState(*mid)
		xform = os.xform
		lines = str(xform).strip().split("\n")
		print>>f, "\t" + "\n\t".join(lines)
	if fileName != "-":
		f.close()

def matrixset(fileName):
	try:
		f = file(fileName, "r")
	except IOError, v:
		raise MidasError(v)
	lines = f.readlines()
	f.close()
	if len(lines) % 4 != 0:
		raise MidasError("Matrixset file not composed of 4-line groups"
			" (model numbers each with a 3x4 matrix)")
	for i in range(0, len(lines), 4):
		fields = lines[i].strip().split()
		raiseError = False
		if len(fields) != 2 or fields[0] != "Model" \
		or '.' not in fields[1]:
			raiseError = True
		else:
			mid = fields[1].split('.')
			if len(mid) != 2 or not mid[0].isdigit() \
			or not mid[1].isdigit():
				raiseError = True
			else:
				mid = map(int, mid)
		if raiseError:
			raise MidasError("Matrixset 'Model' line %d not of the"
					" form: Model number.number" % (i+1))
		nums = []
		for j in range(i+1, i+4):
			fields = lines[j].strip().split()
			if len(fields) != 4:
				raiseError = True
			else:
				try:
					nums.extend(map(float, fields))
				except ValueError:
					raiseError = True
			if raiseError:
				raise MidasError("Matrixset 3x4 matrix line %d"
						" is not 4 numbers" % (j+1))
		args = nums + [True]
		xform = chimera.Xform.xform(*args)
		try:
			openState = chimera.openModels.openState(*mid)
		except ValueError:
			replyobj.warning("Ignoring matrix for non-existent"
					" model %d.%d\n" % tuple(mid))
			continue
		openState.xform = xform

def modelcolor(color, sel='sel'):
	"""Change model color"""

	try:
		color = convertColor(color)
	except RuntimeError, e:
		raise MidasError(e)
	def _color(thing):
		thing.color = color
	_editMolecule(sel, _color)
modelcolour = modelcolor

def modeldisplay(sel='sel'):
	def _modeldisplay(thing):
		thing.display = 1
	_editModel(sel, _modeldisplay)

def move(x=0, y=0, z=0, frames=None, coordinateSystem=None, models=None):
	v = chimera.Vector(x, y, z)
	param = {'command':'move',
		 'xform':chimera.Xform.translation(v),
		 'frames':frames,
		 'coordinateSystem':coordinateSystem,
		 'models':models}
	if frames is None:
		_movement(None, param, None)
	else:
		_addMotionHandler(_movement, param)

def namesel(selName=None):
	from chimera.selection import saveSel, savedSels
	if not selName:
		selNames = savedSels.keys()
		if not selNames:
			_showStatus("No saved selections")
		else:
			_showStatus("Saved selections: %s" %
							', '.join(selNames))
		return
	saveSel(selName)

def objdisplay(sel='sel'):
	def _objdisplay(thing):
		if not isinstance(thing, chimera.Molecule)\
		and not isinstance(thing, chimera.MSMSModel):
			thing.display = 1
	_editModel(sel, _objdisplay)

def open(filename, filetype=None, model=chimera.OpenModels.Default,
		noprefs=False):
	if filetype in ['model', 'pdb', 'PDB']:
		filetype = 'PDB'
	elif filetype in ['mol2', 'Mol2']:
		filetype = 'Mol2'
	elif filetype in ['obj', 'OBJ', 'vrml', 'VRML']:
		filetype = 'VRML'
	try:
		mList = chimera.openModels.open(filename,
						type=filetype,
						defaultType="PDB",
						baseId=model,
						prefixableType=1,
						noprefs=noprefs)
	except IOError, s:
		try:
			code, msg = s
		except:
			msg = s
		raise MidasError(str(msg))
	else:
		if len(mList) == 1:
			_showStatus('1 model opened')
		elif len(mList) > 1:
			_showStatus('%d models opened' % len(mList))
	return mList

def pause():
	if chimera.nogui:
		return
	import Pmw
	cancel = [False]
	def waitForKey(event, cancel=cancel):
		chimera.tkgui.deleteKeyboardFunc(waitForKey)
		Pmw.popgrab(chimera.tkgui.app.graphics)
		chimera.tkgui.app.graphics.quit()
		replyobj.status("")
		if event.keysym in ["End", "Escape"]:
			cancel[0] = True
	chimera.tkgui.addKeyboardFunc(waitForKey)
	replyobj.status("Script paused; Hit Escape or End to abort, any"
		" other key to continue", color="blue", blankAfter=0)
	Pmw.pushgrab(chimera.tkgui.app.graphics, False, lambda: None)
	chimera.tkgui.app.graphics.mainloop()
	if cancel[0]:
		from chimera import CancelOperation
		raise CancelOperation("cancel script")

def pdbrun(cmd, all=0, conect=0, nouser=0, noobj=0, nowait=0, surface=0,
							mark=None, viewer=None):
	# any marks specified should be a sequence

	if viewer == None:
		viewer = chimera.viewer
	
	# wrappy isn't smart enough to provide the arguments that the
	# full-fledged pdbrun requires, so ignore marks for now
	if sys.platform == 'win32':
		# need to double up backslashes
		cmd = cmd.replace('\\', '\\\\')
	viewer.pdbrunNoMarks(all, conect, nouser, surface, nowait, cmd)

def rainbow(sel='sel', **kw):
	"""Color selected models in rainbow pattern"""
	import midas_rainbow
	models = []
	_editMolecule(sel, lambda m, ms=models: ms.append(m))
	if 'colors' in kw:
		kw['colors'] = [convertColor(c) for c in kw['colors']]
	midas_rainbow.rainbowModels(models, **kw)

def _prepRangeColor(attrName, wayPoints, noValue, sel):
	atoms = _selectedAtoms(sel)
	if not atoms:
		raise MidasError("No atoms specified")

	residues = _selectedResidues(sel)
	if '.' in attrName:
		level, attrName = attrName.split('.', 1)
		if level == "atom":
			isAtomAttr = True
		elif level[:3] == "res":
			isAtomAttr = False
		else:
			raise MidasError("attribute qualifier must be"
							" 'residue' or 'atom'")
	else:
		isAtomAttr = True
		for r in residues:
			if hasattr(r, attrName):
				isAtomAttr = False
				break
	if isAtomAttr:
		items = atoms
	else:
		items = residues

	needSurvey = False
	for value, color in wayPoints:
		if isinstance(value, basestring):
			needSurvey = True
			break

	if needSurvey:
		minVal = maxVal = None
		for i in items:
			try:
				val = getattr(i, attrName)
			except AttributeError:
				continue
			if val is None:
				continue
			if minVal is None or val < minVal:
				minVal = val
			if maxVal is None or val > maxVal:
				maxVal = val
		if minVal is None:
			raise MidasError("No items had attribute '%s'"
								% attrName)
		else:
			midVal = (minVal + maxVal) / 2.0
			_showStatus("%s min/mid/max: %g / %g / %g" %
				(attrName, minVal, midVal, maxVal))

	finalWayPoints = []
	for val, color in wayPoints:
		try:
			index = ["min", "mid", "max"].index(val)
		except ValueError:
			if isinstance(val, basestring):
				raise MidasError("non-numeric attribute value "
					"must be min, mid, max, or novalue")
		else:
			val = [minVal, midVal, maxVal][index]
		try:
			color = convertColor(color)
		except RuntimeError, e:
			raise MidasError(e)
		finalWayPoints.append((val, color.rgba()))
	finalWayPoints.sort()
	noValueColor = convertColor(noValue)
	if noValueColor is not None:
		noValueRgba = noValueColor.rgba()
	else:
		noValueRgba = None
	return isAtomAttr, items, residues, finalWayPoints, noValueRgba

def _doRangeColor(items, attrFunc, attrName, colorFunc, finalWayPoints,
							noValue, noValueRgba):
	colorCache = {}
	for i in items:
		prevWP = None
		try:
			val = attrFunc(i, attrName)
		except AttributeError:
			val = None
		if val is None:
			if noValue is None:
				continue
			else:
				rgba = noValueRgba
		else:
			for wpVal, rgba in finalWayPoints:
				if val < wpVal:
					break
				prevWP = (wpVal, rgba)
			else:
				wpVal = None
			if prevWP is None:
				rgba = finalWayPoints[0][1]
			elif wpVal is None:
				rgba = finalWayPoints[-1][1]
			else:
				lval, lrgba = prevWP
				pos = (val - lval) / float(wpVal - lval)
				rgba = tuple(map(lambda l, r:
					l * (1 - pos) + r * pos, lrgba, rgba))
		if rgba:
			try:
				color = colorCache[rgba]
			except KeyError:
				color = chimera.MaterialColor(*rgba)
				colorCache[rgba] = color
		else:
			color = rgba

		colorFunc(i, color)

def rangeColor(attrName, colorItems, wayPoints, noValue,
						sel='#', showKey=False):
	"""color atom parts by attribute

	   'attrName' is a residue or atom attribute name.  It can be 
	   prepended with 'atom.' or 'residue.' to resolve ambiguity if
	   necessary.  Otherwise, residue-level attributes win "ties".
	   
	   'colorItems' is a comma-separated string of items to color (labels,
	   surfaces, etc., as per the 'color' command) or an empty string
	   (color everything).  In addition to the color command characters,
	   the character 'r' means to color ribbons.

	   'wayPoints' is a sequence of value/color tuples describing the color
	   range layout.  The values can be 'max', 'min', 'mid' or numeric.

	   'noValue' is the color to apply to items missing the attribute.
	   A value of None means to leave them unchanged.

	   If 'showKey' is True, bring up the Color Key tool with the
	   appropriate values filled in.
	"""

	isAtomAttr, items, residues, finalWayPoints, noValueRgba = \
			_prepRangeColor(attrName, wayPoints, noValue, sel)
	if showKey:
		keyData = []
		for val, rgba in finalWayPoints:
			keyData.append((rgba, str(val)))
		from Ilabel.gui import IlabelDialog
		d = dialogs.display(IlabelDialog.name)
		d.keyConfigure(keyData)

	atomItems, resItems = _colorItems([ci
				for ci in colorItems.split(',') if ci])
	if atomItems:
		def doColorItems(i, c, isAtomAttr=isAtomAttr,
						colorItems=atomItems):
			if isAtomAttr:
				for ci in colorItems:
					setattr(i, ci, c)
			else:
				for a in i.oslChildren():
					for ci in colorItems:
						setattr(a, ci, c)

		_doRangeColor(items, getattr, attrName, doColorItems,
					finalWayPoints, noValue, noValueRgba)
	if resItems:
		valCache = {}
		def getVal(residue, attrName):
			try:
				val = valCache[residue]
			except KeyError:
				tot = None
				atoms = residue.oslChildren()
				for a in atoms:
					try:
						val = getattr(a, attrName)
					except AttributeError:
						continue
					if tot is None:
						tot = 0
					tot += val
				if tot is None:
					val = None
				else:
					val =  tot / float(len(atoms))
				valCache[residue] = val
			return val

		if isAtomAttr:
			attrFunc = getVal
		else:
			attrFunc = getattr

		def colorItem(i, c, colorItems=resItems):
			for ci in colorItems:
				setattr(i, ci, c)

		_doRangeColor(residues, attrFunc, attrName, colorItem,
					finalWayPoints, noValue, noValueRgba)
rangeColour = rangeColor

def represent(style, sel='sel'):
	if style == "bs" or style == "b+s":
		# ball-and-stick
		atomMode = chimera.Atom.Ball
		bondMode = chimera.Bond.Stick
	elif style == "stick":
		atomMode = chimera.Atom.EndCap
		bondMode = chimera.Bond.Stick
	elif style == "wire":
		atomMode = chimera.Atom.Dot
		bondMode = chimera.Bond.Wire
	elif style == "cpk" or style == "sphere":
		atomMode = chimera.Atom.Sphere
		bondMode = chimera.Bond.Wire
	else:
		raise MidasError('Unknown representation style "%s"' % style)
	atoms = _selectedAtoms(sel)
	for a in atoms:
		a.drawMode = atomMode
	for b in misc.bonds(atoms, internal=True):
		b.drawMode = bondMode

def reset(name='default', frames=None, mode='linear'):
	if name == "list":
		statStr = "Saved positions:"
		for posName in positions.keys():
			statStr = statStr + "\n\t" + posName
		_showStatus(statStr)
		return
	
	if not positions.has_key(name):
		if name == 'default':
			chimera.viewer.resetView()
			window('#')
			uncofr()
		else:
			raise MidasError("No saved position named '%s'" % name)
		return

	if frames is not None and frames < 1:
		raise MidasError("frame count must be positive")
	param = {'command':'reset', 'position':positions[name], 'mode':mode,
					'frames':frames, 'duration':frames}
	if frames is None:
		param.update({'frames':0})
		_restorePosition(None, param, None)
	else:
		_addMotionHandler(_restorePosition, param)

def ribbon(sel='sel'):
	"""Display residue as ribbon"""
	def _residuedisplay(thing):
		thing.ribbonDisplay = 1
	_editResidue(sel, _residuedisplay)
	anyRibbon = False
	for m in _selectedModels(sel):
		if m.updateRibbonData():
			anyRibbon = True
	if not anyRibbon:
		replyobj.warning("no residues with ribbons found\n")

def ribbackbone(sel='sel'):
	def _ribbackbone(thing):
		thing.ribbonHidesMainchain = 0
	_editMolecule(sel, _ribbackbone)

def ribinsidecolor(color, sel='sel'):
	"""Change inside ribbon color"""
	try:
		color = convertColor(color)
	except RuntimeError, e:
		raise MidasError(e)
	def _color(thing):
		thing.ribbonInsideColor = color
	_editMolecule(sel, _color)
ribinsidecolour = ribinsidecolor

def ribrepr(style, sel='sel'):
	if style == "flat" or style == "ribbon":
		# ball-and-stick
		mode = chimera.Residue.Ribbon_2D
	elif style == "sharp" or style == "edged":
		mode = chimera.Residue.Ribbon_Edged
	elif style == "smooth" or style == "rounded" or style == "round":
		mode = chimera.Residue.Ribbon_Round
	else:
		from RibbonStyleEditor import xsection
		exs = xsection.findXSection(style)
		if exs is None:
			raise MidasError('Unknown representation style "%s"'
								% style)
		xs = exs.getXS()
		mode = chimera.Residue.Ribbon_Custom
	def _residuestyle(thing):
		thing.ribbonDrawMode = mode
		if mode == chimera.Residue.Ribbon_Custom:
			thing.ribbonXSection = xs
	_editResidue(sel, _residuestyle)

def ribscale(name, sel='sel'):
	from RibbonStyleEditor import scaling
	if name == scaling.SystemDefault:
		def _residuestyle(thing):
			thing.ribbonStyle = None
		_editResidue(sel, _residuestyle)
	else:
		sc = scaling.findScaling(name)
		if sc is None:
			raise MidasError('Unknown ribbon scaling "%s"' % name)
		def _residuestyle(thing, sc=sc):
			sc.setResidue(thing)
		_editResidue(sel, _residuestyle)

def fillring(style=None, sel='sel'):
	if style is None:
		def _filldisplay(thing):
			thing.fillDisplay = True
		_editResidue(sel, _filldisplay)
		return
	if style in ('unfilled', 'off'):
		return unfillring(sel)
	elif style == 'thin':
		mode = chimera.Residue.Thin
	elif style == 'thick':
		mode = chimera.Residue.Thick
	elif style not in (chimera.Residue.Thin, chimera.Residue.Thick):
		raise MidasError('unknown representation type ("%s")' % style)
	def _fillstyle(thing):
		thing.fillDisplay = True
		thing.fillMode = mode
	_editResidue(sel, _fillstyle)

def rlabel(sel='sel', offset=None, warnLarge=False):
	"""Display residue information as part of one atom label"""
	if offset == 'default':
		offset = chimera.Vector(chimera.Molecule.DefaultOffset, 0, 0)
	def _rlabel(r, offset=offset):
		r.label = '%s %s' % (r.type, r.id)
		if offset is not None:
			r.labelOffset = offset
	_editResidue(sel, _rlabel)

def rmsd(f, t, log=True):
	import math
	fAtoms, tAtoms, fMol, tMol = _atomSpecErrorCheck(f, t)
	dSqrSum = 0
	for i in range(len(fAtoms)):
		dSqrSum += fAtoms[i].xformCoord().sqdistance(
							tAtoms[i].xformCoord())
	sol = dSqrSum / len(fAtoms)
	final = math.sqrt(sol)
	_showStatus('RMSD between %d atom pairs is %.3f angstroms'
						% (len(fAtoms), final), log=log)
	return final

def rock(axis, magnitude=90, frequency=60, frames=-1, coordinateSystem = None,
	 models=None, center=None):
	angles = []
	maximum = float(frequency - 1)
	for i in range(frequency):
		a = i / maximum * math.pi
		angles.append(magnitude * math.sin(a))
	v = _axis(axis)
	xformList = []
	for i in range(len(angles) - 1):
		delta = angles[i + 1] - angles[i]
		xformList.append(chimera.Xform.rotation(v, delta))
	param = {'command':'rock',
		'xformList':xformList,
		'counter':0,
		'direction':1,
		'mode':'bounce',
		'frames':frames,
		'coordinateSystem': coordinateSystem,
		'models': models,
		'center':center}
	_addMotionHandler(_flight, param)

def roll(axis, angle=3, frames=-1, coordinateSystem=None, models=None,
	 center=None):
	turn(axis, angle, frames, coordinateSystem, models, center)

def rotation(sel='sel', rotID=None, reverse=False, adjust=None, frames=None):
	from BondRotMgr import bondRotMgr
	if adjust is not None:
		if rotID is None:
			raise MidasError("Must specify rotation ID to adjust")
		from BondRotMgr import bondRotMgr
		if rotID not in bondRotMgr.rotations:
			raise MidasError("Bond rotation '%d' does not exist!"
				% rotID)
		rot = bondRotMgr.rotations[rotID]
		param = {
			'command': 'rotation',
			'adjust':adjust,
			'rot': rot,
			'frames': frames
		}
		if frames is None:
			_rotation(None, param, None)
		else:
			_addMotionHandler(_rotation, param)
		return rot
	atoms = _selectedAtoms(sel, ordered=True)
	if len(atoms) != 2:
		raise MidasError('Only two atoms must be selected.'
					'  You selected %d.' % len(atoms))
	bond = atoms[0].findBond(atoms[1])
	if bond == None:
		raise MidasError('Selected atoms are not connected'
						' with a covalent bond')
	from chimera import UserError
	try:
		br = bondRotMgr.rotationForBond(bond, requestedID=rotID)
	except UserError, v:
		raise MidasError(str(v))
	if reverse:
		br.anchorSide = br.SMALLER
	return br

def save(filename):
	from OpenSave import compressSuffixes
	for cs in compressSuffixes:
		if filename.endswith(cs):
			break
	else:
		if not filename.endswith(".py"):
			filename += ".py"
	from SimpleSession import saveSession
	saveSession(filename)

def savepos(name='default'):
	if name == "list":
		_showStatus("Saved positions: " + ", ".join(positions.keys()))
		return
	
	positions[name] = _savePosition()

def scale(s, frames=None):
	updateZoomDepth()
	param = {'command':'scale', 'scaleFactor':s, 'frames':frames}
	if frames is None:
		_scale(None, param, None)
	else:
		_addMotionHandler(_scale, param)

def updateZoomDepth(viewer = None):
	if viewer is None:
		viewer = chimera.viewer
	from chimera import openModels
	try:
		cr = openModels.cofr
	except:
		return	# Indep rotation mode or no displayed/active models.
	c = viewer.camera
	cc = c.center
	c.center = (cc[0],cc[1],cr.z)
	if not c.ortho:
		# Adjust view size for new center depth.
		dz = cc[2] - cr.z
		from math import pi, tan
		fov = c.fieldOfView * pi / 180
		try:
			dvs = tan(0.5*fov)*dz*viewer.scaleFactor
		except:
			return	# Illegal field of view = 180 degrees.
		viewer.viewSize += dvs

def section(delta, frames=None):
	param = {'command':'section', 'plane':'section', 'delta':delta,
							'frames':frames}
	if frames is None:
		_clip(None, param, None)
	else:
		_addMotionHandler(_clip, param)

def select(sel='sel'):
	"""Make selected models active"""
	def _select(thing):
		thing.openState.active = 1
	_editModel(sel, _select)

def setAutocolor():
	from chimera import preferences
	from chimera.initprefs import MOLECULE_DEFAULT, MOL_AUTOCOLOR
	preferences.set(MOLECULE_DEFAULT, MOL_AUTOCOLOR, 1, asSaved=1)
	preferences.save()
setAutocolour = setAutocolor

def setBg_color(color):
	try:
		chimera.viewer.background = convertColor(color)
	except RuntimeError, e:
		raise MidasError(e)
setBg_colour = setBg_color

def setDepth_cue():
	chimera.viewer.depthCue = True

def setDc_color(color):
	try:
		chimera.viewer.depthCueColor = convertColor(color)
	except RuntimeError, e:
		raise MidasError(e)
setDc_colour = setDc_color

def setDc_start(s):
	v = chimera.viewer
	cs, ce = v.depthCueRange
	try:
		v.depthCueRange = float(s), ce
	except ValueError, e:
		raise MidasError(e)

def setDc_end(e):
	v = chimera.viewer
	cs, ce = v.depthCueRange
	try:
		v.depthCueRange = cs, float(e)
	except ValueError, e:
		raise MidasError(e)

def setIndependent():
	chimera.openModels.cofrMethod = chimera.OpenModels.Independent

def setLight_quality(q):
	if q in ('glossy', 'normal'):
		import Lighting
		Lighting.setLightQuality(chimera.viewer, q)
	else:
		raise MidasError('Light quality must be "glossy" or "normal", got %s' % q)

def setProjection(mode):
	ortho = mode.lower().startswith('o')
	chimera.viewer.camera.ortho = ortho

def setSilhouette():
	chimera.viewer.showSilhouette = True

def setSilhouette_color(color):
	try:
		chimera.viewer.silhouetteColor = convertColor(color)
	except RuntimeError, e:
		raise MidasError(e)

def setSilhouette_width(width):
	try:
		chimera.viewer.silhouetteWidth = float(width)
	except ValueError, e:
		raise MidasError(e)

def setSubdivision(s):
	lod = chimera.LODControl.get()
	try:
		lod.quality = float(s)
	except ValueError, e:
		raise MidasError(e)

def setAttr(level, name, val, sel='sel'):
	selFunc = _attrSelFunc(level)
	for item in selFunc(sel):
		setattr(item, name, val)

def show(sel='sel', asChain=0):
	models = _selectedModels(sel)
	aDict = _selectedAtoms(sel, asDict=True)
	for m in models:
		if not hasattr(m, 'atoms'):
			continue
		if asChain:
			m.autochain = 1
		for a in m.atoms:
			a.display = a in aDict

def chain(*args, **kw):
	kw["asChain"] = 1
	show(*args, **kw)

# despite the leading '_', _stereoKwMap is used by midas_text.py
_stereoKwMap = {
	'mono':			'mono',
	'off':			'mono',
	'seq':			'sequential stereo',
	'sequential':		'sequential stereo',
	'on':			'sequential stereo',
	'cross eye':		'cross-eye stereo',
	'cross-eye':		'cross-eye stereo',
	'crosseye':		'cross-eye stereo',
	'cross':		'cross-eye stereo',
	'wall eye':		'wall-eye stereo',
	'wall-eye':		'wall-eye stereo',
	'walleye':		'wall-eye stereo',
	'wall':			'wall-eye stereo',
	'left':			'stereo left eye',
	'left eye':		'stereo left eye',
	'left-eye':		'stereo left eye',
	'right':		'stereo right eye',
	'right eye':		'stereo right eye',
	'right-eye':		'stereo right eye',
	'row interleaved':	'row interleaved stereo',
	'row':			'row interleaved stereo',
	'red-cyan':		'red-cyan stereo',
	'anaglyph':		'red-cyan stereo',
	'dti':			'DTI side-by-side stereo',
	'DTI':			'DTI side-by-side stereo',
	'dti side-by-side':	'DTI side-by-side stereo',
	'DTI side-by-side':	'DTI side-by-side stereo',
}
def stereo(mode):
	try:
		mode = _stereoKwMap[mode]
	except KeyError:
		raise MidasError("Unknown stereo mode: %s" % mode)
	from chimera.viewing import setCameraMode
	return setCameraMode(mode, chimera.viewer)

surfaceMethods = {
	"msms":		chimera.MSMSModel,
}
def registerSurfaceMethod(name, func):
	surfaceMethods[name] = func

def surfaceNew(category, sel='sel', models=None, method=None):
	if category in ['ions', 'solvent']:
		_showStatus("Surfacing ions/solvent not yet supported;"
			" skipping those.", log=False, color='red')
		return
	modelClass = chimera.MSMSModel
	if method:
		try:
			modelClass = surfaceMethods[method]
		except KeyError:
			raise MidasError("Unknown surface method: %s" % method)
	if models is None:
		models = _selectedModels(sel)
	for m in models:
		surf = None
		surfModels = chimera.openModels.list(m.id,
					modelTypes=[modelClass])
		for s in surfModels:
			if s.subid == m.subid and s.category == category:
			   	if s.calculationFailed:
					s.update_surface()
				break
		else:
			from chimera.initprefs import (
				SURFACE_DEFAULT, SURF_REPR, SURF_PROBE_RADIUS,
				SURF_DENSITY, SURF_LINEWIDTH, SURF_DOTSIZE,
				SURF_DISJOINT)
			from chimera.preferences import get as prefget
			surf = modelClass(m, category,
				prefget(SURFACE_DEFAULT, SURF_PROBE_RADIUS),
				prefget(SURFACE_DEFAULT, SURF_DISJOINT),
				prefget(SURFACE_DEFAULT, SURF_DENSITY))
			surf.drawMode = prefget(SURFACE_DEFAULT, SURF_REPR)
			surf.lineWidth = prefget(SURFACE_DEFAULT, SURF_LINEWIDTH)
			surf.pointSize = prefget(SURFACE_DEFAULT, SURF_DOTSIZE)
			if m.name:
				catname = category
				surf.name = "MSMS %s surface of %s" % (catname,
									m.name)
			chimera.openModels.add([surf], sameAs=m)

def surfaceDelete(category, sel='sel'):
	models = _selectedModels(sel, chimera.MSMSModel)
	models = filter(lambda m, c=category: m.category == c, models)
	chimera.openModels.close(models)

def surface(atomSpec='sel', category='main', warnLarge=False, **kw):
	def _surfaceDisplay(thing):
		thing.surfaceDisplay = 1

	if warnLarge and not chimera.nogui:
		numAffected = len(_selectedModels(atomSpec))
		if numAffected > 20:
			from chimera.tkgui import SurfaceWarningDialog
			SurfaceWarningDialog(numAffected,
					lambda : surface(atomSpec, category))
			return
	if category != "all categories":
		surfaceNew(category, atomSpec, **kw)
		aSpec = "%s & @/surfaceCategory=%s" % (atomSpec, category)
		atoms = _editAtom(aSpec, _surfaceDisplay)
	else:
		categories = {}
		selAtoms = _selectedAtoms(atomSpec)
		for atom in selAtoms:
			categories.setdefault(atom.surfaceCategory, set()).add(
								atom.molecule)
		for category, models in categories.items():
			if category in ['ions', 'solvent']:
				continue
			surfaceNew(category, models=models, **kw)
		atoms = _editAtom(atomSpec, _surfaceDisplay)
	surfaceVisibilityByAtom(atoms)

def surfaceVisibilityByAtom(atoms):
	for s in atomMSMSModels(atoms).keys():
		s.visibilityMode = s.ByAtom

def atomMSMSModels(atoms):
	molcat = {}
	from chimera import MSMSModel
	for surf in chimera.openModels.list(modelTypes=[MSMSModel]):
		molcat[(surf.molecule, surf.category)] = surf
	surfatoms = {}
	for a in atoms:
		amc = (a.molecule, a.surfaceCategory)
		if amc in molcat:
			surf = molcat[amc]
			surfatoms.setdefault(surf,[]).append(a)
	return surfatoms

def surfaceCategory(category, sel='sel'):
	def _category(thing, c):
		thing.surfaceCategory = c
	_editAtom(sel, lambda t, c=category, f=_category: f(t, c))

def surfacecolormode(style, sel='sel'):
	mode = None
	if style == "bymodel":
		mode = chimera.MSMSModel.ByMolecule
	elif style == "byatom":
		mode = chimera.MSMSModel.ByAtom
	elif style == "custom":
		mode = chimera.MSMSModel.Custom
	else:
		raise MidasError('Unknown surface color mode "%s"' % style)
	models = _selectedModels(sel, chimera.MSMSModel)
	for m in models:
		m.colorMode = mode
surfacecolourmode = surfacecolormode

def surfacerepresent(style, sel='sel'):
	mode = None
	if style == "filled" or style == "solid":
		mode = chimera.MSMSModel.Filled
	elif style == "mesh":
		mode = chimera.MSMSModel.Mesh
	elif style == "dot":
		mode = chimera.MSMSModel.Dot
	else:
		raise MidasError('Unknown surface representation style "%s"'
								% style)
	models = _selectedModels(sel, chimera.MSMSModel)
	for m in models:
		m.drawMode = mode

def surfacetransparency(val, sel='sel', frames=None):
	if not val is None:
		val = (100.0 - val) / 100.0
	atoms = _selectedAtoms(sel)
	plist = _selectedSurfacePieces(sel)
	if plist:
		# Exclude MSMS surfaces with selected atoms.
		molecules = set([a.molecule for a in atoms])
		mlist = set([p.model for p in plist])
		msmsbyatom = [m for m in mlist 
			      if (isinstance(m, chimera.MSMSModel) and
				  m.colorMode == m.ByAtom and
				  m.molecule in molecules)]
		plist = [p for p in plist if not p.model in msmsbyatom]
	if frames is None or frames < 2:
		_surftransp(val, atoms, plist)
	else:
		def cb(frac, val=val, atoms=atoms, plist=plist):
			_surftransp(val, atoms, plist, frac)
		fracs = [(1.0/n,) for n in range(frames,0,-1)]
		fracs[-1] = (1,)
		addNewFrameCallback(cb, fracs)

def addNewFrameCallback(func, fargs):
	def call(tname, cdata, fnum):
		f, fargs, h = cdata
		if len(fargs) == 0:
			chimera.triggers.deleteHandler('new frame', h)
		else:
			args = fargs[0]
			params[1] = fargs[1:]
			f(*args)
	params = [func, fargs, None]
	params[2] = chimera.triggers.addHandler('new frame', call, params)

def _surftransp(opac, atoms, plist, frac=1):
	_adjustAtomsSurfaceOpacity(atoms, opac, frac)
	if opac is None:
		opac = 1.0
	from chimera import actions
	for p in plist:
		actions.adjustSurfacePieceTransparency(p, opac, frac)

def _adjustAtomsSurfaceOpacity(atoms, opac, frac):
	if opac is None:
		if frac == 1:
			for a in atoms:
				a.surfaceOpacity = -1.0
		else:
			for a in atoms:
				asop, aop = _atomSurfaceOpacity(a)
				a.surfaceOpacity = frac*aop + (1-frac)*asop
	elif frac == 1:
		for a in atoms:
			a.surfaceOpacity = opac
	else:
		for a in atoms:
			asop, aop = _atomSurfaceOpacity(a)
			a.surfaceOpacity = frac*opac + (1-frac)*asop

def _atomSurfaceOpacity(atom):
	c = atom.surfaceColor
	if c is None:
		c = atom.color
		if c is None:
			c = atom.molecule.color
	aop = c.opacity
	asop = atom.surfaceOpacity
	if asop < 0:
		asop = aop
	return asop, aop

def swapres(newRes, sel='sel', preserve=False, bfactor=None):
	from SwapRes import swap, BackboneError
	newRes = newRes.upper()
	selResidues = _selectedResidues(sel)
	if not selResidues:
		raise MidasError("No residues specified for swapping")
	for res in selResidues:
		try:
			swap(res, newRes, preserve=preserve, bfactor=bfactor)
		except BackboneError, v:
			raise MidasError(v)
		if res.label:
			res.label = '%s %s' % (res.type, res.id)
swapna = swapres
swapaa = swapres

def tColor(index, sel='sel'):
	if not currentTexture:
		textureNew('default')

	index, atomItems, resItems = _colorSplit(index)

	if index in ['byatom', 'byelement', 'byhet', 'byhetero']:
		raise MidasError('Cannot texture color byatom/byhet'
					' (too many colors required)')
	try:
		color = currentTexture.color(index)
	except KeyError:
		from chimera import UserError
		raise UserError('Texture color "%s" is undefined' % index)

	if atomItems:
		def _color(thing, items=atomItems, color=color):
			for item in atomItems:
				setattr(thing, item, color)
		_editAtom(sel, _color)

	if resItems:
		def _color(thing, items=resItems, color=color):
			for item in items:
				setattr(thing, item, color)
		_editResidue(sel, _color)
				
def textureColor(index, color):
	if not currentTexture:
		textureNew('default')

	currentTexture.setColor(index, color)
textureColour = textureColor

def textureMap(**kw):
	if not currentTexture:
		textureNew('default')

	for key in kw.keys():
		if key[:5] != "color":
			raise TypeError, "Unexpected keyword argument: " + key
		try:
			index = int(key[5:])
		except ValueError:
			raise TypeError, "Unexpected keyword argument: " + key
		
		if index < 1 or index > len(currentTexture.textureColors):
			raise IndexError, \
			  "Index (%d) out of bounds for current texture" % index
		currentTexture.mapName(index, kw[key])

		# if the name is a color name, set the index to that color
		c = chimera.Color.lookup(kw[key])
		if c is not None:
			currentTexture.setColor(index, c)


def textureNew(name, numColors=5):
	import Texturer
	global currentTexture

	if textures.has_key(name):
		raise AttributeError, "Texture named "+name+" already exists"

	if numColors == 5:
		currentTexture = Texturer.FiveColorTexture()
	elif numColors == 4:
		currentTexture = Texturer.FourColorTexture()
	else:
		raise ValueError, "Number of colors for texture must be 4 or 5"

	# allow for integer strings to be used as indices
	for i in range(1, len(currentTexture.textureColors)+1):
		currentTexture.mapName(i, str(i))
	textures[name] = currentTexture

def textureUse(name):
	global currentTexture
	if not currentTexture:
		textureNew('default')

	try:
		currentTexture = textures[name]
	except KeyError:
		raise KeyError, "No texture named '" + name + "' exists"
	
def thickness(delta, frames=None):
	param = {'command':'thickness', 'plane':'thickness', 'delta':delta/2.0,
							'frames':frames}
	if frames is None:
		_clip(None, param, None)
	else:
		_addMotionHandler(_clip, param)

def turn(axis, angle=3, frames=None, coordinateSystem=None, models=None,
	 center=None):
	v = _axis(axis)
	param = {'command':'turn',
		 'xform':chimera.Xform.rotation(v, angle),
		 'frames':frames,
		 'coordinateSystem':coordinateSystem,
		 'models':models,
		 'center':center}
	if frames is None:
		_movement(None, param, None)
	else:
		_addMotionHandler(_movement, param)

def unbond(sel='sel'):
	atoms = _selectedAtoms(sel, asDict=True)
	for a1 in atoms:
		for a2, b in a1.bondsMap.items():
			if a2 in atoms:
				a1.molecule.deleteBond(b)

def unbondcolor(sel='sel'):
	atoms = _selectedAtoms(sel)
	for b in misc.bonds(atoms, internal=True):
		b.color = None
		b.halfbond = True
unbondcolour = unbondcolor

def unchimeraSelect(sel='sel'):
	if not isinstance(sel, selection.Selection):
		sel = evalSpec(sel)
	if not hasattr(sel, 'addImplied'):
		newSel = selection.ItemizedSelection()
		newSel.merge(selection.REPLACE, sel)
		sel = newSel
	sel.addImplied(vertices=0)
	# ~select implies removal, regardless of selection mode
	selection.mergeCurrent(selection.REMOVE, sel)

def unclip(plane):
	for mh in _motionHandlers[:]:
		if mh['command'] == 'clip' and mh['plane'] == plane:
			_removeMotionHandler(mh)
	
def uncofr():
	from chimera import viewing
	chimera.openModels.cofrMethod = viewing.defaultCofrMethod

def uncolor(which, sel='sel'):
	"""Clear atom color"""
	atomItems, resItems = _colorItems(which)
	if atomItems:
		def _uncolor(thing, items=atomItems):
			for item in items:
				setattr(thing, item, None)
		_editAtom(sel, _uncolor)
	if resItems:
		def _uncolor(thing, items=resItems):
			for item in items:
				setattr(thing, item, None)
		_editResidue(sel, _uncolor)
uncolour = uncolor

def undisplay(sel='sel'):
	"""Undisplay atoms

	Atoms specification may come from either a selection or
	an osl string.  If no atom specification is supplied,
	the current selection is undisplayed."""
	def _undisplay(thing):
		thing.display = 0
	_editAtomBond(sel, _undisplay, None)

def undistance(sel='sel'):
	"""Remove distance monitor"""
	if isinstance(sel, basestring):
		if sel == "all":
			for b in DistMonitor.distanceMonitor.pseudoBonds:
				DistMonitor.removeDistance(b)
			return
		sel = evalSpec(sel)
	atoms = sel.atoms()
	if len(atoms) != 2:
		raise MidasError('Exactly two atoms must be selected.  You '
				'selected %d.' % len(atoms))
	try:
		DistMonitor.removeDistance(atoms[0], atoms[1])
	except ValueError, s:
		raise MidasError('Error removing distance: %s.' % s)

def unfillring(sel='sel'):
	"""turn off ring filling"""
	def _fillstyle(thing):
		thing.fillDisplay = False
	_editResidue(sel, _fillstyle)

def unlabel(sel='sel'):
	"""Add label to selected atoms"""
	def _unlabel(thing):
		thing.label = ''
	_editAtom(sel, _unlabel)

def unlongbond():
	from chimera import LONGBOND_PBG_NAME
	from chimera.misc import getPseudoBondGroup
	pbg = getPseudoBondGroup(LONGBOND_PBG_NAME)
	if not pbg.display:
		raise MidasError("Missing segments already hidden."
				" Use longbond to show them.")
	pbg.display = False

def unmodeldisplay(sel='sel'):
	def _unmodeldisplay(thing):
		thing.display = 0
	_editModel(sel, _unmodeldisplay)

def unobjdisplay(sel):
	def _unobjdisplay(thing):
		if not isinstance(thing, chimera.Molecule) \
		and not isinstance(thing, chimera.MSMSModel):
			thing.display = 0
	_editModel(sel, _unobjdisplay)

def unribinsidecolor(which, sel='sel'):
	"""Clear inside ribbon color"""
	def _uncolor(thing):
		thing.ribbonInsideColor = None
	_editMolecule(sel, _uncolor)
unribinsidecolour = unribinsidecolor

def unribbon(sel='sel'):
	def _undisplay(thing):
		thing.ribbonDisplay = 0
	_editResidue(sel, _undisplay)

def unribbackbone(sel='sel'):
	def _unribbackbone(thing):
		thing.ribbonHidesMainchain = 1
	_editMolecule(sel, _unribbackbone)

def unfilldisplay(sel='sel'):
	def _undisplay(thing):
		thing.fillDisplay = False
	_editResidue(sel, _undisplay)

def unrlabel(sel='sel'):
	"""Do not display residue information as part of any atom label"""
	def _residuedisplay(r):
		r.label = ""
	_editResidue(sel, _residuedisplay)

def unrotation(rotID):
	from BondRotMgr import bondRotMgr
	try:
		br = bondRotMgr.rotations[rotID]
	except KeyError:
		raise MidasError("No such bond rotation")
	br.destroy()
	
def unsavepos(name):
	try:
		del positions[name]
	except KeyError:
		raise MidasError("No position named '%s'" % name)

def unscale():
	for mh in _motionHandlers[:]:
		if mh['command'] == 'scale':
			_removeMotionHandler(mh)
	
def unselect(sel='sel'):
	"""Make selected models inactive"""
	def _unselect(thing):
		thing.openState.active = 0
	_editModel(sel, _unselect)

def unsetAutocolor():
	from chimera import preferences
	from chimera.initprefs import MOLECULE_DEFAULT, MOL_AUTOCOLOR
	preferences.set(MOLECULE_DEFAULT, MOL_AUTOCOLOR, 0, asSaved=1)
	preferences.save()
unsetAutocolour = unsetAutocolor

def unsetDepth_cue():
	chimera.viewer.depthCue = False

def unsetIndependent():
	from chimera import viewing
	chimera.openModels.cofrMethod = viewing.defaultCofrMethod

def unsetSilhouette():
	chimera.viewer.showSilhouette = False

def unsetAttr(level, name, sel='sel'):
	selFunc = _attrSelFunc(level)
	for item in selFunc(sel):
		try:
			setattr(item, name, None)
		except TypeError:
			raise MidasError("Cannot set attribute '%s' to None"
								% name)

unshow = undisplay

def unsurface(sel='sel'):
	def _surfaceDisplay(thing):
		thing.surfaceDisplay = 0
	atoms = _editAtom(sel, _surfaceDisplay)
	surfaceVisibilityByAtom(atoms)
	orphan_surfaces = [s for s in _selectedModels(sel, chimera.MSMSModel)
			   if s.molecule is None]
	chimera.openModels.close(orphan_surfaces)

def unvdw(sel='sel'):
	"""Hide point vdw surface of atoms

	Atoms specification may come from either a selection or
	an osl string.  If no atom specification is supplied,
	the current selection is displayed."""
	def _unvdw(thing):
		thing.vdw = 0
	_editAtom(sel, _unvdw)

def unvdwdefine(sel='sel'):
	"""Revert to default VDW radii"""
	def _revertVDW(thing):
		thing.revertDefaultRadius()
	_editAtom(sel, _revertVDW)

def vdw(sel='sel'):
	"""Display point vdw surface of atoms

	Atoms specification may come from either a selection or
	an osl string.  If no atom specification is supplied,
	the current selection is displayed."""
	def _vdw(thing):
		thing.vdw = 1
	_editAtom(sel, _vdw)

def vdwdefine(radius, sel='sel', increment=False):
	"""Change vdw radius"""
	errors = []
	def _vdwdefine(a, radius=radius, increment=increment, errors=errors):
		r = a.residue
		if increment:
			rad = a.radius
			rad += radius
			if rad <= 0.0:
				errors.append(1)
				rad = 0.1
			a.radius = rad
		else:
			a.radius = radius
	_editAtom(sel, _vdwdefine)
	if errors:
		replyobj.error(
			"Some radii too small to decrement; set to 0.1\n")

def vdwdensity(density, sel='sel'):
	"""Change vdw surface point density"""
	def _vdwdensity(thing, density=density):
		thing.vdwDensity = density
	_editMolecule(sel, _vdwdensity)

def version():
	dialogs.display(chimera.tkgui._OnVersionDialog.name)

def _waiting(param):
	return param['frames'] > 0

def wait(frames=-1):
	if frames < 0:
		frames = _motionRemaining()
	if frames <= 0:
		return
	param = {'command':'wait', 'frames':frames}
	_addMotionHandler(_wait, param)
	import chimera.update
	if chimera.nogui:
		app = None
	else:
		app = chimera.tkgui.app
	chimera.update.wait(lambda p=param: _waiting(p), app)

def window(sel='sel'):
	"""Recompute window parameters"""
	if sel == '#':
		chimera.viewer.viewAll(resetCofrMethod=False)
		return
	# mimic chimera.viewer.viewAll with the current selection
	sph = boundingSphere(sel)
	if sph is None:
		raise MidasError("Nothing to window")
	viewSize = sph.radius + 1.5
	v = chimera.viewer
	camera = v.camera
	v.scaleFactor = 1.0
	v.viewSize = viewSize
	camera.center = sph.center.data()
	v.clipping = True
	focal = sph.center[2]
	camera.nearFar = focal + viewSize + 3, focal - viewSize - 3
	camera.focal = focal

def boundingSphere(sel):
	'Return a bounding sphere for the selection'
	s = None
	atoms = _selectedAtoms(sel)
	if atoms:
		pts = [a.xformCoord() for a in atoms]
		valid, s = chimera.find_bounding_sphere(pts)
		assert(valid)
	plist = _selectedSurfacePieces(sel)
	if plist:
		import Surface
		ps = Surface.surface_sphere(plist)
		if ps:
			if s: s.merge(ps)
			else: s = ps
	return s

def windoworigin(xy=None):
	"Return the window origin if no arguments, or set it to (x, y)"
	if chimera.nogui:
		return
	top = chimera.tkgui.app.winfo_toplevel()
	geom = top.wm_geometry()
	parts = geom.split('+')
	if xy is None:
		_showStatus("window origin is %s, %s" % tuple(parts[1:3]))
		return
	new_geom = parts[0] + "+%d+%d" % xy

	top.wm_geometry(new_geom)
	chimera.tkgui.update_windows()
	top.wm_geometry('')

def windowsize(wh=None):
	"Return the window size if no arguments, or set it to (width, height)"
	if wh is None:
		_showStatus("window size is %dx%d" % chimera.viewer.windowSize)
		return
	if chimera.viewer.windowSize == wh:
		return
	width, height = wh
	if chimera.nogui:
		chimera.viewer.windowSize = width, height
		return

	# to restore very small windows (narrower than status line etc.)
	# these contortions seem to be necessary...
	top = chimera.tkgui.app.winfo_toplevel()
	top.wm_geometry('')
	graphics = chimera.tkgui.app.graphics
	graphics.config(width=width, height=height)
	graphics.grid_configure(sticky='')
	top.update_idletasks()
	parent = graphics.winfo_parent()
	if isinstance(parent, str):
		parent = graphics._nametowidget(parent)
	info = graphics.grid_info()
	xywh = parent.grid_bbox(info['row'], info['column'])
	if width == xywh[2] and height == xywh[3]:
		unwindowsize()

def unwindowsize():
	if chimera.nogui:
		return
	chimera.tkgui.app.graphics.grid_configure(sticky='news')

def write(writeModel, relModel, filename, allFrames=False, dispOnly=False,
				selOnly=False, format="pdb", resNum=True, atomTypes="sybyl"):
	"""write a PDB or Mol2 file
	
	   write coordinates relative to relModel position.  If relModel
	   is None, write current coordinates.

	   allFrames controls whether all frames of a trajectory are 
	   written out or just the current frame

	   dispOnly, if true, means to write only displayed atoms

	   selOnly, if true, means to write only selected atoms

	   format should be "pdb" or "mol2"

	   if format is mol2, resNum controls whether residue sequence
	   numbers are included in substructure names.  Ignored if format
	   is pdb. Similarly, if format is mol2, write Sybyl atom types if
	   atomTypes is "sybyl", Amber/GAFF atom types if atomTypes is "gaff"
	   or "amber".
	"""
	if relModel is None:
		xform = chimera.Xform.identity()
	else:
		try:
			xform = relModel.openState.xform
		except AttributeError:
			mList = _getModelsFromId(relModel)
			if len(mList) != 1:
				id, subid = relModel
				if subid is None:
					s = str(id)
				else:
					s = "%d.%d" % (id, subid)
				raise MidasError, "%d model ids match \"%s\"" \
							% (len(mList), s)
			relModel = mList[0]
			xform = relModel.openState.xform
		xform.invert()
	if isinstance(writeModel, list):
		mList = writeModel
	elif isinstance(writeModel, tuple):
		mList = _getModelsFromId(writeModel,
					modelTypes=[chimera.Molecule])
	else:
		mList = [writeModel]
	if format.lower() == "pdb":
		from OpenSave import osOpen
		try:
			f = osOpen(filename, 'w')
			chimera.viewer.pdbWrite(mList, xform, f,
					allFrames=allFrames,
					displayedOnly=dispOnly,
					selectedOnly=selOnly)
		except IOError, v:
			raise MidasError(v)
		f.close()
	else:
		if allFrames:
			raise MidasError("Trajectories cannot be written in"
							" Mol2 format")
		if (dispOnly or selOnly) and not isinstance(mList,
							selection.Selection):
			ml = selection.ItemizedSelection()
			ml.add(mList)
			mList = ml
		if dispOnly:
			ml = selection.ItemizedSelection()
			ml.add([a for a in mList.atoms() if a.display])
			mList = ml
		if selOnly:
			mList.merge(selection.INTERSECT,
						selection.copyCurrent())
		writeGaff = atomTypes in ["gaff", "amber"]
		from WriteMol2 import writeMol2
		try:
			writeMol2(mList, filename, relModel=relModel, resNum=resNum,
						gaffType=writeGaff, gaffFailError=MidasError)
		except IOError, v:
			raise MidasError(v)
	import os
	from os.path import isabs
	if isabs(filename):
		replyobj.status("Wrote %s\n" % filename, log=True)
	else:
		replyobj.status("Wrote %s into %s\n" % (filename, os.getcwd()),
								log=True)

def _getModelsFromId(mid, **kw):
	id, subid = mid
	kw['id'] = id
	if subid is not None:
		kw['subid'] = subid
	mList = chimera.openModels.list(**kw)
	if not mList:
		if subid is None:
			s = str(id)
		else:
			s = "%d.%d" % (id, subid)
		raise MidasError, "no model ids match \"%s\"" % s
	return mList

#
# General utility functions
#
def deleteAtomsBonds(atoms=[], bonds=[]):
	# also called from tkgui
	residues = set()
	for b in bonds:
		b.atoms[0].molecule.deleteBond(b)
	for a in atoms:
		residues.add(a.residue)
		a.molecule.deleteAtom(a)
	mols = set()
	for r in residues:
		if len(r.atoms) == 0:
			mols.add(r.molecule)
			r.molecule.deleteResidue(r)
	nullModels = []
	for m in mols:
		if len(m.atoms) == 0:
			nullModels.append(m)
	if nullModels:
		chimera.openModels.close(nullModels)

def model(n):
	if isinstance(n, basestring):
		mList = _selectedModels[0]
	else:
		mList = chimera.openModels.list(n)
	if len(mList) == 1:
		(m,) = mList
		return m
	return mList
deselect = unselect

textures = {}
currentTexture = None

positions = {}

#
# session save/restore stuff
#

import SimpleSession
def _saveSession(trigger, x, sessionFile):
	def reformatPosition(pos):
		xfDict = {}
		for molId, xf in pos[5].items():
			tr = xf.getTranslation()
			rot = xf.getRotation()
			xfDict[molId] = (tr.data(), rot[0].data() + (rot[1],))
		clipDict = {}
		if len(pos) > 6:
			for m, clipInfo in pos[6].items():
				key = (m.id, m.subid, m.__class__.__name__)
				useClip, plane, useThick, thickness = clipInfo
				origin, normal = plane.origin, plane.normal
				clipDict[key] = (useClip, origin.x, origin.y,
					origin.z, normal.x, normal.y, normal.z,
					useThick, thickness)
		return pos[:5] + (xfDict, clipDict) + pos[7:]
	saveablePositions = {}
	for name, pos in positions.items():
		saveablePositions[name] = reformatPosition(pos)
	restoring_code = \
"""
def restoreMidasBase():
	import chimera
	from SimpleSession import modelMap, modelOffset
	def deformatPosition(pos):
		xfDict = {}
		for molId, xfData in pos[5].items():
			mid, subid = molId
			trData, rotData = xfData
			xf = chimera.Xform.translation(*trData)
			xf.rotate(*rotData)
			xfDict[(mid+modelOffset, subid)] = xf
		try:
			from chimera.misc import KludgeWeakWrappyDict
			clipDict = KludgeWeakWrappyDict("Model")
		except ImportError:
			from weakref import WeakKeyDictionary
			clipDict = WeakKeyDictionary()
		for clipID, clipInfo in pos[6].items():
			mid, subid, className = clipID
			models = [m for m in modelMap.get((mid, subid), [])
					if m.__class__.__name__ == className]
			if not models:
				continue
			useClip, ox, oy, oz, nx, ny, nz, useThick, thickness = clipInfo
			if useClip:
				origin = chimera.Point(ox, oy, oz)
				normal = chimera.Vector(nx, ny, nz)
				plane = chimera.Plane(origin, normal)
			else:
				plane = chimera.Plane()
			for m in models:
				clipDict[m] = (useClip, plane,
							useThick, thickness)
		return pos[:5] + (xfDict, clipDict) + pos[7:]
	formattedPositions = %s
	positions = {}
	for name, fpos in formattedPositions.items():
		positions[name] = deformatPosition(fpos)
	import Midas
	if modelOffset == 0:
		Midas.positions.clear()
	Midas.positions.update(positions)

def delayedMidasBase():
	try:
		restoreMidasBase()
	except:
		reportRestoreError('Error restoring Midas base state')
import SimpleSession
SimpleSession.registerAfterModelsCB(delayedMidasBase)

""" % (repr(saveablePositions))
	sessionFile.write(restoring_code)
chimera.triggers.addHandler(SimpleSession.SAVE_SESSION, _saveSession, None)

def _closeSession(*args):
	positions.clear()
chimera.triggers.addHandler(chimera.CLOSE_SESSION, _closeSession, None)

def _postRestore(*args):
	# reformat old positions to current format
	def reformatPosition(pos):
		xfDict = {}
		for key, xf in pos[5].items():
			if isinstance(key, tuple):
				xfDict[key] = xf
				continue
			if key.__destroyed__:
				continue
			xfDict[(key.id, key.subid)] = xf
		return pos[:5] + (xfDict,) + pos[6:]
	for name, pos in positions.items():
		positions[name] = reformatPosition(pos)
	import SimpleSession
	if not (SimpleSession.mergedSession and'session-start' in positions):
		savepos("session-start")
chimera.triggers.addHandler(SimpleSession.END_RESTORE_SESSION,
							_postRestore, None)

def _atomSpecErrorCheck(f, t):
	from chimera.specifier import pickSynonyms
	if f in pickSynonyms:
		atoms = _selectedAtoms(f, ordered=True)
		half, rem = divmod(len(atoms), 2)
		if rem != 0:
			raise ValueError, "Odd number of atoms selected"
		fAtoms = atoms[0:half]
		tAtoms = atoms[half:]
	else:
		if isinstance(f, (list, tuple, set)):
			fAtoms = f
		else:
			fAtoms = _selectedAtoms(f, ordered=True)
		if isinstance(t, (list, tuple, set)):
			tAtoms = t
		else:
			tAtoms = _selectedAtoms(t, ordered=True)
	if len(fAtoms) != len(tAtoms):
		raise MidasError, "Unequal numbers of atoms chosen for evaluation"
	if len(fAtoms) < 1:
		raise TooFewAtomsError("At least one atom must be selected"
							" from each model")
	nAtom = len(fAtoms)
	fMol = fAtoms[0].molecule
	tMol = tAtoms[0].molecule
	for a in fAtoms[1:]:
		if a.molecule != fMol:
			raise MidasError, "Atoms in each selection must be in the same model"
	for a in tAtoms[1:]:
		if a.molecule != tMol:
			raise MidasError, "Atoms in each selection must be in the same model"
	if fMol == tMol:
		raise MidasError, "Two different models must be selected"
	return (fAtoms, tAtoms, fMol, tMol)

#define element colors (but after graphics initializes...)
def _initElementColors():
	for i, rgb in enumerate([
	[255,255,255], [217,255,255], [204,128,255], [194,255,0],
	[255,181,181], [144,144,144], [48,80,248], [255,13,13],
	[144,224,80], [179,227,245], [171,92,242], [138,255,0],
	[191,166,166], [240,200,160], [255,128,0], [255,255,48],
	[31,240,31], [128,209,227], [143,64,212], [61,255,0],
	[230,230,230], [191,194,199], [166,166,171], [138,153,199],
	[156,122,199], [224,102,51], [240,144,160], [80,208,80],
	[200,128,51], [125,128,176], [194,143,143], [102,143,143],
	[189,128,227], [255,161,0], [166,41,41], [92,184,209],
	[112,46,176], [0,255,0], [148,255,255], [148,224,224],
	[115,194,201], [84,181,181], [59,158,158], [36,143,143],
	[10,125,140], [0,105,133], [192,192,192], [255,217,143],
	[166,117,115], [102,128,128], [158,99,181], [212,122,0],
	[148,0,148], [66,158,176], [87,23,143], [0,201,0],
	[112,212,255], [255,255,199], [217,255,199], [199,255,199],
	[163,255,199], [143,255,199], [97,255,199], [69,255,199],
	[48,255,199], [31,255,199], [0,255,156], [0,230,117],
	[0,212,82], [0,191,56], [0,171,36], [77,194,255],
	[77,166,255], [33,148,214], [38,125,171], [38,102,150],
	[23,84,135], [208,208,224], [255,209,35], [184,184,208],
	[166,84,77], [87,89,97], [158,79,181], [171,92,0],
	[117,79,69], [66,130,150], [66,0,102], [0,125,0],
	[112,171,250], [0,186,255], [0,161,255], [0,143,255],
	[0,128,255], [0,107,255], [84,92,242], [120,92,227],
	[138,79,227], [161,54,212], [179,31,212], [179,31,186],
	[179,13,166], [189,13,135], [199,0,102], [204,0,89],
	[209,0,79], [217,0,69], [224,0,56], [230,0,46],
	[235,0,38]]):
		colordef(chimera.Element(i+1).name, (rgb[0]/255.0,
						rgb[1]/255.0, rgb[2]/255.0))
chimera.registerPostGraphicsFunc(_initElementColors)

def elementColor(element):
	if isinstance(element, chimera.Element):
		sym = element.name
	else:
		sym = element
	c = chimera.Color.lookup(sym)
	if c == None:
		return chimera.Color.lookup("magenta")
	return c

def deduceFileFormat(filename, filters):
	# try to deduce file format from filename
	# by looking for known suffix
	ext = os.path.splitext(filename)[1]
	if ext:
		for format, glob, suffix in filters:
			if isinstance(glob, basestring):
				if glob.endswith(ext):
					return format
			else:
				for g in glob:
					if g.endswith(ext):
						return format
	return None
