import os
import os.path

import chimera.extension

class BlastEMO(chimera.extension.EMO):

	def name(self):
		return "Blast Protein"
	def description(self):
		return "find similar protein sequences using BLAST"
	def categories(self):
		return ["Sequence"]
	def activate(self):
		from chimera.dialogs import display
		display(self.module("gui").BlastChainDialog.name)

	def cmdLine(self, cmdName, args):
		self.module("cmdline").run(cmdName, args)
	def modelPanel(self, molecules):
		self.module("gui").run(molecules[0])

emo = BlastEMO(__file__)
chimera.extension.manager.registerExtension(emo)

from Midas.midas_text import addCommand
addCommand("blast", emo.cmdLine, help=True, changesDisplay=False)
addCommand("psiblast", emo.cmdLine, help=True, changesDisplay=False)
