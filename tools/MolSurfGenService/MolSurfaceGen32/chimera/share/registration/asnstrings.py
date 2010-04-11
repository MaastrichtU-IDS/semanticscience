# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import sys
import string
import binascii

import asn1

StringTypes = [
	asn1.PrintableString,
	asn1.T61String,
	asn1.IA5String,
	asn1.UTCTime
]
ContainerTypes = [
	asn1.SEQUENCE,
	asn1.SET
]

def printASN(asn, prefix=''):
	for t, v in asn:
		if isinstance(v, list):
			print '%s%s' % (prefix, repr(t))
			printASN(v, prefix + '  ')
		else:
			print '%s%s - %s' % (prefix, repr(t), repr(v))

def dumpStrings(asn):
	for t, v in asn:
		if t in StringTypes:
			print v.tostring()
		elif t in ContainerTypes:
			dumpStrings(v)

if __name__ == '__main__':
	f = open(sys.argv[1])
	block = []
	collect = 0
	while 1:
		line = f.readline()
		if not line:
			break
		if line[:5] == '-----':
			if block:
				break
			else:
				collect = 1
		elif collect:
			block.append(line)
	f.close()
	asn = asn1.decode(a2b_base64(string.join(block, '')))
	dumpStrings(asn)
