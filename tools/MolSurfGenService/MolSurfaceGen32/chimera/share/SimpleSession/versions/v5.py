# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: v5.py 26655 2009-01-07 22:02:30Z gregc $

from v4 import init, beginRestore, endRestore, updateOSLmap, getOSL, \
	oslMap, registerAfterModelsCB, reportRestoreError, makeAfterModelsCBs, \
	findFile, oslLookup, restoreSurfaces, getColor, restoreMiscAttrs, \
	restoreWindowSize, restoreOpenStates, restoreLabels, \
	makeOslMappings, restoreVdw, restoreDrawModes, restoreDispChanged, \
	weedOSLlist, weedOSLdict, restoreSelections, restorePseudoBondGroups, \
	restoreOpenModelsAttrs, restoreCamera, RemapDialog
from v4 import restoreColors as v4restoreColors

def restoreColors(colors, materials, *args):
	# restore materials first, since colors use them
	from chimera import MaterialColor, Material, Color

	# since colors use materials, restore materials first
	for name, matInfo in materials.items():
		mat = Material.lookup(name)
		if mat is not None:
			mat.remove()
		mat = Material(name)
		specular, shininess = matInfo
		mat.specular = specular
		mat.shininess = shininess

	for name, colorInfo in colors.items():
		rgb, a, matName = colorInfo
		mat = Material.lookup(matName)
		c = Color.lookup(name)
		if c is not None:
			c.remove()
		c = MaterialColor(rgb[0], rgb[1], rgb[2], a, material=mat)
		c.save(name)

	v4restoreColors(*args)
