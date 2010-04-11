# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ChimeraExtension.py 26655 2009-01-07 22:02:30Z gregc $

import chimera.extension

class ColorSSEMO(chimera.extension.EMO):
	help = "color by secondary structure"
	def name(self):
		return 'Color Secondary Structure'
	def description(self):
		return self.help
	def categories(self):
		return ['Depiction']
	def icon(self):
		return self.path('colorss.png')
	def activate(self):
		from chimera import dialogs
		dd = dialogs.display(self.module().ColorSSDialog.name)
		return None

chimera.extension.manager.registerExtension(ColorSSEMO(__file__))

def showDialog(models):
	import ColorSS
	from chimera import dialogs
	d = dialogs.display(ColorSS.ColorSSDialog.name)
	d.configure(models=models)

import ModelPanel
ModelPanel.addButton("color by SS...", lambda models, sd=showDialog:
		sd(models), balloon=ColorSSEMO.help, defaultFrequent=False)
