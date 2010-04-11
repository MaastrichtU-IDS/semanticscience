# Copyright (c) 2000-2003 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: help.py 27169 2009-03-14 05:57:23Z gregc $

"""
Chimera GUI Help Support

Help should be registered for all modeless dialogs.
Registering help makes 'help on context' work.
Specific help can be registered for widgets within the dialog.

Chimera does not support help in modal dialogs.
"""
import sys, os
import urllib, urlparse
import weakref
import chimera
import replyobj

_balloonWidget = None

_helpMap = weakref.WeakKeyDictionary()

def display(widgetOrURL, package=chimera, newWindow=False):
	"""Display given html help file.

	display(widgetOrURL, package=chimera, newWindow=False) => None
	
	The url may be either a string, or a "widget" that has been
	registered.  In the latter case it is mapped according to
	how it was registered.
	"""
	try:
		# compensate for Pmw megawidgets not being Tk widgets
		widgetOrURL = widgetOrURL.component('hull')
	except:
		pass
	if isinstance(widgetOrURL, basestring):
		url = widgetOrURL
	elif hasattr(widgetOrURL, 'winfo_parent'):
		# show help associated with widget or parent widget
		while widgetOrURL:
			if _helpMap.has_key(widgetOrURL):
				url, package = _helpMap[widgetOrURL]
				break
			parent = widgetOrURL.winfo_parent()
			if not isinstance(parent, str):
				widgetOrURL = parent
			elif parent == "":
				widgetOrURL = None
			else:
				widgetOrURL = widgetOrURL._nametowidget(parent)
		if not widgetOrURL:
			replyobj.warning('internal error -- no help found for widget\n')
			return
	elif isinstance(widgetOrURL, tuple):
		url, package = widgetOrURL
		if isinstance(package, basestring):
			package = __import__(package)
	else:
		replyobj.warning("internal error -- no help avaiable for: %s\n" % widgetOrURL)
		return
	protocol, location, path, parameters, query, fragment = \
		urlparse.urlparse(url, allow_fragments=True)
	path = urllib.quote(path)
	parameters = urllib.quote(parameters)
	query = urllib.quote(query)
	fragment = urllib.quote(fragment)
	if path and path[0] != '/':
		file = os.path.join(package.__path__[0], "helpdir", path)
		if os.path.exists(file):
			protocol = 'file'
			if sys.platform == 'darwin':
				#
				# Setting location to localhost is needed on
				# Mac OS X with Internet Explorer because
				# urlunparse() produces urls like
				# file:/index.blah instead of
				# file:///index.html or
				# file://localhost/index.html
				# required by the browser.
				#
				location = 'localhost'
			path = urllib.pathname2url(file)
			if path[0:3] == '///':
				path = path[2:]
			url = urlparse.urlunparse((protocol, location,
							path, parameters,
							query, fragment))
		else:
			# Fetch development version of docs -- a released
			# version would have the help files included.
			protocol = 'http'
			url = urlparse.urljoin(
				'http://www.cgl.ucsf.edu/chimera/docs/', url)
	replyobj.status("See web browser for %s\n" % url, blankAfter=10)
	import webbrowser
	try:
		webbrowser.open(url, newWindow)
	except webbrowser.Error:
		from chimera import NonChimeraError
		raise NonChimeraError("Could not locate a web browser to use.\n"
			"\nTry setting your BROWSER environment variable to\n"
			"the command-line name of the web browser you want\n"
			"to use and restart Chimera.")
	except OSError, e:
		from chimera import NonChimeraError
		import errno
		if e.errno == errno.ENOENT:
			if protocol == 'file' \
			and not os.path.exists(urllib.url2pathname(path)):
				raise
			# Bug starting webbrowser (firefox, bug 1512),
			# Windows usually opens it eventually
			raise NonChimeraError(
				"Error or delay starting default web browser.\n"
				"\n"
				"Wait a little and if the default web browser\n"
				"doesn't start up, start it by hand, and try\n"
				"again.")
		raise NonChimeraError("Unable to start web browswer.\n"
				"Open <%s> in your web browswer.\n"
				"(%s)" % (path, e))

def contextCB(app):
	"""Display help for selected widget.
	
	contextCB(app) => None
	"""
	rootX, rootY = chimera.viewer.trackingXY("help")
	if rootX != -1:
		# find widget that was under cursor
		widget = app.winfo_containing(rootX, rootY)
		if widget:
			widget.event_generate('<<Help>>', rootx=rootX,
								rooty=rootY)
			return
	replyobj.warning('pick part of application to get context help\n')

def _showHelp(event):
	display(event.widget)
	return 'break'

_firstTime = True
def register(widget, urlAndPackage=None, balloon=None):
	"""Register URL for context sensitive help.
	
	register(widget, urlAndPackage, balloon) => None

	urlAndPackage -- can be a URL or (URL, package)
	balloon -- balloon help text

	While it is expected that the widget argument will be a (Tk) widget,
	it can be any python object.
	"""
	try:
		# compensate for Pmw megawidgets not being Tk widgets
		widget = widget.component('hull')
	except:
		pass
	global _firstTime
	if _firstTime:
		_firstTime = False
		widget.event_add('<<Help>>', '<Key-F1>', '<Help>')
	if urlAndPackage:
		global _helpMap
		if isinstance(urlAndPackage, tuple):
			url, package = urlAndPackage
		else:
			url = urlAndPackage
			package = chimera
		_helpMap[widget] = (url, package)
		widget.bind('<<Help>>', _showHelp)
		# TODO: in debug mode, validate the url
	if balloon and _balloonWidget:
		_balloonWidget.bind(widget, balloon)

def dump(dumpfile):
	"""dump contents of help map to file"""
	for url, package in _helpMap.itervalues():
		protocol, location, path, parameters, query, fragment = \
			urlparse.urlparse(url)
		if path and path[0] != '/':
			file = os.path.join(package.__path__[0], "helpdir",
									path)
			if os.path.exists(file):
				protocol = 'file'
				path = urllib.pathname2url(file)
				if path[0:3] == '///':
					path = path[2:]
				url = urlparse.urlunparse((protocol, location,
							path, parameters,
							query, fragment))
			else:
				url = urlparse.urljoin(
					'http://www.cgl.ucsf.edu/chimera/docs/',
					url)
		print >> dumpfile, url
