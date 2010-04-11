# -----------------------------------------------------------------------------
# Dialog for computing small-angle x-ray scattering profile.
#

# -----------------------------------------------------------------------------
#
from chimera.baseDialog import ModelessDialog
class SAXS_Dialog(ModelessDialog):

  title = 'Small-angle X-ray Profile'
  name = 'small-angle x-ray profile'
  buttons = ('Profile', 'Options', 'Close',)
#  help = 'ContributedSoftware/fitmaps/fitmaps.html'
  
  def fillInUI(self, parent):

    self.plot = None

    t = parent.winfo_toplevel()
    self.toplevel_widget = t
    t.withdraw()

    parent.columnconfigure(0, weight = 1)
    row = 0

    from chimera.preferences import addCategory, HiddenCategory
    prefs = addCategory("SAXS", HiddenCategory,
                        optDict = {'saxs executable': ''})
    self.preferences = prefs

    import Tkinter
    from CGLtk import Hybrid

    from chimera import widgets as w
    mm = w.ExtendedMoleculeOptionMenu(parent, label_text = 'Molecule ',
                                      labelpos = 'w',
                                      labels = ['selected atoms','all molecules'])
    mm.grid(row = row, column = 0, sticky = 'w')
    row += 1
    self.molecule_menu = mm

    ep = Hybrid.Entry(parent, 'Experimental profile ', 25, browse = True)
    ep.frame.grid(row = row, column = 0, sticky = 'ew')
    row += 1
    self.experimental_profile = ep.variable

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

    np = Hybrid.Checkbutton(opf, 'Use new plot window', False)
    np.button.grid(row = orow, column = 0, sticky = 'w')
    orow += 1
    self.new_plot = np.variable

    ex = Hybrid.Entry(opf, 'Executable ', 25,
                      initial = prefs['saxs executable'], browse = True)
    ex.frame.grid(row = orow, column = 0, sticky = 'ew')
    orow += 1
    ex.entry.xview('end')
    self.executable = ex.variable

  # ---------------------------------------------------------------------------
  #
  def Profile(self):

    self.compute_profile()

  # ---------------------------------------------------------------------------
  #
  def compute_profile(self):

    from chimera.replyobj import warning

    molecules, selected_only = self.chosen_atoms()
    if len(molecules) == 0:
      warning('No atoms selected for SAXS profile computation.')
      return

    expath = self.experimental_profile.get()
    from os.path import isfile
    if expath and not isfile(expath):
      warning('Experimental profile "%s" does not exist' % expath)
      expath = ''

    epath = self.executable_path()

    p = None if self.new_plot.get() else self.plot
    import saxs
    p = saxs.show_saxs_profile(molecules, selected_only, epath, expath, p)
    self.plot = p
    self.plot.raiseWindow()

  # ---------------------------------------------------------------------------
  #
  def executable_path(self):

    epath = self.executable.get().strip()
    if len(epath) == 0:
      self.preferences['saxs executable'] = ''
      from CGLutil.findExecutable import findExecutable
      epath = findExecutable('profile')
      if epath is None:
        return None
    else:
      from os.path import isfile
      if not isfile(epath):
        return None
      self.preferences['saxs executable'] = epath

    return epath

  # ---------------------------------------------------------------------------
  #
  def chosen_atoms(self):

    m = self.molecule_menu.getvalue()
    from chimera import Molecule, openModels, selection
    if isinstance(m, Molecule):
      return [m], False
    elif m == 'selected atoms':
      mlist = list(set([a.molecule for a in selection.currentAtoms()]))
      return mlist, True
    elif m == 'all molecules':
      mlist = openModels.list(modelTypes = [Molecule])
      return mlist, False
    return [], False
      
  # ---------------------------------------------------------------------------
  #
  def Options(self):

    self.options_panel.set(not self.options_panel.get())

# -----------------------------------------------------------------------------
#
def saxs_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(SAXS_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_saxs_dialog():

  from chimera import dialogs
  return dialogs.display(SAXS_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(SAXS_Dialog.name, SAXS_Dialog, replace = True)
