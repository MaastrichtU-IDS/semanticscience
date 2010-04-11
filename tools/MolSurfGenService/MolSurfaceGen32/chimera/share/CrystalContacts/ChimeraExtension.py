import chimera.extension

# -----------------------------------------------------------------------------
#
class Crystal_Contacts_EMO(chimera.extension.EMO):

  def name(self):
    return 'Crystal Contacts'
  def description(self):
    return 'Display contacts between crystal asymmetric units'
  def categories(self):
    return ['Higher-Order Structure']
  def icon(self):
    return None
  def activate(self):
    self.module('gui').show_crystal_contacts_dialog()
    return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Crystal_Contacts_EMO(__file__))

# -----------------------------------------------------------------------------
#
def show_contacts(distance = 1.0):
    import chimera
    for m in chimera.openModels.list(modelTypes = [chimera.Molecule]):
        from CrystalContacts import show_crystal_contacts
        show_crystal_contacts(m, distance)

from Accelerators import add_accelerator
add_accelerator('xx', 'Show crystal contacts', show_contacts)

# -----------------------------------------------------------------------------
#
def crystal_contacts_command(cmdname, args):
  from CrystalContacts.command import crystal_contacts
  crystal_contacts(cmdname, args)

# -----------------------------------------------------------------------------
#
from Midas.midas_text import addCommand
addCommand('crystalcontacts', crystal_contacts_command, help = True)
