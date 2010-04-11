# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Fragment.py 26655 2009-01-07 22:02:30Z gregc $

RING5 = "5-member rings"
RING6 = "6-member rings"
RING65 = "fused 6+5 member rings"
RING66 = "fused 6+6 member rings"
RING665 = "fused 6+6+5 member rings"
RING666 = "fused 6+6+6 member rings"

class Fragment:
	def __init__(self, name, atoms, bonds):
		"""'atoms' should be a list of tuples: (element name, xyz)
		   'bonds' should be a list of tuples: (indices, depict)
		   	'indices' should be a two-tuple into the atom list
			'depict' should be None [single bond], or an xyz
			[center of ring] for a double bond
		"""
		self.name = name
		self.atoms = atoms
		self.bonds = bonds
	
	def depict(self, canvas, scale):
		depictedHydrogens = []
		font = ("Helvetica", "%d" % int(scale-1))
		texts = {}
		for indices, double in self.bonds:
			atoms = [self.atoms[i] for i in indices]
			elements = [a[0] for a in atoms]
			if "H" in elements:
				if "C" not in elements:
					hPlace = elements.index("H")
					depictedHydrogens.append(
						(indices[hPlace],
						indices[1-hPlace])
					)
				continue
			canvas.create_line(*tkCoords(atoms, scale=scale))

			if double:
				doubleBond = []
				for a in atoms:
					for i in range(2):
						doubleBond.append(scale *
							(0.8*a[1][i] +
							0.2*double[i]))
				canvas.create_line(*tkCoords(doubleBond))
		for a in self.atoms:
			element = a[0]
			if element in "HC" or a in texts:
				continue
			textKw = { 'anchor': "center", 'text': element,
						'font': font }
			txt = canvas.create_text(*tkCoords([a], scale=scale),
								**textKw)
			texts[a] = txt
			bkg = canvas['bg']
			kw = {'fill': bkg, 'outline': bkg}
			txtBkg = canvas.create_rectangle(*canvas.bbox(txt),
									**kw)
			canvas.tag_raise(txt, txtBkg)

		for hi, oi in depictedHydrogens:
			textKw = { 'text': 'H', 'font': font }
			h = self.atoms[hi]
			o = self.atoms[oi]
			xdiff = o[1][0] - h[1][0]
			ydiff = o[1][1] - h[1][1]
			bbox = canvas.bbox(texts[o])
			if abs(xdiff) > abs(ydiff):
				if xdiff < 0:
					# H to the right
					textKw['anchor'] = 'w'
					x = bbox[2]
				else:
					textKw['anchor'] = 'e'
					x = bbox[0]
				y = (bbox[1] + bbox[3]) / 2.0
			else:
				x = (bbox[0] + bbox[2]) / 2.0
				if ydiff < 0:
					# H is above
					textKw['anchor'] = 's'
					y = bbox[1]
				else:
					textKw['anchor'] = 'n'
					y = bbox[3]
			canvas.create_text(x, y, **textKw)

			
def tkCoords(source, scale=None):
	coords = []
	if scale == None:
		for i in range(0, len(source), 2):
			coords.append(source[i])
			coords.append(0 - source[i+1])
	else:
		for a in source:
			coords.append(scale * a[1][0])
			coords.append(0 - scale * a[1][1])
	return tuple(coords)

fragDict = {}
from fragments import infos
for info in infos:
	curDict = fragDict
	for cat in info[:-1]:
		curDict = curDict.setdefault(cat, {})
	curDict[info[-1].name] = info[-1]

def collate(info):
	output = []
	keys = info.keys()
	keys.sort()
	for k in keys:
		v = info[k]
		if type(v) == dict:
			output.append([k, collate(v)])
		else:
			output.append(v)
	return output
fragments = collate(fragDict)
