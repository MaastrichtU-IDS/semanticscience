# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import sys
import operator

import chimera
from chimera.colorTable import getColorByName

defaultColors = ['blue', 'cyan', 'green', 'yellow', 'red']
_rainbowColors = {}

def rainbowTexture(colors):
	key = tuple(colors)
	if key not in _rainbowColors:
		actualColors = []
		for color in colors:
			if isinstance(color, basestring):
				c = getColorByName(color)
			elif isinstance(color, chimera.MaterialColor):
				c = color
			else:
				c = chimera.MaterialColor()
				c.ambientDiffuse =  color[:3]
				if len(color) > 3:
					c.opacity = color[-1]
				else:
					c.opacity = 1.0
			actualColors.append(c)
		_rainbowColors[key] = RainbowColors(actualColors)
	return _rainbowColors[key]

def rainbowModels(models, changeAt='residues', colors=defaultColors):
	"""rainbow-color given models

	   'changeAt' (which is either 'residues', 'chains', or 'models')
	   specifies where colors change.

	   'colors' is a list of colors to run through in the rainbow.
	   The default colors run through yellow and cyan in order to
	   get full saturation.
	"""

	if changeAt == 'residues':
		for m in models:
			for rng in _getResidueRanges(m):
				_rainbowRange(rainbowTexture(colors), rng)
		return
	if changeAt == 'models':
		sortable = map(lambda m: (m.oslIdent(), m), models)
		from chimera.misc import oslModelCmp
		sortable.sort(oslModelCmp)
		ranges = [[[m] for osl, m in sortable]]
	else:
		ranges = []
		for m in models:
			ranges.extend(_getChainRanges(m))

	for rng in ranges:
		_rainbowRange(rainbowTexture(colors), rng)
	#if changeAt == 'models':
	#	for m in models:
	#		m.color = m.residues[0].atoms[0].color

def _getResidueRanges(m):
	try:
		residues = m.residues
	except AttributeError:
		return []

	ranges = []
	start = 0
	prev = None
	n = -1
	for r in residues:
		n = n + 1
		if prev is None:
			start = n
			prev = r
		elif chimera.bondsBetween(prev, r, 1):
			# connected to previous residue, just track prev
			prev = r
		else:
			# not connected
			ranges.append(residues[start:n])
			start = n
			prev = r
	if n > start:
		ranges.append(residues[start:n+1])
	return ranges

def _getChainRanges(m):
	if not isinstance(m, chimera.Molecule):
		return []
	return [[x.residues for x in m.sequences()]]

def _getSubmodelRanges(models):
	return [m.residues for m in models]

def _rainbowRange(rainbow, rng):
	if not rng:
		return
	isChain = isinstance(rng[0], list)
	if len(rng) == 1 and not isChain:
		# don't color stand-alone residues
		r = rng[0]
		atoms = r.oslChildren()
		if len(atoms) == 0:
			return
		a = atoms[0]
		if a.molecule.rootForAtom(a, 1).size.numAtoms <= len(atoms):
			return
	maxIndex = float(len(rng) - 0.99)
	for n in range(len(rng)):
		if len(rng) == 1:
			coord = 0.5
		else:
			coord = 0.0001 + 0.9998 * (n / float(len(rng)-1))
		c = rainbow.color(coord)
		if isChain:
			residues = rng[n]
			if isinstance(residues[0], chimera.Molecule):
				m = residues[0]
				m.color = c
				for r in m.residues:
					r.ribbonColor = None
					r.labelColor = None
					for a in r.oslChildren():
						a.color = None
						a.surfaceColor = None
						a.labelColor = None
						a.vdwColor = None
				continue
		else:
			residues = [rng[n]]
		for r in residues:
			if not r:
				continue
			r.ribbonColor = c
			r.labelColor = c
			for a in r.oslChildren():
				a.color = c
				a.surfaceColor = c
				a.labelColor = c
				a.vdwColor = c

class RainbowColors:
	def __init__(self, colors):
		self.colors = colors

	def color(self, coord):
		place = coord * (len(self.colors) - 1)
		leftIndex = int(place)
		if leftIndex == place:
			return self.colors[leftIndex]
		c = chimera.MaterialColor()
		c1, c2 = self.colors[leftIndex:leftIndex+2]
		f = place - leftIndex
		c.ambientDiffuse = tuple(map(lambda a,b: a*(1-f) + b*f,
					c1.ambientDiffuse, c2.ambientDiffuse))
		c.opacity = c1.opacity * (1-f) + c2.opacity * f
		return c
