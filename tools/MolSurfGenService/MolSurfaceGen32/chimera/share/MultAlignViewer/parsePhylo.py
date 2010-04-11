# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: parsePhylo.py 29149 2009-10-26 23:16:01Z pett $

class PhyloNode:
	def __init__(self):
		self.subNodes = []
		self.label = None
		self.length = None

	def assignedIndices(self):
		if self.subNodes:
			assignments = []
			for n in self.subNodes:
				assignments.extend(n.assignedIndices())
			return assignments
		return [self.seqIndex]

	def assignSeqIndices(self, seqs, assignments=None):
		if assignments is None:
			assignments = {}
		if self.subNodes:
			indices = []
			consecutive = True
			for n in self.subNodes:
				subconsecutive, subIndices = n.assignSeqIndices(
							seqs, assignments)
				consecutive = consecutive and subconsecutive
				indices.extend(subIndices)
			if consecutive:
				indices.sort()
				if indices[-1] - indices[0] != len(indices) - 1:
					consecutive = False
			return consecutive, indices
		thisAssign = [i for i, s in enumerate(seqs)
			if self.label.lower().strip() == s.name
					.replace('_', ' ').lower().strip()]
		from chimera import UserError
		if not thisAssign:
			raise UserError("No sequence name matches tree node"
				" name '%s'" % self.label)
		if len(thisAssign) > 1:
			raise UserError("Tree node '%s' matches multiple"
				" sequences" % self.label)
		assignment = thisAssign[0]
		if assignment in assignments:
			raise UserError("Sequence '%s' matches multiple tree"
					" nodes: '%s' and '%s'" % (
					seqs[assignment].name, self.label,
					assignments[assignment].label))
		assignments[assignment] = self
		self.seqIndex = assignment
		return True, [self.seqIndex]
				
	def assignXdeltas(self):
		byXPos = {}
		nodes = [self]
		while nodes:
			node = nodes.pop()
			if not node.subNodes:
				node.xDelta = 0
				continue
			nodes.extend(node.subNodes)
			xPosNodes = byXPos.setdefault(node.xPos, {})
			delta = 0
			conflict = True
			while conflict:
				conflict = False
				deltaNodes = xPosNodes.setdefault(delta, [])
				for dnode in deltaNodes:
					nys = [n.yPos for n in node.subNodes]
					dnys = [n.yPos for n in dnode.subNodes]
					if max(nys) > min(dnys) \
					or min(nys) < max(dnys):
						conflict = True
						if delta > 0:
							delta = 0 - delta
						else:
							delta = 1 - delta
						break
			deltaNodes.append(node)
			node.xDelta = delta

	def assignXpositions(self, branchStyle="even", curX=0.0,
							maxLength=None):
		if branchStyle == "even":
			self.xPos = curX
			for n in self.subNodes:
				subdepth = n.depth()
				baseX = curX + (1.0 - curX) / subdepth
				n.assignXpositions(branchStyle, curX=baseX)
		elif branchStyle == "weighted":
			if maxLength is None:
				ml = self.maxLength()
				if ml:
					self.assignXpositions(branchStyle,
							curX=curX, maxLength=ml)
				else:
					self.assignXpositions("even",
								curX=curX)
				return
			self.xPos = curX
			for n in self.subNodes:
				baseX = curX + n.length / maxLength
				n.assignXpositions(branchStyle, curX=baseX,
							maxLength=maxLength)
		else:
			raise ValueError("Unknown/unimplemented branch style: "
								+ branchStyle)

	def assignYpositions(self):
		if self.subNodes:
			subMax = subMin = None
			for n in self.subNodes:
				subPos = n.assignYpositions()
				if subMax is None or subPos > subMax:
					subMax = subPos
				if subMin is None or subPos < subMin:
					subMin = subPos
			self.yPos = (subMax + subMin) / 2.0
		else:
			self.yPos = float(self.seqIndex)
		return self.yPos

	def countNodes(self, nodeType=None):
		if nodeType == "leaf" and self.subNodes \
		or nodeType == "interior" and not self.subNodes:
			count = 0
		else:
			count = 1
		for node in self.subNodes:
			count += node.countNodes(nodeType)
		return count

	def depth(self):
		depth = 1
		for sn in self.subNodes:
			subdepth = sn.depth()
			if subdepth+1 > depth:
				depth = subdepth+1
		return depth

	def freshCopy(self):
		copyNode = PhyloNode()
		copyNode.subNodes = [n.freshCopy() for n in self.subNodes]
		copyNode.label = self.label
		copyNode.length = self.length
		return copyNode
		
	def maxLength(self):
		if not self.subNodes:
			return 0.0
		ml = 0.0
		for n in self.subNodes:
			if n.length == None:
				return None
			sml = n.maxLength()
			if sml is None:
				return None
			if n.length + sml > ml:
				ml = n.length + sml
		return ml

	def __str__(self):
		if self.subNodes:
			val = '(' + ",".join([str(sn) for sn in self.subNodes]) + ')'
		else:
			val = ""
		if self.label is not None:
			val += self.label.replace(' ', '_')
		if self.length is not None:
			val += ":%g" % self.length
		return val

class NewickTree(PhyloNode):
	def __init__(self, text, numberingsStripped=False):
		self.numberingsStripped = numberingsStripped
		PhyloNode.__init__(self)
		root, text = self._interiorNode(text, node=self)
		text = self._removeComment(text).strip()
		if not text.startswith(';'):
			raise SyntaxError("No ending ';'")
		if text != ';':
			raise SyntaxError("Extraneous text after ending ';'")
	
	def __str__(self):
		return "%s;" % PhyloNode.__str__(self)

	def _interiorNode(self, text, node=None):
		text = self._removeComment(text)
		if not text or text[0] != '(':
			raise SyntaxError(
				"Interior node expected but no '(' found")
		if node is None:
			node = PhyloNode()
		text = self._removeComment(text[1:])
		while text:
			if text[0] == '(':
				subNode, text = self._interiorNode(text)
			elif text[0] == ')':
				text = text[1:]
				break
			elif text[0] == ',':
				text = self._removeComment(text[1:])
				continue
			else:
				subNode, text = self._leafNode(text)
			node.subNodes.append(subNode)
		if not text:
			raise SyntaxError("No ending ')' for interior node")
		if not node.subNodes:
			raise SyntaxError("No contents for interior node")
		node.label, text = self._findLabel(text)
		node.length, text = self._findLength(text)
		return node, text
	
	def _findLabel(self, text):
		text = self._removeComment(text)
		if not text:
			return None, text
		label = ""
		if text[0] == "'":
			quote = False
			for i, c in enumerate(text[1:]):
				if quote:
					if c == "'":
						label += "'"
						quote = False
					else:
						break
				else:
					if c == "'":
						quote = True
					else:
						label += c
			if not quote:
				raise SyntaxError("No ending single quote for"
							" quoted label")
			# the enumeration goes into text[1:], which would
			# normally mean you want i+2 into text, but since
			# the enumeration checks the character past the quote...
			return label, text[i+1:]
		for c in text:
			if c in " ()[]':;,":
				break
			if c == '_':
				label += " "
			else:
				label += c
		if not label:
			return None, text
		return label, text[len(label):]
				
	def _findLength(self, text):
		text = self._removeComment(text)
		if not text or text[0] != ":":
			return None, text
		numText = ""
		for c in text[1:]:
			if not c.isdigit() and c not in "+-.":
				break
			numText += c
		try:
			if '.' in numText:
				val = float(numText)
			else:
				val = int(numText)
		except ValueError:
			raise SyntaxError("Non-numeric branch length: %s"
								% numText)
		return val, text[1+len(numText):]

	def _leafNode(self, text):
		node = PhyloNode()
		node.label, text = self._findLabel(self._removeComment(text))
		if node.label is None:
			raise SyntaxError("Label missing for leaf node")
		if self.numberingsStripped:
			node.label = node.label[:node.label.rindex('/')]
		node.length, text = self._findLength(text)
		return node, text

	def _removeComment(self, text):
		text = text.lstrip()
		if text[0] == '[':
			# PAUP allows nested comments
			numStart = 0
			end = None
			for i, c in enumerate(text):
				if c == ']':
					numStart -= 1
					if numStart == 0:
						end = i
						break
				elif c == '[':
					numStart += 1
			if end is None:
				raise SyntaxError("No ']' to end comment")
			return text[end+1:].lstrip()
		return text

def parseNewick(lines, numberingsStripped=False):
	trees = []
	text = ""
	for line in lines:
		line = line.strip()
		if ';' in line:
			front, back = line.split(';', 1)
			text += front
			if text:
				trees.append(NewickTree(text+';',
					numberingsStripped=numberingsStripped))
			text = back
		else:
			text += line
	if not trees:
		raise SyntaxError("No trees found")
	if text:
		raise SyntaxError("Extra text at end of file")
	return trees

from OpenSave import OpenModeless
class PhylogenyDialog(OpenModeless):
	"""Dialog to open phylogeny file"""

	title = "Load Newick Phylogeny"

	def __init__(self, mav):
		self.mav = mav
		OpenModeless.__init__(self, historyID="MAV phylogeny")

	def destroy(self):
		self.mav = None
		from chimera.baseDialog import ModelessDialog
		ModelessDialog.destroy(self)

	def Apply(self):
		if not self.getPaths():
			from chimera import replyobj
			replyobj.error("No phylogeny file specified.\n")
			self.enter()
			return
		self.mav.usePhylogenyFile(self.getPaths()[0])
