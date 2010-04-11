#!/usr/bin/env python

# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: PrintPanel.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter
Tk = Tkinter
from tkFileDialog import asksaveasfilename
from ModalWindow import ModalWindow

class PrintPanel(ModalWindow):
	"""
	PrintPanel presents a panel containing some standard
	print options (paper type, orientation, printers).  Return
	The option values are stored in a dictionary that is
	passed in at invocation time.
	"""

	def __init__(self, *args, **kw):
		apply(ModalWindow.__init__, (self,) + args, kw)
		self.optionDict = {}

		#
		# Start with buttons at bottom
		#
		f = Tk.Frame(self)
		f.pack(side=Tk.BOTTOM, fill=Tk.X, ipadx=2, ipady=2, padx=5)
		b = Tk.Button(f, text='Print', width=6, command=self._toPrinter)
		b.pack(side=Tk.RIGHT, fill=Tk.X)
		b = Tk.Button(f, text='Save...', width=6, command=self._toFile)
		b.pack(side=Tk.RIGHT, fill=Tk.X)
		b = Tk.Button(f, text='Cancel', width=6, command=self.end)
		b.pack(side=Tk.RIGHT, fill=Tk.X)

		#
		# Available printers
		#
		self.printerList, defaultPrinter = self._findPrinters()
		f = Tk.Frame(self)
		f.pack(side=Tk.BOTTOM, fill=Tk.X, padx=5)
		l = Tk.Label(f, text='Printer:', width=10, anchor=Tk.E)
		l.pack(side=Tk.LEFT)
		self.printerVar = Tk.StringVar(self)
		args = (f, self.printerVar) + tuple(self.printerList)
		self.printerMenuButton = apply(Tk.OptionMenu, args)
		self.printerMenuButton['anchor'] = Tk.W
		self.printerMenuButton['width'] = 10
		self.printerMenuButton.pack(side=Tk.LEFT, expand=Tk.TRUE, fill=Tk.X)
		self.printerVar.set(defaultPrinter)

		#
		# Page layout options
		#
		f = Tk.Frame(self)
		f.pack(side=Tk.BOTTOM, fill=Tk.X, padx=5)
		l = Tk.Label(f, text='Orientation:', width=10, anchor=Tk.E)
		l.pack(side=Tk.LEFT)
		self.orientationVar = Tk.StringVar(self)
		self.orientationButton = Tk.OptionMenu(f, self.orientationVar,
						'Landscape', 'Portrait')
		self.orientationButton['anchor'] = Tk.W
		self.orientationButton['width'] = 10
		self.orientationButton.pack(side=Tk.LEFT, expand=Tk.TRUE, fill=Tk.X)
		self.orientationVar.set('Landscape')

		f = Tk.Frame(self)
		f.pack(side=Tk.BOTTOM, fill=Tk.X, padx=5)
		l = Tk.Label(f, text='Paper Type:', width=10, anchor=Tk.E)
		l.pack(side=Tk.LEFT)
		self.paperTypeVar = Tk.StringVar(self)
		self.paperTypeButton = Tk.OptionMenu(f, self.paperTypeVar,
						'Letter', 'Legal', 'EPS')
		self.paperTypeButton['anchor'] = Tk.W
		self.paperTypeButton['width'] = 10
		self.paperTypeButton.pack(side=Tk.LEFT, expand=Tk.TRUE, fill=Tk.X)
		self.paperTypeVar.set('Letter')

	def _toPrinter(self):
		self.optionDict['orientation'] = self.orientationVar.get()
		self.optionDict['paperType'] = self.paperTypeVar.get()
		self.optionDict['destination'] = 'printer'
		self.optionDict['printer'] = self.printerVar.get()
		self.end(self.optionDict)

	def _toFile(self):
		self.optionDict['orientation'] = \
					self.orientationVar.get()
		self.optionDict['paperType'] = self.paperTypeVar.get()
		if self.optionDict['paperType'] == 'EPS':
			extension = '.eps'
			filetypes = [('Encapsulated PostScript', '*.eps'),
					('All Files', '*.*')]
		else:
			extension = '.ps'
			filetypes = [('PostScript', '*.ps'),
					('All Files', '*.*')]
		try:
			import OpenSave
		except ImportError:
			func = self._useTk
		else:
			func = self._useOpenSave
		func('Save As PostScript', extension, filetypes)

	def _useTk(self, title, extension, filetypes):
		filename = asksaveasfilename(master=self, title=title,
				defaultextension=extension, filetypes=filetypes)
		if not filename:
			self.end()
		else:
			self.optionDict['destination'] = 'file'
			self.optionDict['file'] = filename
			self.end(self.optionDict)

	def _useOpenSave(self, title, extension, filetypes):
		from OpenSave import SaveModal
		filters = []
		for description, glob in filetypes:
			if glob == "*.*":
				continue
			filters.append((description, glob, glob[1:]))
		paths = SaveModal(title=title, filters=filters).run(self)
		if not paths:
			self.end()
		else:
			self.optionDict['destination'] = 'file'
			self.optionDict['file'] = paths[0]
			self.end(self.optionDict)

	def _findPrinters(self):
		#
		# Normally I would try to locate printers in /etc/printcap,
		# but ours is so overloaded with non-local printers that
		# I'm just going to supply a static list (plus the PRINTER
		# environment variable, of course)
		#
		import posix
		list = ['arg', 'asp', 'trp', 'cys',
			'pro', 'gly', 'ala', 'his']
		try:
			defaultPrinter = posix.environ['PRINTER']
			if defaultPrinter not in list:
				list.append(defaultPrinter)
		except KeyError:
			defaultPrinter = list[0]
		list.sort()
		return list, defaultPrinter

if __name__ == '__main__':
	p = PrintPanel()
	print p.run()
