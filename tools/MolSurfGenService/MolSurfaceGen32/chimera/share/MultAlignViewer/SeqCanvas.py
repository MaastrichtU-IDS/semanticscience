# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: SeqCanvas.py 29637 2009-12-17 20:08:02Z pett $

from Consensus import Consensus
from Conservation import Conservation
import string
from prefs import SINGLE_PREFIX
from prefs import WRAP_IF, WRAP_THRESHOLD, WRAP, LINE_WIDTH, BLOCK_SPACE
from prefs import FONT_NAME, FONT_SIZE, BOLD_ALIGNMENT
from prefs import LINE_SEP, COLUMN_SEP, TEN_RES_GAP
from prefs import CONSERVATION_STYLE, CSV_CLUSTAL_CHARS
from prefs import CONSENSUS_STYLE
from prefs import RC_CLUSTALX, RC_BLACK, RC_RIBBON, RC_CUSTOM_SCHEMES
from prefs import RESIDUE_COLORING, nonFileResidueColorings
from prefs import SEQ_NAME_ELLIPSIS
from prefs import SHOW_CONSERVATION_AT_STARTUP, SHOW_CONSENSUS_AT_STARTUP
from prefs import SHOW_RULER_AT_STARTUP
from chimera import replyobj
from chimera.misc import chimeraLabel
import tkFont
import Tkinter
import Pmw
import chimera

ADD_HEADERS = "add headers"
DEL_HEADERS = "delete headers"
SHOW_HEADERS = "show headers"
HIDE_HEADERS = "hide headers"
DISPLAY_TREE = "hide/show tree"

class SeqCanvas:
	EditUpdateDelay = 7000
	def __init__(self, parent, mav, seqs):
		self.labelCanvas = Tkinter.Canvas(parent, bg="#E4E4E4")
		self._vdivider = Tkinter.Frame(parent, bd=2, relief='raised')
		self._hdivider = Tkinter.Frame(parent, bd=0, relief='flat',
			background="black")
		# force dividers to show...
		Tkinter.Frame(self._vdivider).pack()
		Tkinter.Frame(self._hdivider, background='black').pack()
		self.mainCanvas = Tkinter.Canvas(parent, bg="#E4E4E4")

		self._vscrollMapped = self._hscrollMapped = 0
		self.horizScroll = Tkinter.Scrollbar(parent,
							orient="horizontal")
		self.mainCanvas["xscrollcommand"] = self.horizScroll.set
		self.horizScroll["command"] = self.mainCanvas.xview

		self.vertScroll = Tkinter.Scrollbar(parent, orient="vertical")
		# hooking up the label canvas yscrollcommand does weird things
		# if it's not managed, so just the main canvas...
		self.mainCanvas["yscrollcommand"] = self.vertScroll.set
		self.vertScroll["command"] = self._multiScroll

		# scroll wheel...
		self.mainCanvas.bind('<MouseWheel>', lambda e:
					self.vertScroll.event_generate('<MouseWheel>',
					state=e.state, delta=e.delta))
		# X doesn't deliver MouseWheel events, instead uses Button 4/5
		# events.  Greg's workaround code in tkgui to translate them into
		# MouseWheel events doesn't deliver the events to widgets that
		# don't accept the focus, so I need to bind them explicitly.
		self.mainCanvas.bind('<4>',
			lambda event: self._multiScroll('scroll', -1, 'units'))
		self.mainCanvas.bind('<5>',
			lambda event: self._multiScroll('scroll', 1, 'units'))

		self.mainCanvas.bind('<Configure>', self._configureCB)

		self.mav = mav
		self.seqs = seqs
		for trig in [ADD_HEADERS, DEL_HEADERS,
				SHOW_HEADERS, HIDE_HEADERS, DISPLAY_TREE]:
			self.mav.triggers.addTrigger(trig)
		parent.winfo_toplevel().configure(takefocus=1)
		parent.winfo_toplevel().focus()
		self.mainCanvas.configure(takefocus=1)
		parent.winfo_toplevel().bind('<Next>', self._pageDownCB)
		parent.winfo_toplevel().bind('<space>', self._pageDownCB)
		parent.winfo_toplevel().bind('<Prior>', self._pageUpCB)
		parent.winfo_toplevel().bind('<Shift-space>', self._pageUpCB)
		parent.winfo_toplevel().bind('<Left>', self._arrowCB)
		parent.winfo_toplevel().bind('<Right>', self._arrowCB)
		parent.winfo_toplevel().bind('<Up>', self._arrowCB)
		parent.winfo_toplevel().bind('<Down>', self._arrowCB)
		parent.winfo_toplevel().bind('<Escape>', self._escapeCB)
		self.lineWidth = self.lineWidthFromPrefs()
		self.font = tkFont.Font(parent,
			(self.mav.prefs[FONT_NAME], self.mav.prefs[FONT_SIZE]))
		self.treeBalloon = Pmw.Balloon(parent)
		self.tree = self._treeCallback = None
		self.treeShown = self.nodesShown = False
		self._residueHandlers = None
		self.layout()
		self.mainCanvas.grid(row=1, column=2, sticky='nsew')
		parent.columnconfigure(2, weight=1)
		parent.rowconfigure(1, weight=1)

		# make the main canvas a reasonable size
		left, top, right, bottom = map(int,
				self.mainCanvas.cget("scrollregion").split())
		totalWidth = right - left + 1
		if self.shouldWrap():
			self.mainCanvas.config(width=totalWidth)
		else:
			seven = self.mainCanvas.winfo_pixels("7i")
			self.mainCanvas.config(width=min(seven, totalWidth))
		totalHeight = bottom - top + 1
		three = self.mainCanvas.winfo_pixels("3i")
		height = min(three, totalHeight)
		self.mainCanvas.config(height=height)
		self.labelCanvas.config(height=height)

		# need to update label outline box colors when molecules change
		self._trigID = chimera.triggers.addHandler(
					'Molecule', self._molChange, None)

		# for tracking delayed update of headers/attrs during editing
		self._editBounds = self._delayedAttrsHandler = None

		# for undo/redo
		self._checkPoint(fromScratch=True)

		from MAViewer import ADDDEL_SEQS
		self._addDelSeqsHandler = self.mav.triggers.addHandler(
				ADDDEL_SEQS, self._addDelSeqsCB, None)

	def activeNode(self):
		return self.leadBlock.treeNodeMap['active']

	def _addDelSeqsCB(self, trigName, myData, trigData):
		self._clustalXcache = {}
		for seq in self.seqs:
			try:
				cf = seq.colorFunc
			except AttributeError:
				continue
			break
		for seq in self.seqs:
			seq.colorFunc = cf
			if cf != self._cfBlack:
				self.recolor(seq)
		
	def addSeqs(self, seqs):
		for seq in seqs:
			self.labelBindings[seq] = {
				'<Enter>': lambda e, s=seq: self.mav.status(
						self._getBindSeqLabelText(s))
			}
		self.mav.regionBrowser._preAddLines(seqs)
		self.leadBlock.addSeqs(seqs)
		self.mav.regionBrowser.redrawRegions()

	def adjustScrolling(self):
		self._resizescrollregion()
		self._recomputeScrollers()
		
	def _arrowCB(self, event):
		if event.state & 4 != 4:
			if event.keysym == "Up":
				self.mav.regionBrowser.raiseRegion(
						self.mav.currentRegion())
			elif event.keysym == "Down":
				self.mav.regionBrowser.lowerRegion(
						self.mav.currentRegion())
			else:
				self.mav.status(
					"Use control-arrow to edit alignment\n")
			return

		if event.keysym == "Up":
			self._undoRedo(False)
			return
		if event.keysym == "Down":
			self._undoRedo(True)
			return

		region = self.mav.currentRegion()
		if not region:
			replyobj.error("No active region.\n")
			return

		from RegionBrowser import SEL_REGION_NAME
		if region.name == SEL_REGION_NAME:
			replyobj.error(
				"Cannot edit using Chimera selection region\n")
			return

		if len(region.blocks) > 1:
			replyobj.error(
				"Cannot edit with multi-block region.\n")
			return

		line1, line2, pos1, pos2 = region.blocks[0]
		if line1 not in self.seqs:
			line1 = self.seqs[0]
		if line2 not in self.seqs:
			replyobj.error("Edit region does not contain any"
						" editable sequences.\n")
			return

		if event.keysym == "Left":
			incr = -1
			start = pos1
			end = pos2 + 1
		else:
			incr = 1
			start = pos2
			end = pos1 - 1

		gapPos = start + incr
		seqs = self.seqs[self.seqs.index(line1)
						:self.seqs.index(line2)+1]

		offset = 0
		if gapPos < 0 or gapPos >= len(line1):
			self.mav.status("Need to add columns to alignment to"
				" allow for requested motion.\nPlease wait...")
			# try to figure out the gap character
			# in use...
			gapChar = None
			for s in self.seqs:
				for c in str(s):
					if not c.isalnum():
						gapChar = c
						break
				if gapChar is not None:
					break
			else:
				gapChar = '.'
			num2add = 10
			if incr == -1:
				newSeqs = [gapChar * num2add + str(x)
							for x in self.seqs]
				start += num2add
				end += num2add
				pos1 += num2add
				pos2 += num2add
				gapPos += num2add
				offset = num2add
			else:
				newSeqs = [str(x) + gapChar * num2add
							for x in self.seqs]
			self.mav.realign(newSeqs, offset=offset,
							markEdited=True)
			self.mav.status("Columns added\n")
		else:
			for seq in seqs:
				if seq[gapPos].isalnum():
					replyobj.error("No all-gap column in"
						" requested direction; cannot"
						" move editing region.\n"
						" Select a larger region to"
						" continue motion.\n")
					return

		motion = 0
		while True:
			motion += incr
			for seq in seqs:
				gapChar = seq[gapPos]
				for i in range(start, end, 0-incr):
					seq[i+incr] = seq[i]
				seq[end+incr] = gapChar
			if event.state & 1 != 1: # shift key not down
				break
			nextGap = gapPos + incr
			if nextGap < 0 or nextGap >= len(line1):
				break
			for seq in seqs:
				if seq[nextGap].isalnum():
					break
			else:
				start += incr
				end += incr
				gapPos = nextGap
				continue
			break
		self.mav._edited = True
		if incr == -1:
			left, right = gapPos, end-2-motion
		else:
			left, right = end+2-motion, gapPos
			
		self._editRefresh(seqs, left, right, region=region,
			lastBlock=[line1, line2, pos1+motion, pos2+motion])
		self._checkPoint(offset=offset, left=left, right=right)

	def addHeaders(self, headers):
		headers = [hd for hd in headers if hd not in self.headers]
		if not headers:
			return
		for hd in headers:
			self.labelBindings[hd] = {}
		self.headers.extend(headers)
		self.displayHeader.update({}.fromkeys(headers, False))
		self.mav.triggers.activateTrigger(ADD_HEADERS, headers)
		self.showHeaders(headers)

	def _associationsCB(self, trigName, myData, trigData):
		matchMaps = trigData[1]
		for mm in matchMaps:
			self.recolor(mm['aseq'])

	def assocSeq(self, aseq):
		"""alignment sequence has gained or lost associated structure"""
		self.leadBlock.assocSeq(aseq)

	def bboxList(self, line1, line2, pos1, pos2, coverGaps=True):
		"""return coords that bound given lines and positions"""
		return self.leadBlock.bboxList(line1, line2, pos1, pos2,
								coverGaps)

	def boundedBy(self, x1, y1, x2, y2):
		"""return lines and offsets bounded by given coords"""
		return self.leadBlock.boundedBy(x1, y1, x2, y2)

	def _attrsUpdateCB(self):
		self._delayedAttrsHandler = None
		self.mav.status("Updating residue attributes")
		self.mav.setResidueAttrs()
		self.mav.status("Residue attributes updated")

	def _checkPoint(self, fromScratch=False, checkChange=False, offset=0,
						left=None, right=None):
		if fromScratch:
			self._checkPoints = []
			self._checkPointIndex = -1
		self._checkPoints = self._checkPoints[:self._checkPointIndex+1]
		chkpt = [s[:] for s in self.seqs]
		if checkChange:
			if chkpt == self._checkPoints[self._checkPointIndex][0]:
				return
		self._checkPoints.append(
			(chkpt, (offset, self.mav._edited, left, right)))
		self._checkPointIndex += 1

	def _configureCB(self, e):
		# size change; scrollbars?
		import sys
		if hasattr(self, "_configureWait") and self._configureWait:
			self.mainCanvas.after_cancel(self._configureWait)
		# Windows/Mac can get into a configure loop somehow unless we
		# do an actual 'after' instead of after_idle
		self._configureWait = self.mainCanvas.after(100, lambda e=e:
			self._configureWaitCB(e))

	def _configureWaitCB(self, e):
		self._configureWait = None

		if e.width <= 1 or e.height <=1:
			# wait for a 'real' event
			return

		self._recomputeScrollers(e.width, e.height)

	def deleteHeaders(self, headers):
		if not headers:
			return
		for header in headers:
			if header in self.seqs:
				raise ValueError(
					"Cannot delete an alignment sequence")
			if header in self.builtinHeaders:
				raise ValueError("Cannot delete builtin header"
							" sequence")
		self.hideHeaders(headers)
		for hd in headers:
			del self.displayHeader[hd]
			self.headers.remove(hd)
		self.mav.triggers.activateTrigger(DEL_HEADERS, headers)

	def destroy(self):
		chimera.triggers.deleteHandler('Molecule', self._trigID)
		from MAViewer import ADDDEL_SEQS
		self.mav.triggers.deleteHandler(ADDDEL_SEQS,
						self._addDelSeqsHandler)
		if self._residueHandlers:
			chimera.triggers.deleteHandler('Residue',
						self._residueHandlers[0])
			from MAViewer import MOD_ASSOC
			self.mav.triggers.deleteHandler(MOD_ASSOC,
						self._residueHandlers[1])
		for header in self.headers:
			header.destroy()
		self.leadBlock.destroy()
		
	def _editHdrCB(self):
		left, right = self._editBounds
		self._editBounds = None
		for header in self.headers:
			if not hasattr(header, 'alignChange'):
				continue
			if header.fastUpdate():
				# already updated
				continue
			self.mav.status("Updating %s header" % header.name)
			header.alignChange(left, right)
			self.refresh(header, left=left, right=right)
			self.mav.status("%s header updated" % header.name)

	def _editRefresh(self, seqs, left, right, region=None, lastBlock=None):
		for header in self.headers:
			if not hasattr(header, 'alignChange'):
				continue
			if not self.displayHeader[header]:
				continue
			if not header.fastUpdate():
				# header can't update quickly; delay it
				self.mav.status("Postponing update of %s header"
							% header.name)
				if self._editBounds:
					self._editBounds = (min(left,
						self._editBounds[0]), max(
						right, self._editBounds[1]))
					self.mainCanvas.after_cancel(
							self._editHdrHandler)
				else:
					self._editBounds = (left, right)
				self._editHdrHandler = self.mainCanvas.after(
					self.EditUpdateDelay, self._editHdrCB)
				continue
			header.alignChange(left, right)
			self.refresh(header, left=left, right=right,
							updateAttrs=False)
		for seq in seqs:
			self.refresh(seq, left=left, right=right,
							updateAttrs=False)
		if region:
			region.updateLastBlock(lastBlock)
		self.mav.regionBrowser.redrawRegions(justGapping=True)
		if not self._editBounds:
			if self._delayedAttrsHandler:
				self.mainCanvas.after_cancel(
						self._delayedAttrsHandler)
			self._delayedAttrsHandler = self.mainCanvas.after(
				self.EditUpdateDelay, self._attrsUpdateCB)
	def _escapeCB(self, event):
		if event.state & 4 != 4:
			self.mav.status(
				"Use control-escape to revert to unedited\n")
			return
		while self._checkPointIndex > 0:
			self._undoRedo(True)

	def _getBindSeqLabelText(self, aseq):
		basicText = "%s (%d non-gap residues)\n" % (aseq.name,
							len(aseq.ungapped()))
		if not hasattr(aseq, 'matchMaps') or not aseq.matchMaps:
			return basicText
		return "%s%s associated with %s\n" % (basicText,
			seqName(aseq, self.mav.prefs),
			", ".join(["%s (%s %s)" % (m.oslIdent(), m.name,
			aseq.matchMaps[m]['mseq'].name)
			for m in aseq.matchMaps.keys()]))

	def headerDisplayOrder(self):
		return self.leadBlock.lines[:-len(self.seqs)]

	def hideHeaders(self, headers):
		headers = [hd for hd in headers if self.displayHeader[hd]]
		if not headers:
			return

		# only handle headers in continuous blocks...
		if len(headers) > 1:
			continuous = True
			li = self.leadBlock.lineIndex[headers[0]]
			for header in headers[1:]:
				li += 1
				if self.leadBlock.lineIndex[header] != li:
					continuous = False
					break
			if not continuous:
				jump = headers.index(header)
				self.hideHeaders(headers[:jump])
				self.hideHeaders(headers[jump:])
				return
		for header in headers:
			header.hide()
		self.displayHeader.update({}.fromkeys(headers, False))
		self.mav.regionBrowser._preDelLines(headers)
		self.leadBlock.hideHeaders(headers)
		self.mav.regionBrowser.redrawRegions(cullEmpty=True)
		self.mav.triggers.activateTrigger(HIDE_HEADERS, headers)

	def _labelCanvas(self, grid=1):
		if self.shouldWrap():
			labelCanvas = self.mainCanvas
			if grid:
				self.labelCanvas.grid_forget()
				self._vdivider.grid_forget()
		else:
			labelCanvas = self.labelCanvas
			if grid:
				self.labelCanvas.grid(row=1, column=0,
								sticky="nsw")
				self._vdivider.grid(row=1, column=1,
						rowspan=2, sticky="nsew")
		return labelCanvas
		
	def layout(self):
		self.consensus = Consensus(self.mav)
		def colorConsensus(line, offset, upper=string.uppercase):
			if line[offset] in upper:
				if line.conserved[offset]:
					return 'red'
				return 'purple'
			return 'black'
		self.consensus.colorFunc = colorConsensus
		self.conservation = Conservation(self.mav, evalWhileHidden=True)
		self.headers = [self.consensus, self.conservation]
		self.builtinHeaders = self.headers[:]
		singleSequence = len(self.seqs) == 1
		self.displayHeader = {
			self.consensus:
				self.mav.prefs[SHOW_CONSENSUS_AT_STARTUP]
				and not (singleSequence and not
				self.consensus.singleSequenceRelevant),
			self.conservation:
				self.mav.prefs[SHOW_CONSERVATION_AT_STARTUP]
				and not (singleSequence and not
				self.conservation.singleSequenceRelevant)
		}
		for header, show in self.displayHeader.items():
			if show:
				header.show()
		from HeaderSequence import registeredHeaders
		for seq, defaultOn in registeredHeaders.items():
			header = seq(self.mav)
			self.headers.append(header)
			self.displayHeader[header] = defaultOn and not (
					singleSequence and not
					header.singleSequenceRelevant)
		self.headers.sort(lambda s1, s2: cmp(s1.sortVal, s2.sortVal)
						or cmp(s1.name, s2.name))
		self.labelBindings = {}
		for seq in self.seqs:
			self.labelBindings[seq] = {
				'<Enter>': lambda e, s=seq: self.mav.status(
						self._getBindSeqLabelText(s))
			}
		initialHeaders = [hd for hd in self.headers
						if self.displayHeader[hd]]
		for line in self.headers:
			self.labelBindings[line] = {}

		# first, set residue coloring to a known safe value...
		from clustalX import clustalInfo
		if singleSequence:
			prefResColor = RC_BLACK
		else:
			prefResColor = self.mav.prefs[RESIDUE_COLORING]
		if prefResColor == RC_BLACK:
			rc = self._cfBlack
		elif prefResColor == RC_RIBBON:
			from MAViewer import MOD_ASSOC
			self._residueHandlers = [chimera.triggers.addHandler(
					'Residue', self._resChangeCB, None),
				self.mav.triggers.addHandler(MOD_ASSOC,
					self._associationsCB, None)]
			rc = self._cfRibbon
		else:
			rc = self._cfClustalX
		for seq in self.seqs:
			seq.colorFunc = rc
		self._clustalXcache = {}
		self._clustalCategories, self._clustalColorings = clustalInfo()
		# try to set to external color scheme
		if prefResColor not in nonFileResidueColorings:
			try:
				self._clustalCategories, self._clustalColorings\
						= clustalInfo(prefResColor)
			except:
				schemes = self.mav.prefs[RC_CUSTOM_SCHEMES]
				if prefResColor in schemes:
					schemes.remove(prefResColor)
					self.mav.prefs[
						RC_CUSTOM_SCHEMES] = schemes[:]
				self.mav.prefs[RESIDUE_COLORING] = RC_CLUSTALX
				from sys import exc_info
				replyobj.error("Error reading %s: %s\nUsing"
					" default ClustalX coloring instead\n"
					% (prefResColor, exc_info()[1]))

		self.showRuler = self.mav.prefs[SHOW_RULER_AT_STARTUP] \
						and not singleSequence
		self.showNumberings = [self.mav.leftNumberingVar.get(),
					self.mav.rightNumberingVar.get()]
		self.leadBlock = SeqBlock(self._labelCanvas(), self.mainCanvas,
			None, self.font, 0, initialHeaders, self.seqs,
			self.lineWidth, self.labelBindings, self.mav.status,
			self.showRuler, self.treeBalloon, self.showNumberings,
			self.mav.prefs)
		self._resizescrollregion()

	def lineWidthFromPrefs(self):
		if self.shouldWrap():
			if len(self.mav.seqs) == 1:
				prefix = SINGLE_PREFIX
			else:
				prefix = ""
			return self.mav.prefs[prefix + LINE_WIDTH]
		# lay out entire sequence horizontally
		return 2 * len(self.seqs[0])

	def _molChange(self, trigger, myData, changes):
		# molecule attributes changed

		# find sequences (if any) with associations to changed mols
		assocSeqs = []
		for mol in changes.created | changes.modified:
			try:
				seq = self.mav.associations[mol]
			except KeyError:
				continue
			if seq not in assocSeqs:
				assocSeqs.append(seq)
		if assocSeqs:
			self.leadBlock._molChange(assocSeqs)

	def _multiScroll(self, *args):
		self.labelCanvas.yview(*args)
		self.mainCanvas.yview(*args)

	def _newFont(self):
		if len(self.mav.seqs) == 1:
			prefix = SINGLE_PREFIX
		else:
			prefix = ""
		fontname, fontsize = (self.mav.prefs[prefix + FONT_NAME],
						self.mav.prefs[prefix + FONT_SIZE])
		self.font = tkFont.Font(self.mainCanvas, (fontname, fontsize))
		self.mav.status("Changing to %d point %s\n"
					% (fontsize, fontname), blankAfter=0)
		self.leadBlock.fontChange(self.font)
		if self.treeShown:
			self.leadBlock.showTree({'tree': self.tree},
					self._treeCallback, self.nodesShown,
					active=self.activeNode())
		self.mav.regionBrowser.redrawRegions()
		self.mav.status("Font changed\n")

	def _newWrap(self):
		"""alignment wrapping preferences have changed"""
		lineWidth = self.lineWidthFromPrefs()
		if lineWidth == self.lineWidth:
			return
		self.lineWidth = lineWidth
		self._reformat()

	def _pageDownCB(self, event):
		numBlocks = self.leadBlock.numBlocks()
		v1, v2 = self.mainCanvas.yview()
		for i in range(numBlocks-1):
			if (i + 0.1) / numBlocks > v1:
				self.mainCanvas.yview_moveto(
							float(i+1) / numBlocks)
				self.labelCanvas.yview_moveto(
							float(i+1) / numBlocks)
				return
		self.mainCanvas.yview_moveto(float(numBlocks - 1) / numBlocks)
		self.labelCanvas.yview_moveto(float(numBlocks - 1) / numBlocks)

	def _pageUpCB(self, event):
		numBlocks = self.leadBlock.numBlocks()
		v1, v2 = self.mainCanvas.yview()
		for i in range(numBlocks):
			if (i + 0.1) / numBlocks >= v1:
				if i == 0:
					self.mainCanvas.yview_moveto(0.0)
					self.labelCanvas.yview_moveto(0.0)
					return
				self.mainCanvas.yview_moveto(
							float(i-1) / numBlocks)
				self.labelCanvas.yview_moveto(
							float(i-1) / numBlocks)

				return
		self.mainCanvas.yview_moveto(float(numBlocks - 1) / numBlocks)
		self.labelCanvas.yview_moveto(float(numBlocks - 1) / numBlocks)
	
	def realign(self, seqs, offset=None):
		savedSNs = self.showNumberings[:]
		if self.showNumberings[0]:
			self.setLeftNumberingDisplay(False)
		if self.showNumberings[1]:
			self.setRightNumberingDisplay(False)
		prevLen = len(self.seqs[0])
		for i in range(len(seqs)):
			self.seqs[i][:] = seqs[i]
		for header in self.headers:
			header.reevaluate()
		self._clustalXcache = {}
		self.leadBlock.realign(prevLen)
		if savedSNs[0]:
			self.setLeftNumberingDisplay(True)
		if savedSNs[1]:
			self.setRightNumberingDisplay(True)
		self._resizescrollregion()
		if len(self.seqs[0]) != prevLen:
			self._recomputeScrollers()

	def recolor(self, seq):
		self.leadBlock.recolor(seq)

	def _recomputeScrollers(self, width=None, height=None, xShowAt=None):
		if width is None:
			width = int(self.mainCanvas.cget('width'))
			height = int(self.mainCanvas.cget('height'))
		x1, y1, x2, y2 = map(int,
				self.mainCanvas.cget('scrollregion').split())

		needXScroll = x2 - x1 > width
		if needXScroll:
			if not self._hscrollMapped:
				self.horizScroll.grid(row=2, column=2,
								sticky="ew")
				self._hscrollMapped = True
			if xShowAt is not None:
				self.mainCanvas.xview_moveto(xShowAt)
		elif not needXScroll and self._hscrollMapped:
			self.horizScroll.grid_forget()
			self._hscrollMapped = False

		needYScroll = y2 - y1 > height
		if needYScroll and not self._vscrollMapped:
			self.vertScroll.grid(row=1, column=3, sticky="ns")
			self._vscrollMapped = True
		elif not needYScroll and self._vscrollMapped:
			self.vertScroll.grid_forget()
			self._vscrollMapped = False

		if not self.shouldWrap() and self._vscrollMapped:
			self._hdivider.grid(row=2, column=0, sticky="new")
		else:
			self._hdivider.grid_forget()

	def _reformat(self, cullEmpty=False):
		self.mav.status("Reformatting alignment; please wait...\n",
								blankAfter=0)
		if self.tree:
			activeNode = self.activeNode()
		self.leadBlock.destroy()
		initialHeaders = [hd for hd in self.headers
						if self.displayHeader[hd]]
		self.leadBlock = SeqBlock(self._labelCanvas(), self.mainCanvas,
			None, self.font, 0, initialHeaders, self.seqs,
			self.lineWidth, self.labelBindings, self.mav.status,
			self.showRuler, self.treeBalloon, self.showNumberings,
			self.mav.prefs)
		if self.tree:
			if self.treeShown:
				self.leadBlock.showTree({'tree': self.tree},
					self._treeCallback, self.nodesShown,
					active=activeNode)
			else:
				self.leadBlock.treeNodeMap = {'active':
								activeNode }
		self.mav.regionBrowser.redrawRegions(cullEmpty=cullEmpty)
		if len(self.seqs) != len(self._checkPoints[0]):
			self._checkPoint(fromScratch=True)
		else:
			self._checkPoint(checkChange=True)
		self.mav.status("Alignment reformatted\n")

	def refresh(self, seq, left=0, right=None, updateAttrs=True):
		if seq in self.displayHeader and not self.displayHeader[seq]:
			return
		if right is None:
			right = len(self.seqs[0])-1
		self.leadBlock.refresh(seq, left, right)
		if updateAttrs:
			self.mav.setResidueAttrs()

	def _resChangeCB(self, trigName, myData, trigData):
		mols = set([r.molecule for r in trigData.modified])
		for m in mols:
			if m in self.mav.associations:
				self.recolor(self.mav.associations[m])

	def _resizescrollregion(self):
		left, top, right, bottom = self.mainCanvas.bbox("all")
		left -= 2
		top -= 2
		right += 2
		bottom += 2
		if self._labelCanvas(grid=0) == self.labelCanvas:
			ll, lt, lr, lb = self.labelCanvas.bbox("all")
			ll -= 2
			lt -= 2
			lr += 2
			lb += 2
			top = min(top, lt)
			bottom = max(bottom, lb)
			self.labelCanvas.configure(width=lr-ll,
					scrollregion=(ll, top, lr, bottom))
		self.mainCanvas.configure(scrollregion=
						(left, top, right, bottom))

	def saveEPS(self, fileName, colorMode, rotate, extent, hideNodes):
		if self.tree:
			savedNodeDisplay = self.nodesShown
			self.showNodes(not hideNodes)
		mainFileName = fileName
		msg = ""
		twoCanvas = self._labelCanvas(grid=0) != self.mainCanvas
		import os.path
		if twoCanvas:
			twoCanvas = True
			if fileName.endswith(".eps"):
				base = fileName[:-4]
				tail = ".eps"
			else:
				base = fileName
				tail = ""
			mainFileName = base + "-alignment" + tail
			labelFileName = base + "-names" + tail
			msg = "Sequence names and main alignment saved" \
				" as separate files\nSequence names saved" \
				" to %s\n" % os.path.split(labelFileName)[1]

		msg += "Alignment saved to %s\n" % os.path.split(
							mainFileName)[1]
		mainKw = labelKw = {}
		if extent == "all":
			left, top, right, bottom = self.mainCanvas.bbox("all")
			if twoCanvas:
				ll, lt, lr, lb = self.labelCanvas.bbox("all")
				top = min(top, lt)
				bottom = max(bottom, lb)
				labelKw = {
					'x': ll, 'y': top,
					'width': lr-ll, 'height': bottom-top
				}
			mainKw = {
				'x': left, 'y': top,
				'width': right-left, 'height': bottom-top
			}
		self.mainCanvas.postscript(colormode=colorMode,
				file=mainFileName, rotate=rotate, **mainKw)
		if twoCanvas:
			self.labelCanvas.postscript(colormode=colorMode,
				file=labelFileName, rotate=rotate, **labelKw)
		if self.tree:
			self.showNodes(savedNodeDisplay)
		self.mav.status(msg)

	def seeBlocks(self, blocks):
		"""scroll canvas to show given blocks"""
		minx, miny, maxx, maxy = self.bboxList(coverGaps=True,
								*blocks[0])[0]
		for block in blocks:
			for x1, y1, x2, y2 in self.bboxList(coverGaps=True,
								*block):
				minx = min(minx, x1)
				miny = min(miny, y1)
				maxx = max(maxx, x2)
				maxy = max(maxy, y2)
		viewWidth = float(self.mainCanvas.cget('width'))
		viewHeight = float(self.mainCanvas.cget('height'))
		if maxx - minx > viewWidth or maxy - miny > viewHeight:
			# blocks don't fit in view; just show first block
			minx, miny, maxx, maxy = self.bboxList(coverGaps=True,
								*blocks[0])[0]
		cx = (minx + maxx) / 2
		cy = (miny + maxy) / 2
		
		x1, y1, x2, y2 = map(int,
			self.mainCanvas.cget('scrollregion').split())
		totalWidth = float(x2 - x1 + 1)
		totalHeight = float(y2 - y1 + 1)

		if cx < x1 + viewWidth/2:
			cx = x1 + viewWidth/2
		if cy < y1 + viewHeight/2:
			cy = y1 + viewHeight/2
		startx = max(0.0, min((cx - viewWidth/2 - x1) / totalWidth,
					(x2 - viewWidth - x1) / totalWidth))
		self.mainCanvas.xview_moveto(startx)
		starty = max(0.0, min((cy - viewHeight/2 - y1) / totalHeight,
					(y2 - viewHeight - y1) / totalHeight))
		if not self.shouldWrap():
			self.labelCanvas.yview_moveto(starty)
		self.mainCanvas.yview_moveto(starty)

	def setClustalParams(self, categories, colorings):
		self._clustalXcache = {}
		self._clustalCategories, self._clustalColorings = \
						categories, colorings
		if self.mav.prefs[RESIDUE_COLORING] in [RC_BLACK, RC_RIBBON]:
			return
		for seq in self.seqs:
			self.refresh(seq)

	def setColorFunc(self, coloring):
		if self._residueHandlers:
			chimera.triggers.deleteHandler('Residue',
						self._residueHandlers[0])
			from MAViewer import MOD_ASSOC
			self.mav.triggers.deleteHandler(MOD_ASSOC,
						self._residueHandlers[1])
			self._residueHandlers = None
		if coloring == RC_BLACK:
			cf = self._cfBlack
		elif coloring == RC_RIBBON:
			from MAViewer import MOD_ASSOC
			self._residueHandlers = [chimera.triggers.addHandler(
					'Residue', self._resChangeCB, None),
				self.mav.triggers.addHandler(MOD_ASSOC,
					self._associationsCB, None)]
			cf = self._cfRibbon
		else:
			cf = self._cfClustalX
		for seq in self.seqs:
			if not hasattr(seq, 'colorFunc'):
				seq.colorFunc = None
			if seq.colorFunc != cf:
				seq.colorFunc = cf
				self.recolor(seq)

	def setLeftNumberingDisplay(self, showNumbering):
		if self.showNumberings[0] == showNumbering:
			return
		self.showNumberings[0] = showNumbering
		self.leadBlock.setLeftNumberingDisplay(showNumbering)
		self.mav.regionBrowser.redrawRegions()
		self._resizescrollregion()
		self._recomputeScrollers()

	def setRightNumberingDisplay(self, showNumbering):
		if self.showNumberings[1] == showNumbering:
			return
		self.showNumberings[1] = showNumbering
		self.leadBlock.setRightNumberingDisplay(showNumbering)
		self._resizescrollregion()
		if showNumbering:
			self._recomputeScrollers(xShowAt=1.0)
		else:
			self._recomputeScrollers()

	def setRulerDisplay(self, showRuler):
		if showRuler == self.showRuler:
			return
		self.showRuler = showRuler
		self.leadBlock.setRulerDisplay(showRuler)
		self.mav.regionBrowser.redrawRegions(cullEmpty=not showRuler)

	def _cfBlack(self, line, offset):
		return 'black'

	def _cfClustalX(self, line, offset):
		consensusChars = self.clustalConsensusChars(offset)
		res = line[offset].upper()
		if res in self._clustalColorings:
			for color, needed in self._clustalColorings[res]:
				if not needed:
					return color
				for n in needed:
					if n in consensusChars:
						return color
		return 'black'

	def _cfRibbon(self, line, offset):
		if not hasattr(line, 'matchMaps') or not line.matchMaps:
			return 'black'
		ungapped = line.gapped2ungapped(offset)
		if ungapped == None:
			return 'black'
		rgbas = []
		for matchMap in line.matchMaps.values():
			try:
				r = matchMap[ungapped]
			except KeyError:
				continue
			rc = r.ribbonColor
			if rc == None:
				rc = r.molecule.color
			rgbas.append(rc.rgba())
		if not rgbas:
			return 'black'
		import numpy
		rgba = numpy.array(rgbas).mean(0)
		from CGLtk.color import rgba2tk
		return rgba2tk(rgba)

	def clustalConsensusChars(self, offset):
		try:
			consensusChars = self._clustalXcache[offset]
			return consensusChars
		except KeyError:
			pass
		chars = {}
		for seq in self.seqs:
			char = seq[offset].lower()
			chars[char] = chars.get(char, 0) + 1
		consensusChars = {}
		numSeqs = float(len(self.seqs))

		for members, threshold, result in self._clustalCategories:
			sum = 0
			for c in members:
				sum += chars.get(c, 0)
			if sum / numSeqs >= threshold:
				consensusChars[result] = True

		self._clustalXcache[offset] = consensusChars
		return consensusChars

	def shouldWrap(self):
		return shouldWrap(len(self.seqs), self.mav.prefs)

	def showHeaders(self, headers):
		headers = [hd for hd in headers if not self.displayHeader[hd]]
		if not headers:
			return
		for header in headers:
			header.show()
		self.displayHeader.update({}.fromkeys(headers, True))
		self.mav.regionBrowser._preAddLines(headers)
		self.leadBlock.showHeaders(headers)
		self.mav.regionBrowser.redrawRegions()
		self.mav.setResidueAttrs()
		self.mav.triggers.activateTrigger(SHOW_HEADERS, headers)

	def showNodes(self, show):
		if show == self.nodesShown:
			return
		self.nodesShown = show
		self.leadBlock.showNodes(show)

	def showTree(self, show):
		if show == self.treeShown or not self.tree:
			return

		if show:
			self.leadBlock.showTree({'tree': self.tree},
						self._treeCallback, True,
						active=self.activeNode())
			self.mav.triggers.activateTrigger(
							DISPLAY_TREE, self.tree)
		else:
			self.leadBlock.showTree(None, None, None)
			self.mav.triggers.activateTrigger(DISPLAY_TREE, None)
		self._resizescrollregion()
		self._recomputeScrollers(xShowAt=0.0)
		self.treeShown = show

	def updateNumberings(self):
		self.leadBlock.updateNumberings()
		self._resizescrollregion()

	def usePhyloTree(self, tree, callback=None):
		treeInfo = {}
		if tree:
			tree.assignYpositions()
			tree.assignXpositions(branchStyle="weighted")
			tree.assignXdeltas()
			treeInfo['tree'] = tree
		self.leadBlock.showTree(treeInfo, callback, True)
		self.leadBlock.activateNode(tree)
		self._resizescrollregion()
		self._recomputeScrollers(xShowAt=0.0)
		self.tree = tree
		self._treeCallback = callback
		self.treeShown = self.nodesShown = bool(tree)
		self.mav.triggers.activateTrigger(DISPLAY_TREE, tree)

	def _undoRedo(self, undo):
		# up/down == redo/undo
		curOffset, curEdited, curLeft, curRight = self._checkPoints[
						self._checkPointIndex][1]
		if undo:
			if self._checkPointIndex == 0:
				replyobj.error("Nothing to undo.\n")
				return
			self._checkPointIndex -= 1
		else:
			if self._checkPointIndex == len(self._checkPoints) - 1:
				replyobj.error("Nothing to redo.\n")
				return
			self._checkPointIndex += 1
		checkPoint, info = self._checkPoints[self._checkPointIndex]
		chkOffset, chkEdited, chkLeft, chkRight = info
		if undo:
			offset = 0 - curOffset
			left, right = curLeft, curRight
		else:
			offset = chkOffset
			left, right = chkLeft, chkRight
		self.mav._edited = chkEdited
		if len(checkPoint[0]) != len(self.seqs[0]):
			self.mav.status("Need to change number of columns in"
				" alignment to allow for requested change.\n"
				"Please wait...")
			self.mav.realign(checkPoint, offset=offset)
			self.mav.status("Columns changed\n")
			return
		for seq, chkSeq in zip(self.seqs, checkPoint):
			seq[:] = chkSeq
		self._editRefresh(self.seqs, left, right)


class SeqBlock:
	normalLabelColor = 'black'
	headerLabelColor = 'blue'

	def __init__(self, labelCanvas, mainCanvas, prevBlock, font, seqOffset,
			headers, seqs, lineWidth, labelBindings, statusFunc,
			showRuler, treeBalloon, showNumberings, prefs):
		self.labelCanvas = labelCanvas
		self.mainCanvas = mainCanvas
		self.prevBlock = prevBlock
		self.seqs = seqs
		self.font = font
		self.labelBindings = labelBindings
		self.statusFunc = statusFunc
		self._mouseID = None
		if len(seqs) == 1:
			prefPrefix = SINGLE_PREFIX
		else:
			prefPrefix = ""
		self.letterGaps = [prefs[prefPrefix + COLUMN_SEP],
						prefs[prefPrefix + LINE_SEP]]
		if prefs[prefPrefix + TEN_RES_GAP]:
			self.chunkGap = 20
		else:
			self.chunkGap = 0
		if prefs[prefPrefix + BLOCK_SPACE]:
			self.blockGap = 15
		else:
			self.blockGap = 0
		self.showRuler = showRuler
		self.treeBalloon = treeBalloon
		self.showNumberings = showNumberings[:]
		self.prefs = prefs
		self.seqOffset = seqOffset
		self.lineWidth = lineWidth

		if prevBlock:
			self.topY = prevBlock.bottomY + self.blockGap
			self.labelWidth = prevBlock.labelWidth
			self.fontPixels = prevBlock.fontPixels
			self.lines = prevBlock.lines
			self.lineIndex = prevBlock.lineIndex
			self.emphasisFont = prevBlock.emphasisFont
			self.numberingWidths = prevBlock.numberingWidths
		else:
			self.topY = 0
			self.lineIndex = {}
			lines = list(headers) + list(self.seqs)
			for i in range(len(lines)):
				self.lineIndex[lines[i]] = i
			self.lines = lines
			self.emphasisFont = self.font.copy()
			self.emphasisFont.configure(weight=tkFont.BOLD)
			if prefs[prefPrefix + BOLD_ALIGNMENT]:
				self.font = self.emphasisFont
			self.labelWidth = self.findLabelWidth(self.font,
							self.emphasisFont)
			fontWidth, fontHeight = self.measureFont(self.font)
			# pad font a little...
			self.fontPixels = (fontWidth + 1, fontHeight + 1)
			self.numberingWidths = self.findNumberingWidths(
								self.font)
		self.bottomY = self.topY

		self.labelTexts = {}
		self.labelRects = {}
		self.numberingTexts = {}
		self.lineItems = {}
		self.itemAuxInfo = {}
		self.treeItems = { 'lines': [], 'boxes': [] }

		self.layoutRuler()
		self.layoutLines(headers, self.headerLabelColor)
		self.layoutLines(self.seqs, self.normalLabelColor)

		if seqOffset + lineWidth >= len(seqs[0]):
			self.nextBlock = None
		else:
			self.nextBlock = SeqBlock(labelCanvas, mainCanvas,
				self, self.font, seqOffset + lineWidth, headers,
				seqs, lineWidth, labelBindings, statusFunc,
				showRuler, treeBalloon, showNumberings,
				self.prefs)

	def activateNode(self, node, callback=None,
					fromPrev=False, fromNext=False):
		active = self.treeNodeMap['active']
		if active == node:
			return
		if active:
			self.labelCanvas.itemconfigure(
					self.treeNodeMap[active], fill='black')
		self.labelCanvas.itemconfigure(
					self.treeNodeMap[node], fill='red')
		self.treeNodeMap['active'] = node
		if not fromPrev and self.prevBlock:
			self.prevBlock.activateNode(node, callback,
								fromNext=True)
		if not fromNext and self.nextBlock:
			self.nextBlock.activateNode(node, callback,
								fromPrev=True)
		if callback and not fromPrev and not fromNext:
			callback(node)

	def addSeqs(self, seqs, pushDown=0):
		self.topY += pushDown
		if self.prevBlock:
			newLabelWidth = self.prevBlock.labelWidth
			newNumberingWidths = self.prevBlock.numberingWidths
			insertIndex = len(self.lines) - len(seqs)
		else:
			insertIndex = len(self.lines)
			self.lines.extend(seqs)
			for i, seq in enumerate(seqs):
				self.lineIndex[seq] = insertIndex + i
			newLabelWidth = self.findLabelWidth(self.font,
							self.emphasisFont)
			newNumberingWidths = self.findNumberingWidths(self.font)
		labelChange = newLabelWidth - self.labelWidth
		self.labelWidth = newLabelWidth
		numberingChanges = [newNumberingWidths[i]
				- self.numberingWidths[i] for i in range(2)]
		self.numberingWidths = newNumberingWidths

		for rulerText in self.rulerTexts:
			self.mainCanvas.move(rulerText,
				labelChange + numberingChanges[0], pushDown)
		self.bottomRulerY += pushDown

		self._moveLines(self.lines[:insertIndex], labelChange,
						numberingChanges[0], pushDown)

		for i, seq in enumerate(seqs):
			self._layoutLine(seq, self.normalLabelColor,
						lineIndex=insertIndex+i)
		push = len(seqs) * (self.fontPixels[1] + self.letterGaps[1])
		pushDown += push
		self._moveLines(self.lines[insertIndex+len(seqs):],
				labelChange, numberingChanges[0], pushDown)
		self.bottomY += pushDown
		if self.nextBlock:
			self.nextBlock.addSeqs(seqs, pushDown=pushDown)

	def _assocResBind(self, item, aseq, index):
		self.mainCanvas.tag_bind(item, '<Enter>', lambda e:
					self._mouseResidue(1, aseq, index))
		self.mainCanvas.tag_bind(item, '<Leave>', lambda e:
					self._mouseResidue(0))

	def assocSeq(self, aseq):
		item = self.labelTexts[aseq]
		self.labelCanvas.itemconfigure(item, font=self._labelFont(aseq))
		if self.hasAssociatedStructures(aseq):
			self._colorizeLabel(aseq)
		else:
			if self.labelRects.has_key(aseq):
				self.labelCanvas.delete(self.labelRects[aseq])
				del self.labelRects[aseq]
		lineItems = self.lineItems[aseq]
		associated = hasattr(aseq, 'matchMaps') and aseq.matchMaps
		for i in range(len(lineItems)):
			item = lineItems[i]
			if associated:
				self._assocResBind(item, aseq, self.seqOffset+i)
			else:
				self.mainCanvas.tag_bind(item, '<Enter>', "")
				self.mainCanvas.tag_bind(item, '<Leave>', "")
		if self.nextBlock:
			self.nextBlock.assocSeq(aseq)
		
	def baseLayoutInfo(self):
		halfX = self.fontPixels[0] / 2
		leftRectOff = 0 - halfX
		rightRectOff = self.fontPixels[0] - halfX
		return halfX, leftRectOff, rightRectOff

	def bboxList(self, line1, line2, pos1, pos2, coverGaps):
		if pos1 >= self.seqOffset + self.lineWidth:
			return self.nextBlock.bboxList(line1, line2, pos1, pos2,
								coverGaps)
		left = max(pos1, self.seqOffset) - self.seqOffset
		right = min(pos2, self.seqOffset + self.lineWidth - 1) \
							- self.seqOffset
		bboxes = []
		if coverGaps:
			bboxes.append(self._boxCorners(left,right,line1,line2))
		else:
			l1 = self.lineIndex[line1]
			l2 = self.lineIndex[line2]
			lmin = min(l1, l2)
			lmax = max(l1, l2)
			for line in self.lines[l1:l2+1]:
				l = None
				for lo in range(left, right+1):
					if line.gapped2ungapped(lo +
							self.seqOffset) is None:
						# gap
						if l is not None:
							bboxes.append(self._boxCorners(l, lo-1, line, line))
							l = None
					else:
						# not gap
						if l is None:
							l = lo
				if l is not None:
					bboxes.append(self._boxCorners(
							l, right, line, line))
							
		if pos2 >= self.seqOffset + self.lineWidth:
			bboxes.extend(self.nextBlock.bboxList(
					line1, line2, pos1, pos2, coverGaps))
		return bboxes

	def _boxCorners(self, left, right, line1, line2):
		ulx = self._leftSeqsEdge() + left * (
				self.letterGaps[0] + self.fontPixels[0]) \
				+ int(left/10) * self.chunkGap
		uly = self.bottomRulerY + self.letterGaps[1] \
				+ self.lineIndex[line1] * (
				self.fontPixels[1] + self.letterGaps[1])
		lrx = self._leftSeqsEdge() - self.letterGaps[0] + (right+1) * (
				self.letterGaps[0] + self.fontPixels[0]) \
				+ int(right/10) * self.chunkGap
		lry = self.bottomRulerY + (self.lineIndex[line2] + 1) * (
				self.fontPixels[1] + self.letterGaps[1])
		if len(self.seqs) == 1:
			prefPrefix = SINGLE_PREFIX
		else:
			prefPrefix = ""
		if self.prefs[prefPrefix + COLUMN_SEP] < -1:
			overlap = int(abs(self.prefs[prefPrefix + COLUMN_SEP]) / 2)
			ulx += overlap
			lrx -= overlap
		return ulx, uly, lrx, lry

	def boundedBy(self, x1, y1, x2, y2):
		end = self.bottomY + self.blockGap
		if y1 > end and y2 > end:
			if self.nextBlock:
				return self.nextBlock.boundedBy(x1, y1, x2, y2)
			else:
				return (None, None, None, None)
		relY1 = self.relativeY(y1)
		relY2 = self.relativeY(y2)
		if relY1 < relY2:
			hiRow = self.rowIndex(relY1, bound="top")
			lowRow = self.rowIndex(relY2, bound="bottom")
		else:
			hiRow = self.rowIndex(relY2, bound="top")
			lowRow = self.rowIndex(relY1, bound="bottom")
		if hiRow is None or lowRow is None:
			return (None, None, None, None)

		if y1 <= end and y2 <= end:
			if y1 > self.bottomY and y2 > self.bottomY \
			or y1 <= self.bottomRulerY and y2 <= self.bottomRulerY:
				# entirely in the same block gap or ruler
				return (None, None, None, None)
			# both on this block; determine right and left...
			leftX = min(x1, x2)
			rightX = max(x1, x2)
			leftPos = self.pos(leftX, bound="left")
			rightPos = self.pos(rightX, bound="right")
		else:
			# the one on this block is left...
			if y1 <= end:
				leftX, rightX, lowY = x1, x2, y2
			else:
				leftX, rightX, lowY = x2, x1, y1
			leftPos = self.pos(leftX, bound="left")
			if self.nextBlock:
				rightPos = self.nextBlock.pos(rightX,
							bound="right", y=lowY)
			else:
				rightPos = self.pos(rightX, bound="right")
		if leftPos is None or rightPos is None or leftPos > rightPos:
			return (None, None, None, None)
		return (self.lines[hiRow], self.lines[lowRow],
							leftPos, rightPos)

	def _colorFunc(self, line):
		try:
			return line.colorFunc
		except AttributeError:
			return lambda l, o: 'black'

	def _colorizeLabel(self, aseq):
		labelText = self.labelTexts[aseq]
		bbox = self.labelCanvas.bbox(labelText)
		if self.labelRects.has_key(aseq):
			labelRect = self.labelRects[aseq]
			self.labelCanvas.coords(labelRect, *bbox)
		else:
			labelRect = self.labelCanvas.create_rectangle(*bbox)
			self.labelCanvas.tag_lower(labelRect, labelText)
			self.labelRects[aseq] = labelRect
		if len(aseq.matchMaps) > 1:
			stipple = ""
			color = ""
			dash = "."
			outline = "dark green"
		else:
			from CGLtk.color import rgba2tk
			color = rgba2tk(aseq.matchMaps.keys()[0].color.rgba())
			stipple= ""
			dash = ""
			outline = ""
		self.labelCanvas.itemconfigure(labelRect, stipple=stipple,
					dash=dash, outline=outline, fill=color)

	def _computeNumbering(self, line, end):
		if end == 0:
			count = len([c for c in line[:self.seqOffset]
						if c.isalpha()])
			if count == len(line.ungapped()):
				count -= 1
		else:
			count = len([c for c in line[:self.seqOffset
				+ self.lineWidth] if c.isalpha()]) - 1
		return line.numberingStart + count

	def destroy(self):
		if self.nextBlock:
			self.nextBlock.destroy()
			self.nextBlock = None
		for rulerText in self.rulerTexts:
			self.mainCanvas.delete(rulerText)
		for labelText in self.labelTexts.values():
			self.labelCanvas.delete(labelText)
		for numberings in self.numberingTexts.values():
			for numbering in numberings:
				if numbering:
					self.mainCanvas.delete(numbering)
		for box in self.treeItems['boxes']:
			self.treeBalloon.tagunbind(self.labelCanvas, box)
		for treeItems in self.treeItems.values():
			for treeItem in treeItems:
				self.labelCanvas.delete(treeItem)
		for labelRect in self.labelRects.values():
			self.labelCanvas.delete(labelRect)
		for lineItems in self.lineItems.values():
			for lineItem in lineItems:
				self.mainCanvas.delete(lineItem)
		
	def findLabelWidth(self, font, emphasisFont):
		labelWidth = 0
		for seq in self.lines:
			name = seqName(seq, self.prefs)
			labelWidth = max(labelWidth, font.measure(name))
			labelWidth = max(labelWidth, emphasisFont.measure(name))
		labelWidth += 3
		return labelWidth

	def findNumberingWidths(self, font):
		lwidth = rwidth = 0
		if self.showNumberings[0]:
			baseNumBlocks = int(len(self.seqs[0]) / self.lineWidth)
			blocks = baseNumBlocks + (baseNumBlocks !=
					len(self.seqs[0]) / self.lineWidth)
			extent = (blocks - 1) * self.lineWidth
			for seq in self.lines:
				if getattr(seq, 'numberingStart', None) == None:
					continue
				offset = len([c for c in seq[:extent]
							if c.isalpha()])
				lwidth = max(lwidth, font.measure(
					"%d " % (seq.numberingStart + offset)))
			lwidth += 3
		if self.showNumberings[1]:
			for seq in self.lines:
				if getattr(seq, 'numberingStart', None) == None:
					continue
				offset = len(seq.ungapped())
				rwidth = max(rwidth, font.measure(
					"  %d" % (seq.numberingStart + offset)))
		return [lwidth, rwidth]

	def fontChange(self, font, emphasisFont=None, pushDown=0):
		self.topY += pushDown
		self.font = font
		if emphasisFont:
			self.emphasisFont = emphasisFont
		else:
			self.emphasisFont = self.font.copy()
			self.emphasisFont.configure(weight=tkFont.BOLD)
		if len(self.seqs) == 1:
			prefPrefix = SINGLE_PREFIX
		else:
			prefPrefix = ""
		if self.prefs[prefPrefix + BOLD_ALIGNMENT]:
			self.font = self.emphasisFont
		if self.prevBlock:
			newLabelWidth = self.prevBlock.labelWidth
			fontPixels = self.prevBlock.fontPixels
			newNumberingWidths = self.prevBlock.numberingWidths
		else:
			newLabelWidth = self.findLabelWidth(font,
							self.emphasisFont)
			w, h = self.measureFont(self.font)
			fontPixels = (w+1, h+1) # allow padding
			newNumberingWidths = self.findNumberingWidths(font)
		labelChange = newLabelWidth - self.labelWidth
		leftNumberingChange = newNumberingWidths[0] \
						- self.numberingWidths[0]
		curWidth, curHeight = self.fontPixels
		newWidth, newHeight = fontPixels

		perLine = newHeight - curHeight
		perChar = newWidth - curWidth

		over = labelChange + leftNumberingChange + perChar / 2
		down = pushDown + perLine
		for rulerText in self.rulerTexts:
			self.mainCanvas.itemconfigure(rulerText, font=font)
			self.mainCanvas.move(rulerText, over, down)
			over += perChar * 10
		self.bottomRulerY += down

		down = pushDown + 2 * perLine
		for line in self.lines:
			labelText = self.labelTexts[line]
			self.labelCanvas.itemconfigure(labelText,
						font=self._labelFont(line))
			self.labelCanvas.move(labelText, 0, down)
			if self.labelRects.has_key(line):
				self._colorizeLabel(line)
			leftNumberingText = self.numberingTexts[line][0]
			if leftNumberingText:
				self.mainCanvas.itemconfigure(leftNumberingText,
								font=font)
				self.mainCanvas.move(leftNumberingText,
					labelChange + leftNumberingChange, down)
			down += perLine

		down = pushDown + 2 * perLine
		histLeft = perChar / 2
		histRight = perChar - histLeft
		for seq in self.lines:
			over = labelChange + leftNumberingChange + perChar / 2
			lineItems = self.lineItems[seq]
			itemAuxInfo = self.itemAuxInfo[seq]
			colorFunc = self._colorFunc(seq)
			depictable = hasattr(seq, 'depictionVal')
			for i in range(len(lineItems)):
				lineItem = lineItems[i]
				oldx, oldy = itemAuxInfo[i]
				itemAuxInfo[i] = (oldx + over, oldy + down)
				if lineItem:
					index = self.seqOffset + i
					if depictable:
						val = seq.depictionVal(index)
					else:
						val = seq[index]
					if isinstance(val, basestring):
						self.mainCanvas.move(lineItem,
								over, down)
						self.mainCanvas.itemconfigure(
							lineItem, font=self.font)
					else:
						x1, y1, x2, y2 = self.\
							mainCanvas.coords(
							lineItem)
						if x1 < x2:
							leftX, rightX = x1, x2
						else:
							leftX, rightX = x2, x1
						if y1 < y2:
							topY, bottomY = y1, y2
						else:
							topY, bottomY = y2, y1
						leftX += over - histLeft
						rightX += over + histRight
						oldHeight = bottomY - topY
						bottomY += down
						topY = bottomY - (newHeight *
								float(oldHeight)
								/ curHeight)
						self.mainCanvas.coords(lineItem,
								leftX, topY,
								rightX, bottomY)

				over += perChar
			rightNumberingText = self.numberingTexts[seq][1]
			if rightNumberingText:
				self.mainCanvas.move(rightNumberingText, over,
									down)
				self.mainCanvas.itemconfigure(
						rightNumberingText, font=font)
			down += perLine
		self.labelWidth = newLabelWidth
		self.fontPixels = fontPixels
		self.bottomY += down
		self.numberingWidths = newNumberingWidths
		if self.nextBlock:
			self.nextBlock.fontChange(font,
				emphasisFont=self.emphasisFont, pushDown=down)

	def _getXs(self, amount):
		xs = []
		halfX, leftRectOff, rightRectOff = self.baseLayoutInfo()
		x = self._leftSeqsEdge() + halfX
		for chunkStart in range(0, amount, 10):
			for offset in range(chunkStart,
						min(chunkStart + 10, amount)):
				xs.append(x)
				x += self.fontPixels[0] + self.letterGaps[0]
			x += self.chunkGap
		return xs

	def hasAssociatedStructures(self, line):
		if hasattr(line, 'matchMaps') \
		and [mol for mol in line.matchMaps.keys() if not mol.__destroyed__]:
			return True
		return False

	def hideHeaders(self, headers, pushDown=0, delIndex=None):
		self.topY += pushDown
		if self.prevBlock:
			newLabelWidth = self.prevBlock.labelWidth
		else:
			# assuming parent function passes us a continuous block
			delIndex = self.lineIndex[headers[0]]
			del self.lines[delIndex:delIndex+len(headers)]
			for line in headers:
				del self.lineIndex[line]
			for line in self.lines[delIndex:]:
				self.lineIndex[line] -= len(headers)
			newLabelWidth = self.findLabelWidth(self.font,
							self.emphasisFont)
		labelChange = newLabelWidth - self.labelWidth
		self.labelWidth = newLabelWidth

		for rulerText in self.rulerTexts:
			self.mainCanvas.move(rulerText, labelChange, pushDown)
		self.bottomRulerY += pushDown

		self._moveLines(self.lines[:delIndex], labelChange, 0, pushDown)

		for line in headers:
			labelText = self.labelTexts[line]
			del self.labelTexts[line]
			self.labelCanvas.delete(labelText)

			lineItems = self.lineItems[line]
			del self.lineItems[line]
			for item in lineItems:
				if item is not None:
					self.mainCanvas.delete(item)
			del self.itemAuxInfo[line]
		pull = len(headers) * (self.fontPixels[1]
							+ self.letterGaps[1])
		pushDown -= pull
		self._moveLines(self.lines[delIndex:], labelChange, 0, pushDown)
		self._moveTree(pushDown)

		self.labelWidth = newLabelWidth
		self.bottomY += pushDown
		if self.nextBlock:
			self.nextBlock.hideHeaders(headers, pushDown=pushDown,
							delIndex=delIndex)

	def _labelFont(self, line):
		if self.hasAssociatedStructures(line):
			return self.emphasisFont
		return self.font

	def layoutRuler(self, rerule=0):
		if rerule:
			for text in self.rulerTexts:
				self.mainCanvas.delete(text)
		self.rulerTexts = []
		if not self.showRuler:
			self.bottomRulerY = self.topY
			return
		x = self._leftSeqsEdge() + self.fontPixels[0]/2
		y = self.topY + self.fontPixels[1] + self.letterGaps[1]

		end = min(self.seqOffset + self.lineWidth, len(self.seqs[0]))
		for chunkStart in range(self.seqOffset, end, 10):
			text = self.mainCanvas.create_text(x, y, anchor='s',
				font=self.font, text="%d" % (chunkStart+1))
			self.rulerTexts.append(text)
			x += self.chunkGap + 10 * (self.fontPixels[0]
							+ self.letterGaps[0])
		if not rerule:
			self.bottomY += self.fontPixels[1] + self.letterGaps[1]
			self.bottomRulerY = y

	def _layoutLine(self, line, labelColor, baseLayoutInfo=None, end=None,
							lineIndex=None):
		if not end:
			end = min(self.seqOffset + self.lineWidth,
							len(self.seqs[0]))
		if baseLayoutInfo:
			halfX, leftRectOff, rightRectOff = baseLayoutInfo
		else:
			halfX, leftRectOff, rightRectOff = self.baseLayoutInfo()

		x = 0
		if lineIndex is None:
			y = self.bottomY + self.fontPixels[1] \
							+ self.letterGaps[1]
		else:
			y = self.bottomRulerY + (lineIndex+1) * (
					self.fontPixels[1] + self.letterGaps[1])

		if hasattr(line, 'labelColor'):
			lColor = line.labelColor
		else:
			lColor = labelColor
		text = self.labelCanvas.create_text(x, y, anchor='sw',
				fill=lColor, font=self._labelFont(line),
				text=seqName(line, self.prefs))
		self.labelTexts[line] = text
		if self.hasAssociatedStructures(line):
			self._colorizeLabel(line)
		bindings = self.labelBindings[line]
		if bindings:
			for eventType, function in bindings.items():
				self.labelCanvas.tag_bind(text,
							eventType, function)
		colorFunc = self._colorFunc(line)
		lineItems = []
		itemAuxInfo = []
		xs = self._getXs(end - self.seqOffset)
		for i in range(end - self.seqOffset):
			item = self.makeItem(line, self.seqOffset + i, xs[i],
				y, halfX, leftRectOff, rightRectOff, colorFunc)
			if hasattr(line, "matchMaps") and line.matchMaps:
				self._assocResBind(item, line,
							self.seqOffset + i)
			lineItems.append(item)
			itemAuxInfo.append((xs[i], y))
			
		self.lineItems[line] = lineItems
		self.itemAuxInfo[line] = itemAuxInfo
		if lineIndex is None:
			self.bottomY += self.fontPixels[1] + self.letterGaps[1]

		numberings = [None, None]
		if line.numberingStart != None:
			for numbering in range(2):
				if self.showNumberings[numbering]:
					numberings[numbering] = \
					self._makeNumbering(line, numbering)
		self.numberingTexts[line] = numberings

	def layoutLines(self, lines, labelColor):
		end = min(self.seqOffset + self.lineWidth, len(self.seqs[0]))
		bli = self.baseLayoutInfo()
		for line in lines:
			self._layoutLine(line, labelColor, bli, end)

	def _layoutTree(self, treeInfo, node, callback, nodesShown,
							prevXpos=None):
		def xFunc(x, delta):
			return 216.0 * (x - 1.0 + delta/100.0)
		def yFunc(y):
			return (self.bottomRulerY + self.letterGaps[1] +
				0.5 * self.fontPixels[1] +
				(y + len(self.lines) - len(self.seqs)) *
				(self.fontPixels[1] + self.letterGaps[1]))
		x = xFunc(node.xPos, node.xDelta)
		y = yFunc(node.yPos)
		lines = self.treeItems['lines']
		if prevXpos is not None:
			lines.append(self.labelCanvas.create_line(
					"%.2f" % prevXpos, y, "%.2f" % x, y))
		if not node.subNodes:
			rightmostX = xFunc(1.0, 0.0)
			if x != rightmostX:
				lines.append(self.labelCanvas.create_line(
					"%.2f" % x, y, "%.2f" % rightmostX, y,
					fill="black", stipple="gray25"))
			return
		subYs = [n.yPos for n in node.subNodes]
		minSubY = min(subYs)
		maxSubY = max(subYs)
		lines.append(self.labelCanvas.create_line(
			"%.2f" % x, yFunc(minSubY), "%.2f" % x, yFunc(maxSubY)))
		if self.treeNodeMap['active'] == node:
			fill = 'red'
		else:
			fill = 'black'
		box = self.labelCanvas.create_rectangle(x-2, y-2,
					x+2, y+2, fill=fill, outline="black")
		self.labelCanvas.tag_bind(box, "<ButtonRelease-1>",
			lambda e, cb=callback, n=node: self.activateNode(n, cb))
		self.treeNodeMap[node] = box
		if node.label:
			balloonText = "%s: " % node.label
		else:
			balloonText = ""
		balloonText += "%d sequences" % node.countNodes("leaf")
		self.treeBalloon.tagbind(self.labelCanvas, box, balloonText)
		self.treeItems['boxes'].append(box)
		if not nodesShown:
			self.labelCanvas.itemconfigure(box, state='hidden')
		for sn in node.subNodes:
			self._layoutTree(treeInfo, sn, callback, nodesShown, x)

	def _leftSeqsEdge(self):
		return self.labelWidth + self.letterGaps[0] \
						+ self.numberingWidths[0]

	def makeItem(self, line, offset, x, y, halfX,
					leftRectOff, rightRectOff, colorFunc):
		if hasattr(line, 'depictionVal'):
			info = line.depictionVal(offset)
		else:
			info = line[offset]
		if isinstance(info, basestring):
			return self.mainCanvas.create_text(x, y, anchor='s',
					font=self.font, fill=colorFunc(line,
					offset), text=info)
		if info != None and info > 0.0:
			topRect = y - info * self.fontPixels[1]
			return self.mainCanvas.create_rectangle(x + leftRectOff,
				topRect, x + rightRectOff, y, width=0,
				outline="", fill=colorFunc(line, offset))
		return None

	def _makeNumbering(self, line, numbering):
		n = self._computeNumbering(line, numbering)
		x, y = self.itemAuxInfo[line][-1]
		if numbering == 0:
			item = self.mainCanvas.create_text(self._leftSeqsEdge(),
				y, anchor='se', font=self.font, text="%d " % n)
		else:
			item = self.mainCanvas.create_text(x +
				self.baseLayoutInfo()[0], y, anchor='sw',
				font=self.font, text="  %d" % n)
		return item

	def measureFont(self, font):
		height = self.font.actual('size')
		if height > 0: # points
			height = self.mainCanvas.winfo_pixels(
							"%gp" % float(height))
		else:
			height = 0 - height

		width = 0
		for let in string.uppercase:
			width = max(width, font.measure(let))
		return (width, height)

	def _molChange(self, seqs):
		for seq in seqs:
			self._colorizeLabel(seq)
		if self.nextBlock:
			self.nextBlock._molChange(seqs)

	def _mouseResidue(self, enter, seq=None, index=None):
		if enter:
			self._mouseID = self.mainCanvas.after(300,
					lambda: self._showResidue(seq, index))
		else:
			if self._mouseID:
				if self._mouseID == "done":
					# only clear the status line if we've
					# put # a residue ID in it previously...
					self.statusFunc("\n")
				else:
					self.mainCanvas.after_cancel(
								self._mouseID)
				self._mouseID = None

	def _moveLines(self, lines, overLabel, overNumber, down):
		over = overLabel + overNumber
		for line in lines:
			self.labelCanvas.move(self.labelTexts[line], 0, down)

			lnum, rnum = self.numberingTexts[line]
			if lnum:
				self.mainCanvas.move(lnum, overLabel, down)
			if rnum:
				self.mainCanvas.move(rnum, over, down)
			for item in self.lineItems[line]:
				if item is not None:
					self.mainCanvas.move(item, over, down)
			itemAuxInfo = []
			for oldx, oldy in self.itemAuxInfo[line]:
				itemAuxInfo.append((oldx+over, oldy+down))
			self.itemAuxInfo[line] = itemAuxInfo
			if self.labelRects.has_key(line):
				self.labelCanvas.move(self.labelRects[line],
								0, down)
	def _moveTree(self, down):
		for itemType, itemList in self.treeItems.items():
			for item in itemList:
				self.labelCanvas.move(item, 0, down)
	def numBlocks(self):
		if self.nextBlock:
			return self.nextBlock.numBlocks() + 1
		return 1

	def pos(self, x, bound=None, y=None):
		"""return 'sequence' position of x"""
		if y is not None and self.nextBlock \
		and y > self.bottomY + self.blockGap:
			return self.nextBlock.pos(x, bound, y)
		if x < self._leftSeqsEdge():
			if bound == "left":
				return self.seqOffset
			elif bound == "right":
				if self.seqOffset > 0:
					return self.seqOffset -1
				else:
					return None
			else:
				return None
		chunk = int((x - self._leftSeqsEdge()) /
			(10 * (self.fontPixels[0] + self.letterGaps[0])
			+ self.chunkGap))
		chunkX = x - self._leftSeqsEdge() - chunk * (
			10 * (self.fontPixels[0] + self.letterGaps[0])
			+ self.chunkGap)
		chunkOffset = int(chunkX / (self.fontPixels[0]
							+ self.letterGaps[0]))
		offset = 10 * chunk + min(chunkOffset, 10)
		myLineWidth = min(self.lineWidth,
					len(self.seqs[0]) - self.seqOffset)
		if offset >= myLineWidth:
			if bound == "left":
				if self.nextBlock:
					return self.seqOffset + myLineWidth
				return None
			elif bound == "right":
				return self.seqOffset + myLineWidth - 1
			return None
		offset = 10 * chunk + min(chunkOffset, 9)
		rightEdge = self._leftSeqsEdge() + \
			chunk * (10 * (self.fontPixels[0]
				+ self.letterGaps[0]) + self.chunkGap) + \
			(chunkOffset + 1) * (self.fontPixels[0] +
					self.letterGaps[0])
		if chunkOffset >= 10 or rightEdge - x < self.letterGaps[0]:
			# in gap
			if bound == "left":
				return self.seqOffset + offset + 1
			elif bound == "right":
				return self.seqOffset + offset
			return None
		# on letter
		return self.seqOffset + offset

	def recolor(self, seq):
		if self.nextBlock:
			self.nextBlock.recolor(seq)

		colorFunc = self._colorFunc(seq)

		for i, lineItem in enumerate(self.lineItems[seq]):
			if lineItem is None:
				continue
			self.mainCanvas.itemconfigure(lineItem,
					fill=colorFunc(seq, self.seqOffset + i))
		
	def refresh(self, seq, left, right):
		if self.seqOffset + self.lineWidth <= right:
			self.nextBlock.refresh(seq, left, right)
		if left >= self.seqOffset + self.lineWidth:
			return
		myLeft = max(left - self.seqOffset, 0)
		myRight = min(right - self.seqOffset, self.lineWidth - 1)

		halfX, leftRectOff, rightRectOff = self.baseLayoutInfo()
		lineItems = self.lineItems[seq]
		itemAuxInfo = self.itemAuxInfo[seq]
		rebind = self.hasAssociatedStructures(seq)
		colorFunc = self._colorFunc(seq)
		for i in range(myLeft, myRight+1):
			lineItem = lineItems[i]
			if lineItem is not None:
				self.mainCanvas.delete(lineItem)
			x, y = itemAuxInfo[i]
			lineItems[i] = self.makeItem(seq, self.seqOffset + i,
						x, y, halfX, leftRectOff,
						rightRectOff, colorFunc)
			if rebind:
				self._assocResBind(lineItems[i], seq,
							self.seqOffset + i)
		if self.showNumberings[0] and seq.numberingStart != None \
							and myLeft == 0:
			self.mainCanvas.delete(self.numberingTexts[seq][0])
			self.numberingTexts[seq][0] = self._makeNumbering(seq,0)
		if self.showNumberings[1] and seq.numberingStart != None \
					and myRight == self.lineWidth - 1:
			self.mainCanvas.delete(self.numberingTexts[seq][1])
			self.numberingTexts[seq][1] = self._makeNumbering(seq,1)
		
	def relativeY(self, rawY):
		"""return the y relative to the block the y is in"""
		if rawY < self.topY:
			if not self.prevBlock:
				return 0
			else:
				return self.prevBlock.relativeY(rawY)
		if rawY > self.bottomY + self.blockGap:
			if not self.nextBlock:
				return self.bottomY - self.topY
			else:
				return self.nextBlock.relativeY(rawY)
		return min(rawY - self.topY, self.bottomY - self.topY)
			
	def realign(self, prevLen):
		"""sequences globally realigned"""

		if shouldWrap(len(self.seqs), self.prefs):
			blockEnd = self.seqOffset + self.lineWidth
		else:
			blockEnd = len(self.seqs[0])
			self.lineWidth = blockEnd
		prevBlockLen = min(prevLen, blockEnd)
		curBlockLen = min(len(self.seqs[0]), blockEnd)

		halfX, leftRectOff, rightRectOff = self.baseLayoutInfo()

		numUnchanged = min(prevBlockLen, curBlockLen) - self.seqOffset
		for line in self.lines:
			lineItems = self.lineItems[line]
			itemAuxInfo = self.itemAuxInfo[line]
			colorFunc = self._colorFunc(line)
			rebind = self.hasAssociatedStructures(line)
			for i in range(numUnchanged):
				item = lineItems[i]
				if item is not None:
					self.mainCanvas.delete(item)
				x, y = itemAuxInfo[i]
				lineItems[i] = self.makeItem(line,
					self.seqOffset + i, x, y, halfX,
					leftRectOff, rightRectOff, colorFunc)
				if rebind:
					self._assocResBind(lineItems[i], line,
							self.seqOffset + i)

		if curBlockLen < prevBlockLen:
			# delete excess items
			self.layoutRuler(rerule=1)
			for line in self.lines:
				lineItems = self.lineItems[line]
				for i in range(curBlockLen, prevBlockLen):
					item = lineItems[i - self.seqOffset]
					if item is None:
						continue
					self.mainCanvas.delete(item)
				start = curBlockLen - self.seqOffset
				end = prevBlockLen - self.seqOffset
				lineItems[start:end] = []
				self.itemAuxInfo[line][start:end] = []
		elif curBlockLen > prevBlockLen:
			# add items
			self.layoutRuler(rerule=1)
			for line in self.lines:
				rebind = self.hasAssociatedStructures(line)
				lineItems = self.lineItems[line]
				itemAuxInfo = self.itemAuxInfo[line]
				x, y = itemAuxInfo[0]
				colorFunc = self._colorFunc(line)
				xs = self._getXs(curBlockLen - self.seqOffset)
				for i in range(prevBlockLen, curBlockLen):
					x = xs[i - self.seqOffset]
					lineItems.append(self.makeItem(line, i,
						x, y, halfX, leftRectOff,
						rightRectOff, colorFunc))
					itemAuxInfo.append((x, y))
					if rebind:
						self._assocResBind(
							lineItems[-1], line, i)

		if len(self.seqs[0]) <= blockEnd:
			# no further blocks
			if self.nextBlock:
				self.nextBlock.destroy()
				self.nextBlock = None
		else:
			# more blocks
			if self.nextBlock:
				self.nextBlock.realign(prevLen)
			else:
				self.nextBlock = SeqBlock(self.labelCanvas,
					self.mainCanvas, self, self.font,
					self.seqOffset + self.lineWidth,
					self.lines[:0-len(self.seqs)],
					self.seqs, self.lineWidth,
					self.labelBindings, self.statusFunc,
					self.showRuler, self.treeBalloon,
					self.showNumberings, self.prefs)

	def rowIndex(self, y, bound=None):
		"""Given a relative y, return the row index"""
		relRulerBottom = self.bottomRulerY - self.topY
		if y <= relRulerBottom:
			# in header
			if bound == "top":
				return 0
			elif bound == "bottom":
				if self.prevBlock:
					return len(self.lines) - 1
				return None
			return None
		row = int((y - relRulerBottom) /
				(self.fontPixels[1] + self.letterGaps[1]))
		if row >= len(self.lines):
			# off bottom
			if bound == "top":
				if self.nextBlock:
					return 0
				return None
			elif bound == "bottom":
				return len(self.lines) - 1
			return None
					
		topY = relRulerBottom + row * (
					self.fontPixels[1] + self.letterGaps[1])
		if y - topY < self.letterGaps[1]:
			# in gap
			if bound == "top":
				return row
			elif bound == "bottom":
				if row > 0:
					return row - 1
				return len(self.lines) - 1
			return None
		# on letter
		return row
	
	def setLeftNumberingDisplay(self, showNumbering):
		if showNumbering == self.showNumberings[0]:
			return
		self.showNumberings[0] = showNumbering
		numberedLines = [l for l in self.lines if getattr(l,
					'numberingStart', None) != None]
		if showNumbering:
			if not self.prevBlock:
				self.numberingWidths[:] = \
					self.findNumberingWidths(self.font)
			delta = self.numberingWidths[0]
			for rulerText in self.rulerTexts:
				self.mainCanvas.move(rulerText, delta, 0)
			for line in numberedLines:
				self.numberingTexts[line][0] = \
						self._makeNumbering(line, 0)
			self._moveLines(self.lines, 0, delta, 0)
		else:
			delta = 0 - self.numberingWidths[0]
			for rulerText in self.rulerTexts:
				self.mainCanvas.move(rulerText, delta, 0)
			for texts in self.numberingTexts.values():
				if not texts[0]:
					continue
				self.mainCanvas.delete(texts[0])
				texts[0] = None
			self._moveLines(self.lines, 0, delta, 0)
			if not self.nextBlock:
				self.numberingWidths[0] = 0
		if self.nextBlock:
			self.nextBlock.setLeftNumberingDisplay(showNumbering)

	def setRightNumberingDisplay(self, showNumbering):
		if showNumbering == self.showNumberings[1]:
			return
		self.showNumberings[1] = showNumbering
		if showNumbering:
			if not self.prevBlock:
				self.numberingWidths[:] = \
					self.findNumberingWidths(self.font)
			numberedLines = [l for l in self.lines if getattr(l,
					'numberingStart', None) != None]
			for line in numberedLines:
				self.numberingTexts[line][1] = \
						self._makeNumbering(line, 1)
		else:
			for texts in self.numberingTexts.values():
				if not texts[1]:
					continue
				self.mainCanvas.delete(texts[1])
				texts[1] = None
			if not self.nextBlock:
				self.numberingWidths[1] = 0
		if self.nextBlock:
			self.nextBlock.setRightNumberingDisplay(showNumbering)

	def setRulerDisplay(self, showRuler, pushDown=0):
		if showRuler == self.showRuler:
			return
		self.showRuler = showRuler
		self.topY += pushDown
		self.bottomY += pushDown
		pull = self.fontPixels[1] + self.letterGaps[1]
		if showRuler:
			pushDown += pull
			self.layoutRuler()
		else:
			for text in self.rulerTexts:
				self.mainCanvas.delete(text)
			pushDown -= pull
			self.bottomRulerY = self.topY
			self.bottomY -= pull
		self._moveLines(self.lines, 0, 0, pushDown)
		self._moveTree(pushDown)
		if self.nextBlock:
			self.nextBlock.setRulerDisplay(showRuler,
							pushDown=pushDown)

	def _showResidue(self, aseq, index):
		self._mouseID = "done"
		ungapped = aseq.gapped2ungapped(index)
		if ungapped is None:
			self.statusFunc("gap\n", blankAfter=0)
			return
		residues = []
		for matchMap in aseq.matchMaps.values():
			try:
				residues.append(matchMap[ungapped])
			except KeyError:
				continue
		if not residues:
			self.statusFunc("no corresponding structure residue\n",
								blankAfter=0)
			return

		self.statusFunc(", ".join(map(lambda m, cl=chimeraLabel:
			cl(m, modelName=1, style="verbose"), residues)) + "\n",
			blankAfter=0)

	def showHeaders(self, headers, pushDown=0):
		self.topY += pushDown
		if self.prevBlock:
			newLabelWidth = self.prevBlock.labelWidth
			insertIndex = len(self.lines) - len(self.seqs) - len(
								headers)
		else:
			insertIndex = len(self.lines) - len(self.seqs)
			self.lines[insertIndex:insertIndex] = headers
			for seq in self.seqs:
				self.lineIndex[seq] += len(headers)
			for i in range(len(headers)):
				self.lineIndex[headers[i]] = insertIndex + i
			newLabelWidth = self.findLabelWidth(self.font,
							self.emphasisFont)
		labelChange = newLabelWidth - self.labelWidth
		self.labelWidth = newLabelWidth

		for rulerText in self.rulerTexts:
			self.mainCanvas.move(rulerText, labelChange, pushDown)
		self.bottomRulerY += pushDown

		self._moveLines(self.lines[:insertIndex], labelChange, 0,
								pushDown)

		for i in range(len(headers)):
			self._layoutLine(headers[i], self.headerLabelColor,
						lineIndex=insertIndex+i)
		push = len(headers) * (self.fontPixels[1]
							+ self.letterGaps[1])
		pushDown += push
		self._moveLines(self.lines[insertIndex+len(headers):],
						labelChange, 0, pushDown)
		self._moveTree(pushDown)
		self.labelWidth = newLabelWidth
		self.bottomY += pushDown
		if self.nextBlock:
			self.nextBlock.showHeaders(headers, pushDown=pushDown)

	def showNodes(self, show):
		if show:
			state = 'normal'
		else:
			state = 'hidden'
		for box in self.treeItems['boxes']:
			self.labelCanvas.itemconfigure(box, state=state)
		if self.nextBlock:
			self.nextBlock.showNodes(show)

	def showTree(self, treeInfo, callback, nodesShown, active=None):
		for box in self.treeItems['boxes']:
			self.treeBalloon.tagunbind(self.labelCanvas, box)
		for treeItems in self.treeItems.values():
			while treeItems:
				self.labelCanvas.delete(treeItems.pop())
		if self.nextBlock:
			self.nextBlock.showTree(treeInfo, callback, nodesShown)
		if not treeInfo:
			return
		self.treeNodeMap = {'active': active}
		self._layoutTree(treeInfo, treeInfo['tree'], callback,
								nodesShown)

	def updateNumberings(self):
		numberedLines = [l for l in self.lines if getattr(l,
					'numberingStart', None) != None]
		for line in numberedLines:
			for i in range(2):
				nt = self.numberingTexts[line][i]
				if not nt:
					continue
				self.mainCanvas.delete(nt)
				self.numberingTexts[line][i] = \
						self._makeNumbering(line, i)
		if self.nextBlock:
			self.nextBlock.updateNumberings()
			
def shouldWrap(numSeqs, prefs):
	if numSeqs == 1:
		prefix = SINGLE_PREFIX
	else:
		prefix = ""
	if prefs[prefix + WRAP_IF]:
		if numSeqs <= prefs[prefix + WRAP_THRESHOLD]:
			return 1
		else:
			return 0
	elif prefs[prefix + WRAP]:
		return 1
	return 0

def seqName(seq, prefs):
	return ellipsisName(seq.name, prefs[SEQ_NAME_ELLIPSIS])

def ellipsisName(name, ellipsisThreshold):
	if len(name) > ellipsisThreshold:
		half = int(ellipsisThreshold/2)
		return name[0:half-1] + "..." + name[len(name)-half:]
	return name
