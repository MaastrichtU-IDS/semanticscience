import sys
from string import *
from math import *

# Utility functions
def getDistance(p1, p2):
	return ( (p2[0] - p1[0])**2 + (p2[1] - p1[1])**2 + (p2[2] - p1[2])**2 ) ** 0.5

def interp(t, a, b):
	c = list(a)
	for i in range(3):
		c[i] += t*(float(b[i]) - float(a[i]))
	return c

def getMidpoint(p1, p2):
	return tuple(interp(0.5, p1, p2))

def getRGBcolor(nCol):
	if nCol == 0: return (1, 1, 1)
	if nCol < 9: return interp( (nCol - 1)/8.0, (0, 1, 0), (0, 1, 1))
	if nCol < 17: return interp( (nCol - 8)/8.0, (0, 1, 1), (0, 0, 1))
	if nCol < 25: return interp( (nCol - 16)/8.0, (0, 0, 1), (1, 0, 1))
	if nCol < 33: return interp( (nCol - 24)/8.0, (1, 0, 1), (1, 0, 0))
	if nCol < 49: return interp( (nCol - 32)/16.0, (1, 0, 0), (1, 1, 0))
	if nCol < 65: return interp( (nCol - 48)/16.0, (1, 1, 0), (0, 0, 0))
	if nCol == 65: return (0.7, 0.7, 0.7)
	return None

def getRGBcolor_byName(sCol):
	from chimera import colorTable
	try:
		c = colorTable.getColorByName(sCol)
		return c.rgba()[:3]
	except KeyError:
		return None

#######################

# Generic object class; used to hold environment data
class Object:
	def __init__(self, **pw):
		for k in pw.keys():
			setattr(self, k, pw[k])

# Generic output object; used to hold output data
class Output:
	def __init__(self):
		self.indentLength = 0
		self.textList = []
	def __lt__(self, line):
		if len(line) < 1:
			self.textList.append('\n')
		else:
			if line[0] == "]" or line[0] == "}":
				self.indentLength -= 1
			self.textList.append(("\t" * self.indentLength) + line)
			if line[-1] == "[" or line[-1] == "{":
				self.indentLength += 1
	def __str__(self):
		return join(self.textList, '\n')

class Environment:
	def __init__(self):
		self.transformStack = []
		self.curLines = None
		self.lineObjs = []
		self.geomObjs = []
		self.polyObjs = []
		self.color = None
		self.transparency = 0
		self.tCoords = (0, 0, 0)
		self.fontSize = 5
		self.fontStyle = "PLAIN"
		self.fontFamily = "TYPEWRITER"

	def handleLine(self, line):
		if len(line) < 2: return
		if line[0] != '.':
			self.handleLine(".text " + line)
			return
		line = split(line[1:])
		if line[0] == "arrow":
			p1 = [float(line[1]), float(line[2]), float(line[3])]
			p2 = [float(line[4]), float(line[5]), float(line[6])]
			if len(line) > 7: r1 = float(line[7])
			else: r1 = 0.1
			if len(line) > 8: r2 = float(line[8])
			else: r2 = 4.0 * r1
			if len(line) > 9: rho = float(line[9])
			else: rho = 0.75

			pJunct = list(interp(rho, p1, p2))
			self.handleLine(".cylinder %f %f %f %f %f %f %f" % tuple(p1 + pJunct + [r1]))
			self.handleLine(".cone %f %f %f %f %f %f %f" % tuple(pJunct + p2 + [r2]))
		elif line[0] == "cmov":
			self.tCoords = (float(line[1]), float(line[2]), float(line[3]))
		elif line[0] == "color":
			if len(line) == 2:
				try:
					color = getRGBcolor(int(line[1]))
				except:
					if line[1].lower() == "none":
						self.color = color = None
					else:
						color = getRGBcolor_byName(
									line[1])
			else:
				try:
					color = (float(line[1]), float(line[2]), float(line[3]))
				except:
					color = getRGBcolor_byName(" ".join(line[1:]))
			if color:
				color = tuple(map(float, color))
				self.color = color
		elif line[0] == "transparency":
			try:
				transparency = float(line[1])
			except:
				transparency = 0
			self.transparency = transparency
		elif line[0] == "box":
			obj = Object(shape = "box")
			p1 = (float(line[1]), float(line[2]), float(line[3]))
			p2 = (float(line[4]), float(line[5]), float(line[6]))
			pCentre = getMidpoint(p1, p2)
			obj.width = p2[0] - p1[0]
			obj.height = p2[1] - p1[1]
			obj.depth = p2[2] - p1[2]
			obj.color = self.color
			obj.transparency = self.transparency
			obj.transforms = self.transformStack[:]
			obj.transforms.append(Object(to=pCentre, form='translate'))
			self.geomObjs.append(obj)
		elif line[0] == "cone":
			obj = Object(shape = "cone")
			p1 = (float(line[1]), float(line[2]), float(line[3]))
			p2 = (float(line[4]), float(line[5]), float(line[6]))
			obj.radius = float(line[7])
			obj.height = getDistance(p1, p2)
			pCentre = getMidpoint(p1, p2)
			if len(line) < 9: obj.closed = True
			elif lower(line[8]) == "open": obj.closed = False
			obj.color = self.color
			obj.transparency = self.transparency
			obj.transforms = self.transformStack[:]
			fTheta = asin( (p2[2] - p1[2]) / obj.height )
			try:
				fPhi = atan2(p2[0] - p1[0], p2[1] - p1[1])
			except ValueError:
				fPhi = 0.0
			obj.transforms.append(Object(to=pCentre, form='translate'))
			obj.transforms.append(Object(angle=-fPhi, axis='z', form='rotate'))
			obj.transforms.append(Object(angle=fTheta, axis='x', form='rotate'))
			self.geomObjs.append(obj)
		elif line[0] == "cylinder":
			obj = Object(shape = "cylinder")
			p1 = (float(line[1]), float(line[2]), float(line[3]))
			p2 = (float(line[4]), float(line[5]), float(line[6]))
			obj.radius = float(line[7])
			obj.height = getDistance(p1, p2)
			pCentre = getMidpoint(p1, p2)
			if len(line) < 9: obj.closed = True
			elif lower(line[8]) == "open": obj.closed = False
			obj.color = self.color
			obj.transparency = self.transparency
			obj.transforms = self.transformStack[:]
			fTheta = asin( (p2[2] - p1[2]) / obj.height )
			try:
				fPhi = atan2(p2[0] - p1[0], p2[1] - p1[1])
			except ValueError:
				fPhi = 0.0
			obj.transforms.append(Object(to=pCentre, form='translate'))
			obj.transforms.append(Object(angle=-fPhi, axis='z', form='rotate'))
			obj.transforms.append(Object(angle=fTheta, axis='x', form='rotate'))
			self.geomObjs.append(obj)
		elif line[0] in ("d", "draw"):
			if self.curLines:

				x, y, z = (float(line[1]), float(line[2]), float(line[3]))
				self.curPosition = (x, y, z)

				self.curLines.vertices.append(self.curPosition)
				self.curLines.vertex_colors.append(self.color)
			else:
				self.handleLine(".move " + join(line[1:]))
		elif line[0] in ("dot", "dotat"):
			self.handleLine(".move " + join(line[1:]))
			self.handleLine(".sphere " + join(line[1:]) + " 1")
		elif line[0] in ("dr", "drawrel"):
			dx, dy, dz = (float(line[1]), float(line[2]), float(line[3]))
			x, y, z = self.curPosition
			self.handleLine(".draw " + join(map(str, (x+dx, y+dy, z+dz))))
		elif line[0] == "font":
			family, size = lower(line[1]), int(line[2])
			if len(line) > 3: style = lower(line[3])
			else: style = "plain"

			self.fontSize = size

			if family[:5] == "times": self.fontFamily = "SERIF"
			elif family == "helvetica": self.fontFamily = "SANS"
			elif family == "courier": self.fontFamily = "TYPEWRITER"
			elif family == "serif": self.fontFamily = "SERIF"
			elif family[:4] == "sans": self.fontFamily = "SANS"
			elif family == "typewriter": self.fontFamily = "TYPEWRITER"
			elif family == "tt": self.fontFamily = "TYPEWRITER"
			else: self.fontFamily = "TYPEWRITER"

			if style == "plain": self.fontStyle = "PLAIN"
			elif style == "bold": self.fontStyle = "BOLD"
			elif style == "italic": self.fontStyle = "ITALIC"
			elif style == "bold italic": self.fontStyle = "BOLD ITALIC"
			else: self.fontStyle = "PLAIN"
		elif line[0] in ("m", "move"):
			self.flush()
			x, y, z = (float(line[1]), float(line[2]), float(line[3]))
			self.curPosition = (x, y, z)
			self.curLines = Object()
			self.curLines.vertices = [self.curPosition]
			self.curLines.vertex_colors = [self.color]
		elif line[0] == "marker":
			self.handleLine(".move " + join(line[1:]))
			x, y, z = float(line[1]), float(line[2]), float(line[3])
			self.handleLine(".box %f %f %f %f %f %f" % (x-0.5, y-0.5, z-0.5, x+0.5, y+0.5, z+0.5))
		elif line[0] == "mr" or line[0] == "moverel":
			dx, dy, dz = (float(line[1]), float(line[2]), float(line[3]))
			x, y, z = self.curPosition
			self.handleLine(".move " + join(map(str, (x+dx, y+dy, z+dz))))
		elif line[0] == "polygon":
			obj = Object(shape = "polygon")
			obj.vertices = []
			for i in range(1, len(line), 3):
				x = float(line[i])
				y = float(line[i + 1])
				z = float(line[i + 2])
				obj.vertices.append( (x, y, z) )
			obj.color = self.color
			obj.transparency = self.transparency
			obj.transforms = self.transformStack[:]
			self.polyObjs.append(obj)
		elif line[0] == "pop":
			self.flush()
			self.transformStack.pop()
		elif line[0] in ("rot", "rotate"):
			self.flush()
			if line[2][0] in 'xyzXYZ':
				obj = Object(form='rotate', axis=lower(line[2][0]), angle=radians(float(line[1])))
			else:
				obj = Object(form='rotate', axis=(float(line[2]), float(line[3]), float(line[4])), angle=radians(float(line[1])))
			self.transformStack.append(obj)
		elif line[0] == "scale":
			self.flush()
			obj = Object(form = 'scale')
			xscale = float(line[1])
			if len(line) > 2:
				yscale = float(line[2])
				zscale = float(line[3])
			else:
				yscale = zscale = xscale
			obj.xscale, obj.yscale, obj.zscale = xscale, yscale, zscale
			self.transformStack.append(obj)
		elif line[0] == "sphere":
			obj = Object(shape = "sphere")
			pCentre = (float(line[1]), float(line[2]), float(line[3]))
			obj.radius = float(line[4])
			obj.color = self.color
			obj.transparency = self.transparency
			obj.transforms = self.transformStack[:]
			obj.transforms.append(Object(to=pCentre, form='translate'))
			self.geomObjs.append(obj)
		elif line[0] == "text":
			obj = Object(shape = "text")
			obj.color = self.color
			obj.transparency = self.transparency
			obj.string = join(line[1:])
			obj.fontSize = self.fontSize
			obj.fontStyle = self.fontStyle
			obj.fontFamily = self.fontFamily
			obj.transforms = self.transformStack[:]
			obj.transforms.append(Object(to=self.tCoords, form='translate'))
			self.geomObjs.append(obj)
		elif line[0] in ("tran", "translate"):
			self.flush()
			tCoords = (float(line[1]), float(line[2]), float(line[3]))
			self.transformStack.append(Object(form='translate', to=tCoords))
		elif line[0] == "v" or line[0] == "vector":
			self.handleLine(".m " + join(line[1:4]))
			self.handleLine(".d " + join(line[4:7]))
		elif line[0] in ("c", "comment"):
			pass
		else:
			raise "Unrecognized Command"

	def flush(self):
		if self.curLines:
			self.curLines.transforms = self.transformStack[:]
			self.lineObjs.append(self.curLines)
			self.curLines = None

	# Finish generating the environment object; called after the last handleLine().
	def finish(self):
		self.flush()

	# Convert from the "environment" object to a VRML output
	def buildVRML(self):
		o = Output()

		o < "#VRML V2.0 utf8"
		for obj in self.lineObjs:
			post = handleTransform(o, obj.transforms)
			o < ""
			o < "Transform {"
			o <  "children ["
			o <   "Shape {"
			o <    "geometry IndexedLineSet {"
			o <     "coord Coordinate {"
			o <      "point ["
			for vertex in obj.vertices:
				o < "%f %f %f," % vertex
			o <         "0 0 0"
			o <      "]"
			o <     "}"
			o <     "coordIndex ["
			o <      join(map(str, range(len(obj.vertices))))
			o <     "]"
			if obj.vertex_colors[0] is not None:
				o <     "color Color {"
				o <      "color ["
				for vcolor in obj.vertex_colors:
					o < "%f %f %f," % vcolor
				o <         "0 0 0"
				o <      "]"
				o <     "}"
				o <     "colorIndex ["
				o <      join(map(str, range(len(obj.vertex_colors))))
				o <     "]"
				o <     "colorPerVertex TRUE"
			o <    "}"
			o <   "}"
			o <  "]"
			o < "}"
			for s in post: o < s

		for obj in self.polyObjs:
			post = handleTransform(o, obj.transforms)
			o < ""
			o < "Transform {"
			o <  "children ["
			o <   "Shape {"
			o <    "appearance Appearance {"
			if obj.color is None:
				o <   'namedColor "__model__"'
			else:
				o <   "material Material {"
				o <    "diffuseColor %f %f %f" % obj.color
				o <    "transparency %f" % obj.transparency
				o <   "}"
			o <    "}"

			o <    "geometry IndexedFaceSet {"
			o <     "coord Coordinate {"
			o <      "point ["
			for vertex in obj.vertices:
				o < "%f %f %f," % vertex
			o <         "0 0 0"
			o <      "]"
			o <     "}"
			o <     "coordIndex ["
			o <      join(map(str, range(len(obj.vertices))))
			o <     "]"
			o <     "color Color {"
			o <      "color ["
			for vertex in obj.vertices:
				o < "%f %f %f," % obj.color
			o <         "0 0 0"
			o <      "]"
			o <     "}"
			o <     "colorIndex ["
			o <      join(map(str, range(len(obj.vertices))))
			o <     "]"
			o <     "solid FALSE"
			o <     "colorPerVertex TRUE"
			o <    "}"
			o <   "}"
			o <  "]"
			o < "}"
			for s in post: o < s

		for obj in self.geomObjs:
			post = handleTransform(o, obj.transforms)
			o < ""
			o < "Shape {"
			o <  "appearance Appearance {"
			if obj.color is None:
				o <   'namedColor "__model__"'
			else:
				o <   "material Material {"
				o <    "diffuseColor %f %f %f" % obj.color
				o <    "transparency %f" % obj.transparency
				o <   "}"
			o <  "}"

			if obj.shape == "sphere":
				o < "geometry Sphere {"
				o <  "radius %f" % obj.radius
				o < "}"
			elif obj.shape == "cylinder":
				o < "geometry Cylinder {"
				o <  "radius %f" % obj.radius
				o <  "height %f" % obj.height
				if not obj.closed:
					o < "top FALSE"
					o < "bottom FALSE"
				o < "}"
			elif obj.shape == "cone":
				o < "geometry Cone {"
				o <  "bottomRadius %f" % obj.radius
				o <  "height %f" % obj.height
				if not obj.closed:
					o < "bottom FALSE"
				o < "}"
			elif obj.shape == "box":
				o < "geometry Box {"
				o <  "size %f %f %f" % (obj.width, obj.height, obj.depth)
				o < "}"
			elif obj.shape == "text":
				o < "geometry Text {"
				o <  "string [ \"%s\" ]" % obj.string
				o <  "fontStyle FontStyle {"
				o <   "size %d" % obj.fontSize
				o <   "family \"%s\"" % obj.fontFamily
				o <   "style \"%s\"" % obj.fontStyle
				o <  "}"
				o < "}"

			o < "}"
			for s in post: o < s

		return str(o)

# Appropriately generate the enclosing Transform blocks from the environment transform stack
# Return the lines that go at the end
def handleTransform(o, tStack):
	if not tStack:
		return []
	else:
		post = handleTransform(o, tStack[:-1])
		trans = tStack[-1]

		o < "Transform {"
		if trans.form == "translate":
			o < "translation %f %f %f" % trans.to
		elif trans.form == "rotate" and isinstance(trans.axis, tuple):
			o < "rotation %f %f %f %f" % (trans.axis + (trans.angle,))
		elif trans.form == "rotate" and trans.axis == 'x':
			o < "rotation 1 0 0 %f" % trans.angle
		elif trans.form == "rotate" and trans.axis == 'y':
			o < "rotation 0 1 0 %f" % trans.angle
		elif trans.form == "rotate" and trans.axis == 'z':
			o < "rotation 0 0 1 %f" % trans.angle
		elif trans.form == "scale":
			o < "scale %f %f %f" % (trans.xscale, trans.yscale, trans.zscale)
		o < "children ["

		post.append(']')
		post.append('}')
		return post

def main():
	env = Environment()
	code = [".color white", ".dot 0 0 0"]
	code += [".color red", ".vector 0 0 0 20 0 0", ".dot 20 0 0"]
	code += [".color green", ".vector 0 0 0 0 20 0", ".dot 0 20 0"]
	code += [".color blue", ".vector 0 0 0 0 0 20", ".dot 0 0 20"]

	code += [".color 44", ".arrow 1 1 1 5 5 5", ".arrow 1 1 2 8 6 9"]
	code += [".arrow 1 2 1 10 10 4", ".arrow 2 1 1 -2 7 10"]
	code += [".color 22", ".polygon 20 0 0 0 20 0 0 0 20"]
	code += [".color 5", ".marker 20 20 20", ".dr -20 0 0"]
	code += [".v 20 20 20 20 0 20", ".dr 0 20 -20"]
	code += [".v 20 20 20 20 20 0", ".dr -20 0 20", ".dr 20 -20 0"]
	code += [".color 12", ".sphere 10 10 10 3"]
	code += [".color 10", ".arrow 19 19 19 12 12 12 0.2 1.0"]

	code += [".color 53", ".cylinder 14 -5 14 14 0 14 2 open"]
	code += [".sphere 14 -5 14 2", ".sphere 14 0 14 2"]

	for line in code:
		try:
			env.handleLine(line)
		except:
			sys.stderr.write("ERROR: \"%s\" raised an %s:\n\t\"%s\"\n" % (line, str(sys.exc_type), str(sys.exc_value)))

	env.finish()
	print env.buildVRML()

if __name__ == "__main__":
	main()
