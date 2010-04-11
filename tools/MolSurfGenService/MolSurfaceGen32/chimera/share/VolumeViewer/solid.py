# -----------------------------------------------------------------------------
# Create a partially transparent solid model from volume data and a color map.
#
# Call update_model() to display the model with current levels, colors,
# and rendering options.  Argument align can be a model to align with.
#
class Solid:

  def __init__(self, name, matrix, matrix_id, transform,
               align = None, message_cb = None):

    self.name = name

    self.matrix = matrix
    self.matrix_id = matrix_id          # indicates if matrix changed
    self.matrix_range = None

    self.transform = transform

    self.volume = None                  # Volume_Model
    self.add_handler = None

    from chimera import Model, addModelClosedCallback
    if isinstance(align, Model):
      self.attached_model = align
      addModelClosedCallback(self.attached_model, self.attached_model_closed_cb)
    else:
      self.attached_model = None

    self.message_cb = message_cb

    self.transfer_function = ()
    self.brightness_factor = 1
    self.transparency_depth = 0
    self.colormap_size = 256
    self.clamp = False

    self.color_mode = 'auto8'
    self.c_mode = 'rgba8'
    self.projection_mode = 'auto'
    self.p_mode = '2d-xyz'
    self.use_plane_callback = True      # Avoids allocating 3d color array
    self.dim_transparent_voxels = True
    self.bt_correction = False
    self.minimal_texture_memory = False
    self.maximum_intensity_projection = False
    self.linear_interpolation = True
    self.show_outline_box = True
    self.outline_box_rgb = (1,1,1)
    self.outline_box_linewidth = 1

    self.update_colors = False
    
  # ---------------------------------------------------------------------------
  #
  def message(self, text, large_data_only = True):

    if self.message_cb:
      if large_data_only and self.matrix.size <= (1 << 26):
          return
      self.message_cb(text)

  # ---------------------------------------------------------------------------
  #
  def set_matrix(self, matrix, matrix_id):

    if matrix_id != self.matrix_id:
      self.matrix = matrix
      self.matrix_id = matrix_id
      self.matrix_range = None
      self.p_mode = self.auto_projection_mode()
      self.update_colors = True

  # ---------------------------------------------------------------------------
  #
  def set_colormap(self, transfer_function,
                   brightness_factor, transparency_depth, clamp = False):

    if (self.transfer_function != transfer_function or 
        self.brightness_factor != brightness_factor or
        self.transparency_depth != transparency_depth or
        self.clamp != clamp):
      self.transfer_function = transfer_function
      self.brightness_factor = brightness_factor
      self.transparency_depth = transparency_depth
      self.clamp = clamp
      self.c_mode = self.auto_color_mode()              # update color mode
      self.update_colors = True
      
  # ---------------------------------------------------------------------------
  # After setting options need to call update_model() update display.
  #
  def set_options(self, color_mode, projection_mode,
                  dim_transparent_voxels, bt_correction, minimal_texture_memory,
		  maximum_intensity_projection, linear_interpolation,
                  show_outline_box, outline_box_rgb, outline_box_linewidth):
    
    self.update_colors = (color_mode != self.color_mode)
    self.color_mode = color_mode
    self.c_mode = self.auto_color_mode()
    self.projection_mode = projection_mode
    self.p_mode = self.auto_projection_mode()
    self.dim_transparent_voxels = dim_transparent_voxels
    self.bt_correction = bt_correction
    self.minimal_texture_memory = minimal_texture_memory
    self.maximum_intensity_projection = maximum_intensity_projection
    self.linear_interpolation = linear_interpolation
    self.show_outline_box = show_outline_box
    self.outline_box_rgb = outline_box_rgb
    self.outline_box_linewidth = outline_box_linewidth
    
  # ---------------------------------------------------------------------------
  #
  def set_transform(self, transform):

    self.transform = transform

  # ---------------------------------------------------------------------------
  #
  def update_model(self, open = True):

    create_volume = self.volume is None
    if create_volume:
      self.volume = self.make_model()

    v = self.volume
    v.set_array_coordinates(self.transform)
    v.color_mode = self.c_mode
    v.set_modulation_rgba(self.luminance_color())
    v.projection_mode = self.p_mode
    if self.dim_transparent_voxels:
      bmode = v.SRC_ALPHA_DST_1_MINUS_ALPHA
    else:
      bmode = v.SRC_1_DST_1_MINUS_ALPHA
    v.transparency_blend_mode = bmode
    v.brightness_and_transparency_correction = self.bt_correction
    v.minimal_texture_memory = self.minimal_texture_memory
    v.maximum_intensity_projection = self.maximum_intensity_projection
    v.linear_interpolation = self.linear_interpolation
    v.show_outline_box = self.show_outline_box
    v.outline_box_rgb = self.outline_box_rgb
    v.outline_box_linewidth = self.outline_box_linewidth

    if create_volume or self.update_colors:
      self.update_colors = False
      self.update_coloring()

    self.volume.display = True

    if create_volume and open:
      am = self.attached_model
      from chimera import openModels
      if am and not am in openModels.list():
        # Defer adding model to model list until attached model is added so
        # that the solid model with have the same id number as attached model.
        self.add_handler = openModels.addAddHandler(self.open_model_cb, None)
      else:
        self.open_model()
    
  # ---------------------------------------------------------------------------
  #
  def make_model(self):

    import _volume
    volume = _volume.Volume_Model()
    volume.name = self.name

    return volume
    
  # ---------------------------------------------------------------------------
  #
  def open_model(self):

    from chimera import openModels, addModelClosedCallback
    openModels.add([self.volume], sameAs = self.attached_model)
    addModelClosedCallback(self.volume, self.model_closed_cb)
    
  # ---------------------------------------------------------------------------
  # Defer adding model to model list until attached model is added so
  # that the solid model with have the same id number as attached model.
  #
  def open_model_cb(self, trigger_name, x, models):

    am = self.attached_model
    if am is None or am in models:
      from chimera import openModels
      openModels.deleteAddHandler(self.add_handler)
      self.add_handler = None
      self.open_model()
    
  # ---------------------------------------------------------------------------
  #
  def update_coloring(self):

    self.message('Setting texture colors')
    if self.use_plane_callback:
      cmap, cmap_range = self.colormap()
      def get_color_plane(axis, plane, cmap = cmap, cmap_range = cmap_range):
        s = [slice(None), slice(None), slice(None)]
        s[2-axis] = plane
        colors = self.color_values(s, cmap, cmap_range)
        return colors
      zsize, ysize, xsize = self.matrix.shape
      self.volume.set_color_plane_callback((xsize,ysize,zsize), get_color_plane)
    else:
      colors = self.color_values()
      self.volume.set_volume_colors(colors)
    self.message('')

  # ---------------------------------------------------------------------------
  #
  def color_values(self, slice = None, cmap = None, cmap_range = None):

    if slice is None or 0 in slice:
      self.message('Coloring %s' % self.name)

    if cmap is None:
      cmap, cmap_range = self.colormap()
    dmin, dmax = cmap_range

    m = self.matrix
    if slice:
      m = m[slice]

    colors = self.color_array(cmap.dtype, tuple(m.shape) + (cmap.shape[1],))
    import _volume
    if slice:
      _volume.data_to_colors(m, dmin, dmax, cmap, self.clamp, colors)
    else:
      for z in range(m.shape[0]):
        _volume.data_to_colors(m[z:z+1,:,:], dmin, dmax, cmap, self.clamp,
                               colors[z:z+1,:,:])

    if hasattr(self, 'mask_colors'):
      self.mask_colors(colors, slice = slice)

    if slice is None or [True for a in range(3)
                         if slice[a] == self.matrix.shape[a]-1]:
      self.message('')

    return colors

  # ---------------------------------------------------------------------------
  # Reuse current volume color array if it has correct size.
  # This gives 2x speed-up over allocating a new array when flipping
  # through planes.
  #
  def color_array(self, ctype, cshape):

    v = self.volume
    if hasattr(v, 'colors'):
      colors = v.colors
      if colors.dtype == ctype and tuple(colors.shape) == cshape:
        return colors

    from numpy import empty
    try:
      colors = empty(cshape, ctype)
    except MemoryError:
      self.message("Couldn't allocate color array of size (%d,%d,%d,%d) region" % cshape, large_data_only = False)
      raise
    v.colors = colors        # TODO: make sure this array is freed.
    return colors
  
  # ---------------------------------------------------------------------------
  # Returned values are uint8 or uint16 with 4 (BGRA), 3 (BGR), 2 (LA), or 1 (L)
  # components per color depending on color mode.
  # Transparency and brightness adjustments are applied to transfer function.
  #
  def colormap(self):

    tf = self.transfer_function
    if len(tf) < 2:
      return None

    if self.c_mode.startswith('l'):
      tf, mc = luminance_transfer_function(tf)

    size, drange, ctype = self.colormap_properties()
    dmin, dmax = drange

    # Convert transfer function to a colormap.
    from numpy import zeros, float32
    tfcmap = zeros((size,4), float32)
    from _volume import transfer_function_colormap
    transfer_function_colormap(tf, dmin, dmax, tfcmap)

    # Adjust brightness of RGB components.
    bf = self.brightness_factor
    tfcmap[:,:3] *= bf

    # Modify colormap transparency.
    td = self.transparency_depth
    if not td is None:
      planes = td * min(self.matrix.shape)
      alpha = tfcmap[:,3]
      if planes == 0:
        alpha[:] = 1
      else:
        trans = (alpha < 1)         # Avoid divide by zero for alpha == 1.
        atrans = alpha[trans]
        alpha[trans] = 1.0 - (1.0-atrans) ** (1.0/(planes*(1-atrans)))

    # Use only needed color components (e.g. bgra, la, l).
    cmap = self.rgba_to_colormap(tfcmap)

    # Convert from float to uint8 or uint16.
    from numpy import empty
    icmap = empty(cmap.shape, ctype)
    import _volume
    _volume.colors_float_to_uint(cmap, icmap)

    return icmap, drange
  
  # ---------------------------------------------------------------------------
  #
  def colormap_properties(self):

    # Color component type
    from numpy import uint8, int8, uint16, int16
    m = self.c_mode
    if m.endswith('8') or m.endswith('4'):      t = uint8
    elif m.endswith('16') or m.endswith('12'):  t = uint16
    else:                                       t = uint8

    # If data is 8-bit or 16-bit integer (signed or unsigned) then use data
    # full type range for colormap so data can be used as colormap index.
    dtype = self.matrix.dtype.type
    if dtype in (uint8, int8, uint16, int16):
      drange = dmin, dmax = value_type_range(dtype)
      size = (dmax - dmin + 1)
      return size, drange, t

    size = min(self.colormap_size, 2 ** 16)

    tf = self.transfer_function
    drange = tf[0][0], tf[-1][0]

    return size, drange, t

  # ---------------------------------------------------------------------------
  # Convert rgba colormap to format appropriate for color mode (e.g. la).
  #
  def rgba_to_colormap(self, colormap):

    c = self.colormap_components()
    from numpy import empty
    cmap = empty((colormap.shape[0],len(c)), colormap.dtype)
    for i,ci in enumerate(c):
      cmap[:,i] = colormap[:,ci]
    return cmap

  # ---------------------------------------------------------------------------
  # Tuple of colormap component numbers 0=R, 1=G, 2=B, 3=A for mapping RGBA
  # to a format appropriate for color mode.
  #
  def colormap_components(self):

    m = self.c_mode
    if m.startswith('rgba'):    c = (2,1,0,3)  # BGRA
    elif m.startswith('rgb'):   c = (2,1,0)    # BGR
    elif m.startswith('la'):    c = (0,3)      # RA
    elif m.startswith('l'):     c = (0,)       # R
    else:                       c = (2,1,0,3)  # BGRA
    return c

  # ---------------------------------------------------------------------------
  # 
  def auto_color_mode(self):

    cm = self.color_mode
    if cm.startswith('auto'):
      from numpy import array
      tf = array(self.transfer_function)
      if len(tf) == 0: m = 'rgba'
      else:
        
        if colinear(tf[:,2:5], 0.99):      m = 'l'   # single color
        else:                              m = 'rgb' # multi color
        td = self.transparency_depth
        if td > 0 or td is None:
          opaque = ((tf[:,5] == 1).all() and (tf[:,1] == 1).all())
          if not opaque: m += 'a'
      m += cm[4:] # Append bit count, stripping off "auto" prefix from cm.
    else:
      m = cm
    return m

  # ---------------------------------------------------------------------------
  #
  def luminance_color(self):

    if self.c_mode.startswith('l'):
      ltf, rgba = luminance_transfer_function(self.transfer_function)
    else:
      rgba = (1,1,1,1)
    return rgba

  # ---------------------------------------------------------------------------
  # 
  def auto_projection_mode(self):

    pm = self.projection_mode
    if pm == 'auto':
      s = self.matrix.shape
      smin, smid = sorted(s)[:2]
      aspect_cutoff = 4
      if smin > 0 and aspect_cutoff*smin <= smid:
        pm = ('2d-z','2d-y','2d-x')[list(s).index(smin)]
      else:
        pm = '2d-xyz'
    return pm

  # ---------------------------------------------------------------------------
  #
  def model(self):

    return self.volume
    
  # ---------------------------------------------------------------------------
  #
  def close_model(self):

    v = self.volume
    if v:
      from chimera import openModels
      openModels.close([v])
    
  # ---------------------------------------------------------------------------
  #
  def model_closed_cb(self, model):

    if model == self.volume:
      self.volume = None
      
  # ---------------------------------------------------------------------------
  #
  def attached_model_closed_cb(self, model):

    self.attached_model = None

# -----------------------------------------------------------------------------
#
def luminance_transfer_function(tf):

  if len(tf) == 0:
    return tf

  ltf = []
  for v,i,r,g,b,a in tf:
    l = 0.3*r + 0.59*g + 0.11*b
    ltf.append((v,i,l,l,l,a))

  # Normalize to make maximum luminance = 1
  from numpy import argmax
  lmi = argmax([r for v,i,r,g,b,a in ltf])
  lmax = ltf[lmi][2]
  if lmax != 0:
    ltf = [(v,i,r/lmax,g/lmax,b/lmax,a) for v,i,r,g,b,a in ltf]
  lcolor = tuple(tf[lmi][2:5]) + (1,)

  return ltf, lcolor

# -----------------------------------------------------------------------------
#
def colinear(vlist, tolerance = 0.99):

  from numpy import inner
  vnz = [v for v in vlist if inner(v,v) > 0]
  if len(vnz) <= 1:
    return True
  v0 = vnz[0]
  m0 = inner(v0,v0)
  t2 = tolerance * tolerance
  for v in vnz[1:]:
    m = inner(v,v0)
    m2 = m*m
    if m2 < t2 * m0 * inner(v,v):
      return False
  return True

# -----------------------------------------------------------------------------
#
def value_type_range(numpy_type):

  from numpy import uint8, int8, uint16, int16
  tsize = {
    uint8: (0, 255),
    int8: (-128, 127),
    uint16: (0, 65535),
    int16: (-32768, 32767),
    }
  return tsize.get(numpy_type, (None, None))
