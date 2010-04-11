# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class RibbonStyleEMO(chimera.extension.EMO):
	def name(self):
		return "Ribbon Style Editor"
	def description(self):
		return "change default secondary structure ribbon styles"
	def categories(self):
		return ["Depiction"]
	def activate(self):
		self.module("base").edit()
		return None

emo = RibbonStyleEMO(__file__)
chimera.extension.manager.registerExtension(emo)
