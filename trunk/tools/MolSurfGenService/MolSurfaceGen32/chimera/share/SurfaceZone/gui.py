# -----------------------------------------------------------------------------
# Dialog for showing piece of surface near selected atoms.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Surface_Zone_Dialog(ModelessDialog):

  title = 'Surface Zone'
  name = 'surface zone'
  buttons = ('Zone', 'No Zone', 'Close',)
  help = 'ContributedSoftware/surfzone/surfzone.html'
  
  def fillInUI(self, parent):

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()
    
    row = 0

    import Tkinter
    from CGLtk import Hybrid
    from chimera import widgets

    from SurfaceZone import zonable_surface_models
    sm = widgets.ModelOptionMenu(parent, labelpos = 'w',
                                 label_text = 'Surface ',
                                 listFunc = zonable_surface_models,
                                 command = self.surface_menu_cb)

    sm.grid(row = row, column = 0, sticky = 'w')
    self.surface_menu = sm
    row = row + 1

    rs = Hybrid.Scale(parent, 'Radius ', 0, 30, .1, 2)
    rs.frame.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    rs.callback(self.radius_changed_cb)
    rs.entry.bind('<KeyPress-Return>', self.radius_changed_cb)
    self.radius = rs
    
    #
    # Specify a label width so dialog is not resized for long messages.
    #
    msg = Tkinter.Label(parent, width = 40, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.message_label = msg

    self.surface_menu_cb()      # Set slider for current surface
    
  # ---------------------------------------------------------------------------
  #
  def message(self, text):

    self.message_label['text'] = text
    self.message_label.update_idletasks()
    
  # ---------------------------------------------------------------------------
  #
  def surface_menu_cb(self, text = None):

    surface = self.chosen_surface()
    if surface == None:
      return

    import SurfaceZone
    if SurfaceZone.showing_zone(surface):
      points, radius = SurfaceZone.zone_points_and_distance(surface)
      self.radius.set_value(radius, invoke_callbacks = False)

  # ---------------------------------------------------------------------------
  #
  def Zone(self):

    self.zone_cb()

  # ---------------------------------------------------------------------------
  #
  def NoZone(self):

    self.no_zone_cb()

  # ---------------------------------------------------------------------------
  #
  def radius_changed_cb(self, event = None):

    surface = self.chosen_surface()
    if surface == None:
        return

    import SurfaceZone
    if SurfaceZone.showing_zone(surface):
      points, radius = SurfaceZone.zone_points_and_distance(surface)
      radius = self.radius_from_gui()
      if radius != None and len(points) > 0:
        SurfaceZone.surface_zone(surface, points, radius, auto_update = True)
    
  # ---------------------------------------------------------------------------
  #
  def zone_cb(self, event = None):

    self.message('')

    surface = self.chosen_surface()
    if surface == None:
      self.message('Select a surface')
      return

    radius = self.radius_from_gui()
    if radius == None:
      return

    from chimera import selection
    atoms = selection.currentAtoms()
    bonds = selection.currentBonds()

    from SurfaceZone import path_points, surface_zone
    points = path_points(atoms, bonds, surface.openState.xform.inverse())
    if len(points) > 0:
      surface_zone(surface, points, radius, auto_update = True)
    else:
      self.message('No atoms are selected')
      
  # ---------------------------------------------------------------------------
  #
  def radius_from_gui(self):

    radius = self.radius.value()
    if radius == None:
      self.message('Radius is set to a non-numeric value')
      return None
    else:
      self.message('')
    return radius
      
  # ---------------------------------------------------------------------------
  #
  def no_zone_cb(self, event = None):

    surface = self.chosen_surface()
    if surface == None:
        self.message('Select a surface')
        return

    import SurfaceZone
    SurfaceZone.no_surface_zone(surface)
      
  # ---------------------------------------------------------------------------
  #
  def chosen_surface(self):

    sm = self.surface_menu
    surface = sm.getvalue()
    return surface

# -----------------------------------------------------------------------------
#
def surface_zone_dialog(create = 0):

  from chimera import dialogs
  return dialogs.find(Surface_Zone_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_surface_zone_dialog():

  from chimera import dialogs
  return dialogs.display(Surface_Zone_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Surface_Zone_Dialog.name, Surface_Zone_Dialog, replace = 1)
