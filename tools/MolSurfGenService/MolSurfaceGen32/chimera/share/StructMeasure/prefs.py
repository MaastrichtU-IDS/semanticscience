# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: prefs.py 28667 2009-08-26 00:37:07Z pett $

from chimera import preferences

ROT_LABEL = "rot label"
ROT_DIAL_SIZE = "dial size"
ANGLE_PRECISION = "angle precision"
TORSION_PRECISION = "torsion precision"
SHOW_DEGREE_SYMBOL = "show degree symbol"
AXIS_RADIUS = "axis radius"
AXIS_SEL_OBJ = "axis sel obj"
AXIS_SEL_ATOMS = "axis sel atoms"
OBJ_SEL_AXIS = "obj sel axis"
ATOMS_SEL_AXIS = "atoms sel axis"
PLANE_THICKNESS = "plane thickness"

defaults = {
	ROT_LABEL: 'None',
	ROT_DIAL_SIZE: 1,
	ANGLE_PRECISION: 3,
	TORSION_PRECISION: 3,
	SHOW_DEGREE_SYMBOL: True,
	AXIS_RADIUS: 1,
	AXIS_SEL_OBJ: True,
	AXIS_SEL_ATOMS: False,
	OBJ_SEL_AXIS: True,
	ATOMS_SEL_AXIS: False,
	PLANE_THICKNESS: 0.1
}

# so the defaults above can be used elsewhere, send a copy of the dictionary...
prefs = preferences.addCategory("Struct Measure", preferences.HiddenCategory,
						optDict=defaults.copy())
