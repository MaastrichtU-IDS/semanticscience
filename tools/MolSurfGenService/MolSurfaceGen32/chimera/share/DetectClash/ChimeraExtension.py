# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera

class DetectClashEMO(chimera.extension.EMO):
	def name(self):
		return 'Find Clashes/Contacts'
	def description(self):
		return 'Find steric clashes or atomic contacts'
	def icon(self):
		return self.path('dc2.png')
	def categories(self):
		return ['Structure Analysis', 'Surface/Binding Analysis']
	def activate(self):
		import chimera.dialogs
		chimera.dialogs.display(
				self.module('gui').DetectClashDialog.name)
		return None

chimera.extension.manager.registerExtension(DetectClashEMO(__file__))

def cmdDetectClash(cmdName, args):
	import DetectClash
	from Midas.midas_text import doExtensionFunc
	doExtensionFunc(DetectClash.cmdDetectClash, args,
				specInfo=[("atomSpec", "testAtoms", "atoms")])

def cmdUndetectClash(cmdName, args):
	import DetectClash
	if DetectClash._continuousID != None:
		from chimera import triggers
		triggers.deleteHandler('OpenState', DetectClash._continuousID)
		DetectClash._continuousID = None
	DetectClash.nukeGroup()

from Midas.midas_text import addCommand
addCommand("findclash", cmdDetectClash, revFunc=cmdUndetectClash, help=True)
