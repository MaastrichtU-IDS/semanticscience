# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera.extension

class TileStructuresEMO(chimera.extension.EMO):
	def name(self):
		return 'Tile Structures'
	def description(self):
		return 'display structures in tiled arrangement'
	def categories(self):
		return ['Structure Comparison', 'MD/Ensemble Analysis']
	def activate(self):
		self.module('choose').TileStructuresCB()
		return None

class EnsembleMatchEMO(chimera.extension.EMO):
	def name(self):
		return 'Ensemble Match'
	def description(self):
		return 'match conformer members of two ensembles'
	def categories(self):
		return ['Structure Comparison', 'MD/Ensemble Analysis']
	def activate(self):
		self.module('choose').EnsembleMatchCB()
		# Instance will register itself
		return None

class EnsembleClusterEMO(chimera.extension.EMO):
	def name(self):
		return 'Ensemble Cluster'
	def description(self):
		return 'cluster conformer members of an ensemble'
	def categories(self):
		return ['Structure Comparison', 'MD/Ensemble Analysis']
	def activate(self):
		self.module('choose').EnsembleClusterCB()
		# Instance will register itself
		return None

chimera.extension.manager.registerExtension(TileStructuresEMO(__file__))
chimera.extension.manager.registerExtension(EnsembleMatchEMO(__file__))
chimera.extension.manager.registerExtension(EnsembleClusterEMO(__file__))

# Register tile command.
def tile_cmd(cmdname, args):
    from EnsembleMatch import tilecommand
    tilecommand.tile_command(cmdname, args)
from Midas.midas_text import addCommand
addCommand('tile', tile_cmd, tile_cmd, help = True)
