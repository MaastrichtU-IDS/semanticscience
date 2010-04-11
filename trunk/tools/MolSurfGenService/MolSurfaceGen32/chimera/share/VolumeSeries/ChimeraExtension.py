import chimera.extension

# -----------------------------------------------------------------------------
#
class Volume_Series_EMO(chimera.extension.EMO):

  def name(self):
    return 'Volume Series'
  def description(self):
    return 'Control display of sequences of volume data sets'
  def categories(self):
    return ['Volume Data']
  def icon(self):
    return None
  def activate(self):
    self.module('gui').show_volume_series_dialog()
    return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Volume_Series_EMO(__file__))

# -----------------------------------------------------------------------------
#
def open_priism_time_series(path):
  from VolumeSeries import openpriism
  return openpriism.open_priism_time_series(path)

# -----------------------------------------------------------------------------
#
from chimera import fileInfo
fileInfo.register('Priism time series', open_priism_time_series,
		  ['.xyzt'], ['priism_t'], canDecompress = False)
