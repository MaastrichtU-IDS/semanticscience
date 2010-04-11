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
		return 'FindHBond'
	def description(self):
		return 'find hydrogen bonds'
	def categories(self):
		return ['Structure Analysis', 'Surface/Binding Analysis']
	def icon(self):
		return self.path('hbond.png')
	def activate(self):
		self.module('gui').showUI()
		return None

chimera.extension.manager.registerExtension(FindHBondEMO(__file__))

def cmdHBonds(cmdName, args):
	from Midas.midas_text import doExtensionFunc
	from FindHBond import createHBonds
	doExtensionFunc(createHBonds, args,
				specInfo=[("spec", "models", "molecules")])

def cmdUnHBonds(cmdName, args):
	from Midas.midas_text import doExtensionFunc, MidasError
	import chimera
	mgr = chimera.PseudoBondMgr.mgr()
	pbg = mgr.findPseudoBondGroup("hydrogen bonds")
	if pbg:
		chimera.openModels.close([pbg])
	else:
		raise MidasError, "No hydrogen bonds to remove"

from Midas.midas_text import addCommand
addCommand("hbonds", cmdHBonds, revFunc=cmdUnHBonds, help=True)
addCommand("findhbond", cmdHBonds, revFunc=cmdUnHBonds, help=True)
