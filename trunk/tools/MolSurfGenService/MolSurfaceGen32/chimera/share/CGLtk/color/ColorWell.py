# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ColorWell.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter
import tkFont
from Tkinter import Canvas, Frame
from ColorDnd import ColorSource, ColorTarget

_colorPanel = None
_defaultColorPanel = None

def colorPanel(*args, **kw):
	global _colorPanel, _defaultColorPanel
	if not _colorPanel:
		if not _defaultColorPanel:
			import Editor
			_defaultColorPanel = Editor.editor
		_colorPanel = apply(_defaultColorPanel, args, kw)
	return _colorPanel

def setColorPanel(panel):
	global _colorPanel
	if _colorPanel and _colorPanel != panel:
		if _colorPanel.state() == "normal":
			# not withdrawn or iconified
			panel.setRGBA(rgba=_colorPanel.rgba)
			panel.show()
		_colorPanel.deactivate()
	_colorPanel = panel

def setDefaultColorPanel(cp):
	global _defaultColorPanel
	_defaultColorPanel = cp

import ColorPanel

def _mapFraction(f):
	if f < 0: return 0
	elif f > 1: return 65535
        return int(f * 65535 + 0.5)

def _tkColor(r, g, b):
        return '#%04x%04x%04x' % (r, g, b)

def rgba2tk(rgba):
        return _tkColor(_mapFraction(rgba[0]), _mapFraction(rgba[1]),
                                _mapFraction(rgba[2]))
def pref2tk(colorVal):
	if colorVal == None or isinstance(colorVal, str):
		return colorVal
	return rgba2tk(colorVal)

def _tkrgb2rgba(tkrgb):
	return (tkrgb[0] / 65535.0, tkrgb[1] / 65535.0, tkrgb[2] / 65535.0, 1.0)

class _WellInterior(Canvas, ColorSource):
	def __init__(self, colorWell, *args, **kw):
		apply(Canvas.__init__, (self,) + args, kw)
		apply(ColorSource.__init__, (self, self), {})
		self._colorWell = colorWell
		self._startEvent = None

	def __getattr__(self, name):
		# rgb/rgba tracked in containing well
		if name == "rgb":
			try:
				return self._colorWell.rgb
			except:
				return None
		if name == "rgba":
			try:
				return self._colorWell.rgba
			except:
				return None
		raise AttributeError, "Unknown attribute '%s'" % name

	def cs_dragStart(self, event):
		if not self._colorWell._multiple and \
		  self._colorWell.rgba != None:
			self._startEvent = event
			ColorSource.cs_dragStart(self, event)
		else:
			if event.state % 2 == 1:
				# 'shift' key depressed
				self._colorWell.activate(exclusive=0) 
			else:
				self._colorWell.activate(exclusive=1) 

	def dnd_end(self, target, event):
		if (target is None
		  and self._startEvent is not None
		  and event is not None):
			if (event.type == "5"	# ButtonRelease
			  and event.x_root == self._startEvent.x_root
			  and event.y_root == self._startEvent.y_root):
				self._colorWell.edgeClick(event)
		self._startEvent = None

class ColorWell(Frame, ColorTarget):
	# holds an RGBA color, but deals with Tk colors

	def __init__(self, parent,
	  color = None,
		# color to show in the well
	  width = 38, height = 38,
		# size of well
	  callback = None,
		# method to call upon color change
		#  [with argument of (WellColor)]
	  noneOkay = 0,
	  	# can the well return 'none'
	  multiple = 0,
		# does the well currently represent data with multiple colors
	  wantAlpha = 1
		# does the app want alpha supported in this well
	  ):	
		
		self._callback = callback
		self.noneOkay = noneOkay
		self._active = 0
		self.wantAlpha = wantAlpha
		self._enabled = True

		# convert width/height to pixels
		width = parent.master.winfo_pixels(width)
		height = parent.master.winfo_pixels(height)

		borderwidth = int(min(width, height) / 15)

		# border is added to width/height, so reduce them
		width = width - 2 * borderwidth
		height = height - 2 * borderwidth
		
		Frame.__init__(self, parent, width = width, height = height,
		  borderwidth = borderwidth, relief = Tkinter.RAISED)
		self.bind("<Button-1>", self.edgeClick)

		self._activeBG = 'white'
		self._inactiveBG = self['bg']

		# use a Frame around the well interior so that the relief
		# doesn't interfere with the interior's canvas coordinate
		# system
		edgewidth = int(min(width, height) / 12)
		self._wellFrame = Frame(self, borderwidth = borderwidth,
		  relief = Tkinter.SUNKEN)
		self._wellFrame.place(x=edgewidth+borderwidth, y=edgewidth+borderwidth,
		  relwidth=1, relheight=1,
		  width=0-2*(edgewidth+borderwidth), height=0-2*(edgewidth+borderwidth))
		self._well = _WellInterior(self, master=self._wellFrame,
		  borderwidth=0, highlightthickness=0)
		self._well.bind('<Configure>', self._resizeMarkers)
		self._well.pack(expand=1, fill="both")
		self._wellMarkers = None

		if not multiple and color == None and not noneOkay:
			# default to black
			self.showColor('black', doCallback=0)
		else:
			self.showColor(color=color, multiple=multiple,
								doCallback=0)

	def __getattr__(self, name):
		# convenience to allow '.rgb[a]' access
		if name == "rgb" or name == "rgba":
			if self._multiple:
				raise AttributeError, "Multiple colors in well"
			if self._rgba == None:
				if not self.noneOkay:
					raise AttributeError, "No color in well"
				return None
			if name == "rgb":
				return self._rgba[:3]
			return self._rgba
		raise AttributeError, "Unknown attribute '%s'" % name

	def edgeClick(self, event):
		if not self._enabled:
			return
		if self._active:
			if event.state % 2 == 1:
				# 'shift' key depressed
				self.deactivate()
			else:
				# Nothing happens, even if there are more
				# than one well selected.  Alternative is
				# pass
				colorPanel().show()
		else:
			if event.state % 2 == 1:
				# 'shift' key depressed
				self.activate(exclusive=0) 
			else:
				self.activate(exclusive=1) 
	
	def deactivate(self, notifyPanel=1):
		if self._active:
			if notifyPanel:
				colorPanel().deregister(self, notifyWell=0)
			self._active = 0
			self['bg'] = self._inactiveBG
	
	def activate(self, exclusive=1, notifyPanel=1):
		if not self._enabled:
			return
		if not self._active:
			if notifyPanel:
				colorPanel().register(self, exclusive=exclusive)
			colorPanel().show()
			self._active = 1
			self['bg'] = self._activeBG

	def enable(self):
		self._enabled = True
		if self._wellMarkers:
			for marker in self._wellMarkers:
				self._well.itemconfigure(marker,
						state = Tkinter.NORMAL)

	def disable(self):
		self._enabled = False
		self.deactivate()
		if self._wellMarkers:
			for marker in self._wellMarkers:
				self._well.itemconfigure(marker,
						state = Tkinter.DISABLED)
		
	def showColor(self, color=None, multiple=0, notifyPanel=1,
								doCallback=1):
		if hasattr(self, '_multiple'):
			# okay, showColor must have been called before to
			# set _multiple
			#
			# if color requested is not different, do nothing
			if multiple and self._multiple:
				return
			if not multiple and not self._multiple:
				if color == None:
					if self._rgba == None:
						return
				elif isinstance(color, basestring):
					if self._rgba == _tkrgb2rgba(
							self.winfo_rgb(color)):
						return
				elif len(color) == 3:
					if self._rgba and self.rgb == color:
						return
				elif self._rgba == color:
					return

		self._multiple = multiple
		try:
			ignore = self._well['bg']
		except Tkinter.TclError:
			# presumably we were active when our window was
			# destroyed by window manager -- deregister ourselves
			colorPanel().deregister(self, notifyWell=0)
			return

		if multiple:
			self._rgba = None
			self._clearWell()
			self._wellMultiple()
			return

		if color == None:
			if not self.noneOkay:
				raise ValueError, 'Attempt to show None in' \
						 ' color well not so configured'
			self._rgba = None
			if self._callback != None and doCallback:
				apply(self._callback, (None,), {})
			
			self._clearWell()
			self._wellNoColor()
			return

		# Now we are sure we have a real color
		# Figure out if the new color is the same as the old color
		if isinstance(color, basestring):
			# presumably Tk color
			rgba = _tkrgb2rgba(self.winfo_rgb(color))
		elif len(color) == 3:
			rgba = tuple(color) + (1.0,)
		else:
			rgba = tuple(color)

		self._clearWell()
		self._rgba = rgba
		self._well['bg'] = rgba2tk(self._rgba)
		self._wellFrame['bg'] = rgba2tk(self._rgba)

		if self._rgba[3] < 1.0:
			# some alpha
			self._wellAlpha()

		if self._active and notifyPanel:
			# even though color panel will call this
			# method again, it will short-circuit at the
			# top because the color will be the same,
			# so allow fall-though to fire self._callback
			colorPanel().setRGBA(rgba=self._rgba)

		if self._callback != None and doCallback:
			apply(self._callback, (self._rgba,), {})

	def _clearWell(self):
		if self._wellMarkers:
			for marker in self._wellMarkers:
				self._well.delete(marker)
			self._wellMarkers = None

	def _wellNoColor(self):
		# draw "No" on checkerboard
		self._well['bg'] = "#a0a0a0"
		self._wellFrame['bg'] = "gray"
		ww = self._well.winfo_width()
		wh = self._well.winfo_height()
		self._wellMarkers = [self._well.create_rectangle(
		  0.0, 0.0, ww/2.0, wh/2.0)]
		self._wellMarkers.append(self._well.create_rectangle(
		  ww/2.0, wh/2.0, ww, wh))
		
		for marker in self._wellMarkers:
			self._well.itemconfig(marker, fill="#d0d0d0",
			  disabledfill="#707070", outline="", width=0)
		noText = "No"
		fontSize = -10  # use pixels rather than points
		font = tkFont.Font(family="Helvetica", weight=tkFont.BOLD,
								size=fontSize)
		textWidth = font.measure(noText) 
		if textWidth >= ww:
			# crank down size
			while textWidth > ww and fontSize < -4:
				fontSize = fontSize + 1
				font.configure(size=fontSize)
				textWidth = font.measure(noText)
		elif textWidth < ww/2.0 and 2 - fontSize < wh:
			# up the size
			while textWidth < ww/2.0 and 2 - fontSize < wh:
				fontSize = fontSize - 2
				font.configure(size=fontSize)
				textWidth = font.measure(noText)
		self._wellMarkers.append(self._well.create_text(
		  ww/2.0, wh/2.0, text=noText, fill="black",
		  disabledfill="gray", font=font))

	def _wellMultiple(self):
		# draw ">1" on top of four color quadrants
		self._wellFrame['bg'] = "gray"
		ww = self._well.winfo_width()
		wh = self._well.winfo_height()
		self._wellMarkers = [self._well.create_rectangle(
		  0.0, 0.0, ww/2.0, wh/2.0,
		  fill=rgba2tk((0.0, 208/255.0, 1.0, 1.0)),
		  disabledfill=rgba2tk((0.0, 104/255.0, 0.5, 1.0)),
		  )]
		self._wellMarkers.append(self._well.create_rectangle(
		  0.0, wh/2.0, ww/2.0, wh,
		  fill=rgba2tk((1.0, 123/255.0, 0.0, 1.0)),
		  disabledfill=rgba2tk((0.5, 62/255.0, 0.0, 1.0)),
		  ))
		self._wellMarkers.append(self._well.create_rectangle(
		  ww/2.0, 0.0, ww, wh/2.0,
		  fill=rgba2tk((1.0, 127/255.0, 234/255.0, 1.0)),
		  disabledfill=rgba2tk((0.5, 64/255.0, 117/255.0, 1.0)),
		  ))
		self._wellMarkers.append(self._well.create_rectangle(
		  ww/2.0, wh/2.0, ww, wh,
		  fill=rgba2tk((106/255.0, 1.0, 0.0, 1.0)),
		  disabledfill=rgba2tk((53/255.0, 0.5, 0.0, 1.0)),
		  ))
		for marker in self._wellMarkers:
			self._well.itemconfig(marker, outline="")
		manyText = ">1"
		fontSize = -10  # use pixels rather than points
		font = tkFont.Font(family="Helvetica", size=fontSize)
		textWidth = font.measure(manyText) 
		if textWidth >= ww:
			# crank down size
			while textWidth > ww and fontSize < -7:
				fontSize = fontSize + 1
				font.configure(size=fontSize)
				textWidth = font.measure(manyText)
		elif textWidth < ww/2.0 and 2 - fontSize < wh:
			# up the size
			while textWidth < ww/2.0 and 2 - fontSize < wh:
				fontSize = fontSize - 2
				font.configure(size=fontSize)
				textWidth = font.measure(manyText)
		if fontSize < -7:
			self._wellMarkers.append(self._well.create_text(ww/2.0,
				wh/2.0, text=manyText, fill="black",
				disabledfill="gray", font=font))
	
	def _wellAlpha(self):
		# draw "alpha triangles"
		ww = self._well.winfo_width()
		wh = self._well.winfo_height()
		# upper-left triangle
		self._wellMarkers = [self._well.create_polygon(
		  0.0, 0.0, 0.0, wh, ww, 0.0)]
		# lower-right triangle
		self._wellMarkers.append(self._well.create_polygon(
		  ww, 0.0, ww, wh, 0.0, wh))
		rgba = self._rgba
		opaque = rgba[3]
		clear = 1 - opaque
		ulColor = rgba2tk((rgba[0] * opaque,
		  rgba[1] * opaque, rgba[2] * opaque, 1.0))
		lrColor = rgba2tk((rgba[0] * opaque + clear,
		  rgba[1] * opaque + clear, rgba[2] * opaque + clear, 1.0))
		self._well.itemconfig(self._wellMarkers[0],
		  fill=ulColor, disabledstipple="gray50", outline="")
		self._well.itemconfig(self._wellMarkers[1],
		  fill=lrColor, disabledstipple="gray12", outline="")

	def _resizeMarkers(self, event):
		if not self._wellMarkers:
			return
		numMarkers = len(self._wellMarkers)
		self._clearWell()
		if numMarkers == 5 or numMarkers == 4:
			# optional text on color quadrants
			self._wellMultiple()
		elif numMarkers == 3:
			# text on gray quadrants
			self._wellNoColor()
		elif numMarkers == 2:
			# alpha triangles
			self._wellAlpha()
		else:
			raise AssertionError, "Unknown items in well canvas"

	def destroy(self, *args, **kw):
		for base in self.__class__.__bases__:
			if hasattr(base, "destroy"):
				apply(base.destroy, (self,) + args, kw)
		if self._active:
			colorPanel().deregister(self, notifyWell=0)

	def __del__(self):
		for base in self.__class__.__bases__:
			if hasattr(base, "__del__"):
				base.__del__(self)
		if self._active:
			colorPanel().deregister(self, notifyWell=0)
