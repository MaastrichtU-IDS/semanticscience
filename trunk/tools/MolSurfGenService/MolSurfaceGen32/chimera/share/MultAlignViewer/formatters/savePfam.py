# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: savePfam.py 26655 2009-01-07 22:02:30Z gregc $


extension = ".pfam"
from MultAlignViewer.parsers.readPfam import fileType, extensions
globs = ["*" + ext for ext in extensions]

def save(fileObj, mav, seqs, fileMarkups):
	longest = max([len(seq.name) for seq in seqs])
	for seq in seqs:
		print>>fileObj, "%*s    %s" % (0-longest, seq.name, str(seq))
