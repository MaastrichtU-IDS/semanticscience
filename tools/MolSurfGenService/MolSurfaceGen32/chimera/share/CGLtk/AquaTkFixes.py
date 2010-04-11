# ------------------------------------------------------------------------------
# Work around Aqua Tk 8.5.2 problems.
#

# ------------------------------------------------------------------------------
#
def balloonDontTakeFocus(widget):

  if widget.tk.call('tk', 'windowingsystem') == 'aqua':
    # Aqua Tk voodoo to make popup balloons not take focus.
    widget.tk.call('::tk::unsupported::MacWindowStyle',
                   'style', str(widget), 'help', 'none')

# ------------------------------------------------------------------------------
#
def raiseWindow(widget):

  t = widget.winfo_toplevel()
  aqua = (widget.tk.call('tk', 'windowingsystem') == 'aqua')
  if aqua:
    # tkraise() focuses window on aqua.  Avoid that.
    t.wm_attributes('-topmost', 1)
    t.wm_attributes('-topmost', 0)
  else:
    t.tkraise()

# ------------------------------------------------------------------------------
# Create a menubar that appears in a window in Aqua.  This can be used in
# addition to setting the toplevel -menu option which will place the menu
# at the top of the screen when the window has the focus.
#
# Browsing the menus by posting one menu then moving the mouse pointer over
# a different menu does not work.  Didn't find any way to implement that in
# Aqua Tk 8.5.2.  Don't get Enter/Leave window events.  Can poll to see what
# menu the pointer is over but there is no way to unpost the current menu.
# Menu.unpost() does nothing on the Mac.  Posting a second menu causes an
# error and leaves the first menu posted.  Also found no way to even determine
# when a menu is  still posted (by say a click on some other window).
# Tk mapped and viewable state is not accurate.
#
class WindowMenuBar:

  def __init__(self, menubar, parent, row = None, columnspan = 1, pack = None):

    self.menubar = menubar
    import Tkinter
    f = Tkinter.Frame(parent, borderwidth = 1, relief = 'groove')
    self.frame = f

    self.labels = []
    self.update_menus()

    if not row is None:
      f.grid(row = row, column = 0, columnspan = columnspan, sticky = 'ew')
    elif not pack is None:
      f.pack(side = 'top', fill = 'x', anchor = 'w')

  def update_menus(self):

    mb = self.menubar
    n = mb.index('end')
    f = self.frame
    f.columnconfigure(n+1, weight = 1)
    for i in range(1,n+1):      # Skip first menu = application menu
      name = mb.entrycget(i, 'label')
      if i-1 < len(self.labels):
        label = self.labels[i-1]
        label['text'] = name
      else:
        import Tkinter
        label = Tkinter.Label(f, text = name)
        f.columnconfigure(i, pad = 10)
        label.grid(row = 0, column = i, sticky = 'w')
        label.bind('<Enter>', lambda e, label=label: self.highlight_cb(label))
        label.bind('<Leave>', lambda e, label=label: self.unhighlight_cb(label))
        label.bind('<Any-ButtonPress>',
                   lambda e, label=label: self.post_menu_cb(label))
        self.labels.append(label)
      menu = mb.entrycget(i, 'menu')
      if menu and isinstance(menu, str):
        menu = mb.nametowidget(menu)
      label.menu = menu

    # Destroy extra menu entries.
    for label in self.labels[n:]:
      label.destroy()
    self.labels = self.labels[:n]

  def post_menu_cb(self, label):

    # Delay posting menu.  Without this if then menu title was clicked
    # while another Chimera dialog has the focus then the button release
    # after clicking a menu entry is not detected (nothing happens) until
    # the mouse is moved.  Bug #7898.
    label.after(1, lambda label=label: self.delayed_post(label))

  def delayed_post(self, label):

    if label.menu:
      x, y = label.winfo_rootx(), label.winfo_rooty() + label.winfo_height() + 3
      from _tkinter import TclError
      try:
        label.menu.post(x, y)
      except TclError:
        # Error is raised if another menu is already posted.
        # Apparently the mouse grab for the other menu was released before
        # unposting that menu.
        pass
    
  def highlight_cb(self, label):

    color = label.getvar('::tk::Palette(selectBackground)')
    label.configure(background = color)

  def unhighlight_cb(self, label):

    color =  self.frame['background']
    label.configure(background = color)

  def show(self, show):

    f = self.frame
    if show:
      if hasattr(self, 'grid_info'):
        f.grid()
      elif hasattr(self, 'pack_info'):
        pi = self.pack_info
        s = pi['in'].pack_slaves()
        if s:
          pi['before'] = s[0]
        f.pack(**pi)
    else:
      m = f.winfo_manager()
      if m == 'grid':
        self.grid_info = f.grid_info()
        f.grid_remove()
      elif m == 'pack':
        self.pack_info = f.pack_info()
        f.pack_forget()
