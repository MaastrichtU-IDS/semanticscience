# -----------------------------------------------------------------------------
# Dialog for convolving volume data with a Gaussian.
#
import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Volume_Filter_Dialog(ModelessDialog):

  title = 'Volume Filter'
  name = 'volume filter'
  buttons = ('Filter', 'Options', 'Close',)
  help = 'ContributedSoftware/volumeviewer/gaussian.html'
  
  def fillInUI(self, parent):

    self.filter_widgets = fw = []

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()

    parent.columnconfigure(0, weight=1)         # Allow scalebar to expand.
    
    row = 0

    import Tkinter
    from CGLtk import Hybrid

    self.gaussian = 'Gaussian'
    self.median = 'Median 3x3x3'
    self.bin = 'Bin'
    self.laplacian = 'Laplacian'
    self.fourier = 'Fourier Transform'
    self.scale = 'Scale'
    ft = Hybrid.Option_Menu(parent, 'Filter type:',
                            self.gaussian, self.median, self.bin,
                            self.laplacian, self.fourier, self.scale)
    ft.button.configure(indicatoron = False)
    ft.frame.grid(row = row, column = 0, sticky = 'w')
    row += 1
    self.filter_type = ft.variable
    ft.add_callback(self.filter_type_changed_cb)
    
    ws = Hybrid.Scale(parent, 'Width ', 1.0, 10.0, 0.0, 1.0)
    ws.frame.grid(row = row, column = 0, sticky = 'ew')
    row += 1
    ws.callback(self.filter_parameter_changed_cb)
    ws.entry.bind('<KeyPress-Return>', self.filter_cb)
    self.sdev = ws
    Hybrid.Balloon_Help(ws.label, 'Width is one standard deviation.',
                        delay = 0.5)
    fw.append((self.gaussian, ws.frame))
    
    mi = Hybrid.Scale(parent, 'Iterations ', 0, 5, 1, 1, 2)
    mi.frame.grid(row = row, column = 0, sticky = 'ew')
    row += 1
    mi.callback(self.filter_parameter_changed_cb)
    mi.entry.bind('<KeyPress-Return>', self.filter_cb)
    self.median_iterations = mi
    fw.append((self.median, mi.frame))

    bs = Hybrid.Entry(parent, 'Bin size', 5, '2')
    bs.frame.grid(row = row, column = 0, sticky = 'w')
    row += 1
    self.binsize = bs.variable
    bs.entry.bind('<KeyPress-Return>', self.filter_cb)
    fw.append((self.bin, bs.frame))

    sf = Tkinter.Frame(parent)
    sf.grid(row = row, column = 0, sticky = 'w')
    row += 1
    fw.append((self.scale, sf))

    sh = Hybrid.Entry(sf, 'Shift', 5, '0')
    sh.frame.grid(row = 0, column = 0, sticky = 'w')
    self.shift = sh.variable
    sh.entry.bind('<KeyPress-Return>', self.filter_cb)

    sc = Hybrid.Entry(sf, 'Scale', 5, '1')
    sc.frame.grid(row = 0, column = 1, sticky = 'w')
    self.scale_factor = sc.variable
    sc.entry.bind('<KeyPress-Return>', self.filter_cb)

    vt = Hybrid.Option_Menu(sf, 'Value type', 'same', 'int8', 'uint8', 'int16', 'uint16', 'int32', 'uint32', 'float32', 'float64')
    vt.frame.grid(row = 0, column = 2, sticky = 'w')
    self.value_type = vt.variable

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
 
    sr = Hybrid.Checkbutton(opf, 'Displayed subregion only', True)
    sr.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.use_subregion = sr.variable

    ss = Hybrid.Checkbutton(opf, 'Displayed subsampling only', False)
    ss.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.use_step = ss.variable

    ta = Hybrid.Checkbutton(opf, 'Adjust threshold for constant volume', True)
    ta.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.adjust_thresholds = ta.variable

    iu = Hybrid.Checkbutton(opf, 'Immediate update', False)
    iu.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.immediate_update = iu.variable

    self.filter_type_changed_cb()
    self.set_scale_range(initial = True)

  # ---------------------------------------------------------------------------
  #
  def filter_type_changed_cb(self):

    # Display parameter widgets for chosen filter type.
    ftype = self.filter_type.get()
    for ft, w in self.filter_widgets:
      if ft == ftype:
        w.grid()
      else:
        w.grid_remove()
      
  # ---------------------------------------------------------------------------
  #
  def Filter(self):

    self.filter_cb()
    self.set_scale_range()

  # ---------------------------------------------------------------------------
  #
  def filter_cb(self, event = None):

    from VolumeViewer import active_volume
    v = active_volume()
    if v is None:
      return

    ftype = self.filter_type.get()

    uv,r,params = self.unfiltered_volume(v, ftype)
    if uv:
      self.update_filtered_volume(v, ftype)
    else:
      step, subreg = self.step_and_subregion()
      try:
        fv, params = self.apply_filter(v, ftype, step, subreg)
      except MemoryError:
        from chimera.replyobj import warning
        warning('Out of memory calculating %s filter of %s' % (ftype, v.name))
        return

      if fv is None:
        return

      self.update_thresholds(fv, v)
      fv.show()
      r = v.subregion(step, subreg)
      fv.filtered_volume = (ftype, v, r, params)

  # ---------------------------------------------------------------------------
  #
  def step_and_subregion(self):
    
      if self.use_step.get():
        step = None
      else:
        step = 1
      if self.use_subregion.get():
        subregion = None
      else:
        subregion = 'all'
      return step, subregion

  # ---------------------------------------------------------------------------
  #
  def apply_filter(self, v, ftype, step, subreg):

    if ftype == self.gaussian:
      sd = self.sdev.value(default = None)
      if sd is None:
        return None, None
      params = [sd]
      from chimera import CancelOperation, tasks
      task = tasks.Task('Gaussian filter %s' % v.name, modal = True)
      from gaussian import gaussian_convolve
      try:
        fv = gaussian_convolve(v, sd, step, subreg, task = task)
      except CancelOperation:
        return None, None
      task.finished()
    elif ftype == self.median:
      i = int(self.median_iterations.value(default = -1))
      if i < 0:
        return None, None
      params = [i]
      from median import median_filter
      fv = median_filter(v, 3, i, step, subreg)
    elif ftype == self.bin:
      b = self.bin_size()
      if b is None:
        return None, None
      params = [b]
      from bin import bin
      fv = bin(v, b, step, subreg)
    elif ftype == self.laplacian:
      from laplace import laplacian
      fv = laplacian(v, step, subreg)
      params = []
    elif ftype == self.fourier:
      from fourier import fourier_transform
      fv = fourier_transform(v, step, subreg)
      params = []
    elif ftype == self.scale:
      s, o, t = self.scale_parameters()
      from scale import scaled_volume
      fv = scaled_volume(v, s, o, t, step, subreg)
      params = [s,o,t]
    else:
      return None, None

    return fv, params

  # ---------------------------------------------------------------------------
  #
  def filter_parameter_changed_cb(self, event = None):

    if not self.immediate_update.get():
      return

    from VolumeViewer import active_volume
    fv = active_volume()
    if fv is None:
      return

    self.update_filtered_volume(fv, self.filter_type.get())

  # ---------------------------------------------------------------------------
  #
  def update_filtered_volume(self, fv, ftype):

    v, region, params = self.unfiltered_volume(fv, ftype)
    if v is None:
      return

    if ftype == self.gaussian:
      sd = self.sdev.value(default = None)
      if sd is None:
        return
      from gaussian import gaussian_grid
      g = gaussian_grid(v, sd, region = region)
      params[0] = sd
    elif ftype == self.median:
      i = int(self.median_iterations.value(default = -1))
      if i < 0:
        return
      from median import median_grid
      if i > params[0]:
        g = median_grid(fv, 3, i - params[0], region = fv.region)
      else:
        g = median_grid(v, 3, i, region = region)
      params[0] = i
    elif ftype == self.bin:
      b = self.bin_size()
      if b is None:
        return
      params[0] = b
      from bin import bin_grid
      g = bin_grid(v, b, region = region)
    elif ftype == self.scale:
      s, o, t = self.scale_parameters()
      from scale import scaled_grid
      g = scaled_grid(v, s, o, t, region = region)
      params[:] = (s,o,t)
    else:
      return

    a = self.adjust_thresholds.get()
    if a:
      srank, sorank = self.level_ranks(fv)
    if g.step != fv.data.step:
      nr = [a/b for a,b in zip(fv.data.step, g.step)]
    else:
      nr = None
    from VolumeViewer.volume import replace_data
    replace_data(fv.data, g)
    if nr:
      # Voxel size changed, keep region same size.
      ijk_min, ijk_max, ijk_step = fv.region
      ijk_min = [round(s*i) for s,i in zip(nr, ijk_min)]
      ijk_max = [round(s*(i+1)-1) for s,i in zip(nr, ijk_max)]
      fv.new_region(ijk_min, ijk_max, ijk_step)
    if a:
      self.set_level_ranks(fv, srank, sorank)

    fv.show()

  # ---------------------------------------------------------------------------
  #
  def bin_size(self):

      try:
        b = [int(x) for x in self.binsize.get().split()]
      except ValueError:
        return None
      if len(b) == 1:
        b = [b[0], b[0], b[0]]
      if len(b) != 3 or b[0] < 1 or b[1] < 1 or b[2] < 1:
        return None
      return b

  # ---------------------------------------------------------------------------
  #
  def scale_parameters(self):

    from CGLtk.Hybrid import float_variable_value
    s = float_variable_value(self.scale_factor, 1.0)
    o = float_variable_value(self.shift, 0.0)
    import numpy
    t = getattr(numpy, self.value_type.get(), None)
    return s,o,t

  # ---------------------------------------------------------------------------
  #
  def unfiltered_volume(self, fv, ftype):

    if hasattr(fv, 'filtered_volume'):
      ft, v, region, params = fv.filtered_volume
      if ft == ftype and not v.__destroyed__:
        return v, region, params
    return None, None, None

  # ---------------------------------------------------------------------------
  # Record threshold level ranks for automatic threshold adjustment that
  # preserves enclosed volume.
  #
  def level_ranks(self, v):

    vs = v.matrix_value_statistics()
    srank = [vs.data_value_rank(lev) for lev in v.surface_levels]
    sorank = [(vs.data_value_rank(lev), b) for lev,b in v.solid_levels]
    return srank, sorank

  # ---------------------------------------------------------------------------
  #
  def set_level_ranks(self, v, srank, sorank):

    vs = v.matrix_value_statistics()
    slev = [vs.rank_data_value(r) for r in srank]
    solev = [(vs.rank_data_value(r), b) for r,b in sorank]
    v.set_parameters(surface_levels = slev, solid_levels = solev)

  # ---------------------------------------------------------------------------
  #
  def update_thresholds(self, gv, v):

    if self.adjust_thresholds.get():
      srank, sorank = self.level_ranks(v)
      self.set_level_ranks(gv, srank, sorank)

  # ---------------------------------------------------------------------------
  #
  def set_scale_range(self, initial = False):

    from VolumeViewer import active_volume
    v = active_volume()
    if v is None:
      return

    s = min(v.data.step)
    if s > 0:
      self.sdev.set_range(0.5*s, 5*s)
      if initial:
        self.sdev.set_value(s, invoke_callbacks = False)
    
  # ---------------------------------------------------------------------------
  #
  def Options(self):

    self.options_panel.set(not self.options_panel.get())
    
# -----------------------------------------------------------------------------
#
def volume_filter_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Volume_Filter_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_volume_filter_dialog():

  from chimera import dialogs
  return dialogs.display(Volume_Filter_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Volume_Filter_Dialog.name, Volume_Filter_Dialog,
                 replace = True)
