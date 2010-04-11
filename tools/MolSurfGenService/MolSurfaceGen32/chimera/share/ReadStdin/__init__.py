import Queue, threading, sys
import chimera

singleton = None

def run():
	global singleton
	if not singleton:
		singleton = ReadStdin()

class ReadStdin:

	def __init__(self):
		if chimera.nogui:
			self._readLoop()
		else:
			chimera.extension.manager.registerInstance(self)
			self._thread()

	def _readLoop(self):
		import sys
		try:
			while 1:
				sys.stdout.write("> ")
				line = sys.stdin.readline()
				if not line:
					break
				self._runCommand(line)
		except chimera.ChimeraSystemExit:
			pass

	def _thread(self):
		self.queue = Queue.Queue()
		self.handler = chimera.triggers.addHandler("check for changes",
					self._checkQueue, None)
		self.thread = threading.Thread(target=self._readStdin)
		self.thread.setDaemon(True)
		self.thread.start()
		self.executing = False

	def _checkQueue(self, trigger, closure, ignore):
		# This function is run in the main Chimera thread
		if self.executing:
			# Don't start executing another typed command
			# if we are already in the middle of one
			return
		r = chimera.replyobj.pushReply(None)
		self.executing = True
		try:
			while 1:
				try:
					cmd = self.queue.get(False)
					if not cmd:
						self.emQuit()
						break
					self._runCommand(cmd)
				except Queue.Empty:
					return
		finally:
			self.executing = False
			chimera.replyobj.popReply(r)

	def _runCommand(self, cmd):
		import sys
		if not chimera.nogui:
			print "CMD", cmd.rstrip()
		sys.stdout.flush()
		try:
			from Midas import MidasError
			from chimera.oslParser import OSLSyntaxError
			from chimera import replyobj
			try:
				chimera.runCommand(cmd)
			except (MidasError, OSLSyntaxError), v:
				replyobj.error(str(v) + '\n')
		finally:
			if not chimera.nogui:
				print "\nEND"
			sys.stdout.flush()

	def _readStdin(self):
		import sys
		while 1:
			line = sys.stdin.readline()
			if not line:
				self.queue.put("")
				break
			self.queue.put(line)
			

	def emRaise(self):
		# Do nothing
		pass

	def emHide(self):
		# Do nothing
		pass

	def emQuit(self):
		chimera.extension.manager.deregisterInstance(self)
