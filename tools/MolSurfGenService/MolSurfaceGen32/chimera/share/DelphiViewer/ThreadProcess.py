# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
File:		ThreadProcess.py
Date:		07.11.2000
Description:	Runs a separate, non-interactive process as a
		thread.  Follows the worker-thread paradigm.
	
		Once you instantiate a WorkerThread class, you must:
		1) run it.
		2) use the WorkerThread isRunning() method to check to see
		if it is done.
		

Imports:	- threading	higher-level threading 
		- time		basic timing functionality

Classes:	WorkerThread

Caveats:	Only works for command-line, non-interactive, ie non-Tkinter sub
		processes.  

Last modified:	07.11.2000 - Added.

To do:		07.11.2000 -
"""

class WorkerThread:

	def __init__(self, command, workDir=None):
		# initialize members
		import threading
		self.command = command
		self.workDir = workDir
		self.thread = threading.Thread(target=self._execute)
		self.thread.setDaemon(1)
		self.startTime = None
		self.endTime = None
		self.output = None
		self.exitStatus = None

	def __repr__(self):
		return "WorkerThread:"
	
	def _execute(self):
		# execute the command as a system call, piped to an output
		# file
		import subprocess, time
		sp = subprocess.Popen(self.command, shell=True,
					stdin=subprocess.PIPE,
					stdout=subprocess.PIPE,
					stderr=subprocess.STDOUT,
					cwd=self.workDir)
		self.stdoutData, self.stderrData = sp.communicate()
		self.exitStatus = sp.returncode
		self.endTime = time.time()
		
	def run(self):
		# "run" the thread and its corresponding command
		import time
		self.startTime = time.time()
		self.thread.start()

	def stop(self):
		import time
		self.stopTime = time.time()
		# haven't figured out how to "stop" the thread
		# maybe just kill the process and cleanup?

	def isRunning(self):
		return self.thread.isAlive()

	def isDone(self):
		return not self.thread.isAlive()


# testing stubs
	
if __name__ == '__main__':
	import Tkinter
	root = Tkinter.Tk()
	wt = WorkerThread('delphi sod.prm > sod.out', root)
	wt.run()
	root.mainloop()
