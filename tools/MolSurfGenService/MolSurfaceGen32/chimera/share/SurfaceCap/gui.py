# -----------------------------------------------------------------------------
# Dialog for controlling capping of surfaces.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Capper_Dialog(ModelessDialog):

  title = 'Surface Capping'
  name = 'surface capping'
  buttons = ('Close',)
  help = 'ContributedSoftware/surfcapper/surfcapper.html'

  def fillInUI(self, parent):

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()

    row = 0

    import Tkinter
    from CGLtk import Hybrid

    from surfcaps import capper
    c = capper()

    cp = Hybrid.Checkbutton(parent, 'Cap surfaces at clip planes',
                            c.caps_shown())
    cp.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.show_caps = cp.variable
    self.show_caps.add_callback(self.settings_changed_cb)

    ccf = Tkinter.Frame(parent)
    ccf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    ucc = Hybrid.Checkbutton(ccf, 'Use cap color ', not c.cap_color is None)
    ucc.button.grid(row = 0, column = 0, sticky = 'w')
    self.use_cap_color = ucc.variable
    self.use_cap_color.add_callback(self.settings_changed_cb)

    from CGLtk.color import ColorWell
    cc = ColorWell.ColorWell(ccf, callback = self.settings_changed_cb)
    self.cap_color = cc
    rgba = c.cap_color
    if rgba is None:
      rgba = (1,1,1,1)
    cc.showColor(rgba, doCallback = 0)
    cc.grid(row = 0, column = 1, sticky = 'w')

    cs = Hybrid.Radiobutton_Row(parent, 'Cap style: ', ('solid', 'mesh'),
                                self.settings_changed_cb)
    cs.frame.grid(row = row, column = 0, sticky = 'w')
    if c.mesh_style: style = 'mesh'
    else:            style = 'solid'
    cs.variable.set(style, invoke_callbacks = False)
    row = row + 1
    self.cap_style = cs.variable

    sf = Hybrid.Entry(parent, 'Mesh subdivision factor', 4,
                      '%g' % c.subdivision_factor)
    sf.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.subdivision_factor = sf.variable
    sf.entry.bind('<KeyPress-Return>', self.settings_changed_cb)

    cd = Hybrid.Entry(parent, 'Cap to clip plane distance', 5,
                      '%.3g' % c.cap_offset)
    cd.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.cap_offset = cd.variable
    cd.entry.bind('<KeyPress-Return>', self.settings_changed_cb)

    import SimpleSession
    chimera.triggers.addHandler(SimpleSession.SAVE_SESSION,
				self.save_session_cb, None)
    
    chimera.replyobj.status("Capping surfaces might reduce responsiveness",
      color="orange red")
    
  # ---------------------------------------------------------------------------
  #
  def save_session_cb(self, trigger, x, file):

    import session
    session.save_capper_state(self, file)

  # ---------------------------------------------------------------------------
  #
  def settings_changed_cb(self, event = None):

    cap = self.show_caps.get()
    from surfcaps import capper
    c = capper()
    if cap:
      if self.use_cap_color.get():
        color = self.cap_color.rgba
      else:
        color = None
      c.set_cap_color(color)
      c.set_style(self.cap_style.get() == 'mesh')
      from CGLtk import Hybrid      
      sf = Hybrid.float_variable_value(self.subdivision_factor, 1.0)
      c.set_subdivision_factor(sf)
      cap_offset = Hybrid.float_variable_value(self.cap_offset,
                                               c.default_cap_offset)
      c.set_cap_offset(cap_offset)
      c.show_caps()
    else:
      c.unshow_caps()
  
# -----------------------------------------------------------------------------
#
def capper_dialog(create = 0):

  from chimera import dialogs
  return dialogs.find(Capper_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_capper_dialog():

  from chimera import dialogs
  return dialogs.display(Capper_Dialog.name)
  
# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Capper_Dialog.name, Capper_Dialog, replace = 1)
