# -----------------------------------------------------------------------------
# Copy colors, display styles, coordinates, ... from one molecule to another.
#
def mcopy_command(cmdname, args):

    from Midas.midas_text import doExtensionFunc
    doExtensionFunc(molecule_copy, args,
                    specInfo = [('atomSpec','from_atoms','atoms'),
                                ('atomSpec','to_atoms','atoms')])

# -----------------------------------------------------------------------------
# Settings: c = color, s = style, v = visibilty, l = labels, x = coords,
#           p = placement, a = all
#
def molecule_copy(from_atoms, to_atoms, settings = 'csv'):

    ma, upa, mb, upb, mr, upr, mm = match_objects(from_atoms, to_atoms)

    ct = (('c', copy_colors),
          ('s', copy_style),
          ('v', copy_visibility),
          ('l', copy_labels),
          ('x', copy_coordinates),
          ('p', copy_placement),
          )

    settings = settings.lower()
    for c, cf in ct:
        if c in settings or 'a' in settings:
            cf(ma, mb, mr, mm)

    if upa > 0 or upb > 0 or upr > 0:
        from chimera.replyobj import status
        status('mcopy: %d unpaired atoms, %d unpaired bonds, %d unpaired residues' % (upa, upb, upr))

# -----------------------------------------------------------------------------
#
def match_objects(from_atoms, to_atoms):

    fms = set([a.molecule for a in from_atoms])
    if len(fms) != 1:
        from Midas import MidasError
        raise MidasError, 'Must specify one source molecule, got %d' % len(fms)
    fm = fms.pop()
    tms = set([a.molecule for a in to_atoms])
    mm = {fm : list(tms)}

    mr = {}
    upr = 0
    frt = {}
    for r in set([a.residue for a in from_atoms]):
        frt[(r.id.chainId, r.id.position, r.type)] = r
        mr[r] = []
    for r in set([a.residue for a in to_atoms]):
        k = (r.id.chainId, r.id.position, r.type)
        if k in frt:
            mr[frt[k]].append(r)
        else:
            upr += 1

    ma = {}
    upa = 0
    fat = {}
    for a in from_atoms:
        r = a.residue
        fat[(r.id.chainId, r.id.position, r.type, a.name, a.altLoc)] = a
        ma[a] = []
    for a in to_atoms:
        r = a.residue
        k = (r.id.chainId, r.id.position, r.type, a.name, a.altLoc)
        if k in fat:
            ma[fat[k]].append(a)
        else:
            upa += 1

    mb = {}
    upb = 0
    for a in ma.keys():
        for ao, b in a.bondsMap.items():
            if a < ao and ao in ma:
                tbl = []
                for ta in ma[a]:
                    tbl.extend([tb for tao, tb in ta.bondsMap.items()
                                if tao in ma[ao]])
                if tbl:
                    mb[b] = tbl
                upb += len(ma[a]) - len(tbl)

    return ma, upa, mb, upb, mr, upr, mm

# -----------------------------------------------------------------------------
#
def copy_colors(ma, mb, mr, mm):

    for a, tal in ma.items():
        for ta in tal:
            ta.color = a.color
            ta.vdwColor = a.vdwColor
            ta.labelColor = a.labelColor
            ta.surfaceColor = a.surfaceColor
            ta.surfaceOpacity = a.surfaceOpacity

    for b, tbl in mb.items():
        for tb in tbl:
            tb.color = b.color
            tb.labelColor = b.labelColor
            tb.halfbond = b.halfbond

    for r, trl in mr.items():
        for tr in trl:
            tr.ribbonColor = r.ribbonColor
            tr.labelColor = r.labelColor

    for m, tml in mm.items():
        for tm in tml:
            tm.color = m.color
            tm.surfaceColor = m.surfaceColor
            tm.surfaceOpacity = m.surfaceOpacity
            tm.ribbonInsideColor = m.ribbonInsideColor
            
# -----------------------------------------------------------------------------
#
def copy_style(ma, mb, mr, mm):

    for a, tal in ma.items():
        for ta in tal:
            ta.drawMode = a.drawMode
            ta.radius = a.radius
            ta.vdw = a.vdw

    for b, tbl in mb.items():
        for tb in tbl:
            tb.drawMode = b.drawMode
            tb.radius = b.radius

    for r, trl in mr.items():
        for tr in trl:
            tr.ribbonDrawMode = r.ribbonDrawMode
            tr.ribbonStyle = r.ribbonStyle
            tr.ribbonXSection = r.ribbonXSection
            tr.ribbonResidueClass = r.ribbonResidueClass
            tr.isHelix = r.isHelix
            tr.isSheet = r.isSheet
            tr.isTurn = r.isTurn
            tr.isHet = r.isHet
            tr.ringMode = r.ringMode

    for m, tml in mm.items():
        for tm in tml:
            tm.lineWidth = m.lineWidth
            tm.lineType = m.lineType
            tm.wireStipple = m.wireStipple
            tm.autochain = m.autochain
            tm.stickScale = m.stickScale
            tm.pointSize = m.pointSize
            tm.ballScale = m.ballScale
            tm.vdwDensity = m.vdwDensity

# -----------------------------------------------------------------------------
#
def copy_visibility(ma, mb, mr, mm):

    for a, tal in ma.items():
        for ta in tal:
            ta.display = a.display
            ta.surfaceDisplay = a.surfaceDisplay

    for b, tbl in mb.items():
        for tb in tbl:
            tb.display = b.display

    for r, trl in mr.items():
        for tr in trl:
            tr.ribbonDisplay = r.ribbonDisplay

    for m, tml in mm.items():
        for tm in tml:
            tm.display = m.display
            tm.ribbonHidesMainchain = m.ribbonHidesMainchain
            
# -----------------------------------------------------------------------------
#
def copy_labels(ma, mb, mr, mm):

    for a, tal in ma.items():
        for ta in tal:
            ta.label = a.label
            ta.labelOffset = a.labelOffset

    for b, tbl in mb.items():
        for tb in tbl:
            tb.label = b.label
            tb.labelOffset = b.labelOffset

    for r, trl in mr.items():
        for tr in trl:
            tr.label = r.label
            tr.labelOffset = r.labelOffset

# -----------------------------------------------------------------------------
#
def copy_coordinates(ma, mb, mr, mm):

    for a, tal in ma.items():
        for ta in tal:
            ta.setCoord(a.coord())

# -----------------------------------------------------------------------------
#
def copy_placement(ma, mb, mr, mm):

    for m, tml in mm.items():
        for tm in tml:
            tm.openState.xform = m.openState.xform
