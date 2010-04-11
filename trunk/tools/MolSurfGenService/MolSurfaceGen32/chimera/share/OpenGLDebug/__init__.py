from __future__ import with_statement
import libgfxinfo as gi
import os, re

all = ('checkConfig', 'FeatureNames', 'Features')

FeatureNames = [''] * gi.NumFeatures	# map int to feature names
Features = {}				# map feature names to int

def init():
	global FeatureNames
	SKIP = set(("Not", "Extension", "Native", "Disabled", "NumFeatures"))
	for k in vars(gi):
		if k in SKIP:
			continue
		v = getattr(gi, k)
		if isinstance(v, int):
			FeatureNames[v] = k
			Features[k] = v
	assert(len(FeatureNames) == gi.NumFeatures)
init()

escape = re.escape

un = re.compile(r'\\(.)')
def unescape(s):
	return un.sub(r'\1', s)

def writeGfxInfo(file, features):
	import chimera.version as chver
	print >> file, '#CHIMERA_RELEASE', escape(chver.release)
	print >> file, 'VENDOR', escape(gi.getVendor())
	print >> file, 'RENDERER', escape(gi.getRenderer())
	print >> file, 'VERSION', escape(gi.getVersion())
	print >> file, 'OS', escape(gi.getOS())
	print >> file
	for i in range(gi.NumFeatures):
		if gi.hasInfo(i) & (gi.Extension|gi.Native):
			if features[i]:
				print >> file, "enable",
			else:
				print >> file, "disable",
			print >> file, FeatureNames[i]

def readGfxInfo(file):
	release = vendor = renderer = version = os = None
	settings = [False] * gi.NumFeatures
	for line in file:
		line = line.strip()
		if not line:
			continue
		cmd, value = line.split(' ', 1)
		if cmd == 'disable':
			try:
				settings[Features[value]] = False
			except KeyError:
				pass
		elif cmd == 'enable':
			try:
				settings[Features[value]] = True
			except KeyError:
				pass
		elif cmd == "#CHIMERA_RELEASE":
			release = unescape(value)
		elif cmd == "VENDOR":
			vendor = unescape(value)
		elif cmd == "RENDERER":
			renderer = unescape(value)
		elif cmd == "VERSION":
			version = unescape(value)
		elif cmd == "OS":
			os = unescape(value)

	return release, vendor, renderer, version, os, settings

def filenames():
	import chimera
	pf = chimera.pathFinder()
	paths = pf.pathList("", "gfxinfo.txt")
	paths = paths[:-1]	# skip system location
	paths.reverse()
	for p in paths:
		if os.path.isabs(p):
			name = p
	else:
		name = os.path.abspath(paths[0])
	base = os.path.splitext(name)[0]
	save = base + '.sav'
	return name, save

from chimera.baseDialog import ModalDialog, buttonFuncName
from chimera import tkoptions
import Tkinter as Tk
import Tix

class BooleanOption(tkoptions.Option):
	"""use boolean check box (no multivalues)"""

	def _addOption(self, row, col, **kw):
		self._var = Tk.BooleanVar(self._master)
		self._option = Tk.Checkbutton(self._master, indicatoron=Tk.TRUE,
			relief=Tk.FLAT, highlightthickness=0, command=self._set,
			variable=self._var)
		if row == -1:
			self._option.pack(side=Tk.RIGHT)
		else:
			self._option.grid(row=row, column=col, sticky=Tk.W)

	def get(self):
		b = self._var.get()
		if b:
			return 1
		return 0

	def set(self, value):
		if value:
			value = 1
		else:
			value = 0
		self._var.set(value)

	def setMultiple(self):
		pass

class OpenGLDebug(ModalDialog):
	"""Debug problems with graphics driver"""

	title = 'Debug Graphics Driver'
	buttons = ('Start Chimera',)
	default = buttons[0]
	help = "ContributedSoftware/debug/debug.html"

	def __init__(self, graphics, msg, master=None, *args, **kw):
		self.features = []
		self.graphics = graphics
		self.message = msg
		ModalDialog.__init__(self, master, resizable=False, *args, **kw)

	def fillInUI(self, parent):
		name, save = filenames()
		label = Tk.Label(parent, justify=Tk.LEFT,
			text=
			"This is a tool for disabling graphics features that might be\n"
			"unreliable on your platform.  Changing settings often results\n"
			"in lower performance or lower visual quality.\n")
		label.pack(padx=2)
		if self.message:
			label = Tk.Label(parent, justify=Tk.LEFT,
					foreground='red', text=self.message)
			label.pack(padx=2)

		oglinfo = Tix.LabelFrame(parent, label="OpenGL information")
		oglinfo.pack(padx=2)
		n = Tk.Label(oglinfo.frame, text="Vendor:")
		n.grid(row=0, column=0, sticky='e', padx=2)
		v = Tk.Label(oglinfo.frame, text=gi.getVendor())
		v.grid(row=0, column=1, sticky='w', padx=2)
		n = Tk.Label(oglinfo.frame, text="Renderer:")
		n.grid(row=1, column=0, sticky='e', padx=2)
		v = Tk.Label(oglinfo.frame, text=gi.getRenderer())
		v.grid(row=1, column=1, sticky='w', padx=2)
		n = Tk.Label(oglinfo.frame, text="Version:")
		n.grid(row=2, column=0, sticky='e', padx=2)
		v = Tk.Label(oglinfo.frame, text=gi.getVersion())
		v.grid(row=2, column=1, sticky='w', padx=2)
		n = Tk.Label(oglinfo.frame, text="OS:")
		n.grid(row=3, column=0, sticky='e', padx=2)
		v = Tk.Label(oglinfo.frame, text=gi.getOS())
		v.grid(row=3, column=1, sticky='w', padx=2)

		features = Tix.LabelFrame(parent, label="Enabled OpenGL features:")
		features.pack(padx=2)
		for i in range(gi.NumFeatures):
			b = BooleanOption(features.frame, i // 2,
					FeatureNames[i], gi.has(i), None,
					startCol=2 * (i % 2))
			if (gi.hasInfo(i) & (gi.Extension|gi.Native)) == 0:
				b.disable()
			self.features.append(b)
		self.factoryDefaults = tuple(f.get() for f in self.features)

		self.Actions = (
			'Disable All', 'Revert to Saved',
			'Factory Defaults', 'Save',
		)
		self.actionWidgets = {}
		for a in self.Actions:
			def command(s=self, a=a):
				if s.actionWidgets[a].cget('state') != 'disabled':
					getattr(s, buttonFuncName(a))()
			b = Tk.Button(parent, text=a, command=command)
			b.pack(side=Tk.RIGHT, padx=2, pady=2)
			self.actionWidgets[a] = b

		if not os.path.exists(save):
			b = self.actionWidgets['Revert to Saved']
			b.config(state=Tk.DISABLED)
		elif not self.message:
			self.ReverttoSaved()

	def StartChimera(self):
		self.Cancel()
		import chimera
		global _report
		_report = chimera.triggers.addHandler(chimera.APPQUIT,
							reportConfig, None)
		name, save = filenames()
		for i in range(gi.NumFeatures):
			if self.factoryDefaults[i] != self.features[i].get():
				break
		else:
			return
		dir = os.path.dirname(name)
		if not os.path.exists(dir):
			os.mkdir(dir)
		with open(name, 'w') as info:
			writeGfxInfo(info, [f.get() for f in self.features])

	def Save(self):
		name, save = filenames()
		for i in range(gi.NumFeatures):
			if self.factoryDefaults[i] != self.features[i].get():
				break
		else:
			if os.path.exists(save):
				os.remove(save)
			b = self.actionWidgets['Revert to Saved']
			b.config(state=Tk.DISABLED)
			return
		dir = os.path.dirname(save)
		if not os.path.exists(dir):
			os.mkdir(dir)
		with open(save, 'w') as info:
			writeGfxInfo(info, [f.get() for f in self.features])
		b = self.actionWidgets['Revert to Saved']
		b.config(state=Tk.NORMAL)

	def FactoryDefaults(self):
		for i in range(gi.NumFeatures):
			self.features[i].set(self.factoryDefaults[i])

	def ReverttoSaved(self):
		name, save = filenames()
		with open(save) as f:
			release, vendor, renderer, version, osver, settings = readGfxInfo(f)
		for i in range(gi.NumFeatures):
			self.features[i].set(settings[i])

	def DisableAll(self):
		for b in self.features:
			b.set(False)

def reportConfig(*args):
	"""submit configuration back to chimera team"""
	from tkMessageBox import askyesno
	name, save = filenames()
	curExists = os.path.exists(name)
	if curExists:
		os.remove(name)
	savExists = os.path.exists(save)
	if not curExists and not savExists:
		return
	curInfo = (
		gi.getVendor(), gi.getRenderer(), gi.getVersion(), gi.getOS(),
		[gi.has(i) for i in range(gi.NumFeatures)]
	)
	if savExists:
		with open(save) as f:
			savInfo = readGfxInfo(f)
	else:
		savInfo = None
	if curInfo != savInfo \
	and askyesno(title="OpenGL Debug Report", default="no",
			message="Save current OpenGL debug configuration?"):
		with open(save, 'w') as f:
			writeGfxInfo(f, curInfo[4])
		savExists = True
		savInfo = curInfo

	if not savExists or curInfo != savInfo:
		# if the user didn't care to save the configuration,
		# we don't want to know about it
		return
	if not askyesno(title="OpenGL Debug Report", default="no",
			message="Report successful OpenGL debug configuration to Chimera team?"):
		return
	from cStringIO import StringIO
	info = StringIO()
	print >> info, 'Results of OpenGL Debugging:\n'
	writeGfxInfo(info, curInfo[4])
	import BugReport
	br_gui = BugReport.displayDialog(wait=True)
	if not br_gui:
		return
	br = BugReport.BugReport(info=info.getvalue(),
			description='Successful OpenGL debug configuration')
	br_gui.setBugReport(br)
	if not br_gui._toplevel.winfo_viewable():
		br_gui._toplevel.wait_visibility()
	while br_gui._toplevel.winfo_viewable():
		br_gui._toplevel.wait_visibility() # wait for it to disappear

def checkForChange(save):
	if not os.path.exists(save):
		return ""
	with open(save) as f:
		release, vendor, renderer, version, osver, settings = readGfxInfo(f)
	import chimera.version as chver
	if release != chver.release:
		return "Different chimera version found."
	if vendor != gi.getVendor() \
	or renderer != gi.getRenderer():
		return "Different graphics card found."
	if version != gi.getVersion():
		return "New graphics driver found."
	if osver != gi.getOS():
		return  "Different operating system found."
	return ""

def checkConfig(parent, debug_opengl):
	import Togl
	try:
		graphics = Togl.Togl(parent, width=1, height=1)
	except Tk.TclError, what:
		e = str(what)
		if (e.startswith("couldn't choose pixel format")
		or e.startswith("could not create rendering context")):
			e = ("Display misconfiguration.  Please "
			"increase the color quality (24 bit color or "
			"greater), update your display (graphics) "
			"driver, and/or upgrade your graphics card.  "
			"Also see chimera installation instructions.")
		else:
			e = "Error initializing OpenGL: %s" % e
		import chimera
		raise chimera.ChimeraExit(e)
	graphics.place()
	graphics.update_idletasks()
	if not graphics.winfo_viewable():
		graphics.wait_visibility()

	try:
		name, save = filenames()
		if os.path.exists(name):
			os.remove(name)
		gi.makeWSCurrent()
		gi.makeCurrent()
		msg = checkForChange(save)
		if not msg and not debug_opengl:
			if os.path.exists(save):
				import shutil
				shutil.copyfile(save, name)
			return
		if msg:
			msg += ("  Previous configuration ignored.\n"
				"Using Factory Defaults.\n")

		o = OpenGLDebug(graphics, msg)
		o.run(parent)
	finally:
		gi._reset()
		# Don't destory here, let destruction of splash screen do it
		#graphics.destroy()
