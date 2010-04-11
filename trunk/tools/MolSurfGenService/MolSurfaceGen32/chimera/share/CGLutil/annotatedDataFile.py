# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: annotatedDataFile.py 26655 2009-01-07 22:02:30Z gregc $

def readDataFile(attrFile):
	"""read an annotated data file

	   'attrFile' indicates a file-like object or list of strings.
	   attrFile contains control lines and data lines.  Control and
	   data lines may be freely interspersed.  The data lines are of
	   the form:

	   	<tab>field 1 [<tab>field 2...]

	   The control lines are of the form:

	   	name: value
	   
	   Empty lines are ignored and lines beginning with the '#' character
	   are considered comments and ignored.

	   If a control line with a duplicate name is encountered, then
	   it is assumed that the file is basically several separate files
	   concatenated together (which can be convenient for defining
	   attributes for example).  The previous data/control line are
	   remembered and a new set gathered from scratch.

	   This function returns a list of tuples, one for each "set" of
	   control/data lines in the file (see previous paragraph).  Each
	   tuple consists of a dictionary of the controls lines, keyed on
	   name, and a list of the data line tuples (split at tabs).
	"""

	attrs = {}
	data = []

	all = []
	lineNum = 0
	dataErrors = []
	# data values can have significant spaces, so be careful with the
	# stripping
	for line in attrFile:
		lineNum += 1

		while line and line[-1] in "\r\n":
			line = line[:-1]
		if not line.strip(): continue
		if line[0] == '#': continue

		if line[0] == '\t':
			# data line
			data.append(line[1:].split("\t"))
		else:
			# control line
			try:
				name, value = line.split(": ")
			except ValueError:
				raise SyntaxError("Line %d of file is either"
					" not 'name: value' or is missing"
					" initial tab" % lineNum)
			name = name.strip().lower()
			value = value.strip()
			if name in attrs:
				# presumably another "set" of control/data
				# lines starting
				all.append((attrs, data))
				attrs = {}
				data = []
			attrs[name] = value
			if not value:
				raise SyntaxError("Empty value on line %d"
						" of file" % lineNum)
	if dataErrors:
		raise SyntaxError, "\n".join(dataErrors)
	all.append((attrs, data))
	return all
