# -----------------------------------------------------------------------------
# Common combinations of Tk widgets.
#
import math
import Tkinter

# -----------------------------------------------------------------------------
# Entry with a label on left.
#
class Entry:

  def __init__(self, parent, title, width, initial = None, suffix = None,
               browse = False):

    f = Tkinter.Frame(parent)
    f.columnconfigure(1, weight = 1)
    self.frame = f
    
    t = Tkinter.Label(f, text = title)
    t.grid(row = 0, column = 0, sticky = 'w')

    v = StringVariable(f)
    if initial != None:
      v.set(initial)
    self.variable = v
    e = Tkinter.Entry(f, width = width, textvariable = v.tk_variable)
    e.grid(row = 0, column = 1, sticky = 'ew')
    self.entry = e

    if suffix:
      s = Tkinter.Label(f, text = suffix)
      s.grid(row = 0, column = 2, sticky = 'w')

    if browse:
      b = Tkinter.Button(f, text = 'Browse', command = self.browse_cb)
      b.grid(row = 0, column = 3, sticky = 'w')
    
  # ---------------------------------------------------------------------------
  #
  def browse_cb(self, event = None):

    def set_path(apply, dialog):
      if apply:
        paths = dialog.getPaths()
        if paths:
          self.variable.set(paths[0])
          self.entry.xview('end')
    import OpenSave
    d = OpenSave.OpenModeless(command = set_path)
    d.enter()
    
  # ---------------------------------------------------------------------------
  #
  def destroy(self):

    self.frame.destroy()
    self.variable.destroy()
    self.entry.destroy()

# -----------------------------------------------------------------------------
#
def float_variable_value(v, default = None):

  try:
    return float(v.get())
  except:
    return default
    
# -----------------------------------------------------------------------------
#
def integer_variable_value(v, default = None, minimum = None):

  try:
    value = int(v.get())
  except:
    return default
  if minimum != None and value < minimum:
    value = minimum
  return value

# -----------------------------------------------------------------------------
# Row of buttons packed in a frame.
#
class Button_Row:

  def __init__(self, parent, title, name_callback_list):

    f = Tkinter.Frame(parent)
    self.frame = f

    col = 0
    if title:
      t = Tkinter.Label(f, text = title)
      t.grid(row = 0, column = col, sticky = 'w')
      col = col + 1

    blist = []
    for name, callback in name_callback_list:
      b = Tkinter.Button(f, text = name, command = callback)
      b.grid(row = 0, column = col, sticky = 'nw')
      col = col + 1
      blist.append(b)
    self.buttons = blist

# -----------------------------------------------------------------------------
# Row of radio buttons packed in a frame.
#
class Radiobutton_Row:

  def __init__(self, parent, title, names, callback = None):

    f = Tkinter.Frame(parent)
    self.frame = f

    col = 0
    if title:
      t = Tkinter.Label(f, text = title)
      t.grid(row = 0, column = col, sticky = 'w')
      col = col + 1

    v = StringVariable(f)
    self.variable = v
    if names:
      v.set(names[0])
    if callback:
      v.add_callback(callback)

    self.buttons = []
    for name in names:
      b = Tkinter.Radiobutton(f, text = name, variable = v.tk_variable,
			      value = name, highlightthickness = 0)
      b.grid(row = 0, column = col, sticky = 'w')
      col = col + 1
      self.buttons.append(b)

  # ---------------------------------------------------------------------------
  #
  def destroy(self):
    self.frame.destroy()
    self.variable.destroy()

# -----------------------------------------------------------------------------
# Menu button and pane.
#
class Menu:

  def __init__(self, parent, name, entry_list):

    self.button = Tkinter.Menubutton(parent, text = name)
    self.pane = Tkinter.Menu(self.button)
    self.button['menu'] = self.pane
    
    self.variables = add_menu_entries(self.pane, entry_list)

  # ---------------------------------------------------------------------------
  #
  def destroy(self):
    self.button.destroy()
    self.pane.destroy()
    for var in self.variables:
      var.destroy()

  # --------------------------------------------------------------------------
  #
  def add_entry(self, name, callback):

    self.pane.add_command(label = name, command = callback)

  # --------------------------------------------------------------------------
  #
  def add_checkbutton_entry(self, name, variable):

    self.pane.add_checkbutton(label = name, variable = variable.tk_variable)

  # --------------------------------------------------------------------------
  #
  def rename_entry(self, index, name):

    self.pane.entryconfigure(index, label = name)

  # --------------------------------------------------------------------------
  #
  def remove_entry(self, index):

    self.pane.delete(index)

  # --------------------------------------------------------------------------
  #
  def remove_all_entries(self):

    self.pane.delete(0, 'end')

# -----------------------------------------------------------------------------
#
def cascade_menu(menu, name, entries = []):

  cmenu = Tkinter.Menu(menu)
  menu.add_cascade(label = name, menu = cmenu)
  add_menu_entries(cmenu, entries)
  return cmenu

# -----------------------------------------------------------------------------
#
def add_menu_entries(pane, entry_list):

  variables = []
  for e in entry_list:
    if e == 'separator':
      # Horizontal line
      pane.add_separator()
    elif len(e) == 2:
      # Normal entry
      name, callback = e
      pane.add_command(label = name, command = callback)
    elif len(e) == 3:
      # Checkbutton entry
      name, onoff, callback = e
      v = BooleanVariable(pane)
      v.set(onoff)
      variables.append(v)
      pane.add_checkbutton(label = name, variable = v.tk_variable,
                           command = callback)
  return variables

# -----------------------------------------------------------------------------
#
def base_menu_index(pane):

  if pane.cget('tearoff'):
    return 1
  else:
    return 0

# -----------------------------------------------------------------------------
# Option menu with label on left.
#
class Option_Menu:

  def __init__(self, parent, title, *values):

    f = Tkinter.Frame(parent)
    self.frame = f
    
    if title:
      label = Tkinter.Label(f, text = title)
      label.grid(row = 0, column = 0, sticky = 'w')
      self.label = label

    v = StringVariable(parent)
    self.variable = v

    mb = Tkinter.Menubutton(f, textvariable = v.tk_variable,
                            indicatoron = 1, borderwidth = 2,
                            relief = 'raised',
                            highlightthickness = 2, anchor = 'c')
    mb.grid(row = 0, column = 1, sticky = 'w')
    self.button = mb

    m = Tkinter.Menu(mb, tearoff = 0)
    self.menu = m
    
    self.values = []
    mb['menu'] = m
    for name in values:
      self.add_entry(name)

    if values:
      self.variable.set(values[0])

  # ---------------------------------------------------------------------------
  #
  def destroy(self):
    self.frame.destroy()
    self.variable.destroy()
    self.button.destroy()
    self.menu.destroy()

  # --------------------------------------------------------------------------
  #
  def add_callback(self, callback):

    self.variable.add_callback(callback)

  # --------------------------------------------------------------------------
  #
  def add_entry(self, name):

    set_variable_cb = lambda v=self.variable, n=name: v.set(n)
    self.menu.add_command(label = name, command = set_variable_cb)
    self.values.append(name)

  # --------------------------------------------------------------------------
  #
  def insert_entry(self, index, name):

    set_variable_cb = lambda v=self.variable, n=name: v.set(n)
    self.menu.insert_command(index, label = name, command = set_variable_cb)
    self.values.insert(index, name)

  # --------------------------------------------------------------------------
  #
  def remove_entry(self, index):

    self.menu.delete(index)
    del self.values[index]

  # --------------------------------------------------------------------------
  #
  def remove_all_entries(self, invoke_callbacks = 0):

    self.menu.delete(0, 'end')
    self.variable.set('', invoke_callbacks = invoke_callbacks)
    self.values = []

# -----------------------------------------------------------------------------
# Option menu with label on left that updates entries whenever menu is posted.
#
class Updating_Option_Menu:

  def __init__(self, parent, title, values_cb):

    self.values_cb = values_cb
    self.name_to_value = {}

    import Tkinter
    f = Tkinter.Frame(parent)
    self.frame = f
    
    if title:
      label = Tkinter.Label(f, text = title)
      label.grid(row = 0, column = 0, sticky = 'w')
      self.label = label

    from CGLtk import Hybrid
    v = Hybrid.StringVariable(parent)
    self.variable = v

    mb = Tkinter.Menubutton(f, textvariable = v.tk_variable,
                            indicatoron = 1, borderwidth = 2,
                            relief = 'raised',
                            highlightthickness = 2, anchor = 'c')
    mb.grid(row = 0, column = 1, sticky = 'w')

    m = Tkinter.Menu(mb, tearoff = 0, postcommand = self.update_menu)
    self.menu = m
    
    mb['menu'] = m
    self.update_menu()

  # ---------------------------------------------------------------------------
  #
  def destroy(self):
    self.frame.destroy()
    self.variable.destroy()
    self.menu.destroy()

  # --------------------------------------------------------------------------
  #
  def value(self):

    name = self.variable.get()
    v = self.name_to_value.get(name)
    return v

  # --------------------------------------------------------------------------
  #
  def add_callback(self, callback):

    self.variable.add_callback(callback)

  # --------------------------------------------------------------------------
  #
  def update_menu(self, allow_new_choice = True):

    chosen = self.variable.get()
    
    self.remove_all_entries()
    name_value_pairs = self.values_cb()
    for name, value in name_value_pairs:
        self.add_entry(name, value)

    names = map(lambda nv: nv[0], name_value_pairs)
    if not chosen or not chosen in names:
        if names and allow_new_choice:
            chosen = names[0]
        else:
            chosen = ''
    if chosen:
      self.variable.set(chosen)

  # --------------------------------------------------------------------------
  #
  def add_entry(self, name, value):

    set_variable_cb = lambda v=self.variable, n=name: v.set(n)
    self.menu.add_command(label = name, command = set_variable_cb)
    self.name_to_value[name] = value

  # --------------------------------------------------------------------------
  #
  def remove_all_entries(self, invoke_callbacks = 0):

    self.menu.delete(0, 'end')
    self.variable.set('', invoke_callbacks = invoke_callbacks)
    self.name_to_value.clear()

# -----------------------------------------------------------------------------
# List with vertical and horizontal scrollbars.
#
class Scrollable_List:

  def __init__(self, parent, heading, height, callback = None):

    f = Tkinter.Frame(parent)
    self.frame = f
    f.rowconfigure(1, weight = 1)
    f.columnconfigure(0, weight = 1)

    if heading != None:
      lbl = Tkinter.Label(f, text = heading, justify = 'left')
      lbl.grid(row = 0, column = 0, sticky = 'nw')
      self.heading = lbl
    
    lb = Tkinter.Listbox(f, height = height)
    lb.grid(row = 1, column = 0, sticky = 'news')
    lb['selectmode'] = 'extended'
    if callback:
      lb.bind('<ButtonRelease-1>', callback)
    self.listbox = lb

    hb = Tkinter.Scrollbar(f, orient = 'horizontal', command = lb.xview)
    hb.grid(row = 2, column = 0, sticky = 'ew')
    lb['xscrollcommand'] = scrollbar_adjuster(hb)

    vb = Tkinter.Scrollbar(f, command = lb.yview)
    vb.grid(row = 1, column = 1, sticky = 'ns')
    lb['yscrollcommand'] = scrollbar_adjuster(vb)

# -----------------------------------------------------------------------------
# Return function to set scrollbar range.
# Functioon will remove scrollbar from grid if full document is visible.
#
def scrollbar_adjuster(sbar):

  def adjust(first, last, sbar=sbar):
    if float(first) == 0 and float(last) == 1:
      sbar.grid_remove()
    else:
      sbar.set(first, last)
      if not sbar.winfo_manager():
        sbar.grid()
  return adjust

# -----------------------------------------------------------------------------
# Text with vertical and horizontal scrollbars.
#
class Scrollable_Text:

  def __init__(self, parent, heading, height, horizontal_scroll = True):

    f = Tkinter.Frame(parent)
    self.frame = f
    f.rowconfigure(1, weight = 1)
    f.columnconfigure(0, weight = 1)

    if heading != None:
      lbl = Tkinter.Label(f, text = heading, justify = 'left')
      lbl.grid(row = 0, column = 0, sticky = 'nw')
      self.heading = lbl
    
    t = Tkinter.Text(f, height = height)
    t.grid(row = 1, column = 0, sticky = 'news')
    self.text = t

    if horizontal_scroll:
      hb = Tkinter.Scrollbar(f, orient = 'horizontal', command = t.xview)
      hb.grid(row = 2, column = 0, sticky = 'ew')
      t['xscrollcommand'] = scrollbar_adjuster(hb)

    vb = Tkinter.Scrollbar(f, command = t.yview)
    vb.grid(row = 1, column = 1, sticky = 'ns')
    t['yscrollcommand'] = scrollbar_adjuster(vb)

# -----------------------------------------------------------------------------
# Checkbutton and variable to hold state.
#
class Checkbutton:

  def __init__(self, parent, text, onoff):
        
    v = BooleanVariable(parent)
    v.set(onoff)
    self.variable = v
    b = Tkinter.Checkbutton(parent, text = text, variable = v.tk_variable)
    b['highlightbackground'] = b['background']
    self.button = b

  # ---------------------------------------------------------------------------
  #
  def destroy(self):
    self.variable.destroy()
    self.button.destroy()

  # ---------------------------------------------------------------------------
  # Popup frame when check button turned on.  Keyword arguments must
  # contain grid keywords.
  #
  def popup_frame(self, frame, **kw):

    self.popup_frame = frame
    self.grid_args = kw
    trace_tk_variable(self.variable.tk_variable, self.popup_frame_cb)

  # ---------------------------------------------------------------------------
  #
  def popup_frame_cb(self):

    if self.variable.get():
      apply(self.popup_frame.grid, (), self.grid_args)
    else:
      self.popup_frame.grid_forget()

  # ---------------------------------------------------------------------------
  #
  def callback(self, cb):

    self.variable.add_callback(cb)

# -----------------------------------------------------------------------------
# Row of checkbuttons packed in a frame.
#
class Checkbutton_Row:

  def __init__(self, parent, title, names):

    f = Tkinter.Frame(parent)
    self.frame = f

    col = 0
    if title:
      t = Tkinter.Label(f, text = title)
      t.grid(row = 0, column = col, sticky = 'w')
      col = col + 1

    buttons = []
    for name in names:
      b = Checkbutton(f, name, 0)
      b.button.grid(row = 0, column = col, sticky = 'w')
      buttons.append(b)
      col = col + 1

    self.checkbuttons = buttons


# -----------------------------------------------------------------------------
# Checkbutton followed by text with interpersed entry fields.
#
class Checkbutton_Entries:

  def __init__(self, parent, onoff, *text_and_entries):

    self.variables = []
    self.entries = []
    
    f = Tkinter.Frame(parent)
    self.frame = f
        
    v = BooleanVariable(f)
    v.set(onoff)
    self.variables.append(v)
    b = Tkinter.Checkbutton(f, variable = v.tk_variable)
    if text_and_entries and isinstance(text_and_entries[0], str):
      b['text'] = text_and_entries[0]
      text_and_entries = text_and_entries[1:]
    b.grid(row = 0, column = 0, sticky = 'w')
    b['highlightbackground'] = b['background']
    self.button = b

    for c, te in enumerate(text_and_entries):
      if isinstance(te, str):
        t = Tkinter.Label(f, text = te)
        t.grid(row = 0, column = c+1, sticky = 'w')
      else:
        width, value = te
        v = StringVariable(f)
        v.set(value)
        self.variables.append(v)
        e = Tkinter.Entry(f, width = width, textvariable = v.tk_variable)
        e.grid(row = 0, column = c+1, sticky = 'w')
        self.entries.append(e)

  # ---------------------------------------------------------------------------
  #
  def destroy(self):
    self.frame.destroy()
    self.button.destroy()
    for var in self.variables:
      var.destroy()
    for entry in self.entries:
      entry.destroy()

# -----------------------------------------------------------------------------
# Horizontal scale with label, entry, and slider packed into a frame.
#
# Allow typing in entry field outside the range of the scale bar.
#
class Scale:

  def __init__(self, parent, title, min, max, step, start, entry_width = 5):

    f = Tkinter.Frame(parent)
    f.columnconfigure(2, weight = 1)
    self.frame = f

    lbl = Tkinter.Label(f, text = title)
    lbl.grid(row = 0, column = 0, sticky = 'w')
    self.label = lbl

    v = StringVariable(f)
    v.set(str(start))
    self.variable = v

    e = Tkinter.Entry(f, width = entry_width, textvariable = v.tk_variable)
    e.grid(row = 0, column = 1, sticky = 'w')
    self.entry = e
    v.add_callback(self.entry_changed_cb)

    sv = StringVariable(f)
    sv.set(str(start))
    self.scale_variable = sv

    s = Tkinter.Scale(f, orient = 'horizontal', showvalue = 0,
		      variable = sv.tk_variable)
    s['resolution'] = step
    s['from'] = min
    s['to'] = max
    s.grid(row = 0, column = 2, sticky = 'ew')
    self.scale = s

    sv.add_callback(self.scale_changed_cb)

    self.ignore_scale_change = False

  # ---------------------------------------------------------------------------
  #
  def destroy(self):
    self.frame.destroy()
    self.variable.destroy()
    self.entry.destroy()
    self.scale_variable.destroy()
    self.scale.destroy()

  # ---------------------------------------------------------------------------
  #
  def entry_changed_cb(self):

    # Clamp the value to scale bar range before setting scale position.
    v = self.value()
    s = self.scale
    if v < s['from']:
      sval = str(s['from'])
    elif v > s['to']:
      sval = str(s['to'])
    else:
      sval = self.variable.get()
    self.scale_variable.set(sval, invoke_callbacks = False)

  # ---------------------------------------------------------------------------
  #
  def scale_changed_cb(self):

    if self.ignore_scale_change:
      return

    #
    # Update the entry field later.  This works around a Tk 8.4.15 bug where
    # an event loop update() call in a scale bar callback can cause a mouse
    # click in the trough of the scale bar to be repeatedly processed.  The
    # bug could be that the mouse up event gets handled by the update() and
    # then returning from this event handler causes the Tk scale to start
    # waiting for the mouse up which has already been processed.
    #
    self.frame.after_idle(self.make_entry_match_scale)

  # ---------------------------------------------------------------------------
  #
  def make_entry_match_scale(self):

    self.variable.set(self.scale_variable.get())
    
  # ---------------------------------------------------------------------------
  #
  def callback(self, cb):

    self.variable.add_callback(cb)

  # ---------------------------------------------------------------------------
  #
  def value(self, default = None):

    try:
      return float(self.variable.get())
    except:
      return default

  # ---------------------------------------------------------------------------
  #
  def set_value(self, value, invoke_callbacks = 1):

    self.variable.set(value, invoke_callbacks)
    self.entry_changed_cb()                     # Update slider position

  # ---------------------------------------------------------------------------
  #
  def range(self):

    s = self.scale
    return (s['from'] ,s['to'])

  # ---------------------------------------------------------------------------
  #
  def set_range(self, min, max, step = 0):

    s = self.scale

    # Avoid processing a scale changed callback which happens if the new
    # range does not contain the scale value.
    self.ignore_scale_change = True

    # Have to set resolution before from/to because the from/to get rounded
    # using the resolution.  Step of 0 means no discretization of steps
    s['resolution'] = step
    s['from'] = min
    s['to'] = max

    self.ignore_scale_change = False

# -----------------------------------------------------------------------------
# Horizontal scale with label, entry, and slider packed into a frame.
# The scale value is a power of the horizontal position.  The min and max
# values must both be positive.
#
# Didn't combine this into the Scale class because it requires significantly
# more complexity.
#
class Logarithmic_Scale:

  def __init__(self, parent, title, min, max, start,
               entry_format = '%.0f', entry_width = 5):

    self.min = min
    self.max = max
    self.entry_format = entry_format
    self.synchronize = 1        # Breaks entry/scale variable setting loops
    
    f = Tkinter.Frame(parent)
    f.columnconfigure(2, weight = 1)
    self.frame = f

    lbl = Tkinter.Label(f, text = title)
    lbl.grid(row = 0, column = 0, sticky = 'w')
    self.label = lbl

    v = StringVariable(f)
    v.set(str(start))
    self.variable = v
    trace_tk_variable(v.tk_variable, self.entry_changed_cb)

    e = Tkinter.Entry(f, width = entry_width, textvariable = v.tk_variable)
    e.grid(row = 0, column = 1, sticky = 'w')
    self.entry = e

    sv = DoubleVariable(f)
    self.scale_variable = sv
    trace_tk_variable(sv.tk_variable, self.scale_changed_cb)

    s = Tkinter.Scale(f, orient = 'horizontal', showvalue = 0,
		      variable = sv.tk_variable)
    s['from'] = 0
    s['to'] = 1
    s['resolution'] = 0
    s.grid(row = 0, column = 2, sticky = 'ew')

    self.entry_changed_cb()     # synchronize slider postion with entry value
    
  # ---------------------------------------------------------------------------
  #
  def destroy(self):
    self.frame.destroy()
    self.variable.destroy()
    self.entry.destroy()
    self.scale_variable.destroy()
    self.scale.destroy()

  # ---------------------------------------------------------------------------
  # Synchronize scale slider position with entry
  #
  def entry_changed_cb(self):

    if not self.synchronize:
      return
    
    evalue = self.value()
    if evalue == None:
      return

    svalue = self.scale_position(evalue)
    self.synchronize = 0
    self.scale_variable.set(svalue)
    self.synchronize = 1

  # ---------------------------------------------------------------------------
  #
  def scale_position(self, value):

    if value < self.min:
      return 0
    if value > self.max:
      return 1

    one_factor = self.max / self.min
    value_factor = value / self.min
    svalue = math.log(value_factor) / math.log(one_factor)

    return svalue

  # ---------------------------------------------------------------------------
  # Synchronize entry field value with scale slider position.
  #
  def scale_changed_cb(self):

    if not self.synchronize:
      return
    
    svalue = self.scale_variable.get()
    one_factor = self.max / self.min
    value = self.min * math.pow(one_factor, svalue)

    self.synchronize = 0
    self.variable.set(self.entry_format % value)
    self.synchronize = 1
    
  # ---------------------------------------------------------------------------
  #
  def callback(self, cb):

    self.variable.add_callback(cb)

  # ---------------------------------------------------------------------------
  #
  def value(self, default = None):

    try:
      return float(self.variable.get())
    except:
      return default

  # ---------------------------------------------------------------------------
  #
  def set_value(self, value, invoke_callbacks = 1):

    self.variable.set(value, invoke_callbacks)

  # ---------------------------------------------------------------------------
  #
  def set_range(self, min, max):

    self.min = min
    self.max = max
    self.entry_changed_cb()

# -----------------------------------------------------------------------------
# Make a column of labels in a grid
#
def label_column(frame, heading, column, rows, initial = None):

  hl = Tkinter.Label(frame, text = heading)
  hl.grid(row = 0, column = column)
  labels = []
  for a in range(rows):
    lbl = Tkinter.Label(frame)
    if initial:
      lbl['text'] = str(initial[a])
    lbl.grid(row = 1+a, column = column)
    labels.append(lbl)
  return labels

# -----------------------------------------------------------------------------
# Make a column of entry fields in a grid.
#
def entry_column(frame, heading, column, rows, initial = None):

  hl = Tkinter.Label(frame, text = heading)
  hl.grid(row = 0, column = column)
  entries = []
  variables = []
  for a in range(rows):
    v = StringVariable(frame)
    if initial and initial[a] != None:
      v.set(str(initial[a]))
    e = Tkinter.Entry(frame, width = 5, textvariable = v.tk_variable)
    e.grid(row = 1+a, column = column)
    entries.append(e)
    variables.append(v)
  return entries, variables
    
# -----------------------------------------------------------------------------
# Make a column of check buttons in a grid.
#
def checkbutton_column(frame, heading, column, rows, initial = None):

  hl = Tkinter.Label(frame, text = heading)
  hl.grid(row = 0, column = column)
  variables = []
  for a in range(rows):
    v = BooleanVariable(frame)
    if initial:
      v.set(initial[a])
    cb = Tkinter.Checkbutton(frame, variable = v.tk_variable)
    cb.grid(row = 1+a, column = column)
    variables.append(v)
  return variables

# ---------------------------------------------------------------------------
# Make a column of canvases in a grid.
#
def canvas_column(frame, heading, column, rows, width, height):

  hl = Tkinter.Label(frame, text = heading)
  hl.grid(row = 0, column = column)
  canvases = []
  for a in range(rows):
    # set highlight thickness = 0 so line in column 0 is visible.
    c = Tkinter.Canvas(frame, width = width, height = height,
                       highlightthickness = 0)
    c.grid(row = 1+a, column = column)
    canvases.append(c)
  return canvases

# ---------------------------------------------------------------------------
# Make a column of color wells in a grid.
#
def color_column(frame, heading, column, rows,
                 initial = None, callbacks = None):

  from color import ColorWell
  hl = Tkinter.Label(frame, text = heading)
  hl.grid(row = 0, column = column)
  colors = []
  for a in range(rows):
    if callbacks:
      cb = callbacks[a]
    else:
      cb = None
    c = ColorWell.ColorWell(frame, callback = cb)
    if initial:
      c.showColor(initial[a])
    c.grid(row = 1+a, column = column)
    colors.append(c)
  return colors

# -----------------------------------------------------------------------------
# Wrapper around Tk variables that allows variables to be set without
# invoking variable modified callbacks.
#
class Variable:

  def __init__(self, tk_variable):

    self.tk_variable = tk_variable

    self.callbacks = []
    self.block_callbacks = 0

  # ---------------------------------------------------------------------------
  #
  def destroy(self):

    self.callbacks = []

  # ---------------------------------------------------------------------------
  #
  def get(self):

    return self.tk_variable.get()

  # ---------------------------------------------------------------------------
  #
  def set(self, value, invoke_callbacks = 1):

    if not invoke_callbacks:
      self.block_callbacks += 1

    try:
      self.tk_variable.set(value)
    except:
      # Make callback blocking works even after an exception.
      if not invoke_callbacks:
        self.block_callbacks -= 1
      raise

    if not invoke_callbacks:
      self.block_callbacks -= 1

  # ---------------------------------------------------------------------------
  #
  def add_callback(self, callback):

    if len(self.callbacks) == 0:
      trace_tk_variable(self.tk_variable, self.tk_variable_changed_cb)

    self.callbacks.append(callback)

  # ---------------------------------------------------------------------------
  #
  def tk_variable_changed_cb(self):

    if self.block_callbacks == 0:
      for cb in self.callbacks:
	cb()

# -----------------------------------------------------------------------------
# Wrappers around Tk variables that allows variables to be set without
# invoking variable modified callbacks.
#
class StringVariable(Variable):
  def __init__(self, parent):
    Variable.__init__(self, Tkinter.StringVar(parent))

class BooleanVariable(Variable):
  def __init__(self, parent):
    Variable.__init__(self, Tkinter.BooleanVar(parent))

class DoubleVariable(Variable):
  def __init__(self, parent):
    Variable.__init__(self, Tkinter.DoubleVar(parent))

# -----------------------------------------------------------------------------
# Call a callback with no arguments when Tk variable value changes.
#
# If a Tk variable changes within a write callback for that variable
# another invocation of the callback is not made by the Tk trace mechanism.
# This code remedies that, calling the callback repeatedly until the variable
# does not change.
#
def trace_tk_variable(var, callback):

  def cb(n1, n2, op, v=var, callback=callback):
    changed = 1
    while changed:
      vbefore = v.get()
      callback()
      vafter = v.get()
      changed = (vafter != vbefore)

  var.trace_variable('w', cb)
  
# -----------------------------------------------------------------------------
#
def destroy_child_widgets(w):

  for c in w.winfo_children():
    c.destroy()

# -----------------------------------------------------------------------------
#
class Popup_Panel:

  def __init__(self, parent):

    self.frame = Tkinter.Frame(parent)

    v = BooleanVariable(parent)
    self.panel_shown_variable = v
    v.add_callback(self.show_panel_cb)

    self.close_button = None
    self.show_close_button = True
    
  # ---------------------------------------------------------------------------
  #
  def show_panel_cb(self):

    show = self.panel_shown_variable.get()
    if show:
      self.frame.grid()
      if self.close_button:
        if self.show_close_button:
          self.close_button.grid()
        else:
          self.close_button.grid_remove()
    else:
      self.frame.grid_remove()

    self.frame.winfo_toplevel().geometry('')    # Allow toplevel resize.

  # ---------------------------------------------------------------------------
  #
  def make_close_button(self, parent):

    b = Tkinter.Button(parent,
                       image = self.close_button_bitmap(),
                       command = self.close_panel_cb)
    self.close_button = b
    return b

  # ---------------------------------------------------------------------------
  #
  def close_panel_cb(self):

    self.panel_shown_variable.set(False)

  # ---------------------------------------------------------------------------
  # Used for closing panels.
  #
  def close_button_bitmap(self):

    return bitmap('x')

# -----------------------------------------------------------------------------
#
bitmap_specs = (
      ('x',
'''#define x_width 9
#define x_height 8
static unsigned char x_bits[] = {
   0x83, 0x01, 0xc6, 0x00, 0x6c, 0x00, 0x38, 0x00, 0x38, 0x00, 0x6c, 0x00,
   0xc6, 0x00, 0x83, 0x01};
'''),
      ('eye',
'''#define eye_width 16
#define eye_height 11
static unsigned char eye_bits[] = {
   0x00, 0x00, 0x00, 0x00, 0xe0, 0x07, 0x38, 0x1c, 0x88, 0x11, 0xcc, 0x33,
   0x88, 0x11, 0x38, 0x1c, 0xe0, 0x07, 0x00, 0x00, 0x00, 0x00};
'''),
      ('closed eye',
'''#define closed_eye_width 16
#define closed_eye_height 11
static unsigned char closed_eye_bits[] = {
   0x00, 0x00, 0x00, 0x00, 0xe0, 0x07, 0x38, 0x1c, 0x08, 0x10, 0x0c, 0x30,
   0x08, 0x10, 0x38, 0x1c, 0xe0, 0x07, 0x00, 0x00, 0x00, 0x00};
'''),
      ('dash',
'''#define dash_width 9
#define dash_height 8
static unsigned char dash_bits[] = {
   0x00, 0x00, 0x00, 0x00, 0x00, 0x00, 0xfe, 0x00, 0xfe, 0x00, 0x00, 0x00,
   0x00, 0x00, 0x00, 0x00};
'''),
      )

# -----------------------------------------------------------------------------
# Create Tk bitmaps of standard icons.
#
bitmaps = {}
def bitmap(name):

  global bitmaps, bitmap_specs
  if not bitmaps:
    for n, bmap in bitmap_specs:
      bitmaps[n] = Tkinter.BitmapImage(data = bmap, foreground = 'black')

  return bitmaps.get(name, None)

# -----------------------------------------------------------------------------
# Row of checkbuttons eaching popping up a specific panel.
#
class Feature_Buttons_Panel(Popup_Panel):

  name = 'Feature buttons'           # Used in feature menu.
  
  def __init__(self, dialog, parent):
    
    self.dialog = dialog

    Popup_Panel.__init__(self, parent)

    frame = self.frame
    frame.columnconfigure(1, weight = 1)

    self.balloon_toplevel = None
    self.balloon_label = None

    h = Tkinter.Label(frame, text = 'Features ')
    h.grid(row = 0, column = 0, sticky = 'w')

    bf = Tkinter.Frame(frame)
    bf.grid(row = 0, column = 1, sticky = 'ew')
    self.button_frame = bf

    b = self.make_close_button(frame)
    b.grid(row = 0, column = 2, sticky = 'e')
    
  # ---------------------------------------------------------------------------
  # Only call this one time.
  #
  def set_panels(self, panels):

    # Would prefer to use grid instead of place packing but it creates too
    # much space between checkbuttons which always pads a full indicator
    # width between text and indicator even if there is no text.
    bf = self.button_frame
    x = 0
    pad = 1
    if self.frame.tk.call('tk', 'windowingsystem') == 'aqua':
      pad = 5
    col = 0
    for p in panels:
      if isinstance(p, Feature_Buttons_Panel):
        continue
      var = p.panel_shown_variable.tk_variable
      import Tkinter
      b = Tkinter.Checkbutton(bf, variable = var)
      Balloon_Help(b, p.name)
      # Checkbutton pads a full indicator width between text and indicator.
      w = b.winfo_reqwidth() / 2 + pad
      b.place(x = x, width = w)
      x += w
      col += 1
      if col % 5 == 0:
        x += w
        
    bf.configure(width = x, height = b.winfo_reqheight())

# -----------------------------------------------------------------------------
# Pops up text when mouse is over a Tk widget.  Delay is in seconds.
#
class Balloon_Help:

  # Use the same toplevel window for all balloons
  balloon_toplevel = None
  balloon_label = None

  def __init__(self, widget, text, delay = 0):

    self.widget = widget
    self.text = text
    self.delay = delay
    self.pointer_over_widget = False

    widget.bind('<Any-Enter>', self.enter_cb)
    widget.bind('<Any-Leave>', self.hide_balloon)
    widget.bind('<Destroy>', self.hide_balloon)
    
  # ---------------------------------------------------------------------------
  #
  def enter_cb(self, event = None):

    self.pointer_over_widget = True
    if self.delay > 0:
      self.widget.after(int(1000*self.delay), self.delayed_show_cb)
    else:
      self.show_balloon()

  # ---------------------------------------------------------------------------
  #
  def delayed_show_cb(self):

    if self.pointer_over_widget:
      self.show_balloon()

  # ---------------------------------------------------------------------------
  #
  def show_balloon(self):

    bt = self.balloon_toplevel
    if bt is None:
      t = self.widget.winfo_toplevel()
      import Tkinter
      bt = Tkinter.Toplevel(t)
      import CGLtk
      CGLtk.balloonDontTakeFocus(bt)    # Aqua bug work-around.
      bt.wm_overrideredirect(True)
      self.balloon_toplevel = bt
      bt.bind('<Destroy>', self.balloon_destroyed_cb)
      Balloon_Help.balloon_toplevel = bt
      bl = Tkinter.Label(bt, borderwidth = 1, relief = 'solid')
      bl.pack()
      Balloon_Help.balloon_label = bl

    bl = self.balloon_label
    bl.configure(text = self.text)
    w, h = bl.winfo_reqwidth(), bl.winfo_reqheight()
    wt = self.widget
    bh = wt.winfo_height()
    x, y = wt.winfo_rootx(), wt.winfo_rooty()
    geom = '%dx%d+%d+%d' % (w, h, x, y - h)
    bt.geometry(geom)
    bt.deiconify()
    import CGLtk
    CGLtk.raiseWindow(bt)
    
  # ---------------------------------------------------------------------------
  #
  def hide_balloon(self, event = None):

    self.pointer_over_widget = False
    bt = self.balloon_toplevel
    if bt:
      bt.wm_withdraw()
    
  # ---------------------------------------------------------------------------
  #
  def balloon_destroyed_cb(self, event = None):

    Balloon_Help.balloon_toplevel = None
    Balloon_Help.balloon_label = None
