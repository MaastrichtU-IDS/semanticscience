# -----------------------------------------------------------------------------
# Dialog for hiding small blobs of surfaces based on a size threshold.
#
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Dust_Dialog(ModelessDialog):

  title = 'Hide Dust'
  name = 'hide dust'
  buttons = ('Hide', 'Unhide', 'Options', 'Close',)
  help = 'ContributedSoftware/volumeviewer/hidedust.html'
  
  def fillInUI(self, parent):

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()

    parent.columnconfigure(0, weight=1)

    row = 0

    import Tkinter
    from CGLtk import Hybrid
    from chimera import widgets

    from Surface import surface_models
    sm = widgets.ModelOptionMenu(parent, labelpos = 'w',
                                 label_text = 'Surface ',
                                 listFunc = surface_models,
                                 command = self.surface_menu_cb)
    sm.grid(row = row, column = 0, sticky = 'w')
    self.surface_menu = sm
    row += 1

    ls = Hybrid.Logarithmic_Scale(parent, 'Size ', 1, 1000, 100,
                                  entry_width = 8)
    ls.frame.grid(row = row, column = 0, sticky = 'ew')
    row += 1
    ls.callback(self.limit_changed_cb)
    ls.entry.bind('<KeyPress-Return>', self.limit_changed_cb)
    self.limit = ls

    op = Hybrid.Popup_Panel(parent)
    opf = op.frame
    opf.grid(row = row, column = 0, sticky = 'news')
    opf.grid_remove()
    opf.columnconfigure(0, weight=1)
    self.options_panel = op.panel_shown_variable
    row += 1
    orow = 0

    cb = op.make_close_button(opf)
    cb.grid(row = orow, column = 1, sticky = 'e')

    mo = Hybrid.Option_Menu(opf, 'Hide small blobs based on ',
                            'size', 'rank', 'volume')
    mo.frame.grid(row = orow, column = 0, sticky = 'w')
    row += 1
    mo.add_callback(self.method_changed_cb)
    self.method = mo.variable
    
    # Specify a label width so dialog is not resized for long messages.
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
    if surface is None:
      return

    import dust
    if dust.hiding_dust(surface):
      method, limit = dust.dust_limit(surface)
      self.method.set(method, invoke_callbacks = False)
      self.limit.set_value(limit, invoke_callbacks = False)

    self.set_scale_range()

  # ---------------------------------------------------------------------------
  #
  def set_scale_range(self):

    surface = self.chosen_surface()
    if surface is None:
      return

    l = self.limit
    m = self.method.get()
    if m == 'size' or m == 'volume':
      have_box, box = surface.bbox()
      if have_box:
        s = max((box.urb - box.llf).data())
        if s > 0:
          e = 1
          if m == 'volume':
            e = 3
          l.set_range((s/1000)**e, s**e)
      l.entry_format = '%.3g'
    else:
      l.set_range(1, 1000)
      l.entry_format = '%.0f'

  # ---------------------------------------------------------------------------
  #
  def Hide(self):

    self.hide_cb()

  # ---------------------------------------------------------------------------
  #
  def Unhide(self):

    self.unhide_cb()

  # ---------------------------------------------------------------------------
  #
  def method_changed_cb(self, event = None):

    self.limit.label['text'] = self.method.get().capitalize() + ' '
    self.set_scale_range()
    self.limit_changed_cb()

  # ---------------------------------------------------------------------------
  #
  def limit_changed_cb(self, event = None):

    surface = self.chosen_surface()
    if surface is None:
        return

    import dust
    if not dust.hiding_dust(surface):
      return

    limit = self.limit_from_gui()
    if limit != None:
      dust.hide_dust(surface, self.method.get(), limit, auto_update = True)
    
  # ---------------------------------------------------------------------------
  #
  def hide_cb(self, event = None):

    self.message('')

    surface = self.chosen_surface()
    if surface is None:
      self.message('Select a surface')
      return

    limit = self.limit_from_gui()
    if limit is None:
      return

    self.set_scale_range()
      
    import dust
    dust.hide_dust(surface, self.method.get(), limit, auto_update = True)

  # ---------------------------------------------------------------------------
  #
  def limit_from_gui(self):

    limit = self.limit.value()
    if limit is None:
      self.message('Limit is set to a non-numeric value')
      return None
    else:
      self.message('')
    return limit
      
  # ---------------------------------------------------------------------------
  #
  def unhide_cb(self, event = None):

    surface = self.chosen_surface()
    if surface is None:
        self.message('Select a surface')
        return

    import dust
    dust.unhide_dust(surface)
    
  # ---------------------------------------------------------------------------
  #
  def Options(self):

    self.options_panel.set(not self.options_panel.get())
      
  # ---------------------------------------------------------------------------
  #
  def chosen_surface(self):

    sm = self.surface_menu
    surface = sm.getvalue()
    return surface

# -----------------------------------------------------------------------------
#
def dust_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Dust_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_dust_dialog():

  from chimera import dialogs
  return dialogs.display(Dust_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Dust_Dialog.name, Dust_Dialog, replace = True)
