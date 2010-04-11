# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import string
import os
import stat
import threading

PasswordFile = '/usr/local/www/cgl/public/datadocs/chimera/regpasswd'

lastChange = 0
password = ''
sem = None

def setup():
	global sem
	if sem is None:
		sem = threading.Semaphore(1)

def RegistrationPassword():
	global password
	global lastChange
	s = os.stat(PasswordFile)
	sem.acquire()
	if s[stat.ST_MTIME] != lastChange:
		f = open(PasswordFile)
		password = string.strip(f.readline())
		f.close()
		lastChange = s[stat.ST_MTIME]
	sem.release()
	return password
