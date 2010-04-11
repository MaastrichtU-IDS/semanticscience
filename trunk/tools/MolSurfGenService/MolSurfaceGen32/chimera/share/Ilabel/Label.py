# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Label.py 29048 2009-10-14 21:16:14Z pett $


import chimera

class Label:
	"""an entire label, possibly multi-line, composed of Characters"""
	shown = True

	def __init__(self, pos, model):
		self.pos = pos
		self.model = model
		# one list of characters per line
		self.lines = [[]]

	def clear(self):
		for line in self.lines:
			for c in line:
				c.destroy()
		self.lines = [[]]

	def destroy(self):
		self.clear()
		self.model = None

	def __setattr__(self, attrName, val):
		if attrName == 'shown':
			if self.shown == val:
				return
			if unicode(self):
				self.model.setMajorChange()
		self.__dict__[attrName] = val

	def set(self, text):
		self.clear()
		self.lines = [ map(Character, x) for x in text.splitlines() ]
		
	def __unicode__(self):
		return self.text()

	def text(self):
		text = ""
		for line in self.lines:
			for c in line:
				text += unicode(c)
			text += '\n'
		return text[:-1]

	def _restoreSession(self, info):
		self.lines = []
		# Helvetica/Times/Courier became Sans Serif/Serif/Fixed
		fontMap = {
			'Helvetica': 'Sans Serif',
			'Times': 'Serif',
			'Courier': 'Fixed'
		}
		for l in info["lines"]:
			for cinfo in l:
				try:
					fn = cinfo["kw"]["fontName"]
				except KeyError:
					continue
				if fn in fontMap:
					cinfo["kw"]["fontName"] = fontMap[fn]
			self.lines.append([Character(*cinfo["args"],
						**cinfo["kw"]) for cinfo in l])
		if "shown" in info:
			self.shown = info["shown"]

	def _sessionInfo(self):
		info = {}
		info["args"] = (self.pos,)
		info["shown"] = self.shown
		lines = []
		for l in self.lines:
			lines.append([c._sessionInfo() for c in l])
		info["lines"] = lines
		return info

_fonts = {}

class Character:
	"""individual character in a label"""

	def __init__(self, c, fontName='Sans Serif', size=24,
					rgba=(1.,1.,1.,1.), baselineOffset = 0,
					style=chimera.OGLFont.normal):
		self._fontName = fontName
		self._size = size
		self._rgba = rgba
		self._style = style
		self._font = None
		self._baselineOffset = baselineOffset
		self._makeFont()
		self._char = c

	def _fontKey(self):
		return (self._fontName, self._size, self._style)

	def _makeFont(self):
		self._delFont()
		key = self._fontKey()
		try:
			font = _fonts[key]
		except KeyError:
			font = chimera.OGLFont(*key)
			_fonts[key] = font
		self._font = font
	
	def _delFont(self, *args):
		self._font = None

	def _restoreSession(self, info):
		self._char = info["char"]
		self._size = info["size"]
		self._rgba = info["rgba"]
		self._fontName = info["fontName"]
		self._style = info["style"]
		self._baselineOffset = info["baselineOffset"]
		self._makeFont()

	def _sessionInfo(self):
		info = {}
		info["args"] = (self._char,)
		info["kw"] = {
			"rgba": self._rgba,
			"size": self._size,
			"fontName": self._fontName,
			"style": self._style,
			"baselineOffset": self._baselineOffset
		}
		return info

	def __str__(self):
		# allow high-bit-set 8-bit characters...
		# (that would otherwise be unconvertible unicode)
		return chr(ord(self._char))
		
	def __unicode__(self):
		return unicode(self._char)
		
	def __getattr__(self, attr):
		if attr in ("rgba", "fontName", "size", "style", "font",
							"baselineOffset"):
			try:
				return self.__dict__["_" + attr]
			except KeyError:
				pass
		raise AttributeError, "Unknown attribute '%s'" % attr

	def __setattr__(self, attr, val):
		if attr in ("rgba", "baselineOffset"):
			self.__dict__["_" + attr] = val
		elif attr in ("size", "fontName", "style"):
			self.__dict__["_" + attr] = val
			self._makeFont()
		else:
			self.__dict__[attr] = val

	def destroy(self):
		self._delFont()
