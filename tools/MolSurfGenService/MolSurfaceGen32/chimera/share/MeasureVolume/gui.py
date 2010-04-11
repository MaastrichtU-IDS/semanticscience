# -----------------------------------------------------------------------------
# Dialog for computing volume enclosed by a surface and surface area.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Surface_Volume_Dialog(ModelessDialog):

  title = 'Measure Volume and Area'
  name = 'measure volume'
  buttons = ('Update', 'Close',)
  help = 'ContributedSoftware/measurevol/measurevol.html'
  
  def fillInUI(self, parent):

    self.surface_change_handler = None

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()

    parent.columnconfigure(0, weight=1)
    row = 0

    import Tkinter
    from CGLtk import Hybrid
    from chimera import widgets

    from MeasureVolume import surface_models
    sm = widgets.ModelOptionMenu(parent, labelpos = 'w',
                                 label_text = 'Surface ',
                                 listFunc = surface_models,
                                 command = self.surface_menu_cb)
    sm.grid(row = row, column = 0, sticky = 'w')
    self.surface_menu = sm
    row = row + 1

    ve = Hybrid.Entry(parent, 'Volume = ', 20)
    ve.entry.configure(relief = Tkinter.FLAT, state = 'readonly',
                       highlightthickness = 0)
    ve.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.volume = ve.variable

    ae = Hybrid.Entry(parent, 'Area = ', 20)
    ae.entry.configure(relief = Tkinter.FLAT, state = 'readonly',
                       highlightthickness = 0)
    ae.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.area = ae.variable

    au = Hybrid.Checkbutton(parent, 'Update automatically', True)
    au.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.autoupdate = au.variable
    au.callback(self.update_switch_cb)

    # Set menu to a displayed surface.
    surfs = filter(lambda sm: sm.display, surface_models())
    if surfs:
      self.surface_menu.setvalue(surfs[0])
    
  # ---------------------------------------------------------------------------
  # Turn off surface change tracking when dialog not displayed.
  #
  def map(self, event = None):
    self.compute_volume_and_area()
    self.register_auto_update()
  def unmap(self, event = None):
    self.register_auto_update()
    
  # ---------------------------------------------------------------------------
  #
  def surface_menu_cb(self, text = None):

    surface = self.surface_menu.getvalue()
    if surface == None:
      return

    if self.autoupdate.get() and self.isVisible():
      self.compute_volume_and_area()
    else:
      self.volume.set('')
      self.area.set('')

    self.register_auto_update()

  # ---------------------------------------------------------------------------
  #
  def update_switch_cb(self):

    self.register_auto_update()
    if self.autoupdate.get():
      self.compute_volume_and_area()

  # ---------------------------------------------------------------------------
  # Register handler to detect surface geometry changes.
  #
  def register_auto_update(self):

    if self.autoupdate.get() and self.isVisible():
      surface = self.surface_menu.getvalue()
    else:
      surface = None
    self.track_surface_changes(surface)
            
  # --------------------------------------------------------------------------
  #
  def track_surface_changes(self, surface):

    from _surface import SurfaceModel
    if isinstance(surface, SurfaceModel):
      if self.surface_change_handler is None:
        from chimera import triggers as t
        h = t.addHandler('SurfacePiece', self.surface_changed_cb, None)
        self.surface_change_handler = h
    elif self.surface_change_handler:
      from chimera import triggers as t
      t.deleteHandler('SurfacePiece', self.surface_change_handler)
      self.surface_change_handler = None

    # TODO: Doesn't update when surface piece deleted.

  # --------------------------------------------------------------------------
  #
  def surface_changed_cb(self, trigger_name, unused, tdata):

    if 'geometry changed' in tdata.reasons:
      surface = self.surface_menu.getvalue()
      modsurfs = set([p.model for p in tdata.modified])
      if surface in modsurfs:
        self.compute_volume_and_area()

  # ---------------------------------------------------------------------------
  #
  def Update(self):

    self.compute_volume_and_area()
    
  # ---------------------------------------------------------------------------
  #
  def compute_volume_and_area(self):

    surface = self.surface_menu.getvalue()
    if surface == None:
      return
    
    import MeasureVolume
    volume, area, hole_count = MeasureVolume.surface_volume_and_area(surface)
    if volume == None:
      vstr = 'N/A (non-oriented surface)'
    else:
      vstr = engineering_notation(volume, 4)
      if hole_count > 0:
        vstr += ' (%d holes)' % hole_count

    astr = engineering_notation(area, 4)

    self.volume.set(vstr)
    self.area.set(astr)

    msg = ('Surface %s (%s): volume = %s, area = %s\n'
           % (surface.name, surface.oslIdent(), vstr, astr))
    from chimera import replyobj
    replyobj.info(msg)

# -----------------------------------------------------------------------------
#
def engineering_notation(value, precision):

  from decimal import Decimal
  format = '%%#.%dg' % precision
  e = Decimal(format % value).to_eng_string()
  e = e.replace('E', 'e')
  e = e.replace('e+', 'e')
  return e
  
# -----------------------------------------------------------------------------
#
def surface_volume_dialog(create = 0):

  from chimera import dialogs
  return dialogs.find(Surface_Volume_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_surface_volume_dialog():

  from chimera import dialogs
  return dialogs.display(Surface_Volume_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Surface_Volume_Dialog.name, Surface_Volume_Dialog, replace = 1)
