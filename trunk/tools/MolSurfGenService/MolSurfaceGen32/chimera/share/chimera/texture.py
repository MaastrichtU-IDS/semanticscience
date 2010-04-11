# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: texture.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter
import tkMessageBox
import Pmw
from PIL import Image

import chimera
from baseDialog import ModelessDialog, ModalDialog
from CGLtk.color import TextureEditor, TextureMap

goodSizes = ( 256, 128, 64, 32, 16, 8, 4, 2, 1 )

class ChimeraTextureMap(TextureEditor.EditorTextureMap):

	def __init__(self, *args, **kw):
		self.panel = None
		self.causedRedisplay = 0
		TextureEditor.EditorTextureMap.__init__(self, *args, **kw)

	def redisplay(self):
		TextureEditor.EditorTextureMap.redisplay(self)
		if self.panel:
			state = self.panel.texture.editorState
			xFactor = state['xFactor']
			yFactor = state['yFactor']
			if xFactor == 1 and yFactor == 1:
				self.panel.updateTexture(self.textureImage)
			else:
				image = self._unscaleImage(self.textureImage,
								xFactor,
								yFactor)
				self.panel.updateTexture(image)
			self.causedRedisplay = 1

	def changeTexture(self):
		texture = self.panel.texture
		try:
			state = texture.editorState
		except AttributeError:
			w, h, depth, nc, nb = texture.sizes()
			if h >= 16 and w >= 16:
				xFactor = 1
				yFactor = 1
				size = (w, h)
				image = texture.image
			else:
				xFactor = 1
				while w < 16:
					xFactor = xFactor * 2
					w = w * 2
				yFactor = 1
				while h < 16:
					yFactor = yFactor * 2
					h = h * 2
				size = (w, h)
				image = self._scaleImage(texture.image,
							xFactor, yFactor)
			state = { 'size': size,
				  'xFactor': xFactor,
				  'yFactor': yFactor,
				  'background': image }
			texture.editorState = state
		self.xStep = state['xFactor']
		self.yStep = state['yFactor']
		self.restoreState(state)

	def redrawIfNeeded(self):
		if not self.causedRedisplay:
			texture = self.panel.texture
			texture.editorState.update(self.saveState())
			texture.editorState['background'] = texture.image
			self.redisplay()
		self.causedRedisplay = 0

	def _scaleImage(self, orig, xFactor, yFactor):
		size = orig.size
		newSize = (size[0] * xFactor, size[1] * yFactor)
		return orig.resize(newSize)

	def _unscaleImage(self, scaled, xFactor, yFactor):
		size = scaled.size
		newSize = (size[0] / xFactor, size[1] / yFactor)
		return scaled.resize(newSize)

class NewPanel(ModalDialog):

	buttons = ('OK', 'Cancel')
	highlight = 'OK'
	title = 'Define New Texture'

	def __init__(self, *args, **kw):
		apply(ModalDialog.__init__, (self,) + args, kw)
	
	def fillInUI(self, master):
		self.entry = Pmw.EntryField(master, labelpos='we',
						label_text='Texture Name')
		self.entry.pack(side=Tkinter.TOP, fill=Tkinter.X)

		g = Pmw.Group(master, tag_text='Texture Size')
		g.pack(side=Tkinter.TOP, expand=1, fill=Tkinter.X)
		inside = g.interior()
		self.widthVar, om = self.__makeSize(inside)
		om.pack(side=Tkinter.LEFT, expand=1, fill=Tkinter.X)
		l = Tkinter.Label(inside, text=' x ')
		l.pack(side=Tkinter.LEFT)
		self.heightVar, om = self.__makeSize(inside)
		om.pack(side=Tkinter.LEFT, expand=1, fill=Tkinter.X)

	def __makeSize(self, master):
		v = Tkinter.IntVar(master)
		v.set(goodSizes[0])
		args = tuple((master, v) + goodSizes)
		om = apply(Tkinter.OptionMenu, args)
		return v, om

	def OK(self):
		ModalDialog.Cancel(self, value=1)

	def Cancel(self):
		ModalDialog.Cancel(self, value=0)

	def values(self):
		entry = self.entry.component('entry')
		return entry.get(), self.widthVar.get(), self.heightVar.get()

class TextureDialog(ModelessDialog):

	name = '2D Texture Editor'
	help = '2dTexture.html'
	buttons = ('New', 'Close')

	defaultTexture = None
	createdTextures = []

	def __init__(self, master=None, *args, **kw):
		self.texture = None
		self.newPanel = None
		apply(ModelessDialog.__init__, (self, master) + args, kw)

	def fillInUI(self, master):
		# TextureEditor
		top = Tkinter.Frame(master)
		top.pack(side=Tkinter.TOP, anchor=Tkinter.W,
				fill=Tkinter.X, padx=2, pady=2)

		te = TextureEditor.TextureEditor(top,
				TextureMap=ChimeraTextureMap)
		te.map.panel = self
		te.pack(side=Tkinter.TOP, expand=1, fill=Tkinter.BOTH)
		self.editor = te

		# Texture option menu
		self.names = Tkinter.Menubutton(te, width=10, bd=2,
						indicatoron=1,
						relief=Tkinter.RAISED,
						anchor='c')
		self.names.pack(side=Tkinter.TOP, expand=1, fill=Tkinter.X)
		self.menu = Tkinter.Menu(self.names)
		self.names['menu'] = self.menu

		# Texture background
		b = Tkinter.Button(te, text='Load Background',
					command=self.__loadBackground)
		b.pack(side=Tkinter.TOP, fill=Tkinter.X)

		self.reloadTextures()
		self.monitorHandler = chimera.triggers.addHandler(
					'Texture', self.__textureHandler, None)

	def __del__(self):
		chimera.triggers.deleteHandler('Texture', self.monitorHandler)

	def New(self):
		if not self.newPanel:
			self.newPanel = NewPanel(self.uiMaster())
		if not self.newPanel.run(self.uiMaster()):
			return
		name, width, height = self.newPanel.values()
		if len(name) == 0:
			tkMessageBox.showerror(title='Error',
				message='No texture name specified')
			return
		if chimera.Texture.lookup(name):
			tkMessageBox.showerror(title='Error',
				message='Texture "%s" already exists' % name)
			return
		t = chimera.Texture(name, chimera.Texture.RGBA,
				chimera.Texture.UnsignedByte, width, height)
		t.editorState = { 'size': (width, height),
					'xFactor': 1, 'yFactor': 1 }
		self.__selectTexture(name)
		TextureDialog.createdTextures.append(t)

	def __selectTexture(self, textureName):
		if self.texture:
			state = self.editor.map.saveState()
			if not hasattr(self.texture, 'editorState'):
				self.texture.editorState = state
			else:
				self.texture.editorState.update(state)
		self.texture = chimera.Texture.lookup(textureName)
		if self.texture is None:
			raise NameError, 'Cannot find texture named "%s"' \
						% textureName
		self.editor.map.changeTexture()
		self.names.config(text=textureName)

	def __loadBackground(self):
		if not hasattr(self, '_loadBGDialog'):
			from OpenSave import OpenModeless
			self._loadBGDialog = OpenModeless(
				title='Load Background', command=self._loadBGCB)
		self._loadBGDialog.enter()

	def _loadBGCB(self, okayed, dialog):
		if not okayed:
			return
		for path in dialog.getPaths():
			self.editor.map.setBackground(Image.open(path))

	def reloadTextures(self):
		cursel = self.names['text']
		tList = chimera.Texture.list().items()
		if tList:
			nList = []
			for n, t in tList:
				if t.type() != t.UnsignedByte:
					continue
				w, h, depth, nc, nb = t.sizes()
				if w not in goodSizes or h not in goodSizes:
					continue
				if depth != 1 or nc < 3:
					continue
				nList.append(n)
			tList = nList
			tList.sort()
		if TextureDialog.defaultTexture is None:
			name = '2dTexture'
			x = chimera.Texture(name, chimera.Texture.RGBA,
						chimera.Texture.UnsignedByte,
						128, 128)
			x.editorState = { 'size': (128, 128),
						'xFactor': 1, 'yFactor': 1 }
			tList.append(name)
			TextureDialog.defaultTexture = x
		tList.sort()
		self.menu.delete(0, Tkinter.END)
		for t in tList:
			self.menu.add_command(label=t,
						command=lambda s=self, t=t:
							s.__selectTexture(t))
		if cursel not in tList:
			cursel = None
		if not cursel:
			cursel = tList[0]
		self.__selectTexture(cursel)

	def updateTexture(self, image):
		if not self.texture:
			return
		w, h, depth, nc, nb = self.texture.sizes()
		if image.size[0] != w or image.size[1] != h:
			raise ValueError, 'image/texture size mismatch'
		self.texture.image = image

	def __textureHandler(self, trigger, closure, textures):
		if textures.created or textures.deleted:
			self.reloadTextures()
			return
		for t in textures.modified:
			if t == self.texture:
				self.editor.map.redrawIfNeeded()
import dialogs
dialogs.register(TextureDialog.name, TextureDialog)
