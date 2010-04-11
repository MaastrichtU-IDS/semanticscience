import weakref
import chimera
from chimera import Residue

prefScaling = None
SystemDefault = "Chimera default"
userScaling = {}
systemScaling = {}
scalingName = weakref.WeakKeyDictionary()
Trigger = "RibbonStyleScalingListChanged"
scalingUnnamed = "unnamed"
scalingId = 1

SaveOrder = [
	Residue.RS_TURN,
	Residue.RS_HELIX,
	Residue.RS_SHEET,
	Residue.RS_ARROW,
	Residue.RS_NUCLEIC,
]
SaveTypes = {
	Residue.RS_TURN:	chimera.RibbonStyleFixed,
	Residue.RS_HELIX:	chimera.RibbonStyleFixed,
	Residue.RS_SHEET:	chimera.RibbonStyleFixed,
	Residue.RS_ARROW:	chimera.RibbonStyleTapered,
	Residue.RS_NUCLEIC:	chimera.RibbonStyleFixed,
}

ChimeraScalings = {
	"licorice": [
			[ 0.35, 0.35, ],		# turn
			[ 0.35, 0.35, ],		# helix
			[ 0.35, 0.35, ],		# sheet
			[ 0.35, 0.35, 0.35, 0.35],	# arrow
			[ 0.35, 0.35, ],		# nucleic
	]
}

def initialize(p):
	# create system scaling
	getRS = chimera.Residue.getDefaultRibbonStyle
	systemScaling[SystemDefault]  = Scaling(SystemDefault,
						scales=[ getRS(type)
							for type in SaveOrder ])
	# add other Chimera default scalings
	for name, pList in ChimeraScalings.iteritems():
		if name not in userScaling:
			systemScaling[name] = Scaling(name, pList)

	# create user scaling
	global prefScaling
	prefScaling = p

	# make sure user scaling values have current number of entries
	for name, values in prefScaling.iteritems():
		if not name:
			# ignore old convention of overriding system
			# default with user default
			continue
		values = convertSaved(values)
		userScaling[name] = Scaling(name, pList=values)

	# Add trigger for scaling updates
	chimera.triggers.addTrigger(Trigger)

# Indices below are for old style ribbon preferences
I_TURN_WIDTH = 0
I_TURN_THICKNESS = 1
I_HELIX_WIDTH = 2
I_HELIX_THICKNESS = 3
I_SHEET_WIDTH = 4
I_SHEET_THICKNESS = 5
I_ARROW_TIP_WIDTH = 6
I_ARROW_TIP_THICKNESS = 7
I_ARROW_BASE_WIDTH = 8
I_ARROW_BASE_THICKNESS = 9
I_NUCLEIC_WIDTH = 10
I_NUCLEIC_THICKNESS = 11

def convertSaved(values):
	if len(values) == 10:
		# expand with I_NUCLEIC_WIDTH and I_NUCLEIC_THICKNESS
		# which used to be the same as the helix parameters
		values = [
				[ values[I_TURN_WIDTH],
				  values[I_TURN_THICKNESS] ],
				[ values[I_HELIX_WIDTH],
				  values[I_HELIX_THICKNESS] ],
				[ values[I_SHEET_WIDTH],
				  values[I_SHEET_THICKNESS] ],
				[ values[I_ARROW_TIP_WIDTH],
				  values[I_ARROW_TIP_THICKNESS],
				  values[I_ARROW_BASE_WIDTH],
				  values[I_ARROW_BASE_THICKNESS] ],
				[ values[I_HELIX_WIDTH],
				  values[I_HELIX_THICKNESS] ],
		]
	elif len(values) == 12:
		values = [
				[ values[I_TURN_WIDTH],
				  values[I_TURN_THICKNESS] ],
				[ values[I_HELIX_WIDTH],
				  values[I_HELIX_THICKNESS] ],
				[ values[I_SHEET_WIDTH],
				  values[I_SHEET_THICKNESS] ],
				[ values[I_ARROW_TIP_WIDTH],
				  values[I_ARROW_TIP_THICKNESS],
				  values[I_ARROW_BASE_WIDTH],
				  values[I_ARROW_BASE_THICKNESS] ],
				[ values[I_NUCLEIC_WIDTH],
				  values[I_NUCLEIC_THICKNESS] ]
		]
	return values

class ScalingEditor:

	def __init__(self, parent, dialog):
		getRS = chimera.Residue.getDefaultRibbonStyle
		self.currentScaling = None
		self.dialog = dialog

		from chimera.preferences import saveui
		self.saveui = saveui.SaveUI(parent, self)

		import Tkinter
		f = Tkinter.Frame(parent)
		f.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)
		l = Tkinter.Label(f, text="Width")
		l.grid(column=1, row=0)
		l = Tkinter.Label(f, text="Height")
		l.grid(column=2, row=0)
		l = Tkinter.Label(f, text="Turn")
		l.grid(column=0, row=1)
		l = Tkinter.Label(f, text="Helix")
		l.grid(column=0, row=2)
		l = Tkinter.Label(f, text="Sheet")
		l.grid(column=0, row=3)
		l = Tkinter.Label(f, text="Arrow (base)")
		l.grid(column=0, row=4)
		l = Tkinter.Label(f, text="Arrow (tip)")
		l.grid(column=0, row=5)
		l = Tkinter.Label(f, text="Nucleic")
		l.grid(column=0, row=6)

		self.turnWidth = self._makeCounter(f)
		self.turnWidth.grid(column=1, row=1)
		self.turnHeight = self._makeCounter(f)
		self.turnHeight.grid(column=2, row=1)
		self.helixWidth = self._makeCounter(f)
		self.helixWidth.grid(column=1, row=2)
		self.helixHeight = self._makeCounter(f)
		self.helixHeight.grid(column=2, row=2)
		self.sheetWidth = self._makeCounter(f)
		self.sheetWidth.grid(column=1, row=3)
		self.sheetHeight = self._makeCounter(f)
		self.sheetHeight.grid(column=2, row=3)
		self.arrowTipWidth = self._makeCounter(f)
		self.arrowTipWidth.grid(column=1, row=4)
		self.arrowTipHeight = self._makeCounter(f)
		self.arrowTipHeight.grid(column=2, row=4)
		self.arrowBaseWidth = self._makeCounter(f)
		self.arrowBaseWidth.grid(column=1, row=5)
		self.arrowBaseHeight = self._makeCounter(f)
		self.arrowBaseHeight.grid(column=2, row=5)
		self.nucleicWidth = self._makeCounter(f)
		self.nucleicWidth.grid(column=1, row=6)
		self.nucleicHeight = self._makeCounter(f)
		self.nucleicHeight.grid(column=2, row=6)
		self.counters = [
			self.turnWidth, self.turnHeight,
			self.helixWidth, self.helixHeight,
			self.sheetWidth, self.sheetHeight,
			self.arrowTipWidth, self.arrowTipHeight,
			self.arrowBaseWidth, self.arrowBaseHeight,
			self.nucleicWidth, self.nucleicHeight,
		]
		self.saveui_select(self.saveui_defaultItem())

	def _makeCounter(self, parent):
		import Pmw
		return Pmw.Counter(parent,
					entry_width=6,
					entry_justify="center",
					entryfield_value="1.0",
					entryfield_validate={
						"validator":"real",
						"minstrict":0,
						"maxstrict":0,
						"min":0.05, "max":10
					},
					entryfield_modifiedcommand=
						self._counterChanged,
					datatype={"counter":"real"},
					increment=0.05)

	def _counterChanged(self):
		self.currentScaling = None

	def _makeScalingValues(self):
		return [
			[ float(self.turnWidth.get()),
			  float(self.turnHeight.get()) ],
			[ float(self.helixWidth.get()),
			  float(self.helixHeight.get()) ],
			[ float(self.sheetWidth.get()),
			  float(self.sheetHeight.get()) ],
			[ float(self.arrowTipWidth.get()),
			  float(self.arrowTipHeight.get()),
			  float(self.arrowBaseWidth.get()),
			  float(self.arrowBaseHeight.get()) ],
			[ float(self.nucleicWidth.get()),
			  float(self.nucleicHeight.get()) ],
		]

	def Apply(self, restrict):
		for c in self.counters:
			if not c.valid():
				replyobj.error("invalid entry field")
				return
		if self.currentScaling:
			sc = self.currentScaling
		else:
			sc = Scaling(None, self._makeScalingValues())
		sc.apply(restrict)

	# SaveUI callback functions
	def saveui_label(self):
		return "Ribbon Scaling"

	def saveui_presetItems(self):
		return systemScaling.keys()

	def saveui_userItems(self):
		return prefScaling.keys()

	def saveui_defaultItem(self):
		return SystemDefault

	def saveui_select(self, name):
		try:
			sc = userScaling[name]
		except KeyError:
			sc = systemScaling[name]
		turn = sc.parameters[Residue.RS_TURN]
		self.turnWidth.setvalue(tostr(turn[0]))
		self.turnHeight.setvalue(tostr(turn[1]))
		helix = sc.parameters[Residue.RS_HELIX]
		self.helixWidth.setvalue(tostr(helix[0]))
		self.helixHeight.setvalue(tostr(helix[1]))
		sheet = sc.parameters[Residue.RS_SHEET]
		self.sheetWidth.setvalue(tostr(sheet[0]))
		self.sheetHeight.setvalue(tostr(sheet[1]))
		arrow = sc.parameters[Residue.RS_ARROW]
		self.arrowTipWidth.setvalue(tostr(arrow[0]))
		self.arrowTipHeight.setvalue(tostr(arrow[1]))
		self.arrowBaseWidth.setvalue(tostr(arrow[2]))
		self.arrowBaseHeight.setvalue(tostr(arrow[3]))
		nucleic = sc.parameters[Residue.RS_NUCLEIC]
		self.nucleicWidth.setvalue(tostr(nucleic[0]))
		self.nucleicHeight.setvalue(tostr(nucleic[1]))
		self.currentScaling = sc

	def saveui_save(self, name):
		from chimera import preferences
		addScaling(name, self._makeScalingValues())
		preferences.save()
		self.dialog.status("Setting \"%s\" saved" % name)
		return True

	def saveui_delete(self, name):
		from chimera import preferences
		removeScaling(name)
		preferences.save()
		self.dialog.status("Setting \"%s\" deleted" % name)
		return True

class Scaling:
	def __init__(self, name, pList=None, scales=None):
		if name is None:
			global scalingId
			name = "%s%d" % (scalingUnnamed, scalingId)
			scalingId += 1
		self.name = name
		self.pList = pList
		self.parameters = {}
		self.scales = {}
		if pList:
			for i, param in enumerate(pList):
				self.parameters[SaveOrder[i]] = param
		else:
			for i, sc in enumerate(scales):
				type = SaveOrder[i]
				self.scales[type] = sc
				self.parameters[type] = sc.size
				scalingName[sc] = (self.name, self.pList)

	def apply(self, restrict=False):
		if restrict:
			from chimera import selection
			rList = selection.currentResidues()
		else:
			rList = []
		if rList:
			for r in rList:
				self.setResidue(r)
		else:
			for m in chimera.openModels.list(
					modelTypes=[chimera.Molecule]):
				for r in m.residues:
					self.setResidue(r)

	def setResidue(self, r):
		ss = r.ribbonFindStyleType()
		r.ribbonStyle = self.getScale(ss)

	def getScale(self, type):
		try:
			sc = self.scales[type]
		except KeyError:
			sc = SaveTypes[type](self.parameters[type])
			self.scales[type] = sc
			scalingName[sc] = (self.name, self.pList)
		return sc

	def parameterList(self):
		return [ self.parameters[type] for type in SaveOrder ]

def getScalingName(r):
	if r.ribbonStyle is None:
		return SystemDefault
	try:
		return scalingName[r.ribbonStyle][0]
	except KeyError:
		return "none"

def setScalingByName(r, name):
	try:
		sc = userScaling[name]
	except KeyError:
		try:
			sc = systemScaling[name]
		except KeyError:
			from chimera import replyobj
			replyobj.error("no ribbon scaling named \"%s\"" % name)
			return
	sc.setResidue(r)

def addScaling(name, pList):
	exists = prefScaling.has_key(name)
	prefScaling[name] = pList
	userScaling[name] = Scaling(name, pList=pList)
	if not exists:
		chimera.triggers.activateTrigger(Trigger, name)

def findScaling(name):
	try:
		return userScaling[name]
	except KeyError:
		try:
			return systemScaling[name]
		except KeyError:
			return None

def removeScaling(name):
	del prefScaling[name]
	del userScaling[name]
	chimera.triggers.activateTrigger(Trigger, name)

def listScalings(all=False):
	if all:
		return systemScaling.keys() + userScaling.keys()
	else:
		return userScaling.keys()

# Following methods are used for saving and restoring session

def sessionSaveUsed():
	values = []
	for n, v in prefScaling.iteritems():
		values.append((n, v))
	seen = {}
	for sc, (n, pList) in scalingName.items():
		if n == SystemDefault or n in userScaling or n in seen:
			continue
		values.append((n, pList))
		seen[n] = True
	return values

def sessionSaveResidue(r):
	name = getScalingName(r)
	if name != "none":
		return name
	else:
		style = r.ribbonStyle
		return (style.__class__.__name__, style.size)

def sessionRestoreUsed(used):
	unnamed = {}
	for n, v in used:
		if n.startswith(scalingUnnamed):
			sc = Scaling(n, pList=convertSaved(v))
			unnamed[n] = sc
			for type in SaveOrder:
				scalingName[sc.getScale(type)] = (n, v)
		else:
			addScaling(n, convertSaved(v))
	return unnamed

def sessionRestoreResidue(r, n, d):
	if isinstance(n, tuple):
		# A tuple, so must be (class_name, size)
		className, size = n
		try:
			klass = getattr(chimera, className)
		except AttributeError:
			pass
		else:
			r.ribbonStyle = klass(size)
		return
	try:
		sc = d[n]
	except KeyError:
		# If name is "Chimera default", just leave
		# the ribbonStyle value alone since it should
		# already be the default value
		try:
			sc = userScaling[n]
		except KeyError:
			return
	sc.setResidue(r)

def tostr(f):
	return "%.4g" % f
