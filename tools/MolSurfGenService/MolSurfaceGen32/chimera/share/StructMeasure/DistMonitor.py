# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: DistMonitor.py 27803 2009-06-09 23:09:05Z gregc $

import operator
import chimera
from chimera.misc import getPseudoBondGroup

def _addGroup(category, color):
	g = getPseudoBondGroup(category, modelID=-2, hidden=1)
	if not hasattr(g, 'fixedLabels'):
		def _setColor(color=color, g=g):
			from chimera.colorTable import getColorByName
			g.color = getColorByName(color)
			g.lineType = chimera.Dash
		# delay setting the color until colors are set up
		chimera.registerPostGraphicsFunc(_setColor)
		g.fixedLabels = 0
		g.updateCallbacks = []
	return g

distanceMonitor = _addGroup('distance monitor', 'yellow')
distanceHandlers = {}

def updateDistance(*args):
	if len(distanceMonitor.pseudoBonds) == 0 and distanceHandlers:
		_clearHandlers()
		return
	for b in distanceMonitor.pseudoBonds:
		format = '%%.%df' % _pref['precision']
		if _pref['show units']:
			format += u'\u00C5'
		b.distance = format % b.length()
		if not distanceMonitor.fixedLabels:
			b.label = b.distance
	for cb in distanceMonitor.updateCallbacks:
		cb()

def addDistance(atom1, atom2):
	b = _findDistance(atom1, atom2)
	if b is not None:
		from chimera import UserError
		raise UserError('Distance monitor already exists')
	b = distanceMonitor.newPseudoBond(atom1, atom2)
	from chimera import replyobj
	replyobj.info("Distance between %s and %s: %.*f\n" % (atom1, atom2,
					_pref['precision'], b.length()))
	b.drawMode = chimera.Bond.Wire
	updateDistance()
	if not distanceHandlers:
		_startHandlers()
	return b

def removeDistance(*args):
	if len(args) == 1:
		b = args[0]
	elif len(args) == 2:
		b = _findDistance(args[0], args[1])
		if b is None:
			raise ValueError, 'distance monitor does not exist'
	else:
		raise ValueError, 'wrong number of argument to removeDistance'
	distanceMonitor.deletePseudoBond(b)

def _clearHandlers():
	for trigName, handler in distanceHandlers.items():
		chimera.triggers.deleteHandler(trigName, handler)
	distanceHandlers.clear()

def _findDistance(atom1, atom2):
	for b in distanceMonitor.pseudoBonds:
		atoms = b.atoms
		if atoms[0] == atom1 and atoms[1] == atom2:
			return b
		if atoms[0] == atom2 and atoms[1] == atom1:
			return b
	return None

def _startHandlers():
	def justCSMods(trigName, myData, changes):
		if changes.modified:
			updateDistance()
	distanceHandlers['CoordSet'] = chimera.triggers.addHandler(
					'CoordSet', justCSMods, None)
	def justCoordSets(trigName, myData, changes):
		if 'activeCoordSet changed' in changes.reasons:
			updateDistance()
	distanceHandlers['Molecule'] = chimera.triggers.addHandler(
					'Molecule', justCoordSets, None)
	def openStateCB(trigName, myData, changes):
		if 'transformation change' not in changes.reasons:
			return
		activity = None
		for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
			if activity is None:
				activity = m.openState.active
			elif activity != m.openState.active:
				updateDistance()
				return
	distanceHandlers['OpenState'] = chimera.triggers.addHandler(
					'OpenState', openStateCB, None)

from chimera import preferences
_pref = preferences.addCategory("Distance Monitors",
				preferences.HiddenCategory,
				optDict={
					'precision': 3,
					'show units': True
				})

def precision():
	return _pref['precision']

def setPrecision(p):
	if not isinstance(p, int):
		raise TypeError, "precision must be integer"
	if p < 0:
		raise ValueError, "precision must be non-negative"
	_pref['precision'] = p
	updateDistance()

def showUnits(val=None):
	if val is None:
		return _pref['show units']
	_pref['show units'] = val
	updateDistance()

##### saving into sessions:
def restoreDistances(version=1):
	import StructMeasure
	from StructMeasure.DistMonitor import distanceMonitor
	if len(distanceMonitor.pseudoBonds) > 0 and not distanceHandlers:
		_startHandlers()

def _sessionSave(trigName, myData, sessionFile):
	print>>sessionFile, """
try:
	import StructMeasure
	from StructMeasure.DistMonitor import restoreDistances
	registerAfterModelsCB(restoreDistances, 1)
except:
	reportRestoreError("Error restoring distances in session")
"""


from SimpleSession import SAVE_SESSION
chimera.triggers.addHandler(SAVE_SESSION, _sessionSave, None)
