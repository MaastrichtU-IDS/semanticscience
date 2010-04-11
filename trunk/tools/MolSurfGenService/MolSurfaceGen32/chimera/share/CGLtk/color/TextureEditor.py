# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: TextureEditor.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter

import BlockSource
import TextureMap
import TextureBlock

class EditorTextureMap(TextureMap.TextureMap):

	def __init__(self, master=None, editor=None, **kw):
		self.editor = editor
		apply(TextureMap.TextureMap.__init__, (self, master), kw)

	def dnd_accept(self, source, event):
		if not isinstance(source, BlockSource.BlockSource):
			return None
		return self

	def dnd_enter(self, source, event):
		pass

	def dnd_motion(self, source, event):
		pass

	def dnd_leave(self, source, event):
		pass

	def dnd_commit(self, source, event):
		self.addBlock(source, event.x_root, event.y_root)

	def restoreState(self, state):
		TextureMap.TextureMap.restoreState(self, state)
		self.editor.setSelectedBlock(self.selectedBlock())

	def setSelected(self, n):
		TextureMap.TextureMap.setSelected(self, n)
		self.editor.setSelectedBlock(self.selectedBlock())

class EditorSolidSource(BlockSource.SolidBlockSource):

	def __init__(self, master=None, editor=None, **kw):
		self.editor = editor
		apply(BlockSource.SolidBlockSource.__init__,
						(self, master), kw)

	def redisplay(self):
		BlockSource.SolidBlockSource.redisplay(self)
		self.editor.redisplay()

class EditorBandedSource(BlockSource.BandedBlockSource):

	def __init__(self, master=None, editor=None, **kw):
		self.editor = editor
		apply(BlockSource.BandedBlockSource.__init__,
						(self, master), kw)

	def redisplay(self):
		BlockSource.BandedBlockSource.redisplay(self)
		self.editor.redisplay()

class TextureEditor(Tkinter.Frame):

	def __init__(self, master=None, TextureMap=EditorTextureMap,
			SolidSource=EditorSolidSource,
			BandedSource=EditorBandedSource,
			width=256, height=256, **kw):
		apply(Tkinter.Frame.__init__, (self, master), kw)
		self.map = None
		f = Tkinter.Frame(self, bd=4, relief=Tkinter.GROOVE)
		f.pack(side=Tkinter.RIGHT, padx=5, pady=5)
		self.solidSource = SolidSource(self, self, bd=3,
							relief=Tkinter.GROOVE)
		self.solidSource.pack(side=Tkinter.BOTTOM, fill=Tkinter.Y,
					expand=1, padx=5, pady=5)
		self.bandedSource = BandedSource(self, self, bd=3,
							relief=Tkinter.GROOVE)
		self.bandedSource.pack(side=Tkinter.BOTTOM, fill=Tkinter.Y,
					expand=1, padx=5, pady=5)
		self.map = TextureMap(f, self, width=width, height=height,
					initBlock=self.bandedSource.block)
		self.map.grid(row=0, column=0)

	def redisplay(self):
		if self.map:
			self.map.redisplay()

	def setSelectedBlock(self, block):
		if isinstance(block, TextureBlock.SolidBlock):
			self.solidSource.setBlock(block)
		elif isinstance(block, TextureBlock.BandedBlock):
			self.bandedSource.setBlock(block)
