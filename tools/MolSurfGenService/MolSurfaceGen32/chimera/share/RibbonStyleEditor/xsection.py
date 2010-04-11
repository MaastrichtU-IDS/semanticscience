import weakref
import chimera
from chimera import Residue

# prefXSection should be set to a dictionary in a HiddenCategory
# created in base.py.  Whenever we change things in userXS, we
# also change the corresponding item in prefXSection so that
# preferences.save() will always get the right values.
prefXSection = None
systemXS = {}
userXS = {}
xsName = weakref.WeakKeyDictionary()
Trigger = "RibbonStyleXSectionListChanged"
xsUnnamed = "unnamed"
xsId = 1

NameToDrawMode = {
	"flat":		Residue.Ribbon_2D,
	"edged":	Residue.Ribbon_Edged,
	"rounded":	Residue.Ribbon_Round,
}
Reserved = [ "round", "smooth", "sharp", "ribbon" ]
DrawModeToName = {}
for name, value in NameToDrawMode.iteritems():
	DrawModeToName[value] = name
del name, value

def makeSuperSmooth():
	from math import sin, cos, pi
	steps = 100
	twopi = pi * 2
	xs = chimera.RibbonXSection(True, True, True)
	for i in range(steps):
		angle = twopi * i / steps
		y = cos(angle)
		x = sin(angle)
		xs.addOutlineVertex(x, y)
	return xs

def initialize(p):
	# create system cross sections
	# XXX The second parameter in the following dictionary item is
	# the "grid" size.  The coordinates in the cross sections when
	# multiplied by "grid" should yield an integer value.  If not,
	# the outline will be displayed incorrectly.
	defaultMap = {
		"flat":	  (chimera.RibbonXSection.line(), 10),
		"edged":  (chimera.RibbonXSection.square(), 10),
		"rounded": (chimera.RibbonXSection.circle(), 50),
		"supersmooth": (makeSuperSmooth(), 100),
	}
	for name, (xsection, grid) in defaultMap.iteritems():
		xs = XS(name)
		mode = NameToDrawMode.get(name, Residue.Ribbon_Custom)
		xs.setXS(xsection, mode, grid)
		systemXS[name] = xs
		xsName[xsection] = (name, grid)

	# create user cross sections
	global prefXSection
	prefXSection = p
	for name, values in p.items():
		points = values[0]
		if len(points) < 3:
			del p[name]
		else:
			userXS[name] = XS(name, *values)

	# Add trigger for xsection updates
	chimera.triggers.addTrigger(Trigger)

class XSectionEditor:

	def __init__(self, parent, dialog):

		self.points = []
		self.divisions = 10
		self.closed = 0
		self.smoothacross = 0
		self.smoothalong = 0
		self.mapped = 0
		self.dialog = dialog
		self.currentXS = None

		from chimera.preferences import saveui
		self.saveui = saveui.SaveUI(parent, self)

		import Tkinter, Pmw
		f = Tkinter.Frame(parent)
		f.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)
		self.opt = Pmw.RadioSelect(f,
				buttontype="checkbutton",
				command=self._optChange,
				orient="vertical",
				labelpos="n",
				label_text="Display Options",
				pady=0,
				hull_borderwidth=2,
				hull_relief=Tkinter.RIDGE)
		self.opt.pack(side=Tkinter.TOP)
		self.opt.add("closed", text="Closed cross section")
		self.opt.add("smoothacross", text="Smooth across ribbon")
		self.opt.add("smoothalong", text="Smooth along ribbon")
		t = Tkinter.Label(f, text="Click to add point; "
						"BackSpace to delete point.",
						fg="gray40")
		t.pack(side=Tkinter.TOP)
		t = Tkinter.Label(f, text="Changing grid division "
						"erases drawn cross section!",
						fg="gray40")
		t.pack(side=Tkinter.BOTTOM)
		subf = Tkinter.Frame(f)
		subf.pack(side=Tkinter.BOTTOM)
		self.div = Pmw.Counter(subf,
				labelpos="w",
				label_text="Number of grid divisions:",
				entry_width=3,
				entryfield_modifiedcommand=self._setDivisions,
				entryfield_value=self.divisions,
				entryfield_validate = {
					"validator":"integer",
					"minstrict":0, "maxstrict": 0,
					"min":4, "max":100 })
		self.div.pack(side=Tkinter.LEFT)
		self.divEntryfield = self.div.component("entryfield")
		self.erase = Tkinter.Button(subf, text="Erase All",
						command=self._erase)
		self.erase.pack(side=Tkinter.LEFT)
		self._makeDrawingSurface(f)

		item = self.saveui_defaultItem()
		if item:
			self.saveui_select(item)

	def _makeDrawingSurface(self, parent):
		import Tkinter
		f = Tkinter.Frame(parent, bd=2, relief=Tkinter.RIDGE)
		f.pack(expand=1, fill=Tkinter.BOTH)
		self.canvas = Tkinter.Canvas(f, bd=0, highlightthickness=0,
						bg="white", takefocus="1",
						width=200, height=200)
		self.grid = []
		self.outline = None
		self.curPoint = None
		self.canvasWidth = 0
		self.canvasHeight = 0
		self.drawingSize = 0
		self.drawingXStart = 0
		self.drawingXEnd = 0
		self.drawingYStart = 0
		self.drawingYEnd = 0
		self.canvas.bind("<Configure>", self._configureCanvas)
		self.canvas.bind("<ButtonRelease>", self._addPoint)
		self.canvas.bind("<BackSpace>", self._deletePoint)
		self.canvas.bind("<Delete>", self._deletePoint)
		self.canvas.bind("<Enter>", self._canvasEnter)
		self.canvas.bind("<Motion>", self._movePoint)
		self.canvas.pack(expand=1, fill=Tkinter.BOTH)

	def _optChange(self, option, onoff):
		self.currentXS = None
		setattr(self, option, onoff)
		if option == "closed":
			self._remakeOutline()

	def _setDivisions(self):
		self.currentXS = None
		if not self.divEntryfield.valid():
			return
		d = int(self.divEntryfield.get())
		if d == self.divisions:
			return
		self.divisions = d
		if self.outline:
			self.outline.delete()
			self.outline = None
		self.points = []
		self._configureCanvas()

	def _configureCanvas(self, event=None):
		import Canvas
		if event is not None:
			self.mapped = True
			if (event.width == self.canvasWidth
			and event.height == self.canvasHeight):
				return
			self.canvasWidth = event.width
			self.canvasHeight = event.height
		# Leave some space for user to draw right
		# to the edge of canvas
		self.drawingSize = min(self.canvasWidth, self.canvasHeight) - 10
		self.drawingXStart = (self.canvasWidth - self.drawingSize) / 2
		self.drawingXEnd = self.drawingXStart + self.drawingSize
		self.drawingYStart = (self.canvasHeight - self.drawingSize) / 2
		self.drawingYEnd = self.drawingYStart + self.drawingSize
		self.scale = float(self.drawingSize) / self.divisions

		# Remake grid lines
		for line in self.grid:
			line.delete()
		self.grid = []
		for i in range(self.divisions + 1):
			line = Canvas.Line(self.canvas,
						[self._mapToCanvas((i, 0)),
						 self._mapToCanvas(
						 	(i, self.divisions))],
						fill="gray")
			self.grid.append(line)
			line = Canvas.Line(self.canvas,
						[self._mapToCanvas((0, i)),
						 self._mapToCanvas(
						 	(self.divisions, i))],
						fill="gray")
			self.grid.append(line)
		self._remakeOutline()
		self.canvas.focus_set()

	def _remakeOutline(self):
		if not self.mapped:
			return
		import Canvas
		if self.outline:
			self.outline.delete()
		if not self.points:
			self.outline = None
		elif len(self.points) < 2:
			pt = self._mapToCanvas(self.points[0])
			ul = (pt[0] - 1, pt[1] - 1)
			lr = (pt[0] + 1, pt[1] + 1)
			self.outline = Canvas.Rectangle(self.canvas, [ul, lr],
							fill="black")
		else:
			coords = []
			for pt in self.points:
				coords.append(self._mapToCanvas(pt))
			if "closed" in self.opt.getvalue():
				if self.points[0] != self.points[-1]:
					coords.append(self._mapToCanvas(self.points[0]))
				else:
					del self.points[-1]
			self.outline = Canvas.Line(self.canvas, coords,
						fill="black", width=3)

	def _addPoint(self, event):
		self.currentXS = None
		pt = self._mapFromCanvas(event)
		if not self.points or self.points[-1] != pt:
			self.points.append(pt)
		self._remakeOutline()

	def _deletePoint(self, event):
		self.currentXS = None
		if not self.points:
			return
		del self.points[-1]
		self._remakeOutline()

	def _movePoint(self, event):
		import Canvas
		pt = self._mapToCanvas(self._mapFromCanvas(event))
		if self.curPoint:
			self.curPoint.delete()
		ul = (pt[0] - 1, pt[1] - 1)
		lr = (pt[0] + 1, pt[1] + 1)
		self.curPoint = Canvas.Rectangle(self.canvas, [ul, lr],
							outline="red")

	def _mapFromCanvas(self, event):
		if event.x < self.drawingXStart:
			x = 0
		elif event.x >= self.drawingXEnd:
			x = self.divisions
		else:
			x = int(round((event.x - self.drawingXStart)
					/ self.scale))
		if event.y < self.drawingYStart:
			y = 0
		elif event.y >= self.drawingYEnd:
			y = self.divisions
		else:
			y = int(round((event.y - self.drawingYStart)
					/ self.scale))
		return x, y

	def _mapToCanvas(self, pt):
		x = self.drawingXStart + pt[0] * self.scale
		y = self.drawingYStart + pt[1] * self.scale
		return x, y

	def _canvasEnter(self, event):
		self.canvas.focus_set()

	def _erase(self):
		self.points = []
		self._remakeOutline()

	def _showXSection(self, name):
		xs = findXSection(name)
		values = []
		self.smoothacross = xs.sw
		if xs.sw:
			values.append("smoothacross")
		self.smoothalong = xs.sl
		if xs.sl:
			values.append("smoothalong")
		self.closed = xs.closed
		if xs.closed:
			values.append("closed")
		self.opt.setvalue(values)
		self.divEntryfield.setvalue(str(xs.grid))
		self.points = xs.points
		self._remakeOutline()
		self.currentXS = xs

	def Apply(self, restrict):
		if self.currentXS:
			xs = self.currentXS
		else:
			xs = XS(None, self.points, self.smoothacross,
				self.smoothalong, self.closed,
				self.divisions)
		if restrict:
			from chimera import selection
			rList = selection.currentResidues()
		else:
			rList = []
		if rList:
			for r in rList:
				xs.setResidue(r)
		else:
			for m in chimera.openModels.list(
					modelTypes=[chimera.Molecule]):
				for r in m.residues:
					xs.setResidue(r)

	# SaveUI callback functions
	def saveui_label(self):
		return "Ribbon Cross Section"

	def saveui_presetItems(self):
		return systemXS.keys()

	def saveui_userItems(self):
		return userXS.keys()

	def saveui_defaultItem(self):
		try:
			return userXS.keys()[0]
		except IndexError:
			return systemXS.keys()[0]

	def saveui_select(self, name):
		self._showXSection(name)

	def saveui_save(self, name):
		if name in Reserved:
			from chimera import replyobj
			replyobj.error("%s is a reserved name.  "
					"Please choose a different name."
					% name)
			return False
		try:
			checkXSection(self.closed, self.points)
		except ValueError, s:
			from chimera import replyobj
			replyobj.error(s)
			return False
		from chimera import preferences
		addXSection(name, self.points,
				self.smoothacross, self.smoothalong,
				self.closed, self.divisions)
		preferences.save()
		redisplayMenu()
		self.dialog.status("Setting \"%s\" saved" % name)
		return True

	def saveui_delete(self, name):
		from chimera import preferences
		removeXSection(name)
		preferences.save()
		redisplayMenu()
		self.dialog.status("Setting \"%s\" deleted" % name)
		return True

class XS:
	def __init__(self, name, points=None, sw=None, sl=None,
				closed=None, grid=None):
		# "points" should be integer coordinates in
		# the range [0, grid].  This is necessary to
		# make the cross section displayable in the editor.
		if name is None:
			global xsId
			name = "%s%d" % (xsUnnamed, xsId)
			xsId += 1
		self.name = name
		self.points = points
		self.sw = sw
		self.sl = sl
		self.closed = closed
		self.grid = grid
		self.xs = None
		self.mode = Residue.Ribbon_Custom

	def setXS(self, xs, mode, grid):
		self.xs = xs
		self.mode = mode
		def mapToGrid(c):
			return int(round(((c / 2 + 0.5) * grid)))
		self.points = [ (mapToGrid(x), mapToGrid(y))
					for x, y in xs.outline ]
		self.sw = xs.smoothWidth
		self.sl = xs.smoothLength
		self.closed = xs.closed
		self.grid = grid

	def setResidue(self, r):
		if self.mode == Residue.Ribbon_Custom:
			r.ribbonDrawMode = r.Ribbon_Custom
			r.ribbonXSection = self.getXS()
		else:
			r.ribbonDrawMode = self.mode
			r.ribbonXSection = None

	def getXS(self):
		if self.xs is None:
			self._makeXSection()
		return self.xs

	def _makeXSection(self):
		try:
			checkXSection(self.closed, self.points)
		except ValueError, s:
			from chimera import replyobj
			replyobj.error(s)
			return False
		xs = chimera.RibbonXSection(self.sw, self.sl, self.closed)
		# Figure out whether the points are in clockwise
		# or counterclockwise order.  Back-face culling
		# of polygons requires one particular direction.
		try:
			p = chimera.Plane([ chimera.Point(x, y, 0)
						for x, y in self.points ])
		except chimera.error:
			# probably caused by colinear points
			pass
		else:
			if p.normal.z > 0:
				self.points.reverse()
		outline = []
		g = float(self.grid)
		for x, y in self.points:
			mx = ((x / g) - 0.5) * 2.0
			my = ((y / g) - 0.5) * 2.0
			outline.append((mx, my))
		xs.outline = outline
		self.xs = xs
		xsName[xs] = (self.name, self.grid)

def findXSection(name):
	try:
		return userXS[name]
	except KeyError:
		return systemXS.get(name, None)

def addXSection(name, points, sw, sl, closed, grid):
	exists = prefXSection.has_key(name)
	prefXSection[name] = (points, sw, sl, closed, grid)
	xs = XS(name, points, sw, sl, closed, grid)
	userXS[name] = xs
	if not exists:
		chimera.triggers.activateTrigger(Trigger, name)

def removeXSection(name):
	del prefXSection[name]
	del userXS[name]
	chimera.triggers.activateTrigger(Trigger, name)

def getXSectionName(r):
	try:
		return DrawModeToName[r.ribbonDrawMode]
	except KeyError:
		try:
			return xsName[r.ribbonXSection][0]
		except (KeyError, TypeError):
			return "none"

def setXSectionByName(r, name):
	xs = findXSection(name)
	if xs:
		xs.setResidue(r)
	else:
		from chimera import replyobj
		replyobj.error("cannot find ribbon XS named %s" % name)

def listXSections(all=False):
	if all:
		return systemXS.keys() + userXS.keys()
	else:
		return userXS.keys()

def redisplayMenu():
	from chimera.actions import setRibbonCustom
	menubar = chimera.tkgui.app.menubar
	aMenu = menubar.nametowidget(menubar.entrycget("Actions", "menu"))
	rMenu = aMenu.nametowidget(aMenu.entrycget("Ribbon", "menu"))
	end = rMenu.index("end")
	last = None
	for n in range(end + 1):
		if rMenu.type(n) == "separator":
			last = n
	if end >= last + 1:
		rMenu.delete(last + 1, "end")
	name = "supersmooth"
	rMenu.add_command(label=name, command=lambda
				xs=findXSection(name).getXS():
				setRibbonCustom(xs))
	names = userXS.keys()
	names.sort()
	for name in names:
		rMenu.add_command(label=name, command=lambda
					xs=findXSection(name).getXS():
					setRibbonCustom(xs))

# Following methods are used for saving and restoring session

def sessionSaveUsed():
	values = []
	for n, v in prefXSection.iteritems():
		values.append((n, v))
	def mapToGrid(c, grid):
		return int(round(((c / 2 + 0.5) * grid)))
	for xs, (n, grid) in xsName.items():
		if n in systemXS or n in userXS:
			continue
		points = [ (mapToGrid(x, grid), mapToGrid(y, grid))
					for x, y in xs.outline ]
		sw = xs.smoothWidth
		sl = xs.smoothLength
		closed = xs.closed
		v = (points, sw, sl, closed, grid)
		values.append((n, v))
	return values

def sessionSaveResidue(r):
	return getXSectionName(r)

def sessionRestoreUsed(used):
	unnamed = {}
	for n, v in used:
		if n.startswith(xsUnnamed):
			xs = XS(n, *v)
			unnamed[n] = xs
			xsName[xs.getXS()] = (n, xs.grid)
		else:
			addXSection(n, *v)
	return unnamed

def sessionRestoreResidue(r, n, d):
	try:
		xs = d[n]
	except KeyError:
		try:
			xs = userXS[n]
		except KeyError:
			try:
				xs = systemXS[n]
			except KeyError:
				return
	xs.setResidue(r)

def checkXSection(closed, points):
	if closed:
		if len(points) < 3:
			raise ValueError("closed cross section outline must "
						"have at least 3 points")
	else:
		if len(points) < 2:
			raise ValueError("cross section outline must "
						"have at least 2 points")
