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

SHOWN_COLS = "shown columns"

colAttr = {
	"Template PDB":		( "TEMPLATE PDB", "%s" ),
	"Template Chain":	( "TEMPLATE CHAIN", "%s" ),
	"Template Begin":	( "TEMPLATE BEGIN", "%d" ),
	"Template End":		( "TEMPLATE END", "%d" ),
	"Model Score":		( "MODEL SCORE", "%.2f" ),
	"E-value":		( "EVALUE", "%.2e" ),
	"Experiment Type":	( "EXPERIMENT TYPE", "%s" ),
	"Method":		( "METHOD", "%s" ),
	"ModPipe Alignment Id":	( "MODPIPE ALIGNMENT ID", "%s" ),
	"ModPipe Model Id":	( "MODPIPE MODEL ID", "%s" ),
	"ModPipe Run":		( "MODPIPE RUN", "%s" ),
	"Program":		( "PROGRAM", "%s" ),
	"Sequence Identity":	( "SEQUENCE IDENTITY", "%.1f" ),
	"Target Begin":		( "TARGET BEGIN", "%d" ),
	"Target End":		( "TARGET END", "%d" ),
	"Target Length":	( "TARGET LENGTH", "%d" ),
}

attrMap = {
	"MODEL SCORE":		"modbaseModelScore",
	"EVALUE":		"modbaseEvalue",
	"SEQUENCE IDENTITY":	"modbaseSequenceIdentity",
}

colOrder = [
	"Model Score",
	"Sequence Identity",
	"E-value",
	"Template PDB",
	"Template Chain",
	"Template Begin",
	"Template End",
	"Target Length",
	"Target Begin",
	"Target End",
	"ModPipe Run",
	"ModPipe Model Id",
	"ModPipe Alignment Id",
	"Program",
	"Experiment Type",
	"Method",
]

defaults = {
	"Template PDB": True,
	"Model Score": True,
	"E-value": True,
	"Sequence Identity": True,
	"Target Begin": True,
	"Target End": True,
}

# so the defaults above can be used elsewhere, send a copy of the dictionary...
prefs = preferences.addCategory("ModBase", preferences.HiddenCategory,
						optDict=defaults.copy())
