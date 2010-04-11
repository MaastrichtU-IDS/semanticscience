# --- UCSF Chimera Copyright ---
# Copyright (c) 2004 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: FilterDialog.py 26655 2009-01-07 22:02:30Z gregc $

from sets import Set
import Pmw, Tkinter

from chimera.baseDialog import ModelessDialog
from Compound import Compound

class FilterDialog(ModelessDialog):
	
	title = "ViewDock Choose by Value"
	help = "ContributedSoftware/viewdock/viewdock.html#filter"

	def __init__(self, viewdock, *args, **kw):
		self.viewdock = viewdock
		self.results = viewdock.results
		self.compounds = Set()
		self.selected = None
		self.valueCache = {}
		self._isMapped = False
		self._colAddHandler = None
		self._colDelHandler = None
		self._colUpdHandler = None
		self._needChangeCompounds = False
		ModelessDialog.__init__(self, *args, **kw)
		self._exitHandler = self.viewdock.triggers.addHandler(
						self.viewdock.EXIT,
						self._exit, None)
		self._cpdChgHandler = self.viewdock.triggers.addHandler(
						self.viewdock.COMPOUND_STATE_CHANGED,
						self._compoundStateChanged,
						None)

	def fillInUI(self, parent):
		self.columns = []	# Names of columns
		self.columnMap = {}	# Column name-to-instance map
		parent.winfo_toplevel().bind("<Map>", self._map)
		parent.winfo_toplevel().bind("<Unmap>", self._unmap)
		parent.columnconfigure(0, weight=10)
		g = Pmw.Group(parent, tag_text="Choose from")
		g.grid(row=0, column=0, sticky="ew")
		self.varV = Tkinter.IntVar(parent)
		self.varV.set(1)
		self.buttonV = Tkinter.Checkbutton(g.interior(),
						variable=self.varV,
						text="Viable",
						command=self.changeCompounds)
		self.buttonV.pack(side="left", expand=1, fill="x")
		self.varD = Tkinter.IntVar(parent)
		self.varD.set(0)
		self.buttonD = Tkinter.Checkbutton(g.interior(),
						variable=self.varD,
						text="Deleted",
						command=self.changeCompounds)
		self.buttonD.pack(side="left", expand=1, fill="x")
		self.varP = Tkinter.IntVar(parent)
		self.varP.set(0)
		self.buttonP = Tkinter.Checkbutton(g.interior(),
						variable=self.varP,
						text="Purged",
						command=self.changeCompounds)
		self.buttonP.pack(side="left", expand=1, fill="x")
		self.label = Tkinter.Label(parent, text="")
		self.label.grid(row=1, column=0)
		self.firstRow = 2
		self.parent = parent
		self.updateCompounds()
		self.updateChosen()

	def updateColumns(self):
		columns = self.results.getColumns()
		columns.sort()
		if columns == self.columns:
			return
		self.columns = columns
		self.updateFilters()

	def updateFilters(self):
		row = self.firstRow
		for k in self.columns:
			c = self._getFilter(k, True)
			c.group.grid(row=row, column=0, sticky="nsew")
			c.row = row
			if c.var.get():
				self.parent.rowconfigure(row, weight=10)
			else:
				self.parent.rowconfigure(row, weight=0)
			row += 1
		for k in self.columnMap.iterkeys():
			if k in self.columns:
				continue
			c = self._getFilter(k, False)
			if c is not None:
				c.group.grid_forget()

	def updateCompounds(self):
		wanted = {}
		if self.varV.get():
			wanted[Compound.Viable] = 1
		if self.varD.get():
			wanted[Compound.Deleted] = 1
		if self.varP.get():
			wanted[Compound.Purged] = 1
		self.compounds = Set([ c for c in self.results.compoundList
					if c.state in wanted])
		self.valueCache = {}

	def updateChosen(self):
		selected = self.compounds.copy()
		for k, c in self.columnMap.iteritems():
			if k not in self.columns:
				# Not displayed
				continue
			if not c.var.get():
				# Not selected
				continue
			selected.intersection_update(c.chosen)
		self.selected = selected
		self.label.config(text="%d of %d compounds applicable" %
				(len(self.selected), len(self.compounds)))

	def changeCompounds(self):
		self.updateCompounds()
		for k in self.columnMap.iterkeys():
			c = self._getFilter(k, False)
			if c is not None:
				c.redisplay()
		self.updateChosen()
		self._needChangeCompounds = False

	def _map(self, event=None):
		if event and event.widget is not self.uiMaster():
			return
		if self._isMapped:
			return
		if self._colAddHandler is None:
			self._colAddHandler = self.viewdock.triggers.addHandler(
						self.viewdock.COLUMN_ADDED,
						self._columnAdded, None)
		if self._colDelHandler is None:
			self._colDelHandler = self.viewdock.triggers.addHandler(
						self.viewdock.COLUMN_DELETED,
						self._columnDeleted, None)
		if self._colUpdHandler is None:
			self._colUpdHandler = self.viewdock.triggers.addHandler(
						self.viewdock.COLUMN_UPDATED,
						self._columnUpdated, None)
		self.updateColumns()
		if self._needChangeCompounds:
			self.changeCompounds()
		self._isMapped = True

	def _unmap(self, event=None):
		if event and event.widget is not self.uiMaster():
			return
		if not self._isMapped:
			return
		if self._colAddHandler is not None:
			self.viewdock.triggers.deleteHandler(
						self.viewdock.COLUMN_ADDED,
						self._colAddHandler)
			self._colAddHandler = None
		if self._colDelHandler is not None:
			self.viewdock.triggers.deleteHandler(
						self.viewdock.COLUMN_DELETED,
						self._colDelHandler)
			self._colDelHandler = None
		if self._colUpdHandler is not None:
			self.viewdock.triggers.deleteHandler(
						self.viewdock.COLUMN_UPDATED,
						self._colUpdHandler)
			self._colUpdHandler = None
		self._isMapped = False

	def _columnAdded(self, trigger, ignore, sel):
		self.updateColumns()

	def _columnDeleted(self, trigger, ignore, colName):
		self.updateColumns()
		try:
			del self.valueCache[colName]
		except KeyError:
			pass

	def _columnUpdated(self, trigger, ignore, colName):
		try:
			del self.valueCache[colName]
		except KeyError:
			pass
		c = self._getFilter(colName, False)
		if c is not None:
			c.redisplay()

	def _compoundStateChanged(self, trigger, ignore, sel):
		if self._isMapped:
			self.changeCompounds()
		else:
			self._needChangeCompounds = True

	def _exit(self, trigger, ignore, sel):
		self.destroy()

	def _getCompoundValues(self, col):
		try:
			return self.valueCache[col]
		except KeyError:
			values = []
			for c in self.compounds:
				try:
					v = c.fields[col]
				except KeyError:
					pass
				else:
					values.append(v)
			values.sort()
			self.valueCache[col] = values
			return values

	def _getFieldValues(self, col):
		try:
			return self.valueCache[col]
		except KeyError:
			vDict = {}
			for c in self.compounds:
				try:
					v = c.fields[col]
				except KeyError:
					pass
				else:
					vDict[v] = 1
			values = vDict.keys()
			values.sort()
			self.valueCache[col] = values
			return values

	def _getFilter(self, col, create):
		try:
			return self.columnMap[col]
		except KeyError:
			pass
		if not create:
			return None
		if self.results.style[col] == "number":
			c = HistogramColumn(self, col)
		else:
			c = ListboxColumn(self, col)
		self.columnMap[col] = c
		return c

	def Apply(self):
		self.viewdock.filter(self.selected)

class Column:
	def __init__(self, dialog, name):
		self.dialog = dialog
		self.parent = dialog.parent
		self.name = name
		self.var = Tkinter.IntVar(self.parent)
		self.var.set(1)
		self.group = Pmw.Group(self.parent,
					tag_pyclass=Tkinter.Checkbutton,
					tag_text=name,
					tag_variable=self.var,
					tag_command=self._groupCB)
		self.row = None		# Row number for data column
		self.chosen = Set()

	def _groupCB(self):
		if self.var.get():
			self.group.expand()
			self.parent.rowconfigure(self.row, weight=10)
		else:
			self.group.collapse()
			self.parent.rowconfigure(self.row, weight=0)
		self.dialog.updateChosen()

class HistogramColumn(Column):
	def __init__(self, dialog, name):
		Column.__init__(self, dialog, name)
		self._makeHistogram()
		self.updateChosen()

	def updateChosen(self):
		lo, hi = self._range()
		self.chosen = Set()
		for c in self.dialog.compounds:
			try:
				v = c.fields[self.name]
			except KeyError:
				pass
			else:
				if v >= lo and v <= hi:
					self.chosen.add(c)

	def redisplay(self):
		values = self.dialog._getCompoundValues(self.name)
		if len(values) > 0:
			self.minValue = values[0]
			self.maxValue = values[-1]
			if self.minValue == self.maxValue:
				ds = ("attribute has only one value: %s"
					% self.minValue)
			else:
				ds = (float(self.minValue), float(self.maxValue),
					self._bins)
			self.histogram.configure(datasource=ds)
		else:
			self.minValue = 0
			self.maxValue = 0
			ds = "No compounds to choose from"
		self.histogram.configure(datasource=ds)
		self.updateChosen()

	def _makeHistogram(self):
		from CGLtk.Histogram import MarkedHistogram
		values = self.dialog._getCompoundValues(self.name)
		self.minValue = values[0]
		self.maxValue = values[-1]
		# Use floats to make histogram continuous
		if self.minValue == self.maxValue:
			ds = "attribute has only one value: %s" % self.minValue
		else:
			ds = (float(self.minValue), float(self.maxValue),
				self._bins)
		self.histogram = MarkedHistogram(self.group.interior(),
					datasource=ds,
					colorwell=False,
					showmarkerhelp=False,
					scaling="linear",
					minlabel=True,
					maxlabel=True,
					hull_relief="sunken",
					hull_bd=2)
		self.histogram.pack(expand=True, fill="both")
		self.markers = self.histogram.addmarkers(
					coordtype="absolute",
					minmarks=2,
					maxmarks=2,
					movecallback=self._selectCB)
		self.markers.extend([ ((self.minValue, 0.0), (0.0, 1.0, 0.0)),
					  ((self.maxValue, 1.0), (0.0, 1.0, 0.0)) ])

	def _bins(self, bins):
		if bins <= 0:
			return [1]
		values = self.dialog.valueCache[self.name]
		r = values[-1] - values[0]
		if r == 0:
			return [ len(values) ]
		incr = float(r) / bins
		counts = bins * [0]
		lo = values[0]
		for v in values:
			n = int((v - lo) / incr)
			if n >= bins:
				n = bins - 1
			counts[n] += 1
		return counts

	def _selectCB(self, where):
		if isinstance(where, basestring):
			return
		self.updateChosen()
		self.dialog.updateChosen()

	def _range(self):
		return [ m["xy"][0] for m in self.markers ]

class ListboxColumn(Column):
	def __init__(self, dialog, name):
		Column.__init__(self, dialog, name)
		self._makeListbox()
		self.updateChosen()

	def updateChosen(self):
		chosenValues = {}
		for v in self.listbox.getvalue():
			chosenValues[v] = 1
		self.chosen = Set()
		for c in self.dialog.compounds:
			try:
				v = c.fields[self.name]
			except KeyError:
				pass
			else:
				if v in chosenValues:
					self.chosen.add(c)

	def redisplay(self):
		values = self.dialog._getFieldValues(self.name)
		selected = [ v for v in self.listbox.getvalue()
				if v in values ]
		self.listbox.setlist(values)
		self.listbox.setvalue(selected)
		self.updateChosen()

	def _makeListbox(self):
		values = self.dialog._getFieldValues(self.name)
		self.listbox = Pmw.ScrolledListBox(self.group.interior(),
				items=tuple(values),
				listbox_height=8,
				listbox_selectmode="extended",
				selectioncommand=self._selectCB,
				hull_relief="sunken",
				hull_bd=2)
		self.listbox.setvalue(values)
		self.listbox.pack(expand=True, fill="both")

	def _selectCB(self):
		self.updateChosen()
		self.dialog.updateChosen()
