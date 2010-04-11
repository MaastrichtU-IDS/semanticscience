# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: saveRSF.py 26655 2009-01-07 22:02:30Z gregc $


extension = ".rsf"
from MultAlignViewer.parsers.readRSF import fileType, extensions
globs = ["*" + ext for ext in extensions]
from chimera.Sequence import Sequence

LINELEN = 60

def save(fileObj, mav, seqs, fileMarkups):
	print>>fileObj, "!!RICH_SEQUENCE 1.0"
	if "comments" in mav.fileAttrs:
		print>>fileObj, mav.fileAttrs["comments"]
	print>>fileObj, ".."

	for seq in seqs:
		print>>fileObj, "{"
		try:
			attrs = seq.attrs
		except AttributeError:
			attrs = {}
		print>>fileObj, "name  ", seq.name
		if "description" in attrs:
			print>>fileObj, "descrip  ", seq.attrs['description']
		for attr, val in attrs.items():
			if attr == "RSF features" or attr == "description":
				continue
			if attr.startswith("RSF "):
				attr = attr[4:]
			attr.replace(" ", "_")
			if '\n' in str(val):
				print>>fileObj, attr
				if val[0].isspace():
					indent = ""
				else:
					indent = "  "
				for line in val.split('\n'):
					print>>fileObj, indent + line
			else:
				print>>fileObj, attr, "  ", val
		offset = 0
		while offset < len(seq) and not seq[offset].isalnum():
			offset += 1
		print>>fileObj, "offset  ", offset

		if "RSF features" in attrs:
			for feature in attrs["RSF features"]:
				print>>fileObj, "feature", feature[0]
				for line in feature[1:]:
					print>>fileObj, line
		trailer = len(seq)
		while trailer > 0 and not seq[trailer-1].isalnum():
			trailer -= 1
		print>>fileObj, "sequence"
		for start in range(offset, trailer-1, LINELEN):
			end = min(start+LINELEN, trailer)
			print>>fileObj, "  ", seq[start:end]

		print>>fileObj, "}"

