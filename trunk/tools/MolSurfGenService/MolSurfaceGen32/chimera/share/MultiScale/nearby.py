# -----------------------------------------------------------------------------
# Select atoms and chains near the currently selected atoms and chains.
#
def select_nearby(distance, load_atoms, displayed_only):

    atom_sets_1, atom_sets_2 = selected_and_unselected_atom_sets(displayed_only)
    atoms1, chains1, atoms2, chains2 = \
            atomic_contacts(atom_sets_1, atom_sets_2, distance, load_atoms)

    satoms1, schains1 = all_atoms_and_chains(atom_sets_1, load_atoms)
    select_atoms_and_chains(satoms1 + atoms2, schains1 + chains2)
    
# -----------------------------------------------------------------------------
# Select contacts between selected and unselected atoms and chains
#
def select_contacts(distance, load_atoms, displayed_only):

    atom_sets_1, atom_sets_2 = selected_and_unselected_atom_sets(displayed_only)
    atoms1, chains1, atoms2, chains2 = \
            atomic_contacts(atom_sets_1, atom_sets_2, distance, load_atoms)

    select_atoms_and_chains(atoms1 + atoms2, chains1 + chains2)

# -----------------------------------------------------------------------------
#
def select_atoms_and_chains(atoms, cplist):

    # Don't select chains where atoms are selected.
    rlist = list(set([a.residue for a in atoms]))
    import MultiScale
    ac = set(MultiScale.containing_chain_pieces(cplist, rlist))
    splist = [cp.surface_piece for cp in cplist
              if not cp in ac and cp.surface_piece != None]
    
    from chimera import selection
    sel = selection.ItemizedSelection()
    sel.add(atoms + splist)
    sel.addImplied(vertices = False, edges = True)      # Select bonds
    selection.setCurrent(sel)

# -----------------------------------------------------------------------------
# Find atomic contacts between two sets of multiscale chains.
# Return contact atoms, optionally loading atoms if needed.
#
def atomic_contacts(asets1, asets2, distance, load_atoms):

    tp1 = map(lambda a: (a.xyz, a.transform), asets1)
    tp2 = map(lambda a: (a.xyz, a.transform), asets2)
        
    from _closepoints import find_close_points_sets, BOXES_METHOD
    i1, i2 = find_close_points_sets(BOXES_METHOD, tp1, tp2, distance)

    atoms1, chains1 = atoms_and_chains(asets1, i1, load_atoms)
    atoms2, chains2 = atoms_and_chains(asets2, i2, load_atoms)

    return atoms1, chains1, atoms2, chains2

# -----------------------------------------------------------------------------
#
class Atom_Set:

    def __init__(self, xyz, transform, atoms = None, chain = None):

        self.xyz = xyz
        self.transform = transform
        self.atoms = atoms
        self.chain = chain

# -----------------------------------------------------------------------------
# Deal with loaded and unloaded atoms, multiscale and non-multiscale models,
# and atom and multiscale chain selections.
#
def selected_and_unselected_atom_sets(displayed_only):

    # Get selected atoms.
    from chimera import selection
    atoms = selection.currentAtoms()

    # Group atoms by multiscale chain piece or non-multiscale molecule.
    ca_sel, ma_sel = group_atoms(atoms)

    # Get multiscale chains with selected surfaces.
    cp_sel = selected_multiscale_chains()

    # When chain atoms and surface are both selected ignore surface selection.
    cp_sel = filter(lambda cp: not cp in ca_sel, cp_sel)

    # Separate out unloaded selected chains.
    cpul_sel = filter(lambda cp: not cp.lan_chain.is_loaded(), cp_sel)

    # Merge loaded selected chains into table of atoms grouped by chain.
    cpl_sel = filter(lambda cp: cp.lan_chain.is_loaded(), cp_sel)
    for cp in cpl_sel:
        catoms = cp.lan_chain.atoms()
        ca_sel[cp] = catoms
        atoms.extend(catoms)

    # Get unselected atoms
    unsel_atoms = subtract_lists(all_atoms(), atoms)
    ca_unsel, ma_unsel = group_atoms(unsel_atoms)

    # Get unselected multiscale chains.
    cp_unsel = subtract_lists(all_multiscale_chains(), cp_sel)

    # Don't include chains with selected atoms.
    cp_unsel = filter(lambda cp: not cp in ca_sel, cp_unsel)
    
    # Separate out unloaded unselected chains.
    cpul_unsel = filter(lambda cp: not cp in ca_unsel, cp_unsel)

    # Eliminate undisplayed atoms and chains.
    if displayed_only:
        cpul_sel = filter(lambda cp: cp.surface_shown(), cpul_sel)
        cpul_unsel = filter(lambda cp: cp.surface_shown(), cpul_unsel)
        for table in (ca_sel, ca_unsel, ma_sel, ma_unsel):
            remove_undisplayed_table_atoms(table)

    # Make selected and unselected atom sets for non-multiscale models,
    # loaded multiscale chains, and unloaded multiscale chains.
    asets_sel = (map(molecule_atom_set, ma_sel.items()) +
                 map(chain_atom_subset, ca_sel.items()) +
                 chain_atom_sets(cpul_sel))
    asets_unsel = (map(molecule_atom_set, ma_unsel.items()) +
                   map(chain_atom_subset, ca_unsel.items()) +
                   chain_atom_sets(cpul_unsel))
    
    return asets_sel, asets_unsel

# -----------------------------------------------------------------------------
#
def group_atoms(atoms):
    
    ca = {}         # Atoms from multiscale chains
    ma = {}         # Atoms from non-multiscale molecules
    for a in atoms:
        r = a.residue
        if hasattr(r, 'model_piece') and r.model_piece:
            ca.setdefault(r.model_piece,[]).append(a)
        else:
            ma.setdefault(a.molecule,[]).append(a)

    return ca, ma

# -----------------------------------------------------------------------------
#
def all_atoms():

    from chimera import openModels, Molecule
    mlist = openModels.list(modelTypes = [Molecule])
    atoms = []
    for m in mlist:
        atoms.extend(m.atoms)
    return atoms

# -----------------------------------------------------------------------------
#
def selected_multiscale_chains():
    
    import MultiScale
    d = MultiScale.multiscale_model_dialog()
    if d == None:
        return []
    
    cp_sel = d.selected_chains(selected_surfaces_only = True,
                               warn_if_none_selected = False)
    return cp_sel

# -----------------------------------------------------------------------------
#
def all_multiscale_chains():
    
    import MultiScale
    d = MultiScale.multiscale_model_dialog()
    if d == None:
        return []

    cp_all = MultiScale.find_pieces(d.models, MultiScale.Chain_Piece)
    return cp_all

# -----------------------------------------------------------------------------
#
def remove_undisplayed_table_atoms(table):

    for g, atoms in table.items():
        satoms = filter(atom_shown, atoms)
        if satoms:
            table[g] = satoms
        else:
            del table[g]

# -----------------------------------------------------------------------------
# Check if atom, ribbon or multiscale surface is shown for an atom.
#
# TODO: Would like to check MSMS surface representation too.
#
def atom_shown(a):

    m = a.molecule
    r = a.residue
    if m.display and (a.display or r.ribbonDisplay):
        return True

    c = getattr(r, 'model_piece', None)
    if c:
        return c.surface_shown()
    
    return False

# -----------------------------------------------------------------------------
# Get chain coordinates and transforms.  Chains that differ only by a transform
# use the same NumPy array of coordinates.
#
def chain_atom_sets(cplist):

    asets = []

    for cp in cplist:
        lc = cp.lan_chain
        xyz = lc.source_atom_xyz()
        transform = chain_transform(cp)
        atoms = lc.atoms(load = False)
        aset = Atom_Set(xyz, transform, atoms, cp)
        asets.append(aset)

    return asets

# -----------------------------------------------------------------------------
# Make Atom_Set for subset of atoms from multiscale chain.
#
def chain_atom_subset(ca):

    cp, atoms = ca

    from _multiscale import get_atom_coordinates
    xyz = get_atom_coordinates(atoms)

#    transform = chain_transform(cp)
    from Matrix import xform_matrix
    transform = xform_matrix(cp.surface_model().openState.xform)

    aset = Atom_Set(xyz, transform, atoms, cp)
    return aset
    
# -----------------------------------------------------------------------------
# Make Atom_Set for subset of atoms not in a multiscale chain.
#
def molecule_atom_set(ma):

    m, atoms = ma

    from _multiscale import get_atom_coordinates
    xyz = get_atom_coordinates(atoms)

    from Matrix import xform_matrix
    transform = xform_matrix(m.openState.xform)

    aset = Atom_Set(xyz, transform, atoms)
    return aset

# -----------------------------------------------------------------------------
#
def atoms_and_chains(asets, ilists, load_atoms):
    
    atoms = []
    chains = []
    for k in range(len(asets)):
        aset = asets[k]
        ilist = ilists[k]
        if len(ilist) > 0:
            c = aset.chain
            if c:
                chains.append(c)
            if aset.atoms == None:
                if load_atoms and c:
                    atoms.extend(sublist(c.lan_chain.atoms(), ilist))
            else:
                atoms.extend(sublist(aset.atoms, ilist))

    return atoms, chains

# -----------------------------------------------------------------------------
#
def all_atoms_and_chains(asets, load_atoms):
    
    atoms = []
    chains = []
    for aset in asets:
        c = aset.chain
        if c:
            chains.append(c)
        if aset.atoms == None:
            if load_atoms and c:
                atoms.extend(c.lan_chain.atoms())
        else:
            atoms.extend(aset.atoms)

    return atoms, chains

# -----------------------------------------------------------------------------
#
def chain_transform(cp):

    sm = cp.surface_model()
    xf = sm.openState.xform
    xf.multiply(cp.xform)
    from Matrix import xform_matrix
    t = xform_matrix(xf)
    return t
    
# -----------------------------------------------------------------------------
#
def sublist(list, indices):

    slist = []
    for i in indices:
        slist.append(list[i])
    return slist
  
# -----------------------------------------------------------------------------
#
def subtract_lists(list1, list2):

  t2 = {}
  for e2 in list2:
    t2[e2] = 1
  diff = filter(lambda e1: not t2.has_key(e1), list1)
  return diff
