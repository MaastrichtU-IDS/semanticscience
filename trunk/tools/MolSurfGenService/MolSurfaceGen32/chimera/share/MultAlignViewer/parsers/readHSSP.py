# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
reads a PIR file
"""

import string
from chimera.Sequence import Sequence
from MultAlignViewer.parse import WrongFileTypeError, FormatSyntaxError, \
								makeReadable

# extensions to look for in file browser
extensions = [".hssp"]

# prefix to use on Chimera command line
prefixes = ["hssp"]

# what type of file do we provide parsing for...
fileType = "HSSP"

def parse(fileName):
	from OpenSave import osOpen
	f = osOpen(fileName, "r")
	doing = None
	sequences = []
	headerOK = False
	lineNum = 0
	alignStartIndex = None
	for line in f:
		if doing == 'alignments':
			# don't strip() alignment section since it has significant
			# leading spaces
			line = line.rstrip()
		else:
			line = line.strip()
		lineNum += 1
		if not headerOK:
			if line.lower().startswith('hssp'):
				headerOK = True
				continue
			raise WrongFileTypeError("No initial HSSP header line")
		if line.startswith('##'):
			if doing == 'proteins' and not sequences:
				raise FormatSyntaxError("No entries in PROTEINS section")
			try:
				doing = line.split()[1].lower()
			except IndexError:
				doing = None
			if doing == 'alignments':
				try:
					hashes, alignments, begin, dash, end = line.strip().split()
					begin = int(begin)
					end = int(end)
				except ValueError:
					raise FormatSyntaxError("ALIGNMENTS line (line #%d) not of "
						"the form: ## ALIGNMENTS (number) - (number)" % lineNum)
			continue
		if doing == 'proteins':
			if not line[0].isdigit():
				continue
			try:
				seqName = line.split()[2]
			except IndexError:
				raise WrongFormatError("Line %d in PROTEINS section does not "
					"start with [integer] : [sequence name]" % lineNum)
			sequences.append(Sequence(makeReadable(seqName)))
		elif doing == 'alignments':
			if line.lstrip().lower().startswith('seqno'):
				try:
					alignStartIndex = line.index('.')
				except:
					raise FormatSyntaxError("No indication of alignment "
						" starting column ('.' character) in SeqNo line "
						" in ALIGNMENTS section")
				continue
			if alignStartIndex == None:
				raise FormatSyntaxError("No initial SeqNo line in "
					"ALIGNMENTS section")
			block = line[alignStartIndex:]
			if not block:
				raise FormatSyntaxError("No alignment block given on line %d"
					% lineNum)
			blockLen = end - begin + 1
			if len(block) > blockLen:
				raise FormatSyntaxError("Too many characters (%d, only %d "
				" sequences) in alignment block given on line %d"
				% (len(block), blockLen, lineNum))
			block = block + ' ' * (blockLen - len(block))
			for seq, c in zip(sequences[begin-1:end], block):
				seq.append(c)
	f.close()
	return sequences, {}, {}
