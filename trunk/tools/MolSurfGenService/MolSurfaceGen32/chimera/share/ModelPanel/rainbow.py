# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: rainbow.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog
import Tkinter
import Pmw
from CGLtk.color.ColorWell import ColorWell
from chimera import replyobj
from Midas.midas_rainbow import rainbowModels, defaultColors
from chimera import preferences

class RainbowDialog(ModelessDialog):
	title = 'Rainbow'
	buttons = ('OK', 'Apply', 'Defaults', 'Close',)
	default = 'OK'
	name = "rainbow models"
	help = "UsersGuide/modelpanel.html#rainbow"

	def __init__(self):
		self.prefs = preferences.addCategory("Rainbow models",
					preferences.HiddenCategory,
					optDict={ "colors": defaultColors })
		ModelessDialog.__init__(self)
	
	def configure(self, models=[], target=None):
		self.molListBox.setvalue(models)
		if target:
			self.colorChangeVar.set(target)

	def fillInUI(self, parent):
		self.parent = parent
		Tkinter.Label(parent, text="Change color every:").grid(
					row=0, rowspan=3, column=0, sticky='w')
		self.colorChangeVar = Tkinter.StringVar(parent)
		self.colorChangeVar.set("residues")
		Tkinter.Radiobutton(parent, text='residue', value='residues',
					variable=self.colorChangeVar).grid(
					row=0, column=1, sticky='w')
		Tkinter.Radiobutton(parent, text='chain', value='chains',
					variable=self.colorChangeVar).grid(
					row=1, column=1, sticky='w')
		Tkinter.Radiobutton(parent, text='model', value='models',
					variable=self.colorChangeVar).grid(
					row=2, column=1, sticky='w')
		group = Pmw.Group(parent, tag_text='Color range')
		group.grid(row=3, column=0, columnspan=2)
		self.wells = []
		for i, color in enumerate(self.prefs["colors"]):
			well = ColorWell(group.interior(), color=color,
								noneOkay=1)
			well.grid(row=0, column=i)
			self.wells.append(well)
		from chimera.widgets import MoleculeScrolledListBox
		self.molListBox = MoleculeScrolledListBox(parent,
			listbox_selectmode="extended", labelpos="n",
			label_text="Models")
		self.molListBox.grid(row=0, column=2, rowspan=4, sticky="news")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(2, weight=1)

	def Apply(self):
		colors = []
		allColors = []
		for well in self.wells:
			color = well.rgba
			allColors.append(color)
			if color is None:
				continue
			colors.append(color)
		if not colors:
			replyobj.error("No colors for rainbow")
			return
		rainbowModels(self.molListBox.getvalue(),
				changeAt=self.colorChangeVar.get(),
				colors=colors)
		self.prefs["colors"] = allColors
		
	def Defaults(self):
		for i, color in enumerate(defaultColors):
			self.wells[i].showColor(color=color)

from chimera import dialogs
dialogs.register(RainbowDialog.name, RainbowDialog)
