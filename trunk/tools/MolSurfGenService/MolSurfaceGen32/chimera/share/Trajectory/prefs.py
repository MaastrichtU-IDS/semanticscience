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

FORMAT = "format"
INPUT_FILES = "input files"
GROMOS_SCALING = "Gromos coord scaling"
PDB_STYLE = "PDB input scheme"

options = {
	FORMAT: 'Amber',
	INPUT_FILES: {},
	GROMOS_SCALING: 10.0,
	PDB_STYLE: "multiple files"
}

prefs = preferences.addCategory("Trajectory",
				preferences.HiddenCategory,
				optDict=options)
