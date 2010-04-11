# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
reads a Pfam file
"""

from chimera.Sequence import Sequence
from MultAlignViewer.parse import WrongFileTypeError, FormatSyntaxError, \
								makeReadable

# extensions to look for in file browser
extensions = [".pfam", ".slx", ".selex"]

# prefix to use on Chimera command line
prefixes = ["selex", "pfam"]

# what type of file do we provide parsing for...
fileType = "Selex"

def parse(fileName):
	from OpenSave import osOpen
	f = osOpen(fileName, "r")
	# skip header crap
	inHeader = True
	lineNum = 0
	sequences = []
	for line in f:
		line = line.strip()
		lineNum += 1
		if not line:
			continue
		fields = line.split()
		if inHeader:
			if len(fields[0]) == 2:
				continue
			inHeader = False
		if len(fields) != 2:
			# since this format lacks mandatory headers,
			# cannot be sure it _is_ a Pfam file and therefore
			# cannot raise FormatSyntaxError
			raise WrongFileTypeError()
		seq = Sequence(makeReadable(fields[0]))
		seq.extend(fields[1])
		sequences.append(seq)
	f.close()
	if not sequences:
		raise WrongFileTypeError()
	return sequences, {}, {}
