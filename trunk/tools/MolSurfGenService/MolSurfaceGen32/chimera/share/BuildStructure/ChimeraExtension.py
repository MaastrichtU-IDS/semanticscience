# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ChimeraExtension.py 28000 2009-07-03 00:29:28Z pett $

import chimera.extension

class BuildStructureEMO(chimera.extension.EMO):
	def name(self):
		return 'Build Structure'
	def description(self):
		return "build/modify structures"
	def categories(self):
		return ['Structure Editing']
	def activate(self):
		from chimera import dialogs
		gui = self.module('gui')
		dlg = dialogs.display(gui.BuildStructureDialog.name)
		dlg.notebook.selectpage(gui.ADD_ATOMS)
		return None
	def openSmiles(self, smiles):
		Smiles = self.module('Smiles')
		return [Smiles.smiles2mol(smiles)]
	def openPubChem(self, pcID):
		PubChem = self.module('PubChem')
		return [PubChem.pubChem2mol(pcID)]

emo = BuildStructureEMO(__file__)
chimera.extension.manager.registerExtension(emo)

chimera.fileInfo.register("SMILES", emo.openSmiles, None,
		["smiles", "SMILES"], category=chimera.FileInfo.STRUCTURE)
chimera.fileInfo.register("PubChem", emo.openPubChem, None,
		["pubchem", "PubChem"], category=chimera.FileInfo.STRUCTURE)
from chimera import fetch, openModels
fetch.registerIdType("PubChem",				# name of database
			6,				# identifier length
			"12123", 			# example
			lambda id, om=openModels: om.open(id, type="PubChem"),
							# callback
			"pubchem.ncbi.nlm.nih.gov",	# homepage
			"http://www.ncbi.nlm.nih.gov/sites/entrez?db=pccompound&term=%s")				# info url
