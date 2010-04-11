# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class IlabelEMO(chimera.extension.EMO):
	def name(self):
		return '2D Labels'
	def description(self):
		return 'annotate screen with text/arrows'
	def categories(self):
		return ['Utilities']
	def icon(self):
		return self.path('il.png')
	def activate(self):
		from chimera import dialogs
		d = dialogs.display(self.module('gui').IlabelDialog.name)
		d.notebook.selectpage(d.LABELS)
		return None

chimera.extension.manager.registerExtension(IlabelEMO(__file__))

class ColorKeyEMO(chimera.extension.EMO):
	def name(self):
		return 'Color Key'
	def description(self):
		return 'place color key'
	def categories(self):
		return ['Utilities']
	def icon(self):
		return self.path('keyIcon.png')
	def activate(self):
		from chimera import dialogs
		d = dialogs.display(self.module('gui').IlabelDialog.name)
		d.notebook.selectpage(d.COLOR_KEY)
		return None

chimera.extension.manager.registerExtension(ColorKeyEMO(__file__))

def doLabel2DCmd(cmdName, args):
    from Midas.midas_text import doExtensionFunc
    from Midas import MidasError
    import Ilabel

    try:
        doExtensionFunc(Ilabel.processLabel2DCmd, args)
    except MidasError, what:
        raise

from Midas.midas_text import addCommand
addCommand("2dlabels", doLabel2DCmd, help=True)
