# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: BlockSource.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter
import Tkdnd

import ColorWell
import TextureMap
import TextureBlock

class BlockSource(Tkinter.Frame):

	# BlockSource is an abstract base class and assumes that the
	# __init__ function of the derived class has created self.block
	# (which must be a TextureBlock.Block)

	def __init__(self, master=None, **kw):
		apply(Tkinter.Frame.__init__, (self, master), kw)
		f = Tkinter.Frame(self, bd=3, relief=Tkinter.RIDGE)
		f.pack(side=Tkinter.TOP, pady=5, anchor=Tkinter.N)
		self.map = TextureMap.TextureMap(f, width=100, height=20,
							selectable=0,
							initBlock=self.block)
		self.map.pack(anchor=Tkinter.N)
		self.map.bind('<ButtonPress>', self.dnd_start)

	def redisplay(self):
		self.map.redisplay()

	def setBlock(self, block):
		self.block = block
		self.map.resetBlock(block)
		self.redisplay()

	def dnd_start(self, event):
		Tkdnd.dnd_start(self, event)

	def dnd_end(self, target, event):
		pass

class SolidBlockSource(Tkinter.Frame, BlockSource):

	InitColor = (0, 0, 0, 1)

	def __init__(self, master=None, **kw):
		self.block = TextureBlock.SolidBlock(self.InitColor)
		apply(BlockSource.__init__, (self, master), kw)
		self.well = ColorWell.ColorWell(self,
						color=self.InitColor,
						callback=self._updateColor)
		self.well.pack(side=Tkinter.TOP)

	def _updateColor(self, color):
		self.block.color = color
		self.redisplay()

	def setBlock(self, block):
		BlockSource.setBlock(self, block)
		self.well.showColor(block.color)

class BandedBlockSource(Tkinter.Frame, BlockSource):
	
	InitLeftColor = (1, 0, 0, 1)
	InitMidColor = (0, 0, 1, 1)
	InitRightColor = (0, 1, 0, 1)

	def __init__(self, master=None, **kw):
		self.numBandsVar = Tkinter.IntVar(master)
		self.numBandsVar.set(2)
		self.block = TextureBlock.BandedBlock(self.InitLeftColor,
							self.InitMidColor,
							self.InitRightColor,
							self.numBandsVar.get())
		apply(BlockSource.__init__, (self, master), kw)
		self.scale = Tkinter.Scale(self, digits=0, from_=0, to=10,
						var=self.numBandsVar,
						showvalue=0,
						orient=Tkinter.HORIZONTAL,
						command=self._setScale)
		self.scale.pack(side=Tkinter.BOTTOM, fill=Tkinter.BOTH,
						expand=1)
		self.leftWell = ColorWell.ColorWell(self,
						color=self.InitLeftColor,
						callback=self._updateLeftColor)
		self.leftWell.pack(side=Tkinter.LEFT, expand=1)
		self.midWell = ColorWell.ColorWell(self,
						color=self.InitMidColor,
						callback=self._updateMidColor)
		self.midWell.pack(side=Tkinter.LEFT, expand=1)
		self.rightWell = ColorWell.ColorWell(self,
						color=self.InitRightColor,
						callback=self._updateRightColor)
		self.rightWell.pack(side=Tkinter.LEFT, expand=1)

	def _updateLeftColor(self, color):
		self.block.leftColor = color
		self.redisplay()

	def _updateMidColor(self, color):
		self.block.midColor = color
		self.redisplay()

	def _updateRightColor(self, color):
		self.block.rightColor = color
		self.redisplay()

	def _setScale(self, v):
		self.block.numBands = int(v)
		self.redisplay()

	def setBlock(self, block):
		BlockSource.setBlock(self, block)
		self.leftWell.showColor(block.leftColor)
		self.midWell.showColor(block.midColor)
		self.rightWell.showColor(block.rightColor)
		self.numBandsVar.set(block.numBands)
