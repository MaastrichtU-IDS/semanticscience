# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: base.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera import selection, replyobj
from chimera.colorTable import colors, getColorByName

Wire = chimera.Bond.Wire
Stick = chimera.Bond.Stick

def readPBinfo(fileName, category=None, clearCategory=1, lineWidth=None,
		drawMode=None, leftModel=None, rightModel=None, defColor=None):
	"""read a file containing pseudobond info and display those bonds

	   'category' defaults to 'fileName'.  'clearCategory' controls
	   whether the pseudobond group should be cleared of pre-existing
	   pseudobonds before reading the file.  'lineWidth' is a floating-
	   point number and controls the width of lines used to draw the
	   pseudobonds.  This only is relevant if 'drawMode' is Wire.
	   'drawMode' controls the depiction style of the pseudobonds.
	   Possible modes are:

	   	Wire (aka chimera.Bond_Wire) -- wireframe
		Stick (aka chimera.Bond_Stick) -- sticks
	
	   'leftModel' and 'rightModel' control what models the endpoints
	   of the pseudobond lie in, if none are specified in the input file.
	   'defColor' is the color assigned to the pseudobond group as a whole,
	   which can be overridden by specific pseudobonds.
	"""
	foundErrors = False
	colorCache = {}

	if not category:
		category = fileName
	
	group = chimera.misc.getPseudoBondGroup(category)
	if lineWidth:
		group.lineWidth = lineWidth
	if drawMode:
		group.drawMode = drawMode

	if clearCategory:
		group.deleteAll()
	
	if defColor:
		if isinstance(defColor, basestring):
			c = chimera.Color.lookup(defColor)
			if not c:
				replyobj.message(
					"Cannot find color '%s'\n" % defColor)
				foundErrors = True
		else:
			c = defColor
		group.color = c

	from OpenSave import osOpen
	bondFile = osOpen(fileName)
	lineNum = 0
	for line in bondFile.readlines():
		line = line.strip()
		lineNum = lineNum + 1

		if not line:
			# blank line
			continue
		
		try:
			spec1, spec2, color = line.split(None, 2)
		except:
			label = color = None
			try:
				spec1, spec2 = line.split()
			except ValueError:
				replyobj.message("Line %d does not have at"
					" least two atom specifiers.")
				foundErrors = True
				continue
		if color:
			# try to distinguish between color name and label
			try:
				color, label = color.split(None, 1)
			except:
				label = None
			if color[0] != "#":
				while (label and not colors.has_key(color)):
					try:
						c, label = label.split(None, 1)
					except:
						color = " ".join([color, label])
						label = None
					else:
						color = " ".join([color, c])
						
		atom1 = _processSpec(spec1, leftModel)
		if not atom1:
			replyobj.message(
				"Left atom spec of line %d of file doesn't"
						" select exactly one atom."
						"  Skipping.\n" % lineNum)
			foundErrors = True
			continue

		atom2 = _processSpec(spec2, leftModel)
		if not atom2:
			replyobj.message(
				"Right atom spec of line %d of file doesn't"
						" select exactly one atom."
						"  Skipping.\n" % lineNum)
			foundErrors = True
			continue

		if color:
			if color[0] == '#':
				fieldLen = int((len(color) - 1) / 3)
				if 3 * fieldLen + 1 != len(color):
					replyobj.message("Bad Tk color '%s'"
						" on line %d of file.\n"
						% (color, lineNum))
					foundErrors = True
				elif colorCache.has_key(color):
					color = colorCache[color]
				else:
					r = color[1:1+fieldLen]
					g = color[1+fieldLen:1+2*fieldLen]
					b = color[1+2*fieldLen:]
					r = int(r, 16)
					g = int(g, 16)
					b = int(b, 16)
					maxVal = int('f' * fieldLen, 16)
					maxVal = float(maxVal)
					c = chimera.MaterialColor(r/maxVal,
							g/maxVal, b/maxVal)
					colorCache[color] = c
					color = c
			else:
				try:
					color = getColorByName(color)
				except KeyError:
					replyobj.message(
						"Unknown color '%s' on line %d"
						" of file.\n" % (color,lineNum))
					foundErrors = True
					color = None
		
		pb = group.newPseudoBond(atom1, atom2)
		if color:
			pb.color = color
		if label:
			pb.label = label
	bondFile.close()

	if foundErrors:
		chimera.replyobj.error(
				"Errors encountered while reading file.\n"
				"Check reply log for details.\n")


def _processSpec(spec, defModel):
	if spec[0] not in "#:@":
		spec = ":" + spec
	sel = selection.OSLSelection(spec)
	atoms = sel.atoms()
	if len(atoms) == 1:
		return atoms[0]
	if defModel and spec[0] != "#":
		spec = "#" + defModel + spec
		sel = selection.OSLSelection(spec)
		atoms = sel.atoms()
		if len(atoms) == 1:
			return atoms[0]
	return None
