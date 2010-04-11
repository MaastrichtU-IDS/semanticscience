# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Axes.py 28652 2009-08-24 23:21:53Z pett $

import chimera
from chimera import replyobj, selection, Point, Vector
from prefs import prefs, defaults, PLANE_THICKNESS

from Geometry import Geometry, GeometrySubmanager
class Plane(Geometry):
	def __init__(self, number, name, color, radius, thickness, sameAs, plane):
		Geometry.__init__(self, number)
		self.name = name
		self.radius = radius
		self.thickness = thickness
		self.plane = plane
		from StringIO import StringIO
		vec = plane.normal * (thickness/2.0)
		end1 = plane.origin + vec
		end2 = plane.origin - vec
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
		return planeManager.planeAtoms(self)

	def destroy(self, checkForChanges):
		chimera.openModels.close([self.model], checkForChanges=checkForChanges)

	def pointDistances(self, target, signed=False):
		if isinstance(target, chimera.Point):
			points = [target]
		else:
			points = target
		measurePlane = chimera.Plane(self.xformOrigin(), self.xformNormal())
		if signed:
			return [measurePlane.distance(pt) for pt in points]
		return [abs(measurePlane.distance(pt)) for pt in points]

	def xformOrigin(self):
		return self.model.openState.xform.apply(self.plane.origin)

	def xformNormal(self):
		return self.model.openState.xform.apply(self.plane.normal)

class PlaneManager(GeometrySubmanager):
	def __init__(self):
		self.planeData = {}
		self.planeOrdinal = 0
		from Geometry import geomManager
		geomManager.registerManager(self, Plane)

	@property
	def planes(self):
		planes = self.planeData.keys()
		return planes
	items = planes

	def planeAtoms(self, plane):
		return self.planeData[plane].atoms()

	def createPlane(self, name, atoms, number=None, radius=None,
				radiusOffset=0.0, color=None, sourceModel=None,
				thickness=defaults[PLANE_THICKNESS]):
		if len(atoms) < 3:
			raise ValueError("Need at least 3 atoms to define plane")
		numbers = dict([(pl.number, pl) for pl in self.planes])
		if number == None:
			if numbers:
				number = max(numbers.keys()) + 1
			else:
				number = 1
		elif number in numbers:
			self.removePlanes([numbers[number]])

		if color == None:
			from StructMeasure import matchStructureColor
			color = matchStructureColor(atoms)
		if sourceModel == None:
			sourceModel = self._getSourceModel(atoms)
		import StructMeasure
		if radius == None:
			plane, proj, radius = StructMeasure.plane(
					chimera.numpyArrayFromAtoms(atoms), findBounds=True)
			radius += radiusOffset
		else:
			plane = StructMeasure.plane(
					chimera.numpyArrayFromAtoms(atoms), findBounds=False)
		replyobj.info("%s has radius %g\n" % (name, radius))
		self.planeOrdinal += 1
		return self._instantiatePlane(number, name, self.planeOrdinal, color,
				radius, thickness, sourceModel, atoms, plane)
		
	def removePlanes(self, planes, checkForChanges=True):
		for plane in planes:
			del self.planeData[plane]
			plane.destroy(checkForChanges)
		if not self.planeData:
			self.planeOrdinal = 0
		from Geometry import geomManager
		geomManager.removeInterfaceItems(planes)
	removeItems = removePlanes

	def _instantiatePlane(self, number, name, cmpVal, color, radius,
			thickness, sourceModel, atoms, chimeraPlane):
		plane = Plane(number, name, color, radius,
					thickness, sourceModel, chimeraPlane)
		from chimera.selection import ItemizedSelection
		sel = ItemizedSelection(selChangedCB=lambda pl=plane:
				self.removePlanes([pl], checkForChanges=False))
		sel.add(atoms)
		self.planeData[plane] = sel

		from Geometry import geomManager
		geomManager.addInterfaceItems([plane])
		return plane

	def _restoreSession(self, planeData, fromGeom=False):
		from SimpleSession import getColor, idLookup
		maxNumber = 0
		for data, atomIDs in planeData.items():
			number, name, cmpVal, radius, thickness, colorID, origin, normal\
															= data
			atoms = [idLookup(a) for a in atomIDs]
			self._instantiatePlane(number, name, self.planeOrdinal + number,
							getColor(colorID), radius, thickness,
							self._getSourceModel(atoms), atoms,
							chimera.Plane(Point(*origin), Vector(*normal)))
			maxNumber = max(number, maxNumber)
		self.planeOrdinal += maxNumber

	def _sessionData(self):
		from SimpleSession import sessionID, colorID
		planeData = {}
		for plane, sel in self.planeData.items():
			planeData[(
				plane.number,
				plane.name,
				0, # used to be cmpVal
				plane.radius,
				plane.thickness,
				colorID(plane.model.color),
				plane.plane.origin.data(),
				plane.plane.normal.data()
			)] = [sessionID(a) for a in sel.atoms()]
		return planeData

planeManager = PlaneManager()

from chimera.baseDialog import ModelessDialog
class CreatePlaneDialog(ModelessDialog):
	title = "Define Plane"
	help = "ContributedSoftware/structuremeas/structuremeas.html#define-plane"
	provideStatus = True
	statusPosition = "above"

	def fillInUI(self, parent):
		import Pmw, Tkinter
		row = 0
		Tkinter.Label(parent, text="Create plane for selected atoms...").grid(
							row=row, columnspan=2)
		row += 1

		from chimera.tkoptions import StringOption, BooleanOption
		self.nameOpt = StringOption(parent, row, "Plane name", "plane", None)
		row += 1

		self.replaceExistingOpt = BooleanOption(parent, row,
										"Replace existing planes", False, None)
		row += 1

		from chimera.tkoptions import ColorOption, FloatOption
		self.colorOpt = ColorOption(parent, row, "Color", None, None,
			balloon="Plane color.  If No Color, then the plane"
			" will be colored to match the structure")
		row += 1

		self.autoRadiusOpt = BooleanOption(parent, row,
			"Set disk size to enclose atom projections", True, self._radCB)
		row += 1
		self.radRow = row
		self.radOffsetOpt = FloatOption(parent, row, "Extra radius"
			" (padding)", 0.0, None)
		self.radiusOpt = FloatOption(parent, row, "Fixed radius", 10.0, None)
		self.radiusOpt.forget()
		row += 1

		self.thicknessOpt = FloatOption(parent, row, "Disk thickness",
										prefs[PLANE_THICKNESS], None)

	def Apply(self):
		from chimera import UserError
		if self.replaceExistingOpt.get():
			planeManager.removePlanes(planeManager.planes)
		kw = {
			'color': self.colorOpt.get(),
			'thickness': self.thicknessOpt.get()
		}
		prefs[PLANE_THICKNESS] = kw['thickness']
		if self.autoRadiusOpt.get():
			kw['radiusOffset'] = self.radOffsetOpt.get()
		else:
			kw['radius'] = self.radiusOpt.get()

		replyobj.info("Creating plane\n")
		selAtoms = selection.currentAtoms()
		if len(selAtoms) < 3:
			self.enter()
			raise UserError("Need to select at least three"
					" atoms to define a plane")
		planeManager.createPlane(self.nameOpt.get().strip(), selAtoms, **kw)

	def _radCB(self, opt):
		if opt.get():
			self.radiusOpt.forget()
			self.radOffsetOpt.manage()
		else:
			self.radOffsetOpt.forget()
			self.radiusOpt.manage()
