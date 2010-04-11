# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
VRML output module:

    A VRML scene graph is a directed acyclic graph (DAG) of nodes.  The
    nodes and their fields are documented in:
    <http://www.web3d.org/x3d/specifications/vrml/ISO_IEC_14772-All/index.html>.
    Each VRML node is a represented by a Python class of the same name
    (only those that are implemented).  The VRML field names are Python
    attribute names and can be given as keyword arguments to the various
    node constructors.  VRML eventIn fields are used as Python method
    names (when provided).

    Typically use consists of (1) creating a Group or Transform node as
    the root node of the VRML DAG and then using the addChildren method
    to add child nodes, and (2) calling vrml(root_node) to get the text
    version of the VRML DAG, and (3) writing that text to a file.
"""

try:
        from cStringIO import StringIO
except ImportError:
        from StringIO import StringIO

Indent = '    '

def vrml(node):
	"""node -> str

	Convert a VRML DAG to its text representation.
	"""
	out = StringIO()
	out.write('#VRML V2.0 utf8\n')
	if not hasattr(node, '__iter__'):
		node.writeNode(out)
	else:
		for n in node:
			n.writeNode(out)
	return out.getvalue()

class _Node:
	def __init__(self, **kw):
		for k, v in kw.items():
			setattr(self, k, v)

	def writeAttribute(self, f, prefix, attr, fmt):
		try:
			value = getattr(self, attr)
		except AttributeError:
			return
		f.write(prefix)
		f.write(fmt % value)
		f.write('\n')

	def writeBooleanAttribute(self, f, prefix, attr, fmt):
		try:
			value = getattr(self, attr)
		except AttributeError:
			return
		if value:
			bvalue = 'TRUE'
		else:
			bvalue = 'FALSE'
		f.write(prefix)
		f.write(fmt % bvalue)
		f.write('\n')

	def writeAppearance(self, f, prefix):
		if hasattr(self, 'color') \
		or hasattr(self, 'emissiveColor') \
		or hasattr(self, 'transparency') \
		or hasattr(self, 'ambientIntensity'):
			f.write('%s%sappearance Appearance {\n'
					% (prefix, Indent))
			f.write('%s%s%smaterial Material {\n'
					% (prefix, Indent, Indent))
			p = prefix + Indent + Indent + Indent
			self.writeAttribute(f, p, 'color',
						'diffuseColor %g %g %g')
			self.writeAttribute(f, p, 'emissiveColor',
						'emissiveColor %g %g %g')
			self.writeAttribute(f, p, 'specularColor',
						'specularColor %g %g %g')
			self.writeAttribute(f, p, 'shininess',
						'shininess %g')
			self.writeAttribute(f, p, 'transparency',
						'transparency %g')
			self.writeAttribute(f, p, 'ambientIntensity',
						'ambientIntensity %g')
			f.write('%s%s%s}\n' % (prefix, Indent, Indent))
			f.write('%s%s}\n' % (prefix, Indent))

	def addChildren(self, c):
		self.children.append(c)
	addChild = addChildren		# backwards compatibility

	def writeChildren(self, f, prefix):
		if not self.children:
			return
		f.write('%schildren [\n' % prefix)
		p = prefix + Indent
		for c in self.children:
			c.writeNode(f, prefix=p)
		f.write('%s]\n' % prefix)

class Group(_Node):
	def __init__(self, **kw):
		self.children = []
		_Node.__init__(self, **kw)

	def writeNode(self, f, prefix=''):
		f.write('%sGroup {\n' % prefix)
		p = prefix + Indent
		self.writeAttribute(f, p, 'bboxCenter', 'bboxCenter %g %g %g')
		self.writeAttribute(f, p, 'bboxSize', 'bboxSize %g %g %g')
		self.writeChildren(f, p)
		f.write('%s}\n' % prefix)

class Transform(_Node):
	def __init__(self, **kw):
		self.children = []
		_Node.__init__(self, **kw)

	def writeNode(self, f, prefix=''):
		f.write('%sTransform {\n' % prefix)
		p = prefix + Indent
		self.writeAttribute(f, p, 'center', 'center %g %g %g')
		self.writeAttribute(f, p, 'scaleOrientation',
					'scaleOrientation %g %g %g  %g')
		self.writeAttribute(f, p, 'scale', 'scale %g %g %g')
		self.writeAttribute(f, p, 'rotation', 'rotation %g %g %g  %g')
		self.writeAttribute(f, p, 'translation', 'translation %g %g %g')
		self.writeAttribute(f, p, 'bboxCenter', 'bboxCenter %g %g %g')
		self.writeAttribute(f, p, 'bboxSize', 'bboxSize %g %g %g')
		self.writeChildren(f, p)
		f.write('%s}\n' % prefix)

class Sphere(_Node):
	def writeNode(self, f, prefix=''):
		f.write('%sShape {\n' % prefix)
		self.writeAppearance(f, prefix)
		f.write('%s%sgeometry Sphere {\n' % (prefix, Indent))
		p = prefix + Indent + Indent
		self.writeAttribute(f, p, 'radius', 'radius %g')
		f.write('%s%s}\n' % (prefix, Indent))
		f.write('%s}\n' % prefix)

class Box(_Node):
	def writeNode(self, f, prefix=''):
		f.write('%sShape {\n' % prefix)
		self.writeAppearance(f, prefix)
		f.write('%s%sgeometry Box {\n' % (prefix, Indent))
		p = prefix + Indent + Indent
		self.writeAttribute(f, p, 'size', 'size %g %g %g')
		f.write('%s%s}\n' % (prefix, Indent))
		f.write('%s}\n' % prefix)

class Cylinder(_Node):
	def writeNode(self, f, prefix=''):
		f.write('%sShape {\n' % prefix)
		self.writeAppearance(f, prefix)
		f.write('%s%sgeometry Cylinder {\n' % (prefix, Indent))
		p = prefix + Indent + Indent
		self.writeAttribute(f, p, 'radius', 'radius %g')
		self.writeAttribute(f, p, 'height', 'height %g')
		self.writeBooleanAttribute(f, p, 'bottom', 'bottom %s')
		self.writeBooleanAttribute(f, p, 'top', 'top %s')
		self.writeBooleanAttribute(f, p, 'side', 'side %s')
		f.write('%s%s}\n' % (prefix, Indent))
		f.write('%s}\n' % prefix)

class HalfCylinder(Cylinder):
	def writeNode(self, f, prefix=''):
		f.write('%sTransform {\n' % prefix)
		p = prefix + Indent
		f.write('%sscale 1 0.5 1\n' % p)
		f.write('%stranslation 0 1 0\n' % p)
		f.write('%schildren [\n' % p)
		Cylinder.writeNode(self, f, p + Indent)
		f.write('%s]\n' % p)
		f.write('%s}\n' % prefix)

class Cone(_Node):
	def writeNode(self, f, prefix=''):
		f.write('%sShape {\n' % prefix)
		self.writeAppearance(f, prefix)
		f.write('%s%sgeometry Cone {\n' % (prefix, Indent))
		p = prefix + Indent + Indent
		self.writeAttribute(f, p, 'bottomRadius', 'bottomRadius %g')
		self.writeAttribute(f, p, 'height', 'height %g')
		self.writeBooleanAttribute(f, p, 'bottom', 'bottom %s')
		self.writeBooleanAttribute(f, p, 'side', 'side %s')
		f.write('%s%s}\n' % (prefix, Indent))
		f.write('%s}\n' % prefix)

class HalfCone(Cone):
	def __init__(self, **kw):
		self.height = 2.0
		Cone.__init__(self, **kw)

	def writeNode(self, f, prefix=''):
		f.write('%sTransform {\n' % prefix)
		p = prefix + Indent
		f.write('%stranslation 0 %g 0\n' % (p, self.height / 2.0))
		f.write('%schildren [\n' % p)
		Cone.writeNode(self, f, p + Indent)
		f.write('%s]\n' % p)
		f.write('%s}\n' % prefix)

class Lines(_Node):
	# use addLine()
	# colorPerVertex defaults True
	def __init__(self, **kw):
		self.coords = []
		self.colors = []
		_Node.__init__(self, **kw)

	def writeNode(self, f, prefix=''):
		f.write('%sShape {\n' % prefix)
		self.writeAppearance(f, prefix)
		f.write('%s%sgeometry IndexedLineSet {\n' % (prefix, Indent))
		p = prefix + Indent + Indent
		self.writeBooleanAttribute(f, p, 'colorPerVertex',
							'colorPerVertex %s')
		self.writeCoords(f, p)
		self.writeColors(f, p)
		f.write('%s%s}\n' % (prefix, Indent))
		f.write('%s}\n' % prefix)

	def addLine(self, coords, color):
		if not isinstance(coords, list):
			raise ValueError, 'expecting an array of coordinates'
		self.coords.append(coords)
		self.colors.append(color)

	def writeCoords(self, f, prefix):
		if not self.coords:
			return
		f.write(prefix)
		f.write('coord Coordinate { point [\n')
		p = prefix + Indent
		coordList = []
		for cList in self.coords:
			for c in cList:
				coordList.append('%g %g %g' % c)
		if coordList:
			f.write(p)
			f.write((',\n' + p).join(coordList))
			f.write('\n')
		f.write(prefix)
		f.write('] }\n')
		f.write(prefix)
		f.write('coordIndex [\n')
		indexList = []
		n = 0
		for cList in self.coords:
			iList = []
			for c in cList:
				iList.append('%d' % n)
				n = n + 1
			indexList.append(' '.join(iList))
		if indexList:
			f.write(p)
			f.write((' -1\n' + p).join(indexList))
			f.write('\n')
		f.write(prefix)
		f.write(']\n')

	def writeColors(self, f, prefix):
		if not self.colors:
			return
		f.write(prefix)
		f.write('color Color { color [\n')
		p = prefix + Indent
		colorList = []
		for color in self.colors:
			colorList.append('%g %g %g' % color)
		if colorList:
			f.write(p)
			f.write((',\n' + p).join(colorList))
			f.write('\n')
		f.write(prefix)
		f.write('] }\n')
		f.write(prefix)
		f.write('colorIndex [\n')
		indexList = []
		n = 0
		for color in self.colors:
			indexList.append('%d' % n)
			n = n + 1
		if indexList:
			f.write(p)
			f.write(('\n' + p).join(indexList))
			f.write('\n')
		f.write(prefix)
		f.write(']\n')
		f.write(prefix)
		f.write('colorPerVertex FALSE\n')

class Faces(_Node):
	# use addFace()
	# ccw defaults True
	# convex defaults True
	# solid defaults True
	# colorPerVertex defaults True
	# normalPerVertex defaults True
	def __init__(self, **kw):
		self.coords = []
		self.colors = []
		self.normals = []
		_Node.__init__(self, **kw)

	def writeNode(self, f, prefix=''):
		f.write('%sShape {\n' % prefix)
		self.writeAppearance(f, prefix)
		f.write('%s%sgeometry IndexedFaceSet {\n' % (prefix, Indent))
		p = prefix + Indent + Indent
		self.writeBooleanAttribute(f, p, 'ccw', 'ccw %s')
		self.writeBooleanAttribute(f, p, 'convex', 'convex %s')
		self.writeBooleanAttribute(f, p, 'solid', 'solid %s')
		self.writeAttribute(f, p, 'creaseAngle', 'creaseAngle %g')
		#TODO: self.writeNormals(f, p)
		self.writeCoords(f, p)
		self.writeBooleanAttribute(f, p, 'normalPerVertex',
							'normalPerVertex %s')
		self.writeColors(f, p)
		self.writeBooleanAttribute(f, p, 'colorPerVertex',
							'colorPerVertex %s')
		f.write('%s%s}\n' % (prefix, Indent))
		f.write('%s}\n' % prefix)

	def addFace(self, coords, color=None):
		if not isinstance(coords, list):
			raise ValueError, 'expecting an array of coordinates'
		self.coords.append(coords)
		if hasattr(self, 'colorPerVertex'):
			if self.colorPerVertex:
				# color should be sequence of 3-tuples
				assert(hasattr(color, '__len__') \
					and hasattr(color[0], '__len__') \
					and len(coords) == len(color))
			else:
				assert(not color or not hasattr(color[0], '__len__'))
		else:
			if color and hasattr(color[0], '__len__'):
				assert(len(coords) == len(color))
				self.colorPerVertex = True
			else:
				self.colorPerVertex = False
		if color:
			self.colors.append(color)

	def writeCoords(self, f, prefix):
		if not self.coords:
			return
		f.write(prefix)
		f.write('coord Coordinate { point [\n')
		p = prefix + Indent
		coordList = []
		for cList in self.coords:
			for c in cList:
				coordList.append('%g %g %g' % c)
		if coordList:
			f.write(p)
			f.write((',\n' + p).join(coordList))
			f.write('\n')
		f.write(prefix)
		f.write('] }\n')
		f.write(prefix)
		f.write('coordIndex [\n')
		indexList = []
		n = 0
		for cList in self.coords:
			iList = []
			for c in cList:
				iList.append('%d' % n)
				n = n + 1
			indexList.append(' '.join(iList))
		if indexList:
			f.write(p)
			f.write((' -1\n' + p).join(indexList))
			f.write('\n')
		f.write(prefix)
		f.write(']\n')

	def writeColors(self, f, prefix):
		if not self.colors:
			return
		f.write(prefix)
		f.write('color Color { color [\n')
		p = prefix + Indent
		colorList = []
		if not hasattr(self, 'colorPerVertex') or self.colorPerVertex:
			for colors in self.colors:
				for color in colors:
					colorList.append('%g %g %g' % color)
		else:
			for color in self.colors:
				colorList.append('%g %g %g' % color)
		if colorList:
			f.write(p)
			f.write((',\n' + p).join(colorList))
			f.write('\n')
		f.write(prefix)
		f.write('] }\n')
		#f.write(prefix)
		#f.write('colorIndex [\n')
		#indexList = []
		#n = 0
		#for color in self.colors:
		#	indexList.append('%d' % n)
		#	n = n + 1
		#if indexList:
		#	f.write(p)
		#	f.write(('\n' + p).join(indexList))
		#	f.write('\n')
		#f.write(prefix)
		#f.write(']\n')

class Extrusion(_Node):
	def writeNode(self, f, prefix=''):
		f.write('%sShape {\n' % prefix)
		p1 = prefix + Indent
		p2 = p1 + Indent
		p3 = p2 + Indent
		self.writeAppearance(f, prefix)
		f.write('%sgeometry NurbsSurface {\n' % p1)
		self.writeBooleanAttribute(f, p2, 'solid', 'solid %s')
		self.writeBooleanAttribute(f, p2, 'ccw', 'ccw %s')
		f.write('%scontrolPoint [\n' % p2)
		vCount = len(self.edges) + 2
		uCount = len(self.edges[0])
		for v in range(vCount):
			edge = self.edges[v % len(self.edges)]
			for u in range(uCount):
				coord = edge[u]
				f.write('%s%g %g %g,\n'
					% (p3, coord[0], coord[1], coord[2]))
		f.write('%s]\n' % p2)		# end point
		f.write('%suDimension %d\n' % (p2, uCount))
		f.write('%svDimension %d\n' % (p2, vCount))
		f.write('%suKnot [\n' % p2)
		f.write('%s0, 0, 0,' % p3)
		for u in range(uCount - 2):
			f.write(' %d,' % u)
		f.write(' %d, %d, %d\n' % (uCount - 3, uCount - 3, uCount - 3))
		f.write('%s]\n' % p2)		# end uKnotVector
		f.write('%svKnot [\n' % p2)
		f.write('%s0,' % p3)
		for v in range(vCount):
			f.write(' %d,' % v)
		f.write(' %d,\n' % (vCount - 1))
		f.write('%s]\n' % p2)		# end vKnotVector
		f.write('%s}\n' % p1)		# end geometry
		f.write('%s}\n' % prefix)	# end Shape
