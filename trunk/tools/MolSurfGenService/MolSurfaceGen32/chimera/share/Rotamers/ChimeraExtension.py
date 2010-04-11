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

class FindHBondEMO(chimera.extension.EMO):
	def name(self):
		return 'Rotamers'
	def description(self):
		return 'choose side-chain rotamers'
	def categories(self):
		return ['Structure Editing']
	def icon(self):
		return self.path('beanie.png')
	def activate(self):
		self.module('gui')._prd()
		return None

chimera.extension.manager.registerExtension(FindHBondEMO(__file__))

def cmdRotamers(cmdName, args):
	from Midas.midas_text import doExtensionFunc
	from Rotamers import useBestRotamers
	doExtensionFunc(useBestRotamers, args, specInfo=[
		("spec", "targets", "residues"),
		("densitySpec", "density", "models")
	])
from Midas.midas_text import addCommand
addCommand("swapaa", cmdRotamers, help=True)
