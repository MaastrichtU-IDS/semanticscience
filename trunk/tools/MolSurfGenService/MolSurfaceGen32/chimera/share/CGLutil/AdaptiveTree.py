# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

""" AdaptiveTree.py: Define AdaptiveTree class to simplify 3D space
	partitioning (though class is not limited to three dimensions).
	Defines an 'adaptive k-d tree' as per Friedman, Bentley, and
	Finkel and as described in "The Design and Analysis of Spatial
	Data Structures", H. Samet (1989), pp. 70-71.
"""
from numpy import array, object_
from operator import add

leaf = intern('leaf')
interior = intern('interior')

class AdaptiveTree:
	"""Define an 'adaptive k-d tree' as per "The Design and Analysis of
		Spatial Data Structures" pp. 70-71.  Basically, given a set
		of k-dimensional points (each dimension referred to as an
		"attribute") with associated data, they are partitioned into
		leaf nodes.  Each leaf nodes hold lists of associated data
		whose corresponding attributes vary by less than an initially-
		supplied threshold ('sepVal').  Also, each leaf node holds a
		bounding box of the leaf data.
		
		The interior nodes of the tree contain details of the
		partitioning.  In particular, what attribute this node
		partitions along ('axis'), and what value ('median')
		partitions left child node from right child node.  Whether
		a node is interior or leaf is stored in 'type'.
	"""

	def __init__(self, attributeData, leafData, sepVal):
		"""attributeData is a sequence of sequences.  Each individual
		   sequence is attribute data.  For example, in a 3D space 
		   partitioning, the attribute data is x, y, and z values.

		   leafData ia a sequence of the same length as attributeData.
		   Each item is what is to put into leaf nodes after tree
		   partitioning.

		   sepVal is the value at which a tree will no longer be
		   decomposed, i.e. if the maximum variance of each attribute
		   is less than sepVal, then a leaf node is created."""

		if attributeData:
			attrData = array(attributeData)
			leafData = array(leafData, object_)
			self.root = Node(attrData, leafData, sepVal)
		else:
			self.root = None

	def searchTree(self, target, window, zero=0.0):
		"""Search tree for all leaves within 'window' of target.

		The cumulative difference of all attributes from target must
		be less than 'window'.

		Note that this search only identifies leaf nodes that could
		satisfy the window criteria and returns all leaf data in
		those nodes.  Each individual leaf data may not satisfy the
		window criteria.

		For attributes that aren't floats or ints but that otherwise
		obey numeric operations and comparisons, the 'zero' parameter
		may be specified so that the searches know how to initialize
		their difference totals.
		"""

		if not self.root:
			return []
		return _searchNode(self.root, target, window * window,
						[zero]*len(target), zero)

	def bboxSearchTree(self, bbox):
		"""Search tree for all leaves within a bounding box.

		Mostly similar to 'searchTree'.  'bbox' is a sequence of
		lower-bound / upper-bound pairs defining the bounds on
		each axis.
		"""

		if not self.root:
			return []
		leaves = []
		_bboxSearchNode(self.root, bbox, leaves)
		return leaves

class Node:
	def __init__(self, attrData, leafData, sepVal):
		if len(attrData) < 2:
			# leaf node
			self._makeLeaf(leafData, attrData)
			return

		maxVar = -1
		lastIndex = len(attrData) - 1
		for axis in range(len(attrData[0])):
			axisData = attrData[:,axis]
			sort = axisData.argsort()
			var = axisData[sort[lastIndex]] - axisData[sort[0]]
			if var < sepVal:
				continue

			# want axis that varies most from the median rather
			# than the one that varies most from end to end
			median = (axisData[sort[lastIndex/2]] +
					axisData[sort[1+lastIndex/2]]) / 2.0
			var1 = median - axisData[sort[0]]
			var2 = axisData[sort[lastIndex]] - median
			if var1 > var2:
				var = var1
			else:
				var = var2
			if var > maxVar:
				maxVar = var
				maxAxis = axis
				maxSort = sort
				maxAxisData = axisData
				# there can be freak cases where the median
				# is the same as an end value (e.g. [a a b]),
				# so we need to tweak the median in these
				# cases so that the left and right nodes both
				# receive data
				if axisData[sort[0]] == median:
					for ad in axisData[sort]:
						if ad > median:
							median = (median +
								ad) / 2.0
							break
				elif axisData[sort[-1]] == median:
					for ad in axisData[sort[-1::-1]]:
						if ad < median:
							median = (median +
								ad) / 2.0
							break
				maxMedian = median
		
		if maxVar < 0:
			# leafNode
			self._makeLeaf(leafData, attrData)
			return
		
		self.type = interior
		self.axis = maxAxis
		self.median = maxMedian

		# less than median goes into left node, greater-than-or-
		# equal-to goes into right node
		leftIndex = 0
		for index in range(lastIndex/2, -1, -1):
			if maxAxisData[maxSort[index]] < maxMedian:
				leftIndex = index + 1
				break
		self.left = Node(attrData.take(maxSort[:leftIndex], 0),
				leafData.take(maxSort[:leftIndex], 0), sepVal)
		self.right = Node(attrData.take(maxSort[leftIndex:], 0),
				leafData.take(maxSort[leftIndex:], 0), sepVal)
	
	def _makeLeaf(self, leafData, attrData):
		self.type = leaf
		if isinstance(leafData, list):
			self.leafData = leafData
		else:
			self.leafData = leafData.tolist()
		self.bbox = []
		lastIndex = len(attrData) - 1
		for axis in range(len(attrData[0])):
			axisData = attrData[:,axis]
			sort = axisData.argsort()
			self.bbox.append(([axisData[sort[0]],
						axisData[sort[lastIndex]]]))
def _searchNode(node, target, windowSq, diffsSq, zero):
	if node.type == leaf:
		diffSqSum = zero
		for axis in range(len(target)):
			min, max = node.bbox[axis]
			targetVal = target[axis]
			if targetVal < min:
				diff = min - targetVal
				diffSqSum = diffSqSum + diff * diff
			elif targetVal > max:
				diff = targetVal - max
				diffSqSum = diffSqSum + diff * diff
			if diffSqSum > windowSq:
				return []
		return node.leafData
	
	# interior
	targetVal = target[node.axis]
	diffSqSum = reduce(add, diffsSq)
	diffSqSum = diffSqSum - diffsSq[node.axis]
	remainingWindowSq = windowSq - diffSqSum
	
	if targetVal < node.median:
		leaves = _searchNode(node.left, target, windowSq, diffsSq, zero)
		diff = node.median - targetVal
		diffSq = diff * diff
		if diffSq <= remainingWindowSq:
			prevDiffSq = diffsSq[node.axis]
			diffsSq[node.axis] = diffSq
			leaves = leaves + _searchNode(node.right, target,
							windowSq, diffsSq, zero)
			diffsSq[node.axis] = prevDiffSq
	else:
		leaves = _searchNode(node.right, target, windowSq, diffsSq,
									zero)
		diff = targetVal - node.median
		diffSq = diff * diff
		if diffSq <= remainingWindowSq:
			prevDiffSq = diffsSq[node.axis]
			diffsSq[node.axis] = diffSq
			leaves = leaves + _searchNode(node.left, target,
							windowSq, diffsSq, zero)
			diffsSq[node.axis] = prevDiffSq
	return leaves

def _bboxSearchNode(node, bbox, leafList):
	if node.type == leaf:
		for axis in range(len(bbox)):
			nmin, nmax = node.bbox[axis]
			bbmin, bbmax = bbox[axis]
			if nmin > bbmax or nmax < bbmin:
				return
		for datum in node.leafData:
			leafList.append(datum)
		return
	
	# interior node
	bbmin, bbmax = bbox[node.axis]
	if bbmin < node.median:
		_bboxSearchNode(node.left, bbox, leafList)
	if bbmax >= node.median:
		_bboxSearchNode(node.right, bbox, leafList)
