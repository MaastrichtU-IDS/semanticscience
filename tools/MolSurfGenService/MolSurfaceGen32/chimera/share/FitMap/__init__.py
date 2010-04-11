# -----------------------------------------------------------------------------
# Optimize the position of molecules in density maps.
#
# Uses gradient descent to rigidly move molecule to increase sum of density
# values at selected atom positions.
#

# -----------------------------------------------------------------------------
#
def move_selected_atoms_to_maximum(max_steps = 100, ijk_step_size_min = 0.01,
                                   ijk_step_size_max = 0.5,
                                   optimize_translation = True,
                                   optimize_rotation = True,
                                   move_whole_molecules = True,
                                   request_stop_cb = None):

    from VolumeViewer import active_volume
    volume = active_volume()
    if volume == None or volume.model_transform() == None:
        if request_stop_cb:
            request_stop_cb('No volume data set.')
        return {}
    
    from chimera import selection
    atoms = selection.currentAtoms()
    if len(atoms) == 0:
        if request_stop_cb:
            request_stop_cb('No atoms selected.')
        return {}

    stats = move_atoms_to_maximum(atoms, volume, max_steps,
                                  ijk_step_size_min, ijk_step_size_max,
                                  optimize_translation, optimize_rotation,
                                  move_whole_molecules,
                                  request_stop_cb)
    return stats

# -----------------------------------------------------------------------------
#
def move_atoms_to_maximum(atoms, volume,
                          max_steps = 100, ijk_step_size_min = 0.01,
                          ijk_step_size_max = 0.5,
                          optimize_translation = True,
                          optimize_rotation = True,
                          move_whole_molecules = True,
                          request_stop_cb = None):

    points = atom_coordinates(atoms)
    point_weights = None        # Each atom give equal weight in fit.

    metric = 'sum product'
    move_tf, stats = motion_to_maximum(points, point_weights, volume, max_steps,
                                       ijk_step_size_min, ijk_step_size_max,
                                       optimize_translation, optimize_rotation,
                                       metric, request_stop_cb)
    stats['data region'] = volume
    stats['molecules'] = list(set([a.molecule for a in atoms]))
    import move
    move.move_models_and_atoms(move_tf, [], atoms, move_whole_molecules, volume)

    from Matrix import chimera_xform
    poc, clevel = points_outside_contour(points, chimera_xform(move_tf), volume)
    stats['atoms outside contour'] = poc
    stats['contour level'] = clevel

    return stats

# -----------------------------------------------------------------------------
#
def motion_to_maximum(points, point_weights, data_region, max_steps,
                      ijk_step_size_min, ijk_step_size_max,
                      optimize_translation, optimize_rotation,
                      metric = 'sum product', request_stop_cb = None):

    xyz_to_ijk_transform = data_region_xyz_to_ijk_transform(data_region)
    data_array = data_region.matrix(step = 1)
    move_tf, stats = \
             locate_maximum(points, point_weights,
                            data_array, xyz_to_ijk_transform,
                            max_steps, ijk_step_size_min, ijk_step_size_max,
                            optimize_translation, optimize_rotation,
                            metric, request_stop_cb)

    return move_tf, stats

# -----------------------------------------------------------------------------
# Find transformation to move to local sum of densities maximum.
# Take gradient steps of fixed length and cut step length when several
# steps in a row produce little overall motion.
#
def locate_maximum(points, point_weights, data_array, xyz_to_ijk_transform,
                   max_steps, ijk_step_size_min, ijk_step_size_max,
                   optimize_translation, optimize_rotation,
                   metric, request_stop_cb):

    segment_steps = 4
    cut_step_size_threshold = .5
    step_cut_factor = .5
    
    ijk_step_size = ijk_step_size_max

    from Matrix import identity_matrix, multiply_matrices
    from Matrix import shift_and_angle, axis_center_angle_shift
    move_tf = identity_matrix()

    from numpy import sum
    rotation_center = sum(points, axis=0) / len(points)

    step = 0
    while step < max_steps and ijk_step_size > ijk_step_size_min:
        xyz_to_ijk_tf = multiply_matrices(xyz_to_ijk_transform, move_tf)
        seg_tf = step_to_maximum(points, point_weights,
                                 data_array, xyz_to_ijk_tf,
                                 segment_steps, ijk_step_size,
                                 optimize_translation, optimize_rotation,
                                 rotation_center, metric)
        step += segment_steps
        mm = maximum_ijk_motion(points, xyz_to_ijk_tf, seg_tf)
        if mm < cut_step_size_threshold * segment_steps * ijk_step_size:
            ijk_step_size *= step_cut_factor
        move_tf = multiply_matrices(seg_tf, move_tf)
        if request_stop_cb:
            shift, angle = shift_and_angle(move_tf, rotation_center)
            if request_stop_cb('After %d steps: shift %.3g, rotation %.3g degrees'
                               % (step, shift, angle)):
                break

    # Record statistics of optimization.
    shift, angle = shift_and_angle(move_tf, rotation_center)
    axis, axis_point, angle, axis_shift = axis_center_angle_shift(move_tf)
    xyz_to_ijk_tf = multiply_matrices(xyz_to_ijk_transform, move_tf)
    stats = {'shift': shift, 'axis': axis, 'axis point': axis_point,
             'angle': angle, 'axis shift': axis_shift, 'steps': step,
             'points': len(points), 'transform': move_tf}

    if point_weights is None:
        amv, npts = average_map_value(points, xyz_to_ijk_tf, data_array)
        stats['average map value'] = amv
        stats['points in map'] = npts      # Exludes out of bounds points
    else:
        from VolumeData import interpolate_volume_data
        map_values, outside = interpolate_volume_data(points, xyz_to_ijk_tf,
                                                      data_array)
        olap, cor, corm = overlap_and_correlation(point_weights, map_values)
        stats['overlap'] = olap
        stats['correlation'] = cor
        stats['correlation about mean'] = corm
                
    return move_tf, stats
    
# -----------------------------------------------------------------------------
#
def step_to_maximum(points, point_weights, data_array, xyz_to_ijk_transform,
                    steps, ijk_step_size,
                    optimize_translation, optimize_rotation,
                    rotation_center, metric):

    step_types = []
    if optimize_translation:
        step_types.append(translation_step)
    if optimize_rotation:
        step_types.append(rotation_step)
        
    from Matrix import identity_matrix, multiply_matrices
    move_tf = identity_matrix()

    if step_types:
        for step in range(steps):
            calculate_step = step_types[step % len(step_types)]
            xyz_to_ijk_tf = multiply_matrices(xyz_to_ijk_transform, move_tf)
#            amv, npts = average_map_value(points, xyz_to_ijk_tf, data_array)
#            print 'average map value = %.3g for %d atoms' % (amv, npts)
            step_tf = calculate_step(points, point_weights,
                                     rotation_center, data_array,
                                     xyz_to_ijk_tf, ijk_step_size, metric)
            move_tf = multiply_matrices(step_tf, move_tf)
#            mm = maximum_ijk_motion(points, xyz_to_ijk_transform, move_tf)
#            print 'ijk motion for step', step, ' = ', mm

    return move_tf

# -----------------------------------------------------------------------------
#
def translation_step(points, point_weights, center, data_array,
                     xyz_to_ijk_transform, ijk_step_size, metric):

    g = gradient_direction(points, point_weights, data_array,
                           xyz_to_ijk_transform, metric)
    from numpy import array, float, dot as matrix_multiply
    tf = array(xyz_to_ijk_transform)
    gijk = matrix_multiply(tf[:,:3], g)
    from Matrix import norm
    n = norm(gijk)
    if n > 0:
        delta = g * (ijk_step_size / n)
    else:
        delta = array((0,0,0), float)

    delta_tf = ((1,0,0,delta[0]),
                (0,1,0,delta[1]),
                (0,0,1,delta[2]))
    return delta_tf

# -----------------------------------------------------------------------------
#
def gradient_direction(points, point_weights, data_array,
                       xyz_to_ijk_transform, metric = 'sum product'):

    if metric == 'sum product':
        f = sum_product_gradient_direction
        kw = {}
    elif metric == 'correlation':
        f = correlation_gradient_direction
        kw = {'about_mean':False}
    elif metric == 'correlation about mean':
        f = correlation_gradient_direction
        kw = {'about_mean':True}
    a = f(points, point_weights, data_array, xyz_to_ijk_transform, *kw)
    return a

# -----------------------------------------------------------------------------
#
def sum_product_gradient_direction(points, point_weights, data_array,
                                   xyz_to_ijk_transform):

    from VolumeData import interpolate_volume_gradient
    gradients, outside = interpolate_volume_gradient(points,
                                                     xyz_to_ijk_transform,
                                                     data_array)
    from numpy import sum, dot as matrix_multiply
    if point_weights is None:
        g = sum(gradients, axis=0)
    else:
        g = matrix_multiply(point_weights, gradients)
    return g

# -----------------------------------------------------------------------------
# Derivative of correlation with respect to translation of points.
#
def correlation_gradient_direction(points, point_weights, data_array,
                                   xyz_to_ijk_transform, about_mean):

    # TODO: Exclude points outside data.  Currently treated as zero values.
    import VolumeData as vd
    values, outside = vd.interpolate_volume_data(points,
                                                 xyz_to_ijk_transform,
                                                 data_array)
    gradients, outside = vd.interpolate_volume_gradient(points,
                                                        xyz_to_ijk_transform,
                                                        data_array)
    # g = (|v-vm|^2*sum(wi*vi,j) - sum(wi*vi)*sum((vi-vm)*vi,j)) / |w||v-vm|^3
    from numpy import dot
    wv = dot(point_weights, values)
    if about_mean:
        vm = values.sum() / len(values)
        values -= vm
    vg = dot(values, gradients)
    wg = dot(point_weights, gradients)
    values *= values
    v2 = values.sum()
    ga = v2*wg - wv*vg
    return ga
    
# -----------------------------------------------------------------------------
#
def rotation_step(points, point_weights, center, data_array,
                  xyz_to_ijk_transform, ijk_step_size, metric):

    axis = torque_axis(points, point_weights, center, data_array,
                       xyz_to_ijk_transform, metric)

    from Matrix import norm, rotation_transform
    na = norm(axis)
    if len(points) == 1 or na == 0:
        axis = (0,0,1)
        angle = 0
    else:
        axis /= na
        angle = angle_step(axis, points, center, xyz_to_ijk_transform,
                           ijk_step_size)
    move_tf = rotation_transform(axis, angle, center)
    return move_tf
    
# -----------------------------------------------------------------------------
#
def torque_axis(points, point_weights, center, data_array,
                xyz_to_ijk_transform, metric = 'sum product'):

    if metric == 'sum product':
        f = sum_product_torque_axis
        kw = {}
    elif metric == 'correlation':
        f = correlation_torque_axis
        kw = {'about_mean':False}
    elif metric == 'correlation about mean':
        f = correlation_torque_axis
        kw = {'about_mean':True}
    a = f(points, point_weights, center, data_array, xyz_to_ijk_transform, **kw)
    return a
    
# -----------------------------------------------------------------------------
#
def sum_product_torque_axis(points, point_weights, center, data_array,
                            xyz_to_ijk_transform):

    from VolumeData import interpolate_volume_gradient
    gradients, outside = interpolate_volume_gradient(points,
                                                     xyz_to_ijk_transform,
                                                     data_array)
    from numpy import multiply, sum, subtract
    forces = gradients
    if not point_weights is None:
        for a in range(3):
            multiply(forces[:,a], point_weights, forces[:,a])
    from Matrix import cross_products, cross_product
    torques = cross_products(points, forces)
    torque = sum(torques, axis=0)               # Torque about (0,0,0)
    f = sum(forces, axis=0)
    center_torque = cross_product(center, f)
    axis = subtract(torque, center_torque)  # Torque about center
    return axis

# -----------------------------------------------------------------------------
# Correlation variation with respect to rotation of points about center.
#
def correlation_torque_axis(points, point_weights, center, data_array,
                            xyz_to_ijk_transform, about_mean):

    # TODO: Exclude points outside data.  Currently treated as zero values.
    import VolumeData as vd
    values, outside = vd.interpolate_volume_data(points,
                                                 xyz_to_ijk_transform,
                                                 data_array)
    gradients, outside = vd.interpolate_volume_gradient(points,
                                                        xyz_to_ijk_transform,
                                                        data_array)
    # t = (|v-vm|^2*sum(wi*rixDvi) - sum(wi*vi)*sum((vi-vm)*rixDvi)) / |w||v-vm|^3
    from numpy import dot
    wv = dot(point_weights, values)
    if about_mean:
        vm = values.sum() / len(values)
        values -= vm
    r = points - center
    from Matrix import cross_products
    rxg = cross_products(r, gradients)
    wrxg = dot(point_weights, rxg)
    vrxg = dot(values, rxg)
    values *= values
    v2 = values.sum()
    ta = v2*wrxg - wv*vrxg
    if v2 != 0:
        ta /= v2 ** 1.5         # Avoid overflow error normalizing ta.
    return ta

# -----------------------------------------------------------------------------
# Return angle such that rotating point about given axis and center causes the
# largest motion in ijk space to equal ijk_step_size.
#
def angle_step(axis, points, center, xyz_to_ijk_transform, ijk_step_size):

    from numpy import subtract, array
    xyz_offset = subtract(points, center)
    from Matrix import cross_product_transform, multiply_matrices, apply_matrix, maximum_norm
    cp_tf = cross_product_transform(axis)
    tf = array(multiply_matrices(xyz_to_ijk_transform, cp_tf))
    tf[:,3] = 0         # zero translation
    av_ijk = apply_matrix(tf, xyz_offset)
    av = maximum_norm(av_ijk)
    if av > 0:
        from math import pi
        angle = (ijk_step_size / av) * 180.0/pi
    else:
        angle = 0
    return angle
    
# -----------------------------------------------------------------------------
#
def maximum_ijk_motion(points, xyz_to_ijk_transform, move_tf):

    from Matrix import multiply_matrices, apply_matrix, maximum_norm
    ijk_moved_tf = multiply_matrices(xyz_to_ijk_transform, move_tf)

    from numpy import subtract
    diff_tf = subtract(ijk_moved_tf, xyz_to_ijk_transform)

    ijk_diff = apply_matrix(diff_tf, points)
    d = maximum_norm(ijk_diff)
    return d


# -----------------------------------------------------------------------------
#
def atom_coordinates(atoms):

    from _multiscale import get_atom_coordinates
    points = get_atom_coordinates(atoms, transformed = True)
    return points

# -----------------------------------------------------------------------------
#
def average_map_value_at_atom_positions(atoms, volume = None):

    if volume is None:
        from VolumeViewer import active_volume
        volume = active_volume()

    points = atom_coordinates(atoms)

    if volume is None or len(points) == 0:
        return 0, len(points)

    xyz_to_ijk_transform = data_region_xyz_to_ijk_transform(volume)
    data_array = volume.matrix(step = 1)

    amv, npts = average_map_value(points, xyz_to_ijk_transform, data_array)
    return amv, npts

# -----------------------------------------------------------------------------
#
def average_map_value(points, xyz_to_ijk_transform, data_array):

    from VolumeData import interpolate_volume_data
    values, outside = interpolate_volume_data(points, xyz_to_ijk_transform,
                                              data_array)
    from numpy import sum
    s = sum(values)
    n = len(points) - len(outside)
    if n > 0:
        amv = s / n
    else:
        amv = 0
    return amv, n

# -----------------------------------------------------------------------------
#
def data_region_xyz_to_ijk_transform(data_region):
    
    xf = data_region.model_transform()
    xf.invert()
    from Matrix import xform_matrix, translation_matrix, multiply_matrices
    xyz_to_data_xyz = xform_matrix(xf)
    data_xyz_to_ijk = data_region.data.xyz_to_ijk_transform
    ijk_min = data_region.region[0]
    ijk_origin_shift = translation_matrix(map(lambda a: -a, ijk_min))
    xyz_to_ijk_transform = multiply_matrices(
        ijk_origin_shift, data_xyz_to_ijk, xyz_to_data_xyz)
    return xyz_to_ijk_transform

# -----------------------------------------------------------------------------
#
def map_points_and_weights(v, above_threshold, metric = 'sum product'):

    from chimera import Xform
    m, tf_inv = v.matrix_and_transform(Xform(), subregion = None, step = None)
          
    from Matrix import invert_matrix
    tf = invert_matrix(tf_inv)

    size = list(m.shape)
    size.reverse()

    from VolumeData import grid_indices
    from numpy import single as floatc, ravel, nonzero, take
    points = grid_indices(size, floatc)        # i,j,k indices
    import _contour
    _contour.affine_transform_vertices(points, tf)

    weights = ravel(m).astype(floatc)

    if above_threshold:
        # Keep only points where density is above lowest displayed threshold
        threshold = min(v.surface_levels)
        from numpy import greater_equal, compress
        ge = greater_equal(weights, threshold)
        points = compress(ge, points, 0)
        weights = compress(ge, weights)

    if metric == 'correlation about mean':
        wm = weights.sum() / len(weights)
        weights -= wm
    else:
        # Eliminate points with zero weight.
        nz = nonzero(weights)[0]
        if len(nz) < len(weights):
            points = take(points, nz, axis=0)
            weights = take(weights, nz, axis=0)

    return points, weights
    
# -----------------------------------------------------------------------------
# xform is transform to apply to first map in global coordinates.
#
def map_overlap_and_correlation(map1, map2, above_threshold, xform = None):

    p, w1 = map_points_and_weights(map1, above_threshold)
    if xform is None:
        from chimera import Xform
        xform = Xform()
    w2 = map2.interpolated_values(p, xform, subregion = None, step = None)
    return overlap_and_correlation(w1, w2)

# -----------------------------------------------------------------------------
#
def overlap_and_correlation(v1, v2):

    from numpy import sum
    from numpy import dot as inner_product
    v1 = float_array(v1)
    v2 = float_array(v2)
    olap = inner_product(v1, v2)
    n1 = inner_product(v1, v1)
    n2 = inner_product(v2, v2)
    n = len(v1)
    m1 = sum(v1) / n
    m2 = sum(v2) / n
    d2 = (n1 - n*m1*m1)*(n2 - n*m2*m2)
    if d2 < 0:
        d2 = 0          # This only happens due to rounding error.
    from math import sqrt
    d = sqrt(d2)
    corm = (olap - n*m1*m2) / d if d > 0 else 0.0
    d = sqrt(n1*n2)
    cor = olap / d if d > 0 else 0.0
    return olap, cor, corm
    
# -----------------------------------------------------------------------------
#
def float_array(a):

    from numpy import ndarray, float32, float64, single as floatc, array
    if type(a) is ndarray and a.dtype in (float32, float64):
        return a
    return array(a, floatc)

# -----------------------------------------------------------------------------
# Move selected atoms to local maxima of map shown by volume viewer.
# Each atom is moved independently.
#
def move_atoms_to_maxima():

    from chimera.selection import currentAtoms
    atoms = currentAtoms()
    if len(atoms) == 0:
        from chimera.replyobj import status
        status('No atoms selected.')
        return
        
    for a in atoms:
        move_atom_to_maximum(a)

# -----------------------------------------------------------------------------
#
def move_atom_to_maximum(a, max_steps = 100,
                         ijk_step_size_min = 0.001, ijk_step_size_max = 0.5):

    from VolumeViewer import active_volume
    dr = active_volume()
    if dr == None or dr.model_transform() == None:
        from chimera.replyobj import status
        status('No data shown by volume viewer dialog')
        return

    points = atom_coordinates([a])
    point_weights = None
    move_tf, stats = motion_to_maximum(points, point_weights, dr, max_steps,
                                       ijk_step_size_min, ijk_step_size_max,
                                       optimize_translation = True,
                                       optimize_rotation = False)

    # Update atom position.
    from Matrix import chimera_xform
    xf = chimera_xform(move_tf)
    mxf = a.molecule.openState.xform
    p = mxf.inverse().apply(xf.apply(a.xformCoord()))
    a.setCoord(p)

# -----------------------------------------------------------------------------
#
def atoms_outside_contour(atoms, volume = None):

    if volume is None:
        from VolumeViewer import active_volume
        volume = active_volume()
    points = atom_coordinates(atoms)
    from chimera import Xform
    poc, clevel = points_outside_contour(points, Xform(), volume)
    return poc, clevel

# -----------------------------------------------------------------------------
#
def points_outside_contour(points, xf, dr):

    if (dr == None or
        dr.surface_model() == None or
        not dr.surface_model().display):
        return None, None

    levels = dr.surface_levels
    if len(levels) == 0:
        return None, None

    contour_level = min(levels)
    values = dr.interpolated_values(points, xf, subregion = None, step = None)
    from numpy import sum
    poc = sum(values < contour_level)
    return poc, contour_level
