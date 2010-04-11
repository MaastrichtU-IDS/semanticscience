# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: TextureBlock.py 26655 2009-01-07 22:02:30Z gregc $

from PIL import Image
from PIL import ImageDraw
import Ink

class Block:

	handlesAlpha = 0

	def displayBand(self, draw, minX, maxX, minY, maxY, c):
		draw.rectangle((minX, minY, maxX, maxY), fill=Ink.RGB(*c))

	def displaySelected(self, draw, width, minY, maxY):
		draw.rectangle((0, minY, width - 1, maxY - 1),
						outline=Ink.RGB(0.0, 0.0, 0.0))
		draw.rectangle((1, minY + 1, width - 2, maxY - 2),
						outline=Ink.RGB(1.0, 1.0, 0.0))


class SolidBlock(Block):

	handlesAlpha = 1

	def __init__(self, color):
		self.color = color

	def display(self, draw, image, minY, maxY, selected=0):
		width = image.size[0]
		self.displayBand(draw, 0, width, minY, maxY, self.color)
		if selected:
			self.displaySelected(draw, width, minY, maxY)


class BandedBlock(Block):

	def __init__(self, leftColor, midColor, rightColor, numBands):
		self.leftColor = leftColor
		self.midColor = midColor
		self.rightColor = rightColor
		self.numBands = numBands

	def display(self, draw, image, minY, maxY, selected=0):
		width = image.size[0]
		bandCount = 3 + self.numBands * 2
		minX = 0
		maxX = width / bandCount
		self.displayBand(draw, minX, maxX, minY, maxY, self.leftColor)
		for i in range(self.numBands):
			minX = width * (i + 1) / bandCount
			maxX = width * (i + 2) / bandCount
			c = self._interpColor(i, self.leftColor, self.midColor)
			self.displayBand(draw, minX, maxX, minY, maxY, c)
		minX = width * (self.numBands + 1) / bandCount
		maxX = width * (self.numBands + 2) / bandCount
		self.displayBand(draw, minX, maxX, minY, maxY, self.midColor)
		for i in range(self.numBands):
			minX = width * (self.numBands + i + 2) / bandCount
			maxX = width * (self.numBands + i + 3) / bandCount
			c = self._interpColor(i, self.midColor, self.rightColor)
			self.displayBand(draw, minX, maxX, minY, maxY, c)
		minX = width * (bandCount - 1) / bandCount
		maxX = width
		self.displayBand(draw, minX, maxX, minY, maxY, self.rightColor)
		if selected:
			self.displaySelected(draw, width, minY, maxY)

	def _interpColor(self, i, minC, maxC):
		f = (i + 1) / float(self.numBands + 1)
		r = minC[0] + (maxC[0] - minC[0]) * f
		g = minC[1] + (maxC[1] - minC[1]) * f
		b = minC[2] + (maxC[2] - minC[2]) * f
		m = max(r, g, b)
		if len(minC) < 4 and len(maxC) < 4:
			return (r / m, g / m, b / m)
		if len(minC) < 4:
			minA = 1.0
		else:
			minA = minC[3]
		if len(maxC) < 4:
			maxA = 1.0
		else:
			maxA = maxC[3]
		a = minA + (maxA - minA) * f
		return (r / m, g / m, b / m, a)

if __name__ == '__main__':
	import Tkinter
	from PIL import ImageTk
	app = Tkinter.Frame()
	app.pack(expand=1, fill=Tkinter.BOTH)
	image = Image.new('RGBA', (256, 256))
	draw = ImageDraw.ImageDraw(image)
	solid = SolidBlock((0, 0, 0))
	solid.display(draw, image, 0, 128, selected=1)
	bands = BandedBlock((1, 0, 0), (0, 0, 1), (0, 1, 0), 1)
	bands.display(draw, image, 128, 256, selected=0)
	imageTk = ImageTk.PhotoImage(image)
	l = Tkinter.Label(app, image=imageTk, bd=2, relief=Tkinter.GROOVE)
	l.pack()
	app.mainloop()
