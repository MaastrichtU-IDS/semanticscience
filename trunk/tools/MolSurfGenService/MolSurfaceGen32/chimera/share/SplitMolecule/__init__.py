# -----------------------------------------------------------------------------
# Command to split molecules so that each chain is in a separate molecule.
#

# -----------------------------------------------------------------------------
#
def split_molecules(cmdname, args):

    fields = args.split()

    from chimera import openModels, Molecule
    if len(fields) >= 1:
        from chimera import specifier
        sel = specifier.evalSpec(fields[0])
        mlist = sel.molecules()
    else:
        mlist = openModels.list(modelTypes = [Molecule])

    if len(mlist) == 0:
        from Midas.midas_text import error
        error('%s: No molecules to split.' % cmdname)
        return

    slist = []
    for m in mlist:
        clist = split_molecule(m)
        if clist:
            openModels.add(clist, baseId = m.id, noprefs=True)
            for c in clist:
                c.openState.xform = m.openState.xform
            slist.append(m)
            from chimera import makeLongBondsDashed, makePseudoBondsToMetals
            makePseudoBondsToMetals(clist)
            makeLongBondsDashed(clist)

    openModels.close(slist)
    
# -----------------------------------------------------------------------------
#
def split_molecule(m):

    chains = molecule_chains(m)
    if len(chains) == 1:
        return []

    clist = chains.keys()
    clist.sort()
    
    mlist = []
    for cid in clist:
        alist = chains[cid]
        ma = molecule_from_atoms(m, alist)
        ma.name = m.name + '_' + cid
        mlist.append(ma)

    return mlist
    
# -----------------------------------------------------------------------------
#
def molecule_chains(m):

    ct = {}
    for a in m.atoms:
        cid = a.residue.id.chainId
        if cid in ct:
            ct[cid].append(a)
        else:
            ct[cid] = [a]
    return ct

# -----------------------------------------------------------------------------
#
def molecule_from_atoms(m, atoms):

    import chimera
    cm = chimera.Molecule()
    cm.color = m.color
    cm.display = m.display

    for attr in ('name', 'openedAs'):
        if hasattr(m, attr):
            setattr(cm, attr, getattr(m,attr))

    if hasattr(m, 'pdbHeaders'):
        cm.setAllPDBHeaders(m.pdbHeaders)

    rmap = {}
    rlist = atom_residues(atoms)
    rlist.sort(lambda r1, r2: cmp(r1.id.position, r2.id.position))
    for r in rlist:
        crid = chimera.MolResId(r.id.chainId, r.id.position)
        cr = cm.newResidue(r.type, crid)
        cr.isHet = r.isHet
        cr.isHelix = r.isHelix
        cr.isSheet = r.isSheet
        cr.isTurn = r.isTurn
        cr.ribbonColor = r.ribbonColor
        cr.ribbonStyle = r.ribbonStyle
        cr.ribbonDrawMode = r.ribbonDrawMode
        cr.ribbonDisplay = r.ribbonDisplay
        rmap[r] = cr

    amap = {}
    for a in atoms:
        ca = cm.newAtom(a.name, a.element)
        ca.setCoord(a.coord())
        ca.altLoc = a.altLoc
        ca.color = a.color
        ca.drawMode = a.drawMode
        ca.display = a.display
        if hasattr(a, 'bfactor'):
            ca.bfactor = a.bfactor
        amap[a] = ca
        cr = rmap[a.residue]
        cr.addAtom(ca)

    for b in atom_bonds(atoms):
        a1, a2 = b.atoms
        cb = cm.newBond(amap[a1], amap[a2])
        cb.color = b.color
        cb.drawMode = b.drawMode
        cb.display = b.display

    for am in m.associatedModels():
        if not isinstance(am, chimera.PseudoBondGroup):
            continue
        if not am.category.startswith("coordination complexes"):
            continue
        for pb in am.pseudoBonds:
            a1, a2 = pb.atoms
            if a1 not in amap or a2 not in amap:
                continue
            cm.newBond(amap[a1], amap[a2])

    return cm

# -----------------------------------------------------------------------------
#
def atom_residues(atoms):

    rt = {}
    for a in atoms:
        rt[a.residue] = 1
    rlist = rt.keys()
    return rlist

# -----------------------------------------------------------------------------
# Bonds with both ends in given atom set.
#
def atom_bonds(atoms):

    at = {}
    for a in atoms:
        at[a] = 1
    bt = {}
    for a in atoms:
        for b in a.bonds:
            if not b in bt:
                a1, a2 = b.atoms
                if a1 in at and a2 in at:
                    bt[b] = 1
    blist = bt.keys()
    return blist
