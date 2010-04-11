# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

# -----------------------------------------------------------------------------
# Show Python integrated development environment (IDLE) window.
#
# Copied this stuff from IDLE PyShell main() leaving out commandline
# argument parsing.
#
# I also commented out two lines in IDLE 0.5 PyShell.py that set
# Tkinter._default_root to None since this causes creation of some
# Chimera top level windows to fail.
#
# I also commented out a line from IDLE 0.5 FileList.py that calls
# Tkinter quit() when last IDLE window is closed.
#
# Sent email to idle-dev@python.org suggesting fixes for these problems.
#
# ----------------------------------------------------------------------------
# UPDATE 1/05
#
# In the process of updating to Python 2.4, we are now
# using the version of Idle that comes bundled with Python, as opposed to
# keeping our own copy of Idle in chimera/share/Idle/idle8
#
# The first comment from above is no longer valid. We now save a reference
# to Tkinter._default_root, call PyShell.begin (which sets _default_root to
# None), then restore the ref.
#
# The second comment is also not exactly true, because we don't have easy
# access to that FileList.py file any more; it is in the chimera/lib/python2.4/lib
# directory, not in share/Idle/idle8 . So I've subclassed the PyShellFileList class 
# below as noQuitPyShellFileList, overrode the offending function, and 
# commented out the appropriate code.
#
# In addition, the move to the native Idle required several more changes in the code:
#
# (1) Instead of using a plain-old-Toplevel window to house the new
#     interpreter window, the new Idle uses a 'ListedToplevel' window, 
#     which attempts to call self.quit() when it exits, which would quit Chimera. 
#     I've subclassed this class, as a 'noQuitListedToplevel' with that code
#     commented out (this was a similar problem as occurred in FileList.py, described) 
#     above
#
# (2) I also needed to add a couple of global variables to PyShell ('use_subprocess')
#     and also define sys.ps1, which are normally defined at the top level in
#     the PyShell module
#


# Use Chimera root window so that IDLE windows are iconified
# when Chimera is iconified.
#
import chimera
root = chimera.tkgui.app

import os

import Tkinter

## need to figure out how to do configuration
## with new scheme...
#IdleConf.load(os.path.join(os.path.dirname(__file__), 'idle8'))

# defer importing Pyshell until IdleConf is loaded

from chimera.replyobj import pushReply, popReply

from idlelib import PyShell, WindowList

## keep a reference to the ListedToplevel class
oldListedToplevel = WindowList.ListedToplevel

## define a subclass of the 'old' ListedToplevel class
class noQuitListedToplevel(oldListedToplevel):
	def __init__(self, *args, **kw):
		## call the __init__ on the 'old' class, not
		## WindowList.Toplevel (which will have been assigned
		## the 'noQuit...' class by the time this
		## code is called. What ?!?
		oldListedToplevel.__init__(self, *args, **kw)

	def destroy(self):
		WindowList.registry.delete(self)
		Tkinter.Toplevel.destroy(self)

		## commented out on purpose - don't want to quit
		## Tkinter's mainloop
		# If this is Idle's last window then quit the mainloop
		# (Needed for clean exit on Windows 98)
		#if not registry.dict:
		#	self.quit()

## make sure that WindowList will use the ListedToplevel that won't
## quit out of Chimera!
WindowList.ListedToplevel = noQuitListedToplevel

## need to define this so Idle will run. *Don't* execute Idle
## commands in a Python subprocess. 
PyShell.use_subprocess= False

class _myPyShell(PyShell.PyShell):
	# overload __init__ and __del__ to grab and restore output/error
	# redirection within the context of Chimera
	def __init__(self, *args, **kw):
		apply(PyShell.PyShell.__init__, (self,) + args, kw)
		self.__replyState = pushReply(None, False, False)

	def begin(self):
		try:
			import sys
			sys.ps1
		except AttributeError:
			sys.ps1 = ">>> "

		## save a reference to _default_root, because
		## PyShell.begin will set this to None
		root = Tkinter._default_root
		PyShell.PyShell.begin(self)
		## restore Tkinter._default_root
		Tkinter._default_root = root
		self.interp.runsource('import chimera')
		self.write('import chimera\n')
		self.showprompt()
	
	def runit(self):
		from chimera import update
		update.withoutChecks(lambda s=self: PyShell.PyShell.runit(s))
	def close(self, *args, **kw):
		ret = apply(PyShell.PyShell.close, (self,) + args, kw)
		popReply(self.__replyState)
		return ret


class noQuitPyShellFileList(PyShell.PyShellFileList):

	def close_edit(self, edit):
		try:
		    key = self.inversedict[edit]
		except KeyError:
		    print "Don't know this EditorWindow object.  (close)"
		    return
		if key:
		    del self.dict[key]
		del self.inversedict[edit]
		## commented out on purpose, so Chimera won't
		## quit when Idle exits
		#if not self.inversedict:
		#	self.root.quit()


	def open_shell(self, event=None):
		if self.pyshell:
		    self.pyshell.top.wakeup()
		else:
		    self.pyshell = _myPyShell(self)
		    
		    if self.pyshell:
			if not self.pyshell.begin():
			    return None
		return self.pyshell



PyShell.root = root
flist = noQuitPyShellFileList(root)
PyShell.flist = flist

def start_shell():
	global flist
	flist.open_shell()
