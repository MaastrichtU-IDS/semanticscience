# -----------------------------------------------------------------------------
# Menu widget for choosing a volume data set.
#
class Volume_Menu:

  def __init__(self, parent, label = '', command = None, open_button = None,
               show_on_open = False):

    import Tkinter
    f = Tkinter.Frame(parent)
    self.frame = f

    from chimera.widgets import ModelOptionMenu
    m = ModelOptionMenu(f, labelpos = 'w', label_text = label,
                        listFunc = volume_models, command = command)
    m.grid(row = 0, column = 0, sticky = 'w')
    self.menu = m

    if open_button:
      if not type(open_button) is str:
        open_button = 'Browse...'
      bb = Tkinter.Button(f, text = open_button, command = self.open_volume_cb)
      bb.grid(row = 0, column = 1, sticky = 'w')

    self.show_on_open = show_on_open
    
  # ---------------------------------------------------------------------------
  #
  def volume(self):

    v = self.menu.getvalue()
    if v == 'browse...':
      return None
    return v

  # ---------------------------------------------------------------------------
  #
  def set_volume(self, v):

    m = self.menu
    if v in m.valueMap:
      m.setvalue(v)

  # ---------------------------------------------------------------------------
  # Deprecated.  Use volume(), set_volume().
  #
  def data_region(self):
    return self.volume()
  def set_data_region(self, dr):
    self.set_volume(dr)
    
  # ---------------------------------------------------------------------------
  #
  def open_volume_cb(self):

    def open_volumes(vlist):
      if vlist:
        self.menu.setvalue(vlist[0])
      
    from volumedialog import show_volume_file_browser
    show_volume_file_browser('Open Volume File', open_volumes,
                             show_data = self.show_on_open,
                             show_volume_dialog = self.show_on_open)
    
# -----------------------------------------------------------------------------
#
def volume_models():

  from volume import Volume
  from chimera import openModels
  vlist = openModels.list(modelTypes = [Volume])
  return vlist
