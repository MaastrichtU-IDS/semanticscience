# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v4.py 26655 2009-01-07 22:02:30Z gregc $

from v3 import init, beginRestore, endRestore, updateOSLmap, getOSL, \
	oslMap, registerAfterModelsCB, reportRestoreError, makeAfterModelsCBs, \
	findFile, oslLookup, restoreSurfaces, getColor, restoreMiscAttrs, \
	restoreColors, restoreWindowSize, restoreOpenStates, restoreLabels, \
	restoreVdw, restoreDrawModes, restoreDispChanged, \
	weedOSLlist, weedOSLdict, restoreSelections, restorePseudoBondGroups, \
	restoreOpenModelsAttrs, restoreCamera, RemapDialog
import chimera
from chimera import PDBio
import v1

def makeOslMappings(srcMolMap):
	from tempfile import mktemp
	import os
	pdbio = PDBio()
	for idInfo, fileContents in srcMolMap.items():
		fname = mktemp()
		f = file(fname, "w")
		f.write(fileContents)
		f.close() # force a flush
		mid, subid, name = idInfo
		mols = chimera.openModels.open(fname, type="PDB", baseId=mid,
			subid=subid, explodeNMR=False, identifyAs=name)
		os.unlink(fname)
			
		for m in mols:
			updateOSLmap(m.oslIdent(), m.oslIdent())

		# prepopulate osl lookup map
		for m in mols:
			for r in m.residues:
				v1._oslItemMap[r.oslIdent()] = r
			for a in m.atoms:
				v1._oslItemMap[a.oslIdent()] = a

