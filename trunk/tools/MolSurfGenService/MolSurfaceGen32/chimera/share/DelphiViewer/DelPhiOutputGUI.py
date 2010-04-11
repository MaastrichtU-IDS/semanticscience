# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
File:           DelPhiOutputGUI.py
Date:           06.19.2000
Description:    Handles the logic and GUI interface for sending DelPhi output
                to Chimera (or output files).

Caveats:

Last modified:  06.19.2000 - Added.
                12.14.2006 - Replaced with opening PHI file in VolumeViewer.
"""

import chimera

def DelPhiOutputGUI(options):
	filename = None
	for name, optionsgroup in options:
		if name != "Output":
			continue
		for group, optionslist in optionsgroup:
			if group != "To a File":
				continue
			for o in optionslist:
				if o.statement == "phi":
					filename = o.var.get()
	if not filename:
		raise SystemError, "Cannot locate name of PHI file"
	else:
		chimera.openModels.open(filename,
					type="DelPhi or GRASP potential")
