# -----------------------------------------------------------------------------
# Dialog for showing piece of surface near selected atoms.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Icosahedron_Dialog(ModelessDialog):

  title = 'Icosahedron Surface'
  name = 'icosahedron surface'
  buttons = ('Show', 'Remove', 'Close',)
  help = 'ContributedSoftware/icosahedron/icosahedron.html'
  
  def fillInUI(self, parent):

    self.default_radius = 100
    self.surface_model = None
    self.surface_piece = None
    
    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()
    parent.columnconfigure(0, weight = 1)
    
    row = 0

    import Tkinter
    from CGLtk import Hybrid

    # Radius
    rs = Hybrid.Scale(parent, 'Radius ', 1, 1000, 0.01, self.default_radius)
    rs.frame.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    rs.callback(self.radius_changed_cb)
    rs.entry.bind('<KeyPress-Return>', self.radius_changed_cb)
    self.radius = rs

    # Interpolation factor between icosahedron and sphere
    sf = Hybrid.Scale(parent, 'Sphere factor ', 0, 1, .01, 0)
    sf.frame.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    sf.callback(self.sphere_factor_changed_cb)
    sf.entry.bind('<KeyPress-Return>', self.sphere_factor_changed_cb)
    self.sphere_factor = sf
    
    # Orientation menu
    self.orient_222 = 'xyz 2-fold axes'
    self.orient_222r = 'xyz 2-fold axes, alt'
    self.orient_2n3 = 'x 2-fold, z 3-fold'
    self.orient_2n3r = 'x 2-fold, z 3-fold, alt'
    self.orient_2n5 = 'x 2-fold, z 5-fold'
    self.orient_2n5r = 'x 2-fold, z 5-fold, alt'
    self.orient_n25 = 'y 2-fold, z 5-fold'
    self.orient_n25r = 'y 2-fold, z 5-fold, alt'
    io = Hybrid.Option_Menu(parent, 'Orientation ',
                            self.orient_222, self.orient_222r,
                            self.orient_2n3, self.orient_2n3r,
                            self.orient_2n5, self.orient_2n5r,
                            self.orient_n25, self.orient_n25r)
    io.frame.grid(row = row, column = 0, sticky = 'w')
    io.add_callback(self.show_cb)
    row = row + 1
    self.orientation = io.variable

    # Subdivision factor
    sf = Tkinter.Frame(parent)
    sf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    sb = Hybrid.Entry(sf, 'Subdivision factor ', 5, '1')
    sb.frame.grid(row = 0, column = 0, sticky = 'w')
    self.subdivision_factor = sb.variable
    sb.entry.bind('<KeyPress-Return>', self.show_cb)

    sp = Tkinter.Label(sf, text = '')
    sp.grid(row = 0, column = 1, sticky = 'w')
    self.subdivision_spacing = sp
    
    # Surface style: filled, mesh
    st = Hybrid.Radiobutton_Row(parent, 'Surface style: ', ('solid', 'mesh'),
                                self.style_changed_cb)
    st.frame.grid(row = row, column = 0, sticky = 'w')
    st.variable.set('mesh', invoke_callbacks = False)
    row = row + 1
    self.surface_style = st.variable

    # Color
    cf = Tkinter.Frame(parent)
    cf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    cl = Tkinter.Label(cf, text = 'Color')
    cl.grid(row = 0, column = 0, sticky = 'w')

    initial_color = (.7,.7,.7,1)
    from CGLtk.color import ColorWell
    cw = ColorWell.ColorWell(cf, callback = self.color_changed_cb)
    cw.showColor(initial_color)
    cw.grid(row = 0, column = 1, sticky = 'w')
    self.color = cw
    
    #
    # Specify a label width so dialog is not resized for long messages.
    #
    msg = Tkinter.Label(parent, width = 40, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.message_label = msg

    import SimpleSession
    chimera.triggers.addHandler(SimpleSession.SAVE_SESSION,
				self.save_session_cb, None)

  # ---------------------------------------------------------------------------
  #
  def message(self, text):

    self.message_label['text'] = text
    self.message_label.update_idletasks()
    
  # ---------------------------------------------------------------------------
  #
  def save_session_cb(self, trigger, x, file):

    import session
    session.save_icosahedron_state(self, file)

  # ---------------------------------------------------------------------------
  #
  def Show(self):

    self.show_cb()

  # ---------------------------------------------------------------------------
  #
  def Remove(self):

    self.remove_cb()

  # ---------------------------------------------------------------------------
  #
  def radius_changed_cb(self, event = None):

    self.update_radii()

  # ---------------------------------------------------------------------------
  #
  def sphere_factor_changed_cb(self, event = None):

    self.update_radii()

  # ---------------------------------------------------------------------------
  #
  def update_radii(self):

    g = self.surface_piece
    if self.surface_piece == None:
      return
    
    radius = self.radius.value(self.default_radius)
    sphere_factor = self.sphere_factor.value(0)
    from Icosahedron import interpolate_icosahedron_with_sphere
    interpolate_icosahedron_with_sphere(g, radius, sphere_factor)

    self.subdivision_levels(radius, update_subdivision_spacing = True)
    
  # ---------------------------------------------------------------------------
  #
  def style_changed_cb(self, event = None):

    p = self.surface_piece
    if p is None:
      return

    if self.surface_style.get() == 'mesh':
      style = p.Mesh
    else:
      style = p.Solid
    p.displayStyle = style

  # ---------------------------------------------------------------------------
  #
  def color_changed_cb(self, event = None):

    p = self.surface_piece
    if p is None:
      return

    p.color = self.color.rgba
  
  # ---------------------------------------------------------------------------
  #
  def show_cb(self, event = None, model_id = None):

    radius = self.radius.value(self.default_radius)
    sphere_factor = self.sphere_factor.value(0)
    surface_style = self.surface_style.get()
    orientation = self.orientation_name()
    subdivision_levels = self.subdivision_levels(radius)

    if self.surface_model == None:
      import _surface
      sm = _surface.SurfaceModel()
      sm.name = 'Icosahedron'
      self.surface_model = sm
      import chimera
      chimera.addModelClosedCallback(sm, self.surface_closed_cb)
      self.surface_piece = None

    from Icosahedron import make_icosahedron_surface
    p = make_icosahedron_surface(radius, orientation, subdivision_levels,
                                 sphere_factor, surface_style, self.color.rgba,
                                 self.surface_model)
    
    if self.surface_piece:
      self.surface_model.removePiece(self.surface_piece)
    else:
      from chimera import openModels as om
      if model_id is None:
        id = subid = om.Default
      else:
        id, subid = model_id
      om.add([self.surface_model], baseId = id, subid = subid)

    self.surface_piece = p
  
  # ---------------------------------------------------------------------------
  #
  def orientation_name(self):

    t = {self.orient_222: '222',
         self.orient_222r: '222r',
         self.orient_2n3: '2n3',
         self.orient_2n3r: '2n3r',
         self.orient_2n5: '2n5',
         self.orient_2n5r: '2n5r',
         self.orient_n25: 'n25',
         self.orient_n25r: 'n25r'}
    orientation = t[self.orientation.get()]
    return orientation
  
  # ---------------------------------------------------------------------------
  #
  def subdivision_levels(self, radius, update_subdivision_spacing = True):
    
    from CGLtk import Hybrid
    subdivision_factor = Hybrid.float_variable_value(self.subdivision_factor,
                                                     1)
    if subdivision_factor <= 0:
      subdivision_factor = 1
      
    from math import log, pow
    subdivision_levels = max(0, int(round(log(subdivision_factor)/log(2))))

    if update_subdivision_spacing:
      import Icosahedron
      edge = radius * Icosahedron.icosahedron_edge_length()
      subdivision_spacing = edge / pow(2.0, subdivision_levels)
      self.subdivision_spacing['text'] = ' spacing %.3g' % subdivision_spacing

    return subdivision_levels
  
  # ---------------------------------------------------------------------------
  #
  def remove_cb(self, event = None):

    if self.surface_model:
      import chimera
      chimera.openModels.close([self.surface_model])
  
  # ---------------------------------------------------------------------------
  #
  def surface_closed_cb(self, event = None):

    self.surface_model = None
    self.surface_piece = None

# -----------------------------------------------------------------------------
#
def icosahedron_dialog(create = 0):

  from chimera import dialogs
  return dialogs.find(Icosahedron_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_icosahedron_dialog():

  from chimera import dialogs
  return dialogs.display(Icosahedron_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Icosahedron_Dialog.name, Icosahedron_Dialog, replace = 1)
