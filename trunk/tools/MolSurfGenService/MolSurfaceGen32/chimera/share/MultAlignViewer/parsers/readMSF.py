# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
MSF reads a Multiple Sequence Format (MSF) file.
See Wisconsin Package (GCG) User's Guide, pp 2-28.
"""

import re
from chimera.Sequence import Sequence
from MultAlignViewer.parse import WrongFileTypeError, FormatSyntaxError, \
								makeReadable

# extensions to look for in file browser
extensions = [".msf"]

# prefix to use on Chimera command line
prefixes = ["msf"]

# what type of file do we provide parsing for...
fileType = "MSF"

def parse(f):
	msf = MSF(f)
	fileMarkups = {}
	if msf.multalin:
		for i, seq in enumerate(msf.sequenceList):
			if seq.name.lower() == "consensus":
				c = msf.sequenceList.pop(i)
				fileMarkups["multalin consensus"] = str(c)
				break
	return msf.sequenceList, msf.fileAttrs, fileMarkups

class MSF:

	_Hdr = re.compile('\s*(\S*)\s*'			# name
				'MSF:\s*(\S*)\s*'	# length?
				'Type:\s*(\S*)\s*'	# type
				'(.*)\s*'		# date/time
				'Check:\s*(\S*)\s*'	# checksum
				'\.\.')			# signature
	_MultalinHdr = re.compile('\s*(\S.*)\s*'	# name
				'MSF:\s*(\S*)\s*'	# length?
							# missing type
							# missing date/time
				'Check:\s*(\S*)\s*'	# checksum
				'\.\.')			# signature

	_Sum = re.compile('\s*Name:\s*(\S*)\s*o*\s*'	# name
				'Len:\s*(\S*)\s*'	# length
				'Check:\s*(\S*)\s*'	# checksum
				'Weight:\s*(\S*)\s*')	# weight

	def __init__(self, f):
		self.fileAttrs = {}
		if isinstance(f, basestring):
			from OpenSave import osOpen
			file = osOpen(f)
			self._readMSF(file)
			file.close()
		else:
			self._readMSF(f)

	def _readMSF(self, f):
		self._readHeader(f)
		self._readSequences(f)
		self._readAlignment(f)

	def _readHeader(self, f):
		while 1:
			line = f.readline()
			if not line:
				raise WrongFileTypeError()
			m = MSF._Hdr.match(line)
			if m is not None:
				name = m.group(1).strip()
				if name:
					self.fileAttrs['MSF name'] = name
				self.fileAttrs['MSF length'] = m.group(2)
				self.fileAttrs['MSF type'] = m.group(3)
				date = m.group(4).strip()
				if date:
					self.fileAttrs['date'] = date
				self.fileAttrs['MSF checksum'] = m.group(5)
				self.multalin = False
				break
			m = MSF._MultalinHdr.match(line)
			if m is not None:
				self.fileAttrs['MSF name'] = m.group(1)
				self.fileAttrs['MSF length'] = m.group(2)
				self.fileAttrs['MSF checksum'] = m.group(3)
				self.multalin = True
				break
			try:
				self.fileAttrs['MSF header'] += line
			except KeyError:
				self.fileAttrs['MSF header'] = line
		try:
			self.fileAttrs['MSF header'] = self.fileAttrs[
							'MSF header'].strip()
		except KeyError:
			self.fileAttrs['MSF header'] = ''

	def _readSequences(self, f):
		#self.sequenceDict = {}
		self.sequenceList = []
		while 1:
			line = f.readline()
			if not line:
				raise FormatSyntaxError(
						'no alignment separator')
			if line == '//\n' or line == '//\r\n':
				break
			m = MSF._Sum.match(line)
			if m is not None:
				name = m.group(1)
				length = m.group(2)
				check = m.group(3)
				weight = m.group(4)
				s = Sequence(makeReadable(name))
				self.sequenceList.append(s)
				s.attrs = {}
				s.attrs['MSF length'] = length
				s.attrs['MSF check'] = check
				s.attrs['MSF weight'] = weight
		if not self.sequenceList:
			raise FormatSyntaxError('No sequences found in header')

	def _readAlignment(self, f):
		line = f.readline()
		if not line:
			raise FormatSyntaxError('no alignment data')
		while self._readBlock(f):
			pass

	def _readBlock(self, f):
		line = f.readline()
		if not line:
			return 0
		if line == '\n' or line == '\r\n':
			return 1	# ignore empty line
		# check (and skip) any column numbering
		if "".join(line.split()).isdigit():
			line = f.readline()
			if not line:
				raise FormatSyntaxError('unexpected EOF')
		seqIndex = 0
		while 1:
			if line.isspace():
				break
			field = line.split()
			try:
				seq = self.sequenceList[seqIndex]
			except IndexError:
				raise FormatSyntaxError('more sequences'
					' in actual alignment than in header')
			#try:
			#	seq = self.sequenceDict[field[0]]
			#except KeyError:
			#	raise FormatSyntaxError(
			#		'unexpected sequence ' + field[0])
			for block in field[1:]:
				seq.append(block)
			line = f.readline()
			if not line:
				# allow for files that don't end in newline
				if self.sequenceList[-1] == seq \
				and len(seq) == int(seq.attrs['MSF length']):
					return 0
				raise FormatSyntaxError('unexpected EOF')
			seqIndex += 1
		return 1
