# -----------------------------------------------------------------------------
# Dialog for coloring piece of surface near selected atoms.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Color_Zone_Dialog(ModelessDialog):

  title = 'Color Zone'
  name = 'color zone'
  buttons = ('Color', 'Uncolor', 'Split Map', 'Close',)
  help = 'ContributedSoftware/colorzone/colorzone.html'
  
  def fillInUI(self, parent):

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()

    parent.columnconfigure(0, weight=1)         # Allow scalebar to expand.
    
    row = 0

    import Tkinter
    from CGLtk import Hybrid
    from chimera import widgets

    import ColorZone
    sm = widgets.ModelOptionMenu(parent, labelpos = 'w',
                                 label_text = 'Surface ',
                                 listFunc = ColorZone.zonable_surface_models,
                                 command = self.surface_menu_cb)
    sm.grid(row = row, column = 0, sticky = 'w')
    self.surface_menu = sm
    row = row + 1

    rs = Hybrid.Scale(parent, 'Coloring radius ', 0, 30, .1, 2)
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

    # Set slider range.
    has_box, box = surface.bbox()
    if has_box:
      r = (box.urb - box.llf).length
      rv = self.radius
      rv.set_range(0, r)
      if rv.value() > r:
        rv.set_value(0.5*r, invoke_callbacks = False)

    # Show currently used coloring radius.
    import ColorZone
    if ColorZone.coloring_zone(surface):
      points, colors, radius = \
          ColorZone.zone_points_colors_and_distance(surface)
      self.radius.set_value(radius, invoke_callbacks = False)
      
  # ---------------------------------------------------------------------------
  #
  def Color(self):

    self.color_zone_cb()

  # ---------------------------------------------------------------------------
  #
  def Uncolor(self):

    self.uncolor_zone_cb()

  # ---------------------------------------------------------------------------
  #
  def SplitMap(self):

    surface = self.chosen_surface()
    if surface == None:
      return

    from VolumeViewer import Volume
    if not isinstance(surface, Volume):
      self.message('%s is not a map' % surface.name)
      return

    import ColorZone
    if ColorZone.split_volume_by_color_zone(surface) is None:
      self.message('%s has no color zone' % surface.name)

  # ---------------------------------------------------------------------------
  #
  def radius_changed_cb(self, event = None):

    surface = self.chosen_surface()
    if surface == None:
        return

    import ColorZone
    if ColorZone.coloring_zone(surface):
      points, colors, old_radius = \
          ColorZone.zone_points_colors_and_distance(surface)
      radius = self.radius_from_gui()
      if radius != None:
        ColorZone.color_zone(surface, points, colors, radius,
                             auto_update = True)
    
  # ---------------------------------------------------------------------------
  #
  def color_zone_cb(self, event = None):

    self.message('')

    surface = self.chosen_surface()
    if surface == None:
      self.message('Select a surface')
      return

    radius = self.radius_from_gui()
    if radius == None:
      return

    xform_to_surface = surface.openState.xform.inverse()

    from chimera import selection
    atoms = selection.currentAtoms()
    bonds = selection.currentBonds()
    from ColorZone import points_and_colors, color_zone
    points, colors = points_and_colors(atoms, bonds, xform_to_surface)
    if len(points) > 0:
      color_zone(surface, points, colors, radius, auto_update = True)
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
  def uncolor_zone_cb(self, event = None):

    surface = self.chosen_surface()
    if surface == None:
        self.message('Select a surface')
        return

    import ColorZone
    ColorZone.uncolor_zone(surface)
      
  # ---------------------------------------------------------------------------
  #
  def chosen_surface(self):

    sm = self.surface_menu
    surface = sm.getvalue()
    return surface
  
# -----------------------------------------------------------------------------
#
def color_zone_dialog(create = 0):

  from chimera import dialogs
  return dialogs.find(Color_Zone_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_color_zone_dialog():

  from chimera import dialogs
  return dialogs.display(Color_Zone_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Color_Zone_Dialog.name, Color_Zone_Dialog, replace = 1)
