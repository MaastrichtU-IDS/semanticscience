import chimera.extension

# -----------------------------------------------------------------------------
#
class Constrained_Move_EMO(chimera.extension.EMO):

  def name(self):
    return 'Constrained Move'
  def description(self):
    return 'Rotate models about a fixed axis with the mouse.  Translate models along an axis or plane using the mouse.'
  def categories(self):
    return ['Movement']
  def icon(self):
    return None
  def activate(self):
    self.module().show_constrained_move_dialog()
    return None

# -----------------------------------------------------------------------------
#
emo = Constrained_Move_EMO(__file__)
chimera.extension.manager.registerExtension(emo)
