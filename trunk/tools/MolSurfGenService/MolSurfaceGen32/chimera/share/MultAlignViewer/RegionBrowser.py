# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: RegionBrowser.py 29484 2009-12-01 22:38:28Z pett $

from chimera.baseDialog import ModelessDialog
from chimera import replyobj
from CGLtk.color import rgba2tk
from chimera import colorTable
import Pmw
import Tkinter
import os
import chimera
from chimera import selectionOperation
from chimera.selection import ItemizedSelection, currentResidues
import operator
from MAViewer import DEL_ASSOC
from prefs import SHOW_SEL, SCF_COLOR_STRUCTURES, NEW_REGION_BORDER, \
	NEW_REGION_INTERIOR, SEL_REGION_BORDER, SEL_REGION_INTERIOR
from prefs import REGION_NAME_ELLIPSIS

SEL_REGION_NAME = "Chimera selection"

class Region(object):
	def __init__(self, regionBrowser, name=None, initBlocks=[], shown=True,
			borderRGBA=None, interiorRGBA=None, namePrefix="",
			coverGaps=False):
		self.name = name
		self.namePrefix = namePrefix
		self.regionBrowser = regionBrowser
		self.seqCanvas = self.regionBrowser.seqCanvas
		self.canvas = self.seqCanvas.mainCanvas
		self.borderRGBA = borderRGBA
		self.interiorRGBA = interiorRGBA
		self.coverGaps = coverGaps
		self.highlighted = 0

		self._items = []
		self.blocks = []
		self._shown = shown
		self.addBlocks(initBlocks)

	def addBlock(self, block):
		self.addBlocks([block])

	def addBlocks(self, blockList, makeCB=True):
		self.blocks.extend(blockList)
		if makeCB:
			self.regionBrowser._regionSizeChangedCB(self)
		if not self.shown:
			return
		kw = self._rectKw()
		for block in blockList:
			for x1, y1, x2, y2 in self.seqCanvas.bboxList(
					coverGaps=self.coverGaps, *block):
				if self._borderRGBA():
					# for some reason, tk canvas
					# rectangle borders are inside the 
					# upper left edges and outside the
					# lower right
					x1 -= 1
					y1 -= 1
				self._items.append(self.canvas.create_rectangle(
							x1, y1, x2, y2, **kw))
				if len(self._items) > 1:
					self.canvas.tag_lower(self._items[-1],
								self._items[-2])
					continue

				regions = self.regionBrowser.regions
				above = below = None
				if self in regions:
					index = regions.index(self)
					for r in regions[index+1:]:
						if r._items:
							above = r
							break
					else:
						for i in range(index-1, -1, -1):
							r = regions[i]
							if r._items:
								below = r
								break
				else:
					for r in regions:
						if r._items:
							above = r
							break
				if above:
					self.canvas.tag_raise(self._items[-1],
							above._items[0])
				elif below:
					self.canvas.tag_lower(self._items[-1],
							below._items[-1])
				else:
					self.canvas.tag_lower(self._items[-1])

	def _addLines(self, lines):
		pass

	def _borderRGBA(self):
		# account for highlighting
		if not self.borderRGBA and self.highlighted:
			return (0.0, 0.0, 0.0, 1.0)
		return self.borderRGBA

	def clear(self, makeCB=True):
		if self.blocks:
			self.blocks = []
			for item in self._items:
				self.canvas.delete(item)
			self._items = []
			if makeCB:
				self.regionBrowser._regionSizeChangedCB(self)

	def contains(self, x, y):
		items = self.canvas.find_overlapping(x, y, x, y)
		for item in items:
			if item in self._items:
				return 1
		return 0

	def dehighlight(self):
		if not self.highlighted:
			return
		self.highlighted = 0
		self.redraw()

	def _delLines(self, lines):
		blocks = self.blocks
		self.blocks = []
		for block in blocks:
			line1, line2, pos1, pos2 = block
			li1 = self.seqCanvas.leadBlock.lineIndex[line1]
			li2 = self.seqCanvas.leadBlock.lineIndex[line2]
			for nli1 in range(li1, li2+1):
				newLine1 = self.seqCanvas.leadBlock.lines[nli1]
				if newLine1 not in lines:
					break
			else:
				continue
			for nli2 in range(li2, nli1-1, -1):
				newLine2 = self.seqCanvas.leadBlock.lines[nli2]
				if newLine2 not in lines:
					break
			self.blocks.append((newLine1, newLine2, pos1, pos2))

	def destroy(self):
		for item in self._items:
			self.canvas.delete(item)
		self.blocks = []
		self.regionBrowser._regionDestroyedCB(self)

	def highlight(self):
		if self.highlighted:
			return
		self.highlighted = 1
		self.redraw()

	def lowerBelow(self, otherRegion):
		if not self._items or not otherRegion._items:
			return
		self.canvas.tag_lower(self._items[0], otherRegion._items[-1])
		for i in range(1, len(self._items)):
			self.canvas.tag_lower(self._items[i], self._items[i-1])

	def raiseAbove(self, otherRegion):
		if not self._items or not otherRegion._items:
			return
		self.canvas.tag_raise(self._items[0], otherRegion._items[0])
		for i in range(1, len(self._items)):
			self.canvas.tag_lower(self._items[i], self._items[i-1])

	def _rectKw(self):
		kw = {}
		if self.interiorRGBA:
			kw['fill'] = rgba2tk(self.interiorRGBA)
		if self._borderRGBA():
			kw['outline'] = rgba2tk(self._borderRGBA())
			if self.highlighted:
				kw['dash'] = '-'
		else:
			kw['width'] = 0
			kw['outline'] = ""
		return kw

	def redraw(self):
		for item in self._items:
			self.canvas.delete(item)
		self._items = []
		blocks = self.blocks
		self.blocks = []
		self.addBlocks(blocks, makeCB=False)

	def removeLastBlock(self, destroyIfEmpty=False, makeCB=True):
		if self.blocks:
			prevBBoxes = self.seqCanvas.bboxList(
				coverGaps=self.coverGaps, *self.blocks[-1])
			self.blocks = self.blocks[:-1]
			for item in self._items[0-len(prevBBoxes):]:
				self.canvas.delete(item)
			self._items = self._items[:0-len(prevBBoxes)]
		if destroyIfEmpty and not self.blocks:
			self.destroy()
		elif makeCB:
			self.regionBrowser._regionSizeChangedCB(self)

	def setBorderRGBA(self, rgba):
		self.borderRGBA = rgba
		# kind of complicated due to highlighting; just redraw
		self.redraw()
			
	def setCoverGaps(self, cover):
		if cover != self.coverGaps:
			self.coverGaps = cover
			self.redraw()

	def setInteriorRGBA(self, rgba):
		if rgba:
			fill = rgba2tk(rgba)
		else:
			fill = ""
		for item in self._items:
			self.canvas.itemconfigure(item, fill=fill)
		self.interiorRGBA = rgba

	def setShown(self, val):
		if val == self._shown:
			return
		self._shown = val
		self.redraw()

	def getShown(self):
		return self._shown

	shown = property(getShown, setShown)

	def __str__(self):
		if self.name:
			return self.namePrefix + self.name
		if not self.blocks:
			return self.namePrefix + "<empty>"
		line1, line2, pos1, pos2 = self.blocks[0]
		if line1 != line2:
			base = "%s..%s " % (line1.name, line2.name)
		else:
			base = line1.name + " "
		if pos1 != pos2:
			base += "[%d-%d]" % (pos1+1, pos2+1)
		else:
			base += "[%d]" % (pos1+1)

		if len(self.blocks) > 1:
			base += " + %d other block" % (len(self.blocks) - 1)
		if len(self.blocks) > 2:
			base += "s"
		return self.namePrefix + base

	def updateLastBlock(self, block):
		self.removeLastBlock(makeCB=False)
		self.addBlocks([block])

class RegionBrowser(ModelessDialog):
	buttons = ('Close',)
	help = \
	"ContributedSoftware/multalignviewer/multalignviewer.html#regionbrowser"

	def __init__(self, seqCanvas):
		self.seqCanvas = seqCanvas
		seqCanvas.mainCanvas.bind('<ButtonPress-1>', self._mouseDownCB)
		seqCanvas.mainCanvas.bind('<ButtonRelease-1>', self._mouseUpCB)
		seqCanvas.mainCanvas.bind('<B1-Motion>', self._mouseDragCB)
		seqCanvas.mainCanvas.bind('<Button-3>',
				lambda e: self._focusCB(e, pref="residue"))
		seqCanvas.mainCanvas.bind('<Shift-Button-3>',
				lambda e: self._focusCB(e, pref="region"))
		self.title = "Region Browser for " + seqCanvas.mav.title
		self._dragLines = []
		self._dragRegion = None
		self._prevDrag = None
		self._bboxes = []
		self._afterID = None
		self._highlightedRegion = None
		self.regions = []
		self.associatedRegions = {}
		self.renameDialogs = {}
		self._scfDialog = None
		ModelessDialog.__init__(self)

	def clearRegions(self, doAssocRegions=True):
		if doAssocRegions:
			for region in self.regions[:]:
				region.destroy()
			self.associatedRegions.clear()
		else:
			assocRegions = set()
			for ars in self.associatedRegions.values():
				assocRegions.update(ars)
			for region in self.regions[:]:
				if region not in assocRegions:
					region.destroy()

	def copyRegion(self, region):
		if not region:
			self.seqCanvas.mav.status("No active region",
								color="red")
			return
		if not isinstance(region, Region):
			for r in region:
				self.copyRegion(r)
			return
		copy = self.newRegion(name="Copy of " + str(region),
				blocks=region.blocks, fill=region.interiorRGBA,
				outline=region.borderRGBA,
				coverGaps=region.coverGaps)
		hlist = self.regionListing.hlist
		hlist.selection_clear()
		hlist.selection_set(self.regions.index(copy))
		self.renameRegion(copy)

	def curRegion(self):
		return self._curRegion

	def deleteRegion(self, region):
		if not region:
			self.seqCanvas.mav.status("No active region",
								color="red")
			return
		if not isinstance(region, Region):
			for r in region:
				self.deleteRegion(r)
			return
		if region == self.getRegion(SEL_REGION_NAME):
			self.seqCanvas.mav.status(
				"Cannot delete Chimera selection region",
				color="red")
		else:
			for key, assocRegions in self.associatedRegions.items():
				if region in assocRegions:
					assocRegions.remove(region)
					if not assocRegions:
						del self.associatedRegions[key]
			region.destroy()

	def destroy(self):
		self.regionListing.hlist._widgetCache.clear()
		self.seqCanvas.mav.triggers.deleteHandler(DEL_ASSOC,
							self.delAssocHandlerID)
		if hasattr(self,'_selChangeHandler') and self._selChangeHandler:
			chimera.triggers.deleteHandler("selection changed",
							self._selChangeHandler)
		if self._scfDialog:
			self._scfDialog.destroy()
			self._scfDialog = None
		for rd in self.renameDialogs.values():
			rd.destroy()
		self.renameDialogs.clear()
		ModelessDialog.destroy(self)

	def fillInUI(self, parent):
		self.Close()
		browseFrame = Tkinter.Frame(parent)
		browseFrame.grid(row=0, column=0, columnspan=3, sticky='nsew')
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)
		parent.columnconfigure(1, weight=1)
		from Tix import ScrolledHList, DisplayStyle
		self.regionListing = ScrolledHList(browseFrame, width="3i",
						options="""hlist.columns 3
						hlist.header 1
						hlist.selectMode extended
						hlist.indicator 1""")
		hlist = self.regionListing.hlist
		hlist._widgetCache = {}
		hlist.config(browsecmd=self._listingCB)
		hlist.header_create(0, itemtype="text", text="Name")
		hlist.NAME_COL = 0
		hlist.header_create(1, itemtype="text", text="Active")
		hlist.CURRENT_COL = 1
		hlist._widgetCache[hlist.CURRENT_COL] = []
		hlist.header_create(2, itemtype="text", text="Shown")
		hlist.SHOWN_COL = 2
		hlist._widgetCache[hlist.SHOWN_COL] = []
		self.textStyle = DisplayStyle("text",
						refwindow=self.regionListing)
		self._curRegion = None
		self.regionButtons = {}
		for i, butName in enumerate(('raise', 'lower', 'copy',
							'rename', 'delete')):
			self.regionButtons[butName] = Tkinter.Button(
				browseFrame, text=butName.capitalize(),
				command=lambda cmd=getattr(self,
				butName+"Region"): cmd(self.selected()), pady=0)
			self.regionButtons[butName].grid(row=1, column=i)
			browseFrame.columnconfigure(i, weight=1)
		self.regionListing.grid(row=0, column=0, columnspan=i+1,
								sticky='nsew')
		browseFrame.rowconfigure(0, weight=1)
		from chimera.tkoptions import RGBAOption, BooleanOption
		class BorderRGBA(RGBAOption):
			attribute = "borderRGBA"
		class InteriorRGBA(RGBAOption):
			attribute = "interiorRGBA"
		self.borderRGBAOption = BorderRGBA(parent, 1,
				"Border color", None, self._curBorderRGBAcb)
		self.interiorRGBAOption = InteriorRGBA(parent, 2,
				"Interior color", None, self._curInteriorRGBAcb)
		
		class CoverGapsOption(BooleanOption):
			attribute = "coverGaps"
		f = Tkinter.Frame(parent)
		f.grid(row=1, column=2, rowspan=2)
		self.coverGapsOption = CoverGapsOption(f, 1,
			"Include gaps", None, self._coverGapsCB, startCol=2)

		self._selChangeFromSelf = False
		self._firstChimeraShow = True
		if self.seqCanvas.mav.prefs[SHOW_SEL]:
			self._showSelCB()

		cb = lambda e, s=self: s.deleteRegion(s.selected())
		parent.winfo_toplevel().bind('<Delete>', cb)
		parent.winfo_toplevel().bind('<BackSpace>', cb)

		self.delAssocHandlerID = self.seqCanvas.mav.triggers.addHandler(
					DEL_ASSOC, self._delAssocCB, None)

	def getRegion(self, name, **kw):
		try:
			create = kw['create']
			del kw['create']
		except KeyError:
			create = 0
		for region in self.regions:
			if region.name == name:
				return region
		if not create:
			return None
		if 'coverGaps' not in kw:
			kw['coverGaps'] = False
		return self.newRegion(name=name, **kw)

	def highlight(self, region):
		if self._highlightedRegion:
			self._highlightedRegion.dehighlight()
		if region:
			region.highlight()
			if region != self.getRegion(SEL_REGION_NAME):
				self._selectOnStructures(region)
		self._highlightedRegion = region

	def lastDrag(self):
		return self._prevDrag

	def loadScfCB(self, okayed, dialog):
		if not okayed:
			return
		self.seqCanvas.mav.prefs[SCF_COLOR_STRUCTURES] = \
						dialog.colorStructureVar.get()

		for path in dialog.getPaths():
			self.loadScfFile(path,
				self.seqCanvas.mav.prefs[SCF_COLOR_STRUCTURES])
		
	def loadScfFile(self, path, colorStructures=True):
		if path is None:
			if not self._scfDialog:
				self._scfDialog = ScfDialog(
						self.seqCanvas.mav.prefs[
						SCF_COLOR_STRUCTURES],
						command=self.loadScfCB)
			self._scfDialog.enter()
			return

		seqs = self.seqCanvas.seqs
		from OpenSave import osOpen
		scfFile = osOpen(path)
		lineNum = 0
		regionInfo = {}
		for line in scfFile.readlines():
			lineNum += 1
			line.strip()
			if not line or line[0] == '#' \
			or line.startswith('//'):
				continue
			for commentIntro in ['//', '#']:
				commentPos = line.find(commentIntro)
				if commentPos >= 0:
					break
			if commentPos >= 0:
				comment = line[commentPos
					+ len(commentIntro):].strip()
				line = line[:commentPos].strip()
			else:
				comment = None

			try:
				pos1, pos2, seq1, seq2, r, g, b = map(
						int, line.split())
				if seq1 == -1:
					# internal to jevtrace/webmol
					continue
				if seq1 == 0:
					seq2 = -1
				else:
					seq1 -= 1
					seq2 -= 1
			except:
				try:
					pos, seq, r, g, b = map(int,
							line.split())
					pos1 = pos2 = pos
				except:
					replyobj.error("Bad format for line %d of %s [not 5 or 7 integers]\n" % (lineNum, path))
					scfFile.close()
					return
				if seq == 0:
					seq1 = 0
					seq2 = -1
				else:
					seq1 = seq2 = seq - 1
			key = ((r, g, b), comment)
			if key in regionInfo:
				regionInfo[key].append((seqs[seq1],
					seqs[seq2], pos1, pos2))
			else:
				regionInfo[key] = [(seqs[seq1],
					seqs[seq2], pos1, pos2)]
		scfFile.close()

		if not regionInfo:
			replyobj.error("No annotations found in %s\n"
				% path)
			return
		for rgbComment, blocks in regionInfo.items():
			rgb, comment = rgbComment
			rgb = map(lambda v: v/255.0, rgb)
			region = self.newRegion(namePrefix="Seqsel: ",
				blocks=blocks, name=comment, fill=rgb,
				coverGaps=True)
			if not colorStructures:
				continue
			c = chimera.MaterialColor(*rgb)
			for res in self.regionResidues(region):
				res.ribbonColor = c
				for a in res.atoms:
					a.color = c
		self.seqCanvas.mav.status("%d scf regions created\n"
						% len(regionInfo))
		
	def lowerRegion(self, region):
		if not region:
			self.seqCanvas.mav.status("No active region",
								color="red")
			return
		if not isinstance(region, Region):
			for r in region:
				self.lowerRegion(r)
			return
		selRegions = self.selected()
		index = self.regions.index(region)
		if index == len(self.regions) - 1:
			return
		self.regions.remove(region)
		self.regions.append(region)
		for higherRegion in self.regions[-2::-1]:
			if higherRegion.blocks and higherRegion.shown:
				region.lowerBelow(higherRegion)
				break
		self._rebuildListing(selRegions)

	def moveRegions(self, offset, startOffset=0, exceptBottom=None):
		if not offset:
			return
		for region in self.regions:
			blocks = region.blocks[:]
			region.clear(makeCB=False)
			newBlocks = []
			for l1, l2, p1, p2 in blocks:
				if l2 == exceptBottom:
					continue
				if p1 >= startOffset:
					p1 += offset
				if p2 >= startOffset:
					p2 += offset
				newBlocks.append([l1, l2, p1, p2])
			region.addBlocks(newBlocks, makeCB=False)

	def newRegion(self, name=None, blocks=[], fill=None, outline=None,
			namePrefix="", select=0, assocWith=None, shown=True,
			coverGaps=True, after=SEL_REGION_NAME):
		if not name and not namePrefix:
			# possibly first user-dragged region
			for reg in self.regions:
				if not reg.name and not reg.namePrefix:
					# another user region
					break
			else:
				self.seqCanvas.mav.status(
				  "Use delete/backspace key to remove regions")
		interior = self._getRGBA(fill)
		border = self._getRGBA(outline)
		region = Region(self, initBlocks=blocks, name=name,
				namePrefix=namePrefix, shown=shown,
				borderRGBA=border, interiorRGBA=interior,
				coverGaps=coverGaps)
		selRegions = self.selected()
		if isinstance(after, Region):
			insertIndex = self.regions.index(after) + 1
		elif isinstance(after, basestring):
			try:
				insertIndex = [r.name for r in self.regions
							].index(after) + 1
			except ValueError:
				insertIndex = 0
		else:
			insertIndex = 0
		self.regions.insert(insertIndex, region)
		self._rebuildListing(selRegions)
		if select:
			self._toggleCurrent(region)
		if assocWith:
			try:
				self.associatedRegions[assocWith].append(region)
			except KeyError:
				self.associatedRegions[assocWith] = [region]
		return region

	def raiseRegion(self, region):
		if not region:
			self.seqCanvas.mav.status("No active region",
								color="red")
			return
		if not isinstance(region, Region):
			for r in region[::-1]:
				self.raiseRegion(r)
			return
		selRegions = self.selected()
		index = self.regions.index(region)
		if index == 0:
			return
		self.regions.remove(region)
		self.regions.insert(0, region)
		for lowerRegion in self.regions[1:]:
			if lowerRegion.blocks and lowerRegion.shown:
				region.raiseAbove(lowerRegion)
				break
		self._rebuildListing(selRegions)

	def redrawRegions(self, justGapping=False, cullEmpty=False):
		for region in self.regions[:]:
			if justGapping and region.coverGaps:
				continue
			region.redraw()
			if cullEmpty and not region.blocks \
			and region != self.getRegion(SEL_REGION_NAME):
				region.destroy()
		self.seqCanvas.adjustScrolling()
		
	def regionResidues(self, region=None):
		if not region:
			region = self._dragRegion
			if not region:
				return []
		selResidues = []
		for block in region.blocks:
			selResidues.extend(self._residuesInBlock(block))
		return selResidues

	def renameRegion(self, region, name=None):
		if not region:
			self.seqCanvas.mav.status("No active region",
								color="red")
			return
		if not isinstance(region, Region):
			for r in region:
				self.renameRegion(r)
			return
		if region == self.getRegion(SEL_REGION_NAME):
			self.seqCanvas.mav.status(
				"Cannot rename Chimera selection region",
				color="red")
			return
		if name == SEL_REGION_NAME:
			self.seqCanvas.mav.status("Cannot rename region as '%s'"
				% SEL_REGION_NAME, color="red")
			return
		if name is not None:
			region.name = name
			self._rebuildListing(self.selected())
			if region in self.renameDialogs:
				self.renameDialogs[region].destroy()
				del self.renameDialogs[region]
			return
		if region not in self.renameDialogs:
			self.renameDialogs[region] = RenameDialog(self, region)
		self.renameDialogs[region].enter()

	def seeRegion(self, region=None):
		if not region:
			region = self.curRegion()
			if not region:
				return
		if isinstance(region, basestring):
			regionName = region
			region = self.getRegion(regionName)
			if not region:
				replyobj.error("No region named '%s'\n" %
								regionName)
				return
		
		self.seqCanvas.seeBlocks(region.blocks)

	def selected(self):
		"""Return a list of selected regions"""
		return [self.regions[int(i)]
			for i in self.regionListing.hlist.info_selection()]

	def showChimeraSelection(self):
		selRegion = self.getRegion(SEL_REGION_NAME, create=1,
			fill=self.seqCanvas.mav.prefs[SEL_REGION_INTERIOR],
			outline=self.seqCanvas.mav.prefs[SEL_REGION_BORDER])
		selRegion.clear()

		resDict = {}
		for res in currentResidues():
			resDict[res] = 1
		blocks = []
		for aseq in self.seqCanvas.seqs:
			try:
				matchMaps = aseq.matchMaps
			except AttributeError:
				continue
			for matchMap in matchMaps.values():
				start = None
				end = None
				for i in range(len(aseq.ungapped())):
					if i in matchMap \
					and matchMap[i] in resDict:
						if start is not None:
							end = i
						else:
							end = start = i
					else:
						if start is not None:
							blocks.append([aseq, 
							 aseq, aseq. \
							 ungapped2gapped(start
							 ), aseq. \
							 ungapped2gapped(end)])
							start = end = None
				if start is not None:
					blocks.append([aseq, aseq,
						aseq.ungapped2gapped(start),
						aseq.ungapped2gapped(end)])
		if blocks and self._firstChimeraShow:
			self._firstChimeraShow = False
			self.seqCanvas.mav.status(
				"Chimera selection region displayed.\n"
				"Preferences..Regions controls this display.\n")
		selRegion.addBlocks(blocks)
		self.raiseRegion(selRegion)

	def showPredictedSS(self, show):
		"""show predicted secondary structure"""
		from gor import gorI
		from chimera.Sequence import defHelixColor, defStrandColor
		helixReg = self.getRegion("predicted helices", create=1,
							outline=defHelixColor)
		strandReg = self.getRegion("predicted strands", create=1,
							outline=defStrandColor)
		helixReg.shown = show
		strandReg.shown = show
		if not show:
			return
		helixReg.clear(makeCB=False)  # callback will happen in 
		strandReg.clear(makeCB=False) # addBlocks below

		helices = []
		strands = []
		for aseq in self.seqCanvas.seqs:
			if hasattr(aseq, 'matchMaps') and aseq.matchMaps:
				# has real associated structure
				continue
			pred = gorI(aseq)
			inHelix = inStrand = 0
			for pos in range(len(pred)):
				ss = pred[pos]
				if pred[pos] == 'C':
					inHelix = inStrand = 0
					continue
				gapped = aseq.ungapped2gapped(pos)
				if ss == 'H':
					inStrand = 0
					if inHelix:
						helices[-1][-1] = gapped
					else:
						helices.append([aseq, aseq,
							gapped, gapped])
						inHelix = 1
				else:
					inHelix = 0
					if inStrand:
						strands[-1][-1] = gapped
					else:
						strands.append([aseq, aseq,
							gapped, gapped])
						inStrand = 1
		helixReg.addBlocks(helices)
		strandReg.addBlocks(strands)

	def showSS(self, show):
		"""show actual secondary structure"""
		from chimera.Sequence import defHelixColor, defStrandColor
		helixReg = self.getRegion("structure helices", create=1,
				fill=(1.0, 1.0, 0.8), outline=defHelixColor)
		strandReg = self.getRegion("structure strands", create=1,
				fill=(0.8, 1.0, 0.8), outline=defStrandColor)
		helixReg.shown = show
		strandReg.shown = show
		if not show:
			return
		helixReg.clear(makeCB=False)  # callback will happen in
		strandReg.clear(makeCB=False) # addBlocks below

		assocSeqs = {}
		helices = []
		strands = []
		for aseq in self.seqCanvas.mav.associations.values():
			assocSeqs[aseq] = 1
		for aseq in assocSeqs.keys():
			inHelix = inStrand = 0
			for pos in range(len(aseq.ungapped())):
				isHelix = isStrand = 0
				for matchMap in aseq.matchMaps.values():
					try:
						res = matchMap[pos]
					except KeyError:
						continue
					if res.isHelix:
						isHelix = 1
					elif res.isStrand:
						isStrand = 1
				gapped = aseq.ungapped2gapped(pos)
				if isHelix:
					if inHelix:
						helices[-1][-1] = gapped
					else:
						helices.append([aseq, aseq,
								gapped, gapped])
						inHelix = 1
				else:
					if inHelix:
						inHelix = 0
				if isStrand:
					if inStrand:
						strands[-1][-1] = gapped
					else:
						strands.append([aseq, aseq,
								gapped, gapped])
						inStrand = 1
				else:
					if inStrand:
						inStrand = 0
		helixReg.addBlocks(helices)
		strandReg.addBlocks(strands)
						
	def _clearDrag(self):
		if self._dragLines:
			for box in self._dragLines:
				for line in box:
					self.seqCanvas.mainCanvas.delete(line)
			self._dragLines = []
			self._bboxes = []
			if self._dragRegion:
				self._dragRegion.removeLastBlock()

	def _columnPick(self, event):
		canvas = self.seqCanvas.mainCanvas
		canvasX = canvas.canvasx(event.x)
		canvasY = canvas.canvasy(event.y)
		block = self.seqCanvas.boundedBy(canvasX, canvasY,
							canvasX, canvasY)
		if block[0] is None or block[0] in self.seqCanvas.seqs:
			return None
		return block[2]

	def _coverGapsCB(self, opt):
		for r in self.selected():
			r.setCoverGaps(opt.get())

	def _curBorderRGBAcb(self, opt):
		rgba = self._getRGBA(option=opt)
		for r in self.selected():
			r.setBorderRGBA(rgba)

	def _curInteriorRGBAcb(self, opt):
		rgba = self._getRGBA(option=opt)
		for r in self.selected():
			r.setInteriorRGBA(rgba)

	def _delAssocCB(self, trigName, myData, delMatchMaps):
		for matchMap in delMatchMaps:
			key = (matchMap['mseq'], matchMap['aseq'])
			if key in self.associatedRegions:
				for region in self.associatedRegions[key]:
					if region not in self.regions:
						continue
					region.destroy()
				del self.associatedRegions[key]
				
	def _focusCB(self, event, pref=None):
		if pref == "residue":
			funcs = [self._residueCB, self._regionResiduesCB]
		else:
			funcs = [self._regionResiduesCB, self._residueCB]

		for func in funcs:
			residues = func(event)
			if residues is None: # no residue/region 
				continue
			if not residues: # region with no structure residues
				return
			break
		if residues is None:
			return
		from Midas import cofr, window
		from chimera.selection import ItemizedSelection
		sel = ItemizedSelection()
		sel.add(residues)
		window(sel)
		cofr(sel)

	def _getRGBA(self, specified=None, option=None):
		if not specified and option:
			return option.get()
		elif isinstance(specified, basestring):
			return map(lambda v: v/255.0,
						colorTable.colors[specified])
		return specified
	
	def _listingCB(self, val=None):
		regions = self.selected()
		self.interiorRGBAOption.display(regions)
		self.borderRGBAOption.display(regions)
		self.coverGapsOption.display(regions)

	def _mouseDownCB(self, event):
		canvas = self.seqCanvas.mainCanvas
		self._startX = canvas.canvasx(event.x)
		self._startY = canvas.canvasy(event.y)
		self._canvasHeight = canvas.winfo_height()
		self._canvasWidth = canvas.winfo_width()
		self._clearDrag()

		self._dragRegion = None
		if event.state % 2 == 1:
			# shift key down
			self._dragRegion = self.curRegion()
		else:
			self._dragRegion = None

	def _mouseDragCB(self, event=None):
		if not hasattr(self, '_startX') or self._startX is None:
			return
		canvas = self.seqCanvas.mainCanvas
		if not event:
			# callback from over-edge mouse drag
			controlDown = 0
			if self._dragX < 0:
				xscroll = int(self._dragX/14) - 1
				x = 0
			elif self._dragX >= self._canvasWidth:
				xscroll = int((self._dragX - self._canvasWidth)
					/ 14) + 1
				x = self._canvasWidth
			else:
				xscroll = 0
				x = self._dragX
			if self._dragY < 0:
				yscroll = int(self._dragY/14) - 1
				y = 0
			elif self._dragY >= self._canvasHeight:
				yscroll = int((self._dragY - self._canvasHeight)
					/ 14) + 1
				y = self._canvasHeight
			else:
				yscroll = 0
				y = self._dragY
			if xscroll:
				canvas.xview_scroll(xscroll, 'units')
			if yscroll:
				canvas.yview_scroll(yscroll, 'units')
				if self.seqCanvas.labelCanvas != canvas:
					self.seqCanvas.labelCanvas.yview_scroll(yscroll, 'units')
			if xscroll or yscroll:
				self._afterID = canvas.after(100,
							self._mouseDragCB)
			else:
				self._afterID = None
		else:
			x = event.x
			y = event.y
			controlDown = event.state & 4 == 4
			if x < 0 or x >= self._canvasWidth \
			or y < 0 or y >= self._canvasHeight:
				# should scroll
				self._dragX = x
				self._dragY = y
				if self._afterID:
					# already waiting on a scroll
					return
				self._afterID = canvas.after(100,
							self._mouseDragCB)
				return
			else:
				# should not scroll
				if self._afterID:
					canvas.after_cancel(self._afterID)
					self._afterID = None
				
		canvasX = canvas.canvasx(x)
		canvasY = canvas.canvasy(y)
		if abs(canvasX - self._startX) > 1 \
		or abs(canvasY - self._startY) > 1:
			block = self.seqCanvas.boundedBy(canvasX, canvasY,
						self._startX, self._startY)
			if block[0] is None:
				self._clearDrag()
				return
			if not self._dragRegion:
				prefs = self.seqCanvas.mav.prefs
				self._dragRegion = self.newRegion(
					blocks=[block], select=True,
					outline=prefs[NEW_REGION_BORDER],
					fill=prefs[NEW_REGION_INTERIOR],
					coverGaps=True)
				if not controlDown and self._prevDrag:
					self._prevDrag.destroy()
					self._prevDrag = None
			elif not self._dragLines:
				self._dragRegion.addBlock(block)
			else:
				self._dragRegion.updateLastBlock(block)

			bboxes = []
			for block in self._dragRegion.blocks:
				bboxes.extend(self.seqCanvas.bboxList(
							coverGaps=True, *block))
			for i in range(len(bboxes)):
				curBBox = bboxes[i]
				try:
					prevBBox = self._bboxes[i]
				except IndexError:
					prevBBox = None
				if curBBox == prevBBox:
					continue
				ulX, ulY, lrX, lrY = curBBox
				ulX -= 1
				ulY -= 1
				lrX += 1
				lrY += 1
				if not prevBBox:
					create_line = self.seqCanvas.mainCanvas\
								.create_line
					dragLines = []
					dragLines.append(create_line(ulX, ulY,
						ulX, lrY, stipple="gray50"))
					dragLines.append(create_line(ulX, lrY,
						lrX, lrY, stipple="gray50"))
					dragLines.append(create_line(lrX, lrY,
						lrX, ulY, stipple="gray50"))
					dragLines.append(create_line(lrX, ulY,
						ulX, ulY, stipple="gray50"))
					self._dragLines.append(dragLines)
				else:
					coords = self.seqCanvas.mainCanvas.coords
					dragLines = self._dragLines[i]
					coords(dragLines[0], ulX, ulY,
								ulX, lrY)
					coords(dragLines[1], ulX, lrY,
								lrX, lrY)
					coords(dragLines[2], lrX, lrY,
								lrX, ulY)
					coords(dragLines[3], lrX, ulY,
								ulX, ulY)
			for i in range(len(bboxes), len(self._bboxes)):
				self.seqCanvas.mainCanvas.delete(
							*self._dragLines[i])
			self._dragLines = self._dragLines[:len(bboxes)]
			self._bboxes = bboxes
		else:
			self._clearDrag()

	def _mouseUpCB(self, event):
		canvas = self.seqCanvas.mainCanvas
		if not self._dragRegion:
			# maybe a region pick
			region = self._region(event)
			if region:
				self._toggleCurrent(region)
			else:
				# maybe a column pick
				col = self._columnPick(event)
				if col is not None:
					residues = self._residuesInBlock((
						self.seqCanvas.seqs[0],
						self.seqCanvas.seqs[-1],
						col, col))
					sel = ItemizedSelection()
					sel.add(residues)
					selectionOperation(sel)
		else:
			self._selectOnStructures()
			self._prevDrag = self._dragRegion
			self.seqCanvas.mav.status(
				"Shift-drag to add to region; "
				"control-drag to add new region\n"
				"Tools->Region Browser to change colors; "
				"control left/right arrow to realign region",
				blankAfter=120)
		self._startX, self._startY = None, None
		if self._afterID:
			canvas.after_cancel(self._afterID)
			self._afterID = None
		self._dragRegion = None
		self._clearDrag()

	def _preAddLines(self, lines):
		for region in self.regions:
			region._addLines(lines)

	def _preDelLines(self, lines):
		for region in self.regions:
			region._delLines(lines)

	def _rebuildListing(self, selected):
		makeCB = False
		if not selected and self.regions:
			selected = self.regions[:1]
			makeCB = True
		hlist = self.regionListing.hlist
		hlist.delete_all()
		for wl in hlist._widgetCache.values():
			while wl:
				wl.pop().destroy()
		if not hasattr(self, "_checkButtonStyle"):
			from Tix import DisplayStyle
			self._checkButtonStyle = DisplayStyle("window",
				background=hlist["background"],
				refwindow=self.regionListing, anchor="center")
			self._onImg = self.regionListing.tk.call('tix',
							'getimage', 'ck_on')
			self._offImg = self.regionListing.tk.call('tix',
							'getimage', 'ck_off')
		for i, r in enumerate(self.regions):
			hlist.add(i, itemtype="text", style=self.textStyle,
				text=regionName(r, self.seqCanvas.mav.prefs))
			if r == self._curRegion:
				img = self._onImg
			else:
				img = self._offImg
			toggle = Tkinter.Checkbutton(hlist, command=lambda r=r:
					self._toggleCurrent(r), image=img,
					selectcolor="",
					indicatoron=False, borderwidth=0)
			hlist.item_create(i, hlist.CURRENT_COL,
					itemtype="window", window=toggle,
					style=self._checkButtonStyle)
			hlist._widgetCache[hlist.CURRENT_COL].append(toggle)
			if r.shown:
				img = self._onImg
			else:
				img = self._offImg
			toggle = Tkinter.Checkbutton(hlist, image=img, command=
					lambda r=r: self._toggleShown(r),
					selectcolor="",
					indicatoron=False, borderwidth=0)
			hlist.item_create(i, hlist.SHOWN_COL,
					itemtype="window", window=toggle,
					style=self._checkButtonStyle)
			hlist._widgetCache[hlist.SHOWN_COL].append(toggle)
			if r in selected:
				hlist.selection_set(i)
		if makeCB:
			self._listingCB()
		
	def _region(self, event):
		canvas = self.seqCanvas.mainCanvas
		canvasX = canvas.canvasx(event.x)
		canvasY = canvas.canvasy(event.y)
		for region in self.regions:
			if region.contains(canvasX, canvasY):
				return region
		return None

	def _regionDestroyedCB(self, region):
		if region == self._curRegion:
			self._toggleCurrent(region)
		sels = self.selected()
		if region in sels:
			sels.remove(region)
		self.regions.remove(region)
		self._rebuildListing(sels)
		if region == self._prevDrag:
			self._prevDrag = None
		if region == self._dragRegion:
			self._dragRegion = None
		if region == self._highlightedRegion:
			self._highlightedRegion = None
		if region in self.renameDialogs:
			self.renameDialogs[region].destroy()
			del self.renameDialogs[region]

	def _regionResiduesCB(self, event):
		region = self._region(event)
		if not region:
			return None
		residues = []
		for block in region.blocks:
			residues.extend(self._residuesInBlock(block))
		return residues

	def _regionSizeChangedCB(self, region):
		self._rebuildListing(self.selected())

	def _residueCB(self, event):
		canvas = self.seqCanvas.mainCanvas
		canvasX = canvas.canvasx(event.x)
		canvasY = canvas.canvasy(event.y)
		block = self.seqCanvas.boundedBy(canvasX, canvasY,
							canvasX, canvasY)
		if block[0] is None:
			return None
		return self._residuesInBlock(block)

	def _residuesInBlock(self, block):
		line1, line2, pos1, pos2 = block

		residues = []
		seqs = self.seqCanvas.seqs
		try:
			index1 = seqs.index(line1)
		except ValueError:
			index1 = 0
		try:
			index2 = seqs.index(line2) + 1
		except ValueError:
			index2 = 0
		for aseq in seqs[index1:index2]:
			try:
				matchMaps = aseq.matchMaps
			except AttributeError:
				continue
			for matchMap in matchMaps.values():
				for gapped in range(pos1, pos2+1):
					ungapped = aseq.gapped2ungapped(gapped)
					if ungapped is None:
						continue
					try:
						res = matchMap[ungapped]
					except KeyError:
						continue
					residues.append(res)
		return residues

	def _selectOnStructures(self, region=None):
		# highlight on chimera structures
		from chimera import getSelMode
		self._selChangeFromSelf = getSelMode() == "replace"
		sel = ItemizedSelection()
		sel.add(self.regionResidues(region))
		sel.addImplied(vertices=False)
		selectionOperation(sel)
		self._selChangeFromSelf = False

	def _selBorderRGBAcb(self, opt):
		self.seqCanvas.mav.prefs[SEL_REGION_BORDER] = opt.get()
		selRegion = self.getRegion(SEL_REGION_NAME)
		if selRegion:
			selRegion.setBorderRGBA(self._getRGBA(option=opt))

	def _selChangeCB(self, trigName, myData, trigData):
		selRegion = self.getRegion(SEL_REGION_NAME, create=1,
			fill=self.seqCanvas.mav.prefs[SEL_REGION_INTERIOR],
			outline=self.seqCanvas.mav.prefs[SEL_REGION_BORDER])
		if self._selChangeFromSelf:
			selRegion.clear()
		else:
			self.showChimeraSelection()
		
	def _selInteriorRGBAcb(self, opt):
		self.seqCanvas.mav.prefs[SEL_REGION_INTERIOR] = opt.get()
		selRegion = self.getRegion(SEL_REGION_NAME)
		if selRegion:
			selRegion.setInteriorRGBA(self._getRGBA(option=opt))

	def _showSelCB(self):
		# also called from PrefDialog.py
		if self.seqCanvas.mav.prefs[SHOW_SEL]:
			self.showChimeraSelection()
			self._selChangeHandler = chimera.triggers.addHandler(
				"selection changed", self._selChangeCB, None)
		else:
			chimera.triggers.deleteHandler("selection changed",
						self._selChangeHandler)
			selRegion = self.getRegion(SEL_REGION_NAME)
			if selRegion:
				selRegion.destroy()

	def _toggleCurrent(self, region):
		hlist = self.regionListing.hlist
		if self._curRegion is not None:
			hlist._widgetCache[hlist.CURRENT_COL][
				self.regions.index(self._curRegion)].configure(
					selectcolor="", image=self._offImg)
			if self._curRegion == region:
				region.dehighlight()
				self._curRegion = None
				return
		self._curRegion = region
		hlist._widgetCache[hlist.CURRENT_COL][
			self.regions.index(region)].configure(selectcolor="",
							image=self._onImg)
		self.highlight(region)

	def _toggleShown(self, region):
		if region.shown:
			img = self._offImg
		else:
			img = self._onImg
		hlist = self.regionListing.hlist
		hlist._widgetCache[hlist.SHOWN_COL][
			self.regions.index(region)].configure(selectcolor="",
								image=img)
		region.shown = not region.shown

from OpenSave import OpenModeless
class ScfDialog(OpenModeless):
	title = "Load SCF/Seqsel File"

	def __init__(self, colorStructuresDefault, **kw):
		kw['filters'] = [("SCF", ["*.scf", "*.seqsel"])]
		kw['defaultFilter'] = 0
		kw['clientPos'] = 's'
		OpenModeless.__init__(self, **kw)

	def fillInUI(self, parent):
		OpenModeless.fillInUI(self, parent)
		self.colorStructureVar = Tkinter.IntVar(self.clientArea)
		self.colorStructureVar.set(colorStructuresDefault)

		Tkinter.Checkbutton(self.clientArea,
				text="Color structures also",
				variable=self.colorStructureVar).grid()

class RenameDialog(ModelessDialog):
	buttons = ('OK', 'Cancel')
	default = 'OK'

	def __init__(self, regionBrowser, region):
		self.title = "Rename '%s' Region" % regionName(region,
				regionBrowser.seqCanvas.mav.prefs)
		self.regionBrowser = regionBrowser
		self.region = region
		ModelessDialog.__init__(self)

	def map(self, e=None):
		self.renameOpt._option.focus_set()

	def fillInUI(self, parent):
		from chimera.tkoptions import StringOption
		self.renameOpt = StringOption(parent, 0, "Rename region to",
								"", None)
	def Apply(self):
		newName = self.renameOpt.get().strip()
		if not newName:
			self.enter()
			from chimera import UserError
			raise UserError("Must supply a new region name or "
							"click Cancel")
		self.regionBrowser.renameRegion(self.region, newName)

	def destroy(self):
		self.region = None
		self.regionBrowser = None
		ModelessDialog.destroy(self)
		
from SeqCanvas import ellipsisName
def regionName(region, prefs):
	return ellipsisName(str(region), prefs[REGION_NAME_ELLIPSIS])
