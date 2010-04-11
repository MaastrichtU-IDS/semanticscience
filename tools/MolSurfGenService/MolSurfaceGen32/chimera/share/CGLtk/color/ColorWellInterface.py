# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ColorWellInterface.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter

#
# Local functions
#
def _tkColorName(rgba):
	r, g, b, a = rgba
	return '#%04x%04x%04x' % (round(r * 65535), round(g * 65535),
					round(b * 65535))

def _toRGBA(tkRGB):
	return (tkRGB[0] / 65535.0, tkRGB[1] / 65535.0, tkRGB[2] / 65535.0, 1.0)

_activeWells = []

class ColorWellInterface(Tkinter.Toplevel):
	"ColorWellInterface has all methods invoked by ColorWell class"

	def __init__(self, **kw):
		apply(Tkinter.Toplevel.__init__, (self,), kw)
		self.title('Color Editor')
		self.protocol('WM_DELETE_WINDOW', self.deactivate)
		self.withdraw()

	def show(self, initialColor=None):
		"Show the color panel"
		if initialColor:
			self.setRGBA(name=initialColor)
		self.deiconify()

	def setRGBA(self, name=None, rgba=None):
		"Set the color displayed in color panel"

		# This method should be overridden with an implementation like:
		#	ColorWellInterface.setRGBA(self, name, rgba)
		#	... do something with self.rgba ...
		if rgba is None:
			if name is None:
				return
			try:
				rgba = _toRGBA(self.winfo_rgb(name))
			except Tkinter.TclError, v:
				from tkMessageBox import showerror
				showerror(master=self,
						title='Color Conversion Error',
						message=v)
				return
		else:
			if name is None:
				name = _tkColorName(rgba)
		self.rgba = tuple(rgba)
		self.name = name
		for well in _activeWells:
			well.showColor(color=self.rgba, notifyPanel=0)

	def register(self, well, exclusive=1):
		"Add well to list to be notified when color changes"

		if exclusive:
			while _activeWells:
				self.deregister(_activeWells[0])
			try:
				wellRGBA = well.rgba
			except AttributeError:
				# multiple colors or None
				wellRGBA = (0, 0, 0, 1)
			self.setRGBA(rgba=wellRGBA)
		else:
			well.showColor(color=self.rgba, notifyPanel=0)
		if well not in _activeWells:
			_activeWells.append(well)

	def deregister(self, well, notifyWell=1):
		"Remove well from list to be notified when color changes"

		if well in _activeWells:
			if notifyWell:
				well.deactivate(notifyPanel=0)
			while well in _activeWells:
				_activeWells.remove(well)
	
	def deactivate(self):
		self.deactivateWells()
		self.withdraw()

	def deactivateWells(self):
		while _activeWells:
			well = _activeWells.pop()
			well.deactivate(notifyPanel=0)
