# -----------------------------------------------------------------------------
# Align two molecules using selected atoms.  Two selected atoms are paired if
# one is from each molecule, they have the same chain identifier, residue
# number, residue name, and atom name, and the atom name is CA or P (ie.
# backbone only).  Selected atoms which are not paired are not used in the
# alignment.  The model with the higher model id number is moved to align
# it with the one with the lower id number.  The RMSD and the rotation
# angle are printed to the reply log and status line.
#
def align_backbones_using_selected_atoms():

    # Find atom pairs
    from chimera import selection
    a1, a2 = backbone_atom_pairs(selection.currentAtoms())
    if a1 == None:
        return

    # Compute alignment
    from chimera import match
    xform, rmsd = match.matchAtoms(a1, a2)

    # Apply transformation
    m1 = a1[0].molecule
    m2 = a2[0].molecule
    xf = m1.openState.xform
    xf.multiply(xform)
    xf2 = m2.openState.xform
    m2.openState.xform = xf

    # Report atom count, rmsd, and angle
    xf2.invert()
    xf.multiply(xf2)
    axis, angle = xf.getRotation()
    from chimera import replyobj
    replyobj.status('RMSD between %d atom pairs is %.3f angstroms, rotation angle = %.2f degrees\n'
                    % (len(a1), rmsd, angle), log = True)


# -----------------------------------------------------------------------------
#
def backbone_atom_pairs(atoms):
    
    nmol = len(atom_molecules(atoms))
    if nmol != 2:
        from chimera import replyobj
        replyobj.status('alignment: Must select atoms from 2 molecules (%d selected).\n' % nmol, log = True)
        return None, None

    bb_atoms = filter(lambda a: a.name == 'CA' or a.name == 'P', atoms)
        
    atom_pairs = paired_alignment_atoms(bb_atoms)
    if len(atom_pairs) < 3:
        from chimera import replyobj
        replyobj.status('alignment: Too few backbone atom pairs (%d).\n' %
                        len(atom_pairs), log = True)
        return None, None

    a1 = map(lambda p: p[0], atom_pairs)
    a2 = map(lambda p: p[1], atom_pairs)

    m1 = a1[0].molecule
    m2 = a2[0].molecule
    if (m1.id, m1.subid) > (m2.id, m2.subid):
        return a2, a1

    return a1, a2

# -----------------------------------------------------------------------------
#
def atom_molecules(atoms):

    mtable = {}
    for a in atoms:
        mtable[a.molecule] = 1
    mlist = mtable.keys()
    mlist.sort(lambda m1,m2: cmp((m1.id, m1.subid), (m2.id, m2.subid)))
    return mlist

# -----------------------------------------------------------------------------
#
def paired_alignment_atoms(atoms):

    # Sort atoms by molecule
    mtable = {}
    for a in atoms:
        m = a.molecule
        if m in mtable:
            mtable[m].append(a)
        else:
            mtable[m] = [a]

    if len(mtable) != 2:
        return []

    a1, a2 = mtable.values()

    # Build table for matching chain, residue number and type, and atom name
    a2table = {}
    for a in a2:
        r = a.residue
        rid = r.id
        a2table[(rid.position, rid.chainId, r.type, a.name)] = a

    # Find pairs of atoms
    atom_pairs = []
    for a in a1:
        r = a.residue
        rid = r.id
        key = (rid.position, rid.chainId, r.type, a.name)
        if key in a2table:
            atom_pairs.append((a, a2table[key]))

    return atom_pairs

# -----------------------------------------------------------------------------
#
def illustrate_backbone_alignment():

    # Find atom pairs
    from chimera import selection
    a1, a2 = backbone_atom_pairs(selection.currentAtoms())
    if a1 == None:
        return

    # Compute alignment
    from chimera import match
    xform, rmsd = match.matchAtoms(a1, a2)

    # Find aligning transformation to apply to molecule 2 object coordinates
    m1 = a1[0].molecule
    m2 = a2[0].molecule
    xf = m1.openState.xform
    xf.multiply(xform)                  # New m2 transform to align.
    inv_xf2 = m2.openState.xform
    inv_xf2.invert()
    xf.premultiply(inv_xf2)             # xform in m2 object coordinates

    # Make schematic illustrating rotation
#    alpha = .5
    from_rgba = list(m2.color.rgba())
#    from_rgba[3] = alpha
    to_rgba = list(m1.color.rgba())
#    to_rgba[3] = alpha
    sm = transform_schematic(xf, center_of_atoms(a2), from_rgba, to_rgba)
    if sm:
        sm.name = 'Transform from %s to %s' % (m2.name, m1.name)
        from chimera import openModels
        openModels.add([sm], sameAs = m2)

    # Report atom count, rmsd, and angle
    axis, angle = xf.getRotation()
    from chimera import replyobj
    replyobj.status('RMSD between %d atom pairs is %.3f angstroms, rotation angle = %.2f degrees\n'
                    % (len(a1), rmsd, angle), log = True)

# -----------------------------------------------------------------------------
# In object coordinates.  Assume they are all from same model.
#
def center_of_atoms(atoms):

    from _multiscale import get_atom_coordinates
    xyz = get_atom_coordinates(atoms)
    from numpy import sum
    center = tuple(sum(xyz, axis=0) / len(xyz))
    return center
    
# -----------------------------------------------------------------------------
# Create a surface model showing two squares, the second being the transformed
# version of the first.  The first should pass through the center point.
# The two squares should have a common edge (rotation axis).
#
def transform_schematic(xform, center, from_rgba, to_rgba):

    corners = transform_square(xform, center)
    if corners is None:
        return None             # No rotation.

    import _surface
    sm = _surface.SurfaceModel()

    varray = corners
    tarray = ((0,1,2),(0,2,3),(0,1,5),(0,5,4),(1,2,6),(1,6,5),
              (2,3,7),(2,7,6),(3,0,4),(3,4,7),(4,5,6),(4,6,7))
    g1 = sm.addPiece(varray, tarray, from_rgba)

    from Matrix import xform_matrix, apply_matrix
    tf = xform_matrix(xform)
    corners2 = [apply_matrix(tf, p) for p in corners]
    varray2 = corners2
    g2 = sm.addPiece(varray2, tarray, to_rgba)

    return sm

# -----------------------------------------------------------------------------
#
def transform_square(xform, center):

    axis, angle_deg = xform.getRotation()
    trans = xform.getTranslation()
    t1 = trans - axis*(trans*axis)
    import chimera
    t2 = chimera.cross(axis, t1)

    from math import pi, sin, cos
    angle = angle_deg * pi / 180
    sa, ca = sin(angle), cos(angle)
    if 1-ca == 0:
        return None     # No rotation
    axis_offset = t1*.5 + t2*(.5*sa/(1-ca))
    c = chimera.Vector(center[0], center[1], center[2])
    cd = c - axis_offset
    sq1 = cd - axis*(cd*axis)
    sq2 = axis*sq1.length
    e = 2       # Factor for enlarging square
    dz = chimera.cross(axis, sq1) * .05 # Thickness vector
    corners = [p.data() for p in (c - sq1 - sq2*e - dz, c - sq1 + sq2*e - dz,
                                c + sq1*e + sq2*e - dz, c + sq1*e - sq2*e - dz,
                                c - sq1 - sq2*e + dz, c - sq1 + sq2*e + dz,
                                c + sq1*e + sq2*e + dz, c + sq1*e - sq2*e + dz,
                                )]
    return corners
