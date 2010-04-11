# -----------------------------------------------------------------------------
# Scale, shift, and change value type of volume values.
#
def scaled_volume(v = None, scale = 1, shift = 0, type = None,
                 step = None, subregion = None, model_id = None):

  if v is None:
    from VolumeViewer import active_volume
    v = active_volume()
    if v is None:
      return

  sd = scaled_grid(v, scale, shift, type, subregion, step)
  import VolumeViewer
  sv = VolumeViewer.volume_from_grid_data(sd, model_id = model_id)
  return sv

# -----------------------------------------------------------------------------
#
def scaled_grid(v, scale, shift, type, subregion = None, step = 1,
                region = None):
  if region is None:
    d = v.grid_data(subregion, step, mask_zone = False)
  else:
    from VolumeData import Grid_Subregion
    d = Grid_Subregion(v.data, *region)
  sd = Scaled_Grid(d, scale, shift, type)
  return sd

# -----------------------------------------------------------------------------
#
from VolumeData import Grid_Data
class Scaled_Grid(Grid_Data):
  
  def __init__(self, grid_data, scale, shift, value_type):

    self.grid_data = g = grid_data
    self.scale = scale
    self.shift = shift
    self.value_type = vt = (value_type or g.value_type)
    Grid_Data.__init__(self, g.size, vt, g.origin, g.step,
                       g.cell_angles, g.rotation, g.symmetries,
                       name = g.name + ' scaled', default_color = g.rgba)
    
  # ---------------------------------------------------------------------------
  #
  def read_matrix(self, ijk_origin, ijk_size, ijk_step, progress):

    data = self.grid_data.read_matrix(ijk_origin, ijk_size, ijk_step, progress)
    s = self.scale
    o = self.shift
    t = self.value_type
    if s == 1 and o == 0:
      dt = data
    else:
      # Convert to float32, then scale and shift.
      from numpy import float32, multiply, add
      dt = data.astype(float32)
      if o != 0:
        add(dt, o, dt)
      if s != 1:
        multiply(dt, s, dt)

    if t == dt.dtype:
      d = dt
    else:
      from numpy import dtype
      if dtype(t).kind in 'iu':
        # Clamp integer types to limit values.
        from numpy import empty, iinfo
        d = empty(dt.shape, t)
        di = iinfo(t)
        dt.clip(di.min, di.max, d)
      else:
        d = dt.astype(t)

    return d
