# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class MinrmsPlotEMO(chimera.extension.EMO):
	def __init__(self, path):
		chimera.extension.EMO.__init__(self, path)
	def name(self):
		return "Minrms Plot"
	def description(self):
		return "display output of Minrms structure alignment run"
	def categories(self):
		return ["Structure Comparison"]
	def activate(self):
		self.module("base").run(self.name())
		return None

emo = MinrmsPlotEMO(__file__)
chimera.extension.manager.registerExtension(emo)
