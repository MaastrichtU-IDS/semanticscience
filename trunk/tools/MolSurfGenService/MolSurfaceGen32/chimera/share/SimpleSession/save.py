# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: save.py 28717 2009-09-01 21:38:52Z pett $

import chimera
from chimera import replyobj, selection, SessionPDBio, version
import os
from versions.v45 import sessionID, setSessionIDparams, \
					noAutoRestore, autoRestorable
from tempfile import mktemp

SAVE_SESSION = "save session"
chimera.triggers.addTrigger(SAVE_SESSION)
BEGIN_RESTORE_SESSION = "begin restore session"
chimera.triggers.addTrigger(BEGIN_RESTORE_SESSION)
END_RESTORE_SESSION = "end restore session"
chimera.triggers.addTrigger(END_RESTORE_SESSION)

optionalAttributes = {
	chimera.Molecule: {'openedAs': True},
	chimera.Residue: {},
	chimera.Bond: {},
	chimera.Atom: {'bfactor': True, 'occupancy': True, 'charge': True,
			'anisoU': False}
}

def registerAttribute(level, attrName, hashable=True):
	optionalAttributes[level][attrName] = hashable

def sesRepr(obj):
	if type(obj) == dict:
		lines = []
		accum = []
		totLen = 0
		for k, v in obj.items():
			kvStr = "%s: %s" % (sesRepr(k), sesRepr(v))
			lastNewline = kvStr.rfind("\n")
			if lastNewline == -1:
				totLen += len(kvStr)
			else:
				totLen = len(kvStr) - lastNewline
			accum.append(kvStr)
			if totLen > 1024:
				lines.append(", ".join(accum))
				accum = []
				totLen = 0
		if accum:
			lines.append(", ".join(accum))
		return "{" + ",\n".join(lines) + "}"
	elif type(obj) in (list, tuple):
		lines = []
		accum = []
		totLen = 0
		for item in obj:
			itemStr = sesRepr(item)
			lastNewline = itemStr.rfind("\n")
			if lastNewline == -1:
				totLen += len(itemStr)
			else:
				totLen = len(itemStr) - lastNewline
			accum.append(itemStr)
			if totLen > 1024:
				lines.append(", ".join(accum))
				accum = []
				totLen = 0
		if accum:
			lines.append(", ".join(accum))
		if type(obj) == list:
			startChar = "["
			endChar = "]"
		else:
			startChar = "("
			if len(obj) == 1:
				endChar = ",)"
			else:
				endChar = ")"
		return startChar + ",\n".join(lines) + endChar
	elif type(obj) == set:
		return "set(" + sesRepr(list(obj)) + ")"
	elif type(obj) == float:
		return "%g" % obj
	return repr(obj)

def saveSession(filename):
	replyobj.status("Initializing session save...", blankAfter=0)
	from OpenSave import osOpen, tildeExpand
	fullName = tildeExpand(filename)
	try:
		outf = osOpen(fullName, "w")
	except:
		replyobj.reportException(
				"Error opening %s for writing" % filename)
		return
	try:
		from cStringIO import StringIO
	except ImportError:
		from StringIO import StringIO
	class SessionIO:
		def __init__(self, stringIO, fileName):
			self.fileName = fileName
			self.stringIO = stringIO()
		def __getattr__(self, attrName):
			return getattr(self.stringIO, attrName)
	buf = SessionIO(StringIO, fullName)

	print>> outf, "import cPickle, base64"
	print>> outf, "try:"
	print>> outf, "\tfrom SimpleSession.versions.v45 import beginRestore,\\"
	print>> outf, "\t    registerAfterModelsCB, reportRestoreError, checkVersion"
	print>> outf, "except ImportError:"
	print>> outf, "\tfrom chimera import UserError"
	print>> outf, "\traise UserError('Cannot open session that was saved in a'"
	print>> outf, "\t    ' newer version of Chimera; update your version')"
	print>> outf, "checkVersion(%s)" % repr(version.releaseNum)
	print>> outf, "import chimera"
	print>> outf, "from chimera import replyobj"
	print>> outf, "replyobj.status('Beginning session restore...', \\"
	print>> outf, "    blankAfter=0)"
	print>> outf, "beginRestore()"
	print>> outf, """
def restoreCoreModels():
\tfrom SimpleSession.versions.v45 import init, restoreViewer, \\
\t     restoreMolecules, restoreColors, restoreSurfaces, \\
\t     restoreVRML, restorePseudoBondGroups, restoreModelAssociations"""
	global _id2color, _color2id
	_id2color = {}
	_color2id = {}

	molecules = [m for m in
		chimera.openModels.list(modelTypes=[chimera.Molecule], all=True)
		if autoRestorable(m)]
	allSurfaces = chimera.openModels.list(modelTypes=[chimera.MSMSModel])
	allVrmls = [m for m in
		chimera.openModels.list(modelTypes=[chimera.VRMLModel])
		if autoRestorable(m)]

	surfaces = [s for s in allSurfaces if s.molecule]
	if surfaces != allSurfaces:
		replyobj.warning("Cannot save surfaces without associated structure.\nSurface will not be saved.\n")
	vrmls = []
	for v in allVrmls:
		source = v.openedAs[0]
		if not source.startswith('#VRML')\
		and not os.path.exists(source):
			replyobj.warning("Source file for VRML model '%s' no"
				" longer exists.\nThe model will not be"
				" saved.\n" % v.name)
		else:
			vrmls.append(v)

	atoms = []
	bonds = []
	residues = []
	for m in molecules:
		atoms.extend(m.atoms)
		bonds.extend(m.bonds)
		residues.extend(m.residues)

	mgr = chimera.PseudoBondMgr.mgr()
	pbGroups = []
	for g in mgr.pseudoBondGroups:
		if g.category.startswith("internal-chain-"):
			noAutoRestore(g)
		else:
			pbGroups.append(g)
	pseudobonds = []
	pbMap = {}
	for pbg in pbGroups:
		pbs = [pb for pb in pbg.pseudoBonds
				if autoRestorable(pb.atoms[0].molecule)
				and autoRestorable(pb.atoms[1].molecule)]
		pseudobonds.extend(pbs)
		pbMap[pbg] = pbs

	setSessionIDparams(molecules, residues, atoms, bonds, surfaces, vrmls,
							pseudobonds, pbGroups)

	replyobj.status("Gathering molecule information...", blankAfter=0)
	molInfo = {}
	molInfo['ids'] = summarizeVals([(m.id, m.subid) for m in molecules])
	molInfo['name'] = summarizeVals([m.name for m in molecules])
	molInfo['color'] = summarizeVals([colorID(m.color) for m in molecules])
	molInfo['display'] = summarizeVals([m.display for m in molecules])
	molInfo['lineWidth'] = summarizeVals([m.lineWidth for m in molecules])
	molInfo['pointSize'] = summarizeVals([m.pointSize for m in molecules])
	molInfo['stickScale'] = summarizeVals([m.stickScale for m in molecules])
	molInfo['pdbHeaders'] = [m.pdbHeaders for m in molecules]
	molInfo['surfaceOpacity'] = summarizeVals([m.surfaceOpacity
							for m in molecules])
	molInfo['ballScale'] = summarizeVals([m.ballScale for m in molecules])
	molInfo['vdwDensity'] = summarizeVals([m.vdwDensity for m in molecules])
	molInfo['autochain'] = summarizeVals([m.autochain for m in molecules])
	molInfo['ribbonHidesMainchain'] = summarizeVals([m.ribbonHidesMainchain
							for m in molecules])
	molInfo['ribbonInsideColor'] = summarizeVals([colorID(m.ribbonInsideColor)
							for m in molecules])
	molInfo['aromaticColor'] = summarizeVals([colorID(m.aromaticColor)
							for m in molecules])
	molInfo['aromaticDisplay'] = summarizeVals([m.aromaticDisplay
							for m in molecules])
	molInfo['aromaticLineType'] = summarizeVals([m.aromaticLineType
							for m in molecules])
	molInfo['aromaticMode'] = summarizeVals([m.aromaticMode
							for m in molecules])
	molInfo['hidden'] = summarizeVals([m in m.openState.hidden
							for m in molecules])
	molInfo['optional'] = saveOptionalAttrs(chimera.Molecule, molecules)
	print>> outf, "\tmolInfo =", pickled(molInfo)

	replyobj.status("Gathering residue information...", blankAfter=0)
	resInfo = {}
	resInfo['molecule'] = summarizeVals([sessionID(r.molecule)
				for r in residues], consecutiveExceptions=True)
	resInfo['name'] = summarizeVals([r.type for r in residues])
	resInfo['chain'] = summarizeVals([r.id.chainId for r in residues],
						consecutiveExceptions=True)
	resInfo['insert'] = summarizeVals([r.id.insertionCode
							for r in residues])
	resInfo['position'] = summarizeSequentialVals(
					[r.id.position for r in residues])
	resInfo['ribbonColor'] = summarizeVals([colorID(r.ribbonColor)
				for r in residues], consecutiveExceptions=True)
	resInfo['labelColor'] = summarizeVals([colorID(r.labelColor)
				for r in residues], consecutiveExceptions=True)
	resInfo['ss'] = summarizeVals([(r.isHelix, r.isStrand, r.isTurn)
				for r in residues], consecutiveExceptions=True)
	resInfo['ssId'] = summarizeVals([r.ssId for r in residues],
				consecutiveExceptions=True)
	resInfo['ribbonDrawMode'] = summarizeVals([r.ribbonDrawMode
				for r in residues], consecutiveExceptions=True)
	resInfo['ribbonDisplay'] = summarizeVals([r.ribbonDisplay
				for r in residues], consecutiveExceptions=True)
	resInfo['label'] = summarizeVals([r.label for r in residues])
	resInfo['labelOffset'] = summarizeVals([r.labelOffset for r in residues])
	resInfo['isHet'] = summarizeVals([r.isHet for r in residues],
						consecutiveExceptions=True)
	resInfo['fillDisplay'] = summarizeVals([r.fillDisplay for r in residues],
						consecutiveExceptions=True)
	resInfo['fillMode'] = summarizeVals([r.fillMode for r in residues],
						consecutiveExceptions=True)
	resInfo['optional'] = saveOptionalAttrs(chimera.Residue, residues)
	print>> outf, "\tresInfo =", pickled(resInfo)

	replyobj.status("Gathering atom information...", blankAfter=0)
	atomInfo = {}
	atomInfo['altLoc'] = summarizeVals([a.altLoc for a in atoms])
	atomInfo['residue'] = summarizeVals([sessionID(a.residue)
				for a in atoms], consecutiveExceptions=True)
	atomInfo['element'] = summarizeVals([a.element.number for a in atoms])
	atomInfo['name'] = summarizeVals([a.name for a in atoms])
	atomInfo['color'] = summarizeVals([colorID(a.color) for a in atoms])
	atomInfo['vdwColor'] = summarizeVals([colorID(a.vdwColor)
							for a in atoms])
	atomInfo['labelColor'] = summarizeVals([colorID(a.labelColor)
							for a in atoms])
	atomInfo['surfaceColor'] = summarizeVals([colorID(a.surfaceColor)
							for a in atoms])
	atomInfo['drawMode'] = summarizeVals([a.drawMode for a in atoms],
						consecutiveExceptions=True)
	atomInfo['display'] = summarizeVals([a.display for a in atoms],
						consecutiveExceptions=True)
	atomInfo['label'] = summarizeVals([a.label for a in atoms])
	atomInfo['labelOffset'] = summarizeVals([a.labelOffset for a in atoms])
	atomInfo['radius'] = summarizeVals([a.radius for a in atoms])
	atomInfo['surfaceDisplay'] = summarizeVals([a.surfaceDisplay
				for a in atoms], consecutiveExceptions=True)
	atomInfo['surfaceCategory'] = summarizeVals([a.surfaceCategory
				for a in atoms], consecutiveExceptions=True)
	atomInfo['surfaceOpacity'] = summarizeVals([a.surfaceOpacity
				for a in atoms], consecutiveExceptions=True)
	atomInfo['vdw'] = summarizeVals([a.vdw for a in atoms],
						consecutiveExceptions=True)
	atomInfo['optional'] = saveOptionalAttrs(chimera.Atom, atoms)

	# only restore explicitly-set IDATM types...
	atomInfo['idatmType'] = summarizeVals([(a.idatmIsExplicit and
						a.idatmType) for a in atoms])
	print>> outf, "\tatomInfo =", pickled(atomInfo)

	replyobj.status("Gathering bond information...", blankAfter=0)
	bondInfo = {}
	bondInfo['atoms'] = [[sessionID(a) for a in b.atoms] for b in bonds]
	bondInfo['drawMode'] = summarizeVals([b.drawMode for b in bonds],
						consecutiveExceptions=True)
	bondInfo['display'] = summarizeVals([b.display for b in bonds])
	bondInfo['label'] = summarizeVals([b.label for b in bonds])
	bondInfo['labelOffset'] = summarizeVals([b.labelOffset for b in bonds])
	bondInfo['radius'] = summarizeVals([b.radius for b in bonds])
	bondInfo['optional'] = saveOptionalAttrs(chimera.Bond, bonds)

	print>> outf, "\tbondInfo =", pickled(bondInfo)

	replyobj.status("Gathering coordinates...", blankAfter=0)
	crdInfo = {}
	for m in molecules:
		crdSets = {}
		crdInfo[sessionID(m)] = crdSets
		for key, coordSet in m.coordSets.items():
			crdSets[key] = [(sessionID(a), str(a.coord(coordSet)))
							for a in m.atoms]
			if coordSet == m.activeCoordSet:
				crdSets['active'] = key
	print>> outf, "\tcrdInfo =", pickled(crdInfo)

	replyobj.status("Gathering surface information...", blankAfter=0)
	surfInfo = {}
	surfInfo['molecule'] = [sessionID(s.molecule) for s in surfaces]
	surfInfo['name'] = [s.name for s in surfaces]
	surfInfo['customColors'] = surfColors = []
	for attrname in ('category', 'colorMode', 'density', 'drawMode',
			 'display', 'probeRadius', 'allComponents',
			 'lineWidth', 'pointSize', 'useLighting',
			 'twoSidedLighting', 'smoothLines',
			 'transparencyBlendMode', 'oneTransparentLayer'):
		values = [getattr(s, attrname) for s in surfaces]
		surfInfo[attrname] = summarizeVals(values)
	for s in surfaces:
		if s.colorMode == chimera.MSMSModel.Custom:
			surfColors.append(summarizeVals([colorID(c)
						for c in s.customColors]))
		else:
			surfColors.append(summarizeVals([]))
	print>> outf, "\tsurfInfo =", sesRepr(surfInfo)

	replyobj.status("Gathering VRML information...", blankAfter=0)
	vrmlInfo = {}
	vrmlInfo['id'] = summarizeVals([v.id for v in vrmls])
	vrmlInfo['subid'] = summarizeVals([v.subid for v in vrmls])
	vrmlInfo['name'] = summarizeVals([v.name for v in vrmls])
	vrmlInfo['display'] = summarizeVals([v.display for v in vrmls])
	vrmlInfo['vrmlString'] = vrmlStrings = []
	for v in vrmls:
		source = v.openedAs[0]
		if source.startswith('#VRML'):
			vrmlStrings.append(source)
		else:
			# source is file name
			vrmlFile = open(source, 'r')
			vrmlStrings.append(vrmlFile.read())
			vrmlFile.close()
	print>> outf, "\tvrmlInfo =", sesRepr(vrmlInfo)

	replyobj.status("Gathering color information...", blankAfter=0)
	# remember all saved colors/materials...
	knownColors = {}
	knownMaterials = {}
	from chimera import _savedColors, _savedMaterials
	for name, material in _savedMaterials.items():
		knownMaterials[name] = (
			material.specular,
			material.shininess
		)
	for name, color in _savedColors.items():
		if not isinstance(color, chimera.MaterialColor):
			continue
		matName = color.material.name()
		if matName is None: # unnamed material
			matName = "mat" + str(id(color.material))
		knownColors[name] = (
			color.ambientDiffuse,
			color.opacity,
			matName
		)
		if matName not in knownMaterials:
			mat = color.material
			knownMaterials[matName] = (
				mat.specular,
				mat.shininess
			)
	print>> outf, "\tcolors =", sesRepr(knownColors)
	print>> outf, "\tmaterials =", sesRepr(knownMaterials)

	replyobj.status("Gathering pseudobond information...", blankAfter=0)
	pbInfo = {}
	pbInfo['category'] = [g.category for g in pbGroups]
	pbInfo['id'] = [g.id for g in pbGroups]
	pbInfo['color'] = summarizeVals([colorID(g.color) for g in pbGroups])
	pbInfo['showStubBonds'] = summarizeVals([g.showStubBonds
							for g in pbGroups])
	pbInfo['lineWidth'] = summarizeVals([g.lineWidth for g in pbGroups])
	pbInfo['stickScale'] = summarizeVals([g.stickScale for g in pbGroups])
	pbInfo['lineType'] = summarizeVals([g.lineType for g in pbGroups])
	pbInfo['bondInfo'] = pbBondInfos = []
	for g in pbGroups:
		pbs = pbMap[g]
		info = {}
		pbBondInfos.append(info)
		info['atoms'] = [[sessionID(a) for a in pb.atoms] for pb in pbs]
		info['drawMode'] = summarizeVals([pb.drawMode for pb in pbs])
		info['display'] = summarizeVals([pb.display for pb in pbs])
		info['halfbond'] = summarizeVals([pb.halfbond for pb in pbs])
		info['label'] = summarizeVals([pb.label for pb in pbs])
		info['color'] = summarizeVals([colorID(pb.color) for pb in pbs])
		info['labelColor'] = summarizeVals([colorID(pb.labelColor)
								for pb in pbs])
	print>> outf, "\tpbInfo =", sesRepr(pbInfo)

	associations = {}
	for m in molecules + surfaces + vrmls + pbGroups:
		ams = []
		for am in m.associatedModels():
			if autoRestorable(am):
				ams.append(sessionID(am))
		if ams:
			associations[sessionID(m)] = ams
	print>> outf, "\tmodelAssociations =", sesRepr(associations)

	replyobj.status("Gathering font information...", blankAfter=0)
	from chimera.bgprefs import BACKGROUND, LABEL_FONT
	from chimera import preferences
	fontInfo = {
		'face': preferences.getOption(BACKGROUND, LABEL_FONT).get()
	}

	replyobj.status("Gathering clip plane information...", blankAfter=0)
	clipPlaneInfo = {}
	for m in molecules + surfaces:
		if m.useClipPlane:
			pl = m.clipPlane
			clipPlaneInfo[sessionID(m)] = (
				pl.origin.data(),
				pl.normal.data(),
				m.useClipThickness,
				m.clipThickness
			)

	replyobj.status("Gathering selection information...", blankAfter=0)
	curSelIds = []
	curSel = selection.copyCurrent()
	selMols = curSel.molecules()
	badMols = filter(lambda m: not autoRestorable(m), selMols)
	if badMols:
		curSel.remove(badMols)
	for a in curSel.atoms():
		curSelIds.append(sessionID(a))
	for b in curSel.bonds():
		curSelIds.append(sessionID(b))

	savedSels = []
	from copy import copy
	for selName, sel in selection.savedSels.items():
		badMols = [m for m in sel.molecules() if not autoRestorable(m)]
		filtSel = copy(sel)
		if badMols:
			filtSel.remove(badMols)
		ids = []
		for a in filtSel.atoms():
			ids.append(sessionID(a))
		for b in filtSel.bonds():
			ids.append(sessionID(b))
		savedSels.append((selName, ids))

	replyobj.status("Gathering transformation information...", blankAfter=0)
	xfDict = {}
	for m in (molecules + vrmls):
		xf = m.openState.xform
		rotV, angle = xf.getRotation()
		rot = tuple([float(v) for v in str(rotV).split()])
		trans = tuple([float(v)
				for v in str(xf.getTranslation()).split()])
		xfDict[sessionID(m)] = ((rot, angle), trans, m.openState.active)

	replyobj.status("Gathering view information...", blankAfter=0)
	viewer = chimera.viewer
	camera = viewer.camera

	viewerAttrs = {}
	for va in ("viewSize", "scaleFactor", "clipping", "highlight",
		   "depthCue", "depthCueRange", "showSilhouette",
		   "silhouetteColor", "silhouetteWidth"):
		if va.endswith("Color"):
			viewerAttrs[va] = colorID(getattr(viewer, va))
		else:
			viewerAttrs[va] = getattr(viewer, va)
	cameraAttrs = {}
	for ca in ("ortho", "nearFar", "focal", "center", "fieldOfView",
							"eyeSeparation"):
		cameraAttrs[ca] = getattr(camera, ca)

	viewerInfo = {
		"detail": chimera.LODControl.get().quality,
		"viewerFog": colorID(viewer.depthCueColor),
		"viewerBG": colorID(viewer.background),
		"viewerHL": colorID(viewer.highlightColor),
		"viewerAttrs": viewerAttrs,
		"cameraAttrs": cameraAttrs,
		"cameraMode": camera.mode(),
		}
		
	# start printing into buffer so that color map can be inserted here
	replyobj.status("Writing preliminary session info...", blankAfter=0)
	print>> buf, "\tviewerInfo =", sesRepr(viewerInfo)
	print>> buf, """
\treplyobj.status("Initializing session restore...", blankAfter=0)
\tinit(colorInfo)
\treplyobj.status("Restoring colors...", blankAfter=0)
\trestoreColors(colors, materials)
\treplyobj.status("Restoring molecules...", blankAfter=0)
\trestoreMolecules(molInfo, resInfo, atomInfo, bondInfo, crdInfo)
\treplyobj.status("Restoring surfaces...", blankAfter=0)
\trestoreSurfaces(surfInfo)
\treplyobj.status("Restoring VRML models...", blankAfter=0)
\trestoreVRML(vrmlInfo)
\treplyobj.status("Restoring pseudobond groups...", blankAfter=0)
\trestorePseudoBondGroups(pbInfo)
\treplyobj.status("Restoring model associations...", blankAfter=0)
\trestoreModelAssociations(modelAssociations)
\treplyobj.status("Restoring camera...", blankAfter=0)
\trestoreViewer(viewerInfo)

try:
	restoreCoreModels()
except:
	reportRestoreError("Error restoring core models")

\treplyobj.status("Restoring extension info...", blankAfter=0)
"""
	replyobj.status("Writing extension session info...", blankAfter=0)
	chimera.triggers.activateTrigger(SAVE_SESSION, buf)
	replyobj.status("Writing remaining session info...", blankAfter=0)
	print>> buf, """
def restoreRemainder():
\tfrom SimpleSession.versions.v45 import restoreWindowSize, \\
\t     restoreOpenStates, restoreSelections, restoreFontInfo, \\
\t     restoreOpenModelsAttrs, restoreModelClip
"""
	# any use of colors below have to have those colors also run through
	# colorID() before init() gets printed, so that the color map contains
	# those colors
	print>> buf, "\tcurSelIds = ", sesRepr(curSelIds)
	print>> buf, "\tsavedSels =", sesRepr(savedSels)
	print>> buf, "\topenModelsAttrs = { 'cofrMethod': %d }" % (
					chimera.openModels.cofrMethod)
	if chimera.openModels.cofrMethod == chimera.openModels.Fixed:
		cofr = chimera.openModels.cofr
		print>> buf, "\tfrom chimera import Point"
		print>> buf, "\topenModelsAttrs['cofr'] = Point(%g, %g, %g)" \
						% (cofr.x, cofr.y, cofr.z)
	print>> buf, "\twindowSize =", sesRepr(chimera.viewer.windowSize)
	print>> buf, "\txformMap =", sesRepr(xfDict)
	print>> buf, "\tfontInfo =", sesRepr(fontInfo)
	print>> buf, "\tclipPlaneInfo =", sesRepr(clipPlaneInfo)
	print>> buf, """
\treplyobj.status("Restoring window...", blankAfter=0)
\trestoreWindowSize(windowSize)
\treplyobj.status("Restoring open states...", blankAfter=0)
\trestoreOpenStates(xformMap)
\treplyobj.status("Restoring font info...", blankAfter=0)
\trestoreFontInfo(fontInfo)
\treplyobj.status("Restoring selections...", blankAfter=0)
\trestoreSelections(curSelIds, savedSels)
\treplyobj.status("Restoring openModel attributes...", blankAfter=0)
\trestoreOpenModelsAttrs(openModelsAttrs)
\treplyobj.status("Restoring model clipping...", blankAfter=0)
\trestoreModelClip(clipPlaneInfo)

\treplyobj.status("Restoring remaining extension info...", blankAfter=0)
try:
	restoreRemainder()
except:
	reportRestoreError("Error restoring post-model state")
from SimpleSession.versions.v45 import makeAfterModelsCBs
makeAfterModelsCBs()
"""
	print>> buf, "from SimpleSession.versions.v45 import endRestore"
	print>> buf, "replyobj.status('Finishing restore...', blankAfter=0)"
	print>> buf, "endRestore()"

	print>> buf, "replyobj.status('Restore finished.')"

	# insert color map
	print>> outf, "\tcolorInfo =", sesRepr(_id2color)

	# print buffered output
	print>> outf, buf.getvalue()
	buf.close()
	outf.close()
	from versions import globals
	del globals.sessionMap
	_id2color = _color2id = None
	replyobj.status("Session written")

def colorID(color):
	if color is None:
		return None
	try:
		return _color2id[color]
	except KeyError:
		pass
	key = len(_color2id)
	_color2id[color] = key
	_id2color[key] = (color.name(), color.rgba())
	return key

def summarizeVals(vals, consecutiveExceptions=False, hashable=True):
	if not hashable:
		if vals.count(None) == len(vals):
			return len(vals), None, []
		return len(vals), None, [repr(v) for v in vals]
	sorted = {}
	for i, val in enumerate(vals):
		sorted.setdefault(val, []).append(i)
	mostCount = None
	for val, indices in sorted.items():
		if mostCount is None or len(indices) > mostCount:
			mostVal = val
			mostCount = len(indices)
	if mostCount is None:
		return len(vals), None, {}
	del sorted[mostVal]
	if consecutiveExceptions:
		for k, v in sorted.items():
			sorted[k] = (None, summarizeSequentialVals(v))
	return len(vals), mostVal, sorted

def summarizeSequentialVals(vals):
	summary = []
	startVal = prevVal = None
	for v in vals:
		if startVal == None:
			startVal = prevVal = v
			continue
		if v == prevVal + 1:
			prevVal = v
		else:
			summary.append((startVal, prevVal - startVal + 1))
			startVal = prevVal = v
	if startVal != None:
		summary.append((startVal, prevVal - startVal + 1))
	return summary

def saveOptionalAttrs(level, items):
	saveDict = {}
	for optAttr, hashable in optionalAttributes[level].items():
		vals = [getattr(i, optAttr, None) for i in items]
		sv = summarizeVals(vals, hashable=hashable)
		if sv[1] is None and not sv[2]:
			continue
		saveDict[optAttr] = (hashable, sv)
	return saveDict

def pickled(data):
	import cPickle, base64
	pData = cPickle.dumps(data, protocol=2)
	peData = base64.b64encode(pData)
	return "cPickle.loads(base64.b64decode(%s))" % repr(peData)
