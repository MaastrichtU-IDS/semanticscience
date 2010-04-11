# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import string
import whrandom
import time
import os

import x509

#
# Protocol for registration is (C=client, S=server):
#	S->C	Challenge (encrypted random string)
#	C->S	Response (decrypted challenge)
#	S->C	Status (accept/reject)
#	C->S	Registration data
#	S->C	Signed S/MIME message
#		repeat last two steps
#	C->S	Close connection
#

CharSet = 'abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ0123456789'

def challengeSend(f, password):
	cList = []
	for i in range(16):
		cList.append(whrandom.choice(CharSet))
	challenge = string.join(cList, '')
	f.write('%s\n' % x509.RC4(password, challenge, 0, len(challenge)))
	f.flush()
	return challenge

def challengeRecv(f):
	line = f.readline()
	if not line:
		return None
	return line[:-1]

def responseSend(f, challenge, password):
	f.write('%s\n' % x509.RC4(password, challenge, 0, len(challenge)))
	f.flush()

def responseRecv(f):
	return challengeRecv(f)

def statusSend(f, okay):
	f.write('%d\n' % okay)
	f.flush()

def statusRecv(f):
	line = f.readline()
	if not line:
		return None
	return string.atoi(line)

def dataSend(f, data):
	if data[-1] != '\n':
		data = data + '\n'
	numLines = string.count(data, '\n')
	f.write('%d\n' % numLines)
	f.write(data)
	f.flush()

def dataRecv(f):
	line = f.readline()
	if not line:
		return None
	numLines = string.atoi(line)
	data = []
	for i in range(numLines):
		data.append(f.readline())
	return string.join(data, '')

def smimeSend(f, smime):
	return dataSend(f, smime)

def smimeRecv(f):
	return dataRecv(f)

whrandom.seed(int(time.time()) % 256, os.getpid() % 256, os.getppid() % 256)
