# --- UCSF Chimera Copyright ---
# Copyright (c) 2004 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class NucleotideEMO(chimera.extension.EMO):
	def name(self):
		return 'Nucleotides'
	def description(self):
		return 'abstract A, C, G, T, and U'
	def categories(self):
		return ['Depiction']
	def icon(self):
		return self.path('na.png')
	def activate(self):
		self.module('gui').gui()
		return None

chimera.extension.manager.registerExtension(NucleotideEMO(__file__))

# Register nucleotides command.
def nucleotides(cmdname, args):
	from NucleicAcids.cmd import nucleotides
	nucleotides(cmdname, args)
from Midas.midas_text import addCommand
addCommand('nucleotides', nucleotides, help=True)
