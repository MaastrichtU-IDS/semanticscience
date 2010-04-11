# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: SubprocessMonitor.py 28562 2009-08-19 00:20:51Z gregc $

from chimera import baseDialog
from subprocess import PIPE, STDOUT, MAXFD
import sys

class SubprocessProgress(baseDialog.ModelessDialog):
	"""monitor a process and show its progress

	Provide a SubprocessMonitor.Popen interface so a dialog instance
	may be handed to code that is expecting a Subprocess.Popen
	return value.
	"""

	title = "Monitoring progress"
	buttons = ('Abort')

	def __init__(self, text, subproc, afterCB=None, *args, **kw):
		self._handler = None
		self._subproc = subproc
		self._grabbed = False
		self._aborted = False
		self._after = afterCB
		self.returncode = None
		if isinstance(text, basestring):
			self._text = text
		else:
			self._text = ' '.join(text)
		baseDialog.ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		import Tkinter
		text = Tkinter.Label(parent, text=self._text)
		text.pack()
		from CGLtk import Progress
		self._progressBar = Progress.Progress(parent, maximum=1.0)
		self._progressBar.pack(ipadx=2, ipady=2, fill='x', expand=1)

	def map(self, event=None):
		"""Turn on tracking of subprocess"""
		import chimera
		self._handler = chimera.triggers.addHandler(
				'check for changes', self._update, None)

	def unmap(self, event=None):
		"""Turn off tracking of subprocess"""
		handler = self._handler
		self._handler = None
		if handler:
			import chimera
			chimera.triggers.deleteHandler('check for changes',
								handler)

	def poll(self):
		return self._subproc.poll()

	def _modalWait(self):
		self._update(None, None, None)
		if self.returncode is None and self._subproc is not None:
			from chimera.update import UPDATE_INTERVAL
			self._toplevel.after(UPDATE_INTERVAL, self._modalWait)

	def wait(self):
		baseDialog.ModelessDialog.enter(self)
		self._toplevel.grab_set()
		self._grabbed = True
		from chimera.update import UPDATE_INTERVAL
		self._toplevel.after(UPDATE_INTERVAL, self._modalWait)
		self._toplevel.mainloop()
		if self._aborted:
			from chimera import NonChimeraError
			raise NonChimeraError("Raytrace cancelled by user")
		return self.returncode

	def _update(self, trigger, closure, ignored):
		if not self._subproc:
			return
		progress = self._subproc.progress()
		self.returncode = self._subproc.poll()
		if self.returncode is not None:
			self.Cancel()
			return
		self._progressBar.set(progress)

	def Abort(self):
		# kill/terminate process
		if self._subproc:
			# workaround bug 6451 (_subproc should never be None)
			self._aborted = True
			self._subproc.terminate()
		self.Cancel()

	def Cancel(self, value=None):
		self._subproc = None
		if self._grabbed:
			self._toplevel.grab_release()
			self._toplevel.quit()
		baseDialog.ModelessDialog.Cancel(self)
		if self._after:
			self._after(self._aborted)

class SubprocessTask:
	"""monitor a process and show its progress as a Chimera task

	Provide a SubprocessMonitor.Popen interface so an instance
	may be handed to code that is expecting a Subprocess.Popen
	return value.
	"""

	def __init__(self, text, subproc, task=None, afterCB=None, *args, **kw):
		from tasks import Task
		self._subproc = subproc
		self._aborted = False
		if not isinstance(text, basestring):
			text = ' '.join(text)
		if task is None:
			self._ownTask = True
			self._task = Task(text, self.cancelCB, self.statusCB)
			self._text = ""
		else:
			self._ownTask = False
			task.addCallbacks(self.cancelCB, self.statusCB)
			self._task = task
			self._text = text
		self._after = afterCB
		self.returncode = None

	def poll(self):
		return self._subproc.poll()

	def wait(self):
		import chimera
		from chimera import tkgui
		from chimera.update import UPDATE_INTERVAL
		from time import sleep
		interval = UPDATE_INTERVAL / 1000.0	# msec -> sec
		self.statusCB()
		while self.returncode is None and not self._aborted:
			sleep(interval)
			self.statusCB()
			tkgui.update_windows()
		if self._aborted:
			from chimera import NonChimeraError
			raise NonChimeraError("Raytrace cancelled by user")
		return self.returncode

	def statusCB(self):
		if not self._subproc:
			return
		progress = self._subproc.progress()
		self.returncode = self._subproc.poll()
		if self.returncode is not None:
			self.finished()
			return
		if self._text:
			msg = "%s: %d%% complete" % (self._text,
							int(progress * 100))
		else:
			msg = "%d%% complete" % int(progress * 100)
		self._task.updateStatus(msg)

	def cancelCB(self):
		print "SubprocessTask canceled"
		# kill/terminate process
		if self._subproc:
			# workaround bug 6451 (_subproc should never be None)
			self._subproc.terminate()
		self._aborted = True
		self.finished()

	def finished(self, value=None):
		if self._aborted:
			status = "aborted"
		else:
			status = "completed"
		if self._text:
			msg = "%s: %s" % (self._text, status)
		else:
			msg = status
		self._task.updateStatus(msg)
		if self._ownTask:
			self._task = None
		else:
			self._task.removeCallbacks(self.cancelCB, self.statusCB)
		self._subproc = None
		if self._after:
			self._after(self._aborted)

import subprocess
class Popen(subprocess.Popen):
	"""Add terminate and progress methods to subprocess.Popen"""

	def __init__(self, *args, **kw):
		import os
		self._daemon = kw.get('daemon', False)
		if 'daemon' in kw:
			del kw['daemon']
		self._progress = kw.get('progressCB', False)
		if 'progressCB' in kw:
			del kw['progressCB']
		self._terminate = kw.get('terminateCB', False)
		if 'terminateCB' in kw:
			del kw['terminateCB']
		if sys.platform == 'win32':
			# on Windows, if you redirect one, you have to
			# redirect them all.
			stdin = kw.get('stdin', None)
			stdout = kw.get('stdout', None)
			stderr = kw.get('stderr', None)
			if stdin or stdout or stderr:
				if not stdin:
					kw['stdin'] = PIPE
				if not stdout:
					kw['stdout'] = PIPE
				if not stderr:
					kw['stderr'] = PIPE
		if self._daemon:
			if os.name == 'posix':
				kw['close_fds'] = True
				# do non-POSIX systems support setsid?
				setsid = getattr(os, 'setsid', None)
				if not setsid:
					setsid = getattr('setpgrp', None)
				kw['preexec_fn'] = setsid
			elif os.name == 'nt' and 'creationflags' not in kw:
				# Windows
				CREATE_NEW_PROCESS_GROUP = 0x00000200
				CREATE_NO_WINDOW = 0x08000000
				kw['creationflags'] = CREATE_NEW_PROCESS_GROUP|CREATE_NO_WINDOW

		# TODO: check path of program to be started by Popen,
		# if it isn't in CHIMERA/bin, then remove the chimera
		# directories from the PATH and LD_LIBRARY_PATH (and
		# restore them afterwards).
		subprocess.Popen.__init__(self, *args, **kw)
		if sys.platform == 'win32' and (stdin or stdout or stderr):
			if not stdin:
				self.stdin.close()
			if not stdout:
				self.stdout.close()
			if not stderr:
				self.stderr.close()

	def terminate(self):
		"""kill/terminate process"""
		if self._terminate:
			self._terminate()
			self._terminate = None
			return
		import os
		if self._daemon and hasattr(os, 'killpg'):
			from signal import SIGKILL
			os.killpg(self.pid, SIGKILL)
		elif hasattr(os, 'kill'):
			from signal import SIGKILL
			os.kill(self.pid, SIGKILL)
		else:
			# assume it's Windows (sys.platform == 'win32')
			# and assume Windows XP
			import subprocess
			subprocess.call(("TASKKILL", "/PID",
						str(self.pid), "/F", "/T"))

	def setTerminate(self, terminate):
		self._terminate = terminate

	def progress(self):
		"""return progress
		
		0 is "nothing done yet", .5 is "half done", and 1 is finished"""
		if self._progress:
			return self._progress(self)
		else:
			if self._daemon or self.poll() == None:
				return 1
			return 0

	def setProgress(self, progress):
		self._progress = progress

def call(*args, **kw):
	"""replacement for subprocess.call that fixes up runtime paths"""
	# identical to subprocess.call
	return Popen(*args, **kw).wait()

def monitor(text, subproc, task=None, *args, **kw):
	import chimera
	if chimera.nogui:
		import time
		while 1:
			returncode = subproc.poll()
			if returncode is not None:
				break
			progress = subproc.progress()
			sys.stdout.write('\r%g%% done' % (progress * 100))
			if progress == 1:
				sys.stdout.write('\n')
				return
			time.sleep(1)
		return
	# gui mode
	#return SubprocessProgress(text, subproc, *args, **kw)
	return SubprocessTask(text, subproc, task=task, *args, **kw)

if __debug__:
	def guiTest():
		def percent(count):
			for i in xrange(count + 1):
				yield i / float(count)
		def callback(p=percent(150)):
			try:
				return p.next()
			except StopIteration:
				return 1
		global save
		if sys.platform == 'win32':
			cmd = 'pause'
		else:
			cmd = 'sleep 100'
		subproc = Popen(cmd, shell=True, progressCB=callback)
		Hubproc = SubprocessProgress('runing "%s"' % cmd, subproc,
				        title="SubprocessProgress test")
