# -----------------------------------------------------------------------------
# Dialog to allow placing markers on volume data and connecting them with
# links.
#
import chimera
from chimera.baseDialog import ModelessDialog
from CGLtk.Hybrid import Popup_Panel

from markerset import marker_sets, selected_markers, selected_links

# -----------------------------------------------------------------------------
#
class Volume_Path_Dialog(ModelessDialog):

  title = 'Volume Tracer'
  name = 'volume tracer'
  buttons = ('Close',)
  help = 'ContributedSoftware/volumepathtracer/framevolpath.html'

  # ---------------------------------------------------------------------------
  #
  def fillInUI(self, parent):

    self.active_marker_set = None
    self.form_link_trigger = None
    self.last_selected_marker = None    # For linking consecutively selected
                                        #   markers.
    self.grabbed_marker = None
    self.pause_marker_placement = False   # After loop closure.
    
    self.gui_panels = []
    self.open_dialog = None

    tw = parent.winfo_toplevel()
    self.toplevel_widget = tw
    tw.withdraw()
    
    parent.columnconfigure(0, weight = 1)
    row = 1

    import Tkinter
    from CGLtk import Hybrid

    menubar = Tkinter.Menu(parent, type = 'menubar', tearoff = False)
    tw.config(menu = menubar)

    file_menu_entries = (('Open marker set...', self.open_marker_set_cb),
                         ('New marker set', self.new_marker_set_cb),
                         ('Save current marker set', self.save_marker_set_cb),
                         ('Save current marker set as...',
                          self.save_marker_set_as_cb),
                         ('Save all marker sets as...',
                          self.save_all_marker_sets_cb),
                         ('Save selected marker sets as...',
                          self.save_selected_marker_sets_cb),
                         ('Close marker set', self.close_marker_set_cb),
                         )
    Hybrid.cascade_menu(menubar, 'File', file_menu_entries)

    action_menu_entries = (('Show markers',
                            lambda s=self: s.show_chosen_markers(True)),
                           ('Hide markers',
                            lambda s=self: s.show_chosen_markers(False)),
                           ('Delete markers', self.delete_markers_cb),
                           'separator',
                           ('Show links',
                            lambda s=self: s.show_chosen_links(True)),
                           ('Hide links',
                            lambda s=self: s.show_chosen_links(False)),
                           ('Delete links', self.delete_links_cb),
                           'separator',
                           ('Show marker notes',
                            lambda s=self: s.show_marker_notes(True)),
                           ('Hide marker notes',
                            lambda s=self: s.show_marker_notes(False)),
                           ('Delete marker notes',
                            self.delete_marker_notes_cb),
                           'separator',
                           ('Transfer selected markers to current set',
                            self.transfer_markers_cb),
                           )
    am = Hybrid.cascade_menu(menubar, 'Actions', action_menu_entries)

    # Create mouse modes menu
    ub = self.update_mouse_binding_cb
    mouse_menu_entries = (('Place markers on high density', True, ub),
                          ('Place markers on data planes', False, ub),
                          ('Place markers on surfaces', False, ub),
                          ('Place markers outside data', False, ub),
                          ('Place markers while dragging', False, ub),
                          ('Move and resize markers', False, ub),
                          ('Marker color matches volume color', False, None),
                          ('Link new marker to selected marker', True, None),
                          ('Link consecutively selected markers', False,
                           self.consecutive_selection_cb),
                          )
    mmenu = Hybrid.cascade_menu(menubar, 'Mouse')
    mmvars = Hybrid.add_menu_entries(mmenu, mouse_menu_entries)
    (self.place_markers_on_spots, self.place_markers_on_planes,
     self.place_markers_on_surfaces, self.place_markers_outside_data,
     self.place_markers_continuously,
     self.move_markers, self.marker_matches_volume_color,
     self.link_to_selected, self.link_consecutive) = mmvars
    self.mouse_mode_vars = zip([m[0] for m in mouse_menu_entries], mmvars)

    # Create popup panels
    panel_classes = (Hybrid.Feature_Buttons_Panel, Marker_Set_Menu_Panel,
                     Marker_Sets_Panel, Rename_Panel,
                     Mouse_Button_Panel, Mouse_Mode_Panel,
                     Color_Radius_Panel, Note_Panel,
                     Spline_Panel, Slice_Panel, Surface_Panel)

    for pc in panel_classes:
      p = pc(self, parent)
      p.frame.grid(row = row, column = 0, sticky = 'news')
      p.frame.grid_remove()
      p.panel_row = row
      self.gui_panels.append(p)
      row = row + 1

    (self.feature_buttons_panel, self.marker_set_menu_panel,
     self.marker_sets_panel, self.rename_panel, self.mouse_button_panel,
     self.mouse_mode_panel, self.color_radius_panel, self.note_panel,
     self.spline_panel, self.slice_panel, self.surface_panel) = self.gui_panels

    sorted_panels = list(self.gui_panels)
    sorted_panels.sort(lambda p1, p2: cmp(p1.name, p2.name))
    self.feature_buttons_panel.set_panels(sorted_panels)

    # Create features menu
    fmenu = Hybrid.cascade_menu(menubar, 'Features')
    for p in sorted_panels:
      fmenu.add_checkbutton(label = p.name,
      		            variable = p.panel_shown_variable.tk_variable)
    fmenu.add_separator()
    fmenu.add_command(label = 'Show only default panels',
    		      command = self.show_default_panels_cb)
#    fmenu.add_command(label = 'Save default dialog settings',
#                      command = self.save_default_settings_cb)
#    fmenu.add_command(label = 'Use factory default settings',
#     		       command = self.use_factory_defaults_cb)

    from chimera.tkgui import aquaMenuBar
    aquaMenuBar(menubar, parent, row = 0)

    # Make marker sets panel expand vertically when dialog resized
    parent.rowconfigure(self.marker_sets_panel.panel_row, weight = 1)

    self.default_panels = (self.marker_set_menu_panel,
                           self.mouse_button_panel,
                           self.color_radius_panel)
    for p in self.default_panels:
        p.show_close_button = False
        p.panel_shown_variable.set(True)
    
    msg = Tkinter.Label(parent, width = 40, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.message_label = msg

    callbacks = (self.mouse_down_cb, self.mouse_drag_cb, self.mouse_up_cb)
    from chimera import mousemodes
    mousemodes.addFunction('mark volume', callbacks, self.mouse_mode_icon())

    import markerset as mset
    mset.add_marker_set_opened_callback(self.add_marker_sets)
    mset.add_marker_set_closed_callback(self.marker_sets_closed_cb)
    self.add_marker_sets(marker_sets())

    import SimpleSession
    chimera.triggers.addHandler(SimpleSession.SAVE_SESSION,
				self.save_session_cb, None)

  # ---------------------------------------------------------------------------
  #
  def mouse_mode_icon(self):

    import os.path
    icon_path = os.path.join(os.path.dirname(__file__), 'marker.gif')
    from PIL import Image
    image = Image.open(icon_path)
    from chimera import chimage
    from chimera import tkgui
    icon = chimage.get(image, tkgui.app)
    return icon
      
  # ---------------------------------------------------------------------------
  #
  def map(self, event):

    self.note_panel.register_for_selection_updates(True)
    self.color_radius_panel.register_for_selection_updates(True)

  # ---------------------------------------------------------------------------
  #
  def unmap(self, event):

    self.note_panel.register_for_selection_updates(False)
    self.color_radius_panel.register_for_selection_updates(False)
    
  # ---------------------------------------------------------------------------
  #
  def save_session_cb(self, trigger, x, file):

    import session
    session.save_path_tracer_state(self, file)

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
  def show_default_panels_cb(self):

    self.show_panels(map(lambda p: p.name, self.default_panels))
    
  # ---------------------------------------------------------------------------
  #
  def active_set(self):

    marker_set = self.active_marker_set
    if marker_set == None:
      marker_set = self.new_marker_set_cb()
    return marker_set
    
  # ---------------------------------------------------------------------------
  #
  def open_marker_set_cb(self):

    if self.open_dialog == None:
      import OpenSave
      d = OpenSave.OpenModeless(title = 'Open Marker Set',
                                filters = [('Chimera Markers', '*.cmm')],
                                defaultFilter = 0,
                                command = self.open_file_dialog_cb)
      self.open_dialog = d
    else:
      self.open_dialog.enter()

  # ---------------------------------------------------------------------------
  #
  def open_file_dialog_cb(self, apply, dialog):

    if not apply:
      return            # User pressed Cancel

    for path in dialog.getPaths():
      self.open_marker_set(path)
    
  # ---------------------------------------------------------------------------
  #
  def save_marker_set_cb(self):

    if self.active_marker_set:
      self.save_marker_sets([self.active_marker_set], ask_path = 0)
      
  # ---------------------------------------------------------------------------
  #
  def save_marker_set_as_cb(self):

    if self.active_marker_set:
      self.save_marker_sets([self.active_marker_set], ask_path = 1)
    
  # ---------------------------------------------------------------------------
  #
  def save_all_marker_sets_cb(self):

    self.save_marker_sets(marker_sets(), ask_path = True)
    
  # ---------------------------------------------------------------------------
  #
  def save_selected_marker_sets_cb(self):

    mslist = self.selected_marker_sets()
    self.save_marker_sets(mslist, ask_path = 1)

  # ---------------------------------------------------------------------------
  # Save marker sets in one file.
  #
  def save_marker_sets(self, mslist, path = None, ask_path = True):

    if len(mslist) == 0:
      self.message('No marker sets saved')
      return

    if path == None:
      path = self.get_file_path(mslist, ask_path)
      if not path:
        return

    out = open(path, 'w')
    import markerset
    markerset.save_marker_sets(mslist, out)
    out.close()

    for ms in mslist:
      ms.file_path = path

  # ---------------------------------------------------------------------------
  #
  def get_file_path(self, mslist, ask_path):

    paths = {}
    for ms in mslist:
      paths[ms.file_path] = 1

    if len(paths) == 1:
      common_path = paths.keys()[0]
    else:
      common_path = None
      
    if not ask_path and common_path:
      return common_path
    
    path_list = filter(lambda p: p, paths.keys())
    if path_list:
      default_path = path_list[0]
    else:
      default_path = None

    if len(mslist) == 1:
      title = 'Save Marker Set %s' % ms.name
    else:
      title = 'Save %d Marker Sets' % len(mslist)
      
    path = self.ask_for_save_path(title, default_path)

    return path

  # ---------------------------------------------------------------------------
  #
  def ask_for_save_path(self, title, default_path):

    if default_path:
      import os.path
      initialdir, initialfile = os.path.split(default_path)
    else:
      initialdir, initialfile = None, None

    import OpenSave
    d = OpenSave.SaveModal(title = title,
                           initialdir = initialdir,
                           initialfile = initialfile,
                           filters = [('Chimera Markers', '*.cmm', '')])
    paths_and_types = d.run(self.toplevel_widget)
    if paths_and_types and len(paths_and_types) == 1:
      path = paths_and_types[0][0]
    else:
      path = None

    return path

  # ---------------------------------------------------------------------------
  #
  def close_marker_set_cb(self):

    for ms in self.selected_marker_sets():
      ms.close()

  # ---------------------------------------------------------------------------
  #
  def marker_sets_closed_cb(self, msets):

    if self.active_marker_set in msets:
      omsets = marker_sets()
      if omsets:
        ams = omsets[0]
      else:
        ams = None
      self.set_active_marker_set(ams)

    self.update_marker_set_listbox()

  # ---------------------------------------------------------------------------
  #
  def set_active_marker_set(self, marker_set):

    self.active_marker_set = marker_set
    if marker_set:
      name = marker_set.name
    else:
      name = ''
    self.rename_panel.set_rename_text(name)
    self.marker_set_menu_panel.set_menu(name, invoke_callbacks = False)
          
  # ---------------------------------------------------------------------------
  #
  def rename_active_marker_set(self, name):

    ams = self.active_marker_set
    if ams is None:
      return
    
    ams.name = name
    self.marker_sets_panel.rename_entry(ams)
    self.marker_set_menu_panel.rename_entry(ams)
    
  # ---------------------------------------------------------------------------
  #
  def update_marker_set_listbox(self):

    msets = marker_sets()
    self.marker_sets_panel.update_list(msets)
    self.marker_set_menu_panel.update_menu(msets, self.active_marker_set)

  # ---------------------------------------------------------------------------
  # If no list box line is selected, include the active marker set.
  #
  def selected_marker_sets(self):

    marker_sets = self.marker_sets_panel.selected_marker_sets()
    if len(marker_sets) == 0 and self.active_marker_set:
      marker_sets = [self.active_marker_set]
      
    return marker_sets

  # ---------------------------------------------------------------------------
  #
  def new_marker_set_cb(self):

    n = self.highest_marker_set_number()
    if n == None:
      n = 0
    name = 'marker set %d' % (n + 1)
    from markerset import Marker_Set
    ms = Marker_Set(name)
    ms.marker_model()           # Create model
    return ms

  # ---------------------------------------------------------------------------
  #
  def highest_marker_set_number(self):

    num = None
    for ms in marker_sets():
      if ms.name.startswith('marker set '):
        suffix = ms.name[len('marker set '):]
        try:
          s = int(suffix)
        except:
          continue
        if num == None or s > num:
          num = s
    return num
    
  # ---------------------------------------------------------------------------
  #
  def add_marker_sets(self, msets, remove_empty_duplicate_sets = True):

    if remove_empty_duplicate_sets:
        self.remove_empty_duplicate_marker_sets(msets)
    for ms in msets:
      self.marker_sets_panel.add_entry(ms)
      self.marker_set_menu_panel.add_entry(ms)
    if msets:
      self.set_active_marker_set(msets[0])

  # ---------------------------------------------------------------------------
  #
  def remove_empty_duplicate_marker_sets(self, msets):
    
    mss = set(msets)
    names = set([ms.name for ms in msets])
    dms = [ms for ms in marker_sets()
           if not ms in mss and ms.name in names and len(ms.markers()) == 0]
    for ms in dms:
      ms.close()
    
  # ---------------------------------------------------------------------------
  #
  def grab_marker(self, pointer_x, pointer_y):

    import markerset
    marker = markerset.pick_marker(pointer_x, pointer_y, marker_sets())
    if marker:
      self.message('Grabbed marker')
      self.last_pointer_xy = (pointer_x, pointer_y)
    self.grabbed_marker = marker

    return marker
    
  # ---------------------------------------------------------------------------
  #
  def add_marker_at_screen_xy(self, pointer_x, pointer_y,
                              minimum_spacing = None):

    place_on_spot = self.place_markers_on_spots.get()
    place_on_plane = self.place_markers_on_planes.get()
    place_on_surface = self.place_markers_on_surfaces.get()
    place_outside = self.place_markers_outside_data.get()
    m = self.add_marker(pointer_x, pointer_y, place_on_spot,
                        place_on_plane, place_on_surface,
                        place_outside, minimum_spacing)
    return m
    
  # ---------------------------------------------------------------------------
  #
  def add_marker(self, pointer_x, pointer_y,
                 place_on_spot, place_on_plane,
                 place_on_surface, place_outside_data,
                 minimum_spacing = None):

    slice, no_slice_warning = self.data_slice(pointer_x, pointer_y)

    sp = self.slice_panel
    sp.erase_slice_line()
        
    if slice:
      sp.display_slice_line(slice)
      sp.update_slice_graphs(slice)

    marker_set = self.active_marker_set
    if marker_set == None:
      marker_set = self.new_marker_set_cb()

    if place_on_spot and slice:
      m = self.mark_first_maximum(slice, marker_set,
                                  minimum_spacing = minimum_spacing)
      if m:
        return m

    if place_on_plane and slice:
      m = self.mark_slice_midpoint(slice, marker_set,
                                   minimum_spacing = minimum_spacing)
      self.message('Dropped marker halfway through data')
      return m
    if place_on_surface:
      m = self.mark_surface(pointer_x, pointer_y, marker_set,
                            minimum_spacing = minimum_spacing)
      if m:
        self.message('Dropped marker on surface')
        return m
    if place_outside_data:
      prevent_camera_adjustment(marker_set)
      m = self.mark_clip_planes_midpoint(pointer_x, pointer_y, marker_set,
                                         minimum_spacing = minimum_spacing)
      self.message('Dropped marker between clip planes')
      return m

    if (place_on_spot or place_on_plane) and slice is None:
      self.message(no_slice_warning)
      return

    self.message('')
    
  # ---------------------------------------------------------------------------
  #
  def place_marker_continuous(self, x, y):

    # Determine minimum spacing.
    from CGLtk.Hybrid import float_variable_value
    vspacing = float_variable_value(self.mouse_mode_panel.marker_spacing, 10.0)
    from VolumeViewer import active_volume
    v = active_volume()
    if v:
      spacing = vspacing * min(v.data.step)
    else:
      spacing = vspacing * pixel_size_at_midplane()

    # Place marker
    m = self.add_marker_at_screen_xy(x, y, minimum_spacing = spacing)

    # Close loop if near starting marker
    loop_closed = False
    if m:
      from surface import chain_end_marker
      m0 = chain_end_marker(m)
      if m0 and distance(m.xyz(), m0.xyz()) < spacing:
        e = self.create_link(m, m0)
        if e:
          e.deselect()
          m.deselect()
          loop_closed = True

    return m, loop_closed
    
  # ---------------------------------------------------------------------------
  # Used with 3D input devices.
  #
  # The user interface option to turn on and off marker placement and motion
  # apply are intended only to restrict mouse input.  So they are not checked
  # here.
  #
  def add_marker_3d(self, xyz):

    marker_set = self.active_marker_set
    if marker_set == None:
      marker_set = self.new_marker_set_cb()

    m = self.mark_data(xyz, marker_set)
    if m is None:
      m = self.mark_point(xyz, marker_set)
    return m
    
  # ---------------------------------------------------------------------------
  #
  def grab_marker_3d(self, xyz):

    import markerset
    marker = markerset.pick_marker_3d(xyz, marker_sets())
    if marker:
      self.message('Grabbed marker')
    self.grabbed_marker = marker
    return marker
    
  # ---------------------------------------------------------------------------
  #
  def select_marker_3d(self, xyz):

    import markerset
    marker = markerset.pick_marker_3d(xyz, marker_sets())
    if marker:
      self.select_marker(marker)
    return marker

  # ---------------------------------------------------------------------------
  #
  def data_slice(self, pointer_x, pointer_y):

    from VolumeViewer import active_volume
    v = active_volume()
    if v is None:
      return None, 'No volume region'

    if not v.shown():
      return None, 'Volume not shown'

    from VolumeViewer.slice import volume_segment
    xyz_in, xyz_out, shown = volume_segment(v, pointer_x, pointer_y)

    if not shown:
      return None, 'Volume not shown'

    if xyz_in == None or xyz_out == None:
      return None, 'No intersection with volume'

    slice = Slice(v, xyz_in, xyz_out)

    return slice, ''
    
  # ---------------------------------------------------------------------------
  #
  def mark_first_maximum(self, slice, marker_set, minimum_spacing = None):

    t_max, v_max, trace = slice.first_maximum_above_threshold()
    if t_max == None:
      return None

    self.slice_panel.show_slice_maximum(t_max)

    dr_xyz = linear_combination(1-t_max, slice.xyz_in, t_max, slice.xyz_out)
    ms_xyz = transform_coordinates(dr_xyz, slice.data_region.model_transform(),
				   marker_set.transform())

    crp = self.color_radius_panel
    if self.marker_matches_volume_color.get():
      rgba = trace.visible_data.volume_rgba(v_max)
    else:
      rgba = crp.marker_color.rgba

    marker_radius, link_radius = crp.marker_and_link_radius(marker_set,
                                                            slice.data_region)
    marker = self.drop_and_link_marker(ms_xyz, rgba,
				       marker_radius, link_radius,
                                       marker_set, minimum_spacing)
    if marker:
      self.message('Dropped marker on data')
    slice.marker = marker
    
    return marker
    
  # ---------------------------------------------------------------------------
  # Place marker if data value is above detection threshold.
  #
  # Xyz position must be in Chimera world coordinates.
  #
  def mark_data(self, xyz, marker_set):

    from VolumeViewer import active_volume
    v = active_volume()
    if v is None:
      return None

    xf = v.model_transform()
    if xf == None:
      return None

    from Matrix import apply_inverse_matrix
    v_xyz = apply_inverse_matrix(xf, xyz)
    ms_xyz = apply_inverse_matrix(marker_set.transform(), xyz)

    visible_data = self.visible_data_above_threshold(v, v_xyz)
    if visible_data == None:
      return None

    rp = self.color_radius_panel
    if self.marker_matches_volume_color.get():
      data_value = visible_data.interpolated_value(v_xyz)
      rgba = visible_data.volume_rgba(data_value)
    else:
      rgba = rp.marker_color.rgba

    marker_radius, link_radius = rp.marker_and_link_radius(marker_set)
    marker = self.drop_and_link_marker(ms_xyz, rgba,
				       marker_radius, link_radius,
                                       marker_set)
    self.message('Dropped marker on data')
    return marker

  # ---------------------------------------------------------------------------
  #
  def visible_data_above_threshold(self, data_region, xyz):

    vdlist = visible_data_components(data_region)
    for visdata in vdlist:
      if visdata.interpolated_value(xyz) > visdata.threshold():
	return visdata
    return None

  # ---------------------------------------------------------------------------
  #
  def mark_slice_midpoint(self, slice, marker_set = None,
                          minimum_spacing = None):

    if marker_set is None:
      marker_set = self.active_set()

    dr_xyz = linear_combination(.5, slice.xyz_in, .5, slice.xyz_out)
    ms_xyz = transform_coordinates(dr_xyz, slice.data_region.model_transform(),
				   marker_set.transform())
    rp = self.color_radius_panel
    rgba = rp.marker_color.rgba
    marker_radius, link_radius = rp.marker_and_link_radius(marker_set,
                                                           slice.data_region)
    m = self.drop_and_link_marker(ms_xyz, rgba, marker_radius, link_radius,
                                  marker_set, minimum_spacing)
    return m

  # ---------------------------------------------------------------------------
  #
  def mark_surface(self, pointer_x, pointer_y, marker_set,
                   minimum_spacing = None):

    from _surface import SurfaceModel
    from chimera import openModels as om
    surfs = om.list(modelTypes = [SurfaceModel])
    from VolumeViewer import slice
    xyz_in, xyz_out = slice.clip_plane_points(pointer_x, pointer_y)
    import PickBlobs
    f, p, tri = PickBlobs.closest_surface_intercept(surfs, xyz_in, xyz_out)
    if f is None:
      return None
    xyz = linear_combination((1.0-f), xyz_in, f, xyz_out)
    m = self.mark_point(xyz, marker_set, minimum_spacing)
    return m
    
  # ---------------------------------------------------------------------------
  #
  def mark_clip_planes_midpoint(self, pointer_x, pointer_y, marker_set = None,
                                minimum_spacing = None):

    from VolumeViewer import slice
    xyz_in, xyz_out = slice.clip_plane_points(pointer_x, pointer_y)
    xyz = linear_combination(.5, xyz_in, .5, xyz_out)
    m = self.mark_point(xyz, marker_set, minimum_spacing)
    return m
    
  # ---------------------------------------------------------------------------
  # Xyz position must be in Chimera world coordinates.
  #
  def mark_point(self, xyz, marker_set = None, minimum_spacing = None):

    if marker_set is None:
      marker_set = self.active_set()

    from Matrix import apply_inverse_matrix
    ms_xyz = apply_inverse_matrix(marker_set.transform(), xyz)

    rp = self.color_radius_panel
    rgba = rp.marker_color.rgba
    
    marker_radius, link_radius = rp.marker_and_link_radius(marker_set)
    m = self.drop_and_link_marker(ms_xyz, rgba, marker_radius, link_radius,
                                  marker_set, minimum_spacing)
    if m:
      self.message('Dropped marker outside data')
    return m

  # ---------------------------------------------------------------------------
  # Xyz position must be in marker set coordinates.
  #
  def drop_and_link_marker(self, xyz, rgba, marker_radius, link_radius,
                           marker_set, minimum_spacing = None):

    m0 = None
    link = self.link_to_selected.get()
    if minimum_spacing != None or link:
      markers = selected_markers()
      if len(markers) == 1:
        m0 = markers[0]

    if minimum_spacing != None and m0:
      if distance(xyz, m0.xyz()) < minimum_spacing:
        return None

    marker = marker_set.place_marker(xyz, rgba, marker_radius)

    if link and m0:
      self.create_link(marker, m0, radius = link_radius)

    self.select_marker(marker)
    return marker

  # ---------------------------------------------------------------------------
  #
  def create_link(self, m1, m2, rgba = None, radius = None):

    if rgba is None:
      crp = self.color_radius_panel
      rgba = crp.link_color.rgba

    if radius is None:
      crp = self.color_radius_panel
      radius = crp.link_radius()
      if radius is None:
        radius = .5 * m1.radius()

    if m1.marker_set != m2.marker_set or m1 == m2 or m1.linked_to(m2):
      return None

    import markerset
    e = markerset.Link(m1, m2, rgba, radius)
    
    for es in selected_links():
      es.deselect()
    e.select()
    return e
    
  # ---------------------------------------------------------------------------
  #
  def move_or_resize_marker(self, pointer_x, pointer_y, shift, resize):

    m = self.grabbed_marker
    if m == None:
      return None

    last_x, last_y = self.last_pointer_xy
    dx = pointer_x - last_x
    dy = -(pointer_y - last_y)

    if resize:
      dmax, dmin = max(dx,dy), min(dx,dy)
      if dmax >= -dmin: delta = dmax
      else:             delta = dmin
      if shift:
        factor_per_pixel = 1.001  # shift key held so scale by smaller amount
      else:
        factor_per_pixel = 1.01
      factor = factor_per_pixel ** delta
      m.set_radius(factor*m.radius())
      self.color_radius_panel.show_marker_radius(m.radius())
    else:
      if shift:
        if abs(dx) > abs(dy):   dz = -dx
        else:                   dz = -dy
        dx = dy = 0
      else:
        dz = 0
      xyz = m.xyz()
      xform = m.marker_set.transform()
      vx, vy, vz = screen_axes(xyz, xform)
      delta_xyz = linear_combination_3(dx, vx, dy, vy, dz, vz)
      new_xyz = map(lambda a,b: a+b, xyz, delta_xyz)
      m.set_xyz(new_xyz)

    self.last_pointer_xy = (pointer_x, pointer_y)
    return m
    
  # ---------------------------------------------------------------------------
  # Used with 3D input devices.
  #
  def move_marker_3d(self, xyz):

    m = self.grabbed_marker
    if m == None:
      return None

    from Matrix import apply_inverse_matrix
    ms_xyz = apply_inverse_matrix(m.marker_set.transform(), xyz)

    m.set_xyz(ms_xyz)
    return m
  
  # ---------------------------------------------------------------------------
  #
  def ungrab_marker(self):

    clear_message = (not self.grabbed_marker is None)
    self.grabbed_marker = None
    if clear_message:
      self.message('')
    
  # ---------------------------------------------------------------------------
  # If no markers selected return all markers of active marker set.
  #
  def chosen_markers(self):
    
    markers = selected_markers()
    if len(markers) == 0:
      markers = self.all_current_markers()

    return markers
    
  # ---------------------------------------------------------------------------
  #
  def all_current_markers(self):
      
    marker_set = self.active_marker_set
    if marker_set == None:
      markers = []
    else:
      markers = marker_set.markers()

    return markers
    
  # ---------------------------------------------------------------------------
  # Select new marker and deselect other markers.
  #
  def select_marker(self, marker):

    marker.select()
    for m in selected_markers():
      if m != marker:
	m.deselect()
    
  # ---------------------------------------------------------------------------
  #
  def unselect_all_markers(self):

    for m in selected_markers():
      m.deselect()
    
  # ---------------------------------------------------------------------------
  #
  def chosen_links(self):
    
    links = selected_links()
    if len(links) == 0:
      links = self.all_current_links()

    return links
    
  # ---------------------------------------------------------------------------
  #
  def all_current_links(self):
      
    marker_set = self.active_marker_set
    if marker_set == None:
      links = []
    else:
      links = marker_set.links()

    return links
  
  # ---------------------------------------------------------------------------
  #
  def show_chosen_markers(self, show):

    for m in self.chosen_markers():
      m.show(show)
  
  # ---------------------------------------------------------------------------
  #
  def show_chosen_links(self, show):

    for l in self.chosen_links():
      l.show(show)
    
  # ---------------------------------------------------------------------------
  #
  def show_marker_notes(self, show):

    markers = self.chosen_markers()
    for m in markers:
      m.show_note(show)
    
  # ---------------------------------------------------------------------------
  #
  def delete_marker_notes_cb(self):

    for m in selected_markers():
      m.set_note('')
  
  # ---------------------------------------------------------------------------
  # This code relies on markers being implemented as atoms.
  #
  def consecutive_selection_cb(self):

    from chimera import triggers
    if self.link_consecutive.get():
      if self.form_link_trigger == None:
        self.form_link_trigger = \
          triggers.addHandler('selection changed', self.form_link_cb, None)
        markers = selected_markers()
        if len(markers) == 1:
          self.last_selected_marker = markers[0]
    elif self.form_link_trigger:
      triggers.deleteHandler('selection changed', self.form_link_trigger)
      self.form_link_trigger = None
  
  # ---------------------------------------------------------------------------
  # Link consecutively selected markers.
  #
  def form_link_cb(self, trigger, user_data, selection):

    markers = selected_markers()
    if len(markers) == 0:
      self.last_selected_marker = None
    if len(markers) == 1:
      marker = markers[0]
      if self.last_selected_marker:
        self.create_link(marker, self.last_selected_marker)
      self.last_selected_marker = marker
    
  # ---------------------------------------------------------------------------
  #
  def delete_markers_cb(self):

    selected = selected_markers()
    s = self.slice_panel.shown_slice
    if s and hasattr(s, 'marker') and s.marker in selected:
      delattr(s, 'marker')
    if self.last_selected_marker in selected:
      self.last_selected_marker = None
    if self.grabbed_marker in selected:
      self.grabbed_marker = None
    for m in selected:
      m.delete()

  # ---------------------------------------------------------------------------
  #
  def delete_links_cb(self):

    for e in selected_links():
      e.delete()

  # ---------------------------------------------------------------------------
  # Transfer selected markers to current marker set.
  #
  def transfer_markers_cb(self):

    ams = self.active_marker_set
    if ams == None:
      return

    mlist = selected_markers()

    import markerset
    count =  markerset.transfer_markers(mlist, ams)
    if count == None:
      self.message('Markers not transfered.  Markers in one set\n'
                   'cannot link to markers in a different set')
    else:
      self.message('Transfered %d markers.' % count)

  # ---------------------------------------------------------------------------
  #
  def update_mouse_binding_cb(self):

    self.mouse_button_panel.bind_placement_button_cb()
    
  # ---------------------------------------------------------------------------
  #
  def message(self, string):

    self.message_label['text'] = string
    self.message_label.update_idletasks()

  # ---------------------------------------------------------------------------
  #
  def mouse_down_cb(self, viewer, event):

    grabbed = (self.move_markers.get() and self.grab_marker(event.x, event.y))
    if not grabbed:
      self.add_marker_at_screen_xy(event.x, event.y)
    
  # ---------------------------------------------------------------------------
  #
  def mouse_drag_cb(self, viewer, event):

    if self.move_markers.get():
      shift_mask = 1
      shift = (event.state & shift_mask)
      capslock_mask = 2
      capslock = (event.state & capslock_mask)
      if self.move_or_resize_marker(event.x, event.y, shift, capslock):
        return

    if (self.place_markers_continuously.get() and
        not self.pause_marker_placement):
      m, loop_closed = self.place_marker_continuous(event.x, event.y)
      if loop_closed:
        # Wait for mouse up to continue placing markers.
        self.pause_marker_placement = True
  
  # ---------------------------------------------------------------------------
  #
  def mouse_up_cb(self, viewer, event):

    self.ungrab_marker()
    self.pause_marker_placement = False

  # ---------------------------------------------------------------------------
  #
  def enter(self):

    self.mouse_button_panel.use_mouse.set(True)        # Turn on mouse mode.
    ModelessDialog.enter(self)

  # ---------------------------------------------------------------------------
  #
  def Close(self):

    self.slice_panel.erase_slice_line()
    self.link_consecutive.set(False)
    self.mouse_button_panel.use_mouse.set(False)        # Turn off mouse mode.
    ModelessDialog.Close(self)

      
# -----------------------------------------------------------------------------
# User interface for showing current marker set.
#
class Marker_Set_Menu_Panel(Popup_Panel):

  name = 'Marker set menu'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog
    self.menu_marker_sets = []

    Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(4, weight = 1)

    from CGLtk import Hybrid
    
    msm = Hybrid.Option_Menu(frame, 'Marker set ')
    msm.frame.grid(row = 0, column = 0, sticky = 'w')
    msm.add_callback(self.marker_set_menu_cb)
    self.marker_set_menu = msm

    b = self.make_close_button(frame)
    b.grid(row = 0, column = 4, sticky = 'e')

  # ---------------------------------------------------------------------------
  #
  def marker_set_menu_cb(self):

    name = self.marker_set_menu.variable.get()

    import markerset
    ms = markerset.find_marker_set_by_name(name)
    d = self.dialog
    d.set_active_marker_set(ms)

  # ---------------------------------------------------------------------------
  #
  def set_menu(self, name, invoke_callbacks = True):

    v = self.marker_set_menu.variable
    v.set(name, invoke_callbacks = invoke_callbacks)

  # ---------------------------------------------------------------------------
  #
  def update_menu(self, marker_sets, active_marker_set):
      
    menu = self.marker_set_menu
    menu.remove_all_entries()
    self.menu_marker_sets = list(marker_sets)
    for ms in marker_sets:
      menu.add_entry(ms.name)
      
    if active_marker_set:
      menu.variable.set(active_marker_set.name, invoke_callbacks = False)

  # ---------------------------------------------------------------------------
  #
  def rename_entry(self, mset):
    
    mmsets = self.menu_marker_sets
    if not mset in mmsets:
      return
    i = mmsets.index(mset)
    menu = self.marker_set_menu
    menu.remove_entry(i)
    menu.insert_entry(i, mset.name)
    menu.variable.set(mset.name, invoke_callbacks = False)

  # ---------------------------------------------------------------------------
  #
  def add_entry(self, mset):

    self.menu_marker_sets.append(mset)
    self.marker_set_menu.add_entry(mset.name)
      
# -----------------------------------------------------------------------------
#
class Marker_Sets_Panel(Popup_Panel):

  name = 'Marker set list'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog
    self.list_marker_sets = []

    Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(0, weight = 1)
    row = 0

    import Tkinter
    lbl = Tkinter.Label(frame, text = 'Marker Sets')
    lbl.grid(row = row, column = 0, sticky = 'nw')

    b = self.make_close_button(frame)
    b.grid(row = row, column = 1, sticky = 'ne')
    row += 1
    
    from CGLtk import Hybrid
    msl = Hybrid.Scrollable_List(frame, None, 3, self.marker_set_selection_cb)
    self.marker_set_listbox = msl.listbox
    msl.frame.grid(row = row, column = 0, columnspan = 2, sticky = 'news')
    frame.rowconfigure(row, weight = 1)
    row += 1

  # ---------------------------------------------------------------------------
  #
  def marker_set_selection_cb(self, event):

    sel = self.selected_marker_sets()
    if len(sel) == 1:
      d = self.dialog
      d.set_active_marker_set(sel[0])
      
  # ---------------------------------------------------------------------------
  #
  def selected_marker_sets(self):

    indices = map(int, self.marker_set_listbox.curselection())
    msets = [self.list_marker_sets[i] for i in indices]
    return msets
      
  # ---------------------------------------------------------------------------
  #
  def update_list(self, marker_sets):

    self.list_marker_sets = list(marker_sets)
    listbox = self.marker_set_listbox
    listbox.delete(0, 'end')
    for ms in marker_sets:
      listbox.insert('end', ms.name)
      
  # ---------------------------------------------------------------------------
  #
  def rename_entry(self, mset):
    lmsets = self.list_marker_sets
    if not mset in lmsets:
      return
    i = lmsets.index(mset)
    listbox = self.marker_set_listbox
    listbox.delete(i)
    listbox.insert(i, mset.name)
      
  # ---------------------------------------------------------------------------
  #
  def add_entry(self, mset):

    self.list_marker_sets.append(mset)
    self.marker_set_listbox.insert('end', mset.name)
      
# -----------------------------------------------------------------------------
#
class Rename_Panel(Popup_Panel):

  name = 'Rename marker set'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(1, weight = 1)

    from CGLtk import Hybrid
    
    rms = Hybrid.Entry(frame, 'Rename marker set ', 25)
    rms.frame.grid(row = 0, column = 0, sticky = 'ew')
    self.marker_set_rename = rms.variable
    rms.entry.bind('<KeyPress-Return>', self.rename_marker_set_cb)

    b = self.make_close_button(frame)
    b.grid(row = 0, column = 1, sticky = 'e')
          
  # ---------------------------------------------------------------------------
  #
  def rename_marker_set_cb(self, event):

    name = self.marker_set_rename.get()
    self.dialog.rename_active_marker_set(name)
          
  # ---------------------------------------------------------------------------
  #
  def set_rename_text(self, name):

      self.marker_set_rename.set(name)

# -----------------------------------------------------------------------------
#
class Mouse_Button_Panel(Popup_Panel):

  name = 'Mouse button menu'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog
    self.bound_button = None          # Mouse button bound for Marker placement

    Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(3, weight = 1)

    import Tkinter
    from CGLtk import Hybrid

    um = Hybrid.Checkbutton(frame, 'Use', False)
    um.button.grid(row = 0, column = 0, sticky = 'w')
    self.use_mouse = um.variable
    um.callback(self.bind_placement_button_cb)

    mb = Hybrid.Option_Menu(frame, '',
                            'button 1', 'button 2', 'button 3',
                            'ctrl button 1', 'ctrl button 2', 'ctrl button 3')
    mb.variable.set('button 2')
    mb.frame.grid(row = 0, column = 1, sticky = 'w')
    mb.add_callback(self.bind_placement_button_cb)
    self.placement_button = mb

    mbl = Tkinter.Label(frame, text = ' to place/move markers')
    mbl.grid(row = 0, column = 2, sticky = 'w')

    b = self.make_close_button(frame)
    b.grid(row = 0, column = 3, sticky = 'e')

    self.bind_placement_button_cb()
    
  # ---------------------------------------------------------------------------
  #
  def bind_placement_button_cb(self):

    d = self.dialog
    bind = (self.use_mouse.get() and
            (d.place_markers_on_spots.get() or
             d.place_markers_on_planes.get() or
             d.place_markers_on_surfaces.get() or
             d.place_markers_outside_data.get() or
             d.move_markers.get()))
    self.bind_placement_button(bind)
    
  # ---------------------------------------------------------------------------
  #
  def bind_placement_button(self, bind):

    if bind:
      button, modifiers = self.placement_button_spec()
      if self.bound_button != (button, modifiers):
        self.bind_placement_button(0)
        from chimera import mousemodes
        mousemodes.setButtonFunction(button, modifiers, 'mark volume')
        self.bound_button = (button, modifiers)
    elif self.bound_button:
      button, modifiers = self.bound_button
      from chimera import mousemodes
      def_mode = mousemodes.getDefault(button, modifiers)
      mousemodes.setButtonFunction(button, modifiers, def_mode)
      self.bound_button = None

  # ---------------------------------------------------------------------------
  #
  def placement_button_spec(self):

    name = self.placement_button.variable.get()
    name_to_bspec = {'button 1':('1', []), 'ctrl button 1':('1', ['Ctrl']),
                     'button 2':('2', []), 'ctrl button 2':('2', ['Ctrl']),
                     'button 3':('3', []), 'ctrl button 3':('3', ['Ctrl'])}
    bspec = name_to_bspec[name]
    return bspec
      
# -----------------------------------------------------------------------------
#
class Color_Radius_Panel(Popup_Panel):

  name = 'Marker color and radius'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog
    self.show_color_and_radius_handler = None # Update marker color and radius

    Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(3, weight = 1)

    import Tkinter
    from CGLtk import Hybrid

    sm = Tkinter.Label(frame, text = 'Marker color ')
    sm.grid(row = 0, column = 0, sticky = 'w')
    
    from CGLtk.color import ColorWell
    mc = ColorWell.ColorWell(frame, callback = self.marker_color_cb)
    self.marker_color = mc
    mc.showColor((1,1,1), doCallback = 0)
    mc.grid(row = 0, column = 1, sticky = 'w')

    mr = Hybrid.Entry(frame, '  and radius ', 5)
    mr.frame.grid(row = 0, column = 2, sticky = 'w')
    mr.entry.bind('<KeyPress-Return>', self.marker_radius_cb)
    self.marker_radius_entry = mr.variable

    sl = Tkinter.Label(frame, text = ' Link color ')
    sl.grid(row = 1, column = 0, sticky = 'e')

    lc = ColorWell.ColorWell(frame, callback = self.link_color_cb)
    self.link_color = lc
    lc.showColor((1,1,1), doCallback = 0)
    lc.grid(row = 1, column = 1, sticky = 'w')

    lr = Hybrid.Entry(frame, '  and radius ', 5)
    lr.frame.grid(row = 1, column = 2, sticky = 'w')
    lr.entry.bind('<KeyPress-Return>', self.link_radius_cb)
    self.link_radius_entry = lr.variable

    b = self.make_close_button(frame)
    b.grid(row = 0, column = 3, sticky = 'e')
  
  # ---------------------------------------------------------------------------
  #
  def marker_radius_cb(self, event):

    radius = self.marker_radius()
    if radius == None:
      return
    
    for m in selected_markers():
      m.set_radius(radius)
      
  # ---------------------------------------------------------------------------
  #
  def marker_radius(self, data_region = None, marker_set = None):
    
    rstring = self.marker_radius_entry.get()
    try:
      radius = float(rstring)
      if radius <= 0:
        radius = None
    except ValueError:
      radius = None

    if radius == None and data_region:
      radius = data_plane_spacing(data_region)

    if radius == None and marker_set:
      mlist = marker_set.markers()
      if len(mlist) > 0:
	radius = mlist[0].radius()
      else:
	radius = .01 * clip_plane_spacing()

    return radius
          
  # ---------------------------------------------------------------------------
  #
  def marker_color_cb(self, rgba):

    for m in selected_markers():
      m.set_rgba(self.marker_color.rgba)
  
  # ---------------------------------------------------------------------------
  #
  def link_radius_cb(self, event):

    radius = self.link_radius()
    if radius == None:
      return
    
    for e in selected_links():
      e.set_radius(radius)
      
  # ---------------------------------------------------------------------------
  #
  def link_radius(self, data_region = None):
    
    rstring = self.link_radius_entry.get()
    try:
      radius = float(rstring)
      if radius < 0:
        radius = None
    except ValueError:
      radius = None

    if radius == None and data_region:
      radius = .5 * data_plane_spacing(data_region)

    return radius
          
  # ---------------------------------------------------------------------------
  #
  def link_color_cb(self, rgba):

    for e in selected_links():
      e.set_rgba(self.link_color.rgba)
      
  # ---------------------------------------------------------------------------
  #
  def marker_and_link_radius(self, marker_set, data_region = None):

    if data_region:
      marker_radius = self.marker_radius(data_region)
      link_radius = self.link_radius(data_region)
    else:
      marker_radius = self.marker_radius(marker_set = marker_set)
      link_radius = self.link_radius()
      if link_radius == None:
        link_radius = .5 * marker_radius

    return marker_radius, link_radius

  # -------------------------------------------------------------------------
  #
  def register_for_selection_updates(self, register):

    if register and self.show_color_and_radius_handler == None:
      ct = chimera.triggers
      self.show_color_and_radius_handler = \
        ct.addHandler('selection changed', self.show_color_and_radius_cb, None)

    if not register and self.show_color_and_radius_handler:
      ct = chimera.triggers
      ct.deleteHandler('selection changed', self.show_color_and_radius_handler)
      self.show_color_and_radius_handler = None
      
  # -------------------------------------------------------------------------
  # Update colorwell color when a single model piece is selected.
  #
  def show_color_and_radius_cb(self, trigger, user_data, selection):

    d = self.dialog
    markers = selected_markers()
    if len(markers) == 1:
      m = markers[0]
      self.marker_color.showColor(m.rgba(), doCallback = False)
      self.show_marker_radius(m.radius())

    links = selected_links()
    if len(links) == 1:
      l = links[0]
      self.link_color.showColor(l.rgba(), doCallback = False)
      self.link_radius_entry.set('%g' % l.radius(), invoke_callbacks = False)

  # -------------------------------------------------------------------------
  #
  def show_marker_radius(self, radius, invoke_callbacks = False):
    self.marker_radius_entry.set('%g' % radius)

# -----------------------------------------------------------------------------
#
class Note_Panel(Popup_Panel):

  name = 'Marker notes'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog
    self.show_note_handler = None

    Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(2, weight = 1)

    from CGLtk import Hybrid
    
    mn = Hybrid.Entry(frame, 'Marker note: ', 10)
    mn.frame.grid(row = 0, column = 0, sticky = 'ew')
    mn.entry.bind('<KeyPress-Return>', self.marker_note_cb)
    self.marker_note = mn.variable

    from CGLtk.color import ColorWell
    nc = ColorWell.ColorWell(frame, callback = self.note_color_cb)
    self.note_color = nc
    nc.showColor((1,1,1), doCallback = 0)
    nc.grid(row = 0, column = 1, sticky = 'w')

    b = self.make_close_button(frame)
    b.grid(row = 0, column = 2, sticky = 'e')

  # ---------------------------------------------------------------------------
  #
  def marker_note_cb(self, event):

    note_text = self.marker_note.get()
    for m in selected_markers():
      m.set_note(note_text)
      m.show_note(1)
          
  # ---------------------------------------------------------------------------
  #
  def note_color_cb(self, rgba):

    for m in self.dialog.chosen_markers():
      m.set_note_rgba(self.note_color.rgba)

  # -------------------------------------------------------------------------
  #
  def register_for_selection_updates(self, register):

    if register and self.show_note_handler == None:
      ct = chimera.triggers
      self.show_note_handler = \
        ct.addHandler('selection changed', self.show_note_cb, None)

    if not register and self.show_note_handler:
      ct = chimera.triggers
      ct.deleteHandler('selection changed', self.show_note_handler)
      self.show_note_handler = None
          
  # -------------------------------------------------------------------------
  # Update marker note entry field when marker is selected.
  #
  def show_note_cb(self, trigger, user_data, selection):

    markers = selected_markers()
    if len(markers) == 1:
      m = markers[0]
      note = m.note()
      note_rgba = m.note_rgba()
    else:
      note = ''
      note_rgba = (1,1,1,1)
    self.marker_note.set(note)
    self.note_color.showColor(note_rgba, doCallback = 0)
      
# -----------------------------------------------------------------------------
#
class Spline_Panel(Popup_Panel):

  name = 'Smooth paths'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(1, weight = 1)

    import Tkinter
    from CGLtk import Hybrid

    row = 0

    br = Hybrid.Button_Row(frame, 'Curve: ',
                           (('Show', self.show_curve_cb),
                            ('Unshow', self.unshow_curve_cb)))
    br.frame.grid(row = row, column = 0, sticky = 'w')

    b = self.make_close_button(frame)
    b.grid(row = row, column = 1, sticky = 'e')
    row = row + 1

    cr = Hybrid.Entry(frame, 'Curve radius: ', 5, '0')
    cr.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.curve_radius = cr.variable
    cr.entry.bind('<KeyPress-Return>', self.show_curve_cb)

    bl = Hybrid.Entry(frame, 'Band length: ', 5, '0')
    bl.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1    
    self.curve_band_length = bl.variable
    bl.entry.bind('<KeyPress-Return>', self.show_curve_cb)

    sd = Hybrid.Entry(frame, 'Segment subdivisions: ', 5, '10')
    sd.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.curve_segment_subdivisions = sd.variable
    sd.entry.bind('<KeyPress-Return>', self.show_curve_cb)
    
  # ---------------------------------------------------------------------------
  #
  def show_curve_cb(self, event = None):

    ams = self.dialog.active_marker_set
    if ams == None:
      return

    self.unshow_curve_cb()

    from CGLtk.Hybrid import float_variable_value, integer_variable_value
    radius = float_variable_value(self.curve_radius, 0)
    band_length = float_variable_value(self.curve_band_length, 0)
    subdivisions = integer_variable_value(self.curve_segment_subdivisions, 0)

    ams.show_curve(radius, band_length, subdivisions)

  # ---------------------------------------------------------------------------
  #
  def unshow_curve_cb(self):

    ams = self.dialog.active_marker_set
    if ams:
      ams.unshow_curve()
      
# -----------------------------------------------------------------------------
#
class Slice_Panel(Popup_Panel):

  name = 'Slice display'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog
    self.shown_slice = None             # For interactive marker z movement
    self.max_line_id = None             # Canvas id for slice graph depth line
    self.slice_line_model = None        # VRML model showing slice position

    Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(1, weight = 1)

    import Tkinter
    from CGLtk import Hybrid

    row = 0
    
    c = Tkinter.Canvas(frame, height = 100)
    frame.rowconfigure(row, weight = 1)
    c.grid(row = row, column = 0, sticky = 'news')
    row = row + 1
    self.canvas = c

    sc = Hybrid.Checkbutton(frame, 'Slice graph color matches volume color', 0)
    sc.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.use_volume_colors = sc.variable

    trf = Tkinter.Frame(frame)
    trf.grid(row = row, column = 0, sticky = 'nw')
    row = row + 1
    
    trb = Tkinter.Button(trf, text = 'Reset',
			 command = self.reset_thresholds_cb)
    trb.grid(row = 0, column = 0, sticky = 'w')

    trl = Tkinter.Label(trf, text = ' thresholds to displayed levels')
    trl.grid(row = 0, column = 1, sticky = 'w')

    slf = Tkinter.Frame(frame)
    slf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    
    ss = Hybrid.Checkbutton(slf, 'Show slice line using color ', 0)
    ss.button.grid(row = 0, column = 0, sticky = 'w')
    ss.callback(self.show_slice_line_cb)
    self.show_slice_line = ss.variable

    from CGLtk.color import ColorWell
    sc = ColorWell.ColorWell(slf)
    self.slice_color = sc
    sc.showColor((1,1,1))
    sc.grid(row = 0, column = 1, sticky = 'w')

    b = self.make_close_button(frame)
    b.grid(row = 0, column = 1, sticky = 'ne')
  
  # ---------------------------------------------------------------------------
  #
  def show_slice_line_cb(self):

    if not self.show_slice_line.get():
      self.erase_slice_line()
  
  # ---------------------------------------------------------------------------
  # Make a VRML line containing a single line connecting 2 points.
  #
  def display_slice_line(self, slice):

    if self.show_slice_line.get():
      mlist = slice.data_region.models()
      if len(mlist) == 0:
        return
      model = mlist[0]
      vrml = line_vrml(slice.xyz_in, slice.xyz_out, self.slice_color.rgba)
      lm = chimera.openModels.open(vrml, 'VRML', sameAs = model)[0]
      self.slice_line_model = lm
  
  # ---------------------------------------------------------------------------
  #
  def erase_slice_line(self):

    if self.slice_line_model:
      close_model(self.slice_line_model)
      self.slice_line_model = None

  # ---------------------------------------------------------------------------
  #
  def reset_thresholds_cb(self):

    s = self.shown_slice
    if s:
      s.reset_thresholds()

  # ---------------------------------------------------------------------------
  #
  def update_slice_graphs(self, slice):
    
    c = self.canvas
    c.delete('all')
    slice.show_slice_graphs(c, self.use_volume_colors.get())
    self.shown_slice = slice

  # ---------------------------------------------------------------------------
  # Put vertical line on graph to indicate first maximum.
  #
  def show_slice_maximum(self, t_max):
          
    c = self.canvas
    w = c.winfo_width()
    x = int(t_max*w)
    h = c.winfo_height()
    self.max_line_id = c.create_line(x, 0, x, h)
    c.tag_bind(self.max_line_id, "<Button1-Motion>", self.move_marker_cb,
               add = 1)
    
  # ---------------------------------------------------------------------------
  #
  def move_marker_cb(self, event):

    x = event.x
    c = self.canvas

    h = c.winfo_height()
    c.coords(self.max_line_id, x, 0, x, h)

    slice = self.shown_slice
    if slice:
      if hasattr(slice, 'marker'):
        t = float(x) / slice.graph_width
        xyz = linear_combination(1-t, slice.xyz_in, t, slice.xyz_out)
        slice.marker.set_xyz(xyz)
      
# -----------------------------------------------------------------------------
#
class Mouse_Mode_Panel(Popup_Panel):

  name = 'Mouse mode options'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.dialog = dialog

    Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(1, weight = 1)

    from CGLtk import Hybrid

    row = 0

    b = self.make_close_button(frame)
    b.grid(row = row, column = 1, sticky = 'e')

    d = dialog
    for text, var in d.mouse_mode_vars:
      onoff = var.get()
      b = Hybrid.Checkbutton(frame, text, onoff)
      b.button.grid(row = row, column = 0, sticky = 'w')
      b.button['variable'] = var.tk_variable
      b.variable = var
      row += 1
      if text.find('dragging') >= 0:
        drow = row
        row += 1

    sp = Hybrid.Entry(frame, 'Dragging marker spacing (voxels/pixels) ',
                      3, '10')
    sp.frame.grid(row = drow, column = 0, sticky = 'w')
    self.marker_spacing = sp.variable
      
# -----------------------------------------------------------------------------
#
class Surface_Panel(Popup_Panel):

  name = 'Surfaces'           # Used in feature menu.
  
  def __init__(self, dialog, parent):

    self.surface_model = None

    self.dialog = dialog

    Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(1, weight = 1)

    import Tkinter
    from CGLtk import Hybrid

    row = 0

    b = self.make_close_button(frame)
    b.grid(row = row, column = 1, sticky = 'ne')

    cs = Hybrid.Checkbutton(frame, 'Cap surface end loops', False)
    cs.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.cap_ends = cs.variable

    br = Hybrid.Button_Row(frame, 'Surface: ',
                           (('Create', self.make_surface_cb),
                            ('Delete', self.delete_surface_cb)))
    br.frame.grid(row = row, column = 0, sticky = 'w')
    row += 1
      
  # ---------------------------------------------------------------------------
  #
  def make_surface_cb(self):

    d = self.dialog
    mlist = d.chosen_markers()
    if len(mlist) == 0:
      return

    sm = self.surface_model
    if sm is None or sm.__destroyed__:
      from _surface import SurfaceModel
      sm = SurfaceModel()
      self.surface_model = sm
      sm.name = 'Traced surfaces'
      from chimera import openModels, addModelClosedCallback
      openModels.add([sm])
      addModelClosedCallback(sm, self.surface_closed_cb)
      sm.openState.xform = mlist[0].model().openState.xform

    caps = self.cap_ends.get()

    from surface import make_marker_surface, No_Surface
    try:
      g = make_marker_surface(mlist, sm, caps)
    except No_Surface, (reason, mlist):
      d.message('No surface, ' + reason)
      from VolumePath import select_markers
      select_markers(mlist)
      return

    if g:
      g.traced = True   # Mark for session saving.
      d.message('Created surface using %d markers' % len(mlist))
    else:
      d.message('No surface')
      
  # ---------------------------------------------------------------------------
  #
  def delete_surface_cb(self):

    from Surface import selected_surface_pieces, delete_surfaces
    plist = selected_surface_pieces()
    tplist = [p for p in plist if p.model == self.surface_model]
    delete_surfaces(tplist)
      
  # ---------------------------------------------------------------------------
  #
  def surface_closed_cb(self, model):

    self.surface_model = None

# -----------------------------------------------------------------------------
# Graph the data values along a line passing through a volume on a Tkinter
# canvas.  The volume data may have multiple components.  Each component is
# graphed using a Trace object.
#
class Slice:

  def __init__(self, data_region, xyz_in, xyz_out):

    self.data_region = data_region
    self.xyz_in = xyz_in
    self.xyz_out = xyz_out

    self.canvas = None
    self.graph_width = None
    self.traces = []

  # ---------------------------------------------------------------------------
  #
  def show_slice_graphs(self, canvas, use_volume_colors):

    c = canvas
    self.canvas = c
    self.graph_width = c.winfo_width()

    vdlist = visible_data_components(self.data_region)

    n = len(vdlist)
    h = c.winfo_height()
    ystep = h / n
    if n > 1:
      ypad = ystep / 4
    else:
      ypad = 3                                                     # pixels
    ymin = ypad
    ymax = max(ypad, ystep - ypad)

    traces = []
    for visdata in vdlist:
      t = Trace(visdata, self.xyz_in, self.xyz_out, c, ymin, ymax,
		use_volume_colors)
      traces.append(t)
      ymin = ymin + ystep
      ymax = ymax + ystep
    self.traces = traces

  # ---------------------------------------------------------------------------
  #
  def reset_thresholds(self):

    d = self.data_region.data
    if hasattr(d, 'volume_path_threshold'):
      delattr(d, 'volume_path_threshold')
    self.redraw_threshold_lines()

  # ---------------------------------------------------------------------------
  #
  def redraw_threshold_lines(self):

    for t in self.traces:
      t.redraw_threshold_line()

  # ---------------------------------------------------------------------------
  #
  def first_maximum_above_threshold(self):

    t_max = None
    v_max = None
    trace_max = None
    for trace in self.traces:
      t, v = trace.first_maximum_above_threshold()
      if t != None and (t_max == None or t < t_max):
        t_max = t
	v_max = v
        trace_max = trace
    return t_max, v_max, trace_max

# -----------------------------------------------------------------------------
#
class Visible_Data:

  def __init__(self, data_region):

    self.data_region = data_region

  # ---------------------------------------------------------------------------
  #
  def interpolated_value(self, xyz):

    vertex_xform = None
    dr = self.data_region
    values = dr.interpolated_values([xyz], vertex_xform, subregion = None)
    v = values[0]
    return v
  
  # ---------------------------------------------------------------------------
  #
  def threshold(self):

    data = self.data_region.data
    if hasattr(data, 'volume_path_threshold'):
      return data.volume_path_threshold

    threshold = None
    dr = self.data_region
    rep = dr.representation
    if rep in ('surface', 'mesh'):
      if dr.surface_levels:
        threshold = min(dr.surface_levels)
    elif rep == 'solid':
      levels = filter(lambda sl: sl[1] > 0, dr.solid_levels)
      if levels:
        threshold = min(levels)[0]

    return threshold

  # ---------------------------------------------------------------------------
  #
  def set_threshold(self, threshold):

    self.data_region.data.volume_path_threshold = threshold

  # ---------------------------------------------------------------------------
  #
  def using_displayed_threshold(self):

    return not hasattr(self.data_region.data, 'volume_path_threshold')

  # ---------------------------------------------------------------------------
  # Find the closest displayed data color for the given data value.
  # If no data value is given, use the color for the lowest threshold.
  # Otherwise use the color of the first surface level below the data value
  # if surfaces are shown.  If not level is below the data level use the
  # color of the lowest surface.  For the interpolated solid use the
  # interpolated color for the data component, or if the data value
  # is outside the threshold range, use the closest endpoint color.
  #
  def volume_rgba(self, data_value = None):

    data_region = self.data_region

    if data_region.surface_levels:
      tclist = map(lambda t,c: (t,c),
		   data_region.surface_levels, data_region.surface_colors)
      tclist.sort()
      if data_value != None:
	tclower = filter(lambda tc, v=data_value: tc[0] <= v , tclist)
	if tclower:
	  rgba = tclower[-1][1]
	else:
	  rgba = tclist[-1][1]
      else:
	rgba = tclist[0][1]
    elif data_region.solid and data_region.solid_levels:
      tclist = map(lambda tf,c: (tf[0],c),
		   data_region.solid_levels, data_region.solid_colors)
      tclist.sort()
      if data_value != None:
	if data_value <= tclist[0][0]:
	  rgba = tclist[0][1]
	elif data_value >= tclist[-1][0]:
	  rgba = tclist[-1][1]
	else:
	  k = 1
	  while tclist[k][0] <= data_value: 
	    k = k + 1
	  d0, rgba0 = tclist[k-1]
	  d1, rgba1 = tclist[k]
	  f = (data_value - d0) / (d1 - d0)
	  rgba = map(lambda c0, c1, f=f: (1-f)*c0 + f*c1, rgba0, rgba1)
      else:
	rgba = tclist[-1][1]
    else:
      rgba = (0,0,0,0)

    return rgba

# -----------------------------------------------------------------------------
# Graph the data values along a line passing through a volume data set.
#
class Trace:

  def __init__(self, visible_data, xyz_in, xyz_out,
               canvas, ymin, ymax, use_volume_color):

    self.visible_data = visible_data

    self.canvas = canvas
    self.canvas_y_range = (ymin, ymax)
    
    dr = visible_data.data_region
    self.trace = slice_data_values(dr, xyz_in, xyz_out)

    threshold = visible_data.threshold()

    self.value_range = self.calculate_value_range(threshold)
    self.plot_scale = self.calculate_plot_scale()

    self.use_volume_color = use_volume_color

    color = self.volume_color()
    xy_values = self.trace_values_to_canvas_xy(self.trace)
    canvas.create_line(xy_values, fill = color)

    if threshold != None:
      self.threshold_line_id = self.plot_threshold_line(threshold, color)
    else:
      self.threshold_line_id = None

  # ---------------------------------------------------------------------------
  #
  def calculate_value_range(self, threshold):
    
    values = map(lambda tv: tv[1], self.trace)
    min_value = min(values)
    max_value = max(values)

    if threshold != None:
      min_value = min(min_value, threshold)
      max_value = max(max_value, threshold)
    value_range = max_value - min_value

    return (min_value, max_value)

  # ---------------------------------------------------------------------------
  #
  def calculate_plot_scale(self):

    w = self.canvas.winfo_width()
    x_scale = w
    vrange = self.value_range[1] - self.value_range[0]
    if vrange == 0:
      y_scale = 1
    else:
      ymin, ymax = self.canvas_y_range
      y_scale = max(1, ymax - ymin) / float(vrange)

    return (x_scale, y_scale)

  # ---------------------------------------------------------------------------
  #
  def trace_values_to_canvas_xy(self, tvlist):

    x_scale, y_scale = self.plot_scale
    y0 = self.canvas_y_range[1]
    v0 = self.value_range[0]
    return map(lambda tv, xs=x_scale, y0=y0, ys=y_scale, v0=v0:
               (xs * tv[0], y0 - ys * (tv[1] - v0)),
               tvlist)

  # ---------------------------------------------------------------------------
  #
  def volume_color(self):

    if not self.use_volume_color:
      return 'black'
    
    color_256 = lambda c: min(255, max(0, int(256*c)))
    rgb_256 = map(color_256, self.visible_data.volume_rgba()[:3])
    color = '#%02x%02x%02x' % tuple(rgb_256)
    return color

  # ---------------------------------------------------------------------------
  #
  def plot_threshold_line(self, threshold, color):

    thresh_xy = self.trace_values_to_canvas_xy(((0,threshold),(1,threshold)))
    if self.visible_data.using_displayed_threshold():
      dash_pattern = '.'
    else:
      dash_pattern = '-'
    c = self.canvas
    id = c.create_line(thresh_xy, fill = color, dash = dash_pattern)
    c.tag_bind(id, "<Button1-Motion>", self.move_line_cb, add = 1)
    return id

  # ---------------------------------------------------------------------------
  #
  def redraw_threshold_line(self):

    color = self.volume_color()
    threshold = self.visible_data.threshold()
    if threshold != None:
      if self.threshold_line_id != None:
        self.canvas.delete(self.threshold_line_id)
      self.threshold_line_id = self.plot_threshold_line(threshold, color)

  # ---------------------------------------------------------------------------
  #
  def move_line_cb(self, event):

    line_id = self.threshold_line_id
    ymin, ymax = self.canvas_y_range
    min_value, max_value = self.value_range
    
    y = event.y
    c = self.canvas
    w = c.winfo_width()
    c.coords(line_id, 0, y, w, y)
    
    if ymax > ymin:
      f = float(y - ymin) / (ymax - ymin)
      threshold = (1-f) * max_value + f * min_value
      self.visible_data.set_threshold(threshold)
      c.itemconfigure(line_id, dash = '-')

  # ---------------------------------------------------------------------------
  #
  def first_maximum_above_threshold(self):

    thresh = self.visible_data.threshold()
    trace = self.trace
    n = len(trace)
    for k in range(n):
      t, v = trace[k]
      if v >= thresh:
        if ((k-1 < 0 or trace[k-1][1] < v) and
            (k+1 >= n or trace[k+1][1] <= v)):
          return t, v
    return None, None

# -----------------------------------------------------------------------------
#
def visible_data_components(data_region):

  if not data_region.shown():
    return []
  return [Visible_Data(data_region)]

# -----------------------------------------------------------------------------
#
def slice_data_values(data_region, xyz_in, xyz_out):

  d = distance(xyz_in, xyz_out)
  #
  # Sample step of 1/2 voxel size can easily miss single bright voxels.
  # A possible fix is to compute the extrema in each voxel the slice line
  # passes through.  Use these points instead of a uniform spaced sampling.
  #
  sample_step = .5 * data_plane_spacing(data_region)
  t_step = sample_step / d
  steps = 1 + max(1, int(1.0/t_step))

  fsteps = float(steps)
  t_list = map(lambda k: k/fsteps, range(steps))
  xyz_list = map(lambda t: linear_combination(1-t, xyz_in, t, xyz_out), t_list)
  vertex_xform = None
  values = data_region.interpolated_values(xyz_list, vertex_xform,
                                           subregion = None)
  trace = zip(t_list, values)

  return trace

# -----------------------------------------------------------------------------
#
def clip_plane_spacing():

  c = chimera.viewer.camera
  view = 0
  left, right, bottom, top, znear, zfar, f = c.window(view)
  return zfar - znear

# -----------------------------------------------------------------------------
#
def data_plane_spacing(data_region):

  # TODO: This does not correctly compute the data plane spacing
  #       for skewed volume data.
  ijk_min, ijk_max, ijk_step = data_region.region
  data = data_region.data
  xyz_step = map(lambda a, b: a * b, data.step, ijk_step)
  spacing = min(xyz_step)
  return spacing

# -----------------------------------------------------------------------------
# Check if model already deleted before trying to close.
#
def close_model(m):

  if not m.__destroyed__:
    chimera.openModels.close([m])

# -----------------------------------------------------------------------------
# Return VRML for a line connecting two points.
#
def line_vrml(xyz_1, xyz_2, rgba):

  vrml_template = (
'''#VRML V2.0 utf8

Transform {
  children Shape {
    appearance Appearance {
      material Material {
        emissiveColor %s
        transparency %s
      }
    }
    geometry IndexedLineSet {
      coord Coordinate {
	point [ %s ]
      }
      coordIndex [ 0 1 ]
    }
  }
}
'''
  )

  rgb = '%.3g %.3g %.3g' % rgba[:3]
  transparency = '%.3g' % (1-rgba[3])
  pformat = '%.5g %.5g %.5g'
  p1 = pformat % xyz_1
  p2 = pformat % xyz_2
  points = '%s, %s' % (p1, p2)
  vrml = vrml_template % (rgb, transparency, points)

  return vrml

# -----------------------------------------------------------------------------
# Return vx, vy, and vz screen vectors in object coordinates.
# The vx vector is scaled so that one screen pixel displacement in x is
# equivalent to an object coordinate displacement vx at the given xyz
# position.  The vy vector is scaled likewise.  The vz vector length
# is set to equal the vy vector length.
#
def screen_axes(xyz, object_xform):

  c = chimera.viewer.camera
  view = 0
  llx, lly, width, height = c.viewport(view)
  left, right, bottom, top, znear, zfar, f = c.window(view)

  if c.ortho:
    zratio = 1
  else:
    xyz_eye = apply_xform(object_xform, xyz)
    zeye = xyz_eye[2]
    eye_z = c.eyePos(view)[2]
    zratio = (eye_z - zeye) / znear
  
  xs = zratio * float(right - left) / width
  ys = zratio * float(top - bottom) / height
  zs = ys
  
  from Matrix import apply_inverse_matrix
  ex, ey, ez = (xs,0,0), (0,ys,0), (0,0,zs)
  v0 = apply_inverse_matrix(object_xform, (0,0,0))
  vx, vy, vz = apply_inverse_matrix(object_xform, ex, ey, ez)
  vx = map(lambda a,b: a-b, vx, v0)
  vy = map(lambda a,b: a-b, vy, v0)
  vz = map(lambda a,b: a-b, vz, v0)
  
  return vx, vy, vz

# -----------------------------------------------------------------------------
#
def pixel_size_at_midplane():

  w,h = chimera.viewer.windowSize
  from VolumeViewer.slice import clip_plane_points
  p1, p2 = clip_plane_points((w/2)-0.5,h/2)
  cm = linear_combination(0.5, p1, 0.5, p2)
  p1, p2 = clip_plane_points((w/2)+0.5,h/2)
  cp = linear_combination(0.5, p1, 0.5, p2)
  d = distance(cm, cp)
  return d

# -----------------------------------------------------------------------------
# Prevent camera adjustment when first model gets bounding box.
#
def prevent_camera_adjustment(marker_set):

  marker_set.marker_model()     # Make sure model is created.
  from chimera import viewer as v
  v.viewSize = v.viewSize       # Indicate that camera has been initialized.

# -----------------------------------------------------------------------------
#
def transform_coordinates(from_xyz, from_transform, to_transform):

  xyz = apply_xform(from_transform, from_xyz)
  from Matrix import apply_inverse_matrix
  to_xyz = apply_inverse_matrix(to_transform, xyz)
  return to_xyz

# -----------------------------------------------------------------------------
#
def apply_xform(xform, xyz):

  c_xyz = apply(chimera.Point, xyz)
  xform_c_xyz = xform.apply(c_xyz)
  xform_xyz = (xform_c_xyz.x, xform_c_xyz.y, xform_c_xyz.z)
  return xform_xyz

# -----------------------------------------------------------------------------
# Return vector a*u + b*v where a, b are scalars.
#
def linear_combination(a, u, b, v):

  return tuple(map(lambda uc, vc, a=a, b=b: a*uc + b*vc, u, v))
  
# -----------------------------------------------------------------------------
# Return vector a*u + b*v + c*w where a, b, c are scalars.
#
def linear_combination_3(a, u, b, v, c, w):

  return tuple(map(lambda uk, vk, wk, a=a, b=b, c=c: a*uk + b*vk + c*wk,
                   u, v, w))

# -----------------------------------------------------------------------------
#
def distance(u, v):

  sum2 = 0
  for a in range(len(u)):
    d = u[a] - v[a]
    sum2 = sum2 + d * d

  from math import sqrt
  return sqrt(sum2)

# -----------------------------------------------------------------------------
#
def place_marker(xyz):

   d = volume_path_dialog(create = True)
   m = d.add_marker_3d(xyz)
   return m

# -----------------------------------------------------------------------------
#
def place_marker_at_mouse():

  d = volume_path_dialog(create = True)
  from chimera import tkgui
  w = tkgui.app.graphics
  x = w.winfo_pointerx() - w.winfo_rootx()
  y = w.winfo_pointery() - w.winfo_rooty()
  d.add_marker_at_screen_xy(x, y)

# -----------------------------------------------------------------------------
#
def place_markers_on_atoms():

   from chimera import selection
   atoms = selection.currentAtoms(ordered = True)
   for a in atoms:
     place_marker(a.xformCoord().data())
     
# -----------------------------------------------------------------------------
#
def volume_path_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Volume_Path_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_volume_path_dialog():

  from chimera import dialogs
  return dialogs.display(Volume_Path_Dialog.name)
    
# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Volume_Path_Dialog.name, Volume_Path_Dialog, replace = 1)
