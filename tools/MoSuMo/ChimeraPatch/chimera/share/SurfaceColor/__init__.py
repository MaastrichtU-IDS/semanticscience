# -----------------------------------------------------------------------------
# All color arguments are rgba 4-tuples.
#
class Color_Map:

    def __init__(self, data_values, colors,
                 color_above_value_range = None,
                 color_below_value_range = None,
                 color_no_value= None):

        self.data_values = data_values
        self.colors = colors

        if color_above_value_range == None:
            color_above_value_range = colors[-1]
        if color_below_value_range == None:
            color_below_value_range = colors[0]
        if color_no_value == None:
            color_no_value = (.5,.5,.5,1)

        self.color_above_value_range = color_above_value_range
        self.color_below_value_range = color_below_value_range
        self.color_no_value = color_no_value

# -----------------------------------------------------------------------------
#
gui_palette_names = {
    'Rainbow': 'rainbow',
    'Gray': 'grayscale',
    'Red-Blue': 'red-white-blue',
    'Blue-Red': 'blue-white-red',
    'Cyan-Maroon': 'cyan-white-maroon',
    }
standard_color_palettes = {
    'rainbow': ((1,0,0,1), (1,1,0,1), (0,1,0,1), (0,1,1,1), (0,0,1,1)),
    'grayscale': ((0,0,0,1), (1,1,1,1)),
    'red-white-blue': ((1,0,0,1), (1,1,1,1), (0,0,1,1)),
    'blue-white-red': ((0,0,1,1), (1,1,1,1), (1,0,0,1)),
    'cyan-white-maroon': ((0.059,0.78,0.81,1), (1,1,1,1), (0.62,0.125,0.37,1)),
    }

# -----------------------------------------------------------------------------
# Color a surface using a coloring function.  The color function takes an
# n by 3 NumPy array of floats and returns an n by 4 array specifying the
# point colors as red, green, blue, and alpha components in [0,1].
#
def color_surface(model, color_source, caps_only, auto_update,
                  include_outline_boxes = False):

    # Turn off coloring of main surface in case where "caps only" was
    # previously off and is now turned on.
    stop_coloring_surface(model)

    if auto_update:
        color_updater.auto_recolor(model, color_source, caps_only)

    plist = model.surfacePieces
    if caps_only:
        import SurfaceCap
        plist = [p for p in plist if SurfaceCap.is_surface_cap(p)]
    if not include_outline_boxes:
        plist = [p for p in plist if not hasattr(p, 'outline_box')]
    color_source.color_surface_pieces(plist)

# -------------------------------------------------------------------------
#
def texture_surface_piece(p, t, txf, border_color, offset = 0):

    p.textureId = t.texture_id()
    p.useTextureTransparency = ('a' in t.color_mode)
    p.textureModulationColor = t.modulation_rgba()
    p.textureBorderColor = border_color
    va = offset_vertices(p, offset)
    s2tc = t.texture_matrix()
    p2s = p.model.openState.xform
    p2s.premultiply(txf.inverse())
    import Matrix
    p2tc = Matrix.multiply_matrices(s2tc, Matrix.xform_matrix(p2s))
    import _contour
    _contour.affine_transform_vertices(va, p2tc)
    p.textureCoordinates = va
    p.using_surface_coloring = True

# -----------------------------------------------------------------------------
# Calculate range of surface values.  The value range function takes an
# n by 3 NumPy array of floats and returns a min and max value.
#
def surface_value_range(model, value_range_function, caps_only,
                        include_outline_boxes = False):

    vrange = (None, None)
    plist = model.surfacePieces
    if caps_only:
        import SurfaceCap
        plist = [p for p in plist if SurfaceCap.is_surface_cap(p)]
    if not include_outline_boxes:
        plist = [p for p in plist if not hasattr(p, 'outline_box')]
    for p in plist:
        grange = value_range_function(p)
        vrange = combine_min_max(vrange, grange)
    return vrange
    
# -----------------------------------------------------------------------------
#
def combine_min_max(min_max_1, min_max_2):

    if tuple(min_max_1) == (None, None):
        return min_max_2
    elif tuple(min_max_2) == (None, None):
        return min_max_1
    return (min((min_max_1[0], min_max_2[0])),
            max((min_max_1[1], min_max_2[1])))

# -----------------------------------------------------------------------------
# Colors must be rgba tuples.
#
def color_by_volume(surface, volume, values, value_colors,
                    color_above = None, color_below = None,
                    color_outside = None,
                    caps_only = False, auto_update = False):

    cmap = Color_Map(values, value_colors,
                     color_above, color_below, color_outside)
    vcolor = Volume_Color()
    vcolor.set_volume(volume)
    vcolor.set_colormap(cmap)
    color_surface(surface, vcolor, caps_only, auto_update)

# -----------------------------------------------------------------------------
#
class Volume_Color:

    menu_name = 'volume data value'
    volume_name = 'volume'
    uses_volume_data = True
    uses_origin = False
    uses_axis = False

    def __init__(self):

        self.volume = None            # VolumeViewer Volume object
        self.colormap = None
        self.offset = 0
        self.per_pixel_coloring = False
        self.solid = None             # Manages 3D texture

    # -------------------------------------------------------------------------
    #
    def set_volume(self, volume):

        self.volume = volume

        from chimera import addModelClosedCallback
        addModelClosedCallback(volume, self.volume_closed_cb)

    # -------------------------------------------------------------------------
    #
    def set_colormap(self, colormap):

        self.colormap = colormap
        self.set_texture_colormap()

    # -------------------------------------------------------------------------
    #
    def color_surface_pieces(self, plist):

        t = self.texture()
        if t:
            txf = self.volume.openState.xform
            border_color = self.colormap.color_no_value
            for p in plist:
                texture_surface_piece(p, t, txf, border_color, self.offset)
        else:
            for p in plist:
                p.vertexColors = self.vertex_colors(p)
                p.using_surface_coloring = True
        
    # -------------------------------------------------------------------------
    #
    def vertex_colors(self, surface_piece):

        values, outside = self.volume_values(surface_piece)
        cmap = self.colormap

        #--------------Start of Alex's Code-----------------------------------
    	import makeMeshes
    	makeMeshes.printVertices(self)
	#--------------end of Alex's Code-----------------------------------

        rgba = interpolate_colormap(values, cmap.data_values, cmap.colors,
                                    cmap.color_above_value_range,
                                    cmap.color_below_value_range)
        if len(outside) > 0:
            set_outside_volume_colors(outside, cmap.color_no_value, rgba)

        return rgba
        
    # -------------------------------------------------------------------------
    #
    def value_range(self, surface_piece):

        if self.volume is None:
            return (None, None)

        values, outside = self.volume_values(surface_piece)
        v = inside_values(values, outside)
        return array_value_range(v)
        
    # -------------------------------------------------------------------------
    #
    def volume_values(self, surface_piece):

        p = surface_piece
        vertex_xform = p.model.openState.xform
        if isinstance(self.offset, (tuple, list)):
            # Average values from several offsets.
            val = None
            out = set()
            for o in self.offset:
                vertices = offset_vertices(p, o)
                values, outside = self.vertex_values(vertices, vertex_xform)
                if val is None:
                    val = values
                else:
                    val += values
                out.update(set(outside))
            val *= 1.0/len(self.offset)
            values = val
            outside = list(out)
        else:
            # Single offset
            vertices = offset_vertices(p, self.offset)
            values, outside = self.vertex_values(vertices, vertex_xform)

        return values, outside

    # -------------------------------------------------------------------------
    #
    def vertex_values(self, vertices, vertex_xform):

        v = self.volume
        values, outside = v.interpolated_values(vertices, vertex_xform,
                                                out_of_bounds_list = True)
        return values, outside

    # -------------------------------------------------------------------------
    #
    def texture(self):

        if not self.per_pixel_coloring:
            return None
        if isinstance(self.offset, (tuple, list)):
            return None
        if self.solid is None:
            self.create_3d_texture()
        t = self.solid.volume
        if t.texture_id() == 0:
            return None
        return t

    # -------------------------------------------------------------------------
    #
    def create_3d_texture(self):

        v = self.volume
        name = v.name + ' texture'
        matrix = v.full_matrix()
        matrix_id = 0
        transform = v.matrix_indices_to_xyz_transform(step = 1,
                                                      subregion = 'all')
        from VolumeViewer import solid
        s = solid.Solid(name, matrix, matrix_id, transform)
        self.solid = s
        s.set_options(color_mode = 'auto8',
                      projection_mode = '3d',
                      dim_transparent_voxels = True,
                      bt_correction = False,
                      minimal_texture_memory = False,
                      maximum_intensity_projection = False,
                      linear_interpolation = True,
                      show_outline_box = False,
                      outline_box_rgb = (1,1,1),
                      outline_box_linewidth = 0)
        self.set_texture_colormap()
        return s

    # -------------------------------------------------------------------------
    #
    def set_texture_colormap(self):

        cmap = self.colormap
        s = self.solid
        if cmap and s:
            tfunc = map(lambda v,c: (v,1) + tuple(c),
                        cmap.data_values, cmap.colors)
            s.set_colormap(tfunc, 1, None, clamp = True)
            s.update_model(open = False)
            
    # -------------------------------------------------------------------------
    #
    def volume_closed_cb(self, volume):

        self.volume = None
        
    # -------------------------------------------------------------------------
    #
    def closed(self):

        return self.volume is None

# -----------------------------------------------------------------------------
#
class Electrostatic_Color(Volume_Color):

    menu_name = 'electrostatic potential'
    volume_name = 'potential'

# -----------------------------------------------------------------------------
#
class Gradient_Color(Volume_Color):

    menu_name ='volume data gradient norm'

    def vertex_values(self, vertices, vertex_xform):

        v = self.volume
        gradients, outside = v.interpolated_gradients(vertices, vertex_xform,
                                                      out_of_bounds_list = True)
        # Compute gradient norms.
        from numpy import multiply, sum, sqrt
        multiply(gradients, gradients, gradients)
        gnorms2 = sum(gradients, axis=1)
        gnorms = sqrt(gnorms2)
        
        return gnorms, outside

    # -------------------------------------------------------------------------
    #
    def color_surface_pieces(self, plist):

        for p in plist:
            p.vertexColors = self.vertex_colors(p)
            p.using_surface_coloring = True
    
# -----------------------------------------------------------------------------
#
def interpolate_colormap(values, color_data_values, rgba_colors,
                         rgba_above_value_range, rgba_below_value_range):

    from _interpolate import interpolate_colormap
    rgba = interpolate_colormap(values, color_data_values, rgba_colors,
                                rgba_above_value_range, rgba_below_value_range)
    return rgba
            
# -----------------------------------------------------------------------------
#
def set_outside_volume_colors(outside, rgba_outside_volume, rgba):

    import _interpolate
    _interpolate.set_outside_volume_colors(outside, rgba_outside_volume, rgba)
            
# -----------------------------------------------------------------------------
#
def inside_values(values, outside):
        
    if len(outside) == 0:
        return values
    
    n = len(values)
    if len(outside) == n:
        return ()

    from numpy import zeros, int, array, put, subtract, nonzero, take
    m = zeros(n, int)
    one = array(1, int)
    put(m, outside, one)
    subtract(m, one, m)
    inside = nonzero(m)[0]
    v = take(values, inside, axis=0)
    return v
    
# -----------------------------------------------------------------------------
#
def array_value_range(a):

    if len(a) == 0:
        return (None, None)
    from numpy import minimum, maximum
    r = (minimum.reduce(a), maximum.reduce(a))
    return r
    
# -----------------------------------------------------------------------------
#
def offset_vertices(p, offset):

    varray, tarray = p.geometry
    if offset == 0:
        return varray
    vo = offset * p.normals
    vo += varray
    return vo
    
# -----------------------------------------------------------------------------
#
class Geometry_Color:

    menu_name = 'distance'
    uses_volume_data = False
    uses_origin = True
    uses_axis = True

    def __init__(self):

        self.colormap = None
        self.origin = (0,0,0)
        self.axis = (0,0,1)

    # -------------------------------------------------------------------------
    #
    def set_origin(self, origin):
        self.origin = tuple(origin)
    def set_axis(self, axis):
        self.axis = tuple(axis)
        
    # -------------------------------------------------------------------------
    #
    def set_colormap(self, colormap):

        self.colormap = colormap

    # -------------------------------------------------------------------------
    #
    def color_surface_pieces(self, plist):

        for p in plist:
            p.vertexColors = self.vertex_colors(p)
            p.using_surface_coloring = True

    # -------------------------------------------------------------------------
    #
    def vertex_colors(self, surface_piece):

        p = surface_piece
        vertices, tarray = p.geometry
        vertex_xform = p.model.openState.xform
        values = self.values(vertices)
        cmap = self.colormap
        rgba = interpolate_colormap(values, cmap.data_values, cmap.colors,
                                    cmap.color_above_value_range,
                                    cmap.color_below_value_range)
        return rgba
        
    # -------------------------------------------------------------------------
    #
    def value_range(self, surface_piece):

        vertices, tarray = surface_piece.geometry
        vertex_xform = surface_piece.model.openState.xform
        v = self.values(vertices)
        return array_value_range(v)
        
    # -------------------------------------------------------------------------
    #
    def closed(self):

        return False
    
# -----------------------------------------------------------------------------
#
class Height_Color(Geometry_Color):

    menu_name = 'height'
        
    # -------------------------------------------------------------------------
    #
    def values(self, vertices):

        d = distances_along_axis(vertices, self.origin, self.axis)
        return d

# -----------------------------------------------------------------------------
# Given n by 3 array of points and an axis return an array of distances
# of points along the axis.
#
def distances_along_axis(points, origin, axis):

    from numpy import zeros, single as floatc
    d = zeros(len(points), floatc)
        
    import _distances
    _distances.distances_parallel_to_axis(points, origin, axis, d)

    return d
    
# -----------------------------------------------------------------------------
#
class Radial_Color(Geometry_Color):

    menu_name = 'radius'
    uses_axis = False
        
    # -------------------------------------------------------------------------
    #
    def values(self, vertices):

        d = distances_from_origin(vertices, self.origin)
        return d

# -----------------------------------------------------------------------------
# Given n by 3 array of points and an origin return an array of distances
# of points from origin.
#
def distances_from_origin(points, origin):

    from numpy import zeros, single as floatc
    d = zeros(len(points), floatc)
        
    import _distances
    _distances.distances_from_origin(points, origin, d)

    return d

# -----------------------------------------------------------------------------
#
class Cylinder_Color(Geometry_Color):

    menu_name = 'cylinder radius'

    def values(self, vertices):

        d = distances_from_axis(vertices, self.origin, self.axis)
        return d

# -----------------------------------------------------------------------------
# Given n by 3 array of points and an axis return an array of distances
# of points from axis.
#
def distances_from_axis(points, origin, axis):

    from numpy import zeros, single as floatc
    d = zeros(len(points), floatc)
        
    import _distances
    _distances.distances_perpendicular_to_axis(points, origin, axis, d)

    return d
        
# -----------------------------------------------------------------------------
# Stop coloring a surface using a coloring function.
#
def stop_coloring_surface(model):
    
    color_updater.stop_coloring(model)

    import SurfaceCap
    cm = SurfaceCap.cap_model(model, create = False)
    if cm and cm != model:
        color_updater.stop_coloring(cm)
            
# -----------------------------------------------------------------------------
#
class Color_Updater:

    def __init__(self):

        self.models = {}

        import SimpleSession
        import chimera
        chimera.triggers.addHandler(SimpleSession.SAVE_SESSION,
                                    self.save_session_cb, None)
            
    # -------------------------------------------------------------------------
    #
    def auto_recolor(self, model, color_source, caps_only):

        add_callback = not self.models.has_key(model)
        self.models[model] = (color_source, caps_only)
        from Surface import set_coloring_method
        set_coloring_method('surface color', model, self.stop_coloring)
        if add_callback:
            model.addGeometryChangedCallback(self.surface_changed_cb)
            from chimera import addModelClosedCallback
            addModelClosedCallback(model, self.model_closed_cb)
            
    # -------------------------------------------------------------------------
    #
    def stop_coloring(self, model, erase_coloring = True):

        if not model in self.models:
            return

        del self.models[model]
        model.removeGeometryChangedCallback(self.surface_changed_cb)

        # Remove per-vertex coloring.
        plist = [p for p in model.surfacePieces
                 if hasattr(p, 'using_surface_coloring')
                 and p.using_surface_coloring]
        for p in plist:
            if erase_coloring:
                p.vertexColors = None
                p.textureId = 0
                p.textureCoordinates = None
            p.using_surface_coloring = False
            
    # -------------------------------------------------------------------------
    # p is SurfacePiece.
    #
    def surface_changed_cb(self, p, detail):

        if detail == 'removed':
            return

        m = p.model
        (color_source, caps_only) = self.models[m]
        if color_source.closed():
            self.stop_coloring(m)
            return
        if caps_only:
            import SurfaceCap
            if not SurfaceCap.is_surface_cap(p):
                return
        include_outline_boxes = False
        if not include_outline_boxes and hasattr(p, 'outline_box'):
            return
        color_source.color_surface_pieces([p])

    # -------------------------------------------------------------------------
    #
    def model_closed_cb(self, model):

        if model in self.models:
            del self.models[model]
            
    # -------------------------------------------------------------------------
    #
    def surface_coloring(self, surface):

        mtable = self.models
        if surface in mtable:
            color_source, caps_only = mtable[surface]
            if color_source.closed():
                self.stop_coloring(surface, erase_coloring = False)
            else:
                return color_source, caps_only
        return None, None
            
    # -------------------------------------------------------------------------
    #
    def save_session_cb(self, trigger, x, file):

        import session
        session.save_surface_color_state(self.models, file)

# -----------------------------------------------------------------------------
#
def colorable_surface_models():

    from chimera import openModels
    from _surface import SurfaceModel
    mlist = openModels.list(modelTypes = [SurfaceModel])
    from SurfaceCap import is_surface_cap
    mlist = [m for m in mlist if not is_surface_cap(m)]

    return mlist
            
# -----------------------------------------------------------------------------
#
def surface_coloring(surface):

    return color_updater.surface_coloring(surface)

# -----------------------------------------------------------------------------
#
coloring_methods = (Radial_Color, Cylinder_Color, Height_Color,
                    Electrostatic_Color, Volume_Color, Gradient_Color,
                    )

# -----------------------------------------------------------------------------
#
color_updater = Color_Updater()
