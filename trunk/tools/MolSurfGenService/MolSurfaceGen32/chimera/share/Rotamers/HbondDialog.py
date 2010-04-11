# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: HbondDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog
from prefs import prefs, HBOND_COLOR, RELAX_COLOR, HBOND_WIDTH, DRAW_HBONDS, \
				HBOND_IGNORE_OTHERS

class HbondDialog(ModelessDialog):
	title = "Hydrogen Bond Params"
	buttons = ("OK", "Apply", "Close")
	help = "ContributedSoftware/rotamers/rotamers.html#hbonds"

	def __init__(self, rotDialog):
		self.rotDialog = rotDialog
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		import Tkinter, Pmw
		row = 0
		f = Tkinter.Frame(parent)
		f.grid(row=row, column=0)
		self.drawHbondsVar = Tkinter.IntVar(parent)
		self.drawHbondsVar.set(prefs[DRAW_HBONDS])
		Tkinter.Checkbutton(f, text="Draw H-bonds of color",
			variable=self.drawHbondsVar).grid(row=0, column=0)
		from CGLtk.color.ColorWell import ColorWell
		self.hbColorWell = ColorWell(f, noneOkay=False,
						color=prefs[HBOND_COLOR])
		self.hbColorWell.grid(row=0, column=1)
		self.hbWidthEntry = Pmw.EntryField(f, labelpos='w',
			label_text=" and width", validate={'validator': 'real',
			'min': 0.01}, entry_width=4, entry_justify="center",
			value=str(prefs[HBOND_WIDTH]))
		self.hbWidthEntry.grid(row=0, column=2)
		row += 1

		from FindHBond.gui import RelaxParams
		self.relaxParams = RelaxParams(parent, prefs[RELAX_COLOR])
		self.relaxParams.grid(row=row, column=0)
		row += 1

		self.ignoreOthersVar = Tkinter.IntVar(parent)
		self.ignoreOthersVar.set(prefs[HBOND_IGNORE_OTHERS])
		Tkinter.Checkbutton(parent, text="Ignore H-bonds with other"
			" models", variable=self.ignoreOthersVar).grid(row=row,
			column=0, sticky='w')
		row += 1

	def Apply(self):
		dhb = self.drawHbondsVar.get()
		prefs[DRAW_HBONDS] = dhb

		prefs[HBOND_COLOR] = self.hbColorWell.rgba
		bc = chimera.MaterialColor(*prefs[HBOND_COLOR])

		self.hbWidthEntry.invoke()
		if not self.hbWidthEntry.valid():
			self.enter()
			raise UserError("Invalid H-bond width")
		lw = prefs[HBOND_WIDTH] = float(self.hbWidthEntry.getvalue())

		distSlop = 0.0
		angleSlop = 0.0
		twoColors = False
		relax = self.relaxParams.relaxConstraints
		rc = self.relaxParams.relaxColor
		if relax:
			distSlop = self.relaxParams.relaxDist
			angleSlop = self.relaxParams.relaxAngle
			if self.relaxParams.useRelaxColor:
				twoColors = True
				prefs[RELAX_COLOR] = rc.rgba()
		self.groupName = "H-bonds for rotamers of %s" % (
						self.rotDialog.residue)
		prefs[HBOND_IGNORE_OTHERS] = self.ignoreOthersVar.get()
		self.rotDialog.addHbondColumn(dhb, bc, lw, relax, distSlop,
				angleSlop, twoColors, rc, self.groupName,
				prefs[HBOND_IGNORE_OTHERS])

	def destroy(self):
		self.rotDialog = None
		if hasattr(self, 'groupName'):
			from Rotamers import nukeGroup
			nukeGroup(self.groupName)
		ModelessDialog.destroy(self)
