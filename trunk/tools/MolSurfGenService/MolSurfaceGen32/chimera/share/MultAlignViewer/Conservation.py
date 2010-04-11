# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Conservation.py 27358 2009-04-21 00:32:47Z pett $

"""Find consensus sequences"""

from HeaderSequence import DynamicHeaderSequence
from chimera.Sequence import clustalStrongGroups, clustalWeakGroups
import string
from prefs import CONSERVATION_STYLE, \
		CSV_AL2CO, CSV_PERCENT, CSV_CLUSTAL_HIST, CSV_CLUSTAL_CHARS, \
		AL2CO_FREQ, AL2CO_CONS, AL2CO_WINDOW, AL2CO_GAP, AL2CO_MATRIX, \
		AL2CO_TRANSFORM

class Conservation(DynamicHeaderSequence):
	name = "Conservation"
	sortVal = 1.7
	def alignChange(self, left, right):
		if self.mav.prefs[CONSERVATION_STYLE] == CSV_AL2CO:
			self.reevaluate()
		else:
			DynamicHeaderSequence.alignChange(self, left, right)
	
	def evaluate(self, pos):
		if self.mav.prefs[CONSERVATION_STYLE] == CSV_PERCENT:
			return self.percentIdentity(pos)
		if self.mav.prefs[CONSERVATION_STYLE] == CSV_CLUSTAL_HIST:
			values = [0.0, 0.33, 0.67, 1.0]
		else:
			values = [' ', '.', ':', '*']
		return values[self.clustalType(pos)]

	def fastUpdate(self):
		return self.mav.prefs[CONSERVATION_STYLE] != CSV_AL2CO

	def reevaluate(self):
		style = self.mav.prefs[CONSERVATION_STYLE]
		if style == CSV_AL2CO:
			self.depictionVal = self.histInfinity
		elif style == CSV_PERCENT:
			self.depictionVal = self._histPercent
		else:
			if hasattr(self, 'depictionVal'):
				delattr(self, 'depictionVal')
		if style != CSV_AL2CO:
			return DynamicHeaderSequence.reevaluate(self)
		self[:] = []
		from formatters.saveALN import save, extension
		from tempfile import mkstemp
		tfHandle, tfName = mkstemp(extension)
		import os
		os.close(tfHandle)
		tf = open(tfName, "w")
		save(tf, None, self.mav.seqs, None)
		tf.close()
		import os, os.path
		chimeraRoot = os.environ.get("CHIMERA")
		command =  [ os.path.join(chimeraRoot, 'bin', 'al2co'),
				"-i", tfName,
				"-f", str(self.mav.prefs[AL2CO_FREQ]),
				"-c", str(self.mav.prefs[AL2CO_CONS]),
				"-w", str(self.mav.prefs[AL2CO_WINDOW]),
				"-g", str(self.mav.prefs[AL2CO_GAP]) ]
		if self.mav.prefs[AL2CO_CONS] == 2:
			command += ["-m", str(self.mav.prefs[AL2CO_TRANSFORM])]
			matrix = self.mav.prefs[AL2CO_MATRIX]
			from SmithWaterman import matrixFiles
			if matrix in matrixFiles:
				command += [ "-s", matrixFiles[matrix] ]
		from subprocess import Popen, PIPE, STDOUT
		alOut = Popen(command, stdin=PIPE, stdout=PIPE, stderr=STDOUT).stdout
		for line in alOut:
			if len(self) == len(self.mav.seqs[0]):
				break
			line = line.strip()
			if line.endswith("zero"):
				# variance is zero
				continue
			if line.endswith("position"):
				# one or fewer columns have values
				self[:] = [0.0] * len(self.mav.seqs[0])
				delattr(self, 'depictionVal')
				break
			if line[-1] == "*":
				self.append(None)
				continue
			self.append(float(line.split()[-1]))
		os.unlink(tfName)
		if len(self) != len(self.mav.seqs[0]):
			# failure, possibly due to no variance in alignment
			self[:] = [1.0] * len(self.mav.seqs[0])
			self.histogramFunc = None
	
	def colorFunc(self, seq, offset):
		return self.mav.prefs[CONSERVATION_STYLE] == CSV_CLUSTAL_CHARS \
				and 'black' or 'dark gray'

	def percentIdentity(self, pos, forHistogram=False):
		"""actually returns a fraction"""
		occur = {}
		for i in range(len(self.mav.seqs)):
			let = self.mav.seqs[i][pos]
			try:
				occur[let] += 1
			except KeyError:
				occur[let] = 1
		best = 0
		for let, num in occur.items():
			if let not in string.letters:
				continue
			if num > best:
				best = num
		if best == 0:
			return 0.0
		if forHistogram:
			return (best - 1) / (float(len(self.mav.seqs)) - 1)
		return best / float(len(self.mav.seqs))

	def clustalType(self, pos):
		conserve = None
		for i in range(len(self.mav.seqs)):
			char = self.mav.seqs[i][pos].upper()
			if conserve is None:
				conserve = char
				continue
			if char != conserve:
				break
		else:
			return 3

		for group in clustalStrongGroups:
			for i in range(len(self.mav.seqs)):
				char = self.mav.seqs[i][pos].upper()
				if char not in group:
					break
			else:
				return 2

		for group in clustalWeakGroups:
			for i in range(len(self.mav.seqs)):
				char = self.mav.seqs[i][pos].upper()
				if char not in group:
					break
			else:
				return 1

		return 0

	def _histPercent(self, pos):
		return self.percentIdentity(pos, forHistogram=True)
