# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
reads a Stockholm (Pfaat, HMMer, Pfam) format file
"""

from chimera.Sequence import Sequence
from MultAlignViewer.parse import WrongFileTypeError, FormatSyntaxError, \
								makeReadable

# extensions to look for in file browser
extensions = [".sth", ".sto"]

# prefix to use on Chimera command line
prefixes = ["sth", "hmmer"]

# what type of file do we provide parsing for...
fileType = "Stockholm"

# what format-specific features can be used generically by MAV...
# (also used by saveStockholm.py...)
genericFileAttrs = {
	"AC":  "accession",
	"AU":  "author",
	"CC":  "comments",
	"DE":  "description"
}
genericSeqAttrs = {
	"AC":	"accession",
	"DE":	"description",
	"WT":	"weight"
}

def parse(fileName):
	from OpenSave import osOpen
	from chimera import replyobj
	f = osOpen(fileName, "r")
	lineNum = 0
	fileAttrs = {}
	fileMarkups = {}
	seqAttrs = {}
	seqMarkups = {}
	sequences = {}
	seqSequence = []
	for line in f:
		line = line[:-1] # drop newline
		lineNum += 1
		if lineNum == 1:
			if line.startswith("# STOCKHOLM"):
				continue
			raise WrongFileTypeError()
		if not line:
			continue
		if line.startswith('#='):
			markupType = line[2:4]
			markup = line[5:].strip()
			def trySplit(numSplit):
				fields = markup.split(None, numSplit)
				if len(fields) == numSplit:
					# value is empty
					fields.append("")
				if len(fields) != numSplit + 1:
					raise FormatSyntaxError("Not enough"
						" arguments after #=%s markup"
						" on line %d" % (
						markupType, lineNum))
				return fields
			if markupType == "GF":
				tag, val = trySplit(1)
				tag = tag.replace("_", " ")
				tag = genericFileAttrs.get(tag,
							"Stockholm " + tag)
				if tag in fileAttrs:
					fileAttrs[tag] += '\n' + val
				else:
					fileAttrs[tag] = val
			elif markupType == "GS":
				seqName, tag, val = trySplit(2)
				tag = tag.replace("_", " ")
				attrs = seqAttrs.setdefault(seqName, {})
				tag = genericSeqAttrs.get(tag,
							"Stockholm " + tag)
				if tag in attrs:
					attrs[tag] += '\n' + val
				else:
					attrs[tag] = val
			elif markupType == "GC":
				tag, val = trySplit(1)
				tag = tag.replace("_", " ")
				fileMarkups[tag] = fileMarkups.get(tag,
								"") + val
			elif markupType == "GR":
				seqName, tag, val = trySplit(2)
				tag = tag.replace("_", " ")
				seqMarkups.setdefault(seqName,
							{}).setdefault(tag, "")
				seqMarkups[seqName][tag] += val
			# ignore other types
			continue
		elif line.startswith('#'):
			# unstructured comment
			if 'comments' in fileAttrs:
				fileAttrs['comments'] += "\n" + line[1:]
			else:
				fileAttrs['comments'] = line[1:]
			continue
		elif line.strip() == "//":
			# end of sequence alignment blocks, but comments
			# may follow this, so keep going...
			continue
		# sequence info...
		try:
			seqName, block = line.split(None, 1)
		except ValueError:
			raise FormatSyntaxError("Sequence info not in name/"
				"contents format on line %d" % lineNum)
		if seqName not in sequences:
			sequences[seqName] = Sequence(makeReadable(seqName))
			seqSequence.append(seqName)
		sequences[seqName].extend(block)
	f.close()
			
	if not sequences:
		raise FormatSyntaxError("No sequences found")
	for seqName, seq in sequences.items():
		if seqName in seqAttrs:
			seq.attrs = seqAttrs[seqName]
		if seqName in seqMarkups:
			seq.markups = seqMarkups[seqName]
			for tag, markup in seq.markups.items():
				if len(markup) != len(seq):
					replyobj.warning("Markup %s for"
						" sequence %s is wrong length;"
						" ignoring\n" % (tag, seqName))
					del seq.markups[tag]
	for seqInfo, label in [(seqAttrs, "sequence"), (seqMarkups, "residue")]:
		for seqName in seqInfo.keys():
			if seqName in sequences:
				continue
			# might be sequence name without trailing '/start-end'
			for fullName in sequences.keys():
				if fullName.startswith(seqName) \
				and fullName[len(seqName)] == '/' \
				and '/' not in fullName[len(seqName)+1:]:
					break
			else:
				raise FormatSyntaxError("%s annotations "
					"provided for non-existent sequence %s"
					% (label.capitalize(), seqName))
			replyobj.info("Updating %s %s annotions with %s "
				"annotations\n" % (fullName, label, seqName))
			seqInfo[fullName].update(seqInfo[seqName])
			del seqInfo[seqName]
	for tag, markup in fileMarkups.items():
		if len(markup) != len(sequences[seqSequence[0]]):
			raise FormatSyntaxError("Column annotation %s is"
							" wrong length" % tag)
			
	return map(lambda name: sequences[name], seqSequence), \
							fileAttrs, fileMarkups
