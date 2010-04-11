# -----------------------------------------------------------------------------
# Command to make copies of a molecule positioned using volume data symmetries
# or BIOMT PDB header matrices, with positions updated whenever the original
# PDB model is moved relative to a reference volume model.
#

# -----------------------------------------------------------------------------
#
def symmetry_copies_command(cmdname, args):

    from Commands import parse_arguments
    from Commands import molecule_arg, model_arg, string_arg, float_arg, bool_arg
    req_args = ()
    opt_args = (('molecule', molecule_arg),
                ('coordinateSystem', model_arg),)
    kw_args = (('group', string_arg),
               ('center', string_arg),
               ('axis', string_arg),
               ('contact', float_arg),
               ('range', float_arg),
               ('update', bool_arg),
               )
    kw = parse_arguments(cmdname, args, req_args, opt_args, kw_args)
    symmetry_copies(**kw)
                    
# -----------------------------------------------------------------------------
#
def symmetry_copies(molecule = None, group = 'biomt',
                    center = (0,0,0), axis = (0,0,1), coordinateSystem = None,
                    contact = None, range = None, update = False):

    from Commands import CommandError

    if molecule is None:
        molecule = default_molecule()
        if molecule is None:
            raise CommandError, 'No molecule opened'

    csys = coordinateSystem
    if csys is None:
        csys = molecule

    from Commands import parse_center_axis
    center_point, axis_vector, csys_os = \
                  parse_center_axis(center, axis, csys.openState, 'sym')
    c = center_point.data()
    a = axis_vector.data()
    tflist = group_symmetries(group, c, a, molecule)
    copies = create_symmetry_copies(molecule, csys, tflist, contact, range)
    if len(copies) == 0:
        raise CommandError, 'No symmetric molecules in range'

    if update and molecule.openState != csys.openState:
        add_symmetry_update_handler(molecule)

# -----------------------------------------------------------------------------
#
def group_symmetries(group, center, axis, mol):

    from Commands import CommandError

    g0 = group[:1].lower()
    if g0 in ('c', 'd'):
        # Cyclic or dihedral symmetry: C<n>, D<n>
        try:
            n = int(group[1:])
        except ValueError:
            raise CommandError, 'Invalid symmetry group syntax "%s"' % group
        if n < 2:
            raise CommandError, 'Cn or Dn with n = %d < 2' % (n,)
        if g0 == 'c':
            tflist = cyclic_symmetries(n)
        else:
            tflist = dihedral_symmetries(n)
    elif g0 == 'i':
        # Icosahedral symmetry: i[,<orientation>]
        import Icosahedron as icos
        gfields = group.split(',')
        if len(gfields) == 1:
            orientation = '222'
        elif len(gfields) == 2:
            orientation = gfields[1]
            if not orientation in icos.coordinate_system_names:
                raise CommandError, ('Unknown icosahedron orientation "%s"'
                                     % orientation)
        else:
            raise CommandError, 'Invalid symmetry group syntax "%s"' % group
        tflist = icos.icosahedral_symmetry_matrices(orientation)
    elif g0 == 'h':
        # Helical symmetry: h,<repeat>,<rise>[,<angle>[,<n>,<offet>]]
        gfields = group.split(',')
        nf = len(gfields)
        if nf < 3 or nf > 6:
            raise CommandError, 'Invalid symmetry group syntax "%s"' % group
        try:
            param = [float(f) for f in gfields[1:]]
        except ValueError:
            raise CommandError, 'Invalid symmetry group syntax "%s"' % group
        if len(param) == 2:
            param.append(360.0)
        if len(param) == 3:
            param.append(int(param[0]))
        if len(param) == 4:
            param.append(0)
        repeat, rise, angle, n, offset = param
        tflist = helical_symmetry(repeat, rise, angle, n, offset)
    elif g0 == 't':
        # Translation symmetry: t,<n>,<distance> or t,<n>,<dx>,<dy>,<dz>
        gfields = group.split(',')
        nf = len(gfields)
        if nf != 3 and nf != 5:
            raise CommandError, 'Invalid symmetry group syntax "%s"' % group
        try:
            param = [float(f) for f in gfields[1:]]
        except ValueError:
            raise CommandError, 'Invalid symmetry group syntax "%s"' % group
        n = param[0]
        if n != int(n):
            raise CommandError, 'Invalid symmetry group syntax "%s"' % group
        if nf == 3:
          delta = (0,0,param[1])
        else:
          delta = param[1:]
        tflist = translation_symmetry(n, delta)
    elif group.lower() == 'biomt':
        # BIOMT biological unit matrices from PDB file header.
        if not hasattr(mol, 'pdbHeaders'):
            msg = 'Molecule %s has no BIOMT matrices or PDB headers' % mol.name
            raise CommandError, msg
        from PDBmatrices import pdb_biomt_matrices
        tflist = pdb_biomt_matrices(mol.pdbHeaders)
        if len(tflist) == 0:
            msg = 'Molecule %s has no BIOMT matrices in PDB header' % mol.name
            raise CommandError, msg
        from Matrix import is_identity_matrix
        if len(tflist) == 1 and is_identity_matrix(tflist[0]):
            msg = 'Molecule %s has only identity BIOMT matrix in PDB header' % mol.name
            raise CommandError, msg
    else:
        raise CommandError, 'Unknown symmetry group "%s"' % group

    # Apply center and axis transformation.
    if tuple(center) != (0,0,0) or tuple(axis) != (0,0,1):
        import Matrix as m
        tf = m.multiply_matrices(m.vector_rotation_transform(axis, (0,0,1)),
                                 m.translation_matrix([-c for c in center]))
        tfinv = m.invert_matrix(tf)
        tflist = [m.multiply_matrices(tfinv, t, tf) for t in tflist]

    return tflist

# -----------------------------------------------------------------------------
# Rotation about z axis.
#
def cyclic_symmetries(n):

    tflist = []
    from math import sin, cos, pi
    for k in range(n):
        a = 2*pi * float(k) / n
        c = cos(a)
        s = sin(a)
        tf = ((c, -s, 0, 0),
              (s, c, 0, 0),
              (0,0,1,0))
        tflist.append(tf)
    return tflist

# -----------------------------------------------------------------------------
# Rotation about z axis, reflection about x axis.
#
def dihedral_symmetries(n):

    clist = cyclic_symmetries(n)
    reflect = ((-1,0,0,0),(0,1,0,0),(0,0,-1,0))
    from Matrix import matrix_products, identity_matrix
    tflist = matrix_products([identity_matrix(), reflect], clist)
    return tflist

# -----------------------------------------------------------------------------
# Helix centered on z axis.  Rise and angle over repeat subunits.
# Angle in degrees.  Number of transformations to return is n.
#
def helical_symmetry(repeat, rise, angle, n, offset):

    tflist = []
    from math import sin, cos, pi
    for k in range(n):
        i = offset + k
        a = i * (float(angle)/repeat) * pi / 180
        c = cos(a)
        s = sin(a)
        tf = ((c, -s, 0, 0),
              (s, c, 0, 0),
              (0,0,1,i*float(rise)/repeat))
        tflist.append(tf)
    return tflist

# -----------------------------------------------------------------------------
#
def translation_symmetry(n, delta):

    tflist = []
    dx, dy, dz = delta
    for k in range(n):
        tf = ((1, 0, 0, k*dx),
              (0, 1, 0, k*dy),
              (0, 0, 1, k*dz))
        tflist.append(tf)
    return tflist

# -----------------------------------------------------------------------------
#
def undo_symmetry_copies_command(cmdname, args):

    from Commands import molecules_arg, parse_arguments
    req_args = ()
    opt_args = (('molecules', molecules_arg),)
    kw = parse_arguments(cmdname, args, req_args, opt_args)
    undo_symmetry_copies(**kw)
    
# -----------------------------------------------------------------------------
#
def undo_symmetry_copies(molecules = None):

    mlist = molecules
    if mlist is None:
        from chimera import openModels as om, Molecule
        mlist = om.list(modelTypes = [Molecule])

    mlist = [m for m in mlist if hasattr(m, 'symmetry_copies')]

    for mol in mlist:
        remove_symmetry_copies(mol)
    
# -----------------------------------------------------------------------------
#
def remove_symmetry_copies(mol):
        
    if not hasattr(mol, 'symmetry_copies'):
        from Midas import MidasError
        raise MidasError, 'Model %s does not have symmetry copies' % mol.name

    remove_symmetry_update_handler(mol)

    import chimera
    chimera.openModels.close(mol.symmetry_copies)
    del mol.symmetry_copies
    del mol.symmetry_reference_model

# -----------------------------------------------------------------------------
#
def add_symmetry_update_handler(mol):

    import chimera
    h = chimera.triggers.addHandler('OpenState', motion_cb, mol)
    mol.symmetry_handler = h

# -----------------------------------------------------------------------------
#
def remove_symmetry_update_handler(mol):

    if hasattr(mol, 'symmetry_handler'):
        import chimera
        chimera.triggers.deleteHandler('OpenState', mol.symmetry_handler)
        del mol.symmetry_handler
    
# -----------------------------------------------------------------------------
#
def motion_cb(trigger_name, mol, trigger_data):

    if not 'transformation change' in trigger_data.reasons:
        return

    if is_model_deleted(mol) or is_model_deleted(mol.symmetry_reference_model):
        remove_symmetry_update_handler(mol)
        return

    mos = mol.openState
    ros = mol.symmetry_reference_model.openState
    if (mos.active and ros.active) or (not mos.active and not ros.active):
        # Both model and reference model are movable or both are frozen.
        return

    modified = trigger_data.modified
    if not (mos in modified or ros in modified):
        return

    update_symmetry_positions(mol)

# -----------------------------------------------------------------------------
#
def create_symmetry_copies(mol, csys, tflist, cdist, rdist,
                           exclude_identity = True):

    if exclude_identity:
        from Matrix import is_identity_matrix
        tflist = [tf for tf in tflist if not is_identity_matrix(tf)]

    close_contacts = not cdist is None
    close_centers = not rdist is None
    if not close_contacts and not close_centers:
        transforms = tflist     # Use all transforms
    elif close_contacts and not close_centers:
        transforms = contacting_transforms(mol, csys, tflist, cdist)
    elif close_centers and not close_contacts:
        transforms = close_center_transforms(mol, csys, tflist, rdist)
    else:
        transforms = unique(contacting_transforms(mol, csys, tflist, cdist) +
                            close_center_transforms(mol, csys, tflist, rdist))

    if hasattr(mol, 'symmetry_copies'):
        remove_symmetry_copies(mol)

    copies = []
    from chimera import openModels, replyobj
    from PDBmatrices import copy_molecule
    from Matrix import chimera_xform
    for tf in transforms:
        copy = copy_molecule(mol)
        copy.symmetry_xform = chimera_xform(tf)
        copies.append(copy)
        replyobj.status('Created symmetry copy %d of %d'
                        % (len(copies), len(transforms)))

    if len(copies) == 0:
        return copies

    openModels.add(copies)
    replyobj.status('')

    mol.symmetry_copies = copies
    mol.symmetry_reference_model = csys

    # TODO: Set xform before opening so that code that detects open sees
    # the correct position.  Currently not possible.  Bug 4486.
    update_symmetry_positions(mol)

    return copies

# -----------------------------------------------------------------------------
#
def contacting_transforms(mol, csys, tflist, cdist):

    from _multiscale import get_atom_coordinates
    points = get_atom_coordinates(mol.atoms)
    pxf = mol.openState.xform
    pxf.premultiply(csys.openState.xform.inverse())
    from Matrix import xform_matrix, identity_matrix
    from numpy import array, float32
    point_tf = xform_matrix(pxf)
    from _contour import affine_transform_vertices
    affine_transform_vertices(points, point_tf) # points in reference coords
    ident = array(identity_matrix(),float32)
    from _closepoints import find_close_points_sets, BOXES_METHOD
    ctflist = [tf for tf in tflist if
               len(find_close_points_sets(BOXES_METHOD,
                                          [(points, ident)],
                                          [(points, array(tf,float32))],
                                          cdist)[0][0]) > 0]
    return ctflist

# -----------------------------------------------------------------------------
#
def close_center_transforms(mol, csys, tflist, rdist):

    have_box, box = mol.bbox()
    if not have_box:
        return []
    c = mol.openState.xform.apply(box.center()) # center
    cref = csys.openState.xform.inverse().apply(c).data() # reference coords
    from Matrix import distance, apply_matrix
    rtflist = [tf for tf in tflist
               if distance(cref, apply_matrix(tf, cref)) < rdist]
    return rtflist

# -----------------------------------------------------------------------------
#
def update_symmetry_positions(mol):

    mol_xf = mol.openState.xform
    ref_xf = mol.symmetry_reference_model.openState.xform
    mol.symmetry_copies = filter(lambda m: not is_model_deleted(m),
                                 mol.symmetry_copies)
    for m in mol.symmetry_copies:
        m.openState.xform = symmetry_xform(mol_xf, m.symmetry_xform, ref_xf)

# -----------------------------------------------------------------------------
#
def symmetry_xform(mol_xform, sym_xform, ref_xform):

    from chimera import Xform
    xf = Xform(mol_xform)
    xf.premultiply(ref_xform.inverse())
    xf.premultiply(sym_xform)
    xf.premultiply(ref_xform)
    return xf

# -----------------------------------------------------------------------------
#
def default_molecule():
        
    from chimera import openModels, Molecule
    mlist = openModels.list(modelTypes = [Molecule])
    mlist = [m for m in mlist if not hasattr(m, 'symmetry_xform')]
    if len(mlist) == 0:
        from Midas import MidasError
        raise MidasError, 'No molecules are opened'
    elif len(mlist) > 1:
        from Midas import MidasError
        raise MidasError, 'Multiple molecules opened, must specify one'
    mol = mlist[0]
    return mol
    
# -----------------------------------------------------------------------------
# Eliminate identical objects from list.
#
def unique(s):

    u = []
    found = {}
    for e in s:
        if not id(e) in found:
            found[id(e)] = True
            u.append(e)
    return u
    
# -----------------------------------------------------------------------------
#
def is_model_deleted(m):

    return m.__destroyed__
    
# -----------------------------------------------------------------------------
#
def set_volume_icosahedral_symmetry():

    from VolumeViewer import active_volume
    v = active_volume()
    if v is None:
        from chimera.replyobj import status
        status('Set icosahedral symmetry: No active volume data.')
        return

    from Icosahedron.gui import icosahedron_dialog
    d = icosahedron_dialog()
    if d is None:
        orientation = '222'
    else:
        orientation = d.orientation_name()

    from Icosahedron import icosahedral_symmetry_matrices
    v.data.symmetries = icosahedral_symmetry_matrices(orientation)

    from chimera.replyobj import status
    status('Set icosahedral symmetry %s of volume %s.' % (orientation, v.name))
