# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ChimeraExtension.py 28856 2009-09-24 21:08:06Z pett $

import chimera.extension

class Match2AlignEMO(chimera.extension.EMO):
	def name(self):
		return 'Match -> Align'
	def description(self):
		return 'sequence alignment from structural match'
	def categories(self):
		return ['Structure Comparison', 'Sequence']
	def activate(self):
		self.module().Match2Align()
		return None

emo = Match2AlignEMO(__file__)
chimera.extension.manager.registerExtension(emo)
