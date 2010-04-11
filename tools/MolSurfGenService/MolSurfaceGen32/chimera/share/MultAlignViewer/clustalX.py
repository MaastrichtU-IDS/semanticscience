# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: clustalX.py 26655 2009-01-07 22:02:30Z gregc $

from CGLtk.color import rgba2tk
_clustalRed     = rgba2tk((0.9, 0.2, 0.1))
_clustalBlue    = rgba2tk((0.1, 0.5, 0.9))
_clustalGreen   = rgba2tk((0.1, 0.8, 0.1))
_clustalCyan    = rgba2tk((0.1, 0.7, 0.7))
_clustalPink    = rgba2tk((0.9, 0.5, 0.5))
_clustalMagenta = rgba2tk((0.8, 0.3, 0.8))
#_clustalYellow  = rgba2tk((0.8, 0.8, 0.0))
# above is very hard to see on the gray background, so...
_clustalYellow  = rgba2tk((0.69, 0.69, 0.0))
_clustalOrange  = rgba2tk((0.9, 0.6, 0.3))
_clustalCategories = [("wlvimafcyhp", 0.6, '%'),
		("wlvimafcyhp", 0.8, '#'), ("ed", 0.5, '-'),
		("kr", 0.6, "+"), ("g", 0.5, 'g'), ("n", 0.5, 'n'),
		("qe", 0.5, 'q'), ("p", 0.5, 'p'), ("ts", 0.5, 't')]
for c in "acdefghiklmnpqrstvwy":
	_clustalCategories.append((c, 0.85, c.upper()))
_clustalColorings = {
	'G': [(_clustalOrange, None)],
	'P': [(_clustalYellow, None)],
	'T': [(_clustalGreen, "tST%#")],
	'S': [(_clustalGreen, "tST#")],
	'N': [(_clustalGreen, "nND")],
	'Q': [(_clustalGreen, "qQE+KR")],
	'W': [(_clustalBlue, "%#ACFHILMVWYPp")],
	'L': [(_clustalBlue, "%#ACFHILMVWYPp")],
	'V': [(_clustalBlue, "%#ACFHILMVWYPp")],
	'I': [(_clustalBlue, "%#ACFHILMVWYPp")],
	'M': [(_clustalBlue, "%#ACFHILMVWYPp")],
	'A': [(_clustalBlue, "%#ACFHILMVWYPpTSsG")],
	'F': [(_clustalBlue, "%#ACFHILMVWYPp")],
	'C': [(_clustalBlue, "%#AFHILMVWYSPp"), (_clustalPink, "C")],
	'H': [(_clustalCyan, "%#ACFHILMVWYPp")],
	'Y': [(_clustalCyan, "%#ACFHILMVWYPp")],
	'E': [(_clustalMagenta, "-DEqQ")],
	'D': [(_clustalMagenta, "-DEnN")],
	'K': [(_clustalRed, "+KRQ")],
	'R': [(_clustalRed, "+KRQ")]
}

def clustalInfo(fileName=None):
	if fileName is None:
		return _clustalCategories, _clustalColorings

	from prefs import RC_HYDROPHOBICITY
	if fileName == RC_HYDROPHOBICITY:
		import os.path
		fileName = os.path.join(os.path.dirname(__file__),
							"kdHydrophob.par")
	colorInfo = {}
	for colorName in [ "RED", "BLUE", "GREEN", "CYAN",
					"PINK", "MAGENTA", "YELLOW", "ORANGE"]:
		colorInfo[colorName] = eval("_clustal%s"
						% colorName.capitalize())
	from OpenSave import osOpen
	from chimera import UserError
	f = osOpen(fileName)
	section = None
	colorSeen = False
	categories = []
	colorings = {}
	for line in f:
		line = line.strip()
		if line.startswith("@"):
			section = line[1:].lower()
			continue
		if not line:
			continue
		if section == "rgbindex":
			try:
				name, sr, sg, sb = line.split()
			except ValueError:
				raise UserError("Line in @rgbindex section of"
					" %s is not color name followed by"
					" red, green and blue values: '%s'"
					% (fileName, line))
			try:
				r, g, b = [float(x) for x in [sr, sg, sb]]
			except ValueError:
				raise UserError("Line in @rgbindex section of"
					" %s has non-floating-point"
					" red, green or blue value: '%s'"
					% (fileName, line))
			if r>1 or g>1 or b>1 or r<0 or g<0 or b<0:
				raise UserError("Line in @rgbindex section of"
					" %s has red, green or blue value"
					" not in the range 0-1: '%s'"
					% (fileName, line))
			colorInfo[name] = rgba2tk((r, g, b))
		elif section == "consensus":
			try:
				symbol, eq, percent, composition = line.split()
			except ValueError:
				raise UserError("Line in @consensus section of"
					" %s is not of the form 'symbol = "
					" percentage%% res-list: '%s'"
					% (fileName, line))
			if eq != '=':
				raise UserError("Line in @consensus section of"
					" %s doesn't have '=' as second"
					" component: '%s'" % (fileName, line))
			if percent[-1] != '%':
				raise UserError("Line in @consensus section of"
					" %s doesn't have '%' as last character"
					" of third component: '%s'"
					% (fileName, line))
			try:
				percentage = float(percent[:-1])
			except ValueError:
				raise UserError("Line in @consensus section of"
					" %s doesn't have a number before the"
					" '%' of third component: '%s'"
					% (fileName, line))
			if percentage < 0 or percentage > 100:
				raise UserError("Line in @consensus section of"
					" %s has a percentage not in the range"
					" 0-100: '%s'" % (fileName, line))
			composition = composition.replace(":", "")
			categories.append((composition, percentage/100.0,
								symbol))
		elif section == "color":
			colorSeen = True
			fields = line.split()
			if len(fields) not in [3,5]:
				raise UserError("Line in @color section of"
					" %s not of the form AA = color"
					" [if consensus-list]: '%s'"
					% (fileName, line))
			aa, eq, color = fields[:3]
			if len(aa) > 1 or not aa.islower():
				raise UserError("Line in @color section of"
					" %s uses amino-acid code that is not"
					" a single lowercase character: '%s'"
					% (fileName, line))
			if eq != '=':
				raise UserError("Line in @color section of"
					" %s doesn't have '=' as second"
					" component: '%s'" % (fileName, line))
			if color not in colorInfo:
				raise UserError("Line in @color section of"
					" %s uses an unknown color:"
					" '%s'" % (fileName, line))
			if len(fields) == 3:
				colorings.setdefault(aa.upper(), []).append(
						(colorInfo[color], None))
				continue
			if fields[3] != 'if':
				raise UserError("Line in @color section of"
					" %s doesn't have 'if' as fourth"
					" component: '%s'" % (fileName, line))
			colorings.setdefault(aa.upper(), []).append(
				(colorInfo[color], fields[-1].replace(":", "")))
	f.close()
	if not colorSeen:
		raise UserError("'%s' has missing or empty @color section"
								% fileName)
	return categories, colorings

from OpenSave import OpenModeless
class ColorSchemeDialog(OpenModeless):
	"""Dialog to open ClustalX-style coloring file"""

	title = "Load Residue-Letter Color Scheme"

	def __init__(self, mav):
		self.mav = mav
		OpenModeless.__init__(self, clientPos='s',
						historyID="MAV residue colors")

	def fillInUI(self, parent):
		OpenModeless.fillInUI(self, parent)
		import Tkinter
		self.defaultVar = Tkinter.IntVar(parent)
		self.defaultVar.set(True)
		Tkinter.Checkbutton(self.clientArea, variable=self.defaultVar,
			text="Make this scheme the default").grid()

	def destroy(self):
		self.mav = None
		from chimera.baseDialog import ModelessDialog
		ModelessDialog.destroy(self)

	def Apply(self):
		if not self.getPaths():
			from chimera import replyobj
			replyobj.error("No coloring file specified.\n")
			self.enter()
			return
		self.mav.useColoringFile(self.getPaths()[0],
					makeDefault=self.defaultVar.get())
