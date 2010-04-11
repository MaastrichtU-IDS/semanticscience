# -----------------------------------------------------------------------------
# Dialog for coloring atoms according to density map values.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Atom_Density_Dialog(ModelessDialog):

  title = 'Values at Atom Positions'
  name = 'values at atom positions'
  buttons = ('Histogram', 'Close',)
  help = 'ContributedSoftware/density/density.html'
  
  def fillInUI(self, parent):

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()
    
    row = 0

    import Tkinter

    from chimera.widgets import MoleculeOptionMenu
    mm = MoleculeOptionMenu(parent, labelpos = 'w', label_text = 'Molecule ')
    mm.grid(row = row, column = 0, sticky = 'w')
    self.molecule_menu = mm
    row = row + 1

    from VolumeViewer import Volume_Menu
    vm = Volume_Menu(parent, 'Volume data ', open_button = True)
    vm.frame.grid(row = row, column = 0, sticky = 'w')
    self.volume_menu = vm
    row = row + 1
    
    #
    # Specify a label width so dialog is not resized for long messages.
    #
    msg = Tkinter.Label(parent, width = 30, anchor = 'w', justify = 'left')
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
  def Histogram(self):

    self.set_and_show_atom_volume_values()

  # ---------------------------------------------------------------------------
  #
  def set_and_show_atom_volume_values(self):
    
    m = self.molecule_menu.getvalue()
    if m == None:
      self.message('Select a molecule')
      return

    v = self.volume_menu.data_region()
    if v == None:
      self.message('Select a volume')
      return

    attribute_name = 'value_' + v.name
    
    import AtomDensity
    attribute_name = AtomDensity.replace_special_characters(attribute_name,'_')
    AtomDensity.set_atom_volume_values(m, v, attribute_name)
    AtomDensity.show_attribute_histogram(m, attribute_name)

# -----------------------------------------------------------------------------
#
def atom_density_dialog(create = 0):

  from chimera import dialogs
  return dialogs.find(Atom_Density_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_atom_density_dialog():

  from chimera import dialogs
  return dialogs.display(Atom_Density_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Atom_Density_Dialog.name, Atom_Density_Dialog, replace = 1)
