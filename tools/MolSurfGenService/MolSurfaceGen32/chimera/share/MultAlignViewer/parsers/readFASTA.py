# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
reads an aligned FASTA file
"""

from chimera.Sequence import Sequence
from MultAlignViewer.parse import WrongFileTypeError, FormatSyntaxError, \
								makeReadable

# extensions to look for in file browser
extensions = [".fasta", ".fa", ".afasta", ".afa"]

# prefix to use on Chimera command line
prefixes = ["afasta"]

# what type of file do we provide parsing for...
fileType = "Aligned FASTA"

def parse(fileName):
	from OpenSave import osOpen
	f = osOpen(fileName, "r")
	inSequence = 0
	sequences = []
	for line in f.readlines():
		if inSequence:
			if not line or line.isspace():
				inSequence = 0
				continue
			if line[0] == '>':
				inSequence = 0
				# fall through
			else:
				sequences[-1].extend(line.strip())
		if not inSequence:
			if line[0] == '>':
				if sequences and len(sequences[-1]) == 0:
					raise FormatSyntaxError("No sequence"
					" found for %s" % sequences[-1].name)
				inSequence = 1
				sequences.append(Sequence(makeReadable(
								line[1:])))
	f.close()
	if not sequences:
		raise WrongFileTypeError()
	return sequences, {}, {}
