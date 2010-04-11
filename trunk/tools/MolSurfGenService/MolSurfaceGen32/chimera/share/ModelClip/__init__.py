# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog
import Tkinter
from chimera.tkgui import getClipModel, setClipModel, initClip
from chimera import mousemodes, replyobj

class ClipDialog(ModelessDialog):
	name = "per-model clipping"
	title = "Per-Model Clipping"
	buttons = ("Close",)
	help = 'ContributedSoftware/per-model/per-model.html'

	def fillInUI(self, parent):
		import Pmw
		from chimera.widgets import ModelOptionMenu
		self.menu = ModelOptionMenu(parent, command=self._menuCB,
			labelpos='w', label_text="Model:")
		self.menu.grid(row=0, sticky='w')

		self.infoArea = None
		self.normMouse = None
		self.clipMouse = [None, None]
		if self.menu.getvalue() is not None:
			self.menu.invoke() # cause callback

		group = Pmw.Group(parent, tag_text="Clip Motion Assignments")
		group.grid(row=2, sticky="nsew")

		self.buttonLabels = []
		self.labelValues = {}
		for mod in ("",) + mousemodes.usedMods:
			for but in mousemodes.usedButtons:
				if mod:
					self.buttonLabels.append(
						mod.lower() + " button " + but)
					self.labelValues[self.buttonLabels[-1]]\
						= (but, (mod,))
				else:
					self.buttonLabels.append("button "+but)
					self.labelValues[self.buttonLabels[-1]]\
						= (but, ())
		self.transMenu = Pmw.OptionMenu(group.interior(),
			command=lambda bname: self._assignmentChange(0, bname),
			initialitem="button 2", items=self.buttonLabels,
			labelpos='n', label_text="Translation")
		self.transMenu.grid(row=0, column=0)
		self.pivotMenu = Pmw.OptionMenu(group.interior(),
			command=lambda bname: self._assignmentChange(1, bname),
			initialitem="button 3", items=self.buttonLabels,
			labelpos='n', label_text="Rotation")
		self.pivotMenu.grid(row=0, column=1)

		mousemodes.addFunction("plane rotate", (
				lambda v, e: self._planeStart(v, e, "rotate"),
				self._planeRot,
				self._planeStop))
		mousemodes.addFunction("plane translate", (
				lambda v, e: self._planeStart(
							v, e, "translate z"),
				self._planeTrans,
				self._planeStop))

		def showCapDialog():
			from SurfaceCap.gui import Capper_Dialog
			from chimera import dialogs
			d = dialogs.display(Capper_Dialog.name)
			d.show_caps.set(True)
		Tkinter.Button(parent, text="Cap clipped surfaces...", pady=0,
			command=showCapDialog).grid(row=3)

	def Close(self):
		if self.infoArea and self.infoArea.mouseVar.get():
			self.infoArea.mouseVar.set(False)
			self.stopMouseClip()
		ModelessDialog.Close(self)

	def setModel(self, model):
		self.menu.setvalue(model)

	def startMouseClip(self, model):
		setClipModel(model)
		if self.normMouse is not None: # clipping already ongoing
			return
		transVal = self.transMenu.getvalue()
		pivotVal = self.pivotMenu.getvalue()
		if transVal == pivotVal:
			replyobj.error("Cannot assign both clip functions to"
				" same button\n")
			return
		self.normMouse = [
			mousemodes.getFuncName(*self.labelValues[transVal]),
			mousemodes.getFuncName(*self.labelValues[pivotVal])
		]
		self._activateMouse(0, transVal)
		self._activateMouse(1, pivotVal)

	def stopMouseClip(self):
		if self.normMouse is None: # already stopped
			return
		setClipModel(None)
		self._restoreButton(0)
		self._restoreButton(1)
		self.normMouse = None

	def _activateMouse(self, but, butName):
		self.clipMouse[but] = butName
		args = self.labelValues[butName] + (["plane translate",
							"plane rotate"][but],)
		mousemodes.setButtonFunction(*args)

	def _align(self, refModel):
		if not refModel.useClipPlane:
			from chimera import LimitationError
			raise LimitationError("Cannot align clip planes:"
				" both models must have clipping on")

		matchModel = self.menu.getvalue()
		refMat = refModel.openState.xform
		matchMat = matchModel.openState.xform
		if refMat == matchMat:
			matchModel.clipPlane = refModel.clipPlane
			return
		xf = matchMat.inverse()
		xf.multiply(refMat)
		refClip = refModel.clipPlane
		matchModel.clipPlane = chimera.Plane(xf.apply(refClip.origin),
						xf.apply(refClip.normal))

	def _assignmentChange(self, pos, val):
		if self.normMouse is None:  # no ongoing clip
			return
		if val == self.clipMouse[1 - pos]:
			replyobj.error("Cannot assign both clip functions to"
				" same button\n")
			[self.transMenu, self.pivotMenu][pos].setvalue(
							self.clipMouse[pos])
			return
		# restore former function to button
		self._restoreButton(pos)

		# remember normal function of new button
		self._rememberButton(pos, val)

		# assign clip function to new button
		self._activateMouse(pos, val)

	def _flipPlane(self):
		model = self.menu.getvalue()
		p = model.clipPlane
		normal = p.normal
		normal.negate()
		p.normal = normal
		model.clipPlane = p

	def _menuCB(self, model):
		if self.infoArea:
			self.infoArea.grid_forget()
			if isinstance(self.infoArea, ClipFrame):
				self.infoArea.destroy()
		if model:
			self.infoArea = ClipFrame(self, model)
			self.infoArea.grid(row=1, sticky='nsew')
		else:
			self.infoArea = None

	def _rememberButton(self, but, butName):
		self.normMouse[but] = mousemodes.getFuncName(
						*self.labelValues[butName])

	def _restoreButton(self, but):
		# restore former function of translation (but == 0) or
		# pivot button (but == 1)
		restoreFunc = self.normMouse[but]
		restoreArgs = self.labelValues[self.clipMouse[but]] + (
								restoreFunc,)
		mousemodes.setButtonFunction(*restoreArgs)

	def _planeRot(self, viewer, event):
		xf = viewer.vsphere(event.time, event.x, event.y,
							event.state % 2 == 1)
		if xf.isIdentity():
			return
		clipModel = getClipModel()
		if not clipModel:
			return
		p = clipModel.clipPlane
		axis, angle = clipModel.openState.xform.getRotation()
		mxf = chimera.Xform.rotation(axis, angle)
		mxfinv = chimera.Xform.rotation(axis, -angle)
		mxfinv.multiply(xf)
		mxfinv.multiply(mxf)
		p.xformNormal(mxfinv)
		clipModel.clipPlane = p

	def _doPlaneAutospin(self, trigger, xform, frameNumber):
		clipModel = getClipModel()
		if not clipModel:
			return
		p = clipModel.clipPlane
		p.xformNormal(xform)
		clipModel.clipPlane = p

	def _planeStart(self, viewer, event, cursor):
		viewer.recordPosition(event.time, event.x, event.y, cursor),
		clipModel = getClipModel()
		if not clipModel:
			return
		viewer.showPlaneModel = clipModel, .5

	def _planeStop(self, viewer, event):
		viewer.setCursor(None)
		viewer.showPlaneModel = None, 0

	def _planeTrans(self, viewer, event):
		clipModel = getClipModel()
		if not clipModel:
			return
		p = clipModel.clipPlane
		dx, dy = viewer.delta(event.x, event.y, event.state % 2 == 1)
		axis, angle = clipModel.openState.xform.getRotation()
		mxf = chimera.Xform.rotation(axis, angle)
		n = mxf.apply(p.normal)

		# figure out major axis of normal in lab space
		if abs(n.x) >= abs(n.y):
			axis = (0, 1)
		else:
			axis = (1, 0)

		# reassign normal so there are no zeros 
		# in mouse adjustment calculation
		def fuzzySign(x):
			if x < -1e-6:
				return -1
			if x > 1e-6:
				return 1
			return 0
		n = [fuzzySign(n.x), fuzzySign(n.y), fuzzySign(n.z)]
		if n[axis[0]] == 0:
			# should never happen with non-zero normal
			n[axis[0]] = 1
		if n[axis[1]] == 0:
			n[axis[1]] = n[axis[0]]		# mimic major axis
		n = chimera.Vector(*n)
		adjust = n.x * dx + n.y * dy

		distance = 2 * viewer.camera.extent * adjust
		p.moveOrigin(distance)
		clipModel.clipPlane = p

chimera.dialogs.register(ClipDialog.name, ClipDialog)

class ClipFrame(Tkinter.Frame):
	def __init__(self, clipDialog, model):
		from chimera.widgets import ModelOptionMenu
		self.clipDialog = clipDialog
		self.model = model
		self.clipDependentWidgets = []
		Tkinter.Frame.__init__(self, clipDialog.uiMaster())
		interior = self # used to be a Pmw.Group instead of a Frame!
		self.clipVar = Tkinter.IntVar(interior)
		self.clipVar.set(self.model.useClipPlane)
		Tkinter.Checkbutton(interior, command=self._toggleClip,
			text="Enable clipping", variable=self.clipVar).grid(
			row=0, sticky='w')
		slabFrame = Tkinter.Frame(interior)
		slabFrame.grid(row=1, sticky='w')
		self.slabVar = Tkinter.IntVar(interior)
		self.slabVar.set(self.model.useClipThickness)
		cbutton = Tkinter.Checkbutton(slabFrame,
				    command=self._changeSlab,
				    text="Use slab mode with thickness",
				    variable=self.slabVar)
		cbutton.grid(row=0, column=0, sticky='w')
		self.clipDependentWidgets.append(cbutton)
		self.slabThicknessVar = Tkinter.DoubleVar(slabFrame)
		self.slabThicknessVar.set(self.model.clipThickness)
		entry = Tkinter.Entry(slabFrame, width=4,
				      textvariable=self.slabThicknessVar)
		entry.grid(row=0, column=1, sticky='w')
		entry.bind('<KeyPress-Return>', self._changeSlab)
		self.clipDependentWidgets.append(entry)
		butFrame = Tkinter.Frame(interior)
		butFrame.grid(row=2, sticky='w')
		button = Tkinter.Button(butFrame, pady=0, command=lambda:
				chimera.tkgui.normalizeClipFacing(self.model),
				text="Orient plane")
		button.grid(row=0, column=0, sticky='e')
		self.clipDependentWidgets.append(button)
		label = Tkinter.Label(butFrame,
					text="perpendicular to line of sight")
		label.grid(row=0, column=1, sticky='w')
		self.clipDependentWidgets.append(label)
		label = Tkinter.Label(butFrame,
			text="with center of rotation at center of view")
		label.grid(row=1, column=0, columnspan=2)
		self.clipDependentWidgets.append(label)

		butFrame = Tkinter.Frame(interior)
		butFrame.grid(row=3, sticky='w')
		button = Tkinter.Button(butFrame, pady=0, command=
				clipDialog._flipPlane, text="Flip plane")
		button.grid(row=0, column=0, sticky='e')
		self.clipDependentWidgets.append(button)
		label = Tkinter.Label(butFrame, text="180 degrees")
		label.grid(row=0, column=1, sticky='w')
		self.clipDependentWidgets.append(label)

		butFrame = Tkinter.Frame(interior)
		butFrame.grid(row=4, sticky='w')
		button = Tkinter.Button(butFrame, pady=0, command=lambda :
				self.clipDialog._align(self.menu.getvalue()),
				text="Align plane")
		button.grid(row=0, column=0, sticky='e')
		self.clipDependentWidgets.append(button)
		self.menu = ModelOptionMenu(butFrame, labelpos='w',
							label_text="with")
		def kludge(self=self.menu, **kw):
			newKw = {}
			for k, v in kw.items():
				newKw["menubutton_" + k] = v
				newKw["label_" + k] = v
			self.configure(**newKw)
		self.menu.config = kludge
		self.menu.grid(row=0, column=1, sticky='w')
		self.clipDependentWidgets.append(self.menu)
		label = Tkinter.Label(butFrame, text="clip plane")
		label.grid(row=0, column=2, sticky='w')
		self.clipDependentWidgets.append(label)

		self.mouseVar = Tkinter.IntVar(interior)
		self.mouseVar.set(getClipModel() == model)
		self.mouseActiveButton = Tkinter.Checkbutton(interior,
			command=self._toggleMouse, variable=self.mouseVar,
			text="Adjust clipping with mouse as below")
		self.mouseActiveButton.grid(row=5, sticky='w')
		self.clipDependentWidgets.append(self.mouseActiveButton)

		if not self.clipVar.get():
			for w in self.clipDependentWidgets:
				w.config(state='disabled')

	def destroy(self):
		delattr(self, 'model')
		if self.mouseVar.get():
			self.clipDialog.stopMouseClip()
		Tkinter.Frame.destroy(self)

	def _toggleClip(self):
		if self.clipVar.get():
			try:
				initClip(self.model)
			except ValueError:
				replyobj.error("Model cannot currently be"
					" clipped [no valid bounding box]\n")
				self.clipVar.set(False)
				return
			self.slabThicknessVar.set(self.model.clipThickness)
			for w in self.clipDependentWidgets:
				w.config(state='normal')
		else:
			self.model.useClipPlane = False
			if getClipModel() == self.model:
				self.clipDialog.stopMouseClip()
				self.mouseVar.set(False)
			for w in self.clipDependentWidgets:
				w.config(state='disabled')

	def _toggleMouse(self):
		if self.mouseVar.get():
			self.clipDialog.startMouseClip(self.model)
		else:
			self.clipDialog.stopMouseClip()

	def _changeSlab(self, event = None):

		self.model.useClipThickness = self.slabVar.get()
		try:
			thick = float(self.slabThicknessVar.get())
		except ValueError:
			replyobj.error("Invalid slab thickness.\n")
			return
		self.model.clipThickness = thick
