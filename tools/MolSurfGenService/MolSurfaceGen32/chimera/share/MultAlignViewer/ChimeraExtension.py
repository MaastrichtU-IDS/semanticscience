# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class MultAlignViewerEMO(chimera.extension.EMO):
	def name(self):
		return 'Multalign Viewer'
	def description(self):
		return 'display/manipulate multiple sequence alignment'
	def categories(self):
		return ['Sequence']
	def icon(self):
		return self.path('mav.png')
	def activate(self):
		self.module('startup').startExtension()
		return None
	def open(self, fileName, fileType):
		self.module('MAViewer').MAViewer(fileName, fileType)
		return []

emo =MultAlignViewerEMO(__file__)
chimera.extension.manager.registerExtension(emo)
from parse import prefixes, extensions
for fileType in prefixes.keys():
	chimera.fileInfo.register(fileType,
			lambda fn, e=emo, ft=fileType: e.open(fn, ft),
			extensions[fileType], prefixes[fileType],
			category=chimera.FileInfo.SEQUENCE)
del prefixes, extensions, fileType
