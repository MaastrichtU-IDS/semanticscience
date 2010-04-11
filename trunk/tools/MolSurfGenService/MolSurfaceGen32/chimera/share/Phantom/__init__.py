# -----------------------------------------------------------------------------
# Settings dialog for using Phantom force feedback device with volume data.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Phantom_Dialog(ModelessDialog):

  title = 'Phantom Cursor'
  name = 'phantom cursor'
  buttons = ('Settings', 'Markers', 'Close')
  help = 'ContributedSoftware/phantom/framephantom.html'
  
  def fillInUI(self, parent):

    self.phantom_device = None
    self.cursor_model = None
    self.phantom_handler = None
    self.gradient_force = None
    self.phantom_button_down = 0
    self.last_phantom_transform = None
    self.last_roll = None
    self.key_callback_registered = None
    self.mode = 'cursor'        # 'cursor', 'move models', 'zoom',
                                # 'contour level', 'move marker'
    self.command_list_shown = False

    import Tkinter
    from CGLtk import Hybrid

    row = 0

    po = Hybrid.Checkbutton_Row(parent, 'Enable', ('cursor', 'forces', 'key commands'))
    po.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.phantom_on, self.force_field, self.commands = \
        [c.variable for c in po.checkbuttons]
    self.phantom_on.add_callback(self.settings_changed_cb)
    self.force_field.add_callback(self.settings_changed_cb)
    self.commands.add_callback(self.toggle_commands_cb)

    cf = Tkinter.Frame(parent)
    cf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    cs = Hybrid.Option_Menu(cf, 'Cursor shape ',
                            'cross', 'jack', 'sphere', 'volume crosshair')
    cs.frame.grid(row = 0, column = 0, sticky = 'nw')
    row = row + 1
    cs.variable.set('jack')
    cs.add_callback(self.settings_changed_cb)
    self.cursor_shape = cs.variable

    from VolumeViewer import active_volume
    v = active_volume()
    if v:
      csize = '%.3g' % (10 * max(v.data.step))
    else:
      csize = '1'
    cs = Hybrid.Entry(cf, ' size ', 5, csize)
    cs.frame.grid(row = 0, column = 1, sticky = 'w')
    cs.entry.bind('<KeyPress-Return>', self.settings_changed_cb)
    self.cursor_size = cs.variable

    cl = Tkinter.Label(cf, text = ' color ')
    cl.grid(row = 0, column = 2, sticky = 'w')

    from CGLtk.color import ColorWell
    cc = ColorWell.ColorWell(cf, callback = self.settings_changed_cb)
    self.cursor_color = cc
    cc.showColor((0,0.5,1), doCallback = 0)
    cc.grid(row = 0, column = 3, sticky = 'w')

    sp = Hybrid.Popup_Panel(parent)
    spf = sp.frame
    spf.grid(row = row, column = 0, sticky = 'news')
    spf.grid_remove()
    spf.columnconfigure(0, weight=1)
    self.settings_panel = sp.panel_shown_variable
    row += 1
    srow = 0

    cb = sp.make_close_button(spf)
    cb.grid(row = srow, column = 1, sticky = 'e')

    pr = Hybrid.Entry(spf, 'Phantom physical range (mm) ', 5, '200')
    pr.frame.grid(row = srow, column = 0, sticky = 'w')
    srow += 1
    pr.entry.bind('<KeyPress-Return>', self.settings_changed_cb)
    self.phantom_range = pr.variable

    mf = Hybrid.Entry(spf, 'Maximum force (lbs) ', 5, '.4')
    mf.frame.grid(row = srow, column = 0, sticky = 'w')
    srow += 1
    mf.entry.bind('<KeyPress-Return>', self.settings_changed_cb)
    self.maximum_force = mf.variable

    af = Hybrid.Checkbutton(spf, 'Auto-adjust force constant', 1)
    af.button.grid(row = srow, column = 0, sticky = 'w')
    srow += 1
    self.auto_adjust_force_constant = af.variable
    self.force_field.add_callback(self.settings_changed_cb)

    fc = Hybrid.Logarithmic_Scale(spf, 'Force constant ',
                                  .0001, 100, 1, '%.2g')
    fc.frame.grid(row = srow, column = 0, sticky = 'ew')
    srow += 1
    fc.set_value(1)
    fc.callback(self.force_constant_changed_cb)
    fc.entry.bind('<KeyPress-Return>', self.force_constant_changed_cb)
    self.force_constant = fc
    
    vf = Tkinter.Frame(spf)
    vf.grid(row = srow, column = 0, sticky = 'ew')
    srow += 1

    self.label_row(vf, 0, ('', 'x', 'y', 'z'))
    pl = self.label_row(vf, 1, ('Phantom position', '', '', ''))
    self.phantom_position_labels = pl[1:]
    cpl = self.label_row(vf, 2, ('Chimera position', '', '', ''))
    self.chimera_position_labels = cpl[1:]
    vpl = self.label_row(vf, 3, ('Volume position', '', '', ''))
    self.volume_position_labels = vpl[1:]
    vil = self.label_row(vf, 4, ('Volume index', '', '', ''))
    self.volume_index_labels = vil[1:]
    gl = self.label_row(vf, 5, ('Gradient', '', '', ''))
    self.gradient_labels = gl[1:]
    fl = self.label_row(vf, 6, ('Force', '', '', ''))
    self.force_labels = fl[1:]
    dvl = self.label_row(vf, 7, ('Data value', ''))
    self.data_value_label = dvl[1]
    
  # ---------------------------------------------------------------------------
  #
  def Settings(self):

    self.settings_panel.set(not self.settings_panel.get())
    
  # ---------------------------------------------------------------------------
  #
  def Markers(self):

    import VolumePath
    VolumePath.show_volume_path_dialog()
      
  # ---------------------------------------------------------------------------
  #
  def toggle_commands_cb(self):

    self.activate_key_commands(self.commands.get())

  # ---------------------------------------------------------------------------
  #
  def activate_key_commands(self, active):

    #
    # Always delete callback and reregister so it preempts
    # the Chimera command line.
    #
    if self.key_callback_registered:
      from chimera import tkgui
      tkgui.deleteKeyboardFunc(self.key_callback_registered)
      self.key_callback_registered = None

    if active:
      from chimera import tkgui
      self.key_callback_registered = self.key_pressed_cb
      tkgui.addKeyboardFunc(self.key_callback_registered)
      self.list_commands()
      tkgui.app.graphics.focus()
 
    self.commands.set(active, invoke_callbacks = 0)

  # ---------------------------------------------------------------------------
  #
  def key_pressed_cb(self, event):

    if event.keysym == 'Escape':
      self.activate_key_commands(False)
      from chimera.replyobj import status
      status('escape - turned off Phantom keyboard commands')
      return

    c = event.char
    if c == '':
      return		# Modifier or function key

    msg = None
    if c == ' ':
      if self.mode == 'cursor': self.mode = 'move models'
      else: self.mode = 'cursor'
    elif c == 'z':
      if self.mode == 'zoom': self.mode = 'cursor'
      else: self.mode = 'zoom'
    elif c == 'c':
      if self.mode == 'contour level': self.mode = 'cursor'
      else: self.mode = 'contour level'
    elif c == 'p':
      if self.mode == 'move marker':
        self.mode = 'cursor'
      else:
        if self.grab_marker():
          self.mode = 'move marker'
        else:
          msg = 'No marker under cursor'
    elif c == 'f':
      self.toggle_force_field()
    elif c == 'm':
      self.place_marker()
    elif c == 's':
      self.select_marker()
    elif c == 'u':
      self.unselect_markers()
    elif c == 'd':
      self.delete_selected_markers()
    elif c == 'x':
      self.delete_selected_links()

    if msg is None:
      msg = {
        ' ': 'move models',
        'z': 'zoom',
        'c': 'contour level adjustment',
        'f': 'force on/off',
        'm': 'place marker',
        'p': 'move marker position',
        's': 'select marker',
        'u': 'unselect all markers',
        'd': 'delete selected markers',
        'x': 'delete selected links',
        }.get(c, 'unknown Phantom command')

      if c in (' ', 'z', 'c', 'p') and self.mode == 'cursor':
        msg += ' (off)'

    from chimera.replyobj import status
    status('%s - %s' % (c, msg))

  # ---------------------------------------------------------------------------
  #
  def list_commands(self):

    if self.command_list_shown:
      return

    commands = \
'''Phantom keyboard commands
        space - move models
          z   - zoom
          c   - contour level adjustment
          f   - force on/off
          m   - place marker
          p   - move marker position
          s   - select marker
          u   - unselect all markers
          d   - delete selected markers
          x   - delete selected links
        escape - turn off commands
'''
    from chimera.replyobj import info
    info(commands)
    self.command_list_shown = True
    from Accelerators.standard_accelerators import show_reply_log
    show_reply_log()

  # ---------------------------------------------------------------------------
  #
  def label_row(self, parent, row, strings):

    labels = []
    import Tkinter
    for col in range(len(strings)):
      label = Tkinter.Label(parent, text = strings[col], anchor = 'e')
      if col > 0:
        label.configure(width = 8)
      label.grid(row = row, column = col, sticky = 'w')
      labels.append(label)

    return labels
    
  # ---------------------------------------------------------------------------
  #
  def have_phantom(self):

    try:
      import _phantomcursor
    except:
      from chimera.replyobj import warning
      warning('Could not load Chimera _phantomcursor library.\n' +
              'This library is only available on Windows.\n' +
	      'You must have the Sensable OpenHaptics libraries installed.\n')
      return 0

    return 1
      
  # ---------------------------------------------------------------------------
  #
  def settings_changed_cb(self, event = None):

    if not self.have_phantom():
      return
    
    phantom_on = self.phantom_on.get()
    if not phantom_on:
      if self.cursor_model:
	chimera.openModels.close([self.cursor_model])
      return

    phantom_range_mm = float_variable_value(self.phantom_range)
    box_size_mm = (phantom_range_mm, phantom_range_mm, phantom_range_mm)

    shape = self.cursor_shape.get()
    from _phantomcursor import Cursor_Model
    cursor_shape = {'cross': Cursor_Model.Cross,
                    'jack': Cursor_Model.Jack,
                    'sphere': Cursor_Model.Sphere,
                    'volume crosshair': Cursor_Model.Cross,
                    }[shape]

    cursor_size = float_variable_value(self.cursor_size)
    r,g,b = self.cursor_color.rgb
    cursor_color = chimera.MaterialColor(r,g,b)

    pd = self.phantom_device
    cm = self.cursor_model
    if pd == None or cm == None:
      pd, cm = self.make_phantom_cursor_model(box_size_mm, cursor_shape,
					      cursor_size, cursor_color)
      self.phantom_device = pd
      self.cursor_model = cm
      chimera.addModelClosedCallback(cm, self.model_closed_cb)
    else:
      pd.box_size_mm = box_size_mm
      cm.cursor_style = cursor_shape
      cm.cursor_size = cursor_size
      cm.cursor_color = cursor_color

    crosshair_on = (self.cursor_shape.get() == 'volume crosshair')
    cm.show_crosshair = crosshair_on

    self.update_force_field()
      
  # ---------------------------------------------------------------------------
  # Force constant adjusted by user, so turn of auto-adjust.
  #
  def force_constant_changed_cb(self, event = None):

    self.auto_adjust_force_constant.set(0)

  # ---------------------------------------------------------------------------
  #
  def toggle_force_field(self):

    self.force_field.set(not self.force_field.get())

  # ---------------------------------------------------------------------------
  #
  def place_marker(self):

    if self.phantom_device:
      d = volume_path_dialog()
      p = self.phantom_device.cursor_position()
      xyz = (p.x, p.y, p.z)
      d.add_marker_3d(xyz)

  # ---------------------------------------------------------------------------
  #
  def grab_marker(self):

    if self.phantom_device:
      d = volume_path_dialog()
      p = self.phantom_device.cursor_position()
      xyz = (p.x, p.y, p.z)
      return d.grab_marker_3d(xyz)

  # ---------------------------------------------------------------------------
  #
  def move_marker(self):

    if self.phantom_device:
      d = volume_path_dialog()    
      p = self.phantom_device.cursor_position()
      xyz = (p.x, p.y, p.z)
      d.move_marker_3d(xyz)

  # ---------------------------------------------------------------------------
  #
  def delete_selected_markers(self):

    d = volume_path_dialog()    
    d.delete_markers_cb()

  # ---------------------------------------------------------------------------
  #
  def select_marker(self):

    if self.phantom_device:
      d = volume_path_dialog()    
      p = self.phantom_device.cursor_position()
      xyz = (p.x, p.y, p.z)
      d.select_marker_3d(xyz)

  # ---------------------------------------------------------------------------
  #
  def unselect_markers(self):

    d = volume_path_dialog()    
    d.unselect_all_markers()

  # ---------------------------------------------------------------------------
  #
  def delete_selected_links(self):

    d = volume_path_dialog()
    d.delete_links_cb()

  # ---------------------------------------------------------------------------
  #
  def make_phantom_cursor_model(self, box_size_mm, cursor_shape,
                                cursor_size, cursor_color):

    import _phantomcursor

    p = _phantomcursor.Phantom_Device('Default PHANToM')
    p.box_size_mm = box_size_mm

    m = _phantomcursor.Cursor_Model()
    m.name = 'Phantom cursor'
    m.cursor_style = cursor_shape
    m.cursor_size = cursor_size
    m.cursor_color = cursor_color
    m.show_cursor = 1

    chimera.openModels.add([m])
    self.add_phantom_handler()

    return p, m
      
  # ---------------------------------------------------------------------------
  #
  def add_phantom_handler(self):

    if self.phantom_handler == None:
      h = chimera.triggers.addHandler('check for changes',
                                      self.update_phantom_position, None)
      self.phantom_handler = h
      
  # ---------------------------------------------------------------------------
  #
  def remove_phantom_handler(self):

    if self.phantom_handler != None:
      chimera.triggers.deleteHandler('check for changes', self.phantom_handler)
      self.phantom_handler = None
      
  # ---------------------------------------------------------------------------
  # Phantom only updates the displayed cursor position when its
  # update_cursor_position() method is called.
  #
  def update_phantom_position(self, trigger, callData, triggerData):

    if self.phantom_device == None:
      self.remove_phantom_handler()
      return

    self.update_phantom_bounds()
    self.handle_button_events()
    self.update_cursor_position()
    self.handle_marker_drag()
    self.handle_model_drag()
    self.handle_zoom()
    self.handle_threshold_change()

    if self.settings_panel.get():
      self.show_position()

    self.update_force_field()

    yaw, pitch, roll = self.phantom_device.stylus_gimbal_angles()
    self.last_roll = roll

  # ---------------------------------------------------------------------------
  #
  def update_phantom_bounds(self):

    self.phantom_device.position_phantom_box(chimera.viewer.camera)

  # ---------------------------------------------------------------------------
  #
  def handle_button_events(self):

    button_down = self.phantom_device.button_pressed()
    pressed = (button_down and not self.phantom_button_down)
    released = (not button_down and self.phantom_button_down)
    self.phantom_button_down = button_down
    if pressed:
      self.phantom_button_pressed()
    elif released:
      self.phantom_button_released()
      
  # ---------------------------------------------------------------------------
  #
  def update_cursor_position(self):

    try:
      xf = self.phantom_device.transform()
      self.cursor_model.openState.xform = xf
    except:
      self.remove_phantom_handler()
      return
      
  # ---------------------------------------------------------------------------
  #
  def handle_marker_drag(self):

    if self.phantom_button_down	or self.mode == 'move marker':
      self.move_marker()
      
  # ---------------------------------------------------------------------------
  #
  def handle_model_drag(self):

    if self.mode == 'move models':
      xf = self.phantom_device.transform()
      if self.last_phantom_transform:
	delta = chimera.Xform()
	delta.multiply(self.last_phantom_transform)
	delta.invert()
	delta.premultiply(xf)
	move_active_models(delta)
      self.last_phantom_transform = xf
    else:
      self.last_phantom_transform = None
      
  # ---------------------------------------------------------------------------
  #
  def handle_zoom(self):

    if not self.mode == 'zoom' or self.last_roll == None:
      return

    yaw, pitch, roll = self.phantom_device.stylus_gimbal_angles()
    import math
    scale = math.exp(roll - self.last_roll)
    chimera.viewer.scaleFactor *= scale
      
  # ---------------------------------------------------------------------------
  #
  def handle_threshold_change(self):

    if not self.mode == 'contour level' or self.last_roll == None:
      return

    r = self.data_region()
    if r == None:
      return

    yaw, pitch, roll = self.phantom_device.stylus_gimbal_angles()
    import math
    scale = math.exp(roll - self.last_roll)

    if r.representation == 'surface' or r.representation == 'mesh':
      surf_levels = r.surface_levels
      if surf_levels:
	surf_levels[0] *= scale
	r.show()
    elif r.representation == 'solid':
      solid_levels = r.solid_levels
      if solid_levels:
	t, h = solid_levels[0]
	solid_levels[0] = (scale*t, h)
	r.show()
      
  # ---------------------------------------------------------------------------
  #
  def phantom_button_pressed(self):

    if not self.grab_marker():
      self.place_marker()
      
  # ---------------------------------------------------------------------------
  #
  def phantom_button_released(self):

    d = volume_path_dialog()
    d.ungrab_marker()

  # ---------------------------------------------------------------------------
  #
  def show_position(self):

    ppos = self.phantom_device.cursor_position_mm()
    cpos = self.phantom_device.cursor_position()
    for a in range(3):
      self.phantom_position_labels[a]['text'] = float_format(ppos[a], 3)
      self.chimera_position_labels[a]['text'] = float_format(cpos[a], 3)

    gf = self.gradient_force
    v = self.data_region()
    if gf and v:
      xf = v.model_transform()
      vpos = xf.inverse().apply(cpos)
      from Matrix import apply_matrix
      ipos = apply_matrix(gf.xyz_to_grid_index, cpos.data())
      grad = gf.gradient(cpos)
      grad = xf.inverse().apply(grad)   # Transform global to volume coords
      force = gf.force(cpos)
      force = xf.inverse().apply(force)   # Transform global to volume coords
      for a in range(3):
        self.volume_position_labels[a]['text'] = float_format(vpos[a], 3)
        self.volume_index_labels[a]['text'] = float_format(ipos[a], 3)
        self.gradient_labels[a]['text'] = float_format(grad[a], 3)
        self.force_labels[a]['text'] = float_format(force[a], 3)
      data_value = gf.data_value(cpos)
      self.data_value_label['text'] = float_format(data_value, 3)
    else:
      labels = (self.volume_position_labels + self.volume_index_labels +
                self.gradient_labels + self.force_labels +
                [self.data_value_label])
      for label in labels:
        label['text'] = ''
      
  # ---------------------------------------------------------------------------
  # Create or update Gradient_Force_Field for the active volume.
  #
  def update_force_field(self):

    pd = self.phantom_device
    if pd == None:
      return

    dr = self.data_region()
    if dr == None:
      self.remove_gradient_force()
      return

    data = dr.matrix(read_matrix = False)
    if data is None:
      self.remove_gradient_force()
      return

    xform = dr.model_transform()
    if xform == None:
      self.remove_gradient_force()
      return

    ijk_min, ijk_max = dr.ijk_bounds()
    bbox = chimera.BBox()
    bbox.llf = chimera.Point(*ijk_min)
    bbox.urb = chimera.Point(*ijk_max)
    cm = self.cursor_model
    cm.crosshair_bounding_box = bbox
    from Matrix import multiply_matrices, xform_matrix, invert_matrix
    btf = multiply_matrices(xform_matrix(xform), dr.data.ijk_to_xyz_transform)
    btf_inv = invert_matrix(btf)
    cm.crosshair_box_transform = (btf, btf_inv)

    #
    # TODO: These parameters are not adequate to determine whether volume
    # has changed.
    #
    volume_parameters = data.shape
    gf = self.gradient_force
    if gf and gf.volume_parameters != volume_parameters:
      self.remove_gradient_force()
      gf = None

    newtons_per_pound = 4.45
    max_force_lbs = float_variable_value(self.maximum_force)
    max_force = newtons_per_pound * max_force_lbs

    force_constant = self.force_constant.value(default = 0)
    if self.auto_adjust_force_constant.get():
      force_constant = self.adjust_force_constant(force_constant, max_force)

    ijk_to_vxyz = dr.matrix_indices_to_xyz_transform()
    from Matrix import multiply_matrices, xform_matrix, invert_matrix
    ijk_to_xyz = multiply_matrices(xform_matrix(xform), ijk_to_vxyz)
    xyz_to_ijk = invert_matrix(ijk_to_xyz)

    if gf == None:
      import _phantomcursor
      gf = _phantomcursor.Gradient_Force_Field(data, xyz_to_ijk,
					       force_constant, max_force)
      gf.volume_parameters = volume_parameters
      self.gradient_force = gf
      pd.force_active = 0
      pd.phantom_force_field = gf
    else:
      gf.maximum_force = max_force
      gf.force_constant = force_constant
      gf.xyz_to_grid_index = xyz_to_ijk

    force_on = (self.force_field.get() and
	        (self.mode == 'cursor' or self.mode == 'move marker'))
    pd.force_active = force_on

  # ---------------------------------------------------------------------------
  # If auto-adjust force constant is on, 
  #
  def adjust_force_constant(self, force_constant, max_force):

    pd = self.phantom_device
    if pd == None:
      return force_constant

    gf = self.gradient_force
    if gf == None:
      self.force_constant.set_value(0, invoke_callbacks = 0)
      return 0

    cpos = pd.cursor_position()
    grad = gf.gradient(cpos)
    import math
    gnorm = math.sqrt(grad[0]*grad[0] + grad[1]*grad[1] + grad[2]*grad[2])
    if ((force_constant == 0 and gnorm > 0)
	or gnorm * force_constant > max_force):
      force_constant = max_force / gnorm
      self.force_constant.set_value(force_constant, invoke_callbacks = 0)

    return force_constant

  # ---------------------------------------------------------------------------
  #
  def remove_gradient_force(self):

    if self.gradient_force:
      self.gradient_force = None
      if self.phantom_device:
	self.phantom_device.phantom_force_field = None
    
  # ---------------------------------------------------------------------------
  #
  def data_region(self):

    from VolumeViewer import active_volume
    return active_volume()
    
  # ---------------------------------------------------------------------------
  #
  def model_closed_cb(self, model):

    self.cursor_model = None
    import sys
    self.phantom_device.close()
    self.phantom_device = None
    self.remove_phantom_handler()
    self.gradient_force = None

# -----------------------------------------------------------------------------
#
def float_variable_value(v, default = None):

  try:
    return float(v.get())
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

  text = format % value

  return text

# -----------------------------------------------------------------------------
#
def move_active_models(xform):

  ostates = {}
  for m in chimera.openModels.list(all = 1):
    ostates[m.openState] = 1

  active_ostates = filter(lambda ostate: ostate.active, ostates.keys())
  for ostate in active_ostates:
    ostate.globalXform(xform)

# -----------------------------------------------------------------------------
#
def volume_path_dialog():

  import VolumePath
  return VolumePath.volume_path_dialog(create = 1)
  
# -----------------------------------------------------------------------------
#
def show_phantom_dialog():

  from chimera import dialogs
  return dialogs.display(Phantom_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Phantom_Dialog.name, Phantom_Dialog, replace = 1)
