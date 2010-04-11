# -----------------------------------------------------------------------------
# Graphical user interface to display surfaces, meshes, and transparent solids
# for 3 dimensional grid data.
#
import Tkinter

import chimera
from chimera.baseDialog import ModelessDialog
from CGLtk import Hybrid

# -----------------------------------------------------------------------------
#
class Volume_Dialog(ModelessDialog):

  title = 'Volume Viewer'
  name = 'volume viewer'
  buttons = ('Update', 'Center', 'Orient', 'Close',)
  help = 'ContributedSoftware/volumeviewer/framevolumeviewer.html'
  
  def fillInUI(self, parent):

    self.gui_panels = []

    self.focus_region = None
    self.menu_volumes = []

    self.redisplay_in_progress = False

    tw = parent.winfo_toplevel()
    self.toplevel_widget = tw
    tw.withdraw()

    parent.columnconfigure(0, weight = 1)
    row = 1

    menubar = Tkinter.Menu(parent, type = 'menubar', tearoff = False)
    tw.config(menu = menubar)

    file_menu_entries = (('Open map...', self.open_cb),
                         ('Save map as...', self.save_data_cb),
                         ('Duplicate', self.duplicate_cb),
                         ('Remove surface', self.remove_surface_cb),
                         ('Close map', self.close_data_cb),
                         )
    Hybrid.cascade_menu(menubar, 'File', file_menu_entries)

    # Order of panel_classes determines top to bottom location in dialog.
    panel_classes = (Hybrid.Feature_Buttons_Panel,
                     Data_List_Panel,
                     Precomputed_Subsamples_Panel, Coordinates_Panel,
                     Thresholds_Panel, Brightness_Transparency_Panel,
                     Display_Style_Panel, Plane_Panel,
                     Region_Size_Panel, Subregion_Panel,
                     Zone_Panel, Atom_Box_Panel, Named_Region_Panel,
                     Display_Options_Panel, Solid_Options_Panel,
                     Surface_Options_Panel)

    for pc in panel_classes:
      p = pc(self, parent)
      p.frame.grid(row = row, column = 0, sticky = 'news')
      p.frame.grid_remove()
      p.panel_row = row
      self.gui_panels.append(p)
      setattr(self, pc.__name__.lower(), p)
      row += 1

    sorted_panels = list(self.gui_panels)
    sorted_panels.sort(lambda p1, p2: cmp(p1.name, p2.name))
    self.feature_buttons_panel.set_panels(sorted_panels)

    fmenu = Hybrid.cascade_menu(menubar, 'Features')
    for p in sorted_panels:
      fmenu.add_checkbutton(label = p.name,
                            variable = p.panel_shown_variable.tk_variable)
    fmenu.add_separator()
    feature_menu_entries = (
      ('Show only default panels', self.show_default_panels_cb),
      ('Save default panels', self.save_default_panels_cb),
      ('Save default dialog settings', self.save_default_settings_cb),
      ('Use factory default settings', self.use_factory_defaults_cb))
    for name, cb in feature_menu_entries:
      fmenu.add_command(label = name, command = cb)
    
    # Make data panel expand vertically when dialog resized
    data_list_panel_row = self.data_list_panel.panel_row
    parent.rowconfigure(data_list_panel_row, weight = 1)

    self.data_menu = Hybrid.cascade_menu(menubar, 'Data')
    from chimera import triggers
    triggers.addHandler('Model', self.volume_name_change_cb, None)

    from chimera.extension import manager
    cat = manager.findCategory('Volume Data')
    tool_menu_entries = [(e.name(), lambda e=e, cat=cat: e.menuActivate(cat))
                         for e in cat.sortedEntries()
                         if e.name() != 'Volume Viewer']
    Hybrid.cascade_menu(menubar, 'Tools', tool_menu_entries)

    from chimera.tkgui import aquaMenuBar
    aquaMenuBar(menubar, parent, row = 0)

    #
    # Specify a label width so dialog is not resized for long messages.
    #
    msg = Tkinter.Label(parent, width = 40, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row += 1
    self.message_label = msg

    ub = self.buttonWidgets['Update']
    self.update_button = ub
    self.update_button_pack_settings = ub.pack_info()
    ub.pack_forget()

    from volume import default_settings
    default_settings.set_gui_to_defaults(self)
    default_settings.add_change_callback(self.default_settings_changed_cb)
    
    # Add any data sets opened prior to volume dialog being created.
    import volume
    drlist = volume.volume_list()
    for dr in drlist:
      self.volume_opened_cb(dr)

    volume.add_volume_opened_callback(self.volume_opened_cb)
    volume.add_volume_closed_callback(self.volume_closed_cb)
    volume.add_session_save_callback(self.save_session_cb)
      
  # ---------------------------------------------------------------------------
  #
  def find_gui_panel(self, name):

    for p in self.gui_panels:
      if p.name == name:
        return p
    return None

  # ---------------------------------------------------------------------------
  #
  def shown_panels(self):

    pshown = filter(lambda p: p.panel_shown_variable.get(), self.gui_panels)
    pshown.sort()
    return pshown

  # ---------------------------------------------------------------------------
  #
  def show_panels(self, pnames):

    for p in self.gui_panels:
      p.panel_shown_variable.set(p.name in pnames)

  # ---------------------------------------------------------------------------
  #
  def update_default_panels(self, pnames):

    # Don't show panel close buttons for default panels.
    for p in self.gui_panels:
      p.show_close_button = not (p.name in pnames)

  # ---------------------------------------------------------------------------
  #
  def show_default_panels_cb(self):

    from volume import default_settings
    self.show_panels(default_settings['shown_panels'])
    
  # ---------------------------------------------------------------------------
  #
  def default_settings_changed_cb(self, default_settings, changes):

    dop = self.display_options_panel
    dop.default_settings_changed(default_settings, changes)
    srp = self.subregion_panel
    srp.default_settings_changed(default_settings, changes)

  # ---------------------------------------------------------------------------
  #
  def save_default_settings_cb(self):

    from volume import default_settings as ds
    ds.set_defaults_from_gui(self, panel_settings = False)
    ds.save_to_preferences_file(panel_settings = False)
    
  # ---------------------------------------------------------------------------
  #
  def save_default_panels_cb(self):

    from volume import default_settings as ds
    ds.set_defaults_from_gui(self, data_settings = False,
                             global_settings = False)
    ds.save_to_preferences_file(data_settings = False, global_settings = False)
    self.update_default_panels(ds['shown_panels'])

  # ---------------------------------------------------------------------------
  #
  def use_factory_defaults_cb(self):

    from volume import default_settings
    default_settings.restore_factory_defaults(self)
    self.redisplay_needed_cb()
    
  # ---------------------------------------------------------------------------
  #
  def save_session_cb(self, file):

    import session
    session.save_volume_dialog_state(self, file)

  # ---------------------------------------------------------------------------
  #
  def open_cb(self):
      
    show_volume_file_browser('Open Volume Files', show_data = True)

  # ---------------------------------------------------------------------------
  # Show data set parameters in dialog but do not render data.
  #
  def volume_opened_cb(self, data_region):

    dr = data_region

    # Set data region status messages to display in volume dialog
    dr.message_cb = self.message

    # Update data list and menu.
    line = dr.name_with_id()
    self.data_list_panel.list_region(line)

    #
    # Have to use id of volume object to avoid a memory leak.
    # In Aqua Chimera 1.2540 deleting data menu entry does not free command
    # leaving a reference to the volume if it is used as an argument.
    #
    cb = lambda i=id(dr): self.data_menu_cb(i)
    self.data_menu.add_command(label = line, command = cb)
    self.menu_volumes.append(dr)

    # Add data values changed callback.
    dr.add_volume_change_callback(self.data_region_changed)

    # Show data parameters.
    self.display_region_info(dr)

    # Show plane panel if needed
    from volume import show_one_plane, default_settings as ds
    if show_one_plane(dr, ds['show_plane'], ds['voxel_limit_for_plane']):
      self.plane_panel.panel_shown_variable.set(True)

  # ---------------------------------------------------------------------------
  #
  def volume_closed_cb(self, data_regions):

    # Remove data menu and data listbox entries.
    mv = self.menu_volumes
    indices = [mv.index(dr) for dr in data_regions]
    indices.sort()
    indices.reverse()
    dm = self.data_menu
    from CGLtk.Hybrid import base_menu_index
    i0 = base_menu_index(dm)
    for i in indices:
      self.data_list_panel.remove_listed_region(i)
      dm.delete(i+i0)
      del mv[i]

    # Remove data changed callbacks
    # Add data values changed callback.
    for dr in data_regions:
      dr.remove_volume_change_callback(self.data_region_changed)

    # Update focus region.
    if self.focus_region in data_regions:
      self.focus_region = None
      import volume
      drlist = volume.volume_list()
      if len(drlist) > 0:
        dr = drlist[0]
      else:
        dr = None
      self.display_region_info(dr)

  # ---------------------------------------------------------------------------
  #
  def volume_name_change_cb(self, trigger, x, changes):

    if 'name changed' in changes.reasons:
      from volume import Volume
      vlist = [m for m in changes.modified
               if isinstance(m, Volume) and m in self.menu_volumes]
      dm = self.data_menu
      from CGLtk.Hybrid import base_menu_index
      i0 = base_menu_index(dm)
      for v in vlist:
        dm.entryconfigure(self.menu_volumes.index(v)+i0, label = v.name)

  # ---------------------------------------------------------------------------
  #
  def data_menu_cb(self, vol_id):

    vol = [v for v in self.menu_volumes if id(v) == vol_id][0]
    self.display_region_info(vol)
    self.redisplay_needed_cb()

  # ---------------------------------------------------------------------------
  #
  def display_region_info(self, data_region):

    self.focus_region = data_region

    for p in self.gui_panels:
      if hasattr(p, 'update_panel_widgets'):
        p.update_panel_widgets(data_region)
      
  # ---------------------------------------------------------------------------
  # Notify all panels that representation changed so they can update gui if
  # it depends on the representation.
  #
  def representation_changed(self, representation):

    for p in self.gui_panels:
      if hasattr(p, 'representation_changed'):
        p.representation_changed(representation)

  # ---------------------------------------------------------------------------
  #
  def selected_regions(self):

    rlist = self.data_list_panel.selected_list_regions()
    if len(rlist) == 0 and self.focus_region:
      rlist = [self.focus_region]
    return rlist
      
  # ---------------------------------------------------------------------------
  #
  def Update(self):

    self.show_cb()
      
  # ---------------------------------------------------------------------------
  #
  def show_cb(self, event = None):

    data_regions = self.selected_regions()
    for dr in data_regions:
      # For region displayed in dialog use the current dialog settings.
      if dr == self.focus_region:
        self.show_using_dialog_settings(dr, recreate_thresholds = True)
      else:
        # Set display style of data regions if needed.
        if dr.representation == None:
          dr.representation = self.display_style_panel.representation.get()
          
        # Set initial thresholds if there are currently no thresholds.
        dr.initialize_thresholds(first_time_only = False)
        dr.show() # Display region not shown in dialog.

  # ---------------------------------------------------------------------------
  #
  def show_region(self, data_region, representation):

    self.display_region_info(data_region)
    self.display_style_panel.representation.set(representation,
                                                invoke_callbacks = 0)
    self.show_using_dialog_settings(data_region)
    
  # ---------------------------------------------------------------------------
  #
  def show_using_dialog_settings(self, data_region,
                                 recreate_thresholds = False):

    dr = data_region
    if dr == None:
      return

    # The voxel limit setting effects the region size panel computation of
    # step size.  So make sure that setting is applied before region size
    # panel settings are used.  Ick.
    dop = self.display_options_panel
    dop.use_gui_settings(dr)

    for p in self.gui_panels:
      if hasattr(p, 'use_gui_settings'):
        p.use_gui_settings(dr)

    dr.initialize_thresholds(first_time_only = not recreate_thresholds)
    dr.show()

  # ---------------------------------------------------------------------------
  # Notify user interface panels of region bounds change.
  #
  def update_region_in_panels(self, ijk_min, ijk_max, ijk_step):
    
    for p in self.gui_panels:
      if hasattr(p, 'update_panel_ijk_bounds'):
        p.update_panel_ijk_bounds(ijk_min, ijk_max, ijk_step)
    
  # ---------------------------------------------------------------------------
  #
  def rendering_options_from_gui(self):

    from volume import Rendering_Options
    ro = Rendering_Options()
    dop = self.display_options_panel
    dop.rendering_options_from_gui(ro)
    slop = self.solid_options_panel
    slop.rendering_options_from_gui(ro)
    sop = self.surface_options_panel
    sop.rendering_options_from_gui(ro)
    return ro
    
  # ---------------------------------------------------------------------------
  # Update display even if immediate redisplay mode is off.
  # This is used when the pressing return in entry fields.
  #
  def redisplay_cb(self, event = None):

    #
    # TODO: probably want to avoid recursive shows just like in
    #  redisplay_needed_cb().  The purpose of avoiding recursive
    #  redisplay is to accumulate many (eg threshold) changes made
    #  when system is responding slowly, so each one does not require
    #  a separate redisplay.
    #
    if self.focus_region:
      self.show_using_dialog_settings(self.focus_region,
                                      recreate_thresholds = True)
    
  # ---------------------------------------------------------------------------
  # Update display if immediate redisplay mode is on.
  #
  def redisplay_needed_cb(self, event = None):

    if self.focus_region == None:
      return

    #
    # While in this routine another redisplay may be requested.
    # Remember so we can keep redisplaying until everything is up to date.
    #
    self.need_redisplay = True

    if self.redisplay_in_progress:
      # Don't try to redisplay if we are in the middle of redisplaying.
      return

    dop = self.display_options_panel
    while dop.immediate_update.get() and self.need_redisplay:
      self.need_redisplay = False
      self.redisplay_in_progress = True
      try:
        self.show_using_dialog_settings(self.focus_region)
      except:
        # Need this to avoid disabling automatic volume redisplay when
        # user cancels file read cancel or out of memory exception raised.
        self.redisplay_in_progress = False
        raise
      self.redisplay_in_progress = False
  
  # ---------------------------------------------------------------------------
  #
  def data_region_changed(self, dr, type):

    tp = self.thresholds_panel

    if type == 'data values changed':
      if tp.histogram_shown(dr):
        tp.update_histograms(dr)

    elif type == 'displayed':
      if not tp.histogram_shown(dr):
        # Histogram, data range, and initial thresholds are only displayed
        #  after data is shown to avoid reading data file for undisplayed data.
        tp.update_panel_widgets(dr, activate = False)

    elif type == 'representation changed':
      tp.update_panel_widgets(dr)
      if dr is self.focus_region:
        dsp = self.display_style_panel
        dsp.update_panel_widgets(dr)

    elif type == 'region changed':
      if tp.histogram_shown(dr):
        tp.update_histograms(dr)
      if dr is self.focus_region:
        self.update_region_in_panels(*dr.region)
        dop = self.display_options_panel
        if dop.adjust_camera.get():
          self.focus_camera_on_region(dr)
      else:
        tp.update_panel_widgets(dr, activate = False)

    elif type == 'thresholds changed':
      tp.update_panel_widgets(dr, activate = False)

    elif type == 'colors changed':
      tp.update_panel_widgets(dr, activate = False)
      if dr is self.focus_region:
        btp = self.brightness_transparency_panel
        btp.update_panel_widgets(dr)

    elif type == 'voxel limit changed':
      dop = self.display_options_panel
      dop.set_gui_voxel_limit(dr.rendering_options)

    elif type == 'coordinates changed':
      if dr is self.focus_region:
        cp = self.coordinates_panel
        cp.update_panel_widgets(dr)

    elif type == 'rendering options changed':
      if dr is self.focus_region:
        for p in (self.display_options_panel, self.surface_options_panel,
                  self.solid_options_panel):
          p.update_panel_widgets(dr)

  # ---------------------------------------------------------------------------
  #
  def Center(self):

    self.center_cb()

  # ---------------------------------------------------------------------------
  #
  def center_cb(self):

    if self.focus_region:
      self.focus_camera_on_region(self.focus_region)

  # ---------------------------------------------------------------------------
  #
  def focus_camera_on_region(self, data_region):

    xform = data_region.model_transform()
    if xform == None:
      return

    xyz_min, xyz_max = data_region.xyz_bounds()
    dx, dy, dz = map(lambda a,b: b-a, xyz_min, xyz_max)
    import math
    view_radius = .5 * math.sqrt(dx*dx + dy*dy + dz*dz)

    center = map(lambda a,b: .5*(a+b), xyz_min, xyz_max)
    center_point = apply(chimera.Point, center)
    center_eye = xform.apply(center_point)          # in eye coordinates
    v = chimera.viewer
    c = v.camera
    c.center = (center_eye.x, center_eye.y, center_eye.z)

    v.viewSize = view_radius
    v.scaleFactor = 1
    v.clipping = False
      
  # ---------------------------------------------------------------------------
  #
  def Orient(self):

    self.orient_cb()

  # ---------------------------------------------------------------------------
  #
  def orient_cb(self):

    data_region = self.focus_region
    if data_region == None:
      return
    
    xform = data_region.model_transform()
    if xform == None:
      return

    xyz_min, xyz_max = data_region.xyz_bounds()
    cx, cy, cz = map(lambda a,b: .5*(a+b), xyz_min, xyz_max)
    c = chimera.Point(cx, cy, cz)
    ceye = xform.apply(c)
    xf1 = chimera.Xform.translation(-ceye.x, -ceye.y, -ceye.z)
    axis, angle = xform.getRotation()
    xf2 = chimera.Xform.rotation(axis, -angle)
    xf3 = chimera.Xform.translation(ceye.x, ceye.y, ceye.z)
    xf = chimera.Xform.identity()
    xf.multiply(xf3)
    xf.multiply(xf2)
    xf.multiply(xf1)

    ostates = {}
    for m in chimera.openModels.list(all = 1):
      ostates[m.openState] = 1

    active_ostates = filter(lambda ostate: ostate.active, ostates.keys())
    for ostate in active_ostates:
      ostate.globalXform(xf)
      
  # ---------------------------------------------------------------------------
  #
  def unshow_cb(self):

    for r in self.selected_regions():
      r.unshow()

  # ---------------------------------------------------------------------------
  #
  def save_data_cb(self):

    from VolumeData import select_save_path
    select_save_path(self.save_dialog_cb)

  # ---------------------------------------------------------------------------
  #
  def save_dialog_cb(self, path, file_type):

    dr = self.focus_region
    if dr == None:
      return

    try:
      dr.write_file(path, file_type)
    except ValueError, e:
      from chimera.replyobj import warning
      warning('File not saved. %s.' % e)

  # ---------------------------------------------------------------------------
  #
  def duplicate_cb(self):

    r = self.focus_region
    if r == None:
      return

    dr = r.copy()
    self.display_region_info(dr)
    dr.show()
  
  # ---------------------------------------------------------------------------
  #
  def CloseData(self):

    self.close_data_cb()
      
  # ---------------------------------------------------------------------------
  #
  def close_data_cb(self):

    import volume
    volume.remove_volumes(self.selected_regions())
    
  # ---------------------------------------------------------------------------
  #
  def remove_surface_cb(self):

    for dr in self.selected_regions():
      dr.remove_surfaces()
    
  # ---------------------------------------------------------------------------
  #
  def message(self, text, append = False):

    if append:
      self.message_label['text'] = self.message_label['text'] + text
    else:
      self.message_label['text'] = text
    self.message_label.update_idletasks()

# -----------------------------------------------------------------------------
# User interface for showing list of data sets.
#
class Data_List_Panel(Hybrid.Popup_Panel):

  name = 'Data set list'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(0, weight = 1)

    row = 0

    hf = Tkinter.Frame(frame)
    hf.grid(row = row, column = 0, sticky = 'ew')
    hf.columnconfigure(1, weight = 1)
    row += 1
    
    h = Tkinter.Label(hf, text = 'Data Sets')
    h.grid(row = 0, column = 0, sticky = 'w')
    
    b = self.make_close_button(hf)
    b.grid(row = 0, column = 1, sticky = 'e')
    
    rl = Hybrid.Scrollable_List(frame, None, 3, self.region_selection_cb)
    self.region_listbox = rl.listbox
    rl.frame.grid(row = row, column = 0, sticky = 'news')
    frame.rowconfigure(row, weight = 1)
    row += 1

  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):

    pass

  # ---------------------------------------------------------------------------
  #
  def region_selection_cb(self, event):

    rlist = self.selected_list_regions()
    if len(rlist) == 1:
      self.dialog.display_region_info(rlist[0])
      self.dialog.redisplay_needed_cb()

  # ---------------------------------------------------------------------------
  #
  def selected_list_regions(self):

    indices = map(int, self.region_listbox.curselection())
    mv = self.dialog.menu_volumes
    regions = [mv[i] for i in indices]
    return regions

  # ---------------------------------------------------------------------------
  #
  def list_region(self, line):

    self.region_listbox.insert('end', line)

  # ---------------------------------------------------------------------------
  #
  def remove_listed_region(self, index):

    self.region_listbox.delete(index)

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    pass

# -----------------------------------------------------------------------------
# User interface for opening precomputed subsamples.
#
class Precomputed_Subsamples_Panel(Hybrid.Popup_Panel):

  name = 'Precomputed subsamples'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(2, weight = 1)
    
    pss = Hybrid.Option_Menu(frame, 'Precomputed subsamplings ')
    pss.frame.grid(row = 0, column = 0, sticky = 'w')
    pss.add_callback(self.subsample_menu_cb)
    self.subsampling_menu = pss

    oss = Tkinter.Button(frame, text = 'Open...',
                         command = self.open_subsamplings_cb)
    oss.grid(row = 0, column = 1, sticky = 'w')
    
    b = self.make_close_button(frame)
    b.grid(row = 0, column = 2, sticky = 'e')
    
  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):

    if data_region == None:
      self.subsampling_menu.remove_all_entries()
    else:
      self.update_subsample_menu(data_region)
    
  # ---------------------------------------------------------------------------
  #
  def open_subsamplings_cb(self):

    from VolumeData.opendialog import show_grid_file_browser
    show_grid_file_browser('Open Subsampled Volumes', self.open_subsamplings)

  # ---------------------------------------------------------------------------
  #
  def open_subsamplings(self, grid_objects):

    data_region = active_volume()
    if data_region == None:
      return
    data = data_region.data

    import subsample
    for g in grid_objects:
      cell_size = subsample.cell_size(g.size, g.name, data.size, data.name,
				      self.dialog.toplevel_widget)
      if cell_size and cell_size != (1,1,1):
        self.open_subsamples(data_region.data, g, cell_size)

  # ---------------------------------------------------------------------------
  #
  def open_subsamples(self, data, grid_object, cell_size):
    
    from VolumeData import Subsampled_Grid
    if isinstance(data, Subsampled_Grid):
      ssdata = data
    else:
      ssdata = Subsampled_Grid(data)
      import volume
      volume.replace_data(data, ssdata)
    
    ssdata.add_subsamples(grid_object, cell_size)

    data_region = active_volume()
    if data_region.data == ssdata:
      self.update_subsample_menu(data_region)

  # ---------------------------------------------------------------------------
  #
  def update_subsample_menu(self, data_region):

    ssm = self.subsampling_menu
    ssm.remove_all_entries()
    if data_region:
      ssm.add_entry('full data')
      data = data_region.data
      if hasattr(data, 'available_subsamplings'):
        sslist = data.available_subsamplings.keys()
        sslist.sort()
        for subsampling in sslist:
          if tuple(subsampling) != (1,1,1):
            ssm.add_entry(step_text(subsampling))
      self.set_subsample_menu(data_region)
    
  # ---------------------------------------------------------------------------
  #
  def set_subsample_menu(self, data_region):

    ijk_min, ijk_max, ijk_step = data_region.region
    subsampling, ss_size = data_region.choose_subsampling(ijk_step)

    if tuple(subsampling) == (1,1,1):
      text = 'full data'
    else:
      text = step_text(subsampling)

    self.subsampling_menu.variable.set(text, invoke_callbacks = 0)
    
  # ---------------------------------------------------------------------------
  # Currently don't do anything when subsample menu selection is changed.
  #
  def subsample_menu_cb(self):

    text = self.subsampling_menu.variable.get()
    if text == '':
      return
    elif text == 'full data':
      cell_size = (1,1,1)
    else:
      cell_size = map(int, text.split())
      if len(cell_size) == 1:
        cell_size = cell_size * 3

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    pass

# -----------------------------------------------------------------------------
#
def size_text(size):

  if size[1] == size[0] and size[2] == size[0]:
    t = u'%d\u00B3' % (size[0],)       # Superscript 3
  else:
    t = '%d %d %d' % tuple(size)
  return t

# -----------------------------------------------------------------------------
#
def step_text(step):

  if step[1] == step[0] and step[2] == step[0]:
    t = '%d' % (step[0],)
  else:
    t = '%d %d %d' % tuple(step)
  return t

# -----------------------------------------------------------------------------
# Check if text represents a different vector value.
#
def vector_value(text, v, allow_singleton = False):

    vfields = text.split()
    if allow_singleton and len(vfields) == 1:
      vfields *= 3
    nv = list(v)
    if len(vfields) == 3:
      for a in range(3):
        if vfields[a] != float_format(v[a], 5):
          nv[a] = string_to_float(vfields[a], v[a])
    if nv == list(v):
      return v
    return tuple(nv)

# -----------------------------------------------------------------------------
#
def vector_value_text(vsize, precision = 5):

  if vsize[1] == vsize[0] and vsize[2] == vsize[0]:
    vst = float_format(vsize[0],precision)
  else:
    vst = ' '.join([float_format(vs,precision) for vs in vsize])
  return vst

# -----------------------------------------------------------------------------
# User interface for placement of data array in xyz coordinate space.
# Displays origin, voxel size, cell angles (for skewed x-ray data), rotation.
#
class Coordinates_Panel(Hybrid.Popup_Panel):

  name = 'Coordinates'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(0, weight = 1)

    row = 0

    hf = Tkinter.Frame(frame)
    hf.grid(row = row, column = 0, sticky = 'ew')
    hf.columnconfigure(1, weight = 1)
    row += 1

    ostext = 'Placement of data array in x,y,z coordinate space:'
    osh = Tkinter.Label(hf, text = ostext)
    osh.grid(row = 0, column = 0, sticky = 'w')
    
    b = self.make_close_button(hf)
    b.grid(row = 0, column = 1, sticky = 'e')
    
    osf = Tkinter.Frame(frame)
    osf.grid(row = row, column = 0, sticky = 'w')
    row += 1

    org = Hybrid.Entry(osf, 'Origin index ', 20)
    org.frame.grid(row = 0, column = 0, sticky = 'e')
    self.origin = org.variable
    org.entry.bind('<KeyPress-Return>', dialog.redisplay_cb)

    orb = Tkinter.Button(osf, text = 'center',
			 command = self.center_origin_cb)
    orb.grid(row = 0, column = 1, sticky = 'w')

    orb = Tkinter.Button(osf, text = 'reset',
			 command = self.reset_origin_cb)
    orb.grid(row = 0, column = 2, sticky = 'w')

    vs = Hybrid.Entry(osf, 'Voxel size ', 20)
    vs.frame.grid(row = 1, column = 0, sticky = 'e')
    self.voxel_size = vs.variable
    vs.entry.bind('<KeyPress-Return>', dialog.redisplay_cb)

    srb = Tkinter.Button(osf, text = 'reset',
			 command = self.reset_voxel_size_cb)
    srb.grid(row = 1, column = 2, sticky = 'w')

    ca = Hybrid.Entry(osf, 'Cell angles ', 20)
    ca.frame.grid(row = 2, column = 0, sticky = 'e')
    self.cell_angles = ca.variable
    ca.entry.bind('<KeyPress-Return>', dialog.redisplay_cb)

    rx = Hybrid.Entry(osf, 'Rotation axis ', 20)
    rx.frame.grid(row = 3, column = 0, sticky = 'e')
    self.rotation_axis = rx.variable
    rx.entry.bind('<KeyPress-Return>', dialog.redisplay_cb)

    ra = Hybrid.Entry(osf, ' angle ', 5)
    ra.frame.grid(row = 3, column = 1, columnspan = 2, sticky = 'w')
    self.rotation_angle = ra.variable
    ra.entry.bind('<KeyPress-Return>', dialog.redisplay_cb)

  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):

    if data_region == None:
      self.update_origin(None, None)
      self.update_voxel_size(None)
      self.update_cell_angles(None)
      self.update_rotation(None)
    else:
      data = data_region.data
      self.update_origin(data.origin, data.step)
      self.update_voxel_size(data.step)
      self.update_cell_angles(data.cell_angles)
      self.update_rotation(data.rotation)

  # ---------------------------------------------------------------------------
  #
  def update_origin(self, xyz_origin, xyz_step):

    if xyz_origin is None:
      origin = ''
    else:
      index_origin = map(lambda a,b: -a/b, xyz_origin, xyz_step)
      origin = vector_value_text(index_origin)
    self.origin.set(origin)

  # ---------------------------------------------------------------------------
  #
  def update_voxel_size(self, xyz_step):

    if xyz_step is None:
      vsize = ''
    else:
      vsize = vector_value_text(xyz_step)
    self.voxel_size.set(vsize)

  # ---------------------------------------------------------------------------
  #
  def update_cell_angles(self, cell_angles):

    if cell_angles is None:
      ca = ''
    else:
      ca = vector_value_text(cell_angles)
    self.cell_angles.set(ca)

  # ---------------------------------------------------------------------------
  #
  def update_rotation(self, rotation):

    if rotation is None:
      axis, angle = (0,0,1), 0
    else:
      import Matrix
      axis, angle = Matrix.rotation_axis_angle(rotation)
    raxis = ' '.join([float_format(x,5) for x in axis])
    rangle = float_format(angle,5)
    self.rotation_axis.set(raxis)
    self.rotation_angle.set(rangle)

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    data = data_region.data
    self.use_origin_from_gui(data)
    self.use_step_from_gui(data)
    self.use_cell_angles_from_gui(data)
    self.use_rotation_from_gui(data)

  # ---------------------------------------------------------------------------
  #
  def use_origin_from_gui(self, data):

    dorigin = map(lambda a,b: -a/b, data.origin, data.step)
    origin = vector_value(self.origin.get(), dorigin, allow_singleton = True)
    if origin != dorigin:
      xyz_origin = map(lambda a,b: -a*b, origin, data.step)
      data.set_origin(xyz_origin)
      self.redraw_regions(data)
      self.dialog.message('Set new origin.')

  # ---------------------------------------------------------------------------
  #
  def use_step_from_gui(self, data):

    vsize = vector_value(self.voxel_size.get(), data.step,
                         allow_singleton = True)
    if vsize != data.step:
      # Preserve index origin.
      xyz_origin = map(lambda a,b,c: (a/b)*c, data.origin, data.step, vsize)
      data.set_origin(xyz_origin)
      data.set_step(vsize)
      self.redraw_regions(data)
      self.dialog.message('Set new voxel size.')

  # ---------------------------------------------------------------------------
  #
  def use_cell_angles_from_gui(self, data):

    cell_angles = vector_value(self.cell_angles.get(), data.cell_angles,
                               allow_singleton = True)
    if [a for a in cell_angles if a <= 0 or a >= 180]:
      self.dialog.message('Cell angles must be between 0 and 180 degrees')
      return
    if cell_angles != data.cell_angles:
      data.set_cell_angles(cell_angles)
      self.redraw_regions(data)
      self.dialog.message('Set new cell angles.')

  # ---------------------------------------------------------------------------
  #
  def use_rotation_from_gui(self, data):

    if data.rotation == ((1,0,0),(0,1,0),(0,0,1)):
      axis, angle = (0,0,1), 0
    else:
      import Matrix
      axis, angle = Matrix.rotation_axis_angle(data.rotation)

    naxis = vector_value(self.rotation_axis.get(), axis)
    if naxis == (0,0,0):
      self.dialog.message('Rotation axis must be non-zero')
      return

    if self.rotation_angle.get() != float_format(angle, 5):
      nangle = string_to_float(self.rotation_angle.get(), angle)
    else:
      nangle = angle

    if naxis != axis or nangle != angle:
      import Matrix
      r = Matrix.rotation_from_axis_angle(naxis, nangle)
      data.set_rotation(r)
      self.redraw_regions(data)
      self.dialog.message('Set new rotation.')

  # ---------------------------------------------------------------------------
  #
  def redraw_regions(self, data):

    from volume import regions_using_data
    drlist = regions_using_data(data)
    for dr in drlist:
      if dr.shown():
        dr.show()

  # ---------------------------------------------------------------------------
  #
  def center_origin_cb(self):

    v = active_volume()
    if v is None:
      return

    data = v.data
    index_origin = [0.5*(s-1) for s in data.size]
    xyz_origin = map(lambda a,b: -a*b, index_origin, data.step)
    self.update_origin(xyz_origin, data.step)
    self.dialog.redisplay_needed_cb()

  # ---------------------------------------------------------------------------
  #
  def reset_origin_cb(self):

    v = active_volume()
    if v is None:
      return

    data = v.data
    self.update_origin(data.original_origin, data.original_step)
    self.dialog.redisplay_needed_cb()

  # ---------------------------------------------------------------------------
  #
  def reset_voxel_size_cb(self):

    data_region = active_volume()
    if data_region == None:
      return

    data = data_region.data
    self.update_voxel_size(data.original_step)
    self.dialog.redisplay_needed_cb()

# -----------------------------------------------------------------------------
# User interface for setting display style: surface, mesh, solid.
#
class Display_Style_Panel(Hybrid.Popup_Panel):

  name = 'Display style'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)
    
    frame = self.frame
    frame.columnconfigure(1, weight = 1)
    row = 0

    tm = Hybrid.Radiobutton_Row(frame, 'Style ',
				('surface', 'mesh', 'solid'),
				self.dialog.redisplay_needed_cb)
    tm.frame.grid(row = row, column = 0, sticky = 'nw')
    self.representation = tm.variable
    Hybrid.trace_tk_variable(self.representation.tk_variable,
			     self.representation_changed_cb)
    self.representation.add_callback(self.dialog.redisplay_needed_cb)
    self.representation.set('surface', invoke_callbacks = 0)
    
    b = self.make_close_button(frame)
    b.grid(row = row, column = 1, sticky = 'e')
    row += 1

  # ---------------------------------------------------------------------------
  # Notify all panels that representation changed so they can update gui if
  # it depends on the representation.
  #
  def representation_changed_cb(self):

    self.dialog.representation_changed(self.representation.get())
  
  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):

    if data_region and data_region.representation:
      self.representation.set(data_region.representation, invoke_callbacks = 0)
    
  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    data_region.representation = self.representation.get()

# -----------------------------------------------------------------------------
# User interface for adjusting thresholds and colors.
#
class Thresholds_Panel(Hybrid.Popup_Panel):

  name = 'Threshold and Color'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)

    self.histogram_height = 64
    self.histogram_panes = []
    self.histogram_table = {}           # maps Volume to Histogram_Pane
    self.active_hist = None             # Histogram_Pane
    self.active_order = []              # Histogram_Panes
    self.active_color = 'white'
    self.delayed_update = None

    from chimera.tkgui import windowSystem
    if windowSystem == 'aqua':
      self.active_color = parent.getvar('::tk::Palette(selectBackground)')

    frame = self.frame
    frame.columnconfigure(0, weight = 1)
    row = 0
    
    hf = Tkinter.Frame(frame)
    hf.grid(row = row, column = 0, sticky = 'ew')
    hf.columnconfigure(0, weight = 1)
    self.histograms_frame = hf
    self.next_histogram_row = 0
    
    b = self.make_close_button(frame)
    b.grid(row = row, column = 1, sticky = 'e')
    row += 1

    rcf = Tkinter.Frame(frame)
    rcf.grid(row = row, column = 0, sticky = 'ew')
    row += 1

    col = 0

    rh = Tkinter.Label(rcf, text = 'Range')
    rh.grid(row = 0, column = col, sticky = 'w')
    col += 1
    
    rn = Tkinter.Label(rcf, text = '? - ?')
    rn.grid(row = 0, column = col, padx = 5)
    rn['font'] = non_bold_font(frame)    # Use bold only on headings.
    col += 1
    self.data_range = rn
    
    lh = Tkinter.Label(rcf, text = 'Level')
    lh.grid(row = 0, column = col)
    col += 1

    lv = Hybrid.StringVariable(rcf)
    le = Tkinter.Entry(rcf, width = 5, textvariable = lv.tk_variable)
    le.grid(row = 0, column = col, padx = 5)
    col += 1
    le.bind('<KeyPress-Return>', self.threshold_entry_enter_cb)
    self.threshold = lv

    ch = Tkinter.Label(rcf, text = 'Color')
    ch.grid(row = 0, column = col)
    col += 1
      
    from CGLtk.color import ColorWell
    c = ColorWell.ColorWell(rcf, width = 25, height = 25,
                            callback = self.color_changed_cb)
    c.grid(row = 0, column = col, padx = 5)
    self.color = c
    col += 1

    rcf.columnconfigure(col, weight=1)

    # Configure widgets for surface representation.
    self.representation_changed('surface')

    self.update_panel_widgets(None)
    
    import volume
    volume.add_volume_closed_callback(self.data_closed_cb)

  # ---------------------------------------------------------------------------
  # Create histogram for data region if needed.
  #
  def add_histogram_pane(self, data_region):

    dr = data_region
    hptable = self.histogram_table
    if dr in hptable:
      return

    if None in hptable:
      hp = hptable[None]                # Reuse unused histogram
      del hptable[None]
    elif len(hptable) >= self.maximum_histograms():
      hp = self.active_order[-1]        # Reuse least recently active histogram
      del hptable[hp.data_region]
    else:
      # Make new histogram
      hp = Histogram_Pane(self.dialog, self.histograms_frame,
                          self.histogram_height,
                          self.set_threshold_and_color_widgets)
      hp.frame.grid(row = self.next_histogram_row, column = 0, sticky = 'ew')
      self.next_histogram_row += 1
      self.histogram_panes.append(hp)

    hp.set_data_region(dr)
    hptable[dr] = hp
    self.set_active_data(hp)

  # ---------------------------------------------------------------------------
  # Switch histogram threshold markers between vertical
  # lines or piecewise linear function for surfaces or solid.
  #
  def representation_changed(self, rep):

    dr = active_volume()
    if dr:
      hp = self.histogram_table.get(dr, None)
      if hp:
        hp.solid_mode(rep == 'solid')
  
  # ---------------------------------------------------------------------------
  #
  def data_closed_cb(self, volumes):

    hptable = self.histogram_table
    for v in tuple(volumes):
      if v in hptable:
        self.close_histogram_pane(hptable[v])
  
  # ---------------------------------------------------------------------------
  #
  def close_histogram_pane(self, hp):

    self.histogram_panes.remove(hp)
    del self.histogram_table[hp.data_region]
    hp.close()
    if self.active_hist == hp:
      self.active_hist = None
    if hp in self.active_order:
      self.active_order.remove(hp)
    if len(self.histogram_table) == 0:
      self.add_histogram_pane(None)

  # ---------------------------------------------------------------------------
  #
  def max_histograms_cb(self, event = None):

    hptable = self.histogram_table
    if len(hptable) <= 1:
      return

    h = self.maximum_histograms()
    while len(hptable) > h:
      hp = self.active_order.pop()
      self.close_histogram_pane(hp)

  # ---------------------------------------------------------------------------
  #
  def maximum_histograms(self):

    if not hasattr(self.dialog, 'display_options_panel'):
      return 1
    dop = self.dialog.display_options_panel
    h = max(1, integer_variable_value(dop.max_histograms, 1))
    return h

  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region, activate = True):

    if activate:
      if data_region or len(self.histogram_table) == 0:
        self.add_histogram_pane(data_region)
    
    if data_region is None:
      return
    
    hp = self.histogram_table.get(data_region, None)
    if hp is None:
      return

    hp.update_threshold_gui(self.dialog.message)

    if activate or hp.data_region is active_volume():
      self.set_active_data(hp)
      self.set_threshold_and_color_widgets(hp)
      self.update_data_range(data_region)

  # ---------------------------------------------------------------------------
  #
  def update_histograms(self, data_region, read_matrix = True):

    hp = self.histogram_table.get(data_region, None)
    if hp:
      hp.update_histogram(read_matrix, self.dialog.message)
      if data_region is active_volume():
        self.update_data_range(data_region)

  # ---------------------------------------------------------------------------
  #
  def update_data_range(self, volume = None, delay = 0.5):

    # Delay data range update so graphics window update is not slowed when
    # flipping through data planes.
    if delay > 0:
      f = self.frame
      if not self.delayed_update is None:
        f.after_cancel(self.delayed_update)
      def update_cb(s=self):
        s.delayed_update = None
        s.update_data_range(delay = 0)
      self.delayed_update = f.after(int(delay*1000), update_cb)
      return

    if volume is None:
      volume = active_volume()
      if volume is None:
        return

    s = volume.matrix_value_statistics(read_matrix = False)
    if s is None or s.minimum is None or s.maximum is None:
      min_text = max_text = '?'
    else:
      min_text = float_format(s.minimum, 3)
      max_text = float_format(s.maximum, 3)
    self.data_range['text'] = '%s - %s' % (min_text, max_text)

  # ---------------------------------------------------------------------------
  #
  def update_panel_ijk_bounds(self, ijk_min, ijk_max, ijk_step):

    hp = self.active_histogram()
    if hp:
      hp.update_size_and_step((ijk_min, ijk_max, ijk_step))

  # ---------------------------------------------------------------------------
  #
  def threshold_entry_enter_cb(self, event):

    hp = self.active_histogram()
    if hp is None:
      return

    markers, m = hp.selected_histogram_marker()
    if m == None:
      return

    threshold = m.xy[0]
    if float_format(threshold, 3) != self.threshold.get():
      try:
	t = float(self.threshold.get())
      except ValueError:
	return
      m.xy = (t, m.xy[1])
      markers.update_plot()

    self.dialog.redisplay_cb()

  # ---------------------------------------------------------------------------
  #
  def color_changed_cb(self, rgba):

    hp = self.active_histogram()
    if hp is None:
      return
    
    markers, m = hp.selected_histogram_marker()
    if m:
      m.set_color(rgba, markers.canvas)
    self.dialog.redisplay_needed_cb()

  # ---------------------------------------------------------------------------
  #
  def set_threshold_and_color_widgets(self, hp):

    if hp != self.active_histogram():
      return
    
    markers, m = hp.selected_histogram_marker()
    if m:
      threshold = m.xy[0]
      t_str = float_format(threshold, 3)
      self.threshold.set(t_str, invoke_callbacks = False)
      self.color.showColor(m.rgba, doCallback = False)

  # ---------------------------------------------------------------------------
  #
  def active_histogram(self):

    return self.active_hist

  # ---------------------------------------------------------------------------
  #
  def set_active_data(self, hp):

    a = self.active_hist
    if a and a.frame:
      a.data_name['background'] = self.frame['background']
    self.active_hist = hp
    if hp and hp.frame:
      hp.data_name['background'] = self.active_color
      ao = self.active_order
      if hp in ao:
        ao.remove(hp)
      ao.insert(0, hp)
    
  # ---------------------------------------------------------------------------
  #
  def histogram_shown(self, data_region):

    hp = self.histogram_table.get(data_region, None)
    return hp and hp.histogram_shown
    
  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    hp = self.histogram_table.get(data_region, None)
    if hp and hp.histogram_shown:
      hp.set_threshold_parameters_from_gui()
  
# -----------------------------------------------------------------------------
# Manages histogram and heading with data name, step size, shown indicator,
# and map close button.
#
class Histogram_Pane:

  def __init__(self, dialog, parent, histogram_height,
               show_threshold_and_color_cb):

    self.dialog = dialog
    self.data_region = None
    self.show_threshold_and_color_cb = show_threshold_and_color_cb
    self.histogram_data = None
    self.histogram_size = None
    self.delayed_update = None

    f = Tkinter.Frame(parent)
    f.columnconfigure(0, weight = 1)
    self.frame = f
    row = 0

    df = Tkinter.Frame(f)
    df.grid(row = row, column = 0, sticky = 'ew')
    df.columnconfigure(4, weight = 1)
    row += 1

    nm = Tkinter.Label(df)
    nm.grid(row = 0, column = 0, sticky = 'w')
    nm.bind("<ButtonPress>", self.select_data_cb)
    self.data_name = nm

    sz = Tkinter.Label(df)
    sz.grid(row = 0, column = 1, padx = 10, sticky = 'w')
    self.size = sz
    sz.bind("<ButtonPress>", self.select_data_cb)

    dsm = Hybrid.Option_Menu(df, 'step ', '1', '2', '4', '8', '16')
    dsm.button.configure(pady = 1, indicatoron = False)
    dsm.frame.grid(row = 0, column = 2, sticky = 'w')
    dsm.add_callback(self.data_step_cb)
    self.data_step = dsm

    sh = Hybrid.Checkbutton(df, '', True)
    sh.button.configure(image = Hybrid.bitmap('eye'),
                        borderwidth = 0, indicatoron = False,
                        selectcolor = sh.button['background'])
    Hybrid.Balloon_Help(sh.button, 'Display or undisplay data', delay = 1.0)
    sh.button.grid(row = 0, column = 3, padx = 10, sticky = 'w')
    self.shown = sh.variable
    self.shown_button = sh.button
    self.shown.add_callback(self.show_cb)
    self.shown_handlers = []

    cb = Tkinter.Button(df, image = Hybrid.bitmap('dash'),
                        command = self.close_map_cb)
    Hybrid.Balloon_Help(cb, 'Close data set', delay = 1.0)
    cb.grid(row = 0, column = 4, sticky = 'e')

    self.make_histogram(f, row, histogram_height, new_marker_color = (1,1,1,1))
    row += 1

  # ---------------------------------------------------------------------------
  #
  def set_data_region(self, data_region):

    self.data_region = data_region
    self.histogram_shown = False
    self.histogram_data = None
    self.show_data_name()
    if data_region:
      if not self.shown_handlers:
        from chimera import triggers, openModels as om
        h = [(tset, tname, tset.addHandler(tname, self.check_shown_cb, None))
             for tset, tname in ((triggers, 'Model'),
                                 (om.triggers, om.ADDMODEL))]
        self.shown_handlers = h
      new_marker_color = data_region.default_rgba
    else:
      new_marker_color = (1,1,1,1)

    self.surface_thresholds.new_marker_color = new_marker_color
    from volume import saturate_rgba
    self.solid_thresholds.new_marker_color = saturate_rgba(new_marker_color)

  # ---------------------------------------------------------------------------
  #
  def show_data_name(self):

    if self.data_region:
      self.data_name['text'] = self.data_region.name_with_id()
    else:
      self.data_name['text'] = ''

  # ---------------------------------------------------------------------------
  #
  def close_map_cb(self, event = None):

    dr = self.data_region
    if dr:
      import volume
      volume.remove_volumes([dr])

  # ---------------------------------------------------------------------------
  #
  def make_histogram(self, frame, row, histogram_height, new_marker_color):

    cborder = 2
    #
    # set highlight thickness = 0 so line in column 0 is visible.
    #
    c = Tkinter.Canvas(frame, height = histogram_height,
                       borderwidth = cborder, relief = 'sunken',
                       highlightthickness = 0)
    c.grid(row = row, column = 0, columnspan = 9, padx = 5, pady = 5,
	   sticky = 'ew')
    self.canvas = c

    import histogram
    self.histogram = histogram.Histogram(c)
    self.histogram_shown = False

    bins = 2
    hbox = (cborder, cborder + 5,
            cborder + bins - 1, cborder + histogram_height - 5)
    st = histogram.Markers(c, hbox, 'line', new_marker_color, 0,
			   self.select_marker_cb)
    self.surface_thresholds = st

    import volume
    new_solid_marker_color = volume.saturate_rgba(new_marker_color)
    sdt = histogram.Markers(c, hbox, 'box', new_solid_marker_color, 1,
			    self.select_marker_cb)
    self.solid_thresholds = sdt

    c.bind('<Configure>', self.canvas_resize_cb)
    c.bind("<ButtonPress>", self.select_data_cb, add = True)
    c.bind("<ButtonPress-1>", self.select_data_cb, add = True)

  # ---------------------------------------------------------------------------
  #
  def canvas_resize_cb(self, event = None):

    if self.histogram_shown:
      self.update_histogram(read_matrix = False,
                            message_cb = self.dialog.message,
                            resize = True)

  # ---------------------------------------------------------------------------
  #
  def select_data_cb(self, event = None):

    dr = self.data_region
    if dr:
      d = self.dialog
      if dr != d.focus_region:
        d.display_region_info(dr)
      d.redisplay_needed_cb()

  # ---------------------------------------------------------------------------
  #
  def select_marker_cb(self):

    self.select_data_cb()
    self.show_threshold_and_color_cb(self)

  # ---------------------------------------------------------------------------
  #
  def data_step_cb(self):

    dr = self.data_region
    if dr is None or dr.region is None:
      return

    step = self.data_step.variable.get()
    ijk_step = map(int, step.split(' '))
    if len(ijk_step) == 1:
      ijk_step = ijk_step * 3

    if tuple(ijk_step) == tuple(dr.region[2]):
      return

    ijk_min, ijk_max = dr.region[:2]
    dr.new_region(ijk_min, ijk_max, ijk_step, adjust_step = False, show = False)
    d = self.dialog
    if dr != d.focus_region:
      d.display_region_info(dr)
    d.redisplay_needed_cb()

  # ---------------------------------------------------------------------------
  #
  def show_cb(self):

    dr = self.data_region
    if dr is None:
      return

    show = self.shown.get()
    for m in self.data_region.models():
      m.display = show

    self.update_shown_icon()

    if show:
      self.select_data_cb()

  # ---------------------------------------------------------------------------
  #
  def check_shown_cb(self, trigger, x, changes):

    from chimera import openModels
    if trigger == 'Model':
      if self.data_region.representation == 'solid':
        from _volume import Volume_Model
        if [m for m in changes.deleted if isinstance(m, Volume_Model)]:
          self.update_shown_icon()
      if not [m for m in self.data_region.models()
              if m in changes.modified or m in changes.created]:
        return
      if 'name changed' in changes.reasons:
        self.show_data_name()
      if 'display changed' in changes.reasons:
        self.update_shown_icon()
    elif trigger == openModels.ADDMODEL:
      self.update_shown_icon()
      
  # ---------------------------------------------------------------------------
  #
  def update_shown_icon(self):

    v = self.data_region
    if v is None:
      return

    shown = v.shown()
    self.shown.set(shown, invoke_callbacks = False)
    if shown:
      icon_name = 'eye'
    else:
      icon_name = 'closed eye'
    self.shown_button.configure(image = Hybrid.bitmap(icon_name))
      
  # ---------------------------------------------------------------------------
  #
  def solid_mode(self, solid):

    self.solid_thresholds.show(solid)
    self.surface_thresholds.show(not solid)
    self.show_threshold_and_color_cb(self)

  # ---------------------------------------------------------------------------
  #
  def selected_histogram_marker(self):

    if self.solid_thresholds.shown:
      markers = self.solid_thresholds
    elif self.surface_thresholds.shown:
      markers = self.surface_thresholds
    else:
      return None, None

    return markers, markers.selected_marker()

  # ---------------------------------------------------------------------------
  #
  def update_threshold_gui(self, message_cb):

    read_matrix = False
    self.update_histogram(read_matrix, message_cb)

    self.update_size_and_step()
    self.update_shown_icon()

    self.plot_surface_levels()
    self.plot_solid_levels()
    rep = self.data_region.representation
    if rep == None:
      rep = self.dialog.display_style_panel.representation.get()
    self.solid_mode(rep == 'solid')
    
  # ---------------------------------------------------------------------------
  #
  def update_size_and_step(self, region = None):

    if region is None:
      dr = self.data_region
      if dr is None:
        return
      region = dr.region

    ijk_min, ijk_max, ijk_step = region
    size = map(lambda a,b: a-b+1, ijk_max, ijk_min)
    self.size['text'] = size_text(size)

    step = step_text(ijk_step)
    ds = self.data_step
    if not step in ds.values:
      ds.add_entry(step)
    ds.variable.set(step, invoke_callbacks = False)
    
  # ---------------------------------------------------------------------------
  #
  def plot_surface_levels(self):

    dr = self.data_region
    if dr is None:
      return

    from histogram import Marker
    surf_markers = map(lambda t, c, m = Marker: m((t,0), c),
		       dr.surface_levels, dr.surface_colors)
    self.surface_thresholds.set_markers(surf_markers)
    
  # ---------------------------------------------------------------------------
  #
  def plot_solid_levels(self):

    dr = self.data_region
    if dr is None:
      return

    from histogram import Marker
    solid_markers = map(lambda ts, c, m=Marker: m(ts, c),
			dr.solid_levels, dr.solid_colors)
    self.solid_thresholds.set_markers(solid_markers)
    
  # ---------------------------------------------------------------------------
  #
  def update_histogram(self, read_matrix, message_cb, resize = False,
                       delay = 0.5):

    dr = self.data_region
    if dr is None:
      return

    # Delay histogram update so graphics window update is not slowed when
    # flipping through data planes.
    if delay > 0:
      f = self.frame
      if not self.delayed_update is None:
        f.after_cancel(self.delayed_update)
      def update_cb(s=self, rm=read_matrix, m=message_cb, rz=resize):
        s.delayed_update = None
        s.update_histogram(rm, m, rz, delay = 0)
      self.delayed_update = f.after(int(delay*1000), update_cb)
      return

    s = dr.matrix_value_statistics(read_matrix)
    if s is None:
      return

    if s == self.histogram_data and not resize:
      return

    bins = self.histogram_bins()
    if resize and bins == self.histogram_size and s == self.histogram_data:
      return    # Histogram size and data unchanged.

    message_cb('Showing histogram')
    self.histogram_data = s
    counts = s.bin_counts(bins)
    h = self.histogram
    from numpy import log
    h.show_data(log(counts + 1))
    self.histogram_shown = True
    self.histogram_size = bins
    message_cb('')
    first_bin_center, last_bin_center, bin_size = s.bin_range(bins)
    self.solid_thresholds.set_user_x_range(first_bin_center,
                                           last_bin_center)
    self.surface_thresholds.set_user_x_range(first_bin_center,
                                             last_bin_center)
  
  # ---------------------------------------------------------------------------
  #
  def histogram_bins(self):

    c = self.canvas
    hwidth = c.winfo_width() - 2*int(c['borderwidth'])
    if hwidth <= 1:
      c.update_idletasks()
      hwidth = c.winfo_width() - 2*int(c['borderwidth'])
    if hwidth <= 1:
      hwidth = 300
    cborder = int(c['borderwidth'])
    hheight = int(c['height'])
    bins = hwidth - 1
    hbox = (cborder, cborder + 5, cborder + bins - 1, cborder + hheight - 5)
    self.surface_thresholds.set_canvas_box(hbox)
    self.solid_thresholds.set_canvas_box(hbox)
    return bins

  # ---------------------------------------------------------------------------
  #
  def set_threshold_parameters_from_gui(self):

    dr = self.data_region
    if dr == None:
      return
    
    markers = self.surface_thresholds.markers
    dr.surface_levels = map(lambda m: m.xy[0], markers)
    dr.surface_colors = map(lambda m: m.rgba, markers)
    markers = self.solid_thresholds.markers
    dr.solid_levels = map(lambda m: m.xy, markers)
    dr.solid_colors = map(lambda m: m.rgba, markers)

  # ---------------------------------------------------------------------------
  # Delete widgets and references to other objects.
  #
  def close(self):

    for tset, tname, h in self.shown_handlers:
      tset.deleteHandler(tname, h)
    self.shown_handlers = []

    self.dialog = None
    self.data_region = None
    self.histogram_data = None

    self.frame.destroy()
    self.frame = None

# -----------------------------------------------------------------------------
# User interface for adjusting brightness and transparency.
#
class Brightness_Transparency_Panel(Hybrid.Popup_Panel):

  name = 'Brightness and Transparency'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)
    
    frame = self.frame
    frame.columnconfigure(0, weight = 1)
    row = 0

    bf = Hybrid.Logarithmic_Scale(frame, 'Brightness ', .01, 10, 1, '%.2g')
    bf.frame.grid(row = row, column = 0, sticky = 'ew')
    bf.callback(dialog.redisplay_needed_cb)
    bf.entry.bind('<KeyPress-Return>', dialog.redisplay_cb)
    self.surface_brightness_factor = bf

    bfs = Hybrid.Logarithmic_Scale(frame, 'Brightness ', .01, 10, 1, '%.2g')
    bfs.frame.grid(row = row, column = 0, sticky = 'ew')
    bfs.callback(dialog.redisplay_needed_cb)
    bfs.entry.bind('<KeyPress-Return>', dialog.redisplay_cb)
    self.solid_brightness_factor = bfs

    b = self.make_close_button(frame)
    b.grid(row = row, column = 1, sticky = 'e')
    row += 1

    tfs = Hybrid.Scale(frame, 'Transparency ', 0, 1, .01, 0)
    tfs.frame.grid(row = row, column = 0, sticky = 'ew')
    tfs.callback(dialog.redisplay_needed_cb)
    tfs.entry.bind('<KeyPress-Return>', dialog.redisplay_cb)
    self.transparency_factor = tfs

    tds = Hybrid.Scale(frame, 'Transparency ', 0, 1, .01, 0)
    tds.frame.grid(row = row, column = 0, sticky = 'ew')
    row += 1
    tds.callback(dialog.redisplay_needed_cb)
    tds.entry.bind('<KeyPress-Return>', dialog.redisplay_cb)
    self.transparency_depth = tds

    self.representation_changed('surface')
    
  # ---------------------------------------------------------------------------
  # Show brightness and transparency sliders appropriate for surface or solid.
  # Solid uses logarithmic transparency depth slider and surface uses linear
  # transparency factor.
  #
  def representation_changed(self, representation):

    solid = (representation == 'solid')
    place_in_grid(self.transparency_factor.frame, not solid)
    place_in_grid(self.surface_brightness_factor.frame, not solid)
    place_in_grid(self.transparency_depth.frame, solid)
    place_in_grid(self.solid_brightness_factor.frame, solid)
  
  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):
    
    dr = data_region
    if dr == None:
      return

    self.transparency_factor.set_value(dr.transparency_factor,
                                       invoke_callbacks = False)
    self.transparency_depth.set_value(dr.transparency_depth,
                                      invoke_callbacks = False)
    self.surface_brightness_factor.set_value(dr.surface_brightness_factor,
                                             invoke_callbacks = False)
    self.solid_brightness_factor.set_value(dr.solid_brightness_factor,
                                           invoke_callbacks = False)

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    dr = data_region
    tf = self.transparency_factor.value(default = 0)
    td = self.transparency_depth.value(default = 0)
    bf = self.surface_brightness_factor.value(default = 1)
    bfs = self.solid_brightness_factor.value(default = 1)

    dr.transparency_factor = tf      # for surface/mesh
    dr.surface_brightness_factor = bf
    dr.transparency_depth = td       # for solid
    dr.solid_brightness_factor = bfs

# -----------------------------------------------------------------------------
# User interface for selecting subregions of a data set.
#
class Named_Region_Panel(Hybrid.Popup_Panel):

  name = 'Named regions'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)
    
    frame = self.frame
    frame.columnconfigure(3, weight = 1)

    rn = Hybrid.Entry(frame, 'Named region ', 10)
    rn.frame.grid(row = 0, column = 0, sticky = 'w')
    rn.entry.bind('<KeyPress-Return>', self.region_name_cb)
    self.region_name = rn.variable

    nm = Hybrid.Menu(frame, 'Show', [])
    nm.button.configure(borderwidth = 2, relief = 'raised',
			highlightthickness = 2)
    nm.button.grid(row = 0, column = 1, sticky = 'w')
    self.region_name_menu = nm

    rb = Hybrid.Button_Row(frame, '',
                           (('Add', self.add_named_region_cb),
                            ('Delete', self.delete_named_region_cb),
			    ))
    rb.frame.grid(row = 0, column = 2, sticky = 'w')
    
    b = self.make_close_button(frame)
    b.grid(row = 0, column = 3, sticky = 'e')

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    pass

  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):

    self.update_region_name_menu(data_region)
    if data_region and data_region.region:
      self.update_panel_ijk_bounds(*data_region.region)
    
  # ---------------------------------------------------------------------------
  #
  def update_panel_ijk_bounds(self, ijk_min, ijk_max, ijk_step):

    self.show_region_name(ijk_min, ijk_max)
    
  # ---------------------------------------------------------------------------
  #
  def region_name_cb(self, event):

    name = self.region_name.get()
    self.show_named_region(name)
    
  # ---------------------------------------------------------------------------
  #
  def add_named_region_cb(self):

    name = self.region_name.get()
    if not name:
      return

    data_region = active_volume()
    if data_region == None:
      return

    self.delete_named_region_cb()
    self.region_name.set(name)

    ijk_min, ijk_max, ijk_step = data_region.region
    rlist = data_region.region_list
    rlist.add_named_region(name, ijk_min, ijk_max)

    cb = lambda show=self.show_named_region, nm=name: show(name)
    self.region_name_menu.add_entry(name, cb)
    
  # ---------------------------------------------------------------------------
  #
  def show_named_region(self, name):

    dr = active_volume()
    if dr == None:
      return
    
    self.region_name.set(name)
    ijk_min, ijk_max = dr.region_list.named_region_bounds(name)
    if ijk_min == None or ijk_max == None:
      return
    dr.new_region(ijk_min, ijk_max)

  # ---------------------------------------------------------------------------
  # If region bounds has a name then show it.
  #
  def show_region_name(self, ijk_min, ijk_max):

    data_region = active_volume()
    if data_region:
      rlist = data_region.region_list
      name = rlist.find_named_region(ijk_min, ijk_max)
      if name == None:
        name = ''
      self.region_name.set(name)
    
  # ---------------------------------------------------------------------------
  #
  def delete_named_region_cb(self):

    data_region = active_volume()
    if data_region == None:
      return

    name = self.region_name.get()
    rlist = data_region.region_list
    index = rlist.named_region_index(name)
    if index == None:
      return

    rlist.remove_named_region(index)
    rnm = self.region_name_menu
    from CGLtk.Hybrid import base_menu_index
    i0 = base_menu_index(rnm)
    rnm.remove_entry(index+i0)
    self.region_name.set('')
    
  # ---------------------------------------------------------------------------
  #
  def update_region_name_menu(self, data_region):

    self.region_name.set('')
    self.region_name_menu.remove_all_entries()
    if data_region == None:
      return

    rlist = data_region.region_list
    for name in rlist.region_names():
      cb = lambda show=self.show_named_region, nm=name: show(nm)
      self.region_name_menu.add_entry(name, cb)

# -----------------------------------------------------------------------------
# User interface for showing data z planes.
#
class Plane_Panel(Hybrid.Popup_Panel):

  name = 'Planes'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)
    
    frame = self.frame

    self.play_handler = None
    self.play_direction = 1
    self.plane_step = 1
    self.cycle_plane_center = 0
    self.cycle_time = 0
    self.last_axis = 2
    self.data_size = (1,1,1)
    self.change_plane_in_progress = False
    
    frame.columnconfigure(0, weight = 1)       # Let scale width expand
    row = 0

    ps = Hybrid.Scale(frame, 'Plane ', 0, 100, 1, 0, entry_width = 4)
    ps.frame.grid(row = row, column = 0, sticky = 'ew')
    ps.callback(self.change_plane_cb)
    ps.entry.bind('<KeyPress-Return>', self.change_plane_cb)
    self.plane = ps

    b = self.make_close_button(frame)
    b.grid(row = row, column = 1, sticky = 'e')
    row += 1

    from chimera.tkgui import windowSystem
    if windowSystem == 'aqua': xp = 9
    else: xp = 2

    cf = Tkinter.Frame(frame)
    cf.grid(row = row, column = 0, columnspan = 3, sticky = 'w')
    row += 1

    oa = Hybrid.Button_Row(cf, '', (('One', self.single_plane_cb),
                                    ('All', self.full_depth_cb)))
    oa.frame.grid(row = 0, column = 0, padx = 5, sticky = 'w')
    for b in oa.buttons:
      b.configure(padx = xp, pady = 1)
    
    cp = Hybrid.Checkbutton_Entries(cf, False, 'Cycle through',
                                    (2, '20'), ' planes at speed ', (2, '30'))
    cp.frame.grid(row = 0, column = 1, sticky = 'nw')
    self.cycle_planes, self.cycle_planes_count, self.cycle_frame_rate = \
       cp.variables
    self.cycle_planes.add_callback(self.cycle_planes_cb)

    sf = Tkinter.Frame(frame)
    sf.grid(row = row, column = 0, columnspan = 3, sticky = 'w')
    row += 1

    dp = Hybrid.Entry(sf, 'Depth ', 3, '1')
    dp.frame.grid(row = 0, column = 0, padx = 5, sticky = 'w')
    dp.entry.bind('<KeyPress-Return>', self.change_plane_cb)
    self.depth_var = dp.variable

    self.axis_names = ['X axis', 'Y axis', 'Z axis']
    am = Hybrid.Option_Menu(sf, '', *self.axis_names)
    am.button.configure(pady = 1, indicatoron = False)
    am.frame.grid(row = 0, column = 1, sticky = 'w')
    self.axis = am.variable
    self.axis.set(self.axis_names[2], invoke_callbacks = False)
    am.add_callback(self.change_axis_cb)

    fp = Tkinter.Button(sf, text = 'Full plane', padx = xp, pady = 1,
                        command = self.full_plane_cb)
    fp.grid(row = 0, column = 2, padx = 5, sticky = 'w')

    pl = Tkinter.Button(sf, text = 'Preload', padx = xp, pady = 1,
                        command = self.preload_cb)
    pl.grid(row = 0, column = 3, sticky = 'w')

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    pass

  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, volume):

    if volume:
      r = volume.region
      if r:
        self.data_size = volume.data.size
        self.update_axis(*r)
        self.update_panel_ijk_bounds(*r)
    
  # ---------------------------------------------------------------------------
  #
  def update_panel_ijk_bounds(self, ijk_min, ijk_max, ijk_step):

    # Set number of planes shown.
    a = self.axis_number()
    s = ijk_step[a]
    d = max(1, ijk_max[a]/s - (ijk_min[a]+s-1)/s + 1)
    self.depth_var.set(d, invoke_callbacks = False)

    # Set scale range.
    smax = self.data_size[a]
    self.set_scale_range(smax, s)

    # Set plane scale value, unless it is due to a user slider adjustment.
    if not self.change_plane_in_progress:
      self.plane.set_value(ijk_min[a], invoke_callbacks = False)
    
  # ---------------------------------------------------------------------------
  #
  def update_axis(self, ijk_min, ijk_max, ijk_step):

    # Set axis to one with fewest planes.
    size = [(ijk_max[a] - ijk_min[a] + 1, -a) for a in range(3)]
    size.sort()
    axis = -size[0][1]
    self.axis.set(self.axis_names[axis], invoke_callbacks = False)
    self.last_axis = axis
    
  # ---------------------------------------------------------------------------
  #
  def set_scale_range(self, size, step):

    s = self.plane
    if size is None:
      size = s.scale['to']
    self.plane_step = step
    pmax = max(0, size - self.depth()*step)
    s.set_range(0, pmax, step)

  # ---------------------------------------------------------------------------
  #
  def single_plane_cb(self):

    v = active_volume()
    if v is None or v.region is None:
      return

    self.depth_var.set(1, invoke_callbacks = False)
    ijk_min, ijk_max, ijk_step = v.region
    a = self.axis_number()
    p = (ijk_min[a] + ijk_max[a]) / 2
    p -= p % ijk_step[a]
    self.plane.set_value(p)
    if v.representation != 'solid':
      v.set_representation('solid')
      v.show()

  # ---------------------------------------------------------------------------
  #
  def full_depth_cb(self):

    v = active_volume()
    if v is None or v.region is None:
      return

    ijk_min, ijk_max, ijk_step = v.region
    a = self.axis_number()
    s = ijk_step[a]
    d = (v.data.size[a] + s - 1) / s
    self.depth_var.set(d)
    self.plane.set_value(0)

  # ---------------------------------------------------------------------------
  #
  def change_axis_cb(self):

    v = active_volume()
    if v is None or v.region is None:
      return

    ijk_min, ijk_max, ijk_step = v.region
    a = self.axis_number()
    step = ijk_step[a]
    max = v.data.size[a]
    self.set_scale_range(max, step)
    p = (ijk_min[a] + ijk_max[a]) / 2
    p -= p % step
    self.plane.set_value(p, invoke_callbacks = False)
    self.change_plane_cb(extend_axes = [self.last_axis])
    self.last_axis = a

    # If region did not change, update plane and depth numbers for new axis.
    self.update_panel_ijk_bounds(*v.region)

  # ---------------------------------------------------------------------------
  #
  def axis_number(self):

    axis = self.axis_names.index(self.axis.get())
    return axis

  # ---------------------------------------------------------------------------
  #
  def depth(self):

    d = integer_variable_value(self.depth_var, 1)
    return d
    
  # ---------------------------------------------------------------------------
  #
  def cycle_planes_cb(self):

    from chimera import triggers
    c = self.cycle_planes.get()
    if c:
      self.cycle_center_plane = int(self.plane.value(default = 0))
      h = triggers.addHandler('new frame', self.next_plane_cb, None)
      self.play_handler = h
    elif self.play_handler:
      triggers.deleteHandler('new frame', self.play_handler)
      self.play_handler = None

  # ---------------------------------------------------------------------------
  #
  def next_plane_cb(self, trigger_name, call_data, trigger_data):

    import time
    r = float_variable_value(self.cycle_frame_rate, 100)
    t = time.time()
    if r * (t-self.cycle_time) < 1:
      return                            # Wait for next frame
    self.cycle_time = t
    
    p = self.plane
    z = int(p.value(default = 0))
    zn = z + self.play_direction*self.plane_step
    zmin, zmax = p.range()
    cc = integer_variable_value(self.cycle_planes_count, None)
    if not cc is None:
      zmin = max(zmin, self.cycle_center_plane - cc/2)
      zmax = min(zmax, self.cycle_center_plane + cc/2)
    if zmin >= zmax:
      self.cycle_planes.set(False)       # Only one valid plane value.
      return
    if zn > zmax:
      self.play_direction = -1
      zn = min(z + self.play_direction*self.plane_step, zmax)
    elif zn < zmin:
      self.play_direction = 1
      zn = max(z + self.play_direction*self.plane_step, zmin)
    p.set_value(zn)
    
  # ---------------------------------------------------------------------------
  #
  def full_plane_cb(self, event = None):
    
    a = self.axis_number()
    plane_axes = [(a+1)%3, (a+2)%3]
    self.change_plane_cb(extend_axes = plane_axes)
    
  # ---------------------------------------------------------------------------
  #
  def preload_cb(self, event = None):

    v = active_volume()
    if v:
      v.full_matrix()
  
  # ---------------------------------------------------------------------------
  #
  def change_plane_cb(self, event = None, extend_axes = [],
                      save_in_region_queue = False):

    self.change_plane_in_progress = True
    self.change_plane(extend_axes, save_in_region_queue)
    self.change_plane_in_progress = False

  # ---------------------------------------------------------------------------
  #
  def change_plane(self, extend_axes = [], save_in_region_queue = False):

    v = active_volume()
    if v is None:
      return

    # Get plane number
    s = self.plane
    p = s.value()
    if p == None:
      return            # Scale value is non-numeric

    a = self.axis_number()
    d = self.depth()
    from volume import show_planes
    if not show_planes(v, a, p, d, extend_axes,
                       save_in_region_queue = save_in_region_queue):
      return    # Plane already shown.

    max = v.data.size[a]
    step = v.region[2][a]
    self.set_scale_range(max, step) # Update scale range.

# -----------------------------------------------------------------------------
# User interface for selecting subregions of a data set.
#
class Region_Size_Panel(Hybrid.Popup_Panel):

  name = 'Region bounds'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)
    
    frame = self.frame

    rl = Tkinter.Label(frame, text = 'Region min max step ')
    rl.grid(row = 0, column = 0, sticky = 'w')

    col = 1
    self.region_bounds = []
    for axis_name in ('x', 'y', 'z'):
      rb = Hybrid.Entry(frame, axis_name, 9)
      rb.frame.grid(row = 0, column = col, sticky = 'w')
      col += 1
      self.region_bounds.append(rb.variable)
      rb.entry.bind('<KeyPress-Return>', self.changed_region_text_cb)
    
    b = self.make_close_button(frame)
    b.grid(row = 0, column = col, sticky = 'e')

    frame.columnconfigure(col, weight = 1)

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    region = self.grid_region()
    from volume import is_empty_region
    if is_empty_region(region):
      return

    ijk_min, ijk_max, ijk_step = region
    data_region.new_region(ijk_min, ijk_max, ijk_step, show = False)

  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):

    if data_region == None:
      for rb in self.region_bounds:
        rb.set('')
    else:
      self.update_panel_ijk_bounds(*data_region.region)
      
  # ---------------------------------------------------------------------------
  #
  def update_panel_ijk_bounds(self, ijk_min, ijk_max, ijk_step):

    self.set_region_gui_min_max(ijk_min, ijk_max)
    self.set_region_gui_step(ijk_step)
    
  # ---------------------------------------------------------------------------
  # User typed new region bounds in entry field.
  #
  def changed_region_text_cb(self, event):

    dr = active_volume()
    if dr:
      ijk_min, ijk_max, ijk_step = self.grid_region()
      dr.new_region(ijk_min, ijk_max, ijk_step, adjust_step = False)
      
  # ---------------------------------------------------------------------------
  #
  def set_region_gui_min_max(self, ijk_min, ijk_max):

    for a in range(3):
      rb = self.region_bounds[a]
      minmax, step = split_fields(rb.get(), 2)
      rb.set('%d %d %s' % (ijk_min[a], ijk_max[a], step))
      
  # ---------------------------------------------------------------------------
  #
  def set_region_gui_step(self, ijk_step):

    for a in range(3):
      rb = self.region_bounds[a]
      minmax, step = split_fields(rb.get(), 2)
      rb.set('%s %d' % (minmax, ijk_step[a]))
  
  # ---------------------------------------------------------------------------
  #
  def grid_region(self):

    ijk_min = [0,0,0]
    ijk_max = [0,0,0]
    ijk_step = [1,1,1]

    bounds = map(integer_variable_values, self.region_bounds)
    for a in range(3):
      b = bounds[a]
      if len(b) > 0 and b[0] != None: ijk_min[a] = b[0]
      if len(b) > 1 and b[1] != None: ijk_max[a] = b[1]
      if len(b) > 2 and b[2] != None: ijk_step[a] = max(1, b[2])

    return (ijk_min, ijk_max, ijk_step)

# -----------------------------------------------------------------------------
# User interface for selecting subregions of a data set.
#
class Atom_Box_Panel(Hybrid.Popup_Panel):

  name = 'Atom box'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)
    
    frame = self.frame
    frame.columnconfigure(2, weight = 1)

    bb = Tkinter.Button(frame, text = 'Box', command = self.atom_box_cb)
    bb.grid(row = 0, column = 0, sticky = 'w')

    pe = Hybrid.Entry(frame, ' around selected atoms with padding ', 5, '0')
    pe.frame.grid(row = 0, column = 1, sticky = 'w')
    self.box_padding = pe.variable
    pe.entry.bind('<KeyPress-Return>', self.atom_box_cb)
    
    b = self.make_close_button(frame)
    b.grid(row = 0, column = 2, sticky = 'e')

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    pass

  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):

    pass
    
  # ---------------------------------------------------------------------------
  #
  def atom_box_cb(self, event = None):

    pad = float(self.box_padding.get())
    self.set_region_to_atom_box(pad)
    
  # ---------------------------------------------------------------------------
  #
  def set_region_to_atom_box(self, pad):

    import chimera.selection
    atoms = chimera.selection.currentAtoms()
    if len(atoms) == 0:
      return

    points = map(lambda a: a.xformCoord().data(), atoms)

    dr = active_volume()
    if dr == None:
      return

    xform_to_volume = dr.model_transform()
    if xform_to_volume == None:
      return
    xform_to_volume.invert()

    import volume
    vpoints = volume.transformed_points(points, xform_to_volume)

    from VolumeData import points_ijk_bounds
    ijk_min, ijk_max = points_ijk_bounds(vpoints, pad, dr.data)

    dr.new_region(ijk_min, ijk_max)

# -----------------------------------------------------------------------------
# User interface for selecting subregions of a data set.
#
class Subregion_Panel(Hybrid.Popup_Panel):

  name = 'Subregion selection'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog
    self.subregion_selector = None
    self.last_subregion = (None, None)

    Hybrid.Popup_Panel.__init__(self, parent)
    
    frame = self.frame
    frame.columnconfigure(0, weight = 1)
    row = 0

    srf = Tkinter.Frame(frame)
    srf.grid(row = row, column = 0, sticky = 'ew')
    srf.columnconfigure(2, weight = 1)
    row += 1
    
    sr = Hybrid.Checkbutton(srf, 'Select subregions using ', 0)
    sr.button.grid(row = 0, column = 0, sticky = 'w')
    self.selectable_subregions = sr.variable
    sr.callback(self.selectable_subregions_cb)

    srm = Hybrid.Option_Menu(srf, '', 'button 1', 'button 2', 'button 3',
                             'ctrl button 1', 'ctrl button 2', 'ctrl button 3')
    srm.variable.set('button 2')
    srm.frame.grid(row = 0, column = 1, sticky = 'w')
    srm.add_callback(self.subregion_button_cb)
    self.subregion_button = srm
    
    b = self.make_close_button(srf)
    b.grid(row = 0, column = 2, sticky = 'e')

    cf = Tkinter.Frame(frame)
    cf.grid(row = row, column = 0, sticky = 'w')
    row += 1

    cb = Hybrid.Button_Row(cf, '', (('Crop', self.crop_cb),))
    cb.frame.grid(row = 0, column = 0, sticky = 'nw')
    
    aus = Hybrid.Checkbutton(cf, 'auto', False)
    aus.button.grid(row = 0, column = 1, sticky = 'w')
    self.auto_show_subregion = aus.variable

    zb = Hybrid.Button_Row(cf, '',
                           (('Back', self.back_cb),
                            ('Forward', self.forward_cb),
                            ('Full', self.zoom_full_cb),
			    ))
    zb.frame.grid(row = 0, column = 2, sticky = 'nw')
    self.back_button = zb.buttons[0]
    self.back_button['state'] = 'disabled'
    self.forward_button = zb.buttons[1]
    self.forward_button['state'] = 'disabled'

    rsf = Tkinter.Frame(frame)
    rsf.grid(row = row, column = 0, sticky = 'ew')
    rsf.columnconfigure(2, weight = 1)
    row += 1

    rb = Hybrid.Checkbutton(rsf, 'Rotate selection box,', 0)
    rb.button.grid(row = 0, column = 0, sticky = 'w')
    self.rotate_box = rb.variable
    rb.callback(self.rotate_box_cb)

    vs = Hybrid.Entry(rsf, ' sample at voxel size ', 6)
    vs.frame.grid(row = 0, column = 1, sticky = 'ew')
    self.resample_voxel_size = vs.variable

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    pass
    
  # ---------------------------------------------------------------------------
  #
  def default_settings_changed(self, default_settings, changes):

    if 'auto_show_subregion' in changes:
      self.auto_show_subregion.set(changes['auto_show_subregion'])

  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):
      
    self.activate_back_forward(data_region)
    if data_region:
      self.resample_voxel_size.set(vector_value_text(data_region.data.step))

  # ---------------------------------------------------------------------------
  #
  def update_panel_ijk_bounds(self, ijk_min, ijk_max, ijk_step):

    self.activate_back_forward(active_volume())

  # ---------------------------------------------------------------------------
  #
  def insert_region_in_queue(self, data_region, ijk_min, ijk_max):

    data_region.region_list.insert_region(ijk_min, ijk_max)
    self.activate_back_forward(data_region)

  # ---------------------------------------------------------------------------
  #
  def activate_back_forward(self, data_region):

    if data_region == None:
      back = 0
      forward = 0
    else:
      from_beginning, from_end = data_region.region_list.where()
      back = (from_beginning > 0)
      forward = (from_end > 0)

    if back:
      self.back_button['state'] = 'normal'
    else:
      self.back_button['state'] = 'disabled'

    if forward:
      self.forward_button['state'] = 'normal'
    else:
      self.forward_button['state'] = 'disabled'
      
  # ---------------------------------------------------------------------------
  #
  def crop_cb(self):

    if self.need_resample():
      self.resample(replace = True)
      return

    ijk_min, ijk_max = self.subregion_box_bounds()
    if ijk_min == None or ijk_max == None:
      self.dialog.message('No subregion selected for cropping')
      return

    v = active_volume()
    if v:
      # Make sure at least one integer plane in each dimension.
      from math import ceil
      ijk_max = [max(ijk_max[a], ceil(ijk_min[a])) for a in (0,1,2)]
      v.new_region(ijk_min, ijk_max)
      
  # ---------------------------------------------------------------------------
  #
  def subregion_box_bounds(self):
    
    ss = self.subregion_selector
    v = active_volume()
    if ss == None or v == None:
      return None, None

    return ss.ijk_box_bounds(v.model_transform())
      
  # ---------------------------------------------------------------------------
  #
  def back_cb(self):

    self.switch_region(-1)
      
  # ---------------------------------------------------------------------------
  #
  def forward_cb(self):

    self.switch_region(1)
      
  # ---------------------------------------------------------------------------
  #
  def switch_region(self, offset):

    dr = active_volume()
    if dr == None:
      return

    ijk_min, ijk_max = dr.region_list.other_region(offset)
    if ijk_min == None or ijk_max == None:
      return

    dr.new_region(ijk_min, ijk_max)
    
  # ---------------------------------------------------------------------------
  #
  def zoom_full_cb(self):

    dr = active_volume()
    if dr == None:
      return

    ijk_min = [0, 0, 0]
    ijk_max = map(lambda n: n-1, dr.data.size)
    dr.new_region(ijk_min, ijk_max)
    
  # ---------------------------------------------------------------------------
  #
  def zoom(self, factor):

    dr = active_volume()
    if dr == None or dr.region == None:
      return

    ijk_min, ijk_max, ijk_step = dr.region
    size = map(lambda a,b: (b - a + 1), ijk_min, ijk_max)
    f = .5 * (factor - 1)
    zoom_ijk_min = map(lambda i,s,f=f: i - f*s, ijk_min, size)
    zoom_ijk_max = map(lambda i,s,f=f: i + f*s, ijk_max, size)

    # If zoomed in to less than one plane, display at least one plane.
    for a in range(3):
      if zoom_ijk_max[a] - zoom_ijk_min[a] < 1:
        mid = .5 * (zoom_ijk_max[a] + zoom_ijk_min[a])
        zoom_ijk_max[a] = mid + 0.5
        zoom_ijk_min[a] = mid - 0.5

    dr.new_region(zoom_ijk_min, zoom_ijk_max)
  
  # ---------------------------------------------------------------------------
  #
  def selectable_subregions_cb(self):

    ss = self.subregion_selector
    if self.selectable_subregions.get():
      if ss == None:
        import selectregion
        self.subregion_selector = selectregion.Select_Volume_Subregion(self.box_changed_cb)
      button, modifiers = self.subregion_button_spec()
      self.subregion_selector.bind_mouse_button(button, modifiers)
    else:
      if ss:
        ss.unbind_mouse_button()
        ss.box_model.delete_box()
        self.last_subregion = (None, None)
      self.rotate_box.set(False)
    
  # ---------------------------------------------------------------------------
  #
  def subregion_button_cb(self):

    if self.selectable_subregions.get() and self.subregion_selector:
      button, modifiers = self.subregion_button_spec()
      self.subregion_selector.bind_mouse_button(button, modifiers)
      
  # ---------------------------------------------------------------------------
  #
  def subregion_button_spec(self):

    name = self.subregion_button.variable.get()
    name_to_bspec = {'button 1':('1', []), 'ctrl button 1':('1', ['Ctrl']),
                     'button 2':('2', []), 'ctrl button 2':('2', ['Ctrl']),
                     'button 3':('3', []), 'ctrl button 3':('3', ['Ctrl'])}
    bspec = name_to_bspec[name]
    return bspec

  # ---------------------------------------------------------------------------
  #
  def box_changed_cb(self, initial_box):

    if self.auto_show_subregion.get() and not initial_box:
      self.crop_cb()

  # ---------------------------------------------------------------------------
  #
  def rotate_box_cb(self):

    ss = self.subregion_selector
    if ss:
      r = self.rotate_box.get()
      ss.rotate_box(r)

  # ---------------------------------------------------------------------------
  #
  def need_resample(self):

    if self.rotate_box.get():
      return True

    v = active_volume()
    ss = self.subregion_selector
    if v is None or ss is None:
      return False

    pv = getattr(v, 'subregion_of_volume', None)
    if pv and not pv.__destroyed__:
      return True

    m = ss.box_model.model()
    if m is None:
      return False

    same = (m.openState.xform.getCoordFrame() ==
            v.openState.xform.getCoordFrame())
    return not same

  # ---------------------------------------------------------------------------
  #
  def resample(self, replace = False):

    v = active_volume()
    if v is None:
      return

    if (hasattr(v, 'subregion_of_volume')
        and not v.subregion_of_volume.__destroyed__):
      sv = v
      v = v.subregion_of_volume
      if self.last_subregion == (None, None):
        self.last_subregion = (sv, v)

    ss = self.subregion_selector
    if ss is None:
      return

    rvsize = self.resample_voxel_size.get()
    try:
      rstep = [float(f) for f in rvsize.split()]
    except ValueError:
      self.dialog.message('Invalid resample voxel size "%s"' % rvsize)
      return
    
    if len(rstep) == 1:
      rstep *= 3
    if len(rstep) != 3:
      self.dialog.message('Resample voxel size must be 1 or 3 values')
      return

    g = ss.subregion_grid(rstep, v.model_transform(), v.name + ' resampled')
    if g is None:
      self.last_subregion = (None, None)
      return

    lsv, lv = self.last_subregion
    if replace and v is lv and not lsv.__destroyed__:
      sv = lsv
      sv.openState.xform = v.model_transform()
      from volume import replace_data, full_region
      replace_data(sv.data, g)
      sv.add_interpolated_values(v)
      sv.new_region(*full_region(g.size))
      sv.data_changed_cb('coordinates changed')
      sv.show()
    else:
      from VolumeViewer import volume_from_grid_data
      sv = volume_from_grid_data(g, show_data = False)
      sv.openState.xform = v.model_transform()
      if self.rotate_box.get():
        sv.openState.active = False
      sv.add_interpolated_values(v)
      sv.copy_settings_from(v, copy_region = False, copy_xform = False)
      if not replace:
        sv.set_parameters(show_outline_box = True)
      sv.initialize_thresholds()
      self.last_subregion = (sv, v)
      sv.subregion_of_volume = v
      sv.show()
      v.unshow()
    
# -----------------------------------------------------------------------------
# User interface for zones.
#
class Zone_Panel(Hybrid.Popup_Panel):

  name = 'Zone'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)
    
    frame = self.frame
    frame.columnconfigure(0, weight = 1)
    row = 0

    zf = Tkinter.Frame(frame)
    zf.grid(row = row, column = 0, sticky = 'ew')
    zf.columnconfigure(2, weight = 1)
    row += 1

    zb = Tkinter.Button(zf, text = 'Zone', command = self.zone_cb)
    zb.grid(row = 0, column = 0, sticky = 'w')

    zl2 = Tkinter.Label(zf, text = ' near selected atoms. ')
    zl2.grid(row = 0, column = 1, sticky = 'w')

    nzb = Tkinter.Button(zf, text = 'No Zone', command = self.no_zone_cb)
    nzb.grid(row = 0, column = 2, sticky = 'w')
    
    b = self.make_close_button(zf)
    b.grid(row = 0, column = 3, sticky = 'e')

    rs = Hybrid.Scale(frame, 'Radius ', 0, 30, .1, 2)
    rs.frame.grid(row = row, column = 0, sticky = 'ew')
    row += 1
    rs.callback(self.zone_radius_changed_cb)
    rs.entry.bind('<KeyPress-Return>', self.zone_radius_changed_cb)
    self.zone_radius = rs

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    pass
  
  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):

    if data_region:
      self.set_zone_radius_slider_range(data_region)
    
  # ---------------------------------------------------------------------------
  #
  def zone_cb(self, event = None):

    surface = self.zone_surface()
    if surface == None:
      self.dialog.message('No surface shown for active volume')
      return

    radius = self.zone_radius_from_gui()
    if radius == None:
      return

    from chimera import selection
    atoms = selection.currentAtoms()
    bonds = selection.currentBonds()

    from SurfaceZone import path_points, surface_zone
    points = path_points(atoms, bonds, surface.openState.xform.inverse())
    if len(points) > 0:
      self.resize_region_for_zone(points, radius, initial_resize = True)
      surface_zone(surface, points, radius, auto_update = True)
    else:
      self.dialog.message('No atoms are selected for zone')
      
  # ---------------------------------------------------------------------------
  #
  def no_zone_cb(self, event = None):

    surface = self.zone_surface()
    if surface:
      import SurfaceZone
      SurfaceZone.no_surface_zone(surface)
      self.dialog.subregion_panel.zoom_full_cb()

  # ---------------------------------------------------------------------------
  #
  def zone_radius_changed_cb(self, event = None):

    surface = self.zone_surface()
    if surface == None:
        return

    import SurfaceZone
    if SurfaceZone.showing_zone(surface):
      radius = self.zone_radius_from_gui()
      if radius != None:
        points, old_radius = SurfaceZone.zone_points_and_distance(surface)
        self.resize_region_for_zone(points, radius)
        SurfaceZone.surface_zone(surface, points, radius, auto_update = True)
      
  # ---------------------------------------------------------------------------
  #
  def zone_radius_from_gui(self):

    radius = self.zone_radius.value()
    if radius == None:
      self.dialog.message('Radius is set to a non-numeric value')
      return None
    else:
      self.dialog.message('')
    return radius
      
  # ---------------------------------------------------------------------------
  #
  def zone_surface(self):

    data_region = active_volume()
    if data_region == None:
      return None

    surface = data_region.surface_model()
    return surface

  # ---------------------------------------------------------------------------
  # Adjust volume region to include a zone.  If current volume region is
  # much bigger than that needed for the zone, then shrink it.  The purpose
  # of this resizing is to keep the region small so that recontouring is fast,
  # but not resize on every new zone radius.  Resizing on every new zone
  # radius requires recontouring and redisplaying the volume histogram which
  # slows down zone radius updates.
  #
  def resize_region_for_zone(self, points, radius, initial_resize = False):

    dr = active_volume()
    if dr is None:
      return

    from volume import resize_region_for_zone
    new_ijk_min, new_ijk_max = resize_region_for_zone(dr, points,
                                                      radius, initial_resize)
    if not new_ijk_min is None:
      dr.new_region(new_ijk_min, new_ijk_max, save_in_region_queue = False)

  # ---------------------------------------------------------------------------
  # Use diagonal length of bounding box of full data set.
  #
  def set_zone_radius_slider_range(self, data_region):

    import volume
    r = volume.maximum_data_diagonal_length(data_region.data)

    step = r / 1000.0
    if step > 0:
      step = smaller_power_of_ten(step)

    # A step of 0 is supposed to make Tk scale have not discretization.
    # But in Tk 8.4 it appears to discretize giving only integer values for
    # a scale range 0 to 101.

    self.zone_radius.set_range(0, r, step)
  
# -----------------------------------------------------------------------------
#
def smaller_power_of_ten(x):

  from math import pow, floor, log10
  y = pow(10, floor(log10(x)))
  return y

# -----------------------------------------------------------------------------
# User interface for setting general data display and management options.
#
class Display_Options_Panel(Hybrid.Popup_Panel):

  name = 'Data display options'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)
    
    frame = self.frame
    frame.columnconfigure(0, weight = 1)
    
    row = 0

    obf = Tkinter.Frame(frame)
    obf.grid(row = row, column = 0, sticky = 'new')
    obf.columnconfigure(2, weight = 1)
    row += 1

    ob = Hybrid.Checkbutton(obf, 'Show outline box using color ', 0)
    ob.button.grid(row = 0, column = 0, sticky = 'w')
    self.show_outline_box = ob.variable
    self.show_outline_box.add_callback(dialog.redisplay_needed_cb)

    from CGLtk.color import ColorWell
    cb = lambda rgba, d=dialog: d.redisplay_needed_cb()
    obc = ColorWell.ColorWell(obf, width = 25, height = 25, callback = cb)
    obc.grid(row = 0, column = 1, sticky = 'w')
    self.outline_box_color = obc

    lw = Hybrid.Entry(obf, ' linewidth ', 3, '1')
    lw.frame.grid(row = 0, column = 2, sticky = 'w')
    self.outline_width = lw.variable
    lw.entry.bind('<KeyPress-Return>', dialog.redisplay_needed_cb)
    
    b = self.make_close_button(obf)
    b.grid(row = 0, column = 2, sticky = 'e')

    mh = Hybrid.Entry(frame, 'Maximum number of histograms shown ', 4, '3')
    mh.frame.grid(row = row, column = 0, sticky = 'w')
    row += 1
    self.max_histograms = mh.variable
    mh.entry.bind('<KeyPress-Return>',
                  dialog.thresholds_panel.max_histograms_cb)

    icf = Tkinter.Frame(frame)
    icf.grid(row = row, column = 0, sticky = 'new')
    icf.columnconfigure(11, weight = 1)
    row += 1

    icb = Hybrid.Checkbutton(icf, 'Initial colors ', True)
    icb.button.grid(row = 0, column = 0, sticky = 'w')
    self.use_initial_colors = icb.variable
    self.use_initial_colors.add_callback(self.update_global_defaults)
    
    self.initial_colors = []
    for c in range(10):
      from CGLtk.color import ColorWell
      ic = ColorWell.ColorWell(icf, width = 20, height = 20,
                               callback = self.update_global_defaults)
      ic.grid(row = 0, column = c+1, sticky = 'w')
      self.initial_colors.append(ic)

    iu = Hybrid.Checkbutton(frame, 'Update display automatically', True)
    iu.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.immediate_update = iu.variable
    self.immediate_update.add_callback(self.immediate_update_cb)

    sop = Hybrid.Checkbutton_Entries(frame, False,
                                     'Show data when opened if smaller than',
                                     (4, ''),
                                     ' Mvoxels')
    sop.frame.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.show_on_open, self.voxel_limit_for_open = sop.variables
    self.show_on_open.add_callback(self.update_global_defaults)
    sop.entries[0].bind('<KeyPress-Return>', self.update_global_defaults)


    spl = Hybrid.Checkbutton_Entries(frame, True,
                                     'Show plane when data larger than',
                                     (4, ''),
                                     ' Mvoxels')
    spl.frame.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.show_plane, self.voxel_limit_for_plane = spl.variables
    self.show_plane.add_callback(self.update_global_defaults)
    sop.entries[0].bind('<KeyPress-Return>', self.update_global_defaults)
    
    ssb = Hybrid.Checkbutton_Entries(frame, True,
                                     'Adjust step to show at most',
                                     (4, '1'),
                                     ' Mvoxels')
    ssb.frame.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.limit_voxel_count, self.voxel_limit = ssb.variables
    self.limit_voxel_count.add_callback(dialog.redisplay_needed_cb)
    ssb.entries[0].bind('<KeyPress-Return>', dialog.redisplay_cb)

    vc = Tkinter.Frame(frame)
    vc.grid(row = row, column = 0, sticky = 'w')
    row += 1

    from VolumeData import data_cache
    csize = data_cache.size / (2 ** 20)
    cs = Hybrid.Entry(vc, 'Data cache size (Mb)', 4, csize)
    cs.frame.grid(row = 0, column = 0, sticky = 'w')
    self.data_cache_size = cs.variable
    cs.entry.bind('<KeyPress-Return>', self.cache_size_cb)

    cu = Tkinter.Button(vc, text = 'Current use', command = self.cache_use_cb)
    cu.grid(row = 0, column = 1, sticky = 'w')
    
    ac = Hybrid.Checkbutton(frame,
                            'Zoom and center camera when region changes', 0)
    ac.button.grid(row = row, column = 0, sticky = 'w')
    row += 1
    self.adjust_camera = ac.variable

  # ---------------------------------------------------------------------------
  #
  def update_global_defaults(self, event = None):

    from volume import default_settings as ds
    ds.set_defaults_from_gui(self.dialog, global_settings = True,
                             data_settings = False, panel_settings = False)

  # ---------------------------------------------------------------------------
  #
  def immediate_update_cb(self):

    d = self.dialog
    b = d.update_button
    if self.immediate_update.get():
      b.pack_forget()                              # Unshow update button
    else:
      b.pack(d.update_button_pack_settings)        # Show update button
    d.redisplay_needed_cb()

  # ---------------------------------------------------------------------------
  #
  def cache_size_cb(self, event = None):

    size_mb = float_variable_value(self.data_cache_size, None)
    if size_mb:
      from VolumeData import data_cache
      data_cache.resize(size_mb * (2**20))
        
  # ---------------------------------------------------------------------------
  #
  def cache_use_cb(self):

    from VolumeData import memoryuse
    memoryuse.show_memory_use_dialog()
    
  # ---------------------------------------------------------------------------
  #
  def default_settings_changed(self, default_settings, changes):

    self.set_gui_state(changes)
    
  # ---------------------------------------------------------------------------
  #
  def set_gui_state(self, settings):

    for b in ('use_initial_colors', 'immediate_update', 'show_on_open',
              'show_plane', 'adjust_camera'):
      if b in settings:
        var = getattr(self, b)
        var.set(settings[b], invoke_callbacks = False)

    from defaultsettings import number_string
    for v in ('max_histograms', 'voxel_limit_for_open',
              'voxel_limit_for_plane', 'data_cache_size'):
      if v in settings:
        var = getattr(self, v)
        var.set(number_string(settings[v]), invoke_callbacks = False)

    if 'data_cache_size' in settings:
      self.cache_size_cb()

    if 'initial_colors' in settings:
      icolors = settings['initial_colors']
      for c in range(10):
        self.initial_colors[c].showColor(icolors[c], doCallback = False)
    
  # ---------------------------------------------------------------------------
  #
  def get_gui_state(self, settings):

    for b in ('use_initial_colors', 'immediate_update', 'show_on_open',
              'show_plane', 'adjust_camera'):
      var = getattr(self, b)
      settings[b] = var.get()

    from defaultsettings import float_value
    from volume import default_settings
    for v in ('max_histograms', 'voxel_limit_for_open',
              'voxel_limit_for_plane', 'data_cache_size'):
      var = getattr(self, v)
      settings[v] = float_value(var.get(), default_settings[v])

    colors = tuple([c.rgba for c in self.initial_colors])
    settings['initial_colors'] = colors
        
  # ---------------------------------------------------------------------------
  #
  def ijk_step_for_voxel_limit(self, ijk_min, ijk_max, ijk_step):
    
    mvoxels = float_variable_value(self.voxel_limit)
    import volume
    step = volume.ijk_step_for_voxel_limit(ijk_min, ijk_max, ijk_step,
                                           self.limit_voxel_count.get(),
                                           mvoxels)
    return step

  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):

    if data_region == None:
      return
    
    ro = data_region.rendering_options
    if ro:
      self.set_gui_from_rendering_options(ro)

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    self.rendering_options_from_gui(data_region.rendering_options)

  # ---------------------------------------------------------------------------
  #
  def set_gui_from_rendering_options(self, ro):

    self.show_outline_box.set(ro.show_outline_box, invoke_callbacks = False)
    self.outline_box_color.showColor(ro.outline_box_rgb, doCallback = False)
    self.outline_width.set('%.3g' % ro.outline_box_linewidth,
                           invoke_callbacks = False)

    self.set_gui_voxel_limit(ro)

  # ---------------------------------------------------------------------------
  #
  def set_gui_voxel_limit(self, ro):

    self.limit_voxel_count.set(ro.limit_voxel_count, invoke_callbacks = False)
    self.voxel_limit.set('%.3g' % ro.voxel_limit, invoke_callbacks = False)

  # ---------------------------------------------------------------------------
  #
  def rendering_options_from_gui(self, ro):
    
    ro.show_outline_box = self.show_outline_box.get()
    ro.outline_box_rgb = self.outline_box_color.rgb
    ro.outline_box_linewidth = float_variable_value(self.outline_width, 1)
    ro.limit_voxel_count = self.limit_voxel_count.get()
    ro.voxel_limit = float_variable_value(self.voxel_limit, 1)

# -----------------------------------------------------------------------------
# User interface for setting solid rendering options.
#
class Solid_Options_Panel(Hybrid.Popup_Panel):

  name = 'Solid rendering options'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)
    
    frame = self.frame
    frame.columnconfigure(0, weight = 1)

    row = 0

    cmf = Tkinter.Frame(frame)
    cmf.grid(row = row, column = 0, sticky = 'new')
    cmf.columnconfigure(2, weight=1)
    row += 1
    
    b = self.make_close_button(cmf)
    b.grid(row = 0, column = 2, sticky = 'e')

    self.color_mode_descriptions = (
      ('auto', 'auto'),
      ('rgba', 'multi-color transparent'),
      ('rgb', 'multi-color opaque'),
      ('la', 'single-color transparent'),
      ('l', 'single-color opaque'))
    descrip = [d for m,d in self.color_mode_descriptions]
    cm = Hybrid.Option_Menu(cmf, 'Color mode:', *descrip)
    cm.button.configure(indicatoron = False)
    cm.frame.grid(row = 0, column = 0, sticky = 'w')
    self.color_mode = cm.variable
    cm.add_callback(dialog.redisplay_needed_cb)

    cb = Hybrid.Option_Menu(cmf, '', '4 bits', '8 bits', '12 bits', '16 bits')
    cb.button.configure(indicatoron = False)
    cb.frame.grid(row = 0, column = 1, sticky = 'w')
    self.color_mode_bits = cb.variable
    cb.add_callback(dialog.redisplay_needed_cb)

    pmodes = (('auto','auto'),
              ('2d-xyz','x, y or z planes'),
              ('2d-x','x planes'),
              ('2d-y','y planes'),
              ('2d-z','z planes'),
              ('3d','perpendicular to view'))
    pm = Hybrid.Option_Menu(frame, 'Projection mode', *[n for m,n in pmodes])
    pm.button.configure(indicatoron = False)
    pm.frame.grid(row = row, column = 0, sticky = 'w')
    row += 1
    self.projection_mode = pm.variable
    pm.add_callback(dialog.redisplay_needed_cb)
    self.proj_mode_name = dict(pmodes)
    self.proj_mode_from_name = dict([(n,m) for m,n in pmodes])
    
    mipd = 'Maximum intensity projection'
    import _volume
    if not _volume.maximum_intensity_projection_supported():
      mipd = mipd + ' (not available)'
    mp = Hybrid.Checkbutton(frame, mipd, 0)
    mp.button.grid(row = row, column = 0, sticky = 'w')
    row += 1
    self.maximum_intensity_projection = mp.variable
    self.maximum_intensity_projection.add_callback(dialog.redisplay_needed_cb)

    dt = Hybrid.Checkbutton(frame, 'Dim transparent voxels', False)
    dt.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.dim_transparent_voxels = dt.variable
    self.dim_transparent_voxels.add_callback(dialog.redisplay_needed_cb)
    
    bt = Hybrid.Checkbutton(frame, 'Solid brightness correction', 0)
    bt.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.bt_correction = bt.variable
    self.bt_correction.add_callback(dialog.redisplay_needed_cb)
    
    mt = Hybrid.Checkbutton(frame, 'Minimize texture memory use', 0)
    mt.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.minimal_texture_memory = mt.variable
    self.minimal_texture_memory.add_callback(dialog.redisplay_needed_cb)
    
    vli = Hybrid.Checkbutton(frame, 'Solid linear interpolation', 0)
    vli.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.linear_interpolation = vli.variable
    self.linear_interpolation.add_callback(dialog.redisplay_needed_cb)

  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):

    if data_region == None:
      return
    
    ro = data_region.rendering_options
    if ro:
      self.set_gui_from_rendering_options(ro)

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    self.rendering_options_from_gui(data_region.rendering_options)

  # ---------------------------------------------------------------------------
  #
  def set_gui_from_rendering_options(self, ro):

    self.maximum_intensity_projection.set(ro.maximum_intensity_projection,
                                          invoke_callbacks = False)
    m,b = self.color_mode_from_name(ro.color_mode)
    self.color_mode.set(m, invoke_callbacks = False)
    self.color_mode_bits.set(b, invoke_callbacks = False)
    self.projection_mode.set(self.proj_mode_name[ro.projection_mode],
                             invoke_callbacks = False)
    self.dim_transparent_voxels.set(ro.dim_transparent_voxels,
                                    invoke_callbacks = False)
    self.bt_correction.set(ro.bt_correction, invoke_callbacks = False)
    self.minimal_texture_memory.set(ro.minimal_texture_memory,
                                    invoke_callbacks = False)
    self.linear_interpolation.set(ro.linear_interpolation,
                                  invoke_callbacks = False)

  # ---------------------------------------------------------------------------
  #
  def rendering_options_from_gui(self, ro):
    
    ro.color_mode = self.color_mode_name()
    ro.projection_mode = self.proj_mode_from_name[self.projection_mode.get()]
    ro.maximum_intensity_projection = self.maximum_intensity_projection.get()
    ro.dim_transparent_voxels = self.dim_transparent_voxels.get()
    ro.bt_correction = self.bt_correction.get()
    ro.minimal_texture_memory = self.minimal_texture_memory.get()
    ro.linear_interpolation = self.linear_interpolation.get()

  # ---------------------------------------------------------------------------
  #
  def color_mode_name(self):

    cmode = self.color_mode.get()
    mode = [m for m,d in self.color_mode_descriptions if d == cmode][0]
    mname = mode + self.color_mode_bits.get()[:-5] # strip off ' bits' text
    return mname

  # ---------------------------------------------------------------------------
  #
  def color_mode_from_name(self, mname):

    for prefix, descrip in self.color_mode_descriptions:
      if mname.startswith(prefix):
        m = descrip
        break
    b = {'4':'4 bits', '8':'8 bits', '2':'12 bits', '6':'16 bits'}[mname[-1]]
    return m,b

# -----------------------------------------------------------------------------
# User interface for setting surface and mesh rendering options.
#
class Surface_Options_Panel(Hybrid.Popup_Panel):

  name = 'Surface and Mesh options'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Hybrid.Popup_Panel.__init__(self, parent)
    
    frame = self.frame
    frame.columnconfigure(0, weight = 1)
    
    row = 0

    smf = Tkinter.Frame(frame)
    smf.grid(row = row, column = 0, sticky = 'new')
    smf.columnconfigure(4, weight = 1)
    row += 1
    
    ssm = Hybrid.Checkbutton_Entries(smf, False,
                                     'Surface smoothing iterations', (2, ''),
                                     ' factor', (4,''))
    ssm.frame.grid(row = 0, column = 0, sticky = 'nw')
    self.surface_smoothing, self.smoothing_iterations, self.smoothing_factor = ssm.variables
    self.surface_smoothing.add_callback(dialog.redisplay_needed_cb)
    for e in ssm.entries:
      e.bind('<KeyPress-Return>', dialog.redisplay_cb)
    
    b = self.make_close_button(smf)
    b.grid(row = 0, column = 4, sticky = 'e')
    
    sd = Hybrid.Checkbutton_Entries(frame, False,
                                    'Subdivide surface',
                                    (2, '1'),
                                    ' times')
    sd.frame.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.subdivide_surface, self.subdivision_levels = sd.variables
    self.subdivide_surface.add_callback(dialog.redisplay_needed_cb)
    sd.entries[0].bind('<KeyPress-Return>', dialog.redisplay_cb)
    
    sl = Hybrid.Checkbutton(frame, 'Smooth mesh lines', 0)
    sl.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.smooth_lines = sl.variable
    self.smooth_lines.add_callback(dialog.redisplay_needed_cb)
    
    sm = Hybrid.Checkbutton(frame, 'Square mesh', False)
    sm.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.square_mesh = sm.variable
    self.square_mesh.add_callback(dialog.redisplay_needed_cb)

    ltf = Tkinter.Frame(frame)
    ltf.grid(row = row, column = 0, sticky = 'nw')
    row += 1

    lt = Hybrid.Entry(ltf, 'Mesh line thickness', 3, suffix = 'pixels')
    lt.frame.grid(row = 0, column = 0, sticky = 'w')
    lt.entry.bind('<KeyPress-Return>', dialog.redisplay_cb)
    self.line_thickness = lt.variable
    
    ds = Hybrid.Checkbutton(frame, 'Dim transparent surface/mesh', 0)
    ds.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.dim_transparency = ds.variable
    self.dim_transparency.add_callback(dialog.redisplay_needed_cb)
    
    ol = Hybrid.Checkbutton(frame, 'One transparent layer', False)
    ol.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.one_transparent_layer = ol.variable
    self.one_transparent_layer.add_callback(dialog.redisplay_needed_cb)
    
    ml = Hybrid.Checkbutton(frame, 'Mesh lighting', 1)
    ml.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.mesh_lighting = ml.variable
    self.mesh_lighting.add_callback(dialog.redisplay_needed_cb)
    
    l2 = Hybrid.Checkbutton(frame, 'Two-sided surface lighting', 1)
    l2.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.two_sided_lighting = l2.variable
    self.two_sided_lighting.add_callback(dialog.redisplay_needed_cb)
    
    fn = Hybrid.Checkbutton(frame, 'Light flip side for thresholds < 0', 1)
    fn.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.flip_normals = fn.variable
    self.flip_normals.add_callback(dialog.redisplay_needed_cb)
    
    cp = Hybrid.Checkbutton(frame, 'Cap high values at box faces', True)
    cp.button.grid(row = row, column = 0, sticky = 'nw')
    row += 1
    self.cap_faces = cp.variable
    self.cap_faces.add_callback(dialog.redisplay_needed_cb)

  # ---------------------------------------------------------------------------
  #
  def update_panel_widgets(self, data_region):

    if data_region == None:
      return
    
    ro = data_region.rendering_options
    if ro:
      self.set_gui_from_rendering_options(ro)

  # ---------------------------------------------------------------------------
  #
  def use_gui_settings(self, data_region):

    self.rendering_options_from_gui(data_region.rendering_options)

  # ---------------------------------------------------------------------------
  #
  def set_gui_from_rendering_options(self, ro):

    self.dim_transparency.set(ro.dim_transparency, invoke_callbacks = 0)
    self.one_transparent_layer.set(ro.one_transparent_layer,
                                   invoke_callbacks = 0)
    self.line_thickness.set('%.3g' % ro.line_thickness, invoke_callbacks = 0)
    self.smooth_lines.set(ro.smooth_lines, invoke_callbacks = 0)
    self.mesh_lighting.set(ro.mesh_lighting, invoke_callbacks = 0)
    self.two_sided_lighting.set(ro.two_sided_lighting, invoke_callbacks = 0)
    self.flip_normals.set(ro.flip_normals, invoke_callbacks = 0)
    self.subdivide_surface.set(ro.subdivide_surface, invoke_callbacks = 0)
    self.subdivision_levels.set('%d' % ro.subdivision_levels,
                                invoke_callbacks = 0)
    self.surface_smoothing.set(ro.surface_smoothing, invoke_callbacks = 0)
    self.smoothing_iterations.set('%d' % ro.smoothing_iterations,
                                  invoke_callbacks = 0)
    self.smoothing_factor.set('%.3g' % ro.smoothing_factor,
                              invoke_callbacks = 0)
    self.square_mesh.set(ro.square_mesh, invoke_callbacks = 0)
    self.cap_faces.set(ro.cap_faces, invoke_callbacks = False)

  # ---------------------------------------------------------------------------
  #
  def rendering_options_from_gui(self, ro):

    ro.dim_transparency = self.dim_transparency.get()
    ro.one_transparent_layer = self.one_transparent_layer.get()
    lt = float_variable_value(self.line_thickness, 1)
    if lt <= 0:
      lt = 1
    ro.line_thickness = lt
    ro.smooth_lines = self.smooth_lines.get()
    ro.mesh_lighting = self.mesh_lighting.get()
    ro.two_sided_lighting = self.two_sided_lighting.get()
    ro.flip_normals = self.flip_normals.get()
    ro.subdivide_surface = self.subdivide_surface.get()
    sl = integer_variable_value(self.subdivision_levels, 1)
    if sl < 0:
      sl = 0
    ro.subdivision_levels = sl
    ro.surface_smoothing = self.surface_smoothing.get()
    si = integer_variable_value(self.smoothing_iterations, 2)
    if si < 0:
      si = 0
    ro.smoothing_iterations = si
    sf = float_variable_value(self.smoothing_factor, .3)
    if sf < 0: sf = 0
    elif sf > 1: sf = 1
    ro.smoothing_factor = sf
    ro.square_mesh = self.square_mesh.get()
    ro.cap_faces = self.cap_faces.get()

# -----------------------------------------------------------------------------
#
nbfont = None
def non_bold_font(frame):

  global nbfont
  if nbfont == None:
    e = Tkinter.Entry(frame)
    nbfont = e['font']
    e.destroy()
  return nbfont
  
# -----------------------------------------------------------------------------
#
def place_in_grid(widget, place):

  if place:
    widget.grid()
  else:
    widget.grid_remove()

# -----------------------------------------------------------------------------
#
def split_fields(s, nfields):

  fields = s.split()
  leading = ' '.join(fields[:nfields])
  trailing = ' '.join(fields[nfields:])
  return leading, trailing

# -----------------------------------------------------------------------------
#
def integer_variable_value(v, default = None):

  try:
    return int(v.get())
  except:
    return default
  
# -----------------------------------------------------------------------------
#
def integer_variable_values(v, default = None):

  fields = v.get().split(' ')
  values = []
  for field in fields:
    try:
      value = int(field)
    except:
      value = default
    values.append(value)
  return values
    
# -----------------------------------------------------------------------------
#
def float_variable_value(v, default = None):

  return string_to_float(v.get(), default)
    
# -----------------------------------------------------------------------------
#
def string_to_float(v, default = None):

  try:
    return float(v)
  except:
    return default
    
# -----------------------------------------------------------------------------
# Format a number using %g but do not use scientific notation for large
# values if the number can be represented more compactly without it.
#
def float_format(value, precision):

  if value == None:
    return ''
  
  import math

  if (abs(value) >= math.pow(10.0, precision) and
      abs(value) < math.pow(10.0, precision + 4)):
    format = '%.0f'
  else:
    format = '%%.%dg' % precision

  if value == 0:
    value = 0           # Avoid including sign bit for -0.0.

  text = format % value

  return text

# -----------------------------------------------------------------------------
#
def show_volume_file_browser(dialog_title, volumes_cb = None,
                             show_data = False, show_volume_dialog = False):

  def grids_cb(grids):
    from volume import volume_from_grid_data
    vlist = [volume_from_grid_data(g, show_data = show_data,
                                   show_dialog = show_volume_dialog)
             for g in grids]
    if volumes_cb:
      volumes_cb(vlist)

  from VolumeData import show_grid_file_browser
  show_grid_file_browser(dialog_title, grids_cb)

# -----------------------------------------------------------------------------
#
def subregion_selection_bounds():

  d = volume_dialog()
  if d is None:
    return None, None
  ijk_min, ijk_max = d.subregion_panel.subregion_box_bounds()
  return ijk_min, ijk_max

# -----------------------------------------------------------------------------
#
def active_volume():

  vv = volume_dialog()
  if vv:
    dr = vv.focus_region
  else:
    dr = None
  return dr

# -----------------------------------------------------------------------------
#
def set_active_volume(dr):

  vv = volume_dialog(create = True)
  vv.display_region_info(dr)
    
# -----------------------------------------------------------------------------
#
def volume_dialog(create=False):

  from chimera import dialogs
  return dialogs.find(Volume_Dialog.name, create=create)

# -----------------------------------------------------------------------------
#
def show_volume_dialog():

  from chimera import dialogs
  d = volume_dialog(create = True)
  # Avoid transient dialog resizing when created and mapped for first time.
  d.toplevel_widget.update_idletasks()
  d.enter()
  return d
    
# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Volume_Dialog.name, Volume_Dialog, replace = 1)
