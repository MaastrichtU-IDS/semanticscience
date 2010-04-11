# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: __init__.py 28910 2009-09-29 21:52:47Z pett $

"""
The selection module provides tools for managing selection set and
maintains the current selection.

The module constants are:

REPLACE -- replace selection with new selection
EXTEND -- extend selection with new selection
REMOVE -- remove new selection from selection
INTERSECT -- intersect new selection with selection
"""
#import sys, traceback,operator
import chimera
from chimera import SelEdge, SelVertex, SelSubgraph, SelGraph
import copy

# selection update methods
REPLACE = intern("replace")
EXTEND = intern("extend")
REMOVE = intern("remove from")
INTERSECT = intern("intersect with")

# user-saved selections (from Selection menu)
savedSels = {}
def saveSel(saveName, sel=None, updateGui=True):
	if sel is None:
		sel = copyCurrent()
	if updateGui and not chimera.nogui:
		from chimera.tkgui import selSaver
		selSaver[0]._saveCB(saveName, sel) # will call back...
		return
	savedSels[saveName] = sel

class Selection:
	"""Base class for selections.
	
	Selection(name, description) => Selection instance

	A Selection is a set of selectable objects.

	This class must be subclassed.
	"""

	def contents(self, asDict=False):
		"""Return all vertices/edges selected by the selection.

		selection.contents() => ( [vertex-objs], [edge-objs] )
		
		if 'asDict' is True, the vertices/edges are returned as 
		dictionaries (keys are vertices/edges, arbitrary values)

		This is a default implementation that uses the apply function.
		"""

		if asDict:
			vertices = {}
			edges = {}
			def setDict(d, k):
				d[k] = ()
			vFunc = lambda v, f=setDict, dict=vertices: f(dict, v)
			eFunc = lambda e, f=setDict, dict=edges: f(dict, e)
		else:
			vertices = []
			edges = []
			vFunc = lambda v, list=vertices: list.append(v)
			eFunc = lambda e, list=edges: list.append(e)
		self.apply(vFunc, eFunc)
		return (vertices, edges)

	def counts(self):
		return map(len, self.contents())

	def __len__(self):
		"""Total count of items in selection"""
		vertices, edges = self.contents()
		return len(vertices) + len(edges)

	def __str__(self):
		"""Return the printable string representation of the selection.
		
		str(selection) => string
		"""
		raise TypeError, "Instance must be of a subtype of Selection"

	def apply(self, vFunc = None, eFunc = None):
		"""Call given functions for objects that match selection.

		selection.apply(vFunc, eFunc) => None

		vFunc is the function for vertices while eFunc is the
		function for edges.

		All calls to the eFunc are made before any calls to the vFunc.

		This function must be implemented in subclasses.
		"""
		raise AssertionError, \
			"Selection subclass does not implement apply()"

	def edges(self, asDict=False):
		"""Return all edges in the selection.

		selection.edges() => [edge-objs]
		
		if 'asDict' is True, the edges are returned as a
		dictionary (keys are edges, arbitrary values)

		This is a default implementation that uses the apply function.
		"""
		if asDict:
			edges = {}
			def setDict(d, k):
				d[k] = ()
			eFunc = lambda e, f=setDict, dict=edges: f(dict, e)
		else:
			edges = []
			eFunc = lambda e, list=edges: list.append(e)
		self.apply(None, eFunc)
		return edges
	
	def vertices(self, asDict=False):
		"""Return all vertices in the selection.

		selection.vertices() => [vertex-objs]
		
		if 'asDict' is True, the vertices are returned as a
		dictionary (keys are vertices, arbitrary values)

		This is a default implementation that uses the apply function.
		"""

		if asDict:
			vertices = {}
			def setDict(d, k):
				d[k] = ()
			vFunc = lambda v, f=setDict, dict=vertices: f(dict, v)
		else:
			vertices = []
			vFunc = lambda v, list=vertices: list.append(v)
		self.apply(vFunc, None)
		return vertices

	def subgraphs(self, asDict=False):
		"""Return the implicitly selected graphs

		selection.subgraphs() => [subgraphs]
		
		if 'asDict' is True, the subgraphs are returned as a
		dictionary (keys are subgraphs, arbitrary values)
		"""

		verts, edges = self.contents()

		vSet = set()
		vOrder = []
		for v in verts:
			if v not in vSet:
				vSet.add(v)
				vOrder.append(v)
		
		for e in edges:
			if isinstance(e, chimera.PseudoBond):
				# pseudobonds are not subgraph components
				continue
			for v in e.oslParents():	# ends
				if v not in vSet:
					vSet.add(v)
					vOrder.append(v)
		
		sMap = {}
		sOrder = []
		for v in vOrder:
			sg = v.oslParents()[0]
			if sg.oslLevel() == SelSubgraph:
				if sg not in sMap:
					sMap[sg] = 1
					sOrder.append(sg)
		
		if asDict:
			return sMap
		return sOrder

	def graphs(self, asDict=False):
		gMap = {}
		gOrder = []
		for v in self.vertices():
			p = v.oslParents()[0]
			if p.oslLevel() == SelGraph:
				if p not in gMap:
					gMap[p] = 1
					gOrder.append(p)
			elif p.oslLevel() == SelSubgraph:
				pp = p.oslParents()[0]
				if pp.oslLevel() == SelGraph:
					if pp not in gMap:
						gMap[pp] = 1
						gOrder.append(pp)
		for sg in self.subgraphs():
			p = sg.oslParents()[0]
			if p not in gMap:
				gMap[p] = 1
				gOrder.append(p)
		for b in self.barrenGraphs():
			if b not in gMap:
				gMap[b] = 1
				gOrder.append(b)
		
		# while a selected chain trace doesn't select residues, bonds,
		# or atoms, it _should_ select the molecule (graph).  Add them.
		for e in self.edges():
			if not isinstance(e, chimera.PseudoBond):
				continue
			pbg = e.pseudoBondGroup
			if pbg not in gMap:
				gMap[pbg] = 1
				gOrder.append(pbg)
			if isinstance(pbg, chimera.ChainTrace):
				m = e.atoms[0].molecule
				if m not in gMap:
					gMap[m] = 1
					gOrder.append(m)
		if asDict:
			return gMap
		return gOrder

	models = graphs
	
	def barrenGraphs(self, asDict=False):
		"""Graphs that have no vertices/edges
		
		   Since contained graphs are normally computed from 
		   vertices/edges, such 'barren' graphs have to be
		   tracked separately.  If 'asDict' is True, then a 
		   dictionary (keys: barren graphs, values: arbitrary)
		   is returned instead of a list.
		   
		   Must be implemented by subclasses
		"""
		raise AssertionError, \
			"Selection subclass does not implement barrenGraphs()"

	def _filtered(self, items, klass):
		if isinstance(items, list):
			return filter(lambda i: isinstance(i, klass), items)
		for i in items.keys():
			if not isinstance(i, klass):
				del items[i]
		return items

	def atoms(self, **kw):
		return self._filtered(self.vertices(**kw), chimera.Atom)

	def bonds(self, **kw):
		return self._filtered(self.edges(**kw), chimera.Bond)

	def residues(self, **kw):
		resList = list(chimera.atomsBonds2Residues(self.atoms(),
							self.bonds()))
		if kw.get('asDict', False):
			resDict = {}
			for res in resList:
				resDict[res] = 1
			return resDict
		return resList

	def chains(self, **kw):
		resDict = self.residues(asDict=True)
		chains = []
		if 'asDict' in kw:
			asDict = kw['asDict']
			del kw['asDict']
		else:
			asDict = False
		for mol in self.molecules():
			for seq in mol.sequences(**kw):
				for res in seq.residues:
					if res in resDict:

						chains.append(seq)
						break
		if asDict:
			chainDict = {}
			for chain in chains:
				chainDict[chain] = 1
			return chainDict
		return chains

	def molecules(self, **kw):
		return self._filtered(self.graphs(**kw), chimera.Molecule)

class ItemizedSelection(Selection):
	"""Itemized Selection class

	ItemizedSelection() => ItemizedSelection instance

	Itemized selections are selections where all of the objects selected
	are enumerated.

	A callback can be provided for notification of changes to the contents
	of the selection that occur "automatically" (i.e. in response to the
	Selectable trigger, not from API calls such as add()).
	"""

	def __init__(self, initialItems=[], selChangedCB=None):
		self._cache = {} # can't cache in Selection itself (OSL)
		self._edges = {}
		self._vertices = {}
		self._barrenGraphs = {}
		self._index = 0
		self.selChangedCB = selChangedCB
		self.items = {
			SelVertex: self._vertices,
			SelEdge: self._edges,
			SelGraph: self._barrenGraphs
		}

		# since bound methods are "first class" objects, using
		# a proxy of a bound method doesn't work as expected
		# (the proxy immediately becomes invalid), so...
		from weakref import proxy
		def wrapper(a1, a2, a3, s=proxy(self)):
			s._removeType(a1, a2, a3)
		self.removeHandler = chimera.triggers.addHandler(
					'Selectable', wrapper, None)

		if initialItems:
			self.add(initialItems)

	def __del__(self):
		if not chimera or not chimera.triggers:
			# chimera package already gone
			return
		chimera.triggers.deleteHandler('Selectable', self.removeHandler)

	def _removeType(self, trigger, myData, types):
		deleted = types.deleted
		if not deleted:
			return
		selChanged = False
		for obj in deleted:
			# be careful to use Python-level attributes only
			if not hasattr(obj.__class__, "selLevel"):
				continue
			level = obj.__class__.selLevel
			if level not in self.items:
				continue
			if obj in self.items[level]:
				selChanged = True
				del self.items[level][obj]
		if selChanged:
			self._cache = {}
			if self.selChangedCB:
				self.selChangedCB()

	def __copy__(self):
		s = ItemizedSelection()
		s._index = self._index
		s._vertices = self._vertices.copy()
		s._edges = self._edges.copy()
		s._barrenGraphs = self._barrenGraphs.copy()
		s.items[SelVertex] = s._vertices
		s.items[SelEdge] = s._edges
		s.items[SelGraph] = s._barrenGraphs
		return s

	def __str__(self):
		"""Return simple string representation.

		str(selection) => string

		The returned string has the name of the selection and
		the number of contained vertices and edges.
		"""
		rep = "<" + self.__class__.__name__ + ": "
		separator = ""
		count = len(self._vertices)
		if count > 0:
			rep = rep + separator
			separator = ", "
			if count == 1:
				rep = rep + " 1 vertex"
			else:
				rep = rep + " " + str(count) + " vertices"
		count = len(self._edges)
		if count > 0:
			rep = rep + separator
			separator = ", "
			if count == 1:
				rep = rep + " 1 edge"
			else:
				rep = rep + " " + str(count) + " edges"
		count = len(self._barrenGraphs)
		if count > 0:
			rep = rep + separator
			separator = ", "
			if count == 1:
				rep = rep + " 1 childless graph"
			else:
				rep = rep + " %d childless graphs" % count
		if not separator:
			rep = rep + "empty"
		rep = rep + ">"
		return rep

	def contents(self, asDict=False, ordered=False):
		"""Return all vertices/edges selected by the selection.

		selection.contents() => ( [vertex-objs], [edge-objs] )

	   	Returns a 2-tuple composed of a list of vertices and a list of
	   	edges.  If 'asDict' is true, then dictionaries whose keys are
	   	vertices/edges are returned instead of lists.
	
	   	if 'ordered' is true and lists are being returned, the lists are
	   	in the same order as the edges and vertices were added to the
	   	selection.  If dictionaries are being returned, the values are
	   	integers that indicate the ordering (may be non-consecutive
	   	integers).
		"""

		if asDict:
			return (self._vertices.copy(), self._edges.copy())
		vertices = self._vertices.keys()
		edges = self._edges.keys()
		if ordered:
			vertices.sort(lambda a, b, d=self._vertices:
							cmp(d[a], d[b]))
			edges.sort(lambda a, b, d=self._edges:
							cmp(d[a], d[b]))
		return (vertices, edges)

	def counts(self):
		"""Return counts of vertices/atoms as tuple"""
		return (len(self._vertices), len(self._edges))
	
	def __len__(self):
		"""Return total count of items (except barren graphs)"""
		return len(self._vertices) + len(self._edges)

	def empty(self):
		"""Return True if selection is empty"""
		return len(self) == 0 and not self._barrenGraphs

	def edges(self, asDict=False, ordered=False):
		"""Return all edges in the selection.

		selection.edges() => [edge-objs]

		if 'asDict' is True, return a dictionary whose keys are
		the edges and whose values are arbitrary.

		if 'ordered' is True, return in the same order that the
		edges were added to the selection.
		"""

		if asDict:
			return self._edges.copy()
		edges = self._edges.keys()
		if ordered:
			edges.sort(lambda a, b, d=self._edges: cmp(d[a], d[b]))
		return edges

	def vertices(self, asDict=False, ordered=False):
		"""Return all vertices in the selection.

		selection.vertices() => [vertex-objs]

		if 'asDict' is True, return a dictionary whose keys are
		the vertices and whose values are arbitrary.

		if 'ordered' is True, return in the same order that the
		vertices were added to the selection.
		"""

		if asDict:
			return self._vertices.copy()
		vertices = self._vertices.keys()
		if ordered:
			vertices.sort(lambda a, b, d=self._vertices:
							cmp(d[a], d[b]))
		return vertices

	def subgraphs(self, asDict=False):
		cacheKey = ("subgraphs", asDict)
		if not self._cache.has_key(cacheKey):
			self._cache[cacheKey] = Selection.subgraphs(self,asDict)
		return copy.copy(self._cache[cacheKey])

	def graphs(self, asDict=False):
		cacheKey = ("graphs", asDict)
		if not self._cache.has_key(cacheKey):
			self._cache[cacheKey] = Selection.graphs(self, asDict)
		return copy.copy(self._cache[cacheKey])

	models = graphs

	def barrenGraphs(self, asDict=False):
		"""Graphs that have no child edges/vertices"""

		if asDict:
			return self._barrenGraphs.copy()
		return self._barrenGraphs.keys()

	def atoms(self, **kw):
		cacheInfo = kw.items()
		cacheInfo.sort()
		cacheKey = ("atoms", tuple(cacheInfo))
		if not self._cache.has_key(cacheKey):
			self._cache[cacheKey] = Selection.atoms(self, **kw)
		return copy.copy(self._cache[cacheKey])

	def bonds(self, **kw):
		cacheInfo = kw.items()
		cacheInfo.sort()
		cacheKey = ("bonds", tuple(cacheInfo))
		if not self._cache.has_key(cacheKey):
			self._cache[cacheKey] = Selection.bonds(self, **kw)
		return copy.copy(self._cache[cacheKey])

	def residues(self, **kw):
		cacheInfo = kw.items()
		cacheInfo.sort()
		cacheKey = ("residues", tuple(cacheInfo))
		if not self._cache.has_key(cacheKey):
			self._cache[cacheKey] = Selection.residues(self, **kw)
		return copy.copy(self._cache[cacheKey])

	def chains(self, **kw):
		cacheInfo = kw.items()
		cacheInfo.sort()
		cacheKey = ("chains", tuple(cacheInfo))
		if not self._cache.has_key(cacheKey):
			self._cache[cacheKey] = Selection.chains(self, **kw)
		return copy.copy(self._cache[cacheKey])

	def molecules(self, **kw):
		cacheInfo = kw.items()
		cacheInfo.sort()
		cacheKey = ("molecules", tuple(cacheInfo))
		if not self._cache.has_key(cacheKey):
			self._cache[cacheKey] = Selection.molecules(self, **kw)
		return copy.copy(self._cache[cacheKey])

	def apply(self, vFunc = None, eFunc = None):
		"""Apply given functions to selected items.

		selection.apply(vFunc=lambda....) => None
		"""
		if vFunc:
			for v in self._vertices.keys():
				vFunc(v)
		if eFunc:
			for e in self._edges.keys():
				eFunc(e)

	def implied(self, vertices=True, edges=True, asDict=False):
		"""Return vertices/edges implied by selection but not in it.

		selection.implied() => ( [vertices], [edges] )

		if 'vertices' and/or 'edges' is False, the corresponding tuple
		entry will be None.  If 'asDict' is True, the vertices/edges
		will be returned as dictionaries (keys: vertices/edges,
		values: arbitrary)
		"""
		
		vDict, eDict = self._vertices, self._edges

		if vertices:
			impVDict = {}
			for e in eDict.keys():
				for v in e.oslParents():
					if not vDict.has_key(v):
						impVDict[v] = self._index
						self._index +=1
			if asDict:
				impV = impVDict
			else:
				impV = impVDict.keys()
		else:
			impV = None
		
		if edges:
			candidates = {}
			impEDict = {}
			for v in vDict.keys():
				for e in v.oslChildren():
					if eDict.has_key(e):
						continue
					if candidates.has_key(e):
						impEDict[e] = self._index
						self._index += 1
					else:
						candidates[e] = ()
			if asDict:
				impE = impEDict
			else:
				impE = impEDict.keys()
		else:
			impE = None
		
		return (impV, impE)

	def addImplied(self, vertices=True, edges=True):
		"""Add implied vertices/edges (see implied())

		selection.addImplied() => None

		Somewhat more efficient than implied() followed by add()
		"""

		impV, impE = self.implied(vertices=vertices, edges=edges,
								asDict=True)
		if impV:
			self._vertices.update(impV)
		if impE:
			self._edges.update(impE)
		self._cache = {}

	def add(self, it):
		"""Add selectable item or sequence/dict of items to selection.

		selection.add(it) => None

		if 'it' is a dictionary, the keys are assumed to be the items
		to add.  The values are ignored.
		"""
		if isinstance(it, dict):
			it = it.keys()
		elif not isinstance(it, (list, tuple, set)):
			it = [it]

		subitems = []
		for item in it:
			level = item.oslLevel()
			if level == SelGraph:
				if isinstance(item, chimera.Molecule):
					# preserve atom ordering...
					for r in item.residues:
						subitems.extend(r.oslChildren())
					subitems.extend(item.bonds)
					continue
				elif isinstance(item, chimera.MSMSModel):
					subitems.extend(item.atoms)
					subitems.extend(item.bonds)
					subitems.extend(item.surfacePieces)
				else:
					if item.oslChildren():
						subitems.extend(
							item.oslChildren())
					else:
						self._barrenGraphs[item] = ()
					continue

			elif level == SelSubgraph:
				vertices = item.oslChildren()
				# add only edges completely contained in
				# subgraph
				candidate = {}
				contained = []
				for v in vertices:
					for e in v.oslChildren():
						if candidate.has_key(e):
							contained.append(e)
						else:
							candidate[e] = 1
				subitems.extend(vertices)
				subitems.extend(contained)
				continue

			from _surface import SurfacePiece
			if (isinstance(item, SurfacePiece) and
			    isinstance(item.model, chimera.MSMSModel)):
				surf = item.model
				subitems.extend(surf.atoms)
				subitems.extend(surf.bonds)

			# ordinary vertices/edges
			self.items[level][item] = self._index
			self._index += 1

		self._cache = {}
		if subitems:
			self.add(subitems)

	def remove(self, it):
		"""Remove selectable item or items from selection.

		selection.remove(it) => None
		"""
		if isinstance(it, dict):
			it = it.keys()
		elif not isinstance(it, (list, tuple, set)):
			it = [it]

		for item in it:
			level = item.oslLevel()
			if level == SelGraph and item.oslChildren():
				if isinstance(item, chimera.Molecule):
					self.remove(item.atoms)
					self.remove(item.bonds)
				else:
					self.remove(item.oslChildren())
				continue

			if level == SelSubgraph:
				vertices = item.oslChildren()
				# remove all edges connected to subgraph
				edges = {}
				for v in vertices:
					for e in v.oslChildren():
						edges[e] = 1
				self.remove(vertices)
				self.remove(edges.keys())
				continue

			try:
				del self.items[level][item]
			except KeyError:
				continue

		self._cache = {}

	def clear(self):
		if self._vertices:
			self._vertices.clear()
		if self._edges:
			self._edges.clear()
		if self._barrenGraphs:
			self._barrenGraphs.clear()
		self._index = 0
		self._cache = {}

	def toggle(self, it):
		"""Toggle selectable item or items in selection.

		selection.toggle(it) => None

		Add the item if it isn't there, remove it if it is there.
		"""
		if isinstance(it, dict):
			it = it.keys()
		elif not isinstance(it, (list, tuple, set)):
			it = [it]
		
		addItems = {}
		removeItems = {}

		for item in it:
			if self.contains(item):
				items = removeItems
			else:
				items = addItems
			if items.has_key(item):
				del items[item]
			else:
				items[item] = ()
		
		if addItems:
			self.add(addItems.keys())
		if removeItems:
			self.remove(removeItems.keys())

	def contains(self, object):
		"""Is object contained in selection?

		selection.contains(object) => boolean

		Test for membership in selection.
		"""
		lev = object.oslLevel()
		if lev == SelGraph:
			return object in self.graphs(asDict=True)
		elif lev == SelSubgraph:
			return object in self.subgraphs(asDict=True)
		return self.items[lev].has_key(object)

	def merge(self, method, selection):
		"""Use method to merge given selection with this selection.

		selection.merge(method, other-selection) => None

		method may be one of the module constants INTERSECT, EXTEND,
		REPLACE, or REMOVE.
		"""
		if method == INTERSECT:
			vertices, edges = selection.contents(asDict=True)
			bgraphs = selection.barrenGraphs(asDict=True)
			for v in self._vertices.keys():
				if not vertices.has_key(v):
					del(self._vertices[v])

			for e in self._edges.keys():
				if not edges.has_key(e):
					del(self._edges[e])
			
			for bg in self._barrenGraphs.keys():
				if not bgraphs.has_key(bg):
					del(self._barrenGraphs[bg])
		elif method == EXTEND or method == REPLACE:
			vertices, edges = selection.contents(asDict=True)
			bgraphs = selection.barrenGraphs(asDict=True)
			if method == REPLACE:
				self._vertices.clear()
				self._edges.clear()
				self._barrenGraphs.clear()
				if isinstance(selection, ItemizedSelection):
					self._index = len(vertices) + len(edges)
				else:
					self._index = 0
					for v in vertices.keys():
						vertices[v] = self._index
						self._index += 1
					for e in edges.keys():
						edges[e] = self._index
						self._index += 1
			else:
				# maintain ordering
				if isinstance(selection, ItemizedSelection):
					maxOther = 0
					for v, i in vertices.items():
						if self._vertices.has_key(v):
							vertices[v] = \
							self._vertices[v]
							continue
						vertices[v] += self._index
						maxOther = max(maxOther, i)
					for e, i in edges.items():
						if self._edges.has_key(e):
							edges[e] = \
							self._edges[e]
							continue
						edges[e] += self._index
						maxOther = max(maxOther, i)
					self._index += maxOther
				else:
					for v in vertices.keys():
						vertices[v] = self._index
						self._index += 1
					for e in edges.keys():
						edges[e] = self._index
						self._index += 1
			self._vertices.update(vertices)
			self._edges.update(edges)
			self._barrenGraphs.update(bgraphs)
		elif method == REMOVE:
			# need to extend given selection to add connected
			# edges, so that there will not be "dangling"
			# edges after removal
			vertices, edges = selection.contents(asDict=True)
			for v in vertices.keys():
				for e in v.oslChildren():
					if e not in edges:
						edges[e] = 0

			for v in vertices:
				if self._vertices.has_key(v):
					del(self._vertices[v])
			for e in edges:
				if self._edges.has_key(e):
					del(self._edges[e])
			for bg in selection.barrenGraphs():
				if self._barrenGraphs.has_key(bg):
					del(self._barrenGraphs[bg])
		else:
			raise TypeError, "improper merge method"
		# clearing the cache needs to be down here since,
		# due to optimizing intersect and subtract operations,
		# the current graphs may be asked for in the above code,
		# which will repopulate the cache with old values
		self._cache = {}

class _CurrentSelection(ItemizedSelection):

	def __init__(self):
		ItemizedSelection.__init__(self,
					selChangedCB=self._typesRemoved)
		self.monitorHandler = None
		chimera.triggers.addTrigger("selection changed")
		self.color = None

	def _monitorChangesCB(self, trigName, myData, trigData):
		chimera.triggers.deleteHandler('monitor changes',
							self.monitorHandler)
		self.monitorHandler = None
		self._updateGraphics()
		chimera.triggers.activateTrigger('selection changed', self)

	def _typesRemoved(self):
		if not self.monitorHandler:
			# don't fire 'selection changed' trigger or 
			# update selection here;
			# wait for all changes by registering with
			# 'monitor changes' before firing
			self.monitorHandler = chimera.triggers.addHandler(
				'monitor changes', self._monitorChangesCB, None)

	def _updateGraphics(self):
		sset = chimera.viewer.selectionSet
		sset.clear()
		for items in self.items.values():
			sset.update(items)
		sset.update({}.fromkeys(chimera.atomsBonds2Residues(
					self.atoms(), self.bonds()), True))
		try:
			chimera.viewer.invalidateSelectionCache()
		except AttributeError:
			pass  # presumably nogui
		
	def add(self, it):
		if isinstance(it, dict):
			it = it.keys()
		elif not isinstance(it, (list, tuple, set)):
			it = [it]
		ItemizedSelection.add(self, it)
		self._updateGraphics()
		chimera.triggers.activateTrigger('selection changed', self)

	def addImplied(self, vertices=True, edges=True):
		impV, impE = self.implied(vertices=vertices, edges=edges)
		ItemizedSelection.addImplied(self,
						vertices=vertices, edges=edges)
		if impV or impE:
			self._updateGraphics()
		chimera.triggers.activateTrigger('selection changed', self)

	def clear(self):
		if len(self) == 0 and not self._barrenGraphs:
			return
		ItemizedSelection.clear(self)
		self._updateGraphics()
		chimera.triggers.activateTrigger('selection changed', self)

	def remove(self, it):
		if isinstance(it, dict):
			it = it.keys()
		elif not isinstance(it, (list, tuple, set)):
			it = [it]
		ItemizedSelection.remove(self, it)
		self._updateGraphics()
		chimera.triggers.activateTrigger('selection changed', self)

	def merge(self, method, selection):
		ItemizedSelection.merge(self, method, selection)
		self._updateGraphics()
		chimera.triggers.activateTrigger('selection changed', self)

from chimera import oslParser
class OSLSelection(Selection):
	"""Object Selection Language selection

	OSLSelection(OSL_string) => OSLSelection instance

	Encapsulate an OSL query string into a selection.

	Note: if the OSL-string has a syntax error, then the constructor
	will raise the SyntaxError exception.
	"""
	def __init__(self, oslstr, models=None):
		if hasattr(Selection, '__init__'):
			Selection.__init__(self)
		self.oslStr = oslstr
		self.limitedModelList = models
		# do a parsing, so that SyntaxError gets thrown if OSL
		# string is invalid
		oslParser.Parser(oslstr, None, None, None)

	def __str__(self):
		"""String representation is OSL string"""
		return self.oslStr

	def apply(self, vFunc = None, eFunc = None):
		vList = []
		if vFunc is None:
			myVFunc = None
			mySGFunc = None
		else:
			myVFunc = lambda v, si, ci, mi, l=vList: \
					l.append((si, ci, mi, v))
			# Handle graphs that have children which are
			# vertices instead of subgraphs as in SurfaceModel.
			def mySGFunc(v, si, ci, mi, l=vList):
				if v.oslLevel() == SelVertex:
					l.append((si, ci, mi, v))
		if self.limitedModelList is None:
			models = chimera.openModels.list()
		else:
			models = self.limitedModelList
		oslParser.applyFunctions(self.oslStr, models,
						None, mySGFunc, myVFunc)
		if vFunc and len(vList) > 0:
			vList.sort()
			for si, ci, mi, v in vList:
				vFunc(v)
	
	def barrenGraphs(self, asDict=False):
		"""Graphs that have no child edges/vertices"""

		if asDict:
			bgraphs = {}
			def addBG(g, si, ci, mi, bgs=bgraphs):
				children = g.oslChildren()
				if not children \
				or not children[0].oslChildren():
					bgs[g] = ()
		else:
			bgraphs = []
			def addBG(g, si, ci, mi, bgs=bgraphs):
				children = g.oslChildren()
				if not children \
				or not children[0].oslChildren():
					bgs.append(g)
		oslParser.applyFunctions(self.oslStr, chimera.openModels.list(),
						addBG, None, None)
		return bgraphs

class CodeSelection(Selection):
	"""CodeSelection class

	CodeSelection(code_string, name, descriptin) => CodeSelection instance

	Encapsulate Python code into a selection.  The code has access
	to several local variables:

	models -- : reference to chimera.openModels.
	vFunc -- the function to apply to vertices.
	eFunc -- the function to apply to edges.
	funcs -- a dictionary of all of the [gsve]func's.
	selApply -- a function that applies the right [ve]func to the given object.

	Note: if the code-string is not legal Python code, then the
	constructor will raise a SyntaxError exception.
	"""

	def __init__(self, codestr):
		if hasattr(Selection, '__init__'):
			Selection.__init__(self)
		self.codeObj = compile(codestr, '<string>', "exec")
		self.codeStr = codestr

	def __str__(self):
		"""String representation is code string"""
		return self.codeStr

	def apply(self, vFunc = None, eFunc = None):
		"""Apply given functions to selected objects
		
		selection.apply(vFunc=lambda...) => None

		It is incumbant on the code to follow guarantees that
		the the vertex function is called before the edge
		function.

		Note: many types of exceptions can happen when the code
		is executed.
		"""
		funcGlobals = {
			"__doc__": None,
			"__name__": "CodeSelection",
			"__builtins__": __builtins__
		}
		funcLocals = {
			"models": chimera.openModels.list(),
			"vFunc": vFunc, "eFunc" : eFunc,
			"funcs": {
				SelVertex: vFunc, SelEdge: eFunc
			}
		}
		# helper function, so code can call 'selApply(obj)' without
		# knowing what the selection type of the object is.
		funcLocals["selApply"] = lambda obj, funcs=funcLocals["funcs"]:\
			funcs[obj.oslLevel()](obj)
		try:
			exec self.codeObj in funcGlobals, funcLocals
		except:
			import string
			from chimera import replyobj
			replyobj.pushMode(replyobj.ERROR)
			replyobj.message(str(self.name()) +
						" Code Selection failed\n")
			s = apply(traceback.format_exception,
					sys.exc_info())
			replyobj.message(string.join(s, ''))
			replyobj.popMode()
	
	def barrenGraphs(self, asDict=False):
		if asDict:
			return {}
		return []

_selectionDialog = None
_currentSelection = _CurrentSelection()
emptySelection = ItemizedSelection()

def mergeCurrent(method, selection):
	"""Merge given selection into the current selection
	
	mergeCurrent(method, selection) => None

	method is one of module constants REPLACE, EXTEND, REMOVE, or INTERSECT.
	selection is a instance of a subclass of Selection.
	"""
	_currentSelection.merge(method, selection)

def mergeUsingCurrent(method, selection):
	"""Merge the current selection into the given selection

	mergeWithCurrent(method, selection) => None

	method is one of module constants REPLACE, EXTEND, REMOVE, or INTERSECT.
	selection is a instance of a subclass of Selection.
	"""
	selection.merge(method, _currentSelection)

def setCurrent(selection):
	"""Set current selection to the given selection.
	
	setCurrent(what) => None
	
	selection is a instance of a subclass of Selection, or a list
	of objects, or a single object (object's must have an oslLevel
	function).
	"""
	if selection is _currentSelection:
		return

	if isinstance(selection, CodeSelection):
		# since code may use current selection, get an
		# ItemizedSelection before altering current selection
		replacement = ItemizedSelection()
		replacement.merge(REPLACE, selection)
		mergeCurrent(REPLACE, replacement)
	elif isinstance(selection, Selection):
		mergeCurrent(REPLACE, selection)
	else:
		replacement = ItemizedSelection()
		replacement.add(selection)
		mergeCurrent(REPLACE, replacement)

def addCurrent(items):
	"""add given item or items to current selection"""
	_currentSelection.add(items)

def addImpliedCurrent(vertices=True, edges=True):
	"""add implied vertices and/or edges to current selection

	   An edge is 'implied' if both endpoints are in the selection.
	   A vertex is 'implied' if any of its edges are in the selection.

	   The method is "one pass", so edges between implied vertices
	   won't be added if not already present.
	"""
	_currentSelection.addImplied(vertices=vertices, edges=edges)

def removeCurrent(items):
	"""remove given item or items from current selection"""
	_currentSelection.remove(items)

def clearCurrent():
	"""empty the selection"""
	_currentSelection.clear()

def currentContents(**kw):
	"""Return contents of current selection.

	Takes the same arguments and returns the same values as
	ItemizedSelection.contents()
	"""
	return _currentSelection.contents(**kw)

def currentEdges(**kw):
	"""Return edges in current selection.

	Takes the same arguments and returns the same values as
	ItemizedSelection.edges()
	"""
	return _currentSelection.edges(**kw)

def currentVertices(**kw):
	"""Return vertices in current selection.

	Takes the same arguments and returns the same values as
	ItemizedSelection.vertices()
	"""
	return _currentSelection.vertices(**kw)

def currentGraphs(**kw):
	"""Return graphs in current selection.

	Takes the same arguments and returns the same values as
	ItemizedSelection.graphs()
	"""
	return _currentSelection.graphs(**kw)

def currentBarrenGraphs(**kw):
	"""Return graphs in current selection.

	Takes the same arguments and returns the same values as
	ItemizedSelection.barrenGraphs()
	"""
	return _currentSelection.barrenGraphs(**kw)

def currentSubgraphs(**kw):
	"""Return subgraphs in current selection.

	Takes the same arguments and returns the same values as
	ItemizedSelection.subgraphs()
	"""
	return _currentSelection.subgraphs(**kw)

def currentAtoms(**kw):
	"""Return atoms in current selection.

	Takes the same arguments and returns the same values as
	ItemizedSelection.atoms()
	"""
	return _currentSelection.atoms(**kw)

def currentBonds(**kw):
	"""Return bonds in current selection.

	Takes the same arguments and returns the same values as
	ItemizedSelection.bonds()
	"""
	return _currentSelection.bonds(**kw)

def currentResidues(**kw):
	"""Return residues in current selection.

	Takes the same arguments and returns the same values as
	ItemizedSelection.residues()
	"""
	return _currentSelection.residues(**kw)

def currentChains(**kw):
	"""Return chains in current selection (Sequence objects).

	Takes the same arguments and returns the same values as
	ItemizedSelection.chains()
	"""
	return _currentSelection.chains(**kw)

def currentMolecules(**kw):
	"""Return molecules in current selection.

	Takes the same arguments and returns the same values as
	ItemizedSelection.molecules()
	"""
	return _currentSelection.molecules(**kw)

def currentEmpty():
	"""Return True if current selection is empty."""
	return _currentSelection.empty()

def applyCurrent(vFunc=None, eFunc=None):
	"""Apply functions to current selection at corresponding graph level

	functions are for vertices and edges, respectively,
	and receive a single vertex or edge argument
	"""
	_currentSelection.apply(vFunc, eFunc)

def copyCurrent():
	"""Return a copy of the current selection"""
	import copy
	return copy.copy(_currentSelection)

def toggleInCurrent(objs):
	_currentSelection.toggle(objs)

def invertCurrent(allModels=True):
	orig = copyCurrent()
	if allModels:
		models = chimera.openModels.list()
	else:
		models = currentGraphs()
	clearCurrent()
	addCurrent(models)
	mergeCurrent(REMOVE, orig)

def containedInCurrent(obj):
	return _currentSelection.contains(obj)
