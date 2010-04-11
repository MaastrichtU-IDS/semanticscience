FreezeNone = "none"
FreezeSelected = "selected"
FreezeUnselected = "unselected"

class Minimizer:

	def __init__(self, molecules, nsteps=100, stepsize=0.02,
			interval=10, freeze=FreezeNone,
			nogui=False, addhyd=True, callback=None):
		self._mi = None
		# nsteps and interval are public and may be changed by caller
		self.nsteps = nsteps
		self.stepsize = stepsize
		self.interval = interval
		self.freeze = freeze
		self.callback = callback
		_find(molecules, nogui, addhyd, self._finishInit)

	def _finishInit(self, mi):
		self._mi = mi
		if self.callback:
			self.callback(self)
		del self.callback

	def updateCoords(self, mi):
		import chimera
		assert(self._mi is mi)
		self._mi.saveMMTKCoordinates()
		chimera.runCommand("wait 1")

	def run(self):
		if self._mi is None:
			from chimera import UserError
			raise UserError("Please finish adding hydrogens and "
					"charges before trying to minimize")
		import chimera
		self._mi.setFixed(self.freeze)
		self._mi.loadMMTKCoordinates()
		chimera.runCommand("wait 1")
		self._mi.minimize(nsteps=self.nsteps, stepsize=self.stepsize,
					interval=self.interval,
					action=self.updateCoords)

# Private functions below here

_miCache = []

def _find(molecules, nogui, addhyd, callback):
	global _miCache
	#print "_find", id(_miCache), _miCache
	for t in _miCache:
		mols, mi = t
		if _sameMolecules(mols, molecules):
			callback(mi)
			return
	def cacheIt(mi, molecules=molecules, callback=callback, cache=_miCache):
		#print "cacheIt", id(cache), cache
		callback(mi)
		cache.append((molecules, mi))
		#print "end cacheIt", id(cache), cache
	#print "creating MMTKinter instance", molecules
	from MMTKinter import MMTKinter
	mi = MMTKinter(molecules, nogui=nogui, addhyd=addhyd, callback=cacheIt)

def _sameMolecules(ml0, ml1):
	if len(ml0) != len(ml1):
		return False
	tl = ml1[:]
	for m in ml0:
		try:
			tl.remove(m)
		except ValueError:
			return False
	return True

def _moleculeCheck(triggerName, data, mols):
	# Remove all entries that refer to a molecule that is being closed
	_removeFromCache(mols)

def _removeFromCache(mols):
	global _miCache
	#print "Remove from cache", id(_miCache), _miCache
	junk = []
	for t in _miCache:
		molecules = t[0]
		for m in mols:
			if m in molecules:
				junk.append(t)
				break
	for t in junk:
		_miCache.remove(t)

def _atomCheck(trigger, closure, atoms):
	# If an atom is deleted, we invalidate the entire cache because
	# there's no easy way to find out the molecule from which the
	# atom was deleted (the C++ object is already gone).  If an atom
	# is added, we can do partial invalidation of the cache.
	if atoms.deleted:
		global _miCache
		while _miCache:
			_miCache.pop()
		#print "clear miCache, atom delete", id(_miCache), _miCache
		return
	if atoms.created:
		mols = set([])
		for a in atoms.created:
			mols.add(a.molecule)
		_removeFromCache(mols)

def _bondCheck(trigger, closure, bonds):
	# See _atomCheck comment
	if bonds.deleted:
		global _miCache
		while _miCache:
			_miCache.pop()
		#print "clear miCache, bond delete", id(_miCache), _miCache
		return
	if bonds.created:
		mols = set([])
		for b in bonds.created:
			mols.add(b.molecule)
		_removeFromCache(mols)

# Register for model removal so we can clean up our cache

import chimera
chimera.openModels.addRemoveHandler(_moleculeCheck, None)
chimera.triggers.addHandler("Atom", _atomCheck, None)
chimera.triggers.addHandler("Bond", _bondCheck, None)
