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

"""Convenience classes for making small 2D textures"""

import chimera

class Texturer:
	texturePrefix = 0 # used to generate unique texture names

	def __init__(self, maxColors, name=None, withAlpha=0):
		# also must define self.textureColors as a list of 
		# texture coordinates the user can access

		if not name:
			trialName = str(Texturer.texturePrefix) + "texture5"
			while chimera.Texture.lookup(trialName):
				# find an unused name
				Texturer.texturePrefix = \
				  Texturer.texturePrefix + 1
				trialName = str(Texturer.texturePrefix) \
				  + "texture%s" % maxColors
			name = trialName
		self.textureName = name
		
		self.haveAlpha = withAlpha

		if self.haveAlpha:
			self.textureType = chimera.Texture.RGBA
			self.componentSize = 4
		else:
			self.textureType = chimera.Texture.RGB
			self.componentSize = 3

		self.nameMap = {}
		self.trackedColors = [None] * maxColors
		self.trackColorHandler = None

	def mapName(self, index, name):
		"""associate a mnemonic name with texture index
		   index parameter ranges starts at 1, not 0
		"""
		self.nameMap[name] = index

	def setColor(self, index, color):
		"""set color of texture region associated with index"""

		if isinstance(index, basestring):
			try:
				index = self.nameMap[index]
			except KeyError:
				raise KeyError, "No texture region named " + \
				  index
		
		if isinstance(color, basestring):
			color = chimera.Color.lookup(color)
		
		if hasattr(color, "rgba"):
			self.trackedColors[index - 1] = color
			if not self.trackColorHandler:
				self.trackColorHandler = \
				chimera.triggers.addHandler('Color',
						self._colorTracking, None)
			color = color.rgba()

		if self.componentSize == 4 and len(color) == 3:
			"""add alpha if missing"""
			color = color + (1.0,)
		
		if self.componentSize == 3 and len(color) == 4:
			"""ignore alpha"""
			color = color[:3]
		
		if len(color) != self.componentSize:
			raise ValueError, "Color tuple wrong size"
		
		self._colorRegion(index - 1, color)
	
	def _colorRegion(self, index, color):
		"""This must be implemented by derived class
		
		Color the texture region associated with index"""
		raise AttributeError, \
		  "_colorRegion() not implemented by %s class" % \
		  self.__class__.__name__

	def _colorBox(self, mem, box, color):
		"""put given color in texture ('mem') grid at 'box'"""
		cSize = self.componentSize
		offset = cSize * box
		mem[offset + 0] = color[0]
		mem[offset + 1] = color[1]
		mem[offset + 2] = color[2]
		if cSize == 4:
			mem[offset + 3] = color[3]
	
	def _colorTracking(self, triggerName, data, colorChanges):
		for i in range(len(self.trackedColors)):
			trackedColor = self.trackedColors[i]
			if not trackedColor:
				continue
			if trackedColor in colorChanges.modified:
				self.setColor(i+1, trackedColor)
				
	def color(self, index):
		"""return texture coordinate associated with index"""
		if isinstance(index, basestring):
			index = self.nameMap[index]
		
		return self.textureColors[index-1]
	
class FiveColorTexture(Texturer):
	"""class to make a five-color 2D texture map
	
	Transitions between colors do not occur midway along the interpolation
	between them in this texture.  If this is problematic, the 
	FourColorTexture class offers midway transitions."""

	def __init__(self, **kw):
		apply(Texturer.__init__, (self, 5), kw)

		self.texture = chimera.Texture(self.textureName,
		  self.textureType, chimera.Texture.Float, 8, 8)
		
		# init everything to black, just for that warm fuzzy
		# safe feeling
		mem = chimera.memoryMap(self.texture.startEditing(),
		  64 * self.componentSize, self.texture.type())
		for i in range(64 * self.componentSize):
			mem[i] = 0.0
		self.texture.finishEditing()

                self.textureColors = []
                self.textureColors.append(chimera.TextureColor(self.texture,
                  8.0/16.0, 1.0/16.0))
                self.textureColors.append(chimera.TextureColor(self.texture,
                  7.0/16.0, 7.0/16.0))
                self.textureColors.append(chimera.TextureColor(self.texture,
                  9.0/16.0, 7.0/16.0))
                self.textureColors.append(chimera.TextureColor(self.texture,
                  1.0/16.0, 15.0/16.0))
                self.textureColors.append(chimera.TextureColor(self.texture,
                  15.0/16.0, 15.0/16.0))
	
	def _colorRegion(self, index, color):
		mem = chimera.memoryMap(self.texture.startEditing(),
		  64 * self.componentSize, self.texture.type())
		if index == 0:
			for i in range(32):
				if i == 27 or i == 28:
					continue
				self._colorBox(mem, i, color)
		elif index == 1:
			self._colorBox(mem, 27, color)
		elif index == 2:
			self._colorBox(mem, 28, color)
		elif index == 3:
			for i in range(4):
				for j in range(4):
					self._colorBox(mem, 32+8*i+j, color)
		elif index == 4:
			for i in range(4):
				for j in range(4):
					self._colorBox(mem, 32+8*i+4+j, color)

		self.texture.finishEditing()
	
class FourColorTexture(Texturer):
	""" class to make a four-color 2D texture map
	
	uses slightly less memory than a FiveColorTexture and colors
	transition midway between coordinates (unlike FiveColorTexture)"""

	def __init__(self, **kw):
		apply(Texturer.__init__, (self, 4), kw)

		self.texture = chimera.Texture(self.textureName,
		  self.textureType, chimera.Texture.Float, 2, 2)
		
		# init everything to black, just for that warm fuzzy
		# safe feeling
		mem = chimera.memoryMap(self.texture.startEditing(),
		  4 * self.componentSize, self.texture.type())
		for i in range(4 * self.componentSize):
			mem[i] = 0.0
		self.texture.finishEditing()

                self.textureColors = []
                self.textureColors.append(chimera.TextureColor(self.texture,
                  0.25, 0.25))
                self.textureColors.append(chimera.TextureColor(self.texture,
                  0.75, 0.25))
                self.textureColors.append(chimera.TextureColor(self.texture,
                  0.25, 0.75))
                self.textureColors.append(chimera.TextureColor(self.texture,
                  0.75, 0.75))
	
	def _colorRegion(self, index, color):
		mem = chimera.memoryMap(self.texture.startEditing(),
		  4 * self.componentSize, self.texture.type())
		self._colorBox(mem, index, color)
		self.texture.finishEditing()

class _RampTexture(Texturer):
	"""Class to make an interpolated ramp from a matrix of colors.
	
	Note that _RampTexture constructor expects either an array or an
	array of arrays of Chimera colors (not RGB tuples or lists)."""

	def __init__(self, colors, width=256, height=0, **kw):
		self.width = width
		if not isinstance(colors[0], list):
			colors = [colors, colors]
			height = 2
		self.xCount = len(colors[0])
		for cList in colors[1:]:
			if len(cList) != self.xCount:
				raise ValueError, \
					'lists must be the same length'
		self.yCount = len(colors)
		if height > 0:
			self.height = height
		else:
			h = width * self.yCount / self.xCount
			p2 = 1
			while p2 < h:
				p2 = p2 * 2
			self.height = p2
		apply(Texturer.__init__, (self, self.xCount * self.yCount), kw)
		self.texture = chimera.Texture(self.textureName,
						self.textureType,
						chimera.Texture.Float,
						self.width, self.height)
		n = 1
		if isinstance(colors[0], list):
			for cList in colors:
				for c in cList:
					self.setColor(n, c, rebuild=0)
					n = n + 1
		else:
			for c in colors:
				self.setColor(n, c, rebuild=0)
				n = n + 1
		self.rebuild()

	def setColor(self, index, color, rebuild=1):
		self._needRebuild = 1
		Texturer.setColor(self, index, color)
		if rebuild:
			self.rebuild()

	def _colorRegion(self, index, color):
		if self._needRebuild:
			return
		tSize = self.width * self.height * self.componentSize
		mem = chimera.memoryMap(self.texture.startEditing(),
					tSize, self.texture.type())
		x = index % self.xCount
		y = int(index / self.xCount)
		if x > 0:
			if y > 0:
				self._rebuildRect(mem, x - 1, y - 1)
			if y < self.yCount:
				self._rebuildRect(mem, x - 1, y)
		if x < self.xCount:
			if y > 0:
				self._rebuildRect(mem, x, y - 1)
			if y < self.yCount:
				self._rebuildRect(mem, x, y)
		self.texture.finishEditing()

	def _rebuildRect(self, mem, x, y):
		ulIndex = y * self.xCount + x
		llIndex = (y + 1) * self.xCount + x
		urIndex = y * self.xCount + (x + 1)
		lrIndex = (y + 1) * self.xCount + (x + 1)

		ulColor = self.trackedColors[ulIndex]
		llColor = self.trackedColors[llIndex]
		urColor = self.trackedColors[urIndex]
		lrColor = self.trackedColors[lrIndex]
		cList = [ ulColor, llColor, urColor, lrColor ]

		xSize = float(self.xCount - 1)
		ySize = float(self.yCount - 1)
		xStart = int(x * self.width / xSize)
		xEnd = int((x + 1) * self.width / xSize)
		yStart = int(y * self.height / ySize)
		yEnd = int((y + 1) * self.height / ySize)

		width = float(xEnd - xStart)
		height = float(yEnd - yStart)
		for x in range(xStart, xEnd):
			s = (x - xStart) / width
			ns = 1 - s
			for y in range(yStart, yEnd):
				t = (y - yStart) / height
				nt = 1 - t
				ulFrac = ns * nt
				urFrac = s * nt
				llFrac = ns * t
				lrFrac = s * t
				fList = [ ulFrac, llFrac, urFrac, lrFrac ]
				self._rebuildPixel(mem, x, y, cList, fList)

	def _rebuildPixel(self, mem, x, y, cList, fList):
		cSize = self.componentSize
		color = self._interpolate(cList, fList)
		offset = cSize * (y * self.width + x)
		mem[offset + 0] = color[0]
		mem[offset + 1] = color[1]
		mem[offset + 2] = color[2]
		if cSize == 4:
			mem[offset + 3] = color[3]

	def rebuild(self):
		tSize = self.width * self.height * self.componentSize
		mem = chimera.memoryMap(self.texture.startEditing(),
					tSize, self.texture.type())
		for x in range(self.xCount - 1):
			for y in range(self.yCount - 1):
				self._rebuildRect(mem, x, y)
		self._needRebuild = 0
		self.texture.finishEditing()

class RGBRampTexture(_RampTexture):
	"Class to make an RGB-interpolated ramp from a matrix of colors."

	def _interpolate(self, cList, fList):
		r = 0.0
		g = 0.0
		b = 0.0
		a = 0.0
		rgbaList = map(lambda c: c.rgba(), cList)
		for i in range(len(fList)):
			f = fList[i]
			rgba = rgbaList[i]
			r = r + rgba[0] * f
			g = g + rgba[1] * f
			b = b + rgba[2] * f
			a = a + rgba[3] * f
		return [r, g, b, a]

class HLSRampTexture(_RampTexture):
	"Class to make an HLS-interpolated ramp from a matrix of colors."

	def _interpolate(self, cList, fList):
		import colorsys
		h = 0.0
		l = 0.0
		s = 0.0
		a = 0.0
		rgbaList = map(lambda c: c.rgba(), cList)
		for i in range(len(fList)):
			f = fList[i]
			rgba = rgbaList[i]
			hls = colorsys.rgb_to_hls(rgba[0], rgba[1], rgba[2])
			h = h + hls[0] * f
			l = l + hls[1] * f
			s = s + hls[2] * f
			a = a + rgba[3] * f
		r, g, b = colorsys.hls_to_rgb(h, l, s)
		return [r, g, b, a]
