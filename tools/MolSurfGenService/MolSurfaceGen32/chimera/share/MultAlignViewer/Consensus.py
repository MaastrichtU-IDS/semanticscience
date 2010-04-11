# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: Consensus.py 27358 2009-04-21 00:32:47Z pett $

"""Find consensus sequences"""

from HeaderSequence import DynamicHeaderSequence
import string
from prefs import CONSENSUS_STYLE, CSN_MAJ_GAP, CSN_MAJ_NOGAP

class Consensus(DynamicHeaderSequence):
	name = "Consensus"
	sortVal = 1.3
	def __init__(self, mav, capitalizeAt=0.8):
		self.capitalizeAt = capitalizeAt
		self.conserved = [0] * len(mav.seqs[0])
		DynamicHeaderSequence.__init__(self, mav)

	def evaluate(self, pos):
		occur = {}
		for i in range(len(self.mav.seqs)):
			let = self.mav.seqs[i][pos]
			if self.mav.prefs[CONSENSUS_STYLE] == CSN_MAJ_NOGAP \
			and let not in string.letters:
				continue
			try:
				occur[let] += 1
			except KeyError:
				occur[let] = 1
		best = (0, None)
		for let, num in occur.items():
			if num > best[0]:
				best = (num, let)
			elif num == best[0] and let not in string.letters:
				# "gappy" characters win ties
				best = (num, let)
		num, let = best
		self.conserved[pos] = 0
		if let is None:
			return ' '
		if num / float(len(self.mav.seqs)) >= self.capitalizeAt:
			retlet = let.upper()
			if num == len(self.mav.seqs):
				self.conserved[pos] = 1
		else:
			retlet = let.lower()
		return retlet

	def reevaluate(self):
		"""sequences changed, possibly including length"""
		self.conserved = [0] * len(self.mav.seqs[0])
		DynamicHeaderSequence.reevaluate(self)
