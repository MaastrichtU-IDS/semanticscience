# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class PaPEMO(chimera.extension.EMO):
	def name(self):
		return 'PipesAndPlanks'
	def description(self):
		return 'display cylinders for helices and boxes for sheets'
	def categories(self):
		return ['Depiction']
	def icon(self):
		return self.path('pap.tiff')
	def activate(self):
		self.module('choose').gui()
		return None

chimera.extension.manager.registerExtension(PaPEMO(__file__))
