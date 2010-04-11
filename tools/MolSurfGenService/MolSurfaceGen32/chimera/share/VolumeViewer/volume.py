# -----------------------------------------------------------------------------
#
class Volume_Manager:

  def __init__(self):
    
    self.data_regions = []
    self.data_to_regions = {}

    import defaultsettings as d
    self.default_settings = ds = d.Volume_Viewer_Default_Settings()

    # Set default data cache size.
    from VolumeData import data_cache
    data_cache.resize(ds['data_cache_size'] * (2**20))

    self.open_callbacks = []
    self.close_callbacks = []
    self.save_session_callbacks = []

    from chimera import openModels as om
    self.open_handler = om.addAddHandler(self.open_models_cb, None)

    from chimera import triggers, CLOSE_SESSION
    from SimpleSession import SAVE_SESSION
    triggers.addHandler(SAVE_SESSION, self.save_session_cb, None)
    triggers.addHandler(CLOSE_SESSION, self.close_session_cb, None)

  # ---------------------------------------------------------------------------
  #
  def add_volume_opened_callback(self, volume_opened_cb):

    self.open_callbacks.append(volume_opened_cb)

  # ---------------------------------------------------------------------------
  #
  def add_volume_closed_callback(self, volume_closed_cb):

    self.close_callbacks.append(volume_closed_cb)

  # ---------------------------------------------------------------------------
  # Callbacks are called after data has be saved.
  # State saved via a callback registered with this routine is restored
  # only after volume data has been restored.
  #
  def add_session_save_callback(self, save_session):

    self.save_session_callbacks.append(save_session)

  # ---------------------------------------------------------------------------
  #
  def open_models_cb(self, trigger_name, args, models):

    for v in models:
      if isinstance(v, Volume):
        self.add_volume(v)
      
  # ---------------------------------------------------------------------------
  #
  def add_volume(self, v):

    self.data_regions.append(v)

    data = v.data

    d2r = self.data_to_regions
    if not data in d2r:
      d2r[data] = []
    d2r[data].append(v)

    import chimera
    chimera.addModelClosedCallback(v, self.model_closed_cb)

    for cb in self.open_callbacks:
      cb(v)
    
  # ---------------------------------------------------------------------------
  #
  def set_initial_volume_color(self, v):

    ds = self.default_settings
    if ds['use_initial_colors']:
      n = len(volume_list())
      if v in volume_list():
        n -= 1
      icolors = ds['initial_colors']
      rgba = icolors[n%len(icolors)]
      v.set_parameters(default_rgba = rgba)
    
  # ---------------------------------------------------------------------------
  #
  def replace_data(self, data, new_data):

    d2r = self.data_to_regions 
    d2r[new_data] = d2r[data]
    del d2r[data]
    for dr in d2r[new_data]:
      dr.replace_data(new_data)

  # ---------------------------------------------------------------------------
  #
  def volume_list(self):

      return self.data_regions

  # ---------------------------------------------------------------------------
  #
  def regions_using_data(self, data):

    return self.data_to_regions.get(data, [])

  # ---------------------------------------------------------------------------
  #
  def data_already_opened(self, path, grid_id):

    if not path:
      return None
    
    dlist = self.data_to_regions.keys()
    for data in dlist:
      if not data.writable and data.path == path and data.grid_id == grid_id:
        return data
    return None

  # ---------------------------------------------------------------------------
  #
  def model_closed_cb(self, v):

    if v in self.data_regions:
      self.remove_volumes([v])
    
  # ---------------------------------------------------------------------------
  #
  def save_session_cb(self, trigger, x, file):

    import session
    session.save_volume_data_state(self, file)

    for cb in self.save_session_callbacks:
      cb(file)
    
  # ---------------------------------------------------------------------------
  #
  def close_session_cb(self, trigger, a1, a2):

    self.remove_volumes(self.data_regions)
      
  # ---------------------------------------------------------------------------
  #
  def remove_volumes(self, volumes):

    remove_volumes = tuple(volumes)

    for v in remove_volumes:
      index = self.data_regions.index(v)
      del self.data_regions[index]

      data = v.data
      if data is None:
        # Volume has already been closed and data attribute set to None.
        data = [d for d,vlist in self.data_to_regions.items() if v in vlist][0]
      vlist = self.data_to_regions[data]
      vlist.remove(v)
      if len(vlist) == 0:
        del self.data_to_regions[data]
        data.clear_cache()

    for cb in self.close_callbacks:
      cb(remove_volumes)

    # Close models only after removing from volume list.
    # This stops the model closed callback from recalling this routine.
    for v in remove_volumes:
      v.close()

# -----------------------------------------------------------------------------
# Decide whether a data region is small enough to show when opened.
#
def show_when_opened(data_region, show_on_open, max_voxels):

  if not show_on_open:
    return False
  
  if max_voxels == None:
    return False
  
  voxel_limit = int(max_voxels * (2 ** 20))
  ss_origin, ss_size, subsampling, ss_step = data_region.ijk_region()
  voxels = float(ss_size[0]) * float(ss_size[1]) * float(ss_size[2])

  return (voxels <= voxel_limit)

# -----------------------------------------------------------------------------
# Decide whether a data region is large enough that only a single z plane
# should be shown.
#
def show_one_plane(data_region, show_plane, min_voxels):

  if not show_plane:
    return False
  
  if min_voxels == None:
    return False
  
  voxel_limit = int(min_voxels * (2 ** 20))
  size = data_region.data.size
  voxels = float(size[0]) * float(size[1]) * float(size[2])

  return (voxels >= voxel_limit)


# -----------------------------------------------------------------------------
# Manages surface and volume display for a region of a data set.
# Holds surface and solid thresholds, color, and transparency and brightness
# factors.
#
from _surface import SurfaceModel
class Volume(SurfaceModel):

  def __init__(self, data, region = None, rendering_options = None,
               model_id = None, open_model = True, message_cb = None):

    SurfaceModel.__init__(self)
    self.data = data
    data.add_change_callback(self.data_changed_cb)

    if region is None:
      region = full_region(data.size)
    self.region = clamp_region(region, data.size)

    # C++ Model object raises an error if a unicode name is set.
    # Encode in utf-8 to get a str object that the C++ code can handle.
    self.name = utf8_string(self.data.name)

    if rendering_options is None:
      rendering_options = Rendering_Options()
    self.rendering_options = rendering_options

    self.message_cb = message_cb
    
    self.matrix_stats = None
    self.matrix_id = 1          # Incremented when shape or values change.

    rlist = Region_List()
    ijk_min, ijk_max = self.region[:2]
    rlist.insert_region(ijk_min, ijk_max)
    self.region_list = rlist

    self.representation = 'surface'

    self.solid = None
    self.keep_matrix = None

    self.display = False        # Undisplay surface

    self.initialized_thresholds = False

    # Surface display parameters
    self.surface_levels = []
    self.surface_colors = []
    self.surface_piece_list = []    # SurfacePiece graphics objects
    self.surface_brightness_factor = 1
    self.transparency_factor = 0                # for surface/mesh
    self.outline_box = Outline_Box(self)

    # Solid display parameters
    self.solid_levels = []			# list of (threshold, scale)
    self.solid_colors = []
    self.transparency_depth = 0.5               # for solid
    self.solid_brightness_factor = 1

    self.default_rgba = data.rgba

    self.change_callbacks = []

    if open_model:
      self.open_model(model_id)

    from chimera import addModelClosedCallback
    addModelClosedCallback(self, self.model_closed_cb)

    from chimera import triggers
    h = triggers.addHandler('SurfacePiece', self.surface_piece_changed_cb, None)
    self.surface_piece_change_handler = h

  # ---------------------------------------------------------------------------
  #
  def message(self, text):

    if self.message_cb:
      self.message_cb(text)
    
  # ---------------------------------------------------------------------------
  #
  def full_name(self):

    return self.name
    
  # ---------------------------------------------------------------------------
  #
  def name_with_id(self):

    if self.subid:
      sid = '#%d.%d' % (self.id, self.subid)
    else:
      sid = '#%d' % self.id
    return self.name + ' ' + sid

  # ---------------------------------------------------------------------------
  #
  def add_volume_change_callback(self, cb):

    self.change_callbacks.append(cb)

  # ---------------------------------------------------------------------------
  #
  def remove_volume_change_callback(self, cb):

    self.change_callbacks.remove(cb)
    
  # ---------------------------------------------------------------------------
  # Detect surface piece color change and display style change.
  #
  def surface_piece_changed_cb(self, trigger, unused, changes):

    change = ('color changed' in changes.reasons
              or 'display style changed' in changes.reasons)
    if not change:
      return

    if len(self.surface_piece_list) != len(self.surface_colors):
      return

    pindex = {}
    for i, p in enumerate(self.surface_piece_list):
      pindex[p] = i

    # Check if surface pieces for this volume have changed.
    ctypes = set()
    pchange = False
    for p in changes.modified:
      if p in pindex:
        i = pindex[p]
        vcolor = self.modulated_surface_color(self.surface_colors[i])
        from numpy import array, single as floatc
        if (p.color != array(vcolor, floatc)).any():
          self.surface_colors[i] = p.color
          ctypes.add('colors changed')
        pchange = True

    # Check if display style of all surface pieces has changed.
    if pchange and self.representation != 'solid':
      styles = set()
      for p in self.surface_piece_list:
        styles.add(p.displayStyle)
      if len(styles) == 1:
        pstyle = {p.Solid: 'surface', p.Mesh: 'mesh'}.get(styles.pop(), None)
        if pstyle and self.representation != pstyle:
          # TODO: Eliminate special case for 2d contour rendering.
          contour_2d = (pstyle == 'mesh' and
                        not self.rendering_options.cap_faces
                        and self.single_plane())
          if not contour_2d:
            self.set_representation(pstyle)

    # Notify about changes.
    for ctype in ctypes:
      for cb in self.change_callbacks:
        cb(self, ctype)
  
  # ---------------------------------------------------------------------------
  #
  def replace_data(self, data):

    d = self.data
    cc = (data.origin != d.origin or
          data.step != d.step or
          data.cell_angles != d.cell_angles)
    dc = self.data_changed_cb
    d.remove_change_callback(dc)
    self.data = data
    data.add_change_callback(dc)
    dc('values changed')
    if cc:
      dc('coordinates changed')
    
  # ---------------------------------------------------------------------------
  # Programatically set data region parameters.  The following keyword
  # parameters are valid.
  #
  #   surface_levels
  #   surface_colors              (rgb or rgba values)
  #   surface_brightness_factor
  #   transparency_factor
  #   solid_levels
  #   solid_colors                (rgb or rgba values)
  #   transparency_depth
  #   solid_brightness_factor
  #
  #   Any rendering option attribute names can also be used.
  #
  # The volume display is not automatically updated.  Use v.show() when
  # redisplay is desired.
  #
  def set_parameters(self, **kw):

    parameters = ('surface_levels',
                  'surface_colors',
                  'surface_brightness_factor',
                  'transparency_factor',
                  'solid_levels',
                  'solid_colors',
                  'solid_brightness_factor',
                  'transparency_depth',
                  'default_rgba',
                  )

    def rgb_to_rgba(color):
      if len(color) == 3:
        return tuple(color) + (1,)
      return color

    if 'surface_colors' in kw:
      kw['surface_colors'] = map(rgb_to_rgba, kw['surface_colors'])
    if 'solid_colors' in kw:
      kw['solid_colors'] = map(rgb_to_rgba, kw['solid_colors'])

    if ('surface_levels' in kw and
        not 'surface_colors' in kw and
        len(kw['surface_levels']) != len(self.surface_levels)):
      kw['surface_colors'] = [self.default_rgba] * len(kw['surface_levels'])
    if ('solid_levels' in kw and
        not 'solid_colors' in kw and
        len(kw['solid_levels']) != len(self.solid_colors)):
      rgba = saturate_rgba(self.default_rgba)
      kw['solid_colors'] = [rgba] * len(kw['solid_levels'])

    if 'default_rgba' in kw:
      self.default_rgba = kw['default_rgba'] = rgb_to_rgba(kw['default_rgba'])

    # Make copies of lists.
    for param in ('surface_levels', 'surface_colors',
                  'solid_levels', 'solid_colors'):
      if param in kw:
        kw[param] = list(kw[param])

    for param in parameters:
      if param in kw:
        values = kw[param]
        setattr(self, param, values)

    option_changed = False
    for k,v in kw.items():
      if k in self.rendering_options.__dict__:
        setattr(self.rendering_options, k, v)
        option_changed = True

    if 'surface_levels' in kw or 'solid_levels' in kw:
      for cb in self.change_callbacks:
        cb(self, 'thresholds changed')

    if ('surface_colors' in kw or 'solid_colors' in kw or
        'surface_brightness_factor' in kw or 'transparency_factor' in kw or
        'solid_brightness_factor' in kw or 'transparency_depth' in kw):
      for cb in self.change_callbacks:
        cb(self, 'colors changed')

    if option_changed:
      for cb in self.change_callbacks:
        cb(self, 'rendering options changed')

  # ---------------------------------------------------------------------------
  # Sets new region and optionally shows it.
  #
  def new_region(self, ijk_min = None, ijk_max = None, ijk_step = None,
                 show = True, adjust_step = True, save_in_region_queue = True):

    if ijk_min is None:
      ijk_min = self.region[0]
    if ijk_max is None:
      ijk_max = self.region[1]

    # Make bounds integers.
    from math import ceil, floor
    ijk_min = [int(ceil(x)) for x in ijk_min]
    ijk_max = [int(floor(x)) for x in ijk_max]

    # Make it lie within dota bounds.
    (ijk_min, ijk_max) = clamp_region((ijk_min, ijk_max), self.data.size)

    # Determine ijk_step.
    if ijk_step == None:
      if self.region:
        ijk_step = self.region[2]
      else:
        ijk_step = (1,1,1)
    else:
      ijk_step = [int(ceil(x)) for x in ijk_step]

    # Adjust ijk_step to meet voxel limit.
    ro = self.rendering_options
    adjusted_ijk_step = ijk_step_for_voxel_limit(ijk_min, ijk_max, ijk_step,
                                                 ro.limit_voxel_count,
                                                 ro.voxel_limit)
    if adjust_step:
      ijk_step = adjusted_ijk_step
    elif tuple(ijk_step) != tuple(adjusted_ijk_step):
      # Change automatic step adjustment voxel limit.
      vc = subarray_size(ijk_min, ijk_max, ijk_step)
      ro.voxel_limit = (1.01*vc) / (2**20)  # Mvoxels rounded up for gui value
      for cb in self.change_callbacks:
        cb(self, 'voxel limit changed')

    if save_in_region_queue:
      self.region_list.insert_region(ijk_min, ijk_max)

    region = (ijk_min, ijk_max, ijk_step)
    if self.same_region(region, self.region):
      return False

    self.region = region
    self.matrix_changed()

    for cb in self.change_callbacks:
      cb(self, 'region changed')

    if show:
      self.show()

    return True

  # ---------------------------------------------------------------------------
  #
  def is_full_region(self, region = None):

    if region is None:
      region = self.region
    elif region == 'all':
      return True
    ijk_min, ijk_max,ijk_step = region
    dmax = tuple([s-1 for s in self.data.size])
    full = (tuple(ijk_min) == (0,0,0) and
            tuple(ijk_max) == dmax and
            tuple(ijk_step) == (1,1,1))
    return full

  # ---------------------------------------------------------------------------
  # Either data values or subregion has changed.
  #
  def matrix_changed(self):

    self.matrix_stats = None
    self.matrix_id += 1
      
  # ---------------------------------------------------------------------------
  # Handle ijk_min, ijk_max, ijk_step as lists or tuples.
  #
  def same_region(self, r1, r2):

    for i in range(3):
      if tuple(r1[i]) != tuple(r2[i]):
        return False
    return True
    
  # ---------------------------------------------------------------------------
  #
  def has_thresholds(self):

    return len(self.surface_levels) > 0 and len(self.solid_levels) > 0

  # ---------------------------------------------------------------------------
  # Returns True if thresholds are changed.
  #
  def initialize_thresholds(self, first_time_only = True,
                            vfrac = (0.01, 0.90), mfrac = None,
                            replace = False):

    if not replace:
      if first_time_only and self.initialized_thresholds:
        return False
      if self.has_thresholds():
        self.initialized_thresholds = True
        return False

    from chimera import CancelOperation
    try:
      s = self.matrix_value_statistics()
    except CancelOperation:
      return False

    polar = (hasattr(self.data, 'polar_values') and self.data.polar_values)

    if replace or len(self.surface_levels) == 0:
      if mfrac is None:
        v = s.rank_data_value(1-vfrac[0])
      else:
        v = s.mass_rank_data_value(1-mfrac[0])
      rgba = self.default_rgba
      if polar:
        self.surface_levels = [-v,v]
        neg_rgba = tuple([1-c for c in rgba[:3]] + [rgba[3]])
        self.surface_colors = [neg_rgba,rgba]
      else:
        self.surface_levels = [v]
        self.surface_colors = [rgba]

    if replace or len(self.solid_levels) == 0:
      if mfrac is None:
        vlow = s.rank_data_value(1-vfrac[1])
        vmid = s.rank_data_value(1-vfrac[0])
      else:
        vlow = s.mass_rank_data_value(1-mfrac[1])
        vmid = s.mass_rank_data_value(1-mfrac[0])
      vmax = s.maximum
      rgba = saturate_rgba(self.default_rgba)
      if polar:
        self.solid_levels = ((s.minimum,1), (max(-vmid,s.minimum),0.99), (0,0),
                             (0,0), (vmid,0.99), (vmax,1))
        neg_rgba = tuple([1-c for c in rgba[:3]] + [rgba[3]])
        self.solid_colors = (neg_rgba,neg_rgba,neg_rgba, rgba,rgba,rgba)
      else:
        if vlow < vmid and vmid < vmax:
          self.solid_levels = ((vlow,0), (vmid,0.99), (vmax,1))
        else:
          self.solid_levels = ((vlow,0), (vmax,1))
        self.solid_colors = [rgba]*len(self.solid_levels)

    self.initialized_thresholds = True

    for cb in self.change_callbacks:
      cb(self, 'thresholds changed')

    return True

  # ---------------------------------------------------------------------------
  #
  def set_representation(self, rep):

    if rep != self.representation:
      self.representation = rep
      for cb in self.change_callbacks:
        cb(self, 'representation changed')

  # ---------------------------------------------------------------------------
  #
  def show(self, representation = None, rendering_options = None, show = True):

    if representation:
      self.set_representation(representation)

    if rendering_options:
      self.rendering_options = rendering_options

    if show:
      # Prevent cached matrix for displayed data from being freed.
      from chimera import CancelOperation
      try:
        self.keep_matrix = self.matrix()
      except CancelOperation:
        return
      
    if self.representation == 'surface' or self.representation == 'mesh':
      self.close_solid()
      show_mesh = (self.representation == 'mesh')
      self.show_surface(show, show_mesh, self.rendering_options)
    elif self.representation == 'solid':
      self.hide_surface()
      self.show_solid(show, self.rendering_options)

    if show:
      for cb in self.change_callbacks:
        cb(self, 'displayed')

  # ---------------------------------------------------------------------------
  #
  def show_surface(self, show, show_mesh, rendering_options):

    if show:
      self.update_surface(show_mesh, rendering_options)
      self.display = True
    else:
      self.hide_surface()

  # ---------------------------------------------------------------------------
  #
  def update_surface(self, show_mesh, rendering_options):

    pieces = self.match_surface_pieces(self.surface_levels)
    self.surface_piece_list = pieces
    ro = rendering_options
    self.oneTransparentLayer = ro.one_transparent_layer
    from chimera import CancelOperation
    try:
      for k, level in enumerate(self.surface_levels):
        color = self.surface_colors[k]
        rgba = self.modulated_surface_color(color)
        self.update_surface_piece(level, rgba, show_mesh, ro, pieces[k])
    except CancelOperation:
      pass

    self.show_outline_box(ro.show_outline_box, ro.outline_box_rgb,
                          ro.outline_box_linewidth)

  # ---------------------------------------------------------------------------
  # Pair up surface pieces with contour levels.  Aim is to avoid
  # recalculating contours if a piece already exists for a contour
  # level.  Common cases are 1) no levels have changed, 2) one level
  # has changed, 3) one level added or deleted, 4) multiple levels
  # added or deleted.  Level order is typically preserved.
  #
  def match_surface_pieces(self, levels):

    smodel = self
    plist = [p for p in self.surface_piece_list if not p.__destroyed__]
    for k,level in enumerate(levels):
      if k < len(plist) and level == plist[k].contour_settings['level']:
        pass
      elif (k+1 < len(plist) and k+1 < len(levels) and
            levels[k+1] == plist[k+1].contour_settings['level']):
        pass
      elif k+1 < len(plist) and level == plist[k+1].contour_settings['level']:
        smodel.removePiece(plist[k])
        del plist[k]
      elif (k < len(plist) and k+1 < len(levels) and
            levels[k+1] == plist[k].contour_settings['level']):
        plist.insert(k, smodel.newPiece())
      elif k >= len(plist):
        plist.append(smodel.newPiece())

    while len(plist) > len(levels):
      smodel.removePiece(plist[-1])
      del plist[-1]
      
    return plist
  
  # ---------------------------------------------------------------------------
  #
  def update_surface_piece(self, level, rgba, show_mesh, rendering_options,
                           piece):

    ro = rendering_options
    p = piece

    contour_settings = {'level': level,
                        'matrix_id': self.matrix_id,
                        'transform': self.matrix_indices_to_xyz_transform(),
                        'surface_smoothing': ro.surface_smoothing,
                        'smoothing_factor': ro.smoothing_factor,
                        'smoothing_iterations': ro.smoothing_iterations,
                        'subdivide_surface': ro.subdivide_surface,
                        'subdivision_levels': ro.subdivision_levels,
                        'square_mesh': ro.square_mesh,
                        'cap_faces': ro.cap_faces,
                        'flip_normals': ro.flip_normals,
                        }
    if (not hasattr(p, 'contour_settings') or
        p.contour_settings != contour_settings):
      if self.calculate_contour_surface(level, rendering_options, p):
        p.contour_settings = contour_settings

    p.color = rgba

    # OpenGL draws nothing for degenerate triangles where two vertices are
    # identical.  For 2d contours want to see these triangles so show as mesh.
    single_plane = self.single_plane()
    contour_2d = single_plane and not ro.cap_faces

    if show_mesh or contour_2d:
      style = p.Mesh
    else:
      style = p.Solid
    p.displayStyle = style
    
    if contour_2d:  lit = False
    elif show_mesh: lit = ro.mesh_lighting
    else:           lit = True
    p.useLighting = lit

    p.twoSidedLighting = ro.two_sided_lighting

    p.lineThickness = ro.line_thickness

    p.smoothLines = ro.smooth_lines

    if ro.dim_transparency:
      bmode = p.SRC_ALPHA_DST_1_MINUS_ALPHA
    else:
      bmode = p.SRC_1_DST_1_MINUS_ALPHA
    p.transparencyBlendMode = bmode
      
  # ---------------------------------------------------------------------------
  #
  def calculate_contour_surface(self, level, rendering_options, piece):

    name = self.data.name
    self.message('Computing %s surface, level %.3g' % (name, level))

    matrix = self.matrix()

    # _contour code does not handle single data planes.
    # Handle these by stacking two planes on top of each other.
    plane_axis = [a for a in (0,1,2) if matrix.shape[a] == 1]
    for a in plane_axis:
      matrix = matrix.repeat(2, axis = a)

    ro = rendering_options

    from _contour import surface
    try:
      varray, tarray, narray = surface(matrix, level,
                                       cap_faces = ro.cap_faces,
                                       calculate_normals = True)
    except MemoryError:
      from chimera.replyobj import warning
      warning('Ran out of memory contouring at level %.3g.\n' % level +
              'Try a higher contour level.')
      return False

    for a in plane_axis:
      varray[:,2-a] = 0
    
    if ro.flip_normals and level < 0:
      from _surface import invert_vertex_normals
      invert_vertex_normals(narray, tarray)

    # Preserve triangle vertex traversal direction about normal.
    transform = self.matrix_indices_to_xyz_transform()
    from Matrix import determinant
    if determinant(transform) < 0:
      from _contour import reverse_triangle_vertex_order
      reverse_triangle_vertex_order(tarray)

    if ro.subdivide_surface:
      from _surface import subdivide_triangles
      for level in range(ro.subdivision_levels):
        varray, tarray, narray = subdivide_triangles(varray, tarray, narray)

    if ro.square_mesh:
      from _surface import principle_plane_edges
      hidden_edges = principle_plane_edges(varray, tarray)

    if ro.surface_smoothing:
      sf, si = ro.smoothing_factor, ro.smoothing_iterations
      from _surface import smooth_vertex_positions
      smooth_vertex_positions(varray, tarray, sf, si)
      smooth_vertex_positions(narray, tarray, sf, si)

    # Transform vertices and normals
    from _contour import affine_transform_vertices
    affine_transform_vertices(varray, transform)
    from Matrix import invert_matrix, transpose_matrix, zero_translation
    tf = zero_translation(transpose_matrix(invert_matrix(transform)))
    affine_transform_vertices(narray, tf)
    from Matrix import normalize_vectors
    normalize_vectors(narray)

    self.message('Making %s surface with %d triangles' % (name, len(tarray)))

    p = piece
    p.geometry = varray, tarray
    p.normals = narray

    if ro.square_mesh:
      p.setEdgeMask(hidden_edges)
    else:
      p.setEdgeMask(None)

    self.message('')

    return True
    
  # ---------------------------------------------------------------------------
  #
  def remove_surfaces(self):

    for p in self.surface_piece_list:
      if not p.__destroyed__:
        self.removePiece(p)
    self.surface_piece_list = []
    
  # ---------------------------------------------------------------------------
  #
  def open_model(self, model_id):

    from chimera import openModels
    if model_id == None:
      m_id = m_subid = openModels.Default
    elif isinstance(model_id, int):
      m_id = model_id
      m_subid = openModels.Default
    else:
      m_id, m_subid = model_id
    openModels.add([self], baseId = m_id, subid = m_subid)

  # ---------------------------------------------------------------------------
  #
  def show_outline_box(self, show, rgb, linewidth):
    
    if show and rgb:
      from VolumeData import box_corners
      ijk_corners = box_corners(*self.ijk_bounds())
      corners = [self.data.ijk_to_xyz(ijk) for ijk in ijk_corners]
      self.outline_box.show(corners, rgb, linewidth)
    else:
      self.outline_box.erase_box()

  # ---------------------------------------------------------------------------
  #
  def show_solid(self, show, rendering_options):

    if show:
      self.update_solid(rendering_options)
    else:
      self.close_solid()

  # ---------------------------------------------------------------------------
  #
  def update_solid(self, rendering_options):

    from chimera import CancelOperation
    try:
      m = self.matrix()
    except CancelOperation:
      return

    s = self.solid
    if s is None:
      s = self.make_solid()
      self.solid = s

    ro = rendering_options
    s.set_options(ro.color_mode, ro.projection_mode,
                  ro.dim_transparent_voxels,
                  ro.bt_correction, ro.minimal_texture_memory,
                  ro.maximum_intensity_projection, ro.linear_interpolation,
                  ro.show_outline_box, ro.outline_box_rgb,
                  ro.outline_box_linewidth)

    s.set_transform(self.matrix_indices_to_xyz_transform())


    tf = self.transfer_function()
    s.set_colormap(tf, self.solid_brightness_factor, self.transparency_depth)
    s.set_matrix(m, self.matrix_id)

    s.update_model()

  # ---------------------------------------------------------------------------
  #
  def make_solid(self):

    import solid
    name = self.name + ' solid'
    matrix = self.matrix()

    transform = self.matrix_indices_to_xyz_transform()
    align = self.surface_model()
    s = solid.Solid(name, matrix, self.matrix_id, transform, align, self.message)
    if hasattr(self, 'mask_colors'):
      s.mask_colors = self.mask_colors
    return s

  # ---------------------------------------------------------------------------
  #
  def shown(self):

    for m in self.models():
      if m.display:
        return True
    return False

  # ---------------------------------------------------------------------------
  #
  def copy(self):

    v = volume_from_grid_data(self.data, self.representation,
                              show_data = False, show_dialog = False)
    v.copy_settings_from(self)
    return v

  # ---------------------------------------------------------------------------
  #
  def copy_settings_from(self, v,
                         copy_style = True,
                         copy_thresholds = True,
                         copy_colors = True,
                         copy_rendering_options = True,
                         copy_region = True,
                         copy_xform = True,
                         copy_active = True,
                         copy_zone = True):

    if copy_style:
      # Copy display style
      self.set_representation(v.representation)

    if copy_thresholds:
      # Copy thresholds
      self.set_parameters(
        surface_levels = v.surface_levels,
        solid_levels = v.solid_levels,
        )
    if copy_colors:
      # Copy colors
      self.set_parameters(
        surface_colors = v.surface_colors,
        surface_brightness_factor = v.surface_brightness_factor,
        transparency_factor = v.transparency_factor,
        solid_colors = v.solid_colors,
        transparency_depth = v.transparency_depth,
        solid_brightness_factor = v.solid_brightness_factor,
        default_rgba = v.default_rgba
        )

    if copy_rendering_options:
      # Copy rendering options
      self.set_parameters(**v.rendering_options.__dict__)

    if copy_region:
      # Copy region bounds
      ijk_min, ijk_max, ijk_step = v.region
      self.new_region(ijk_min, ijk_max, ijk_step, show = False)

    if copy_xform:
      # Copy position and orientation
      self.surface_model().openState.xform = v.model_transform()

    if copy_active:
      # Copy movability
      self.surface_model().openState.active = v.surface_model().openState.active

    if copy_zone:
      # Copy surface zone
      sm = v.surface_model()
      sm_copy = self.surface_model()
      import SurfaceZone
      if sm and SurfaceZone.showing_zone(sm) and sm_copy:
        points, distance = SurfaceZone.zone_points_and_distance(sm)
        SurfaceZone.surface_zone(sm_copy, points, distance, True)

    # TODO: Should copy color zone too.

  # ---------------------------------------------------------------------------
  # If volume data is not writable then make a writable copy.
  #
  def writable_copy(self, require_copy = False,
                    show = True, unshow_original = True, model_id = None,
                    subregion = None, step = (1,1,1), name = None,
                    copy_colors = True):

    r = self.subregion(step, subregion)
    if not require_copy and self.data.writable and self.is_full_region(r):
      return self

    g = self.region_grid(r)
    g.array[:,:,:] = self.region_matrix(r)

    if name:
      g.name = name
    elif self.name.endswith('copy'):
      g.name = self.name
    else:
      g.name = self.name + ' copy'

    v = volume_from_grid_data(g, self.representation, model_id = model_id,
                              show_data = False, show_dialog = False)
    v.copy_settings_from(self, copy_region = False, copy_colors = copy_colors)

    # Display copy and undisplay original
    if show:
      v.show()
    if unshow_original:
      self.unshow()

    return v

  # ---------------------------------------------------------------------------
  #
  def region_grid(self, r):

    shape = self.matrix_size(region = r, clamp = False)
    shape.reverse()
    d = self.data
    from numpy import zeros
    m = zeros(shape, d.value_type)
    origin, step = self.region_origin_and_step(r)
    from VolumeData import Array_Grid_Data
    g = Array_Grid_Data(m, origin, step, d.cell_angles, d.rotation)
    g.rgba = d.rgba           # Copy default data color.
    return g

  # ---------------------------------------------------------------------------
  # The xyz bounding box encloses the subsampled grid with half a step size
  # padding on all sides.
  #
  def xyz_bounds(self, step = None, subregion = None):

    ijk_min_edge, ijk_max_edge = self.ijk_bounds(step, subregion)
    
    from VolumeData import box_corners
    ijk_corners = box_corners(ijk_min_edge, ijk_max_edge)
    data = self.data
    xyz_min, xyz_max = bounding_box(map(data.ijk_to_xyz, ijk_corners))
    
    return (xyz_min, xyz_max)

  # ---------------------------------------------------------------------------
  # The data ijk bounds with half a step size padding on all sides.
  #
  def ijk_bounds(self, step = None, subregion = None, integer = False):

    ss_origin, ss_size, subsampling, ss_step = self.ijk_region(step, subregion)
    ijk_origin = map(lambda a,b: a*b, ss_origin, subsampling)
    ijk_step = map(lambda a,b: a*b, subsampling, ss_step)
    mat_size = map(lambda a,b: (a+b-1)/b, ss_size, ss_step)
    ijk_last = map(lambda a,b,c: a+b*(c-1), ijk_origin, ijk_step, mat_size)

    ijk_min_edge = map(lambda a,b: a - .5*b, ijk_origin, ijk_step)
    ijk_max_edge = map(lambda a,b: a + .5*b, ijk_last, ijk_step)
    if integer:
      r = self.integer_region(ijk_min_edge, ijk_max_edge, step)
      ijk_min_edge, ijk_max_edge = r[:2]

    return ijk_min_edge, ijk_max_edge

  # ---------------------------------------------------------------------------
  #
  def integer_region(self, ijk_min, ijk_max, step = None):

    if step is None:
      step = self.region[2]
    elif isinstance(step, int):
      step = (step,step,step)
    from math import floor, ceil
    ijk_min = [int(floor(i/s)*s) for i,s in zip(ijk_min,step)]
    ijk_max = [int(ceil(i/s)*s) for i,s in zip(ijk_max,step)]
    r = (ijk_min, ijk_max, step)
    return r

  # ---------------------------------------------------------------------------
  # Points must be in volume local coordinates.
  #
  def bounding_region(self, points, padding = 0, step = None, clamp = True):

    d = self.data
    from VolumeData import points_ijk_bounds
    ijk_min, ijk_max = points_ijk_bounds(points, padding, d)
    if clamp:
      ijk_min, ijk_max = clamp_region((ijk_min, ijk_max, None), d.size)[:2]
    r = self.integer_region(ijk_min, ijk_max, step)
    return r

  # ---------------------------------------------------------------------------
  #
  def matrix(self, read_matrix = True, step = None, subregion = None):

    r = self.subregion(step, subregion)
    m = self.region_matrix(r, read_matrix)
    return m

  # ---------------------------------------------------------------------------
  #
  def full_matrix(self, read_matrix = True, step = (1,1,1)):

    m = self.matrix(read_matrix, step, full_region(self.data.size)[:2])
    return m

  # ---------------------------------------------------------------------------
  # Region includes ijk_min and ijk_max points.
  #
  def region_matrix(self, region = None, read_matrix = True):

    if region is None:
      region = self.region
    origin, size, subsampling, step = self.subsample_region(region)
    d = self.data
    operation = 'reading %s' % d.name
    from VolumeData import Progress_Reporter
    progress = Progress_Reporter(operation, size, d.value_type.itemsize)
    from_cache_only = not read_matrix
    if subsampling == (1,1,1):
      m = d.matrix(origin, size, step, progress, from_cache_only)
    else:
      m = d.matrix(origin, size, step, progress, from_cache_only, subsampling)
    return m

  # ---------------------------------------------------------------------------
  # Size of matrix for subsampled subregion returned by matrix().
  #
  def matrix_size(self, step = None, subregion = None, region = None,
                  clamp = True):

    if region is None:
      region = self.subregion(step, subregion)
    ss_origin, ss_size, subsampling, ss_step = self.subsample_region(region,
                                                                     clamp)
    mat_size = map(lambda a,b: (a+b-1)/b, ss_size, ss_step)
    return mat_size

  # ---------------------------------------------------------------------------
  #
  def single_plane(self):

    return len([s for s in self.matrix_size() if s == 1]) > 0

  # ---------------------------------------------------------------------------
  # Transform mapping matrix indices to xyz.  The matrix indices are not the
  # same as the data indices since the matrix includes only the current
  # subregion and subsampled data values.
  #
  def matrix_indices_to_xyz_transform(self, step = None, subregion = None):

    ss_origin, ss_size, subsampling, ss_step = self.ijk_region(step, subregion)
    ijk_origin = map(lambda a,b: a*b, ss_origin, subsampling)
    ijk_step = map(lambda a,b: a*b, subsampling, ss_step)

    data = self.data
    xo, yo, zo = data.ijk_to_xyz(ijk_origin)
    io, jo, ko = ijk_origin
    istep, jstep, kstep = ijk_step
    xi, yi, zi = data.ijk_to_xyz((io+istep, jo, ko))
    xj, yj, zj = data.ijk_to_xyz((io, jo+jstep, ko))
    xk, yk, zk = data.ijk_to_xyz((io, jo, ko+kstep))
    tf = ((xi-xo, xj-xo, xk-xo, xo),
          (yi-yo, yj-yo, yk-yo, yo),
          (zi-zo, zj-zo, zk-zo, zo))
    return tf

  # ---------------------------------------------------------------------------
  #
  def data_origin_and_step(self, step = None, subregion = None):

    r = self.subregion(step, subregion)
    return self.region_origin_and_step(r)

  # ---------------------------------------------------------------------------
  #
  def region_origin_and_step(self, region):

    ijk_origin, ijk_max, ijk_step = region
    dorigin = self.data.ijk_to_xyz(ijk_origin)
    dstep = map(lambda a,b: a*b, self.data.step, ijk_step)
    return dorigin, dstep

  # ---------------------------------------------------------------------------
  # Data values or coordinates have changed.
  # Surface / solid rendering is not automatically redrawn when data values
  # change.
  #
  def data_changed_cb(self, type):

    if type == 'values changed':
      self.data.clear_cache()
      self.matrix_changed()
      for cb in self.change_callbacks:
        cb(self, 'data values changed')
      # TODO: should this automatically update the data display?
    elif type == 'coordinates changed':
      for cb in self.change_callbacks:
        cb(self, 'coordinates changed')
    elif type == 'path changed':
      self.name = utf8_string(self.data.name)

  # ---------------------------------------------------------------------------
  # Return the origin and size of the subsampled submatrix to be read.
  #
  def ijk_region(self, step = None, subregion = None):

    r = self.subregion(step, subregion)
    return self.subsample_region(r)

  # ---------------------------------------------------------------------------
  # Return the origin and size of the subsampled submatrix to be read.
  # Also return the subsampling factor and additional step (ie stride) that
  # must be used to get the displayed data.
  #
  def subsample_region(self, region, clamp = True):

    ijk_min, ijk_max, ijk_step = region
    
    # Samples always have indices divisible by step, so increase ijk_min if
    # needed to make it a multiple of ijk_step.
    m_ijk_min = map(lambda i,s: s*((i+s-1)/s), ijk_min, ijk_step)

    # If region is non-empty but contains no step multiple decrease ijk_min.
    for a in range(3):
      if m_ijk_min[a] > ijk_max[a] and ijk_min[a] <= ijk_max[a]:
        m_ijk_min[a] -= ijk_step[a]

    subsampling, ss_full_size = self.choose_subsampling(ijk_step)

    ss_origin = map(lambda i,s: (i+s-1)/s, m_ijk_min, subsampling)
    if clamp:
      ss_origin = map(lambda i: max(i,0), ss_origin)
    ss_end = map(lambda i,s: (i+s)/s, ijk_max, subsampling)
    if clamp:
      ss_end = map(lambda i,lim: min(i,lim), ss_end, ss_full_size)
    ss_size = map(lambda e,o: e-o, ss_end, ss_origin)
    ss_step = map(lambda s,d: s/d, ijk_step, subsampling)

    return tuple(ss_origin), tuple(ss_size), tuple(subsampling), tuple(ss_step)

  # ---------------------------------------------------------------------------
  # Return the subsampling and size of subsampled matrix for the requested
  # ijk_step.
  #
  def choose_subsampling(self, ijk_step):
    
    data = self.data
    if not hasattr(data, 'available_subsamplings'):
      return (1,1,1), data.size

    compatible = []
    for step, grid in data.available_subsamplings.items():
      if (ijk_step[0] % step[0] == 0 and
          ijk_step[1] % step[1] == 0 and
          ijk_step[2] % step[2] == 0):
        e = ((ijk_step[0] / step[0]) *
             (ijk_step[1] / step[1]) *
             (ijk_step[2] / step[2]))
        compatible.append((e, step, grid.size))

    if len(compatible) == 0:
      return (1,1,1), data.size

    subsampling, size = min(compatible)[1:]
    return subsampling, size

  # ---------------------------------------------------------------------------
  # Applying point_xform to points gives Chimera world coordinates.  If the
  # point_xform is None then the points are in local volume coordinates.
  #
  def interpolated_values(self, points, point_xform = None,
                          out_of_bounds_list = False, subregion = 'all',
                          step = (1,1,1), method = 'linear'):

    matrix, p2m_transform = self.matrix_and_transform(point_xform,
                                                      subregion, step)
    from VolumeData import interpolate_volume_data
    values, outside = interpolate_volume_data(points, p2m_transform,
                                              matrix, method)

    if out_of_bounds_list:
      return values, outside
    
    return values
    
  # ---------------------------------------------------------------------------
  # Applying point_xform to points gives Chimera world coordinates.  If the
  # point_xform is None then the points are in local volume coordinates.
  #
  def interpolated_gradients(self, points, point_xform = None,
                             out_of_bounds_list = False,
                             subregion = 'all', step = (1,1,1),
                             method = 'linear'):

    matrix, v2m_transform = self.matrix_and_transform(point_xform,
                                                      subregion, step)

    from VolumeData import interpolate_volume_gradient
    gradients, outside = interpolate_volume_gradient(points, v2m_transform,
                                                     matrix, method)
    if out_of_bounds_list:
      return gradients, outside
    
    return gradients

  # ---------------------------------------------------------------------------
  # Add values from another volume interpolated at grid positions
  # of this volume.
  #
  def add_interpolated_values(self, v, subregion = 'all', step = (1,1,1),
                              scale = 1):

    if scale == 0:
      return
    
    d = self.data
    m = d.full_matrix()
    if same_grid(v, v.subregion(step, subregion),
                 self, self.subregion(1, 'all')):
      # Optimization: avoid interpolation for identical grids.
      values = v.matrix(step = step, subregion = subregion)
      const_values = True
    else:
      size_limit = 2 ** 22          # 4 Mvoxels
      if m.size > size_limit:
        # Calculate plane by plane to save memory with grid point array
        from numpy import empty, single as floatc
        values = empty(m.shape, floatc)
        for z in range(m.shape[0]):
          points = self.grid_points(v.model_transform().inverse(), z)
          values1d = v.interpolated_values(points, None, subregion = subregion,
                                           step = step)
          values[z,:,:] = values1d.reshape(m.shape[1:])
      else:
        points = self.grid_points(v.model_transform().inverse())
        values1d = v.interpolated_values(points, None, subregion = subregion,
                                       step = step)
        values = values1d.reshape(m.shape)
      const_values = False

    # Add scaled copy of array.
    if scale == 'minrms':
      level = min(v.surface_levels) if v.surface_levels else 0
      scale = minimum_rms_scale(values, m, level)
      from chimera.replyobj import info
      info('Minimum RMS scale factor for "%s" above level %.5g\n'
           '  subtracted from "%s" is %.5g\n'
           % (v.name_with_id(), level, self.name_with_id(), -scale))
    if scale == 1:
      m[:,:,:] += values
    elif scale == -1:
      m[:,:,:] -= values
    else:
      # Avoid copying array unless needed for scaling.
      if const_values:
        values = values.copy()
      values *= scale
      m[:,:,:] += values
    d.values_changed()

  # ---------------------------------------------------------------------------
  # Return xyz coordinates of grid points of volume data transformed to a
  # local coordinate system.
  #
  def grid_points(self, xform_to_local_coords, zplane = None):

    data = self.data
    size = data.size
    from numpy import float32
    from VolumeData import grid_indices
    if zplane is None:
      points = grid_indices(size, float32)
    else:
      points = grid_indices((size[0],size[1],1), float32)  # Single z plane.
      points[:,2] = zplane
    from Matrix import multiply_matrices, xform_matrix
    mt = multiply_matrices(xform_matrix(xform_to_local_coords),
                           xform_matrix(self.model_transform()),
                           data.ijk_to_xyz_transform)
    from _contour import affine_transform_vertices
    affine_transform_vertices(points, mt)
    return points
  
  # ---------------------------------------------------------------------------
  # Returns 3-d numeric array and transformation from a given "source"
  # coordinate system to array indices.  The source_to_world_xform transforms
  # from the source coordinate system to Chimera world coordinates.
  # If the transform is None it means the source coordinates are the
  # same as the volume local coordinates.
  #
  def matrix_and_transform(self, source_to_world_xform, subregion, step):
    
    m2s_transform = self.matrix_indices_to_xyz_transform(step, subregion)
    if source_to_world_xform:
      volume_xform = self.model_transform()
      if volume_xform:
        # Handle case where vertices and volume have different model xforms.
        from chimera import Xform
	xf = Xform()
	xf.multiply(source_to_world_xform)
	xf.invert()
	xf.multiply(volume_xform)
	from Matrix import xform_matrix, multiply_matrices
	m2s_transform = multiply_matrices(xform_matrix(xf), m2s_transform)
      
    from Matrix import invert_matrix
    s2m_transform = invert_matrix(m2s_transform)

    matrix = self.matrix(step=step, subregion=subregion)

    return matrix, s2m_transform

  # ---------------------------------------------------------------------------
  # Return currently displayed subregion.  If only a zone is being displayed
  # set all grid data values outside the zone to zero.
  #
  def grid_data(self, subregion = None, step = (1,1,1), mask_zone = True,
                region = None):

    if region is None:
      region = self.subregion(step, subregion)
    if self.is_full_region(region):
      sg = self.data
    else:
      ijk_min, ijk_max, ijk_step = region
      from VolumeData import Grid_Subregion
      sg = Grid_Subregion(self.data, ijk_min, ijk_max, ijk_step)

    if mask_zone:
      surf_model = self.surface_model()
      import SurfaceZone
      if SurfaceZone.showing_zone(surf_model):
        points, radius = SurfaceZone.zone_points_and_distance(surf_model)
        from VolumeData import zone_masked_grid_data
        mg = zone_masked_grid_data(sg, points, radius)
        return mg
        
    return sg
  
  # ---------------------------------------------------------------------------
  #
  def subregion(self, step = None, subregion = None):

    if subregion is None:
      ijk_min, ijk_max = self.region[:2]
    elif isinstance(subregion, basestring):
      if subregion == 'all':
        ijk_min, ijk_max = full_region(self.data.size)[:2]
      else:
        ijk_min, ijk_max = self.region_list.named_region_bounds(subregion)
        if ijk_min == None or ijk_max == None:
          ijk_min, ijk_max = self.region[:2]
    else:
      ijk_min, ijk_max = subregion

    if step is None:
      ijk_step = self.region[2]
    elif isinstance(step, int):
      ijk_step = (step, step, step)
    else:
      ijk_step = step

    r = (ijk_min, ijk_max, ijk_step)
    return r
  
  # ---------------------------------------------------------------------------
  #
  def copy_zone(self, outside = False):

    import SurfaceZone
    if not SurfaceZone.showing_zone(self):
      return None

    points, radius = SurfaceZone.zone_points_and_distance(self)
    from VolumeData import zone_masked_grid_data
    masked_data = zone_masked_grid_data(self.data, points, radius,
                                        invert_mask = outside)
    if outside: name = 'outside zone'
    else: name = 'zone'
    masked_data.name = self.name + ' ' + name
    mv = volume_from_grid_data(masked_data, show_data = False)
    mv.copy_settings_from(self, copy_region = False, copy_zone = False)
    mv.show()
    return mv
  
  # ---------------------------------------------------------------------------
  #
  def matrix_value_statistics(self, read_matrix = True):

    if self.matrix_stats is None:
      matrix = self.matrix(read_matrix)
      if matrix is None:
        return None
      self.message('Computing histogram for %s' % self.name)
      from VolumeData import Matrix_Value_Statistics
      self.matrix_stats = Matrix_Value_Statistics(matrix)
      self.message('')

    return self.matrix_stats
  
  # ---------------------------------------------------------------------------
  # Apply surface/mesh transparency factor.
  #
  def modulated_surface_color(self, rgba):

    r,g,b,a = rgba

    bf = self.surface_brightness_factor

    ofactor = 1 - self.transparency_factor
    ofactor = max(0, ofactor)
    ofactor = min(1, ofactor)
      
    return (r * bf, g * bf, b * bf, a * ofactor)
  
  # ---------------------------------------------------------------------------
  # Without brightness and transparency adjustment.
  #
  def transfer_function(self):

    tf = map(lambda ts,c: tuple(ts) + tuple(c),
             self.solid_levels, self.solid_colors)
    tf.sort()

    return tf
  
  # ---------------------------------------------------------------------------
  #
  def write_file(self, path, format = None, options = {}):

    from VolumeData import save_grid_data
    d = self.grid_data()
    format = save_grid_data(d, path, format, options)
  
  # ---------------------------------------------------------------------------
  #
  def view_models(self, view, representation = None):

    mlist = []
    
    if representation in (None, 'surface', 'mesh'):
      mlist.append(self)
      self.display = view

    if representation in (None, 'solid'):
      s = self.solid
      if s:
        m = s.model()
        if m:
          mlist.append(m)
          m.display = view

    return len(mlist) > 0
  
  # ---------------------------------------------------------------------------
  #
  def models(self):

    mlist = [self]

    s = self.solid
    if s and s.model():
      mlist.append(s.model())

    return mlist
  
  # ---------------------------------------------------------------------------
  #
  def surface_model(self):

    return self
  
  # ---------------------------------------------------------------------------
  #
  def solid_model(self):

    s = self.solid
    if s:
      return s.model()
    return None
    
  # ---------------------------------------------------------------------------
  #
  def model_transform(self):

    return self.openState.xform
  
  # ---------------------------------------------------------------------------
  # Hide surface model and close solid model.
  #
  def unshow(self):

    self.close_solid()
    self.hide_surface()
  
  # ---------------------------------------------------------------------------
  #
  def hide_surface(self):

    self.display = False
    
  # ---------------------------------------------------------------------------
  #
  def close_models(self):

    self.close_solid()
    self.close_surface()
  
  # ---------------------------------------------------------------------------
  #
  def close_surface(self):

    import chimera
    chimera.openModels.close([self])
      
  # ---------------------------------------------------------------------------
  #
  def close_solid(self):

    s = self.solid
    if s:
      s.close_model()
      self.solid = None
      
  # ---------------------------------------------------------------------------
  #
  def close(self):

    self.close_models()
      
  # ---------------------------------------------------------------------------
  #
  def model_closed_cb(self, model):

    if self.data:
      self.data.remove_change_callback(self.data_changed_cb)
      self.data = None
      self.keep_matrix = None
      self.outline_box = None	# Remove reference loops
      from chimera import triggers
      triggers.deleteHandler('SurfacePiece', self.surface_piece_change_handler)
      self.surface_piece_change_handler = None

# -----------------------------------------------------------------------------
#
class Outline_Box:

  def __init__(self, surface_model):

    self.model = surface_model
    self.piece = None
    self.corners = None
    self.rgb = None
    self.linewidth = None
    
  # ---------------------------------------------------------------------------
  #
  def show(self, corners, rgb, linewidth):

    if corners and rgb:
      changed = (corners != self.corners or rgb != self.rgb or
                 linewidth != self.linewidth)
      if changed:
        self.erase_box()
        self.make_box(corners, rgb, linewidth)
      
  # ---------------------------------------------------------------------------
  #
  def make_box(self, corners, rgb, linewidth):

    vlist = corners
    qlist = ((0,4,5), (5,1,0), (0,2,6), (6,4,0),
             (0,1,3), (3,2,0), (7,3,1), (1,5,7),
             (7,6,2), (2,3,7), (7,5,4), (4,6,7))

    b = 8 + 2 + 1    # Bit mask, 8 = show triangle, edges are bits 4,2,1
    hide_diagonals = (b,b,b,b,b,b,b,b,b,b,b,b)

    rgba = tuple(rgb) + (1,)
    p = self.model.newPiece()
    p.displayStyle = p.Mesh
    p.lineThickness = linewidth
    p.useLighting = False
    p.outline_box = True # Do not cap clipped outline box.
    # Set geometry after setting outline_box attribute to avoid undesired
    # coloring and capping of outline boxes.
    p.geometry = vlist, qlist
    p.triangleAndEdgeMask = hide_diagonals
    p.color = rgba

    self.piece = p
    self.corners = corners
    self.rgb = rgb
    self.linewidth = linewidth

  # ---------------------------------------------------------------------------
  #
  def erase_box(self):

    p = self.piece
    if not p is None:
      if not p.__destroyed__:
        self.model.removePiece(p)
      self.piece = None
      self.corners = None
      self.rgb = None

# -----------------------------------------------------------------------------
# Compute scale factor f minimizing norm of (f*v + u) over domain v >= level.
#
#   f = -(v,u)/|v|^2 where v >= level.
#
def minimum_rms_scale(v, u, level):

  from numpy import greater_equal, multiply, dot as inner_product

  # Make copy of v with values less than level set to zero.
  vc = v.copy()
  greater_equal(vc, level, vc)
  multiply(v, vc, vc)
  vc = vc.ravel()

  # Compute factor
  vcu = inner_product(vc,u.ravel())
  vcvc = inner_product(vc,vc)
  if vcvc == 0:
    f = 1
  else:
    f = -vcu/vcvc
    
  return f
  
# -----------------------------------------------------------------------------
#
def same_grid(v1, region1, v2, region2):

  from Matrix import same_xform
  same = (region1 == region2 and
          v1.data.ijk_to_xyz_transform == v2.data.ijk_to_xyz_transform and
          same_xform(v1.model_transform(), v2.model_transform()))
  return same
    
# -----------------------------------------------------------------------------
# Remember visited subregions.
#
class Region_List:

  def __init__(self):

    self.region_list = []		# history
    self.current_index = None
    self.max_list_size = 32

    self.named_regions = []

  # ---------------------------------------------------------------------------
  #
  def insert_region(self, ijk_min, ijk_max):

    ijk_min_max = (tuple(ijk_min), tuple(ijk_max))
    ci = self.current_index
    rlist = self.region_list
    if ci == None:
      ni = 0
    elif ijk_min_max == rlist[ci]:
      return
    else:
      ni = ci + 1
    self.current_index = ni
    if ni < len(rlist) and ijk_min_max == rlist[ni]:
      return
    rlist.insert(ni, ijk_min_max)
    self.trim_list()
    
  # ---------------------------------------------------------------------------
  #
  def trim_list(self):

    if len(self.region_list) <= self.max_list_size:
      return

    if self.current_index > self.max_list_size/2:
      del self.region_list[0]
      self.current_index -= 1
    else:
      del self.region_list[-1]

  # ---------------------------------------------------------------------------
  #
  def other_region(self, offset):

    if self.current_index == None:
      return None, None

    i = self.current_index + offset
    if i < 0 or i >= len(self.region_list):
      return None, None

    self.current_index = i
    return self.region_list[i]

  # ---------------------------------------------------------------------------
  #
  def where(self):

    ci = self.current_index
    if ci == None:
      return 0, 0

    from_beginning = ci
    from_end = len(self.region_list)-1 - ci
    return from_beginning, from_end

  # ---------------------------------------------------------------------------
  #
  def region_names(self):

    return map(lambda nr: nr[0], self.named_regions)

  # ---------------------------------------------------------------------------
  #
  def add_named_region(self, name, ijk_min, ijk_max):

    self.named_regions.append((name, (tuple(ijk_min), tuple(ijk_max))))

  # ---------------------------------------------------------------------------
  #
  def find_named_region(self, ijk_min, ijk_max):

    ijk_min_max = (tuple(ijk_min), tuple(ijk_max))
    for name, named_ijk_min_max in self.named_regions:
      if named_ijk_min_max == ijk_min_max:
	return name
    return None

  # ---------------------------------------------------------------------------
  #
  def named_region_bounds(self, name):

    index = self.named_region_index(name)
    if index == None:
      return None, None
    return self.named_regions[index][1]

  # ---------------------------------------------------------------------------
  #
  def named_region_index(self, name):

    try:
      index = self.region_names().index(name)
    except ValueError:
      index = None
    return index

  # ---------------------------------------------------------------------------
  #
  def remove_named_region(self, index):

    del self.named_regions[index]

# -----------------------------------------------------------------------------
#
class Rendering_Options:

  def __init__(self):

    self.show_outline_box = True
    self.outline_box_rgb = (1,1,1)
    self.outline_box_linewidth = 1
    self.limit_voxel_count = True           # auto-adjust step size
    self.voxel_limit = 1                    # Mvoxels
    self.color_modes = (
      'auto4', 'auto8', 'auto12', 'auto16',
      'rgba4', 'rgba8', 'rgba12', 'rgba16', 'rgb4', 'rgb8', 'rgb12', 'rgb16',
      'la4', 'la8', 'la12', 'la16', 'l4', 'l8', 'l12', 'l16')
    self.color_mode = 'auto8'               # solid rendering pixel formats
                                            #   (auto|rgba|rgb|la|l)(4|8|12|16)
    self.projection_modes = ('auto', '2d-xyz', '2d-x', '2d-y', '2d-z', '3d')
    self.projection_mode = 'auto'           # auto, 2d-xyz, 2d-x, 2d-y, 2d-z, 3d
    self.bt_correction = False              # brightness and transparency
    self.minimal_texture_memory = False
    self.maximum_intensity_projection = False
    self.linear_interpolation = True
    self.dim_transparency = True            # for surfaces
    self.dim_transparent_voxels = True      # for solid rendering
    self.one_transparent_layer = False
    self.line_thickness = 1
    self.smooth_lines = False
    self.mesh_lighting = True
    self.two_sided_lighting = True
    self.flip_normals = False
    self.subdivide_surface = False
    self.subdivision_levels = 1
    self.surface_smoothing = False
    self.smoothing_iterations = 2
    self.smoothing_factor = .3
    self.square_mesh = False
    self.cap_faces = True

  # ---------------------------------------------------------------------------
  #
  def copy(self):

    ro = Rendering_Options()
    for key, value in self.__dict__.items():
      if not key.startswith('_'):
        setattr(ro, key, value)
    return ro

# -----------------------------------------------------------------------------
#
def clamp_region(region, size):

  import VolumeData
  r = VolumeData.clamp_region(region[:2], size) + tuple(region[2:])
  return r

# ---------------------------------------------------------------------------
# Return ijk step size so that voxels displayed is at or below the limit.
# The given ijk step size may be increased or decreased by powers of 2.
#
def ijk_step_for_voxel_limit(ijk_min, ijk_max, ijk_step,
                             limit_voxel_count, mvoxel_limit):

  def voxel_count(step, ijk_min = ijk_min, ijk_max = ijk_max):
    return subarray_size(ijk_min, ijk_max, step)

  step = limit_voxels(voxel_count, ijk_step, limit_voxel_count, mvoxel_limit)
  return step

# ---------------------------------------------------------------------------
# Return ijk step size so that voxels displayed is at or below the limit.
# The given ijk step size may be increased or decreased by powers of 2.
#
def limit_voxels(voxel_count, ijk_step, limit_voxel_count, mvoxel_limit):

    if not limit_voxel_count:
      return ijk_step

    if mvoxel_limit == None:
      return ijk_step
    
    voxel_limit = int(mvoxel_limit * (2 ** 20))
    if voxel_limit < 1:
      return ijk_step

    step = ijk_step

    # Make step bigger until voxel limit met.
    while voxel_count(step) > voxel_limit:
      new_step = [2*s for s in step]
      if voxel_count(new_step) >= voxel_count(step):
        break
      step = new_step

    # Make step smaller until voxel limit exceeded.
    while tuple(step) != (1,1,1):
      new_step = [max(1, s/2) for s in step]
      if voxel_count(new_step) > voxel_limit:
        break
      step = new_step
    
    return step

# ---------------------------------------------------------------------------
#
def show_planes(dr, axis, plane, depth = 1, extend_axes = [], show = True,
                save_in_region_queue = True):
  
  # Make sure requested plane number is in range.
  dsize = dr.data.size
  planes = dsize[axis]
  p = int(plane)

  # Set new display plane
  ijk_min, ijk_max, ijk_step = map(list, dr.region)
  for a in extend_axes:
    ijk_min[a] = 0
    ijk_max[a] = dsize[a]-1

  def set_plane_range(step):
    astep = step[axis]
    ijk_min[axis] = max(0, min(p, planes - depth*astep))
    ijk_max[axis] = max(0, min(planes-1, p+depth*astep-1))

  def voxel_count(step):
    set_plane_range(step)
    return subarray_size(ijk_min, ijk_max, step)

  # Adjust step size to limit voxel count.
  ro = dr.rendering_options
  step = limit_voxels(voxel_count, ijk_step,
                      ro.limit_voxel_count, ro.voxel_limit)
  set_plane_range(step)

  if not dr.new_region(ijk_min, ijk_max, step, show = show,
                       save_in_region_queue = save_in_region_queue):
    return False

  return True

# -----------------------------------------------------------------------------
#
class cycle_through_planes:

  def __init__(self, v, axis, pstart, pend = None, pstep = 1, pdepth = 1):

    axis = {'x':0, 'y':1, 'z':2}.get(axis, axis)
    if pend is None:
      pend = pstart
    if pend < 0:
      pend = v.data.size[axis] + pend
    if pstart < 0:
      pstart = v.data.size[axis] + pstart
    if pend < pstart:
      pstep *= -1

    self.volume = v
    self.axis = axis
    self.plane = pstart
    self.plast = pend
    self.step = pstep
    self.depth = pdepth

    from chimera import triggers
    self.handler = triggers.addHandler('new frame', self.next_plane_cb, None)

  def next_plane_cb(self, trigger_name, call_data, trigger_data):
    
    p = self.plane
    if self.step * (self.plast - p) >= 0:
      self.plane += self.step
      show_planes(self.volume, self.axis, p, self.depth,
                  save_in_region_queue = False)
    else:
      from chimera import triggers
      triggers.deleteHandler('new frame', self.handler)
      self.handler = None

# -----------------------------------------------------------------------------
#
def subarray_size(ijk_min, ijk_max, step):

  pi,pj,pk = [max(ijk_max[a]/step[a] - (ijk_min[a]+step[a]-1)/step[a] + 1, 1)
              for a in (0,1,2)]
  voxels = pi*pj*pk
  return voxels

# -----------------------------------------------------------------------------
#
def full_region(size, ijk_step = [1,1,1]):

  ijk_min = [0, 0, 0]
  ijk_max = map(lambda n: n-1, size)
  region = (ijk_min, ijk_max, ijk_step)
  return region

# -----------------------------------------------------------------------------
#
def is_empty_region(ijk_region):

  ijk_min, ijk_max, ijk_step = ijk_region
  ijk_size = map(lambda a, b: a - b + 1, ijk_max, ijk_min)
  if filter(lambda size: size <= 0, ijk_size):
    return 1
  return 0

# ---------------------------------------------------------------------------
# Adjust volume region to include a zone.  If current volume region is
# much bigger than that needed for the zone, then shrink it.  The purpose
# of this resizing is to keep the region small so that recontouring is fast,
# but not resize on every new zone radius.  Resizing on every new zone
# radius requires recontouring and redisplaying the volume histogram which
# slows down zone radius updates.
#
def resize_region_for_zone(data_region, points, radius, initial_resize = False):

  from VolumeData import points_ijk_bounds
  ijk_min, ijk_max = points_ijk_bounds(points, radius, data_region.data)
  ijk_min, ijk_max = clamp_region((ijk_min, ijk_max, None),
                                  data_region.data.size)[:2]

  cur_ijk_min, cur_ijk_max = data_region.region[:2]

  volume_padding_factor = 2.0
  min_volume = 32768

  if not region_contains_region((cur_ijk_min, cur_ijk_max),
                                (ijk_min, ijk_max)):
    import math
    padding_factor = math.pow(volume_padding_factor, 1.0/3)
  else:
    cur_volume = region_volume(cur_ijk_min, cur_ijk_max)
    box_volume = region_volume(ijk_min, ijk_max)
    if cur_volume <= 2 * box_volume or cur_volume <= min_volume:
      return None, None
    import math
    if initial_resize:
      # Pad zone to grow or shrink before requiring another resize
      padding_factor = math.pow(volume_padding_factor, 1.0/6)
    else:
      padding_factor = 1
    new_box_volume = box_volume * math.pow(padding_factor, 3)
    if new_box_volume < min_volume and box_volume > 0:
      # Don't resize to smaller than the minimum volume
      import math
      padding_factor = math.pow(float(min_volume) / box_volume, 1.0/3)

  new_ijk_min, new_ijk_max = extend_region(ijk_min, ijk_max, padding_factor)

  return new_ijk_min, new_ijk_max

# -----------------------------------------------------------------------------
#
def region_contains_region(r1, r2):

  for a in range(3):
    if r2[0][a] < r1[0][a] or r2[1][a] > r1[1][a]:
      return False
  return True

# -----------------------------------------------------------------------------
#
def region_volume(ijk_min, ijk_max):

  vol = 1
  for a in range(3):
    vol *= ijk_max[a] - ijk_min[a] + 1
  return vol

# -----------------------------------------------------------------------------
#
def extend_region(ijk_min, ijk_max, factor):

  e_ijk_min = list(ijk_min)
  e_ijk_max = list(ijk_max)
  for a in range(3):
    pad = int(.5 * (factor - 1) * (ijk_max[a] - ijk_min[a]))
    e_ijk_min[a] -= pad
    e_ijk_max[a] += pad

  return tuple(e_ijk_min), tuple(e_ijk_max)

# -----------------------------------------------------------------------------
#
def maximum_data_diagonal_length(data):

    imax, jmax, kmax = map(lambda a: a-1, data.size)
    ijk_to_xyz = data.ijk_to_xyz
    d = max(distance(ijk_to_xyz((0,0,0)), ijk_to_xyz((imax,jmax,kmax))),
            distance(ijk_to_xyz((0,0,kmax)), ijk_to_xyz((imax,jmax,0))),
            distance(ijk_to_xyz((0,jmax,0)), ijk_to_xyz((imax,0,kmax))),
            distance(ijk_to_xyz((0,jmax,kmax)), ijk_to_xyz((imax,0,0))))
    return d

# -----------------------------------------------------------------------------
#
def distance(xyz1, xyz2):

  dx, dy, dz = map(lambda a, b: a-b, xyz1, xyz2)
  import math
  d = math.sqrt(dx*dx + dy*dy + dz*dz)
  return d

# -----------------------------------------------------------------------------
#
from VolumeData import bounding_box

# -----------------------------------------------------------------------------
#
def transformed_points(points, xform):

  from numpy import array, single as floatc
  from Matrix import xform_matrix
  tf = array(xform_matrix(xform), floatc)
  tf_points = array(points, floatc)
  import _contour
  _contour.affine_transform_vertices(tf_points, tf)

  return tf_points
    
# -----------------------------------------------------------------------------
#
def saturate_rgba(rgba):

  mc = max(rgba[:3])
  if mc > 0:
    s = rgba[0]/mc, rgba[1]/mc, rgba[2]/mc, rgba[3]
  else:
    s = rgba
  return s

# ----------------------------------------------------------------------------
# Return utf-8 encoding in a plain (non-unicode) string.  This is needed
# for setting C++ model name.
#
def utf8_string(s):

  if isinstance(s, unicode):
    return s.encode('utf-8')
  return s

# ----------------------------------------------------------------------------
# Use a periodic unit cell map to create a new map that covers a PDB model
# plus some padding.  Written for Terry Lang.
#
def map_covering_atoms(atoms, pad, volume):

    ijk_min, ijk_max = atom_bounds(atoms, pad, volume)
    g = map_from_periodic_map(volume.data, ijk_min, ijk_max)
    v = volume_from_grid_data(g, show_data = False)
    v.copy_settings_from(volume, copy_region = False)

    return v

# ----------------------------------------------------------------------------
#
def atom_bounds(atoms, pad, volume):

    # Get atom positions.
    from _multiscale import get_atom_coordinates
    xyz = get_atom_coordinates(atoms, transformed = True)

    # Transform atom coordinates to volume ijk indices.
    from Matrix import multiply_matrices, xform_matrix
    tf = multiply_matrices(volume.data.xyz_to_ijk_transform,
                           xform_matrix(volume.model_transform().inverse()))
    from _contour import affine_transform_vertices
    affine_transform_vertices(xyz, tf)
    ijk = xyz

    # Find integer bounds.
    from math import floor, ceil
    ijk_min = [int(floor(i-pad)) for i in ijk.min(axis=0)]
    ijk_max = [int(ceil(i+pad)) for i in ijk.max(axis=0)]

    return ijk_min, ijk_max

# ----------------------------------------------------------------------------
#
def map_from_periodic_map(grid, ijk_min, ijk_max):

    # Create new 3d array.
    ijk_size = map(lambda a,b: a-b+1, ijk_max, ijk_min)
    kji_size = tuple(reversed(ijk_size))
    from numpy import zeros
    m = zeros(kji_size, grid.value_type)

    # Fill in new array using periodicity of original array.
    # Find all overlapping unit cells and copy needed subblocks.
    gsize = grid.size
    cell_min = map(lambda a,b: a/b, ijk_min, gsize)
    cell_max = map(lambda a,b: a/b, ijk_max, gsize)
    for kc in range(cell_min[2], cell_max[2]+1):
        for jc in range(cell_min[1], cell_max[1]+1):
            for ic in range(cell_min[0], cell_max[0]+1):
                ijkc = (ic,jc,kc)
                ijk0 = map(lambda a,b,c: max(a*c,b)-b, ijkc, ijk_min, gsize)
                ijk1 = map(lambda a,b,c,d: min((a+1)*c,b+1)-d,
                           ijkc, ijk_max, gsize, ijk_min)
                size = map(lambda a,b: a-b, ijk1, ijk0)
                origin = map(lambda a,b,c: max(0, b-a*c), ijkc, ijk_min, gsize)
                cm = grid.matrix(origin, size)
                m[ijk0[2]:ijk1[2],ijk0[1]:ijk1[1],ijk0[0]:ijk1[0]] = cm

    # Create volume data copy.
    xyz_min = grid.ijk_to_xyz(ijk_min)
    from VolumeData import Array_Grid_Data
    g = Array_Grid_Data(m, xyz_min, grid.step, grid.cell_angles, grid.rotation,
                        name = grid.name)
    return g

# -----------------------------------------------------------------------------
# Open and display a map.
#
def open_volume_file(path, format = None, name = None, representation = None,
                     open_models = True, model_id = None,
                     show_data = True, show_dialog = True):

  import VolumeData
  try:
    glist = VolumeData.open_file(path, format)
  except VolumeData.File_Format_Error, value:
    from os.path import basename
    if isinstance(path, (list,tuple)):
      descrip = '%s ... (%d files)' % (basename(path[0]), len(path))
    else:
      descrip = basename(path)
    msg = 'Error reading file ' + descrip
    if format:
      msg += ', format %s' % format
    msg += '\n%s\n' % str(value)
    from chimera.replyobj import error
    error(msg)
    return []

  if not name is None:
    for g in glist:
      g.name = name

  drlist = [volume_from_grid_data(g, representation, open_models,
                                  model_id, show_data, show_dialog)
            for g in glist]
  return  drlist

# -----------------------------------------------------------------------------
# Open and display a map using Volume Viewer.
#
def volume_from_grid_data(grid_data, representation = None,
                          open_model = True, model_id = None,
                          show_data = True, show_dialog = True):

  if show_dialog:
    import chimera
    if not chimera.nogui:
      from volumedialog import show_volume_dialog
      show_volume_dialog()


  # Determine initial region bounds and step.
  region = full_region(grid_data.size)[:2]
  ro = default_settings.rendering_option_defaults()
  if hasattr(grid_data, 'polar_values') and grid_data.polar_values:
    ro.flip_normals = True
    ro.cap_faces = False
  ijk_step = ijk_step_for_voxel_limit(region[0], region[1], (1,1,1),
                                      ro.limit_voxel_count, ro.voxel_limit)
  region = tuple(region) + (ijk_step,)

  d = volume_manager.data_already_opened(grid_data.path, grid_data.grid_id)
  if d:
    grid_data = d

  v = Volume(grid_data, region, ro, model_id, open_model)

  # Set display style
  if representation is None:
    # Show single plane data in solid style.
    single_plane = [s for s in v.data.size if s == 1]
    if single_plane:
      rep = 'solid'
    else:
      rep = 'surface'
    v.set_representation(rep)
  else:
    v.set_representation(representation)

  set_initial_volume_color(v)

  # Show data
  if show_data:
    ds = default_settings
    if show_one_plane(v, ds['show_plane'], ds['voxel_limit_for_plane']):
      zmid = int(0.5 * (v.region[0][2] + v.region[1][2]))
      v.set_representation('solid')
      show_planes(v, axis = 2, plane = zmid, depth = 1, show = False)
      v.initialize_thresholds()
      v.show()
    elif show_when_opened(v, ds['show_on_open'], ds['voxel_limit_for_open']):
      v.initialize_thresholds()
      v.show()
    else:
      v.message('%s not shown' % v.name)

  return v

# -----------------------------------------------------------------------------
#
volume_manager = Volume_Manager()
default_settings = volume_manager.default_settings
add_volume_opened_callback = volume_manager.add_volume_opened_callback
add_volume_closed_callback = volume_manager.add_volume_closed_callback
add_session_save_callback = volume_manager.add_session_save_callback
set_initial_volume_color = volume_manager.set_initial_volume_color
volume_list = volume_manager.volume_list
regions_using_data = volume_manager.regions_using_data
replace_data = volume_manager.replace_data
remove_volumes = volume_manager.remove_volumes
