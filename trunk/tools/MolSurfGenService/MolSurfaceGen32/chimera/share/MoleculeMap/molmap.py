# -----------------------------------------------------------------------------
# Simulate an electron density map for an atomic model at a specfied
# resolution.  The simulated map is useful for fitting the model into
# an experimental map using correlation coefficient as a goodness of fit.
#
def molmap_command(cmdname, args):

    from Commands import doExtensionFunc
    doExtensionFunc(molecule_map, args,
                    specInfo = [('atomSpec','atoms','atoms')])

# -----------------------------------------------------------------------------
#
from math import sqrt, pi
def molecule_map(atoms, resolution,
                 gridSpacing = None,    # default is 1/3 resolution
                 edgePadding = None,    # default is 3 times resolution
                 cutoffRange = 5,       # in standard deviations
                 sigmaFactor = 1/(pi*sqrt(2)), # resolution / standard deviation
                 displayThreshold = 0.95, # fraction of total density
                 modelId = None, # integer
                 replace = True,
		 showDialog = True
                 ):

    from Commands import CommandError
    if len(atoms) == 0:
        raise CommandError, 'No atoms specified'

    for vname in ('resolution', 'gridSpacing', 'edgePadding',
                  'cutoffRange', 'sigmaFactor'):
        value = locals()[vname]
        if not isinstance(value, (float,int,type(None))):
            raise CommandError, '%s must be number, got "%s"' % (vname,str(value))

    if edgePadding is None:
        pad = 3*resolution
    else:
        pad = edgePadding

    if gridSpacing is None:
        step = (1./3) * resolution
    else:
        step = gridSpacing

    if not modelId is None:
        from Commands import parse_model_id
        modelId = parse_model_id(modelId)

    v = make_molecule_map(atoms, resolution, step, pad,
                          cutoffRange, sigmaFactor,
                          displayThreshold, modelId, replace, showDialog)
    return v

# -----------------------------------------------------------------------------
#
def make_molecule_map(atoms, resolution, step, pad, cutoff_range,
                      sigma_factor, display_threshold, model_id, replace,
		      show_dialog):

    atoms = tuple(atoms)

    grid, molecules = molecule_grid_data(atoms, resolution, step, pad,
                                         cutoff_range, sigma_factor)

    from chimera import openModels as om
    if replace:
        from VolumeViewer import volume_list
        vlist = [v for v in volume_list()
                 if getattr(v, 'molmap_atoms', None) == atoms]
        om.close(vlist)

    from VolumeViewer import volume_from_grid_data
    v = volume_from_grid_data(grid, open_model = False,
                              show_dialog = show_dialog)
    v.initialize_thresholds(mfrac = (display_threshold, 1), replace = True)
    v.show()

    v.molmap_atoms = tuple(atoms)   # Remember atoms used to calculate volume
    v.molmap_parameters = (resolution, step, pad, cutoff_range, sigma_factor)

    if len(molecules) == 1 and model_id is None:
        om.add([v], sameAs = tuple(molecules)[0])
    else:
        if model_id is None:
            model_id = (om.Default, om.Default)
        om.add([v], baseId = model_id[0], subid = model_id[1])
        v.openState.xform = atoms[0].molecule.openState.xform

    return v

# -----------------------------------------------------------------------------
#
def molecule_grid_data(atoms, resolution, step, pad,
                       cutoff_range, sigma_factor):

    from _multiscale import get_atom_coordinates, bounding_box
    xyz = get_atom_coordinates(atoms, transformed = True)

    # Transform coordinates to local coordinates of the molecule containing
    # the first atom.  This handles multiple unaligned molecules.
    from Matrix import xform_matrix
    m0 = atoms[0].molecule
    tf = xform_matrix(m0.openState.xform.inverse())
    from _contour import affine_transform_vertices
    affine_transform_vertices(xyz, tf)

    xyz_min, xyz_max = bounding_box(xyz)

    origin = [x-pad for x in xyz_min]
    ijk = (xyz - origin) / step
    anum = [a.element.number for a in atoms]
    sdev = sigma_factor * resolution / step
    from numpy import zeros, float32
    sdevs = zeros((len(atoms),3), float32)
    sdevs[:] = sdev
    from math import pow, pi, ceil
    normalization = pow(2*pi,-1.5)*pow(sdev*step,-3)
    shape = [int(ceil((xyz_max[a] - xyz_min[a] + 2*pad) / step))
             for a in (2,1,0)]
    matrix = zeros(shape, float32)

    from _gaussian import sum_of_gaussians
    sum_of_gaussians(ijk, anum, sdevs, cutoff_range, matrix)
    matrix *= normalization

    molecules = set([a.molecule for a in atoms])
    if len(molecules) > 1:
        name = 'molmap res %.3g' % (resolution,)
    else:
        name =  'molmap %s res %.3g' % (m0.name, resolution)
    
    from VolumeData import Array_Grid_Data
    grid = Array_Grid_Data(matrix, origin, (step,step,step), name = name)

    return grid, molecules
