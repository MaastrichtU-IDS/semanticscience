# ----------------------------------------------------------------------------
# Modeless grid file open dialog using Chimera OpenSave.
# Dialog displays an error message if opening a file fails.
# Callback function takes a list of grid objects.
#
og_dialog = None
def show_grid_file_browser(title, grid_objects_cb):

  global og_dialog
  if og_dialog == None:
    og_dialog = Open_Grids_Dialog(title, grid_objects_cb)
  else:
    og_dialog.grid_objects_cb = grid_objects_cb
    og_dialog._toplevel.title(title)
    og_dialog.enter()

# ----------------------------------------------------------------------------
# Modal grid file open dialog using Chimera OpenSave.
# Dialog displays an error message if opening a file fails and waits
# for an acceptable file or Cancel to be pressed.
#
def select_grids(parent_widget, title, message):

  d = Open_Grid_Modal_Dialog(parent_widget, title)
  return d.get_grids(message)

# ----------------------------------------------------------------------------
#
def select_save_path(save_cb = None):

  if save_cb:
    select_save_path_modeless(save_cb)
    return

  from fileformats import file_writers
  filters = map(lambda fw: (fw[0], ['*'+fw[2]], fw[2]), file_writers)
  from OpenSave import SaveModal
  d = SaveModal(title = "Save Volume Data",
                filters = filters, defaultFilter = 0)
  from chimera.tkgui import app
  paths_and_types = d.run(app)
  if paths_and_types:
    paths_and_types = file_descriptions_to_types(paths_and_types)
    if len(paths_and_types) >= 1:
      return paths_and_types[0]
  return None, None
    
# -----------------------------------------------------------------------------
#
def select_save_path_modeless(save_cb):

  from fileformats import file_writers
  filters = map(lambda fw: (fw[0], ['*'+fw[2]], fw[2]), file_writers)

  def save(okay, d, save_cb = save_cb):
    if not okay:
      return
    paths_and_types = d.getPathsAndTypes()
    if len(paths_and_types) == 0:
      return
    path, file_type = paths_and_types[0]
    save_cb(path, file_type)

  from OpenSave import SaveModeless
  d = SaveModeless(title = "Save Volume Data",
                   filters = filters, defaultFilter = 0, command = save)
    
# -----------------------------------------------------------------------------
#
from OpenSave import OpenModeless
class Open_Grids_Dialog(OpenModeless):

  def __init__(self, title, grid_objects_cb):

    self.grid_objects_cb = grid_objects_cb

    OpenModeless.__init__(self, title = title,
                          filters = file_type_filters(),
                          defaultFilter="all (guess type)")

  # ---------------------------------------------------------------------------
  #
  def Apply(self):

    paths_and_types = file_descriptions_to_types(self.getPathsAndTypes())
    grids, error_message = open_grid_files(paths_and_types)
    if error_message:
      from chimera import replyobj
      replyobj.error(error_message)
    self.grid_objects_cb(grids)
    
# -----------------------------------------------------------------------------
#
from OpenSave import OpenModal
class Open_Grid_Modal_Dialog(OpenModal):

  def __init__(self, parent_widget, title):

    self.parent_widget = parent_widget

    OpenModal.__init__(self,
                       title = title,
                       filters = file_type_filters(),
                       defaultFilter="all (guess type)",
                       clientPos = 's',
                       clientSticky = 'w')
    
  # ---------------------------------------------------------------------------
  #
  def fillInUI(self, parent):

    OpenModal.fillInUI(self, parent)

    import Tkinter
    msg = Tkinter.Label(self.clientArea, justify='left', anchor='w',
                        wraplength = '10c')     # 10 centimeters
    msg.grid(row=0, column=0, sticky='w')
    self.message = msg
    
  # ---------------------------------------------------------------------------
  #
  def get_grids(self, message):

    self.message['text'] = message
    return self.run(self.parent_widget)

  # ---------------------------------------------------------------------------
  # Don't close if there was an error opening a file.
  # The error message is displayed in the open file dialog.
  #
  def Open(self):

    paths_and_types = file_descriptions_to_types(self.getPathsAndTypes())
    grids, error_message = open_grid_files(paths_and_types)
    if error_message:
      self.message['text'] = error_message
    elif grids:
      self.returnValue = grids
      self.Cancel(self.returnValue)
    
# -----------------------------------------------------------------------------
#
def file_type_filters():

  from fileformats import file_types

  filters = []
  for descrip, name, prefix_list, suffix_list, batch in file_types:
    suffix_patterns = map(lambda s: '*.' + s, suffix_list)
    filters.append((descrip, suffix_patterns))

  return filters

# -----------------------------------------------------------------------------
#
def description_to_type_table():

  d2t = {}
  from fileformats import file_types
  for ft in file_types:
    d2t[ft[0]] = ft[1]

  return d2t

# -----------------------------------------------------------------------------
#
def type_to_description_table():

  t2d = {}
  from fileformats import file_types
  for ft in file_types:
    t2d[ft[1]] = ft[0]

  return t2d

# -----------------------------------------------------------------------------
#
def file_descriptions_to_types(paths_and_descrips):

  d2t = description_to_type_table()
  paths_and_types = []
  for path, descrip in paths_and_descrips:
    if d2t.has_key(descrip):
      type = d2t[descrip]
    else:
      type = None
    paths_and_types.append((path, type))
  return paths_and_types

# -----------------------------------------------------------------------------
#
def open_grid_files(paths_and_types, stack_images = True):

  grids = []
  error_message = ''
  unknown_type_paths = []
  from fileformats import open_file, File_Format_Error
  if stack_images:
    paths_and_types = batch_paths(paths_and_types)
  for path, file_type in paths_and_types:
    if file_type:
      try:
        glist = open_file(path, file_type)
        grids.extend(glist)
      except (IOError, SyntaxError, File_Format_Error), e:
        from os.path import basename
        if isinstance(path, (list,tuple)):
          descrip = '%s ... (%d files)' % (basename(path[0]), len(path))
        else:
          descrip = basename(path)
        msg = 'File %s, format %s\n%s\n' % (descrip, file_type, str(e))
        error_message = error_message + msg
    else:
      unknown_type_paths.append(path)

  if unknown_type_paths:
    import os.path
    file_names = map(os.path.basename, unknown_type_paths)
    files = ', '.join(file_names)
    msg = 'Unknown file types for %s' % files
    error_message = error_message + msg

  return grids, error_message

# ----------------------------------------------------------------------------
#
def batch_paths(paths_and_types):

  pt = []
  bp = []
  t2d = type_to_description_table()
  from chimera import fileInfo
  for path, ftype in paths_and_types:
    if isinstance(path, (tuple,list)) or not fileInfo.batch(t2d[ftype]):
      pt.append((path, ftype))
    else:
      bp.append((path, ftype))

  # Process file types where paths are batched to open one model.
  bpaths = {}
  for path, ftype in bp:
    if ftype in bpaths:
      bpaths[ftype].append(path)
    else:
      bpaths[ftype] = [path]
  for ftype, paths in bpaths.items():
    pt.append((tuple(paths), ftype))

  return pt
