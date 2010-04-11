# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: dialogs.py 29101 2009-10-20 23:54:29Z pett $

"""
Chimera Dialog Support

Manage dialogs by name.  Typically use would be to register the
dialog class as the original display function, and reregister
the dialog instance (because dialogs typically never go away,
see baseDialog module documentation).
"""
import sys
import replyobj

_allDialogs = {}

def register(name, function, replace=0):
	"""Register dialog creation/display function
	
	The function is called with no arguments.  The function
	can also be a class, or an instance of a class.  If it
	is an instance, then the enter method is called.
	"""
	global _allDialogs
	if not replace and _allDialogs.has_key(name):
		replyobj.warning("error dialog %s already registered\n" % name)
		return

	_allDialogs[name] = function

def reregister(name, function):
	"""Reregister dialog creation/display function
	
	Same function variations allowed as in register.
	"""
	global _allDialogs
	try:
		dialog = _allDialogs[name]
		_allDialogs[name] = function
	except KeyError:
		replyobj.warning("error dialog %s missing\n" % name)

def find(name, create=0):
	"""Find the dialog instance for the given name.
	
	If the name has not been registered None is returned.

	If create is true then the dialog constructor function
	will be called if the object registered for the name is
	not an instance.
	"""
	if not _allDialogs.has_key(name):
		return None
	d = _allDialogs[name]
	if not callable(d):
		return d
	if create:
		return d()
	return None

def display(name, wait=False):
	"""Display the dialog with the given name.
	
	The registered dialog display function is called.
	If wait is true, then this function doesn't return
	until the dialog is displayed.

	The dialog instance is returned if available.
	"""
	if not _allDialogs.has_key(name):
		replyobj.warning("no known dialog named: %s\n" % name)
		return None
	dialog = find(name, create=1)
	if not callable(dialog) and hasattr(dialog, 'enter'):
		dialog.enter()
	if wait:
		import _tkinter
		import chimera.tkgui
		chimera.tkgui.update_windows()
	return dialog
