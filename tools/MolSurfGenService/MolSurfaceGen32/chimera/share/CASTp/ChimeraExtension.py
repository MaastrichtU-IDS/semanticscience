# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class CastpEMO(chimera.extension.EMO):
	def name(self):
		return "CASTp"
	def description(self):
		return "Fetch CASTp database entry"
	def categories(self):
		return ["Structure Analysis"]
	def openID(self, id):
		return self.module("gui").processCastpID(id)
	def openPath(self, path):
		return self.module("gui").openCastp(path)

emo = CastpEMO(__file__)

from chimera import fileInfo, FileInfo
fileInfo.register("CASTp ID",				# name of file type
			emo.openID,			# function to call
			None,				# extensions
			['castp', 'CASTp'],		# prefixes
			category=FileInfo.STRUCTURE)	# category
fileInfo.register("CASTp",				# name of file type
			emo.openPath,			# function to call
			[".poc"],			# extensions
			[],				# prefixes
			category=FileInfo.STRUCTURE)	# category
from chimera import fetch, openModels
fetch.registerIdType("CASTp",				# name of database
			6,				# identifier length
			"1www", 			# example
			lambda id, om=openModels: om.open(id, type="CASTp ID"),
							# callback
			"sts-fw.bioengr.uic.edu/castp/",	# homepage
			"http://sts-fw.bioengr.uic.edu/castp/query.php?pdbid=%s&visual=jmol&submitid=Search")				# info url
