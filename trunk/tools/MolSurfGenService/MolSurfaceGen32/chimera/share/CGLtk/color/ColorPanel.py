#!/usr/bin/env python

# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ColorPanel.py 26655 2009-01-07 22:02:30Z gregc $

import math
import Tkinter
Tk = Tkinter

from CGLtk import ModalWindow
from ColorWellInterface import ColorWellInterface

#
# implement a "singleton" color panel.  available through "colorPanel"
#	function
#
_colorPanel = None

def colorPanel(master=None, title="Color Chooser"):
	global _colorPanel
	if _colorPanel == None:
		_colorPanel = _ColorPanel(master=master)
		_colorPanel.title(title)
	return _colorPanel
		
#
# Local functions
#
def _mapFraction(f):
	return int(f * 255)

def _tkColor(r, g, b):
	return '#%02x%02x%02x' % (r, g, b)

def _tkColorName(rgb):
	return _tkColor(_mapFraction(rgb[0]), _mapFraction(rgb[1]),
				_mapFraction(rgb[2]))

def _toRGB(tkRGB):
	return (tkRGB[0] / 65535.0, tkRGB[1] / 65535.0, tkRGB[2] / 65535.0)

def _sameValue(r, v):
	return math.fabs(r - v) < (Resolution / 2)

#
# Constants
#
ShadesPerColor = 10
ShadesArray = []
limit = float(ShadesPerColor - 1)
for i in range(ShadesPerColor):
	ShadesArray.append(_mapFraction(i / limit))
del limit
del i
Resolution = 0.001
MaxHistory = 10

class _ColorPanel(ColorWellInterface):
	"""
	_ColorPanel is similar to the Tk color picker except
	it also keeps track of the recently used colors and
	a list of favorite colors.
	"""

	def __init__(self, master=None, **kw):

		apply(ColorWellInterface.__init__, (self,), kw)

		spacer = Tk.Frame(self)
		spacer.pack(side=Tk.TOP, pady=5)

		#
		# Current color and color name
		#
		f = Tk.Frame(self)
		f.pack(side=Tk.TOP, fill=Tk.X)
		self.color = Tk.Label(f, text='', bd=2, relief=Tk.SUNKEN)
		self.color.pack(side=Tk.LEFT, padx=5, expand=Tk.TRUE, fill=Tk.BOTH)
		l = Tk.Label(f, text='Color name:')
		l.pack(side=Tk.TOP, padx=5, fill=Tk.X, anchor=Tk.W)
		self.colorName = Tk.Entry(f)
		self.colorName.pack(side=Tk.TOP, padx=5, fill=Tk.X, anchor=Tk.W)
		self.colorName.bind('<Return>', self._colorNameCB)

		spacer = Tk.Frame(self)
		spacer.pack(side=Tk.TOP, pady=5)

		#
		# Sliders a la Tk
		#
		self.redSlider = Tk.Scale(self, width=5, showvalue=Tk.TRUE,
					from_=0, to_=1, resolution=Resolution,
					troughcolor='red',
					orient=Tk.HORIZONTAL,
					command=self._redSliderCB)
		self.redSlider.pack(side=Tk.TOP, padx=5, fill=Tk.X)
		self.red = Tk.Frame(self)
		self.red.pack(side=Tk.TOP, padx=5, fill=Tk.X)
		self.redArray = self._shadeArray(self.red)

		self.greenSlider = Tk.Scale(self, width=5, showvalue=Tk.TRUE,
					from_=0, to_=1, resolution=0.001,
					troughcolor='green',
					orient=Tk.HORIZONTAL,
					command=self._greenSliderCB)
		self.greenSlider.pack(side=Tk.TOP, padx=5, fill=Tk.X)
		self.green = Tk.Frame(self)
		self.green.pack(side=Tk.TOP, padx=5, fill=Tk.X)
		self.greenArray = self._shadeArray(self.green)

		self.blueSlider = Tk.Scale(self, width=5, showvalue=Tk.TRUE,
					from_=0, to_=1, resolution=0.001,
					troughcolor='blue',
					orient=Tk.HORIZONTAL,
					command=self._blueSliderCB)
		self.blueSlider.pack(side=Tk.TOP, padx=5, fill=Tk.X)
		self.blue = Tk.Frame(self)
		self.blue.pack(side=Tk.TOP, padx=5, fill=Tk.X)
		self.blueArray = self._shadeArray(self.blue)

		spacer = Tk.Frame(self)
		spacer.pack(side=Tk.TOP, pady=5)

		#
		# Recently used colors
		#
		l = Tk.Label(self, text='Recently used colors:')
		l.pack(side=Tk.TOP, padx=5)
		self.recent = Tk.Frame(self, height=20)
		self.recent.pack(side=Tk.TOP, padx=5, fill=Tk.X)
		self.recentArray = self._colorArray(self.recent)

		#
		# Favorite colors
		#
		l = Tk.Label(self, text='Favorite colors:')
		l.pack(side=Tk.TOP, padx=5)
		self.favorite = Tk.Frame(self, height=20)
		self.favorite.pack(side=Tk.TOP, padx=5, fill=Tk.X)
		self.favoriteArray = self._colorArray(self.favorite)
		for b in self.favoriteArray:
			b.bind('<B2-ButtonRelease>',
				lambda e, b=b, s=self: s._saveColor(b, e))

		spacer = Tk.Frame(self)
		spacer.pack(side=Tk.TOP, pady=5)

		#
		# Define the current color and initialize everything
		#
		self._loadFavorites()
		self.setRGBA(name=self.favoriteArray[0]['bg'])

		# don't appear unless show() method called
		self.withdraw()

	def setRGBA(self, name=None, rgba=None, updateInternal=1):
		ColorWellInterface.setRGBA(self, name, rgba)
		if updateInternal:
			self.rgb = self.rgba[:3]
			self.redSlider.set(self.rgb[0])
			self.greenSlider.set(self.rgb[1])
			self.blueSlider.set(self.rgb[2])
			self._redisplayCurrent()
			self._redisplayRed()
			self._redisplayGreen()
			self._redisplayBlue()

	def _shadeArray(self, frame):
		array = []
		for i in range(ShadesPerColor):
			b = Tk.Button(frame, text='', font='Helvetica -6',
					bd=0, highlightthickness=0)
			b['command'] = lambda s=self, b=b: s._setColor(b)
			b.pack(side=Tk.LEFT, expand=Tk.TRUE, fill=Tk.X)
			array.append(b)
		return array

	def _colorArray(self, frame):
		array = []
		for i in range(MaxHistory):
			b = Tk.Button(frame, text='', font='Helvetica -6',
					bg='white', activebackground='white')
			b['command'] = lambda s=self, b=b: s._setColor(b)
			b.pack(side=Tk.LEFT, expand=Tk.TRUE, fill=Tk.X)
			array.append(b)
		return array

	def _redisplayCurrent(self):
		self.color['bg'] = self.name
		self.colorName.delete(0, Tk.END)
		self.colorName.insert(0, self.name)
		self.setRGBA(rgba=self.rgb + (1.0,), updateInternal=0)

	def _redisplayRed(self):
		r, g, b = self.rgb
		green = _mapFraction(g)
		blue = _mapFraction(b)
		for i in range(ShadesPerColor):
			l = self.redArray[i]
			c = _tkColor(ShadesArray[i], green, blue)
			l['bg'] = c
			l['activebackground'] = c

	def _redisplayGreen(self):
		r, g, b = self.rgb
		red = _mapFraction(r)
		blue = _mapFraction(b)
		for i in range(ShadesPerColor):
			l = self.greenArray[i]
			c = _tkColor(red, ShadesArray[i], blue)
			l['bg'] = c
			l['activebackground'] = c

	def _redisplayBlue(self):
		r, g, b = self.rgb
		red = _mapFraction(r)
		green = _mapFraction(g)
		for i in range(ShadesPerColor):
			l = self.blueArray[i]
			c = _tkColor(red, green, ShadesArray[i])
			l['bg'] = c
			l['activebackground'] = c

	def _colorNameCB(self, event):
		self.setRGBA(name=self.colorName.get())

	def _redSliderCB(self, location):
		v = float(location)
		if _sameValue(v, self.rgb[0]):
			return
		self.rgb = (v, self.rgb[1], self.rgb[2])
		self.name = _tkColorName(self.rgb)
		self._redisplayCurrent()
		self._redisplayGreen()
		self._redisplayBlue()

	def _greenSliderCB(self, location):
		v = float(location)
		if _sameValue(v, self.rgb[1]):
			return
		self.rgb = (self.rgb[0], v, self.rgb[2])
		self.name = _tkColorName(self.rgb)
		self._redisplayCurrent()
		self._redisplayRed()
		self._redisplayBlue()

	def _blueSliderCB(self, location):
		v = float(location)
		if _sameValue(v, self.rgb[2]):
			return
		self.rgb = (self.rgb[0], self.rgb[1], v)
		self.name = _tkColorName(self.rgb)
		self._redisplayCurrent()
		self._redisplayRed()
		self._redisplayGreen()

	def _setColor(self, button):
		self.setRGBA(name=button['bg'])

	def _saveColor(self, button, event):
		button['bg'] = self.name
		button['activebackground'] = self.name
		self._saveFavorites()

	def _loadFavorites(self):
		import os
		filename = 'FavoriteColors.py'
		self.favoritesFile = filename
		if os.path.isfile(filename):
			self._load(filename)
		else:
			try:
				fn = os.path.join(os.environ['HOME'], filename)
				if os.path.isfile(fn):
					self._load(fn)
					self.favoritesFile = fn
			except KeyError:
				pass

	def _load(self, filename):
		mapDict = {}
		f = open(filename)
		try:
			exec f in mapDict
		finally:
			f.close()
		try:
			colors = mapDict['colors']
		except KeyError:
			colors = []
		limit = max(len(colors), MaxHistory)
		for i in range(limit):
			button = self.favoriteArray[i]
			try:
				button['bg'] = colors[i]
				button['activebackground'] = colors[i]
			except Tkinter.TclError:	# in case of bad name
				pass

	def _saveFavorites(self):
		try:
			f = open(self.favoritesFile, 'w')
			f.write('colors = [\n')
			for button in self.favoriteArray:
				f.write('\t"%s",\n' % button['bg'])
			f.write(']\n')
			f.close()
		except:
			pass
