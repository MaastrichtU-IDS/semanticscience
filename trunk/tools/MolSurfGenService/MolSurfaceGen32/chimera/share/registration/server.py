# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import getpass
import time
import os
import fcntl
import SocketServer
import threading
import Queue

import NSDB
import regpass
import protocol
import x509

SocketName = '/var/run/chimera_registration'
LogName = '/usr/local/lib/chimera_registration.log'

class RegistrationRecorder:
	"Record registration data to file."

	def setParams(self, queue, log):
		self.queue = queue
		self.log = log

	def run(self):
		while 1:
			o = self.queue.get()
			try:
				fcntl.flock(self.log.fileno(), fcntl.LOCK_EX)
			except IOError:
				return
			else:
				self.log.write(o)
				self.log.write('\n')
				self.log.flush()
				fcntl.flock(self.log.fileno(), fcntl.LOCK_UN)

class RegistrationServer(SocketServer.ThreadingUnixStreamServer):
	"Registration server for Chimera."

	NSAliasDir = '/usr/local/suitespot/alias'

	def __init__(self, dbName, daemon=1, password=None):

		# Read Netscape certificate and private key databases
		if password is None:
			password = getpass.getpass('Key File Password: ')
		db = '%s/%s-key.db' % (self.NSAliasDir, dbName)
		self.key = NSDB.extractKey(db, password)
		db = '%s/%s-cert.db' % (self.NSAliasDir, dbName)
		self.cert = NSDB.extractCert(db)
		self.store = x509.CAStore()

		if daemon:
			# Fork.  Parent exits, so any waiting process will
			# continue.  Child acts as registration server.
			pid = os.fork()
			if pid < 0:
				raise OSError, 'cannot fork process'
			if pid > 0:
				raise SystemExit, 0

		# Setup recording of signed data to log file

		# Setup socket
		try:
			os.remove(SocketName)
		except os.error:
			pass
		SocketServer.ThreadingUnixStreamServer.__init__(self, 
							SocketName,
							RegistrationHandler)
		os.chmod(SocketName, 0777)

	def __del__(self):
		self.cleanup()

	def run(self):
		r = RegistrationRecorder()
		self.recorder = threading.Thread(target=r.run,
							name='Recorder')
		self.log = open(LogName, 'a')
		self.queue = Queue.Queue(0)
		r.setParams(self.queue, self.log)
		self.recorder.start()
		self.acceptor = threading.Thread(target=self.serve_forever,
						name='Acceptor')
		self.acceptor.start()
		self.recorder.join()

	def cleanup(self):
		try:
			os.remove(SocketName)
		except OSError:
			pass

class RegistrationHandler(SocketServer.StreamRequestHandler):
	"Registration handler for Chimera."

	def setup(self):
		"Override default to read registration password."

		self.password = regpass.RegistrationPassword()
		self.smime = x509.SMIME(self.server.store)
		SocketServer.StreamRequestHandler.setup(self)

	def handle(self):
		s = protocol.challengeSend(self.wfile, self.password)
		r = protocol.responseRecv(self.rfile)
		if s == r:
			protocol.statusSend(self.wfile, 1)
		else:
			protocol.statusSend(self.wfile, 0)
			return
		data = protocol.dataRecv(self.rfile)
		if not data or not self.server.recorder.isAlive():
			return
		protocol.smimeSend(self.wfile, self.sign(data))

	def sign(self, data):
		now = time.time()
		msg = 'Signed: %s\n%s' % (time.ctime(now), data)
		self.server.queue.put(msg)
		return self.smime.signString(msg, 0, len(msg),
						self.server.cert, None,
						self.server.key)
