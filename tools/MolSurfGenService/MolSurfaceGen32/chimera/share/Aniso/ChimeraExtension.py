# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera

class AnisoEMO(chimera.extension.EMO):
	def name(self):
		return 'Thermal Ellipsoids'
	def description(self):
		return 'show/hide atomic displacement ellipsoids'
	def icon(self):
		return self.path('icon.png')
	def categories(self):
		return ['Structure Analysis']
	def activate(self):
		import chimera.dialogs
		chimera.dialogs.display(
				self.module('gui').AnisoDialog.name)
		return None

chimera.extension.manager.registerExtension(AnisoEMO(__file__))

def cmdAniso(cmdName, args):
	import Aniso
	from Midas.midas_text import doExtensionFunc
	doExtensionFunc(Aniso.aniso, args,
				specInfo=[("spec", "targets", "atoms")])

def cmdUnaniso(cmdName, args):
	import Aniso
	from Midas.midas_text import doExtensionFunc
	doExtensionFunc(Aniso.unaniso, args,
				specInfo=[("spec", "targets", "atoms")])

from Midas.midas_text import addCommand
addCommand("aniso", cmdAniso, revFunc=cmdUnaniso, help=True)
