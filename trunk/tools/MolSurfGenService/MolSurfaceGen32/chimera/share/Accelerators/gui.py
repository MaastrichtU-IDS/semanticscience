from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Accelerator_Browser(ModelessDialog):

  title = 'Keyboard Shortcuts'
  name = 'keyboard shortcuts'
  buttons = ('Close',)
  help = 'ContributedSoftware/accelerators/accelerators.html'
  
  def fillInUI(self, parent):

    self.key_buffer = ''
    self.key_callback_registered = None
    self.time_out_id = None

    import Accelerators
    self.preferences = Accelerators.accelerator_preferences_category()
    self.top = parent.winfo_toplevel()
    self.top.wm_withdraw()     # Do not show automatically when dialog created
    
    parent.columnconfigure(0, weight = 1)
    row = 0

    import Tkinter
    from CGLtk import Hybrid

    al = Hybrid.Scrollable_List(parent, 'Available shortcuts', 10,
				self.accelerator_selection_cb)
    self.accelerator_listbox = al.listbox
    al.frame.grid(row = row, column = 0, sticky = 'news')
    parent.rowconfigure(row, weight = 1)
    row = row + 1

    fi = Hybrid.Entry(parent, 'Filter list ', 20)
    fi.entry.bind('<KeyRelease>', self.filter_cb)
    fi.frame.grid(row = row, column = 0, sticky = 'ew')
    self.filter_text = fi.variable
    row = row + 1
    
    ao = Hybrid.Checkbutton(parent, 'Enable keyboard shortcuts', False)
    ao.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    ao.callback(self.activate_accelerators_cb)
    self.active_var = ao.variable

    from chimera import statusline
    sl = Hybrid.Checkbutton(parent, 'Show main window status line',
                            statusline.status_line_shown())
    sl.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    sl.callback(self.status_line_cb)
    self.status_line_var = sl.variable
    from chimera import triggers
    triggers.addHandler('status line', self.status_line_visibility_cb, None)

    rf = Tkinter.Frame(parent)
    rf.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    rb = Tkinter.Button(rf, text = 'Load', command = self.load_cb)
    rb.grid(row = 0, column = 0, sticky = 'w')
    
    afl = Tkinter.Label(rf, text = ' shortcuts file')
    afl.grid(row = 0, column = 1, sticky = 'w')

    path = self.preferences['path']             # Path might be None
    af = Hybrid.Entry(parent, '', 20, path)
    af.entry.xview_moveto(1)    # show right most part of path
    af.entry.bind('<KeyPress-Return>', self.load_cb)
    af.frame.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.accelerator_file = af.variable

    tot = self.preferences['time out']
    tm = Hybrid.Entry(parent, 'Key press time-out (seconds) ', 3, tot)
    tm.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.time_out = tm.variable
    self.time_out.add_callback(self.time_out_changed_cb)

    #
    # Specify a label width so dialog is not resized for long messages.
    #
    msg = Tkinter.Label(parent, width = 30, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.message_label = msg

    self.load_accelerators()
    
  # ---------------------------------------------------------------------------
  #
  def map(self, e=None):

    self.fill_listbox()

  # ---------------------------------------------------------------------------
  #
  def show_dialog(self):

    ModelessDialog.enter(self)
    
  # ---------------------------------------------------------------------------
  #
  def load_accelerators(self):

    from Accelerators import default_accelerator_file
    path = self.accelerator_file.get()
    if path == '':
      path = default_accelerator_file()
      self.accelerator_file.set(path)

    if path == default_accelerator_file():
      self.preferences['path'] = None
    else:
      self.preferences['path'] = path

    dict = {'__file__':path}
    try:
      execfile(path, dict)
    except:
      from chimera import replyobj
      replyobj.reportException('Error executing accelerators file ' + path)
      return

    if not dict.has_key('register_accelerators'):
      from chimera import replyobj
      replyobj.error('Accelerators file ' + path +
                     ' has no register_accelerators() function.')
      return

    register_accelerators = dict['register_accelerators']
    try:
      register_accelerators()
    except:
      from chimera import replyobj
      replyobj.reportException('Error running register_accelerators() from accelerators file ' + path)
      return

    self.fill_listbox()
    
  # ---------------------------------------------------------------------------
  #
  def load_cb(self, event = None):

    self.load_accelerators()

  # ---------------------------------------------------------------------------
  #
  def fill_listbox(self, filter_words = None):

    from Accelerators import accelerator_table
    t = accelerator_table()
    alist = list(t.accelerators())
    alist.sort(lambda a1,a2: cmp(a1.key_sequence.lower(),
                                 a2.key_sequence.lower()))
    if filter_words:
      alist = [a for a in alist 
               if len([w for w in filter_words
                       if (w.lower() in a.short_description().lower() or
                           w in a.key_sequence)]) == len(filter_words)]

    self.listed_accelerators = alist

    listbox = self.accelerator_listbox
    listbox.delete('0','end')
    lines = map(lambda a: '%s  %s' % (a.key_sequence, a.short_description()),
                self.listed_accelerators)
    apply(listbox.insert, ['0'] +  lines)

  # ---------------------------------------------------------------------------
  #
  def filter_cb(self, event = None):

    w = self.filter_text.get().split()
    self.fill_listbox(w)
    
  # ---------------------------------------------------------------------------
  #
  def accelerator_command(self, cmdname, args):

    if len(args) == 0:
      self.activate(True)
    else:
      from Accelerators import accelerator_table
      t = accelerator_table()
      for seq in args.split():
        a = t.find_accelerator(seq)
        if a is None:
          from Midas import MidasError
          raise MidasError, 'Unknown accelerator "%s"' % seq
        a.invoke()

  # ---------------------------------------------------------------------------
  #
  def message(self, text):

    self.message_label['text'] = text
    self.message_label.update_idletasks()
    
  # ---------------------------------------------------------------------------
  #
  def status(self, text):

    self.message(text)
    from chimera import replyobj
    replyobj.status(text)
    
  # ---------------------------------------------------------------------------
  #
  def log_command(self, text):

    from chimera import replyobj
    replyobj.info(text)
    
  # ---------------------------------------------------------------------------
  #
  def accelerator_selection_cb(self, event):

    indices = map(int, self.accelerator_listbox.curselection())
    if len(indices) != 1:
      return

    index = indices[0]
    a = self.listed_accelerators[index]
    self.message(a.key_sequence + ' - ' + a.long_description())

  # ---------------------------------------------------------------------------
  #
  def activate_accelerators_cb(self):

    enable = self.active_var.get()
    self.preferences['enable at startup'] = enable
    self.activate(enable)

  # ---------------------------------------------------------------------------
  #
  def status_line_cb(self):

    from chimera import statusline
    statusline.show_status_line(self.status_line_var.get())

  # ---------------------------------------------------------------------------
  #
  def status_line_visibility_cb(self, trigger_name, x, shown):

    self.status_line_var.set(shown, invoke_callbacks = 0)

  # ---------------------------------------------------------------------------
  #
  def activate(self, active):

    #
    # Always delete and key press callback and reregister so it preempts
    # the Midas emulator command line.
    #
    if self.key_callback_registered:
      from chimera import tkgui
      tkgui.deleteKeyboardFunc(self.key_callback_registered)
      self.key_callback_registered = None

    if active:
      from chimera import tkgui
      self.key_callback_registered = self.key_pressed_cb
      tkgui.addKeyboardFunc(self.key_callback_registered)
      tkgui.app.graphics.focus()
 
    self.active_var.set(active, invoke_callbacks = 0)
    
  # ---------------------------------------------------------------------------
  #
  def active(self):

    return self.key_callback_registered != None

  # ---------------------------------------------------------------------------
  #
  def key_pressed_cb(self, event):

    c = event.char
    if c == '':
      return		# Modifier or function key

    from Accelerators import accelerator_table
    t = accelerator_table()
    
    key_seq = self.key_buffer + c
    if event.keysym == 'Escape':
      self.status('')
      self.key_buffer = ''
    elif t.find_accelerator(key_seq):
      self.key_buffer = ''
      a = t.find_accelerator(key_seq)
      message = key_seq + ' - ' + a.short_description()
      self.status(message)
      self.log_command('Invoked accelerator ' + message + '\n')
      a.invoke()
    elif t.is_accelerator_prefix(key_seq):
      self.status(key_seq)
      self.key_buffer = key_seq
    else:
      self.status(key_seq + ' - unknown accelerator')
      self.key_buffer = ''

    if self.time_out_id != None:
      self.top.after_cancel(self.time_out_id)
      self.time_out_id = None
      
    time_out = self.time_out_value()
    if self.key_buffer and time_out:
      msec = int(1000 * time_out)
      self.time_out_id = self.top.after(msec, self.time_out_cb)

  # ---------------------------------------------------------------------------
  #
  def time_out_value(self):

    try:
      return float(self.time_out.get())
    except ValueError:
      return None

  # ---------------------------------------------------------------------------
  #
  def time_out_cb(self):

    self.time_out_id = None
    self.key_buffer = ''
    self.status('')

  # ---------------------------------------------------------------------------
  #
  def time_out_changed_cb(self):

    self.preferences['time out'] = self.time_out.get()

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Accelerator_Browser.name, Accelerator_Browser, replace = 1)
