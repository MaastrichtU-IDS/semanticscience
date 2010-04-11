# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: saveFASTA.py 26655 2009-01-07 22:02:30Z gregc $


extension = ".afasta"
from MultAlignViewer.parsers.readFASTA import fileType, extensions
globs = ["*" + ext for ext in extensions]

LINELEN = 60

def save(fileObj, mav, seqs, fileMarkups):
	for seq in seqs:
		print>>fileObj, ">%s" % seq.name
		for i in range(0, len(seq), LINELEN):
			print>>fileObj, seq[i:i+LINELEN]
		print>>fileObj
