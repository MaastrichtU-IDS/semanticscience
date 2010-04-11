# -----------------------------------------------------------------------------
# Dialog for showing flattened icosahedral multiscale virus model.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Flatten_Icosahedron_Dialog(ModelessDialog):

  title = 'Flatten Icosahedron'
  name = 'flatten icosahedron'
  buttons = ('Flatten', 'Unflatten', 'Close',)
  help = 'ContributedSoftware/flatten/flatten.html'
  
  def fillInUI(self, parent):
    
    t = parent.winfo_toplevel()
    self.toplevel_widget = t
    t.withdraw()

    parent.columnconfigure(0, weight = 1)
    row = 0

    import Tkinter
    from CGLtk import Hybrid

    rs = Hybrid.Scale(parent, ' Radius ', 0, 1000, .1, '')
    rs.frame.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
#    rs.callback(self.flatten_cb)
    rs.entry.bind('<KeyPress-Return>', self.flatten_cb)
    self.radius = rs.variable

    # Mesh
    mf = Tkinter.Frame(parent)
    mf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    sm = Hybrid.Checkbutton(mf, 'Show triangle mesh,', True)
    sm.button.grid(row = 0, column = 0, sticky = 'w')
    self.show_mesh = sm.variable
    self.show_mesh.add_callback(self.show_mesh_cb)

    cl = Tkinter.Label(mf, text = 'color')
    cl.grid(row = 0, column = 1, sticky = 'w')
    
    initial_color = (.5,.5,.5,1)
    from CGLtk.color import ColorWell
    mc = ColorWell.ColorWell(mf, callback = self.mesh_color_changed_cb)
    mc.grid(row = 0, column = 2, sticky = 'w')
    self.mesh_color = mc
    mc.showColor(initial_color)

    mo = Hybrid.Entry(mf, ' z offset ', 5, '0')
    mo.frame.grid(row = 0, column = 3, sticky = 'w')
    self.mesh_offset = mo.variable
    mo.entry.bind('<KeyPress-Return>', self.mesh_offset_changed_cb)

    # Orthographic camera mode.
    import chimera
    c = chimera.viewer.camera
    oc = Hybrid.Checkbutton(parent, 'Use orthographic camera mode.', c.ortho)
    oc.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.orthographic = oc.variable
    self.orthographic.add_callback(self.orthographic_cb)

    #
    # Specify a label width so dialog is not resized for long messages.
    #
    msg = Tkinter.Label(parent, width = 40, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.message_label = msg
    
  # ---------------------------------------------------------------------------
  #
  def message(self, text):

    self.message_label['text'] = text
    self.message_label.update_idletasks()

  # ---------------------------------------------------------------------------
  #
  def Flatten(self):

    self.flatten_cb()

  # ---------------------------------------------------------------------------
  #
  def Unflatten(self):

    self.unflatten_cb()

  # ---------------------------------------------------------------------------
  #
  def flatten_cb(self, event = None):

    self.Unflatten()
    self.message('')
    import FlattenIcosahedron
    mlist = FlattenIcosahedron.multiscale_models()
    from CGLtk import Hybrid
    r = Hybrid.float_variable_value(self.radius)
    if r == None:
      r = FlattenIcosahedron.model_radius(mlist)
      if r != None:
        self.radius.set(r)
    elif r <= 0:
      self.message('Radius must be greater than 0.')
      return
    if r != None:
      FlattenIcosahedron.flatten_icosahedron(mlist, r)
      if self.show_mesh.get() and mlist:
        rgba = self.mesh_color.rgba
        zoffset = Hybrid.float_variable_value(self.mesh_offset, 0)
        self.show_triangle_mesh(mlist[0].surface_model(), r, rgba, zoffset)
    
  # ---------------------------------------------------------------------------
  #
  def unflatten_cb(self):

    import FlattenIcosahedron
    mlist = FlattenIcosahedron.multiscale_models()
    FlattenIcosahedron.unflatten_icosahedron(mlist)

    self.unshow_triangle_mesh()

  # ---------------------------------------------------------------------------
  #
  def show_mesh_cb(self, arg = None):

    if self.show_mesh.get():
      self.flatten_cb()
    else:
      self.unshow_triangle_mesh()
      
  # ---------------------------------------------------------------------------
  #
  def mesh_color_changed_cb(self, event = None):

    p = self.mesh_surface_piece()
    if p:
      rgba = self.mesh_color.rgba
      p.color = rgba
      
  # ---------------------------------------------------------------------------
  #
  def mesh_offset_changed_cb(self, event = None):

    p = self.mesh_surface_piece()
    if p:
      varray, tarray = p.geometry
      from CGLtk import Hybrid
      mesh_offset = Hybrid.float_variable_value(self.mesh_offset, 0)
      varray[:,2] = mesh_offset
      p.geometry = varray, tarray

  # ---------------------------------------------------------------------------
  #
  def orthographic_cb(self, arg = None):

    import chimera
    c = chimera.viewer.camera
    c.ortho = self.orthographic.get()
    
  # ---------------------------------------------------------------------------
  #
  def show_triangle_mesh(self, model, radius, rgba, zoffset):

    import FlattenIcosahedron
    varray, tarray = FlattenIcosahedron.flattened_icosahedron_geometry(radius)
    varray[:,2] = zoffset
    
    if hasattr(model, 'flattened_icosahedron_mesh'):
      g = model.flattened_icosahedron_mesh
      g.set_geometry(varray, tarray)
    else:
      g = model.addPiece(varray, tarray, rgba)
      g.displayStyle = g.Mesh
      model.flattened_icosahedron_mesh = g
    
  # ---------------------------------------------------------------------------
  #
  def unshow_triangle_mesh(self):

    p = self.mesh_surface_piece()
    if p:
      sm = p.model
      sm.removePiece(p)
      del sm.flattened_icosahedron_mesh
      
  # ---------------------------------------------------------------------------
  #
  def mesh_surface_piece(self):

    import FlattenIcosahedron
    mlist = FlattenIcosahedron.multiscale_models()
    for m in mlist:
      sm = m.surface_model()
      if hasattr(sm, 'flattened_icosahedron_mesh'):
        g = sm.flattened_icosahedron_mesh
        return g
    return None

# -----------------------------------------------------------------------------
#
def flatten_icosahedron_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Flatten_Icosahedron_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_flatten_icosahedron_dialog():

  from chimera import dialogs
  return dialogs.display(Flatten_Icosahedron_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Flatten_Icosahedron_Dialog.name, Flatten_Icosahedron_Dialog,
                 replace = True)
