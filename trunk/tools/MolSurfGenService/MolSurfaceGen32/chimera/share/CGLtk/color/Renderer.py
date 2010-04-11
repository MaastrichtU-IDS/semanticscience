# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Renderer.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter
from PIL import Image
from PIL import ImageTk
from PIL import ImageDraw

import Ink

class Renderer(ImageTk.PhotoImage):
	"Renderer displays an Image with alpha in an ImageTk"

	def __init__(self, master, image, hasAlpha, **kw):
		self.master = master
		kw['master'] = master
		self.hasAlpha = hasAlpha
		self.alphaImage = image
		self.image = Image.new(self.alphaImage.mode,
					self.alphaImage.size)
		apply(ImageTk.PhotoImage.__init__, (self, self.image) , kw)
		self.background = {}
		self.offset = 0
		self.afterId = None
		self.maxOffset = self.image.size[0] + \
					apply(min, self.image.size)
		grayLevels = 32
		if self.maxOffset < grayLevels:
			self.step = int(grayLevels / self.maxOffset)
			self.grayStep = 1.0 / self.maxOffset
		else:
			self.step = int((self.maxOffset + grayLevels - 1)
						/ grayLevels)
			self.maxOffset = self.step * grayLevels
			self.grayStep = 1.0 / grayLevels
		self.update()

	def setImage(self, image, hasAlpha):
		# Assume that new image is the same size as old image
		# (Does not work otherwise since ImageTk.PhotoImage
		# does not allow resizing
		self.hasAlpha = hasAlpha
		self.alphaImage = image

	def _makeBackground(self):
		if self.background.has_key(self.offset):
			self.image.paste(self.background[self.offset])
			return
		draw = ImageDraw.ImageDraw(self.image)
		xsize, ysize = self.image.size
		shear = apply(min, self.image.size)
		gray = 1.0
		for i in range(self.offset, 0, -self.step):
			draw.polygon((i - shear - self.step, 0,
					i - shear, 0,
					i, ysize,
					i - self.step, ysize),
					fill=Ink.Gray(gray))
			gray = gray - self.grayStep
			if gray < 0.0:
				gray = 1.0 - gray
		gray = 0.0
		for i in range(self.offset, self.maxOffset + 1, self.step):
			draw.polygon((i - shear, 0,
					i - shear + self.step, 0,
					i + self.step, ysize,
					i, ysize),
					fill=Ink.Gray(gray))
			gray = gray + self.grayStep
			if gray > 1.0:
				gray = gray - 1.0
		self.background[self.offset] = self.image.copy()

	def update(self, *args):
		if self.hasAlpha:
			self._makeBackground()
			self.image.paste(self.alphaImage, None, self.alphaImage)
			self.paste(self.image)
		else:
			self.paste(self.alphaImage)

	def animateBegin(self, *args):
		if self.hasAlpha:
			self.afterId = self.master.after_idle(self.animate)

	def animate(self):
		if self.hasAlpha:
			self.offset = self.offset + self.step
			if self.offset >= self.maxOffset:
				self.offset = 0
			self.update()
			self.afterId = self.master.after(100, self.animate)

	def animateEnd(self, *args):
		if self.hasAlpha:
			if self.afterId:
				self.master.after_cancel(self.afterId)
				self.afterId = None
			self.offset = 0
		self.update()

if __name__ == '__main__':
	root = Tkinter.Tk()
	image = Image.new('RGBA', (160, 20))
	image.paste((0, 0, 0, 127), (0, 0, 20, 20))
	image.paste((255, 0, 0, 127), (20, 0, 40, 20))
	image.paste((0, 255, 0, 127), (40, 0, 60, 20))
	image.paste((0, 0, 255, 127), (60, 0, 80, 20))
	image.paste((255, 255, 0, 127), (80, 0, 100, 20))
	image.paste((255, 0, 255, 127), (100, 0, 120, 20))
	image.paste((0, 255, 255, 127), (120, 0, 140, 20))
	image.paste((255, 255, 255, 127), (140, 0, 160, 20))
	renderer = Renderer(root, image, 1)
	holder = Tkinter.Label(root, image=renderer)
	holder.pack(expand=1, fill=Tkinter.BOTH)
	holder.bind('<ButtonPress-1>', renderer.animateBegin)
	holder.bind('<B1-ButtonRelease>', renderer.animateEnd)
	root.mainloop()
