# LightingController
#
#	Manager for the lighting user interface as well as saving
#	settings in hidden Chimera preference category.  The manager
#	is a singleton (unless explicitly created otherwise) and uses
#	the Chimera "Lighting" category a.k.a LightingController.Name.
#	The preference consists of a dictionary of light settings.
#	Each light setting is a dictionary of light parameters.
#	Currently, we save two lights: "key" and "fill".  The dictionary
#	value is a six-tuple:
#		active		Boolean, is light on?
#		diffuseColor	tuple of 3 floats, diffuse light RGB value
#		diffScale	float, diffuse light intensity
#		specularColor	tuple of 3 floats, specular light RGB value
#		specularScale	float, specular light intensity
#		direction	tuple of 3 floats, light direction
#	(Currently, we only handle DirectionalLight instances.)
#
#	In the simple interface:
#
#		overlap = norm(key-direction) * norm(fill-direction)
#		brightness = key-brightness + overlap * fill-brightness
#		key-to-fill ratio = brightness / fill-brightness
#

SystemDefault = "Chimera default"
UserDefault = "User default"

def singleton():
	# We have to stash our singleton in the viewing module
	# because it is first created in ChimeraExtension.py
	# and we cannot store it as a module global variable then
	# because that module gets destroyed once
	# ChimeraExtension.py terminates.
	from chimera import viewing
	if not hasattr(viewing, "lightingController"):
		viewing.lightingController = LightingController()
	#print "Lighting singleton:", viewing.lightingController
	return viewing.lightingController

class LightingController:

	# This class should have a singleton instance.

	Name = "Lighting"

	from chimera import tkoptions
	class _ScaleOption(tkoptions.FloatOption):
		min = -5
		max = 5

	class _QualityOption(tkoptions.EnumOption):
		"""Specialization of EnumOption Class for shader effect"""
		values = ('normal', 'glossy')

	def __init__(self, singleton=True):
		from chimera import preferences
		self.dialog = None
		self.master = None
		self.trackLights = None
		self.trackViewers = None
		self.trackMaterials = None
		self.saveKey = None
		self.saveFill = None
		self.restoreShinyBrightness = None
		self.prefs = preferences.addCategory("Lighting",
						preferences.HiddenCategory)
		self.light = None
		if singleton:
			global _singleton
			_singleton = self

	def postGraphicsFunc(self):
		import chimera
		self.lensViewer = chimera.viewer
		self.keyLight = self.lensViewer.keyLight
		self.fillLight = self.lensViewer.fillLight
		self.whichLight = None
		self.systemDefault = self.currentParams()
		import SimpleSession
		chimera.triggers.addHandler(SimpleSession.SAVE_SESSION,
					self.saveSession, None)
		self.restore()

	def preferences(self):
		# Return hidden preference category so someone else
		# manipulate it
		return self.prefs

	Interface_LightsBasic = 'Lights (basic)'
	Interface_LightsAdvanced = 'Lights (advanced)'
	Interface_Shininess = 'Shininess'
	def create(self, dialog, master):
		from chimera import tkoptions
		from chimera.preferences import saveui
		import Tkinter, Pmw
		self.dialog = dialog
		self.master = master
		self.saveui = saveui.SaveUI(master, self)
		self.interfaceVar = Tkinter.StringVar(master)
		self.interfaceVar.set(self.Interface_LightsBasic)
		w = Pmw.Group(master, tag_pyclass = Tkinter.Menubutton,
				tag_indicatoron=True,
				tag_relief=Tkinter.RAISED,
				tag_borderwidth=2,
				tag_textvariable=self.interfaceVar)
		w.pack(side=Tkinter.LEFT)

		mb = w.component("tag")
		self.interfaceMenu = Tkinter.Menu(mb, tearoff=Tkinter.NO)
		mb.config(menu=self.interfaceMenu)
		self.interfaceMenu.add_radiobutton(
				label=self.Interface_LightsBasic,
				variable=self.interfaceVar,
				value=self.Interface_LightsBasic,
				command=self._chooseInterface)
		self.interfaceMenu.add_radiobutton(
				label=self.Interface_LightsAdvanced,
				variable=self.interfaceVar,
				value=self.Interface_LightsAdvanced,
				command=self._chooseInterface)
		self.interfaceMenu.add_radiobutton(
				label=self.Interface_Shininess,
				variable=self.interfaceVar,
				value=self.Interface_Shininess,
				command=self._chooseInterface)

		self.simpleFrame = Tkinter.Frame(w.interior())
		self.simpleFrame.pack(side=Tkinter.LEFT)
		self.simpleFrame.pack_forget()
		f = self.simpleFrame
		t = Tkinter.Label(f, text="key light:")
		t.grid(row=0, column=0, sticky=Tkinter.E, padx=3)
		t = Tkinter.Frame(f, background="red")
		t.grid(row=0, column=1, sticky=Tkinter.NSEW, padx=1, pady=1)
		t = Tkinter.Label(f, text="fill light:")
		t.grid(row=1, column=0, sticky=Tkinter.E, padx=3)
		t = Tkinter.Frame(f, background="#009F00")
		t.grid(row=1, column=1, sticky=Tkinter.NSEW, padx=1, pady=1)

		brightness, contrast = self._calculateBrightnessContrast()
		from CGLtk import Hybrid
		lbl = Tkinter.Label(f, text="brightness:")
		lbl.grid(row=2, column=0, sticky=Tkinter.W)
		self.brightness = Hybrid.Scale(f, "", 0.1, 5, 0.05,
								brightness)
		self.brightness.callback(self._setBrightnessContrast)
		self.brightness.frame.grid(row=3, column=0, columnspan=2)
		lbl = Tkinter.Label(f, text="key-to-fill ratio:")
		lbl.grid(row=4, column=0, sticky=Tkinter.W)
		self.contrast = Hybrid.Scale(f, "", 1, 20, 0.1, contrast)
		self.contrast.callback(self._setBrightnessContrast)
		self.contrast.frame.grid(row=5, column=0, columnspan=2)
		import chimera.help
		chimera.help.register(self.contrast.frame, balloon=
				"TV news: 1.5, Sitcom: 2,\n"
				"Drama: 4, Action Sequence: 8,\n"
				"Horror movie: 10, Film Noir: 16")

		qf = Tkinter.Frame(f)
		qf.grid(row=6, column=0, columnspan=2, sticky='ew')
		s = self.lensViewer.haveShader()
		q = {False:'normal', True:'glossy'}[s]
		self.quality = self._QualityOption(qf, 0,
					    'quality', q,
					    self._qualityCB)
		if not self.lensViewer.haveShaderSupport():
			self.quality.disable()

		self.advancedFrame = Tkinter.Frame(w.interior())
		self.advancedFrame.pack(side=Tkinter.LEFT)
		self.advancedFrame.pack_forget()
		self.whichLight = Pmw.RadioSelect(self.advancedFrame,
					buttontype="radiobutton",
					command=self._setLight)
		self.whichLight.pack(side=Tkinter.TOP)
		self.whichLight.add("key light", fg="red")
		self.whichLight.add("fill light", fg="#009F00")
		f = Tkinter.Frame(self.advancedFrame)
		f.pack(side=Tkinter.LEFT)
		self.active = tkoptions.BooleanOption(f, 0,
					"active", 1,
					self._setActive)
		self.diffuse = tkoptions.ColorOption(f, 1,
					"diffuse color", None,
					self._setDiffuse,
					noneOkay=False)
		self.diffuseScale = tkoptions.FloatOption(f, 2,
					"diffuse scale", 1,
					self._setDiffuseScale,
					min=-5, max=5)
		self.specular = tkoptions.ColorOption(f, 3,
					"specular color", None,
					self._setSpecular,
					noneOkay=False)
		self.specularScale = tkoptions.FloatOption(f, 4,
					"specular scale", 1,
					self._setSpecularScale,
					min=-5, max=5)
		self.direction = tkoptions.Float3TupleOption(f, 5,
					"direction", (0, 0, 0),
					self._setDirection)

		self.shininessFrame = Tkinter.Frame(w.interior())
		self.shininessFrame.pack(side=Tkinter.LEFT)
		self.shininessFrame.pack_forget()
		f = Tkinter.Frame(self.shininessFrame)
		f.pack(side=Tkinter.LEFT)
		mat = chimera.Material.lookup("default")
		rgb, b = normalizedColor(mat.specular,
					self.restoreShinyBrightness)
		self.shininess = tkoptions.SliderOption(f, 0,
					"shininess", mat.shininess,
					self._setShininess,
					min=1, max=128, step = 1)
		self.shinySpecular = tkoptions.ColorOption(f, 1,
					"specular color", rgb,
					self._setShininess,
					noneOkay=False)
		self.shinyBrightness = tkoptions.SliderOption(f, 2,
					"brightness", b,
					self._setShininess,
					min=0.1, max=10.0, step=0.1)
		self.updatedShininess = False

		f = self._makeGraphics(master)
		f.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH, ipadx=5, ipady=5)
		self.whichLight.invoke("key light")

		self._chooseInterface()

	def showInterface(self, which):
		self.interfaceVar.set(which)
		self._chooseInterface()

	def update(self):
		# update widgets with current values
		pass

	def map(self):
		import chimera
		self._updateLight()
		self._updateShininess()
		if not self.trackLights:
			self.trackLights = chimera.triggers.addHandler(
						"Light",
						self._trackLights, None)
		if not self.trackViewers:
			self.trackViewers = chimera.triggers.addHandler(
						"Viewer",
						self._trackViewers, None)
		if not self.trackMaterials:
			self.trackMaterials = chimera.triggers.addHandler(
						"Material",
						self._trackMaterials, None)

	def unmap(self):
		import chimera
		if self.trackLights:
			chimera.triggers.deleteHandler("Light",
					self.trackLights)
			self.trackLights = None
		if self.trackViewers:
			chimera.triggers.deleteHandler("Viewer",
					self.trackViewers)
			self.trackViewers = None
		if self.trackMaterials:
			chimera.triggers.deleteHandler("Material",
					self.trackMaterials)
			self.trackMaterials = None

	def _makeGraphics(self, master):
		try:
			from _LightViewer import LightViewer
		except ImportError:
			self.viewer = None
			return
		import Tkinter
		import chimera
		import Togl
		f = Tkinter.Frame(master, bd=3, relief=Tkinter.SUNKEN)
		self.drag = False
		self.viewer = v = LightViewer(self.lensViewer)
		kw = {
			'width': 100, 'height': 100,
			'double': True, 'rgba': True, 'depth': True,
			# assume chimera.nomultisample is already set
			'multisample': not chimera.nomultisample,
			'createcommand': v.createCB,
			'reshapecommand': v.reshapeCB,
			'displaycommand': v.displayCB,
			'destroycommand': v.destroyCB,
		}
		self.graphics = Togl.Togl(f, **kw)
		self.graphics.pack(expand=Tkinter.YES, fill=Tkinter.BOTH)
		self.graphics.bind('<ButtonPress-1>', self._press)
		self.graphics.bind('<Button1-Motion>', self._drag)
		self.graphics.bind('<ButtonRelease-1>', self._release)
		return f

	def _press(self, e):
		if self.drag:
			return
		self.drag = self.viewer.dragStart(e.x, e.y)

	def _drag(self, e):
		if self.drag:
			self.viewer.dragMotion(e.x, e.y)
			self.saveui.setItemChanged(True)

	def _release(self, e):
		if self.drag:
			self.viewer.dragEnd()
			self.drag = False

	def _trackLights(self, trigger, closure, lights):
		if self.keyLight in lights.modified \
		or self.fillLight in lights.modified:
			if self.viewer:
				self.viewer.postRedisplay()
		if self.light in lights.modified:
			self._updateLight()

	def _trackViewers(self, trigger, closure, viewers):
		if self.lensViewer not in viewers.modified:
			return
		if self.lensViewer.keyLight is self.keyLight \
		and self.lensViewer.fillLight is self.fillLight:
			return
		self.keyLight = self.lensViewer.keyLight
		self.fillLight = self.lensViewer.fillLight
		if self.light != self.keyLight and self.light != self.fillLight:
			self.light = None
		self._updateLight()
		if self.viewer:
			self.viewer.postRedisplay()

	def _trackMaterials(self, trigger, closure, materials):
		import chimera
		mat = chimera.Material.lookup("default")
		if mat not in materials.modified:
			return
		if self.updatedShininess:
			self.updatedShininess = False
		else:
			self._updateShininess()
		if self.viewer:
			self.viewer.postRedisplay()

	def _setLight(self, which, forceUpdate=0):
		if which == "key light":
			light = self.lensViewer.keyLight
		elif which == "fill light":
			light = self.lensViewer.fillLight
		else:
			raise ValueError, "unknown light type"
		if self.light is light and not forceUpdate:
			return
		self.light = light
		self._updateLight()

	def _updateLight(self):
		if self.light:
			self.active.set(1)
			self._showLightParams(self.light)
		else:
			self.active.set(0)
			if self.whichLight.getvalue() == "key light":
				light = self.saveKey
			else:
				light = self.saveFill
			if light is not None:
				self._showLightParams(light)
		if self.viewer:
			self.viewer.selected = self.light

	def _showLightParams(self, light):
		self.diffuse.set(light.diffuse)
		self.diffuseScale.set(light.diffuseScale)
		self.specular.set(light.specular)
		self.specularScale.set(light.specularScale)
		self.direction.set(light.direction.data())

	def _updateShininess(self):
		import chimera
		mat = chimera.Material.lookup("default")
		self.shininess.set(mat.shininess)
		rgb, b = normalizedColor(mat.specular,
						self.shinyBrightness.get())
		self.shinySpecular.set(rgb)
		self.shinyBrightness.set(b)

	def _qualityCB(self, option):
		self._setQualityFromParams(option.get())
		self.saveui.setItemChanged(True)

	def _setActive(self, opt):
		if opt.get():
			# Turn light on
			if self.light is not None:
				return
			import chimera
			if self.whichLight.getvalue() == "key light":
				light = self.saveKey
				self.saveKey = None
			else:
				light = self.saveFill
				self.saveFill = None
			if light is None:
				light = self._makeLight()
			if self.whichLight.getvalue() == "key light":
				self.lensViewer.keyLight = light
			else:
				self.lensViewer.fillLight = light
			self.light = light
			self._updateLight()
		else:
			# Turn light off
			if self.light is None:
				return
			self.light = None
			if self.whichLight.getvalue() == "key light":
				self.saveKey = self.lensViewer.keyLight
				self.lensViewer.keyLight = None
			else:
				self.saveFill = self.lensViewer.fillLight
				self.lensViewer.fillLight = None
		self.saveui.setItemChanged(True)

	def _makeLight(self):
		import chimera
		light = chimera.DirectionalLight()
		light.diffuse = self.diffuse.get()
		light.diffuseScale = self.diffuseScale.get()
		light.specular = self.specular.get()
		light.specularScale = self.specularScale.get()
		light.direction = chimera.Vector(0.25, 0.25, 1)
		return light

	def _setDiffuse(self, opt):
		if self.light:
			self.light.diffuse = opt.get()
			self.saveui.setItemChanged(True)

	def _setDiffuseScale(self, opt):
		if self.light:
			self.light.diffuseScale = opt.get()
			self.saveui.setItemChanged(True)

	def _setSpecular(self, opt):
		if self.light:
			self.light.specular = opt.get()
			self.saveui.setItemChanged(True)

	def _setSpecularScale(self, opt):
		if self.light:
			self.light.specularScale = opt.get()
			self.saveui.setItemChanged(True)

	def _setDirection(self, opt):
		if self.light:
			import chimera
			self.light.direction = chimera.Vector(*opt.get())
			self.saveui.setItemChanged(True)

	def _calculateBrightnessContrast(self):
		if not self.lensViewer:
			return None, None
		keyLight = self.lensViewer.keyLight
		fillLight = self.lensViewer.fillLight
		if not keyLight or not fillLight:
			return None, None
		kd = keyLight.direction
		fd = fillLight.direction
		overlap = (kd * fd) / kd.length / fd.length
		brightness = keyLight.diffuseScale \
					+ overlap * fillLight.diffuseScale
		if fillLight.diffuseScale == 0:
			fillLight.diffuseScale = 0.01
		contrast = brightness / fillLight.diffuseScale
		return brightness, contrast

	def _chooseInterface(self, value=None):
		if value is None:
			value = self.interfaceVar.get()
		if value == self.Interface_LightsAdvanced:
			try:
				from _LightViewer import LightViewer
				self.viewer.mode = LightViewer.Advanced
			except ImportError:
				pass
			self.simpleFrame.pack_forget()
			self.shininessFrame.pack_forget()
			self.advancedFrame.pack()
			self._updateLight()
		elif value == self.Interface_LightsBasic:
			try:
				from _LightViewer import LightViewer
				self.viewer.mode = LightViewer.Simple
			except ImportError:
				pass
			self.advancedFrame.pack_forget()
			self.shininessFrame.pack_forget()
			self.simpleFrame.pack()
			keyLight = self.lensViewer.keyLight
			if not keyLight and self.saveKey:
				# bring back original in simple interface
				keyLight = self.saveKey
				self.lensViewer.keyLight = keyLight
				self.saveKey = None
			if not keyLight:
				import chimera
				keyLight = chimera.DirectionalLight()
				keyLight.diffuse = keyLight.specular \
							= self.diffuse.get()
				keyLight.diffuseScale = self.diffuseScale.get()
				keyLight.specularScale = 1
				# use default from chimera module
				from math import sin, cos, radians
				angle = radians(45)
				keyLight.direction = chimera.Vector(
					-sin(angle / 2), sin(angle), cos(angle))
				self.lensViewer.keyLight = keyLight
			fillLight = self.lensViewer.fillLight
			if not fillLight and self.saveFill:
				# bring back original in simple interface
				fillLight = self.saveFill
				self.lensViewer.fillLight = fillLight
				self.saveFill = None
			if not fillLight:
				import chimera
				fillLight = chimera.DirectionalLight()
				fillLight.diffuse = keyLight.specular \
							= self.diffuse.get()
				fillLight.diffuseScale = self.diffuseScale.get()
				fillLight.specularScale = 0
				# use default from chimera module
				from math import sin, cos, radians
				angle = radians(15)
				fillLight.direction = chimera.Vector(sin(angle),
							sin(angle), cos(angle))
				self.lensViewer.fillLight = fillLight
			brightness, contrast = self._calculateBrightnessContrast()
			self.brightness.set_value(brightness)
			self.contrast.set_value(contrast)
			if not self.light:
				# update in case user goes to Advanced version
				if self.whichLight.getvalue() == "key light":
					self.light = self.lensViewer.keyLight
				else:
					self.light = self.lensViewer.fillLight
		elif value == self.Interface_Shininess:
			try:
				from _LightViewer import LightViewer
				self.viewer.mode = LightViewer.Shininess
			except ImportError:
				pass
			self.advancedFrame.pack_forget()
			self.simpleFrame.pack_forget()
			self.shininessFrame.pack()

	def _setBrightnessContrast(self):
		brightness = self.brightness.value()
		contrast = self.contrast.value()
		if not brightness or not contrast:
			return
		keyLight = self.lensViewer.keyLight
		fillLight = self.lensViewer.fillLight
		kd = keyLight.direction
		fd = fillLight.direction
		overlap = (kd * fd) / kd.length / fd.length
		fillLight.diffuseScale = brightness / contrast
		keyLight.diffuseScale = brightness \
					- overlap * fillLight.diffuseScale

	def _setShininess(self, opt=None):
		self.saveui.setItemChanged(True)
		shininess = self.shininess.get()
		brightness = self.shinyBrightness.get()
		rgb = self.shinySpecular.get().rgba()[:3]
		self._updateMaterials(shininess, scaledColor(rgb, brightness))
		self.updatedShininess = True

	def _updateMaterials(self, shininess, specular):
		import chimera
		mat = chimera.Material.lookup("default")
		mat.shininess = shininess
		mat.specular = specular

		# _surface models don't use default material,
		# so set their material
		import chimera, _surface
		for m in chimera.openModels.list(
				modelTypes=[_surface.SurfaceModel]):
			m.material = mat

	# Save and restore methods

	def setFromParams(self, p):
		self._setLightFromParams(p["key"], "keyLight", "saveKey")
		self._setLightFromParams(p["fill"], "fillLight", "saveFill")
		try:
			params = p["shininess"]
		except KeyError:
			pass
		else:
			self._setShininessFromParams(params)
		if self.whichLight is not None:
			self._setLight(self.whichLight.getvalue(),
					forceUpdate=1)
			self._chooseInterface()
		self._setQualityFromParams(p.get('quality',None))

	def _setLightFromParams(self, params, activeName, saveName):
		import chimera
		active, diff, diffScale, spec, specScale, dir = params
		light = self._setActiveLight(active, activeName, saveName)
		light.diffuse = chimera.MaterialColor(*diff)
		light.diffuseScale = diffScale
		light.specular = chimera.MaterialColor(*spec)
		light.specularScale = specScale
		light.direction = chimera.Vector(*dir)

	def _setShininessFromParams(self, params):
		if len(params) == 2:
			shininess, specular = params
		else:
			shininess, specular, brightness = params
			try:
				self.shinyBrightness.set(brightness)
			except AttributeError:
				# UI might not exist yet
				self.restoreShinyBrightness = brightness
		self._updateMaterials(shininess, specular)

	def _setQualityFromParams(self, q):
		if q is None:
			return
		setLightQuality(self.lensViewer, q)
		if hasattr(self, 'quality'):
			self.quality.set(q)

	def _setActiveLight(self, active, activeName, saveName):
		al = getattr(self, activeName)
		sl = getattr(self, saveName)
		if active:
			# New state has active light
			if al is None:
				# Current state has inactive light
				if sl is None:
					sl = self._makeLight()
				setattr(self, activeName, sl)
				setattr(self, saveName, None)
				setattr(self.lensViewer, activeName, sl)
				return sl
			else:
				# Current state has active light
				return al
		else:
			# New state has inactive light
			if al is None:
				# Current state has inactive light
				if sl is None:
					sl = self._makeLight()
				return sl
			else:
				# Current state has active light
				setattr(self, activeName, None)
				setattr(self, saveName, al)
				setattr(self.lensViewer, activeName, None)
				return al

	def currentParams(self):
		return { "key": self._paramsFromLight(self.keyLight,
							self.saveKey),
			"fill": self._paramsFromLight(self.fillLight,
							self.saveFill),
			"shininess": self._paramsFromShininess(),
			"quality": self._paramsFromQuality(), }

	def _paramsFromLight(self, light, saveLight):
		if light is not None:
			active = True
			l = light
		elif saveLight is not None:
			active = False
			l = saveLight
		else:
			return ( False, (1.0, 1.0, 1.0), 1.0,
					(1.0, 1.0, 1.0), 1.0,
					(1.0, 1.0, 1.0) )
		return ( active, l.diffuse.ambientDiffuse, l.diffuseScale,
				l.specular.ambientDiffuse, l.specularScale,
				l.direction.data() )

	def _paramsFromShininess(self):
		import chimera
		mat = chimera.Material.lookup("default")
		try:
			brightness = self.shinyBrightness.get()
		except AttributeError:
			# UI might not exist yet
			if self.restoreShinyBrightness is not None:
				brightness = self.restoreShinyBrightness
			else:
				brightness = 1.0
		return (mat.shininess, mat.specular, brightness)

	def _paramsFromQuality(self):
		try:
			q = self.quality.get()
		except AttributeError:
			# UI does not exist yet
			if self.lensViewer.haveShader():
				q = 'glossy'
			else:
				q = 'normal'
		return q

	def saveSession(self, trigger, closure, f):
		print >> f, \
"""
def restoreLightController():
	import Lighting
	c = Lighting.get().setFromParams(%s)
try:
	restoreLightController()
except:
	reportRestoreError("Error restoring lighting parameters")
""" % self.currentParams()

	# Callback functions used by SaveUI

	def saveui_label(self):
		return "Lighting"

	def saveui_presetItems(self):
		return [ SystemDefault ]

	def saveui_defaultItem(self):
		try:
			self.prefs[UserDefault]
		except KeyError:
			return SystemDefault
		else:
			return UserDefault

	def saveui_userItems(self):
		return self.prefs.keys()

	def saveui_select(self, name):
		if name == SystemDefault:
			self.setFromParams(self.systemDefault)
		else:
			self.setFromParams(self.prefs[name])

	def saveui_save(self, name):
		self.prefs[name] = self.currentParams()
		self.prefs.saveToFile()
		return True

	def saveui_delete(self, name):
		del self.prefs[name]
		self.prefs.saveToFile()
		return True

	# Callback functions used by ViewDialog

	def save(self):
		self.saveui.saveAs(UserDefault, confirm=False)

	def restore(self):
		try:
			params = self.prefs[UserDefault]
		except KeyError:
			self.setFromParams(self.systemDefault)
		else:
			self.setFromParams(params)

	def reset(self):
		self.setFromParams(self.systemDefault)

def setLightQuality(viewer, q):
	s = (q == 'glossy')
	if s == viewer.haveShader():
		return
	if s:
		from Lighting.shader import vShader, fShader
	else:
		vShader = fShader = None
	from chimera import nogui
	if not nogui:
		viewer.setShader(vShader, fShader)
	# Update lighting dialog quality setting.
	c = singleton()
	if hasattr(c, 'quality'):
		c.quality.set(q)

def normalizedColor(rgb, brightness=None):
	# Given rgb may have components > 1.  In this case scale to
	# produce maximum color component of 1.
	b = max(rgb)
	if brightness is None:
		if b <= 1:
			return rgb, 1.0
	elif b < brightness:
		# Only use the given brightness if it is high enough to
		# yield a specular color with components <= 1
		b = brightness
	return tuple([ c / b for c in rgb ]), b

def scaledColor(rgb, b):
	return tuple([ c * b for c in rgb ])

def display():
	from chimera.extension.StdTools import raiseViewingTab
	controller = singleton()
	raiseViewingTab(controller.Name)
	controller.showInterface(controller.Interface_LightsBasic)
