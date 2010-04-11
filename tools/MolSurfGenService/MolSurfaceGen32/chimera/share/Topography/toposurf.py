# -----------------------------------------------------------------------------
# Create a surface with z height from a 2d array.
#

# -----------------------------------------------------------------------------
# Interpolation modes are 'isotropic' or 'none'.
# Mesh patterns are 'isotropic', 'slash', or 'backslash'.
# Colormap is 'rainbow' or 'none'.
#
def create_volume_plane_surface(volume, height, interpolate = 'cubic',
                                mesh = 'isotropic', colormap = 'rainbow',
                                smoothing_factor = 0.3,
                                smoothing_iterations = 0,
                                color = (.7, .7, .7, 1),
                                replace = True):

    m = volume.matrix()
    axes = [a for a in range(3) if m.shape[2-a] == 1]
    if len(axes) != 1:
        from chimera.replyobj import warning
        warning('Volume %s has more than one plane shown (%d,%d,%d)' %
                ((volume.name,) + tuple(reversed(m.shape))))
        return
    axis = axes[0]
    m = m.squeeze()     # Convert 3d array to 2d

    tf = volume.matrix_indices_to_xyz_transform()
    perm = {0: ((0,0,1,0),(1,0,0,0),(0,1,0,0)),     # 2d matrix xyh -> 3d yzx
            1: ((1,0,0,0),(0,0,1,0),(0,1,0,0)),     # 2d matrix xyh -> 3d xzy
            2: ((1,0,0,0),(0,1,0,0),(0,0,1,0))}[axis]
    from Matrix import multiply_matrices
    tf = multiply_matrices(tf, perm)
    
    s = create_surface(m, height, tf, color, interpolate, mesh,
                       smoothing_factor, smoothing_iterations)
    s.name = volume.name + ' height'

    if colormap == 'rainbow':
        invert = not height is None and height < 0
        tf = volume.data.ijk_to_xyz_transform
        normal = [tf[i][axis] for i in range(3)]
        colormap_surface(s, normal, rainbow_colormap(invert))

    from chimera import openModels
    if replace:
        openModels.close([m for m in openModels.list()
                          if getattr(m, 'topography_volume', None) == volume])
    openModels.add([s])
    s.openState.xform = volume.model_transform()
    s.topography_volume = volume

    return s
    
# -----------------------------------------------------------------------------
#
def create_surface(matrix, height, transform, color, interpolate, mesh,
                   smoothing_factor, smoothing_iterations):

    if interpolate == 'cubic':
        matrix = cubic_interpolated_2d_array(matrix)
        from Matrix import multiply_matrices
        transform = multiply_matrices(transform,
                                      ((.5,0,0,0),(0,.5,0,0),(0,0,.5,0)))

    if mesh == 'isotropic':
        vertices, triangles = isotropic_surface_geometry(matrix)
    else:
        cell_diagonal_direction = mesh
        vertices, triangles = surface_geometry(matrix, cell_diagonal_direction)

    # Adjust vertex z range.
    x, z = vertices[:,0], vertices[:,2]
    zmin = z.min()
    xsize, zextent = x.max() - x.min(), z.max() - zmin
    z += -zmin
    if zextent > 0:
        if height is None:
            # Use 1/10 of grid voxels in x dimension.
            zscale = 0.1 * xsize / zextent
        else:
            # Convert zscale physical units to volume index z size.
            from Matrix import apply_matrix_without_translation, length
            zstep = length(apply_matrix_without_translation(transform, (0,0,1)))
            zscale = (height/zstep) / zextent
        z *= zscale

    # Transform vertices from index units to physical units.
    from _contour import affine_transform_vertices
    affine_transform_vertices(vertices, transform)

    if smoothing_factor != 0 and smoothing_iterations > 0:
        from _surface import smooth_vertex_positions
        smooth_vertex_positions(vertices, triangles,
                                smoothing_factor, smoothing_iterations)

    from _surface import SurfaceModel
    sm = SurfaceModel()
    p = sm.addPiece(vertices, triangles, color)
        
    return sm

# -----------------------------------------------------------------------------
#
def surface_geometry(matrix, cell_diagonal_direction):

    vertices = surface_vertices(matrix)
    grid_size = tuple(reversed(matrix.shape))
    triangles = surface_triangles(grid_size, cell_diagonal_direction)
    return vertices, triangles
    
# -----------------------------------------------------------------------------
#
def surface_vertices(data):

    ysize, xsize = data.shape
    from numpy import zeros, reshape, float32
    vgrid = zeros((ysize, xsize, 3), float32)
    vgrid[:,:,2] = data
    for j in range(ysize):
        vgrid[j,:,1] = j
    for i in range(xsize):
        vgrid[:,i,0] = i
    vertices = reshape(vgrid, (xsize*ysize, 3))
    return vertices
    
# -----------------------------------------------------------------------------
#
def surface_triangles(grid_size, cell_diagonal_direction = 'slash'):

    xsize, ysize = grid_size
    from numpy import zeros, intc, arange, add, reshape, array
    tgrid = zeros((xsize*ysize, 6), intc)
    i = arange(0, xsize*ysize)
    for k in range(6):
        tgrid[:,k] = i
    if cell_diagonal_direction == 'slash':
        add(tgrid[:,1], 1, tgrid[:,1])
        add(tgrid[:,2], xsize+1, tgrid[:,2])
        add(tgrid[:,4], xsize+1, tgrid[:,4])
        add(tgrid[:,5], xsize, tgrid[:,5])
    else:
        add(tgrid[:,1], 1, tgrid[:,1])
        add(tgrid[:,2], xsize, tgrid[:,2])
        add(tgrid[:,3], xsize, tgrid[:,3])
        add(tgrid[:,4], 1, tgrid[:,4])
        add(tgrid[:,5], xsize+1, tgrid[:,5])
    tgrid = reshape(tgrid, (ysize, xsize, 6))
    tgrid = array(tgrid[:ysize-1, :xsize-1, :])
    triangles = reshape(tgrid, (2*(ysize-1)*(xsize-1),3))
    return triangles

# -----------------------------------------------------------------------------
#
def isotropic_surface_geometry(matrix):

    vertices = isotropic_surface_vertices(matrix)
    grid_size = tuple(reversed(matrix.shape))
    triangles = isotropic_surface_triangles(grid_size)
    return vertices, triangles

# -----------------------------------------------------------------------------
# Include midpoint of every cell.
#
def isotropic_surface_vertices(data):

    ysize, xsize = data.shape
    gsize = ysize*xsize
    msize = (ysize-1)*(xsize-1)
    from numpy import zeros, reshape, add, multiply, float32
    v = zeros((gsize+msize,3), float32)

    # Create grid point vertices
    vg = reshape(v[:gsize,:], (ysize, xsize, 3))
    vg[:,:,2] = data
    for j in range(ysize):
        vg[j,:,1] = j
    for i in range(xsize):
        vg[:,i,0] = i

    # Create cell midpoint vertices
    mg = reshape(v[gsize:,:], (ysize-1, xsize-1, 3))
    mg[:,:,:2] = vg[:ysize-1,:xsize-1,:2]
    add(mg[:,:,:2], .5, mg[:,:,:2])
    mz = mg[:,:,2]
    add(mz, data[:ysize-1,:xsize-1], mz)
    add(mz, data[1:ysize,:xsize-1], mz)
    add(mz, data[:ysize-1,1:xsize], mz)
    add(mz, data[1:ysize,1:xsize], mz)
    multiply(mz, .25, mz)
    
    return v
    
# -----------------------------------------------------------------------------
# Use midpoint of every cell.
#
def isotropic_surface_triangles(grid_size):

    xsize, ysize = grid_size
    gsize = ysize*xsize
    from numpy import zeros, intc, reshape
    t = zeros((4*(ysize-1)*(xsize-1),3), intc)

    # Each cell is divided into 4 triangles using cell midpoint
    tg = reshape(t, (ysize-1, xsize-1, 12))
    tg[:,:,::3] += gsize
    for i in range(xsize-1):
        tg[:,i,0] += i          # Bottom triangle
        tg[:,i,1] += i
        tg[:,i,2] += i+1
        tg[:,i,3] += i          # Right triangle
        tg[:,i,4] += i+1
        tg[:,i,5] += i+1
        tg[:,i,6] += i          # Top triangle
        tg[:,i,7] += i+1
        tg[:,i,8] += i
        tg[:,i,9] += i          # Left triangle
        tg[:,i,10] += i
        tg[:,i,11] += i
    for j in range(ysize-1):
        tg[j,:,0] += j*(xsize-1)
        tg[j,:,1] += j*xsize
        tg[j,:,2] += j*xsize
        tg[j,:,3] += j*(xsize-1)
        tg[j,:,4] += j*xsize
        tg[j,:,5] += (j+1)*xsize
        tg[j,:,6] += j*(xsize-1)
        tg[j,:,7] += (j+1)*xsize
        tg[j,:,8] += (j+1)*xsize
        tg[j,:,9] += j*(xsize-1)
        tg[j,:,10] += (j+1)*xsize
        tg[j,:,11] += j*xsize

    return t

# -----------------------------------------------------------------------------
#
def cubic_interpolated_2d_array(matrix):

    new_size = map(lambda n: 2*n-1, matrix.shape)
    from numpy import zeros, float32
    new_matrix = zeros(new_size, float32)
    new_matrix[::2,::2] = matrix
    temp = zeros(max(matrix.shape), float32)
    for r in range(matrix.shape[0]):
        cubic_interpolate_1d_array(new_matrix[2*r, :], temp)
    for c in range(new_matrix.shape[1]):
        cubic_interpolate_1d_array(new_matrix[:,c], temp)

    return new_matrix

# -----------------------------------------------------------------------------
# Even elements of array are cubic interpolated to set odd elements.
#
def cubic_interpolate_1d_array(array, temp):

    from numpy import multiply, add
    a = (-1.0/16, 9.0/16, 9.0/16, -1.0/16)
    ae = array[::2]
    n = ae.shape[0]
    ao = array[3:-3:2]
    t = temp[:ao.shape[0]]
    for k in range(4):
        multiply(ae[k:n-3+k], a[k], t)
        add(ao, t, ao)

    # Quadratic interpolation for end positions
    c = (3.0/8, 6.0/8, -1.0/8)
    array[1] = c[0]*array[0] + c[1]*array[2] + c[2]*array[4]
    array[-2] = c[0]*array[-1] + c[1]*array[-3] + c[2]*array[-5]
        
# -----------------------------------------------------------------------------
#
def value_colors(values, colormap):

    dmin = min(values)
    dmax = max(values)
    drange = dmax - dmin
    cmap = list(colormap)
    cmap.sort()
    cvalues = map(lambda vc: dmin + drange*vc[0], cmap)
    colors = map(lambda vc: vc[1], cmap)
    above_color = colors[-1]
    below_color = colors[0]
    import SurfaceColor
    rgba = SurfaceColor.interpolate_colormap(values, cvalues, colors,
                                             above_color, below_color)
    return rgba
    
# -----------------------------------------------------------------------------
#
def colormap_surface(model, normal, colormap):

    for p in model.surfacePieces:
        varray, tarray = p.geometry
        from numpy import inner
        heights = inner(varray, normal)
        rgba = value_colors(heights, colormap)
        p.vertexColors = rgba
    
# -----------------------------------------------------------------------------
#
def rainbow_colormap(invert = False):
    
    red = (.7, 0, 0, 1)
    yellow = (.7, .7, 0, 1)
    green = (0, .7, 0, 1)
    cyan = (0, .7, .7, 1)
    blue = (0, 0, .7, 1)
    gray = (.7, .7, .7, 1)
    colormap = ((0, red), (.25, yellow), (.5, green), (.75, cyan), (1, blue))
    if invert:
        colormap = [(1-v,c) for v,c in colormap]
    return colormap
