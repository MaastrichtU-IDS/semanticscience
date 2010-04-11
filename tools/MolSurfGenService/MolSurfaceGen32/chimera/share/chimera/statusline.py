# -----------------------------------------------------------------------------
# Status line at bottom of main Chimera window.
#

button_opts = { "padx":0, "pady":0, "relief":"flat" }
grid_opts = { "ipadx":0, "ipady":0, "padx":0, "pady":0, "sticky":"n" }

# -----------------------------------------------------------------------------
#
class Status_Line:
  
  colorMode = 0
  def __init__(self):

    self.shown = 0
    self.check_for_click = False
    
    import tkgui
    import Tkinter
    f = Tkinter.Frame(tkgui.app)
    self.frame = f

    # Create ext widget for displaying messages
    msg = Tkinter.Text(f, width = 0, height = 1,
                       borderwidth = 2, relief = 'ridge',
                       takefocus = False, cursor = 'left_ptr',
                       state = 'disabled')
    msg.bind('<Map>', self.message_label_mapped_cb)
    msg.grid(row = 0, column = 1, sticky = 'ew')
    f.columnconfigure(1, weight = 1)
    self.message_label = msg

    # Read in static icons
    import chimage
    self.image_info = chimage.get("information_frame.png", f)
    self.image_info_bw = chimage.get("information_frame_bw.png", f)
    self.image_stop = chimage.get("cross_octagon_frame.png", f)

    # Read in the selection icon, which is only in b/w because
    # we want to tint it with the user selected highlight color.
    # To do so, we need to have a PIL image to play with, so we
    # cannot use chimage.
    from CGLtk import textForeground
    icon_name = "magnifier_left_%s.png" % textForeground(f["background"])
    import chimera, os.path
    filename = chimera.pathFinder().firstExistingFile("chimera",
				      os.path.join("images", icon_name),
				      False, False)
    if not filename:
      import errno, os
      raise IOError(errno.ENOENT, os.strerror(errno.ENOENT), icon_name)
    from PIL import Image
    self.pil_selection = image = Image.open(filename)
    self.image_selection_bw = remove_alpha(self.pil_selection, f)
    self.image_selection = None		# to be constructed later

    # Create selection button
    self.selections_button = Tkinter.Button(f, image=self.image_selection_bw,
					      command=self._sel_cb,
					      **button_opts)
    self.selections_button.grid(row=0, column=3, **grid_opts)
    self.selection_handler_ID = None
    self.first_selection = True

    # Create task buttons
    self.task_info_button = Tkinter.Button(f, image=self.image_info_bw,
					    command=self._task_info_cb,
					    **button_opts)
    self.task_info_button.grid(row=0, column=2, **grid_opts)
    self.task_stop_button = Tkinter.Button(f, image=self.image_stop,
					    command=self._task_stop_cb,
					    **button_opts)
    # Stop button is created here but grid'ed in only when needed
    self.task_event_queue = []
    self.task_stop_button.bind("<Key>", self._task_stop_key_handler)
    self.task_stop_button.bind("<Button-1>", self._task_stop_button_handler)

    # Create resize handle
    import Ttk
    sg = Ttk.Sizegrip(f)
    sg.grid(row=0, column=4, sticky='se')

    # Add help balloons to buttons
    import help
    help.register(self.selections_button, balloon="selection inspector")
    help.register(self.task_info_button, balloon="task panel")
    help.register(self.task_stop_button, balloon="cancel current task")

  # ---------------------------------------------------------------------------
  #
  def show(self, show):

    if show:
      if not self.selection_handler_ID:
	import chimera
        self.selections_button.config(text="selection inspector")
        self.frame.after(30000, self.set_selections)
	self.selection_handler_ID = chimera.triggers.addHandler(
	    "selection changed", lambda tn, md, cs: self.set_selections(), None)
      import Tkinter
      from chimera import tkgui
      kw = {}
      for w in tkgui.app.winfo_children():
        if w.winfo_ismapped():
	  kw["before"] = w
	  break
      self.frame.pack(expand=Tkinter.FALSE, side='bottom', fill=Tkinter.X, **kw)
      self.shown = 1
    else:
      self.frame.pack_forget()
      self.shown = 0
      if self.selection_handler_ID:
	import chimera
	chimera.triggers.deleteHandler("selection changed",
						self.selection_handler_ID)
	self.selection_handler_ID = None
    
  # ---------------------------------------------------------------------------
  # Don't let long label text cause resize of toplevel window.
  # Have to wait to turn off geometry propagation until after
  # the label widget is mapped so that height is correct.
  #
  def message_label_mapped_cb(self, event):

    # Bug in Tk 8.3.0 makes grid propagate 0 toggle propagation state.
    if self.frame.grid_propagate():
      self.frame.grid_propagate(0)
    
  # ---------------------------------------------------------------------------
  #
  def message(self, text, append = False, color = 'black',
              click_callback = None, show_now = True):

    if not self.shown:
      return

    if self.check_for_click:
      self.check_for_click = False
      import update
      update.processWidgetEvents(self.message_label)

    while text.endswith('\n'):
      text = text[:-1]

    ml = self.message_label
    ml.configure(state = 'normal')
    if not append:
      ml.delete('0.0', 'end')
      map(ml.tag_delete, ml.tag_names())
    max_message_size = 1024
    tag_name = 't%d' % len(ml.get('0.0','end'))
    ml.tag_configure(tag_name, foreground = color)
    ml.insert('end', text[:max_message_size], tag_name)
    if click_callback:
      ml.tag_bind(tag_name, '<ButtonPress>', lambda e: click_callback())
    self.check_for_click = not click_callback is None
    ml.configure(state = 'disabled')
    if show_now:
      ml.update_idletasks()
    
  # ---------------------------------------------------------------------------
  #
  def set_selections(self):
    # Construct selection icon by tinting the b/w version with
    # the selection color
    if self.image_selection is None:
      from bgprefs import BACKGROUND, HCOLOR
      import preferences
      sel_color = [ int(i * 255) for i in preferences.get(BACKGROUND, HCOLOR) ]
      self.image_selection = tint(self.pil_selection, tuple(sel_color),
								  self.frame)
      del self.pil_selection
    if self._any_selected():
      self.selections_button.config(image=self.image_selection)
    else:
      self.selections_button.config(image=self.image_selection_bw)

  def _any_selected(self):
    from chimera import selection, Molecule, MSMSModel, PseudoBondGroup
    text = ""
    numAtoms = len(selection.currentAtoms())
    if numAtoms:
      text = "%d atom" % numAtoms
      if numAtoms > 1:
        text += "s"
    
    numBonds = len(selection.currentBonds())
    if numBonds:
      if text:
	text += ", "
      text += "%d bond" % numBonds
      if numBonds > 1:
        text += "s"

    numEdges = len(selection.currentEdges())
    if numEdges != numBonds:
      if text:
	text += ", "
      numPBonds = numEdges - numBonds
      text += "%d pbond" % numPBonds
      if numPBonds > 1:
        text += "s"
    
    graphs = selection.currentGraphs()
    numSurfs = numObjs = 0
    for g in graphs:
      if isinstance(g, (Molecule, PseudoBondGroup)):
        continue
      if isinstance(g, MSMSModel) or "surf" in g.__class__.__name__.lower():
        numSurfs += 1
      else:
        numObjs += 1
    if numSurfs:
      if text:
        text += ", "
      text += "%d surf" % numSurfs
      if numSurfs > 1:
        text += "s"
    if numObjs:
      if text:
        text += ", "
      text += "%d obj" % numObjs
      if numObjs > 1:
        text += "s"

    import help
    if not text:
      help.register(self.selections_button, balloon="no selection")
      show_message("selection cleared", blankAfter=5)
      return False
    else:
      help.register(self.selections_button, balloon=text)
      if self.first_selection:
	self.first_selection = False
	show_message(text, followWith="up-arrow to increase selection "
				      "(atoms->residues->chains etc.)")
      else:
	show_message(text)
      return True

  # ---------------------------------------------------------------------------
  #
  def _sel_cb(self):
    import dialogs, tkgui
    dialogs.display(tkgui._InspectDialog.name)

  # ---------------------------------------------------------------------------
  #
  def _task_info_cb(self):
    import dialogs, tasks
    dialogs.display(tasks.TaskPanel.name)

  # ---------------------------------------------------------------------------
  #
  def _task_stop_cb(self):
    import tasks
    tasks.manager().stop_active_task()

  # ---------------------------------------------------------------------------
  #
  def _task_stop_key_handler(self, event):
    if self.task_event_queue:
      queue = self.task_event_queue[-1][1]	# [0] is the focus window
      queue.append(event)
    return "break"

  # ---------------------------------------------------------------------------
  #
  def _task_stop_button_handler(self, event):
    w = self.task_stop_button.winfo_containing(event.x_root, event.y_root)
    if w is None:
      return
    import dialogs
    from tasks import TaskPanel
    d = dialogs.find(TaskPanel.name, create=False)
    if d is None:
      return
    if w is d.modalCancelButton():
      w.invoke()
      return "break"

  # ---------------------------------------------------------------------------
  #
  def update_task_buttons(self):
    import tasks
    mgr = tasks.manager()
    if mgr.active_modal_task():
      self.task_stop_button.grid(row=0, column=0, **grid_opts)
      self.task_info_button.config(image=self.image_info_bw)
    else:
      self.task_stop_button.grid_forget()
      if mgr.active_task_count():
	self.task_info_button.config(image=self.image_info)
      else:
	self.task_info_button.config(image=self.image_info_bw)

  # ---------------------------------------------------------------------------
  #
  def grab_task_button(self, grab):
    import Pmw
    if grab:
      import tkgui
      window = tkgui.app.focus_get()
      if not window:
	window = tkgui.app
      self.task_event_queue.append((window, []))
      Pmw.pushgrab(self.task_stop_button, False, lambda: None)
    else:
      Pmw.popgrab(self.task_stop_button)
      if Pmw.grabstacktopwindow() is None:
	import tkgui
	for window, eventList in self.task_event_queue:
	  for event in eventList:
	    window.event_generate("<KeyPress>", keysym=event.keysym,
				  keycode=event.keycode,
				  state=event.state,
				  when="tail")
	self.task_event_queue = []

# -----------------------------------------------------------------------------
#
sline = None

# -----------------------------------------------------------------------------
#
def status_line(create = 0):

  global sline
  if create and sline == None:
    sline = Status_Line()
  return sline
  
# -----------------------------------------------------------------------------
#
def show_status_line(show):

  shown = status_line_shown()
  if (show and shown) or (not show and not shown):
    return

  status = status_line(create = show)
  if status:
    status.show(show)
    import chimera
    chimera.triggers.activateTrigger('status line', show)
  
# -----------------------------------------------------------------------------
#
def status_line_shown():

  status = status_line()
  return status and status.shown

# -----------------------------------------------------------------------------
#
_statusBlankHandle = None

# -----------------------------------------------------------------------------
#
def show_message(text, append = 0, blankAfter=None, color='black',
                 followWith="", followTime=20, clickCallback=None,
                 showNow = True):

  status = status_line()
  if not status:
    return

  global _statusBlankHandle
  if _statusBlankHandle:
    status.frame.after_cancel(_statusBlankHandle)
    _statusBlankHandle = None

  status.message(text, append, color, clickCallback, showNow)

  blankTime = blankAfter
  if blankAfter is None:
    import preferences
    from chimera.replyobj import REPLY_PREFERENCES, STATUS_CLEARING
    blankTime = preferences.get(REPLY_PREFERENCES, STATUS_CLEARING)
  if blankTime != 0:
    if not followWith:
    	followTime = 0
    _statusBlankHandle = status.frame.after(1000 * blankTime, lambda:
			show_message(followWith, blankAfter=followTime))

# -----------------------------------------------------------------------------
#

def tint(template, color, master):
  from PIL import Image, ImageTk
  img = Image.new("RGB", template.size, color)
  img.paste(template, None, template)
  return ImageTk.PhotoImage(img, master=master)

def remove_alpha(template, master):
  from PIL import Image, ImageTk
  r, g, b = master.winfo_rgb(master["background"])
  rgb = r / 255, g / 255, b / 255
  img = Image.new("RGB", template.size, rgb)
  img.paste(template, None, template)
  return ImageTk.PhotoImage(img, master=master)
