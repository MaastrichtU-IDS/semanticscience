# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: prefs.py 29678 2009-12-23 21:26:15Z pett $

from chimera import preferences
from Rotamers.prefs import defaults as rotamerDefaults
from Rotamers.prefs import LIBRARY as ROTAMER_LIBRARY

INCOMPLETE_SC = "incomplete side chains"
MEMORIZED_SETTINGS = "memorized settings"

defaults = {
	INCOMPLETE_SC: rotamerDefaults[ROTAMER_LIBRARY],
	MEMORIZED_SETTINGS: {}
}
# so the defaults above can be used elsewhere, send a copy of the dictionary...
prefs = preferences.addCategory("DockPrep", preferences.HiddenCategory,
						optDict=defaults.copy())
