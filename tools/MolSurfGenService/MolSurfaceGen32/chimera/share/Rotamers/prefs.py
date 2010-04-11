# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: prefs.py 26655 2009-01-07 22:02:30Z gregc $

from chimera import preferences
from DetectClash.prefs import CLASH_THRESHOLD, HBOND_ALLOWANCE, PB_COLOR, \
	PB_WIDTH
from DetectClash.prefs import defaults as clashDefaults
from FindHBond.prefs import BOND_COLOR, LINE_WIDTH
from FindHBond.prefs import RELAX_COLOR as FHB_RELAX_COLOR
from FindHBond.prefs import defaults as hbondDefaults

LIBRARY = "rotamer library"
CLASH_METHOD = "clash type"
CLASH_PBS = "show clash pseudobonds"
CLASH_COLOR = "clash pb color"
CLASH_WIDTH = "clash pb width"
HBOND_COLOR = "hbond pb color"
RELAX_COLOR = "hbond pb relaxation color"
HBOND_WIDTH = "hbond pb width"
DRAW_HBONDS = "draw hbonds"
CLASH_IGNORE_OTHERS = "Ignore clashes with other models"
HBOND_IGNORE_OTHERS = "Ignore hbonds with other models"

defaults = {
	LIBRARY: "Dunbrack",
	CLASH_THRESHOLD: clashDefaults[CLASH_THRESHOLD],
	HBOND_ALLOWANCE: clashDefaults[HBOND_ALLOWANCE],
	CLASH_METHOD: "num",
	CLASH_PBS: False,
	CLASH_COLOR: clashDefaults[PB_COLOR],
	CLASH_WIDTH: clashDefaults[PB_WIDTH],
	HBOND_COLOR: hbondDefaults[BOND_COLOR],
	RELAX_COLOR: hbondDefaults[FHB_RELAX_COLOR],
	HBOND_WIDTH: hbondDefaults[LINE_WIDTH],
	DRAW_HBONDS: True,
	CLASH_IGNORE_OTHERS: False,
	HBOND_IGNORE_OTHERS: False
}
# so the defaults above can be used elsewhere, send a copy of the dictionary...
prefs = preferences.addCategory("Rotamers", preferences.HiddenCategory,
						optDict=defaults.copy())
