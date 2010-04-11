# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: oslUtil.py 26655 2009-01-07 22:02:30Z gregc $

"""Miscellaneous utilities for OSL identifiers"""

def oslSort(osl1, osl2):
	"""Function that can be used in conjunction with 'sort' to order
	   OSL identifiers in a semantically meaningful way.  The ordering
	   only works right for 'simple' OSL identifiers (no ranges or
	   attribute qualifiers).
	"""

	if osl1[0] == osl2[0]:
		preDot1, postDot1, remainder1 = _parseSegment(osl1[1:])
		preDot2, postDot2, remainder2 = _parseSegment(osl2[1:])
		pre1 = osl[1:preDot1]
		pre2 = osl[1:preDot2]
		if osl1[0] in ['#', '@']:
			# model number more important than submodel number
			# atom name more important than alternate location
			if osl1[0] == '#':
				pre1 = int(pre1)
				pre2 = int(pre2)
			if pre1 < pre2:
				return -1
			elif pre1 > pre2:
				return 1
			if postDot1 and postDot2:
				post1 = osl[preDot1+1:postDot1]
				post2 = osl[preDot2+1:postDot2]
				if osl1[0] == '#':
					post1 = int(post1)
					post2 = int(post2)
				if post1 < post2:
					return -1
				elif post1 > post2:
					return 1
				# equals falls through
			elif postDot1:
				return 1
			elif postDot2:
				return -1

			if remainder1 and remainder2:
				return oslSort(osl1[remainder1:],
							osl2[remainder2:])
			elif remainder1:
				return 1
			elif remainder2:
				return -1
			return 0
		elif osl1[0] == ':':
			# chain id more important than residue sequence
			if postDot1 and postDot2:
				post1 = osl1[preDot1+1:postDot1]
				post2 = osl1[preDot2+1:postDot2]
				if post1 < post2:
					return -1
				elif post1 > post2:
					return 1
				# equals falls through
			elif postDot1:
				return 1
			elif postDot2:
				return -1

			seqNum1, insert1 = _seqParse(osl1[1:preDot1])
			seqNum2, insert2 = _seqParse(osl2[1:preDot2])
			
			if seqNum1 < seqNum2:
				return -1
			elif seqNum1 > seqNum2:
				return 1
			
			if insert1 and insert2:
				return cmp(osl1[insert1:preDot1],
							osl2[insert2:preDot2])
			elif insert1:
				return 1
			elif insert2:
				return -1
			return 0

		return cmp(osl1, osl2)
	else:
		if osl1 < osl2:
			return -1
		elif osl1 > osl2:
			return 1
		return 0

_identSeps = '#:@/.'
def _parseSegment(segment):
	preDotEnd = postDotEnd = None
	for i in range(len(segment)):
		if segment[i] not in _identSeps:
			continue
		if preDotEnd:
			if i+2 >= len(segment):
				return preDotEnd, i, None
			return preDotEnd, i, i+2
		if segment[i] != '.':
			if i+2 >= len(segment):
				return i, None, None
			return i, None, i+2
		preDotEnd = i
	if preDotEnd:
		return preDotEnd, i, None
	return i, None, None

def _seqParse(seq):
	insert = None
	for i in range(len(seq)):
		if seq[i] not in string.digits:
			insert = i
			seqNum = int(seq[:i])
			break
	else:
		seqNum = int(seq)
	
	return seq, insert
