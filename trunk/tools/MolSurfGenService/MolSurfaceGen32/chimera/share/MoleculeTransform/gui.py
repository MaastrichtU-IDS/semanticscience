# -----------------------------------------------------------------------------
# Dialog for applying a rotation and translation to molecule coordinates.
#
import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Molecule_Transform_Dialog(ModelessDialog):

  title = 'Transform Molecule Coordinates'
  name = 'transform molecule coordinates'
  buttons = ('Apply', 'Set', 'Reset', 'Close',)
  help = 'ContributedSoftware/transform/transform.html'
  
  def fillInUI(self, parent):

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()

    parent.columnconfigure(0, weight=1)         # Allow scalebar to expand.
    
    row = 0

    import Tkinter
    from CGLtk import Hybrid

    from chimera.widgets import MoleculeOptionMenu
    mm = MoleculeOptionMenu(parent, labelpos = 'w', label_text = 'Molecule ',
                            command = self.show_cumulative_transform)
    mm.grid(row = row, column = 0, sticky = 'w')
    self.molecule_menu = mm
    row = row + 1

    ea = Hybrid.Entry(parent, 'Euler angles ', 25, '0 0 0')
    ea.frame.grid(row = row, column = 0, sticky = 'e')
    row = row + 1
    self.euler_angles = ea.variable

    tr = Hybrid.Entry(parent, 'Shift ', 25, '0 0 0')
    tr.frame.grid(row = row, column = 0, sticky = 'e')
    row = row + 1
    self.translation = tr.variable

    cas = Tkinter.Label(parent, text = '', justify = 'left')
    cas.grid(row = row, column = 0, sticky = 'w')
    self.cumulative = cas
    row = row + 1

    el = Tkinter.Label(parent, text = 'Apply rotation and translation to atom coordinates\n using the molecule coordinate system.', justify = 'left')
    el.grid(row = row, column = 0, sticky = 'w')
    row = row + 1

    self.show_cumulative_transform(None)
    
  # ---------------------------------------------------------------------------
  #
  def Apply(self):

    self.transform_cb()
      
  # ---------------------------------------------------------------------------
  #
  def Set(self):

    self.reset_cb()
    self.transform_cb()
      
  # ---------------------------------------------------------------------------
  #
  def Reset(self):

    self.reset_cb()

  # ---------------------------------------------------------------------------
  #
  def transform_cb(self, event = None):
    
    m = self.molecule_menu.getvalue()
    if m == None:
      from chimera.replyobj import warning
      warning('No molecule selected in Transform Molecule dialog')
      return

    try:
      ea = map(float, self.euler_angles.get().split())
      t = map(float, self.translation.get().split())
    except ValueError:
      from chimera.replyobj import warning
      warning('Error parsing Euler angle or translation number')
      return

    if len(ea) != 3:
      from chimera.replyobj import warning
      warning('Require 3 Euler angles separated by spaces')
      return

    if len(t) != 3:
      from chimera.replyobj import warning
      warning('Require 3 translation values separated by spaces')
      return
      
    from MoleculeTransform import euler_xform, transform_atom_coordinates
    xf = euler_xform(ea, t)
    transform_atom_coordinates(m.atoms, xf)
    self.record_xform(m, xf)

  # ---------------------------------------------------------------------------
  #
  def reset_cb(self, event = None):

    m = self.molecule_menu.getvalue()
    if m is None or not hasattr(m, 'applied_xform'):
      return

    xf = m.applied_xform.inverse()
    from MoleculeTransform import transform_atom_coordinates
    transform_atom_coordinates(m.atoms, xf)
    self.record_xform(m, None)
    
  # ---------------------------------------------------------------------------
  #
  def record_xform(self, m, xf):

    mxf = getattr(m, 'applied_xform', None)
    if xf is None:
      if mxf:
        delattr(m, 'applied_xform')
    elif mxf:
      mxf.premultiply(xf)
      m.applied_xform = mxf
    else:
      m.applied_xform = xf
    self.show_cumulative_transform(m)
    
  # ---------------------------------------------------------------------------
  #
  def show_cumulative_transform(self, m):

    from chimera import Xform
    mxf = getattr(m, 'applied_xform', Xform())
    import Matrix
    tf = Matrix.xform_matrix(mxf)
    angles = Matrix.euler_angles(tf)
    shift = mxf.getTranslation().data()
    text = ('Cumulative:\n' +
            ' Euler angles %.5g %.5g %.5g\n' % angles +
            ' Shift: %.5g %.5g %.5g' % shift)
    self.cumulative['text'] = text
      
# -----------------------------------------------------------------------------
#
def molecule_transform_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Molecule_Transform_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_molecule_transform_dialog():

  from chimera import dialogs
  return dialogs.display(Molecule_Transform_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Molecule_Transform_Dialog.name, Molecule_Transform_Dialog,
                 replace = True)
