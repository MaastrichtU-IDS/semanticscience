# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import os
import math
import Tkinter

import chimera
from chimera import selection
from chimera import chimage
from chimera import tkgui
from chimera import match
from chimera import preferences
from chimera.baseDialog import ModelessDialog
import Midas

prefs = preferences.addCategory("EnsembleCluster", preferences.HiddenCategory)

class EnsembleMatch(ModelessDialog):
	"""Display a table for manipulating one ensemble relative to another.

	The two ensembles should consist of conformers of the same model.
	Table rows correspond to conformers in the reference ensemble.
	Table columns correspond to conformers in the alternative ensemble.
	A conformer in the alternative ensemble will be matched onto
	a conformer in the reference ensemble when a table entry is
	clicked.  The table entry label is the RMSD between the two
	conformers."""

	title = "Ensemble Match"
	help = "ContributedSoftware/ensemblematch/ensemblematch.html"
	buttons = ("Hide", "Quit")

	def __init__(self, refModels, altModels, subSelection, *args, **kw):
		#
		# Save the subselection (part of model to match)
		# as well as the model lists (ordered by subid)
		#
		self.subSelection = subSelection
		l = [ (m.subid, m) for m in refModels ]
		l.sort()
		self.refModels = [ t[1] for t in l ]
		l = [ (m.subid, m) for m in  altModels ]
		l.sort()
		self.altModels = [ t[1] for t in l ]

		#
		# Grab the atomic coordinates that will be used
		# to compute RMSDs and check for errors
		#
		self.atomDict = {}
		counts = []
		for ml in self.refModels, self.altModels:
			for m in ml:
				osl = '%s%s' % (m.oslIdent(), self.subSelection)
				s = selection.OSLSelection(osl)
				atoms = s.atoms()
				self.atomDict[m] = match._coordArray(atoms)
				counts.append(len(atoms))
		if min(counts) != max(counts):
			raise chimera.UserError("Unequal number of atoms "
						"found in models")
		if counts[0] == 0:
			raise chimera.UserError("No atoms match atom specifier")

		#
		# Add handler to monitor change in display or active
		# status changes
		#
		self.trigger = chimera.triggers.addHandler('check for changes',
							self._statusCheck, None)

		#
		# Initialize dialog
		#
		ModelessDialog.__init__(self, *args, **kw)

		# 
		# Register with extension manager
		#
		chimera.extension.manager.registerInstance(self)

	def fillInUI(self, parent):
		#
		# Construct user interface
		#
		self.modelVars = {}

		# Find images
		top = parent.winfo_toplevel()
		dir = os.path.dirname(__file__)
		icon = os.path.join(dir, 'move.tiff')
		self.moveIcon = chimage.get(icon, top)
		icon = os.path.join(dir, 'zoom.tiff')
		self.zoomIcon = chimage.get(icon, top)
		icon = os.path.join(dir, 'reset.tiff')
		self.resetIcon = chimage.get(icon, top)

		# Label rows
		for n in range(len(self.refModels)):
			parent.rowconfigure(n + 1, weight=1)
			m = self.refModels[n]
			lf = Tkinter.Frame(parent, relief=Tkinter.GROOVE, bd=2)
			lf.grid(row=n + 1, column=0, sticky='nsew')
			self._addRefConformer(lf, m)

		# Label columns
		for n in range(len(self.altModels)):
			parent.columnconfigure(n + 1, weight=1)
			m = self.altModels[n]
			lf = Tkinter.Frame(parent, relief=Tkinter.GROOVE, bd=2)
			lf.grid(row=0, column=n + 1, sticky='nsew')
			self._addAltConformer(lf, m)

		# Add table entries
		# Each column comprises a set of radio buttons.
		# This design is selected because each conformer
		# in the alternative ensemble can only be matched
		# to a single conformer in the reference ensemble.
		self.matchVars = {}
		for a in range(len(self.altModels)):
			alt = self.altModels[a]
			var = Tkinter.IntVar(parent)
			var.set(-1)
			self.matchVars[alt] = var
			for r in range(len(self.refModels)):
				ref = self.refModels[r]
				m = chimera.match.Match(self.atomDict[ref],
							self.atomDict[alt])
				b = Tkinter.Radiobutton(parent,
						relief=Tkinter.SUNKEN,
						text='%.3f' % m.rms,
						value=r,
						variable=var,
						command=lambda s=self, m=alt:
							s.matchModel(m))
				b.grid(column=a + 1, row=r + 1, sticky='nsew')

	def _addRefConformer(self, frame, model):
		#
		# Add reference conformer label and buttons
		# A is for active
		# D is for display
		# 
		frame.columnconfigure(0, weight=1)
		frame.columnconfigure(1, weight=1)
		frame.columnconfigure(2, weight=1)
		l = Tkinter.Label(frame, text=model.oslIdent())
		l.grid(row=0, column=0, sticky='nsew')
		va = Tkinter.IntVar(frame)
		va.set(model.openState.active and 1 or 0)
		ba = Tkinter.Checkbutton(frame,
					text='A',
					indicatoron=Tkinter.FALSE,
					variable=va,
					command=lambda v=va, s=self, m=model:
						s.activateModel(m, v.get()))
		ba.grid(row=0, column=1, sticky='nsew')
		vd = Tkinter.IntVar(frame)
		vd.set(model.display and 1 or 0)
		bd = Tkinter.Checkbutton(frame,
					text='D',
					indicatoron=Tkinter.FALSE,
					variable=vd,
					command=lambda v=vd, s=self, m=model:
						s.displayModel(m, v.get()))
		bd.grid(row=0, column=2, sticky='nsew')
		self.modelVars[model] = (va, vd)
		br = Tkinter.Button(frame,
					image=self.moveIcon,
					command=lambda s=self, m=model:
						s.manipulateModel(m))
		br.grid(row=0, column=3, sticky='nsew')
		br = Tkinter.Button(frame,
					image=self.zoomIcon,
					command=lambda s=self, m=model:
						s.zoomModel(m))
		br.grid(row=0, column=4, sticky='nsew')

	def _addAltConformer(self, frame, model):
		#
		# Add alternative conformer label and buttons
		# A is for active
		# D is for display
		# R is for reset
		#
		frame.columnconfigure(0, weight=1)
		frame.columnconfigure(1, weight=1)
		frame.columnconfigure(2, weight=1)
		l = Tkinter.Label(frame, text=model.oslIdent())
		l.grid(row=0, column=0, columnspan=3, sticky='nsew')
		va = Tkinter.IntVar(frame)
		va.set(model.openState.active and 1 or 0)
		ba = Tkinter.Checkbutton(frame,
					text='A',
					indicatoron=Tkinter.FALSE,
					variable=va,
					command=lambda v=va, s=self, m=model:
						s.activateModel(m, v.get()))
		ba.grid(row=1, column=0, sticky='nsew')
		vd = Tkinter.IntVar(frame)
		vd.set(model.display and 1 or 0)
		bd = Tkinter.Checkbutton(frame,
					text='D',
					indicatoron=Tkinter.FALSE,
					variable=vd,
					command=lambda v=vd, s=self, m=model:
						s.displayModel(m, v.get()))
		bd.grid(row=1, column=1, sticky='nsew')
		self.modelVars[model] = (va, vd)
		br = Tkinter.Button(frame,
					relief=Tkinter.FLAT,
					image=self.resetIcon,
					command=lambda s=self, m=model:
						s.resetModel(m))
		br.grid(row=1, column=2, sticky='nsew')

	def activateModel(self, model, on):
		model.openState.active = on

	def displayModel(self, model, on):
		model.display = on

	def resetModel(self, model):
		self.matchVars[model].set(-1)
		va, vd = self.modelVars[model]
		va.set(0)
		vd.set(0)
		self.activateModel(model, 0)
		self.displayModel(model, 0)

	def matchModel(self, model):
		n = self.matchVars[model].get()
		va, vd = self.modelVars[model]
		if n < 0:
			va.set(0)
			vd.set(0)
			self.activateModel(model, 0)
			self.displayModel(model, 0)
			return
		altOSL = '%s%s' % (model.oslIdent(), self.subSelection)
		ref = self.refModels[n]
		refOSL = '%s%s' % (ref.oslIdent(), self.subSelection)
		try:
			Midas.match(altOSL, refOSL)
		except Midas.MidasError, e:
			raise chimera.UserError(str(e))
		va.set(1)
		vd.set(1)
		self.activateModel(model, 1)
		self.displayModel(model, 1)
		va, vd = self.modelVars[ref]
		va.set(1)
		vd.set(1)
		self.activateModel(ref, 1)
		self.displayModel(ref, 1)

	def manipulateModel(self, model):
		for m in self.refModels:
			state = m == model and 1 or 0
			va, vd = self.modelVars[m]
			va.set(state)
			self.activateModel(m, state)
		for m in self.altModels:
			if m == model:
				# In case we're matching the ensemble to itself
				continue
			n = self.matchVars[m].get()
			if n < 0:
				state = 0
			else:
				state = self.refModels[n] == model and 1 or 0
			va, vd = self.modelVars[m]
			va.set(state)
			self.activateModel(m, state)

	def zoomModel(self, model):
		self.manipulateModel(model)
		sel = selection.ItemizedSelection()
		for m in self.refModels:
			if m.openState.active:
				sel.add(m.atoms)
		for m in self.altModels:
			if m.openState.active:
				sel.add(m.atoms)
		Midas.window(sel)

	def _statusCheck(self, name, closure, triggerData):
		try:
			for ml in self.refModels, self.altModels:
				for m in ml:
					va, vd = self.modelVars[m]
					if va.get() != m.openState.active:
						va.set(m.openState.active)
					if vd.get() != m.display:
						vd.set(m.display)
		except:
			self.emQuit()

	def Hide(self):
		self.emHide()

	def Quit(self):
		self.emQuit()

	#
	# Extension manager callback routines
	#
	def emName(self):
		return self.title

	def emRaise(self):
		self.enter()

	def emHide(self):
		self.Close()

	def emQuit(self):
		if self.trigger:
			chimera.triggers.deleteHandler('check for changes',
							self.trigger)
			self.trigger = None
		self.destroy()
		chimera.extension.manager.deregisterInstance(self)

def tile(modelList, scale=1.1, columns = None, viewAll = True):
	"Arrange the models in the given list in regular rows and columns"

	if not modelList:
		return

	# Make table of openState objects (share same transform)
	osModels = {}
	for m in modelList:
		o = m.openState
		if o in osModels:
			osModels[o].append(m)
		else:
			osModels[o] = [m]
	sortList = [ (min([(m.id, m.subid) for m in mlist]), o)
		     for o,mlist in osModels.items() ]
	sortList.sort()
	oStates = [ t[1] for t in sortList ]

	#
	# Find the bounding sphere of each model.  We first display the
	# model so that the bounding boxes get computed
	# correctly, and reset the display status afterwards.
	#
	displayed = {}
	for m in modelList:
		displayed[m] = m.display
		m.display = True
	bSpheres = {}
	for o,mlist in osModels.items():
		for m in mlist:
			has_bounds, s = m.bsphere()
			if has_bounds:
				s.xform(o.xform)
				if o in bSpheres:
					bSpheres[o].merge(s)
				else:
					bSpheres[o] = s
	if not bSpheres:
		return
	oStates = [o for o in oStates if o in bSpheres]
	radius = max([s.radius for s in bSpheres.values()]) * scale
	for m, disp in displayed.iteritems():
		m.display = disp

	#
	# Find the number of rows and columns that best match the
	# viewer aspect ratio
	#
	nPos = len(bSpheres)
	if columns is None:
		rows, cols = rowAndColumnSize(nPos)
	else:
		cols = columns
		rows = (nPos + cols - 1) / cols

	#
	# Update transformation of models to place them in proper
	# row and column
	#
	diameter = radius * 2
	r = 0
	c = 0
	ref = bSpheres[oStates[0]].center
	xforms = {}
	for o in oStates:
		s = bSpheres[o]
		cx,cy,cz = s.center.data()
		dx = ref.x - cx + c * diameter
		dy = ref.y - cy - r * diameter
		dz = ref.z - cz
		xf = chimera.Xform.translation(dx, dy, dz)
		xforms[m] = xf
		o.globalXform(xf)
		c = c + 1
		if c == cols:
			r = r + 1
			c = 0

	#
	# Update viewing parameters so all models appear in viewer
	#
	if viewAll:
		chimera.viewer.viewAll(resetCofrMethod=False)

def rowAndColumnSize(nPos):

	vWidth, vHeight = chimera.viewer.windowSize
	vRatio = vWidth / float(vHeight)
	for rows in range(1, nPos + 1):
		cols = int((nPos + rows - 1) / rows)
		ratio = cols / float(rows)
		if ratio < vRatio:
			score = ratio / vRatio
		else:
			score = vRatio / ratio
		try:
			if score > bestScore:
				best = (rows, cols)
				bestScore = score
		except NameError:
			best = (rows, cols)
			bestScore = score
	return best

def bboxSize(m):
	for a in m.atoms:
		c = a.coord()
		try:
			if c.x < minX:
				minX = c.x
			elif c.x > maxX:
				maxX = c.x
			if c.y < minY:
				minY = c.y
			elif c.y > maxY:
				maxY = c.y
			if c.z < minZ:
				minZ = c.z
			elif c.z > maxZ:
				maxZ = c.z
		except NameError:
			minX = maxX = c.x
			minY = maxY = c.y
			minZ = maxZ = c.z
	return minX, maxX, minY, maxY, minZ, maxZ

def boundingSphere(m):
	"Compute the bounding sphere with center at average atomic coordinates"
	sumX = 0
	sumY = 0
	sumZ = 0
	atoms = m.atoms
	for a in atoms:
		c = a.coord()
		sumX = sumX + c.x
		sumY = sumY + c.y
		sumZ = sumZ + c.z
	center = chimera.Coord()
	center.x = sumX / len(atoms)
	center.y = sumY / len(atoms)
	center.z = sumZ / len(atoms)
	rsq = 0
	for a in atoms:
		nrsq = center.sqdistance(a.coord())
		if nrsq > rsq:
			rsq = nrsq
	return center.x, center.y, center.z, math.sqrt(rsq)

def cluster(modelList, subSelection):
	"Assign a cluster id to each model in the list"

	if not modelList:
		import chimera
		raise chimera.UserError("No ensemble selected")
	d = EnsembleCluster(modelList, subSelection)

class EnsembleCluster(ModelessDialog):
	"""Display a table for manipulating clusters."""

	title = "Ensemble Cluster"
	help = "ContributedSoftware/ensemblematch/ensemblecluster.html"
	buttons = ("Hide", "Quit")

	def __init__(self, modelList, subSelection, *args, **kw):
		from chimera import preferences
		self._removeHandler = None
		for m in modelList:
			m.preclusterColor = m.color
		self.subSelection = subSelection
		self._cluster(modelList)
		ModelessDialog.__init__(self, *args, **kw)
		chimera.extension.manager.registerInstance(self)
		self._removeHandler = chimera.openModels.addRemoveHandler(
						self._modelsChanged, None)

	def __del__(self):
		if self._removeHandler:
			chimera.openModels.deleteRemoveHandler(self._removeHandler)

	def _cluster(self, modelList):
		from chimera import replyobj
		from distmat import DistanceMatrix
		replyobj.status("Computing distance matrix")
		fulldm = DistanceMatrix(len(modelList))
		sameAs = {}
		atoms = [ match._coordArray(self._getAtoms(m))
				for m in modelList ]
		for i in range(len(modelList)):
			mi = modelList[i]
			if mi in sameAs:
				continue
			ai = atoms[i]
			for j in range(i + 1, len(modelList)):
				aj = atoms[j]
				m = chimera.match.Match(ai, aj)
				if m.rms <= 0:
					mj = modelList[j]
					sameAs[mj] = mi
					print ("Zero RMSD between %s and %s" %
							(mi.oslIdent(), mj.oslIdent()))
				fulldm.set(i, j, m.rms)
		print "RMSD/Distance matrix"
		print fulldm
		if not sameAs:
			dm = fulldm
			models = modelList
		else:
			dm = DistanceMatrix(len(modelList) - len(sameAs))
			models = []
			indexMap = []
			for i, mi in enumerate(modelList):
				if mi in sameAs:
					continue
				models.append(mi)
				indexMap.append(i)
			for i in range(len(models)):
				im = indexMap[i]
				for j in range(i + 1, len(models)):
					jm = indexMap[j]
					dm.set(i, j, fulldm.get(im, jm))
		replyobj.status("Using %d of %d models for clustering" %
					(dm.size, fulldm.size))

		from nmrclust import NMRClust
		nmrc = NMRClust(dm)
		id = 0
		cList = []
		for c in nmrc.clusters:
			members = c.members()
			cList.append((len(members), c, members))
		cList.sort()
		cList.reverse()
		clusterInfo = []
		for i, (size, c, members) in enumerate(cList):
			mList = []
			for member in members:
				m = models[member]
				m.clusterId = id
				m.clusterRep = 0
				mList.append(m)
			rep = nmrc.representative(c)
			m = models[rep]
			m.clusterRep = size
			clusterInfo.append((m, mList))
			id += 1
		for mj, mi in sameAs.iteritems():
			mj.clusterId = mi.clusterId
			mj.clusterRep = 0
			clusterInfo[mj.clusterId][1].append(mj)
		replyobj.status("Generated %d clusters" % id)

		self.nmrc = nmrc
		self.modelList = modelList
		self.clusterInfo = clusterInfo

	def _getAtoms(self, m):
		if not self.subSelection:
			atoms = m.atoms
		else:
			osl = '%s%s' % (m.oslIdent(), self.subSelection)
			s = selection.OSLSelection(osl)
			wanted = s.vertices(asDict=True)
			atoms = [ a for a in m.atoms if a in wanted ]
		return atoms

	def _modelsChanged(self, triggerName, closure, mols):
		self.modelList = [ m for m in self.modelList if m not in mols ]
		for i, (rep, mList) in enumerate(self.clusterInfo):
			newList = [ m for m in mList if m not in mols ]
			if not newList:
				# All members of cluster deleted
				self.clusterInfo[i] = (None, [])
				continue
			if rep in mols:
				newRep = mList[0]
				newRep.clusterRep = rep.clusterRep
			else:
				newRep = rep
			if newRep is not rep or len(newList) != len(mList):
				self.clusterInfo[i] = (newRep, newList)

	def fillInUI(self, parent):
		import Pmw, Tkinter
		from chimera import chimage
		self.parent = parent

		d = prefs.get("treatment", {})
		self.treatmentShow = d.get("show", 0)
		self.treatmentSelAtom = d.get("selectAtoms", 0)
		self.treatmentSelAtomOf = d.get("selectAtomsOf", "all members")
		self.treatmentSelModel = d.get("selectModels", 1)
		self.treatmentSelModelOf = d.get("selectModelsOf", "all members")
		self.treatmentColorModel = d.get("colorModels", 1)
		self.treatmentColorModelOf = d.get("colorModelsOf", "all members")

		self.rightArrow = chimage.get("rightarrow.png", parent)
		self.downArrow = chimage.get("downarrow.png", parent)

		if self.treatmentShow:
			relief = "sunken"
			image = self.downArrow
		else:
			relief = "flat"
			image = self.rightArrow
		self.treatmentGroup = Pmw.Group(parent,
					collapsedsize=0,
					tagindent=0,
					ring_relief=relief,
					tag_pyclass=Tkinter.Button,
					tag_text=" Treatment of Chosen Clusters",
					tag_relief="flat",
					tag_compound="left",
					tag_image=image,
					tag_command=self._treatmentCB)
		if not self.treatmentShow:
			self.treatmentGroup.collapse()
		self.treatmentGroup.pack(side="top", fill="x", padx=3)

		self.treatmentSelAtomVar = Tkinter.IntVar(parent)
		if self.treatmentSelAtom:
			self.treatmentSelAtomVar.set(1)
		else:
			self.treatmentSelAtomVar.set(0)
		f = Tkinter.Frame(self.treatmentGroup.interior())
		f.pack(side="top", fill="x")
		self.treatmentSelAtomButton = Tkinter.Checkbutton(f,
					text=" Select atoms of",
					onvalue=1, offvalue=0,
					variable=self.treatmentSelAtomVar,
					command=self._treatmentSelAtomCB)
		self.treatmentSelAtomButton.pack(side="left")
		self.treatmentSelAtomMenu = Pmw.OptionMenu(f,
					items = ( "representatives",
							"all members" ),
					initialitem=self.treatmentSelAtomOf,
					menubutton_pady=0,
					command=self._treatmentSelAtomCB)
		self.treatmentSelAtomMenu.pack(side="left")

		self.treatmentColorModelVar = Tkinter.IntVar(parent)
		if self.treatmentColorModel:
			self.treatmentColorModelVar.set(1)
		else:
			self.treatmentColorModelVar.set(0)
		f = Tkinter.Frame(self.treatmentGroup.interior())
		f.pack(side="top", fill="x")
		self.treatmentColorModelButton = Tkinter.Checkbutton(f,
					text=" Color",
					onvalue=1, offvalue=0,
					variable=self.treatmentColorModelVar,
					command=self._treatmentColorModelCB)
		self.treatmentColorModelButton.pack(side="left")
		self.treatmentColorModelMenu = Pmw.OptionMenu(f,
					items = ( "representatives",
							"all members" ),
					initialitem=self.treatmentColorModelOf,
					menubutton_pady=0,
					command=self._treatmentColorModelCB)
		self.treatmentColorModelMenu.pack(side="left")

		self.treatmentSelModelVar = Tkinter.IntVar(parent)
		if self.treatmentSelModel:
			self.treatmentSelModelVar.set(1)
		else:
			self.treatmentSelModelVar.set(0)
		f = Tkinter.Frame(self.treatmentGroup.interior())
		f.pack(side="top", fill="x")
		self.treatmentSelModelButton = Tkinter.Checkbutton(f,
					text=" Choose",
					onvalue=1, offvalue=0,
					variable=self.treatmentSelModelVar,
					command=self._treatmentSelModelCB)
		self.treatmentSelModelButton.pack(side="left")
		self.treatmentSelModelMenu = Pmw.OptionMenu(f,
					items = ( "representatives",
							"all members" ),
					initialitem=self.treatmentSelModelOf,
					menubutton_pady=0,
					labelpos="e",
					label_text=" in Model Panel",
					command=self._treatmentSelModelCB)
		self.treatmentSelModelMenu.pack(side="left")

		height = min(len(self.nmrc.clusters), 10)
		values = []
		maxLength = 0
		for id in range(len(self.nmrc.clusters)):
			m = self.clusterInfo[id][0]
			n = len(self.clusterInfo[id][1])
			v = "%d (%d models, rep: %s)" % (id, n, m.oslIdent())
			values.append(v)
			if len(v) > maxLength:
				maxLength = len(v)
		self.listbox = Pmw.ScrolledListBox(self.parent,
					listbox_selectmode="extended",
					listbox_width=maxLength,
					listbox_height=height,
					selectioncommand=self._listboxSelect)
		self.listbox.pack(fill="both", expand=True)
		self.listbox.setlist(values)

	def _treatmentCB(self):
		self.treatmentShow = not self.treatmentShow
		if self.treatmentShow:
			self.treatmentGroup.configure(ring_relief="groove",
						tag_image=self.downArrow)
			self.treatmentGroup.expand()
		else:
			self.treatmentGroup.configure(ring_relief="flat",
						tag_image=self.rightArrow)
			self.treatmentGroup.collapse()
		self._savePrefs()

	def _savePrefs(self):
		prefs["treatment"] = {
			"show": self.treatmentShow,
			"selectAtoms": self.treatmentSelAtom,
			"selectAtomsOf": self.treatmentSelAtomOf,
			"selectModels": self.treatmentSelModel,
			"selectModelsOf": self.treatmentSelModelOf,
			"colorModels": self.treatmentColorModel,
			"colorModelsOf": self.treatmentColorModelOf,
		}
		prefs.save()

	def _treatmentSelAtomCB(self, ignore=None):
		selAtom = self.treatmentSelAtomVar.get()
		selAtomOf = self.treatmentSelAtomMenu.getvalue()
		if (selAtom == self.treatmentSelAtom
		and selAtomOf == self.treatmentSelAtomOf):
			return
		self.treatmentSelAtom = selAtom
		self.treatmentSelAtomOf = selAtomOf
		self._selectionCB()
		self._savePrefs()

	def _treatmentColorModelCB(self, ignore=None):
		colorModel = self.treatmentColorModelVar.get()
		colorModelOf = self.treatmentColorModelMenu.getvalue()
		if (colorModel == self.treatmentColorModel
		and colorModelOf == self.treatmentColorModelOf):
			return
		self.treatmentColorModel = colorModel
		self.treatmentColorModelOf = colorModelOf
		self._colorCB()
		self._savePrefs()

	def _treatmentSelModelCB(self, ignore=None):
		selModel = self.treatmentSelModelVar.get()
		selModelOf = self.treatmentSelModelMenu.getvalue()
		if (selModel == self.treatmentSelModel
		and selModelOf == self.treatmentSelModelOf):
			return
		self.treatmentSelModel = selModel
		self.treatmentSelModelOf = selModelOf
		self._modelPanelCB()
		self._savePrefs()

	def _listboxSelect(self):
		self._selectionCB()
		self._colorCB()
		self._modelPanelCB()

	def _getSelected(self):
		cursel = self.listbox.getcurselection()
		if not cursel:
			idList = range(len(self.clusterInfo))
		else:
			idList = [ int(v.split(None, 1)[0]) for v in cursel ]
		return idList

	def _modelPanelCB(self):
		if not self.treatmentSelModel:
			return
		if self.treatmentSelModelOf == "representatives":
			# Choose representative
			mList = [ self.clusterInfo[id][0]
					for id in self._getSelected() ]
			self._getModelPanel().selectionChange(mList)
		elif self.treatmentSelModelOf == "all members":
			# Choose cluster
			mList = []
			for id in self._getSelected():
				mList.extend(self.clusterInfo[id][1])
			self._getModelPanel().selectionChange(mList)
		else:
			# No action
			pass

	def _selectionCB(self):
		from chimera import selection
		if not self.treatmentSelAtom:
			return
		if self.treatmentSelAtomOf == "representatives":
			# Select representative
			selection.clearCurrent()
			mList = [ self.clusterInfo[id][0]
					for id in self._getSelected() ]
			selection.addCurrent(mList)
			selection.addImpliedCurrent()
		elif self.treatmentSelAtomOf == "all members":
			# Select cluster
			selection.clearCurrent()
			mList = []
			for id in self._getSelected():
				mList.extend(self.clusterInfo[id][1])
			selection.addCurrent(mList)
			selection.addImpliedCurrent()
		else:
			# No action
			pass

	def _getModelPanel(self):
		from ModelPanel import ModelPanel
		from chimera import dialogs
		return dialogs.display(ModelPanel.name)

	def _colorCB(self):
		if self.treatmentColorModel == 0:
			# No action
			return
		idList = self._getSelected()
		from CGLtk.color import colorRange
		from chimera import MaterialColor
		colorList = [MaterialColor(r, g, b, 1.0)
					for r, g, b in colorRange(len(idList))]

		lb = self.listbox.component("listbox")
		origColor = lb["fg"]
		origSelColor = lb["selectforeground"]
		for i, color in enumerate(colorList):
			id = idList[i]
			if self.treatmentColorModelOf == "representatives":
				# Color representative
				for m in self.clusterInfo[id][1]:
					m.color = m.preclusterColor
					self._resetColor(m)
				self.clusterInfo[id][0].color = color
			else:
				# Color cluster
				for m in self.clusterInfo[id][1]:
					m.color = color
					self._resetColor(m)
			r, g, b, a = color.rgba()
			tkColor = "#%02x%02x%02x" % (int(r * 255),
							int(g * 255),
							int(b * 255))
			lb.itemconfigure(id, fg=tkColor,
						selectforeground=tkColor)
		for id in range(len(self.clusterInfo)):
			if id in idList:
				continue
			for m in self.clusterInfo[id][1]:
				m.color = m.preclusterColor
				self._resetColor(m)
			lb.itemconfigure(id, fg=origColor,
						selectforeground=origSelColor)

	def _resetColor(self, m):
		for a in m.atoms:
			a.color = None
			a.surfaceColor = None
			a.labelColor = None
			a.vdwColor = None
		for b in m.bonds:
			b.color = None
			b.labelColor = None

	def Hide(self):
		self.emHide()

	def Quit(self):
		self.emQuit()

	#
	# Extension manager callback routines
	#
	def emName(self):
		return self.title

	def emRaise(self):
		self.enter()

	def emHide(self):
		self.Close()

	def emQuit(self):
		self.destroy()
		chimera.extension.manager.deregisterInstance(self)
