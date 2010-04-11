# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: __init__.py 29760 2010-01-13 00:52:11Z pett $

"""
Chimera module

exports all symbols from C++ _chimera module
"""

import sys, os, errno

from _chimera import *
Coord = Point				# vestige for old code
Xform_translation = Xform.translation	# vestige for old session files
from _vrml import VRMLModel
from libgfxinfo import getVendor as opengl_vendor, getRenderer as opengl_renderer, getVersion as opengl_version, getOS as operating_system
from Sequence import getSequence, getSequences
Molecule.sequence = getSequence
Molecule.sequences = getSequences
def _labelFunc(item):
	from misc import chimeraLabel
	return chimeraLabel(item)
Atom.__str__ = _labelFunc
Bond.__str__ = _labelFunc
PseudoBond.__str__ = _labelFunc
Residue.__str__ = _labelFunc
Model.__str__ = _labelFunc
Point.__repr__ = lambda s: 'chimera.Point(%.17f, %.17f, %.17f)' % s.data()
Vector.__repr__ = lambda s: 'chimera.Vector(%.17f, %.17f, %.17f)' % s.data()
Xform.__repr__ = lambda s: 'chimera.Xform.coordFrame(%r, %r, %r, %r)' % s.getCoordFrame()
Plane.__repr__ = lambda s: 'chimera.Plane(%r, %r)' % (s.origin, s.normal)
from phipsi import getPhi, getPsi, setPhi, setPsi, \
	getChi1, getChi2, getChi3, getChi4, setChi1, setChi2, setChi3, setChi4
Residue.phi = property(getPhi, setPhi)
Residue.psi = property(getPsi, setPsi)
Residue.chi1 = property(getChi1, setChi1)
Residue.chi2 = property(getChi2, setChi2)
Residue.chi3 = property(getChi3, setChi3)
Residue.chi4 = property(getChi4, setChi4)
Residue.altLocs = property(lambda r: set([a.altLoc
							for a in r.atoms if a.altLoc.isalnum()]))

# wrap labelOffset attribute to be more "pythonic"
def getLabelOffset(item):
	""" returns 3-tuple (or None if not set)
	accepts 3-tuple, Vector, or None
	"""
	rawLO = item._labelOffset
	if rawLO.x == Molecule.DefaultOffset:
		return None
	return rawLO.data()

def setLabelOffset(item, val):
	if isinstance(val, Vector):
		item._labelOffset = val
	elif val is None:
		item._labelOffset = Vector(Molecule.DefaultOffset, 0.0, 0.0)
	else:
		item._labelOffset = Vector(*val)

for offsetClass in (Atom, Bond, Residue):
	offsetClass._labelOffset = offsetClass.labelOffset
	offsetClass.labelOffset = property(getLabelOffset, setLabelOffset)

# track session name (if any)
lastSession = None
def setLastSession(session):
	global lastSession
	lastSession = session
	if not nogui:
		tkgui._setLastSession(session)

# MSMSModel is implemented as a SurfaceModel
from MoleculeSurface import MSMSModel

# defaults for command line options
debug = False
nomultisample = None
nostatus = False	# True if no status output in nogui mode
silent = False		# True if no status/info/warning output in nogui mode
stereo = False		# True if stereo framebuffer is requested
bgopacity = False	# True if background opacity is requested
visual = None
screen = None
title = "UCSF Chimera"
geometry = None
preferencesFile = None
fullscreen = False

# default viewer
nogui = True
if opengl_platform() != 'OSMESA':
	viewer = NoGuiViewer()
else:
	viewer = LensViewer()

_postGraphicsFuncs = []
_postGraphics = False

def registerPostGraphicsFunc(func):
	"""Register a function to execute when the graphics state is ready"""

	if _postGraphics:
		# already ready
		func()
	else:
		_postGraphicsFuncs.append(func)

class ChimeraExit(Exception):
	"""Use this exception for known exit error states
	where a backtrace isn't needed.
	"""
	pass

class CancelOperation(Exception):
	"""
	User requested cancelling a long running operation, such as reading
	a file.
	"""

class NotABug(Exception):
	"""
	Base-class for anticipated errors. When these errors
	are caught by top-level exception-handling machinery,
	the message will not include a traceback
	"""
	pass

class UserError(NotABug):
	"""
	An error that results from a wrongful action taken by a user;
	They did something they weren't supposed to.
	"""
	pass

class LimitationError(NotABug):
	"""
	An error that results from a limitation within Chimera;
	Chimera [knowingly] doesn't do what it should do.
	"""
	pass

class NonChimeraError(NotABug):
	"""
	An error that results from circumstances beyond our control,
	such as a temporary network error -- don't want a bug report.
	"""

class ChimeraSystemExit(SystemExit):
	"""Used to allow Chimera to exit faster"""
	pass

# wrap saving functions that derive from NameMap so that a reference is kept,
# otherwise the saved objects instantly disappear since nothing in Python
# references them
for className in ['Color', 'Texture', 'Material', 'PixelMap']:
	args = (className,) * 7
	exec """
_saved%ss = {}
def _%sSave(item, name):
	_saved%ss[name] = item
	item._realSave(name)
%s._realSave = %s.save
%s.save = _%sSave
"""  % args
# SimpleSession uses these save dicts, so changes need to be coordinated...


import triggerSet
triggers = triggerSet.TriggerSet()

# add triggers for each class that we track changes to
for name in TrackChanges.get().enrolled():
	name = name.split('.')[-1]	# drop leading '_chimera.'
	triggers.addTrigger(name)
del name

# add trigger for application exit
APPQUIT = "Chimera exit"
triggers.addTrigger(APPQUIT)

# add trigger for session close
CLOSE_SESSION = "close session"
triggers.addTrigger(CLOSE_SESSION)
def closeSession():
	triggers.activateTrigger(CLOSE_SESSION, None)
	openModels.close(openModels.list())
	for hidden in openModels.list(all=1):
		if hidden.id < -1:
			# "unclosable" groups
			continue
		openModels.close(hidden)

# for updates ala checkForChanges
triggers.addTrigger('new frame')
triggers.addTrigger('post-frame')
triggers.addTrigger('check for changes')
triggers.addTrigger('monitor changes')

# add trigger for motion start/stop
MOTION_START = "motion start"
MOTION_STOP = "motion stop"
_checkForChangesHandlerID = _motionDelayID = None
def _cancelMotionDelayHandlers():
	global _checkForChangesHandlerID, _motionDelayID
	if _motionDelayID:
		from tkgui import app
		app.after_cancel(_motionDelayID)
		_motionDelayID = None
	if _checkForChangesHandlerID:
		triggers.deleteHandler('check for changes',
						_checkForChangesHandlerID)
		_checkForChangesHandlerID = None

def _afterCB():
	global _checkForChangesHandlerID, _motionDelayID
	_motionDelayID = None
	triggers.activateTrigger(MOTION_STOP, None)

def _redrawCB(trigName, myData, trigData):
	global _checkForChangesHandlerID, _motionDelayID
	triggers.deleteHandler('check for changes', _checkForChangesHandlerID)
	_checkForChangesHandlerID = None
	if nogui:
		triggers.activateTrigger(MOTION_STOP, None)
		return
	from tkgui import app
	_motionDelayID = app.after(1000, _afterCB)

def _motionCB(trigName, myData, trigData):
	global _checkForChangesHandlerID, _motionDelayID
	if 'transformation change' not in trigData.reasons:
		return
	if not _checkForChangesHandlerID and not _motionDelayID:
		triggers.activateTrigger(MOTION_START, None)
	_cancelMotionDelayHandlers()
	# schedule a motion stop after a certain amount of delay past the
	# first redraw
	_checkForChangesHandlerID = triggers.addHandler(
					'check for changes', _redrawCB, None)

def _startMotionTriggers():
	global _motionHandlerID
	_motionHandlerID = triggers.addHandler('OpenState', _motionCB, None)

def _stopMotionTriggers():
	global _motionHandlerID
	_cancelMotionDelayHandlers()
	triggers.deleteHandler('OpenState', _motionHandlerID)
	_motionHandlerID = None

_startHandlers = _stopHandlers = False
def _triggerActivityCB(trigName, onOff):
	global _startHandlers, _stopHandlers
	if onOff == 1:
		if not _startHandlers and not _stopHandlers:
			_startMotionTriggers()
	if trigName == MOTION_START:
		_startHandlers = onOff
	else:
		_stopHandlers = onOff
	if not _startHandlers and not _stopHandlers:
		_stopMotionTriggers()

triggers.addTrigger(MOTION_START, _triggerActivityCB)
triggers.addTrigger(MOTION_STOP, _triggerActivityCB)

def oslLevel(obj):
	"""Return OSL level of object or None.

	The OSL level is one of SelGraph, SelSubgraph, SelVertex, SelEdge.
	"""
	if hasattr(obj, 'oslLevel'):
		return obj.oslLevel()
	return None

def isModel(obj):
	"""Return if obj is a model."""
	return isinstance(obj, Model)

#import oslParser
#
# add color testing capability to OSL
#
def testColor(c, op, s):
	import oslParser
	if ',' in s:
		try:
			vals = [float(x) for x in s.split(',')]
		except ValueError:
			raise SyntaxError("RGBA values must be floating point")
		if len(vals) > 4:
			raise SyntaxError("RGBA can be at most 4 numbers")
	else:
		vals = Color.lookup(s).rgba()[:3]
	equal = True
	rgba = c.rgba()
	for i, v in enumerate(vals):
		if abs(rgba[i] - v) >= 0.001:
			equal = False
			break
	if op in [oslParser.OpEQ1, oslParser.OpEQ2]:
		return equal
	elif op == oslParser.OpNE:
		return not equal
	else:
		return False

#
# add element testing capability to OSL
#
def testElement(e, op, value):
	import oslParser
	if ',' in value:
		raise SyntaxError, 'comma not allowed in element name'
	if op == oslParser.OpMatch:
		return 0
	try:
		value = int(value)
	except ValueError:
		d = cmp(e.name.lower(), value.lower())
	else:
		d = cmp(e.number, value)
	if d < 0:
		if op in (oslParser.OpNE, oslParser.OpLE, oslParser.OpLT):
			return 1
	elif d == 0:
		if op in (oslParser.OpEQ1, oslParser.OpEQ2, oslParser.OpGE,
								oslParser.OpLE):
			return 1
	else:
		if op in (oslParser.OpNE, oslParser.OpGE, oslParser.OpGT):
			return 1
	return 0

#
# add draw mode testing capability to OSL
#
def testDrawMode(e, op, value):
	from chimera import Atom
	import oslParser
	wireNames = ("wire", "wireframe", "dot")
	stickNames = ("stick", "endcap")
	ballNames = ("ball", "bs", "ball-and-stick", "ball and stick", "b+s",
								"ball+stick")
	sphereNames = ("sphere", "cpk", "space-filling")

	nameMap = {}
	nameMap[Atom.Dot] = wireNames
	nameMap[Atom.EndCap] = stickNames
	nameMap[Atom.Ball] = ballNames
	nameMap[Atom.Sphere] = sphereNames

	if op in [oslParser.OpEQ1, oslParser.OpEQ2]:
		return value in nameMap[e.drawMode]
	elif op == oslParser.OpNE:
		return value not in nameMap[e.drawMode]
	else:
		return 0

def registerOSLTests():
	import oslParser
	oslParser.registerTest(MaterialColor, testColor)
	oslParser.registerTest(Element, testElement)
	oslParser.registerTest((Atom, 'drawMode'), testDrawMode)

#
# export findfile
#

def findfile(filename, category=""):
	if filename.startswith("http:"):
		return filename
	if os.path.isabs(filename):
		if os.path.exists(filename):
			return filename
		raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), filename)
	from OpenSave import tildeExpand
	simple = tildeExpand(filename)
	if os.path.exists(simple):
		return simple
	file = pathFinder().firstExistingFile("chimera",
					os.path.join(category, filename))
	if not file:
		raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), filename)
	return file

def selectionOperation(sel):
	if nogui:
		from selection import setCurrent
		return setCurrent(sel)
	else:
		import tkgui
		return tkgui.selectionOperation(sel)

def getSelMode():
	if nogui:
		return 'replace'
	from tkgui import selMode
	return selMode

def _pdbFetch(site, url, params, statusName, saveDir = '', saveName = ''):

	if saveName:
		import fetch
		path = fetch.fetch_local_file(saveDir, saveName)
		if path:
			return path
	import replyobj
	replyobj.status('Fetching %s from web site %s\n' %
					(statusName, site), blankAfter=0)

	import tasks
	cancelled = []
	def cancelCB():
		cancelled.append(True)
	task = tasks.Task("Fetch %s" % statusName, cancelCB, modal=True)

	def reportCB(barrived, bsize, fsize):
		if cancelled:
			raise IOError("cancelled at user request")
		if fsize > 0:
			percent = (100.0*barrived*bsize)/fsize
			prog = '%.0f%% of %d bytes' % (percent, fsize)
		else:
			prog = '%.0f Kbytes received' % ((barrived*bsize)/1024,)
		task.updateStatus(prog)
	import urllib
	params = urllib.urlencode(params)
	try:
		tf, headers = urllib.urlretrieve("http://%s/%s" % (site, url),
						 data=params,
						 reporthook = reportCB)
	except IOError, v:
		replyobj.status("\n")
		raise NonChimeraError("Error during PDB fetch: " + str(v))
	task = None

	replyobj.status('Done fetching %s; verifying...\n' % statusName)
	fetched = open(tf, "r")
	numLines = 0
	for l in fetched:
		numLines += 1
		if numLines >= 20:
			break
	else:
		# too short; not a PDB file
		fetched.close()
		os.unlink(tf)
		replyobj.status("\n")
		raise UserError, "No such ID: %s" % statusName
	fetched.close()
	if saveName:
		import fetch
		spath = fetch.save_fetched_file(tf, saveDir, saveName)
		if spath:
			tf = spath
	replyobj.status("Opening %s...\n" % statusName, blankAfter=0)
	return tf

#
# export fileInfo
#

def _openPDBIDModel(IDcode, explodeNMR=True, identifyAs=None, guiErrors=True):
	"""Locate a PDB ID code, read it, and add it to the list of open models.

	_openPDBIDModel(IDcode) => [model(s)]

	'explodeNMR' controls whether multi-MODEL files are split into
	multiple Molecules (if False, use coord sets instead)

	'guiErrors' controls whether PDB errors will be shown in a dialog
	in GUI mode.  Otherwise they will be on stderr.
	"""
	if not identifyAs:
		identifyAs = IDcode

	import replyobj
	statusName = identifyAs or IDcode
	fileName = None

	# try local system PDB directory
	IDcode = IDcode.lower()
	subpath = IDcode[1:3] + os.sep + "pdb" + IDcode + ".ent"
	pdbDir = systemPDBdir()
	if pdbDir is not None:
		pdbPath = os.path.join(pdbDir, subpath)
		if os.path.exists(pdbPath):
			fileName = pdbPath
		else:
			from OpenSave \
				import compressSuffixes, osUncompressedPath
			for cs in compressSuffixes:
				if os.path.exists(pdbPath + cs):
					fileName = osUncompressedPath(
								pdbPath + cs)
					break
		if fileName is not None:
			replyobj.status("Opening %s...\n" % statusName,
								blankAfter=0)

	import preferences
	from initprefs import PREF_PDB, PREF_PDB_DIRS, PREF_PDB_FETCH
	if fileName == None and preferences.get(PREF_PDB, PREF_PDB_FETCH):
		# not found locally; try web if allowed
		fetchFile = _pdbFetch('www.rcsb.org', 'pdb/files/%s.pdb'
			% IDcode.upper(), {}, statusName,
			'PDB', '%s.pdb' % IDcode.upper())
		fileName = fetchFile
	else:
		fetchFile = None

	if fileName == None:
		raise ValueError, (2, 'No such PDB ID: %s' % IDcode)
	if guiErrors and not nogui:
		import cStringIO
		errLog = cStringIO.StringIO()
	else:
		errLog = None
	pdbio = PDBio()
	pdbio.explodeNMR = explodeNMR
	molList = pdbio.readPDBfile(fileName, errOut=errLog)
	if not pdbio.ok():
		replyobj.status("\n")
		raise UserError("Error reading PDB file: %s" % pdbio.error())
	if errLog and errLog.getvalue():
		replyobj.handlePdbErrs(identifyAs, errLog.getvalue())
	for m in molList:
		m.name = identifyAs
	global _openedInfo
	_openedInfo = "Opened %s\n" % statusName
	return molList

def _openCIFIDModel(IDcode, identifyAs=None):
	"""Locate a CIF ID code, read it, and add it to the list of open models.

	_openCIFIDModel(IDcode) => [model(s)]

	'explodeNMR' controls whether multi-MODEL files are split into
	multiple Molecules (if False, use coord sets instead)
	"""
	if not identifyAs:
		identifyAs = IDcode

	import replyobj
	statusName = identifyAs or IDcode
	fileName = None

	import preferences
	from initprefs import PREF_PDB, PREF_PDB_DIRS, PREF_PDB_FETCH
	if fileName == None and preferences.get(PREF_PDB, PREF_PDB_FETCH):
		# not found locally; try web if allowed
		fetchFile = _pdbFetch('www.rcsb.org', 'pdb/files/%s.cif'
			% IDcode.upper(), {}, statusName,
			'PDB', '%s.cif' % IDcode.upper())
		fileName = fetchFile
	else:
		fetchFile = None

	if fileName == None:
		raise ValueError, (2, 'No such CIF ID: %s' % IDcode)
	import mmCIF
	molList = mmCIF.open_mmcif(fileName)
	for m in molList:
		m.name = identifyAs
	global _openedInfo
	_openedInfo = "Opened %s\n" % statusName
	return molList

def _openSCOPModel(scopID, explodeNMR=True, identifyAs=None):
	"""Locate a SCOP PDB file, read it, and add it to open models.

	_openSCOPModel(scopID) => [model(s)]

	'explodeNMR' controls whether multi-MODEL files are split into
	multiple Molecules (if False, use coord sets instead)
	"""
	if not identifyAs:
		identifyAs = scopID

	import replyobj
	statusName = identifyAs or scopID

	fetchFile = _pdbFetch('astral.berkeley.edu', 'pdbstyle.cgi',
	                      {'id': scopID}, statusName,
			      'SCOP', '%s.pdb' % scopID)

	pdbio = PDBio()
	pdbio.explodeNMR = explodeNMR
	molList = pdbio.readPDBfile(fetchFile)
	if not pdbio.ok():
		replyobj.status("\n")
		raise IOError(errno.EIO, pdbio.error(), identifyAs)
	for m in molList:
		m.name = identifyAs
	global _openedInfo
	_openedInfo = "Opened %s\n" % statusName
	return molList

def _openNDBModel(ndbID, explodeNMR=True, identifyAs=None):
	"""Translate an NDB ID to a PDB ID and open that.

	_openNDBModel(ndbID) => [model(s)]

	'explodeNMR' controls whether multi-MODEL files are split into
	multiple Molecules (if False, use coord sets instead)
	"""
	if not identifyAs:
		identifyAs = ndbID

	import replyobj
	statusName = identifyAs or ndbID

	site = "ndbserver.rutgers.edu"
	replyobj.status('Translating NDB ID %s to PDB ID using web site %s\n' % 
					(statusName, site), blankAfter=0)
	import urllib
	params = urllib.urlencode({
		'structure_id': ndbID,
		'return_type': "PDB"
	})
	try:
		f = urllib.urlopen(
			"http://%s/tools/servlet/idswap.servlets.IdSwap"
			% site, params)
	except IOError, v:
		replyobj.error('Failed to successfully translate %s: %s\n' %
							(statusName, str(v)))
		replyobj.status("\n")
		return []
	for l in f:
		if "PDB ID:" not in l:
			continue
		for i, c in enumerate(l):
			if c.isdigit():
				break
		else:
			replyobj.error('Could not identify PDB ID from'
				' translation server %s\n' % site)
			replyobj.status('\n')
			return []
		pdbID = l[i:i+4]
		if len(pdbID) < 4 or not pdbID[1:].isalnum():
			replyobj.error('Could not identify PDB ID code from'
				' NDB translation server %s response:\n%s'
				% (site, l))
			replyobj.status('\n')
			return []
		break
	else:
		replyobj.error('Unknown reply from'
					' translation server %s\n' % site)
		replyobj.status('\n')
		return []
	replyobj.info('NDB code %s corresponds to PDB code %s\n'
							% (ndbID, pdbID))
	return _openPDBIDModel(pdbID, explodeNMR=explodeNMR,
						identifyAs=identifyAs)

# despite the leading _, SimpleSession uses this function
def _openPDBModel(filename, explodeNMR=True, fromSession=False,
			identifyAs=None, noprefs=False, guiErrors=True):
	"""Read in a PDB file and add it list of open models.

	_openPDBModel(filename) => [model(s)]

	'explodeNMR' controls whether multi-MODEL files are split into
	multiple Molecules (if False, use coord sets instead)

	'guiErrors' controls whether PDB errors will be shown in a dialog
	in GUI mode.  Otherwise they will be on stderr.
	"""
	if isinstance(filename, basestring):
		if not identifyAs:
			identifyAs = os.path.split(filename)[-1]

		try:
			file = findfile(filename)
		except IOError:
			file = None

		if file == None:
			# try personal PDB dirs
			import preferences
			from initprefs import PREF_PDB, PREF_PDB_DIRS, \
							PREF_PDB_FETCH
			for pdbDir in preferences.get(PREF_PDB, PREF_PDB_DIRS):
				pdbPath = os.path.join(pdbDir, filename)
				if os.path.exists(pdbPath):
					file = pdbPath
					break
				if os.path.exists(pdbPath + '.pdb'):
					file = pdbPath + '.pdb'
					break

		if file == None and len(filename) == 4:
			return _openPDBIDModel(filename)

		if file == None:
			raise IOError(errno.ENOENT, os.strerror(errno.ENOENT),
								filename)
	else:
		file = filename
		filename = identifyAs
	import replyobj
	statusName = identifyAs or filename
	replyobj.status("Opening %s...\n" % statusName, blankAfter=0)
	if fromSession:
		pdbio = SessionPDBio()
	else:
		pdbio = PDBio()
	pdbio.explodeNMR = explodeNMR
	from OpenSave import osOpen
	f = osOpen(file)
	if guiErrors and not nogui:
		import cStringIO
		errLog = cStringIO.StringIO()
	else:
		errLog = None
	if fromSession:
		molList, lineNum, sessionIDs = pdbio.readSessionPDBstream(
								f, filename, 0)
	else:
		molList, lineNum = pdbio.readPDBstream(f, filename, 0,
							errOut=errLog)
	f.close()
	if not pdbio.ok():
		replyobj.status("\n")
		raise UserError(pdbio.error())
	if errLog and errLog.getvalue():
		replyobj.handlePdbErrs(identifyAs, errLog.getvalue())
	for m in molList:
		m.name = identifyAs
	if molList and fromSession:
		molList[0].sessionIDs = sessionIDs
	global _openedInfo
	_openedInfo = "Opened %s\n" % statusName
	return molList

def _openVRMLModel(filename, identifyAs=None):
	"""Filename contains a VRML 2.0 file.

	_openVRMLModel(filename) => [model]
	"""
	if isinstance(filename, basestring) and filename[0:5] == "#VRML":
		import cStringIO
		f = cStringIO.StringIO(filename)
		filename = "<<VRML string>>"
	else:
		from OpenSave import osOpen
		f = osOpen(filename)
	import replyobj
	statusName = identifyAs or filename
	replyobj.status("Opening VRML model in %s...\n"
			% statusName, blankAfter=0)
	vrml = VRMLModel(f, filename)
	f.close()
	if not vrml.valid():
		replyobj.status("\n")
		if vrml.error():
			error = vrml.error()
		else:
			error = "unknown VRML error"
		raise IOError(errno.EIO, error, statusName)
	vrml.name = statusName
	global _openedInfo
	_openedInfo = "Opened VRML model in %s\n" % statusName
	return [vrml]

defaultMol2ioHelper = PyMol2ioHelper()

def _openMol2Model(filename, helper=None, identifyAs=None):
	"""Filename contains a Mol2 file.

	_openMol2Model(filename) => [model]
	"""

	if isinstance(filename, basestring):
		file = findfile(filename)
	else:
		file = filename
		filename = identifyAs
	import replyobj
	statusName = identifyAs or filename
	replyobj.status("Opening %s..." % statusName, blankAfter=0)
	if helper == None:
		helper = defaultMol2ioHelper
	mol2io = Mol2io(helper)
	from OpenSave import osOpen
	f = osOpen(file)
	molList = mol2io.readMol2stream(f, filename, 0)
	f.close()
	if not mol2io.ok():
		replyobj.status("\n")
		raise IOError(errno.EIO, mol2io.error(), filename)
	from initprefs import MOLECULE_DEFAULT, MOL_MOL2_NAME, Mol2NameOption
	import preferences
	nameSource = preferences.get(MOLECULE_DEFAULT, MOL_MOL2_NAME)
	for m in molList:
		if len(m.residues) == 0:
			replyobj.status("\n")
			raise SyntaxError, "missing residue section"
		if nameSource == Mol2NameOption.FILE_NAME:
			name = os.path.split(filename)[-1]
		elif nameSource == Mol2NameOption.MOL_NAME:
			name = m.mol2name
		elif nameSource == Mol2NameOption.MOL_COMMENT:
			name = m.mol2comment
		from misc import isInformativeName
		if not isInformativeName(name):
			if not identifyAs:
				identifyAs = os.path.split(filename)[-1]
			name = identifyAs
		m.name = name
	from SimpleSession import registerAttribute
	registerAttribute(Molecule, "mol2name")
	registerAttribute(Molecule, "mol2type")
	registerAttribute(Molecule, "chargeModel")
	registerAttribute(Molecule, "mol2comment")
	registerAttribute(Bond, "mol2type")
	registerAttribute(Atom, "mol2type")
	global _openedInfo
	_openedInfo = "Opened %s\n" % statusName
	return molList

def _openPython(filename, identifyAs=None):
	"""Filename contains a Python script.

	_openPython(filename) => []
	"""
	file = findfile(filename)
	# use sandbox module's namespace to avoid contamination
	sandboxName = 'chimeraOpenSandbox'
	while sandboxName in sys.modules:
		# must be a recursive call sequence...
		sandboxName = "_" + sandboxName
	import replyobj
	statusName = identifyAs or filename
	from SimpleSession import END_RESTORE_SESSION
	def cb(a1, a2, a3, fileName=file):
		setLastSession(fileName)
	handler = triggers.addHandler(END_RESTORE_SESSION, cb, None)

	from OpenSave import osUncompressedPath
	ucPath = osUncompressedPath(file)
	import imp
	flags = 'rU'
	if ucPath.endswith('.py'):
		loadFunc = imp.load_source
		if not os.path.exists(ucPath + 'c') \
		and not os.path.exists(ucPath + 'o'):
			# try to pre-compile
			replyobj.status("Compiling %s..." % statusName)
			# use repr() trick to double backslashes
			command = [ sys.executable, "-m", "py_compile", ucPath ]
			try:
				import subprocess
				if subprocess.call(command) < 0:
					raise RuntimeError
			except:
				replyobj.status("Compiling %s failed"
								% statusName)
			else:
				replyobj.status("Compiling %s succeeded"
								% statusName)
	elif ucPath.endswith('.pyc') or ucPath.endswith('.pyo'):
		loadFunc = imp.load_compiled
		flags = 'rb'
	else:
		loadFunc = imp.load_source
	replyobj.status("Executing %s..." % statusName)
	dirName, fileName = os.path.split(ucPath)
	cwd = os.getcwd()
	try:
		try:
			if dirName:
				os.chdir(dirName)
			f = open(fileName, flags)
			if sys.platform == 'win32' and isinstance(fileName, unicode):
				# imp funcs can't handle unicode on Windows
				fileName = fileName.encode('mbcs')
			loadFunc(sandboxName, fileName, f)
			f.close()
		except ImportError, v:
			if unicode(v).startswith("Bad magic number"):
				raise UserError(".pyc files are not portable;"
					" please use .py file instead")
			raise
		finally:
			os.chdir(cwd)
			triggers.deleteHandler(END_RESTORE_SESSION, handler)
			try:
				del sys.modules[sandboxName]
			except KeyError:
				pass
			if file != ucPath and ucPath.endswith(".py"):
				# remove the .pyc we compiled
				pyc = ucPath + 'c'
				if os.path.exists(pyc):
					os.unlink(pyc)

	except CancelOperation, v:
		replyobj.status("Cancelled %s\n" % statusName)
		return []
	except ChimeraSystemExit, v:
		triggers.activateTrigger(APPQUIT, None)
		raise ChimeraSystemExit, v
	except:
		replyobj.status("\n")
		raise
	replyobj.status("Executed %s\n" % statusName)
	return []

def _openGaussianFCF(filename, identifyAs=None):
	"""Filename contains a Gaussian formatted checkpoint file

	_openGaussianFCF(filename) => [model(s)]
	"""
	if isinstance(filename, basestring):
		if not identifyAs:
			identifyAs = os.path.split(filename)[-1]
		file = findfile(filename)
	else:
		file = filename
		filename = identifyAs
	import replyobj
	statusName = identifyAs or filename
	replyobj.status("Opening %s...\n" % statusName, blankAfter=0)
	from OpenSave import osOpen
	fcf = ReadGaussianFCF()
	f = osOpen(file)
	molList, lineNum = fcf.readGaussianStream(f, filename, 0)
	f.close()
	if not fcf.ok():
		replyobj.status("\n")
		raise IOError(errno.EIO, fcf.error(), filename)
	for m in molList:
		m.name = identifyAs
	if molList and molList[0].atoms \
	and hasattr(molList[0].atoms[0], "mullikenCharge"):
		from SimpleSession import registerAttribute
		registerAttribute(Atom, "mullikenCharge")
		registerAttribute(Molecule, "chargeModel")
	global _openedInfo
	_openedInfo = "Opened %s\n" % statusName
	return molList

class FileInfo(object):
	"""Information about file types that can be opened"""
	# some known categories
	DYNAMICS = "Molecular trajectory"
	GENERIC3D = "Generic 3D objects"
	SCRIPT = "Command script"
	SEQUENCE = "Sequence alignment"
	STRUCTURE = "Molecular structure"
	SURFACE = "Molecular surface"
	VOLUME = "Volume data"

	_open = {
		# type: (
		#	open-func, extensions, prefixes,
		#	mime-types, canDecompress, dangerous,
		#	category
		# )
		# filename extensions must be all lowercase
		"PDB": (
			_openPDBModel, [".pdb", ".pdb1", ".ent"], ["pdb"],
			["chemical/x-pdb", "chemical/x-spdbv"], True, False,
			STRUCTURE, False
		),
		"PDBID": (
			_openPDBIDModel, None, ["pdbID"], None, False, False,
			STRUCTURE, False
		),
		"CIFID": (
			_openCIFIDModel, None, ["cifID"], None, False, False,
			STRUCTURE, False
		),
		"VRML": (
			_openVRMLModel, [".wrl", ".vrml"], ["vrml"],
			["model/vrml"], True, False, GENERIC3D, False
		),
		#"X3D": (
		#	_openX3DModel, [".x3d"], ["x3d"], ["model/x3d+xml"],
		#	True, False,
		#	GENERIC3D, False
		#),
		"Mol2": (
			_openMol2Model, [".mol2"], ["mol2"],
			["chemical/x-mol2"], True, False,
			STRUCTURE, False
		),
		"Python": (_openPython,
			[".py", ".pyc", ".pyo", ".pyw"],
			["python", "py", "chimera"],
			["application/x-chimera"], True, True,
			SCRIPT, False
		),
		"Gaussian formatted checkpoint": (
			_openGaussianFCF, [".fchk"], ["fchk", "gaussian"],
			["chemical/x-gaussian-checkpoint"], True, False,
			STRUCTURE, False
		),
		"SCOP": (
			_openSCOPModel, None, ["scop"], None, False, False,
			STRUCTURE, False

		),
		"NDB": (
			_openNDBModel, None, ["ndb"], None, False, False,
			STRUCTURE, False
		),
	}

	triggers = triggerSet.TriggerSet()
	NEWFILETYPE = "new file type"
	triggers.addTrigger(NEWFILETYPE)

	def register(self, type, function, extensions, prefixes, mime=None,
			canDecompress=True, dangerous=None,
			category="Miscellaneous", batch=False):
		"""Register open function for given model type

		register(type, function, extensions, prefixes) -> None

		extensions is a sequence of filename suffixes starting
		with a period.  If the type doesn't open from a filename
		(e.g. PDB ID code), then extensions should be None.

		prefixes is a sequence of filename prefixes (no ':').

		mime is a sequence of mime types.

		If the type doesn't want to be given compressed files of its
		type, 'canDecompress' should be false.  [The OpenSave module
		has functions to assist in the handling of compressed files.]

		dangerous should be true for scripts and other formats that
		may write/delete a users's files.

		category says what kind of data the should be classified as.

		If batch is true then the open function requires a list of
		paths.  If the user selects multiple paths they are all passed
		to the open function in one call instead of a separate call
		for each path.
		"""
		if dangerous is None:
			# scripts are inherently dangerous
			dangerous = category == self.SCRIPT
		if extensions is not None:
			exts = map(lambda s: s.lower(), extensions)
		else:
			exts = None
		self._open[type] = (
				function, exts, prefixes, mime,
				canDecompress, dangerous, category, batch)
		self.triggers.activateTrigger(self.NEWFILETYPE, type)

	def prefixes(self, type):
		"""Return filename prefixes for given model type.

		prefixes(type) -> [filename-prefix(es)]
		"""
		try:
			return self._open[type][2]
		except KeyError:
			return []
		
	def extensions(self, type):
		"""Return filename extensions for given model type.

		extensions(type) -> [filename-extension(s)]
		"""
		try:
			exts = self._open[type][1]
		except KeyError:
			return []
		if exts is None:
			return []
		return exts

	def openCallback(self, type):
		"""Return open callback for given model type.

		openCallback(type) -> [callback]
		"""
		try:
			return self._open[type][0]
		except KeyError:
			return None

	def mimeType(self, type):
		"""Return mime type for given model type."""
		try:
			return self._open[type][3]
		except KeyError:
			return None

	def canDecompress(self, type):
		"""Return whether this type can open compressed files"""
		try:
			return self._open[type][4]
		except KeyError:
			return False

	def dangerous(self, type):
		"""Return whether this type can write to files"""
		try:
			return self._open[type][5]
		except KeyError:
			return False

	def category(self, type):
		"""Return category of this type"""
		try:
			return self._open[type][6]
		except KeyError:
			return "Unknown"

	def batch(self, type):
		"""Return whether open function expects list of file names"""
		try:
			return self._open[type][7]
		except KeyError:
			return False

	def types(self, sourceIsFile=False):
		"""Return known model types.

		types() -> [model-type(s)]
		"""
		if sourceIsFile:
			types = []
			for typeName, typeInfo in self._open.items():
				if typeInfo[1] is not None:
					types.append(typeName)
			return types
		return self._open.keys()

	def categorizedTypes(self):
		"""Return know model types by category

		categorizedTypes() -> { category: model-types() }
		"""
		result = {}
		for t in self._open.keys():
			category = self.category(t)
			list = result.setdefault(category, [])
			list.append(t)
		return result

	def processName(self, filename, defaultType=None, prefixableType=True):
		type = None
		if prefixableType:
			# type may be specified as colon-separated prefix
			try:
				prefix, fname = filename.split(':', 1)
			except ValueError:
				pass
			else:
				for t in fileInfo.types():
					if prefix in fileInfo.prefixes(t):
						type = t
						filename = fname
						break
		from OpenSave import compressSuffixes
		if type == None:
			for cs in compressSuffixes:
				if filename.endswith(cs):
					stripped, ext = os.path.splitext(
								filename)
					break
			else:
				stripped = filename
			base, ext = os.path.splitext(stripped)
			ext = ext.lower()
			for t in fileInfo.types():
				if ext in fileInfo.extensions(t):
					type = t
					break
			if type == None:
				type = defaultType
		return type, filename

fileInfo = FileInfo()

#
# export openModels -- a instance that contains all open models
#	The key is a tuple (model id #, model subid #) and the value
#	is a list of models with that key.
#

# class OpenModel: from _chimera
OpenModels.ADDMODEL    = 'addModel'
OpenModels.REMOVEMODEL = 'removeModel'
OpenModels.triggers = triggerSet.TriggerSet()
OpenModels.triggers.addTrigger(OpenModels.ADDMODEL)
OpenModels.triggers.addTrigger(OpenModels.REMOVEMODEL)

def addAddHandler(self, func, data):
	"""Add trigger handler for adding models"""
	return self.triggers.addHandler(self.ADDMODEL, func, data)
OpenModels.addAddHandler = addAddHandler
del addAddHandler

def deleteAddHandler(self, handler):
	"""Delete trigger handler for adding models"""
	self.triggers.deleteHandler(self.ADDMODEL, handler)
OpenModels.deleteAddHandler = deleteAddHandler
del deleteAddHandler

def addRemoveHandler(self, func, data):
	"""Add trigger handler for removing models"""
	return self.triggers.addHandler(self.REMOVEMODEL, func, data)
OpenModels.addRemoveHandler = addRemoveHandler
del addRemoveHandler

def deleteRemoveHandler(self, handler):
	"""Delete trigger handler for removing models"""
	self.triggers.deleteHandler(self.REMOVEMODEL, handler)
OpenModels.deleteRemoveHandler = deleteRemoveHandler
del deleteRemoveHandler
      
def addModelClosedCallback(model, callback):
	"""Invoke a callback when a specified model is closed.
	The callback is only called when the given model is closed.
	The callback is automattically removed after it is called.
	The callback is passed one argument, the closed model.
	"""
	def cb(trigger_name, args, closed_models):
		model, callback, trigger = args
		if model in closed_models:
			callback(model)
			import chimera
			chimera.openModels.deleteRemoveHandler(trigger)
			args[2] = None    # Break circular link to trigger

	args = [model, callback, None]
	import chimera
	trigger = chimera.openModels.addRemoveHandler(cb, args)
	args[2] = trigger

def add(self, models, baseId=OpenModels.Default, subid=OpenModels.Default,
		sameAs=None, shareXform=True, hidden=False,
		checkForChanges=False, noprefs=False):
	#
	# Note: this function is called from the _chimera C++ code,
	# do not change its name, or how it is accessed without also
	# changing _chimera.
	#
	"""Add models to the list of open models.

	add(models, sameAs=None, hidden=False) => None

	baseId is the base model id to start numbering models with.

	sameAs is an existing model that all of the new models should
	share the same id and subid.
	
	If shareXform is true, then initialize the model's transformation
	matrix to be the same as the lowest positively numbered model 
	(if not baseId specified) or the lowest numbered model with the
	same baseId.  (Using sameAs overrides shareXform).
	
	If hidden is true, that means that the given models do not
	normally appear when listed.
	"""
	if noprefs:
		for m in models:
			m.noprefs = True
	# force Python object creation before checkForChanges
	makePythonAtomsBondsResidues(models)
	molecules = [m for m in models if isinstance(m, Molecule)]
	_postCategorizeModels.extend(molecules)
	self._add(models, baseId, subid, sameAs, shareXform, hidden)
	for m in models:
		viewer.addModel(m)
	# TODO: eliminate need to update cached ref counts
	for id in self.listIds(hidden=hidden):
		os = self.openState(*id)
		if hidden:
			os.hidden
		else:
			os.models
	self.triggers.activateTrigger(self.ADDMODEL, models)
	if checkForChanges:
		import update
		update.checkForChanges()
OpenModels._add = OpenModels.add
OpenModels.add = add
del add

def remove(self, models):
	"""Remove models from the list of open models.

	remove(models) => None
	"""
	if isModel(models):
		models = [models]
	for m in models:
		viewer.removeModel(m)
	removedModels = self._remove(models)
	# TODO: eliminate need to update cached ref counts
	for id in self.listIds(all=True):
		os = self.openState(*id)
		os.hidden
		os.models
	if removedModels:
		self.triggers.activateTrigger(
					self.REMOVEMODEL, removedModels)
	return removedModels
OpenModels._remove = OpenModels.remove
OpenModels.remove = remove
del remove

def list(self, id=OpenModels.Default, subid=OpenModels.Default, modelTypes=[], hidden=False, all=False):
	"""List models from the list of open models.

	list(id = None, hidden=False, all=False, modelTypes=[]) => [models]

	id is a model identifier (an integer).  If hidden is true,
	then the hidden models are returned.  If all is true, then
	both hidden and non-hidden models are returned.  modelTypes
	is a list of model types (see the global list modelTypes)
	that restricts the types of the models returned.
	"""
	models = self._list(id, subid, hidden, all)
	if modelTypes and isinstance(modelTypes, (list, tuple, set)):
		mtypes = tuple(modelTypes)
		models = [m for m in models if isinstance(m,mtypes)]
	return models
OpenModels._list = OpenModels.list
OpenModels.list = list
del list

def open(self, filename, type=None, baseId=OpenModels.Default,
		subid=OpenModels.Default, sameAs=None, shareXform=True,
		hidden=False, defaultType=None, prefixableType=False,
		checkForChanges=True, noprefs=False,
		*args, **kw):
	"""Read in a file and add the models within.

	open(filename, type=None, [add arguments,] *args, **kw) -> [model(s)]

	If the type is given, then then open handler for that type is
	used.  Otherwise the filename suffix is examined to determine
	which open function to call.  See the add documentation above.

	The filename is a list of paths if the file type is specified and
	registered with a batch file reader, i.e. fileInfo.batch(type) = True.
	If the file type is not given then the filename must be a string.
	"""
	if defaultType and defaultType not in fileInfo.types():
		raise ValueError, "unknown default type"
	if isinstance(filename, basestring):
		openedAs = (filename, type, defaultType, prefixableType)
	else:
		openedAs = None
	if type == None:
		type, filename = fileInfo.processName(filename,
			defaultType=defaultType, prefixableType=prefixableType)
	if type == None and not nogui:
		from Pmw import SelectionDialog
		from tkgui import app
		def cb(but):
			val = None
			if but != 'Cancel':
				sels = sd.getcurselection()
				if sels:
					val = sels[0]
			sd.deactivate(val)
		typeList = fileInfo.types()
		typeList.sort(lambda a, b: cmp(a.lower(), b.lower()))
		sd = SelectionDialog(app, defaultbutton='OK',
			buttons=('OK', 'Cancel'), command=cb,
			title="Type Selection", scrolledlist_labelpos='n',
			label_text="Please designate file type for\n%s"
							% (filename),
			scrolledlist_items=typeList)
		type = sd.activate()
		sd.destroy()
		if type is None:
			return []

	if type and not fileInfo.canDecompress(type):
		from OpenSave import compressSuffixes
		for cs in compressSuffixes:
			if fileInfo.batch(type):
				needDecompress = [f for f in filename
						  if f.endswith(cs)]
			else:
				needDecompress = filename.endswith(cs)
			if needDecompress:
				raise UserError(
		"Compressed %s files are not handled automatically.\n"
		"You need to decompress such files manually before using them."
		% type)
	func = fileInfo.openCallback(type)
	if not func:
		raise ValueError, "Unknown model type"

	# stop any ongoing spinning if no non-pseudobond groups are open
	if not nogui:
		doStopSpinning = True
		for m in openModels.list():
			if not isinstance(m, PseudoBondGroup):
				doStopSpinning = False
				break
		if doStopSpinning and not nogui:
			import tkgui
			tkgui.stopSpinning()

	# funcs can stash status info they want shown after the redraw here
	global _openedInfo
	_openedInfo = None

	# remove 'identifyAs' keyword if the function doesn't expect it...
	if 'identifyAs' in kw:
		import inspect
		allArgs, v1, v2, defaults = inspect.getargspec(func)
		if defaults is None:
			defaults = ()
		if 'identifyAs' not in allArgs[len(allArgs) - len(defaults):]:
			del kw['identifyAs']
	elif not isinstance(filename, basestring):
		# streams must supply identifyAs if possible
		import inspect
		allArgs, v1, v2, defaults = inspect.getargspec(func)
		if defaults is None:
			defaults = ()
		if 'identifyAs' in allArgs[len(allArgs) - len(defaults):]:
			raise ValueError("'identifyAs' keyword must be provided"
						" when opening streams")
	models = func(filename, *args, **kw)

	if models:
		# do the self.add first so that the model number
		# is correct when we ask for it, but block the
		# ADDMODEL trigger so we can clean up the metal
		# complexes before callbacks occur
		self.triggers.blockTrigger(self.ADDMODEL)
		self.add(models, baseId=baseId, subid=subid, sameAs=sameAs,
				shareXform=shareXform, hidden=hidden,
				checkForChanges=False, noprefs=noprefs)
		if openedAs:
			for model in models:
				model.openedAs = openedAs
		makePseudoBondsToMetals(models)
		makeLongBondsDashed(models)
		if checkForChanges:
			import update
			update.checkForChanges()
		self.triggers.releaseTrigger(self.ADDMODEL)

		numAtoms, numResidues = countAtomsAndResidues(models)
		if numAtoms > 0:
			if isinstance(filename, basestring):
				if os.path.exists(filename):
					from tempfile import gettempprefix
					fileLabel = os.path.split(filename)[-1]
					if fileLabel.startswith(gettempprefix()):
						fileLabel = "<temp file>"
				else:
					fileLabel = models[0].name
			else:
				fileLabel = "<stream>"
			_openedInfo = "Opened %s containing %d model" % (
							fileLabel, len(models))
			if len(models) > 1:
				_openedInfo += "s"
			_openedInfo += ", %d atoms, and %d residues\n" % (
							numAtoms, numResidues)
	if _openedInfo:
		def _postOpenedStatus(trigName, d1, d2, info=_openedInfo):
			replyobj.status(info)
			from triggerSet import ONESHOT
			return ONESHOT
		triggers.addHandler('post-frame', _postOpenedStatus, None)
	return models

OpenModels.open = open
del open

def makePseudoBondsToMetals(models):
	"""Replace normal bonds with pseudobonds for coordinated metals.

	makePseudoBondsToMetals(models) => numAtoms, deletedBonds
	"""
	from elements import metals
	from misc import getPseudoBondGroup
	from initprefs import MOL_COMPLEX_LW, MOL_COMPLEX_COLOR, \
		MOL_COMPLEX_DASHED, MOLECULE_DEFAULT
	import preferences

	deletedBonds = []
	formedGroups = []
	for model in models:
		if not isinstance(model, Molecule):
			continue
		modelMetals = {}.fromkeys([a for a in model.atoms
						if a.element in metals])
		for metal in modelMetals.keys():
			# skip large inorganic residues (that typically
			# don't distinguish metals by name)
			if not metal.altLoc \
			and len(metal.residue.atomsMap[metal.name]) > 1:
				continue
			# bond -> pseudobond if:
			# 1) cross residue
			# 2) > 4 bonds
			# 3) neighbor is bonded to non-metal in same res
			#    unless metal has only one bond and the
			#    neighbor has no lone pairs (e.g. residue
			#    EMC in 1cjx)
			delBonds = set()
			for bonded, bond in metal.bondsMap.items():
				if bonded.residue != metal.residue:
					delBonds.add(bond)
			# eliminate cross-residue first to preserve FEO in 1av8
			if len(metal.bonds) - len(delBonds) > 4:
				delBonds = metal.bonds
			else:
				for bonded, bond in metal.bondsMap.items():
					# metals with just one bond may be a legitimate
					# compound
					if len(metal.bonds) == 1:
						from idatm import typeInfo
						idatmType = bonded.idatmType
						if (idatmType in typeInfo and
						typeInfo[idatmType].substituents
						==typeInfo[idatmType].geometry):
							continue
					for bn in bonded.neighbors:
						if bn not in modelMetals and \
						bn.residue == bonded.residue:
							delBonds.add(bond)
							break
			if not delBonds:
				continue
			# avoid repeated idatm computations by delaying
			# pseudobond group formation (and bond deletion)
			formedGroups.append((metal, delBonds))
			deletedBonds.extend(delBonds)

	for metal, delBonds in formedGroups:
		# atom.coordination() expects the pseudobond group
		# category to start with "coordination complex"
		mol = metal.molecule
		cmPBG = getPseudoBondGroup("coordination complexes of %s (%s)"
			% (mol.name, mol), associateWith=[mol], issueHint=True)
		for b in delBonds:
			if b.__destroyed__:
				continue
			a = b.otherAtom(metal)
			mol.deleteBond(b)
			cmPBG.newPseudoBond(metal, a)
		cmPBG.lineWidth = preferences.get(MOLECULE_DEFAULT, MOL_COMPLEX_LW)
		cmPBG.color = preferences.get(MOLECULE_DEFAULT, MOL_COMPLEX_COLOR)
		if preferences.get(MOLECULE_DEFAULT,MOL_COMPLEX_DASHED):
			cmPBG.lineType = Dash
	return deletedBonds

LONGBOND_PBG_NAME = "missing segments"
def makeLongBondsDashed(models):
	"""Hide long bonds and replace with dashed pseudobonds"""

	longBonds = []
	for m in models:
		if not isinstance(m, Molecule):
			continue
		for b in m.bonds:
			a1, a2 = b.atoms
			if a1.residue == a2.residue:
				continue
			id1, id2 = a1.residue.id, a2.residue.id
			if id1.chainId and id2.chainId and abs(id1.position -
							id2.position) < 2:
				continue

			idealBL = Element.bondLength(a1.element, a2.element)
			if b.sqlength() > 2.0 * idealBL * idealBL:
				longBonds.append(b)
	if longBonds:
		from misc import getPseudoBondGroup
		preexisting = PseudoBondMgr.mgr().findPseudoBondGroup(
							LONGBOND_PBG_NAME)
		_longBondPBG = getPseudoBondGroup(LONGBOND_PBG_NAME,
								issueHint=True)
		if not preexisting:
			_longBondPBG.lineType = Dash
			_longBondPBG.chainTraceMapping = {}
			triggers.addHandler("Atom", _longBondTraceCB,
								_longBondPBG)
			from SimpleSession import SAVE_SESSION
			triggers.addHandler(SAVE_SESSION, _chainTraceSessionCB,
								_longBondPBG)
		for lb in longBonds:
			lb.display = Bond.Never
			pb = _longBondPBG.newPseudoBond(*tuple(lb.atoms))
			pb.halfbond = True
			_longBondPBG.chainTraceMapping[pb] = None

def _longBondTraceCB(trigName, pbg, changes):
	if pbg.__destroyed__:
		from triggerSet import ONESHOT
		return ONESHOT
	ctMap = pbg.chainTraceMapping
	delPB = pbg.deletePseudoBond
	for normalPB, tracePB in pbg.chainTraceMapping.items():
		# first, fix things up
		if normalPB.__destroyed__:
			if tracePB and not tracePB.__destroyed__:
				delPB(tracePB)
			del ctMap[normalPB]
			continue
		if tracePB and tracePB.__destroyed__:
			normalPB.display = Bond.Smart
			ctMap[normalPB] = None

		# now create/remove trace pseudobonds as necessary
		a1, a2 = normalPB.atoms
		normalShowable = a1.display and a2.display
		if normalShowable:
			if tracePB:
				normalPB.display = Bond.Smart
				delPB(tracePB)
				ctMap[normalPB] = None
		else:
			if not tracePB and a1.molecule.autochain:
				shown1 = [a for a in a1.residue.atoms
								if a.display]
				shown2 = [a for a in a2.residue.atoms
								if a.display]
				if not shown1 or not shown2:
					continue
				ends1 = [(a.xformCoord().sqdistance(
					a2.xformCoord()), a) for a in shown1]
				ends2 = [(a.xformCoord().sqdistance(
					a1.xformCoord()), a) for a in shown2]
				ends1.sort()
				ends2.sort()
				tracePB = pbg.newPseudoBond(
						ends1[0][1], ends2[0][1])
				tracePB.halfbond = True
				normalPB.display = Bond.Never
				ctMap[normalPB] = tracePB

def _chainTraceSessionCB(trigName, pbg, sessionFile):
	if pbg.__destroyed__:
		from triggerSet import ONESHOT
		return ONESHOT
	from SimpleSession import sessionID
	print>>sessionFile, "ctMap = {"
	for k, v in pbg.chainTraceMapping.items():
		if v:
			value = "(%s, %s)" % tuple([repr(sessionID(a))
							for a in v.atoms])
		else:
			value = "None"
		print>>sessionFile, repr(sessionID(k)), ":", value, ","
	print>>sessionFile, "}"
	print>>sessionFile, """
try:
	newMap = {}
	from SimpleSession import idLookup
	for k, v in ctMap.items():
		if v:
			value = [idLookup(a) for a in v]
		else:
			value = v
		newMap[idLookup(k)] = value
	# avoid having the group missing its 'chainTraceMapping' attribute
	# for any period of time...
	from chimera import PseudoBondMgr
	ctGroup = PseudoBondMgr.mgr().findPseudoBondGroup(%s)
	if hasattr(ctGroup, "chainTraceMapping"):
		needHandlers = False
	else:
		needHandlers = True
		ctGroup.chainTraceMapping = {}
	ctGroup.display = %s
	# chain-trace pseudobonds only exists after a redraw...
	def restoreLBCTmap(trigName, info, trigArgs):
		ctGroup, ctMap, needHandlers = info
		try:
			from chimera import triggers, _longBondTraceCB, _chainTraceSessionCB
			from SimpleSession import SAVE_SESSION
			if needHandlers:
				ctGroup.chainTraceMapping = ctm = {}
				triggers.addHandler("Atom",
						_longBondTraceCB, ctGroup)
				triggers.addHandler(SAVE_SESSION,
						_chainTraceSessionCB, ctGroup)
			for lbpb, v in ctMap.items():
				if v:
					a1, a2 = v
					pbs1 = set(a1.pseudoBonds)
					pbs2 = set(a2.pseudoBonds)
					for pb in (pbs1 & pbs2):
						if pb.category.startswith(
						"internal-chain-"):
							value = pb
							break
					else:
						value = None
				else:
					value = v
				ctm[lbpb] = value
		finally:
			from chimera.triggerSet import ONESHOT
			return ONESHOT
	import chimera
	chimera.triggers.addHandler("post-frame", restoreLBCTmap,
						(ctGroup, newMap, needHandlers))
except:
	reportRestoreError('Error restoring chain-trace pseudobond group')
""" % (repr(pbg.category), repr(pbg.display))

def makePythonAtomsBondsResidues(models):
	"""Create Python objects for atoms, bonds, residues and coordsets.

	makePythonAtomsBondsResidues(models) => None
	"""
	for m in models:
		try:
			m.atoms
			m.bonds
			m.residues
			m.coordSets
		except AttributeError:
			continue

def countAtomsAndResidues(models):
	"""Count the total number of atoms and residues in the given models.

	countAtomsAndResidues(models) => numAtoms, numResidues
	"""
	numAtoms = 0
	numResidues = 0
	for model in models:
		if isinstance(model, Molecule):
			numAtoms += len(model.atoms)
			numResidues += len(model.residues)
	return numAtoms, numResidues

def close(self, models, checkForChanges=True):
	"""Close models and remove from list of open models.

	close(models) => None

	Set checkForChanges to False when calling close within a trigger.
	"""
	if not models:
		return
	if isModel(models):
		models = [models]
	for m in models[:]:
		if not isinstance(m, ChainTrace):
			continue
		models.remove(m)
		import replyobj
		replyobj.error(
			"Cannot close autochain pseudobond group; "
			"close molecule instead\n")

	models = self.remove(models)
	for m in models:
		try:
			m.destroy()
		except ValueError:
			# model probably already destroyed because it was
			# associated with another model that was destroyed
			pass

	if checkForChanges:
		import update
		update.checkForChanges()
OpenModels.close = close
del close

def closeAllModels(self, trigger=None, closure=None, triggerData=None):
	# close non-hidden models first, so that "internal chain"
	# pseudobond groups can get removed by callbacks from
	# the C++ layer.  Then close all remaining models.
	#
	# also, delay closure to the end of APPQUIT triggers, so that
	# other modules have opportunity to de-register from model-
	# closing triggers via APPQUIT
	def _closeCB(*args):
		self.close(self.list())
		self.close(self.list(all=True))
	triggers.addHandler(APPQUIT, _closeCB, None)
OpenModels.closeAllModels = closeAllModels
del closeAllModels

openModels = OpenModels.get()
openModels.viewer = viewer
triggers.addHandler(APPQUIT, openModels.closeAllModels, None)

def initializeGraphics():
	# add a background lens to viewer
	# (must be done after openModels is created)
	initializeColors(nogui)

	# set viewer defaults
	green = Color.lookup("green")
	black = Color.lookup("black")
	try:
		try:
			viewer.highlight = LensViewer.Outline
		except ValueError, e:
			replyobj.warning("%s.\n"
				"Defaulting to Fill highlight.\n"
				"\n"
				"Possible display misconfiguration.  Please\n"
				"increase the color quality (24 bit color or\n"
				"greater), update your display (graphics)\n"
				"driver, and/or upgrade your graphics card.\n"
				"Also see chimera installation instructions."
				% e)
			viewer.highlight = LensViewer.Fill
		viewer.highlightColor = green
		#viewer.lensBorder = True
		#viewer.lensBorderColor = green
		if stereo:
			if not viewer.camera.setMode("sequential stereo", viewer):
				replyobj.warning('Unable to set stereo camera mode\n')
		from math import sin, cos, radians
		fill = DirectionalLight()
		angle = radians(15)
		fill.direction = Vector(sin(angle), sin(angle), cos(angle))
		fill.diffuse = MaterialColor(1, 1, 1)
		fill.diffuseScale = 0.49999
		fill.specular = fill.diffuse
		fill.specularScale = 0
		viewer.fillLight = fill
		key = DirectionalLight()
		angle = radians(45)
		key.direction = Vector(-sin(angle / 2), sin(angle), cos(angle))
		key.diffuse = MaterialColor(1, 1, 1)
		fd = fill.direction
		kd = key.direction
		overlap = (kd * fd) / kd.length / fd.length
		brightness = 1	# total brightness
		key.diffuseScale = brightness - overlap * fill.diffuseScale
		key.specular = key.diffuse
		key.specularScale = 1
		viewer.keyLight = key
	except error:
		pass

	import bgprefs
	bgprefs.initialize()

def systemPDBdir():
	pdbDirFile = pathFinder().firstExistingFile("chimera", "pdbDir",
								False, True)
	if pdbDirFile:
		scope = {}
		try:
			execfile(pdbDirFile, scope)
		except:
			replyobj.reportException("Problem executing file"
				" containing location of system PDB directory"
				" (file: %s)" % pdbDirFile)
		if scope.has_key('pdbDir'):
			pdbDir = scope['pdbDir']
		else:
			replyobj.error("File containing location of system PDB"
				" directory (file: %s) failed to define"
				" variable 'pdbDir'.\n" % pdbDirFile)
			pdbDir = None

		if not isinstance(pdbDir, basestring) and pdbDir is not None:
			replyobj.error("File containing location of system PDB"
				" directory (file: %s) failed to define"
				" variable 'pdbDir' as a string or None.\n"
				% pdbDirFile)
		else:
			return pdbDir
	else:
		replyobj.warning("Cannot find file containing location of"
						" system PDB directory\n")
	return None

# set up handling of "new molecule" preferences
openColors = [
	(1.0,  1.0,  1.0),
	(1.0,  0.0,  1.0),
	(0.0,  1.0,  1.0),
	(1.0,  1.0,  0.0),
	(1.0,  0.0,  0.0),
	(0.0,  0.0,  1.0),
	(0.67, 1.0,  0.0),
	(0.67, 0.0,  1.0),
	(0.67, 1.0,  1.0),
	(1.0,  0.67, 0.0),
	(0.0,  0.67, 1.0),
	(1.0,  0.67, 1.0),
	(1.0,  1.0,  0.5),
	(1.0,  0.0,  0.5),
	(0.0,  1.0,  0.5),
	(0.67, 0.67, 1.0)
]
def processNewMolecules(mols, openColors=openColors):
	from tkoptions import MoleculeColorOption, LineWidthOption, \
		RibbonDisplayOption, RibbonXSectionOption, \
		RibbonScalingOption, AtomDrawModeOption, \
		BondDrawModeOption, StickScaleOption, BallScaleOption, \
		AutoChainOption, RibbonHideBackboneOption
	from initprefs import MOLECULE_DEFAULT, MOL_AUTOCOLOR, MOL_COLOR, \
		MOL_LINEWIDTH, MOL_RIBBONDISP, MOL_RIBBONMODE, \
		MOL_RIBBONSCALE, MOL_ATOMDRAW, MOL_BONDDRAW, MOL_IONS_REPR, \
		MOL_STICKSCALE, MOL_BALLSCALE, MOL_PERATOM, \
		MOL_AUTOCHAIN, MOL_HIDE_BACKBONE, MOL_SMART
	import preferences
	prefget = preferences.get
	smartMols = []
	for mol in mols:
		if prefget(MOLECULE_DEFAULT, MOL_AUTOCOLOR):
			if Color.lookup("_openColor00") is None:
				# define some colors
				for i in range(len(openColors)):
					c = MaterialColor(*openColors[i])
					c.save("_openColor%02d" % i)
			molcolor = mol.color
			mol.color = None
			if mol.color != molcolor:
				# already colored somehow
				mol.color = molcolor
			else:
				mol.color = Color.lookup("_openColor%02d"
					% (mol.id % len(openColors)))
		else:
			defColor = prefget(MOLECULE_DEFAULT, MOL_COLOR)
			if defColor != None:
				setattr(mol, MoleculeColorOption.attribute, defColor)

		lineWidth = prefget(MOLECULE_DEFAULT, MOL_LINEWIDTH)
		if lineWidth != LineWidthOption.default:
			setattr(mol, LineWidthOption.attribute, lineWidth)
		
		stickScale = prefget(MOLECULE_DEFAULT, MOL_STICKSCALE)
		if stickScale != StickScaleOption.default:
			setattr(mol, StickScaleOption.attribute, stickScale)
		
		ballScale = prefget(MOLECULE_DEFAULT, MOL_BALLSCALE)
		if ballScale != BallScaleOption.default:
			setattr(mol, BallScaleOption.attribute, ballScale)
		
		if prefget(MOLECULE_DEFAULT, MOL_SMART):
			smartMols.append(mol)
			continue

		name = prefget(MOLECULE_DEFAULT, MOL_RIBBONMODE)
		if name != RibbonXSectionOption.default:
			from RibbonStyleEditor import xsection
			xs = xsection.findXSection(name)
			if xs:
				for res in mol.residues:
					xs.setResidue(res)

		name = prefget(MOLECULE_DEFAULT, MOL_RIBBONSCALE)
		if name != RibbonScalingOption.default:
			from RibbonStyleEditor import scaling
			sc = scaling.findScaling(name)
			if sc:
				for res in mol.residues:
					sc.setResidue(res)

		ribbonDisp = prefget(MOLECULE_DEFAULT, MOL_RIBBONDISP)
		if ribbonDisp != RibbonDisplayOption.default:
			for res in mol.residues:
				setattr(res, RibbonDisplayOption.attribute,
								ribbonDisp)

		hideBackbone = prefget(MOLECULE_DEFAULT, MOL_HIDE_BACKBONE)
		if hideBackbone != RibbonHideBackboneOption.default:
			mol.ribbonHidesMainchain = hideBackbone
		
		atomDraw = prefget(MOLECULE_DEFAULT, MOL_ATOMDRAW)
		if atomDraw != AtomDrawModeOption.default:
			for a in mol.atoms:
				setattr(a, AtomDrawModeOption.attribute,
							atomDraw)
			
		bondDraw = prefget(MOLECULE_DEFAULT, MOL_BONDDRAW)
		if bondDraw != BondDrawModeOption.default:
			for b in mol.bonds:
				setattr(b, BondDrawModeOption.attribute,
							bondDraw)
			
		perAtom = prefget(MOLECULE_DEFAULT, MOL_PERATOM)
		if perAtom == "by element":
			import Midas
			Midas.color('byatom', mol.oslIdent())
		elif perAtom == "by heteroatom":
			import Midas
			Midas.color('byhet', mol.oslIdent())
		
		autochain = prefget(MOLECULE_DEFAULT, MOL_AUTOCHAIN)
		if autochain != AutoChainOption.default:
			setattr(mol, AutoChainOption.attribute, autochain)

	if smartMols:
		from preset import preset
		preset(openedModels=smartMols)

_postCategorizeModels = []
def categorizeSurface(*args):
	import Categorizer
	Categorizer.categorize(*args)
	if _postCategorizeModels:
		from initprefs import MOLECULE_DEFAULT, MOL_IONS_REPR
		import preferences
		prefget = preferences.get
		ionsDraw = prefget(MOLECULE_DEFAULT, MOL_IONS_REPR)
		prefModels = []
		for m in _postCategorizeModels:
			if isinstance(m, Molecule) and not m.__destroyed__:
				if hasattr(m, "noprefs"):
					del m.noprefs
					continue
				prefModels.append(m)
		del _postCategorizeModels[:]
		processNewMolecules(prefModels)
		for model in prefModels:
			for a in model.atoms:
				if ionLike(a):
					a.drawMode = ionsDraw

def ionLike(a):
	from elements import metals
	return a.surfaceCategory == "ions" and (len(a.residue.atoms) == 1
					or a.element in metals)

def defCatAtoms(trigName, myData, atoms):
	for a in atoms.created:
		if not a.surfaceCategory:
			if a.element.number < 9:
				a.surfaceCategory = "solvent"
			else:
				a.surfaceCategory = "ions"

_catHandler = triggers.addHandler('Bond', categorizeSurface, 0)
_defCatHandler = triggers.addHandler('Atom', defCatAtoms, None)

def checkKsdssp(trigName, myData, models):
	from misc import isProtein
	from replyobj import info, status
	from initprefs import ksdsspPrefs, KSDSSP_ENERGY, KSDSSP_HELIX_LENGTH, \
							KSDSSP_STRAND_LENGTH
	import preferences
	energy = ksdsspPrefs[KSDSSP_ENERGY]
	helixLen = ksdsspPrefs[KSDSSP_HELIX_LENGTH]
	strandLen = ksdsspPrefs[KSDSSP_STRAND_LENGTH]
	for model in models:
		if not isinstance(model, Molecule):
			continue
		if model.structureAssigned or not isProtein(model):
			continue
		
		status("Computing secondary structure assignments...\n")
		model.computeSecondaryStructure(energy, helixLen, strandLen)
		status("Computed secondary structure assignments "
							"(see reply log)\n")
		if model == models[0]:
			info(
"""Model %s (%s) appears to be a protein without secondary structure assignments.
Automatically computing assignments using 'ksdssp' and parameter values:
  energy cutoff %g
  minimum helix length %d
  minimum strand length %d
Use command 'help ksdssp' for more information.
""" % (model.oslIdent()[1:], model.name, energy, helixLen, strandLen))
		else:
			info("Model %s (%s) has no secondary structure assignments. Running ksdssp.\n" % (model.oslIdent()[1:], model.name))
_ckHandler = openModels.addAddHandler(checkKsdssp, None)

def _addMODRES(trigName, myData, pdbMolecules):
	"""Add PDB MODRES residues that modify standard residues to
	residue sequence codes"""

	import resCode
	dicts =	(resCode.regex3to1, resCode.nucleic3to1, resCode.protein3to1,
			resCode.standard3to1)
	for m in pdbMolecules:
		try:
			mrRecords = m.pdbHeaders["MODRES"]
		except (AttributeError, KeyError):
			continue
		for mr in mrRecords:
			# chimera allows for 4 character residue names
			# in PDB files
			name = mr[12:16].strip()
			stdName = mr[24:28].strip()
			for d in dicts:
				if stdName in d and name not in d:
					d[name] = d[stdName]
_modresHandler = openModels.addAddHandler(_addMODRES, None)

def suppressNewMoleculeProcessing(*args):
	global _catHandler, _ckHandler, _defCatHandler, _unprocessedModels
	# in case there was an error in an earlier session restore,
	# use an if statement...
	if _catHandler is not None:
		openModels.deleteAddHandler(_ckHandler)
		triggers.deleteHandler('Bond', _catHandler)
		triggers.deleteHandler('Atom', _defCatHandler)
		_unprocessedModels = _postCategorizeModels[:]
		_catHandler = _ckHandler = _defCatHandler = None

def restoreNewMoleculeProcessing(*args):
	global _catHandler, _ckHandler, _defCatHandler, _postCategorizeModels
	if _catHandler is not None:
		# old sessions had no BEGIN trigger, compensate
		return
	# fire triggers so that the below handlers aren't called
	from update import checkForChanges
	checkForChanges()
	_catHandler = triggers.addHandler('Bond', categorizeSurface, 0)
	_defCatHandler = triggers.addHandler('Atom', defCatAtoms, None)
	_ckHandler = openModels.addAddHandler(checkKsdssp, None)
	_postCategorizeModels = _unprocessedModels

from SimpleSession import BEGIN_RESTORE_SESSION, END_RESTORE_SESSION
triggers.addHandler(BEGIN_RESTORE_SESSION, suppressNewMoleculeProcessing, None)
triggers.addHandler(END_RESTORE_SESSION, restoreNewMoleculeProcessing, None)

#
# export application name
#

appName = "chimera"	# actual application name
AppName = "Chimera"	# capitalized application name (used for Tk class too)

# convenience for programming...
def runCommand(*args, **kw):
	from Midas.midas_text import makeCommand
	makeCommand(*args, **kw)
