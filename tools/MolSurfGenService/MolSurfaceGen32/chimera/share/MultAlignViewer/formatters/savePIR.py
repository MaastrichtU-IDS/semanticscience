# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: savePIR.py 26655 2009-01-07 22:02:30Z gregc $

import string

extension = ".pir"
from MultAlignViewer.parsers.readPIR import fileType, extensions
globs = ["*" + ext for ext in extensions]

LINELEN = 60

def save(fileObj, mav, seqs, fileMarkups):
	if hasattr(mav.seqs[0], "nucleic"):
		nucleic = mav.seqs[0].nucleic
	else:
		nucleic = 1
		for res in mav.seqs[0]:
			if res in string.letters \
			and res not in "ACGTUXacgtux":
				nucleic = 0
				break

	for seq in seqs:
		if hasattr(seq, "PIRtype"):
			pirType = seq.PIRtype
		else:
			if nucleic:
				pirType = "DL"
			else:
				pirType = "P1"
		print>>fileObj, ">%2s;%s" % (pirType, seq.name)
		if hasattr(seq, "descript"):
			descript = seq.descript
		else:
			descript = seq.name
		print>>fileObj, descript
		for i in range(0, len(seq), LINELEN):
			print>>fileObj, seq[i:i+LINELEN]
		print>>fileObj, "*"
