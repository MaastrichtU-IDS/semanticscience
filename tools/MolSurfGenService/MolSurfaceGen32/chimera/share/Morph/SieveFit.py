def fitModels(m0, m1, fraction=0.5):
	"""sieveFitModels takes two conformers and identifies the
	fraction of the residues that produce the minimum RMSD."""

	rList0 = m0.residues
	rList1 = m1.residues

	return fitResidues(rList0, rList1, fraction)

def fitResidues(rList0, rList1, fraction=0.5, maxrmsd=0.1):
	"""sieveFitModels takes two lists of corresponding residues
	and identifies the fraction of the residues that produce
	the minimum RMSD."""
	# make sure the residues correspond
	if len(rList0) != len(rList1):
		raise ValueError("matching different number of residues")
	#for r0, r1 in zip(rList0, rList1):
	#	if r0.type != r1.type:
	#		raise ValueError("matching residues of different types")
	from util import getAtomList
	aList0 = getAtomList(rList0)
	aList1 = getAtomList(rList1)
	keep = int(len(rList0) * fraction)
	while len(aList0) > keep:
		if not sieve(aList0, aList1, maxrmsd):
			break
	return ([ a.residue for a in aList0 ], [ a.residue for a in aList1 ])

def sieve(aList0, aList1, maxrmsd):
	import numpy, math
	import chimera
	from chimera import match
	position0 = match._coordArray(aList0)	# fixed
	position1 = match._coordArray(aList1)	# movable
	m = match.Match(position0, position1, wantRMS=1)
	if m.rms < maxrmsd:
		return False
	matrix = m.matrix()
	maxdsq = 0
	Si = numpy.subtract(position0, m.center(position0))
	Sj = numpy.subtract(position1, m.center(position1))
	result = numpy.inner(Si, m.matrix())
	d = numpy.subtract(result, Sj)
	dsq = numpy.add.reduce(numpy.transpose(numpy.multiply(d, d)))
	worst = numpy.argmax(dsq)
	del aList0[worst]
	del aList1[worst]
	return True
