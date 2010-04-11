# -----------------------------------------------------------------------------
# Save and restore volume path tracer state.
#
  
# -----------------------------------------------------------------------------
#
def save_path_tracer_state(path_tracer_dialog, file):

  if path_tracer_dialog:
    ds = Path_Tracer_Dialog_State()
    ds.state_from_dialog(path_tracer_dialog)
  else:
    ds = None
  mss = marker_set_states()
  s = (mss, ds)
  
  from SessionUtil import objecttree
  t = objecttree.instance_tree_to_basic_tree(s)

  file.write('\n')
  file.write('def restore_volume_path_tracer():\n')
  file.write(' path_tracer_state = \\\n')
  objecttree.write_basic_tree(t, file, indent = '  ')
  file.write('\n')
  file.write(' import VolumePath.session\n')
  file.write(' VolumePath.session.restore_path_tracer_state(path_tracer_state)\n')
  file.write('\n')
  file.write('try:\n')
  file.write('  restore_volume_path_tracer()\n')
  file.write('except:\n')
  file.write("  reportRestoreError('Error restoring volume path tracer')\n")
  file.write('\n')
  
# -----------------------------------------------------------------------------
#
def restore_path_tracer_state(path_tracer_dialog_basic_state):

  from SessionUtil.stateclasses import Model_State, Xform_State
  from Surface.session import Surface_Model_State, Surface_Piece_State

  classes = (
    Path_Tracer_Dialog_State,
    Marker_Set_State,
    Marker_State,
    Link_State,
    Surface_Model_State,
    Surface_Piece_State,
    Model_State,
    Xform_State,
    )
  name_to_class = {}
  for c in classes:
    name_to_class[c.__name__] = c

  from SessionUtil import objecttree
  s = objecttree.basic_tree_to_instance_tree(path_tracer_dialog_basic_state,
                                             name_to_class)

  if isinstance(s, tuple):
    marker_set_states, dialog_state = s
    msets = [mss.create_object() for mss in marker_set_states]
  else:
    dialog_state = s
    
  if dialog_state:
    from VolumePath.gui import volume_path_dialog
    d = volume_path_dialog(create = True)
    dialog_state.restore_state(d)

# -----------------------------------------------------------------------------
#
class Path_Tracer_Dialog_State:

  version = 4
  
  state_attributes = ('is_visible',
                      'geometry',
                      'shown_panels',
                      'marker_color',
                      'marker_radius',
                      'marker_note',
                      'note_color',
                      'link_color',
                      'link_radius',
                      'curve_radius',
                      'curve_band_length',
                      'curve_segment_subdivisions',
                      'use_mouse',
                      'placement_button',
                      'place_markers_on_spots',
                      'place_markers_on_planes',
                      'place_markers_on_surfaces',
                      'place_markers_outside_data',
                      'place_markers_continuously',
                      'move_markers',
                      'marker_matches_volume_color',
                      'link_to_selected',
                      'link_consecutive',
                      'use_volume_colors',
                      'show_slice_line',
                      'slice_color',
                      'cap_surface_ends',
                      'surface_model_state',
                      'active_marker_set_name',
		      'version',
                      )
  
  # ---------------------------------------------------------------------------
  #
  def state_from_dialog(self, path_tracer_dialog):

    d = path_tracer_dialog

    self.is_visible = d.isVisible()
    self.geometry = d.toplevel_widget.wm_geometry()
    self.shown_panels = map(lambda p: p.name, d.shown_panels())

    crp = d.color_radius_panel
    self.marker_color = crp.marker_color.rgba
    self.marker_radius = crp.marker_radius_entry.get()
    self.link_color = crp.link_color.rgba
    self.link_radius = crp.link_radius_entry.get()

    np = d.note_panel
    self.marker_note = np.marker_note.get()
    self.note_color = np.note_color.rgba
    
    sp = d.spline_panel
    self.curve_radius = sp.curve_radius.get()
    self.curve_band_length = sp.curve_band_length.get()
    self.curve_segment_subdivisions = sp.curve_segment_subdivisions.get()

    mbp = d.mouse_button_panel
    self.placement_button = mbp.placement_button.variable.get()
    self.use_mouse = mbp.use_mouse.get()

    self.place_markers_on_spots = d.place_markers_on_spots.get()
    self.place_markers_on_planes = d.place_markers_on_planes.get()
    self.place_markers_on_surfaces = d.place_markers_on_surfaces.get()
    self.place_markers_outside_data = d.place_markers_outside_data.get()
    self.place_markers_continuously = d.place_markers_continuously.get()
    self.move_markers = d.move_markers.get()
    self.marker_matches_volume_color = d.marker_matches_volume_color.get()
    self.link_to_selected = d.link_to_selected.get()
    self.link_consecutive = d.link_consecutive.get()

    slp = d.slice_panel
    self.use_volume_colors = slp.use_volume_colors.get()
    self.show_slice_line = slp.show_slice_line.get()
    self.slice_color = slp.slice_color.rgba

    srp = d.surface_panel
    self.cap_surface_ends = srp.cap_ends.get()
    sm = srp.surface_model
    if sm:
      plist = [p for p in sm.surfacePieces if hasattr(p, 'traced')]
      from Surface.session import Surface_Model_State
      sms = Surface_Model_State()
      sms.state_from_surface_model(sm, plist)
    else:
      sms = None
    self.surface_model_state = sms

    ams = d.active_marker_set
    if ams:
      self.active_marker_set_name = ams.name
    else:
      self.active_marker_set_name = ''
      
    # TODO: restore vrml slice line (d.slice_line_model)

  # ---------------------------------------------------------------------------
  #
  def restore_state(self, path_tracer_dialog):

    d = path_tracer_dialog
    if self.is_visible:
      d.enter()

    from SessionUtil import set_window_position
    set_window_position(d.toplevel_widget, self.geometry)

    if self.version >= 2:
      d.show_panels(self.shown_panels)

    crp = d.color_radius_panel
    crp.marker_color.showColor(self.marker_color, doCallback = False)
    crp.marker_radius_entry.set(self.marker_radius, invoke_callbacks = False)
    crp.link_color.showColor(self.link_color, doCallback = False)
    crp.link_radius_entry.set(self.link_radius, invoke_callbacks = False)

    np = d.note_panel
    np.marker_note.set(self.marker_note, invoke_callbacks = False)
    np.note_color.showColor(self.note_color, doCallback = False)

    sp = d.spline_panel
    sp.curve_radius.set(self.curve_radius, invoke_callbacks = False)
    sp.curve_band_length.set(self.curve_band_length, invoke_callbacks = False)
    sp.curve_segment_subdivisions.set(self.curve_segment_subdivisions,
                                      invoke_callbacks = False)

    if self.version >= 3:
      d.place_markers_on_spots.set(self.place_markers_on_spots,
                                   invoke_callbacks = False)
      d.place_markers_on_planes.set(self.place_markers_on_planes,
                                    invoke_callbacks = False)
      if self.version >= 4:
        d.place_markers_on_surfaces.set(self.place_markers_on_surfaces,
                                        invoke_callbacks = False)
      d.place_markers_outside_data.set(self.place_markers_outside_data,
                                       invoke_callbacks = False)
      d.place_markers_continuously.set(self.place_markers_continuously,
                                       invoke_callbacks = False)
    else:
      d.place_markers_on_spots.set(self.place_markers_on_data,
                                   invoke_callbacks = False)
      pmos = self.place_markers_on_space
      d.place_markers_on_planes.set(pmos, invoke_callbacks = False)
      d.place_markers_outside_data.set(pmos, invoke_callbacks = False)
      d.place_markers_continuously.set(False, invoke_callbacks = False)
    d.update_mouse_binding_cb() # Update mouse binding

    d.move_markers.set(self.move_markers, invoke_callbacks = False)
    d.marker_matches_volume_color.set(self.marker_matches_volume_color,
				      invoke_callbacks = False)
    d.link_to_selected.set(self.link_to_selected, invoke_callbacks = False)
    d.link_consecutive.set(self.link_consecutive, invoke_callbacks = False)
    d.consecutive_selection_cb()   # Register selection trigger

    mbp = d.mouse_button_panel
    mbp.placement_button.variable.set(self.placement_button,
                                      invoke_callbacks = False)
    if self.version >= 2:
      mbp.use_mouse.set(self.use_mouse, invoke_callbacks = False)
    mbp.bind_placement_button_cb()    # Update button binding.
    
    slp = d.slice_panel
    slp.use_volume_colors.set(self.use_volume_colors, invoke_callbacks = False)
    slp.show_slice_line.set(self.show_slice_line, invoke_callbacks = False)
    slp.slice_color.showColor(self.slice_color, doCallback = False)

    if self.version >= 3:
      srp = d.surface_panel
      srp.cap_ends.set(self.cap_surface_ends, invoke_callbacks = False)
      sms = getattr(self, 'surface_model_state', None)
      if sms:
        srp.surface_model = sm = sms.create_object()
        for p in sm.surfacePieces:
          p.traced = True

    if self.version <= 3:
      for ms in self.marker_set_states:
        ms.create_object()

    import markerset
    ams = markerset.find_marker_set_by_name(self.active_marker_set_name)
    if ams:
      d.set_active_marker_set(ams)

    from SimpleSession import registerAfterModelsCB
    registerAfterModelsCB(self.fix_stick_scale, path_tracer_dialog)

#
# TODO: Should I try to restore hand chosen marker thresholds for
#  volume data sets?
# data.volume_path_threshold
#
      
  # ---------------------------------------------------------------------------
  # SimpleSession changes the stickScale setting when Chimera 1.1700
  # session files are opened in Chimera >1.18xx.  This resets it to 1.
  #
  def fix_stick_scale(self, path_tracer_dialog):

    d = path_tracer_dialog
    from markerset import marker_sets
    for ms in marker_sets():
      if ms.molecule:
        ms.molecule.stickScale = 1.0

# -----------------------------------------------------------------------------
#
def marker_set_states():

  mss = []
  from markerset import marker_sets
  for ms in marker_sets():
    s = Marker_Set_State()
    s.state_from_marker_set(ms)
    mss.append(s)
  return mss

# -----------------------------------------------------------------------------
#
class Marker_Set_State:
  
  version = 3

  state_attributes = ('name',
		      'marker_model',
                      'molecule_session_id',
                      'color',
		      'curve_model',
		      'curve_parameters',
		      'next_marker_id',
		      'file_path',
		      'markers',
		      'links',
		      'extra_attributes',
		      'version',
		      )

  # ---------------------------------------------------------------------------
  #
  def state_from_marker_set(self, marker_set):

    ms = marker_set
    self.name = ms.name

    if ms.molecule:
      from SessionUtil.stateclasses import Model_State
      self.marker_model = Model_State()
      self.marker_model.state_from_model(ms.molecule)
      from SimpleSession import sessionID
      self.molecule_session_id = sessionID(ms.molecule)
      self.color = ms.molecule.color.rgba()
    else:
      self.marker_model = None
      self.molecule_session_id = None
      self.color = None

    if ms.curve_model:
      from SessionUtil.stateclasses import Model_State
      cm = Model_State()
      cm.state_from_model(ms.curve_model)
      self.curve_parameters = ms.curve_parameters
      self.curve_model = cm
    else:
      self.curve_model = None
      self.curve_parameters = None

    self.next_marker_id = ms.next_marker_id
    self.file_path = ms.file_path

    self.markers = []
    for m in ms.markers():
      s = Marker_State()
      s.state_from_marker(m)
      self.markers.append(s)

    self.links = []
    for l in ms.links():
      s = Link_State()
      s.state_from_link(l)
      self.links.append(s)

    if hasattr(ms, 'extra_attribtues'):		# from reading XML
      self.extra_attributes = ms.extra_attributes
    else:
      self.extra_attributes = None

  # ---------------------------------------------------------------------------
  #
  def create_object(self):

    import markerset
    ms = markerset.Marker_Set(self.name)

    ms.next_marker_id = self.next_marker_id
    ms.file_path = self.file_path

    mm = self.marker_model
    if mm:
      if self.version >= 3:
        from SimpleSession import idLookup
        m = idLookup(self.molecule_session_id)
        ms.set_marker_molecule(m)
        import markerset
        markerset.msc.open_models_cb(None, None, [m])
      else:
        from SimpleSession import modelOffset
        model_id = (mm.id + modelOffset, mm.subid)
        m = ms.marker_model(model_id)
      if self.version >= 2:
        m.color = markerset.chimera_color(self.color)

    id_to_marker = {}
    for m in self.markers:
      marker = m.create_object(ms)
      id_to_marker[marker.id] = marker

    for l in self.links:
      l.create_object(id_to_marker)

    if self.extra_attributes:
      ms.extra_attributes = self.extra_attributes

    if mm and ms.molecule:
      mm.restore_state(ms.molecule)

    cm = self.curve_model
    if cm:
      radius, band_length, subdivisions = self.curve_parameters
      ms.show_curve(radius, band_length, subdivisions)
      cm.restore_state(ms.curve_model)

    return ms

# -----------------------------------------------------------------------------
#
class Marker_State:
  
  version = 2

  state_attributes = ('id',
                      'atom_session_id',
		      'displayed',
		      'xyz',
		      'rgba',
		      'radius',
		      'note',
		      'note_rgba',
		      'note_shown',
		      'extra_attributes',
		      'version',
		      )

  # ---------------------------------------------------------------------------
  #
  def state_from_marker(self, marker):

    m = marker
    self.id = m.id
    from SimpleSession import sessionID
    self.atom_session_id = sessionID(m.atom)
    self.displayed = m.atom.display
    self.xyz = m.xyz()
    self.rgba = m.rgba(allow_none = True)
    self.radius = m.radius()
    self.note = m.note()
    self.note_rgba = m.note_rgba()
    self.note_shown = m.note_shown()
    if hasattr(m, 'extra_attributes'):		# from XML file
      self.extra_attributes = m.extra_attributes
    else:
      self.extra_attributes = None

  # ---------------------------------------------------------------------------
  #
  def create_object(self, marker_set):

    if self.version >= 2:
      from SimpleSession import idLookup
      atom = idLookup(self.atom_session_id)
    else:
      atom = None
    import markerset
    m = markerset.Marker(marker_set, self.id, self.xyz, self.rgba, self.radius,
                         atom = atom)
    m.atom.display = self.displayed
    m.set_note(self.note)
    m.set_note_rgba(self.note_rgba)
    m.show_note(self.note_shown)
    if self.extra_attributes:
      m.extra_attributes = self.extra_attributes

    return m

# -----------------------------------------------------------------------------
#
class Link_State:

  version = 2
  
  state_attributes = ('marker_id_1',
		      'marker_id_2',
                      'bond_session_id',
		      'displayed',
		      'rgba',
		      'radius',
		      'extra_attributes',
		      'version',
		      )

  # ---------------------------------------------------------------------------
  #
  def state_from_link(self, link):

    l = link
    self.marker_id_1 = l.marker1.id
    self.marker_id_2 = l.marker2.id
    from SimpleSession import sessionID
    self.bond_session_id = sessionID(l.bond)
    self.displayed = l.bond.display
    self.rgba = l.rgba(allow_none = True)
    self.radius = l.radius()
    if hasattr(l, 'extra_attributes'):		# from XML file
      self.extra_attributes = l.extra_attributes
    else:
      self.extra_attributes = None

  # ---------------------------------------------------------------------------
  #
  def create_object(self, id_to_marker):

    m1 = id_to_marker[self.marker_id_1]
    m2 = id_to_marker[self.marker_id_2]
    if self.version >= 2:
      from SimpleSession import idLookup
      bond = idLookup(self.bond_session_id)
    else:
      bond = None
    import markerset
    l = markerset.Link(m1, m2, self.rgba, self.radius, bond = bond)
    l.bond.display = self.displayed
    if self.extra_attributes:
      m.extra_attributes = self.extra_attributes

    return l
