# This is an implementation of the NMRCLUST algorithm

debug = False

class NMRClust:

	def __init__(self, distanceMatrix):
		# distanceMatrix should be a map whose key
		# is a two-tuple of indices and whose value
		# is the distance
		from heapq import heappush
		self.dm = distanceMatrix
		self.size = distanceMatrix.size
		self.clusters = set([])
		cluster = []
		for i in range(self.size):
			c = Cluster(0, i, 1, 0.0)
			cluster.append(c)
			self.clusters.add(c)
		self.distances = []
		self.matrix = {}
		for i in range(self.size):
			for j in range(i + 1, self.size):
				d = distanceMatrix.get(i, j)
				k = (cluster[i], cluster[j])
				heappush(self.distances, (d, k))
				self.matrix[k] = d
		step = 0
		self.avSp = []
		while len(self.clusters) > 1:
			step += 1
			self._reduce(step)
			self._addAvgSpread()
		for c in self.clusters:
			self.root = c
			break
		if self.avSp:
			# Only cut if there are more than one cluster
			self._cut()

	def _reduce(self, step):
		# Merge two clusters into one and compute the average spread
		from heapq import heappush, heappop
		while True:
			d, (c0, c1) = heappop(self.distances)
			if c0 not in self.clusters or c1 not in self.clusters:
				# One or both clusters already merged
				continue
			self.clusters.remove(c0)
			self.clusters.remove(c1)
			nc = Cluster(step, [c0, c1], c0.size + c1.size,
					self._spread(c0, c1))
			for c in self.clusters:
				d = self._distance(c, nc)
				k = (c, nc)
				heappush(self.distances, (d, k))
				self.matrix[k] = d
			self.clusters.add(nc)
			break

	def _clusterDistance(self, c0, c1):
		try:
			return self.matrix[(c1, c0)]
		except KeyError:
			return self.matrix[(c0, c1)]

	if debug:
		def _dumbSpread(self, c0, c1):
			members = c0.members() + c1.members()
			sum = 0.0
			count = 0
			for i in range(len(members)):
				mi = members[i]
				for j in range(i + 1, len(members)):
					mj = members[j]
					d = self.dm.get(mi, mj)
					count += 1
					sum += d
			return sum / count

		def _dumbDistance(self, c, nc):
			sum = 0.0
			count = 0
			for m0 in c.members():
				for m1 in nc.members():
					d = self.dm.get(m0, m1)
					count += 1
					sum += d
			return sum / count

	def _spread(self, c0, c1):
		# Compute the spread when combining two clusters
		w0 = (c0.size * (c0.size - 1) / 2)
		w1 = (c1.size * (c1.size - 1) / 2)
		d = self._clusterDistance(c0, c1)
		w01 = c0.size * c1.size
		spread = ((w0 * c0.spread + w1 * c1.spread + w01 * d)
				/ (w0 + w1 + w01))
		if debug:
			dumbSpread = self._dumbSpread(c0, c1)
			if not floatEqual(spread, dumbSpread):
				print "bad spread", spread, dumbSpread
		return spread

	def _distance(self, c, nc):
		# Compute the average distance between clusters
		c0, c1 = nc.value
		d0 = self._clusterDistance(c, c0)
		d1 = self._clusterDistance(c, c1)
		w0 = c0.size * c.size
		w1 = c1.size * c.size
		d = (w0 * d0 + w1 * d1) / (w0 + w1)
		if debug:
			dumbD = self._dumbDistance(c, nc)
			if not floatEqual(d, dumbD):
				print "bad distance", d, dumbD
		return d

	def _addAvgSpread(self):
		cnum = 0
		spread = 0.0
		for c in self.clusters:
			if c.size > 1:
				# Only count if not outlier (cluster of one)
				cnum += 1
				spread += c.spread
		self.avSp.append(spread / cnum)

	def _cut(self):
		maxAvSp = max(self.avSp)
		minAvSp = min(self.avSp)
		coeff = (self.size - 2) / (maxAvSp - minAvSp)
		avSpNorm = []
		penalty = []
		step = 0
		cutStep = None
		minPenalty = None
		for avSp in self.avSp:
			step += 1
			nclusi = self.size - step
			avspni = coeff * (avSp - minAvSp) + 1
			avSpNorm.append(avspni)
			p = avspni + nclusi
			penalty.append(p)
			if cutStep is None or p < minPenalty:
				cutStep = step
				minPenalty = p
		self.clusters = set([])
		self._prune(cutStep, self.root)

	def _prune(self, cutStep, c):
		if c.step <= cutStep or c.isLeaf():
			self.clusters.add(c)
		else:
			for c in c.value:
				self._prune(cutStep, c)

	def __str__(self):
		memberList = []
		for c in self.clusters:
			mList = [ str(v) for v in c.members() ]
			memberList.append("{%s}" % ','.join(mList))
		return "[%s]" % ','.join(memberList)

	def representative(self, c):
		members = c.members()
		if len(members) == 1:
			return members[0]
		from distmat import DistanceMatrix
		dm = DistanceMatrix(len(members))
		for i in range(len(members)):
			mi = members[i]
			for j in range(i + 1, len(members)):
				mj = members[j]
				dm.set(i, j, self.dm.get(mi, mj))
		rep = dm.representative()
		return members[rep]


class Cluster:

	def __init__(self, step, value, size, spread):
		self.step = step
		self.value = value
		self.size = size
		self.spread = spread

	def __str__(self):
		if self.isLeaf():
			return str(self.value)
		else:
			return "(%s)" % ','.join([ str(c) for c in self.value ])

	def isLeaf(self):
		return self.size == 1

	def members(self):
		if self.isLeaf():
			return [ self.value ]
		m = []
		for c in self.value:
			m += c.members()
		return m


def floatEqual(n0, n1):
	return abs(n0 - n1) < 1e-5


if __name__ == "__main__":
	from distmat import DistanceMatrix
	dm = DistanceMatrix(4)
	dm.set(0, 1, 0.2)
	dm.set(0, 2, 1.0)
	dm.set(0, 3, 1.0)
	dm.set(1, 2, 0.8)
	dm.set(1, 3, 0.7)
	dm.set(2, 3, 0.1)
	cl = NMRClust(dm)
	for c in cl.clusters:
		print cl.representative(c), c
