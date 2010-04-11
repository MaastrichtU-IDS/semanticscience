from chimera.selection.manager import selMgr

selName = "protein backbone"

selStr = """
selAdd = []
for mol in molecules:
	for res in mol.residues:
		atomsMap = res.atomsMap
		try:
			selAdd.extend(atomsMap['CA'] + atomsMap['N'] + atomsMap['C'])
		except KeyError:
			# non-peptide (CA, N, or C missing)
			pass
sel.add(selAdd)
sel.addImplied(vertices=0)
"""

selMgr.addSelector("selection example", [selName], selStr, makeCallbacks=1)
