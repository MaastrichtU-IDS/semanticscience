# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

def generateVRML(dmsFile, rgb=(1,1,1), sameAs=None):
	from CGLutil import vrml
	class PointSet(vrml._Node):
		def writeNode(self, f, prefix=''):
			f.write('%sShape {\n' % prefix)
			self.writeAppearance(f, prefix)
			f.write('%s%sgeometry PointSet {\n' % (prefix,
								vrml.Indent))
			p = prefix + vrml.Indent + vrml.Indent
			if hasattr(self, 'point'):
				self.point.writeNode(f, p)
			f.write('%s%s}\n' % (prefix, vrml.Indent))
			f.write('%s}\n' % prefix)

	class Coordinate(vrml._Node):
		def writeNode(self, f, prefix=''):
			f.write('%scoord Coordinate {\n' % prefix)
			p = prefix + vrml.Indent
			if hasattr(self, 'point'):
				f.write('%spoint [\n' % p)
				for i in range(0, len(self.point), 3):
					f.write('%s' % p + vrml.Indent)
					f.write('%g %g %g\n' % tuple(
							self.point[i:i+3]))
				f.write('%s]\n' % p)
			f.write('%s}\n' % prefix)
	from OpenSave import osOpen
	dms = osOpen(dmsFile)
	root = vrml.Transform()
	points = PointSet(emissiveColor=rgb)
	root.addChild(points)
	coords = []
	for line in dms.readlines():
		fields = line.replace('-', ' -').split()
		if len(fields) < 8:
			continue
		if fields[6] == "A":
			continue
		coords.extend(map(float, fields[3:6]))
	dms.close()
	if not coords:
		from chimera import UserError
		raise UserError, "No surface records found in '%s'" % dmsFile
	points.point = Coordinate(point=coords)

	import chimera, os
	chimera.openModels.open(vrml.vrml(root), type='VRML', sameAs=sameAs,
					identifyAs=os.path.basename(dmsFile))
