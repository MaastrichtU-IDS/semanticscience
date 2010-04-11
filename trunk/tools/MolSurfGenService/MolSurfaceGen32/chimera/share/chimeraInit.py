"""module to initialize chimera environment

--- UCSF Chimera Copyright ---
Copyright (c) 2000 Regents of the University of California.
All rights reserved.  This software provided pursuant to a
license agreement containing restrictions on its disclosure,
duplication and use.  This notice must be embedded in or
attached to all copies, including partial copies, of the
software or any revisions or derivations thereof.
--- UCSF Chimera Copyright ---
"""
__rcsid__ = "$Id: chimeraInit.py 28729 2009-09-02 21:41:34Z gregc $"

# TODO: support some of the Xt arguments below on Posix platforms
#XtArgs = [
#	"+rv",
#	"+synchronous",
#	("-background", "*background"),
#	("-bd",         "*borderColor"),
#	("-bg",         "*background"),
#	("-bordercolor","*borderColor"),
#	("-borderwidth",".borderWidth"),
#	("-bw",         ".borderWidth"),
#	("-display",    ".display"),
#	("-fg",         "*foreground"),
#	("-fn",         "*font"),
#	("-font",       "*font"),
#	("-foreground", "*foreground"),
#	("-geometry",   ".geometry"),
#	"-iconic",
#	("-name",       ".name"),
#	"-reverse",
#	"-rv",
#	("-selectionTimeout", ".selectionTimeout"),
#	"-synchronous",
#	("-title",      ".title"),
#	("-xnllanguage",".xnlLanguage"),
#	("-xrm",        ""),
#	("-xtsessionID",".sessionID"),
#]

def _findRoot():
	# New _findRoot() logic: we hard code the installation location
	# of chimera.
	import os
	try:
		root = os.environ["CHIMERA"]
	except KeyError:
		raise RuntimeError, "can not find chimera installation directory"
	return root

def init(argv, nogui=False, nomultisample=None, stereo=False, bgopacity=False,
		visual=None, screen=None, root=None, debug=False,
		geometry=None, title=None, eventloop=True, exitonquit=True,
		nostatus=False, preferencesFile=None, fullscreen=False,
		script=None, silent=False):
	"""initialize chimera environment

	optional arguments:

	nogui -- if set, don't start GUI.
	visual -- Tk visual, eg 'pseudocolor 12' or 'truecolor'.
	screen -- screen number if different than default.
	root -- root of chimera installation tree.
	debug -- if set, don't redirect standard error.
	preferencesFile -- path to preferences file to use
	"""

	import sys, os, traceback, getopt
	ARGS = [
		"--help",
		"--nogui",
		"-n",
		"--nostatus",
		"--silent",
		"--nomultisample",
		"--fullscreen",
		"-f",
		"--stereo",
		"--reverse-stereo",
		"--bgopacity",
		"--geometry wxh+x+y",
		"--title title",
		"--start <extension name>",
		"--pypath <directory>",
		"-P <directory>",
		"--send <file>",
		"--preferences <file>",
		"--visual <visual>",
		"--screen <screen>",
		"--script <python-code>",
		"--root",
		"--release",
		"--version",
		"--listfiletypes",
		"--opt",
		"--debug",
		"--debug-opengl",
	]
	if sys.platform.startswith("win"):
		ARGS.extend(["--console", "--noconsole"])
	USAGE = '[' + "] [".join(ARGS) + ']'
	# add in default argument values
	ARGS += [
		"--gui",
		"--status",
		"--nosilent",
		"--multisample",
		"--nofullscreen",
		"--nostereo",
		"--nobgopacity",
		"--nodebug",
		"--nodebug-opengl",
		"--noreverse-stereo",
	]
	# emulate "python -m py_compile module" for aqua
	ARGS += [ "-m pymodule" ]

	try:
		shortopts = ""
		longopts = []
		for a in ARGS:
			if a.startswith("--"):
				i = a.find(' ')
				if i == -1:
					longopts.append(a[2:])
				else:
					longopts.append(a[2:i] + '=')
			elif a.startswith('-'):
				i = a.find(' ')
				if i == -1:
					shortopts += a[1]
				else:
					shortopts += a[1] + ':'
		optlist, args = getopt.getopt(argv[1:], shortopts, longopts)
	except getopt.error, message:
		sys.stderr.write(argv[0] + ": " + str(message) + '\n')
		sys.stderr.write("usage: %s %s\n" % (argv[0], USAGE))
		return 2

	printRelease = False
	printVersion = False
	printRoot = False
	startExtensions = []
	pathAdditions = []
	listFileTypes = False
	send = None
	debug_opengl = False
	reverseStereo = False
	pymodule = ""
	for o in optlist:
		if o[0] == "--send":
			send = o[1]
		elif o[0] == "-m":
			pymodule = o[1]
		elif o[0] in ("-n", "--nogui"):
			nogui = True
		elif o[0] == "--gui":
			nogui = False
		elif o[0] in ("-f", "--fullscreen"):
			fullscreen = True
		elif o[0] == "--nofullscreen":
			fullscreen = False
		elif o[0] in "--geometry":
			geometry = o[1]
		elif o[0] in "--title":
			title = o[1]
		elif o[0] == "--nomultisample":
			nomultisample = True
		elif o[0] == "--multisample":
			nomultisample = False
		elif o[0] == "--nostatus":
			nostatus = True
		elif o[0] == "--status":
			nostatus = False
		elif o[0] == "--silent":
			nostatus = True
			silent = True
		elif o[0] == "--nosilent":
			nostatus = False
			silent = False
		elif o[0] == "--stereo":
			stereo = True
		elif o[0] == "--nostereo":
			stereo = False
		elif o[0] == "--reverse-stereo":
			reverseStereo = True
		elif o[0] == "--noreverse-stereo":
			reverseStereo = False
		elif o[0] == "--bgopacity":
			bgopacity = True
		elif o[0] == "--nobgopacity":
			bgopacity = False
		elif o[0] == "--debug":
			debug = True
		elif o[0] == "--nodebug":
			debug = False
		elif o[0] == "--debug-opengl":
			debug_opengl = True
		elif o[0] == "--nodebug-opengl":
			debug_opengl = False
		elif o[0] == "--start":
			startExtensions.append(o[1])
		elif o[0] == "--script":
			script = o[1]
		elif o[0] in ("-P", "--pypath"):
			pathAdditions.append(o[1])
		elif o[0] in "--visual":
			visual = o[1]
		elif o[0] in "--screen":
			screen = o[1]
		# query options:
		elif o[0] == "--root":
			nogui = True
			printRoot = True
		elif o[0] == "--release":
			printRelease = True
		elif o[0] == "--version":
			printVersion = True
		elif o[0] == "--listfiletypes":
			nogui = True
			listFileTypes = True
		elif o[0] == "--preferences":
			preferencesFile = o[1]
		elif o[0] == "--help":
			sys.stderr.write("usage: %s %s\n" % (argv[0], USAGE))
			return 0
		# --opt (run python -O) is caught by startup script
		# --console and --noconsole are for the Window startup code

	if pymodule:
		assert pymodule == 'py_compile'
		sys.argv = [pymodule] + args
		main = __import__(pymodule)
		main.main()
		raise SystemExit

	# Figure out which chimera installation tree to use, and tell
	# python where the chimera system python modules are found.

	dataRoot = None
	if not root:
		try:
			root = _findRoot()
			dataRoot = os.environ["CHIMERADATA"]
		except RuntimeError, e:
			print >> sys.stderr, "Error starting chimera:", e
			raise SystemExit, 1
		except KeyError:
			pass
	if not dataRoot:
		dataRoot = os.path.join(root, "share")

	# prepend machine-dependent directory for shared library modules
	import site
	savePath = sys.path
	sys.path = []
	site.addsitedir(os.path.join(root, "lib"))
	sys.path.extend(savePath)
	del savePath

	# In debug mode '.' is at front of path, otherwise place
	# it at the end. Remove the other occurances first.
	while '' in sys.path > 0:
		sys.path.remove('')
	while '.' in sys.path > 0:
		sys.path.remove('.')
	if debug:
		sys.path.insert(0, os.getcwd())	# put it back
	else:
		sys.path.append(os.getcwd())

	# prepend 'pypath' directories
	pathAdditions.reverse()
	for pa in pathAdditions:
		sys.path.insert(0, pa)

	# Setup additional environment variables:
	if sys.platform == 'win32':
		# try to find a "HOME" directory on Window for .files.
		if not os.environ.has_key("HOME"):
			import _winreg
			try:
				h = _winreg.OpenKeyEx(_winreg.HKEY_CURRENT_USER,
	"SOFTWARE\\Microsoft\\Windows\\CurrentVersion\\Explorer\\Shell Folders",
					0, _winreg.KEY_QUERY_VALUE)
				v = _winreg.QueryValueEx(h, "AppData")
				os.environ["HOME"] = v[0].encode('mbcs')
			except WindowsError:
				# presumably Win98
				os.environ["HOME"] = "C:\\WINDOWS\\Application Data"
		# On Windows, we need to remove the bin directory from
		# the Python path (because "import zlib" might get the
		# dll instead of the pyd).
		rpath = os.path.realpath(os.path.join(root, "bin")).lower()
		curdir = os.path.realpath(os.getcwd()).lower()
		for p in sys.path[:]:
			try:
				if p == "":
					r = curdir
				else:
					# cleanup Windows filenames
					r = os.path.realpath(p).lower()
					if r[-1] == '\\':
						r = r[0:-1]
					r = r.replace('progra~1', 'program files')
				if r == rpath:
					sys.path.remove(p)
			except OSError:
				pass
		# make sure rpath is on PATH, so dlls will be found
		if os.environ.has_key("PATH"):
			rpath += os.pathsep + os.environ["PATH"]
		os.environ["PATH"] = rpath
		del rpath, curdir

	if send:
		import send_to_chimera
		msg = send_to_chimera.send(send)
		if msg == 'SENT':
			# successfully sent send argument to a running chimera
			raise SystemExit, 0
		else:
			print >> sys.stderr, msg
			raise SystemExit, 1

	if printRelease:
		from chimera.version import release
		print release
		raise SystemExit, 0
	if printVersion:
		from chimera.version import version
		print 'chimera', version
		raise SystemExit, 0
	if printRoot:
		print root
		raise SystemExit, 0

	if sys.platform in ['linux2', 'irix646', 'irix6-n32']:
		# make C++ shared libraries work when dlopen'd
		import dl
		sys.setdlopenflags(sys.getdlopenflags() | dl.RTLD_GLOBAL)

	# now startup chimera
	import chimera
	if chimera.opengl_platform() == 'OSMESA':
		# we only want the graphics, not the gui
		nogui = True
	chimera.visual = visual
	chimera.screen = screen
	chimera.debug = debug
	chimera.nogui = nogui
	chimera.nomultisample = nomultisample
	chimera.nostatus = nostatus
	chimera.silent = silent
	chimera.stereo = stereo
	chimera.setReverseStereo(reverseStereo)
	chimera.bgopacity = bgopacity
	chimera.geometry = geometry
	chimera.preferencesFile = preferencesFile
	if title:
		chimera.title = title
	chimera.fullscreen = fullscreen
	from chimera import replyobj

	if nogui:
		chimera.initializeGraphics()
		chimera._postGraphics = True
	else:
		from chimera import splash
		splash.create()

		from chimera import tkgui
		tkgui.initializeGUI(exitonquit, debug_opengl)
		chimera.viewer = tkgui.app.viewer
	chimera.registerOSLTests()
	if not nogui:
		replyobj.status('initializing extensions')
	from chimera import extension
	extension.setup()

	if listFileTypes:
		catTypes = chimera.fileInfo.categorizedTypes()
		categories = sorted(list(catTypes.keys()))
		print "category:"
		print "\tfile type: prefix: suffixes"
		print
		for c in categories:
			types = catTypes[c]
			types.sort()
			print '%s:' % c
			for t in types:
				print "\t%s: %s: %s" % (t,
					', '.join(chimera.fileInfo.prefixes(t)),
					', '.join(chimera.fileInfo.extensions(t)))
		raise SystemExit, 0

	if not nogui:
		extraArgs = tkgui.finalizeGUI()
		args.extend(extraArgs)
	extension.startup(startExtensions)
	for extName in startExtensions:
		replyobj.error(
			"Starting extension '%s' failed\n" % extName)

	from chimera import registration
	registration.checkRegistration()

	if not nogui:
		tkgui.periodicCheckForNewerChimera()
		tkgui.setInitialWindowSize()

	# flush NoGuiViewer and any other initialization cruft
	track = chimera.TrackChanges.get()
	track.clear()

	# execute optional scripts
	if script:
		sys.argv = [script] + args
		args = [script]
	return_value = 0
	for a in args:
		try:
			try:
				chimera.openModels.open(a, prefixableType=1)
			except IOError, value:
				# so that we don't get bug reports when
				# people mistype file names
				raise chimera.UserError(value)
		except SystemExit, value:
			return value
		except:
			replyobj.reportException(
					"Error while processing %s" % a)
			return_value = 1

	if nogui:
		from chimera import triggers, APPQUIT, fileInfo
		if not script:
			if args:
				fileType = fileInfo.processName(args[-1])[0]
			else:
				fileType = None
			if fileInfo.category(fileType) != fileInfo.SCRIPT:
				extension.startup(["ReadStdin"])
		triggers.activateTrigger(APPQUIT, None)
		return return_value
	if eventloop:
		# run user interface
		try:
			try:
				tkgui.eventLoop()
			except KeyboardInterrupt:
				pass
		finally:
			pass	# TODO: do exit procedures (e.g., grail stuff)
	else:
		# start monitoring for data changes
		from chimera import update
		update.startFrameUpdate(tkgui.app)
	return return_value
