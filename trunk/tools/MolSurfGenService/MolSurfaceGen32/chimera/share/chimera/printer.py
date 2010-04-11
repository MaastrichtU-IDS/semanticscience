import chimera
from chimera.baseDialog import ModelessDialog, Cancel, OK, ModalDialog
from chimera.tkoptions import FloatOption, EnumOption, SymbolicEnumOption, IntOption, StringOption, Option, BooleanOption, InputFileOption
import Tkinter as Tk
import Tix
from math import log, pow, sqrt
from chimera import help
import tempfile, os, re
import preferences
import replyobj

# augment PIL's tiff saving code with the ability to compress files
# based on <http://aspn.activestate.com/ASPN/Mail/Message/image-sig/582370>
def _tiff_save(im, fp, filename):
	from PIL import TiffImagePlugin
	# check compression mode
	try:
		compression = im.encoderinfo["compression"]
	except KeyError:
		# use standard driver
		return TiffImagePlugin._save(im, fp, filename)
	# compress via temporary file
	#if compression not in ("lzw", "zip", "jpeg", "packbits", "g3", "g4"):
	if compression not in ("lzw", "lzw:2"):
		raise IOError("unknown TIFF compression mode")
	fp.close()
	import tempfile, os, subprocess
	tiffcp = findExecutable('tiffcp')
	if tiffcp == None:
		raise IOError("TIFF compression failed: missing tiffcp program")
	t, tmp = tempfile.mkstemp(suffix='.tif')
	t = os.fdopen(t, 'wb')
	TiffImagePlugin._save(im, t, tmp)
	t.close()
	retcode = subprocess.call([tiffcp, "-c", compression, tmp, filename])
	try:
		os.remove(tmp)
	except OSError:
		pass
	if retcode != 0:
		raise IOError("TIFF compression failed")

from PIL import Image, TiffImagePlugin
Image.register_save(TiffImagePlugin.TiffImageFile.format, _tiff_save)
del Image, TiffImagePlugin

# key is paper type name
# value is tuple (width, height): size of imagable area in points
#
def mm2pt(mm):
	return mm / 25.4 * 72
def in2pt(inches):
	return inches * 72

paper_types = {
	# Note: only list papers that are taller than wide (Portrait mode)
	# extra paper types for AGFA "ChromaScript"
	# "35mm": ( in2pt(7), in2pt(10.5) ),
	"35mm": ( in2pt(7.333333), in2pt(11) ),		# for Concurrence
	#
	# from Appendex B of Adobe's "PostScript Printer Description File
	# Format Specification Version 4.3"
	#
	# ISO/JIS Standard "A" Sizes
	"A2": ( mm2pt(420), mm2pt(594) ),
	"A3": ( mm2pt(297), mm2pt(420) ),
	"A4": ( mm2pt(210), mm2pt(297) ),
	"A5": ( mm2pt(148), mm2pt(210) ),
	"A6": ( mm2pt(105), mm2pt(148) ),
	"A7": ( mm2pt(74), mm2pt(105) ),
	# Other Standard Page Sizes
	"executive": ( in2pt(7.25), in2pt(10.5) ),
	"ledger": ( in2pt(17), in2pt(11) ),
	"legal": ( in2pt(8.5), in2pt(14) ),
	"letter": ( in2pt(8.5), in2pt(11) ),
	"postcard": ( mm2pt(100), mm2pt(148) ),	# (Japanese)
	"tabloid": ( in2pt(11), in2pt(17) ),
	"other": (0, 0)
}

convert = {
	'points': 1.0,
	'inches': 72.0,
	'millimeters': 72.0 / 25.4,
	'centimeters': 72.0 / 2.54,
}

class UnitsOption(EnumOption):
	values = convert.keys()
	values.sort()

class ImageUnitsOption(EnumOption):
	values = ['pixels']

class OrientationOption(EnumOption):
	values = ['portrait', 'landscape']

class PaperTypeOption(EnumOption):
	values = paper_types.keys()
	values.sort()

class ColorsOption(SymbolicEnumOption):
	labels = ('3', '3 + black', '4', '5', '5 + black' , '6')
	values = (3, 3, 4, 5, 5, 6)

class SupersampleOption(SymbolicEnumOption):
	labels = ('1x1', '2x2', '3x3', '4x4', '5x5' , '6x6')
	values = (1, 2, 3, 4, 5, 6)
	balloon = "How many pixels are sampled in the X and Y dimensions\n" \
		  "for each pixel in the final saved image.  Higher values\n" \
		  "increase the smoothness of edges in saved images and\n" \
		  "increase calculation time."

class _PrintModeOption(Option):
	SAME = "same as screen"

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
		modes = chimera.Camera.modes(printOnly=True)
		modes.sort(key=str.lower)
		modes.insert(0, self.SAME)
		for v in modes:
			self.menu.add_radiobutton(label=v, variable=self._var,
						value=v, command=self._set)

	def get(self):
		return self._var.get()

	def set(self, value):
		self._var.set(value)

class OutputAlphaOption(SymbolicEnumOption):
	labels = ('false', 'true', 'same as chimera')
	values = (0, 1, 2)

ONLY_STEREO_CAMERAS = 2
class AdjustFOVOption(SymbolicEnumOption):
	labels = ('no', 'yes', 'stereo cameras')
	values = (0, 1, 2)

PAGE_SETUP = 'Page Setup'		# preferences category
UNITS = 'Units'
PAGE_WIDTH = 'Page width'
PAGE_HEIGHT = 'Page height'
PAGE_ORIENTATION = 'Page orientation'
PAPER_TYPE = 'Paper type'
PRINTER_CMD = 'Printer command'

IMAGE_SETUP = 'Image Setup'		# preferences category
USE_PRINT_UNITS = 'Use print units'
DPI = 'Print resolution (dpi)'
ADJUST_FOV = 'Adjust field of view'
UNIT_PIXELS = 'Pixels per unit'
PRINTER_DOTS = 'Printer dots per unit'
COLORS = 'Colors per dot'
SHADES = 'Shades per color'
SUPERSAMPLE = 'Supersample'

IMAGE_CREDITS = 'Image Credits'		# preferences category
ARTIST = 'Artist'
COPYRIGHT = 'Copyright'

POVRAY_AGREE = 'POV-Ray'		# hidden preferences category
LICENSE_AGREE = 'accepted license agreement'
POVRAY_SETUP = 'POV-Ray Options'	# preferences category
POVRAY_EXE = 'POV-Ray executable'
SHOW_PREVIEW = 'Show preview'
POV_QUALITY = 'Quality'				# 9
ANTIALIAS = 'Antialias'				# On
ANTIALIAS_DEPTH = 'Antialias depth'		# 3
ANTIALIAS_THRESHOLD = 'Antialias threshold'	# 1.0
ANTIALIAS_METHOD = 'Antialias method'
JITTER = 'Jitter'				# Off
JITTER_AMOUNT = 'Jitter amount'			# 0.5
OUTPUT_ALPHA = 'Transparent background'
WAIT_POVRAY = 'Wait for POV-Ray to finish'	# false
KEEP_INPUT = 'Keep POV-Ray input files'		# true

DEFAULT_JPEG_QUALITY = 90

#chimera.triggers.addTrigger(PAGE_SETUP)
#chimera.triggers.addTrigger(IMAGE_SETUP)

def initializeCreditPreferences():
	if os.environ.has_key('NAME'):
		artist = os.environ['NAME']
	elif os.environ.has_key('USERNAME'):
		artist = os.environ['USERNAME']
	elif os.environ.has_key('USER'):
		artist = os.environ['USER']
	elif os.environ.has_key('LOGNAME'):
		artist = os.environ['LOGNAME']
	else:
		artist = ""
	prefs = {
		ARTIST: (StringOption, artist, None),
		COPYRIGHT: (StringOption, "", None)
	}
	prefOrder = [
		ARTIST, COPYRIGHT
	]
	preferences.register(IMAGE_CREDITS, prefs)
	preferences.setOrder(IMAGE_CREDITS, prefOrder)

class PageSetupCategory(preferences.Category):
	"""images setup has it's own ui"""

	def __init__(self, master=None, *args, **kw):
		preferences.Category.__init__(self, master, *args, **kw)
		_initializeCreditPreferences()

		itops = os.path.join(os.environ["CHIMERA"], "bin", "itops") \
							+ " -q -R %s | lpr"
		self._options = {
			# last argument to Option is:
			#	[ tkoption, display name, dialog callback ]
			UNITS: preferences.Option(self, "inches", None,
				[UnitsOption, None, self.updateUnits]),
			PAGE_WIDTH: preferences.Option(self, 8.5, None,
				[FloatOption, None, None],
				UIkw={ 'min': 1e-10 }),
			PAGE_HEIGHT: preferences.Option(self, 11, None,
				[FloatOption, None, None],
				UIkw={ 'min': 1e-10 }),
			PAGE_ORIENTATION: preferences.Option(self, 'portrait',
				None,
				[OrientationOption, None, self.updateOrientation]),
			PAPER_TYPE: preferences.Option(self, "letter", None,
				[PaperTypeOption, None, self.updatePaper]),
			PRINTER_CMD: preferences.Option(self, itops, None,
					[StringOption, "", None]),
		}
		self.adjust = convert[self.get(UNITS)]

	def load(self, optDict, notifyUI=1):
		preferences.Category.load(self, optDict, notifyUI=1)
		self.adjust = convert[self.get(UNITS)]
		self.updateResolution()

	def ui(self, master):
		if self._ui:
			return self._ui

		self._ui = Tk.Frame(master)

		self.units = self._add_opt(UNITS, self._ui, -1)

		self.page = Tix.LabelFrame(self._ui, label="Page Options")
		self.page.pack(fill=Tk.X)
		self.paperType = self._add_opt(PAPER_TYPE, self.page.frame, 0)
		self.pOrient = self._add_opt(PAGE_ORIENTATION, self.page.frame, 1)
		self.pWidth = self._add_opt(PAGE_WIDTH, self.page.frame, 2)
		self.pHeight = self._add_opt(PAGE_HEIGHT, self.page.frame, 3)

		pcmd = Tix.LabelFrame(self._ui, label="Printer Command:")
		pcmd.pack(fill=Tk.X)
		cmd = self._add_opt(PRINTER_CMD, pcmd.frame, -1)
		cmd._option.xview(Tk.END)

	def _add_opt(self, attribute, master, row):
		opt = self._options[attribute]
		closure = opt.closure()
		def cb(tkopt, o=opt, tkcb=closure[2]):
			o.set(tkopt.get())
			if tkcb:
				tkcb(tkopt)
		initialValue = opt.get()
		if closure[1] is not None:
			name = closure[1]
		else:
			name = attribute
		tkOpt = closure[0](master, row, name, opt.defaultValue(), cb,
			attribute=attribute, **opt.UIkw())
		tkOpt.set(initialValue)
		return tkOpt

	def add(self, name, defaultValue, callback, closure, notifyUI=1):
		raise RuntimeError, "not applicable"
	def remove(self, name, notifyUI=1):
		raise RuntimeError, "not applicable"
	def destroy(self, notifyUI=1):
		raise RuntimeError, "not applicable"
	def _destroyUI(self, notifyUI):
		raise RuntimeError, "not applicable"

	def updatePaper(self, option):
		pWidth, pHeight = paper_types[option.get()]
		if self.get(PAGE_ORIENTATION) == 'Landscape':
			pWidth, pHeight = pHeight, pWidth
		w = pWidth / self.adjust
		self.set(PAGE_WIDTH, w)
		self.pWidth.set(w)
		h = pHeight / self.adjust
		self.pHeight.set(h)
		self.set(PAGE_HEIGHT, h)
		self.updateResolution()

	def updateUnits(self, option):
		adjust = convert[option.get()]
		if adjust == self.adjust:
			return
		factor = self.adjust / adjust
		w = self.get(PAGE_WIDTH) * factor
		self.pWidth.set(w)
		self.set(PAGE_WIDTH, w)
		h = self.get(PAGE_HEIGHT) * factor
		self.pHeight.set(h)
		self.set(PAGE_HEIGHT, h)
		self.adjust = adjust

	def updateOrientation(self, option):
		orientation = option.get()
		w = self.get(PAGE_WIDTH)
		h = self.get(PAGE_HEIGHT)
		if (orientation == 'Portrait' and w > h) \
		or (orientation == 'Landscape' and w < h):
			self.pWidth.set(h)
			self.set(PAGE_WIDTH, h)
			self.pHeight.set(w)
			self.set(PAGE_HEIGHT, w)

#class ImageSetupCategory(preferences.Category):
#	"""images setup has it's own ui"""
#
#	def __init__(self, master=None, *args, **kw):
#		preferences.Category.__init__(self, master, *args, **kw)
#		_initializeCreditPreferences()
#
#		self.resolution = None
#		self._options = {
#			# last argument to Option is:
#			#	[ tkoption, display name, dialog callback ]
#			UNITS: preferences.Option(self, "inches", None,
#				[UnitsOption, None, self.updateUnits]),
#			UNIT_PIXELS: preferences.Option(self, 100, None,
#				[FloatOption, None, self.updateResolution],
#				UIkw={ 'min': 1 }),
#			PRINTER_DOTS: preferences.Option(self, 300, None,
#				[FloatOption, None, self.updateResolution],
#				UIkw={ 'min': 1 }),
#			COLORS: preferences.Option(self, 3, None,
#				[ColorsOption, None, self.updateResolution]),
#			SHADES: preferences.Option(self, 2, None,
#				[IntOption, None, self.updateResolution],
#				UIkw={ 'min': 2 }),
#			SUPERSAMPLE: preferences.Option(self, 3, None,
#				[SupersampleOption, None, self.updateSS]),
#		}
#		self.adjust = convert[self.get(UNITS)]
#
#	def load(self, optDict, notifyUI=1):
#		preferences.Category.load(self, optDict, notifyUI=1)
#		self.adjust = convert[self.get(UNITS)]
#		self.updateResolution()
#
#	def ui(self, master):
#		if self._ui:
#			return self._ui
#
#		self._ui = Tk.Frame(master)
#
#		self.units = self._add_opt(UNITS, self._ui, -1)
#
#		image = Tix.LabelFrame(self._ui, label="Image Resolution")
#		image.pack(fill=Tk.X)
#		self.dots = self._add_opt(UNIT_PIXELS, image.frame, -1)
#		calc = Tix.LabelFrame(image.frame, label="Resolution Calculator")
#		calc.pack(fill=Tk.X)
#		self.printerDots = self._add_opt(PRINTER_DOTS, calc.frame, -1)
#		self.colors = self._add_opt(COLORS, calc.frame, -1)
#		self.shades = self._add_opt(SHADES, calc.frame, -1)
#		bg = calc.cget('background')
#		self.resolution = Tk.Text(calc.frame, width=1, height=2, padx=2,
#					background=bg, relief=Tk.GROOVE)
#		self.resolution.tag_configure("center", justify=Tk.CENTER)
#		self.resolution.tag_configure("underline", underline=True)
#		self.resolution.pack()
#
#		aa = Tix.LabelFrame(self._ui, label="Antialiasing:")
#		aa.pack(fill=Tk.X)
#		ss = self._add_opt(SUPERSAMPLE, aa.frame, -1)
#
#		self.updateResolution()
#
#	def _add_opt(self, attribute, master, row):
#		opt = self._options[attribute]
#		closure = opt.closure()
#		def cb(tkopt, o=opt, tkcb=closure[2]):
#			o.set(tkopt.get())
#			if tkcb:
#				tkcb(tkopt)
#		initialValue = opt.get()
#		if closure[1] is not None:
#			name = closure[1]
#		else:
#			name = attribute
#		tkOpt = closure[0](master, row, name, opt.defaultValue(), cb,
#			attribute=attribute, **opt.UIkw())
#		tkOpt.set(initialValue)
#		return tkOpt
#
#	def add(self, name, defaultValue, callback, closure, notifyUI=1):
#		raise RuntimeError, "not applicable"
#	def remove(self, name, notifyUI=1):
#		raise RuntimeError, "not applicable"
#	def destroy(self, notifyUI=1):
#		raise RuntimeError, "not applicable"
#	def _destroyUI(self, notifyUI):
#		raise RuntimeError, "not applicable"
#
#	def updateUnits(self, option):
#		adjust = convert[option.get()]
#		if adjust == self.adjust:
#			return
#		factor = self.adjust / adjust
#		d = self.get(UNIT_PIXELS) / factor
#		self.dots.set(d)
#		self.set(UNIT_PIXELS, d)
#		d = self.get(PRINTER_DOTS) / factor
#		self.printerDots.set(d)
#		self.set(PRINTER_DOTS, d)
#		self.adjust = adjust
#
#	def updateResolution(self, *args):
#		if self.adjust == -1:
#			res = 1
#		else:
#			dots = self.get(PRINTER_DOTS)
#			printer = pow(self.get(SHADES), self.get(COLORS))
#			# TODO: colors is based on image file depth
#			# 8 bits per color component, 3 components
#			colors = pow(pow(2, 8), 3)
#			sqDots = dots * dots
#			dotsPerColor = sqrt(log(colors) / log(printer))
#			res = dots / dotsPerColor
#		if self.resolution == None:
#			return
#		res1 = 'Recommendation for printer'
#		res2 = 'is %g pixels per unit.' % res
#		textWidth = len(res1)
#		if len(res2) > textWidth:
#		       textWidth = len(res2)
#		self.resolution.config(state=Tk.NORMAL)
#		self.resolution.delete('1.0', Tk.END)
#		self.resolution.insert(Tk.END, '%s\nis ' % res1)
#		self.resolution.insert(Tk.END, '%g' % res, 'underline')
#		self.resolution.insert(Tk.END, ' pixels per unit.')
#		self.resolution.tag_add('center', '1.0', 'end')
#		self.resolution.config(state=Tk.DISABLED, width=textWidth)
#		chimera.triggers.activateTrigger(IMAGE_SETUP, None)
#
#	def updateSS(self, option):
#		chimera.triggers.activateTrigger(IMAGE_SETUP, None)

class AntialiasMethodOption(SymbolicEnumOption):
	"""Specialization of EnumOption class for antialias method"""
	values = [1, 2]
	labels = ['fixed', 'recursive']

from CGLutil.findExecutable import findExecutable
povpath = findExecutable('povray')
if povpath == None:
	povpath = "povray"
povrayPreferences = {
	POVRAY_EXE: (InputFileOption, povpath, None),
	SHOW_PREVIEW: (BooleanOption, Tk.NO, None),
	POV_QUALITY: (IntOption, 9, None, { 'min': 0, 'max': 11 }),
	ANTIALIAS: (BooleanOption, Tk.YES, None),
	ANTIALIAS_DEPTH: (IntOption, 3, None, { "min": 1, "max": 256 }),
	ANTIALIAS_THRESHOLD: (FloatOption, 1.0, None, { "min": 0.001 }),
	ANTIALIAS_METHOD: (AntialiasMethodOption, 1, None),
	JITTER: (BooleanOption, Tk.NO, None),
	JITTER_AMOUNT: (FloatOption, 0.5, None, { "min": 0.001, "max": 2.0 }),
	OUTPUT_ALPHA: (OutputAlphaOption, 2, None),
	WAIT_POVRAY: (BooleanOption, Tk.NO, None),
	KEEP_INPUT: (BooleanOption, Tk.NO, None),
}
del povpath
povrayPreferencesOrder = [
	POVRAY_EXE, SHOW_PREVIEW, POV_QUALITY,
	ANTIALIAS, ANTIALIAS_METHOD,
	ANTIALIAS_DEPTH, ANTIALIAS_THRESHOLD,
	JITTER, JITTER_AMOUNT,
	OUTPUT_ALPHA,
	WAIT_POVRAY, KEEP_INPUT
]

class ImageSaveDialog(ModelessDialog):

	name = "Save Image"
	buttons = ['Tips', 'Save As', Cancel]
	default = 'Save As'
	help = 'UsersGuide/print.html'
	provideStatus = True

	def fillInUI(self, master):
		self._ModelTrigger = None
		#self._SetupTrigger = None
		self._SizeTrigger = None
		self.raytrace = None
		# Image Size
		imageSetup = Tix.LabelFrame(master, label="Image Size")
		imageSetup.pack(fill=Tk.X, ipadx=2, ipady=2)
		subframe = imageSetup.frame
		#subframe = Tk.Frame(imageSetup.frame)
		#subframe.pack(fill=Tk.BOTH, expand=1)

		# add in conversion factor for pixels and graphics screen
		from chimera import tkgui
		win = tkgui.app.graphics
		res = tkgui.getScreenMMWidth() / win.winfo_screenwidth()
		convert['pixels'] = mm2pt(res)

		self.matchAspect = Tk.BooleanVar(master)
		self.matchAspect.set(1)

		self.usePrint = Tk.BooleanVar(master)
		self.usePrint.set(preferences.get(IMAGE_SETUP, USE_PRINT_UNITS))
		import itertools
		row = itertools.count()

		self.showUsePrint = Tk.Checkbutton(subframe, indicatoron=1,
				variable=self.usePrint, highlightthickness=0,
				text=USE_PRINT_UNITS,
				command=self._updateUsePrint)
		self.showUsePrint.grid(columnspan=2, row=row.next(), sticky=Tk.W)

		w, h = chimera.viewer.windowSize
		self.units = ImageUnitsOption(subframe, row.next(), UNITS,
						'pixels', self.updateImageUnits)
		self.iWidth = FloatOption(subframe, row.next(), 'Image width',
					w, self.updateImageWidth, min=1e-10)
		self.iHeight = FloatOption(subframe, row.next(), 'Image height',
					h, self.updateImageHeight, min=1e-10)

		matchAspect = Tk.Checkbutton(subframe, indicatoron=1,
				variable=self.matchAspect, highlightthickness=0,
				text="Maintain current aspect ratio",
				command=self.updateMatchAspect)
		matchAspect.grid(columnspan=2, row=row.next(), sticky=Tk.W)
		self.grow = Tk.Button(imageSetup.frame, text="Grow to Fit",
					command=self.Resize, state=Tk.DISABLED)
		fitrow = row.next()
		self.grow.grid(row=fitrow, column=0, padx=2, pady=2,
								sticky=Tk.NSEW)
		self.shrink = Tk.Button(imageSetup.frame, text="Shrink to Fit",
				command=lambda f=self.Resize: f(False),
				state=Tk.DISABLED)
		self.shrink.grid(row=fitrow, column=1, padx=2, pady=2,
								sticky=Tk.NSEW)

		#fetch = Tk.Button(imageSetup.frame, text="Get Pixels",
		#				command=self.fetchWindowSize)
		#fetch.grid(row=row.next(), column=0, padx=2, pady=2, sticky=Tk.NSEW)

		#calc = Tk.Button(imageSetup.frame, text="Image Setup",
		#			command=self.showImageSetupDialog)
		#calc.grid(row=row.next(), column=1, padx=2, pady=2, sticky=Tk.NSEW)

		self.printRes = FloatOption(subframe, row.next(), DPI,
				preferences.get(IMAGE_SETUP, DPI),
				self._updatePrint, min=1)

		# Image Information
		info = Tix.LabelFrame(master, label="Image Information")
		info.pack(fill=Tk.X)
		d = Tk.Label(info.frame, text="Description:")
		d.grid(columnspan=2, row=0, column=0, sticky=Tk.W, padx=2,
									pady=1)
		self.description = Tk.Entry(info.frame)
		info.frame.grid_columnconfigure(0, weight=1)
		info.frame.grid_columnconfigure(1, weight=1)
		self.description.grid(columnspan=2, row=1, column=0,
						sticky=Tk.EW, padx=2, pady=2)
		imageCredits = Tk.Button(info.frame,
					text="Image Credits",
					command=self.showImageCreditsDialog)
		imageCredits.grid(row=2, column=0, padx=2, pady=2)
		credit = Tk.Button(info.frame, text="Citing Chimera",
				command=lambda: help.display("credits.html"))
		credit.grid(row=2, column=1, padx=2, pady=2)

		# Image camera
		self.raytrace = BooleanOption(master, -1,
				'Raytrace with POV-Ray', False,
				self._updateRaytrace)
		self.raytraceOptions = Tk.Button(master, text=POVRAY_SETUP,
					command=self.showPOVRayOptions)
		self.raytraceOptions.pack()
		self.raytraceOptions.pack_forget()
		self.supersample = SupersampleOption(master, -1, SUPERSAMPLE,
				preferences.get(IMAGE_SETUP, SUPERSAMPLE),
				self._updateSS)
		self.adjustFOV = AdjustFOVOption(master, -1, ADJUST_FOV,
				preferences.get(IMAGE_SETUP, ADJUST_FOV),
				self._updateAdjustFOV)
		self.printMode = _PrintModeOption(master, -1,
				'Image camera mode', _PrintModeOption.SAME,
				self._updatePrintMode)
		self.lenticular = IntOption(master, -1,
				'Number of lenticular images',
				chimera.Camera.lenticularImageCount(),
				self._updateLenticular, min=2, width=4)
		self.lenticular.forget()

		# switch to user's prefered units
		self.adjust = convert['pixels']
		units = preferences.get(IMAGE_SETUP, UNITS)
		self._updateUsePrint()
		self.units.set(units)
		self.updateImageUnits()

	def map(self, event=None):
		self._ModelTrigger = chimera.triggers.addHandler('Model',
						self._computeMaxLineWidth, None)
		#self._SetupTrigger = chimera.triggers.addHandler(IMAGE_SETUP,
		#				self._computeMaxLineWidth, None)
		self._SizeTrigger = chimera.triggers.addHandler(
				'graphics window size', self._resetSize, None)
		self._computeMaxLineWidth()

	def unmap(self, event=None):
		if self._ModelTrigger:
			chimera.triggers.deleteHandler('Model',
							self._ModelTrigger)
			self._ModelTrigger = None
		#if self._SetupTrigger:
		#	chimera.triggers.deleteHandler(IMAGE_SETUP,
		#					self._SetupTrigger)
		#	self._SetupTrigger = None

	def _computeMaxLineWidth(self, *args):
		if self.raytrace and self.raytrace.get():
			# not relevant if raytracing
			self.status('', blankAfter=0)
			return
		# this should be called models are modified, when the
		# image size changes and when image setup parameters
		# change (DPI, supersampling)
		opengl_max = min(
				chimera.opengl_getFloat("max point size"),
				chimera.opengl_getFloat("max line width"))
		max_lw = max([m.lineWidth
				for m in chimera.openModels.list(all=True)
					if hasattr(m, 'lineWidth')])
		# compute tile scaling factor like C++ code does
		width = self.iWidth.get()
		height = self.iHeight.get()
		horizPixels, vertPixels, supersample = \
				imageArgs(self.units.get(), width, height)
		width, height = chimera.viewer.windowSize
		tileScale = float(horizPixels) / float(width)
		tmp = float(vertPixels) / float(height)
		if tmp > tileScale:
			tileScale = tmp
		tileScale *= supersample

		opengl_max /= tileScale
		if max_lw > opengl_max:
			color = 'red'
		else:
			color = 'black'
		self.status('effective maximum line width is %g' % opengl_max,
				color=color, blankAfter=0)

	#def Print(self):
	#	self.Cancel()
	#	image, options = self.getImage()
	#	filename = tempfile.mktemp()
	#	image.save(filename, **options)
	#	cmd = preferences.get(PAGE_SETUP, PRINTER_CMD)
	#	cmd = re.sub('%s', "'" + filename + "'", cmd)
	#	os.system(cmd)
	#	os.unlink(filename)

	def SaveAs(self):
		# now save the image
		self.Cancel()
		printMode = self.printMode.get()
		raytrace = self.raytrace.get()
		if printMode == _PrintModeOption.SAME:
			printMode = None
		if not chimera.nogui and raytrace and chimera.viewer.clipping:
			dialog = ClipWarning()
			if not dialog.run(chimera.tkgui.app):
				return
		saveImage(None, self.iWidth.get(), self.iHeight.get(), 
				units=self.units.get(), master=self.uiMaster(),
				description=self.description.get().strip(),
				printMode=printMode, raytrace=raytrace)

	def Tips(self):
		import help
		help.display(self.help + "#tips")

	def Resize(self, larger=True):
		vw, vh = chimera.viewer.windowSize
		iw = self.iWidth.get()
		ih = self.iHeight.get()
		vaspect = vw / float(vh)
		iaspect = iw / float(ih)
		from chimera import tkgui
		top = tkgui.app.winfo_toplevel()
		if larger:
			if vaspect < iaspect:
				w = int(vw * iaspect / vaspect + 0.5)
				if w != vw:
					top.wm_geometry('')
					tkgui.app.graphics.config(width=w)
			elif vaspect > iaspect:
				h = int(vh * vaspect / iaspect + 0.5)
				if h != vh:
					top.wm_geometry('')
					tkgui.app.graphics.config(height=h)
		else:
			if vaspect < iaspect:
				h = int(vh * vaspect / iaspect + 0.5)
				if h != vh:
					top.wm_geometry('')
					tkgui.app.graphics.config(height=h)
			elif vaspect > iaspect:
				w = int(vw * iaspect / vaspect + 0.5)
				if w != vw:
					top.wm_geometry('')
					tkgui.app.graphics.config(width=w)

	def fetchWindowSize(self):
		w, h = chimera.viewer.windowSize
		self.units.set('pixels')
		self.updateImageUnits()
		self.iWidth.set(w)
		self.iHeight.set(h)

	def _updateRaytrace(self, option):
		raytrace = option.get()
		if raytrace:
			self.printMode.forget()
			self.lenticular.forget()
			self.supersample.forget()
			self.raytraceOptions.pack()
		else:
			self.raytraceOptions.pack_forget()
			self.printMode.manage()
			self.supersample.manage()
			self._updatePrintMode(self.printMode)
		self._computeMaxLineWidth()

	def _updatePrintMode(self, option):
		printMode = option.get()
		if printMode == 'lenticular':
			self.lenticular.manage()
		else:
			self.lenticular.forget()

	def _updateLenticular(self, option):
		count = option.get()
		chimera.Camera.setLenticularImageCount(count)

	def updateMatchAspect(self, *args):
		if self.matchAspect.get():
			self.grow.config(state=Tk.DISABLED)
			self.shrink.config(state=Tk.DISABLED)
			self.Resize()
		else:
			self.grow.config(state=Tk.NORMAL)
			self.shrink.config(state=Tk.NORMAL)

	def updateImageUnits(self, *args):
		units = self.units.get()
		if units == 'pixels':
			self.printRes.disable()
			self.adjustFOV.disable()
		else:
			self.printRes.enable()
			self.adjustFOV.enable()
		if units != preferences.get(IMAGE_SETUP, UNITS):
			preferences.set(IMAGE_SETUP, UNITS, units)
		try:
			adjust = convert[units]
		except KeyError:
			adjust = -1
		if adjust == self.adjust:
			return
		if self.adjust != -1 and adjust != -1:
			factor = self.adjust / adjust
			w = self.iWidth.get() * factor
			self.iWidth.set(w)
			h = self.iHeight.get() * factor
			self.iHeight.set(h)
		if adjust == -1:
			# entering pixel mode
			w, h = chimera.viewer.windowSize
			self.iWidth.set(w)
			self.iHeight.set(h)
		elif self.adjust == -1:
			pass
			# leaving pixel mode, sanity check
			#w, h = paper_types[preferences.get(PAGE_SETUP, PAPER_TYPE)]
			#if self.iWidth.get() > w:
			#	self.iWidth.set(w)
			#if self.iHeight.get() > h:
			#	self.iHeight.set(h)
		self.adjust = adjust
		self._computeMaxLineWidth()

	def updateImageWidth(self, option):
		# adjust height to compensate for new width
		if self.matchAspect.get():
			iWidth = option.get()
			w, h = chimera.viewer.windowSize
			self.iHeight.set(iWidth * h / w)
		self._computeMaxLineWidth()

	def updateImageHeight(self, option):
		# adjust width to compensate for new height
		if self.matchAspect.get():
			iHeight = option.get()
			w, h = chimera.viewer.windowSize
			self.iWidth.set(iHeight * w / h)
		self._computeMaxLineWidth()

	def _resetSize(self, triggerName, myData, sizes):
		width, height, mmwidth, mmheight = sizes
		units = self.units.get()
		if units == 'pixels':
			self.iWidth.set(width)
			self.iHeight.set(height)
		else:
			adjust = convert['millimeters'] / convert[units]
			self.iWidth.set(mmwidth * adjust)
			self.iHeight.set(mmheight * adjust)
		self._computeMaxLineWidth()

	def _updateUsePrint(self):
		usePrint = self.usePrint.get()
		preferences.set(IMAGE_SETUP, USE_PRINT_UNITS, usePrint)
		if not usePrint:
			values = ['pixels']
		else:
			values = convert.keys()
			try:
				values.remove('pixels')
			except ValueError:
				pass
			values.sort()
		self.units.values = values
		self.units.remakeMenu()
		if usePrint:
			self.units.set('inches')
		else:
			self.units.set('pixels')
		self.updateImageUnits()
		if not usePrint:
			self.fetchWindowSize()

	def _updatePrint(self, option):
		res = option.get()
		preferences.set(IMAGE_SETUP, DPI, res)

	def _updateAdjustFOV(self, option):
		adjust = option.get()
		preferences.set(IMAGE_SETUP, ADJUST_FOV, adjust)

	def _updateSS(self, option):
		ss = option.get()
		preferences.set(IMAGE_SETUP, SUPERSAMPLE, ss)
		self._computeMaxLineWidth()

	#def showImageSetupDialog(self, *args):
	#	import dialogs
	#	d = dialogs.display("preferences")
	#	d.setCategoryMenu(IMAGE_SETUP)

	def showImageCreditsDialog(self, *args):
		import dialogs
		d = dialogs.display("preferences")
		d.setCategoryMenu(IMAGE_CREDITS)

	def showPOVRayOptions(self, *args):
		import dialogs
		d = dialogs.display("preferences")
		d.setCategoryMenu(POVRAY_SETUP)

import dialogs
dialogs.register(ImageSaveDialog.name, ImageSaveDialog)

def imageArgs(units, width=None, height=None, supersample=None):
	"""return 3-tuple with horizontal pixels, vertical pixels, supersample"""
	if not width:
		width, height = chimera.viewer.windowSize
	if units == 'pixels':
		scale = 1
	elif preferences.get(IMAGE_SETUP, USE_PRINT_UNITS):
		adjust = convert[units] / convert['inches']
		scale = preferences.get(IMAGE_SETUP, DPI) * adjust
	else:
		# use screen resolution
		scale = convert[units] / convert['pixels']
	if supersample is None:
		supersample = preferences.get(IMAGE_SETUP, SUPERSAMPLE)
	else:
		supersample = int(supersample)
	horizPixels = int(scale * width + 0.5)
	vertPixels = int(scale * height + 0.5)
	return horizPixels, vertPixels, supersample

import re, threading, Queue
class povrayProgress(threading.Thread):

	# Example: ' 0:00:01 Rendering line 51 of 240'
	HOWFAR = re.compile(r'.*line (\d+) of (\d+)')

	def __init__(self, subproc, *args, **kw):
		self._progress = 0
		self._subproc = subproc
		self._queue = Queue.Queue()
		threading.Thread.__init__(self, *args, **kw)

	def __call__(self, subproc):
		# called in main thread
		try:
			import sys
			while 1:
				data = self._queue.get_nowait()
				sys.stdout.write(data)
		except Queue.Empty:
			pass
		return self._progress

	def run(self):
		stderr = self._subproc.stderr.fileno()
		while self._subproc.poll() == None:
			data = os.read(stderr, 128)
			if not data:
				break
			self._queue.put(data)
			m = self.HOWFAR.match(data)
			if m:
				line, total = m.groups()
				self._progress = float(line) / float(total)
		# TODO: join?
		self._subproc = None

DefaultFilter = "PNG"
FilenameFilters = [
	("EPS", ["*.eps"], ".eps"),
	("JPEG", ["*.jpg", "*.jpeg"], ".jpg"),
	("PS", ["*.ps"], ".ps"),
	("PNG", ["*.png"], ".png"),
	("PPM", ["*.ppm"], ".ppm"),
	("TIFF", ["*.tif", "*.tiff"], ".tif"),
	("TIFF-fast", ["*.tif", "*.tiff"], ".tif"),
]
DefaultStereoFilter = "Stereo JPEG"
StereoFilenameFilters = [
	("Stereo JPEG", ["*.jps"], ".jps"),
	("Stereo PNG", ["*.pns"], ".pns"),
]
DefaultRaytraceFilter = "PNG"
RaytraceFilenameFilters = [
	# Doesn't work on all platforms, and JPEG sucks, so disable
	# ("JPEG", ["*.jpg"], ".jpg"),
	("PNG", ["*.png"], ".png"),
]

from OpenSave import SaveModal
class _ChooseFileDialog(SaveModal):
	oneshot = True
	title = "Save Image As"
	historyID = "SaveImage"

	def __init__(self, format=None, filterSet='normal'):
		if filterSet == 'normal':
			filters = FilenameFilters
			defaultFilter = DefaultFilter
			title = self.title
			historyID = self.historyID
		elif filterSet == 'stereo':
			filters = FilenameFilters + StereoFilenameFilters
			defaultFilter = DefaultStereoFilter
			title = "Save Stereo Pair As"
			historyID = 'SaveStereoImage'
		elif filterSet == 'povray':
			filters = RaytraceFilenameFilters
			defaultFilter = DefaultRaytraceFilter
			title = self.title
			historyID = self.historyID
		try:
			names = [x[0] for x in filters]
			f = names.index(defaultFilter)
		except ValueError:
			f = 0
		self.quality = None
		SaveModal.__init__(self, title=title, initialfile="image",
			filters=filters, defaultFilter=f,
			setFilterCommand=self._filterChange,
			clientPos='s', clientSticky='ew', historyID=historyID)
		if format:
			self.millerBrowser.setFilter(format)

	def fillInUI(self, parent):
		SaveModal.fillInUI(self, parent)
		parent = self.clientArea
		parent.columnconfigure(0, weight=1)
		parent.columnconfigure(1, weight=1)
		parent = Tk.Frame(parent)
		parent.grid()
		self.quality = IntOption(parent, 0,
			'JPEG quality', DEFAULT_JPEG_QUALITY, None,
			min=5, max=95, width=4, sticky=Tk.E)
		if self.millerBrowser.getFilter() != 'JPEG':
			self.quality.gridUnmanage()

	def _filterChange(self, descript):
		if self.quality is None:
			return
		if descript.endswith("JPEG"):
			self.quality.gridManage()
		else:
			self.quality.gridUnmanage()

def saveImage(filename=None, width=None, height=None, format=None,
	      units="pixels", description=None, supersample=None,
	      master=None, printMode=None, raytrace=False,
	      raytracePreview=None, raytraceWait=None,
	      raytraceKeepInput=None,
	      hideDialogs=True, statusMessages=True, raiseWindow=True,
	      task=None):
	if chimera.nogui and chimera.opengl_platform() != 'OSMESA':
		raise chimera.UserError, "Need graphics to save images (or use headless Linux version)"
	if statusMessages:
		from replyobj import status
	else:
		def status(*args, **kw):
			pass
	if printMode is None:
		printMode = chimera.viewer.camera.mode()
	horizPixels, vertPixels, supersample = \
			imageArgs(units, width, height, supersample)
	savedSD = None	# saved screen distance
	if units != 'pixels':
		adjustFOV = preferences.get(IMAGE_SETUP, ADJUST_FOV)
		if adjustFOV == 1 or (adjustFOV == ONLY_STEREO_CAMERAS
						and printMode != 'mono'):
			# if image is twice as wide as screen,
			# screenDistance is half as much
			savedSD = chimera.viewer.camera.screenDistance
			adjust = convert[units] / convert['millimeters']
			image_width = width * adjust
			adjust = chimera.viewer.camera.windowWidth / image_width
			chimera.viewer.camera.screenDistance *= adjust
	if raytrace:
		if not checkPovrayLicense():
			return
		# TODO: make default an argument or preference
		if raytraceWait is None:
			raytraceWait = preferences.get(POVRAY_SETUP, WAIT_POVRAY)
		if raytraceKeepInput is None:
			raytraceKeepInput = preferences.get(POVRAY_SETUP, KEEP_INPUT)
		if raytracePreview is None:
			raytracePreview = preferences.get(POVRAY_SETUP, SHOW_PREVIEW)
		quality = DEFAULT_JPEG_QUALITY
		format = 'PNG'
		if not chimera.nogui and not filename:
			if not master:
				master = tkgui.app
			chooseDialog = _ChooseFileDialog(filterSet='povray',
					format=format)
			result = chooseDialog.run(master)
			if result is None:
				status("Image save cancelled.")
				return
			filename, format = result[0]
			quality = chooseDialog.quality.get()
		if not filename:
			replyobj.error("Need filename for POV-Ray output")
			return
		if filename.endswith('.png') or filename.endswith('.jpg'):
			povfilename = filename[:-4] + '.pov'
			inifilename = filename[:-4] + '.ini'
		else:
			povfilename = filename + '.pov'
			inifilename = filename + '.ini'
		if task is None:
			from chimera.tasks import Task
			task = Task("raytrace image", None)
		task.updateStatus("Generating POV-Ray data file")
		import exports
		exports.doExportCommand('POV-Ray', povfilename)
		task.updateStatus("Generating POV-Ray parameter file")
		if savedSD is not None:
			chimera.viewer.camera.screenDistance = savedSD
		import SubprocessMonitor as SM
		cmd = [
			preferences.get(POVRAY_SETUP, POVRAY_EXE),
			inifilename,
			"+I%s" % povfilename,
			"+O%s" % filename,
			"+V"		# need verbose to monitor progress
		]
		inifile = open(inifilename, 'w')
		print >> inifile, (
			"Width=%d\n"
			"Height=%d\n"
			# add font path, CHIMERA/share/fonts
			"Library_Path=\"%s\"\n"
			"Bounding=On\n"
			"Bounding_Threshold=1\n"
			"Split_Unions=On\n"
			"Remove_Bounds=On\n"
			"Quality=%d"
		) % (
			horizPixels,
			vertPixels,
			os.path.join(os.environ['CHIMERA'], 'share', 'fonts'),
			preferences.get(POVRAY_SETUP, POV_QUALITY)
		)
		if not preferences.get(POVRAY_SETUP, ANTIALIAS):
			print >> inifile, "Antialias=Off"
		else:
			print >> inifile, (
				"Antialias=On\n"
				"Antialias_Threshold=%f\n"
				"Antialias_Depth=%d\n"
				"Sampling_Method=%d"
			) % (
				preferences.get(POVRAY_SETUP, ANTIALIAS_THRESHOLD),
				preferences.get(POVRAY_SETUP, ANTIALIAS_DEPTH),
				preferences.get(POVRAY_SETUP, ANTIALIAS_METHOD)
			)
		if not preferences.get(POVRAY_SETUP, JITTER):
			print >> inifile, "Jitter=Off"
		else:
			print >> inifile, (
				"Jitter=On\n"
				"Jitter_Amount=%f\n"
			) % (
				preferences.get(POVRAY_SETUP, JITTER_AMOUNT),
			)
		oa = preferences.get(POVRAY_SETUP, OUTPUT_ALPHA)
		if oa == 1 or (oa == 2 and chimera.bgopacity):
			if chimera.viewer.depthCue:
				replyobj.warning("Depth-cueing disables transparent background")
			print >> inifile, "Output_Alpha=On"
		if format in ('PNG', 'Stereo PNG'):
			print >> inifile, ("; output PNG\n"
							"Output_File_Type=N8")
		elif format in ('JPEG', 'Stereo JPEG'):
			print >> inifile, ("; output JPEG\n"
					"Output_File_Type=J%d") % quality
		elif format in ('PPM'):
			print >> inifile, ("; output PPM\n"
							"Output_File_Type=P")
		if chimera.nogui or not raytracePreview:
			print >> inifile, "Display=Off"
		else:
			print >> inifile, "Display=On"
			if not raytraceWait:
				print >> inifile, "Pause_when_Done=On"
		inifile.close()
		if raytraceKeepInput:
			inputs = []
		else:
			inputs = [ povfilename, inifilename ]
		def afterCB(aborted, inputs=inputs, outputs=[filename]):
			import os
			for fn in inputs:
				try:
					os.remove(fn)
				except OSError:
					pass
			if aborted:
				for fn in outputs:
					try:
						os.remove(fn)
					except OSError:
						pass
		task.updateStatus("Starting POV-Ray")
		try:
			subproc = SM.Popen(cmd, stdin=None, stdout=None,
						stderr=SM.PIPE, daemon=True)
		except OSError, e:
			raise chimera.UserError, "Unable run POV-Ray executable: %s" % e
		progress = povrayProgress(subproc)
		progress.start()
		subproc.setProgress(progress)
		info = 'running "%s"' % '" "'.join(cmd)
		if not chimera.nogui and statusMessages:
			from chimera import dialogs, tkgui
			dialogs.display(tkgui._ReplyDialog.name)
			replyobj.info(info + '\n')
		task.updateStatus(info)
		subprog = SM.monitor('running POV-Ray', subproc,
					title="POV-Ray progress",
					task=task,
					afterCB=afterCB)
		if raytraceWait:
			subprog.wait()
		return
	status("Rendering high resolution image...", blankAfter=0)
	artist = preferences.get(IMAGE_CREDITS, ARTIST).strip()
	copyright = preferences.get(IMAGE_CREDITS, COPYRIGHT).strip()
	if raiseWindow and not chimera.nogui:
		from chimera import tkgui
		import CGLtk
		CGLtk.raiseWindow(tkgui.app)
		# guarantee label balloon is gone (for command line interface)
		tkgui.app.cancelLabelBalloon()
	# encourage raise to take place
	if hideDialogs and not chimera.nogui:
		tkgui._hideChildren(tkgui.app, None)
		chimera.tkgui.update_windows()
	# if background has opacity then save opacity
	opacity = chimera.bgopacity
	try:
		images = chimera.viewer.pilImages(horizPixels, vertPixels,
				supersample=supersample, opacity=opacity,
				printMode=printMode)
	except (MemoryError, OverflowError):
		# OverflowError if horizPixels or vertPixels won't fit in an int
		raise chimera.LimitationError("Not enough memory -- make a smaller image")
	finally:
		if savedSD is not None:
			chimera.viewer.camera.screenDistance = savedSD
	if hideDialogs and not chimera.nogui:
		tkgui._showChildren(tkgui.app, None)
	if supersample == 0:
		# just grabbing screen contents,
		# if not in sequential stereo,
		# then we have the data for fancier stuff
		if chimera.viewer.camera.mode() != "sequential stereo":
			printMode = ""		# just a single image
	if printMode in ("stereo pair", "cross-eye stereo"):
		# collapse two images into one with right eye on the left
		# images should be the same mode and size 
		from PIL import Image
		left, right = images
		combo = Image.new(left.mode,
				(left.size[0] + right.size[0], left.size[1]))
		images = [combo]
		combo.paste(right, (0, 0))
		combo.paste(left, (right.size[0], 0))
	elif printMode in ("wall-eye stereo", "DTI side-by-side"):
		# collapse two images into one with left on left
		from PIL import Image
		left, right = images
		combo = Image.new(left.mode,
				(left.size[0] + right.size[0], left.size[1]))
		images = [combo]
		combo.paste(left, (0, 0))
		combo.paste(right, (left.size[0], 0))
	from chimera.version import release
	import time
	# We setup our options for TIFF, as the options are generally
	# a super set of what's available in other formats.
	options = {
		'format': 'TIFF',
		'software': 'UCSF chimera ' + release,
		'date time': time.strftime('%Y:%m:%d %H:%M:%S'),
		'compression': 'lzw:2',
	}
	if artist:
		if isinstance(artist, unicode):
			artist = artist.encode('utf8')
		options['artist'] = artist
	if copyright:
		if isinstance(copyright, unicode):
			copyright = copyright.encode('utf8')
		options['copyright'] = copyright
	if description:
		if isinstance(description, unicode):
			description = description.encode('utf8')
		options['description'] = description
	if units == 'pixels':
		dpi = None
	elif units in ('points', 'inches'):
		dpi = preferences.get(IMAGE_SETUP, DPI)
		options['resolution unit'] = 'inch'
		options['x resolution'] = dpi
		options['y resolution'] = dpi
	elif units in ('millimeters', 'centimeters'):
		dpi = preferences.get(IMAGE_SETUP, DPI)
		adjust = convert['centimeters'] / convert['inches']
		dpcm = dpi * adjust
		options['resolution unit'] = 'cm'
		options['x resolution'] = dpcm
		options['y resolution'] = dpcm

	status("Saving %d high resolution image(s)..." % len(images), blankAfter=0)
	# TODO: make default an argument or preference
	quality = DEFAULT_JPEG_QUALITY
	if not chimera.nogui and not filename:

		if not master:
			master = tkgui.app
		if printMode == "stereo pair":
			filterSet = "stereo"
		else:
			filterSet = "normal"
		chooseDialog = _ChooseFileDialog(filterSet=filterSet, format=format)
		result = chooseDialog.run(master)
		if result is None:
			status("Image save cancelled.")
			return
		filename, format = result[0]
		quality = chooseDialog.quality.get()

	if not format:
		format = "PNG"

	saveFilename = ""
	# fix options for non-TIFF formats
	if format == 'TIFF-fast':
		format = 'TIFF'
		del options['compression']
	elif format in ('PNG', 'Stereo PNG'):
		options['format'] = 'PNG'
		options['optimize'] = True
		if dpi is not None:
			options['dpi'] = (dpi, dpi)
		from PIL import PngImagePlugin
		pnginfo = PngImagePlugin.PngInfo()
		if options.has_key('artist'):
			pnginfo.add_text('Author', options['artist'])
		if options.has_key('description'):
			pnginfo.add_text('Title', options['description'])
		if options.has_key('date time'):
			pnginfo.add_text('Creation Time', options['date time'])
		if options.has_key('software'):
			pnginfo.add_text('Software', options['software'])
		if options.has_key('copyright'):
			pnginfo.add_text('Copyright', options['copyright'])
		options['pnginfo'] = pnginfo
	elif format in ('JPEG', 'Stereo JPEG'):
		options['format'] = 'JPEG'
		# Do not optimze JPEG images without increasing
		# PIL.ImageFile.MAXBLOCK to size of image as per
		# http://mail.python.org/pipermail/image-sig/1999-August/000816.html
		import PIL.ImageFile
		minSize = 1024 * 1024
		if PIL.ImageFile.MAXBLOCK < minSize:
			PIL.ImageFile.MAXBLOCK = minSize
		#options['optimize'] = True
		options['quality'] = quality
		if dpi is not None:
			options['dpi'] = (dpi, dpi)
	elif format in ['EPS', 'PS']:
		# will be converted from TIFF via itops
		saveFilename = filename
		filename = tempfile.mktemp()
	else:
		options['format'] = format
	if len(images) <= 1:
		def fn(filename, i):
			return filename
	elif printMode == "sequential stereo":
		def fn(filename, i):
			eye = ("-left", "-right")[i - 1]
			suf = filename.rfind('.')
			if suf == -1:
				return filename + eye
			return filename[:suf] + eye + filename[suf:]
	else:
		def fn(filename, i):
			suf = filename.rfind('.')
			if suf == -1:
				return "%s%03d" % (filename, i)
			return "%s%03d%s" % (filename[:suf], i, filename[suf:])
	for i in range(5):
		try:
			for n, image in enumerate(images):
				n += 1	# start at one
				image.save(fn(filename, n), **options)
				status("%d image(s) saved." % n)
		except IOError, e:
			if format == 'JPEG' \
			and str(e).startswith('encoder error -2'):
				# buffer too small, try again
				PIL.ImageFile.MAXBLOCK *= 2
				continue
			raise chimera.NonChimeraError, "Unable to save image: %s" % e
		break
	if format in ['EPS', 'PS']:
		if format == 'PS':
			name = 'PostScript'
		else:
			name = 'Encapsulated PostScript'
		status("converting image(s) to %s." % name)
		# convert the temp-file TIFF to (E)PS
		itops = findExecutable('itops')
		from SubprocessMonitor import call
		cmd = [itops, '-a', '-r']
		if format == 'EPS':
			cmd.append('-E')
		for i in range(len(images)):
			i += 1	# start at one
			convertFilename = fn(filename, i)
			stdout = open(fn(saveFilename, i), 'wb')
			call(cmd + [convertFilename], stdout=stdout)
			status("%d image(s) converted." % i)
			os.unlink(convertFilename)
	status("Finished saving image(s).")
	return images

def PovrayLicenseText():
	# suck in povray/povlegal.html
	filename = os.path.join(chimera.__path__[0], "helpdir", "povray",
								"povlegal.txt")
	try:
		f = open(filename, 'r')
		text = f.read().decode('iso8859-1')
		f.close()
	except IOError:
		text = None
	return text

class PovrayCheckLicense(ModalDialog):

	title = "Accept POV-Ray License"
	buttons = ('Accept', 'Decline')
	provideStatus = False
	text_width = 78

	def __init__(self, master=None, *args, **kw):
		ModalDialog.__init__(self, master, resizable=True, *args, **kw)

	def fillInUI(self, parent):
		label = Tk.Label(parent,
			text="You must read and accept the following"
			" license agreement before raytracing an image"
			" with POV-Ray:",
			justify='left', height=2)
		import tkFont
		font = tkFont.Font(root=parent, font=label.cget('font'))
		label.config(wraplength=(self.text_width * font.measure('n')))
		label.grid(row=0, sticky=Tk.W, pady=5)
		#label.grid(row=0, pady=5)

		text = PovrayLicenseText()
		if text:
			text_pyclass = Tk.Text
			height = 25
		else:
			text = "Read contents of <a href='http://www.povray.org/povlegal.html'>POV-Ray End-User License</a>."
			from chimera.HtmlText import HtmlText
			text_pyclass = HtmlText
			height = 2

		import Pmw
		self.infoText = Pmw.ScrolledText(parent,
				text_pyclass=text_pyclass,
				text_relief=Tk.SUNKEN, text_wrap=Tk.WORD,
				text_width=self.text_width, text_height=height,
				text_highlightthickness=0)
		self.infoText.settext(text)

		self.infoText.configure(text_state=Tk.DISABLED,
				hscrollmode='dynamic', vscrollmode='dynamic',
				text_background=parent.cget('background'))
		self.infoText.grid(row=1, sticky=Tk.NSEW, pady=5)
		parent.rowconfigure(1, weight=1)
		parent.columnconfigure(0, weight=1)

	def Accept(self):
		self.Cancel(value=True)

	def Decline(self):
		self.Cancel(value=False)

def checkPovrayLicense():
	if preferences.get(POVRAY_AGREE, LICENSE_AGREE):
		return True
	if not chimera.nogui:
		dialog = PovrayCheckLicense()
		agree = dialog.run(chimera.tkgui.app)
	else:
		text = PovrayLicenseText()
		if text:
			text = ("You must read and accept the following"
				" license agreement before raytracing an image"
				" with POV-Ray:\n\n") + text
		if not text:
			text = "You must read and accept the POV-Ray End-User License at <http://www.povray.org/povlegal.html>."
		print text
		import sys
		sys.stdout.write("\nDo you agree to the Pov-Ray End-User License (y/n)? [n] ")
		yesno = sys.stdin.readline() 
		agree = yesno[0] in "yY"
	preferences.set(POVRAY_AGREE, LICENSE_AGREE, agree)
	return agree

class ClipWarning(ModalDialog):

	title = "POV-Ray clip warning"
	buttons = ('Continue', 'Cancel')
	provideStatus = False
	text_width = 50
	__dsVar = None

	def __init__(self, master=None, *args, **kw):
		ModalDialog.__init__(self, master, resizable=True, *args, **kw)

	def fillInUI(self, parent):
		label = Tk.Label(parent,
			text="Warning: clipping is turned on (see Side View"
			" tool) and will severely slow down POV-Ray raytracing.",
			justify='left', height=2)
		import tkFont
		font = tkFont.Font(root=parent, font=label.cget('font'))
		label.config(wraplength=(self.text_width * font.measure('n')))
		label.grid(row=0, columnspan=2, sticky=Tk.W, pady=5)

		off = Tk.Button(parent, text="Turn off clipping",
				command=self.__turnOff)
		off.grid(row=1, column=0, pady=1)

		if ClipWarning.__dsVar is None:
			ClipWarning.__dsVar = Tk.IntVar(chimera.tkgui.app)
			ClipWarning.__dsVar.set(False)
		ds = Tk.Checkbutton(parent, variable=ClipWarning.__dsVar,
			text="Don't show dialog again")
		from tkFont import Font
		font = Font(font=ds.cget('font'))
		font.config(size=int(0.75*float(font.cget('size'))+0.5),
					weight='normal')
		ds.config(font=font)
		ds.grid(row=1, column=1, sticky=Tk.SE, pady=1)

		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)

	def __turnOff(self):
		chimera.viewer.clipping = False

	def run(self, master):
		if self.__dsVar.get():
			return True
		return ModalDialog.run(self, master)

	def Continue(self):
		self.Cancel(value=True)

def Continue(self):
		self.Cancel(value=True)

if chimera.nogui:
	#preferences.addCategory(IMAGE_SETUP, ImageSetupCategory)
	preferences.register(POVRAY_SETUP, povrayPreferences)
	preferences.setOrder(POVRAY_SETUP, povrayPreferencesOrder)
	initializeCreditPreferences()

povray_options = {
	LICENSE_AGREE: False
}
preferences.addCategory(POVRAY_AGREE, preferences.HiddenCategory,
							optDict=povray_options)
del povray_options

image_setup_options = {
	UNITS: "pixels",
	USE_PRINT_UNITS: False,
	DPI: 100,
	ADJUST_FOV: ONLY_STEREO_CAMERAS,
	SUPERSAMPLE: 3,
}
preferences.addCategory(IMAGE_SETUP, preferences.HiddenCategory,
						optDict=image_setup_options)
del image_setup_options
