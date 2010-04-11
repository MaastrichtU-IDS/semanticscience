import chimera
from chimera import Plane, Xform, cross, Vector, Point

m = chimera.openModels.list()[0]

import os.path
out = open(os.path.splitext(m.openedAs[0])[0] + ".py", "w")
print>>out, "from BuildStructure.Fragment import Fragment, RINGX"
fragName = os.path.splitext(os.path.split(m.openedAs[0])[1])[0]
print>>out, 'frag = Fragment("%s", [' % fragName
atoms = m.atoms
for a in atoms:
	print>>out, '\t("%s",' % a.element.name, \
				'(%g, %g, %g)),' % a.xformCoord().data()
print>>out, '\t], ['
ringInfo = {}
for ring in m.minimumRings():
	center = Point([a.xformCoord() for a in ring.atoms])
	numAtoms = len(ring.atoms)
	for b in ring.bonds:
		if b in ringInfo and ringInfo[b][0] >= numAtoms:
			continue
		ringInfo[b] = (numAtoms, center)
for b in m.bonds:

	print>>out, '\t((%d,%d),' % (atoms.index(b.atoms[0]), atoms.index(b.atoms[1])),
	if b.order > 1 and b in ringInfo:
		print>>out, '(%g, %g, %g)),' % ringInfo[b][1].data()
	else:
		print>>out, 'None),'
print>>out, "\t])\n"
print>>out, 'fragInfo = [RINGX, frag]'
out.close()
