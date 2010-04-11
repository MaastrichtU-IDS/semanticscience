# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

INTEGER = 2
BIT_STRING = 3
OCTET_STRING = 4
NULL = 5
OBJECT_IDENTIFIER = 6
SEQUENCE = 16
SET = 17
PrintableString = 19
T61String = 20
IA5String = 22
UTCTime = 23

def decodeSingle(bytes, offset=0):
	return _decode(bytes, offset)[1]

def decode(bytes, offset=0):
	#print 'decode'
	result = []
	while offset < len(bytes):
		offset, obj = _decode(bytes, offset)
		result.append(obj)
	return result

def _decode(bytes, offset):
	objClass, isComplex, objType, length, offset = header(bytes, offset)
	end = offset + length
	if not isComplex:
		return end, (objType, bytes[offset:end])
	else:
		#if objType != SEQUENCE and objType != SET:
		#	print objType
		#	raise ValueError, 'complex object is not set or seq'
		result = []
		n = offset
		while n < end:
			n, obj = _decode(bytes, n)
			result.append(obj)
		return end, (objType, result)

def header(bytes, offset):
	byte = ord(bytes[offset])
	objClass = byte >> 6
	isComplex = (byte >> 5) & 0x1
	objType = byte & 0x1F
	length = ord(bytes[offset + 1])
	if length & 0x80:
		lengthBytes = length & 0x7F
		if lengthBytes > 4:
			raise ValueError, 'object too large'
		n = 0
		for i in range(lengthBytes):
			n = (n << 8) | ord(bytes[offset + 2 + i])
		length = n
		offset = offset + 2 + lengthBytes
	else:
		offset = offset + 2
	return (objClass, isComplex, objType, length, offset)
