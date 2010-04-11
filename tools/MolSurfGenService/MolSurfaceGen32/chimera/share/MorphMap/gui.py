# -----------------------------------------------------------------------------
# User interface to interpolate between two volume data sets.
#
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Morph_Map_Dialog(ModelessDialog):

  title = 'Morph Map'
  name = 'morph map'
  buttons = ('Play', 'Record', 'Options', 'Close',)
  help = 'ContributedSoftware/morphmap/morphmap.html'
  
  def fillInUI(self, parent ):

    self.morph_maps = {}        # Writable maps for pairs of end-point maps.
    self.default_f_range = (0.0, 1.0, 0.1)

    self.play_stop_button = self.buttonWidgets['Play']
    
    import Tkinter
    from CGLtk import Hybrid
    
    frame = parent
    frame.columnconfigure(0, weight = 1)
    row = 0

    h = Tkinter.Label(parent, text = 'Interpolate between two maps')
    h.grid(row = row, column = 0, sticky = 'w')
    row += 1

    from VolumeViewer import volume_list, Volume_Menu
    vlist = volume_list()
    vm1 = Volume_Menu(parent, 'First map', open_button = True,
                      show_on_open = True)
    vm1.frame.grid(row = row, column = 0, sticky = 'w')
    if len(vlist) >= 1:
      vm1.set_volume(vlist[0])
    row += 1
    self.map_menu_1 = vm1

    vm2 = Volume_Menu(parent, 'Second map', open_button = True,
                      show_on_open = True)
    vm2.frame.grid(row = row, column = 0, sticky = 'w')
    if len(vlist) >= 2:
      vm2.set_volume(vlist[1])
    row += 1
    self.map_menu_2 = vm2

    self.scale = Hybrid.Scale(parent, 'Fraction ', 0.0, 1.0, 0.01, 0)
    self.scale.frame.grid(row = row, column = 0, sticky = 'ew')
    self.scale.callback(self.scale_changed_cb)
    self.scale.entry.bind('<KeyPress-Return>', self.scale_changed_cb)
    row += 1

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

    fr = Tkinter.Frame(opf)
    fr.grid(row=orow, column=0, sticky='w')
    orow += 1

    fmin, fmax, fstep = self.default_f_range
    fn = Hybrid.Entry(fr, 'Movie start ', 5, fmin)
    fn.frame.grid(row=0, column=0, sticky='w')
    fx = Hybrid.Entry(fr, ' end ', 5, fmax)
    fx.frame.grid(row=0, column=1, sticky='w')
    fs = Hybrid.Entry(fr, ' step ', 5, fstep)
    fs.frame.grid(row=0, column=2, sticky='w')
    self.f_range_variables = (fn.variable, fx.variable, fs.variable)

    um = Hybrid.Checkbutton(opf, 'Undisplay original maps', True)
    um.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.undisplay_maps = um.variable

    mu = Hybrid.Checkbutton_Entries(opf, False, 'Multiplier for second map',
                                    (4, '1.0'))
    mu.frame.grid(row=orow, column=0, sticky='w')
    orow += 1
    self.use_multiplier, self.map_2_multiplier = mu.variables

    ta = Hybrid.Checkbutton(opf, 'Adjust threshold for constant volume',
                            False)
    ta.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.adjust_thresholds = ta.variable

    am = Hybrid.Checkbutton(opf, 'Add to first map instead of interpolating',
                            False)
    am.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.add_maps = am.variable
    am.callback(self.add_mode_cb)

    rt = Hybrid.Checkbutton(opf, 'Round trip when recording movie', True)
    rt.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.roundtrip = rt.variable

    #
    # Specify a label width so dialog is not resized for long messages.
    #
    msg = Tkinter.Label(parent, width = 40, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.message_label = msg

  # ---------------------------------------------------------------------------
  #
  def message(self, text):

    self.message_label['text'] = text
    self.message_label.update_idletasks()

  # ---------------------------------------------------------------------------
  #
  def scale_changed_cb(self, event = None):

    im = self.interpolated_map(create = False)
    if im is None:
      return

    # Update scale range.
    fmin, fmax, fstep = self.f_range()
    self.scale.set_range(fmin, fmax, fstep)

    f = self.scale.value(default = self.default_f_range[0])
    im.interpolate(f)

  # ---------------------------------------------------------------------------
  #
  def interpolated_map(self, create = True):

    v1 = self.map_menu_1.volume()
    v2 = self.map_menu_2.volume()
    if v1 is None or v2 is None:
      self.message('Need to select two volume data sets.')
      return None

    im = None
    mm = self.morph_maps
    if (v1,v2) in mm:
      im = mm[(v1,v2)]
      # Check that volume is still opened in volume viewer.
      from VolumeViewer import volume_list
      if not im.result in volume_list():
        im = None
      else:
        # Check that map size matches current v1 subregion
        ijk_min, ijk_max = v1.region[:2]
        v1_size = tuple(map(lambda a,b: b-a+1, ijk_min, ijk_max))
        if im.result.data.size != v1_size:
          im = None

    if not create and im is None:
        return None

    sf = (1.0, self.second_map_multiplier())
    adj = self.adjust_thresholds.get()
    am = self.add_maps.get()
    if im is None:
      if v1 == v2:
        self.message('Two maps are the same.')
        return None
      if v1.data.size != v2.data.size:
        self.message('Map sizes differ.')
        return None
      import morph
      im = morph.Interpolated_Map((v1,v2), scale_factors = sf,
                                  adjust_thresholds = adj,
                                  add_mode = am,
                                  subregion = v1.region[:2])
      mm[(v1,v2)] = mm[(v2,v1)] = im
    else:
      im.adjust_thresholds = adj
      im.add_mode = am
      im.scale_factors = sf

    if self.undisplay_maps.get():
      v1.unshow()
      v2.unshow()

    self.message('')
    
    return im

  # ---------------------------------------------------------------------------
  #
  def second_map_multiplier(self):

    if self.use_multiplier.get():
      from CGLtk.Hybrid import float_variable_value
      m = float_variable_value(self.map_2_multiplier, 1.0)
    else:
      m = 1.0
    return m
    
  # ---------------------------------------------------------------------------
  # Adjust scale range to (0,1) for interpolate mode and (-1,1) for add mode.
  #
  def add_mode_cb(self):

    fmin, fmax, fstep = self.f_range()
    add = self.add_maps.get()
    if add and (fmin,fmax) == (0,1):
      fmin = -1.0
    elif not add and (fmin,fmax) == (-1,1):
      fmin = 0.0
    else:
      return
    self.f_range_variables[0].set(fmin)
    self.scale.set_range(fmin,fmax,fstep)

  # ---------------------------------------------------------------------------
  #
  def Play(self):

    playing = (self.play_stop_button['text'] == 'Stop')
    im = self.interpolated_map(create = not playing)
    if im is None:
      btext = 'Play'
    elif im.playing():
      btext = 'Play'
      im.stop_playing()
    else:
      btext = 'Stop'
      fmin, fmax, fstep = self.f_range()
      f = self.scale.value(default = fmin)
      im.play(f, fmin, fmax, fstep, self.update_f)
    self.play_stop_button['text'] = btext

  # ---------------------------------------------------------------------------
  #
  def update_f(self, f):

    self.scale.set_value(f, invoke_callbacks = False)
    
  # ---------------------------------------------------------------------------
  #
  def f_range(self):

    from CGLtk.Hybrid import float_variable_value
    dfmin, dfmax, dfstep = self.default_f_range
    vfmin, vfmax, vfstep = self.f_range_variables
    fmin = float_variable_value(vfmin, dfmin)
    fmax = float_variable_value(vfmax, dfmax)
    fstep = float_variable_value(vfstep, dfstep)
    return fmin, fmax, fstep

  # ---------------------------------------------------------------------------
  #
  def Record(self):

    im = self.interpolated_map()
    if im:
      def save_movie_cb():
        Save_Movie_Dialog().enter()
      fmin, fmax, fstep = self.f_range()
      rt = self.roundtrip.get()
      im.record(fmin, fmax, fstep, self.update_f, rt, save_movie_cb)
    
  # ---------------------------------------------------------------------------
  #
  def Options(self):

    self.options_panel.set(not self.options_panel.get())

# -----------------------------------------------------------------------------
#
from OpenSave import SaveModeless
class Save_Movie_Dialog(SaveModeless):
  title = 'Save Movie'
  help = 'ContributedSoftware/morphmap/morphmap.html'
  dismiss = 'Cancel'

  def __init__(self):

    self.default_bit_rate = 6000

    from MovieRecorder import RecorderGUI
    filters = map(lambda f: (f[0], '*.%s' % f[1], '.%s' % f[1]), 
                  RecorderGUI.formats)
    SaveModeless.__init__(self, clientPos = 's', clientSticky = 'w',
                          filters = filters, historyID = "MorphMap")

  # ---------------------------------------------------------------------------
  #
  def fillInUI(self, parent):

    SaveModeless.fillInUI(self, parent)

    from CGLtk import Hybrid
    br = Hybrid.Entry(self.clientArea, 'Bit rate (Kb/sec):', 6,
                      self.default_bit_rate)
    br.frame.grid(row = 0, column = 0, sticky = 'w')
    self.bit_rate = br.variable

  # ---------------------------------------------------------------------------
  #
  def Apply(self):

    path, format = self.getPathsAndTypes()[0]
    
    from MovieRecorder import RecorderGUI
    for fmt, f in RecorderGUI.command_formats.items():
      if f[0] == format:
        break
    from CGLtk.Hybrid import float_variable_value
    bit_rate = float_variable_value(self.bit_rate, self.default_bit_rate)

    from chimera import runCommand
    runCommand('movie encode mformat %s bitrate %f output "%s"'
               % (fmt, bit_rate, path))

  # ---------------------------------------------------------------------------
  #
  def Cancel(self):

    from chimera import runCommand
    from Midas import MidasError
    try:
      runCommand('movie reset')
    except MidasError:
      pass      # Suppress error when user already reset movie by other means.
    self.Close()
  
# -----------------------------------------------------------------------------
#
def morph_map_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Morph_Map_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_morph_map_dialog():

  from chimera import dialogs
  return dialogs.display(Morph_Map_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Morph_Map_Dialog.name, Morph_Map_Dialog, replace = True)
