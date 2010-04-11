# -----------------------------------------------------------------------------
# Dialog for showing contacts between asymmetric units of a crystal.
#
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Crystal_Contacts_Dialog(ModelessDialog):

  title = 'Crystal Contacts'
  name = 'crystal contacts'
  buttons = ('Show Contacts', 'Close',)
  help = 'ContributedSoftware/crystalcontacts/crystalcontacts.html'
  
  def fillInUI(self, parent):

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()

    parent.columnconfigure(0, weight=1)
    row = 0

    import Tkinter
    from CGLtk import Hybrid

    from chimera.widgets import MoleculeOptionMenu
    mm = MoleculeOptionMenu(parent, labelpos = 'w', label_text = 'Molecule ')
    mm.grid(row = row, column = 0, sticky = 'w')
    self.molecule_menu = mm
    row = row + 1

    cd = Hybrid.Entry(parent, 'Contact distance', 5, '1.0')
    cd.frame.grid(row = row, column = 0, sticky = 'w')
    self.contact_distance = cd.variable
    cd.entry.bind('<KeyPress-Return>', self.show_contacts)
    row = row + 1

    mc = Hybrid.Checkbutton(parent, 'Create copies of contacting molecules.', False)
    mc.button.grid(row = row, column = 0, sticky = 'w')
    row += 1
    self.copy_molecule = mc.variable
    
    msg = Tkinter.Label(parent, anchor = 'w', justify = 'left')
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
  def ShowContacts(self):

    self.show_contacts()

  # ---------------------------------------------------------------------------
  #
  def show_contacts(self, event = None):
    
    m = self.molecule_menu.getvalue()
    if m == None:
      self.message('Select a molecule from the menu')
      return

    if not hasattr(m, 'pdbHeaders'):
      self.message('Molecule does not have PDB headers for determining symmetry')
      return

    from PDBmatrices.crystal import cryst1_pdb_record
    if cryst1_pdb_record(m.pdbHeaders) is None:
      self.message('Molecule does not have PDB CRYST1 record for determining unit cell')
      return

    from CGLtk.Hybrid import float_variable_value
    d = float_variable_value(self.contact_distance)
    if d == None:
      self.message('Distance value required')
      return

    make_copies = self.copy_molecule.get()

    from CrystalContacts import show_crystal_contacts
    cm = show_crystal_contacts(m, d, make_copies, replace = True)
    
# -----------------------------------------------------------------------------
#
def crystal_contacts_dialog(create = False):

  from chimera import dialogs
  return dialogs.find(Crystal_Contacts_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_crystal_contacts_dialog():

  from chimera import dialogs
  return dialogs.display(Crystal_Contacts_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Crystal_Contacts_Dialog.name, Crystal_Contacts_Dialog,
                 replace = True)
