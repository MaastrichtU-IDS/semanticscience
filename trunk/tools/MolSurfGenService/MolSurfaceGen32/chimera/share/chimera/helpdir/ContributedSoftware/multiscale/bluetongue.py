# -----------------------------------------------------------------------------
# Open bluetongue virus (2btv) multi-scale model making structure hierarchy
# that has trimers, dimers, and outer and inner layers.
#
def make_2btv_multiscale_model():

    # Open 2btv by fetching it from the RCSB
    from chimera import openModels
    m = openModels.open('2btv', 'PDBID')[0]

    # Color atoms by element
    from chimera import actions
    map(actions.colorAtomByElement, m.atoms)

    # 2btv does not have biological oligomer (BIOMT) matrices.
    # So get 120 matrices for a crystal unit cell with 2 virus particles
    # and use only first 60 to get just one particle.
    import PDBmatrices
    slist = PDBmatrices.pdb_smtry_matrices(m.pdbHeaders)
    mlist = PDBmatrices.pdb_mtrix_matrices(m.pdbHeaders)
    matrices = PDBmatrices.matrix_products(slist, mlist)
    matrices = matrices[:60]

    # Make copies of molecule.
    from MultiScale import molecule_copies
    mcopies = molecule_copies(m, matrices)

    # Define groups and colors.
    from MultiScale import make_chain_groups, make_group
    p_trimers = make_chain_groups('P trimer', ('P','C','D'), mcopies,
                                  color = (.5, .6, .9, 1))   # RGBA, A=opacity
    q_trimers = make_chain_groups('Q trimer', ('Q','E','F'), mcopies,
                                  color = (.7, .7, .8, 1))
    r_trimers = make_chain_groups('R trimer', ('R','G','H'), mcopies,
                                  color = (.9, .8, .7, 1))
    s_trimers = make_chain_groups('S trimer', ('S','I','J'), mcopies,
                                  color = (.7, .5, .6, 1))
    # T trimers are made up of a monomer from each of 3 transformed molecules.
    t_triples = ((1,20,23),(2,22,27),(3,26,60),(4,44,59),(5,16,43),
                 (6,18,40),(7,17,42),(8,41,55),(9,49,54),(10,36,48),
                 (11,25,38),(12,37,47),(13,35,46),(14,29,34),(15,21,28),
                 (19,24,39),(30,33,56),(31,50,53),(32,52,57),(45,51,58))
    t_mcopies = map(lambda (i,j,k): (mcopies[i-1],mcopies[j-1],mcopies[k-1]),
                    t_triples)
    t_trimers = make_chain_groups('T trimer', ('T',), t_mcopies,
                                  color = (.5, .9, .6, 1))
    all_trimers = p_trimers + q_trimers + r_trimers + s_trimers + t_trimers
    outer_layer = make_group('Outer layer', all_trimers)
    dimers = make_chain_groups('VP3 dimer', ('A','B'), mcopies,
                               chain_colors = ((.7, .5, .9, 1),
                                               (.5, .8, .8, 1)))
    inner_layer = make_group('Inner layer', dimers)
    capsid = make_group('Bluetongue capsid', (outer_layer, inner_layer))

    import MultiScale
    d = MultiScale.show_multiscale_model_dialog()
    d.add_models([capsid])

# -----------------------------------------------------------------------------
#
make_2btv_multiscale_model()

# Adjust clip planes and center model
import chimera
chimera.viewer.viewAll()
