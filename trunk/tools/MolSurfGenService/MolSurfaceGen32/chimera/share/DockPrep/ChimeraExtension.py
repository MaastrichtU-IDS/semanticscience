# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera

class DockPrepEMO(chimera.extension.EMO):
	def name(self):
		return 'Dock Prep'
	def description(self):
		return 'Prepare a molecule for use as UCSF DOCK input'
	def icon(self):
		return self.path('dockprep.png')
	def categories(self):
		return ['Structure Editing', 'Surface/Binding Analysis']
	def activate(self):
		import chimera.dialogs
		chimera.dialogs.display(self.module('gui').DockPrepDialog.name)
		return None

chimera.extension.manager.registerExtension(DockPrepEMO(__file__))
