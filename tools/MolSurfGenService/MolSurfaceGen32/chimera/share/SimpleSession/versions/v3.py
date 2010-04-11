# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v3.py 26655 2009-01-07 22:02:30Z gregc $

from v2 import init, beginRestore, endRestore, updateOSLmap, getOSL, \
	oslMap, registerAfterModelsCB, reportRestoreError, makeAfterModelsCBs, \
	findFile, oslLookup, restoreSurfaces, getColor, \
	restoreColors, restoreWindowSize, restoreOpenStates, restoreLabels, \
	restoreVdw, restoreDrawModes, restoreDispChanged, \
	weedOSLlist, weedOSLdict, restoreSelections, \
	restoreOpenModelsAttrs, restoreCamera, RemapDialog
import chimera
from chimera import selection
from chimera.misc import getPseudoBondGroup
import v1

# both these funcs from the previous would work, but be slower due to
# attribute remapping
def restoreMiscAttrs(miscAttrs):
	for m, attrDict in weedOSLdict(miscAttrs).items():
		for attr, val in attrDict.items():
			setattr(m, attr, val)

def restorePseudoBondGroups(pbInfo):
	for category, groupInfo in pbInfo.items():
		modelID, attrs, bonds, grpColor = groupInfo
		grp = getPseudoBondGroup(category, modelID)
		for attr, val in attrs.items():
			if attr == "wireStipple":
				if val[0]:
					grp.lineType = chimera.Dash
				continue
			setattr(grp, attr, val)
		grp.color = getColor(grpColor)
		for bondInfo in bonds:
			osl1, osl2, bondColor, labelColor, attrs = bondInfo
			try:
				a1 = oslLookup(osl1)
				a2 = oslLookup(osl2)
			except ValueError:
				continue
			pb = grp.newPseudoBond(a1, a2)
			v1._oslItemMap[getOSL(pb)] = pb
			if bondColor:
				pb.color = getColor(bondColor)
			if labelColor:
				pb.labelColor = getColor(labelColor)
			for attr, val in attrs.items():
				setattr(pb, attr, val)

def makeOslMappings(molOrder, srcMolMap):
	for xfileInfo in molOrder:
		oldOsls = srcMolMap[xfileInfo]
		filename, fileType, defaultType, prefixable = xfileInfo
		try:
			mols = chimera.openModels.open(filename, type=fileType,
			defaultType=defaultType, prefixableType=prefixable)
		except IOError:
			remapped = findFile(filename)
			if remapped is None:
				replyobj.message("Skipping restore of %s\n"
								% filename)
				continue
			mols = chimera.openModels.open(remapped, type=fileType,
						defaultType=defaultType,
						prefixableType=prefixable)

			
		while len(mols) < len(oldOsls):
			mols += chimera.openModels.open(filename, type=fileType,
						defaultType=defaultType,
						prefixableType=prefixable)
		for m in mols:
			for r in m.residues:
				r.ribbonColor = None
			for a in m.atoms:
				a.color = None
		curOsls = [m.oslIdent() for m in mols]
		oldOsls.sort(chimera.misc.oslModelCmp)
		curOsls.sort(chimera.misc.oslModelCmp)
		for i in range(len(oldOsls)):
			updateOSLmap(oldOsls[i], curOsls[i])

		# prepopulate osl lookup map
		for m in mols:
			i = curOsls.index(m.oslIdent())
			mapped = oldOsls[i]
			for r in m.residues:
				v1._oslItemMap[mapped + getOSL(r,
					start=selection.SelSubgraph)] = r
			for a in m.atoms:
				v1._oslItemMap[mapped + getOSL(a,
					start=selection.SelSubgraph)] = a

