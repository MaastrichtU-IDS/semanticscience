# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import socket

import regpass
import protocol
import server

class RegistrationClient:
	"Registration client for Chimera."

	def __init__(self):
		self.password = regpass.RegistrationPassword()
		s = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
		s.connect(server.SocketName)
		self.rfile = s.makefile('rb')
		self.wfile = s.makefile('wb')
		self.socket = s
		challenge = protocol.challengeRecv(self.rfile)
		if not challenge:
			raise IOError, 'challenge protocol failure'
		protocol.responseSend(self.wfile, challenge, self.password)
		status = protocol.statusRecv(self.rfile)
		if not status:
			raise IOError, 'cannot authenticate with server'

	def __del__(self):
		try:
			self.rfile.close()
			self.wfile.close()
			self.socket.close()
		except AttributeError:
			pass

	def register(self, data):
		protocol.dataSend(self.wfile, data)
		return protocol.dataRecv(self.rfile)
