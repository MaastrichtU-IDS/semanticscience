# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v1.py 28989 2009-10-07 00:38:38Z goddard $

import chimera
from chimera import selection, replyobj
from chimera.misc import getPseudoBondGroup
import os.path

def init(ci):
	global _oslItemMap, _oslMap, _colorMap, _colorInfo
	global _dirRemappings, _afterModelsCBs
	_oslItemMap = {}
	_oslMap = {}
	_colorMap = {}
	_colorInfo = ci
	_dirRemappings = {}
	_afterModelsCBs = []

def beginRestore():
	# temporarily make these names available in the SimpleSession module
	import SimpleSession
	SimpleSession.updateOSLmap = updateOSLmap
	SimpleSession.registerAfterModelsCB = registerAfterModelsCB
	SimpleSession.oslMap = oslMap
	SimpleSession.reportRestoreError = reportRestoreError
	SimpleSession.findFile = findFile
	SimpleSession.oslLookup = oslLookup
	SimpleSession.getColor = getColor
	SimpleSession.weedOSLlist = weedOSLlist
	SimpleSession.weedOSLdict = weedOSLdict
	from SimpleSession.versions import highestOpenID
	SimpleSession.modelOffset = highestOpenID() + 1
	from chimera import openModels
	SimpleSession.preexistingModels = openModels.list()
	SimpleSession.mergedSession = (len(SimpleSession.preexistingModels) > 0)

def endRestore():
	import SimpleSession
	del SimpleSession.updateOSLmap
	del SimpleSession.registerAfterModelsCB
	del SimpleSession.oslMap
	del SimpleSession.reportRestoreError
	del SimpleSession.findFile
	del SimpleSession.oslLookup
	del SimpleSession.getColor
	del SimpleSession.weedOSLlist
	del SimpleSession.weedOSLdict
	del SimpleSession.modelOffset

def repairView(width, height):
	# The old and new viewing code maintain the same field of view,
	# so the adjustment is simply a scaling.
	scaleFactor = _computeScaleFactor(width, height)
	chimera.viewer.viewSize *= scaleFactor
	import Midas
	def fixPosition(p):
		l = list(p)
		l[1] = l[1] * scaleFactor
		return tuple(l)
	stack = []
	for p in Midas._positionStack:
		stack.append(fixPosition(p))
	Midas._positionStack = stack
	map = {}
	for name, p in Midas.positions.iteritems():
		map[name] = fixPosition(p)
	Midas.positions = map

def _computeScaleFactor(width, height):
	# Compute the scale factor between the old and new viewing code.
	c = chimera.viewer.camera
	# First we compute the viewing parameters using the old method.
	# This part is from the old Camera::recomputeParams
	R = ((c.windowWidth - c.eyeSeparation) / 2) / c.screenDistance
	E = c.eyeSeparation / c.windowWidth
	a = float(height) / float(width)
	if a < 1:
		ea = c.extent / a
	else:
		ea = c.extent
	d = ea
	w = ea + R * d
	# "w" is the window width at the focal plane in the
	# old scheme.  In the new scheme, this is the extent
	# at the center of view.  The required adjustment for
	# making the new view have an extent of "w", we just
	# take their ratio as the scale factor.
	return w / c.extent

def updateOSLmap(savedOSL, newOSL):
	_oslMap[savedOSL] = newOSL

def getOSL(item, start=None):
	if start is not None:
		rawOSL = item.oslIdent(start=start)
	else:
		rawOSL = item.oslIdent()
	if item.oslLevel() == selection.SelGraph:
		return rawOSL
	if isinstance(item, chimera.Atom):
		res = item.residue
		front, back = rawOSL.split('@')
		join = '@'
	elif isinstance(item, chimera.Residue):
		res = item
		front = rawOSL
		back = join = ''
	elif isinstance(item, chimera.Bond) \
	or isinstance(item, chimera.PseudoBond):
		# "smart" bond OSLs are tricky to parse...
		if rawOSL.count('#') == 2:
			secondHash = rawOSL.rindex('#')
			osl1 = rawOSL[:secondHash]
			osl2 = rawOSL[secondHash:]
		elif rawOSL.count(':') == 2:
			secondColon = rawOSL.rindex(':')
			osl1 = rawOSL[:secondColon]
			osl2 = osl1[:osl1.index(':')] + rawOSL[secondColon:]
		else:
			secondAt = rawOSL.rindex('@')
			osl1 = rawOSL[:secondAt]
			osl2 = osl1[:osl1.index('@')] + rawOSL[secondAt:]
		if item.atoms[0].oslIdent() != osl1:
			tmp = osl1
			osl = osl2
			osl2 = tmp
		front, back = osl1.split('@')
		newOSL1 = front + '/type="' + item.atoms[0].residue.type \
								+ '"@' + back
		front, back = osl2.split('@')
		newOSL2 = front + '/type="' + item.atoms[1].residue.type \
								+ '"@' + back
		if isinstance(item, chimera.PseudoBond):
			return (item.category, newOSL1 + newOSL2)
		return newOSL1 + newOSL2
	else:
		return rawOSL
	return front + '/type="' + res.type + '"' + join + back
		
def oslMap(oldOSL):
	return _oslMap[oldOSL]

def registerAfterModelsCB(cb, data=None):
	_afterModelsCBs.append((cb, data))

def reportRestoreError(msg=None):
	try:
		from chimera.replyobj import reportException
		reportException(msg)
	except:
		print "Error reporting session extension restore error!"

	
def makeAfterModelsCBs():
	for cb, data in _afterModelsCBs:
		try:
			if data is not None:
				cb(data)
			else:
				cb()
		except:
			replyobj.reportException(
					"Error in after-models callback")

def makeOslMappings(molOrder, srcMolMap):
	for xfileInfo in molOrder:
		oldOsls = srcMolMap[xfileInfo]
		filename, fileType, defaultType = xfileInfo
		prefixable = 1
		if fileType:
			prefixable = 0
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
				_oslItemMap[mapped + getOSL(r,
					start=selection.SelSubgraph)] = r
			for a in m.atoms:
				_oslItemMap[mapped + getOSL(a,
					start=selection.SelSubgraph)] = a

def findFile(filename):
	global _dirRemappings
	for origDir, newDir in _dirRemappings.items():
		if not filename.startswith(origDir):
			continue
		remappedFile = newDir + filename[len(origDir):]
		if os.path.exists(remappedFile):
			return remappedFile
	rd = RemapDialog(filename)
	#print rd.__class__.__name__
	#print rd.__class__.__bases__
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
			_dirRemappings[origDir] = remapDir
			return remappedFile
		replyobj.error("Did not find '%s' in %s\n" % (fname, remapDir))

def oslLookup(osl, bondAsAtomPair=0):
	global _oslItemMap
	if _oslItemMap.has_key(osl):
		return _oslItemMap[osl]
	if isinstance(osl, tuple): #pseudobond
		pbOsl = osl
		category, osl = pbOsl
		a1, a2 = oslLookup(osl, bondAsAtomPair=1)
		pb = a1.associations(category, a2)[0]
		_oslItemMap[pbOsl] = pb
		return pb
	if osl.count('@') == 2: #bond
		if osl.count('#') == 2:
			mol2 = osl.rindex('#')
			osl1 = osl[:mol2]
			osl2 = osl[mol2:]
		elif osl.count(':') == 2:
			res2 = osl.rindex(':')
			osl1 = osl[:res2]
			res1 = osl.index(':')
			osl2 = osl[:res1] + osl[res2:]
		else:
			at2 = osl.rindex('@')
			osl1 = osl[:at2]
			at1 = osl.index('@')
			osl2 = osl[:at1] + osl[at2:]
		a1 = oslLookup(osl1)
		a2 = oslLookup(osl2)
		if bondAsAtomPair:
			return a1, a2
		bond = a1.bondsMap[a2]
		_oslItemMap[osl] = bond
		return bond
	if ':' in osl:
		resIndex = osl.index(':')
		molOSL = osl[:resIndex]
		remainder = osl[resIndex:]
	else:
		molOSL = osl
		remainder = ""
	try:
		mappedOSL = _oslMap[molOSL] + remainder
	except KeyError:
		raise ValueError, "OSL for non-existent model"
	sel = selection.OSLSelection(mappedOSL)
	if '@' in mappedOSL:
		items = sel.atoms()
	elif ':' in mappedOSL:
		items = sel.residues()
	else:
		items = sel.molecules()
	if len(items) > 1:
		raise LookupError, "non-unique OSL"
	else:
		item = items[0]
	_oslItemMap[osl] = item
	return item

def restoreSurfaces(surfDisplayed, surfCategories, surfDict):
	for surfDisp in weedOSLlist(surfDisplayed):
		surfDisp.surfaceDisplay = 1
	for category, atList in surfCategories.items():
		for a in weedOSLlist(atList):
			a.surfaceCategory = category
	for mol, attrs in weedOSLdict(surfDict).items():
		surf = chimera.MSMSModel(mol, attrs['category'])
		del attrs['category']
		for attr, val in attrs.items():
			setattr(surf, attr, val)
		chimera.openModels.add([surf], sameAs=mol)

def getColor(colorID):
	global _colorMap
	if colorID is None:
		return None
	if _colorMap.has_key(colorID):
		return _colorMap[colorID]
	name, rgba = _colorInfo[colorID]
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
	_colorMap[colorID] = c
	return c

def restoreColors(colorUsage, vdwColors, labelColors, surfaceColors):
	for item, colorID in weedOSLdict(colorUsage).items():
		if isinstance(item, chimera.Residue):
			item.ribbonColor = getColor(colorID)
		else:
			item.color = getColor(colorID)
	for item, colorID in weedOSLdict(vdwColors).items():
		item.vdwColor = getColor(colorID)
	for item, colorID in weedOSLdict(labelColors).items():
		item.labelColor = getColor(colorID)
	for item, colorID in weedOSLdict(surfaceColors).items():
		item.surfaceColor = getColor(colorID)

def restoreWindowSize((width, height)):
	import SimpleSession
	if SimpleSession.preexistingModels:
		return	# Leave window size as is.
	import Midas
	Midas.windowsize((width, height))
	def delay(arg1, arg2, arg3, width=width, height=height):
		repairView(width, height)
		from chimera.triggerSet import ONESHOT
		return ONESHOT
	chimera.triggers.addHandler('post-frame', delay, None)

def restoreOpenStates(xformMap):
	for model, xfVals in weedOSLdict(xformMap).items():
		rotInfo, transArgs, active = xfVals
		transV = apply(chimera.Vector, transArgs)
		rotArgs, angle = rotInfo
		rotV = apply(chimera.Vector, rotArgs)
		xf = chimera.Xform.translation(transV)
		apply(xf.rotate, (rotV, angle))
		model.openState.xform = xf
		model.openState.active = active

def restoreLabels(labels):
	for item, label in weedOSLdict(labels).items():
		item.label = label

def restoreUndisplayed(undisplayed):
	for undisp in weedOSLlist(undisplayed):
		undisp.display = 0

def restoreDrawModes(reprDict):
	for item, style in weedOSLdict(reprDict).items():
		if isinstance(item, chimera.Residue):
			# ribbon repr got split into a display
			# bit and repr
			if style:
				item.ribbonDrawMode = style - 1
				item.display = 1
		else:
			item.drawMode = style

def restoreVdw(vdwDisp):
	for item in weedOSLlist(vdwDisp):
		item.vdw = 1

def restoreMiscAttrs(miscAttrs):
	for m, attrDict in weedOSLdict(miscAttrs).items():
		for attr, val in attrDict.items():
			if attr == "stickSize":
				attr = "stickScale"
				val *= 5
			elif attr == "ballFract":
				attr = "ballScale"
			setattr(m, attr, val)

def restorePseudoBondGroups(pbInfo):
	for category, groupInfo in pbInfo.items():
		modelID, attrs, bonds, grpColor = groupInfo
		grp = getPseudoBondGroup(category, modelID)
		for attr, val in attrs.items():
			if attr == "stickSize":
				attr = "stickScale"
				val *= 10
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
			_oslItemMap[getOSL(pb)] = pb
			if bondColor:
				pb.color = getColor(bondColor)
			if labelColor:
				pb.labelColor = getColor(labelColor)
			for attr, val in attrs.items():
				setattr(pb, attr, val)

def weedOSLlist(oslList):
	weeded = []
	for osl in oslList:
		try:
			weeded.append(oslLookup(osl))
		except ValueError:
			continue
	return weeded

def weedOSLdict(oslDict):
	weeded = {}
	for osl, value in oslDict.items():
		try:
			weeded[oslLookup(osl)] = value
		except ValueError:
			continue
	return weeded

def restoreSelections(curSelOsls, savedSels):
	selection.setCurrent(weedOSLlist(curSelOsls))

	for selInfo in savedSels:
		selName, osls = selInfo
		sel = selection.ItemizedSelection()
		sel.add(weedOSLlist(osls))
		chimera.selection.saveSel(selName, sel)

def restoreOpenModelsAttrs(openModelsAttrs):
	for attr, val in openModelsAttrs.items():
		setattr(chimera.openModels, attr, val)

def restoreCamera(viewerBG, viewerHL, viewerLB, viewerAttrs, cameraAttrs):
	def delay(viewerBG=viewerBG, viewerHL=viewerHL,
			viewerAttrs=viewerAttrs, cameraAttrs=cameraAttrs):
		viewer = chimera.tkgui.app.viewer
		viewer.background = getColor(viewerBG)
		viewer.highlightColor = getColor(viewerHL)
		fixViewerAttrs(viewerAttrs)
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
		if hasattr(cameraAttrs, "near"):
			# session from before nearFar attribute
			cameraAttrs["nearFar"] = (cameraAttrs["near"],
							cameraAttrs["far"])
			del cameraAttrs["near"]
			del cameraAttrs["far"]
		for attr, val in cameraAttrs.items():
			setattr(camera, attr, val)
		camera.fieldOfView = 25
	chimera.tkgui.app.after_idle(delay)

def RemapDialog(fileName):
	# chimera.nogui is not valid when this module is imported, so imbed the
	# test in a function.  Also, importing OpenSave before nogui was valid
	# would be problematic.
	if chimera.nogui:
		class _RemapDialog:
			def __init__(self, filename):
				self.filename = filename

			def run(self, over):
				print "Skipping missing file '%s'" % self.filename
				return -1

	else:
		from OpenSave import OpenModal
		class _RemapDialog(OpenModal):
			
			def __init__(self, filename):
				self.filename = filename
				self.buttons = ("OK", "Skip File", "Cancel")
				OpenModal.__init__(self, clientPos='n', dirsOnly=1, multiple=0)

			def fillInUI(self, parent):
				import Tkinter
				OpenModal.fillInUI(self, parent)

				path, fname = os.path.split(self.filename)
				l = Tkinter.Label(self.clientArea, text=
					"File '%s' not found in directory '%s'\n"
					"Please indicate the directory where '%s' "
					"is now located" % (fname, path, fname))
				l.grid(row=0, column=0)

			def SkipFile(self):
				self.Cancel(-1)
	return _RemapDialog(fileName)

def fixViewerAttrs(viewerAttrs):
	va = viewerAttrs
	va.setdefault('clipping', True)
	if 'startRatio' in va and 'yonIntensity' in va:
		# Convert to depth range.
		s,y = va['startRatio'], va['yonIntensity']
		if y >= 1 or s >= 1: e = 1
		else:                e = 1 + (1-s)*y/(1-y)
		va['depthCueRange'] = (s,e)
		del va['startRatio']
		del va['yonIntensity']
