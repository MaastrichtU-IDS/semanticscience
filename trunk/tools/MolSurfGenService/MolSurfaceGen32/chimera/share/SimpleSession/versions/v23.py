# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v23.py 28991 2009-10-07 00:38:42Z goddard $

from v1 import RemapDialog, reportRestoreError, restoreWindowSize, \
	restoreOpenModelsAttrs

import globals # so that various version files can easily access same variables
import chimera

from weakref import WeakKeyDictionary
_skipRestore = WeakKeyDictionary()

def noAutoRestore(mol):
	"""Don't automatically save/restore this molecule"""
	_skipRestore[mol] = True

def autoRestorable(mol):
	# 'in' doesn't seem to work for WeakKeyDictionarys
	return not _skipRestore.has_key(mol)

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
			from chimera import replyobj
			replyobj.reportException(
					"Error in after-models callback")

def restoreModelClip(clipInfo):
	for modelID, info in clipInfo.items():
		model = idLookup(modelID)
		originData, normalData, useThickness, thickness = info
		cp = model.clipPlane
		cp.origin = chimera.Point(*originData)
		cp.normal = chimera.Vector(*normalData)
		model.clipPlane = cp
		model.useClipPlane = True
		model.clipThickness = thickness
		model.useClipThickness = useThickness

def restoreSelections(curSelIds, savedSels):
	from chimera import selection
	selection.setCurrent(map(idLookup, curSelIds))

	for selInfo in savedSels:
		selName, ids = selInfo
		sel = selection.ItemizedSelection()
		sel.add(map(idLookup, ids))
		chimera.selection.saveSel(selName, sel)

def restoreCamera(detail, fogColor, viewerBG, viewerHL,
					viewerLB, viewerAttrs, cameraAttrs):
	import chimera
	chimera.LODControl.get().quality = detail
	# globals.colorMap is deleted by end of session so look up colors now
	fogColor = getColor(fogColor)
	viewerBG = getColor(viewerBG)
	viewerHL = getColor(viewerHL)
	for va, val in viewerAttrs.items():
		if va.endswith("Color"):
			viewerAttrs[va] = getColor(val)
	def delay(arg1, arg2, arg3, fogColor=fogColor, viewerBG=viewerBG,
			viewerHL=viewerHL,
			viewerAttrs=viewerAttrs, cameraAttrs=cameraAttrs):
		viewer = chimera.tkgui.app.viewer
		viewer.depthCueColor = fogColor
		viewer.background = viewerBG
		viewer.highlightColor = viewerHL
		import v1
		v1.fixViewerAttrs(viewerAttrs)
		for attr, val in viewerAttrs.items():
			try:
				setattr(viewer, attr, val)
			except ValueError:
				# ignore highlight errors
				if attr != 'highlight':
					raise
		camera = viewer.camera
		for attr, val in cameraAttrs.items():
			setattr(camera, attr, val)
		camera.fieldOfView = 25
		from chimera.triggerSet import ONESHOT
		return ONESHOT
	from SimpleSession import END_RESTORE_SESSION
	chimera.triggers.addHandler(END_RESTORE_SESSION, delay, None)

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
		from chimera import replyobj
		replyobj.error("Did not find '%s' in %s\n" % (fname, remapDir))

def setSessionIDparams(molecules, residues, atoms, bonds, surfaces, vrmls):
	# during session save, 'sessionMap' is item->index
	# during restore, index->item
	sessionMap = {}
	for i, item in enumerate(molecules+residues+atoms+bonds+surfaces+vrmls):
		sessionMap[item] = i
	globals.sessionMap = sessionMap

def sessionID(item):
	return globals.sessionMap[item]

def idLookup(sesID):
	return globals.sessionMap[sesID]

def expandSummary(summary):
	numVals, default, exceptions = summary
	vals = [default] * numVals
	for value, indices in exceptions.items():
		for i in indices:
			vals[i] = value
	return vals

def restoreMolecules(molInfo, resInfo, atomInfo, bondInfo, crdInfo):
	items = []
	sm = globals.sessionMap

	res2mol = []
	atom2mol = []
	openModelsArgs = {}
	for ids, name, cid, display, lineWidth, pointSize, stickScale, \
	pdbHeaders, surfaceOpacity, ballScale, vdwDensity, autochain, \
	ribbonHidesMainchain in zip(
				expandSummary(molInfo['ids']),
				expandSummary(molInfo['name']),
				expandSummary(molInfo['color']),
				expandSummary(molInfo['display']),
				expandSummary(molInfo['lineWidth']),
				expandSummary(molInfo['pointSize']),
				expandSummary(molInfo['stickScale']),
				molInfo['pdbHeaders'],
				expandSummary(molInfo['surfaceOpacity']),
				expandSummary(molInfo['ballScale']),
				expandSummary(molInfo['vdwDensity']),
				expandSummary(molInfo['autochain']),
				expandSummary(molInfo['ribbonHidesMainchain'])
				):
		m = chimera.Molecule()
		sm[len(items)] = m
		items.append(m)
		m.name = name
		from SimpleSession import modelMap, modelOffset
		chimera.openModels.add([m],
				baseId=ids[0]+modelOffset, subid=ids[1])
		modelMap.setdefault(ids, []).append(m)
		m.color = getColor(cid)
		m.display = display
		m.lineWidth = lineWidth
		m.pointSize = pointSize
		m.stickScale = stickScale
		m.setAllPDBHeaders(pdbHeaders)
		m.surfaceOpacity = surfaceOpacity
		m.ballScale = ballScale
		m.vdwDensity = vdwDensity
		m.autochain = autochain
		m.ribbonHidesMainchain = ribbonHidesMainchain

	for mid, name, chain, pos, insert, rcid, lcid, ss, ribbonDrawMode, \
	ribbonDisplay, label in zip(
				expandSummary(resInfo['molecule']),
				expandSummary(resInfo['name']),
				expandSummary(resInfo['chain']),
				resInfo['position'],
				expandSummary(resInfo['insert']),
				expandSummary(resInfo['ribbonColor']),
				expandSummary(resInfo['labelColor']),
				expandSummary(resInfo['ss']),
				expandSummary(resInfo['ribbonDrawMode']),
				expandSummary(resInfo['ribbonDisplay']),
				expandSummary(resInfo['label'])
				):
		m = idLookup(mid)
		r = m.newResidue(name, chain, pos, insert)
		sm[len(items)] = r
		items.append(r)
		r.ribbonColor = getColor(rcid)
		r.labelColor = getColor(lcid)
		r.isHelix, r.isStrand, r.isTurn = ss
		r.ribbonDrawMode = ribbonDrawMode
		r.ribbonDisplay = ribbonDisplay
		r.label = label

	for rid, name, element, cid, vcid, lcid, scid, drawMode, display, \
	label, surfaceDisplay, surfaceCategory, surfaceOpacity, radius, vdw, \
	bfactor, occupancy, charge in zip(
				expandSummary(atomInfo['residue']),
				expandSummary(atomInfo['name']),
				expandSummary(atomInfo['element']),
				expandSummary(atomInfo['color']),
				expandSummary(atomInfo['vdwColor']),
				expandSummary(atomInfo['labelColor']),
				expandSummary(atomInfo['surfaceColor']),
				expandSummary(atomInfo['drawMode']),
				expandSummary(atomInfo['display']),
				expandSummary(atomInfo['label']),
				expandSummary(atomInfo['surfaceDisplay']),
				expandSummary(atomInfo['surfaceCategory']),
				expandSummary(atomInfo['surfaceOpacity']),
				expandSummary(atomInfo['radius']),
				expandSummary(atomInfo['vdw']),
				expandSummary(atomInfo['bfactor']),
				expandSummary(atomInfo['occupancy']),
				expandSummary(atomInfo['charge'])
				):
		r = idLookup(rid)
		a = r.molecule.newAtom(name, chimera.Element(element))
		sm[len(items)] = a
		items.append(a)
		r.addAtom(a)
		a.color = getColor(cid)
		a.vdwColor = getColor(vcid)
		a.labelColor = getColor(lcid)
		a.surfaceColor = getColor(scid)
		a.drawMode = drawMode
		a.display = display
		a.label = label
		a.surfaceDisplay = surfaceDisplay
		a.surfaceCategory = surfaceCategory
		a.surfaceOpacity = surfaceOpacity
		a.radius = radius
		a.vdw = vdw
		if bfactor is not None:
			a.bfactor = bfactor
		if occupancy is not None:
			a.occupancy = occupancy
		if charge is not None:
			a.charge = charge

	for atoms, drawMode, display in zip(
					bondInfo['atoms'],
					expandSummary(bondInfo['drawMode']),
					expandSummary(bondInfo['display'])
					):
		a1, a2 = [idLookup(a) for a in atoms]
		b = a1.molecule.newBond(a1, a2)
		sm[len(items)] = b
		items.append(b)
		b.drawMode = drawMode
		b.display = display

	from chimera import Point
	for mid, crdSets in crdInfo.items():
		m = idLookup(mid)
		active = crdSets.pop('active')
		for key, crds in crdSets.items():
			coordSet = m.newCoordSet(key, len(crds))
			for aid, crdString in crds:
				idLookup(aid).setCoord(Point(*tuple([float(c)
					for c in crdString.split()])), coordSet)
			if key == active:
				m.activeCoordSet = coordSet

def init(ci):
	globals.colorMap = {}
	globals.colorInfo = ci
	globals.dirRemappings = {}
	globals.afterModelsCBs = []
	globals.sessionMap = {}

def beginRestore():
	# temporarily make these names available in the SimpleSession module
	import SimpleSession
	from SimpleSession import BEGIN_RESTORE_SESSION
	chimera.triggers.activateTrigger(BEGIN_RESTORE_SESSION, None)
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
	alignModels(SimpleSession.preexistingModels)
	del SimpleSession.registerAfterModelsCB
	del SimpleSession.reportRestoreError
	del SimpleSession.findFile
	del SimpleSession.getColor
	del SimpleSession.idLookup
	del SimpleSession.modelMap
        del SimpleSession.modelOffset
        del SimpleSession.preexistingModels
	del globals.colorMap
	del globals.colorInfo
	del globals.dirRemappings
	del globals.afterModelsCBs
	del globals.sessionMap
	from SimpleSession import END_RESTORE_SESSION
	chimera.triggers.activateTrigger(END_RESTORE_SESSION, None)
	del SimpleSession.mergedSession

def alignModels(preexistingModels):
	"""Transform session models so model with lowest id has the
	same transform as the preexisting model with lowest id."""
	from chimera import openModels
	pset = set(preexistingModels)
	newModels = [m for m in openModels.list() if not m in pset]
	pxf = lowestIdXform(preexistingModels)
	nxf = lowestIdXform(newModels)
	if pxf is None or nxf is None:
		return
	xf = nxf.inverse()
	xf.premultiply(pxf)
	for os in set([m.openState for m in newModels]):
		os.globalXform(xf)

def lowestIdXform(models):
	if len(models) == 0:
		return None
	m = min(models, key = lambda a: (a.id,a.subid))
	return m.openState.xform

def restoreColors(colors, materials):
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

def restoreSurfaces(surfInfo):
	sm = globals.sessionMap
	for mid, category, colorMode, density, name, drawMode, display, \
	probeRadius, customColorsSummary in zip(
					surfInfo['molecule'],
					expandSummary(surfInfo['category']),
					expandSummary(surfInfo['colorMode']),
					expandSummary(surfInfo['density']),
					surfInfo['name'],
					expandSummary(surfInfo['drawMode']),
					expandSummary(surfInfo['display']),
					expandSummary(surfInfo['probeRadius']),
					surfInfo['customColors']
					):
		mol = idLookup(mid)
		s = chimera.MSMSModel(mol, category)
		chimera.openModels.add([s], sameAs=mol)
		s.colorMode = colorMode
		s.density = density
		s.name = name
		s.drawMode = drawMode
		s.display = display
		s.probeRadius = probeRadius
		customColors = expandSummary(customColorsSummary)
		if customColors:
			if len(customColors) != len(s.triangleData()[0]):
				from chimera import replyobj
				replyobj.error("Number of surface vertices for %s (%s) differs from number of colors.\nCustom color scheme not restored\n" % (mol.oslIdent(), category))
				s.colorMode = chimera.MSMSModel.ByAtom
			else:
				s.customColors = [getColor(c)
							for c in customColors]
				# setting custom colors seems to implicitly
				# set the color mode...
				s.colorMode = colorMode
		sm[len(sm)] = s
		from SimpleSession import modelMap
		modelMap.setdefault((mol.id, mol.subid), []).append(s)

def restoreVRML(vrmlInfo):
	sm = globals.sessionMap
	for id, subid, name, display, vrmlString in zip(
					expandSummary(vrmlInfo['id']),
					expandSummary(vrmlInfo['subid']),
					expandSummary(vrmlInfo['name']),
					expandSummary(vrmlInfo['display']),
					vrmlInfo['vrmlString']
					):
		from SimpleSession import modelMap, modelOffset
		if (id, subid) in modelMap:
			model = modelMap[(id, subid)][0]
			mapId, mapSubid = model.id, model.subid
		else:
			mapId, mapSubid = id+modelOffset, subid
		if not vrmlString.startswith("#VRML"):
			# BILD object
			from Bld2VRML.bld2vrml import Environment
			env = Environment()
			for line in vrmlString.splitlines():
				env.handleLine(line)
			env.finish()
			vrmlString = env.buildVRML()
		vrmlModels = chimera.openModels.open(vrmlString, type="VRML",
				baseId=mapId, subid=mapSubid, identifyAs=name)
		for vrml in vrmlModels:
			vrml.display = display
			sm[len(sm)] = vrml
		modelMap.setdefault((id, subid), []).extend(vrmlModels)

def restorePseudoBondGroups(pbInfo):
	from chimera.misc import getPseudoBondGroup
	mgr = chimera.PseudoBondMgr.mgr()
	for category, id, color, showStubBonds, lineWidth, stickScale, \
	wireStipple, bondInfo in zip(
				pbInfo['category'],
				pbInfo['id'],
				expandSummary(pbInfo['color']),
				expandSummary(pbInfo['showStubBonds']),
				expandSummary(pbInfo['lineWidth']),
				expandSummary(pbInfo['stickScale']),
				expandSummary(pbInfo['wireStipple']),
				pbInfo['bondInfo']
				):
		g = getPseudoBondGroup(category, id)
		g.color = getColor(color)
		g.showStubBonds = showStubBonds
		g.lineWidth = lineWidth
		g.stickScale = stickScale
		if wireStipple[0]:
			g.lineType = chimera.Dash
		for atoms, drawMode, display, halfbond, label, color, \
		labelColor in zip(
					bondInfo['atoms'],
					expandSummary(bondInfo['drawMode']),
					expandSummary(bondInfo['display']),
					expandSummary(bondInfo['halfbond']),
					expandSummary(bondInfo['label']),
					expandSummary(bondInfo['color']),
					expandSummary(bondInfo['labelColor'])
					):
			a1, a2 = [idLookup(a) for a in atoms]
			pb = g.newPseudoBond(a1, a2)
			pb.drawMode = drawMode
			pb.display = display
			pb.halfbond = halfbond
			pb.label = label
			pb.color = getColor(color)
			pb.labelColor = getColor(labelColor)

def restoreOpenStates(xformMap):
	for mid, xfVals in xformMap.items():
		model = idLookup(mid)
		rotInfo, transArgs, active = xfVals
		transV = apply(chimera.Vector, transArgs)
		rotArgs, angle = rotInfo
		rotV = apply(chimera.Vector, rotArgs)
		xf = chimera.Xform.translation(transV)
		apply(xf.rotate, (rotV, angle))
		model.openState.xform = xf
		model.openState.active = active

def restoreFontInfo(fontInfo):
	from chimera.bgprefs import BACKGROUND, LABEL_FONT
	from chimera import preferences
	preferences.getOption(BACKGROUND, LABEL_FONT).set(fontInfo['face'])
