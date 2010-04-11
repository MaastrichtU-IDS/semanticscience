# -----------------------------------------------------------------------------
# Save and restore surface color state.
#

# -----------------------------------------------------------------------------
#
def save_surface_color_state(coloring_table, file):

  s = Surface_Colorings_State()
  s.state_from_coloring_table(coloring_table)

  from gui import surface_color_dialog
  dialog = surface_color_dialog()
  s.state_from_dialog(dialog)
  
  from SessionUtil import objecttree
  t = objecttree.instance_tree_to_basic_tree(s)

  file.write('\n')
  file.write('def restore_surface_color_mapping():\n')
  file.write(' try:\n')
  file.write('  surface_color_state = \\\n')
  objecttree.write_basic_tree(t, file, indent = '   ')
  file.write('\n')
  file.write('  import SurfaceColor.session\n')
  file.write('  SurfaceColor.session.restore_surface_color_state(surface_color_state)\n')
  file.write(' except:\n')
  file.write("  reportRestoreError('Error restoring surface color mapping')\n")
  file.write('\n')
  file.write('registerAfterModelsCB(restore_surface_color_mapping)\n')
  file.write('\n')
  
# -----------------------------------------------------------------------------
#
def restore_surface_color_state(surface_color_state):

  classes = (
    Surface_Colorings_State,
    Volume_Color_State,
    Gradient_Color_State,
    Electrostatic_Color_State,
    Height_Color_State,
    Radial_Color_State,
    Cylinder_Color_State,
    Color_Map_State,
    )
  name_to_class = {}
  for c in classes:
    name_to_class[c.__name__] = c

  from SessionUtil import objecttree
  s = objecttree.basic_tree_to_instance_tree(surface_color_state,
                                             name_to_class)
  s.restore_state()

# -----------------------------------------------------------------------------
#
class Surface_Colorings_State:

  version = 2
  
  state_attributes = ('coloring_table',
                      'is_visible',     # Dialog shown
                      'geometry',       # Dialog position and size
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_dialog(self, dialog):

    if dialog:
      self.is_visible = dialog.isVisible()
      self.geometry = dialog.toplevel_widget.wm_geometry()
    else:
      self.is_visible = False
      self.geometry = None

  # ---------------------------------------------------------------------------
  #
  def state_from_coloring_table(self, coloring_table):

    ctable = {}
    for model, (color_source, caps_only) in coloring_table.items():
      if not color_source.closed():
        css = self.color_source_state(color_source)
        if css:
          m_id_subid = (model.id, model.subid)
          ctable[m_id_subid] = (css, caps_only)
    self.coloring_table = ctable

  # ---------------------------------------------------------------------------
  #
  def restore_state(self):

    import SurfaceColor
    for surface_id_subid, (color_state, caps_only) in self.coloring_table.items():
      from SimpleSession import modelMap
      from _surface import SurfaceModel
      slist = [s for s in modelMap.get(surface_id_subid, [])
               if isinstance(s, SurfaceModel)]
      if len(slist) > 0:
        surface = slist[0]
        color_source = color_state.create_color_source()
        SurfaceColor.color_surface(surface, color_source, caps_only,
                                   auto_update = True)
      else:
        from chimera import replyobj
        replyobj.info('Warning: Could not restore surface color on surface model\n\twith id %d.%d because that surface was not restored.\n' % surface_id_subid)

    # Update gui to show settings from restored session.
    if self.version >= 2:
      if self.coloring_table:
        if self.is_visible:
          from gui import surface_color_dialog
          d = surface_color_dialog(create = True)
          if self.geometry:
            from SessionUtil import set_window_position
            set_window_position(d.toplevel_widget, self.geometry)
          d.surface_menu_cb()
          d.enter()

  # ---------------------------------------------------------------------------
  #
  def color_source_state(self, color_source):

    from SurfaceColor import Gradient_Color, Volume_Color
    from SurfaceColor import Height_Color, Radial_Color, Cylinder_Color
    for cst, css in ((Electrostatic_Color, Electrostatic_Color_State),
                     (Gradient_Color, Gradient_Color_State),
                     (Volume_Color, Volume_Color_State),
                     (Height_Color, Height_Color_State),
                     (Radial_Color, Radial_Color_State),
                     (Cylinder_Color, Cylinder_Color_State)):
      if isinstance(color_source, cst):
        cs = css()
        cs.state_from_color_source(color_source)
        break

    return cs

# -----------------------------------------------------------------------------
#
class Base_Volume_Color_State:

  version = 4

  state_attributes = ('session_volume_id',
                      'colormap',
                      'per_pixel_coloring',
                      'offset',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_color_source(self, color_source):

    self.session_volume_id = id(color_source.volume)
    cmap = Color_Map_State()
    cmap.state_from_color_map(color_source.colormap)
    self.colormap = cmap
    self.per_pixel_coloring = color_source.per_pixel_coloring
    self.offset = color_source.offset
    
  # ---------------------------------------------------------------------------
  #
  def create_color_source(self):

    from VolumeViewer.session import find_volume_by_session_id
    volume = find_volume_by_session_id(self.session_volume_id)
    vc = self.color_source()
    vc.set_volume(volume)
    cmap = self.colormap.create_color_map()
    vc.set_colormap(cmap)
    if self.version >= 3:
      vc.per_pixel_coloring = self.per_pixel_coloring
    if self.version >= 4:
      vc.offset = self.offset
    return vc

# -----------------------------------------------------------------------------
#
from SurfaceColor import Volume_Color, Gradient_Color, Electrostatic_Color

# -----------------------------------------------------------------------------
#
class Volume_Color_State(Base_Volume_Color_State):

  color_source = Volume_Color
  def create_color_source(self):

    if self.version == 1:
      self.session_volume_id = self.volume_name
    return Base_Volume_Color_State.create_color_source(self)

# -----------------------------------------------------------------------------
#
class Gradient_Color_State(Base_Volume_Color_State):
  color_source = Gradient_Color

# -----------------------------------------------------------------------------
#
class Electrostatic_Color_State(Base_Volume_Color_State):
  color_source = Electrostatic_Color

# -----------------------------------------------------------------------------
#
class Height_Color_State:

  version = 1
  
  state_attributes = ('origin',
                      'axis',
                      'colormap',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_color_source(self, color_source):

    self.origin = color_source.origin
    self.axis = color_source.axis

    cmap = Color_Map_State()
    cmap.state_from_color_map(color_source.colormap)
    self.colormap = cmap
    
  # ---------------------------------------------------------------------------
  #
  def create_color_source(self):

    import SurfaceColor
    hc = SurfaceColor.Height_Color()
    hc.set_origin(self.origin)
    hc.set_axis(self.axis)
    cmap = self.colormap.create_color_map()
    hc.set_colormap(cmap)
    return hc

# -----------------------------------------------------------------------------
#
class Radial_Color_State:

  version = 1
  
  state_attributes = ('origin',
                      'colormap',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_color_source(self, color_source):

    self.origin = color_source.origin

    cmap = Color_Map_State()
    cmap.state_from_color_map(color_source.colormap)
    self.colormap = cmap
    
  # ---------------------------------------------------------------------------
  #
  def create_color_source(self):

    import SurfaceColor
    rc = SurfaceColor.Radial_Color()
    rc.set_origin(self.origin)
    cmap = self.colormap.create_color_map()
    rc.set_colormap(cmap)
    return rc

# -----------------------------------------------------------------------------
#
class Cylinder_Color_State:

  version = 1
  
  state_attributes = ('origin',
                      'axis',
                      'colormap',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_color_source(self, color_source):

    self.origin = color_source.origin
    self.axis = color_source.axis

    cmap = Color_Map_State()
    cmap.state_from_color_map(color_source.colormap)
    self.colormap = cmap
    
  # ---------------------------------------------------------------------------
  #
  def create_color_source(self):

    import SurfaceColor
    cc = SurfaceColor.Cylinder_Color()
    cc.set_origin(self.origin)
    cc.set_axis(self.axis)
    cmap = self.colormap.create_color_map()
    cc.set_colormap(cmap)
    return cc

# -----------------------------------------------------------------------------
#
class Color_Map_State:

  version = 1
  
  state_attributes = ('data_values',
                      'colors',
                      'color_above_value_range',
                      'color_below_value_range',
                      'color_no_value',
		      'version',
                      )

  # ---------------------------------------------------------------------------
  #
  def state_from_color_map(self, cmap):

    for attr in self.state_attributes:
      if attr != 'version':
        setattr(self, attr, getattr(cmap, attr))

  # ---------------------------------------------------------------------------
  #
  def create_color_map(self):

    import SurfaceColor
    cmap = SurfaceColor.Color_Map(self.data_values, self.colors,
                                  self.color_above_value_range,
                                  self.color_below_value_range,
                                  self.color_no_value)
    return cmap
