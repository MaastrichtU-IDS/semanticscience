# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: tcl_sockets.py 26655 2009-01-07 22:02:30Z gregc $

# -----------------------------------------------------------------------------
# Wrap Tcl/Tk socket mechanism.  I use Tcl/Tk sockets instead of Python
# sockets because they are automatically serviced by the Tcl event loop.
#
# TODO: Add a way to connect to a remote server and have a callback invoked
# whenever data is received.  Clean this up and make it suitable for the
# Python lib-tk distribution.

__all__ = ['Server']

class Server:
	"""Create an Internet socket that listens for incoming connections.
	The connections are detected and dispatched during the Tcl event
	loop (the Tkinter widget.mainloop()).
	"""

	def __init__(self, widget, callback, callback_data=None, port_number=0):
		# widget is need to get access to Tcl interpreter
		# callback is called when a connection is made to the
		# daemon socket and it gets two arguments: the incoming
		# socket and the given callback_data.  The port_number can
		# be give to bind to a specific port.
		self._widget = widget
		self.port_number = port_number
		self._callback = callback
		self._callback_data = callback_data

		self._cb_name = self._widget.register(self._connect_cb)
		self.socket_channel_id = self._tcl('socket', '-server',
				self._cb_name,
				'-myaddr', '127.0.0.1',
				self.port_number)

		if self.port_number == 0:
			socket_info = self._tcl('fconfigure',
					self.socket_channel_id, '-sockname')
			self.port_number = socket_info.split()[2]


	def getPortNo(self):
		return self.port_number

	def _connect_cb(self, channel_id, client_host, client_port):
		s = Client(channel_id, client_host, client_port,
				self._tcl)
		self._callback(s, self._callback_data)

	def _tcl(self, *args):
		return self._widget.tk.call(*args)

	def close(self):
		if hasattr(self, 'socket_channel_id'):
			self._tcl('close', self.socket_channel_id)
			self._widget.deletecommand(self._cb_name)
			del self.socket_channel_id
			del self._cb_name


class Client:
	"""A file-like object that wraps a Tcl channel returned by Server"""

	def __init__(self, channel_id, from_host, from_port, tcl):
		self.channel_id = channel_id
		self.from_host = from_host
		self.from_port = from_port
		self._tcl = tcl
		self._tcl('fconfigure', self.channel_id, '-buffering', 'line')
		self.closed = False
		self.name = '<tcl %s>' % channel_id
		self.mode = 'rw'
		#self.encoding = 'US-ASCII'

	def read(self, numBytes=None):
		if numBytes:
			text = self._tcl('read', self.channel_id, numBytes)
		else:
			text = self._tcl('read', self.channel_id)
		return str(text)

	def readline(self):
		text = self._tcl('gets', self.channel_id)
		return str(text)

	def write(self, data):
		self._tcl('puts', '-nonewline', self.channel_id, data)
		#DEBUG: self._tcl('flush', self.channel_id)

	def close(self):
		if not self.closed:
			self._tcl('close', self.channel_id)
			self.closed = True
