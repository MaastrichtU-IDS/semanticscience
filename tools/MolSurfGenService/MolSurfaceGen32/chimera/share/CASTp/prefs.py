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

SHOWN_COLS = "incomplete side chains"
DO_SELECT = "select pocket atoms"
DO_COLOR = "color pocket atoms"
POCKET_COLOR = "pocket color"
NONPOCKET_COLOR = "non-pocket color"
DO_SURFACE = "surface pocket atoms"
DO_ZOOM = "zoom on pocket"
EXCLUDE_MOUTH = "exclude mouth"

defaults = {
	SHOWN_COLS: [ "ID", "# openings", "mouth MS area",
		"MS circumference sum", "pocket MS area", "MS volume" ],
	DO_SELECT: True,
	DO_COLOR: False,
	POCKET_COLOR: 'orange',
	NONPOCKET_COLOR: None,
	DO_SURFACE: True,
	DO_ZOOM: False,
	EXCLUDE_MOUTH: False
}

# so the defaults above can be used elsewhere, send a copy of the dictionary...
prefs = preferences.addCategory("CASTp", preferences.HiddenCategory,
						optDict=defaults.copy())
