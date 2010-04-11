# ----------------------------------------------------------------------------
#
os_dialog = None
def open_series_files():

  global os_dialog
  if os_dialog == None:
    os_dialog = Open_Series_Dialog()
  else:
    os_dialog.enter()

# -----------------------------------------------------------------------------
#
import OpenSave
class Open_Series_Dialog(OpenSave.OpenModeless):

  def __init__(self):

    from VolumeData.opendialog import file_type_filters
    filters = file_type_filters()

    self.priism_type = 'Priism time series'
    filters.append((self.priism_type, ['*.xyzt']))
    
    OpenSave.OpenModeless.__init__(self,
                                   title = 'Open Volume Series',
                                   filters = filters,
                                   clientPos = 's',
                                   clientSticky = 'w')
    
  # ---------------------------------------------------------------------------
  #
  def fillInUI(self, parent):

    OpenSave.OpenModeless.fillInUI(self, parent)

    import Tkinter
    msg = Tkinter.Label(self.clientArea, justify='left', anchor='w',
                        wraplength = '10c')     # 10 centimeters
    msg.grid(row=0, column=0, sticky='w')
    self.message = msg

  # ---------------------------------------------------------------------------
  # Don't close if there was an error opening a file.
  # The error message is displayed in the open file dialog.
  #
  def OK(self):

    if self.Apply():
      self.Close()

  # ---------------------------------------------------------------------------
  # Handle single and multiple file series.
  #
  def Apply(self):

    paths_and_types = self.getPathsAndTypes()
    pdlist = []
    for path, type in paths_and_types:
        if type == self.priism_type:
            import openpriism
            openpriism.open_priism_time_series(path)
        else:
            pdlist.append((path, type))
  
    from VolumeData import opendialog
    ptlist = opendialog.file_descriptions_to_types(pdlist)
    grids, error_message = opendialog.open_grid_files(ptlist)
    self.message['text'] = error_message

    if grids:
      sgrids = list(grids)
      sgrids.sort(lambda g1,g2: cmp(g1.name, g2.name))
      from VolumeSeries import Volume_Series, gui
      ts = Volume_Series(sgrids[0].name, sgrids)
      gui.add_volume_series(ts)
      gui.show_volume_series_dialog()

    return error_message == ''
