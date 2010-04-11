# -----------------------------------------------------------------------------
#
def open_priism_time_series(path):

  from VolumeData import open_file
  dlist = open_file(path, 'priism')
  for data in dlist:
    tgrids = map(lambda t: Grid_Data_T(data, t), range(data.num_times))
    from VolumeSeries import Volume_Series, gui
    ts = Volume_Series(data.name, tgrids)
    gui.add_volume_series(ts)
    gui.show_volume_series_dialog()
  models = []
  return models

# -----------------------------------------------------------------------------
#
from VolumeData import Grid_Data

# -----------------------------------------------------------------------------
#
class Grid_Data_T(Grid_Data):

  def __init__(self, data, t):

    self.data = data
    self.time = t

    Grid_Data.__init__(self, data.size, data.value_type,
                       data.origin, data.step, 
                       name = '%s t=%d' % (data.name, t),
                       file_type = data.file_type,
                       default_color = data.rgba)
    
  # ---------------------------------------------------------------------------
  #
  def read_matrix(self, ijk_origin, ijk_size, ijk_step, progress):

    return self.data.read_matrix(ijk_origin, ijk_size, ijk_step, progress,
                                 self.time)
