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

import chimera
from chimera.baseDialog import ModelessDialog
import Tkinter, Pmw
from prefs import prefs, HELIX_COLOR, SHEET_COLOR, OTHER_COLOR

class ColorSSDialog(ModelessDialog):
	title = "Color Secondary Structure"
	buttons = ('OK', 'Apply', 'Defaults', 'Close')
	name = "color by SS"
	help = "ContributedSoftware/colorss/colorss.html"

	def __init__(self):
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		self.info = [
			("Helix", HELIX_COLOR, 'isHelix'),
			("Strand", SHEET_COLOR, 'isSheet'),
			("Other", OTHER_COLOR, None)
		]
		header = Tkinter.Frame(parent)
		header.grid(row=0, column=0, sticky="nsew")
		parent.rowconfigure(0, weight=1)
		for i in range(len(self.info)):
			parent.columnconfigure(i, weight=1)

		from chimera.widgets import MoleculeScrolledListBox
		self.molListBox = MoleculeScrolledListBox(header,
				selectioncommand=lambda: self.configure(
				models=self.molListBox.getvalue()),
				listbox_selectmode="extended",
				labelpos="nw", label_text="Models")
		self.molListBox.grid(row=0, column=0,
					rowspan=len(self.info), sticky="nsew")
		for i in range(3):
			header.rowconfigure(i, weight=1)
		header.columnconfigure(0, weight=1)

		self.colorRibVar = Tkinter.IntVar(parent)
		self.colorRibVar.set(True)
		self.colorAtomVar = Tkinter.IntVar(parent)
		self.colorAtomVar.set(False)
		self.colorSurfVar = Tkinter.IntVar(parent)
		self.colorSurfVar.set(False)
		varFrame = Tkinter.Frame(parent)
		varFrame.grid(row=1, column=0)
		for i, info in enumerate([(self.colorRibVar, "Color ribbons"),
				(self.colorAtomVar, "Color atoms"),
				(self.colorSurfVar, "Color surfaces")]):
			var, text = info
			but = Tkinter.Checkbutton(varFrame, variable=var,
								text=text)
			but.grid(row=i, column=0, sticky='w')

		self.wells = []
		self.actVars = []
		from CGLtk.color.ColorWell import ColorWell
		from chimera.colorTable import getColorByName
		for row, ssInfo in enumerate(self.info):
			ssType, prefName, attrName = ssInfo
			rgba = prefs[prefName]
			if isinstance(rgba, basestring):
				rgba = getColorByName(rgba).rgba()
			well = ColorWell(header, color=rgba,
							noneOkay=True)
			self.wells.append(well)
			well.grid(row=row, column=2)

			actVar = Tkinter.IntVar(parent)
			actVar.set(True)
			self.actVars.append(actVar)
			Tkinter.Checkbutton(header, variable=actVar,
						text=ssType).grid(row=row,
						column=1, sticky='w')
	def Apply(self):
		colors = {}
		for i, ssInfo in enumerate(self.info):
			ssType, prefName, attrName = ssInfo
			rgba = self.wells[i].rgba
			prefs[prefName] = rgba
			if not self.actVars[i].get():
				continue
			if rgba is None:
				color = None
			else:
				color = chimera.MaterialColor(*rgba)
			colors[attrName] = color

		mols = self.molListBox.getvalue()
		# only the protein residues are relevant...
		protein = {}
		for m in mols:
			for r in m.residues:
				ratoms = r.atomsMap
				if 'CA' not in ratoms:
					continue
				if len(ratoms) == 1:
					# possible CA-only model
					if ratoms['CA'][0].element.number == 6:
						protein[r] = True
					continue
				if 'O' in ratoms \
				and 'N' in ratoms \
				and 'C' in ratoms:
					protein[r] = True

		atomAttrs = []
		resAttrs = []
		if self.colorRibVar.get():
			resAttrs = ["ribbonColor"]
		if self.colorAtomVar.get():
			atomAttrs.append("color")
		if self.colorSurfVar.get():
			atomAttrs.append("surfaceColor")
			from chimera.actions import changeSurfsFromCustom
			changeSurfsFromCustom(mols)
		if atomAttrs:
			def colorAttrs(item, res, attrs):
				for attrName, color in colors.items():
					if attrName is None:
						if not (res.isHelix
								or res.isSheet):
							break
					elif getattr(res, attrName):
						break
				else:
					return
				for attr in attrs:
					setattr(item, attr, color)
			for m in mols:
				for a in m.atoms:
					res = a.residue
					if res not in protein:
						continue
					colorAttrs(a, res, atomAttrs)
		if resAttrs:
			for m in mols:
				for res in m.residues:
					if res not in protein:
						continue
					for attrName, color in colors.items():
						if attrName is None:
							if not (res.isHelix
								or res.isSheet):
								break
						elif getattr(res, attrName):
							break
					else:
						continue
					for attr in resAttrs:
						setattr(res, attr, color)

	def configure(self, models=None):
		if models is not None:
			self.molListBox.setvalue(models)

	def Defaults(self):
		from prefs import defaultColors
		for i, ssInfo in enumerate(self.info):
			ssType, prefName, attrName = ssInfo
			self.wells[i].showColor(color=defaultColors[prefName])

from chimera import dialogs
dialogs.register(ColorSSDialog.name, ColorSSDialog)
