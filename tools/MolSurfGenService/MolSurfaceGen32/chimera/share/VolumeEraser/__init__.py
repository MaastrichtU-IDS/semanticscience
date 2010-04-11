# -----------------------------------------------------------------------------
#
def zero_volume_inside_selected_atom():

    from chimera import selection
    atoms = selection.currentAtoms()
    if len(atoms) == 1:
        zero_volume_inside_atom(atoms[0])

# -----------------------------------------------------------------------------
#
def zero_volume_inside_atom(atom):

    dr = writable_volume()
    if dr:
        center, radius = volume_sphere(atom, dr)
        zero_data_in_sphere(dr.data, center, radius)
        dr.data.values_changed()
        dr.show()

# -----------------------------------------------------------------------------
#
def writable_volume():

    from VolumeViewer import active_volume
    dr = active_volume()
    if dr == None:
        return None         # No volume chosen in volume viewer
    return dr.writable_copy()

# -----------------------------------------------------------------------------
#
def zero_volume_outside_atom(atom):

    dr = writable_volume()
    if dr:
        center, radius = volume_sphere(atom, dr)
        zero_data_outside_sphere(dr.data, center, radius)
        dr.data.values_changed()
        dr.show()

# -----------------------------------------------------------------------------
#
def volume_sphere(atom, dr):
    
    xform_to_volume = dr.model_transform()
    if xform_to_volume == None:
        return
    xform_to_volume.invert()

    radius = atom.radius
    import SurfaceZone
    center = SurfaceZone.get_atom_coordinates([atom], xform_to_volume)[0]
    return center, radius

# -----------------------------------------------------------------------------
#
def zero_data_in_sphere(grid_data, center, radius):

    # Optimization: Mask only subregion containing sphere.
    ijk_min, ijk_max = sphere_grid_bounds(grid_data, center, radius)
    from VolumeData import Grid_Subregion, zone_masked_grid_data
    subgrid = Grid_Subregion(grid_data, ijk_min, ijk_max)

    mg = zone_masked_grid_data(subgrid, [center], radius)

    dmatrix = subgrid.full_matrix()
    mdmatrix = mg.full_matrix()

    from numpy import subtract
    subtract(dmatrix, mdmatrix, dmatrix)

# -----------------------------------------------------------------------------
#
def zero_data_outside_sphere(grid_data, center, radius):

    from VolumeData import zone_masked_grid_data
    mg = zone_masked_grid_data(grid_data, [center], radius)

    dmatrix = grid_data.full_matrix()
    mdmatrix = mg.full_matrix()

    dmatrix[:,:,:] = mdmatrix[:,:,:]

# -----------------------------------------------------------------------------
#
def sphere_grid_bounds(grid_data, center, radius):

    ijk_center = grid_data.xyz_to_ijk(center)
    spacings = grid_data.plane_spacings()
    ijk_size = map(lambda s, r=radius: r/s, spacings)
    from math import floor, ceil
    ijk_min = map(lambda c, s: max(int(floor(c-s)), 0), ijk_center, ijk_size)
    ijk_max = map(lambda c, s, m: min(int(ceil(c+s)), m-1),
                  ijk_center, ijk_size, grid_data.size)
    return ijk_min, ijk_max

# -----------------------------------------------------------------------------
#
def zero_volume_inside_selection_box():

    dr = writable_volume()
    if dr:
        from VolumeViewer import subregion_selection_bounds
        ijk_min, ijk_max = subregion_selection_bounds()
        if ijk_min == None:
            return          # No subregion outline box shown
        zero_volume_inside_box(dr.data, ijk_min, ijk_max)
        dr.data.values_changed()
        dr.show()
    
# -----------------------------------------------------------------------------
#
def zero_volume_inside_box(data, ijk_min, ijk_max):
    
    set_box_value(data, 0, ijk_min, ijk_max)
    
# -----------------------------------------------------------------------------
#
def zero_volume_outside_box(data, ijk_min, ijk_max):

    set_value_outside_box(data, 0, ijk_min, ijk_max)

# -----------------------------------------------------------------------------
#
def set_box_value(data, value, ijk_min, ijk_max, outside = False):

    if outside:
        set_value_outside_box(data, value, ijk_min, ijk_max)
        return

    from math import floor, ceil
    ijk_origin = [max(0, int(floor(i))) for i in ijk_min]
    ijk_last = map(lambda i,s: min(s-1, int(ceil(i))), ijk_max, data.size)
    ijk_size = map(lambda a,b: b-a+1, ijk_origin, ijk_last)
    if len([i for i in ijk_size if i > 0]) < 3:
        return

    m = data.matrix(ijk_origin, ijk_size)
    m[:,:,:] = value
    
# -----------------------------------------------------------------------------
#
def set_value_outside_box(data, value, ijk_min, ijk_max):

    i0,j0,k0 = [i-1 for i in ijk_min]
    i1,j1,k1 = [i+1 for i in ijk_max]
    im,jm,km = [s-1 for s in data.size]
    set_box_value(data, value, (0,0,0), (im,jm,k0))
    set_box_value(data, value, (0,0,k1), (im,jm,km))
    set_box_value(data, value, (0,0,k0), (i0,jm,k1))
    set_box_value(data, value, (i1,0,k0), (im,jm,k1))
    set_box_value(data, value, (i0,0,k0), (i1,j0,k1))
    set_box_value(data, value, (i0,j1,k0), (i1,jm,k1))

# -----------------------------------------------------------------------------
# The step parameter allows zeroing more than one plane at some of the 6 faces
# of the volume so that subsampling using every <step> planes will still have
# zeros on the boundary.
#
def zero_volume_boundary(step = 1):

    dr = writable_volume()
    if dr:
        dmatrix = dr.data.full_matrix()
        zero_array_boundary(dmatrix, step)
        dr.data.values_changed()
        dr.show()

# -----------------------------------------------------------------------------
#
def zero_array_boundary(array, step = 1):

    m = array
    from numpy import size
    if size(m) == 0:
        return
    
    m[:,:,0] = 0
    m[:,0,:] = 0
    m[0,:,:] = 0

    i,j,k = map(lambda s: ((s-1)/step)*step, tuple(m.shape))
    m[:,:,k:] = 0
    m[:,j:,:] = 0
    m[i:,:,:] = 0
