# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Editor.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter

from ColorWellInterface import ColorWellInterface, _activeWells
import ColorDnd
import Palette

_editor = None

def _tkColor(rgba):
	r, g, b, a = rgba
	return '#%04x%04x%04x' % (round(r * 65535), round(g * 65535),
					round(b * 65535))

def editor(*args, **kw):
	global _editor
	if _editor is None:
		_editor = apply(Editor, args, kw)
	return _editor

class Favorite(Tkinter.Frame, ColorDnd.ColorSource, ColorDnd.ColorTarget):
	def __init__(self, master=None, editor=None, rgba=None, **kw):
		if rgba is None:
			self.rgba = (0, 0, 0, 1)
		else:
			self.rgba = rgba
		self.editor = editor
		kw['bd'] = 2
		kw['relief'] = Tkinter.RIDGE
		kw['width'] = 20
		kw['height'] = 20
		kw['bg'] = _tkColor(self.rgba)
		apply(Tkinter.Frame.__init__, (self, master), kw)
		ColorDnd.ColorSource.__init__(self, self)

	def dnd_end(self, target, event):
		if target is None \
		and self.winfo_containing(event.x_root, event.y_root) is self:
			self.editor.setFavorite(self)

	def dnd_commit(self, source, event):
		if source is not self:
			ColorDnd.ColorTarget.dnd_commit(self, source, event)
			self.editor.saveFavorite(self)

	def showColor(self, color):
		self.rgba = color
		self.config(bg=_tkColor(self.rgba))

class EditorPalette(Palette.Palette, ColorDnd.ColorSource):
	def __init__(self, editor=None, sourceWidget=None, **kw):
		apply(Palette.Palette.__init__, (self,), kw)
		if sourceWidget:
			ColorDnd.ColorSource.__init__(self, sourceWidget)
		self.editor = editor

	def update(self):
		Palette.Palette.update(self)
		self.editor.setRGBA(rgba=self.rgba, fromPalette=1)

class Editor(ColorWellInterface):

	numFavorites = 10

	def __init__(self, helpCmd=None, **kw):
		apply(ColorWellInterface.__init__, (self,), kw)
		self.mainUI(self)
		self.buttonUI(self, helpCmd)

	def mainUI(self, frame):
		frame.columnconfigure(1, weight=1)
		frame.rowconfigure(3, weight=1)
		self.color = Tkinter.Label(frame, text='', height=2,
						relief=Tkinter.SUNKEN)
		self.color.grid(column=0, columnspan=3, row=0, sticky='nsew')
		label = Tkinter.Label(frame, text='Color name:')
		label.grid(column=0, row=1, sticky='e')
		self.colorName = Tkinter.Entry(frame)
		self.colorName.bind('<Return>', self._colorNameCB)
		self.colorName.grid(column=1, columnspan=2,
						row=1, sticky='nsew')
		label = Tkinter.Label(frame, text='Color space:')
		label.grid(column=0, row=2, sticky='e')
		self.csVar = Tkinter.StringVar(frame)
		self.csVar.set(Palette.DefaultColorSpace)
		self.alphaVar = Tkinter.IntVar(frame)
		self.alphaVar.set(0)
		colorSpaces = Palette.ColorSpaces[:]
		# YIQ conversion to other color spaces is problematic
		colorSpaces.remove('YIQ')
		args = (frame, self.csVar) + tuple(colorSpaces)
		self.colorspaceMenu = apply(Tkinter.OptionMenu, args)
		self.colorspaceMenu.grid(column=1, row=2, sticky='nsew')
		self.withAlpha = Tkinter.Checkbutton(frame, text='Opacity',
				relief=Tkinter.RAISED, variable=self.alphaVar)
		self.withAlpha.grid(column=2, row=2, sticky='news')
		self.colorspace = self._getColorspace()
		self.paletteFrame = Tkinter.Frame(frame)
		self.paletteFrame.grid(column=0, columnspan=3, row=3,
						sticky='nsew')
		self.paletteFrame.columnconfigure(1, weight=1)
		self.palette = EditorPalette(master=self.paletteFrame,
						editor=self,
						sourceWidget=self.color,
						colorspace=self.colorspace,
						width=120, height=40)
		self.channelEntries = []
		self.channelLabels = []
		self._showPalette()
		f = Tkinter.Frame(frame, bd=3, relief=Tkinter.SUNKEN)
		f.grid(column=0, columnspan=3, row=4, sticky='ew')
		self.favorites = []
		for i in range(self.numFavorites):
			b = Favorite(f, editor=self)
			b.grid(column=i, row=0, sticky='nsew')
			f.columnconfigure(i, weight=1)
			self.favorites.append(b)

		self.csVar.trace_variable('w', self._setColorspace)
		self.alphaVar.trace_variable('w', self._setColorspace)
		self.setRGBA(rgba=self.palette.rgba, fromPalette=1)

	def buttonUI(self, frame, helpCmd):
		buttonFrame = Tkinter.Frame(frame, relief="flat", bd=2)
		buttonFrame.grid(column=0, columnspan=3, row=5, sticky="ew")
		self.noneButton = Tkinter.Button(buttonFrame, text="No Color",
					state="disabled", command=self.noColor)
		self.noneButton.pack(side="left", padx='1p')
		if helpCmd:
			helpButton = Tkinter.Button(buttonFrame, text="Help",
						command=helpCmd)
			helpButton.pack(side="right", padx='1p')
		dismissButton = Tkinter.Button(buttonFrame, text="Close",
						command=self.deactivate)
		dismissButton.pack(side="right", padx='1p')

	def _getColorspace(self):
		name = self.csVar.get()
		if self.alphaVar.get():
			name = name + 'A'
		return getattr(Palette, name)()

	def _showPalette(self):
		nc = self.colorspace.numChannels
		self.palette.grid(column=1, row=0, rowspan=nc, sticky='nsew')
		while len(self.channelEntries) < nc:
			e = Tkinter.Entry(self.paletteFrame, width=5)
			e.bind('<Return>', self.setChannel)
			self.channelEntries.append(e)
			l = Tkinter.Label(self.paletteFrame, width=2)
			self.channelLabels.append(l)
		while len(self.channelEntries) > nc:
			e = self.channelEntries[-1]
			e.destroy()
			self.channelEntries.remove(e)
		for l in self.channelLabels:
			l.grid_forget()
		for i in range(nc):
			e = self.channelEntries[i]
			e.grid(column=2, row=i, sticky='ew')
			l = self.channelLabels[i]
			l.config(text=self.colorspace.label[i])
			l.grid(column=0, row=i)
			self.paletteFrame.rowconfigure(i, weight=1)

	def _setColorspace(self, n1, n2, op):
		self.colorspace = self._getColorspace()
		self._showPalette()
		self.palette.setColorspace(self.colorspace)

	def setRGBA(self, fromPalette=0, **kw):
		apply(ColorWellInterface.setRGBA, (self,), kw)
		tkName = _tkColor(self.rgba)
		self.colorName.delete(0, Tkinter.END)
		self.colorName.insert(0, tkName)
		self.color.config(bg=tkName)
		color = self.palette.currentColor
		nc = self.colorspace.numChannels
		for i in range(nc):
			c = color[i]
			e = self.channelEntries[i]
			e.delete(0, Tkinter.END)
			e.insert(0, '%.3f' % c)
		if not fromPalette:
			self.palette.setCurrentRGBA(self.rgba)
			if self.rgba[3] != 1.0 and not self.alphaVar.get():
				self.withAlpha.invoke()

	def _colorNameCB(self, event=None):
		self.setRGBA(name=self.colorName.get())
	
	def noColor(self):
		"""callback for "No Color" button"""
		for well in _activeWells:
			well.showColor(color=None, notifyPanel=0)
	
	def register(self, well, *args, **kw):
		apply(ColorWellInterface.register, (self, well) + args, kw)
		self.checkNoneOkay()
	
	def deregister(self, well, *args, **kw):
		apply(ColorWellInterface.deregister, (self, well) + args, kw)
		self.checkNoneOkay()
	
	def checkNoneOkay(self):
		noneState = "normal"
		for well in _activeWells:
			if not well.noneOkay:
				noneState = "disabled"
				break
		try:
			self.noneButton.config(state=noneState)
		except Tkinter.TclError:
			# We must have been destroyed already and
			# an orphaned ColorWell is trying to go away
			pass

	def setFavorite(self, fav):
		self.setRGBA(rgba=fav.rgba)

	def saveFavorite(self, fav):
		pass

	def setChannel(self, event):
		w = event.widget
		n = self.channelEntries.index(w)
		s = w.get()
		try:
			value = float(s)
			if value < 0 or value > 1:
				raise ValueError, 'Value out of range'
		except ValueError:
			w.delete(0, Tkinter.END)
			w.insert(0, '%.3f' % self.palette.currentColor[n])
			return
		self.palette.setChannelValue(n, value)

if __name__ == '__main__':
	editor = Editor()
	editor.deiconify()
	editor.mainloop()
