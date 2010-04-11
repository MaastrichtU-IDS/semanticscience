import sys
import Tkinter
import Pmw
import os
import os.path
import string
import re
import math

import chimera
from chimera import replyobj
from chimera import resCode
from chimera.baseDialog import ModelessDialog
from OpenSave import OpenModeless
import MSF
import ActivePlot

opener = None
ColorRange = [ "black", "green", "blue", "red", "yellow" ]
DSRange = [ ActivePlot.DataSet, ActivePlot.BarDataSet, ActivePlot.DataSet ]

def run(extensionName):
	"Invocation function called by Chimera extension manager object"
	global opener
	if opener is None:
		filterName = "Minrms Info"
		opener = OpenDialog(extensionName,
					filters=[(filterName, "*.info")],
					defaultFilter=filterName, addAll=0)
	opener.enter()


class OpenDialog(OpenModeless):
	"Dialog for opening a Minrms information file."

	def __init__(self, extensionName, *args, **kw):
		self.extensionName = extensionName
		OpenModeless.__init__(self, *args, **kw)

	def Apply(self):
		paths = self.getPaths()
		if not paths:
			return
		try:
			MinrmsPlot(self.extensionName, paths[0])
		except IOError, s:
			replyobj.error(str(s))


class MinrmsPlot(ModelessDialog):
	"Display the results from a Minrms structure alignment run."

	buttons = ( "Close", "Hide" )
	help = "ContributedSoftware/minrmsplot/minrmsplot.html";

	def __init__(self, extensionName, filename):
		#import time
		#baseTime = time.time()
		#print "__init__", baseTime
		self.sharedState = chimera.SharedState(self)
		self.sharedState.extensionName = extensionName
		self.setup(filename)
		self.mav = None
						
		#print "shared state done", time.time() - baseTime
		self.molHandlerId = chimera.triggers.addHandler(
						"Molecule",
						self._molHandler, None)
		self.pbgHandlerId = chimera.triggers.addHandler(
						"PseudoBondGroup",
						self._pbgHandler, None)
		#print "triggers registered", time.time() - baseTime
		chimera.extension.manager.registerInstance(self)
		#print "extension instance registered", time.time() - baseTime
		ModelessDialog.__init__(self)
		#print "dialog initialized", time.time() - baseTime

	def Hide(self):
		ModelessDialog.Close(self)

	def Close(self):
		chimera.extension.manager.deregisterInstance(self)
		chimera.triggers.deleteHandler("PseudoBondGroup",
						self.pbgHandlerId)
		chimera.triggers.deleteHandler("Molecule", self.molHandlerId)
		ModelessDialog.destroy(self)
		if self.mav:
			self.mav.destroy()
			self.mav = None

	def setup(self, filename):
		"Open file and follow filename references to all Minrms data."
		from OpenSave import osOpen
		try:
			f = osOpen(filename)
		except IOError, s:
			raise IOError, "%s: cannot open: %s" % (filename, s)
		state = self.sharedState
		state.infoDir = os.path.dirname(filename)
		state.infoFile = filename
		state.pdbFixed = None
		state.pdbMovable = None
		state.rmsdFile = None
		state.msfBase = None
		try:
			state.atomNames = []
			while 1:
				line = f.readline()
				if not line:
					break
				fields = map(lambda s: s.strip(),
						line.split(':'))
				if fields[0] == "fixed pdb":
					state.pdbFixed = fields[1]
				elif fields[0] == "moveable pdb":
					state.pdbMovable = fields[1]
				elif fields[0] == "rmsd":
					state.rmsdFile = fields[1]
				elif fields[0] == "base":
					state.msfBase = fields[1]
				elif fields[0] == "number of atoms used":
					n = int(fields[1])
					for i in range(n):
						line = f.readline()
						name = line.rstrip()
						state.atomNames.append(name)
			if state.pdbFixed is None \
			or state.pdbMovable is None \
			or state.rmsdFile is None \
			or state.msfBase is None:
				raise IOError, \
					"%s: incomplete info file" % filename
		finally:
			f.close()
		import sys
		state.molFixed = self.openPDB(state.pdbFixed)
		state.molMovable = self.openPDB(state.pdbMovable)
		self.readRMSD()
		self.readAlignments()

		name = "MinrmsPlot %s %s" % (state.molFixed.name,
						state.molMovable.name)
		self.title = name
		state.pbg = chimera.misc.getPseudoBondGroup(self.title,
				associateWith=[state.molFixed.molecule,
						state.molMovable.molecule])
		state.pbg.color = chimera.colorTable.getColorByName("green")

	def _pbgHandler(self, trigger, closure, changes):
		"Trigger callback for pseudo-bond group state changes."
		state = self.sharedState
		for pbg in changes.deleted:
			if pbg is state.pbg:
				state.pbg = None

	def openPDB(self, pdbFile):
		"Open a PDB file as a Chimera model."
		return MinrmsMolecule(self.sharedState.infoDir, pdbFile)

	def readRMSD(self):
		"Read the Minrms costs file and save data columns as lists."
		path = os.path.join(self.sharedState.infoDir,
					self.sharedState.rmsdFile)
		try:
			f = open(path)
		except IOError, s:
			raise IOError, "%s: cannot open: %s" % (path, s)
		vList = []
		try:
			line = f.readline()
			if not line:
				raise IOError, "%s: file is empty" % path
			if line[0] != '#':
				raise IOError, "%s: not an RMSD file" % path
			self.sharedState.rmsdColumns = map(lambda s: s.strip(),
						line[1:].strip().split(','))
			numColumns = len(self.sharedState.rmsdColumns)
			while 1:
				line = f.readline()
				if not line:
					break
				fields = line.split()
				if len(fields) != numColumns:
					raise IOError, \
						"%s: wrong number of columns" \
						% path
				values = (int(fields[0]),) + \
						tuple(map(float, fields[1:]))
				vList.append(values)
		finally:
			f.close()
		data = []
		for i in range(len(self.sharedState.rmsdColumns)):
			data.append(map(lambda t, n=i: t[n], vList))
		self.sharedState.rmsdData = data

		
	def readAlignments(self):
		"Read all MSF alignments referenced by costs data."
		files = os.listdir(self.sharedState.infoDir)
		msfBase = self.sharedState.msfBase
		msfData = []
		for i in self.sharedState.rmsdData[0]:
			file = "%s%d.msf" % (msfBase, i)
			path = os.path.join(self.sharedState.infoDir, file)
			try:
				f = open(path)
			except IOError, s:
				raise IOError, "%s: cannot open: %s" % (path, s)
			try:
				try:
					msf = self._readOneAlignment(f)
				except IOError, s:
					raise IOError, "%s: %s" % (path, str(s))
			finally:
				f.close()
			msfData.append((path, msf))
		self.sharedState.msfData = msfData

	def _readOneAlignment(self, f):
		"Read a single MSF alignment."
		return MinrmsAlignment(f, self.sharedState.molFixed,
					self.sharedState.molMovable,
					self.sharedState.atomNames)

	def fillInUI(self, parent):
		"Create the extension user interface."
		self.notebook = Pmw.NoteBook(parent, hull_width=500,
						hull_height=400)
		self.notebook.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)

		# Create the RMSD plot tab
		tab = self.notebook.add("RMSD vs. N")
		bgColor = tab["background"]
		labelFrame = Tkinter.Frame(tab)
		labelFrame.pack(side=Tkinter.TOP)
		row = 0
		self.sharedState.rmsdDisplayed = {}
		self.labels = []
		for i in range(len(self.sharedState.rmsdColumns)):
			label = self.sharedState.rmsdColumns[i]
			try:
				color = ColorRange[i]
			except IndexError:
				color = ColorRange[0]
			if i != 0:
				v = Tkinter.IntVar(tab)
				v.set(1)
				cb = Tkinter.Checkbutton(labelFrame, text=label,
							variable=v,
							foreground=color)
				cb.select()
				cb.config(command=lambda s=self, col=i, v=v:
						s._rmsdShowColumn(col, v))
			else:
				v = None
				cb = Tkinter.Label(labelFrame, text=label,
							foreground=color)
			cb.grid(column=0, row=row, sticky="e")
			l = Tkinter.Label(labelFrame, text=" ",
						width=20,
						relief=Tkinter.RIDGE)
			l.grid(column=1, row=row, sticky="ew")
			row += 1
			self.sharedState.rmsdDisplayed[i] = 1
			self.labels.append((v, cb, l))
		self.rmsdPlot = ActivePlot.ActivePlot(master=tab,
					track=Tkinter.FALSE,
					zoom=Tkinter.TRUE,
					xFormat="%4.0f",
					yFormat="%5.2f",
					xPrecision=0,
					yPrecision=0.1,
					labelCnf={ "relief":Tkinter.FLAT,
						"highlightthickness":0,
						"disabledbackground":bgColor,
						"disabledforeground":"black",
						"bg":bgColor },
					controlCnf={ "bd":2,
						"relief":Tkinter.SUNKEN,
						"bg":bgColor },
					canvasCnf={ "bd":2,
						"relief":Tkinter.RIDGE,
						"bg":bgColor })
		self.rmsdPlot.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)
		self.rmsdPlot.canvas.bind("<ButtonPress-1>", self._rmsdDown)
		self.rmsdPlot.canvas.bind("<ButtonRelease-1>", self._rmsdUp)
		self.rmsdPlot.canvas.bind("<B1-Motion>", self._rmsdDrag)

		# Add a "Display Alignment' check button on right
		# of control bar
		self.showAlignVar = Tkinter.IntVar(0)
		self.showAlign = Tkinter.Checkbutton(self.rmsdPlot.control,
					text="Show Alignment",
					variable=self.showAlignVar,
					command=self._showAlignCB)
		self.showAlign.pack(side=Tkinter.RIGHT)

		# Add data to RMSD plot
		self.dataset = {}
		x = self.sharedState.rmsdData[0]
		for i in range(1, len(self.sharedState.rmsdColumns)):
			y = self.sharedState.rmsdData[i]
			try:
				color = ColorRange[i]
			except IndexError:
				color = ColorRange[0]
			try:
				dsClass = DSRange[i]
			except IndexError:
				dsClass = DSRange[0]
			ds = dsClass(x, y=y, baseColor=color)
			self.rmsdPlot.addDataSet(ds)
			self.dataset[i] = ds

	def _rmsdShowColumn(self, col, v):
		"Show or hide a data column in the RMSD plot."
		if v.get():
			self.rmsdPlot.addDataSet(self.dataset[col])
		else:
			self.rmsdPlot.deleteDataSet(self.dataset[col])

	def _rmsdDown(self, event):
		"Button-down callback for RMSD plot."
		self._rmsdHighlight(event)

	def _rmsdUp(self, event):
		"Button-up callback for RMSD plot."
		self._rmsdHighlight(event)

	def _rmsdDrag(self, event):
		"Button-drag callback for RMSD plot."
		self._rmsdHighlight(event)

	def _rmsdHighlight(self, event):
		"Highlight selected alignment in RMSD plot."
		x, y = self.rmsdPlot.unscale(event.x, event.y)
		x = int(round(x))
		values = self.sharedState.rmsdData[0]
		for i in range(len(values)):
			if x == values[i]:
				index = i
				break
		else:
			index = -1
		self.setCurrentAlignment(index)

	def _showAlignCB(self):
		if self.showAlignVar.get():
			state = self.sharedState
			try:
				hasAlignment = state.currentAlignment >= 0
			except AttributeError:
				hasAlignment = False
			if not self.mav and hasAlignment:
				self._startMAV()
		else:
			if self.mav:
				self.mav.destroy()
			self.mav = None

	def _startMAV(self):
		from MultAlignViewer.MAViewer import MAViewer
		state = self.sharedState
		self.mav = MAViewer(self._msfFilename(), quitCB=self._mavQuit,
					autoAssociate=0)
		self.mav.associate([ state.molFixed.molecule,
					state.molMovable.molecule ])

	def _mavQuit(self, mav):
		self.showAlignVar.set(0)
		self.mav = None

	def _msfFilename(self):
		state = self.sharedState
		msfBase = state.msfBase
		return state.msfData[state.currentAlignment][0]

	def setCurrentAlignment(self, n):
		"Set the current alignment in RMSD plot to alignment 'n'."
		state = self.sharedState
		state.currentAlignment = n
		self.showCurrentAlignment(n)
		if state.pbg is not None:
			state.pbg.deleteAll()
		if n < 0 or state.molFixed is None or state.molMovable is None:
			return
		if self.showAlignVar.get():
			if self.mav is None:
				self._startMAV()
			else:
				self.mav.realign(self._msfFilename())
		msf = state.msfData[n][1]
		xf = state.molFixed.molecule.openState.xform
		xf.multiply(chimera.Xform.xform(*msf.matrix))
		state.molMovable.molecule.openState.xform = xf
		if state.pbg is None:
			return
		for pairList in msf.atomPairs:
			for a0, a1 in pairList:
				pb = state.pbg.newPseudoBond(a0, a1)
				c0 = a0.xformCoord()
				c1 = a1.xformCoord()
				if c0.sqdistance(c1) > 0.25:
					pb.drawMode = chimera.Bond.Wire
				else:
					pb.drawMode = chimera.Bond.Stick
					pb.order = 2.0

	def showCurrentAlignment(self, n):
		"Update just the MinrmsPlot user interface"
		for ds in self.dataset.values():
			ds.highlight(n)
		if n < 0:
			for t in self.labels:
				l = t[2]
				l.config(text=" ")
		else:
			state = self.sharedState
			for i in range(len(self.labels)):
				l = self.labels[i][2]
				l.config(text=str(state.rmsdData[i][n]))

	def emName(self):
		return self.title
	def emRaise(self):
		self.enter()
	def emHide(self):
		self.Hide()
	def emQuit(self):
		self.Close()
		
	def _molHandler(self, trigger, closure, changes):
		"Trigger callback for molecule state changes."
		state = self.sharedState
		for m in changes.deleted:
			if state.molFixed is not None and m is state.molFixed.molecule:
				state.molFixed.destroy()
				state.molFixed = None
			elif state.molMovable is not None and m is state.molMovable.molecule:
				state.molMovable.destroy()
				state.molMovable = None

class MinrmsMolecule:
	"""Read in a PDB file, open it in Chimera, and construct
	an ordered list of alignable amino acids and their 
	corresponding Chimera residues"""

	def __init__(self, dirName, fileName):
		self.name = fileName
		path = os.path.join(dirName, fileName)
		mList = chimera.openModels.open(path, type="PDB")
		self.molecule = mList[0]
		self.residues = []
		for r in self.molecule.residues:
			try:
				code = resCode.protein3to1[r.type]
			except KeyError:
				pass
			else:
				self.residues.append((code, r))

	def destroy(self):
		self.molecule = None
		self.residues = []

class MinrmsAlignment:
	"""Read in an MSF file and find the matching pairs of
	Chimera atoms."""

	def __init__(self, f, m0, m1, atomNames):
		s0 = None
		s1 = None
		msf = MSF.MSF(f)
		atomNames = map(lambda s: s.strip(), atomNames)
		self._findPairs(msf, m0, m1, atomNames)
		self._findTransform(msf)

	def _findPairs(self, msf, m0, m1, atomNames):
		for name, seq in msf.sequenceDict.items():
			if self._match(name, m0.name):
				s0 = seq
			elif self._match(name, m1.name):
				s1 = seq
		if s0 is None or s1 is None:
			raise IOError, "cannot find aligned structures"
		seq0 = s0.sequence()
		seq1 = s1.sequence()
		if len(seq0) != len(seq1):
			raise IOError, "unequal alignment sequence lengths"
		rList0 = m0.residues
		rList1 = m1.residues
		rIndex0 = 0
		rIndex1 = 0
		self.atomPairs = []
		self.residuePairs = []
		for i in range(len(seq0)):
			code0 = seq0[i]
			if code0 not in string.uppercase:
				r0 = None
			else:
				while 1:
					try:
						code, r0 = rList0[rIndex0]
					except IndexError:
						r0 = None
						break
					rIndex0 += 1
					if code == code0:
						break
					replyobj.warning("sequence mismatch "
							"for residue %s\n"
							% r0.oslIdent())
					r0 = None
			code1 = seq1[i]
			if code1 not in string.uppercase:
				r1 = None
			else:
				while 1:
					try:
						code, r1 = rList1[rIndex1]
					except IndexError:
						r1 = None
						break
					rIndex1 += 1
					if code == code1:
						break
					replyobj.warning("sequence mismatch "
							"for residue %s\n"
							% r1.oslIdent())
					r1 = None
			if r0 is not None and r1 is not None:
				self._addPair(r0, r1, atomNames)

	def _addPair(self, r0, r1, atomNames):
		pairs = []
		for name in atomNames:
			a0 = r0.findAtom(name)
			a1 = r1.findAtom(name)
			pairs.append((a0, a1))
		self.atomPairs.append(pairs)
		self.residuePairs.append((r0, r1))

	def _match(self, name, otherName):
		if name == otherName:
			return 1
		name = os.path.basename(name)
		otherName = os.path.basename(otherName)
		return name == otherName

	def _findTransform(self, msf):
		sig = "Transform Matrix to apply to structure:"
		sigLen = len(sig)
		lines = msf.header.split('\n')
		base = -1
		for i in range(len(lines)):
			line = lines[i]
			if line[:sigLen] == sig:
				base = i
				break
		if base < 0:
			raise IOError, "no transformation matrix found"
		if base + 3 >= len(lines):
			raise IOError, "transformation matrix too short"
		m0 = map(float, lines[base + 1].split())
		m1 = map(float, lines[base + 2].split())
		m2 = map(float, lines[base + 3].split())
		det = m0[0] * (m1[1] * m2[2] - m1[2] * m2[1]) - \
			m0[1] * (m1[0] * m2[2] - m1[2] * m2[0]) + \
			m0[2] * (m1[0] * m2[1] - m1[1] * m2[0])
		if det != 1.0:
			detscale = math.pow(det, 1.0 / 3.0)
			for i in range(3):
				m0[i] /= detscale
				m1[i] /= detscale
				m2[i] /= detscale
		self.matrix = [ m0[0], m0[1], m0[2], m0[3],
				m1[0], m1[1], m1[2], m1[3],
				m2[0], m2[1], m2[2], m2[3] ]
		#self.matrix = chimera.Xform.xform(
		#			m0[0], m0[1], m0[2], m0[3],
		#			m1[0], m1[1], m1[2], m1[3],
		#			m2[0], m2[1], m2[2], m2[3])
