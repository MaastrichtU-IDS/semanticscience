# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Axes.py 29265 2009-11-09 20:20:30Z pett $

import chimera
from chimera import replyobj, selection, Point, Vector
from prefs import prefs, AXIS_RADIUS

from Geometry import Geometry, GeometrySubmanager
class Axis(Geometry):
	def __init__(self, number, name, color, radius,
						sameAs, center, vec, extents):
		Geometry.__init__(self, number)
		self.name = name
		self.radius = radius
		self.extents = extents
		self.center = center
		self.direction = vec
		from StringIO import StringIO
		end1 = center + vec * extents[0]
		end2 = center + vec * extents[1]
		bild = StringIO(".cylinder %g %g %g %g %g %g %g\n"
				% (end1[0], end1[1], end1[2],
				end2[0], end2[1], end2[2], radius))
		self.model = chimera.openModels.open(bild, type="Bild",
				sameAs=sameAs, hidden=True, identifyAs=name)[0]
		self.model.oslIdent = lambda *args: self.name
		self.model.color = color

	def __str__(self):
		return self.name

	@property
	def atoms(self):
		return axisManager.axisAtoms(self)

	def destroy(self, checkForChanges):
		chimera.openModels.close([self.model],
					checkForChanges=checkForChanges)

	@property
	def length(self):
		return abs(self.extents[1] - self.extents[0])

	def pointDistances(self, target):
		if isinstance(target, chimera.Point):
			points = [target]
		else:
			points = target
		from chimera import cross, Plane
		dists = []
		minExt = min(self.extents)
		maxExt = max(self.extents)
		xfCenter = self.xformCenter()
		xfDirection = self.xformDirection()
		minPt = xfCenter + xfDirection * minExt
		maxPt = xfCenter + xfDirection * maxExt
		for pt in points:
			v = pt - xfCenter
			c1 = cross(v, xfDirection)
			if c1.length == 0.0:
				# colinear
				inPlane = pt
			else:
				plane = Plane(xfCenter, cross(c1, xfDirection))
				inPlane = plane.nearest(pt)
			ptExt = (inPlane - xfCenter) * xfDirection
			if ptExt < minExt:
				measurePt = minPt
			elif ptExt > maxExt:
				measurePt = maxPt
			else:
				measurePt = inPlane
			dists.append(pt.distance(measurePt))
		return dists

	def xformCenter(self):
		return self.model.openState.xform.apply(self.center)

	def xformDirection(self):
		return self.model.openState.xform.apply(self.direction)

	def _axisDistance(self, axis, infinite=False):
		from chimera import angle, cross, Plane
		# shortest distance between lines is perpendicular to both...
		sDir = self.xformDirection()
		aDir = axis.xformDirection()
		if angle(sDir, aDir) in [0.0, 180.0]:
			# parallel
			return self._axisEndsDist(axis)
		shortDir = cross(sDir, aDir)
		# can use analytically shortest dist only if each axis
		# penetrates the plane formed by the other axis and the
		# perpendicular
		if not infinite:
			for a1, a2 in [(axis, self), (self, axis)]:
				normal = cross(a1.xformDirection(), shortDir)
				plane = Plane(a1.xformCenter(), normal)
				d1 = plane.distance(a2.xformCenter()
					+ a2.xformDirection() * a2.extents[0])
				d2 = plane.distance(a2.xformCenter()
					+ a2.xformDirection() * a2.extents[1])
				if cmp(d1, 0.0) == cmp(d2, 0.0):
					# both ends on same side of plane
					return self._axisEndsDist(axis)
		# D is perpendicular distance to origin
		d1 = Plane(self.xformCenter(), shortDir).equation()[3]
		d2 = Plane(axis.xformCenter(), shortDir).equation()[3]
		return abs(d1 - d2)

	def _axisEndsDist(self, axis):
		return min(
			min(self.pointDistances([axis.xformCenter() +
						axis.xformDirection() * ext
						for ext in axis.extents])),
			min(axis.pointDistances([self.xformCenter() +
						self.xformDirection() * ext
						for ext in self.extents]))
		)

class AxisManager(GeometrySubmanager):
	def __init__(self):
		self.axisData = {}
		from Geometry import geomManager
		geomManager.registerManager(self, Axis)

	@property
	def axes(self):
		axes = self.axisData.keys()
		return axes
	items = axes

	def axisAtoms(self, axis):
		return self.axisData[axis].atoms()

	def createAxis(self, name, atoms, number=None, radius=None,
				color=None, sourceModel=None,
				helicalCorrection=True, massWeighting=False):
		if len(atoms) < 3:
			raise ValueError("Need at least 3 atoms to define axis")
		numbers = dict([(a.number, a) for a in self.axes])
		if number == None:
			if numbers:
				number = max(numbers.keys()) + 1
			else:
				number = 1
		elif number in numbers:
			self.removeAxes([numbers[number]])

		if color == None:
			from StructMeasure import matchStructureColor
			color = matchStructureColor(atoms)
		if sourceModel == None:
			sourceModel = self._getSourceModel(atoms)
		axisKw = {}
		if massWeighting:
			from numpy import array
			axisKw['weights'] = array([a.element.mass for a in atoms])
		import StructMeasure
		if radius == None:
			pt, vec, b1, b2, radius = StructMeasure.axis(
					chimera.numpyArrayFromAtoms(atoms),
					findBounds=True, findRadius=True,
					iterate=helicalCorrection, **axisKw)
		else:
			pt, vec, b1, b2 = StructMeasure.axis(
					chimera.numpyArrayFromAtoms(atoms),
					findBounds=True, findRadius=False,
					iterate=helicalCorrection, **axisKw)
		replyobj.info("%s has radius %g\n" % (name, radius))
		return self._instantiateAxis(number, name, color,
				radius, sourceModel, atoms, pt, vec, (b1, b2))
		
	def removeAxes(self, axes, checkForChanges=True):
		for axis in axes:
			del self.axisData[axis]
			axis.destroy(checkForChanges)
		from Geometry import geomManager
		geomManager.removeInterfaceItems(axes)
	removeItems = removeAxes

	def _instantiateAxis(self, number, name, color, radius, sourceModel,
						atoms, center, vec, extents):
		axis = Axis(number, name, color, radius,
					sourceModel, center, vec, extents)
		from chimera.selection import ItemizedSelection
		sel = ItemizedSelection(selChangedCB=lambda a=axis:
				self.removeAxes([a], checkForChanges=False))
		sel.add(atoms)
		self.axisData[axis] = sel

		from Geometry import geomManager
		geomManager.addInterfaceItems([axis])
		return axis

	def _restoreSession(self, axisData, fromGeom=False):
		from SimpleSession import getColor, idLookup
		for i, data in enumerate(axisData.keys()):
			atomIDs = axisData[data]
			try:
				number, name, cmpVal, radius, colorID, extents, center,\
							direction = data
			except ValueError:
				number = i + 1
				name, cmpVal, radius, colorID, extents, center,\
							direction = data
			atoms = [idLookup(a) for a in atomIDs]
			self._instantiateAxis(number, name, getColor(colorID), radius,
				self._getSourceModel(atoms), atoms, Point(*center),
				Vector(*direction), extents)

	def _sessionData(self):
		from SimpleSession import sessionID, colorID
		axisData = {}
		for axis, sel in self.axisData.items():
			axisData[(
				axis.number,
				axis.name,
				0, # used to be cmpVal
				axis.radius,
				colorID(axis.model.color),
				axis.extents,
				axis.center.data(),
				axis.direction.data()
			)] = [sessionID(a) for a in sel.atoms()]
		return axisData

axisManager = AxisManager()

from chimera.baseDialog import ModelessDialog
class CreateAxesDialog(ModelessDialog):
	title = "Define Axes"
	help = "ContributedSoftware/structuremeas/structuremeas.html#define-axes"
	provideStatus = True
	statusPosition = "above"

	MODE_HELICES, MODE_SELECTION = range(2)

	def fillInUI(self, parent):
		import Pmw, Tkinter
		row = 0
		Tkinter.Label(parent, text="Create axis for...").grid(
							row=row, sticky='w')
		row += 1
		self.modeVar = Tkinter.IntVar(parent)
		self.modeVar.set(self.MODE_HELICES)
		f = Tkinter.Frame(parent)
		f.grid(row=row, sticky='nsew')
		row += 1
		Tkinter.Radiobutton(f, text="Each helix in:",
				command=self._helixCB, variable=self.modeVar,
				value=self.MODE_HELICES).grid(row=0, column=0)
		from chimera.widgets import MoleculeScrolledListBox
		self.molList = MoleculeScrolledListBox(f,
						listbox_selectmode='extended')
		self.molList.grid(row=0, column=1, sticky="nsew")
		parent.rowconfigure(1, weight=1)
		parent.columnconfigure(0, weight=1)
		f.rowconfigure(0, weight=1)
		f.columnconfigure(1, weight=1)
		f = Tkinter.Frame(parent)
		f.grid(row=row, sticky='w')
		row += 1
		Tkinter.Radiobutton(f, text="Selected atoms (axis name:",
				command=self._selCB, variable=self.modeVar,
				value=self.MODE_SELECTION).grid(row=0, column=0)
		self.axisNameVar = Tkinter.StringVar(parent)
		self.axisNameVar.set("axis")
		Tkinter.Entry(f, textvariable=self.axisNameVar, width=10
				).grid(row=0, column=1)
		Tkinter.Label(f, text=")").grid(row=0, column=2)

		paramGroup = Pmw.Group(parent, tag_text="Axis Parameters")
		paramGroup.grid(row=row, column=0)
		row += 1
		paramFrame = paramGroup.interior()
		prow = 0

		butFrame = Tkinter.Frame(paramFrame)
		butFrame.grid(row=prow, column=0, columnspan=3)
		prow += 1

		self.massWeighting = Tkinter.IntVar(parent)
		self.massWeighting.set(False)
		self._mwButton = Tkinter.Checkbutton(butFrame,
				command=self._mwCB, text="Mass weighting",
				variable=self.massWeighting)
		self._mwButton.grid(row=0, column=0, sticky='w')
		self._mwButton.grid_remove()

		self.helixCorrection = Tkinter.IntVar(parent)
		self.helixCorrection.set(True)
		Tkinter.Checkbutton(butFrame, text="Use helical correction",
			command=self._hcCB, variable=self.helixCorrection
			).grid(row=1, column=0, sticky='w')
		
		self.replaceExisting = Tkinter.IntVar(parent)
		self.replaceExisting.set(True)
		Tkinter.Checkbutton(butFrame, text="Replace existing axes",
				variable=self.replaceExisting).grid(
				row=2, column=0, sticky='w')

		f = Tkinter.Frame(paramFrame)
		f.grid(row=prow, column=0, columnspan=3)
		prow += 1
		from chimera.tkoptions import ColorOption, FloatOption
		self.colorOpt = ColorOption(f, prow, "Color", None,
			None, balloon="Axis color.  If No Color, then the axis"
			" will be colored to match the structure")

		Tkinter.Label(paramFrame, text="Radius:").grid(
						row=prow, column=0, rowspan=2)
		self.fixedRadiusVar = Tkinter.IntVar(parent)
		self.fixedRadiusVar.set(False)
		Tkinter.Radiobutton(paramFrame, variable=self.fixedRadiusVar,
			padx=0, value=False).grid(row=prow, column=1)
		Tkinter.Label(paramFrame, text="average axis-atom distance"
					).grid(row=prow, column=2, sticky='w')
		Tkinter.Radiobutton(paramFrame, variable=self.fixedRadiusVar,
			padx=0, value=True).grid(row=prow+1, column=1)
		f = Tkinter.Frame(paramFrame)
		f.grid(row=prow+1, column=2, sticky='w')
		self.radiusOpt = FloatOption(f, 0, "angstroms",
					prefs[AXIS_RADIUS], None, min=0.01)
	def Apply(self):
		from chimera import UserError
		if self.replaceExisting.get():
			axisManager.removeAxes(axisManager.axes)
		kw = {}
		kw['color'] = self.colorOpt.get()
		if self.fixedRadiusVar.get():
			kw['radius'] = prefs[AXIS_RADIUS] = self.radiusOpt.get()
		kw['massWeighting'] = self.massWeighting.get() \
				and self.modeVar.get() == self.MODE_SELECTION
		kw['helicalCorrection'] = self.helixCorrection.get() \
				and not kw['massWeighting']
		if kw['helicalCorrection']:
			replyobj.info("Creating axes with helical correction\n")
		elif kw['massWeighting']:
			replyobj.info("Creating axes with mass weighting\n")
		else:
			replyobj.info("Creating axes\n")
		if self.modeVar.get() == self.MODE_HELICES:
			mols = self.molList.getvalue()
			if not mols:
				self.enter()
				raise UserError("No molecules chosen")
			created = 0
			for m in mols:
				createHelices(m, **kw)
		else:
			selAtoms = selection.currentAtoms()
			if len(selAtoms) < 3:
				self.enter()
				raise UserError("Need to select at least three"
						" atoms to define an axis")
			axisManager.createAxis(self.axisNameVar.get().strip(),
								selAtoms, **kw)
	def _helixCB(self):
		self._mwButton.grid_remove()

	def _hcCB(self):
		if self.helixCorrection.get() and self.massWeighting.get():
			self.massWeighting.set(False)

	def _mwCB(self):
		if self.massWeighting.get() and self.helixCorrection.get():
			self.helixCorrection.set(False)

	def _selCB(self):
		self._mwButton.grid()

def createHelices(m, **kw):
	from chimera.specifier import evalSpec
	sel = evalSpec(":/isHelix & backbone.minimal", models=[m])
	residues = sel.residues()
	if not residues:
		return []
	from chimera.misc import oslCmp
	residues.sort(lambda r1, r2: oslCmp(r1.oslIdent(), r2.oslIdent()))
	from chimera import bondsBetween
	from chimera.selection import INTERSECT, ItemizedSelection
	curHelix = []
	axes = []
	from Geometry import geomManager
	geomManager.suspendUpdates()
	while residues:
		if not curHelix:
			r = residues.pop(0)
			curHelix.append(r)
			helixNum = r.ssId
			continue
		if helixNum > -1:
			if helixNum == residues[0].ssId:
				curHelix.append(residues.pop(0))
				continue
		elif bondsBetween(curHelix[-1], residues[0], True):
			curHelix.append(residues.pop(0))
			continue
		resSel = ItemizedSelection()
		resSel.add(curHelix)
		resSel.merge(INTERSECT, sel)
		atoms = resSel.atoms()
		if helixNum < 0:
			created += 1
			helixNum = created
		hname = "%s H%d" % (m.name, helixNum)
		axes.append(axisManager.createAxis(hname, atoms, **kw))
		curHelix = []
	if curHelix:
		resSel = ItemizedSelection()
		resSel.add(curHelix)
		resSel.merge(INTERSECT, sel)
		atoms = resSel.atoms()
		if helixNum < 0:
			created += 1
			helixNum = created
		hname = "%s H%d" % (m.name, helixNum)
		axes.append(axisManager.createAxis(hname, atoms, **kw))
	geomManager.enableUpdates()
	return axes
