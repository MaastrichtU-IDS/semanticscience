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

SCRIPT_PYTHON = "Python"
SCRIPT_CHIMERA = "Chimera commands"

SCRIPT_TYPE = "script type"
DICT_NAME = "substitution dictionary name"
FRAME_TEXT = "frame # substitution text"
ZERO_PAD = "zero pad frame numbers"

RMSD_MIN = "rmsd min"
RMSD_MAX = "rmsd max"
RMSD_AUTOCOLOR = "rmsd autocolor"

VOLUME_CUTOFF = "volume cutoff"
VOLUME_RESOLUTION = "volume resolution"

RECORDER_FORMAT = "animation format"
RECORDER_RECORD_ARGS = "record args"
RECORDER_ENCODE_ARGS = "encode args"
RECORDER_SUPERSAMPLE = "supersample"
RECORDER_SAMPLES = "samples"
RECORDER_ROUNDTRIP = "roundtrip"
RECORDER_RAYTRACE = "raytrace"

options = {
	SCRIPT_TYPE: SCRIPT_PYTHON,
	DICT_NAME: "mdInfo",
	FRAME_TEXT: "<FRAME>",
	ZERO_PAD: True,
	RMSD_MIN: 0.5,
	RMSD_MAX: 3.0,
	RMSD_AUTOCOLOR: True,
	VOLUME_CUTOFF: 10.0,
	VOLUME_RESOLUTION: 1.0,
	RECORDER_FORMAT: -1,
	RECORDER_RECORD_ARGS: "",
	RECORDER_ENCODE_ARGS: "",
	RECORDER_SUPERSAMPLE: True,
	RECORDER_SAMPLES: 3,
	RECORDER_ROUNDTRIP: False,
	RECORDER_RAYTRACE: False
}
prefs = preferences.addCategory("MD Movie", preferences.HiddenCategory,
							optDict=options)
