# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ChimeraExtension.py 26655 2009-01-07 22:02:30Z gregc $

import chimera.extension

class ModelClipEMO(chimera.extension.EMO):
	def name(self):
		return 'Per-Model Clipping'
	def description(self):
		return 'control per-model clip planes'
	def categories(self):
		return ['Depiction']
	def activate(self):
		from chimera import dialogs
		dialogs.display(self.module().ClipDialog.name)
		return None

chimera.extension.manager.registerExtension(ModelClipEMO(__file__))

# -----------------------------------------------------------------------------
# Register mclip command.
#
from ModelClip.mclipcmd import mclip_command, unclip_command
from Midas.midas_text import addCommand
addCommand('mclip', mclip_command, unclip_command, help = True)
