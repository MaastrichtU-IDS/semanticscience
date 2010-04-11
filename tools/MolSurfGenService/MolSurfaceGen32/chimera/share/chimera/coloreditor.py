# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: coloreditor.py 26655 2009-01-07 22:02:30Z gregc $

import CGLtk.color.Editor
import baseDialog

class Editor(baseDialog.ModelessDialog, CGLtk.color.Editor.Editor):
	"""Override CGLtk.color.Editor.Editor to place it in a chimera dialog."""

	title = "Color Editor"
	buttons = ("No Color", baseDialog.Close)
	help = "UsersGuide/colortool.html"

	def __init__(self, helpCmd=None, **kw):
		# do *not* call CGLtk.color.Editor.Editor.__init__()!!
		apply(baseDialog.ModelessDialog.__init__, (self,), kw)

	def __getattr__(self, name):
		# since the color editor's __init__ function is not called,
		# when its methods try to use its Toplevel base class, use
		# the appropriate part of ModelessDialog instead
		if self.__dict__.has_key('_toplevel') and \
						hasattr(self._toplevel, name):
			return getattr(self._toplevel, name)
		raise AttributeError, "no such attribute '%s'" % name
	
	def __setattr__(self, name, value):
		# if we're setting what looks like a Toplevel attribute, put
		# it in the ModelessDialog._toplevel
		if hasattr(self, '_toplevel') and hasattr(self._toplevel, name):
			setattr(self._toplevel, name, value)
		else:
			self.__dict__[name] = value

	def fillInUI(self, frame):
		# create the CGLtk.color.Editor.Editor UI
		self.mainUI(frame)
		self.noneButton = self.buttonWidgets["No Color"]
		import preferences
		self.prefCat = "color panel"
		self.prefColorspace = "colorspace"
		self.prefFavorites = "favorites"
		self.prefs = preferences.addCategory(self.prefCat,
						preferences.HiddenCategory,
						optDict={
						  self.prefColorspace: None,
						  self.prefFavorites: []
						})
		cs = self.prefs[self.prefColorspace]
		if cs:
			self.restoreColorspace(*cs)
		favList = self.prefs[self.prefFavorites]
		for i in range(len(favList)):
			rgba = favList[i]
			if rgba:
				self.restoreFavorite(i, rgba)

	def NoColor(self, event=None):
		# CGLtk.color.Editor.Editor doesn't use the same naming conventions
		self.noColor()

	def show(self, initialColor=None):
		# don't let ColorWellInterface get its hands on our toplevel
		if initialColor:
			self.setRGBA(name=initialColor)
		self.enter()

	def _colorNameCB(self, event=None):
		import chimera
		name = self.colorName.get()
		c = chimera.Color.lookup(name)
		setRGBA = CGLtk.color.Editor.Editor.setRGBA
		if c is None:
			setRGBA(self, name=name)
		else:
			rgba = c.ambientDiffuse + (c.opacity,)
			setRGBA(self, name=name, rgba=rgba)

	def _setColorspace(self, *args):
		CGLtk.color.Editor.Editor._setColorspace(self, *args)
		cs = (self.colorspace.label, self.colorspace.hasAlpha)
		if self.prefs[self.prefColorspace] != cs:
			self.prefs[self.prefColorspace] = cs

	def restoreColorspace(self, name, hasAlpha):
		if hasAlpha:
			self.csVar.set(name[:-1])
			self.alphaVar.set(1)
		else:
			self.csVar.set(name)
			self.alphaVar.set(0)

	def saveFavorite(self, *args):
		CGLtk.color.Editor.Editor.saveFavorite(self, *args)
		self.prefs[self.prefFavorites] = [ f.rgba
							for f in self.favorites]

	def restoreFavorite(self, n, rgba):
		self.favorites[n].showColor(rgba)

	def deactivate(self):
		# don't let ColorWellInterface get its hands on our toplevel
		self.Close()

	def Close(self):
		self.deactivateWells()
		baseDialog.ModelessDialog.Close(self)
