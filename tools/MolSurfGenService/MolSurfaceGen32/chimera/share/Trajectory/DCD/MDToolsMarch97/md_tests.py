
# $Log: not supported by cvs2svn $
# Revision 0.12  1996/10/10 21:42:10  jim
# Changes for new Numeric Python version.
#
# Revision 0.11  1996/08/28 20:52:33  jim
# Changes for new AtomGroup methods (rev. 0.67).
#
# Revision 0.10  1996/08/28 19:28:41  jim
# Switched frames from lists of tuples to arrays.
#
# Revision 0.9  1996/05/24 01:17:57  jim
# Added RCS tests and version reporting.
#
# Revision 0.8  1996/05/24 00:53:49  jim
# Changed Molecule.display() to view() and removed wait.
#
# Revision 0.7  1996/05/23 22:54:11  jim
# Added tests for structure information.
#
# Revision 0.6  1996/05/17 15:42:09  jim
# Added plot() test for Data.
#
# Revision 0.5  1996/05/17 15:38:56  jim
# Tests for first pre-release.
#

print "MDTools for Python Test Set "+"$Revision: 1.1 $"[11:-1]+"$State: Exp $"[8:-1]+"("+"$Date: 2004-05-17 18:43:19 $"[7:-11]+")"
print "$Id: md_tests.py 27463 2009-05-01 06:36:45Z gregc $"
print

import md
import sys
import os

print
print "RCS tests"
print 
print md.RCS
print
print "HomoCoord tests"
print
hcv = md.HomoCoord(0.1,0.2,0.3,0)
print hcv
hc = md.HomoCoord(0.1,0.2,0.3,0.2)
print hc
hcc = md.HomoCoord(0.1,0.2,0.3,1)
print hcc
print
print hcv + hcv
print hcv + hcc
print hcc + hcv
print hcv + hc
print hc + hcv
print hcc + hc
print hc + hcc
print hcc + hcc
print hc + hc
print
c = md.Coord(0.1,0.2,0.3)
print c
v = md.Vector(0.1,0.2,0.3)
print v
print
print v + c
print c + v
print v + v
print c + c
print
print c - c
print c - v
print v - c
print v - v
print v - c
print hc - c
print hc - c
print hc - hc
print
print -c
print -v
print -hc
print
print c + - c
print c + - v
print v + - c
print v + - v
print v + - c
print hc + - c
print hc + - c
print hc + - hc
print
print hc * 0.1
print 0.1 * hc
print hc / 10.
print hc / hc.W
print
print len(hc), hc[0], hc[1], hc[2], hc[3]
print
print "Vector tests"
print
print v
print abs(v)
print v * 0.1
print 0.1 * v
print v * v
print v % v
print v.unit()
print abs(v.unit())
print
print "Coord tests"
print
print c
c.set(md.Coord(4.,5.,6.))
print c
print md.dist(c,(1,2,3))
print md.dist(c,md.Coord(1,2,3))
print md.dist(md.Coord(1,2,3),c)
print md.dist((1,2,3),c)
print md.distsq((1,2,3),(4,5,6))
print
print "angle tests"
print
a = md.Coord(0,0,0)
b = md.Coord(1,0,0)
c = md.Coord(1,1,0)
d = md.Coord(1,1,1)
print md.angle(a,b,c)
print md.angle(a,b,c,'deg')
print md.angle(a,b,c,'rad')
print md.angle(a,b,c,'pi')
print md.angle(a,b,c,d)
print md.angle(a,b,c,d,'deg')
print md.angle(a,b,c,d,'rad')
print md.angle(a,b,c,d,'pi')
print
print "Atom tests"
print
a = md.Atom()
print a
print b
a.set(b)
print a
for f in dir(a):
	print f, getattr(a,f)
print
print "AtomGroup tests"
print
ag = md.AtomGroup()
print ag
for f in dir(ag):
	print f, getattr(ag,f)
alanin = md.Molecule('data/alanin.pdb','data/alanin.psf')
for a in alanin.atoms:
	ag.atoms.append(a)
print ag
print ag.masses()
print ag.tmass()
print ag.charges()
print ag.tcharge()
print ag.cgeom()
print ag.cmass()
print ag.rgyration()
ag.saveframe()
ag.saveframe('bob')
ag.loadframe()
ag.loadframe('bob')
ag.delframe('bob')
ag.delframe()
f = ag.coordinates()
ag.getframe(f)
ag.putframe(f)
print ag.asel(lambda a: 1)
print
print "Residue tests"
print
r = alanin.residues[3]
print r
for f in dir(r):
	print f, getattr(r,f)
r.buildrefs()
print r.atoms[2].residue is r
print r['CA']
print r.phipsi()
r.rotate(90)
print r.atoms
print r.phipsi()
print
print "ASel tests"
print
asel = md.ASel(alanin,lambda a: a.id > 62)
print asel
print asel.atoms[0].id
for f in dir(asel):
	print f, getattr(asel,f)
print
print "ResidueGroup tests"
print
rg = md.ResidueGroup()
print rg
for f in dir(rg):
	print f, getattr(rg,f)
for r in alanin.residues:
	rg.residues.append(r)
print rg
for f in dir(rg):
	print f, getattr(rg,f)
rg.buildlists()
print rg
for f in dir(rg):
	print f, getattr(rg,f)
print rg.phipsi()
print rg.rsel(lambda r: r.id > 6)
print
print "RSel tests"
print
rs = md.RSel(alanin,lambda r: r.id > 9)
print rs
print rs.residues[0].id
for f in dir(rs):
	print f, getattr(rs,f)
print
print "Segment tests"
print
s = alanin.segments[0]
print s
for f in dir(s):
	print f, getattr(s,f)
s.buildrefs()
r = s.residues[2]
print r.prev.id, r.id, r.next.id
print
print "SegmentGroup tests"
print
sg = md.SegmentGroup()
print sg
for f in dir(sg):
	print f, getattr(sg,f)
sg.segments.append(alanin.segments[0])
print sg
sg.buildlists()
print sg
for f in dir(sg):
	print f, getattr(sg,f)
print
print "Molecule tests"
print
alanin = md.Molecule('data/alanin.pdb')
print alanin
alanin = md.Molecule(psf='data/alanin.psf')
print alanin
alanin = md.Molecule('data/alanin.pdb','data/alanin.psf')
print alanin
alanin.buildstructure()
for f in dir(alanin.atoms[0]):
	print f, getattr(alanin.atoms[0],f)
print md.dist(alanin.bonds[0])
print md.angle(alanin.angles[0])
print md.angle(alanin.dihedrals[0])
print md.angle(alanin.impropers[0])
for f in dir(alanin):
	print f, getattr(alanin,f)
alanin.writepdb('tests/test_alanin.pdb')
alanin.view()
print
print "Trans tests"
print
print md.Trans(shift=md.Vector(1,0,0))
print md.Trans(shift=(1,0,0))
print md.Trans(shift=md.Coord(1,0,0))
print md.Trans(shift=(1,0,0,1))
print md.Trans(center=md.Coord(1,0,0))
print md.Trans(center=(1,0,0))
print md.Trans(shift=md.Coord(1,0,0),center=md.Coord(1,0,0),axis=md.Vector(1,0,0),angle=90)
t = md.Trans(shift=md.Coord(1,0,0),center=md.Coord(1,0,0),axis=md.Coord(2,0,0),angle=90)
c = md.Coord(1,0,0)
print c
print t
t(c)
print c
print
print "DCD tests"
print
print alanin
aldcd = md.DCD('data/alanin.dcd')
print aldcd
for f in dir(aldcd):
	print f, getattr(aldcd,f)
print len(aldcd)
print aldcd.asel()
print aldcd.aselfree(alanin)
print aldcd.aselfree()
aldcd.aselfree().getmolframe(aldcd[2])
print
print "DCDWrite tests"
print
try:
	os.unlink('tests/test_alanin.dcd')
except:
	pass
aldcdw = md.DCDWrite(dcdfile='tests/test_alanin.dcd',atoms=alanin)
print aldcdw
for i in range(0,100):
	# alanin.getframe(aldcd[i])
	# aldcdw.append()
	aldcdw.append(aldcd[i])
print aldcdw
del(aldcdw)
aldcdr = md.DCD('tests/test_alanin.dcd')
print aldcdr
print len(aldcdr)
print
print "Data tests"
print
d = md.Data(('x','y','z'),[(1,2,3),(4,5,6),(7,8,9)])
print d
try:
	d.append((1,2))
	print "misshaped data allowed"
except:
	print "error caught"
print d
d.append((10,11,12))
print d
print len(d)
print d[1:3]
print d[:2]
print d[2:]
print d[:]
d.addindex()
print d
print d[1]
d.addfield('x+y',('x','y'),lambda x,y: x+y)
print d
print d[:]
print d[('z')]
print d[('x','x+y')]
d2 = d.filter(('x'),lambda x: x < 5)
print d2
print d2[:]
print d.average('x') + d.average('y')
print d.average('x+y')
print d.average('x')
print d.average('x',lambda x: x*x)
print d.deviation('x')
d.list()
d.plot()
print
print "Tests Complete"
print

