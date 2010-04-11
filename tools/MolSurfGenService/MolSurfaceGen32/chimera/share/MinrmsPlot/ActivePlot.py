#!/usr/bin/env python

# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import math
import Canvas
import Tkinter
import colorsys

def _unitize(value, unit, f):
	return f(value / unit) * unit

class ActivePlot(Tkinter.Frame):
	"""
	ActivePlot manages the layout for several types of datasets
	(scatter, serial bar, etc.).  The display is also an
	user interface: when the user clicks on a data elements,
	registered callbacks are invoked.
	"""
	def __init__(self, master=None, xFormat=None, yFormat=None,
			xRange=[], yRange=[],
			xPrecision=0, yPrecision=0,
			xMargin=5, yMargin=5, dataSet=None,
			track=Tkinter.FALSE, zoom=Tkinter.FALSE,
			singleCallback=None, singleClosure=None,
			doubleCallback=None, doubleClosure=None,
			labelCnf={}, canvasCnf={}, plotCnf={},
			controlCnf={}, **cnf):
		Tkinter.Frame.__init__(self, master, cnf)
		self.xFormat = xFormat
		self.xPrecision = xPrecision
		try:
			self.xMin = xRange[0]
			self.xMax = xRange[1]
			self.xSize = self.xMax - self.xMin
			self.hasXSize = 1
		except:
			self.hasXSize = 0
		self.xMargin = xMargin
		self.yFormat = yFormat
		self.yPrecision = yPrecision
		try:
			self.yMin = yRange[0]
			self.yMax = yRange[1]
			self.ySize = self.yMax - self.yMin
			self.hasYSize = 1
		except:
			self.hasYSize = 0
		self.yMargin = yMargin
		if yFormat:
			yWidth = len(yFormat % 1.234)
		else:
			yWidth = 10
		if xFormat:
			xWidth = len(xFormat % 1.234)
		else:
			xWidth = 10
		if track or zoom:
			self.control = Tkinter.Frame(self, controlCnf)
			self.control.pack(side=Tkinter.BOTTOM,
						fill=Tkinter.X)
			if zoom:
				self.zoomInButton = Tkinter.Button(
						self.control,
						text='Zoom In',
						command=self.zoomIn)
				self.zoomInButton.pack(side=Tkinter.LEFT)
				self.zoomOutButton = Tkinter.Button(
						self.control,
						text='Zoom Out',
						state=Tkinter.DISABLED,
						command=self.zoomOut)
				self.zoomOutButton.pack(side=Tkinter.LEFT)
				if track:
					filler = Tkinter.Frame(self.control,
								width=10)
					filler.pack(side=Tkinter.LEFT)
			if track:
				self.xVar = Tkinter.DoubleVar(self)
				l = Tkinter.Label(self.control, text='X')
				l.pack(side=Tkinter.LEFT)
				self.trackX = Tkinter.Label(self.control,
						textvariable=self.xVar,
						justify=Tkinter.RIGHT,
						bd=2, relief=Tkinter.RIDGE,
						width=xWidth)
				self.trackX.pack(side=Tkinter.LEFT,
						fill=Tkinter.BOTH,
						expand=Tkinter.TRUE)
				self.yVar = Tkinter.DoubleVar(self)
				l = Tkinter.Label(self.control, text='Y')
				l.pack(side=Tkinter.LEFT)
				self.trackY = Tkinter.Label(self.control,
						textvariable=self.yVar,
						justify=Tkinter.RIGHT,
						bd=2, relief=Tkinter.RIDGE,
						width=yWidth)
				self.trackY.pack(side=Tkinter.RIGHT,
						fill=Tkinter.BOTH,
						expand=Tkinter.TRUE)
		if len(plotCnf) > 0:
			master = Tkinter.Frame(self, plotCnf)
			master.pack(fill=Tkinter.BOTH,
					expand=Tkinter.TRUE)
		else:
			master = self
		if yFormat:
			self.yFrame = Tkinter.Frame(master)
			self.yFrame.pack(side=Tkinter.LEFT,
						fill=Tkinter.Y)
			if zoom:
				filler = Tkinter.Frame(self.yFrame, height=12)
				filler.pack(side=Tkinter.TOP)
			self.yMaxVar = Tkinter.StringVar(self)
			self.yMaxEntry = Tkinter.Entry(self.yFrame, labelCnf,
						textvariable=self.yMaxVar,
						justify=Tkinter.RIGHT,
						state=Tkinter.DISABLED,
						width=yWidth)
			self.yMaxEntry.pack(side=Tkinter.TOP,
						fill=Tkinter.X)
			if xFormat:
				filler = Tkinter.Entry(self.yFrame, labelCnf,
						state=Tkinter.DISABLED,
						width=yWidth,
						relief=Tkinter.FLAT)
				filler.pack(side=Tkinter.BOTTOM)
			self.yMinVar = Tkinter.StringVar(self)
			self.yMinEntry = Tkinter.Entry(self.yFrame, labelCnf,
						textvariable=self.yMinVar,
						justify=Tkinter.RIGHT,
						state=Tkinter.DISABLED,
						width=yWidth)
			self.yMinEntry.pack(side=Tkinter.BOTTOM,
						fill=Tkinter.X)
		if xFormat:
			self.xFrame = Tkinter.Frame(master)
			self.xFrame.pack(side=Tkinter.BOTTOM,
						fill=Tkinter.X)
			self.xMaxVar = Tkinter.StringVar(self)
			self.xMaxEntry = Tkinter.Entry(self.xFrame, labelCnf,
						textvariable=self.xMaxVar,
						justify=Tkinter.RIGHT,
						#state=Tkinter.DISABLED,
						width=xWidth)
			self.xMaxEntry.pack(side=Tkinter.RIGHT,
						fill=Tkinter.Y,
						expand=Tkinter.FALSE)
			self.xMinVar = Tkinter.StringVar(self)
			self.xMinEntry = Tkinter.Entry(self.xFrame, labelCnf,
						textvariable=self.xMinVar,
						justify=Tkinter.LEFT,
						#state=Tkinter.DISABLED,
						width=xWidth)
			self.xMinEntry.pack(side=Tkinter.LEFT,
						fill=Tkinter.Y,
						expand=Tkinter.FALSE)
		if zoom:
			self.zoomScrollbar = Tkinter.Scrollbar(master,
						orient=Tkinter.HORIZONTAL,
						width=8)
			self.zoomScrollbar.pack(side=Tkinter.TOP,
						fill=Tkinter.X)
		self.canvas = Tkinter.Canvas(master, canvasCnf)
		self.canvas.pack(fill=Tkinter.BOTH, expand=Tkinter.TRUE)
		if zoom:
			if self.xFormat:
				self.zoomScrollbar['command'] = \
					self.xviewZoom
				self.canvas['xscrollcommand'] = \
					self.setZoom
			else:
				self.zoomScrollbar['command'] = \
					self.canvas.xview
				self.canvas['xscrollcommand'] = \
					self.zoomScrollbar.set
		self.canvasBorder = int(self.canvas['bd'])
		self.canvasWidth = 1
		self.canvasHeight = 1
		self.tag = 1
		self.track = track
		self.zoom = zoom
		self.zoomFactor = 1.0
		self.dataSetList = []
		self.setSingleCallback(singleCallback, singleClosure)
		self.setDoubleCallback(doubleCallback, doubleClosure)
		if dataSet:
			self.addDataSet(dataSet)
		self.canvas.bind('<Configure>', self.rescale)

	def zoomIn(self):
		self.zoomFactor = self.zoomFactor * 2
		left, top, right, bottom = map(int,
					self.canvas['scrollregion'].split())
		fMin, fMax = self.zoomScrollbar.get()
		fRange = 1.0 / self.zoomFactor
		fMax = fMin + fRange
		self.canvasWidth = self.canvasWidth * 2
		self.computeScale()
		right = int(left + self.canvasWidth + 2 * self.xMargin)
		self.canvas['scrollregion'] = (left, top, right, bottom)
		self.setZoom(fMin, fMax)
		self.redisplay()
		self.zoomOutButton['state'] = Tkinter.NORMAL

	def zoomOut(self):
		self.zoomFactor = self.zoomFactor / 2
		left, top, right, bottom = map(int,
					self.canvas['scrollregion'].split())
		fMin, fMax = self.zoomScrollbar.get()
		fRange = 1.0 / self.zoomFactor
		self.canvasWidth = self.canvasWidth / 2
		self.computeScale()
		fMax = fMin + fRange
		if fMax > 1:
			fMax = 1
			fMin = fMax - fRange
			#right = int(self.canvasWidth * self.zoomFactor
			#		+ 2 * self.xMargin + self.canvasBorder)
			#left = int(right - self.canvasWidth - 2 * self.xMargin)
		right = int(left + self.canvasWidth + 2 * self.xMargin)
		self.canvas['scrollregion'] = (left, top, right, bottom)
		self.setZoom(fMin, fMax)
		self.redisplay()
		if self.zoomFactor < 2:
			self.zoomOutButton['state'] = Tkinter.DISABLED

	def setZoom(self, first, last):
		self.zoomScrollbar.set(first, last)
		if self.xFormat and self.hasXSize:
			r = self.xMax - self.xMin
			first = float(first)
			x = first * r + self.xMin
			self.xMinVar.set((self.xFormat % x).lstrip())
			last = float(last)
			x = last * r + self.xMin
			self.xMaxVar.set(self.xFormat % x)

	def xviewZoom(self, *args):
		apply(self.canvas.xview, args)
		if self.xFormat and self.hasXSize:
			first, last = self.zoomScrollbar.get()
			r = self.xMax - self.xMin
			x = first * r + self.xMin
			self.xMinVar.set((self.xFormat % x).lstrip())
			x = last * r + self.xMin
			self.xMaxVar.set(self.xFormat % x)

	def setSingleCallback(self, cb, closure):
		if self.track:
			self.singleCallback = self.singleTrack
			self.singleClosure = (cb, closure)
		else:
			self.singleCallback = cb
			self.singleClosure = closure
		for ds in self.dataSetList:
			ds.setSingleCallback(self.singleCallback,
							self.singleClosure)

	def setDoubleCallback(self, cb, closure):
		self.doubleCallback = cb
		self.doubleClosure = closure
		for ds in self.dataSetList:
			ds.setDoubleCallback(cb, closure)

	def addDataSet(self, dataSet):
		self.computeXRange(dataSet)
		self.computeYRange(dataSet)
		if self.xFormat:
			self.xMaxVar.set(self.xFormat % self.xMax)
			self.xMinVar.set((self.xFormat%self.xMin).lstrip())
		if self.yFormat:
			self.yMaxVar.set(self.yFormat % self.yMax)
			self.yMinVar.set(self.yFormat % self.yMin)
		dataSet.setTag(self, self.tag)
		self.tag = self.tag + 1
		self.computeScale()
		self.dataSetList.append(dataSet)
		self.redisplay()
		dataSet.setSingleCallback(self.singleCallback,
						self.singleClosure)
		dataSet.setDoubleCallback(self.doubleCallback,
						self.doubleClosure)

	def computeXRange(self, dataSet):
		if self.hasXSize:
			return
		xMin = xMax = dataSet.getX(0)
		for i in range(1, dataSet.length()):
			x = dataSet.getX(i)
			if x < xMin:
				xMin = x
			elif x > xMax:
				xMax = x
		if self.xPrecision > 0:
			xMin = _unitize(xMin, self.xPrecision, math.floor)
			xMax = _unitize(xMax, self.xPrecision, math.ceil)
		if len(self.dataSetList) == 0:
			self.xMin = xMin
			self.xMax = xMax
		else:
			if xMin < self.xMin:
				self.xMin = xMin
			elif xMax > self.xMax:
				self.xMax = xMax
		self.xSize = self.xMax - self.xMin
		self.hasXSize = 1

	def computeYRange(self, dataSet):
		if self.hasYSize:
			return
		yMin = yMax = dataSet.getY(0)
		for i in range(1, dataSet.length()):
			y = dataSet.getY(i)
			if y < yMin:
				yMin = y
			elif y > yMax:
				yMax = y
		if self.yPrecision > 0:
			yMin = _unitize(yMin, self.yPrecision, math.floor)
			yMax = _unitize(yMax, self.yPrecision, math.ceil)
		if len(self.dataSetList) == 0:
			self.yMin = yMin
			self.yMax = yMax
		else:
			if yMin < self.yMin:
				self.yMin = yMin
			elif yMax > self.yMax:
				self.yMax = yMax
		self.ySize = self.yMax - self.yMin

	def deleteDataSet(self, dataSet):
		dataSet.deleteItems()
		self.dataSetList.remove(dataSet)
		dsList = self.dataSetList
		self.dataSetList = []
		for ds in dsList:
			self.computeXRange(ds)
			self.computeYRange(ds)
			self.dataSetList.append(ds)
		self.computeScale()
		self.redisplay()
		if self.xFormat:
			self.xMaxVar.set(self.xFormat % self.xMax)
			self.xMinVar.set((self.xFormat%self.xMin).lstrip())
		if self.yFormat:
			self.yMaxVar.set(self.yFormat % self.yMax)
			self.yMinVar.set(self.yFormat % self.yMin)

	def redisplay(self):
		self.canvas.delete('all')
		for ds in self.dataSetList:
			ds.createItems()

	def rescale(self, event):
		self.canvasWidth = event.width - self.canvasBorder * 2 \
					- self.xMargin * 2
		self.canvasHeight = event.height - self.canvasBorder * 2 \
					- self.yMargin * 2
		if self.zoom:
			self.canvasWidth = self.canvasWidth * self.zoomFactor
			left = self.canvasBorder
			top = self.canvasBorder
			right = int(self.canvasWidth + 2 * self.xMargin)
			bottom = int(self.canvasHeight + 2 * self.yMargin)
			self.canvas['scrollregion'] = (left, top, right, bottom)
		self.computeScale()
		self.redisplay()

	def computeScale(self):
		if self.xSize != 0:
			self.xScale = self.canvasWidth / float(self.xSize)
		else:
			self.xScale = 0
		if self.ySize != 0:
			self.yScale = self.canvasHeight / float(self.ySize)
		else:
			self.yScale = 0

	def scale(self, x, y):
		mapX = (x - self.xMin) * self.xScale + self.xMargin
		mapY = (self.yMax - y) * self.yScale + self.yMargin
		return mapX, mapY

	def unscale(self, ex, ey):
		"map event coordinates (ex, ey) to data coordinates"
		mapX = self.canvas.canvasx(ex)
		mapY = self.canvas.canvasy(ey)
		x = (mapX - self.xMargin) / self.xScale + self.xMin
		y = self.yMax - (mapY - self.yMargin) / self.yScale
		return x, y

	def singleTrack(self, closure, ds, n):
		self.xVar.set(ds.getX(n))
		self.yVar.set(ds.getY(n))
		if callable(closure[0]):
			closure[0](closure[1], ds, n)

class DataSet:
	"""
	DataSet presents data points as unconnected items on the plot.
	Data is one of:
		two arrays (first is x; second is y),
		array of tuples (components 0 and 1 are x and y), or
		a single array of values (index is x, value is y).
	"""
	def __init__(self, x, y=None, makeItem=None, highlightItem=None,
			itemWidth=2, itemHeight=2, itemXShift=0, itemYShift=0,
			baseColor='black', highlightColor='red'):
		if y is not None:
			self.data = map(lambda a, b: (a, b), x, y)
		elif isinstance(x[0], tuple):
			self.data = x
		else:
			self.data = map(lambda a, b: (a, b), range(len(x)), x)
		if makeItem != None:
			self.makeItem = makeItem
		else:
			self.makeItem = self.circle
		if highlightItem != None:
			self.highlightItem = highlightItem
		else:
			self.highlightItem = self.highlightCircle
		self.baseColor = baseColor
		self.highlightColor = highlightColor
		self.litItem = -1
		self.itemWidth = itemWidth
		self.itemHeight = itemHeight
		self.itemXShift = itemXShift
		self.itemYShift = itemYShift

	def replaceData(self, x, y=None):
		assert(isinstance(x, list))
		if y is not None:
			self.data = map(lambda a, b: (a, b), x, y)
		elif len(x) > 0 and isinstance(x[0], tuple):
			self.data = x
		else:
			self.data = map(lambda a, b: (a, b), range(len(x)), x)
		self.deleteItems()
		self.createItems()

	def length(self):
		return len(self.data)

	def getX(self, n):
		return self.data[n][0]

	def getY(self, n):
		return self.data[n][1]

	def setTag(self, plot, tag):
		self.plot = plot
		self.tag = 'tag%d' % tag

	def circle(self, canvas, x, y, color):
		return Canvas.Oval(canvas,
				x - self.itemWidth + self.itemXShift,
				y - self.itemHeight + self.itemYShift,
				x + self.itemWidth + self.itemXShift,
				y + self.itemHeight + self.itemYShift,
				fill=color, outline=color,
				tags=(self.tag, 'all'))

	def highlightCircle(self, item, color):
		item['outline'] = color

	def setSingleCallback(self, cb, closure):
		if callable(cb):
			bf = lambda e, cb=cb, c=closure, f=self._singleCB: \
								f(cb, c, e)
			self.plot.canvas.tag_bind(self.tag,
						'<ButtonPress-1>', bf)
			self.plot.canvas.tag_bind(self.tag,
						'<ButtonRelease-1>', bf)
			self.plot.canvas.tag_bind(self.tag, '<B1-Motion>', bf)
		else:
			self.plot.canvas.tag_unbind(self.tag,
							'<ButtonPress-1>')
			self.plot.canvas.tag_unbind(self.tag,
							'<ButtonRelease-1>')
			self.plot.canvas.tag_unbind(self.tag, '<B1-Motion>')

	def setDoubleCallback(self, cb, closure):
		if callable(cb):
			self.plot.canvas.tag_bind(self.tag,
				'<Double-ButtonRelease-1>',
				lambda e, cb=cb, c=closure, f=self._doubleCB:
					f(cb, c, e))
		else:
			self.plot.canvas.tag_unbind(self.tag,
				'<Double-ButtonRelease-1>')

	def deleteItems(self):
		self.plot.canvas.delete(self.tag)

	def createItems(self):
		self.itemList = []
		self.canvasX = []
		self.canvasY = []
		for i in range(len(self.data)):
			mapX, mapY = self.plot.scale(self.data[i][0],
							self.data[i][1])
			item = self.makeItem(self.plot.canvas, mapX, mapY,
						self.baseColor)
			self.itemList.append(item)
			self.canvasX.append(mapX)
			self.canvasY.append(mapY)
		if self.litItem >= 0:
			self.highlightItem(self.itemList[self.litItem],
						self.highlightColor)

	def highlight(self, n):
		if self.litItem >= 0:
			self.highlightItem(self.itemList[self.litItem],
						self.baseColor)
		if n >= 0:
			self.highlightItem(self.itemList[n],
						self.highlightColor)
		self.litItem = n

	def _singleCB(self, cb, closure, event):
		n = self._findItem(event.x, event.y)
		self.highlight(n)
		cb(closure, self, n)

	def _doubleCB(self, cb, closure, event):
		n = self._findItem(event.x, event.y)
		self.highlight(n)
		cb(closure, self, n)

	def _findItem(self, x, y):
		cx = self.plot.canvas.canvasx(x)
		cy = self.plot.canvas.canvasy(y)
		best = -1
		bestDistance = -1
		for i in range(len(self.canvasX)):
			dx = cx - self.canvasX[i]
			dy = cy - self.canvasY[i]
			distance = dx * dx + dy * dy
			if best < 0 or distance < bestDistance:
				best = i
				bestDistance = distance
		return best

class SerialDataSet(DataSet):
	"""
	SerialDataSet displays data points as items connected by lines.
	"""
	def __init__(self, x, lineWidth=1.0, **kw):
		apply(DataSet.__init__, (self, x), kw)
		self.lineWidth = lineWidth

	def createItems(self):
		DataSet.createItems(self)
		coordArgs = []
		for i in range(len(self.canvasX)):
			coordArgs.append(self.canvasX[i])
			coordArgs.append(self.canvasY[i])
		lineTag = self.tag + 'Line'
		Canvas.Line(self.plot.canvas, coordArgs, 
			fill=self.baseColor,
			width=self.lineWidth,
			tags=(self.tag, lineTag, 'all'))
		self.plot.canvas.lower(lineTag)

class BarDataSet(DataSet):
	"""
	BarDataSet displays data points as vertical bars
	"""
	def __init__(self, x, **kw):
		apply(DataSet.__init__, (self, x), kw)

	def createItems(self):
		self.itemList = []
		self.canvasX = []
		self.canvasY = []
		ignore, y2 = self.plot.scale(0, self.plot.yMin)
		for i in range(len(self.data)):
			mapX, mapY = self.plot.scale(self.data[i][0],
							self.data[i][1])
			x1 = mapX - self.itemWidth + self.itemXShift
			y1 = mapY
			x2 = mapX + self.itemWidth + self.itemXShift
			item = Canvas.Rectangle(self.plot.canvas,
						x1, y1, x2, y2,
						fill=self.baseColor,
						outline=self.baseColor,
						tags=(self.tag, 'all'))
			self.itemList.append(item)
			self.canvasX.append(mapX)
			self.canvasY.append(mapY)
		if self.litItem >= 0:
			self.highlightItem(self.itemList[self.litItem],
						self.highlightColor)

	def _findItem(self, x, y):
		cx = self.plot.canvas.canvasx(x)
		best = -1
		bestDistance = -1
		for i in range(len(self.canvasX)):
			dx = cx - self.canvasX[i]
			distance = dx * dx
			if best < 0 or distance < bestDistance:
				best = i
				bestDistance = distance
		return best

class ThreeDDataSet(DataSet):
	"""
	ThreeDDataSet takes an array of (x, y, z)-tuples and two
	colors.  z-values are used to interpolate between the two
	colors so that the minimum matches the first color; the
	maximum matches the second color; and intermediate values
	interpolate between the min and max colors in HLS or RGB space.
	Colors are specified as (r, g, b) tuples where r, g and b
	are between 0 and 1, inclusive.
	"""
	def __init__(self, data, minColor, maxColor, interp='HLS', **kw):
		apply(DataSet.__init__, (self, data), kw)
		zMin = zMax = data[0][2]
		for i in range(1, len(data)):
			z = data[i][2]
			if z < zMin:
				zMin = z
			elif z > zMax:
				zMax = z
		self.itemColor = []
		if interp == 'HLS':
			self._interpHLS(data, zMin, zMax, minColor, maxColor)
		elif interp == 'RGB':
			self._interpRGB(data, zMin, zMax, minColor, maxColor)
		else:
			raise ValueError, 'unknown interpolation space'

	def _interpHLS(self, data, zMin, zMax, minColor, maxColor):
		self.minHLS = apply(colorsys.rgb_to_hls, minColor)
		self.maxHLS = apply(colorsys.rgb_to_hls, maxColor)
		if self.minHLS[2] == 0:
			# minHLS is gray, so match hue with maxHLS
			self.minHLS[0] = self.maxHLS[0]
		if self.maxHLS[2] == 0:
			# maxHLS is gray, so match hue with minHLS
			self.maxHLS[0] = self.minHLS[0]
		minH = float(self.minHLS[0])
		dH = self.maxHLS[0] - minH
		minL = float(self.minHLS[1])
		dL = self.maxHLS[1] - minL
		minS = float(self.minHLS[2])
		dS = self.maxHLS[2] - minS
		dZ = float(zMax - zMin)
		if dZ == 0:
			dZ = 1
		for i in range(len(data)):
			f = (data[i][2] - zMin) / dZ
			h = minH + f * dH
			l = minL + f * dL
			s = minS + f * dS
			red, green, blue = colorsys.hls_to_rgb(h, l, s)
			r = int(red * 255 + 0.5)
			g = int(green * 255 + 0.5)
			b = int(blue * 255 + 0.5)
			self.itemColor.append('#%02x%02x%02x' % (r, g, b))

	def _interpRGB(self, data, zMin, zMax, minColor, maxColor):
		minR = minColor[0]
		dR = maxColor[0] - minColor[0]
		minG = minColor[1]
		dG = maxColor[1] - minColor[1]
		minB = minColor[2]
		dB = maxColor[2] - minColor[2]
		dZ = float(zMax - zMin)
		for i in range(len(data)):
			if dZ == 0:
				f = 0.5
			else:
				f = (data[i][2] - zMin) / dZ
			r = int((minR + f * dR) * 255 + 0.5)
			g = int((minG + f * dG) * 255 + 0.5)
			b = int((minB + f * dB) * 255 + 0.5)
			# We may want to saturate the color
			self.itemColor.append('#%02x%02x%02x' % (r, g, b))

	def createItems(self):
		self.itemList = []
		self.canvasX = []
		self.canvasY = []
		for i in range(len(self.data)):
			mapX, mapY = self.plot.scale(self.data[i][0],
							self.data[i][1])
			item = self.makeItem(self.plot.canvas, mapX, mapY,
						self.itemColor[i])
			self.itemList.append(item)
			self.canvasX.append(mapX)
			self.canvasY.append(mapY)
		if self.litItem >= 0:
			self.highlightItem(self.itemList[self.litItem],
						self.highlightColor)

	def highlight(self, n):
		if self.litItem >= 0:
			self.highlightItem(self.itemList[self.litItem],
						self.itemColor[self.litItem])
		if n >= 0:
			self.highlightItem(self.itemList[n],
						self.highlightColor)
		self.litItem = n

if __name__ == '__main__':
	def singleCB(closure, ds, n):
		print 'singleclick: dataset=%s index=%d' % (ds, n)
	def doubleCB(closure, ds, n):
		print 'doubleclick: dataset=%s index=%d' % (ds, n)
	def addBarData():
		ap.addDataSet(barDs)
		barButton['state'] = Tkinter.DISABLED
	def addSerialData():
		ap.addDataSet(serialDs)
		serialButton['state'] = Tkinter.DISABLED
	def add3DData():
		ap.addDataSet(threeDDs)
		threeDButton['state'] = Tkinter.DISABLED
	ds = DataSet([1.1, 2.2, 3.3])
	serialDs = SerialDataSet([4.5, 2.7, 1.9], baseColor='green')
	barDs = BarDataSet([0.5, 1.7, 1.4, 3.7], baseColor='cyan')
	threeDDs = ThreeDDataSet([(0.5, 0, 0), (0.5, 1, 1),
					(0.5, 2, 2), (0.5, 3, 3)],
					(1, 0, 0), (0, 1, 0),
					highlightColor='black')
	app = Tkinter.Frame()
	app.pack(fill=Tkinter.BOTH, expand=Tkinter.TRUE)
	b = Tkinter.Button(app, text='Quit', command=app.quit)
	b.pack(side=Tkinter.TOP, fill=Tkinter.X)
	barButton = Tkinter.Button(app, text='Add Bar Data', command=addBarData)
	barButton.pack(side=Tkinter.TOP, fill=Tkinter.X)
	serialButton = Tkinter.Button(app, text='Add Serial Data',
					command=addSerialData)
	serialButton.pack(side=Tkinter.TOP, fill=Tkinter.X)
	threeDButton = Tkinter.Button(app, text='Add 3D Data',
					command=add3DData)
	threeDButton.pack(side=Tkinter.TOP, fill=Tkinter.X)
	ap = ActivePlot(master=app,
			track=Tkinter.TRUE, zoom=Tkinter.TRUE,
			xFormat='%4.1f', yFormat='%5.1f',
			xPrecision=0, yPrecision=1.0,
			singleCallback=singleCB,
			doubleCallback=doubleCB,
			dataSet=ds,
			labelCnf={'relief':Tkinter.FLAT},
			controlCnf={'bd':2, 'relief':Tkinter.SUNKEN},
			plotCnf={'bd':2, 'relief':Tkinter.SUNKEN},
			canvasCnf={'bd':2, 'relief':Tkinter.RIDGE})
	ap.pack(fill=Tkinter.BOTH, expand=Tkinter.TRUE)
	app.mainloop()
