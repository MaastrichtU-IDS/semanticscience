# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Palette.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter
from PIL import Image
from PIL import ImageDraw
import Renderer
import colorsys

import Ink

class Palette(Tkinter.Label):
	"Palette (subclasses) maintain an image of directly pickable colors"

	def __init__(self, master=None, color=None, colorspace=None,
			minBandWidth=7, **kw):
		kw['padx'] = 0
		kw['pady'] = 0
		apply(Tkinter.Label.__init__, (self, master), kw)
		self.image = Image.new('RGBA', (1, 1))

		if colorspace is None:
			colorspace = globals['DefaultColorSpace']()
		if color is None:
			color = colorspace.defaultColor
		self.rgba = colorspace.toRGBA(color)
		self.colorspace = colorspace
		self.currentColor = self.colorspace.fromRGBA(self.rgba)
		if colorspace.grayLevel(color) < 0.5:
			self.highlight = Ink.Gray(1)
		else:
			self.highlight = Ink.Gray(0)
		# Note that we cannot use setColorspace since we
		# are not ready to update the display yet.

		self.master = master
		self.minBandWidth = minBandWidth
		self.renderer = Renderer.Renderer(self, self.image,
						self.colorspace.hasAlpha)
		self.config(image=self.renderer)
		self.bind('<Configure>', self.resize)
		self.bind('<ButtonPress-1>', self.buttonDown)
		self.bind('<B1-Motion>', self.buttonDrag)
		self.bind('<B1-ButtonRelease>', self.buttonUp)
		self.animateAfter = None
		self.animating = 0
		# Actual rendering of image will happen during Configure

	def resize(self, event):
		size = (event.width, event.height)
		self.image = Image.new('RGBA', size)
		self._computeBands(size)
		self.display()
		self.renderer = Renderer.Renderer(self.master, self.image,
						self.colorspace.hasAlpha)
		self.config(image=self.renderer)

	def setColorspace(self, colorspace):
		self.colorspace = colorspace
		self.currentColor = self.colorspace.fromRGBA(self.rgba)
		self.renderer.setImage(self.image, colorspace.hasAlpha)
		self._computeBands(self.image.size)
		self.update()

	def _computeBands(self, size):
		width, height = size
		bands = max(min(int(width / self.minBandWidth), 256), 2)
		self.numBands = bands
		self.lowBandWidth = width / bands
		self.lowBandCount = bands - width % bands
		self.lowChannelHeight = height / self.colorspace.numChannels
		self.highChannelCount = height % self.colorspace.numChannels

	def rectangle(self, channel, band):
		if __debug__:
			if channel < 0 or \
			channel >= self.colorspace.numChannels:
				raise ValueError, 'channel out of bounds'
			if band < 0 or band >= self.numBands:
				raise ValueError, 'band %d out of bounds' % band
		if band < self.lowBandCount:
			width = self.lowBandWidth
			ulx = band * width
		else:
			width = self.lowBandWidth + 1
			ulx = self.lowBandCount * self.lowBandWidth + \
				(band - self.lowBandCount) * width
		if channel < self.highChannelCount:
			height = self.lowChannelHeight + 1
			uly = channel * height
		else:
			height = self.lowChannelHeight
			uly = self.highChannelCount * \
				(self.lowChannelHeight + 1) + \
				(channel - self.highChannelCount) * height
		lrx = ulx + width
		lry = uly + height
		return (ulx, uly, lrx, lry)

	def update(self):
		if not hasattr(self, 'numBands'):
			return
		self.display()
		self.renderer.update()

	def buttonDown(self, event):
		self.animating = 0
		if self.colorspace.hasAlpha:
			self.animateAfter = self.after(500, self._startAnimate)
		else:
			self._setColorFromEvent(event)

	def _startAnimate(self):
		self.animateAfter = 0
		self.animating = 1
		self.renderer.animateBegin()

	def buttonUp(self, event):
		if self.animating:
			# We've been animating, so don't update color
			self.renderer.animateEnd()
		else:
			if self.animateAfter:
				self.after_cancel(self.animateAfter)
				self.animateAfter = None
				self._setColorFromEvent(event)

	def buttonDrag(self, event):
		if self.animating:
			# We've been animating, so don't update color
			return
		if self.animateAfter:
			self.after_cancel(self.animateAfter)
			self.animateAfter = None
		self._setColorFromEvent(event)

	def _setColorFromEvent(self, event):
		band = self.getBand(event.x)
		channel = self.getChannel(event.y)
		value = self.bandToValue(band)
		self.setChannelValue(channel, value)

	def getBand(self, x):
		if x < 0:
			return 0
		elif x >= self.image.size[0]:
			return self.numBands - 1
		cutoff = self.lowBandCount * self.lowBandWidth
		if x < cutoff:
			band = int(x / self.lowBandWidth)
		else:
			band = self.lowBandCount + \
				int((x - cutoff) / (self.lowBandWidth + 1))
		return band

	def getChannel(self, y):
		if y < 0:
			return 0
		elif y >= self.image.size[1]:
			return self.colorspace.numChannels - 1
		cutoff = self.highChannelCount * (self.lowChannelHeight + 1)
		if y < cutoff:
			channel = int(y / (self.lowChannelHeight + 1))
		else:
			channel = self.highChannelCount + \
				int((y - cutoff) / self.lowChannelHeight)
		return channel

	def bandToValue(self, band):
		return float(band) / (self.numBands - 1)

	def valueToBand(self, value):
		return int(value * (self.numBands - 1))

	def display(self):
		draw = ImageDraw.ImageDraw(self.image)
		for c in range(self.colorspace.numChannels):
			color = self.currentColor[:]
			denom = float(self.numBands - 1)
			# Base class guarantees that numBands >= 2
			for b in range(self.numBands):
				color[c] = b / denom
				draw.rectangle(self.rectangle(c, b),
						fill=self.colorspace.ink(color))
		gray = self.colorspace.grayLevel(self.currentColor)
		if gray < 0.3:
			self.highlight = Ink.Gray(1)
		elif gray > 0.5:
			self.highlight = Ink.Gray(0)
		draw.setink(self.highlight)
		for c in range(self.colorspace.numChannels):
			b = self.valueToBand(self.currentColor[c])
			r = self.rectangle(c, b)
			nr = (r[0], r[1], r[2] - 1, r[3] - 1)
			draw.rectangle(nr, outline=self.highlight)
			#draw.rectangle(self.rectangle(c, b))

	def setCurrentColor(self, c):
		self.currentColor = c
		self.rgba = self.colorspace.toRGBA(c)
		self.update()

	def setCurrentRGBA(self, rgba):
		self.rgba = rgba
		self.currentColor = self.colorspace.fromRGBA(rgba)
		self.update()

	def setChannelValue(self, c, v):
		self.currentColor[c] = v
		self.rgba = self.colorspace.toRGBA(self.currentColor)
		self.update()


class AlphaMixin:
	def __init__(self):
		self.baseClass = self.__class__.__bases__[1]
		self.baseClass.__init__(self)
		self.defaultColor.append(1.0)
		self.numChannels = self.numChannels + 1
		self.hasAlpha = 1
		self.label += "A"

	def fromRGBA(self, rgba):
		c = self.baseClass.fromRGBA(self, rgba)
		c.append(rgba[-1])
		return c

	def toRGBA(self, color):
		r, g, b, a = self.baseClass.toRGBA(self, color)
		return (r, g, b, color[-1])

class RGB:
	def __init__(self):
		self.defaultColor = [0.0, 0.0, 0.0]
		self.numChannels = 3
		self.hasAlpha = 0
		self.label = "RGB"
		# Label names are composed of single character channel
		# labels.  So "RGB" with 3 channels means the channels
		# are named 'R', 'B' and 'G' in that order.

	def ink(self, color):
		return apply(Ink.RGB, tuple(color))

	def grayLevel(self, color):
		return apply(Ink.RGBgray, tuple(color))

	def fromRGBA(self, rgba):
		return list(rgba[:3])

	def toRGBA(self, color):
		return (color[0], color[1], color[2], 1.0)

class RGBA(AlphaMixin, RGB):
	pass

class HLS(Palette):
	def __init__(self):
		self.defaultColor = [0.0, 0.5, 1.0]
		self.numChannels = 3
		self.hasAlpha = 0
		self.label = "HLS"

	def ink(self, color):
		return apply(Ink.HLS, tuple(color))

	def grayLevel(self, color):
		return apply(Ink.HLSgray, tuple(color))

	def fromRGBA(self, rgba):
		return list(colorsys.rgb_to_hls(rgba[0], rgba[1], rgba[2]))

	def toRGBA(self, color):
		r, g, b = colorsys.hls_to_rgb(color[0], color[1], color[2])
		return (r, g, b, 1.0)

class HLSA(AlphaMixin, HLS):
	pass

class HSV(Palette):
	def __init__(self):
		self.defaultColor = [0.0, 1.0, 1.0]
		self.numChannels = 3
		self.hasAlpha = 0
		self.label = "HSV"

	def ink(self, color):
		return apply(Ink.HSV, tuple(color))

	def grayLevel(self, color):
		return apply(Ink.HSVgray, tuple(color))

	def fromRGBA(self, rgba):
		return list(colorsys.rgb_to_hsv(rgba[0], rgba[1], rgba[2]))

	def toRGBA(self, color):
		r, g, b = colorsys.hsv_to_rgb(color[0], color[1], color[2])
		return (r, g, b, 1.0)

class HSVA(AlphaMixin, HSV):
	pass

class YIQ(Palette):
	def __init__(self):
		self.defaultColor = [0.0, 0.5, 1.0]
		self.numChannels = 3
		self.hasAlpha = 0
		self.label = "YIQ"

	def ink(self, color):
		return apply(Ink.YIQ, tuple(color))

	def grayLevel(self, color):
		return apply(Ink.YIQgray, tuple(color))

	def fromRGBA(self, rgba):
		return list(colorsys.rgb_to_yiq(rgba[0], rgba[1], rgba[2]))

	def toRGBA(self, color):
		r, g, b = colorsys.yiq_to_rgb(color[0], color[1], color[2])
		return (r, g, b, 1.0)

class YIQA(AlphaMixin, YIQ):
	pass

class CMYK(Palette):
	def __init__(self, master=None, color=None, **kw):
		self.defaultColor = [0.0, 0.0, 0.0, 0.0]
		self.numChannels = 4
		self.hasAlpha = 0
		self.label = "CMYK"

	def ink(self, color):
		return apply(Ink.CMYK, tuple(color))

	def grayLevel(self, color):
		return apply(Ink.CMYKgray, tuple(color))

	def fromRGBA(self, (r, g, b, a)):
		k1 = max(1 - r, 1 - g, 1 - b)
		if k1 == 0:
			return [0.0, 0.0, 0.0, 0.0]
		return [(1 - r) / k1, (1 - g) / k1, (1 - b) / k1, 1 - k1]

	def toRGBA(self, color):
		k = color[3]
		k1 = 1 - k
		c = color[0] * k1 + k
		m = color[1] * k1 + k
		y = color[2] * k1 + k
		return (1 - c, 1 - m, 1 - y, 1.0)

class CMYKA(AlphaMixin, CMYK):
	pass

class Gray(Palette):
	def __init__(self, master=None, color=None, **kw):
		self.defaultColor = [0.0]
		self.numChannels = 1
		self.hasAlpha = 0
		self.label = "G"

	def ink(self, color):
		return apply(Ink.Gray, tuple(color))

	def grayLevel(self, color):
		return color[0]

	def fromRGBA(self, (r, g, b, a)):
		return [Ink.RGBgray(r, g, b)]

	def toRGBA(self, color):
		return (color[0], color[0], color[0], 1.0)

class GrayA(AlphaMixin, Gray):
	pass

G = Gray
GA = GrayA

ColorSpaces = [ 'RGB', 'HLS', 'HSV', 'YIQ', 'CMYK', 'Gray' ]
DefaultColorSpace = ColorSpaces[0]

if __name__ == '__main__':
	top = Tkinter.Toplevel(visual='truecolor')
	label = Tkinter.Label(top, text='Palette')
	label.pack(expand=0, fill=Tkinter.X)
	spacesVar = Tkinter.StringVar(top)
	spacesVar.set('RGBA')
	spaces = Tkinter.OptionMenu(top, spacesVar,
			'RGB', 'HLS', 'HSV', 'YIQ', 'CMYK', 'Gray',
			'RGBA', 'HLSA', 'HSVA', 'YIQA', 'CMYKA', 'GrayA')
	spaces.pack(side=Tkinter.TOP, fill=Tkinter.X)
	palette = Palette(top, colorspace=globals()[spacesVar.get()](),
				width=256, height=100, minBandWidth=10)
	palette.pack(expand=1, fill=Tkinter.BOTH)
	def setColorspace(n1, n2, op, palette=palette, var=spacesVar):
		palette.setColorspace(globals()[var.get()]())
	spacesVar.trace_variable('w', setColorspace)
	top.mainloop()

