# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class LightingEMO(chimera.extension.EMO):
	def name(self):
		return "Lighting"
	def description(self):
		return "Manipulate lighting parameters"
	def categories(self):
		return ['Viewing Controls']
	def icon(self):
		return self.path('lighting.png')
	def activate(self):
		self.module('controller').display()
		return None

from controller import LightingController
ext = chimera.extension.manager.findExtensionPackage(LightingController.Name)
if ext is None:
	chimera.extension.manager.registerExtension(LightingEMO(__file__))
	import controller
	c = controller.singleton()
	from chimera import viewing
	viewing.addCategory(LightingController.Name, 0,
				c.create, c.update, c.map, c.unmap,
				c.save, c.restore, c.reset, None)
	chimera.registerPostGraphicsFunc(c.postGraphicsFunc)
