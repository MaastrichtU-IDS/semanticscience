import os, sys, subprocess
from string import split, strip, join

def _sum(a, b):
	return (a[0] + b[0], a[1] + b[1], a[2] + b[2])

def _dist(a, b):
	return ( (a[0] - b[0]) **2 + (a[1] - b[1]) **2 + (a[2] - b[2]) **2 ) ** 0.5

def _rawDist(a, b):
	return ((a[0] - b[0]) **2 + (a[1] - b[1]) **2 + (a[2] - b[2]) **2)

def _orientAboutNormal(rawTriangles, facePt):
	rT = []
	for t in rawTriangles:
		t0, t1, t2 = t
		a = (t1[0] - t0[0], t1[1] - t0[1], t1[2] - t0[2])
		b = (t2[0] - t0[0], t2[1] - t0[1], t2[2] - t0[2])
		c = (a[1]*b[2] - a[2]*b[1], a[2]*b[0] - b[2]*a[0], a[0]*b[1] - b[0]*a[1])
		d = (c[0]*c[0] + c[1]*c[1] + c[2]*c[2]) ** 0.5
		if d == 0: d = 1	#bad case, shouldn't happen
		c = (c[0] / d, c[1] / d, c[2] / d)

		if _rawDist(facePt, _sum(t0, c)) > _rawDist(facePt, _sum(t0, (-c[0], -c[1], -c[2]))):
			rT.append( (t0, t2, t1) )
		else:
			rT.append( (t0, t1, t2) )
	return rT

def _getCentroids(rList):
	cList = []
	for r in rList:
		c = [0.0] * 3
		for a in r.atoms:
			p = a.xformCoord()
			c[0] += p.x
			c[1] += p.y
			c[2] += p.z
		cList.append( (c[0]/len(r.atoms), c[1]/len(r.atoms), c[2]/len(r.atoms) ) )
	return cList

def _pruneResidues(rList, prune, minDist):
	pList = prune.residues
	if callable(pList):
		pList = pList()

	rCentroids = _getCentroids(rList)
	pCentroids = _getCentroids(pList)

	rNewList = []
	for r in range(len(rList)):
		add = 0
		for p in range(len(pList)):
			if _dist(rCentroids[r], pCentroids[p]) < minDist:
				add = 1
				break
		if add:
			rNewList.append(rList[r])
	return rNewList

# Unpack atom lists from Chimera molecules/chains
def GetAtomList(target, prune = None, pruneDist = 30):
	if type(target) is type([]):
		return target
	rList = target.residues
	if callable(rList):
		rList = rList()

	if prune:
		rList = _pruneResidues(rList, prune, pruneDist)

	aList = []
	for r in rList:
		aList.extend(r.atoms)
	return aList

# Unpack Intersurf data from atom lists
def UnpackIntersurfData(atoms_A, atoms_B):
	data = []
	for a in atoms_A:
		p = a.xformCoord()
		data.append( (1, (p.x, p.y, p.z), (a.radius, a)) )
	for a in atoms_B:
		p = a.xformCoord()
		data.append( (2, (p.x, p.y, p.z), (a.radius, a)) )
	return data

# Compute Delaunay Tetrahedralization
def ComputeTetrahedralization(data):
	from CGLutil.findExecutable import findExecutable
	qdelaunay_exe = findExecutable("qdelaunay")
	if qdelaunay_exe == None:
		qdelaunay_exe = "qdelaunay"

	p = subprocess.Popen([qdelaunay_exe, "QJ", "i"],
				stdin=subprocess.PIPE,
				stdout=subprocess.PIPE,
				stderr=subprocess.STDOUT)
	child_stdin = p.stdin
	child_stdout = p.stdout
	child_stdin.write(str(3) + "\n")
	child_stdin.write(str(len(data)) + "\n")
	for point in data:
		child_stdin.write(join(map(str, point[1])) + "\n")
	child_stdin.close()

	lines = []
	for line in child_stdout:
		lines.append(strip(line))
	child_stdout.close()
	tetrahedra = map(lambda x: map(int, x), map(split, lines[1:]))

	return tetrahedra

def _getMid(a, b, y, z, bias):
	d = _dist(a, b)

	y, atom_a = y
	z, atom_b = z

	if d == 0: return (a[0], a[1], a[2], (atom_a, atom_b))
	k = ((1 - bias)*y + bias*(d - z))/d
	c0 = a[0] + k*(b[0] - a[0])
	c1 = a[1] + k*(b[1] - a[1])
	c2 = a[2] + k*(b[2] - a[2])
	return (c0, c1, c2, (atom_a, atom_b))

def _surfPoint(s, p):
	try:
		return s[p]
	except:
		n = s[p] = len(s.keys())
		return n

# Compute Surface using Marching Tetrahedra
# Bias 0 is toward Molecule 1
def ComputeSurface(data, tetrahedra, bias=0.5):
	s = {}
	surfTriangles = []

	realTetra = []
	tetraResolver = lambda x: data[t[x]]
	for t in tetrahedra:
		t_pts = map(tetraResolver, [0, 1, 2, 3])
		if(t_pts[0][0] == t_pts[1][0] == t_pts[2][0] == t_pts[3][0]):
			continue
		realTetra.append(t_pts)
	del tetrahedra

	_sP = lambda x: _surfPoint(s, x)
	for t in realTetra:
		t.sort()
		t0, t1, t2, t3 = (t[0][1], t[1][1], t[2][1], t[3][1])
		t0r, t1r, t2r, t3r = (t[0][2], t[1][2], t[2][2], t[3][2])

		if(t[1][0] == t[2][0] == 1):
			if t[2][0] == t[3][0]:
				t0, t1, t2, t3 = (t3, t0, t1, t2)
				t0r, t1r, t2r, t3r = (t3r, t0r, t1r, t2r)

			m0 = _getMid(t0, t3, t0r, t3r, bias)
			m1 = _getMid(t1, t3, t1r, t3r, bias)
			m2 = _getMid(t2, t3, t2r, t3r, bias)
			rawTriangles = [(m0, m1, m2)]
		elif(t[1][0] == t[2][0] == 2):
			if t[0][0] == t[1][0]:
				t0, t1, t2, t3 = (t3, t0, t1, t2)
				t0r, t1r, t2r, t3r = (t3r, t0r, t1r, t2r)

			m0 = _getMid(t0, t1, t0r, t1r, bias)
			m1 = _getMid(t0, t2, t0r, t2r, bias)
			m2 = _getMid(t0, t3, t0r, t3r, bias)
			rawTriangles = [(m0, m1, m2)]
		else:
			if t[0][0] == 2:
				t0, t1, t2, t3 = (t2, t3, t0, t1)
				t0r, t1r, t2r, t3r = (t2r, t3r, t0r, t1r)

			m02 = _getMid(t0, t2, t0r, t2r, bias)
			m03 = _getMid(t0, t3, t0r, t3r, bias)
			m12 = _getMid(t1, t2, t1r, t2r, bias)
			m13 = _getMid(t1, t3, t1r, t3r, bias)
			rawTriangles = [(m02, m03, m13), (m02, m12, m13)]

		rawTriangles = _orientAboutNormal(rawTriangles, t0)
		for t in rawTriangles:
			surfTriangles.append(map(_sP, t))

	surf_point_list = map(lambda x: (x[1], x[0]), s.items())
	surf_point_list.sort()
	surf_point_list = map(lambda x: x[1], surf_point_list)

	surfPoints = []
	surfAtoms = []
	for p in surf_point_list:
		surfPoints.append((p[0], p[1], p[2]))
		surfAtoms.append(p[3])

	return [surfPoints, surfTriangles, surfAtoms]
