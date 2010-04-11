# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: saveMSF.py 26655 2009-01-07 22:02:30Z gregc $

import string
import time

extension = ".msf"
from MultAlignViewer.parsers.readMSF import fileType, extensions
globs = ["*" + ext for ext in extensions]

def save(fileObj, mav, seqs, fileMarkups):
	if hasattr(mav.seqs[0], "nucleic"):
		nucleic = mav.seqs[0].nucleic
	else:
		nucleic = 1
		for res in mav.seqs[0].ungapped():
			if res in string.letters and res not in "ACGTUXacgtux":
				nucleic = 0
				break
	if mav.fileAttrs and mav.fileAttrs.get('MSF header', False):
		print>>fileObj, mav.fileAttrs['MSF header']
	else:
		if nucleic:
			print>>fileObj, "!!NA_MULTIPLE_ALIGNMENT 1.0"
		else:
			print>>fileObj, "!!AA_MULTIPLE_ALIGNMENT 1.0"
		print>>fileObj, "MultAlignViewer save of %s" % mav.title
	if nucleic:
		typeField = 'N'
	else:
		typeField = 'P'
	name = mav.title.replace(' ', '_')
	print>>fileObj, name, " MSF:", len(seqs[0]), " Type:", \
				typeField, " ", time.asctime(), " Check: 0 .."

	maxName = 0
	for seq in seqs:
		maxName = max(maxName, len(seq.name))

	for seq in seqs:
		print>>fileObj, "Name: %*s  Len: %d  Check: 0  Weight: 1.00" % (
				maxName, seq.name.replace(' ', '_'), len(seq))
	print>>fileObj, "//\n"

	for i in range(0, len(seqs[0]), 50):
		print>>fileObj, "%*s  %-10d" % (maxName, " ", i+1),
		if i+50 >= len(seqs[0]):
			print>>fileObj
		else:
			print>>fileObj, "%47d" % (i+50)
		for seq in seqs:
			print>>fileObj, "%*s" % (maxName,
						seq.name.replace(' ', '_')),
			for j in range(i, i+50, 10):
				if j >= len(seq):
					break
				print>>fileObj, "", seq[j:j+10],
			print>>fileObj
		print>>fileObj


					


