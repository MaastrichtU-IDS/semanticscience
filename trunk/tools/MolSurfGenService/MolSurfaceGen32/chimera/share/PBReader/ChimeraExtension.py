# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class PBReaderEMO(chimera.extension.EMO):
	def name(self):
		return 'PseudoBond Reader'
	def description(self):
		return 'read pseudobonds from a file'
	def categories(self):
		return ['Depiction']
	def icon(self):
		return self.path('PBread.png')
	def activate(self):
		self.module('gui').showUI()
		return None

chimera.extension.manager.registerExtension(PBReaderEMO(__file__))
