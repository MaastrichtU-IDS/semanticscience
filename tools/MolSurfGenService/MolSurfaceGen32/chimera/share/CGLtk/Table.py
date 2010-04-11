import Tkinter
import Pmw

class ScrolledTable(Pmw.MegaWidget):
	"""A scrollable table widget that supports titles that stay put.
	
	The widget should be used like a Frame, with sub-widgets added
	using the Grid geometry manager.  Do *not* set the column or
	row weights, unless you like unpredictable results."""

	def __init__(self, parent=None, **kw):

		# Define the megawidget options.
		INITOPT = Pmw.INITOPT
		optiondefs = (
			('horizfraction',  0.05,         INITOPT),
			('hscrollmode',    'dynamic',    INITOPT),
			('labelmargin',    0,            INITOPT),
			('labelpos',       None,         INITOPT),
			('scrollmargin',   2,            INITOPT),
			('vertfraction',   0.05,         INITOPT),
			('vscrollmode',    'dynamic',    INITOPT),
		)
		self.defineoptions(kw, optiondefs,
				dynamicGroups=('Columntitle', 'Rowtitle'))

		# Initialise the base class (after defining the options).
		Pmw.MegaWidget.__init__(self, parent)

		# Create the components.
		interior = Pmw.MegaWidget.interior(self)

		# Create the vertical scrollbar
		self._vsb = self.createcomponent('vertscrollbar',
			(), 'Scrollbar',
			Tkinter.Scrollbar, (interior,),
			orient='vertical', command=self._vScroll
		)
		if self['vscrollmode'] != 'none':
			interior.columnconfigure(4,
						minsize=self['scrollmargin'])
			self._vsb.grid(column=5, row=3, sticky='wns')

		# Create the horizontal scrollbar
		self._hsb = self.createcomponent('horizscrollbar',
			(), 'Scrollbar',
			Tkinter.Scrollbar, (interior,),
			orient='horizontal', command=self._hScroll
		)
		if self['hscrollmode'] != 'none':
			interior.rowconfigure(4, minsize=self['scrollmargin'])
			self._hsb.grid(column=3, row=5, sticky='new')

		# Create the column clipper
		self._colClipper = self.createcomponent('columnclipper',
			(), 'Titleclipper',
			Tkinter.Frame, (interior,), bd=0)
		self._colClipper.grid(column=3, row=2, sticky='w')

		# Create the column frame
		self._colFrame = self.createcomponent('columnframe',
			(), 'Titleframe',
			Tkinter.Frame, (self._colClipper,), bd=0)
		self._colFrame.place(x=0, y=0)

		# Create the row clipper
		self._rowClipper = self.createcomponent('rowclipper',
			(), 'Titleclipper',
			Tkinter.Frame, (interior,), bd=0)
		self._rowClipper.grid(column=2, row=3, sticky='n')

		# Create the row frame
		self._rowFrame = self.createcomponent('rowframe',
			(), 'Titleframe',
			Tkinter.Frame, (self._rowClipper,), bd=0)
		self._rowFrame.place(x=0, y=0)

		# Create the main content clipper
		self._clipper = self.createcomponent('clipper',
			(), None,
			Tkinter.Frame, (interior,), bd=0)
		self._clipper.grid(column=3, row=3, sticky='nsew')

		# Create the main content frame
		self._frame = self.createcomponent('frame',
			(), None,
			Tkinter.Frame, (self._clipper,), bd=0)
		self._frame.grid(column=1, row=1, sticky='nsew')

		interior.columnconfigure(3, weight=1)
		interior.rowconfigure(3, weight=1)

		self.createlabel(interior, childCols=4, childRows=4)

		self._colTitles = {}
		self._rowTitles = {}

		if self['hscrollmode'] == 'dynamic' \
		and self['vscrollmode'] == 'dynamic':
			self.__config = self._configureXY
		elif self['vscrollmode'] == 'dynamic':
			self.__config = self._configureY
		elif self['hscrollmode'] == 'dynamic':
			self.__config = self._configureX
		else:
			self.__config = self._configureFixed
		self._reqwidth = 0
		self._reqheight = 0

		self._clipper.bind('<Configure>', self._configure)
		self._frame.bind('<Configure>', self._configureContent)

		self.initialiseoptions(ScrolledTable)

	def columnTitles(self, withKw=0):
		"""Return the column titles (a dictionary of column=>title).
		
		If 'withKw', the dictionary value is a 2-tuple of the title
		and the keyword dictionary used for title-widget construction.
		Also, in this case textvariable titles haven't been massaged
		into strings."""

		return self._titles(self._colTitles, withKw)

	def setColumnTitle(self, column, title, **kw):
		"Set the title for a column (column index starts at 0)."
		self._setTitle(self._colTitles, column, title, kw)

	def rowTitles(self, withKw=0):
		"""Return the row titles (a dictionary of row=>title).
		
		If 'withKw', the dictionary value is a 2-tuple of the title
		and the keyword dictionary used for title-widget construction.
		Also, in this case textvariable titles haven't been massaged
		into strings."""

		return self._titles(self._rowTitles, withKw)

	def setRowTitle(self, row, title, **kw):
		"Set the title for a row (row index starts at 0)."
		self._setTitle(self._rowTitles, row, title, kw)

	def showTitles(self):
		"Show row/column titles of an empty table"
		self._updateColumnLabels(force=1)
		self._updateRowLabels(force=1)

	def _setTitle(self, dict, key, value, kw):
		if value:
			dict[key] = (value, kw)
		else:
			try:
				del dict[key]
			except KeyError:
				pass

	def _configureContent(self, event):
		if event.width == self._reqwidth \
		and event.height == self._reqheight:
			return
		self._reqwidth = event.width
		self._reqheight = event.height
		self._configure(event, reuse=0)

	def _configure(self, event, reuse=1):
		reqWidth = self._frame.winfo_reqwidth()
		reqHeight = self._frame.winfo_reqheight()
		w, h = self.__config(reqWidth, reqHeight)
		if self['vscrollmode'] != 'none':
			vStart = self._vsb.get()[-2]
			self._height = float(reqHeight)
			self._vScale = h / self._height
			self._vScroll('moveto', str(vStart))
		if self['hscrollmode'] != 'none':
			hStart = self._hsb.get()[-2]
			self._width = float(reqWidth)
			self._hScale = w / self._width
			self._hScroll('moveto', str(hStart))
		self._updateColumnLabels(force=1, reuse=reuse)
		self._updateRowLabels(force=1, reuse=reuse)

	def _configureXY(self, reqWidth, reqHeight):
		# both scrollbars are automatic

		# never map/unmap more than one scrollbar at a time in
		# this routine.  Since each mapping/unmapping will cause
		# a Configure callback, we want to have the 'ismapped'
		# states accurately reflect the Configure event fields.
		# This won't be true if we do multiple mappings between
		# Configure events.
		clipW = maxW = self._clipper.winfo_width()
		clipH = maxH = self._clipper.winfo_height()
		if self._vsb.winfo_ismapped():
			maxW = maxW + self._vsb.winfo_reqwidth()
		if self._hsb.winfo_ismapped():
			maxH = maxH + self._hsb.winfo_reqheight()

		if reqHeight > maxH:
			if self._vsb.winfo_ismapped():
				maxW = clipW
			else:
				maxW = (clipW - self._vsb.winfo_reqwidth())
				self._vsb.grid(column=5, row=3, sticky='wns')
				return maxW, maxH
			if reqWidth > maxW:
				if self._hsb.winfo_ismapped():
					maxH = clipH
				else:
					maxH = (clipH
						- self._hsb.winfo_reqheight())
					self._hsb.grid(column=3, row=5,
								sticky='new')
			else:
				self._hsb.grid_forget()
		elif reqWidth > maxW:
			if self._hsb.winfo_ismapped():
				maxH = clipH
			else:
				maxH = (clipH - self._hsb.winfo_reqheight())
				self._hsb.grid(column=3, row=5, sticky='new')
				return maxW, maxH
			if reqHeight > maxH:
				if self._vsb.winfo_ismapped():
					maxW = clipW
				else:
					maxW = (clipW
						- self._vsb.winfo_reqwidth())
					self._vsb.grid(column=5, row=3,
								sticky='wns')
			else:
				self._vsb.grid_forget()
		else:
			if self._vsb.winfo_ismapped():
				self._vsb.grid_forget()
			else:
				self._hsb.grid_forget()
		return maxW, maxH

	def _configureY(self, reqWidth, reqHeight):
		# vertical scrollbar is automatic, horizontal is not
		clipW = maxW = self._clipper.winfo_width()
		clipH = self._clipper.winfo_height()
		if reqHeight > clipH:
			if not self._vsb.winfo_ismapped():
				maxW = (clipW - self._vsb.winfo_reqwidth())
				self._vsb.grid(column=5, row=3, sticky='wns')
		else:
			self._vsb.grid_forget()
		return maxW, clipH

	def _configureX(self, reqWidth, reqHeight):
		# horizontal scrollbar is automatic, vertical is not
		clipW = self._clipper.winfo_width()
		clipH = maxH = self._clipper.winfo_height()
		if reqWidth > clipW:
			if not self._hsb.winfo_ismapped():
				maxH = (clipH - self._hsb.winfo_reqheight())
				self._hsb.grid(column=3, row=5, sticky='new')
		else:
			self._hsb.grid_forget()
		return clipW, maxH

	def _configureFixed(self, reqWidth, reqHeight):
		# neither scrollbar is automatic
		clipW = self._clipper.winfo_width()
		clipH = self._clipper.winfo_height()
		return clipW, clipH

	def _titles(self, titleDict, withKw):
		# if returning keywords, assume rebuilding titles is
		# desired, therefore don't massage textvarible titles
		# into strings
		if withKw:
			from copy import copy
			return copy(titleDict)

		ret = {}
		for k, v in titleDict.items():
			title = v[0]
			if not isinstance(title, basestring):
				# textvariable
				title = title.get()
			ret[k] = title
		return ret

	def _updateColumnLabels(self, force=0, reuse=0):
		if not reuse:
			for component in self.components():
				if component[:6] == "column" \
				and component[6].isdigit():
					self.destroycomponent(component)
		maxHeight = 0
		totalWidth = 0
		cols, rows = self._frame.grid_size()
		if force and self._colTitles:
			cols = max(self._colTitles.keys()) + 1
		for c in range(cols):
			slaves = self._frame.grid_slaves(column=c)
			if not slaves:
				width = 0
			else:
				width = max(map(lambda s: s.winfo_reqwidth(),
									slaves))
			self._colFrame.columnconfigure(c, minsize=width)
			if slaves or self._colTitles.has_key(c):
				if not self._colTitles.has_key(c):
					self._colTitles[c] = ("", {})
				text, userkw = self._colTitles[c]
				kw = {}
				if not userkw.has_key('pyclass'):
					kw.update({
						'bd': 2,
						'relief': 'groove'
					})
				kw.update(userkw)
				if isinstance(text, basestring):
					kw['text'] = text
				else:
					kw['textvariable'] = text
				componentName = "column%d" % c
				if reuse:
					try:
						title = self.component(
								componentName)
					except KeyError:
						title = None
				if not reuse or title == None:
					title = apply(self.createcomponent,
						(componentName, (),
						"Columntitle", Tkinter.Label,
						(self._colFrame,)), kw)
					title.grid(row=0, column=c, sticky='ew')
				titleWidth = title.winfo_reqwidth()
				titleHeight = title.winfo_reqheight()
				if titleHeight > maxHeight:
					maxHeight = titleHeight
			else:
				titleWidth = 0
			if titleWidth > width:
				self._frame.columnconfigure(c,
							minsize=titleWidth)
				totalWidth = totalWidth + titleWidth
			else:
				self._frame.columnconfigure(c, minsize=0)
				totalWidth = totalWidth + width
		if cols > 0 and totalWidth == 0:
			self._frame.update_idletasks()
			self._updateColumnLabels()
			return
		self._colClipper.config(height=maxHeight, width=totalWidth)

	def _updateRowLabels(self, force=0, reuse=0):
		if not reuse:
			for component in self.components():
				if component[:3] == "row" \
				and component[3].isdigit():
					self.destroycomponent(component)
		maxWidth = 0
		totalHeight = 0
		cols, rows = self._frame.grid_size()
		if force and self._rowTitles:
			rows = max(self._rowTitles.keys()) + 1
		for r in range(rows):
			slaves = self._frame.grid_slaves(row=r)
			if not slaves:
				height = 0
			else:
				height = max(map(lambda s: s.winfo_reqheight(),
									slaves))
			self._rowFrame.rowconfigure(r, minsize=height)
			if self._rowTitles.has_key(r):
				text, userkw = self._rowTitles[r]
				kw = {}
				if not userkw.has_key('pyclass'):
					kw.update({
						'bd': 2,
						'relief': 'groove'
					})
				kw.update(userkw)
				if isinstance(text, basestring):
					kw['text'] = text
				else:
					kw['textvariable'] = text
				componentName = "row%d" % r
				if reuse:
					try:
						title = self.component(
								componentName)
					except KeyError:
						title = None
				if not reuse or title == None:
					title = apply(self.createcomponent,
						(componentName, (), "Rowtitle",
						Tkinter.Label,
						(self._rowFrame,)), kw)
					title.grid(row=r, column=0, sticky='ew')
				titleHeight = title.winfo_reqheight()
				titleWidth = title.winfo_reqwidth()
				if titleWidth > maxWidth:
					maxWidth = titleWidth
			else:
				titleHeight = 0
			if titleHeight > height:
				self._frame.rowconfigure(r, minsize=titleHeight)
				totalHeight = totalHeight + titleHeight
			else:
				totalHeight = totalHeight + height
		if rows > 0 and totalHeight == 0:
			self._frame.update_idletasks()
			self._updateColumnLabels()
			return
		self._rowClipper.config(width=maxWidth, height=totalHeight)

	def _vScroll(self, cmd, *args):
		s, e = self._scroll(cmd, self._vScale, self._vsb, args,
							self['vertfraction'])
		y = -int(self._height * s)
		self._rowFrame.place(y=y)
		self._frame.place(y=y)
		return s, e

	def _hScroll(self, cmd, *args):
		s, e = self._scroll(cmd, self._hScale, self._hsb, args,
							self['horizfraction'])
		x = -int(self._width * s)
		self._colFrame.place(x=x)
		self._frame.place(x=x)
		return s, e

	def _scroll(self, cmd, scale, sb, args, fract):
		if cmd == 'moveto':
			start = float(args[0])
		elif cmd == 'scroll':
			start = sb.get()[-2]
			if args[1] == 'units':
				start = start + float(args[0]) * scale * fract
			elif args[1] == 'pages':
				start = start + float(args[0]) * scale
		if start < 0:
			start = 0
		if scale > 1:
			start = 0
			end = 1
		else:
			end = start + scale
			if end > 1:
				end = 1
				start = end - scale
		sb.set(start, end)
		return start, end

	def interior(self):
		return self._frame
	
import Tkinter
class SortableTable(Tkinter.Frame):
	""" typically you addColumn()s, setData(), and launch()

	    however if you saved state with getRestoreInfo(), you just setData()
	    and then launch() with the restoreInfo keyword

	    'automultilineHeaders' controls whether header titles can be 
	    automatically split into multiple lines on word boundaries

	    'allowUserSorting' controls whether mouse clicks on column
	    headers will sort the columns.

	    'menuInfo', if provided, should be a (menu, pref dict,
	    defaults dict, fallback default) tuple.
	    The menu will be populated with checkbutton entries as columns
	    are added, controlling what columns are displayed.  The pref dict
	    will be used to store displayed column preferences (under the key
	    "SortableTable info"). The defaults dict controls whether the
	    column is shown by default (i.e. if the addColumn() 'display'
	    keyword is omitted).  The dictionary should have column titles
	    as keys and booleans as values (True = displayed). The fallback
	    default is used if the column isn't in the dictionary.
	"""
	PREF_KEY = "SortableTable info"
	def __init__(self, master, automultilineHeaders=True, menuInfo=None,
						allowUserSorting=True):
		self.tixTable = None
		self.data = None
		self.columns = []
		self.sorting = None
		self.allowUserSorting = allowUserSorting
		self.automultilineHeaders = automultilineHeaders
		self.menuInfo = menuInfo
		Tkinter.Frame.__init__(self, master)
		try:
			from chimera import chimage
			self.upArrow = chimage.get("uparrow.png", self)
			self.downArrow = chimage.get("downarrow.png", self)
		except ImportError:
			self.upArrow = "^"
			self.downArrow = "v"
		self._sortCache = None
		self._lastBrowseSel = None
		self._highlighted = []
		self._widgetData = {}

	def addColumn(self, title, dataFetch, format="%s", display=None,
			titleDisplay=True, anchor='center', wrapLength=0,
			font='TkTextFont', headerPadX=None, headerPadY=None,
			entryPadX=None, entryPadY=None):
		"""if format is the type bool, use column of checkbuttons;
		   if format is a tuple, then use a color well; the tuple
		   should be two booleans: None okay, alpha okay.
		"""
		titles = [c.title for c in self.columns]
		if title in titles:
			return self.columns[titles.index(title)]
		if display == None:
			if self.menuInfo:
				menu, prefDict, displayDefaults, fallback \
								= self.menuInfo
				lookup = prefDict.get(self.PREF_KEY,
							displayDefaults)
				display = lookup.get(title, fallback)
			else:
				display = True
		c = SortableColumn(title, dataFetch, format, titleDisplay,
			anchor, wrapLength, font, headerPadX, headerPadY,
			entryPadX, entryPadY)

		if display != c.display:
			self.columnUpdate(c, display=display)
		self.columns.append(c)
		self.refresh(rebuild=True)
		if self.menuInfo:
			self._addColumnMenuEntry(c, display)
		return c

	def columnUpdate(self, column, **kw):
		if column._update(**kw):
			self.refresh(rebuild=True)

	def destroy(self):
		self.data = self._sortCache = self.userBrowseCmd = None
		if self.tixTable:
			self.tixTable.destroy()
		Tkinter.Frame.destroy(self)
		
	def getRestoreInfo(self):
		"""return info needed for 'restoreInfo' arg of launch()"""
		saveSorting = self.sorting
		if saveSorting:
			sortCol, forward = saveSorting
			saveSorting = (self.columns.index(sortCol), forward)
		return (4, saveSorting,
			[int(s) for s in self.tixTable.hlist.info_selection()],
			[c._getRestoreInfo() for c in self.columns],
			self.highlightedIndices(),
			(self.title, self.titleFont, self.titleSticky))

	def launch(self, browseCmd=None, selectMode="extended", restoreInfo=None,
				title=None, titleFont="TkHeadingFont", titleSticky="ew"):
		self.userBrowseCmd = browseCmd
		self.selectMode = selectMode
		if restoreInfo:
			version = restoreInfo[0]
			if version == 1:
				(version, sorting, selection,
					columnInfo) = restoreInfo
			elif version in [2,3]:
				(version, sorting, selection,
					columnInfo, highlight) = restoreInfo
			elif version == 4:
				(version, sorting, selection,
					columnInfo, highlight, titleInfo) = restoreInfo
				title, titleFont, titleSticky = titleInfo
			if version < 3:
				for header, fetch, format, display in columnInfo:
					self.addColumn(header, fetch, format=format,
								display=display)
			elif version == 3:
				for header, fetch, format, display, anchor in columnInfo:
					self.addColumn(header, fetch, format=format,
								display=display, anchor=anchor)
			else:
				for header, fetch, format, display, anchor, font in columnInfo:
					self.addColumn(header, fetch, format=format,
								display=display, anchor=anchor, font=font)
			if sorting:
				colIndex, forward = sorting
				col = self.columns[colIndex]
				self.sortBy(col)
				if not forward:
					self.sortBy(col)
			sortData = self._sortedData()
			sel = [sortData[i] for i in selection]
		else:
			sel = None
		self.title, self.titleFont, self.titleSticky = \
								title, titleFont, titleSticky
		if self.title == None:
			self.tableRow = 0
		else:
			self.tableRow = 1
			import Tkinter
			self.titleLabel = Tkinter.Label(self, text=title, font=titleFont)
			self.titleLabel.grid(row=0, column=0, sticky=titleSticky)
		self.columnconfigure(0, weight=1)
		self.rowconfigure(self.tableRow, weight=1)
		self._constructEmptyTable()
		self.refresh(selection=sel)
		self.requestFullWidth()
		if restoreInfo:
			if version == 2:
				self.highlight([sortData[i] for i in highlight])

	def refresh(self, selection=None, rebuild=False):
		if not self.tixTable:
			return
		# cull dead data
		liveData = [d for d in self.data
				if not getattr(d, '__destroyed__', False)]
		if len(liveData) != len(self.data):
			self.setData(liveData)
			return
		if selection is None:
			selection = self._selected()
		if rebuild:
			self._constructEmptyTable()
		else:
			self.tixTable.hlist.delete_all()
		for datum, column, widget in self._widgetData.values():
			widget.destroy()
		self._widgetData.clear()
		hlist = self.tixTable.hlist
		for colNum, column in enumerate([c for c in self.columns
								if c.display]):
			hlist.header_create(colNum, itemtype='window',
				style=column.headerStyle,
				window=self._columnHeader(hlist, column))
		# data in the sorting column may have changed...
		self._sortCache = None
		sortData = self._sortedData()
		for row, datum in enumerate(sortData):
			for col, column in enumerate([c for c in self.columns
								if c.display]):
				contents = column.displayValue(datum)
				if col == 0:
					hlist.add(row)
				if type(contents) == bool:
					but = Tkinter.Checkbutton(hlist,
						command=lambda r=row, c=col:
						self._widgetCB(r, c),
						indicatoron=False,
						borderwidth=0, image=
						self._ckButImage(contents))
					self._widgetData[(row, col)] = (datum,
								column, but)
					hlist.item_create(row, col,
						itemtype="window", window=but,
						style=column.checkButtonStyle)
				elif isinstance(contents, basestring):
					hlist.item_create(row, col,
							itemtype="text",
							style=column.textStyle,
							text=contents)
				else:
					color, noneOkay, alphaOkay = contents
					from color.ColorWell import ColorWell
					if hasattr(color, 'rgba') \
					or color == None:
						from chimera \
							import MaterialColor
						cval = color.rgba()
						cb = lambda clr, r=row, c=col:\
							self._widgetCB(r, c,
							newVal=MaterialColor(
							*clr))
					else:
						cval = color
						cb = lambda clr, r=row, c=col:\
							self._widgetCB(r, c,
							newVal=clr)
					well = ColorWell(hlist, cval,
						callback=cb, width=18,
						height=18, noneOkay=noneOkay,
						wantAlpha=alphaOkay)
					self._widgetData[(row, col)] = (datum,
								column, well)
					hlist.item_create(row, col,
						itemtype="window", window=well,
						style=column.colorWellStyle)
		for s in selection:
			if s in sortData:
				hlist.selection_set(sortData.index(s))

	def select(self, selection):
		sortData = self._sortedData()
		hlist = self.tixTable.hlist
		hlist.selection_clear()
		if self.selectMode in ["single", "browse"]:
			selection = [selection]
		for s in selection:
			if s in sortData:
				hlist.selection_set(sortData.index(s))

	def selected(self):
		sortedData = self._sortedData()
		retVals = [sortedData[int(s)]
				for s in self.tixTable.hlist.info_selection()]
		if self.selectMode in ["single", "browse"]:
			if retVals:
				return retVals[0]
			else:
				return None
		return retVals

	def setData(self, data):
		if self.tixTable:
			curSel = self._selected()
		else:
			curSel = []
		self.data = data[:]
		self._sortCache = None
		dataSet = set([id(v) for v in data])
		self._highlighted = []
		remSel = [i for i in curSel if id(i) in dataSet]
		self.refresh(selection=remSel)
		if len(curSel) != len(remSel):
			self._browseCmd(None)

	def sortBy(self, column):
		if self.tixTable:
			selection = self._selected()
		else:
			selection = None
		if self.sorting:
			sortCol, forward = self.sorting
			if column == sortCol:
				self.sorting = (column, not forward)
			else:
				self.sorting = (column, True)
		else:
			self.sorting = (column, True)
		self._sortCache = None
		self.refresh(selection=selection)

	def highlight(self, hlList):
		sortData = self._sortedData()
		old = set([sortData.index(hl) for hl in self._highlighted])
		new = set([sortData.index(hl) for hl in hlList])
		if old == new:
			return
		hlist = self.tixTable.hlist
		if hlist is None:
			return
		removeList = old - new
		addList = new - old
		clist = [c for c in self.columns if c.display]
		for row in removeList:
			for col,column in enumerate(clist):
				hlist.item_configure(row, col,
						style=column.textStyle)
		for row in addList:
			for col,column in enumerate(clist):
				hlist.item_configure(row, col,
						style=column.highlightStyle)
		self._highlighted = hlList

	def highlighted(self):
		return self._highlighted

	def highlightedIndices(self):
		sortData = self._sortedData()
		return [sortData.index(hl) for hl in self._highlighted]

	def _addColumnMenuEntry(self, col, display):
		# use a variable (and hold a reference)
		# so that we can have the checkbutton 'on' initially
		import Tkinter
		if not hasattr(self, '_vars'):
			self._vars = []
		menu, prefDict, displayDefaults, fallback = self.menuInfo
		v = Tkinter.IntVar(menu)
		self._vars.append(v)
		v.set(display)
		menu.add_checkbutton(label=col.title, variable=v,
				command=lambda c=col: self._colDispChange(c))

	def _browseCmd(self, tixArg):
		if not self.userBrowseCmd:
			return
		# prevent multiple callbacks if selection doesn't change
		# during browse
		curSel = self._selected()
		if self._lastBrowseSel != None \
		and curSel == self._lastBrowseSel:
			return
		self._lastBrowseSel = curSel
		self.userBrowseCmd(self.selected())

	def _ckButImage(self, val):
		if val:
			imageName = "ck_on"
		else:
			imageName = "ck_off"
		return self.tixTable.tk.call("tix", "getimage", imageName)

	def _colDispChange(self, col):
		self.columnUpdate(col, display=not col.display)
		menu, prefDict, displayDefaults, fallback = self.menuInfo
		displayStates = {}
		for c in self.columns:
			displayStates[c.title] = c.display
		prefDict[self.PREF_KEY] = displayStates

	def _columnHeader(self, hlist, column):
		frame = Tkinter.Frame(hlist)
		l1 = Tkinter.Label(frame, text=self._headerText(column),
							takefocus=True)
		l1.grid(row=0, column=0)
		frame.columnconfigure(0, weight=1)
		if self.allowUserSorting:
			command = lambda e, c=column: self.sortBy(c)
			l1.bind("<ButtonRelease>", command)
			if self.sorting:
				sortColumn, forward = self.sorting
				if sortColumn == column:
					if forward:
						image = self.upArrow
					else:
						image = self.downArrow
					if isinstance(image, str):
						l2 = Tkinter.Label(frame,
								text=image)
					else:
						l2 = Tkinter.Label(frame,
								image=image)
					l2.grid(row=0, column=1)
					l2.bind("<ButtonRelease>", command)
		return frame

	def _constructEmptyTable(self):
		if self.tixTable:
			self.tixTable.grid_forget()
			self.tixTable.destroy()
		clist = [c for c in self.columns if c.display]
		import Tix
		self.tixTable = t = Tix.ScrolledHList(self, options=
			"""hlist.columns %d
			hlist.header 1
			hlist.selectMode %s
			hlist.indicator 0""" % (len(clist), self.selectMode))
		t.grid(row=self.tableRow, column=0, sticky="nsew")
		t.hlist.config(browsecmd=self._browseCmd)

	def requestFullWidth(self):
		clist = [c for c in self.columns if c.display]
		if clist:
			# Attempt to display table full width.
			h = self.tixTable.hlist
			w = sum([int(h.column_width(c)) +
				 2*int(col.textStyle['padx'])
				 for c,col in enumerate(clist)])
			import tkFont
			fw = tkFont.Font(font=h.cget('font')).measure('0')
			h.configure(width = w/fw)

	def _headerText(self, column):
		if not column.titleDisplay:
			return ""
		rawText = column.title
		if not self.automultilineHeaders:
			return rawText
		words = rawText.strip().split()
		if len(words) < 2:
			return rawText
		longest = max([len(w) for w in words])
		while True:
			bestDiff = bestIndex = None
			for i in range(len(words)-1):
				w1, w2 = words[i:i+2]
				curDiff = max(abs(longest - len(w1)),
						abs(longest - len(w2)))
				diff = abs(longest - len(w1) - len(w2) - 1)
				if diff >= curDiff:
					continue
				if bestDiff == None or diff < bestDiff:
					bestDiff = diff
					bestIndex = i
			if bestDiff == None:
				break
			words[bestIndex:bestIndex+2] = [" ".join(
						words[bestIndex:bestIndex+2])]
		return '\n'.join(words)
	
	def _selected(self):
		sel = self.selected()
		if not isinstance(sel, (list, tuple)):
			if sel:
				sel = [sel]
			else:
				sel = []
		return sel

	def _sortedData(self):
		if self._sortCache:
			return self._sortCache
		if self.sorting:
			sortData = self.data[:]
			sortColumn, forward = self.sorting
			sortData.sort(lambda d1, d2: cmp(sortColumn.value(d1),
							sortColumn.value(d2)))
			if not forward:
				sortData.reverse()
		else:
			sortData = self.data
		self._sortCache = sortData
		return sortData

	def _widgetCB(self, row, col, newVal=None):
		datum, column, widget = self._widgetData[(row, col)]
		if column.displayFormat == bool:
			newVal = not column.value(datum)
			column.setValue(datum, newVal)
			widget.configure(image=self._ckButImage(newVal))
		else:
			column.setValue(datum, newVal)

class SortableColumn:
	def __init__(self, title, dataFetch, displayFormat, titleDisplay,
			anchor, wrapLength, font, headerPadX, headerPadY,
			entryPadX, entryPadY):
		self.title = title
		self._setFetch(dataFetch)
		self.displayFormat = displayFormat
		self.display = True
		self.anchor = anchor
		self.titleDisplay = titleDisplay
		if headerPadX == None:
			headerPadX = 0
		if headerPadY == None:
			headerPadY = 0
		if entryPadX == None:
			textPadX = ".05i"
			wellPadX = checkButtonPadX = 0
		else:
			textPadX = wellPadX = checkButtonPadX = entryPadX
		if entryPadY == None:
			textPadY = wellPadY = checkButtonPadY = 0
		else:
			textPadY = wellPadY = checkButtonPadY = entryPadY

		# find the family and size of the default fixed font
		import tkFont
		fontInfo = tkFont.Font(font=font).actual()
		family, size = fontInfo['family'], fontInfo['size']
		if isinstance(font, basestring):
			self.font = font
		else:
			self.font = (family, size)
		import Tix
		self.textStyle = Tix.DisplayStyle("text", anchor=anchor,
			font=(family, size), wraplength=wrapLength,
			padx=textPadX, pady=textPadY)
		self.highlightStyle = Tix.DisplayStyle("text", anchor=anchor,
			font=(family, size, "bold"), wraplength=wrapLength,
			padx=textPadX, pady=textPadY)
		self.checkButtonStyle = Tix.DisplayStyle("window",
			anchor=anchor, padx=checkButtonPadX, pady=checkButtonPadY)
		self.colorWellStyle = Tix.DisplayStyle("window",
			anchor=anchor, padx=wellPadX, pady=wellPadY)
		self.headerStyle = Tix.DisplayStyle("window", anchor=anchor,
			padx=headerPadX, pady=headerPadY)
	
	def displayValue(self, instance):
		val = self.value(instance)
		if isinstance(self.displayFormat, basestring):
			if val is None:
				return ""
			return self.displayFormat % val
		elif isinstance(self.displayFormat, tuple):
			return (val,) + self.displayFormat
		return val

	def value(self, instance):
		if callable(self.dataFetch):
			return self.dataFetch(instance)
		fetched = instance
		try:
			for fetch in self.dataFetch.split('.'):
				fetched = getattr(fetched, fetch)
		except AttributeError:
			return None
		return fetched

	def setValue(self, instance, val):
		if callable(self.dataFetch):
			raise ValueError("Don't know how to set values for"
				" column %s" % self.title)
		fields = self.dataFetch.split('.')
		for fetch in fields[:-1]:
			instance = getattr(instance, fetch)
		setattr(instance, fields[-1], val)

	def _getRestoreInfo(self):
		if callable(self._saveableFetch):
			raise ValueError("%s column is not saveable due to"
				" directly callable fetch value" % self.title)
		return (self.title, self._saveableFetch, self.displayFormat,
							self.display, self.anchor, self.font)

	def _setFetch(self, dataFetch):
		if getattr(self, "_saveableFetch", None) == dataFetch:
			return False
		self._saveableFetch = self.dataFetch = dataFetch
		# some attributes may just happen to have the same name
		# as built-in functions (e.g. "id"), so don't eval pure
		# alphanumeric strings...
		if not (isinstance(dataFetch, basestring)
						and dataFetch.isalnum()):
			try:
				self.dataFetch = eval(dataFetch)
			except:
				pass
		return True

	def _update(self, dataFetch=None, format=None, display=None):
		changed = False
		if dataFetch != None:
			changed = self._setFetch(dataFetch)
		if format != None and format != self.displayFormat:
			self.displayFormat = format
			changed = True
		if display != None and display != self.display:
			self.display = display
			changed = True
		return changed

if __name__ == '__main__':
	app = Tkinter.Frame(width=200, height=300)
	app.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)
	nextRow = 10
	def addRow():
		global nextRow
		for col in range(11):
			label = Tkinter.Label(table.interior(),
					text='R:%d, C:%d' % (nextRow, col),
					bd=2, relief=Tkinter.SUNKEN)
			label.grid(column=col, row=nextRow, sticky='ew')
		nextRow = nextRow + 1
	b = Tkinter.Button(app, text='Add Row', command=addRow)
	b.pack()
	table = ScrolledTable(app)
	table.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)
	for row in range(10):
		for col in range(11):
			label = Tkinter.Label(table.interior(),
						text='R:%d, C:%d' % (row, col),
						bd=2, relief=Tkinter.SUNKEN)
			label.grid(column=col, row=row, sticky='ew')
	for col in range(5):
		table.setColumnTitle(col, 'Column %d' % col)
	for row in range(8):
		table.setRowTitle(row, 'Row %d' % row)
	app.mainloop()
