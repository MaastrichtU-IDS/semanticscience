# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v7.py 29038 2009-10-13 18:45:06Z pett $

from v1 import reportRestoreError, restoreWindowSize, \
					restoreOpenModelsAttrs, RemapDialog

ATOM, BOND, PSEUDOBOND, RESIDUE, MOLECULE, SURFACE = range(6)

import globals # so that various version files can easily access same variables
import chimera
from chimera import selection, replyobj
from chimera.misc import getPseudoBondGroup

def init(ci):
	import setup # register "session PDB" file type
	globals.colorMap = {}
	globals.colorInfo = ci
	globals.dirRemappings = {}
	globals.afterModelsCBs = []
	globals.atomIDs = {}
	globals.missedBonds = []
	globals.madeBonds = {}
	globals.madeMols = {}

def beginRestore():
	# temporarily make these names available in the SimpleSession module
	import SimpleSession
	SimpleSession.registerAfterModelsCB = registerAfterModelsCB
	SimpleSession.reportRestoreError = reportRestoreError
	SimpleSession.findFile = findFile
	SimpleSession.getColor = getColor
	SimpleSession.idLookup = idLookup
	SimpleSession.modelMap = {}
	from SimpleSession.versions import highestOpenID
	SimpleSession.modelOffset = highestOpenID() + 1
	from chimera import openModels
	SimpleSession.preexistingModels = openModels.list()
	SimpleSession.mergedSession = (len(SimpleSession.preexistingModels) > 0)

def endRestore():
	import SimpleSession
	del SimpleSession.registerAfterModelsCB
	del SimpleSession.reportRestoreError
	del SimpleSession.findFile
	del SimpleSession.getColor
	del SimpleSession.idLookup
	del SimpleSession.modelMap
	del SimpleSession.modelOffset
	del globals.colorMap
	del globals.colorInfo
	del globals.atomIDs
	del globals.missedBonds
	del globals.madeMols
	del globals.madeBonds

def sessionID(item):
	if isinstance(item, chimera.Atom):
		return (ATOM, id(item))
	if isinstance(item, chimera.Bond):
		return (BOND, (id(item.atoms[0]), id(item.atoms[1])))
	if isinstance(item, chimera.Residue):
		return (RESIDUE, id(item.atoms[0]))
	if isinstance(item, chimera.PseudoBond):
		return (PSEUDOBOND,
			(category, (id(item.atoms[0]), id(item.atoms[1]))))
	if isinstance(item, chimera.Molecule):
		return (MOLECULE, id(item.atoms[0]))
	if isinstance(item, chimera.MSMSModel):
		return (SURFACE, id(item.molecule.atoms[0]))
	raise ValueError, \
		"Non-molecular item given to sessionID(): %s" % (item,)

def registerAfterModelsCB(cb, data=None):
	globals.afterModelsCBs.append((cb, data))

def makeAfterModelsCBs():
	for cb, data in globals.afterModelsCBs:
		try:
			if data is not None:
				cb(data)
			else:
				cb()
		except:
			replyobj.reportException(
					"Error in after-models callback")

def findFile(filename):
	for origDir, newDir in globals.dirRemappings.items():
		if not filename.startswith(origDir):
			continue
		remappedFile = newDir + filename[len(origDir):]
		if os.path.exists(remappedFile):
			return remappedFile
	rd = RemapDialog(filename)
	while 1:
		val = rd.run(chimera.tkgui.app)
		if val is None:
			raise LookupError, "Cancel restore"
		if val == -1:
			return None
		remapDir = val[0][0]
		origDir, fname = os.path.split(filename)
		remappedFile = os.path.join(remapDir, fname)
		if os.path.exists(remappedFile):
			globals.dirRemappings[origDir] = remapDir
			return remappedFile
		replyobj.error("Did not find '%s' in %s\n" % (fname, remapDir))

def idLookup(sessionID):
	idType, info = sessionID
	from globals import atomIDs
	if idType == ATOM:
		return atomIDs[info]
	if idType == BOND:
		b =  atomIDs[info[0]].findBond(atomIDs[info[1]])
		if not b:
			a1, a2 = atomIDs[info[0]], atomIDs[info[1]]
			b = a1.molecule.newBond(a1, a2)
			globals.missedBonds.append(b)
		globals.madeBonds[b] = True
		globals.madeMols[b.atoms[0].molecule] += 1
		return b
	if idType == RESIDUE:
		return atomIDs[info].residue
	if idType == PSEUDOBOND:
		category, atoms = info
		return atomIDs[atoms[0]].associations(category,
							atomIDs[atoms[1]])
	if idType == MOLECULE:
		m = atomIDs[info].molecule
		globals.madeMols[m] = 0
		return m
	if idType == SURFACE:
		mol = atomIDs[info].molecule
		from SimpleSession import modelMap
		return filter(lambda m: isinstance(m, chimera.MSMSModel),
					modelMap[(mol.id, mol.subid)])[0]
	raise ValueError("Unknown sessionID: %s" % repr(sessionID))

def restoreSurfaces(surfDisplayed, surfCategories, surfDict):
	for surfDisp in surfDisplayed:
		idLookup(surfDisp).surfaceDisplay = 1
	for category, atList in surfCategories.items():
		for a in atList:
			idLookup(a).surfaceCategory = category
	for molID, attrs in surfDict.items():
		mol = idLookup(molID)
		surf = chimera.MSMSModel(mol, attrs['category'])
		del attrs['category']
		for attr, val in attrs.items():
			setattr(surf, attr, val)
		chimera.openModels.add([surf], sameAs=mol)
		from SimpleSession import modelMap
		modelMap.setdefault((mol.id, mol.subid), []).append(surf)

def getColor(colorID):
	if colorID is None:
		return None
	if globals.colorMap.has_key(colorID):
		return globals.colorMap[colorID]
	name, rgba = globals.colorInfo[colorID]
	if name:
		c = chimera.Color.lookup(name)
		if not c:
			c = chimera.MaterialColor(*rgba)
			c.save(name)
		else:
			c.ambientDiffuse = rgba[:3]
			c.opacity = rgba[3]
	else:
		c = chimera.MaterialColor(*rgba)
	globals.colorMap[colorID] = c
	return c

def restoreMiscAttrs(miscAttrs):
	for mID, attrDict in miscAttrs.items():
		m = idLookup(mID)
		for attr, val in attrDict.items():
			setattr(m, attr, val)

def restoreOpenStates(xformMap):
	for modelID, xfVals in xformMap.items():
		if len(modelID) == 3:
			from SimpleSession import modelMap
			model = modelMap[modelID[1:]][0]
		else:
			model = idLookup(modelID)
		rotInfo, transArgs, active = xfVals
		transV = apply(chimera.Vector, transArgs)
		rotArgs, angle = rotInfo
		rotV = apply(chimera.Vector, rotArgs)
		xf = chimera.Xform.translation(transV)
		apply(xf.rotate, (rotV, angle))
		model.openState.xform = xf
		model.openState.active = active

def restoreLabels(labels):
	for itemID, label in labels.items():
		item = idLookup(itemID)
		item.label = label

def restoreColors(colors, materials,
			colorUsage, vdwColors, labelColors, surfaceColors):
	# restore materials first, since colors use them
	from chimera import MaterialColor, Material, Color

	# since colors use materials, restore materials first
	for name, matInfo in materials.items():
		mat = Material.lookup(name)
		if mat is not None:
			mat.remove()
		mat = Material(name)
		specular, shininess = matInfo
		mat.specular = specular
		mat.shininess = shininess

	for name, colorInfo in colors.items():
		rgb, a, matName = colorInfo
		mat = Material.lookup(matName)
		c = Color.lookup(name)
		if c is not None:
			c.remove()
		c = MaterialColor(rgb[0], rgb[1], rgb[2], a, material=mat)
		c.save(name)

	for itemID, colorID in colorUsage.items():
		item = idLookup(itemID)
		if isinstance(item, chimera.Residue):
			item.ribbonColor = getColor(colorID)
		else:
			item.color = getColor(colorID)
	for itemID, colorID in vdwColors.items():
		idLookup(itemID).vdwColor = getColor(colorID)
	for itemID, colorID in labelColors.items():
		idLookup(itemID).labelColor = getColor(colorID)
	for itemID, colorID in surfaceColors.items():
		idLookup(itemID).surfaceColor = getColor(colorID)

def restoreVdw(vdwDisp):
	for itemID in vdwDisp:
		idLookup(itemID).vdw = 1

def restoreDrawModes(reprDict):
	from chimera import Residue
	for itemID, style in reprDict.items():
		item = idLookup(itemID)
		if isinstance(item, Residue):
			item.ribbonDrawMode = style
		else:
			item.drawMode = style

def restoreDispChanged(dispChanged):
	for dcID in dispChanged:
		dc = idLookup(dcID)
		if isinstance(dc, chimera.Residue):
			dc.ribbonDisplay = 1 - dc.ribbonDisplay
		else:
			dc.display = 1 - dc.display

def restoreSelections(curSelIds, savedSels):
	selection.setCurrent(map(idLookup, curSelIds))

	for selInfo in savedSels:
		selName, ids = selInfo
		sel = selection.ItemizedSelection()
		sel.add(map(idLookup, ids))
		chimera.selection.saveSel(selName, sel)

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
			id1, id2, bondColor, labelColor, attrs = bondInfo
			try:
				a1 = idLookup(id1)
				a2 = idLookup(id2)
			except ValueError:
				continue
			pb = grp.newPseudoBond(a1, a2)
			if bondColor:
				pb.color = getColor(bondColor)
			if labelColor:
				pb.labelColor = getColor(labelColor)
			for attr, val in attrs.items():
				setattr(pb, attr, val)

def restoreCamera(detail, fogColor, viewerBG, viewerHL,
					viewerLB, viewerAttrs, cameraAttrs):
	import chimera
	chimera.LODControl.get().quality = detail
	# globals.colorMap is deleted by end of session so look up colors now
	fogColor = getColor(fogColor)
	viewerBG = getColor(viewerBG)
	viewerHL = getColor(viewerHL)
	def delay(fogColor=fogColor, viewerBG=viewerBG, viewerHL=viewerHL,
			viewerAttrs=viewerAttrs, cameraAttrs=cameraAttrs):
		viewer = chimera.tkgui.app.viewer
		viewer.depthCueColor = fogColor
		viewer.background = viewerBG
		viewer.highlightColor = viewerHL
		import v1
		v1.fixViewerAttrs(viewerAttrs)
		for attr, val in viewerAttrs.items():
			if attr == "showBBox":
				# not strictly necessary, but cleaner
				continue
			try:
				setattr(viewer, attr, val)
			except ValueError:
				# ignore highlight errors
				if attr != 'highlight':
					raise
		camera = viewer.camera
		for attr, val in cameraAttrs.items():
			setattr(camera, attr, val)
	chimera.tkgui.app.after_idle(delay)

def restoreMolecules(srcMolMap):
	from tempfile import mktemp
	import os
        from SimpleSession import modelOffset
	for idInfo, fileContents in srcMolMap.items():
		fname = mktemp()
		f = file(fname, "w")
		f.write(fileContents)
		f.close() # force a flush
		mid, subid, name = idInfo
		mols = chimera.openModels.open(fname, type="session PDB",
                        baseId=mid+modelOffset, subid=subid, identifyAs=name)
		os.unlink(fname)
			
		if mols:
			globals.atomIDs.update(mols[0].sessionIDs)
			delattr(mols[0], 'sessionIDs')
			from SimpleSession import modelMap
			modelMap.setdefault((mid, subid), []).extend(mols)

