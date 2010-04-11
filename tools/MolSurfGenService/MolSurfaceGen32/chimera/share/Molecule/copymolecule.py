# -----------------------------------------------------------------------------
#
def copy_molecule(m):
    
  import chimera
  cm = chimera.Molecule()

  for attr in ('name', 'openedAs'):
    if hasattr(m, attr):
      setattr(cm, attr, getattr(m,attr))

  if hasattr(m, 'pdbHeaders'):
    cm.setAllPDBHeaders(m.pdbHeaders)
    
  rmap = {}
  for r in m.residues:
    cr = cm.newResidue(r.type, r.id)
    cr.isHelix = r.isHelix
    cr.isSheet = r.isSheet
    cr.isTurn = r.isTurn
    cr.isHet = r.isHet
    rmap[r] = cr

  amap = {}
  for a in m.atoms:
    ca = cm.newAtom(a.name, a.element)
    ca.setCoord(a.coord())
    ca.altLoc = a.altLoc
    if hasattr(a, 'bfactor'):
      ca.bfactor = a.bfactor
    amap[a] = ca
    cr = rmap[a.residue]
    cr.addAtom(ca)

  for b in m.bonds:
    a1, a2 = b.atoms
    cm.newBond(amap[a1], amap[a2])

  return cm
