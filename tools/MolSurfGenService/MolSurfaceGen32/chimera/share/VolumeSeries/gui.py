# -----------------------------------------------------------------------------
# Dialog for controlling display of volume series.
#

import chimera
from chimera.baseDialog import ModelessDialog
import VolumeSeries

# -----------------------------------------------------------------------------
#
class Volume_Series_Dialog(ModelessDialog):

  title = 'Volume Series'
  name = 'volume series'
  buttons = ('Open...', 'Close Series', 'Close',)
  help = ('volume_series.html', VolumeSeries)
  
  def fillInUI(self, parent):

    self.series = []
    self.timer_id = {}             # For delaying update of volume dialog
    self.play_handler = None
    self.step = 1                  # +1 or -1 to play forwards/backwards
    self.rendered_times = []       # For limiting cached renderings
    self.rendered_times_table = {}
    self.new_marker_handler = None
    self.last_rendering_walltime = None

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()

    parent.columnconfigure(0, weight=1)         # Allow scalebar to expand.
    
    row = 0

    import Tkinter
    from CGLtk import Hybrid
    from chimera import widgets

    dm = Hybrid.Option_Menu(parent, 'Data ', 'All')
    dm.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    dm.add_callback(self.series_menu_cb)
    self.series_menu = dm

    tf = Tkinter.Frame(parent)
    tf.grid(row = row, column = 0, sticky = 'ew')
    tf.columnconfigure(0, weight=1)         # Allow scalebar to expand.
    row = row + 1
    
    ts = Hybrid.Scale(tf, 'Time ', 0, 100, 1, 0)
    ts.frame.grid(row = 0, column = 0, sticky = 'ew')
    ts.callback(self.time_changed_cb)
    ts.entry.bind('<KeyPress-Return>', self.time_changed_cb)
    self.time = ts

    pb = Tkinter.Button(tf, text = 'Play', command = self.play_stop_cb)
    pb.grid(row = 0, column = 1, sticky = 'w')
    self.play_stop_button = pb

    pd = Hybrid.Radiobutton_Row(parent, 'Play direction',
                                ('forward', 'backward', 'oscillate'),
                                self.play_direction_cb)
    pd.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.play_direction = pd.variable
    self.play_direction.set('forward')
    
    ps = Hybrid.Checkbutton_Entries(parent, False, 'Maximum playback speed',
                                    (2, '5'), ' steps per second')
    ps.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.limit_frame_rate = ps.variables[0]
    self.maximum_frame_rate = ps.variables[1]

    nt = Hybrid.Checkbutton(parent, 'Normalize threshold levels', 0)
    nt.button.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.normalize_thresholds = nt.variable

    cr = Hybrid.Checkbutton_Entries(parent, False, 'Cache', (3, '30'),
                                    ' renderings')
    cr.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.cache_renderings = cr.variables[0]
    self.cache_renderings.add_callback(self.rendering_cache_limit_cb)
    self.rendering_cache_limit = cr.variables[1]
    cr.entries[0].bind('<KeyPress-Return>', self.rendering_cache_limit_cb)
    
    vc = Tkinter.Frame(parent)
    vc.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    from VolumeData import data_cache
    csize = data_cache.size / (2 ** 20)
    cs = Hybrid.Entry(vc, 'Data cache size (Mb)', 4, csize)
    cs.frame.grid(row = 0, column = 0, sticky = 'w')
    self.data_cache_size = cs.variable
    cs.entry.bind('<KeyPress-Return>', self.cache_size_cb)

    cu = Tkinter.Button(vc, text = 'Current use', command = self.cache_use_cb)
    cu.grid(row = 0, column = 1, sticky = 'w')

    sm = Hybrid.Checkbutton_Entries(parent, False, 'Show markers', (2, '0'),
                                    'earlier and', (2, '0'), ' later times')
    sm.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.show_markers = sm.variables[0]
    self.show_markers.add_callback(self.show_markers_cb)
    self.preceding_marker_frames = sm.variables[1]
    sm.entries[0].bind('<KeyPress-Return>', self.show_markers_cb)
    self.following_marker_frames = sm.variables[2]
    sm.entries[1].bind('<KeyPress-Return>', self.show_markers_cb)

    cz = Hybrid.Checkbutton_Entries(parent, False, 'Color zone around markers, range', (4, '1.0'))
    cz.frame.grid(row = row, column = 0, sticky = 'w')
    row = row + 1
    self.color_zone = cz.variables[0]
    self.color_zone.add_callback(self.color_zone_cb)
    self.color_range = cz.variables[1]
    cz.entries[0].bind('<KeyPress-Return>', self.color_zone_cb)
    
    #
    # Specify a label width so dialog is not resized for long messages.
    #
    msg = Tkinter.Label(parent, width = 40, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.message_label = msg

    chimera.triggers.addHandler(chimera.CLOSE_SESSION,
				self.close_session_cb, None)
    
  # ---------------------------------------------------------------------------
  #
  def message(self, text):

    self.message_label['text'] = text
    self.message_label.update_idletasks()
    
  # ---------------------------------------------------------------------------
  #
  def series_menu_cb(self, text = None):

    tslist = self.chosen_series()
    if len(tslist) == 0:
      return

    self.time.set_range(0, tslist[0].number_of_times()-1, 1)

  # ---------------------------------------------------------------------------
  #
  def Open(self):

    self.open_cb()

  # ---------------------------------------------------------------------------
  #
  def open_cb(self):

    import openseries
    openseries.open_series_files()
      
  # ---------------------------------------------------------------------------
  #
  def CloseSeries(self):

    for ts in self.chosen_series():
      self.close_series(ts)
      
  # ---------------------------------------------------------------------------
  #
  def close_series(self, ts, close_volumes = True):

    if close_volumes:
      ts.remove_from_volume_viewer()

    i = self.series.index(ts)
    self.series_menu.remove_entry(i+1)

    del self.series[i]

    # Set menu to an open series.
    if len(self.chosen_series()) == 0:
      if self.series:
        ts_name = self.series[0].menu_name
      else:
        ts_name = 'All'
      self.series_menu.variable.set(ts_name)
    
  # ---------------------------------------------------------------------------
  #
  def close_session_cb(self, trigger, a1, a2):

    for s in list(self.series):
      self.close_series(s, close_volumes = False)

  # ---------------------------------------------------------------------------
  #
  def time_changed_cb(self, event = None):

    t = self.time_from_gui()
    if t == None:
      return

    tslist = self.chosen_series()
    tslist = [ts for ts in tslist
    	      if t < ts.number_of_times() and not ts.is_volume_closed(t)]

    for ts in tslist:
      t0 = self.update_rendering_settings(ts, t)
      self.show_time(ts, t)
      if ts.last_shown_time != t:
        self.unshow_time(ts, ts.last_shown_time)
      if t0 != t:
        self.unshow_time(ts, t0)
      ts.last_shown_time = t
      self.update_volume_dialog(ts, t)

    if tslist:
      if self.show_markers.get():
        self.update_marker_display()
      if self.color_zone.get():
        self.color_zone_cb()
      
  # ---------------------------------------------------------------------------
  # Update based on active volume viewer data set if it is part of series,
  # otherwise use previously shown time.
  #
  def update_rendering_settings(self, ts, t):

    t0 = self.volume_viewer_time(ts)
    if t0 == None:
      t0 = ts.last_shown_time

    if t0 != t:
      normalize = self.normalize_thresholds.get()
      ts.copy_display_parameters(t0, t, normalize)
      
    return t0

  # ---------------------------------------------------------------------------
  #
  def volume_viewer_time(self, ts):

    from VolumeViewer import active_volume
    dr = active_volume()
    if dr == None:
      t = None
    else:
      t = ts.data_time(dr.data)
    return t

  # ---------------------------------------------------------------------------
  #
  def show_time(self, ts, t):

    ts.show_time(t)
    self.cache_rendering(ts, t)

  # ---------------------------------------------------------------------------
  #
  def unshow_time(self, ts, t):

    remove_surface = not self.cache_renderings.get()
    ts.unshow_time(t, remove_surface)
    if remove_surface:
      self.uncache_rendering(ts, t)

  # ---------------------------------------------------------------------------
  #
  def cache_rendering(self, ts, t):

    rtt = self.rendered_times_table
    if not (ts,t) in rtt:
      rtt[(ts,t)] = 1
      self.rendered_times.append((ts,t))
    self.trim_rendering_cache()

  # ---------------------------------------------------------------------------
  #
  def trim_rendering_cache(self):

    if self.cache_renderings.get():
      try:
        climit = max(1, int(self.rendering_cache_limit.get()))
      except:
        return
    else:
      climit = 1

    rt = self.rendered_times
    rtt = self.rendered_times_table
    k = 0
    while len(rtt) > climit and k < len(rt):
      ts, t = rt[k]
      if ts.time_shown(t):
        k += 1
      else:
        ts.unshow_time(t, remove_surface = True)
        del rtt[(ts,t)]
        del rt[k]

  # ---------------------------------------------------------------------------
  #
  def rendering_cache_limit_cb(self, arg = None):

    self.trim_rendering_cache()
    
  # ---------------------------------------------------------------------------
  #
  def uncache_rendering(self, ts, t):

    rtt = self.rendered_times_table
    if (ts,t) in rtt:
      del rtt[(ts,t)]
      self.rendered_times.remove((ts,t))

  # ---------------------------------------------------------------------------
  #
  def show_markers_cb(self, event = None):

    show = self.show_markers.get()
    mset = self.marker_set()
    if show:
      if mset:
        self.update_marker_display(mset)
      else:
        self.show_path_tracer_dialog()
    elif mset:
      mset.show_markers(False)
        
    self.register_new_marker_handler(show)

  # ---------------------------------------------------------------------------
  #
  def marker_set(self):

    import VolumePath
    d = VolumePath.volume_path_dialog(create = False)
    if d == None:
      return None
    return d.active_marker_set

  # ---------------------------------------------------------------------------
  #
  def update_marker_display(self, mset = None):

    if mset == None:
      mset = self.marker_set()
      if mset == None:
        return

    fmin, fmax = self.marker_frame_range()
    if fmin == None or fmax == None:
      return

    mset.show_model(True)
    for m in mset.markers():
      m.show(label_value_in_range(m.note_text, fmin, fmax))

  # ---------------------------------------------------------------------------
  #
  def current_markers_and_links(self):

    mset = self.marker_set()
    if mset == None:
      return [], []

    t = self.time_from_gui()
    if t == None:
      return [], []
    tstr = str(t)

    mlist = filter(lambda m: m.note_text == tstr, mset.markers())
    llist = filter(lambda l: l.marker1.note_text == tstr and l.marker2.note_text == tstr, mset.links())

    return mlist, llist

  # ---------------------------------------------------------------------------
  #
  def show_path_tracer_dialog(self):

    import VolumePath
    VolumePath.show_volume_path_dialog()
    if self.marker_set() == None and self.series:
      VolumePath.Marker_Set(self.series[0].menu_name + ' markers')

  # ---------------------------------------------------------------------------
  #
  def register_new_marker_handler(self, register):

    if register:
      if self.new_marker_handler == None:
        from chimera import triggers
        h = triggers.addHandler('Atom', self.new_marker_cb, None)
        self.new_marker_handler = h
    else:
      if self.new_marker_handler:
        from chimera import triggers
        triggers.deleteHandler('Atom', self.new_marker_handler)
        self.new_marker_handler = None
          
  # -------------------------------------------------------------------------
  # Add current time label to new markers.
  #
  def new_marker_cb(self, trigger, user_data, changes):

    t = self.time_from_gui()
    if t == None:
      return

    mset = self.marker_set()
    if mset == None:
      return
    
    for a in changes.created:
      m = mset.atom_marker(a)
      if m:
        m.set_note('%d' % t)
        
  # ---------------------------------------------------------------------------
  #
  def marker_frame_range(self):

    t = self.time_from_gui()
    if t == None:
      return None, None
    from CGLtk.Hybrid import integer_variable_value
    fmin = t - integer_variable_value(self.preceding_marker_frames,
                                      default = 0, minimum = 0)
    fmax = t + integer_variable_value(self.following_marker_frames,
                                      default = 0, minimum = 0)
    return fmin, fmax
  
  # ---------------------------------------------------------------------------
  #
  def play_stop_cb(self):

    from chimera import triggers
    if self.play_handler:
      triggers.deleteHandler('new frame', self.play_handler)
      self.play_handler = None
      self.play_stop_button['text'] = 'Play'
    else:
      h = triggers.addHandler('new frame', self.next_time_cb, None)
      self.play_handler = h
      self.play_stop_button['text'] = 'Stop'

  # ---------------------------------------------------------------------------
  #
  def next_time_cb(self, trigger_name, call_data, trigger_data):

    if self.delay_next_frame():
      return
      
    t = self.time_from_gui()
    if t == None:
      return

    tslist = self.chosen_series()
    if len(tslist) == 0:
      return
    nt = tslist[0].number_of_times()
    if nt == 0:
      return

    if self.play_direction.get() == 'oscillate':
      if self.step > 0:
        if t == nt - 1:
          self.step = -1
      elif t == 0:
        self.step = 1

    t = (t + self.step) % nt

    self.time.set_value(t)

  # ---------------------------------------------------------------------------
  #
  def delay_next_frame(self):

    if not self.limit_frame_rate.get():
      return False

    t0 = self.last_rendering_walltime
    import time
    t = time.time()
    if t0 != None:
      from CGLtk.Hybrid import float_variable_value
      r = float_variable_value(self.maximum_frame_rate)
      if r != None and (t-t0)*r < 1:
        return True
      
    self.last_rendering_walltime = t
    return False

  # ---------------------------------------------------------------------------
  #
  def play_direction_cb(self):

    dir = self.play_direction.get()
    self.step = {'forward':1, 'backward':-1, 'oscillate':1}[dir]
      
  # ---------------------------------------------------------------------------
  #
  def cache_size_cb(self, event):

    from CGLtk.Hybrid import float_variable_value
    size_mb = float_variable_value(self.data_cache_size, None)
    if size_mb:
      from VolumeData import data_cache
      data_cache.resize(size_mb * (2**20))

  # ---------------------------------------------------------------------------
  #
  def cache_use_cb(self):

    from VolumeData import memoryuse
    memoryuse.show_memory_use_dialog()
    
  # ---------------------------------------------------------------------------
  #
  def color_zone_cb(self, event = None):

    t = self.time_from_gui()
    if t is None:
      return

    tslist = self.chosen_series()
    tslist = [ts for ts in tslist if not ts.surface_model(t) is None]

    for ts in tslist:
      if self.color_zone.get():
	mlist, llist = self.current_markers_and_links()
	if mlist or llist:
	  from CGLtk.Hybrid import float_variable_value
	  r = float_variable_value(self.color_range)

	  atoms = map(lambda m: m.atom, mlist)
	  bonds = map(lambda l: l.bond, llist)
	  model = ts.surface_model(t)
	  xform_to_surface = model.openState.xform.inverse()
	  from ColorZone import points_and_colors, color_zone
	  points, point_colors = points_and_colors(atoms, bonds,
						   xform_to_surface)
	  if hasattr(model, 'series_zone_coloring'):
	    zp, zpc, zr = model.series_zone_coloring
	    from numpy import all
	    if all(zp == points) and all(zpc == point_colors) and zr == r:
	      return        # No change in coloring.
	  model.series_zone_coloring = (points, point_colors, r)
	  color_zone(model, points, point_colors, r, auto_update = True)
      else:
	for t in range(ts.number_of_times()):
	  model = ts.surface_model(t)
	  if model and hasattr(model, 'series_zone_coloring'):
	    from ColorZone import uncolor_zone
	    uncolor_zone(model)
	    delattr(model, 'series_zone_coloring')
      
  # ---------------------------------------------------------------------------
  #
  def update_volume_dialog(self, ts, t, delay_seconds = 1):

    tid = self.timer_id
    if delay_seconds == 0:
      ts.show_time_in_volume_dialog(t)
      if ts in tid:
        del tid[ts]
    else:
      w = self.toplevel_widget
      if ts in tid:
        w.after_cancel(tid[ts])
      delay_msec = 1000 * delay_seconds
      tid[ts] = w.after(delay_msec, self.update_volume_dialog, ts, t, 0)
    
  # ---------------------------------------------------------------------------
  #
  def time_from_gui(self):
 
    time = self.time.value()
    if time == None:
      self.message('Time is set to a non-numeric value')
      return None
    else:
      self.message('')
    time = int(time)
    return time
    
  # ---------------------------------------------------------------------------
  #
  def add_volume_series(self, ts):

    ts.show_in_volume_viewer()

    ts.last_shown_time = 0

    mname = self.series_menu_name(ts.name)
    ts.menu_name = mname
    self.series.append(ts)
    sm = self.series_menu
    sm.add_entry(mname)
    sm.variable.set(mname)
      
  # ---------------------------------------------------------------------------
  # Choose unique menu name for series.
  #
  def series_menu_name(self, sname):

    mname = sname
    mnames = set([ts.menu_name for ts in self.series])
    suffix = 2
    while mname in mnames:
      mname = '%s %d' % (sname, suffix)
      suffix += 1
    return mname
      
  # ---------------------------------------------------------------------------
  #
  def chosen_series(self):

    sm = self.series_menu
    name = sm.variable.get()
    if name == 'All':
      return list(self.series)          # Copy the list.
    name_to_series = {}
    for ts in self.series:
      name_to_series[ts.menu_name] = ts
    if name and name in name_to_series:
      ts = [name_to_series[name]]
    else:
      ts = []
    return ts
  
# -----------------------------------------------------------------------------
#
def label_value_in_range(text, imin, imax):

  try:
    i = int(text)
  except:
    return False
  return i >= imin and i <= imax
  
# -----------------------------------------------------------------------------
#
def add_volume_series(ts):

    import gui
    d = gui.volume_series_dialog(create = True)
    d.add_volume_series(ts)
  
# -----------------------------------------------------------------------------
#
def volume_series_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Volume_Series_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_volume_series_dialog():

  from chimera import dialogs
  return dialogs.display(Volume_Series_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Volume_Series_Dialog.name, Volume_Series_Dialog,
                 replace = True)
