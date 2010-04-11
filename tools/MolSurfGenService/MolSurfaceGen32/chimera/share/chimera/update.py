# The update interval is how often we ask the viewer to poll for changes
# (to models, potentially other stuff) that could cause a redisplay.  If
# such a condition exists, a redisplay is requested, and the next time
# the event loop is idle, the redisplay happens.  Ideally, this number
# would be related to the screen refresh frequency.
#
# Note: in practice, we will never achieve the given update rate as the
# time to update the state via the trigger mechanism is not accounted for.
# See chimera gnats bug XXX for more details.

from __future__ import with_statement
from contextlib import contextmanager
import chimera

UPDATE_INTERVAL	= 33	# 33.33 milliseconds = 30 times per second.
MIN_EVENT_TIME = 1	# Minumum input event processing time per
			#  update interval in milliseconds.

_frameNumber = 0
_inFrameUpdate = False
_frameUpdateStarted = False
_needRedisplay = {}
_blockFUStack = []
inTriggerProcessing = 0

def startFrameUpdate(app):
	global _frameUpdateStarted
	if _frameUpdateStarted:
		return
	_frameUpdateStarted = True
	app.after(UPDATE_INTERVAL, lambda a=app: _frameUpdateLoop(app=a))

@contextmanager
def blockFrameUpdates(forChanges=False):
	global _inFrameUpdate, inTriggerProcessing
	_blockFUStack.append(_inFrameUpdate)
	_inFrameUpdate = True
	if forChanges:
		inTriggerProcessing += 1
	yield
	_inFrameUpdate = _blockFUStack.pop()
	if forChanges:
		inTriggerProcessing -= 1

def _frameUpdateLoop(app):
	"""Do a frame update and schedule a timer for the next frame update."""
	global _inFrameUpdate
	if _inFrameUpdate:
		# Frame update has been blocked with blockFrameUpdates().
		app.after(UPDATE_INTERVAL,
			  lambda a=app: _frameUpdateLoop(app=a))
		return
	import time
	t0 = time.time()
	_frameUpdate(app)
	t1 = time.time()
	frame_time = (t1 - t0) * 1000	# milliseconds
	min_delay = MIN_EVENT_TIME * max(1,int(frame_time/UPDATE_INTERVAL))
	delay = max(min_delay, int(UPDATE_INTERVAL - frame_time))
	app.after(delay, lambda a=app: _frameUpdateLoop(app=a))

def _frameUpdate(app):
	global _inFrameUpdate
	_inFrameUpdate = True
	global _frameNumber
	chimera.triggers.activateTrigger('new frame', _frameNumber)
	chimera.viewer.checkInitialView()
	checkForChanges()
	while _needRedisplay:
		v, dummy = _needRedisplay.popitem()
		v.displayCB(None)
	chimera.triggers.activateTrigger('post-frame', _frameNumber)
	_frameNumber += 1
	_inFrameUpdate = False

def checkForChanges():
	"""check and propagate chimera data changes

	This is called once per frame and whenever otherwise needed.
	"""
	with blockFrameUpdates(forChanges=True):
		chimera.triggers.activateTrigger('check for changes', None)
		track = chimera.TrackChanges.get()
		names = track.check()
		allChanges = []
		selChanges = None	# TODO: remove if selections move to C++
		for n in names:
			name = n.split('.')[-1]
			# Viewer always needed below.
			# Model is needed for sloppy extensions that
			# don't destroy() their temporary models.
			if (name not in ('Viewer', 'Model')
			and not chimera.triggers.hasHandlers(name)):
				continue
			if name == 'Selectable':
				selChanges = track.changes(n)
				continue
			allChanges.append((name, track.changes(n)))
		track.clear()
		if selChanges:
			chimera.triggers.activateTrigger('Selectable',
								selChanges)
		for name, changes in allChanges:
			chimera.triggers.activateTrigger(name, changes)
		if selChanges:
			allChanges = [('Selectable', selChanges)] + allChanges
		chimera.triggers.activateTrigger('monitor changes', allChanges)
		changes = [c for n, c in allChanges if n == 'Viewer']
		if changes:
			modified = changes[0].created | changes[0].modified
			if modified:
				if chimera.nogui:
					for v in modified:
						v.postRedisplay()
				else:
					global _needRedisplay
					for v in modified:
						_needRedisplay[v] = True

def withoutChecks(func):
	# This was designed for IDLE, so a python command could be run
	# without triggers happening during the command
	with blockFrameUpdates():
		func()

_quitRequested = False
def quitCB(*args):
	global _quitRequested
	_quitRequested = True

_waitHandler = None
def wait(waiting, app):
	if not app:
		global _frameNumber
		while waiting():
			chimera.triggers.activateTrigger('new frame',
								_frameNumber)
			checkForChanges()
			chimera.triggers.activateTrigger('post-frame',
								_frameNumber)
			_frameNumber += 1
		return
	startFrameUpdate(app)
	global _waitHandler
	if _waitHandler is None:
		from chimera import APPQUIT
		_waitHandler = chimera.triggers.addHandler(
							APPQUIT, quitCB, None)
	app.viewer.setCursor('wait')
	changesActive = True
	while waiting() and not _quitRequested:
		app.tk.dooneevent()
	app.viewer.setCursor(None)
	if _quitRequested:
		from chimera import ChimeraSystemExit
		raise ChimeraSystemExit, 0

#
# Process only events for a specific widget.
# This is used to detect clicks on halt buttons without handling other events.
#
def processWidgetEvents(w, maxEvents = 100):
	import _tkinter as tk
	from _chimera import restrictEventProcessing
	restrictEventProcessing(w.winfo_id())
	try:
		for i in range(maxEvents):
			if not tk.dooneevent(tk.WINDOW_EVENTS|tk.DONT_WAIT):
				break
	finally:
		restrictEventProcessing(0)
