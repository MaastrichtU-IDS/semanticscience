# -----------------------------------------------------------------------------
# Dialog for fitting molecules or maps in maps.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Fit_Map_Dialog(ModelessDialog):

  title = 'Fit in Map'
  name = 'fit in map'
  buttons = ('Fit', 'Halt', 'Undo', 'Redo', 'Options', 'Results', 'Close')
  help = 'ContributedSoftware/fitmaps/fitmaps.html'
  
  def fillInUI(self, parent):

    self.requested_halt = False
    self.xform_handler = None
    self.last_relative_xform = None
    
    t = parent.winfo_toplevel()
    self.toplevel_widget = t
    t.withdraw()

    parent.columnconfigure(0, weight = 1)
    row = 0

    import Tkinter
    from CGLtk import Hybrid
    from VolumeViewer import Volume_Menu

    ff = Tkinter.Frame(parent)
    ff.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    from chimera.widgets import ModelOptionMenu
    om = ModelOptionMenu(ff, labelpos = 'w', label_text = 'Fit ',
                         listFunc = fit_object_models,
                         sortFunc = compare_fit_objects,
                         command = self.object_chosen_cb)
    om.grid(row = 0, column = 0, sticky = 'w')
    self.object_menu = om

    fm = Volume_Menu(ff, ' in map ')
    fm.frame.grid(row = 0, column = 1, sticky = 'w')
    self.map_menu = fm

    gf = Tkinter.Frame(parent)
    gf.grid(row = row, column = 0, sticky = 'w')
    row += 1

    cl = Tkinter.Label(gf, text = 'Correlation')
    cl.grid(row = 0, column = 0, sticky = 'w')
    cv = Tkinter.Label(gf, width = 6, anchor = 'w',
                       relief=Tkinter.SUNKEN, borderwidth = 2)
    cv.grid(row = 0, column = 1, padx = 5, sticky = 'w')
    self.corr_label = cv
    al = Tkinter.Label(gf, text = 'Average map value')
    al.grid(row = 0, column = 2, sticky = 'w')
    av = Tkinter.Label(gf, width = 6, anchor = 'w',
                       relief=Tkinter.SUNKEN, borderwidth = 2)
    av.grid(row = 0, column = 3, padx = 5, sticky = 'w')
    self.ave_label = av
    ub = Tkinter.Button(gf, text = 'Update', command = self.update_metric_cb)
    ub.grid(row = 0, column = 4, sticky = 'w')

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

    ru = Hybrid.Checkbutton(opf, 'Real-time correlation / average update',
                            False)
    ru.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.realtime_update = ru.variable
    ru.callback(self.realtime_cb)

    sm = Hybrid.Checkbutton_Entries(opf, False,
                                    'Use map simulated from atoms, resolution ',
                                    (4, ''))
    sm.frame.grid(row = orow, column = 0, sticky = 'nw')
    orow += 1
    self.simulate_map, self.map_resolution = sm.variables
    self.simulate_map.add_callback(self.simulate_map_cb)
    sm.entries[0].bind('<KeyPress-Return>', self.simulate_resolution_cb)

    dt = Hybrid.Checkbutton(opf, 'Use only data above contour level from first map', True)
    dt.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    dt.button['state'] = 'disabled'
    self.limit_data = dt
    self.above_threshold = dt.variable

    opt = Hybrid.Radiobutton_Row(opf, 'Optimize ', ('overlap', 'correlation'))
    opt.frame.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.optimize = opt.variable
    self.opt_widget = opt

    cam = Hybrid.Checkbutton(opf, 'Correlation calculated about mean data value', False)
    cam.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    cam.button['state'] = 'disabled'
    self.cam_widget = cam
    self.corr_about_mean = cam.variable

    al = Hybrid.Checkbutton_Row(opf, 'Allow ', ('rotation', 'shift'))
    al.frame.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    ar, ash = [c.variable for c in al.checkbuttons]
    ar.set(True)
    ash.set(True)
    self.allow_rotation = ar
    self.allow_shift = ash

    mm = Hybrid.Checkbutton(opf, 'Move whole molecules', True)
    mm.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.move_whole_molecules = mm.variable
    self.mwm_button = mm.button

    #
    # Specify a label width so dialog is not resized for long messages.
    #
    msg = Tkinter.Label(parent, width = 40, anchor = 'w', justify = 'left')
    msg.grid(row = row, column = 0, sticky = 'ew')
    row = row + 1
    self.message_label = msg

    self.halt_button = self.buttonWidgets['Halt']
    self.allow_halt(False)

    self.update_gray_out()
    self.activate_undo_redo()

  # ---------------------------------------------------------------------------
  #
  def message(self, text):

    self.message_label['text'] = text
    self.message_label.update_idletasks()

  # ---------------------------------------------------------------------------
  # Map chosen to fit into base map.
  #
  def fit_map(self):

    m = self.object_menu.getvalue()
    from VolumeViewer import Volume
    if isinstance(m, Volume):
      return m
    
    return None

  # ---------------------------------------------------------------------------
  # Atoms chosen in dialog for fitting.
  #
  def fit_atoms(self):

    m = self.object_menu.getvalue()
    if m == 'selected atoms':
      from chimera import selection
      atoms = selection.currentAtoms()
      return atoms

    from VolumeViewer import Volume
    from chimera import Molecule
    if isinstance(m, Molecule):
      return m.atoms
    
    return []

  # ---------------------------------------------------------------------------
  #
  def object_chosen_cb(self, obj_name):

    self.update_gray_out()

  # ---------------------------------------------------------------------------
  #
  def update_gray_out(self):

    state = 'disabled' if self.fitting_atoms() else 'normal'
    self.limit_data.button['state'] = state
    self.cam_widget.button['state'] = state
    for c in self.opt_widget.frame.winfo_children():
      c['state'] = state
    self.mwm_button['state'] = 'disabled' if self.fit_map() else 'normal'

  # ---------------------------------------------------------------------------
  #
  def fitting_atoms(self):

    return not (self.simulate_map.get() or self.fit_map())

  # ---------------------------------------------------------------------------
  #
  def realtime_cb(self):

    from chimera import triggers as t
    if self.realtime_update.get():
      if self.xform_handler is None:
        h = t.addHandler('OpenState', self.xform_changed_cb, None)
        self.xform_handler = h
    elif self.xform_handler:
      t.deleteHandler('OpenState', self.xform_handler)
      self.xform_handler = None

  # ---------------------------------------------------------------------------
  #
  def xform_changed_cb(self, trigName, myData, trigData):

    if 'transformation change' in trigData.reasons:
      xf = self.relative_xform()
      if xf:
        import Matrix
        if (self.last_relative_xform is None or
            Matrix.xforms_differ(xf, self.last_relative_xform)):
          self.last_relative_xform = xf
          self.update_metric_cb()

  # ---------------------------------------------------------------------------
  #
  def relative_xform(self):

    fatoms = self.fit_atoms()
    fmap = self.fit_map()
    bmap = self.map_menu.data_region()
    if (len(fatoms) == 0 and fmap is None) or bmap is None:
      return None
    if fatoms:
      xfo = fatoms[0].molecule.openState.xform      # Atom list case
    else:
      xfo = fmap.openState.xform
    xf = xfo.inverse()
    xfm = bmap.openState.xform
    xf.multiply(xfm)
    return xf

  # ---------------------------------------------------------------------------
  #
  def simulate_map_cb(self):

    self.update_gray_out()

  # ---------------------------------------------------------------------------
  #
  def simulate_resolution_cb(self, event = None):

    self.simulated_map()        # Create map.

  # ---------------------------------------------------------------------------
  #
  def simulated_map(self):

    if not self.simulate_map.get():
      return None

    from CGLtk.Hybrid import float_variable_value
    res = float_variable_value(self.map_resolution)
    if res is None:
      self.message('No resolution specified for simulated map.')
      return None

    atoms = self.fit_atoms()
    if len(atoms) == 0:
      return None       # Not fitting atoms

    mwm = self.move_whole_molecules.get()
    v = self.find_simulated_map(atoms, res, mwm)
    if v is None:
      # Need to be able to move map independent of molecule if changing
      #  atom coordinates.
      from chimera import OpenModels
      id = None if mwm else OpenModels.Default
      from MoleculeMap import molecule_map
      v = molecule_map(atoms, res, modelId = id)
      v.fitsim_params = (tuple(atoms), res, mwm)
    return v

  # ---------------------------------------------------------------------------
  #
  def find_simulated_map(self, atoms, res, mwm):

    a = tuple(atoms)
    from VolumeViewer import volume_list
    for v in volume_list():
      if hasattr(v, 'fitsim_params') and v.fitsim_params == (a, res, mwm):
        return v
    return None

  # ---------------------------------------------------------------------------
  #
  def metric(self):

    if self.fitting_atoms():
      m = 'sum product'
    else:
      opt = self.optimize.get()
      if opt == 'overlap':
        m = 'sum product'
      elif self.corr_about_mean.get():
        m = 'correlation about mean'
      else:
        m = 'correlation'
    return m
      
  # ---------------------------------------------------------------------------
  #
  def Fit(self):

    fatoms = self.fit_atoms()
    fmap = self.fit_map()
    bmap = self.map_menu.data_region()
    if (len(fatoms) == 0 and fmap is None) or bmap is None:
      self.message('Choose model and map.')
      return
    if fmap == bmap:
      self.message('Chosen maps are the same.')
      return

    opt_r = self.allow_rotation.get()
    opt_t = self.allow_shift.get()
    if not opt_r and not opt_t:
      self.message('Enable rotation or translation.')
      return

    smap = self.simulated_map()
    if fatoms and smap is None:
      self.fit_atoms_in_map(fatoms, bmap, opt_r, opt_t)
    elif fmap:
      self.fit_map_in_map(fmap, bmap, opt_r, opt_t)
    elif smap:
      self.fit_map_in_map(smap, bmap, opt_r, opt_t, atoms = fatoms)
    if smap:
      self.show_average_map_value(fatoms, bmap)

    self.activate_undo_redo()

  # ---------------------------------------------------------------------------
  #
  def fit_map_in_map(self, mmap, fmap, opt_r, opt_t, atoms = []):

    max_steps = 100
    ijk_step_size_min = 0.01
    ijk_step_size_max = 0.5

    use_threshold = self.above_threshold.get()
    metric = self.metric()
    from FitMap import map_points_and_weights, motion_to_maximum
    points, point_weights = map_points_and_weights(mmap, use_threshold, metric)

    if len(points) == 0:
      if use_threshold:
        self.message('No grid points above map threshold.')
      else:
        self.message('Map has no non-zero values.')
      return

    self.allow_halt(True)
    move_tf, stats = motion_to_maximum(points, point_weights, fmap, max_steps,
                                       ijk_step_size_min, ijk_step_size_max,
                                       opt_t, opt_r, metric, self.report_status)
    self.allow_halt(False)

    mwm = self.move_whole_molecules.get()
    import move
    move.move_models_and_atoms(move_tf, [mmap], atoms, mwm, fmap)

    stats['moved map'] = mmap
    stats['fixed map'] = fmap
    self.report_map_fit(stats)
    self.report_transformation_matrix(mmap, fmap)

  # ---------------------------------------------------------------------------
  #
  def fit_atoms_in_map(self, atoms, fmap, opt_r, opt_t):

    self.allow_halt(True)

    mwm = self.move_whole_molecules.get()
    from FitMap import move_atoms_to_maximum
    stats = move_atoms_to_maximum(atoms, fmap,
                                  optimize_translation = opt_t,
                                  optimize_rotation = opt_r,
                                  move_whole_molecules = mwm,
                                  request_stop_cb = self.report_status)
    self.allow_halt(False)
    if stats:
      self.report_atom_fit(stats)
      if self.move_whole_molecules.get():
        for m in stats['molecules']:
          self.report_transformation_matrix(m, fmap)
    
  # ---------------------------------------------------------------------------
  # Report optimization statistics to reply log and status line.
  #
  def report_map_fit(self, stats):

    mmname = stats['moved map'].name
    fmname = stats['fixed map'].name
    np = stats['points']
    steps = stats['steps']
    shift = stats['shift']
    angle = stats['angle']
    cor = stats['correlation']
    corm = stats['correlation about mean']
    olap = stats['overlap']

    self.report_correlation(cor, corm)
    self.report_average(None)

    message = ('Fit map %s in map %s using %d points\n'
               % (mmname, fmname, np) +
               '  correlation = %.4g, correlation about mean = %.4g, overlap = %.4g\n' % (cor, corm, olap) +
               '  steps = %d, shift = %.3g, angle = %.3g degrees\n'
               % (steps, shift, angle))
    from chimera import replyobj
    replyobj.info(message)

  # ---------------------------------------------------------------------------
  #
  def report_correlation(self, cor = None, corm = None):

    if cor is None or corm is None:
      s = ''
    elif self.corr_about_mean.get():
      s = '%.4g' % corm
    else:
      s = '%.4g' % cor

    self.corr_label['text'] = s
    
  # ---------------------------------------------------------------------------
  # Report optimization statistics to reply log and status line.
  #
  def report_atom_fit(self, stats):

    mlist = stats['molecules']
    mnames = map(lambda m: '%s (%s)' % (m.name, m.oslIdent()), mlist)
    mnames = ', '.join(mnames)
    if len(mlist) > 1:      plural = 's'
    else:                   plural = ''
    vname = stats['data region'].name
    natom = stats['points']
    aoc = stats['atoms outside contour']
    clevel = stats['contour level']
    ave = stats['average map value']
    steps = stats['steps']
    shift = stats['shift']
    angle = stats['angle']

    message = ('Fit molecule%s %s to map %s using %d atoms\n'
               % (plural, mnames, vname, natom) +
               '  average map value = %.4g, steps = %d\n' % (ave, steps) +
               '  shifted from previous position = %.3g\n' % (shift,) +
               '  rotated from previous position = %.3g degrees\n' % (angle,))
    if (not clevel is None) and (not aoc is None):
      message += ('  atoms outside contour = %d, contour level = %.5g\n'
                  % (aoc, clevel))
    from chimera import replyobj
    replyobj.info(message)

    self.report_average(ave)
    self.report_correlation(None)

    if not aoc is None:
      status_message = '%d of %d atoms outside contour' % (aoc, natom)
      self.message(status_message)

  # ---------------------------------------------------------------------------
  #
  def report_average(self, ave):

    if ave is None: s = ''
    else: s = '%.4g' % ave
    self.ave_label['text'] = s

  # ---------------------------------------------------------------------------
  # Print transformation matrix that places model in map in reply log.
  #
  def report_transformation_matrix(self, model, map):

    m = model
    mname = '%s (%s)' % (m.name, m.oslIdent())
    mxf = m.openState.xform

    f = map
    fname = '%s (%s)' % (f.name, f.oslIdent())
    fxf = f.openState.xform
    
    mxf.premultiply(fxf.inverse())
    from Matrix import xform_matrix
    mtf = xform_matrix(mxf)
    message = ('Position of %s relative to %s coordinates:\n'
               % (mname, fname))
    message += transformation_description(mtf)
    from chimera import replyobj
    replyobj.info(message)
    
  # ---------------------------------------------------------------------------
  #
  def report_status(self, status):

    self.message(status)
    from chimera import update
    update.processWidgetEvents(self.halt_button)
    return self.requested_halt
    
  # ---------------------------------------------------------------------------
  #
  def Halt(self):

    self.requested_halt = True

  # ---------------------------------------------------------------------------
  #
  def allow_halt(self, allow):

    if allow:
      self.requested_halt = False
      state = 'normal'
    else:
      state = 'disabled'
    self.halt_button['state'] = state
    from chimera import update
    update.processWidgetEvents(self.halt_button)
    
  # ---------------------------------------------------------------------------
  #
  def update_metric_cb(self, event = None):

    fatoms = self.fit_atoms()
    fmap = self.fit_map()
    bmap = self.map_menu.data_region()
    if (len(fatoms) == 0 and fmap is None) or bmap is None:
      self.message('Choose model and map.')
      return

    if fatoms:
      self.show_average_map_value(fatoms, bmap)
      v = self.simulated_map()
      if v:
        self.show_correlation(v, bmap)
      else:
        self.report_correlation(None)
    elif fmap:
      self.show_correlation(fmap, bmap)
      self.report_average(None)
    
  # ---------------------------------------------------------------------------
  # Report correlation between maps.
  #
  def show_correlation(self, mmap, fmap):
      
    about_mean = self.corr_about_mean.get()
    from FitMap import map_overlap_and_correlation as oc
    olap, cor, corm = oc(mmap, fmap, self.above_threshold.get())
    self.report_correlation(cor, corm)

    msg = 'Correlation = %.4g, Correlation about mean = %.4g, Overlap = %.4g\n' % (cor, corm, olap)
    from chimera import replyobj
    replyobj.info(msg)
    
  # ---------------------------------------------------------------------------
  # Report average map value at selected atom positions.
  #
  def show_average_map_value(self, atoms, fmap):

    if len(atoms) == 0:
        self.message('No atoms selected.')
        return
      
    import FitMap
    amv, npts = FitMap.average_map_value_at_atom_positions(atoms, fmap)
    aoc, clevel = FitMap.atoms_outside_contour(atoms, fmap)

    self.report_average(amv)

    msg = 'Average map value = %.4g for %d atoms' % (amv, npts)
    if not aoc is None:
      msg += ', %d outside contour' % (aoc,)
    from chimera import replyobj
    replyobj.info(msg + '\n')

    if not aoc is None:
      msg = '%d of %d atoms outside contour' % (aoc, npts)
      self.message(msg)
    
  # ---------------------------------------------------------------------------
  #
  def Undo(self):

    from move import position_history
    position_history.undo()
    self.activate_undo_redo()
    self.update_metric_cb()

  # ---------------------------------------------------------------------------
  #
  def Redo(self):

    from move import position_history
    position_history.redo()
    self.activate_undo_redo()
    self.update_metric_cb()

  # ---------------------------------------------------------------------------
  #
  def activate_undo_redo(self):

    from move import position_history as h
    bw = self.buttonWidgets
    bw['Undo']['state'] = 'normal' if h.can_undo() else 'disabled'
    bw['Redo']['state'] = 'normal' if h.can_redo() else 'disabled'

  # ---------------------------------------------------------------------------
  #
  def Options(self):

    self.options_panel.set(not self.options_panel.get())
    
  # ---------------------------------------------------------------------------
  #
  def Results(self):

    from chimera import dialogs, tkgui
    dialogs.display(tkgui._ReplyDialog.name)
    
# -----------------------------------------------------------------------------
#
def fit_object_models():

  from VolumeViewer import Volume
  from chimera import openModels as om, Molecule
  mlist = om.list(modelTypes = [Molecule, Volume])
  folist = ['selected atoms'] + mlist
  return folist
    
# -----------------------------------------------------------------------------
# Put 'selected atoms' first, then all molecules, then all volumes.
#
def compare_fit_objects(a, b):

  if a == 'selected atoms':
    return -1
  if b == 'selected atoms':
    return 1
  from VolumeViewer import Volume
  from chimera import Molecule
  if isinstance(a,Molecule) and isinstance(b,Volume):
    return -1
  if isinstance(a,Volume) and isinstance(b,Molecule):
    return 1
  return cmp((a.id, a.subid), (b.id, b.subid))

# -----------------------------------------------------------------------------
#
from Matrix import transformation_description

# -----------------------------------------------------------------------------
#
def fit_map_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Fit_Map_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_fit_map_dialog():

  from chimera import dialogs
  return dialogs.display(Fit_Map_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Fit_Map_Dialog.name, Fit_Map_Dialog, replace = True)
