# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import bsddb

import asn1
import x509

RC4Signature = '\x2A\x86\x48\x86\xF7\x0D\x03\x04'

def extractKey(inFile, password):
	db = bsddb.hashopen(inFile, 'r')
	keyDict = {}
	try:
		key, value = db.first()
		while 1:
			keyDict[key] = value
			key, value = db.next()
	except KeyError:
		db.close()

	nsKey = asn1.decode(keyDict['Server-Key\0'])
	rc4 = nsKey[1][1][0][1][0][1]
	if rc4 != RC4Signature:
		raise ValueError, 'RC4 signature not found'
	entrySalt = nsKey[0][1]
	octetString = nsKey[1][1][1][1]

	globalSalt = keyDict['global-salt']
	passwd = keyDict['global-salt'] + password
	saltedPasswd = x509.SHA1(passwd, 0, len(passwd))
	key = entrySalt + saltedPasswd
	rc4Key = x509.MD5(key, 0, len(key))
	data = x509.RC4(rc4Key, octetString, 0, len(octetString))
	pkcs1 = asn1.decode(data)
	keyData = pkcs1[0][1][2][1]
	return x509.PrivateKey('rsa', keyData, 0, len(keyData))

def extractCert(inFile):
	db = bsddb.hashopen(inFile, 'r')
	nameDict = {}
	certDict = {}
	try:
		key, value = db.first()
		while 1:
			type = ord(key[0])
			key = key[1:]
			if type == 1:
				certDict[key] = value
			elif type == 2:
				nameDict[key] = value
			key, value = db.next()
	except KeyError:
		db.close()
	subject = nameDict['Server-Cert\0'][5:]
	value = certDict[subject]
	h = asn1.header(value, 10)
	dataOffset = h[4]
	dataLength = h[3]
	length = dataOffset + dataLength - 10
	return x509.Certificate(value, 10, length)

if __name__ == '__main__':
	import getpass
	import os
	cert = extractCert('/usr/local/suitespot/alias/SACS-00-cert.db')
	cert.writePEM('SACS-00-cert.pem')
	password = getpass.getpass('Private Key Password: ')
	key = extractKey('/usr/local/suitespot/alias/SACS-00-key.db', password)
	outFile = 'SACS-00-key.pem'
	key.writePEM(outFile, password)
	os.chmod(outFile, 0600)
