import Pmw, Tkinter
import chimera
from chimera.baseDialog import ModelessDialog
from chimera.widgets import MoleculeScrolledListBox
from chimera.widgets import MoleculeChainScrolledListBox
from CGLtk.color.ColorWell import ColorWell
from CGLtk.Histogram import MarkedHistogram
import SurfMaker

def interpolate(position, marker1, marker2, col1, col2):
	if not marker1 < position < marker2:
		return col1

	ratio = (position - marker1) / float(marker2 - marker1)
	c = list(col1)
	for i in range(4):
		c[i] += ratio*(col2[i]-col1[i])
	return c

def getHistogramColor(x, markers):
	prev = None
	for m in markers:
		if x < m[0]:
			if prev is None:
				return markers[0][1]
			else:
				return interpolate(x, prev[0], m[0],
							prev[1], m[1])
		prev = m
	return markers[-1][1]


def getDistance(a, b):
	a = a.xformCoord()
	b = b.xformCoord()
	return ( (a.x - b.x)**2 + (a.y - b.y)**2 + (a.z - b.z)**2 ) ** 0.5

class Interface(ModelessDialog):
	title = "Compute Interface Surface"
	help = "ContributedSoftware/intersurf/intersurf.html"

	def fillInUI(self, parent):
		self.notebook = Pmw.NoteBook(parent)
		self.notebook.pack(fill="both", expand=True)
		page = self.notebook.add("Molecules")
		self.molChooser = MoleculeScrolledListBox(page,
					listbox_selectmode="extended",
					autoselect="single")
		self.molChooser.pack(fill="both", expand=True)
		page = self.notebook.add("Chains")
		self.chainChooser = MoleculeChainScrolledListBox(page,
					listbox_selectmode="extended",
					autoselect="single")
		self.chainChooser.pack(fill="both", expand=True)
		self.outputOptions = Pmw.RadioSelect(parent,
                                        pady=0,
                                        buttontype="checkbutton",
                                        orient="vertical")
                self.outputOptions.pack(fill="x", expand=False)
                self.outputOptions.add("solid", text="Solid surface (rather than mesh)")
		self.outputOptions.add("track", text="Reuse last surface (if any)")
		self.outputOptions.add("atoms", text="Select interface atoms")
                self.outputOptions.add("prune", text="Residue centroid distance pruning")
		self.outputOptions.setvalue(["solid", "track"])
		self.pruneDistance = Pmw.EntryField(parent,
					labelpos="w",
					label_text="Prune distance:",
					value="30.0",
					validate=self._validatePruneDistance)
		self.pruneDistance.pack(fill="x", expand=False)
		self.moleculeBias = Pmw.Counter(parent,
						labelpos="w",
						label_text="Molecule bias:",
						datatype="real",
						increment = 0.1,
						entryfield_value="0.5",
						entryfield_validate={'validator' : 'real',
						                     'min' : '0.0', 'max' : '1.0',
								     'separator' : '.'})
		self.moleculeBias.pack(fill="x", expand=False)

		histKw = {
			'minlabel': True,
			'maxlabel': True,
			'scaling': 'linear',
		}
		self.histogram = MarkedHistogram(parent, **histKw)
		self.histogramMarkers = self.histogram.addmarkers(activate=True,
						coordtype='relative')
                self.histogramMarkers.extend([
				((1.0, 0.0), (0.0, 0.0, 0.33, 1.0)),
				((0.0, 0.0), (1.0, 0.0, 0.0, 1.0))])
		self.histogram.pack(expand=True, fill="both")
		self._trackedPiece = None
		self._trackedModel = None
		self.models = {}
		chimera.openModels.addRemoveHandler(self._removeModel, None)
		import SimpleSession
		chimera.triggers.addHandler(SimpleSession.SAVE_SESSION,
						self.saveSession, None)
		chimera.triggers.addHandler("Molecule",
						self._moleculeChanged, None)

	def _validatePruneDistance(self, text):
		if len(text) == 0:
			return Pmw.PARTIAL
		try:
			float(text)
		except:
			return Pmw.ERROR
		return Pmw.OK

	def _show_geometry(self, vertices, triangles, vertex_colors, solid=0, track=0):
		import numpy
		varray = numpy.array(vertices, numpy.float32)
		tarray = numpy.array(triangles, numpy.int32)
		carray = numpy.array(vertex_colors, numpy.float32)

		import chimera
		if track and self._trackedPiece:
			sm = self._trackedModel
			g = self._trackedPiece
			g.geometry = varray, tarray
			g.vertexColors = carray
			if solid:
				g.displayStyle = g.Solid
			else:
				g.displayStyle = g.Mesh
		else:
			import _surface
			sm = _surface.SurfaceModel()
			g = sm.addPiece(varray, tarray, (1, 1, 1, 1))
			g.vertexColors = carray
			if solid:
				g.displayStyle = g.Solid
			else:
				g.displayStyle = g.Mesh
			sm.name = "Interface Surface"
			chimera.openModels.add([sm])
			self._trackedPiece = g
			self._trackedModel = sm
		sm.openState.xform = chimera.Xform.identity()
		self.models[sm] = (vertices, triangles, vertex_colors, solid)
		return sm, g

	def Apply(self):
		pageName = self.notebook.getcurselection()
		if pageName == "Molecules":
			target = self.molChooser.getvalue()
		elif pageName == "Chains":
			target = self.chainChooser.getvalue()
		if not target:
			raise chimera.UserError("Please select two molecules/chains")
		if len(target) != 2:
			raise chimera.UserError("Please select exactly two molecules/chains")
                opts = self.outputOptions.getvalue()
                solid = "solid" in opts
		prune = "prune" in opts
		track = "track" in opts
		selAtoms = "atoms" in opts

		if not self.moleculeBias.valid():
			raise chimera.UserError("Please enter a valid bias toward the second molecule")
		bias = float(self.moleculeBias.getvalue())
		if prune:
			if not self.pruneDistance.valid():
				raise chimera.UserError("Please enter a valid prune distance")
			pruneDistance = float(self.pruneDistance.getvalue())
		else:
			pruneDistance = 0
		self.doApply(target, solid, track, selAtoms,
				bias, prune, pruneDistance)

	def doApply(self, target, solid, track, selAtoms,
			bias, prune, pruneDistance):
		m1, m2 = target
		if prune:
			m1_list = SurfMaker.GetAtomList(m1, m2, pruneDistance)
			m2_list = SurfMaker.GetAtomList(m2, m1, pruneDistance)
		else:
			m1_list = SurfMaker.GetAtomList(m1)
			m2_list = SurfMaker.GetAtomList(m2)

		if not m1_list or not m2_list:
			raise chimera.UserError("No interface surface found")
		p = SurfMaker.UnpackIntersurfData(m1_list, m2_list)
		tetras = SurfMaker.ComputeTetrahedralization(p)
		surfPoints, surfTriangles, surfAtoms = SurfMaker.ComputeSurface(p, tetras, bias)

		surfMetric = [ getDistance(x[0], x[1]) for x in surfAtoms ]
		lo = min(surfMetric)
		hi = max(surfMetric)
		scale = hi - lo
		markers = [ (lo + m['xy'][0] * scale, m['rgba'])
				for m in self.histogramMarkers ]
		surfColors = [ getHistogramColor(x, markers)
					for x in surfMetric ] 
		self.histogramData = (lo, hi, surfMetric)
		def myMakeBars(numBins, data=self.histogramData):
			return makeBars(numBins, data)
		self.histogram["datasource"] = (lo, hi, myMakeBars)

		self._show_geometry(surfPoints, surfTriangles, surfColors, solid, track)
		if selAtoms:
			from chimera import selection
			atomSet = set([])
			for a1, a2 in surfAtoms:
				atomSet.add(a1)
				atomSet.add(a2)
			sel = selection.ItemizedSelection()
			sel.add(atomSet)
			sel.addImplied(vertices=False)
			selection.setCurrent(sel)

	def _removeModel(self, trigger, data, models):
		for m in models:
			if self._trackedModel is m:
				self._trackedModel = None
				self._trackedPiece = None
			try:
				del self.models[m]
			except KeyError:
				pass

	def _moleculeChanged(self, trigger, data, models):
		if 'activeCoordSet changed' not in models.reasons:
			return
		pageName = self.notebook.getcurselection()
		if pageName == "Molecules":
			target = self.molChooser.getvalue()
		elif pageName == "Chains":
			target = [ c.molecule for c in self.chainChooser.getvalue() ]
		else:
			return
		for m in models.modified:
			if m in target:
				break
		else:
			return
		self.Apply()

	def saveSession(self, trigger, data, file):
		isMapped = self.uiMaster().winfo_ismapped()
		if not isMapped and not self.models:
			# Not visible and no displayed surfaces
			return
		from SessionUtil import stateclasses, objecttree
		restoring_code = \
"""
def restoreIntersurfSession(state):
	import SimpleSession
	from Intersurf import Intersurf
	SimpleSession.registerAfterModelsCB(Intersurf.restoreSession, state)
risArgs = (%s)
try:
	restoreIntersurfSession(risArgs)
except:
	reportRestoreError("Error restoring Intersurf extension")
"""
		pageName = self.notebook.getcurselection()
		chosenMolecules = self.molChooser.getcurselection()
		chosenChains = self.chainChooser.getcurselection()
                opts = self.outputOptions.getvalue()
		pruneDistance = self.pruneDistance.getvalue()
		bias = self.moleculeBias.getvalue()
		if isinstance(self.histogram["datasource"], basestring):
			histogramData = self.histogram["datasource"]
		else:
			histogramData = self.histogramData
		markerValues = []
		markers, selectedMarker = self.histogram.currentmarkerinfo()
		if markers:
			for m in markers:
				markerValues.append((m["xy"], m["rgba"]))
		ms = stateclasses.Model_State()
		modelData = []
		trackedIndex = -1
		n = 0
		for m, v in self.models.iteritems():
			if self._trackedModel is m:
				trackedIndex = n
			ms.state_from_model(m)
			bt = objecttree.instance_tree_to_basic_tree(ms)
			modelData.append((v, bt))
			n += 1
		state = (pageName, chosenMolecules, chosenChains, opts,
				pruneDistance, bias,
				histogramData, markerValues,
				modelData, trackedIndex, isMapped)
		file.write(restoring_code % repr(state))

	def restoreSession(self, state):
		from SessionUtil import stateclasses, objecttree
		if len(state) == 10:
			(pageName, chosenMolecules, chosenChains, opts,
				pruneDistance, bias,
				dataSource, markerValues,
				modelData, trackedIndex) = state
			if modelData:
				isMapped = True
			else:
				isMapped = False
		else:
			(pageName, chosenMolecules, chosenChains, opts,
				pruneDistance, bias,
				histogramData, markerValues,
				modelData, trackedIndex, isMapped) = state
		# Call get method to make sure items are updated
		self.molChooser.get()
		self.molChooser.setvalue(chosenMolecules)
		self.chainChooser.get()
		self.chainChooser.setvalue(chosenChains)
		self.notebook.selectpage(pageName)
		self.outputOptions.setvalue(list(opts))
		self.pruneDistance.setvalue(pruneDistance)
		self.moleculeBias.setvalue(bias)
		if isinstance(histogramData, basestring):
			dataSource = histogramData
		else:
			lo, hi, surfMetric = histogramData
			self.histogramData = (lo, hi, surfMetric)
			def myMakeBars(numBins, data=self.histogramData):
				return makeBars(numBins, data)
			dataSource = (lo, hi, myMakeBars)
		self.histogram["datasource"] = dataSource
		if markerValues:
			oldMarkers = self.histogram.currentmarkerinfo()[0]
			newMarkers = self.histogram.addmarkers()
			newMarkers.extend(markerValues)
			self.histogram.deletemarkers(oldMarkers)
			self.histogramMarkers = newMarkers
		trackedModel = None
		trackedPiece = None
		nameToClass = {
			"Model_State": stateclasses.Model_State,
			"Xform_State": stateclasses.Xform_State,
		}
		for n, mState in enumerate(modelData):
			if len(mState) == 2:
				v, bt = mState
			else:
				v = mState
				bt = None
			sm, g = self._show_geometry(*v)
			if trackedIndex == n:
				trackedModel = sm
				trackedPiece = g
			if bt is not None:
				ms = objecttree.basic_tree_to_instance_tree(bt,
							nameToClass)
				ms.restore_state(sm)
		if trackedModel:
			self._trackedModel = trackedModel
			self._trackedPiece = trackedPiece
		if not isMapped:
			self.Close()

def makeBars(numBins, data):
	lo, hi, surfMetric = data
	binSize = (hi - lo) / numBins
	if binSize < 0.1:
		binSize = 0.1
		numBins = int((hi - lo) / binSize)
	hist = numBins * [ 0 ]
	for v in surfMetric:
		bin = int((v - lo) / binSize)
		try:
			hist[bin] += 1
		except IndexError:
			# Max value might generate this
			hist[-1] += 1
	return hist

singleton = None

def run():
	global singleton
	if not singleton:
		singleton = Interface()
	singleton.enter()

def restoreSession(state):
	if not singleton:
		run()
	singleton.restoreSession(state)

def makeSurface(target, solid, track, select, bias, prune, pruneDistance):
	if not singleton:
		run()
	singleton.doApply(target, solid, track, select,
				bias, prune, pruneDistance)

#
# Midas command line parsing and execution
#
def commandLine(cmd, args):
	if args.lower().startswith("co"):
		# Handle "color" command differently
		from chimera import LimitationError
		raise LimitationError("intersurf color not available yet")
	from Midas.midas_text import doExtensionFunc
	doExtensionFunc(cmdSurface, args, specInfo=[("refSpec", "refSel", None),
                                        ("matchSpec", "matchSel", None)])

def cmdSurface(refSel, matchSel, pairing="model", solid=True, track=True,
		select=False, bias=0.5, prune=0.0):
	from chimera import UserError
	if bias < 0.0 or bias > 1.0:
		raise UserError("bias must be between 0 and 1")
	if prune > 0.0:
		pruneDistance = prune
		prune = True
	else:
		pruneDistance = 0.0
		prune = False
	if "model".startswith(pairing):
		pairing = "model"
	elif "chain".startswith(pairing):
		pairing = "chain"
	elif "atom".startswith(pairing):
		pairing = "atom"
	else:
		raise UserError("unknown pairing method: %s" % pairing)
	if pairing == "model":
		refMols = refSel.molecules()
		if len(refMols) != 1:
			raise UserError("%d reference molecules selected "
					"(must be 1)" % len(refMols))
		matchMols = matchSel.molecules()
		if len(matchMols) != 1:
			raise UserError("%d match molecules selected "
					"(must be 1)" % len(matchMols))
		target = (refMols[0], matchMols[0])
		if target[0] == target[1]:
			pairing = "chain"
	if pairing == "chain":
		refChains = refSel.chains()
		if len(refChains) != 1:
			raise UserError("%d reference chains selected "
					"(must be 1)" % len(refChains))
		matchChains = matchSel.chains()
		if len(matchChains) != 1:
			raise UserError("%d match chains selected "
					"(must be 1)" % len(matchChains))
		target = (refChains[0], matchChains[0])
	if pairing == "atom":
		refAtoms = refSel.atoms()
		matchAtoms = matchSel.atoms()
		target = (refAtoms, matchAtoms)
		prune = False
	makeSurface(target, solid, track, select, bias, prune, pruneDistance)
