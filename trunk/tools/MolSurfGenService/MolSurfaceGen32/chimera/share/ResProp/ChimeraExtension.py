# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class ResPropEMO(chimera.extension.EMO):
	def name(self):
		return 'ResProp'
	def description(self):
		return 'define amino acid categories'
	def categories(self):
		return ['Structure Analysis']
	def icon(self):
		return self.path('resprop.png')
	def activate(self):
		self.module().doUI()
		return None

chimera.extension.manager.registerExtension(ResPropEMO(__file__))
