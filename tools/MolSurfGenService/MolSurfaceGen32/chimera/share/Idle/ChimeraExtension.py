# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class IDLE_EMO(chimera.extension.EMO):
	def name(self):
		return 'IDLE'
	def description(self):
		return 'Python shell, code editor, and debugger'
	def categories(self):
		return ['General Controls']
	def icon(self):
		return self.path('idle_icon.gif')
	def activate(self):
		self.module().start_shell()
		return None

chimera.extension.manager.registerExtension(IDLE_EMO(__file__))
