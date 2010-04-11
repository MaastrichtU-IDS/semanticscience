# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: writeSel.py 27712 2009-05-29 22:44:03Z goddard $

import chimera
import os.path

classes = [chimera.Atom, chimera.Bond, chimera.PseudoBond,
			chimera.Residue, chimera.Molecule, chimera.Model]

def writeSel(saveFile, namingStyle=None, selected=True, itemType="Residue"):
	from chimera.selection import currentAtoms, currentBonds, \
		currentEdges, currentResidues, currentMolecules, currentGraphs
	classNames = [c.__name__.lower() for c in classes]
	try:
		classIndex = classNames.index(itemType.lower())
	except ValueError:
		# might be a trailing 's'...
		classIndex = classNames.index(itemType.lower()[:-1])
		
	if selected:
		func = [currentAtoms, currentBonds, lambda : filter(
			lambda b: isinstance(b, chimera.PseudoBond),
			currentEdges()), currentResidues,
			currentMolecules, currentGraphs][classIndex]
	else:
		func = [unselAtoms, unselBonds, unselPseudobonds,
			unselResidues, unselMolecules, unselModels][classIndex]

	from chimera.misc import chimeraLabel, oslCmp
	items = map(lambda i: (i.oslIdent(), i), func())
	if items and not isinstance(items[0][1], chimera.Bond) \
	and not isinstance(items[0][1], chimera.PseudoBond):
		items.sort(oslCmp)
	if saveFile == "-":
		import sys
		f = sys.stdout
	else:
		from OpenSave import osOpen, tildeExpand
		saveFile = tildeExpand(saveFile)
		f = osOpen(saveFile, "w")
	for ident, item in items:
		print>>f, chimeraLabel(item, style=namingStyle, bondSep=" <-> ")
	if saveFile != "-":
		f.close()

def unselAtoms():
	from chimera.selection import currentAtoms
	selAtoms = currentAtoms(asDict=True)
	unsel = []
	for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
		unsel.extend(filter(lambda a: a not in selAtoms, m.atoms))
	return unsel

def unselBonds():
	from chimera.selection import currentBonds
	selBonds = currentBonds(asDict=True)
	unsel = []
	for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
		unsel.extend(filter(lambda b: b not in selBonds, m.bonds))
	return unsel

def unselPseudobonds():
	from chimera.selection import currentEdges
	selEdges = currentEdges(asDict=True)
	unsel = []
	mgr = chimera.PseudoBondMgr.mgr()
	for pbg in mgr.pseudoBondGroups:
		unsel.extend(filter(lambda pb: pb not in selEdges,
							pbg.pseudoBonds))
	return unsel

def unselResidues():
	from chimera.selection import currentResidues
	selResidues = currentResidues(asDict=True)
	unsel = []
	for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
		unsel.extend(filter(lambda r: r not in selResidues, m.residues))
	return unsel

def unselMolecules():
	from chimera.selection import currentMolecules
	selMolecules = currentMolecules(asDict=True)
	return filter(lambda m: m not in selMolecules,
		chimera.openModels.list(modelTypes=[chimera.Molecule]))

def unselModels():
	from chimera.selection import currentGraphs
	selModels = currentGraphs(asDict=True)
	return filter(lambda m: m not in selModels, chimera.openModels.list())

def midasCmd(cmdName, typedArgs):
	from Midas.midas_text import doExtensionFunc
	doExtensionFunc(writeSel, typedArgs)

from Midas.midas_text import addCommand
addCommand("writesel", midasCmd, help=True)
