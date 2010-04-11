# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import re

class MSF:
	"""
	MSF reads a Multiple Sequence Format (MSF) file.
	See Wisconsin Package (GCG) User's Guide, pp 2-28.
	"""

	_Hdr = re.compile(' *([^ ]*) *'			# name
				'MSF: *([^ ]*) *'	# length?
				'Type: *([^ ]*) *'	# type
				'(.*) *'		# date/time
				'Check: *([^ ]*) *'	# checksum
				'\.\.')			# signature
	_HdrFmt = ' %s  MSF: %d  Type: %s  %s  Check: %d ..\n'

	_Sum = re.compile(' *Name: *([^ ]*) o* *'	# name
				'Len: *([^ ]*) *'	# length
				'Check: *([^ ]*) *'	# checksum
				'Weight: *([^ ]*) *')	# weight
	_SumFmt = ' Name: %-15s  Len: %5d  Check: %4d  Weight: %5.2f'

	_Cnt = re.compile(' *([0-9]+) *'		# start residues
				'([0-9]+) *')		# end residues

	def __init__(self, f):
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
				raise IOError, (-1, 'no header signature line')
			m = MSF._Hdr.match(line)
			if m is not None:
				self.name = m.group(1)
				self.length = int(m.group(2))
				self.type = m.group(3)
				self.date = m.group(4).strip()
				self.check = int(m.group(5))
				break
			try:
				self.header = self.header + line
			except AttributeError:
				self.header = line
		try:
			self.header = self.header.strip()
		except AttributeError:
			self.header = ''

	def _readSequences(self, f):
		self.sequenceDict = {}
		self.sequenceList = []
		while 1:
			line = f.readline()
			if not line:
				raise IOError, (-1, 'no alignment separator')
			if line == '//\n':
				break
			m = MSF._Sum.match(line)
			if m is not None:
				name = m.group(1)
				length = int(m.group(2))
				check = int(m.group(3))
				weight = float(m.group(4))
				s = Sequence(name, length, check,
							weight, self)
				self.sequenceDict[name] = s
				self.sequenceList.append(s)

	def _readAlignment(self, f):
		line = f.readline()
		if not line:
			raise IOError, (-1, 'no alignment data')
		while self._readBlock(f):
			pass

	def _readBlock(self, f):
		line = f.readline()
		if not line:
			return 0
		if line == '\n' or line == '\r\n':
			return 1	# ignore empty line
		m = MSF._Cnt.match(line)
		if m is not None:
			line = f.readline()
			if not line:
				raise IOError, (-1, 'unexpected EOF')
		while 1:
			if line == '\n':
				break
			field = line.split()
			try:
				seq = self.sequenceDict[field[0]]
			except KeyError:
				raise IOError, \
					(-1, 'unexpected sequence ' + field[0])
			for block in field[1:]:
				seq.addBlock(block)
			line = f.readline()
			if not line:
				# allow for files without trailing newline
				if self.sequenceList[-1] == seq \
			 	and len(seq.sequence()) == seq.length:
					return 0
				raise IOError, (-1, 'unexpected EOF')
		return 1

	def save(self, f):
		if self.header:
			f.write(self.header)
			f.write('\n\n')
		f.write(MSF._HdrFmt % (self.name, self.length,
					self.type, self.date, self.check))
		f.write('\n')
		width = 0
		for s in self.sequenceList:
			width = max(len(s.name), width)
			f.write('%s\n' % s.summary())
		f.write('\n//\n\n')
		nameFmt = '%%%ds  ' % width
		for i in range(0, self.length, 50):
			f.write('%s  %-5d' % (' ' * width, i + 1))
			end = min(self.length, i + 50)
			length = end - i
			gap = length + (length - 1) / 10 - 5 - 5
			if gap > 0:
				f.write('%s%5d\n' % (' ' * gap, end))
			else:
				f.write('\n')
			for s in self.sequenceList:
				f.write(nameFmt % s.name)
				for j in range(0, length, 10):
					offset = i + j
					seq = s.sequence()[offset:offset + 10]
					f.write('%s ' % ''.join(seq))
				f.write('\n')
			f.write('\n')

	def dump(self):
		print 'Name:', self.name
		print 'Length:', self.length
		print 'Type:', self.type
		print 'Date:', `self.date`
		print 'Check:', self.check
		print 'Header:', self.header.strip()
		print 'Sequences:'
		for sequence in self.sequenceList:
			sequence.dump()

class Sequence:
	"""
	Sequence is a single sequence in an MSF file
	"""

	def __init__(self, name, length, check, weight, msf):
		self.name = name
		self.length = length
		self.check = check
		self.weight = weight
		self.msf = msf
		self.blockList = []

	def addBlock(self, block):
		self.blockList.append(block)

	def sequence(self):
		try:
			return self._sequence
		except AttributeError:
			self._sequence = list(''.join(self.blockList))
			return self._sequence

	def summary(self):
		return MSF._SumFmt % (self.name, self.length,
					self.check, self.weight)

	def insert(self, pos, char):
		s = self.sequence()
		s.insert(pos, char)

	def delete(self, first, last=-1):
		s = self.sequence()
		if last < 0:
			del s[first]
		else:
			del s[first:last]

	def dump(self):
		print '\tName:', self.name
		print '\tLength:', self.length
		print '\tCheck:', self.check
		print '\tWeight:', self.weight
		print '\tSequence:', self.sequence()
		print

if __name__ == '__main__':
	import sys
	def test(file):
		try:
			msf = MSF(file)
			#msf.dump()
			msf.save(sys.stdout)
		except IOError, (errno, msg):
			print '%s: %s: %s' % (sys.argv[0], file, msg)
	#print 'This should work'
	#test('data/3.opt.msf')
	#print 'This should not'
	#test('data/badseq.msf')
	test(sys.argv[1])
