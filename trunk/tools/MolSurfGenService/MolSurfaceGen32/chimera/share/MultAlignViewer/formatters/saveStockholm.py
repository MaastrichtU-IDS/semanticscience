# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: saveStockholm.py 26655 2009-01-07 22:02:30Z gregc $


from MultAlignViewer.parsers.readStockholm import fileType, extensions, \
					genericFileAttrs, genericSeqAttrs
extension = ".sto"
globs = ["*" + ext for ext in extensions]
from chimera.Sequence import Sequence

revFileAttrs = {}
for stockholm, generic in genericFileAttrs.items():
	revFileAttrs[generic] = stockholm
revSeqAttrs = {}
for stockholm, generic in genericSeqAttrs.items():
	revSeqAttrs[generic] = stockholm

def save(fileObj, mav, seqs, fileMarkups):
	print>>fileObj, "# STOCKHOLM 1.0"

	for tag, val in mav.fileAttrs.items():
		tag = revFileAttrs.get(tag, tag)
		if tag.startswith("Stockholm "):
			tag = tag[10:]
		tag = tag.replace(" ", "_")
		for line in str(val).split('\n'):
			print>>fileObj, "#=GF", tag, line

	for seq in seqs:
		name = seq.name.replace(' ', '_')
		print>>fileObj, name, seq
		try:
			markups = seq.markups
		except AttributeError:
			markups = {}
		# add an SS markup if appropriate...
		if hasattr(seq, "matchMaps") and seq.matchMaps:
			added = 0
			for mol, matchMap in seq.matchMaps.items():
				added += 1
				def mapFunc(i):
					u = seq.gapped2ungapped(i)
					if u is None:
						return '.'
					if u not in matchMap:
						return 'X'
					res = matchMap[u]
					if res.isHelix:
						return 'H'
					if res.isStrand:
						return 'E'
					return 'C'
				ssMarkup = "".join(
						map(mapFunc, range(len(seq))))
				ssName = "Chimera actual SS %s %s" % (mol.name,
								mol.oslIdent())
				markups[ssName] = ssMarkup
			if added == 1 and 'SS' not in markups:
				markups['SS'] = ssMarkup
		for tag, val in markups.items():
			tag = tag.replace(" ", "_")
			print>>fileObj, "#=GR", name, tag, val
		try:
			attrs = seq.attrs
		except AttributeError:
			attrs = {}
		for tag, val in attrs.items():
			tag = revSeqAttrs.get(tag, tag)
			if tag.startswith("Stockholm "):
				tag = tag[10:]
			tag = tag.replace(" ", "_")
			for line in str(val).split('\n'):
				print>>fileObj, "#=GS", name, tag, line

	for tag, val in fileMarkups.items():
		tag = tag.replace(" ", "_")
		print>>fileObj, "#=GC", tag, val

