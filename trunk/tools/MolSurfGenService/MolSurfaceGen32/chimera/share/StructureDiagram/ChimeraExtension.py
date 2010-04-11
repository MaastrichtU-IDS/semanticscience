# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class StructureDiagramEMO(chimera.extension.EMO):
	def name(self):
		return "Structure Diagram"
	def description(self):
		return "Show 2D structure diagram"
	def categories(self):
		return ["Utilities"]
	def icon(self):
		return self.path("SDicon.png")
	def activate(self):
		from chimera.dialogs import display
		display(self.module("gui").StructureDiagramDialog.name)
		return None
	def cmdLine(self, cmdName, args):
		self.module("cmdline").run(cmdName, args)
	def modelPanelCB(self, molecules):
		self.module("modelpanel").callback(molecules)

emo = StructureDiagramEMO(__file__)

# Don't register if no GUI
chimera.extension.manager.registerExtension(emo)

# Don't add if no Model Panel button
import ModelPanel
ModelPanel.addButton("2D Diagram", emo.modelPanelCB,
			moleculesOnly=True,
			defaultFrequent=False,
			balloon="draw molecules in 2D")

# Don't register if no command line (Shame on you!)
from Midas.midas_text import addCommand
addCommand("struct2d", emo.cmdLine, help=True, changesDisplay=False)
