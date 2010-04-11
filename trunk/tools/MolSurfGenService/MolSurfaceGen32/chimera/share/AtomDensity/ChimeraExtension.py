import chimera.extension

# -----------------------------------------------------------------------------
#
class Atom_Density_EMO(chimera.extension.EMO):

  def name(self):
    return 'Values at Atom Positions'
  def description(self):
    return 'Show volume data values at atom positions.'
  def categories(self):
    return ['Volume Data']
  def icon(self):
    return None
  def activate(self):
    self.module('gui').show_atom_density_dialog()
    return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Atom_Density_EMO(__file__))

# -----------------------------------------------------------------------------
#
def oa():
  import AtomDensity
  AtomDensity.select_atoms_outside_map()

from Accelerators import add_accelerator
add_accelerator('oa', 'Reduce selected atoms to those outside map contour', oa)
