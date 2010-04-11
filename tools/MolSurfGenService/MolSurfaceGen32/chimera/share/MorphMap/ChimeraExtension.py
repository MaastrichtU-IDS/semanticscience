import chimera.extension

# -----------------------------------------------------------------------------
#
class Morph_Map_EMO(chimera.extension.EMO):

  def name(self):
    return 'Morph Map'
  def description(self):
    return 'Interpolate between two volume data sets'
  def categories(self):
    return ['Volume Data']
  def icon(self):
    return None
  def activate(self):
    self.module('gui').show_morph_map_dialog()
    return None

# -----------------------------------------------------------------------------
#
chimera.extension.manager.registerExtension(Morph_Map_EMO(__file__))
