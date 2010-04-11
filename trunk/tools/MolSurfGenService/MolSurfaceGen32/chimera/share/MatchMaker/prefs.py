# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: prefs.py 27959 2009-06-30 18:28:22Z pett $

from MatchMaker import CP_BEST, SA_NEEDLEMAN_WUNSCH

CHAIN_PAIRING = "chain pairing"
SEQUENCE_ALGORITHM = "sequence algorithm"
SHOW_SEQUENCE = "show sequence"
MATRIX = "matrix"
GAP_OPEN = "gap open penalty"
GAP_EXTEND = "gap extend penalty"
USE_SS = "guide with secondary structure"
SS_MIXTURE = "similarity/SS mixture"
SS_SCORES = "SS matrix values"
ITERATE = "iterate matching"
ITER_CUTOFF = "iteration cutoff"
HELIX_OPEN = "helix gap open penalty"
STRAND_OPEN = "strand gap open penalty"
OTHER_OPEN = "non-helix/strand gap open penalty"
COMPUTE_SS = "compute secondary structure"

from chimera.preferences import addCategory, HiddenCategory
defaults = {
	CHAIN_PAIRING: CP_BEST,
	SEQUENCE_ALGORITHM: SA_NEEDLEMAN_WUNSCH,
	SHOW_SEQUENCE: False,
	MATRIX: "BLOSUM-62",
	GAP_OPEN: 12,
	GAP_EXTEND: 1,
	USE_SS: True,
	SS_MIXTURE: 0.3,
	SS_SCORES: {
		('H', 'H'): 6,
		('S', 'S'): 6,
		('O', 'O'): 4,
		('S', 'H'): -9,
		('H', 'S'): -9,
		('S', 'O'): -6,
		('O', 'S'): -6,
		('H', 'O'): -6,
		('O', 'H'): -6
	},
	ITERATE: True,
	ITER_CUTOFF: 2.0,
	HELIX_OPEN: 18,
	STRAND_OPEN: 18,
	OTHER_OPEN: 6,
	COMPUTE_SS: True,
}
from copy import deepcopy
prefs = addCategory("MatchMaker", HiddenCategory, optDict=deepcopy(defaults))
