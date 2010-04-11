# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: prefs.py 26899 2009-02-13 01:19:04Z pett $

from chimera import preferences

DIST_CUTOFF = "distance cutoff"
CIRCULAR = "circular permutation"
ANYALL = "match type"
GAPCHAR = "gap character"
ITERATE = "iterate"
ITER_CONVERGE = "iter until convergence"
ITER_AMOUNT = "iter amount"
ITER_ALL_COLS = "iter all columns"
ITER_CONSECUTIVE_COLS = "iter stretch"

defaults = {
	DIST_CUTOFF: 5.0,
	CIRCULAR: False,
	ANYALL: "any",
	GAPCHAR: ".",
	ITERATE: False,
	ITER_CONVERGE: False,
	ITER_AMOUNT: 3,
	ITER_ALL_COLS: False,
	ITER_CONSECUTIVE_COLS: 3
}
prefs = preferences.addCategory("StructSeqAlign", preferences.HiddenCategory,
						optDict=defaults.copy())
