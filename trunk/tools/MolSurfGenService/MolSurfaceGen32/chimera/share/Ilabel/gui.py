# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 29220 2009-11-03 21:21:58Z pett $

import chimera
from chimera import tkgui, chimage, CLOSE_SESSION
from chimera.mousemodes import getFuncName, setButtonFunction, addFunction
from chimera.baseDialog import ModelessDialog
from SimpleSession import SAVE_SESSION, BEGIN_RESTORE_SESSION
from PIL import Image
import Tkinter
import Pmw

from Label import Character

class IlabelDialog(ModelessDialog):
	name = "2D Labels/Color Key"
	provideStatus = True
	buttons = ("Delete", "Close")

	LABELS = "Labels"
	COLOR_KEY = "Color Key"

	MOUSE_LABEL_TEXT = "Use mouse for label placement"
	MOUSE_KEY_TEXT = "Use mouse for key placement"

	EmphasisColor = "forest green"

	def __init__(self):
		import os.path
		myDir, junk = os.path.split(__file__)
		addFunction('place text', (self._pickLabel, self._moveLabel,
			None), icon=chimage.get(Image.open(os.path.join(myDir,
						'ilabel.png')), tkgui.app))
		addFunction('place key', (self._startOrGrabKey,
			self._sizeOrMoveKey, None), icon=chimage.get(
			Image.open(os.path.join(myDir, 'key.png')), tkgui.app))

		import Ilabel
		if not Ilabel._ilabelModel:
			Ilabel.IlabelModel()
		self.model = Ilabel._ilabelModel
		ModelessDialog.__init__(self)
		self._sessionHandlerID = chimera.triggers.addHandler(
					SAVE_SESSION, self._saveSession, None)
		self._closeHandlerID = chimera.triggers.addHandler(
					CLOSE_SESSION, self.destroy, None)
		self._beginRestoreHandlerID = chimera.triggers.addHandler(
				BEGIN_RESTORE_SESSION, self.destroy, None)
	
	def fillInUI(self, parent):
		top = parent.winfo_toplevel()
		menubar = Tkinter.Menu(top, type="menubar", tearoff=False)
		top.config(menu=menubar)

		self.fileMenu = Tkinter.Menu(menubar)
		menubar.add_cascade(label="File", menu=self.fileMenu)
		self.fileMenu.add_command(label="Write...", command=self._writeFileCB)
		self.fileMenu.add_command(label="Read...", command=self._readFileCB)
		from chimera.tkgui import aquaMenuBar
		aquaMenuBar(menubar, parent, row=0)

		from ColorKey import KeyModel
		parent.rowconfigure(1, weight=1)
		parent.columnconfigure(0, weight=1)
		# _pageRaisedCB uses mouseModeVar, so define first
		self.mouseLabelingVar = Tkinter.IntVar(parent)
		self.mouseLabelingVar.set(True)
		self.mlLabelVar = Tkinter.StringVar(parent)
		self.mouseModeButton = Tkinter.Checkbutton(parent,
					command=self._mouseFuncCB,
					variable=self.mouseLabelingVar,
					textvariable=self.mlLabelVar)
		self.mouseModeButton.grid(row=2, column=0)
		self.notebook = Pmw.NoteBook(parent,
					raisecommand=self._pageRaisedCB)
		self.notebook.add(self.LABELS, tab_text=self.LABELS)
		self.notebook.add(self.COLOR_KEY, tab_text=self.COLOR_KEY)
		self.notebook.grid(row=1, column=0, sticky="nsew")
		self._fillLabelsPage(self.notebook.page(self.LABELS))
		self.keyModel = KeyModel(self)
		self.keyPosition = None
		self._fillColorKeyPage(self.notebook.page(self.COLOR_KEY))

	def _fillLabelsPage(self, page):
		page.columnconfigure(0, weight=1)
		page.columnconfigure(1, weight=1)
		page.columnconfigure(2, weight=1)

		row = 0
		from CGLtk.Table import SortableTable
		self.labelTable = SortableTable(page, automultilineHeaders=False)
		self.labelTable.addColumn("Label [(x, y) text]", self._labelListing,
			anchor='w')
		self.labelTable.addColumn("Shown", "shown", format=bool)
		self.labelTable.setData(self.model.labels)
		self.labelTable.launch(browseCmd=self._tableCB, selectMode="single")
		self.labelTable.grid(row=row, column=0, columnspan=3, sticky="nsew")
		page.rowconfigure(row, weight=1)
		row += 1

		self.labelText = Pmw.ScrolledText(page, labelpos='w',
			label_text="Text", text_height=3, text_width=20,
			text_wrap='none', text_state='disabled',
			text_exportselection=False)
		text = self.labelText.component('text')
		text.bind("<<Modified>>", self._textCB)
		text.bind("<<Selection>>", self._updateTextAttrWidgets)
		self.labelText.grid(row=row, column=0,
						sticky='nsew', columnspan=3)
		page.rowconfigure(row, weight=1)
		row += 1

		self.labelSymbolMenu = Pmw.OptionMenu(page, labelpos='w',
			label_text="Insert symbol:", command=self._insertSymbol,
			items=[
				u'\N{GREEK SMALL LETTER ALPHA}',
				u'\N{GREEK SMALL LETTER BETA}',
				u'\N{GREEK SMALL LETTER GAMMA}',
				u'\N{GREEK SMALL LETTER DELTA}',
				u'\N{GREEK SMALL LETTER EPSILON}',
				u'\N{GREEK SMALL LETTER PI}',
				u'\N{GREEK SMALL LETTER PHI}',
				u'\N{GREEK SMALL LETTER CHI}',
				u'\N{GREEK SMALL LETTER PSI}',
				u'\N{GREEK SMALL LETTER OMEGA}',
				u'\N{LEFTWARDS ARROW}',
				u'\N{RIGHTWARDS ARROW}',
				u'\N{LEFT RIGHT ARROW}',
				u'\N{UPWARDS ARROW}',
				u'\N{DOWNWARDS ARROW}',
				u'\N{SUPERSCRIPT TWO}',
				u'\N{SUPERSCRIPT THREE}',
				u'\N{DEGREE SIGN}',
				u'\N{LATIN CAPITAL LETTER A WITH RING ABOVE}',
				"more..."
			])
		self.labelSymbolMenu.grid(row=row, column=0, columnspan=3)

		row += 1

		colorHouse = Pmw.LabeledWidget(page, labelpos='w',
			label_text="Color")
		colorHouse.grid(row=row, column=0, rowspan=3)
		from CGLtk.color.ColorWell import ColorWell
		self.colorWell = ColorWell(colorHouse.interior(),
			color=self._contrastWithBG(), callback=self._colorCB)
		self.colorWell.grid()

		from chimera.tkoptions import IntOption
		self.labelFontSize = IntOption(page, row, "Font size", 24,
					self._labelChangeCB, startCol=1, min=1,
					attribute="size", width=3)
		row += 1
		self.labelFontStyle = FontStyle(page, row, "Font style",
			oglFont.normal, self._labelChangeCB, startCol=1)
		row += 1
		self.labelFontTypeface = FontTypeface(page, row, "Font typeface",
					FONT_TYPEFACE_VALUES[0],
					self._labelChangeCB, startCol=1)
		row += 1

		if self.model.curLabel:
			self.changeToLabel(self.model.curLabel, force=True)

	def _fillColorKeyPage(self, page):
		from chimera.tkoptions import IntOption, EnumOption, \
						BooleanOption, RGBAOption
		f = Tkinter.Frame(page)
		f.grid(row=0, columnspan=2)
		self.numComponents = IntOption(f, 0, "Number of colors/labels",
					3, self._componentsCB, min=2, width=2)
		self.componentsFrame = Tkinter.Frame(page)
		self.componentsFrame.grid(row=1, column=0, sticky="nsew",
							columnspan=2)
		page.columnconfigure(0, weight=1)
		self.componentsFrame.columnconfigure(1, weight=1)
		class ColorTreatment(EnumOption):
			values = ("distinct", "blended")
		self.colorTreatment = ColorTreatment(page, 2,
			"Color range depiction", "blended", self._keyChangeCB,
			balloon="Should colors be shown as distinct rectangles"
			" or as a continuous range")
		class LabelPosition(EnumOption):
			values = ("left/top", "right/bottom")
		self.labelPos = LabelPosition(page, 3, "Label positions",
			"right/bottom", self._keyChangeCB, balloon="Position of"
			" labels relative to color key.\nLabels always"
			" positioned adjacent to long side.")
		self.labelColor = RGBAOption(page, 4, "Label color",
			self._contrastWithBG(), self._keyChangeCB, balloob=
			"Label color.  If set to 'No color', use corresponding"
			" key color", noneOkay=True)
		class LabelJustification(EnumOption):
			values = ("left", "decimal point", "right")
		self.justification = LabelJustification(page, 5,
			"Label justification", "decimal point",
			self._keyChangeCB, balloon="Justification of label text"
			" in a vertical key layout.\nHorizontal key labels will"
			" always be center justified.")
		self.labelOffset = IntOption(page, 6, "Label offset", 0,
			self._keyChangeCB, width=3, balloon="Additional offset"
			" of labels from color bar, in pixels")
		self.keyFontSize = IntOption(page, 7, "Font size", 24,
			self._keyChangeCB, width=3)
		self.keyFontStyle = FontStyle(page, 8, "Font style",
			oglFont.normal, self._keyChangeCB)
		self.keyFontTypeface = FontTypeface(page, 9, "Font typeface",
			FONT_TYPEFACE_VALUES[0], self._keyChangeCB)
		self.borderColor = RGBAOption(page, 10, "Border color",
			None, self._keyChangeCB, balloon="Color of border"
			" around color key (not each individual color).\n"
			"If 'no color', then no border is drawn.")
		self.borderWidth = IntOption(page, 11, "Border width", 3,
			self._keyChangeCB, balloon="in pixels")
		self.tickMarks = BooleanOption(page, 12, "Show tick marks",
			False, self._keyChangeCB, balloon="Show tick marks"
			" pointing from key to labels")
		self._componentsCB(self.numComponents)

	def destroy(self, *args):
		self.mouseLabelingVar.set(True)
		self.mouseModeButton.invoke()
		chimera.triggers.deleteHandler(SAVE_SESSION,
							self._sessionHandlerID)
		chimera.triggers.deleteHandler(CLOSE_SESSION,
							self._closeHandlerID)
		chimera.triggers.deleteHandler(BEGIN_RESTORE_SESSION,
						self._beginRestoreHandlerID)
		chimera.openModels.close([self.model, self.keyModel])
		ModelessDialog.destroy(self)

	def map(self, e=None):
		self._pageRaisedCB(self.notebook.getcurselection())

	def unmap(self, e=None):
		self.mouseLabelingVar.set(True)
		self.mouseModeButton.invoke()

	def changeToLabel(self, nextLabel, force=False):
		if nextLabel == self.model.curLabel and not force:
			return
		if self.model.curLabel and not unicode(self.model.curLabel) \
		and self.model.curLabel != nextLabel:
			# remove previous label if empty
			self.removeLabel(self.model.curLabel)
		self.model.changeToLabel(nextLabel)
		self.labelText.component('text').configure(state='normal')
		self.labelTable.select(nextLabel)
		self.labelText.settext(unicode(nextLabel))
		text = self.labelText.component('text')
		lineIndex = 1
		for line in self.model.curLabel.lines:
			charIndex = 0
			for c in line:
				text.tag_add(id(c),
					"%d.%d" % (lineIndex, charIndex))
				charIndex += 1
			text.tag_add(id(line), "%d.%d" % (lineIndex, charIndex))
			lineIndex += 1
				
	def Delete(self):
		if self.notebook.getcurselection() == self.LABELS:
			self.labelText.clear()
			if not self.model.curLabel:
				self.status("No label to delete", color="red",
								blankAfter=10)
				return
			self.removeLabel(self.model.curLabel)
			self.labelText.component('text').configure(
							state='disabled')
		else:
			self.keyPosition = None
			self._keyChangeCB()

	def Help(self):
		helpLoc = "ContributedSoftware/2dlabels/2dlabels.html"
		if self.notebook.getcurselection() == self.COLOR_KEY:
			helpLoc += "#colorkey"
		chimera.help.display(helpLoc)

	def keyConfigure(self, data, pageChange=True):
		self._componentsCB(len(data), update=False)
		for datum, well, label in zip(data, self.wells, self.labels):
			color, text = datum
			well.showColor(color, doCallback=False)
			label.variable.set(text, invoke_callbacks=False)
		self._keyChangeCB()
		if pageChange:
			self.notebook.selectpage(self.COLOR_KEY)

	def makeChar(self, char, model):
		attrs = {}
		try:
			attrs['rgba'] = self.colorWell.rgba
		except AttributeError: # multi or None
			if model:
				attrs['rgba'] = model.rgba
		size = self.labelFontSize.get()
		if size is not None:
			attrs['size'] = size
		style = self.labelFontStyle.get()
		if style is not None:
			attrs['style'] = style
		fontName = self.labelFontTypeface.get()
		if fontName is not None:
			attrs['fontName'] = fontName
		return Character(char, **attrs)

	def newLabel(self, pos):
		label = self.model.newLabel(pos)
		self.labelTable.setData(self.model.labels)
		self.status("Mouse drag to reposition label",
						color=self.EmphasisColor)
		return label

	def removeLabel(self, label):
		self.model.removeLabel(label)
		self.labelTable.setData(self.model.labels)
		if self.model.curLabel is not None:
			self.labelTable.select(self.model.curLabel)

	def reverseKey(self):
		data = zip([w.rgba for w in self.wells],
				[l.variable.get() for l in self.labels])
		data.reverse()
		self.keyConfigure(data)
	def setLabelFromText(self):
		curLabel = self.model.curLabel
		text = self.labelText.component('text')
		# delete parts of label not in text...
		#
		# newlines first...
		while len(curLabel.lines) > 1:
			for i, line in enumerate(curLabel.lines[:-1]):
				if not text.tag_ranges(id(line)):
					curLabel.lines[i+1][:0] = line
					del curLabel.lines[i]
					break
			else:
				break
		# characters...
		for line in curLabel.lines:
			for c in line[:]:
				if not text.tag_ranges(id(c)):
					line.remove(c)
		
		# get new parts of text into label
		model = None
		targets = []
		lines = curLabel.lines
		for line in lines:
			targets.extend([id(c) for c in line])
			if not model and line:
				model = line[0]
			if line is not lines[-1]:
				targets.append(id(line))
		contents = self.labelText.get()[:-1] # drop trailing newline

		if targets:
			target = targets.pop(0)
		else:
			target = None

		textLine = 1
		textIndex = -1
		curLine = lines[0]
		for c in contents:
			textIndex += 1
			if str(target) in text.tag_names("%d.%d"
						% (textLine, textIndex)):
				if targets:
					target = targets.pop(0)
				else:
					target = None
				if c == '\n':
					textLine += 1
					textIndex = -1
					curLine = lines[[id(l)
							for l in lines].index(
							id(curLine))+1]
				elif curLine:
					model = curLine[textIndex]
			elif c == '\n':
				insertLine = curLine[0:textIndex]
				lines.insert(textLine-1, insertLine)
				del curLine[0:textIndex]
				text.tag_add(id(insertLine), "%d.%d"
							% (textLine, textIndex))
				textLine += 1
				textIndex = -1
			else:
				labelChar = self.makeChar(c, model)
				curLine.insert(textIndex, labelChar)
				text.tag_add(id(labelChar), "%d.%d"
							% (textLine, textIndex))
		self.model.setMajorChange()

	def updateGUI(self, source="gui"):
		curLabel = self.model.curLabel
		if curLabel and source == "gui":
			self.setLabelFromText()
		self.labelTable.setData(self.model.labels)
		if curLabel:
			self.labelTable.select(curLabel)
		self._updateTextAttrWidgets()

	def _colorCB(self, color):
		curLabel = self.model.curLabel
		if not curLabel:
			self.status("No label to color", color='red')
			return
		self.model.setMajorChange()
		for c in self._selChars():
			c.rgba = color

	def _componentsCB(self, opt, update=True):
		cf = self.componentsFrame
		if hasattr(self, 'wells'):
			for well in self.wells:
				well.grid_forget()
				well.destroy()
			for label in self.labels:
				label.frame.grid_forget()
			self.reverseButton.grid_forget()
			self.reverseButton.destroy()
		else:
			Tkinter.Label(cf, text="Colors").grid(row=0)
			Tkinter.Label(cf, text="Labels").grid(row=0, column=1)
		if isinstance(opt, int):
			numComponents = opt
			self.numComponents.set(opt)
		else:
			numComponents = opt.get()
		wellSize = min(38, int( (7 * 38) / numComponents ))
		from CGLtk.color.ColorWell import ColorWell
		self.wells = []
		self.labels = []
		from CGLtk import Hybrid
		for i in range(numComponents):
			well = ColorWell(cf, width=wellSize, height=wellSize,
				callback=self._keyChangeCB, color='white')
			well.grid(row=i+1)
			self.wells.append(well)
			label = Hybrid.Entry(cf, "", 10)
			label.variable.add_callback(self._keyTypingCB)
			label.frame.grid(row=i+1, column=1, sticky='ew')
			self.labels.append(label)
		self.reverseButton = Tkinter.Button(cf, command=self.reverseKey,
				text="Reverse ordering of above", pady=0)
		self.reverseButton.grid(row=numComponents+1, column=0,
								columnspan=2)
		self.notebook.setnaturalsize()
		if update:
			self._keyChangeCB()

	def _contrastWithBG(self):
		bg = chimera.viewer.background
		if bg:
			bgColor = bg.rgba()
		else:
			bgColor = (0, 0, 0)
		if bgColor[0]*2 + bgColor[1]*3 + bgColor[2] < 0.417:
			return (1, 1, 1)
		else:
			return (0, 0, 0)

	def _eventToPos(self, viewer, event, offset = (0, 0)):
		w, h = viewer.windowSize
		return (event.x - offset[0]) / float(w), \
				(h - event.y - offset[1]) / float(h)
		
	def _handleTextChange(self):
		self.updateGUI()
		self.labelText.edit_modified(False)

	def _insertSymbol(self, item):
		if len(item) > 1:
			from chimera import help
			help.display("ContributedSoftware/2dlabels/symbols.html")
			return
		if not self.model.labels:
			self.status("No labels have been created yet", color="red")
			return
		if not self.labelTable.selected():
			self.status("No labels active", color="red")
		self.labelText.insert("insert", item)
		self.setLabelFromText()

	def _keyChangeCB(self, *args):
		self.keyModel.setMajorChange()

	def _keyTypingCB(self, fromAfter=False):
		# wait for a pause in typing before updating key...
		if fromAfter:
			self._typingHandler = None
			self._keyChangeCB()
			return
		handle = getattr(self, '_typingHandler', None)
		if handle:
			self.componentsFrame.after_cancel(handle)
		self._typingHandler = self.componentsFrame.after(500,
				lambda: self._keyTypingCB(fromAfter=True))

	def _labelChangeCB(self, option):
		curLabel = self.model.curLabel
		self.model.setMajorChange()
		val = option.get()
		attrName = option.attribute
		for c in self._selChars():
			setattr(c, attrName, val)

	def _labelListing(self, label):
		text = unicode(label)
		if '\n' in text:
			newline = text.index('\n')
			text= text[:newline] + "..." 
		if not text:
			text = "<empty>"
		return "(%.2f, %.2f) %s" % (label.pos[0], label.pos[1], text)

	def _mouseFuncCB(self):
		self.status("")
		if not self.mouseLabelingVar.get():
			if hasattr(self, "_prevMouse"):
				setButtonFunction("1", (), self._prevMouse)
				delattr(self, "_prevMouse")
		elif self.mlLabelVar.get() == self.MOUSE_LABEL_TEXT:
			if not hasattr(self, "_prevMouse"):
				self._prevMouse = getFuncName("1", ())
			setButtonFunction("1", (), "place text")
		else:
			if not hasattr(self, "_prevMouse"):
				self._prevMouse = getFuncName("1", ())
			setButtonFunction("1", (), "place key")

	def _moveLabel(self, viewer, event):
		pos = self._eventToPos(viewer, event, self._moveOffset)
		self.model.moveLabel(pos)
		curLabel = self.model.curLabel
		self.labelTable.setData(self.model.labels)
		self.labelTable.select(curLabel)
		
	def _pageRaisedCB(self, pageName):
		if pageName == "Labels":
			pageItem = self.MOUSE_LABEL_TEXT
			if not self.model.labels:
				self.status("Click mouse button 1 in graphics\n"
						"window to place first label",
						color=self.EmphasisColor)
			for index in range(0, self.fileMenu.index('end')+1):
				self.fileMenu.entryconfigure(index, state='normal')
		else:
			pageItem = self.MOUSE_KEY_TEXT
			self.status("Drag mouse to position/size key",
						color=self.EmphasisColor)
			for index in range(0, self.fileMenu.index('end')+1):
				self.fileMenu.entryconfigure(index, state='disabled')
		self.mlLabelVar.set(pageItem)
		# just setting the var doesn't cause the callback, and
		# yet using invoke() toggles the var, so set it _opposite_
		# to what's desired before calling invoke()
		self.mouseLabelingVar.set(False)
		self.mouseModeButton.invoke()
		
	def _pickLabel(self, viewer, event):
		w, h = viewer.windowSize
		pos = self._eventToPos(viewer, event)
		label, self._moveOffset = self.model.pickLabel(pos, w, h)
		if label is None:
			label = self.newLabel(pos)
			self._moveOffset = (0, 0)
		self.changeToLabel(label)
		self.labelText.component('text').focus_set()

	def _readFile(self, okayed, dialog):
		if not okayed:
			return
		from Ilabel import readFiles
		readFiles(dialog.getPaths(), clear=dialog.deleteExistingVar.get())

	def _readFileCB(self):
		if not hasattr(self, "_readFileDialog"):
			self._readFileDialog = ReadFileDialog(
				command=self._readFile, clientPos='s')
		self._readFileDialog.enter()

	def _restoreSession(self, info):
		if info["sel ranges"]:
			self.labelText.tag_add("sel", *info["sel ranges"])
		self._updateTextAttrWidgets()
		self._suppressMap = True
		self.labelText.edit_modified(False)
		if "key position" not in info:
			self.notebook.selectpage(self.LABELS)
			if info["mouse func"] == "normal":
				self.mouseLabelingVar.set(True)
				self.mouseModeButton.invoke()
			return
		self.keyPosition = info["key position"]
		self.colorTreatment.set(info["color depiction"])
		self.labelPos.set(info["label positions"])
		self.labelColor.set(info["label color"])
		self.justification.set(info["label justification"])
		self.labelOffset.set(info["label offset"])
		self.keyFontSize.set(info["font size"])
		self.keyFontStyle.set(info["font typeface"])
		if "font name" in info:
			self.keyFontTypeface.set(info["font name"])
		self.borderColor.set(info["border color"])
		self.borderWidth.set(info["border width"])
		self.tickMarks.set(info["show ticks"])
		self.keyConfigure(info["colors/labels"])
		if self.keyPosition:
			self.notebook.selectpage(self.COLOR_KEY)
		else:
			self.notebook.selectpage(self.LABELS)
		if info["mouse func"] == "normal":
			self.mouseLabelingVar.set(True)
			self.mouseModeButton.invoke()
		return info

	def _saveSession(self, triggerName, myData, sessionFile):
		print>>sessionFile, """
def restore2DLabelDialog(info):
	from chimera.dialogs import find, display
	from Ilabel.gui import IlabelDialog
	dlg = find(IlabelDialog.name)
	if dlg is not None:
		dlg.destroy()
	dlg = display(IlabelDialog.name)
	dlg._restoreSession(info)

import SimpleSession
SimpleSession.registerAfterModelsCB(restore2DLabelDialog, %s)

""" % repr(self._sessionInfo())

	def _selChars(self):
		chars = []
		curLabel = self.model.curLabel
		if curLabel:
			sel = self.labelText.tag_ranges("sel")
			if sel:
				sline, schar = [int(x)
					for x in str(sel[0]).split('.')]
				eline, echar = [int(x)
					for x in str(sel[1]).split('.')]
				sline -= 1
				eline -= 1
				for li, line in enumerate(curLabel.lines):
					if li < sline:
						continue
					if li > eline:
						break
					if sline == eline:
						chars.extend(line[schar:echar])
					elif li == sline:
						chars.extend(line[schar:])
					elif li == eline:
						chars.extend(line[:echar])
					else:
						chars.extend(line)
			else:
				for l in curLabel.lines:
					chars.extend(l)
		return chars

	def _sessionInfo(self):
		info = {}
		info["sel ranges"] = tuple([str(tr)
				for tr in self.labelText.tag_ranges("sel")])
		if self.mouseLabelingVar.get():
			info["mouse func"] = "labeling"
		else:
			info["mouse func"] = "normal"
		info["key position"] = self.keyPosition
		info["colors/labels"] = [(w.rgba, l.variable.get())
				for w, l in zip(self.wells, self.labels)]
		info["color depiction"] = self.colorTreatment.get()
		info["label positions"] = self.labelPos.get()
		info["label color"] = self.labelColor.get()
		info["label justification"] = self.justification.get()
		info["label offset"] = self.labelOffset.get()
		info["font size"] = self.keyFontSize.get()
		info["font typeface"] = self.keyFontStyle.get()
		info["font name"] = self.keyFontTypeface.get()
		info["border color"] = self.borderColor.get()
		info["border width"] = self.borderWidth.get()
		info["show ticks"] = self.tickMarks.get()
		return info

	def _sizeOrMoveKey(self, viewer, event):
		pos = self._eventToPos(viewer, event)
		if self.grabPos:
			deltas = [pos[axis] - self.grabPos[axis]
							for axis in [0, 1]]
			for posIndex in [0, 1]:
				old = self.keyPosition[posIndex]
				self.keyPosition[posIndex] = (
					old[0] + deltas[0], old[1] + deltas[1])
			self.grabPos = pos
		elif len(self.keyPosition) == 1:
			self.keyPosition.append(pos)
		else:
			self.keyPosition[1] = pos
		self._keyChangeCB()
		
	def _startOrGrabKey(self, viewer, event):
		pos = self._eventToPos(viewer, event)
		if self.keyPosition and len(self.keyPosition) == 2:
			# possible grab;
			# see if in middle third of long side...
			p1, p2 = self.keyPosition
			x1, y1 = p1
			x2, y2 = p2
			if abs(x2 - x1) < abs(y2 - y1):
				longAxis = 1
				ymin = min(y2, y1)
				ymax = max(y2, y1)
				b1 = (2* ymin + ymax) / 3.0
				b2 = (2* ymax + ymin) / 3.0
				o1 = min(x1, x2)
				o2 = max(x1, x2)
			else:
				longAxis = 0
				xmin = min(x2, x1)
				xmax = max(x2, x1)
				b1 = (2* xmin + xmax) / 3.0
				b2 = (2* xmax + xmin) / 3.0
				o1 = min(y1, y2)
				o2 = max(y1, y2)
			if b1 < pos[longAxis] < b2 \
			and o1 < pos[1-longAxis] < o2:
				self.grabPos = pos
				return
		self.grabPos = None
		self.keyPosition = [pos]
		self._keyChangeCB()
		self.status("Grab middle of key to reposition",
						color=self.EmphasisColor)

	def _tableCB(self, sel):
		if not sel:
			return
		self.changeToLabel(sel)

	def _textCB(self, e):
		text = self.labelText.component('text')
		if not text.tk.call((text._w, 'edit', 'modified')):
		#if not text.edit_modified():
			return
		# this callback can happen _before_ the change
		# actually occurs, so do the processing after idle
		text.after_idle(self._handleTextChange)

	def _updateTextAttrWidgets(self, e=None):
		rgba = None
		multiple = False
		for c in self._selChars():
			if rgba is None:
				rgba = c.rgba
			elif rgba != c.rgba:
				multiple = True
				break
		if rgba is not None:
			self.colorWell.showColor(rgba, multiple=multiple,
							doCallback=False)
			self.labelFontSize.display(self._selChars())
			self.labelFontStyle.display(self._selChars())
			self.labelFontTypeface.display(self._selChars())

	def _writeFile(self, okayed, dialog):
		if not okayed:
			return
		from Ilabel import writeFile
		writeFile(dialog.getPaths()[0])

	def _writeFileCB(self):
		if not hasattr(self, "_writeFileDialog"):
			from OpenSave import SaveModeless
			self._writeFileDialog = SaveModeless(command=self._writeFile,
				title="Write 2D Labels Info")
		self._writeFileDialog.enter()

from chimera.tkoptions import SymbolicEnumOption
oglFont = chimera.OGLFont
from Ilabel import FONT_STYLE_LABELS, FONT_STYLE_VALUES
class FontStyle(SymbolicEnumOption):
	attribute = "style"
	labels = FONT_STYLE_LABELS
	values = FONT_STYLE_VALUES

from Ilabel import FONT_TYPEFACE_LABELS, FONT_TYPEFACE_VALUES
class FontTypeface(SymbolicEnumOption):
	attribute = "fontName"
	labels = FONT_TYPEFACE_LABELS
	values = FONT_TYPEFACE_VALUES

from OpenSave import OpenModeless
class ReadFileDialog(OpenModeless):
	title="Read 2D Labels Info"

	def fillInUI(self, parent):
		OpenModeless.fillInUI(self, parent)
		self.deleteExistingVar = Tkinter.IntVar(parent)
		self.deleteExistingVar.set(False)
		Tkinter.Checkbutton(self.clientArea, variable=self.deleteExistingVar,
			text="Delete existing labels").grid()
		
from chimera import dialogs
dialogs.register(IlabelDialog.name, IlabelDialog)
