# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
reads a ClustalW ALN format file
"""

from chimera.Sequence import Sequence
from MultAlignViewer.parse import WrongFileTypeError, FormatSyntaxError, \
								makeReadable

# extensions to look for in file browser
extensions = [".aln", ".clustal", ".clustalw", ".clustalx"]

# prefix to use on Chimera command line
prefixes = ["aln"]

# what type of file do we provide parsing for...
fileType = "Clustal ALN"

def parse(fileName):
	from OpenSave import osOpen
	f = osOpen(fileName, "r")
	inHeader = 1
	sequences = []
	lineNum = 0
	for line in f.readlines():
		lineNum += 1
		if inHeader:
			if line.startswith("CLUSTAL"):
				inHeader = 0
				firstBlock = 1
			else:
				if line.strip() !="":
					raise WrongFileTypeError()
			continue
		if not line or line[0].isspace():
			if sequences:
				firstBlock = 0
				expect = 0
			continue
		try:
			seqName, seqBlock, numResidues = line.split()
		except ValueError:
			try:
				seqName, seqBlock = line.split()
			except ValueError:
				raise FormatSyntaxError("Line %d is not "
					"sequence name followed by sequence "
					" contents and optional ungapped length"
					% lineNum)
		if firstBlock:
			sequences.append(Sequence(makeReadable(seqName)))
			sequences[-1].append(seqBlock)
			continue
		try:
			seq = sequences[expect]
		except IndexError:
			raise FormatSyntaxError("Sequence on line %d not in"
				" initial sequence block" % lineNum)
		expect += 1
		seq.append(seqBlock)
	f.close()
	if not sequences:
		raise WrongFileTypeError()
	return sequences, {}, {}
