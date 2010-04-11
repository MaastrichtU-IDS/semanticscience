# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class MorphEMO(chimera.extension.EMO):
	def name(self):
		return 'Morph Conformations'
	def description(self):
		return 'Interpolate among molecular conformations'
	def categories(self):
		return ['Structure Comparison']
	def icon(self):
		return self.path('morph.png')
	def activate(self):
		self.module('gui').MorphDialog()
		return None
	def cmdMorph(self, cmdName, args):
		self.module('cmdline').run(cmdName, args)

emo = MorphEMO(__file__)
chimera.extension.manager.registerExtension(emo)
from Midas.midas_text import addCommand
addCommand("morph", emo.cmdMorph, help=True)
