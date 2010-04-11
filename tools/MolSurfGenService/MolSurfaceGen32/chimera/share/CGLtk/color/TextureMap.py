# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: TextureMap.py 26655 2009-01-07 22:02:30Z gregc $

import copy
import Tkinter
from PIL import Image
from PIL import ImageDraw
from PIL import ImageTk

import TextureBlock
import BlockSource

class TextureMap(Tkinter.Label):

	LeftColor = (1.0, 0.0, 0.0)
	MidColor = (0.0, 0.0, 1.0)
	RightColor = (0.0, 1.0, 0.0)
	TransparentColor = (0.0, 0.0, 0.0, 0.0)

	def __init__(self, master=None, width=256, height=256, selectable=1,
			bg=None, initBlock=None, xStep=1, yStep=1, **kw):
		if initBlock is None:
			if bg is None:
				initBlock = TextureBlock.BandedBlock(
							self.LeftColor,
							self.MidColor,
							self.RightColor, 0)
			else:
				initBlock = TextureBlock.SolidBlock(
							self.TransparentColor)
		self.xStep = xStep
		self.yStep = yStep
		self.pieces = [ initBlock ]
		self.blocks = [ 0, height ]
		self.textureImage = Image.new('RGBA', (width, height))
		self.image = Image.new('RGBA', (width, height))
		self.draw = ImageDraw.ImageDraw(self.image)
		self.photo = ImageTk.PhotoImage(self.image, master=master)
		self.setBackground(bg, redisplay=0)
		kw['master'] = master
		kw['width'] = width
		kw['height'] = height
		kw['bd'] = 0
		kw['image'] = self.photo
		apply(Tkinter.Label.__init__, (self,), kw)
		self.bind('<Configure>', self._resize)
		if selectable:
			self.bind('<ButtonPress-1>', self._buttonDown)
			self.bind('<B1-Motion>', self._buttonDrag)
			self.bind('<ButtonRelease-1>', self._buttonUp)
			self.setSelected(0)
		else:
			self.selected = -1

	def resize(self, width, height):
		size = self.image.size
		if width != size[0] or height != size[1]:
			denom = float(self.blocks[-1])
			for i in range(len(self.blocks)):
				self.blocks[i] = int(self.blocks[i] /
							denom * height)
			self.textureImage = Image.new('RGBA', (width, height))
			self.image = Image.new('RGBA', (width, height))
			self.draw = ImageDraw.ImageDraw(self.image)
			self.photo = ImageTk.PhotoImage(self.image,
							master=self.master)
			self.config(image=self.photo)
		self.redisplay()

	def _resize(self, event):
		self.resize(event.width, event.height)

	def _buttonDown(self, event):
		y = event.y_root - self.winfo_rooty()
		w = self._blockIndex(y)
		self.setSelected(w)
		self.base = (self.blocks[w], self.blocks[w + 1])
		self.origin = event.y_root
		self.lastDelta = 0
		fromTop = y - self.blocks[w]
		fromBottom = self.blocks[w + 1] - y
		if fromTop > 5 and fromBottom > 5:
			self.locked = [0, 0]
		elif fromTop < fromBottom:
			self.locked = [0, 1]
		else:
			self.locked = [1, 0]
		if w == 0:
			self.locked[0] = 1
		if w + 1 == len(self.blocks) - 1:
			self.locked[1] = 1
		if not self.locked[0]:
			maxUp = self.blocks[w - 1] - self.blocks[w]
		elif not self.locked[1]:
			maxUp = self.blocks[w] - self.blocks[w + 1]
		else:
			maxUp = 0
		if not self.locked[1]:
			maxDown = self.blocks[w + 2] - self.blocks[w + 1]
		elif not self.locked[0]:
			maxDown = self.blocks[w + 1] - self.blocks[w]
		else:
			maxDown = 0
		self.limits = (maxUp, maxDown)

	def _buttonDrag(self, event):
		delta = event.y_root - self.origin
		delta = int(delta / self.yStep) * self.yStep
		if delta < self.limits[0]:
			delta = self.limits[0]
		if delta > self.limits[1]:
			delta = self.limits[1]
		if delta == self.lastDelta:
			return
		if not self.locked[0]:
			self.blocks[self.selected] = self.base[0] + delta
		if not self.locked[1]:
			self.blocks[self.selected + 1] = self.base[1] + delta
		self.lastDelta = delta
		self.redisplay()

	def _buttonUp(self, event):
		lastBlock = self.blocks[0]
		newPieces = [ ]
		newBlocks = [ lastBlock ]
		newSelected = -1
		sel = self.selectedBlock()
		for i in range(1, len(self.blocks)):
			piece = self.pieces[i - 1]
			block = self.blocks[i]
			if block > lastBlock:
				if piece == sel:
					newSelected = len(newPieces)
				newPieces.append(piece)
				newBlocks.append(block)
				lastBlock = block
		if len(self.pieces) != len(newPieces):
			self.pieces = newPieces
			self.blocks = newBlocks
			self.selected = newSelected
			self.redisplay()

	def _eventLocation(self, rootx, rooty):
		x = rootx - self.winfo_rootx()
		xs = int(x / self.xStep) * self.xStep
		y = rooty - self.winfo_rooty()
		ys = int(y / self.yStep) * self.yStep
		return x, y, xs, ys

	def _blockIndex(self, y):
		for i in range(1, len(self.blocks)):
			if self.blocks[i] > y:
				return i - 1
				break
		return len(self.blocks) - 1

	def setSelected(self, n):
		self.selected = n
		self.redisplay()

	def selectedBlock(self):
		if self.selected < 0:
			return None
		return self.pieces[self.selected]

	def redisplay(self):
		for i in range(len(self.pieces)):
			piece = self.pieces[i]
			height = self.image.size[1]
			minY = self.blocks[i]
			maxY = self.blocks[i + 1]
			piece.display(self.draw, self.image, minY, maxY, 0)
		if self.background:
			# If we have a background, we create the correct
			# texture image in textureImage, and then copy
			# it back into self.image so we can display it
			self.textureImage.paste(self.background)
			self.textureImage.paste(self.image, None, self.image)
			self.image.paste(self.textureImage)
		else:
			# If we have no background, then textureImage
			# and self.image are identical
			self.textureImage.paste(self.image)
		if self.selected >= 0:
			piece = self.pieces[self.selected]
			minY = self.blocks[self.selected]
			maxY = self.blocks[self.selected + 1]
			piece.displaySelected(self.draw, self.image.size[0],
						minY, maxY)
		self.photo.paste(self.image)

	def addBlock(self, source, rootx, rooty):
		y = rooty - self.winfo_rooty()
		ys = int(y / self.yStep) * self.yStep
		where = self._blockIndex(y)
		fromTop = ys - self.blocks[where]
		fromBottom = self.blocks[where + 1] - ys
		self.blocks.insert(where + 1, ys)
		if fromTop > fromBottom:
			where = where + 1
		block = copy.copy(source.block)
		self.pieces.insert(where, block)
		self.setSelected(where)
		self.redisplay()

	def resetBlock(self, block):
		self.pieces = [ block ]
		self.blocks = [ 0, self.blocks[-1] ]
		self.redisplay()

	def saveState(self):
		return { 'pieces': self.pieces,
			'background': self.background,
			'blocks': self.blocks,
			'selected': self.selected,
			'size': self.image.size }

	def restoreState(self, state):
		self.selected = state.get('selected', -1)
		self.background = state.get('background', None)
		size = state.get('size', (256, 256))
		try:
			self.pieces = state['pieces']
			self.blocks = state['blocks']
		except KeyError:
			if self.background:
				self.pieces = [ TextureBlock.SolidBlock(
							self.TransparentColor) ]
			else:
				self.pieces = [ TextureBlock.BandedBlock(
							self.LeftColor,
							self.MidColor,
							self.RightColor, 0) ]
			self.blocks = [ 0, size[1] ]
		self.config(width=size[0], height=size[1])
		self.resize(size[0], size[1])

	def setBackground(self, bg, redisplay=1):
		if bg is not None:
			if bg.size == self.image.size:
				self.background = bg
			else:
				self.background = bg.resize(self.image.size)
		else:
			self.background = None
		if redisplay:
			self.redisplay()

if __name__ == '__main__':
	def test(self):
		block = TextureBlock.SolidBlock((0, 0, 0))
		self.pieces.append(block)
		self.blocks.insert(1, 96)
		self.redisplay()
	TextureMap.test = test
	app = Tkinter.Frame()
	app.pack(expand=1, fill=Tkinter.BOTH)
	map = TextureMap(app)
	map.pack(side=Tkinter.TOP, expand=1, fill=Tkinter.BOTH)
	b = Tkinter.Button(app, text='Test', command=map.test)
	b.pack(side=Tkinter.BOTTOM, fill=Tkinter.X)
	app.mainloop()
