from chimera.extension import EMO, manager

# -----------------------------------------------------------------------------
#
class Unit_Cell_EMO(EMO):

  def name(self):
    return 'Unit Cell'
  def description(self):
    return 'Make molecule copies to for crystal unit cell'
  def categories(self):
    return ['Higher-Order Structure']
  def icon(self):
    return None
  def activate(self):
    self.module().show_unit_cell_dialog()

manager.registerExtension(Unit_Cell_EMO(__file__))

# -----------------------------------------------------------------------------
#
def show_unit_cell_dialog():
  import UnitCell
  UnitCell.show_unit_cell_dialog()
from Accelerators import add_accelerator
add_accelerator('uc', 'Show unit cell dialog', show_unit_cell_dialog)
