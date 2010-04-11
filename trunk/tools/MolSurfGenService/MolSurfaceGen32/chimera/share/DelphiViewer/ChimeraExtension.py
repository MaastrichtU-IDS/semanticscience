# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
File:		ChimeraExtension.py
Date:		06.08.2000
Description:	Ties the DelPhiViewer extension, through the
		chimera.extension.EMO interface, to Chimera.

Imports:	- chimera.extension module

Classes:	DelPhiViewerEMO(chimera.extension.EMO)
	Input:	(N/A)
	Output:	- Activates the module's code.

Caveats:

Last modified:	06.12.2000 - Added header.
"""

import chimera.extension

class DelPhiControllerEMO(chimera.extension.EMO):

	def name(self):
		return 'DelPhiController'
	def description(self):
		return 'calculate and display DelPhi-calculated electropotential data'
	def categories(self):
		return ['Surface/Binding Analysis']
#	def icon(self):
#		return self.path()
	def activate(self):
		from chimera import tkgui
		self.module().run()
		return None

chimera.extension.manager.registerExtension(DelPhiControllerEMO(__file__))
