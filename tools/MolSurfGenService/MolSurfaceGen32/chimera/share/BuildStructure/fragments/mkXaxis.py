import chimera
from chimera import Plane, Xform, cross, Vector, Point

m = chimera.openModels.list()[0]
b = chimera.selection.currentBonds()[0]
bondVec = b.atoms[0].coord() - b.atoms[1].coord()
bondVec.normalize()
axis = Vector(1.0, 0.0, 0.0)
crossProd = cross(axis, bondVec)
if crossProd.sqlength() > 0:
	from math import acos, degrees
	xform = Xform.rotation(crossProd, degrees(acos(axis * bondVec)))
	xform.invert()
else:
	xform = Xform.identity()

m.openState.xform = xform

# okay, that puts the bond parallel to the X axis, now swing the plane of
# the rest of the molecule into the xy plane...
molPlane = Plane([a.xformCoord() for a in m.atoms[:3]])
angle = chimera.angle(molPlane.normal, Vector(0, 0, -1))
xform2 = Xform.rotation(b.atoms[0].xformCoord()-b.atoms[1].xformCoord(), angle)
xform2.multiply(xform)

m.openState.xform = xform2
