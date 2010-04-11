# -----------------------------------------------------------------------------
# Command to perform volume operations that create a new volume, such as
# erasing an octant, Gaussian filtering, adding maps, ....
#
#   Syntax: vop <operation> <volumeSpec>
#               [radius <r>]
#               [center <x,y,z>]
#               [iCenter <i,j,k>]
#               [fillValue <v>]
#               [sDev <d>]
#               [onGrid <id>]
#               [boundingGrid true|false>]
#               [axisOrder xyz|yxz|zxy|zyx|yzx|xzy]
#               [modelId <n>]
#               [inPlace true|false]
#               [subregion all|<i1,j1,k1,i2,j2,k2>]
#               [step <i>|<i,j,k>]
#               [gridSubregion all|<i1,j1,k1,i2,j2,k2>]
#               [gridStep <i>|<i,j,k>]
#               [frames <n>]
#               [start <f0>]
#               [playStep <fstep>]
#               [playDirection 1|-1]
#               [playRange <fmin,fmax>]
#               [addMode true|false]
#               [constantVolume true|false]
#               [scaleFactors <f1,f2,...>]
#
# where op is one of octant, ~octant, resample, add, zFlip, subtract, fourier,
# laplacian, gaussian, permuteAxes, bin, median, scale, boxes, morph, cover.
#
from Commands import CommandError
from Commands import filter_volumes, parse_floats, parse_ints, check_number
from Commands import parse_step, parse_subregion, parse_model_id, check_in_place

def vop_command(cmdname, args):

    vspec = ('volumeSpec','volumes','models')
    gspec = ('onGridSpec', 'onGrid', 'models')
    operations = {
        'add': (add_op, [vspec, gspec]),
        'bin': (bin_op, [vspec]),
        'boxes': (boxes_op, [vspec, ('markersSpec', 'markers', 'atoms')]),
        'cover': (cover_op, [vspec, ('atomBoxSpec', 'atomBox', 'atoms')]),
        'fourier': (fourier_op, [vspec]),
        'gaussian': (gaussian_op, [vspec]),
        'laplacian': (laplacian_op, [vspec]),
        'median': (median_op, [vspec]),
        'morph': (morph_op, [vspec]),
        'octant': (octant_op, [vspec]),
        '~octant': (octant_complement_op, [vspec]),
        'permuteAxes': (permute_axes_op, [vspec]),
        'resample': (resample_op, [vspec, gspec]),
        'scale': (scale_op, [vspec]),
        'subtract': (subtract_op, [('volume1Spec','vol1','models'),
                                   ('volume2Spec','vol2','models')]),
        'zFlip': (z_flip_op, [vspec]),
        }
    ops = operations.keys()

    sa = args.split(None, 2)
    if len(sa) < 2:
        raise CommandError, 'vop requires at least 2 arguments: vop <operation> <args...>'

    from Commands import parse_enumeration
    op = parse_enumeration(sa[0], ops)
    if op is None:
        # Handle old syntax where operation argument followed volume spec
        op = parse_enumeration(sa[1], ops)
        if op:
            sa = [sa[1], sa[0]] + sa[2:]
        else:
            raise CommandError, 'Unknown vop operation: %s' % sa[0]

    func, spec = operations[op]
    from Commands import doExtensionFunc
    fargs = ' '.join(sa[1:])
    doExtensionFunc(func, fargs, specInfo = spec)

# -----------------------------------------------------------------------------
#
def add_op(volumes, onGrid = None, boundingGrid = None,
           subregion = 'all', step = 1,
           gridSubregion = 'all', gridStep = 1,
           inPlace = False, scaleFactors = None, modelId = None):

    volumes = filter_volumes(volumes)
    if boundingGrid is None and not inPlace:
        boundingGrid = (onGrid is None)
    if onGrid is None:
        onGrid = volumes[:1]
    onGrid = filter_volumes(onGrid, 'onGrid')
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    gridSubregion = parse_subregion(gridSubregion, 'gridSubregion')
    gridStep = parse_step(gridStep, 'gridStep')
    if inPlace:
        if boundingGrid or gridStep != 1 or gridSubregion != 'all':
            raise CommandError, "Can't use inPlace option with boundingGrid or gridStep or gridSubregion options"
        for gv in onGrid:
            if not gv.data.writable:
                raise CommandError, "Can't modify volume in place: %s" % gv.name
            if not gv in volumes:
                raise CommandError, "Can't change grid in place"
    if isinstance(scaleFactors, basestring):
        scaleFactors = parse_floats(scaleFactors, 'scaleFactors', len(volumes))
    modelId = parse_model_id(modelId)
    for gv in onGrid:
        add_operation(volumes, subregion, step,
                      gv, gridSubregion, gridStep,
                      boundingGrid, inPlace, scaleFactors, modelId)

# -----------------------------------------------------------------------------
#
def add_operation(volumes, subregion, step,
                  gv, gridSubregion, gridStep,
                  boundingGrid, inPlace, scale, modelId):

    if scale is None:
        scale = [1]*len(volumes)
    if inPlace:
        rv = gv
        for i, v in enumerate(volumes):
            s = (scale[i] if v != rv else scale[i]-1)
            rv.add_interpolated_values(v, subregion = subregion,
                                       step = step, scale = s)
    else:
        gr = gv.subregion(step = gridStep, subregion = gridSubregion)
        if boundingGrid:
            if same_grids(volumes, subregion, step, gv, gr):
                # Avoid extending grid due to round-off errors.
                r = gr
            else:
                corners = volume_corners(volumes, subregion, step,
                                         gv.model_transform())
                r = gv.bounding_region(corners, step = gridStep, clamp = False)
        else:
            r = gr
        rg = gv.region_grid(r)
        if len(volumes) == 1:
            rg.name = volumes[0].name + ' resampled'
        elif scale[1] == 'minrms' or scale[1] < 0:
            rg.name = 'volume difference'
        else:
            rg.name = 'volume sum'
        from VolumeViewer import volume_from_grid_data
        rv = volume_from_grid_data(rg, model_id = modelId,
                                   show_data = False, show_dialog = False)
        rv.openState.xform = gv.openState.xform
        for i,v in enumerate(volumes):
            rv.add_interpolated_values(v, subregion = subregion, step = step,
                                       scale = scale[i])
    rv.data.values_changed()
    if volumes:
        rv.copy_settings_from(volumes[0],
                              copy_region = False, copy_xform = False)
    rv.show()
    for v in volumes:
        if not v is rv:
            v.unshow()

# -----------------------------------------------------------------------------
#
def same_grids(volumes, subregion, step, gv, gr):

    from VolumeViewer.volume import same_grid
    for v in volumes:
        if not same_grid(v, v.subregion(step, subregion), gv, gr):
            return False
    return True

# -----------------------------------------------------------------------------
#
def volume_corners(volumes, subregion, step, xform):

    from VolumeData import box_corners
    corners = []
    for v in volumes:
        xyz_min, xyz_max = v.xyz_bounds(step = step, subregion = subregion)
        vc = box_corners(xyz_min, xyz_max)
        from VolumeViewer.volume import transformed_points
        xf = xform.inverse()
        xf.multiply(v.model_transform())
        c = transformed_points(vc, xf)
        corners.extend(c)
    return corners

# -----------------------------------------------------------------------------
#
def bin_op(volumes, subregion = 'all', step = 1,
           binSize = (2,2,2), modelId = None):

    volumes = filter_volumes(volumes)
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    if isinstance(binSize, int):
        binSize = (binSize, binSize, binSize)
    elif isinstance(binSize, basestring):
        binSize = parse_ints(binSize, 'binSize', 3)
    modelId = parse_model_id(modelId)

    from bin import bin
    for v in volumes:
        bin(v, binSize, step, subregion, modelId)

# -----------------------------------------------------------------------------
#
def boxes_op(volumes, markers, size = 0, useMarkerSize = False,
             subregion = 'all', step = 1, modelId = None):

    volumes = filter_volumes(volumes)
    check_number(size, 'size')
    if size <= 0 and not useMarkerSize:
        raise CommandError, 'Must specify size or enable useMarkerSize'
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    modelId = parse_model_id(modelId)

    from boxes import boxes
    for v in volumes:
        boxes(v, markers, size, useMarkerSize, step, subregion, modelId)

# -----------------------------------------------------------------------------
#
def cover_op(volumes, atomBox = None, pad = 5.0, 
             box = None, x = None, y = None, z = None,
             fBox = None, fx = None, fy = None, fz = None,
             iBox = None, ix = None, iy = None, iz = None,
             step = 1, modelId = None):

    volumes = filter_volumes(volumes)
    check_number(pad, 'pad')

    if not atomBox is None and len(atomBox) == 0:
        raise CommandError, 'No atoms specified'
    box = parse_box(box, x, y, z, 'box', 'x', 'y', 'z')
    fBox = parse_box(fBox, fx, fy, fz, 'fBox', 'fx', 'fy', 'fz')
    iBox = parse_box(iBox, ix, iy, iz, 'iBox', 'ix', 'iy', 'iz')
    bc = len([b for b in (box, fBox, iBox, atomBox) if b])
    if bc == 0:
        raise CommandError, 'Must specify box to cover'
    if bc > 1:
        raise CommandError, 'Specify covering box in one way'

    step = parse_step(step, require_3_tuple = True)
    modelId = parse_model_id(modelId)

    from VolumeViewer import volume, volume_from_grid_data
    for v in volumes:
        g = v.grid_data(subregion = 'all', step = step, mask_zone = False)
        ijk_min, ijk_max = cover_box_bounds(v, step,
                                            atomBox, pad, box, fBox, iBox)
        cg = volume.map_from_periodic_map(g, ijk_min, ijk_max)
        cv = volume_from_grid_data(cg, model_id = modelId)
        cv.copy_settings_from(v, copy_region = False)
        cv.show()

# -----------------------------------------------------------------------------
#
def cover_box_bounds(volume, step, atoms, pad, box, fBox, iBox):

    grid = volume.data
    if atoms:
        from VolumeViewer.volume import atom_bounds
        ijk_min, ijk_max = atom_bounds(atoms, pad, volume)
    elif box:
        origin, gstep = grid.origin, grid.step
        ijk_min, ijk_max = [[(None if x is None else (x-o)/s)
                             for x,o,s in zip(xyz, origin, gstep)]
                            for xyz in box]
    elif iBox:
        ijk_min, ijk_max = iBox
    elif fBox:
        size = grid.size
        ijk_min = [(None if f is None else f*s) for f, s in zip(fBox[0],size)]
        ijk_max = [(None if f is None else f*s-1) for f, s in zip(fBox[1],size)]

    # Fill in unspecified dimensions.
    ijk_min = [(0 if i is None else i) for i in ijk_min]
    ijk_max = [(s-1 if i is None else i) for i,s in zip(ijk_max,grid.size)]

    # Integer bounds.
    from math import floor, ceil
    ijk_min = [int(floor(i)) for i in ijk_min]
    ijk_max = [int(ceil(i)) for i in ijk_max]

    # Handle step size > 1.
    ijk_min = [i/s for i,s in zip(ijk_min,step)]
    ijk_max = [i/s for i,s in zip(ijk_max,step)]

    return ijk_min, ijk_max

# -----------------------------------------------------------------------------
#
def parse_box(box, x, y, z, bname, xname, yname, zname):

    if box is None and x is None and y is None and z is None:
        return None
    if box:
        b6 = parse_floats(box, bname, 6)
        return (b6[:3], b6[3:])
    box = ([None,None,None], [None,None,None])
    for a,x,name in zip((0,1,2),(x,y,z),(xname,yname,zname)):
        if x:
            box[0][a], box[1][a] = parse_floats(x, name, 2)
    return box

# -----------------------------------------------------------------------------
#
def fourier_op(volumes, subregion = 'all', step = 1, modelId = None):

    volumes = filter_volumes(volumes)
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    modelId = parse_model_id(modelId)

    from fourier import fourier_transform
    for v in volumes:
        fourier_transform(v, step, subregion, modelId)

# -----------------------------------------------------------------------------
#
def gaussian_op(volumes, sDev = 1.0,
                subregion = 'all', step = 1, modelId = None):

    volumes = filter_volumes(volumes)
    check_number(sDev, 'sDev', positive = True)
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    modelId = parse_model_id(modelId)

    from gaussian import gaussian_convolve
    for v in volumes:
        gaussian_convolve(v, sDev, step, subregion, modelId)

# -----------------------------------------------------------------------------
#
def laplacian_op(volumes, subregion = 'all', step = 1, modelId = None):

    volumes = filter_volumes(volumes)
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    modelId = parse_model_id(modelId)
    
    from laplace import laplacian
    for v in volumes:
        laplacian(v, step, subregion, modelId)

# -----------------------------------------------------------------------------
#
def median_op(volumes, binSize = 3, iterations = 1,
              subregion = 'all', step = 1, modelId = None):

    volumes = filter_volumes(volumes)
    check_number(iterations, 'iterations', positive = True)
    binSize = parse_step(binSize, 'binSize', require_3_tuple = True)
    for b in binSize:
        if b <= 0 or b % 2 == 0:
            raise CommandError, 'Bin size must be positive odd integer, got %d' % b
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    modelId = parse_model_id(modelId)

    from median import median_filter
    for v in volumes:
        median_filter(v, binSize, iterations, step, subregion, modelId)

# -----------------------------------------------------------------------------
#
def morph_op(volumes, frames = 25, start = 0, playStep = 0.04,
             playDirection = 1, playRange = None, addMode = False,
             constantVolume = False, scaleFactors = None,
             hideOriginalMaps = True, subregion = 'all', step = 1,
             modelId = None):

    volumes = filter_volumes(volumes)
    check_number(frames, 'frames', int, nonnegative = True)
    check_number(start, 'start')
    check_number(playStep, 'playStep', nonnegative = True)
    if playRange is None:
        if addMode:
            prange = (-1.0,1.0)
        else:
            prange = (0.0,1.0)
    else:
        prange = parse_floats(playRange, 'playRange', 2)
    check_number(playDirection, 'playDirection')
    sfactors = parse_floats(scaleFactors, 'scaleFactors', len(volumes))
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    modelId = parse_model_id(modelId)
    vs = [tuple(v.matrix_size(step = step, subregion = subregion))
          for v in volumes]
    if len(set(vs)) > 1:
        sizes = ' and '.join([str(s) for s in vs])
        raise CommandError, "Volume grid sizes don't match: %s" % sizes
    from MorphMap import morph_maps
    morph_maps(volumes, frames, start, playStep, playDirection, prange,
               addMode, constantVolume, sfactors,
               hideOriginalMaps, subregion, step, modelId)
        
# -----------------------------------------------------------------------------
#
def octant_op(volumes, center = None, iCenter = None,
              subregion = 'all', step = 1, inPlace = False,
              fillValue = 0, modelId = None):

    volumes = filter_volumes(volumes)
    center = parse_floats(center, 'center', 3)
    iCenter = parse_floats(iCenter, 'iCenter', 3)
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    check_in_place(inPlace, volumes)
    check_number(fillValue, 'fillValue')
    modelId = parse_model_id(modelId)
    outside = True
    for v in volumes:
        octant_operation(v, outside, center, iCenter, subregion, step,
                         inPlace, fillValue, modelId)

# -----------------------------------------------------------------------------
#
def octant_complement_op(volumes, center = None, iCenter = None,
              subregion = 'all', step = 1, inPlace = False,
              fillValue = 0, modelId = None):

    volumes = filter_volumes(volumes)
    center = parse_floats(center, 'center', 3)
    iCenter = parse_floats(iCenter, 'iCenter', 3)
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    check_in_place(inPlace, volumes)
    check_number(fillValue, 'fillValue')
    modelId = parse_model_id(modelId)
    outside = False
    for v in volumes:
        octant_operation(v, outside, center, iCenter, subregion, step,
                         inPlace, fillValue, modelId)

# -----------------------------------------------------------------------------
#
def octant_operation(v, outside, center, iCenter,
                     subregion, step, inPlace, fillValue, modelId):

    vc = v.writable_copy(require_copy = not inPlace,
                         subregion = subregion, step = step,
                         model_id = modelId, show = False)
    ic = submatrix_center(v, center, iCenter, subregion, step)
    ijk_max = [i-1 for i in vc.data.size]
    from VolumeEraser import set_box_value
    set_box_value(vc.data, fillValue, ic, ijk_max, outside)
    vc.data.values_changed()
    vc.show()

# -----------------------------------------------------------------------------
#
def permute_axes_op(volumes, axisOrder = 'xyz',
                    subregion = 'all', step = 1, modelId = None):

    volumes = filter_volumes(volumes)
    ao = {'xyz':(0,1,2), 'xzy':(0,2,1), 'yxz':(1,0,2), 
          'yzx':(1,2,0), 'zxy':(2,0,1), 'zyx':(2,1,0)}
    if not axisOrder in ao:
        raise CommandError, 'Axis order must be xyz, xzy, zxy, zyx, yxz, or yzx'
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    modelId = parse_model_id(modelId)

    from permute import permute_axes
    for v in volumes:
        permute_axes(v, ao[axisOrder], step, subregion, modelId)

# -----------------------------------------------------------------------------
#
def resample_op(volumes, onGrid = None, boundingGrid = False,
                subregion = 'all', step = 1,
                gridSubregion = 'all', gridStep = 1,
                modelId = None):

    volumes = filter_volumes(volumes)
    if onGrid is None:
        raise CommandError, 'Resample operation must specify onGrid option'
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    gridSubregion = parse_subregion(gridSubregion, 'gridSubregion')
    gridStep = parse_step(gridStep, 'gridStep')
    onGrid = filter_volumes(onGrid, 'onGrid')
    modelId = parse_model_id(modelId)
    for v in volumes:
        for gv in onGrid:
            add_operation([v], subregion, step,
                          gv, gridSubregion, gridStep,
                          boundingGrid, False, None, modelId)

# -----------------------------------------------------------------------------
#
def scale_op(volumes, shift = 0, factor = 1, type = None,
              subregion = 'all', step = 1, modelId = None):

    volumes = filter_volumes(volumes)
    check_number(shift, 'shift')
    check_number(factor, 'factor')
    if not type is None:
        import numpy as n
        types = {'int8': n.int8,
                 'uint8': n.uint8,
                 'int16': n.int16,
                 'uint16': n.uint16,
                 'int32': n.int32,
                 'uint32': n.uint32,
                 'float32': n.float32,
                 'float64': n.float64,
                 }
        if type in types:
            type = types[type]
        else:
            raise CommandError, ('Unknown data value type "%s", use %s'
                                 % (type, ', '.join(types.keys())))
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    modelId = parse_model_id(modelId)

    from scale import scaled_volume
    for v in volumes:
        scaled_volume(v, factor, shift, type, step, subregion, modelId)

# -----------------------------------------------------------------------------
#
def subtract_op(vol1, vol2, onGrid = None, boundingGrid = False,
                subregion = 'all', step = 1,
                gridSubregion = 'all', gridStep = 1,
                inPlace = False, scaleFactors = None, minRMS = False,
                modelId = None):

    vol1 = filter_volumes(vol1)
    vol2 = filter_volumes(vol2)
    if len(vol1) != 1 or len(vol2) != 1:
        raise CommandError, 'vop subtract operation requires exactly two volumes'
    if minRMS and scaleFactors:
        raise CommandError, 'vop subtract cannot specify both minRMS and scaleFactors options.'
    if minRMS:
        mult = (1,'minrms')
    elif scaleFactors:
        m0,m1 = parse_floats(scaleFactors, 'scaleFactors', 2)
        mult = (m0,-m1)
    else:
        mult = (1,-1)

    add_op(vol1+vol2, onGrid, boundingGrid, subregion, step,
           gridSubregion, gridStep, inPlace, mult, modelId)

# -----------------------------------------------------------------------------
#
def z_flip_op(volumes, subregion = 'all', step = 1,
              inPlace = False, modelId = None):

    volumes = filter_volumes(volumes)
    subregion = parse_subregion(subregion)
    step = parse_step(step)
    check_in_place(inPlace, volumes[:1])
    modelId = parse_model_id(modelId)

    for v in volumes:
        zflip_operation(v, subregion, step, inPlace, modelId)
        
# -----------------------------------------------------------------------------
#
def zflip_operation(v, subregion, step, in_place, model_id):

    g = v.grid_data(subregion = subregion, step = step, mask_zone = False)
    if in_place:
        m = g.full_matrix()
        import zflip
        zflip.zflip(m)
        v.data.values_changed()
        v.show()
    else:
        import zflip
        zfg = zflip.Z_Flip_Grid(g)
        import VolumeViewer
        fv = VolumeViewer.volume_from_grid_data(zfg, model_id = model_id)
        fv.copy_settings_from(v, copy_region = False)
        fv.show()
        v.unshow()

# -----------------------------------------------------------------------------
# Return center in submatrix index units.
#
def submatrix_center(v, xyz_center, index_center, subregion, step):

    ijk_min, ijk_max, step = v.subregion(step, subregion)

    if index_center is None:
        if xyz_center is None:
            index_center = [0.5*(ijk_min[a] + ijk_max[a]) for a in range(3)]
        else:
            index_center = v.data.xyz_to_ijk(xyz_center)

    ioffset = map(lambda a,s: ((a+s-1)/s)*s, ijk_min, step)

    sic = tuple(map(lambda a,b,s: (a-b)/s, index_center, ioffset, step))
    return sic
