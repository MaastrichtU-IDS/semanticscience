# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
reads a GCG9 RSF format file
"""

from chimera.Sequence import Sequence
from MultAlignViewer.parse import WrongFileTypeError, FormatSyntaxError, \
								makeReadable

# extensions to look for in file browser
extensions = [".rsf"]

# prefix to use on Chimera command line
prefixes = ["rsf"]

# what type of file do we provide parsing for...
fileType = "GCG RSF"

def parse(fileName):
	IN_HEADER = 0
	START_ATTRS = 1
	IN_ATTRS = 2
	IN_FEATURES = 3
	IN_SEQ = 4

	state = IN_HEADER

	from OpenSave import osOpen
	f = osOpen(fileName, "r")
	sequences = []
	lineNum = 0
	hasOffset = 0
	longest = None
	fileAttrs = {}
	for line in f:
		line = line.rstrip() # remove trailing whitespace/newline
		lineNum += 1
		if lineNum == 1:
			if line.startswith("!!RICH_SEQUENCE"):
				continue
			raise WrongFileTypeError()
		if state == IN_HEADER:
			if line.strip() == "..":
				state = START_ATTRS
				continue
			if "comments" in fileAttrs:
				fileAttrs["comments"] += "\n" + line
			else:
				fileAttrs["comments"] = line
			continue
		if not line.strip():
			continue
		if state == START_ATTRS:
			if line.strip() == "{":
				state = IN_ATTRS
				curAttr = None
				attrs = {}
			elif line:
				raise FormatSyntaxError("Unexpected text before"
						" start of sequence on line %d"
						% lineNum)
			continue
		if state == IN_ATTRS or state == IN_FEATURES:
			if line.strip() == "sequence" and line[0] == "s":
				if "RSF name" not in attrs:
					raise FormatSyntaxError("sequence on "
						"line %d has no name" % lineNum)
				state = IN_SEQ
				seq = Sequence(makeReadable(attrs["RSF name"]))
				del attrs["RSF name"]
				seq.attrs = attrs
				if "RSF descrip" in attrs:
					attrs["description"] = attrs[
								"RSF descrip"]
					del attrs["RSF descrip"]
				sequences.append(seq)
				if "RSF offset" in attrs:
					seq.extend("." * int(
							attrs["RSF offset"]))
					hasOffset = 1
					del attrs["RSF offset"]
				continue
			if line.startswith("feature"):
				if state == IN_ATTRS:
					attrs["RSF features"] = [[line[8:]]]
				else:
					attrs["RSF features"].append([line[8:]])
				state = IN_FEATURES
				continue

		if state == IN_ATTRS:
			if line[0].isspace():
				# continuation
				if not curAttr:
					raise FormatSyntaxError("Bogus "
							"indentation at line %d"
							% lineNum)
				if attrs[curAttr]:
					attrs[curAttr] += "\n" + line
				else:
					attrs[curAttr] = line
				continue
			if " " in line.strip():
				curAttr, val = line.split(None, 1)
				curAttr.replace("_", " ")
				curAttr = "RSF " + curAttr
				attrs[curAttr] = val.strip()
			else:
				curAttr = "RSF " + line.strip().replace("_", " ")
				attrs[curAttr] = ""
			continue

		if state == IN_FEATURES:
			attrs["RSF features"][-1].append(line)
			continue
		if line.strip() == "}":
			state = START_ATTRS
			if not longest:
				longest = len(seq)
			else:
				if len(seq) < longest:
					seq.extend("." * (longest - len(seq)))
				elif len(seq) > longest:
					longest = len(seq)
					for s in sequences[:-1]:
						s.extend("." *
							(longest - len(s)))
			continue
		seq.extend(line.strip())
		if not seq[0].isalpha():
			hasOffset = 1
			
	f.close()
	if state == IN_HEADER:
		raise FormatSyntaxError(
				"No end to header (i.e. '..' line) found")
	if state == IN_ATTRS or state == IN_FEATURES:
		if "RSF name" in attrs:
			raise FormatSyntaxError(
					"No sequence data found for sequence %s"
					% attrs["RSF name"])
		raise FormatSyntaxError("Sequence without sequence data")
	
	if state == IN_SEQ:
		raise FormatSyntaxError("No terminating brace for sequence %s"
							% attrs["RSF name"])
			
	if not sequences:
		raise FormatSyntaxError("No sequences found")
	if not hasOffset:
		from chimera import replyobj
		replyobj.warning("No offset fields in RSF file;"
						" assuming zero offset\n")
	return sequences, fileAttrs, {}
