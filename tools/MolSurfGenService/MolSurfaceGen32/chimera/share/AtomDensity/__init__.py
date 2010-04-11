# -----------------------------------------------------------------------------
#
def set_atom_volume_values(molecule, volume_data_region, attribute_name):

    atoms = molecule.atoms
    from _multiscale import get_atom_coordinates
    xyz = get_atom_coordinates(atoms)  # Untransformed coordinates
    xyz_xform = molecule.openState.xform

    dr = volume_data_region
    values, outside = dr.interpolated_values(xyz, xyz_xform,
                                             out_of_bounds_list = True)

    n = len(atoms)
    for a in range(n):
        v = float(values[a])    # Use float otherwise get a NumPy scalar.
        setattr(atoms[a], attribute_name, v)

    for a in outside:
        setattr(atoms[a], attribute_name, 0)
    
# -----------------------------------------------------------------------------
#
def show_attribute_histogram(molecule, attribute_name):

    import ShowAttr
    from chimera import dialogs
    d = dialogs.display(ShowAttr.ShowAttrDialog.name)
    d.configure(models = [molecule],
                mode = 'Render',
                attrsOf = ShowAttr.ATTRS_ATOMS,
                attrName = attribute_name)
    d.renderNotebook.selectpage('Colors')
    
# -----------------------------------------------------------------------------
# Normalize an attribute name.  This eliminates punctuation like "." from
# attribute names so they work correctly in Chimera commands and atom specs.
#
def replace_special_characters(attribute_name, repl_char):

    if attribute_name.isalnum():
        return attribute_name
    
    s = ''
    for c in attribute_name:
        if c.isalnum():
            s += c
        else:
            s += repl_char
    return s

# -----------------------------------------------------------------------------
# Find selected atoms outside map contour surface and select just those.
# Also report the number of those atoms.
#
def select_atoms_outside_map():

    from chimera.replyobj import status, info

    from VolumeViewer import active_volume
    dr = active_volume()
    if dr is None:
        status('No density map opened.')
        return

    if dr.surface_model() == None or not dr.surface_model().display:
        status('No surface shown for map.')
        return

    levels = dr.surface_levels
    if len(levels) == 0:
        status('No surface shown for map.')
        return

    contour_level = min(levels)
    from chimera import selection
    atoms = selection.currentAtoms()
    aolist = atoms_outside_map(atoms, dr, contour_level)

    msg = ('%d of %d selected atoms outside %s at level %.5g' %
           (len(aolist), len(atoms), dr.name, contour_level))
    status(msg)
    info(msg + '\n')

    selection.setCurrent(aolist)

# -----------------------------------------------------------------------------
#
def atoms_outside_map(atoms, dr, contour_level):
    
    from _multiscale import get_atom_coordinates
    xyz = get_atom_coordinates(atoms, transformed = True)
    from chimera import Xform
    values = dr.interpolated_values(xyz, Xform())

    from numpy import compress
    aolist = list(compress(values < contour_level, atoms))
    return aolist
