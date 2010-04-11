# --- UCSF Chimera Copyright ---"%g" % self.
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Histogram.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter
import Pmw

class MarkedHistogram(Pmw.MegaWidget):
	"""Histogram with color-indication markers

	   MarkedHistogram shows a histogram of a data set and an optional
	   label for the numeric range of the data set.  Color markers can
	   be placed on the histogram by the user and moved interactively,
	   either with the mouse or by typing in a particular data value.
	   A color well is used to control the color of the "current" marker
	   (the one most recently selected with the mouse).  Markers can
	   either be vertical bars or squares.  Vertical bars can only be
	   moved left/right whereas squares can also be moved up/down.
	   Squares are also connected from left to right by line segments.

	   A row of associated widgets (such as the marker color well) is
	   placed below the histogram.  User-specified widgets can also be
	   placed in this row.

	   Individual markers are grouped into HistogramMarkers instances,
	   and several HistogramMarkers instances can be associated with
	   a single histogram, though only one instance is active/shown at
	   a time.

	   MarkedHistogram has the following options:
	   	[Options noted as init options can only be specified at
		widget creation.  Others can be changed later with the
		config() method.]

		colorwell --  controls whether a color well is offered in
			the user interface for changing marker colors.
			default: True

	   	datasource -- either a string or a 3-tuple.  If a string, then
			no histogram is displayed and instead the string is
			displayed in the histogram area as a text message.
			The first 2 components of a 3-tuple should be the
			minimum and maximum values of the histogram,  The
			third component should either be an array of numbers
			(i.e. the histogram) or a callback function that
			takes as its single argument the number of bins to
			histogram into and that returns a histogram array.
			default: 'no data'

		labelmargin -- [init option] if a label is associated with
			the widget (i.e. labelpos is not None) then this
			is the distance between the label component and the
			rest of the megawidget.
			default: 0

		labelpos -- [init option] where the megawidget label should
			be placed.  Some combination of 'nsew'.  Use the
			label_text option to specify the label text.
			default: None

		layout -- [init option] how to organize the megawidget layout.
			Choices are 'single', 'top', and 'below'.  'single'
			should be used when you are using a single histogram
			in your GUI, or histograms that aren't arrayed
			vertically.  'top' and 'below' should be used for
			histograms that are laid out in a vertical array
			('top' for the top-most one, and 'below' for all
			others).  Certain repeated elements will be omitted
			in 'below' histograms (e.g. some widget labels).
			default: single

		maxlabel/minlabel [init options] show the max/min histogram
			values as labels below the histogram on the right/left.
			If neither is True, then the range will be shown in a
			single label widget below the histogram.
			default: False

		redrawdelay -- amount of time (in seconds) to delay between
			needing to redraw and actually starting to redraw.
			Used to avoid multiple (possibly slow) redraws during
			a resize.
			default: 0.25

		scaling -- how to scale the vertical height of the histogram.
			Either 'logarithmic' or 'linear'.
			default: logarithmic

		selectcallback -- [init option] function to call when the
			"current" marker changes.  The function receives 4
			argments:  previous active marker set/marker,
			new active marker set/marker.  The marker set can
			be None to indicate no active marker set and the
			marker can be None if no marker was/is current.
		
		showmarkerhelp -- [init option] whether to show the help
			text over the histogram describing how to add/delete
			markers.
			default: True

		statusline -- function to use to output messages (such as
			warning when trying to add more markers than allowed).
			The function should take a single string argument.
			default: None

		valuelabel -- [init option] label to use next to the 
			entry widget describing the current marker value.
			default: 'Value'

		valuewidth -- width of the current marker value entry widget.
			default: 6

		widgetreserve -- [init option] number of columns to reserve
			for user widgets on the left side of the below-
			histogram row of widgets.
			default: 0

	   The dynamic group 'Markers' can be used to specify default
	   values for options for use during HistogramMarkers construction
	   (e.g. Markers_connectcolor = 'red').  Options for specific instances
	   can be provided to the addmarkers() method as keyword arguments
	   (without the 'Markers_' prefix).

	   A MarkedHistogram instance has the following components:

		canvas -- the canvas used to draw the histgram/markers

	   	markerhelp -- only created if 'showmarkerhelp' is True and
			'layout' is not 'below'.  The label above the
			histogram displaying the help text describing how
			to add/delete markers.

		minlabel/maxlabel -- labels used if 'minlabel'/'maxlabel'
			are True

		nodatalabel -- the label used when the 'datasource' option
			is a string

		widgetframe -- the frame used to contain the below-histogram
			widgets.  If 'widgetreserve' is not zero, you can
			grid your own widgets into the left of this frame
			used the reserved columns.  You can always grid into
			the right of this frame by using the frame's grid_size
			method to find the last used column.

			Widgets are always gridded into row 1.  If layout is
			'single', labels should also be gridded into row 1.
			If layout is 'top', labels should be gridded into
			row 0.  If layout is 'below', labels should be omitted.
	"""

	def __init__(self, parent=None, **kw):
	
		# Define the megawidget options
		optiondefs = (
			('colorwell',		True,		self._placeCW),
			('datasource',		'no data',	self._newData),
			('labelmargin',		0,		Pmw.INITOPT),
			('labelpos',		None,		Pmw.INITOPT),
			('layout',		'single',	Pmw.INITOPT),
			('maxlabel',		False,		Pmw.INITOPT),
			('minlabel',		False,		Pmw.INITOPT),
			('redrawdelay',		0.25,		None),
			('scaling',		'logarithmic',	self._redraw),
			('selectcallback',	None,		Pmw.INITOPT),
			('showmarkerhelp',	True,		Pmw.INITOPT),
			('statusline',		None,		None),
			('valuelabel',		'Value',	Pmw.INITOPT),
			('valuewidth',		7,		lambda:
				   self.valueEntry.component('entry').config(
				   width=self['valuewidth'])),
			('widgetreserve',	0,		Pmw.INITOPT),
		)
		self.defineoptions(kw, optiondefs, dynamicGroups=['Markers'])

		# Initialise base class (after defining options)
		Pmw.MegaWidget.__init__(self, parent)

		# Create the components
		interior = self.interior()

		# Create the add/delete marker help
		if self['showmarkerhelp'] and self['layout'] != 'below':
			self.markerHelp = self.createcomponent('markerhelp', (),
				None, Tkinter.Label, (interior,), text=
				"Ctrl-click on histogram to add or delete "
				"thresholds")

		# Create the canvas component
		self.canvas = self.createcomponent('canvas', (), None,
			Tkinter.Canvas, (interior,), highlightthickness=0,
			borderwidth=2, relief='sunken', width=300, height=64)
		interior.rowconfigure(3, weight=1)
		interior.columnconfigure(2, weight=1)
		self.canvas.bind('<Configure>', self._redraw)
		self.canvas.bind("<ButtonPress-1>", self._selectMarkerCB)
		self.canvas.bind("<ButtonRelease-1>", self._buttonUpCB)
		self.canvas.bind("<Control-ButtonPress-1>",
						self._addOrDeleteMarkerCB)
		self._motionHandler = None

		# Create the histogram replacement label
		self.noHistogramLabel = self.createcomponent('nodatalabel', (),
			None, Tkinter.Label, (interior,), borderwidth=2,
			relief='sunken', width=37, height=8)

		# Create the minimum value label component
		if self['minlabel']:
			self.minLabel = self.createcomponent('minlabel', (),
				None, Tkinter.Label, (interior,))
			self.minLabel.grid(row=4, column=2, sticky='nw')

		# Create the maximum value label component
		if self['maxlabel']:
			self.maxLabel = self.createcomponent('maxlabel', (),
				None, Tkinter.Label, (interior,))
			self.maxLabel.grid(row=4, column=3, sticky='ne')

		# Create the widget frame component
		self.widgetFrame = self.createcomponent('widgetframe', (),
			None, Tkinter.Frame, (interior,))

		widgetOffset = self['widgetreserve']
		# Create range widget
		if not self['minlabel'] and not self['maxlabel']:
			sticky = "ew"
			if self['layout'] != 'below':
				lab = Tkinter.Label(self.widgetFrame,
								text="Range")
				if self['layout'] == 'single':
					lab.grid(row=1, column=widgetOffset,
								sticky="e")
					sticky = "w"
					widgetOffset += 1
				else: # layout == 'top'
					lab.grid(row=0, column=widgetOffset)
			self.rangeLabel = Tkinter.Label(self.widgetFrame)
			self.rangeLabel.grid(row=1, column=widgetOffset,
							sticky=sticky)
			widgetOffset += 1

		# Create value widget
		sticky = "ew"
		lab = Tkinter.Label(self.widgetFrame, text=self['valuelabel'])
		if self['layout'] != 'below':
			if self['layout'] == 'single':
				lab.grid(row=1, column=widgetOffset, sticky="e")
				sticky = "w"
				widgetOffset += 1
			else:
				lab.grid(row=0, column=widgetOffset)
		self.valueEntry = Pmw.EntryField(self.widgetFrame,
			command=self._setValueCB, entry_state='disabled')
		self.valueEntry.grid(row=1, column=widgetOffset, sticky=sticky)
		widgetOffset += 1

		from color.ColorWell import ColorWell
		self.colorWell = ColorWell(self.widgetFrame,
				noneOkay=True, callback=self._colorWellCB)
		self.colorWellLabel = Tkinter.Label(self.widgetFrame,
								text="Color")
		# prepare layout of color well widget
		sticky = "ew"
		if self['layout'] != 'below':
			self._cwlColumn = widgetOffset
			if self['layout'] == 'single':
				self._cwlSticky = "e"
				sticky = "w"
				widgetOffset += 1
			else:
				self._cwlSticky = None
		self._cwColumn = widgetOffset
		self._cwSticky = sticky
		widgetOffset += 1

		for i in range(widgetOffset):
			self.widgetFrame.columnconfigure(i, weight=1)

		# Optionally create the label component
		self.createlabel(interior, childCols=2, childRows=4)

		# initialize variables
		self._delayID = None
		self._activeMarkers = None
		self._markers = []
		self._markable = False
		self._dragMarker = None
		if self['selectcallback']:
			self._prevMarkers = None
			self._prevMarker = None

		# Check keywords and initialise options
		self.initialiseoptions(MarkedHistogram)

	def activate(self, markers):
		"""Make the given set of markers the currently active set
		
		   Any previously-active set will be hidden.
		"""

		if markers is not None and markers not in self._markers:
			raise ValueError, "activate() called with bad value"
		if markers == self._activeMarkers:
			return
		if self._activeMarkers is not None:
			self._activeMarkers._hide()
		elif self['layout'] != 'below' and self['showmarkerhelp']:
			self.markerHelp.grid(row=2, column=2, columnspan=2)
		self._activeMarkers = markers
		if self._activeMarkers is not None:
			self._activeMarkers._show()
			self._setSelMarker(self._activeMarkers._selMarker)
		else:
			if self['layout'] != 'below' and self['showmarkerhelp']:
				self.markerHelp.grid_forget()
			if self['selectcallback']:
				if self._prevMarker is not None:
					self['selectcallback'](
						self._prevMarkers,
						self._prevMarker, None, None)
				self._prevMarkers = None
				self._prevMarker = None

	def addmarkers(self, activate=True, **kw):
		"""Create and return a new set of markers.

		   If 'activate' is true, the new set will also become
		   the active set.  Other keyword arguments will be passed
		   to the HistogramMarkers constructor.
		"""
		if self._markers:
			newName = "markers" + str(int(
					self._markers[-1]._name[7:]) + 1)
		else:
			newName = "markers1"
		kw['histogram'] = self
		markers = self.createcomponent(newName, (), 'Markers', 
						HistogramMarkers, (), **kw)
		markers._name = newName
		self._markers.append(markers)
		if activate:
			self.activate(markers)
		return markers

	def currentmarkerinfo(self):
		"""Identify the marker currently selected by the user.
		   
		   Returns a HistogramMarkers instance and a marker.
		   The instance will be None if no marker set has been
		   activated.  The marker will be None if no marker has
		   been selected by the user.
		"""
		if self._activeMarkers is None:
			return None, None
		return self._activeMarkers, self._activeMarkers._selMarker

	def deletemarkers(self, markers):
		"""Delete the given set of markers.

		   If the markers were active, there will be no active set
		   of markers afterward.
		"""
		if markers not in self._markers:
			raise ValueError, "Bad value for delete()"
		if markers == self._activeMarkers:
			self.activate(None)
		self._markers.remove(markers)
		self.destroycomponent(markers._name)

	def _abs2rel(self, absXY):
		x, y = absXY
		relX = (x - self.minVal) / float(self.maxVal - self.minVal)
		relY = y / float(self._ymax)
		return relX, relY

	def _absXY(self, canvasXY):
		canvasX, canvasY = canvasXY
		dy = min(max(self._bottom - canvasY, 0), self._canvasHeight - 1)
		if self['scaling'] == 'logarithmic':
			exp = dy / float(self._canvasHeight - 1)
			absY = (self._maxHeight + 1) ** exp - 1
		else:
			absY = self._maxHeight*dy / float(self._canvasHeight-1)

		cx = canvasX - self._border
		numBins = len(self.bins)
		if numBins == self._histWidth:
			fract = cx / (numBins - 1)
			absX = self.minVal + fract * (self.maxVal - self.minVal)
		elif numBins == 2:
			absX = self.minVal + (self.maxVal - self.minVal) * (
				2 * cx / self._histWidth - 0.5)
		else:
			extra = self._histWidth / (2.0*(numBins-1))
			absX = self.minVal + (self.maxVal - self.minVal) * (
				cx - extra) / (self._histWidth - 2.0 * extra)
		absX = max(self.minVal, absX)
		absX = min(self.maxVal, absX)
		return absX, absY

	def _addOrDeleteMarkerCB(self, event=None):
		if self._activeMarkers is None:
			return

		marker = self._activeMarkers._pickMarker(event.x, event.y)

		if marker is None:
			maxMarks = self._activeMarkers['maxmarks']
			if maxMarks is not None \
			and len(self._activeMarkers) >= maxMarks:
				if self['statusline']:
					self['statusline']("Maximum of %d"
						" markers\n" % maxMarks)
				return
			xy = self._absXY((event.x, event.y))
			if self._activeMarkers['coordtype'] == 'relative':
				xy = self._abs2rel(xy)
			selMarker = self._activeMarkers._selMarker
			if selMarker:
				color = selMarker['rgba']
			else:
				color = self._activeMarkers['newcolor']
			marker = self._activeMarkers.append((xy, color))
			self._setSelMarker(marker, dragStart=event)
		else:
			minMarks = self._activeMarkers['minmarks']
			if minMarks is not None \
			and len(self._activeMarkers) <= minMarks:
				if self['statusline']:
					self['statusline']("Minimum of %d"
						" markers\n" % minMarks)
				return
			self._activeMarkers.remove(marker)
			self._setSelMarker(None)
			
	def _buttonUpCB(self, event=None):
		if self._dragMarker:
			self.canvas.bind("<Button1-Motion>", "")
			self._dragMarker = None
			if self._activeMarkers['movecallback']:
				self._activeMarkers['movecallback']('end')

	def _canvasXY(self, absXY):
		# minimum is in the _center_ of the first bin,
		# likewise, maximum is in the center of the last bin

		absX, absY = absXY

		absY = max(0, absY)
		absY = min(self._maxHeight, absY)
		if self['scaling'] == 'logarithmic':
			import math
			absY = math.log(absY+1)
		canvasY = self._bottom - (self._canvasHeight - 1) * (
						absY / self._maxHeight)

		absX = max(self.minVal, absX)
		absX = min(self.maxVal, absX)
		numBins = len(self.bins)
		if numBins == self._histWidth:
			binWidth = (self.maxVal - self.minVal) / float(
								numBins - 1)
			leftEdge = self.minVal - 0.5 * binWidth
			canvasX = int((absX - leftEdge) / binWidth)
		else:
			# histogram is effectively one bin wider
			# (two half-empty bins on each end)
			extra = (self.maxVal - self.minVal) / (2.0*(numBins-1))
			effMinVal = self.minVal - extra
			effMaxVal = self.maxVal + extra
			effRange = float(effMaxVal - effMinVal)
			canvasX = (self._histWidth - 1) * (absX - effMinVal) \
								/ effRange
		return self._border + canvasX, canvasY

	def _colorWellCB(self, rgba):
		m = self._activeMarkers._selMarker
		if not m:
			if self['statusline']:
				self['statusline']("No marker selected")
			return
		if rgba is None:
			if self['statusline']:
				self['statusline'](
					"Cannot set marker color to None")
			# can't reset the color in the middle of the callback
			self.interior().after_idle(lambda rgba=m['rgba']:
					self.colorWell.showColor(rgba,
					doCallback=False))
			return
		m['rgba'] = rgba

	def _marker2abs(self, marker):
		if self._activeMarkers['coordtype'] == 'absolute':
			return marker['xy']
		else:
			return self._rel2abs(marker['xy'])

	def _moveCurMarker(self, x, yy=None):
		#
		# Don't allow dragging out of the canvas box.
		#
		m = self._activeMarkers._selMarker
		if x < self.minVal:
			x = self.minVal
		elif x > self.maxVal:
			x = self.maxVal
		if yy is None:
			y = m['xy'][1]
		else:
			y = yy
			if y < 0:
				y = 0
			elif y > self._ymax:
				y = self._ymax

		if self._activeMarkers['coordtype'] == 'absolute':
			m['xy'] = (x, y)
		else:
			m['xy'] = self._abs2rel((x,y))
		if yy is None:
			m['xy'] = (m['xy'][0], y)

		self._setValueEntry(x)

		self._activeMarkers._updatePlot()

		if self._activeMarkers['movecallback']:
			self._activeMarkers['movecallback'](m)

	def _moveMarkerCB(self, event):
		mouseXY = self._absXY((event.x, event.y))
		dx = mouseXY[0] - self._lastMouseXY[0]
		dy = mouseXY[1] - self._lastMouseXY[1]
		self._lastMouseXY = mouseXY

		shiftMask = 1
		if event.state & shiftMask:
			dx *= .1
			dy *= .1

		m = self._dragMarker
		mxy = self._marker2abs(m)
		x, y = mxy[0] + dx, mxy[1] + dy

		self._moveCurMarker(x, y)

	def _newData(self):
		self.canvas.grid_forget()
		self.noHistogramLabel.grid_forget()
		ds = self['datasource']
		if isinstance(ds, basestring):
			self.noHistogramLabel.config(text=ds)
			self.noHistogramLabel.grid(row=3, column=2,
						columnspan=2, sticky="nsew")
			if self['minlabel']:
				self.minLabel.configure(text="")
			if self['maxlabel']:
				self.maxLabel.configure(text="")
			if self['layout'] != 'below' and self['showmarkerhelp']:
				self.markerHelp.grid_forget()
			self.widgetFrame.grid_forget()
		else:
			self.canvas.grid(row=3, column=2, columnspan=2,
						sticky="nsew")
			if self['layout'] != 'below' and self['showmarkerhelp']:
				self.markerHelp.grid(row=2, column=2,
								columnspan=2)
			self.widgetFrame.grid(row=5, column=2, columnspan=2,
								sticky="ew")
		self._redraw()

	def _placeCW(self):
		if self['colorwell']:
			if self['layout'] != 'below':
				self.colorWellLabel.grid(row=1,
						column=self._cwlColumn,
						sticky=self._cwlSticky)
				self.widgetFrame.columnconfigure(
						self._cwlColumn, weight=1)
			self.colorWell.grid(row=1, column=self._cwColumn,
							sticky=self._cwSticky)
			self.widgetFrame.columnconfigure(self._cwColumn,
							weight=1)
		else:
			if self['layout'] != 'below':
				self.colorWellLabel.grid_forget()
				self.widgetFrame.columnconfigure(
						self._cwlColumn, weight=0)
			self.colorWell.grid_forget()
			self.widgetFrame.columnconfigure(self._cwColumn,
							weight=0)
			self.colorWell.deactivate()

	def _redraw(self, event=None):
		self._markable = False
		if self._delayID is not None:
			self.interior().after_cancel(self._delayID)
		self._delayID = self.interior().after(
			int(1000 * self.cget('redrawdelay')), self._redrawCB)

	def _redrawCB(self):
		self._delayID = None
		ds = self.cget('datasource')
		if ds is None:
			raise ValueError, "No data source for histogram"
		if isinstance(ds, basestring):
			# displaying a text label right now
			return
		canvas = self.canvas
		w = canvas.winfo_width()
		if not w:
			return
		border = canvas.winfo_fpixels(canvas['borderwidth'])
		self._border = border
		histWidth = int(w - 2 * border)
		self._histWidth = histWidth
		self.minVal, self.maxVal, self.bins = ds
		if callable(self.bins):
			self.bins = self.bins(histWidth)
		if self['minlabel']:
			self.minLabel.configure(text=self._strVal(self.minVal))
		if self['maxlabel']:
			self.maxLabel.configure(text=self._strVal(self.maxVal))
		if not self['minlabel'] and not self['maxlabel']:
			self.rangeLabel.configure(text="%s - %s" %
						(self._strVal(self.minVal),
						self._strVal(self.maxVal)))

		canvas.delete('bar')
		canvasHeight = canvas.winfo_height() - 2 * border
		self._canvasHeight = canvasHeight

		self._ymax = max(self.bins)
		if self['scaling'] == 'logarithmic':
			from numpy import array, log, float32
			self.bins = array(self.bins, float32)
			self.bins += 1.0
			log(self.bins, self.bins)

		maxHeight = max(self.bins)
		self._maxHeight = maxHeight
		hScale = float(canvasHeight - 1) / maxHeight
		bottom = canvasHeight + border - 1
		self._bottom = bottom

		numBins = len(self.bins)
		if numBins == histWidth:
			for b, n in enumerate(self.bins):
				x = border + b
				h = int(hScale * n)
				id = canvas.create_line(x, bottom, x, bottom-h,
								tags=('bar',))
				canvas.tag_lower(id)  # keep bars below markers
		else:
			xScale = (histWidth - 1) / float(numBins)
			for b, n in enumerate(self.bins):
				x1 = border + b * xScale
				x2 = border + (b+1) * xScale
				h = int(hScale * n)
				id = canvas.create_rectangle(x1, bottom,
						x2, bottom-h, tags=('bar',))
				canvas.tag_lower(id)  # keep bars below markers
		self._markable = True
		if self._activeMarkers is not None:
			self._activeMarkers._updatePlot()
			marker = self._activeMarkers._selMarker
			if marker:
				self._setValueEntry(self._marker2abs(marker)[0])

	def _rel2abs(self, relXY):
		x, y = relXY
		absX = self.minVal * (1-x) + x * self.maxVal
		absY = y * self._ymax
		return absX, absY

	def _selectMarkerCB(self, event=None):
		if self._activeMarkers is not None:
			marker = self._activeMarkers._pickMarker(event.x,
								event.y)
			self._setSelMarker(marker, dragStart=event)
			if marker is not None:
				return
		# show value where histogram clicked
		self._setValueEntry(self._absXY((event.x, 0))[0])
	
	def _setSelMarker(self, marker, dragStart=None):
		self._activeMarkers._selMarker = marker
		if not marker:
			self.colorWell.showColor(None, doCallback=False)
			self._setValueEntry("")
			self.valueEntry.component('entry').config(
							state='disabled')
		else:
			self.colorWell.showColor(marker['rgba'],
							doCallback=False)
			self.valueEntry.component('entry').config(
							state='normal')
			self._setValueEntry(self._marker2abs(marker)[0])
		if self['selectcallback']:
			if marker is not None or self._prevMarker is not None:
				self['selectcallback'](self._prevMarkers,
					self._prevMarker, self._activeMarkers,
					marker)
			self._prevMarkers = self._activeMarkers
			self._prevMarker = marker
		if not dragStart:
			return
		self._dragMarker = marker
		if not marker:
			return

		self._lastMouseXY = self._absXY((dragStart.x, dragStart.y))
		self._motionHandler = self.canvas.bind("<Button1-Motion>",
							self._moveMarkerCB)
		if self._activeMarkers['movecallback']:
			self._activeMarkers['movecallback']('start')
	
	def _setValueCB(self):
		try:
			v = eval(self.valueEntry.getvalue())
		except:
			raise ValueError, "Invalid histogram value"
		self._moveCurMarker(v)

	def _setValueEntry(self, val):
		if isinstance(val, basestring):
			self.valueEntry.setvalue(val)
			return
		if isinstance(self.minVal, int):
			val = int(val + 0.5)
		self.valueEntry.setvalue("%g" % val)

	def _strVal(self, val):
		if isinstance(val, int):
			# handles booleans also
			return str(val)
		return "%g" % val

Pmw.forwardmethods(MarkedHistogram, Tkinter.Canvas, 'canvas')

from CGLtk.color import rgba2tk
class HistogramMarkers(Pmw.MegaArchetype):
	"""Color-designating markers on a histogram

	   Instances should only created via the addmarkers() method of
	   MarkedHistogram.  Options can be specified as keyword arguments
	   to that function.
	   
	   Contained HistogramMarker instances can be accessed as if
	   HistogramMarker were a sequence.  The instances are always kept
	   sorted ascending in X, so sequence order can change with any
	   method that adds markers (e.g. a marker added with 'append'
	   may not wind up at the end of the sequence).  Methods that create
	   new HistogramMarker instances (append, extend, insert, __setitem__)
	   need 2-tuples/lists for each HistogramMarker instance, the
	   first component of which is the XY value (i.e. another 2-tuple
	   or list) and the second of which is the color info.  The color
	   info can be either:
		an RGBA value
		None (use the 'newmarker' color)
		a color name
		an instance that has either an 'rgba' attribute or
			an argless 'rgba' method (e.g. a MaterialColor)

	   The MarkedHistogram and HistogramMarker doc strings should be
	   examined for further info on usage.

	   Options are:

		boxradius -- the radius in pixels of boxes drawn when the
			markertype is 'box'
			default: 2

	   	connect -- [init option] whether markers should be
			connected left-to-right with lines.  Typically
			used only when the markertype is 'box'.
			default: False

		connectcolor -- [init option] the color used to draw
			lines connecting markers ('connect' must be True)
			default: yellow

		coordtype -- either 'relative' or 'absolute'.  If the former,
			then the 'xy' option of contained HistgramMarkers are
			in the range 0-1 and indicate positioning relative to
			left/right and bottom/top of the histogram.  If the
			latter, then the x of 'xy' indicates a histogram
			bin by value and a height by count.
			default: absolute

		histogram -- [init option provided automatically by
			MarkedHistogram.addmarkers()] the MarkedHistogram
			instance

		markertype -- [init option] the type of markers to use, 
			either 'line' (vertical bars) or 'box' (squares).
			default: line

		maxmarks/minmarks -- the maximum/minimum amount of marks the
			user is allowed to place on the histogram.  A value of
			None indicates no limit.  Can always be exceeded
			programmatically.
			default: None

		movecallback -- [init option] function to call when the user
			moves a marker.  The function receives a value of
			'start' at the beginning of a move and 'end' at the
			end.  During the move the value is the marker being
			moved.
			default: None

		newcolor -- the default color assigned to newly-created
			markers.
			default: yellow
	"""

	def __init__(self, parent=None, **kw):
	
		# Define the megawidget options
		optiondefs = (
			('boxradius',	2,		self._newBoxRadius),
			('connect',	False,		Pmw.INITOPT),
			('connectcolor','yellow',	Pmw.INITOPT),
			('coordtype',	'absolute',	self._convertCoords),
			('histogram',	None,		Pmw.INITOPT),
			('markertype',	'line',		Pmw.INITOPT),
			('maxmarks',	None,		None),
			('minmarks',	None,		None),
			('movecallback',None,		Pmw.INITOPT),
			('newcolor',	'yellow',	None),
		)
		self.defineoptions(kw, optiondefs, dynamicGroups=['Marker'])

		# Initialise base class (after defining options)
		Pmw.MegaArchetype.__init__(self, parent)

		# Check keywords and initialise options
		self._shown = False
		self._selMarker = None
		self._prevBoxRadius = None
		self.markers = []
		self.connectIds = []
		self._prevCoordType = self['coordtype']
		self.initialiseoptions(HistogramMarkers)

		# values derived from options
		self.markerFunc = lambda v: HistogramMarker(markers=self,
					xy=v[0], rgba=self._rgba(v[1]))
		# convenience
		self._canvas = self['histogram'].component('canvas')

	def append(self, val):
		marker = self.markerFunc(val)
		self.markers.append(marker)
		self._updatePlot()
		return marker

	def __delitem__(self, i):
		if isinstance(i, basestring):
			return Pmw.MegaArchetype.__delitem__(self, i)
		del self.markers[i]
		self._updatePlot()

	def destroy(self):
		self._unplotMarkers()
		Pmw.MegaArchetype.destroy(self)

	def extend(self, vals):
		markers = map(self.markerFunc, vals)
		self.markers.extend(markers)
		self._updatePlot()
		return markers

	def __getitem__(self, i):
		if isinstance(i, basestring):
			return Pmw.MegaArchetype.__getitem__(self, i)
		return self.markers[i]

	def index(self, marker):
		return self.markers.index(marker)

	def insert(self, i, val):
		marker = self.markerFunc(val)
		self.markers.insert(i, marker)
		self._updatePlot()
		return marker

	def __iter__(self):
		return self.markers.__iter__()

	def __len__(self):
		return len(self.markers)

	def pop(self):
		ret = self.markers.pop()
		if ret == self._selMarker:
			self._selMarker = None
		self._unplotMarkers(ret)
		self._updatePlot()
		return ret

	def remove(self, marker):
		self.markers.remove(marker)
		if marker is self._selMarker:
			self._selMarker = None
		self._unplotMarkers(marker)
		self._updatePlot()

	def __setitem__(self, i, val):
		if isinstance(i, basestring):
			return Pmw.MegaArchetype.__setitem__(self, i, val)
		if isinstance(i, slice):
			newMarkers = map(self.markerFunc, val)
			selReplaced = self._selMarker in self.markers[i]
		else:
			newMarkers = self.markerFunc(val)
			selReplaced = self._selMarker is self.markers[i]
		if selReplaced:
			self._selMarker = None
		self._unplotMarkers(self.markers[i])
		self.markers[i] = newMarkers
		self._updatePlot()
	
	def sort(self, sortFunc=None):
		self.markers.sort(sortFunc)

	def _canvasXY(self, xy):
		if self['coordtype'] == 'relative':
			absXY = self['histogram']._rel2abs(xy)
		else:
			absXY = xy
		return self['histogram']._canvasXY(absXY)

	def _convertCoords(self):
		if self['coordtype'] == self._prevCoordType:
			return
		if self['coordtype'] == 'relative':
			convFunc = self['histogram']._abs2rel
		else:
			convFunc = self['histogram']._rel2abs
		for m in self.markers:
			m['xy'] = convFunc(m['xy'])
		self._prevCoordType = self['coordtype']

	def _dragRegion(self):
		x1, y1, x2, y2 = self._canvas.bbox('bar')
		br = self['boxradius']
		y1 += br + 1
		y2 -= br + 1
		return x1, y1, x2, y2

	def _hide(self):
		if not self._shown:
			return
		self._shown = False
		self._unplotMarkers()

	def _newBoxRadius(self):
		boxRadius = self['boxradius']
		if boxRadius <= 0:
			raise ValueError, "boxradius must be > 0"
		if self._prevBoxRadius != None:
			diff = boxRadius - self._prevBoxRadius
			canvas = self._canvas
			box = self['markertype'] == 'box'
			for marker in self.markers:
				x0, y0, x1, y1 = canvas.coords(marker['id'])
				x0 += diff
				x1 += diff
				if box:
					y0 += diff
					y1 += diff
				canvas.coords(marker['id'], x0, y0, x1, y1)
		self._prevBoxRadius = boxRadius

	def _pickMarker(self, cx, cy):
		close = self._canvas.find('closest', cx, cy, 3)
		for c in close:
			for m in self.markers:
				if m['id'] == c:
					return m
		return None

	def _plotMarkers(self):
		canvas = self._canvas
		br = self['boxradius']

		markerType = self['markertype']
		if markerType == 'line':
			x1, y1, x2, y2 = self._dragRegion()
		for m in self.markers:
			if m['id'] != None:
				continue
			x, y = self._canvasXY(m['xy'])
			color = rgba2tk(m['rgba'])
			if markerType == 'line':
				m['id'] = canvas.create_rectangle(x-br, y1,
							x+br, y2, fill=color)
			else:
				m['id'] = canvas.create_rectangle(x-br, y-br,
							x+br, y+br, fill=color)

	def _rgba(self, colorInfo):
		if colorInfo is None:
			colorInfo = self['newcolor']
		if isinstance(colorInfo, basestring):
			from chimera.colorTable import getColorByName
			colorInfo = getColorByName(colorInfo)
		if hasattr(colorInfo, 'rgba'):
			if callable(colorInfo.rgba):
				return colorInfo.rgba()
			return colorInfo.rgba
		return colorInfo

	def _show(self):
		if self._shown:
			return
		self._shown = True
		self._updatePlot()

	def _unplotMarkers(self, markers=None):
		if markers is None:
			markers = self.markers
		elif isinstance(markers, HistogramMarker):
			markers = [markers]
		canvas = self._canvas
		for m in markers:
			if m['id'] != None:
				canvas.delete(m['id'])
				m['id'] = None
		for i in self.connectIds:
			canvas.delete(i)
		self.connect_ids = []

	def _updateConnections(self):
		cxy_list = map(lambda m: self._canvasXY(m['xy']), self.markers)

		canvas = self._canvas
		color = rgba2tk(self._rgba(self['connectcolor']))
		ids = []
		for k in range(len(cxy_list) - 1):
			x0, y0 = cxy_list[k]
			x1, y1 = cxy_list[k+1]
			id = canvas.create_line(x0, y0, x1, y1, fill=color)
			ids.append(id)

		for id in self.connectIds:
			c.delete(id)

		self.connectIds = ids

		for m in self.markers:
			canvas.tag_raise(m['id'])

	def _updateMarkerCoordinates(self):
		canvas = self._canvas
		br = self['boxradius']

		markerType = self['markertype']
		if markerType == 'line':
			x1, y1, x2, y2 = self._dragRegion()
		for m in self.markers:
			x, y = self._canvasXY(m['xy'])
			if markerType == 'line':
				canvas.coords(m['id'], x-br, y1, x+br, y2)
			else:
				canvas.coords(m['id'], x-br, y-br, x+br, y+br)

	def _updatePlot(self):
		self.markers.sort()
		if not self._shown:
			return
		if not self['histogram']._markable:
			return

		self._plotMarkers()

		self._updateMarkerCoordinates()

		if self['connect']:
			self._updateConnections()

class HistogramMarker(Pmw.MegaArchetype):
	"""a marker on a histogram
	   
	   Should only be created (or destroyed) with methods of a
	   HistogramMarkers instance.  See that class's doc string 
	   for details.

	   The only options relevant externally are 'rgba' and 'xy'.
	   'xy' should be treated as if it were read-only (use 
	   HistogramMarkers methods to delete/add a marker if it
	   is necessary to get one to "move" programatically).  'xy'
	   values will depend on HistogramMarkers' 'coordtype' option.
	"""

	def __init__(self, parent=None, **kw):
	
		# Define the megawidget options
		optiondefs = (
			('id',		None,		None),
			('markers',	None,		Pmw.INITOPT),
			('rgba',	(1,1,0,0),	self._setRgba),
			('xy',		(0.5, 0.5),	None)
		)
		self.defineoptions(kw, optiondefs)

		# Initialise base class (after defining options)
		Pmw.MegaArchetype.__init__(self, parent)

		# Check keywords and initialise options
		self.initialiseoptions(HistogramMarker)

		# convenience
		self._canvas = self['markers']['histogram'].component('canvas')

	def __cmp__(self, other):
		if not isinstance(other, self.__class__):
			return False
		return cmp(self['xy'], other['xy'])

	def _setRgba(self):
		if self['id'] == None:
			return
		self._canvas.itemconfigure(self['id'],
						fill=rgba2tk(self['rgba']))
