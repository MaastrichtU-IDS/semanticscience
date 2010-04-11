# -----------------------------------------------------------------------------
# Dialog for controlling graphics window scale bar.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Scalebar_Dialog(ModelessDialog):

  title = 'Scale Bar'
  name = 'scale bar'
  buttons = ('Close',)
  help = 'ContributedSoftware/scalebar/scalebar.html'
  
  def fillInUI(self, parent):

    self.model = None
    self.position_handler = None
    self.screen_position = (-.6, -.6)
    self.last_xyz_position = None
    self.frozen_model_list = []

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()
    
    row = 0

    import Tkinter
    from CGLtk import Hybrid

    sb = Hybrid.Checkbutton(parent, 'Show scale bar', 0)
    sb.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.show_scalebar = sb.variable
    self.show_scalebar.add_callback(self.settings_changed_cb)

    bf = Tkinter.Frame(parent)
    bf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    le = Hybrid.Entry(bf, 'Length ', 5, '10')
    le.frame.grid(row = 0, column = 0, sticky = 'w')
    le.entry.bind('<KeyPress-Return>', self.settings_changed_cb)
    self.bar_length = le.variable

    te = Hybrid.Entry(bf, ' Thickness', 3, '1')
    te.frame.grid(row = 0, column = 1, sticky = 'w')
    te.entry.bind('<KeyPress-Return>', self.settings_changed_cb)
    self.bar_thickness = te.variable

    cl = Tkinter.Label(bf, text = ' Color ')
    cl.grid(row = 0, column = 2, sticky = 'w')

    from CGLtk.color import ColorWell
    bc = ColorWell.ColorWell(bf, callback = self.settings_changed_cb)
    self.bar_color = bc
    bc.showColor((1,1,1), doCallback = 0)
    bc.grid(row = 0, column = 3, sticky = 'w')

    lf = Tkinter.Frame(parent)
    lf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    # \u00C5 is the Angstrom symbol
    lb = Hybrid.Entry(lf, 'Label ', 5, u'# \u00C5')
    lb.frame.grid(row = 0, column = 0, sticky = 'w')
    lb.entry.bind('<KeyPress-Return>', self.settings_changed_cb)
    self.label_text = lb.variable

    xo = Hybrid.Entry(lf, ' Offset ', 3, '')
    xo.frame.grid(row = 0, column = 1, sticky = 'w')
    xo.entry.bind('<KeyPress-Return>', self.settings_changed_cb)
    self.label_x_offset = xo.variable

    yo = Hybrid.Entry(lf, '', 3, '')
    yo.frame.grid(row = 0, column = 2, sticky = 'w')
    yo.entry.bind('<KeyPress-Return>', self.settings_changed_cb)
    self.label_y_offset = yo.variable

    ct = Tkinter.Label(lf, text = ' Color ')
    ct.grid(row = 0, column = 3, sticky = 'w')

    from CGLtk.color import ColorWell
    lc = ColorWell.ColorWell(lf, callback = self.settings_changed_cb)
    self.label_color = lc
    lc.showColor((1,1,1), doCallback = 0)
    lc.grid(row = 0, column = 4, sticky = 'w')

    ore = Hybrid.Radiobutton_Row(parent, 'Orientation ',
                                 ('horizontal', 'vertical'),
                                 self.orientation_cb)
    ore.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.orientation = ore.variable
    self.orientation.set('horizontal', invoke_callbacks = 0)

    pf = Tkinter.Frame(parent)
    pf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    
    pp = Hybrid.Checkbutton(pf, 'Preserve screen position', 1)
    pp.button.grid(row = 0, column = 0, sticky = 'w')
    self.preserve_position = pp.variable
    self.preserve_position.add_callback(self.settings_changed_cb)

    xp = Hybrid.Entry(pf, '', 5, '')
    xp.frame.grid(row = 0, column = 1, sticky = 'w')
    xp.entry.bind('<KeyPress-Return>', self.settings_changed_cb)
    self.screen_x_position = xp.variable

    yp = Hybrid.Entry(pf, '', 5, '')
    yp.frame.grid(row = 0, column = 2, sticky = 'w')
    yp.entry.bind('<KeyPress-Return>', self.settings_changed_cb)
    self.screen_y_position = yp.variable

    self.set_screen_position_entries()
    
    mb = Hybrid.Checkbutton(parent,
                            'Move scale bar with data models locked', 0)
    mb.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.move_scalebar = mb.variable
    self.move_scalebar.add_callback(self.move_scalebar_cb)

    import SimpleSession
    chimera.triggers.addHandler(SimpleSession.SAVE_SESSION,
				self.save_session_cb, None)
    chimera.triggers.addHandler(chimera.CLOSE_SESSION,
				self.close_session_cb, None)
    
  # ---------------------------------------------------------------------------
  #
  def save_session_cb(self, trigger, x, file):

    import session
    session.save_scale_bar_state(self, file)
      
  # ---------------------------------------------------------------------------
  #
  def close_session_cb(self, trigger, a1, a2):

    self.show_scalebar.set(0)

  # ---------------------------------------------------------------------------
  #
  def settings_changed_cb(self, event = None, model_id = None):

    show = self.show_scalebar.get()
    if not show:
      if self.model:
	chimera.openModels.close([self.model])
      return

    self.update_screen_position_from_entries()

    length = float_variable_value(self.bar_length, 0)
    thickness = float_variable_value(self.bar_thickness, 1)
    rgb = self.bar_color.rgb
    
    label = self.label_text.get()
    label = label.replace('#', self.bar_length.get())
    xy_offset = (float_variable_value(self.label_x_offset, 0),
                 float_variable_value(self.label_y_offset, 0))
    label_rgb = self.label_color.rgb

    self.update_model(length, thickness, rgb, label, xy_offset, label_rgb,
                      model_id)

    if self.preserve_position.get():
      self.add_position_handler()
    else:
      self.remove_position_handler()
      self.last_xyz_position = None

  # ---------------------------------------------------------------------------
  #
  def set_screen_position_entries(self):

    self.screen_x_position.set('%.2g' % self.screen_position[0],
                               invoke_callbacks = 0)
    self.screen_y_position.set('%.2g' % self.screen_position[1],
                               invoke_callbacks = 0)
    
  # ---------------------------------------------------------------------------
  #
  def update_screen_position_from_entries(self):

    if ('%.2g' % self.screen_position[0] == self.screen_x_position.get() and
        '%.2g' % self.screen_position[1] == self.screen_y_position.get()):
      return
    
    self.screen_position = (float_variable_value(self.screen_x_position, 0),
                            float_variable_value(self.screen_y_position, 0))
      
  # ---------------------------------------------------------------------------
  #
  def update_model(self, length, thickness, rgb, label, xy_offset, label_rgb,
                   model_id = None):

    m = self.model
    if m == None:
      self.make_model(length, thickness, rgb, label, xy_offset, label_rgb,
                      model_id)
    else:
      c = chimera.Coord()
      c.x, c.y, c.z = (-length/2.0, 0, 0)
      m.atom1.setCoord(c)
      c.x, c.y, c.z = (length/2.0, 0, 0)
      m.atom2.setCoord(c)
      c.x, c.y, c.z = (xy_offset[0], xy_offset[1] + thickness/2.0, 0)
      m.label_atom.setCoord(c)
      b = m.bonds[0]
      b.radius = thickness/2.0
      b.color = chimera_color(rgb)
      m.label_atom.label = label
      m.label_atom.labelColor = chimera_color(label_rgb)
      
  # ---------------------------------------------------------------------------
  #
  def make_model(self, length, thickness, rgb, label, xy_offset, label_rgb,
                 model_id):

    m = chimera.Molecule()
    m.name = 'scale bar'
    
    #
    # Need to create a residue because atom without residue causes
    # unknown C++ exceptions.
    #
    rid = chimera.MolResId(1)
    r = m.newResidue('sb', rid)

    atoms = []
    for name, pos in (('1', (-length/2.0, 0, 0)),
                      ('2', (length/2.0, 0, 0)),
                      ('label',
                       (xy_offset[0], xy_offset[1] + thickness/2.0, 0))):
      a = m.newAtom(name, chimera.elements.H)
      r.addAtom(a)
      c = chimera.Coord()
      c.x, c.y, c.z = pos
      a.setCoord(c)                               # a.coord = c does not work
      a.display = 0
      atoms.append(a)
    m.atom1, m.atom2, m.label_atom = atoms
    m.label_atom.color = background_color()
    m.label_atom.display = 1
    
    b = m.newBond(m.atom1, m.atom2)
    b.display = b.Always
    b.drawMode = b.Stick
    b.radius = thickness/2.0
    b.color = chimera_color(rgb)
    b.halfbond = 0
    m.label_atom.label = label
    m.label_atom.labelColor = chimera_color(label_rgb)

    self.model = m

    if model_id == None:
      id, subid = (self.model_id(), chimera.openModels.Default)
    else:
      id, subid = model_id
    chimera.openModels.add([m], baseId = id, subid = subid)
    chimera.addModelClosedCallback(m, self.model_closed_cb)

    import SimpleSession
    SimpleSession.noAutoRestore(m)

    m.openState.active = False
    z_near, z_far = clip_plane_positions()
    self.set_depth(.5 * (z_near + z_far))
    self.set_screen_position(self.screen_position)
    self.orientation_cb()

    return m
      
  # ---------------------------------------------------------------------------
  # Choose a model id higher than all currently opened models and at least 9.
  # The point of this is to avoid having newly opened models aligned to the
  # scale bar.  Chimera aligns newly opened models to the model with lowest
  # id number.
  #
  def model_id(self):

    min_id = 9
    
    ids = map(lambda id_and_subid: id_and_subid[0],
              chimera.openModels.listIds())
    if ids:
      id = max(min_id, max(ids) + 1)
    else:
      id = min_id

    return id
  
  # ---------------------------------------------------------------------------
  #
  def orientation_cb(self):

    orient = self.orientation.get()
    self.orient_bar(orient == 'horizontal')
      
  # ---------------------------------------------------------------------------
  #
  def orient_bar(self, horizontal = 1):

    m = self.model
    if m == None:
      return

    xf = chimera.Xform()
    xyz = m.openState.xform.getTranslation()
    xf.translate(xyz)
    if not horizontal:
      xf.zRotate(-90)
    
    m.openState.xform = xf
      
  # ---------------------------------------------------------------------------
  #
  def add_position_handler(self):

    if self.position_handler == None:
      h = chimera.triggers.addHandler('check for changes',
                                      self.update_position_cb, None)
      self.position_handler = h
      
  # ---------------------------------------------------------------------------
  #
  def remove_position_handler(self):

    if self.position_handler != None:
      chimera.triggers.deleteHandler('check for changes', self.position_handler)
      self.position_handler = None
      
  # ---------------------------------------------------------------------------
  # Move scale bar to keep it at same screen position when camera view changes.
  #
  def update_position_cb(self, trigger, callData, triggerData):

    m = self.model
    if m == None:
      self.remove_position_handler()
      return

    t = m.openState.xform.getTranslation()
    xyz = (t.x, t.y, t.z)
    view = 0                    # Use left eye in stereo mode.
    xn, yn, zn = xyz_to_normalzed_screen_coordinates(xyz, view)

    if xyz != self.last_xyz_position:
      self.last_xyz_position = xyz
      self.screen_position = (xn, yn)
      self.set_screen_position_entries()
    else:
      sp = self.screen_position
      pos_tolerance = 1e-4
      if abs(xn - sp[0]) > pos_tolerance or abs(yn - sp[1]) > pos_tolerance:
        self.set_screen_position(sp)
      
  # ---------------------------------------------------------------------------
  #
  def set_depth(self, z):

    m = self.model
    if m == None:
      return

    xf = m.openState.xform
    t = xf.getTranslation()
    xf.premultiply(chimera.Xform.translation(0, 0, z - t.z))
    m.openState.xform = xf

    t = m.openState.xform.getTranslation()
    self.last_xyz_position = (t.x, t.y, t.z)
      
  # ---------------------------------------------------------------------------
  # Screen position given in normalized coordinates [-1,1].
  #
  def set_screen_position(self, xy_n):

    m = self.model
    if m == None:
      return

    sp = tuple(xy_n)
    xf = m.openState.xform
    t = xf.getTranslation()
    view = 0
    x, y, z = normalzed_screen_to_xyz_coordinates(sp, t.z, view)
    xf.premultiply(chimera.Xform.translation(x - t.x, y - t.y, 0))
    m.openState.xform = xf

    t = m.openState.xform.getTranslation()
    self.last_xyz_position = (t.x, t.y, t.z)
      
  # ---------------------------------------------------------------------------
  #
  def move_scalebar_cb(self):

    if self.model == None:
      return
    
    move = self.move_scalebar.get()
    if move:
      self.freeze_data_models()
    else:
      self.unfreeze_data_models()
      
    self.model.openState.active = move
        
  # ---------------------------------------------------------------------------
  #
  def freeze_data_models(self):

    active_models = filter(lambda m: m.openState.active,
                           chimera.openModels.list(all = True))
    for m in active_models:
      m.openState.active = False
    self.frozen_model_list = active_models
        
  # ---------------------------------------------------------------------------
  #
  def frozen_models(self):

    # Remove closed models from list.
    fmlist = filter(lambda m: not m.__destroyed__, self.frozen_model_list)
    self.frozen_model_list = fmlist
    return fmlist
        
  # ---------------------------------------------------------------------------
  #
  def unfreeze_data_models(self):

    for m in self.frozen_models():
      m.openState.active = True
    self.frozen_model_list = []
        
  # ---------------------------------------------------------------------------
  #
  def model_closed_cb(self, model):

    self.model = None
    self.remove_position_handler()
    self.last_xyz_position = None
    self.show_scalebar.set(0, invoke_callbacks = 0)
    self.move_scalebar.set(0, invoke_callbacks = 0)
    self.unfreeze_data_models()
    
# -----------------------------------------------------------------------------
#
def xyz_to_normalzed_screen_coordinates(xyz, view):

  x, y, z = xyz
  
  #
  # Shift by eye position.
  #
  c = chimera.viewer.camera
  ex, ey, ez = c.eyePos(view)

  xe = x - ex
  ye = y - ey
  ze = z - ez

  #
  # Projection matrix maps window lower left and upper right corners to near
  # clip plane corners (left, bottom, -znear), (right, top, -znear).
  #
  left, right, bottom, top, znear, zfar, f = c.window(view)

  if c.ortho:
    xnr = xe
    ynr = ye
  elif ze == 0:
    xnr = ynr = 0                       # really should be undefined
  else:
    xnr = xe * (-znear / ze)
    ynr = ye * (-znear / ze)

  xn = (xnr - .5*(left + right)) / (.5*(right - left))
  yn = (ynr - .5*(top + bottom)) / (.5*(top - bottom))
  zn = (ze - .5*(zfar + znear)) / (.5*(zfar - znear))
  
  return (xn, yn, zn)

# -----------------------------------------------------------------------------
#
def normalzed_screen_to_xyz_coordinates(xy_n, z, view):

  xn, yn = xy_n

  #
  # Projection matrix maps window lower left and upper right corners to near
  # clip plane corners (left, bottom, -znear), (right, top, -znear).
  #
  c = chimera.viewer.camera
  left, right, bottom, top, znear, zfar, f = c.window(view)

  xe1 = .5 * (left + right) + .5 * xn * (right - left)
  ye1 = .5 * (top + bottom) + .5 * yn * (top - bottom)
  ze1 = -znear

  if c.ortho:
    xe2 = xe1
    ye2 = ye1
  else:
    zratio = zfar / znear
    xe2 = zratio * xe1
    ye2 = zratio * ye1
  ze2 = -zfar

  #
  # Shift by eye position.
  #
  ex, ey, ez = c.eyePos(view)

  xs1 = xe1 + ex
  ys1 = ye1 + ey
  zs1 = ze1 + ez

  xs2 = xe2 + ex
  ys2 = ye2 + ey
  zs2 = ze2 + ez

  xyz_near = (xs1, ys1, zs1)
  xyz_far = (xs2, ys2, zs2)

  f2 = float(z - zs1) / (zs2 - zs1)
  f1 = 1 - f2
  xyz = map(lambda c1, c2, f1=f1, f2=f2: f1*c1 + f2*c2, xyz_near, xyz_far)
  xyz = tuple(xyz)
  
  return xyz
  
# -----------------------------------------------------------------------------
#
def clip_plane_positions():

  c = chimera.viewer.camera
  view = 0
  left, right, bottom, top, znear, zfar, f = c.window(view)
  ex, ey, ez = c.eyePos(view)
  return ez - znear, ez - zfar
  
# -----------------------------------------------------------------------------
#
def chimera_color(rgb):

  return chimera.MaterialColor(*rgb)
  
# -----------------------------------------------------------------------------
#
def background_color():

  from chimera import preferences
  from chimera import bgprefs
  rgba = preferences.get(bgprefs.BACKGROUND, bgprefs.BG_COLOR)
  if not rgba:
    rgba = (0,0,0,1)
  rgb = rgba[:3]
  return chimera_color(rgb)
  
# -----------------------------------------------------------------------------
#
def float_variable_value(v, default = None):

  try:
    return float(v.get())
  except:
    return default
  
# -----------------------------------------------------------------------------
#
def scale_bar_dialog(create = 0):

  from chimera import dialogs
  return dialogs.find(Scalebar_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_scale_bar():

  from chimera import dialogs
  return dialogs.display(Scalebar_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Scalebar_Dialog.name, Scalebar_Dialog, replace = 1)
