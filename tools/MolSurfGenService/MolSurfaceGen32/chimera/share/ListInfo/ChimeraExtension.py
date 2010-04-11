# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class ListInfoEMO(chimera.extension.EMO):
	def name(self):
		return 'ListInfo'
	def description(self):
		return 'list information about models'
	def categories(self):
		return ['Utilities']
	def command(self, cmdName, args):
		self.module("cmdline").process(cmdName, args)

emo = ListInfoEMO(__file__)

from Midas.midas_text import addCommand
addCommand("listmodels", emo.command, help=True, changesDisplay=False)
addCommand("listchains", emo.command, help=True, changesDisplay=False)
addCommand("listresidues", emo.command, help=True, changesDisplay=False)
addCommand("listatoms", emo.command, help=True, changesDisplay=False)
addCommand("listselection", emo.command, help=True, changesDisplay=False)
addCommand("listen", emo.command, help=True, changesDisplay=False)
addCommand("sequence", emo.command, help=True, changesDisplay=False)
