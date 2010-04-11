import weakref
import chimera
from chimera import Residue

# prefRRC should be set to a dictionary in a HiddenCategory
# created in base.py.  Whenever we change things in userRRC, we
# also change the corresponding item in prefRRC so that
# preferences.save() will always get the right values.

# RRC = RibbonResidueClass (from C++ layer)
prefRRC = None
systemRRC = {}
userRRC = {}
rrcName = weakref.WeakKeyDictionary()
Trigger = "RibbonResidueClassListChanged"
rrcUnnamed = "unnamed"
rrcId = 1

def initialize(p):
	# create system residue classes
	d = chimera.RibbonResidueClass.classes()
	for name, crrc in d.iteritems():
		rrc = RRC(name)
		rrc.setRRC(crrc)
		systemRRC[name] = rrc

	# create user residue classes
	global prefRRC
	prefRRC = p
	for name, values in p.items():
		userRRC[name] = RRC(name, *values)

	# Add trigger for residue class updates
	chimera.triggers.addTrigger(Trigger)

class AtomsEditor:

	def __init__(self, parent, dialog):

		self.guide = None
		self.plane = None
		self.isNucleic = False
		self.planeNormal = False
		self.mainchain = {}
		self.mapped = 0
		self.dialog = dialog
		self.currentRRC = None

		from chimera.preferences import saveui
		self.saveui = saveui.SaveUI(parent, self)

		import Tkinter, Pmw
		f = Tkinter.Frame(parent)
		f.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)
		self.guideEntry = Pmw.EntryField(f,
					labelpos="w",
					label_text="Guide atom:",
					modifiedcommand=self._guideAtomChange)
		self.guideEntry.pack(fill=Tkinter.X)
		self.planeEntry = Pmw.EntryField(f,
					labelpos="w",
					label_text="Orientation atom:",
					modifiedcommand=self._planeAtomChange)
		self.planeEntry.pack(fill=Tkinter.X)
		Pmw.alignlabels([self.guideEntry, self.planeEntry])

		g = Pmw.Group(f, tag_text="Mainchain Atoms")
		g.pack(fill=Tkinter.BOTH, expand=True)
		gf = g.interior()
		subf = Tkinter.Frame(gf)
		subf.pack(side=Tkinter.TOP, fill=Tkinter.X)
		self.newPosition = Pmw.Counter(subf,
					labelpos="w",
					label_text="Position:",
					entry_width=4,
					entryfield_value="0.50",
					datatype = {
						'counter': 'real',
					},
					entryfield_validate= {
						"validator":"real",
						"min":0.0,
						"max":1.0
					},
					increment=0.05,
					)
		self.newPosition.pack(side=Tkinter.LEFT, fill=Tkinter.X,
					expand=True)
		self.newName = Pmw.EntryField(subf,
					labelpos="w",
					label_text="Name:",
					entry_width=6,
					modifiedcommand=self._mainchainChange,
					command=self._newMainchain)
		self.newName.pack(side=Tkinter.LEFT, fill=Tkinter.X,
					expand=True)
		self.newButton = Tkinter.Button(subf,
					text="Set",
					command=self._newMainchain)
		self.newButton.pack(side=Tkinter.LEFT, fill=Tkinter.X)
		self.mainchainListbox = Pmw.ScrolledListBox(gf,
					selectioncommand=self._selMainchain)
		self.mainchainListbox.pack(fill=Tkinter.BOTH, expand=True)
		self.removeButton = Tkinter.Button(gf, text="Remove",
					command=self._removeMainchain)
		self.removeButton.pack(side=Tkinter.TOP, fill=Tkinter.X)

		self.opt = Pmw.RadioSelect(f,
				buttontype="checkbutton",
				command=self._optChange,
				orient="vertical",
				labelpos="n",
				label_text="Options",
				pady=0,
				hull_borderwidth=2,
				hull_relief=Tkinter.RIDGE)
		self.opt.pack(side=Tkinter.TOP, fill=Tkinter.X)
		self.opt.add("isNucleic",
				text="Non-helix/sheet uses \"Nucleic\" scaling")
		self.opt.add("planeNormal",
				text="Rotate orientation 90 degrees")
		item = self.saveui_defaultItem()
		if item:
			self.saveui_select(item)

	def _guideAtomChange(self):
		self.guide = self.guideEntry.getvalue().upper()
		self.guideEntry.setvalue(self.guide)
		self.currentRRC = None

	def _planeAtomChange(self):
		self.plane = self.planeEntry.getvalue().upper()
		self.planeEntry.setvalue(self.plane)
		self.currentRRC = None

	def _optChange(self, option, onoff):
		self.currentRRC = None
		setattr(self, option, onoff)

	def _mainchainChange(self):
		name = self.newName.getvalue().upper()
		self.newName.setvalue(name)

	def _newMainchain(self):
		name = self.newName.getvalue().strip()
		if not name:
			from chimera import replyobj
			replyobj.error("No atom name specified")
			return
		ef = self.newPosition.component("entryfield")
		if not ef.valid():
			from chimera import replyobj
			replyobj.error("Invalid position specified")
			return
		pos = float(ef.getvalue())
		self.mainchain[name] = pos
		self.redisplayMainchain()
		self.currentRRC = None

	def _selMainchain(self):
		items = self.mainchainListbox.getvalue()
		if len(items) != 1:
			return
		pos, name = items[0].split()
		self.newName.setvalue(name)
		self.newPosition.setvalue(pos)

	def _removeMainchain(self):
		for item in self.mainchainListbox.getvalue():
			pos, name = item.split()
			del self.mainchain[name]
		self.redisplayMainchain()
		self.currentRRC = None

	def redisplayMainchain(self):
		vList = [ (pos, name)
				for name, pos in self.mainchain.iteritems() ]
		vList.sort()
		self.mainchainListbox.setlist([ "%.3f  %s" % v for v in vList ])

	def _showRRC(self, name):
		rrc = findRRC(name)
		values = []
		self.guide = rrc.guide
		self.guideEntry.setvalue(rrc.guide)
		self.plane = rrc.plane
		self.planeEntry.setvalue(rrc.plane)
		self.isNucleic = rrc.isNucleic
		if rrc.isNucleic:
			values.append("isNucleic")
		self.planeNormal = rrc.planeNormal
		if rrc.planeNormal:
			values.append("planeNormal")
		self.opt.setvalue(values)
		self.mainchain = rrc.mainchain.copy()
		self.redisplayMainchain()
		self.currentRRC = rrc

	def Apply(self, restrict):
		if self.currentRRC:
			rrc = self.currentRRC
		else:
			rrc = RRC(None, self.guide, self.plane,
					self.planeNormal, self.isNucleic,
					self.mainchain)
		if restrict:
			from chimera import selection
			rList = selection.currentResidues()
		else:
			rList = []
		if rList:
			for r in rList:
				rrc.setResidue(r)
		else:
			for m in chimera.openModels.list(
					modelTypes=[chimera.Molecule]):
				for r in m.residues:
					rrc.setResidue(r)

	# SaveUI callback functions
	def saveui_label(self):
		return "Ribbon Residue Class"

	def saveui_presetItems(self):
		return systemRRC.keys()

	def saveui_userItems(self):
		return userRRC.keys()

	def saveui_defaultItem(self):
		try:
			return userRRC.keys()[0]
		except IndexError:
			return systemRRC.keys()[0]

	def saveui_select(self, name):
		self._showRRC(name)

	def saveui_save(self, name):
		from chimera import preferences
		addRRC(name, self.guide, self.plane, self.planeNormal,
			self.isNucleic, self.mainchain)
		preferences.save()
		self.dialog.status("Setting \"%s\" saved" % name)
		return True

	def saveui_delete(self, name):
		from chimera import preferences
		removeRRC(name)
		preferences.save()
		self.dialog.status("Setting \"%s\" deleted" % name)
		return True

class RRC:
	def __init__(self, name, guide=None, plane=None,
			planeNormal=None, isNucleic=None, mainchain=None):
		if name is None:
			global rrcId
			name = "%s%d" % (rrcUnnamed, rrcId)
			rrcId += 1
		self.name = name
		self.guide = guide
		self.plane = plane
		self.planeNormal = planeNormal
		self.isNucleic = isNucleic
		if mainchain is None:
			self.mainchain = {}
		else:
			self.mainchain = mainchain
		self.rrc = None

	def setRRC(self, crrc):
		self.rrc = crrc
		self.guide = crrc.guide()
		self.plane = crrc.plane()
		self.planeNormal = crrc.planeNormal()
		self.isNucleic = crrc.isNucleic()
		self.mainchain = crrc.positions()
		rrcName[crrc] = self.name

	def setResidue(self, r):
		r.ribbonResidueClass = self.getRRC()

	def getRRC(self):
		if self.rrc is None:
			self._makeRRC()
		return self.rrc

	def _makeRRC(self):
		crrc = chimera.RibbonResidueClass(self.guide, self.plane,
							self.planeNormal,
							self.isNucleic)
		for name, pos in self.mainchain.iteritems():
			crrc.addPosition(name, pos)
		self.rrc = crrc
		rrcName[crrc] = self.name

def findRRC(name):
	try:
		return userRRC[name]
	except KeyError:
		return systemRRC.get(name, None)

def addRRC(name, *args):
	exists = prefRRC.has_key(name)
	prefRRC[name] = args
	rrc = RRC(name, *args)
	userRRC[name] = rrc
	if not exists:
		chimera.triggers.activateTrigger(Trigger, name)

def removeRRC(name):
	del prefRRC[name]
	del userRRC[name]
	chimera.triggers.activateTrigger(Trigger, name)

def getRRCName(r):
	try:
		return rrcName[r.ribbonResidueClass]
	except KeyError:
		return "none"

def setRRCByName(r, name):
	rrc = findRRC(name)
	if rrc:
		rrc.setResidue(r)
	else:
		from chimera import replyobj
		replyobj.error("cannot find ribbon residue class named %s"
				% name)

def listRRC(all=False):
	if all:
		return systemRRC.keys() + userRRC.keys()
	else:
		return userRRC.keys()

# Following methods are used for saving and restoring session

def sessionSaveUsed():
	values = []
	for n, v in prefRRC.iteritems():
		values.append((n, v))
	for crrc, n in rrcName.items():
		if n in systemRRC or n in userRRC:
			continue
		v = (crrc.guide(), crrc.plane(), crrc.planeNormal(),
			crrc.isNucleic(), crrc.positions())
		values.append((n, v))
	return values

def sessionSaveResidue(r):
	return getRRCName(r)

def sessionRestoreUsed(used):
	unnamed = {}
	for n, v in used:
		if n.startswith(rrcUnnamed):
			rrc = RRC(n, *v)
			unnamed[n] = rrc
			rrcName[rrc.getRRC()] = n
		else:
			addRRC(n, *v)
	return unnamed

def sessionRestoreResidue(r, n, d, flags):
	try:
		if flags == 0:
			# defaults have switched for nucleic acids
			if n == 'nucleic acid':
				n = 'nucleic acid rotated'
			elif n == 'nucleic acid rotated':
				n = 'nucleic acid'
		rrc = d[n]
	except KeyError:
		try:
			rrc = userRRC[n]
		except KeyError:
			try:
				rrc = systemRRC[n]
			except KeyError:
				return
	rrc.setResidue(r)
