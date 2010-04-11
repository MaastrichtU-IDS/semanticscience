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
extensions = [".pir", ".ali"]

# prefix to use on Chimera command line
prefixes = ["pir"]

# what type of file do we provide parsing for...
fileType = "Aligned NBRF/PIR"

def parse(fileName):
	from OpenSave import osOpen
	f = osOpen(fileName, "r")
	want = 'init'
	sequences = []
	for line in f.readlines():
		line = line.strip()
		if want == 'init':
			if len(line) < 4:
				continue
			if line[0] != '>' or line[3] != ';':
				continue
			sequences.append(Sequence(makeReadable(line[4:])))
			pirType = line[1:3]
			if pirType in ("P1", "F1"):
				sequences[-1].nucleic = 0
			else:
				sequences[-1].nucleic = 1
			sequences[-1].PIRtype = pirType
			want = 'descript'
		elif want == 'descript':
			sequences[-1].descript = line
			sequences[-1].PIRdescript = line
			want = 'sequence'
		elif want == 'sequence':
			if not line:
				continue
			if line[-1] == '*':
				want = 'init'
				line = line[:-1]
			sequences[-1].extend(filter(lambda c,
				whsp=string.whitespace: not c in whsp, line))
	f.close()
	if not sequences:
		raise WrongFileTypeError()
	if want != 'init':
		raise FormatSyntaxError("Could not find end of sequence '%s'"
							% sequences[-1].name)
	return sequences, {}, {}
