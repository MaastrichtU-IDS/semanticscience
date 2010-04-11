# -----------------------------------------------------------------------------
# Dialog for erasing parts of volume data inside a sphere.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Volume_Eraser_Dialog(ModelessDialog):

  title = 'Volume Eraser'
  name = 'volume eraser'
  buttons = ('Erase', 'Close',)
  help = 'ContributedSoftware/voleraser/voleraser.html'
  
  def fillInUI(self, parent):

    self.default_radius = 1
    self.default_color = (1,0.6,0.8,.5)      # Pink eraser
    
    t = parent.winfo_toplevel()
    self.toplevel_widget = t
    t.withdraw()

    parent.columnconfigure(0, weight = 1)
    row = 0

    import Tkinter
    from CGLtk import Hybrid

    sh = Hybrid.Checkbutton(parent, 'Show volume-erasing sphere ', True)
    sh.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.show_sphere_var = sh.variable
    sh.callback(self.show_sphere_cb)

    crf = Tkinter.Frame(parent)
    crf.grid(row = row, column = 0, sticky = 'ew')
    crf.columnconfigure(2, weight = 1)
    row = row + 1

    cl = Tkinter.Label(crf, text = 'Color')
    cl.grid(row = 0, column = 0, sticky = 'w')
    
    from CGLtk.color import ColorWell
    sc = ColorWell.ColorWell(crf, color = self.default_color,
                             callback = self.change_sphere_color_cb)
    sc.grid(row = 0, column = 1, sticky = 'w')
    self.sphere_color = sc

    rs = Hybrid.Scale(crf, ' Radius ', 0, 30, .1, 2)
    rs.frame.grid(row = 0, column = 2, sticky = 'ew')
    row = row + 1
    rs.callback(self.change_radius_cb)
    rs.entry.bind('<KeyPress-Return>', self.change_radius_cb)
    self.sphere_radius_scale = rs
    
    mmf = Tkinter.Frame(parent)
    mmf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    mb = Hybrid.Option_Menu(mmf, 'Use mouse ',
                            'button 1', 'button 2', 'button 3',
                            'ctrl button 1', 'ctrl button 2', 'ctrl button 3')
    mb.variable.set('button 2')
    mb.frame.grid(row = 0, column = 0, sticky = 'w')
    mb.add_callback(self.bind_mouse_button_cb)
    self.mouse_button = mb

    mbl = Tkinter.Label(mmf, text = ' to move sphere')
    mbl.grid(row = 0, column = 1, sticky = 'w')

    ka = Tkinter.Label(parent, text = 'Erase using keyboard accelerator "es".')
    ka.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    from Accelerators import add_accelerator
    add_accelerator('es', 'Erase volume data inside sphere', self.Erase)
    add_accelerator('eo', 'Erase volume data outside sphere',
                    self.erase_outside_sphere)
    
  # ---------------------------------------------------------------------------
  #
  def enter(self):

    # Show eraser sphere when dialog is displayed.
    self.show_sphere_var.set(True)
    ModelessDialog.enter(self)
    
  # ---------------------------------------------------------------------------
  #
  def Close(self):

    # Remove eraser sphere when dialog is closed.
    self.show_sphere_var.set(False)
    ModelessDialog.Close(self)

  # ---------------------------------------------------------------------------
  #
  def Erase(self):

    self.erase_inside_sphere()

  # ---------------------------------------------------------------------------
  #
  def erase_inside_sphere(self):
    
    m = self.marker_sphere()
    if m == None:
      return
    
    import VolumeEraser
    VolumeEraser.zero_volume_inside_atom(m.atom)

  # ---------------------------------------------------------------------------
  #
  def erase_outside_sphere(self):
    
    m = self.marker_sphere()
    if m == None:
      return
    
    import VolumeEraser
    VolumeEraser.zero_volume_outside_atom(m.atom)

  # ---------------------------------------------------------------------------
  #
  def show_sphere_cb(self):

    self.show_sphere(self.show_sphere_var.get())

  # ---------------------------------------------------------------------------
  #
  def show_sphere(self, show):

    if show:
      d = volume_path_dialog()
      d.place_markers_on_spots.set(False)
      d.place_markers_on_planes.set(False)
      d.place_markers_outside_data.set(False)
      d.move_markers.set(True)
      self.set_radius_for_volume_data()
      m = self.marker_sphere(create = True)
      m.marker_set.show_markers(True)
    else:
      self.remove_marker_sphere()

    self.bind_mouse_button(show) # Turn mouse binding on or off

  # ---------------------------------------------------------------------------
  #
  def marker_sphere(self, create = False):

    marker_set = self.marker_set(create)

    if (hasattr(marker_set, 'eraser_marker') and
        marker_set.eraser_marker.atom == None):
      delattr(marker_set, 'eraser_marker')    # Marker was deleted

    if hasattr(marker_set, 'eraser_marker'):
      m = marker_set.eraser_marker
    elif create:
      rgba = self.sphere_color.rgba
      radius = self.sphere_radius(self.default_radius)
      xyz = self.initial_sphere_position(marker_set, radius)
      m = marker_set.place_marker(xyz, rgba, radius)
      marker_set.eraser_marker = m
    else:
      m = None

    return m

  # ---------------------------------------------------------------------------
  # Want to place it in volume but make sure it is visible.
  #
  def initial_sphere_position(self, marker_set, radius):

    eye_xyz = front_of_volume_at_screen_center()
    if eye_xyz == None:
      eye_xyz = screen_center_at_near_clip_plane()
      
    eye_xyz.z -= radius

    xform = marker_set.transform()
    xform.invert()
    xyz = xform.apply(eye_xyz)
    return xyz

  # ---------------------------------------------------------------------------
  #
  def marker_set(self, create = False):

    import VolumePath as vp
    marker_set = vp.find_marker_set_by_name('Volume eraser')
    if marker_set == None and create:
      marker_set = vp.Marker_Set('Volume eraser')
    return marker_set

  # ---------------------------------------------------------------------------
  #
  def remove_marker_sphere(self):

    ms = self.marker_set()
    if ms:
      ms.close()
    
  # ---------------------------------------------------------------------------
  #
  def change_sphere_color_cb(self, rgba):

    ms = self.marker_sphere()
    if ms:
      ms.set_rgba(rgba)

  # ---------------------------------------------------------------------------
  #
  def change_radius_cb(self, event = None):

    radius = self.sphere_radius()
    if radius == None:
      return

    ms = self.marker_sphere()
    if ms:
      ms.set_radius(radius)
      
  # ---------------------------------------------------------------------------
  #
  def sphere_radius(self, default_radius = None):

    radius = self.sphere_radius_scale.value()
    if radius == None or radius <= 0:
      radius = default_radius
    return radius

  # ---------------------------------------------------------------------------
  #
  def set_radius_for_volume_data(self):

    dr = active_volume()
    if dr == None:
      return
    
    xyz_min, xyz_max = dr.xyz_bounds()
    xyz_size = map(lambda a,b: a-b, xyz_max, xyz_min)
    size = max(xyz_size)

    rs = self.sphere_radius_scale
    rs.set_range(0, size)
    rs.set_value(.1 * size)
    
  # ---------------------------------------------------------------------------
  #
  def bind_mouse_button_cb(self):

    self.bind_mouse_button(self.show_sphere_var.get())
    
  # ---------------------------------------------------------------------------
  #
  def bind_mouse_button(self, bind):

    d = volume_path_dialog()
    mbp = d.mouse_button_panel
    if bind:
      bname = self.mouse_button.variable.get()
      mbp.placement_button.variable.set(bname)
    mbp.use_mouse.set(bind)
    
# -----------------------------------------------------------------------------
#
def active_volume():
  
  from VolumeViewer import active_volume
  return active_volume()

# -----------------------------------------------------------------------------
#
def front_of_volume_at_screen_center():
  
  v = active_volume()
  if v == None:
    return None

  import chimera
  wx_size, wy_size = chimera.viewer.windowSize

  from VolumeViewer.slice import volume_segment
  xyz_in, xyz_out, shown = volume_segment(v, wx_size/2, wy_size/2)

  if xyz_in == None:
    return None

  xf = v.model_transform()
  eye_xyz_in = xf.apply(chimera.Point(*xyz_in))

  return eye_xyz_in
  
# -----------------------------------------------------------------------------
#
def screen_center_at_near_clip_plane():

  import chimera
  c = chimera.viewer.camera
  cx, cy, cz = c.center
  n, f = c.nearFar
  center = chimera.Point(cx, cy, n)
  return center

# -----------------------------------------------------------------------------
#
def volume_path_dialog():

  import VolumePath
  d = VolumePath.volume_path_dialog(create = True)
  return d

# -----------------------------------------------------------------------------
#
def volume_eraser_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Volume_Eraser_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_volume_eraser_dialog():

  from chimera import dialogs
  return dialogs.display(Volume_Eraser_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Volume_Eraser_Dialog.name, Volume_Eraser_Dialog, replace = 1)
