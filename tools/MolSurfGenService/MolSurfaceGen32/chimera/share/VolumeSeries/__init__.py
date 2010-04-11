# -----------------------------------------------------------------------------
#
class Volume_Series:

  def __init__(self, name, data_sets):

    self.name = name
    self.data_sets = set(data_sets)
    self.data_regions = []

    for t,d in enumerate(data_sets):
      d.time = t

    self.surface_level_ranks = []  # Cached for normalization calculation
    self.solid_level_ranks = []  # Cached for normalization calculation

  # ---------------------------------------------------------------------------
  #
  def number_of_times(self):

    return len(self.data_sets)
    
  # ---------------------------------------------------------------------------
  #
  def data_time(self, data):

    if data in self.data_sets:
      return data.time
    return None
    
  # ---------------------------------------------------------------------------
  #
  def show_in_volume_viewer(self):

    data_seq = list(self.data_sets)
    data_seq.sort(lambda a,b: cmp(a.time, b.time))
    from VolumeViewer import volume_from_grid_data
    data_regions = [volume_from_grid_data(g, show_data = False)
                    for g in data_seq]
    self.data_regions = list(data_regions)

    # Add callbacks to detect when volume data sets are closed.
    import chimera
    for v in data_regions:
      chimera.addModelClosedCallback(v, self.volume_closed)

    if data_regions:
      dr = data_regions[0]
      from VolumeViewer import set_active_volume
      set_active_volume(dr)
      dr.initialize_thresholds()
      dr.show()

  # ---------------------------------------------------------------------------
  #
  def remove_from_volume_viewer(self):

    for dr in self.data_regions:
      if not dr is None:
        dr.close()

  # ---------------------------------------------------------------------------
  #
  def volume_closed(self, data_region):

    d = data_region.data
    self.data_sets.discard(d)
    self.data_regions[d.time] = None

  # ---------------------------------------------------------------------------
  #
  def is_volume_closed(self, t):

    return self.data_regions[t] == None

  # ---------------------------------------------------------------------------
  #
  def show_time(self, time):

    dr = self.data_regions[time]
    if dr == None:
      return

    dr.show()

  # ---------------------------------------------------------------------------
  #
  def unshow_time(self, time, remove_surface):

    dr = self.data_regions[time]
    if dr == None:
      return

    for m in dr.models():
      m.display = False

    if remove_surface:
      dr.remove_surfaces()
      dr.close_solid()

  # ---------------------------------------------------------------------------
  #
  def time_shown(self, time):

    dr = self.data_regions[time]
    shown = (dr and len(filter(lambda m: m.display, dr.models())) > 0)
    return shown

  # ---------------------------------------------------------------------------
  #
  def surface_model(self, time):

    return self.data_regions[time]

  # ---------------------------------------------------------------------------
  #
  def show_time_in_volume_dialog(self, time):

    dr = self.data_regions[time]
    if dr == None:
      return

    from VolumeViewer import set_active_volume
    set_active_volume(dr)

  # ---------------------------------------------------------------------------
  #
  def copy_display_parameters(self, t1, t2, normalize_thresholds = False):

    dr1 = self.data_regions[t1]
    dr2 = self.data_regions[t2]
    if dr1 == None or dr2 == None:
      return

    dr2.data.set_step(dr1.data.step)
    dr2.data.set_origin(dr1.data.origin)
    dr2.copy_settings_from(dr1)
    if normalize_thresholds:
      self.copy_threshold_rank_levels(dr1, dr2)

  # ---------------------------------------------------------------------------
  #
  def copy_threshold_rank_levels(self, v1, v2):

    levels, ranks = equivalent_rank_values(v1, v1.surface_levels,
                                           v2, v2.surface_levels,
                                           self.surface_level_ranks)
    v2.surface_levels = levels
    self.surface_level_ranks = ranks

    lev1 = [l for l,b in v1.solid_levels]
    lev2 = [l for l,b in v2.solid_levels]
    levels, ranks = equivalent_rank_values(v1, lev1, v2, lev2,
                                           self.solid_level_ranks)
    v2.solid_levels = zip(levels, [b for lev,b in v1.solid_levels])
    self.solid_level_ranks = ranks

# -----------------------------------------------------------------------------
# Avoid creep due to rank -> value and value -> rank not being strict inverses
# by using passed in ranks if they match given values.
#
def equivalent_rank_values(v1, values1, v2, values2, ranks):

  ms1 = v1.matrix_value_statistics()
  ms2 = v2.matrix_value_statistics()
  rlev = [ms1.rank_data_value(r) for r in ranks]
  if rlev != values1:
    ranks = [ms1.data_value_rank(lev) for lev in values1]
  if [ms2.data_value_rank(lev) for lev in values2] != ranks:
    values2 = [ms2.rank_data_value(r) for r in ranks]
  return values2, ranks
