# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: viewing.py 29694 2010-01-05 23:32:26Z goddard $

import Tkinter as Tk
import Tix
import Pmw
import string
import dialogs, help
import replyobj

import chimera
from chimera import preferences
import tkoptions
from baseDialog import ModelessDialog

defaultCofrMethod = chimera.OpenModels.FrontCenter

moreCategories = []

def addCategory(*args):
	# Takes the same arguments as ViewerDialog.addCategory
	d = dialogs.find(ViewerDialog.name)
	if d is not None:
		d.addCategory(*args)
	else:
		moreCategories.append(args)

class _CameraModeOption(tkoptions.Option):

	order = [
			"mono", "stereo left eye", "stereo right eye",
			"cross-eye stereo", "wall-eye stereo",
			"red-cyan stereo", "sequential stereo",
			"DTI side-by-side stereo", "row interleaved stereo",
	]

	def ordering(self, x, y):
		try:
			i = self.order.index(x)
		except ValueError:
			i = -1
		try:
			j = self.order.index(y)
		except ValueError:
			j = -1
		if i >= 0 and j >= 0:
			return cmp(i, j)
		if i >= 0:
			return -1
		if j >= 0:
			return 1
		return cmp(x, y)

	def _addOption(self, row, col, **kw):
		self._var = Tk.StringVar(self._master)
		self._option = Tk.Menubutton(self._master,
			textvariable=self._var, relief=Tk.RAISED, borderwidth=2)
		if row == -1:
			self._option.pack(side=Tk.RIGHT)
		else:
			self._option.grid(row=row, column=col, sticky=Tk.W)
		self.menu = Tk.Menu(self._option, tearoff=Tk.NO)
		self._option["menu"] = self.menu
		modes = chimera.Camera.modes()
		modes.sort(key=str.lower, cmp=self.ordering)
		for v in modes:
			self.menu.add_radiobutton(label=v, variable=self._var,
						value=v, command=self._set)

	def get(self):
		return self._var.get()

	def set(self, value):
		self._var.set(value)

class _CofrMethodOption(tkoptions.SymbolicEnumOption):
	labels = ('fixed', 'center of models', 'independent', 'center of view',
		  'front center')
	values = (chimera.OpenModels.Fixed,
		  chimera.OpenModels.CenterOfModels,
		  chimera.OpenModels.Independent,
		  chimera.OpenModels.CenterOfView,
		  chimera.OpenModels.FrontCenter,)

class _ProjectionOption(tkoptions.SymbolicEnumOption):
	labels = ('perspective', 'orthographic')
	values = (0, 1)

class UnitOption(tkoptions.EnumOption):
	"""Specialization of EnumOption Class for side"""
	mm = 'millimeters'
	cm = 'centimeters'
	inch = 'inches'
	meters = 'meters'
	feet = 'feet'
	values = (mm, cm, meters, inch, feet)
	convert = {
		'points': 1.0,
		inch: 72.0,
		feet: 72.0 * 12,
		mm: 72.0 / 25.4,
		cm: 72.0 / 2.54,
		meters: 72.0 / 0.0254,
	}

class ResolutionOption(tkoptions.SymbolicEnumOption):
	labels = ('high', 'low')
	values = (False, True)

class ViewOption(tkoptions.EnumOption):
	values = ('right', 'top')

class _DefaultOption(tkoptions.SymbolicEnumOption):
	values = [0, 1, None]
	labels = ["false", "true", "default"]

	def __init__(self, master, row, name, default, callback, **kw):
		# override normal default is None behavior
		tkoptions.SymbolicEnumOption.__init__(self, master, row, name,
							default, callback, **kw)
		if default == None:
			self.default = None
			self.set(self.default)

class ViewerDialog(ModelessDialog):
	"""Control viewer properties."""

	name = 'View Editor'
	title = 'Viewing'
	buttons = ('Reset', 'Restore', 'Save', 'Close',)
	# no default button

	def __init__(self, master=None, viewer=None, *args, **kw):
		self.viewer = viewer
		self.first = True
		ModelessDialog.__init__(self, master, *args, **kw)

	def fillInUI(self, master):
		self.mapped = False
		self.trackViewer = None
		self.trackOpenModels = None
		self.updateCallbacks = {}
		self.mapCallbacks = {}
		self.unmapCallbacks = {}
		self.saveCallbacks = {}
		self.restoreCallbacks = {}
		self.resetCallbacks = {}
		self.unmapCB = None
		self.restoreMap = {}
		pages = [
			( 'Camera', 0, self._addCamera, self._updateCamera,
				self._mapCamera, self._unmapCamera,
				self._saveCamera, self._restoreCamera,
				self._resetCamera),
			( 'Side View', 0, self._addSideView,
			        self._updateSideView,
				self._mapSideView, self._unmapSideView,
				self._saveSideview, self._restoreSideview,
				self._resetSideview),
			( 'Rotation', 0, self._addRotation,
				self._updateRotation, self._mapRotation,
				self._unmapRotation,
				self._saveRotation, self._restoreRotation,
				self._resetRotation),
			( 'Effects', 0, self._addEffects, self._updateEffects,
				self._mapEffects, self._unmapEffects,
				self._saveEffects, self._restoreEffects,
				self._resetEffects),
		]
		self.nb = Tix.NoteBook(master)
		self.nb.pack(fill=Tk.BOTH, expand=1)
		help.register(self._toplevel, "UsersGuide/sideview.html")
		for (name, underline, createF, updateF, mapF, unmapF,
		saveF, restoreF, resetF) in pages:
			anchName = string.lower(name.replace(' ', ''))
			url = "UsersGuide/sideview.html#" + anchName
			self.addCategory(name, underline, createF,
						updateF, mapF, unmapF,
						saveF, restoreF, resetF, url)
		for args in moreCategories:
			self.addCategory(*args)
		del moreCategories[:]
		helpButton = self.buttonWidgets['Help']
		helpButton.config(state='normal', command=self.Help)
		# default to SideView
		self.nb.raise_page('pSideView')

	def addCategory(self, name, underline, create, update, map, unmap,
			save, restore, reset, url):
		tabName = 'p' + name	# names must start w/lowercase
		tabName = tabName.replace(' ', '')	# remove spaces
		self.nb.add(tabName, label=name, underline=underline,
						raisecmd=self.raiseCmd)
		page = self.nb.page(tabName)
		create(self, page)
		if update:
			self.updateCallbacks[tabName] = update
		if map:
			self.mapCallbacks[tabName] = map
		if unmap:
			self.unmapCallbacks[tabName] = unmap
		if url:
			help.register(page, url)
		if save:
			self.saveCallbacks[tabName] = save
		if reset:
			self.resetCallbacks[tabName] = reset
		if restore:
			self.restoreCallbacks[tabName] = restore

	def Help(self):
		# implement our own help, since we want different
		# URLs depending on the current notebook page
		help.display(self.nb.subwidget(self.nb.raised()))

	def raiseCmd(self):
		if not self.mapped:
			return
		self.unmap()	# turn off trigger
		self.map()	# reenable the right trigger and update
		tabName = self.nb.raised()
		def state(d):
			if tabName in d:
				return "normal"
			else:
				return "disabled"
		try:
			self.buttonWidgets["Save"].config(
					state=state(self.saveCallbacks))
			self.buttonWidgets["Restore"].config(
					state=state(self.restoreCallbacks))
			self.buttonWidgets["Reset"].config(
					state=state(self.resetCallbacks))
		except Tk.TclError:
			# This can happen when Chimera exits and the
			# viewing dialog is up.  The buttons are apparently
			# gone when the notebook widget tries to raise
			# this tab.
			pass

	def map(self, event=None):
		"""Turn on tracking of Viewer changes."""
		if event:
			self.mapped = True
		tabName = self.nb.raised()
		try:
			cb = self.mapCallbacks[tabName]
		except KeyError:
			pass
		else:
			cb()
		self.unmapCB = self.unmapCallbacks.get(tabName, None)
		# no need to update the UI contents the first time,
		# because the contents are created with the current values.
		if self.first:
			self.first = False
		else:
			self.update()
		
	def unmap(self, event=None):
		"""Turn off tracking of Viewer changes."""
		if event:
			self.mapped = False
		if self.unmapCB:
			self.unmapCB()
			self.unmapCB = None

	def _mapCamera(self):
		self.trackViewer = chimera.triggers.addHandler('Viewer',
						self._trackViewer, None)
	_mapEffects = _mapCamera
	_mapSideView = _mapCamera

	def _unmapCamera(self):
		if self.trackViewer:
			chimera.triggers.deleteHandler('Viewer',
							self.trackViewer)
			self.trackViewer = None
	_unmapEffects = _unmapCamera
	_unmapSideView = _unmapCamera

	def _mapRotation(self):
		self.trackOpenModels = chimera.triggers.addHandler(
			'OpenModels', self._trackOpenModels, None)

	def _unmapRotation(self):
		if self.trackOpenModels:
			chimera.triggers.deleteHandler('OpenModels',
							self.trackOpenModels)
			self.trackOpenModels = None

	def _trackViewer(self, trigger, closure, viewers):
		if self.viewer in viewers.modified:
			self.update()

	def _trackOpenModels(self, trigger, closure, openModels):
		self.update()

	def update(self):
		page = self.nb.raised()
		# Figure out where the focus is so we don't update
		# the widget that the user is editting.
		try:
			updateFunc = self.updateCallbacks[page]
		except KeyError:
			return
		updateFunc()

	def _updateCamera(self):
		view = self.viewer
		cam = view.camera
		self.cameraMode.set(cam.mode())
		self.cameraOrtho.set(cam.ortho)
		self.scaleFactor.set(view.scaleFactor)
		near, far = cam.nearFar
		self.near.set(near)
		#self.focal.set(cam.focal)
		self.far.set(far)
		self.fov.set(cam.fieldOfView)
		adjust = (UnitOption.convert[UnitOption.mm]
					/ UnitOption.convert[self.units.get()])
		self.eyeSep.set(cam.eyeSeparation * adjust)
		self.screenDistance.set(cam.screenDistance * adjust)

	def _updateSideView(self):
		view = self.viewer
		self.clipVar.set(view.clipping)

	def _updateRotation(self):
		view = self.viewer
		self.cofrMethod.set(chimera.openModels.cofrMethod)
		# need to enable before trying to set value...
		self.cofrPoint.enable()
		try:
			self.cofrPoint.set(chimera.openModels.cofr.data())
		except ValueError:
			# When in Independent Rotation mode,
			# chimera.openModels.cofr.data() throws an exception
			pass
		if self.cofrMethod.get() != chimera.OpenModels.Fixed:
			self.cofrPoint.disable()

	def _updateEffects(self):
		viewer = self.viewer
		dc = viewer.depthCue
		if self.depthcue.get() != dc:
			self.depthcue.set(dc)
			self._depthcueCB()
		if not dc:
			self.startDepth.enable()
			self.endDepth.enable()
			self.fogColor.enable()
		self.startDepth.set(viewer.depthCueRange[0])
		self.endDepth.set(viewer.depthCueRange[1])
		self.fogColor.set(viewer.depthCueColor)
		if not dc:
			self.startDepth.disable()
			self.endDepth.disable()
			self.fogColor.disable()

		s = viewer.showSilhouette
		if self.silhouette.get() != s:
			self.silhouette.set(s)
			self._silhouetteCB()
		if not s:
			self.silhouetteColor.enable()
			self.silhouetteWidth.enable()
		self.silhouetteColor.set(viewer.silhouetteColor)
		self.silhouetteWidth.set(viewer.silhouetteWidth)
		if not s:
			self.silhouetteColor.disable()
			self.silhouetteWidth.disable()

		lod = chimera.LODControl.get()
		self.subdivision.set(lod.quality)
		self.localViewer.set(viewer.localViewer)
		self.bgopacity.set(chimera.bgopacity)
		self.shadows.set(viewer.showShadows)
		if chimera.nomultisample is None:
			multisample = None
		else:
			multisample = not chimera.nomultisample
		self.multisample.set(multisample)

	def _cameraModeCB(self, option):
		mode = option.get()
		if not setCameraMode(mode, self.viewer):
			oldMode = self.viewer.camera.mode()
			option.set(oldMode)

	def _reverseStereoCB(self, option):
		onoff = option.get()
		setReverseStereo(onoff, self.viewer)

	def _orthoCB(self, option):
		ortho = option.get()
		setCameraOrtho(ortho, self.viewer)

	def _scaleCB(self, option):
		scale = option.get()
		self.viewer.scaleFactor = scale

	def _nearCB(self, option):
		v = self.viewer
		c = v.camera
		near, far = c.nearFar
		near = option.get()
		v.clipping = True
		try:
			c.nearFar = near, far
		except ValueError, e:
			from chimera import NonChimeraError
			raise NonChimeraError(str(e))


	#def _focalCB(self, option):
	#	focal = option.get()
	#	self.viewer.camera.focal = focal

	def _farCB(self, option):
		v = self.viewer
		c = v.camera
		near, far = c.nearFar
		far = option.get()
		v.clipping = True
		try:
			c.nearFar = near, far
		except ValueError, e:
			from chimera import NonChimeraError
			raise NonChimeraError(str(e))

	def _addCamera(self, dialog, master):
		if Tk.TkVersion >= 8.5:
			master.tk.call('grid', 'anchor', master._w, 'center')
		cam = self.viewer.camera
		import itertools
		row = itertools.count()
		self.cameraMode = _CameraModeOption(master, row.next(),
				'camera mode', cam.mode(), self._cameraModeCB)
		self.reverseStereo = tkoptions.BooleanOption(master, row.next(),
				'reverse sequential stereo',
				chimera.reverseStereo(), self._reverseStereoCB)
		self.cameraOrtho = _ProjectionOption(master, row.next(),
				'projection', cam.ortho, self._orthoCB)
		self.scaleFactor = tkoptions.FloatOption(master, row.next(),
				'scale factor', self.viewer.scaleFactor,
				self._scaleCB, min=1e-10)
		self.scaleFactor.min = 0.00001
		self.scaleFactor.max = 10000.0
		near, far = cam.nearFar
		self.near = tkoptions.FloatOption(master, row.next(),
				'near plane', near, self._nearCB)
		#self.focal = tkoptions.FloatOption(master, row.next(),
		#		'focal plane', cam.focal,
		#		self._focalCB)
		self.far = tkoptions.FloatOption(master, row.next(),
				'far plane', far, self._farCB)
		self.fov = tkoptions.FloatOption(master, row.next(),
				'horizontal field of view', cam.fieldOfView,
				self._fovCB, min=1, max=179)

		# stereo
		stereo = Pmw.Group(master, tag_text='Stereo parameters')
		stereo.grid(row=row.next(), columnspan=2, sticky='news')
		tmp = stereo.interior()

		self.units = UnitOption(tmp, row.next(),
				'units', UnitOption.inch, self._unitsCB)
		self.previousUnits = UnitOption.inch
		adjust = (UnitOption.convert[UnitOption.mm]
					/ UnitOption.convert[self.units.get()])
		self.eyeSep = tkoptions.FloatOption(tmp, row.next(),
				'eye separation', cam.eyeSeparation * adjust,
				self._eyeSepCB, min=0.01)
		self.screenDistance = tkoptions.FloatOption(tmp, row.next(),
				'distance to screen',
				cam.screenDistance * adjust,
				self._screenDistanceCB, min=1)
		self.screenWidth = tkoptions.FloatOption(tmp, row.next(),
				'screen width',
				getScreenWidth() * adjust,
				self._screenWidthCB, min=0)

		# Set up restore functions
		self.addRestoreFunc("SideCam", "mode",
					self.setOption, self.cameraMode)
		self.addRestoreFunc("SideCam", "reverseStereo",
					self.setOption, self.reverseStereo)
		self.addRestoreFunc("SideCam", "projection",
					self.setOption, self.cameraOrtho)
		self.addRestoreFunc("SideCam", "units",
					self.setOption, self.units)
		self.addRestoreFunc("SideCam", "eyeSep",
					self.setDistance, self.eyeSep)
		self.addRestoreFunc("SideCam", "screenDistance",
					self.setDistance, self.screenDistance)
		self.addRestoreFunc("SideCam", "screenWidth",
					self.setDistance, self.screenWidth)

	def _depthcueCB(self):
		dc = self.depthcue.get()
		setViewerDepthcue(dc, self.viewer)
		if dc:
			self.startDepth.enable()
			self.endDepth.enable()
			self.fogColor.enable()
		else:
			self.startDepth.disable()
			self.endDepth.disable()
			self.fogColor.disable()

	def _startDepthCB(self, option):
		v = self.viewer
		s,e = v.depthCueRange
		s = option.get()
		v.depthCueRange = (s,e)

	def _endDepthCB(self, option):
		v = self.viewer
		s,e = v.depthCueRange
		e = option.get()
		v.depthCueRange = (s,e)

	def _fogColorCB(self, option):
		color = option.get()
		setViewerFogColor(color, self.viewer)

	def  _silhouetteCB(self):
		s = self.silhouette.get()
		setViewerSilhouette(s, self.viewer)
		if s:
			self.silhouetteColor.enable()
			self.silhouetteWidth.enable()
		else:
			self.silhouetteColor.disable()
			self.silhouetteWidth.disable()

	def _silhouetteColorCB(self, option):
		color = option.get()
		setViewerSilhouetteColor(color, self.viewer)

	def _silhouetteWidthCB(self, option):
		width = option.get()
		setViewerSilhouetteWidth(width, self.viewer)

	def _qualityCB(self, option):
		quality = option.get()
		setQuality(quality)

	def _localViewerCB(self, option):
		localViewer = option.get()
		setViewerLocal(localViewer, self.viewer)

	def _bgopacity(self, option):
		bgopacity = option.get()
		save_bgopacity = chimera.bgopacity
		if not setBackgroundOpacity(bgopacity):
			chimera.bgopacity = save_bgopacity
			option.set(save_bgopacity)

	def _shadows(self, option):
		shadows = option.get()
		save_shadows = chimera.viewer.showShadows
		if not setShadows(shadows):
			chimera.viewer.showShadows = save_shadows
			option.set(save_shadows)

	def _multisample(self, option):
		multisample = option.get()
		save_nomultisample = chimera.nomultisample
		if not setMultisample(multisample):
			chimera.nomultisample = save_nomultisample
			if save_nomultisample == None:
				option.set(None)
			else:
				option.set(not save_nomultisample)

	def _addEffects(self, dialog, master):
		left = Tk.Frame(master)
		right = Tk.Frame(master)
		import itertools
		leftrow = itertools.count()
		rightrow = itertools.count()
		left.grid(column=0, row=0, sticky='news')
		right.grid(column=1, row=0, sticky='news')
		if Tk.TkVersion >= 8.5:
			left.tk.call('grid', 'anchor', left._w, 'center')
			right.tk.call('grid', 'anchor', right._w, 'center')
		master.columnconfigure(0, pad=2)
		master.columnconfigure(1, pad=2)
		right.columnconfigure(0, weight=1)

		self.depthcue = Tk.IntVar(left)
		tmp = Pmw.Group(left, tag_pyclass = Tk.Checkbutton,
			tag_text='depth cueing', tag_command=self._depthcueCB,
			tag_variable=self.depthcue)
		tmp.grid(row=leftrow.next(), columnspan=2, sticky='news')
		tmp = tmp.interior()
		tmp.columnconfigure(0, weight=1)
		self.startDepth = tkoptions.FloatOption(tmp, 0,
				'start', 0.5, self._startDepthCB,
				 width=5)
		self.endDepth = tkoptions.FloatOption(tmp, 1,
				'end', 0.1, self._endDepthCB,
				width=5)
		pad = ' '*10	# Pmw.Group() box not big enough for title
				#   in Mac Aqua Chimera, Dec 18, 2009.
		self.fogColor = tkoptions.ColorOption(tmp, 2, pad + 'color',
				self.viewer.depthCueColor, self._fogColorCB)
		if self.viewer.depthCue:
			self.depthcue.set(1)
			self._depthcueCB()

		lod = chimera.LODControl.get()
		self.subdivision = tkoptions.FloatOption(right, rightrow.next(),
			'subdivision quality', lod.quality, self._qualityCB,
			min=1e-2, max=20, width=5)

		self.localViewer = tkoptions.BooleanOption(right,
				rightrow.next(), 'local viewer',
				self.viewer.localViewer, self._localViewerCB)

		self.bgopacity = tkoptions.BooleanOption(right, rightrow.next(),
				'transparent background', chimera.bgopacity,
				self._bgopacity)

		self.shadows = tkoptions.BooleanOption(right, rightrow.next(),
				'show shadows', chimera.viewer.showShadows,
				self._shadows)

		self.silhouette = Tk.IntVar(left)
		tmp = Pmw.Group(left, tag_pyclass = Tk.Checkbutton,
			tag_text='silhouettes', tag_command=self._silhouetteCB,
			tag_variable=self.silhouette)
		tmp.grid(row=leftrow.next(), columnspan=2, sticky='news')
		tmp = tmp.interior()
		tmp.columnconfigure(0, weight=1)
		self.silhouetteColor = tkoptions.ColorOption(tmp, 0, 'color',
			self.viewer.silhouetteColor, self._silhouetteColorCB)
		self.silhouetteWidth = tkoptions.FloatOption(tmp, 1, 'width',
			self.viewer.silhouetteWidth, self._silhouetteWidthCB,
			min=0.01, width=5)
		if self.viewer.showSilhouette:
			self.silhouette.set(1)
		#	self._silhouetteCB()
		#else:
		#	self.silhouetteColor.disable()
		#	self.silhouetteWidth.disable()
		self._silhouetteCB()

		if chimera.nomultisample is None:
			multisample = None
		else:
			multisample = not chimera.nomultisample
		defMulti = _DefaultOption.labels[
			not chimera.tkgui.defaultNoMultisampling(master)]
		self.multisample = _DefaultOption(right, rightrow.next(),
				'multisampling', multisample, self._multisample,
				balloon="default is %s" % defMulti)

		# Set up restore functions
		self.addRestoreFunc("Effects", "depthcue",
					self.setVariable, self.depthcue)
		self.addRestoreFunc("Effects", "startDepth",
					self.setOption, self.startDepth)
		self.addRestoreFunc("Effects", "endDepth",
					self.setOption, self.endDepth)
		self.addRestoreFunc("Effects", "fogColor",
					self.setOption, self.fogColor)
		self.addRestoreFunc("Effects", "subdivision",
					self.setOption, self.subdivision)
		self.addRestoreFunc("Effects", "localViewer",
					self.setOption, self.localViewer)
		self.addRestoreFunc("Effects", "bgopacity",
					self.setOption, self.bgopacity)
		self.addRestoreFunc("Effects", "silhouette",
					self.setVariable, self.silhouette)
		self.addRestoreFunc("Effects", "silhouetteColor",
					self.setOption, self.silhouetteColor)
		self.addRestoreFunc("Effects", "silhouetteWidth",
					self.setOption, self.silhouetteWidth)
		self.addRestoreFunc("Effects", "multisample",
					self.setOption, self.multisample)
		return
		# TODO

		self.multipassAA = tkoptions.BooleanOption(left, leftrow.next(),
				'multipass antialiasing', 0, None)

		# right
		self.depthOfField = tkoptions.BooleanOption(right,
				rightrow.next(), 'depth of field', 0, None)
		self.envmap = tkoptions.BooleanOption(right, rightrow.next(),
				'environment map', 0, None)

		tmp = Tix.LabelFrame(right, label='specular')
		tmp.grid(row=rightrow.next(), columnspan=2, sticky='news')
		tmp = tmp.subwidget('frame')
		self.specularOnTexture = tkoptions.BooleanOption(tmp, 0,
				'on textures', 0, None)
		self.specularQuality = tkoptions.BooleanOption(tmp, 1,
				'high quality', 0, None)

	def _cofrMethodCB(self, option):
		method = option.get()
		setCofrMethod(method)
		if method == chimera.OpenModels.Fixed:
			self.cofrPoint.enable()
		else:
			self.cofrPoint.disable()

	def _cofrPointCB(self, option):
		point = option.get()
		if point is None:
			return	# multiple values
		setCofrPoint(point)

	def _addRotation(self, dialog, master):
		if Tk.TkVersion >= 8.5:
			master.tk.call('grid', 'anchor', master._w, 'center')
		self.cofrMethod = _CofrMethodOption(master, 0,
			'center of rotation method',
			chimera.openModels.cofrMethod, self._cofrMethodCB)
		try:
			x = chimera.openModels.cofr.data()
		except ValueError:
			# When in Independent Rotation mode,
			# chimera.openModels.cofr.data() throws an exception
			x = (0, 0, 0)
		self.cofrPoint = tkoptions.Float3TupleOption(master, 1,
				'rotation center', x, self._cofrPointCB)
		if self.cofrMethod.get() != chimera.OpenModels.Fixed:
			self.cofrPoint.disable()

		# Set up restore functions
		self.addRestoreFunc("Rotation", "center",
					self.setOption, self.cofrPoint)
		self.addRestoreFunc("Rotation", "method",
					self.setOption, self.cofrMethod)

	def _moveEye(self, e):
		import Midas
		Midas.updateZoomDepth(self.viewer)
		try:
			self.sideviewer.moveEye(e.x, e.y, e.state % 2)
		except ValueError:
			raise chimera.LimitationError("refocus to continue scaling")

	def _double1(self, e):
		over = self.sideviewer.over(e.x, e.y)
		if over == chimera.SideViewer.OnEye:
			self.cameraMode.menu.post(e.x_root, e.y_root)

	def _press1(self, e):
		if self.svdrag:
			return
		over = self.sideviewer.over(e.x, e.y)
		if over == chimera.SideViewer.OnNothing:
			return
		sv = self.sideviewer
		if over == chimera.SideViewer.OnEye:
			c = 'eye'
			f = self._moveEye
		elif over == chimera.SideViewer.OnHither:
			c = 'hither'
			f = lambda e, s=sv: s.moveHither(e.x, e.y, e.state % 2)
			self.enableClipping()
		elif over == chimera.SideViewer.OnYon:
			c = 'yon'
			f = lambda e, s=sv: s.moveYon(e.x, e.y, e.state % 2)
			self.enableClipping()
		elif over == chimera.SideViewer.OnFocal:
			c = 'focal'
			f = lambda e, s=sv: s.moveFocal(e.x, e.y, e.state % 2)
		elif over == chimera.SideViewer.OnLowFOV:
			c = 'eye'
			f = lambda e, s=sv: s.moveLowFOV(e.x, e.y, e.state % 2)
		elif over == chimera.SideViewer.OnHighFOV:
			c = 'eye'
			f = lambda e, s=sv: s.moveHighFOV(e.x, e.y, e.state % 2)
		else:
			# should never get here
			c = None
			f = None
		sv.setCursor(c)
		self.svdrag = f

	def _press2(self, e):
		if self.svdrag:
			return
		over = self.sideviewer.over(e.x, e.y)
		if over == chimera.SideViewer.OnNothing:
			return
		sv = self.sideviewer
		if over == chimera.SideViewer.OnEye:
			c = 'eye'
			if sv.advancedUI:
				f = lambda e, s=sv: s.moveEyeDist(e.x, e.y, e.state % 2)
			else:
				f = self._moveEye
		elif over == chimera.SideViewer.OnHither:
			c = 'section'
			f = lambda e, s=sv: s.section(e.x, e.y, e.state % 2)
			self.enableClipping()
		elif over == chimera.SideViewer.OnYon:
			c = 'thickness'
			f = lambda e, s=sv: s.thickness(e.x, e.y, e.state % 2)
			self.enableClipping()
		elif over == chimera.SideViewer.OnFocal:
			c = 'focal'
			f = lambda e, s=sv: s.moveFocal(e.x, e.y, e.state % 2)
		else:
			# should never get here
			c = None
			f = None
		sv.setCursor(c)
		self.svdrag = f

	def _drag(self, e):
		if self.svdrag:
			self.svdrag(e)

	def _release(self, e):
		if self.svdrag != None:
			self.sideviewer.setCursor(None)
			self.svdrag = None

	def _viewCB(self, option):
		view = option.get()
		self.sideviewer.advancedUI = (view == 'top')

	def _lowResCB(self, option):
		lowRes = option.get()
		self.sideviewer.lowRes = lowRes

	def _addSideView(self, dialog, master):
		self.svdrag = None
		self.sideviewer = sv = chimera.SideViewer(self.viewer)
		kw = {
			"width": 1, "height": 1, "sharelist": "main",
			"double": True, "rgba": True, "depth": True,
			# assume chimera.nomultisample is already set
			"multisample": not chimera.nomultisample,
			# only need alpha to match Togl in main window,
			# and thus guarantee we can share display lists
			"alpha": chimera.bgopacity,
			"createcommand": sv.createCB,
			"displaycommand": sv.displayCB,
			"reshapecommand": sv.reshapeCB,
			"destroycommand": sv.destroyCB,
		}
		master.grid_rowconfigure(0, weight=1)
		master.grid_columnconfigure(1, weight=1)
		import Togl
		try:
			self.graphics = Togl.Togl(master, **kw)
		except Tk.TclError, what:
			from chimera import NonChimeraError
			e = str(what)
			if e.startswith("unable to share display lists"):
				text = ("Unable to share graphics data"
						" with main window.\n"
					"Upgrade your video/graphics driver.")
				replyobj.warning(text)
				del kw['sharelist']
				self.graphics = Tk.Label(master, text=text,
						bg='black', fg='white')
			else:
				if "configure togl widget" in e:
					raise NonChimeraError(
					"Unable to create second graphics window.\n"
					"Please update your video/graphics\n"
					"driver, and/or upgrade your graphics card.\n")
				raise
		self.graphics.grid(row=0, column=0, columnspan=6,
								sticky=Tk.NSEW)
		self.graphics.bind('<Double-ButtonPress-1>',
						lambda e, s=self: s._double1(e))
		self.graphics.bind('<ButtonPress-1>',
						lambda e, s=self: s._press1(e))
		self.graphics.bind('<Button1-Motion>',
						lambda e, s=self: s._drag(e))
		self.graphics.bind('<ButtonRelease-1>',
						lambda e, s=self: s._release(e))
		self.graphics.bind('<ButtonPress-2>',
						lambda e, s=self: s._press2(e))
		self.graphics.bind('<Button2-Motion>',
						lambda e, s=self: s._drag(e))
		self.graphics.bind('<ButtonRelease-2>',
						lambda e, s=self: s._release(e))
		self.view = ViewOption(master, 1,
				'View', 'right', self._viewCB, startCol=2)
		self.lowRes = ResolutionOption(master, 1,
				'Resolution', 0, self._lowResCB, startCol=4)
		reset = Tk.Button(master, text='View All', command=self._resetCB)
		reset.grid(row=1, column=0, sticky=Tk.E)

		self.clipVar = Tk.BooleanVar(master)
		self.clipVar.set(chimera.viewer.clipping)
		cb = Tk.Checkbutton(master, text = "Clip",
				    variable = self.clipVar,
				    command = self._clipCB)
		cb.grid(row = 2, column = 0, sticky=Tk.W)

		def showCapDialog():
			from SurfaceCap import gui
			gui.show_capper_dialog()
		Tk.Button(master, text="Cap clipped surfaces...", pady=0,
					command=showCapDialog).grid(
					row=2, column=1, columnspan=6)

		# Set up restore functions
		self.addRestoreFunc("Side View", "view",
					self.setOption, self.view)
		self.addRestoreFunc("Side View", "lowRes",
					self.setOption, self.lowRes)
		# need to restoreSideview because it affects appearance
		self._restoreSideview(False)

	def _resetCB(self):
		chimera.viewer.viewAll(resetCofrMethod=False)

	def _clipCB(self):
		chimera.viewer.clipping = self.clipVar.get()

	def enableClipping(self, onoff = True):
		self.clipVar.set(onoff)
		self._clipCB()

	def _fovCB(self, option):
		fov = option.get()
		setCameraFOV(fov, self.viewer)

	def _unitsCB(self, option):
		units = option.get()
		adjust = (UnitOption.convert[self.previousUnits]
						/ UnitOption.convert[units])
		cam = self.viewer.camera
		self.screenDistance.set(self.screenDistance.get() * adjust)
		self.eyeSep.set(self.eyeSep.get() * adjust)
		self.screenWidth.set(self.screenWidth.get() * adjust)
		self.previousUnits = units

	def _eyeSepCB(self, option):
		eyeSep = option.get()
		adjust = (UnitOption.convert[self.units.get()]
					/ UnitOption.convert[UnitOption.mm])
		setCameraEyeSeparation(eyeSep * adjust, self.viewer)

	def _screenDistanceCB(self, option):
		dist = option.get()
		adjust = (UnitOption.convert[self.units.get()]
					/ UnitOption.convert[UnitOption.mm])
		setCameraScreenDistance(dist * adjust, self.viewer)

	def _screenWidthCB(self, option):
		width = option.get()
		adjust = (UnitOption.convert[self.units.get()]
					/ UnitOption.convert[UnitOption.mm])
		setScreenWidth(width * adjust, self.viewer)
		if width == 0:
			option.set(getScreenWidth() / adjust)

	# Save/Restore/Reset callbacks

	def setOption(self, opt, prefDict, defDict, name):
		try:
			val = prefDict[name]
		except KeyError:
			val = defDict[name][0]
		opt.set(val)		# set UI element
		tkoptions.Option._set(opt)	# explicitly trigger callback

	def setDistance(self, opt, prefDict, defDict, name):
		try:
			val = prefDict[name]
		except KeyError:
			val = defDict[name][0]
		# val is in mm and we want to display it
		# in the currently selected units
		adjust = (UnitOption.convert[UnitOption.mm] /
				UnitOption.convert[self.units.get()])
		opt.set(val * adjust)	# set UI element
		tkoptions.Option._set(opt)	# explicitly trigger callback

	def setVariable(self, var, prefDict, defDict, name):
		try:
			val = prefDict[name]
		except KeyError:
			val = defDict[name][0]
		var.set(val)		# set variable which triggers callback

	def addRestoreFunc(self, category, name, setter, target):
		d = self.restoreMap.setdefault(category, {})
		d[name] = (setter, target)

	def restoreCategory(self, category):
		prefDict = prefs[category]
		defDict = defPrefs[category]
		d = self.restoreMap.get(category, {})
		for name, (setter, target) in d.iteritems():
			setter(target, prefDict, defDict, name)

	def _saveSideview(self):
		subPrefs = {
			"view": self.view.get(),
			"lowRes": self.lowRes.get(),
		}
		savePrefCategory("Side View", subPrefs, delaySave=True)
		self._saveSideCam()

	def _restoreSideview(self, restoreCamera=True):
		try:
			self.restoreCategory("Side View")
		except KeyError:
			self._resetSideview(restoreCamera)
		if restoreCamera:
			self._restoreSideCam()

	def _resetSideview(self, resetCamera=True):
		defOpts = {
			"view": "right",
			"lowRes": False,
		}
		self.setOption(self.view, defOpts, defOpts, "view")
		self.setOption(self.lowRes, defOpts, defOpts, "lowRes")
		# We cannot use resetPrefCategory because
		# resetPrefCategory cannot reset options
		# that only exist in the ViewingDialog instance
		#resetPrefCategory("Side View", self.viewer)
		if resetCamera:
			self._resetSideCam()

	def _saveSideCam(self):
		subPrefs = {
			"mode": self.viewer.camera.mode(),
			"reverseStereo": chimera.reverseStereo(),
			"projection": self.viewer.camera.ortho,
			"units": self.units.get(),
			"eyeSep": self.viewer.camera.eyeSeparation,
			"screenDistance": self.viewer.camera.screenDistance,
			"screenWidth": getScreenWidth(),
		}
		savePrefCategory("SideCam", subPrefs)

	def _restoreSideCam(self):
		try:
			self.restoreCategory("SideCam")
		except KeyError:
			self._resetSideCam()

	def _resetSideCam(self):
		resetPrefCategory("SideCam", self.viewer)

	def _saveCamera(self):
		# We don't want to save scaleFactor, near or far
		# because they are data dependent and may already
		# have been set by the user before opening the
		# viewing dialog
		self._saveSideCam()

	def _restoreCamera(self):
		self._restoreSideCam()

	def _resetCamera(self):
		self._resetSideCam()

	def _saveRotation(self):
		subPrefs = {
			"method": self.cofrMethod.get(),
			"center": self.cofrPoint.get(),
		}
		savePrefCategory("Rotation", subPrefs)

	def _restoreRotation(self):
		try:
			self.restoreCategory("Rotation")
		except KeyError:
			self._resetRotation()

	def _resetRotation(self):
		resetPrefCategory("Rotation", self.viewer)

	def _saveEffects(self):
		sc = self.silhouetteColor.get()
		if sc is not None:
			sc = sc.rgba()
		fc = self.fogColor.get()
		if fc is not None:
			fc = fc.rgba()
		subPrefs = {
			"depthcue": self.depthcue.get(),
			"depthCueRange": (self.startDepth.get(),
					  self.endDepth.get()),
			"fogColor": fc,
			"subdivision": self.subdivision.get(),
			"localViewer": self.localViewer.get(),
			"bgopacity": self.bgopacity.get(),
			"silhouette": self.silhouette.get(),
			"silhouetteColor": sc,
			"silhouetteWidth": self.silhouetteWidth.get(),
			"multisample": self.multisample.get(),
		}
		savePrefCategory("Effects", subPrefs)

	def _restoreEffects(self):
		try:
			self.restoreCategory("Effects")
		except KeyError:
			self._resetEffects()

	def _resetEffects(self):
		resetPrefCategory("Effects", self.viewer)

	# Dialog button callbacks

	def Reset(self):
		tabName = self.nb.raised()
		try:
			self.resetCallbacks[tabName]()
		except KeyError:
			pass

	def Restore(self):
		tabName = self.nb.raised()
		try:
			self.restoreCallbacks[tabName]()
		except KeyError:
			pass

	def Save(self):
		pass
		tabName = self.nb.raised()
		try:
			self.saveCallbacks[tabName]()
		except KeyError:
			pass

#
# Lots of "set" functions that are used by ViewingDialog instance
# and by applyPreferences()
#

def setViewerDepthcue(dc, viewer):
	viewer.depthCue = dc

def setViewerDepthCueRange(r, viewer):
	viewer.depthCueRange = r

def setViewerFogColor(fc, viewer):
	if fc is not None and not isinstance(fc, chimera.MaterialColor):
		fc = chimera.MaterialColor(*fc)
	viewer.depthCueColor = fc

def setViewerLocal(local, viewer):
	viewer.localViewer = local

def setViewerSilhouette(s, viewer):
	viewer.showSilhouette = s

def setViewerSilhouetteColor(sc, viewer):
	if sc is not None and not isinstance(sc, chimera.MaterialColor):
		sc = chimera.MaterialColor(*sc)
	viewer.silhouetteColor = sc

def setViewerSilhouetteWidth(w, viewer):
	viewer.silhouetteWidth = w

def setCameraMode(mode, viewer):
	oldMode = viewer.camera.mode()
	if mode == oldMode:
		return True
	# special case going into and out of stereo
	from tkgui import app
	if oldMode == "sequential stereo":
		if not viewer.camera.setMode(mode, viewer):
			return False
		chimera.stereo = False
		try:
			app.makeGraphicsWindow()
		except RuntimeError:
			chimera.stereo = True
			replyobj.warning("Unable to leave stereo mode.")
			viewer.camera.setMode(oldMode, viewer)
			return False
	if mode == "sequential stereo":
		# can't set camera mode until we have stereo window,
		# so reset to mono temporarily
		viewer.camera.setMode('mono', viewer)
		chimera.stereo = True
		try:
			app.makeGraphicsWindow()
		except RuntimeError, what:
			chimera.stereo = False
			replyobj.warning("Unable to turn on stereo viewing.\n"
					"%s" % what)
			viewer.camera.setMode(oldMode, viewer)
			return False
	if not viewer.camera.setMode(mode, viewer):
		viewer.camera.setMode(oldMode, viewer)
		return False
	if mode == "row interleaved stereo":
		# turn of multisampling to avoid blending across lines
		if chimera.nomultisample != True:
			replyobj.status("Turning off multisampling for row interleaved stereo")
			setMultisample(False)
		app.graphics.configure(stereo="row interleaved")
	elif mode != "sequential stereo":
		app.graphics.configure(stereo="none")
	return True

def setReverseStereo(onoff, viewer):
	chimera.setReverseStereo(onoff)

def setCameraOrtho(ortho, viewer):
	viewer.camera.ortho = ortho

def setCameraFOV(fov, viewer):
	viewer.camera.fieldOfView = fov

def setCameraEyeSeparation(eyesep, viewer):
	viewer.camera.eyeSeparation = eyesep

def setCameraScreenDistance(sd, viewer):
	viewer.camera.screenDistance = sd

def getScreenWidth():
	if not chimera.nogui:
		import tkgui
		return tkgui.getScreenMMWidth()
	return 0

def setScreenWidth(sw, viewer):
	if not chimera.nogui:
		import tkgui
		tkgui.setScreenMMWidth(sw)

def setCofrMethod(method, viewer=None):
	chimera.openModels.cofrMethod = method

def setCofrPoint(point, viewer=None):
	chimera.openModels.cofr = chimera.Point(point[0], point[1], point[2])

def getQuality():
	return chimera.LODControl.get().quality

def setQuality(quality, viewer=None):
	lod = chimera.LODControl.get()
	lod.quality = quality

def setBackgroundOpacity(bgopacity, viewer=None):
	if chimera.bgopacity == bgopacity:
		return True
	chimera.bgopacity = bgopacity
	try:
		from tkgui import app
		app.makeGraphicsWindow()
		return True
	except RuntimeError, what:
		if bgopacity:
			onoff = "on"
		else:
			onoff = "off"
		replyobj.warning("Unable to turn %s background transparency.\n"
						"%s" % (onoff, what))
		return False

def setShadows(shadows, viewer=None):
	if chimera.viewer.showShadows == shadows:
		return True
	try:
		chimera.viewer.showShadows = shadows
		return True
	except chimera.error, what:
		if shadows:
			onoff = "on"
		else:
			onoff = "off"
		replyobj.warning("Unable to turn %s shadows.\n%s"
							% (onoff, what))
		return False

def setMultisample(multisample, viewer=None):
	if multisample is None:
		if chimera.nomultisample == None:
			return True
		if chimera.nomultisample == chimera.tkgui.defaultNoMultisampling(chimera.tkgui.app):
			return True
		chimera.nomultisample = None
	elif chimera.nomultisample == (not multisample):
		return True
	else:
		chimera.nomultisample = not multisample
	try:
		from tkgui import app
		app.makeGraphicsWindow()
		return True
	except RuntimeError, what:
		if multisample is None:
			onoff = "reset"
		elif multisample:
			onoff = "on"
		else:
			onoff = "off"
		replyobj.warning("Unable to turn %s multisampling.\n%s"
							% (onoff, what))
		return False

prefs = preferences.addCategory("Viewing", preferences.HiddenCategory)
if chimera.nomultisample is None:
	multisample = None
else:
	multisample = not chimera.nomultisample
defPrefs = {
	# No Camera preferences for now
	"Side View": {
		"view":		( 'right',
				  None ),
		"lowRes":	( False,
				  None ),
	},
	"SideCam": {
		# Preferences shared between Side View and Camera
		"mode":		( chimera.stereo
					and "sequential stereo"
					or "mono",
				  setCameraMode ),
		"reverseStereo": ( chimera.reverseStereo(),
				  setReverseStereo ),
		"projection":	( 0,
				  setCameraOrtho ),
		"units":	( UnitOption.inch,
				  None ),
		"eyeSep":	( 2.0 * UnitOption.convert[UnitOption.inch]
					/ UnitOption.convert[UnitOption.mm],
				  setCameraEyeSeparation ),
		"screenDistance": ( 24.0 * UnitOption.convert[UnitOption.inch]
					/ UnitOption.convert[UnitOption.mm],
				  setCameraScreenDistance ),
		"screenWidth": ( getScreenWidth(), setScreenWidth ),
	},
	"Rotation": {
		"method":	( defaultCofrMethod,
				  setCofrMethod ),
		"center":	( (0.0, 0.0, 0.0),
				  setCofrPoint ),
	},
	"Effects": {
		"depthcue":	( 1,
				  setViewerDepthcue ),
		"depthCueRange":( (0.5, 1.0),
				  setViewerDepthCueRange ),
		"fogColor":	( None,
				  setViewerFogColor ),
		"subdivision":	( 1.0,
				  setQuality ),
		"localViewer":	( 0,
				  setViewerLocal ),
		"bgopacity":	( chimera.bgopacity,
				  setBackgroundOpacity ),
		"shadows":	( False,
				  setShadows ),
		"silhouette":	( 0,
				  setViewerSilhouette ),
		"silhouetteColor":	( None,
				  setViewerSilhouetteColor ),
		"silhouetteWidth":	( 1,
				  setViewerSilhouetteWidth ),
		"multisample":	( multisample,
				  setMultisample ),
	},
}
del multisample

def savePrefCategory(name, subPrefs, delaySave=False):
	newPrefs = {}
	for prefName, (defVal, func) in defPrefs[name].iteritems():
		try:
			newVal = subPrefs[prefName]
		except KeyError:
			pass
		else:
			if not _sameValue(newVal, defVal):
				newPrefs[prefName] = newVal

	prefs[name] = newPrefs
	if not delaySave:
		prefs.saveToFile()

def _sameValue(v1, v2):
	if isinstance(v1, float) and isinstance(v2, float):
		return abs(v1 - v2) < 0.0001
	else:
		return v1 == v2

def resetPrefCategory(name, viewer):
	for prefName, (defVal, func) in defPrefs[name].iteritems():
		if func:
			func(defVal, viewer)

def applyPrefCategory(name, viewer):
	try:
		subPrefs = prefs[name]
	except KeyError:
		subPrefs = {}
	for prefName, (defVal, func) in defPrefs[name].iteritems():
		if func:
			val = subPrefs.get(prefName, defVal)
			func(val, viewer)

def applyPreferences(viewer):
	# No need to restore "Side View" parameters since the
	# side view panel has not been created
	applyPrefCategory("SideCam", viewer)
	applyPrefCategory("Rotation", viewer)
	applyPrefCategory("Effects", viewer)

def registerViewDialog():
	import dialogs
	dialogs.register(ViewerDialog.name,
				lambda: ViewerDialog(viewer=chimera.viewer))
chimera.registerPostGraphicsFunc(registerViewDialog)
