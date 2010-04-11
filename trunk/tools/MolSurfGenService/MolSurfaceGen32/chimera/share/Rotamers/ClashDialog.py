# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ClashDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog
from prefs import prefs, CLASH_THRESHOLD, HBOND_ALLOWANCE, CLASH_METHOD, \
	CLASH_PBS, CLASH_COLOR, CLASH_WIDTH, HBOND_COLOR, HBOND_WIDTH, \
	RELAX_COLOR, CLASH_IGNORE_OTHERS

class ClashDialog(ModelessDialog):
	title = "Rotamer Clash Params"
	buttons = ("OK", "Apply", "Close")
	help = "ContributedSoftware/rotamers/rotamers.html#clashes"

	def __init__(self, rotDialog):
		self.rotDialog = rotDialog
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		row = 0
		from DetectClash.gui import ClashDef, HbondAllow
		self.clashDef = ClashDef(parent, value=prefs[CLASH_THRESHOLD])
		self.clashDef.grid(row=row, column=0, sticky='w')
		row += 1

		self.hbondAllow = HbondAllow(parent,
						value=prefs[HBOND_ALLOWANCE])
		self.hbondAllow.grid(row=row, column=0, sticky='w')
		row += 1

		import Pmw, Tkinter
		Tkinter.Button(parent, text="Default criteria",
			pady=0, command=self._revertDefaults).grid(row=row)
		row += 1

		self.computeType = Pmw.RadioSelect(parent, pady=0,
			buttontype='radiobutton', labelpos='w',
			label_text="Column Value:", orient='vertical',
			frame_borderwidth=2, frame_relief="ridge")
		self.buttonInfo= [
			("Number of clashes", "num"),
			("Sum of overlaps", "sum"),
		]
		for label, short in self.buttonInfo:
			self.computeType.add(label)
			if prefs[CLASH_METHOD] == short:
				default = label
		self.computeType.invoke(default)
		self.computeType.grid(row=row, column=0)
		row += 1

		f = Tkinter.Frame(parent)
		f.grid(row=row, column=0, sticky='w')
		self.pbVar = Tkinter.IntVar(parent)
		self.pbVar.set(prefs[CLASH_PBS])
		Tkinter.Checkbutton(f, text="Draw pseudobonds of color",
			variable=self.pbVar).grid(row=0, column=0)
		from CGLtk.color.ColorWell import ColorWell
		self.pbColorWell = ColorWell(f, noneOkay=False,
			color=prefs[CLASH_COLOR])
		self.pbColorWell.grid(row=0, column=1)
		self.pbWidthEntry = Pmw.EntryField(f, labelpos='w',
			label_text=" and width", validate={'validator': 'real',
			'min': 0.01}, entry_width=4, entry_justify="center",
			value=str(prefs[CLASH_WIDTH]))
		self.pbWidthEntry.grid(row=0, column=2)
		row += 1

		self.ignoreOthersVar = Tkinter.IntVar(parent)
		self.ignoreOthersVar.set(prefs[CLASH_IGNORE_OTHERS])
		Tkinter.Checkbutton(parent, text="Ignore clashes with other"
			" models", variable=self.ignoreOthersVar).grid(row=row,
			column=0, sticky='w')
		row += 1

	def Apply(self):
		from chimera import UserError
		self.clashDef.invoke()
		if not self.clashDef.valid():
			self.enter()
			raise UserError("Invalid clash amount")
		prefs[CLASH_THRESHOLD] = float(self.clashDef.getvalue())
		self.hbondAllow.invoke()
		if not self.hbondAllow.valid():
			self.enter()
			raise UserError("Invalid H-bond overlap amount")
		prefs[HBOND_ALLOWANCE] = float(self.hbondAllow.getvalue())
		prefs[CLASH_PBS] = self.pbVar.get()
		if prefs[CLASH_PBS]:
			prefs[CLASH_COLOR] = self.pbColorWell.rgba
			pbColor = chimera.MaterialColor(*prefs[CLASH_COLOR])
			self.pbWidthEntry.invoke()
			if not self.pbWidthEntry.valid():
				self.enter()
				raise UserError("Invalid pseudobond width")
			prefs[CLASH_WIDTH] = float(self.pbWidthEntry.getvalue())
		else:
			pbColor = None
		prefs[CLASH_METHOD] = self.buttonInfo[self.computeType.index(
			self.computeType.getvalue())][1]
		prefs[CLASH_IGNORE_OTHERS] = self.ignoreOthersVar.get()
		self.rotDialog.addClashColumn(prefs[CLASH_THRESHOLD],
			prefs[HBOND_ALLOWANCE], prefs[CLASH_METHOD],
			prefs[CLASH_PBS], pbColor, prefs[CLASH_WIDTH],
			prefs[CLASH_IGNORE_OTHERS])

	def destroy(self):
		self.rotDialog = None
		if prefs[CLASH_PBS]:
			from DetectClash import nukeGroup
			nukeGroup()
		ModelessDialog.destroy(self)

	def _revertDefaults(self):
		from prefs import defaults
		self.clashDef.setvalue(str(defaults[CLASH_THRESHOLD]))
		self.hbondAllow.setvalue(str(defaults[HBOND_ALLOWANCE]))
