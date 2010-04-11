# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

def run(cmdName, args):
	fields = args.split(None, 1)
	if len(fields) > 1:
		opt, args = fields
	else:
		opt = fields[0]
		args = ""
	from util import findBestMatch
	try:
		bestMatch = findBestMatch(opt, _optArgsTable.iterkeys())
	except ValueError, s:
		from chimera import UserError
		raise UserError("bad option: %s" % s)
	func, kw = _optArgsTable[bestMatch]
	from Midas.midas_text import doExtensionFunc
	doExtensionFunc(func, args, **kw)

def startCommand(molecule, name="default", method="corkscrew",
			rate="linear", frames=20, cartesian=False):
	from chimera import UserError
	if len(molecule) != 1:
		raise UserError("You must specify exactly one molecule")
	m = molecule[0]

	try:
		ms = _find(name)
	except UserError:
		pass
	else:
		raise UserError("You already defined \"%s\"" % name)
	kw = {
		"method": method,
		"rate": rate,
		"frames": frames,
		"cartesian": cartesian,
	}
	_verifyOpts(kw)
	from base import Script
	ms = Script(m, closeCB=_close, **kw)
	_add(name, ms)
	from chimera import replyobj
	msg = "Interpolation \"%s\" created\n" % name
	replyobj.message(msg)
	replyobj.status(msg)
	return ms

def interpolateCommand(molecule, name="default", method=None, rate=None,
			frames=None, cartesian=False):
	if len(molecule) != 1:
		from chimera import UserError
		raise UserError("You must specify exactly one molecule")
	m = molecule[0]

	ms = _find(name)
	kw = {}
	if method is not None:
		kw["method"] = method
	if rate is not None:
		kw["rate"] = rate
	if frames is not None:
		kw["frames"] = frames
	_verifyOpts(kw)
	ms.addAction(m, **kw)
	from chimera import replyobj
	msg = "Interpolation \"%s\" updated\n" % name
	replyobj.message(msg)
	replyobj.status(msg)

def movieCommand(name="default", minimize=None, steps=None):
	import util
	ms = _find(name)
	ms.updateMovieDialog(True, minimize=minimize, steps=steps)

def doneCommand(name="default"):
	from chimera import replyobj
	_remove(name)
	msg = "Interpolation \"%s\" removed\n" % name
	replyobj.message(msg)
	replyobj.status(msg)


#
# Private functions and data
#

_optArgsTable = {
	"start": (
		startCommand,
		{ "specInfo":[("spec", "molecule", "molecules")] }
	),
	"interpolate": (
		interpolateCommand,
		{ "specInfo":[("spec", "molecule", "molecules")] }
	),
	"movie": (
		movieCommand,
		{}
	),
	"done": (
		doneCommand,
		{}
	),
}

_motions = {}		# Map from name to MolecularMotion instance

def _find(name):
	try:
		return _motions[name]
	except KeyError:
		from chimera import UserError
		raise UserError("There is no morph named \"%s\"." % name)

def _remove(name):
	ms = _find(name)
	ms.finish()
	del _motions[name]

def _add(name, ms):
	_motions[name] = ms

def _close(script):
	# Callback invoked when a script is changed due to
	# molecules being closed.  If there are still actions,
	# we don't need to do anything.  But if all relevant
	# models are closed, then we also remove this script.
	if script.actions:
		return
	for n, s in _motions.iteritems():
		if script is s:
			_remove(n)
			from chimera import replyobj
			replyobj.message("Morph \"%s\" removed\n" % n)
			break

def _verifyOpts(kw):
	from chimera import UserError
	from util import findBestMatch
	from Interpolate import InterpolationMap, RateMap
	if kw.has_key("method"):
		method = kw["method"]
		try:
			findBestMatch(method, InterpolationMap.iterkeys())
		except ValueError, s:
			raise UserError("bad interpolation method: %s" % str(s))
	if kw.has_key("rate"):
		rate = kw["rate"]
		try:
			findBestMatch(rate, RateMap.iterkeys())
		except ValueError, s:
			raise UserError("bad rate: %s" % s)
	if kw.has_key("frames"):
		frames = kw["frames"]
		if type(frames) != type(0):
			raise UserError("bad frames: must be an integer")
		if frames <= 1:
			raise UserError("bad frames: must be greater than 1")
	if kw.has_key("steps"):
		steps = kw["steps"]
		if type(steps) != type(0):
			raise UserError("bad steps: must be an integer")
		if steps < 1:
			raise UserError("bad steps: must be greater than 0")
