# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class FillGapsEMO(chimera.extension.EMO):
	def name(self):
		return "Fill Gaps"
	def description(self):
		return "Fill gaps with Modeller"
	def categories(self):
		return ["Structure Editing"]
	#def icon(self):
	#	?
	def activate(self):
		self.module('fillgaps').gui()
		return None

class ModelLoopsEMO(chimera.extension.EMO):
	def name(self):
		return "Model Loops"
	def description(self):
		return "Model loops with Modeller"
	def categories(self):
		return ["Structure Editing"]
	#def icon(self):
	#	?
	def activate(self):
		self.module('modelloops').gui()
		return None

#chimera.extension.manager.registerExtension(FillGapsEMO(__file__))
chimera.extension.manager.registerExtension(ModelLoopsEMO(__file__))
