import chimera.extension

# -----------------------------------------------------------------------------
#
class Movement_Mode_EMO(chimera.extension.EMO):

  def name(self):
    return 'Movement Mouse Mode'
  def description(self):
    return 'Set movement mouse mode to move pieces of models.'
  def categories(self):
    return ['Movement', 'Structure Editing']
  def icon(self):
    return None
  def activate(self):
    self.module('gui').show_movement_mode_dialog()
    return None

  # Accelerator callbacks
  def undo_move(self):
    self.module('move').undo_move()
  def redo_move(self):
    self.module('move').redo_move()
  def toggle_mode(self):
    self.module('move').toggle_move_selection_mouse_modes()

# -----------------------------------------------------------------------------
#
mm = Movement_Mode_EMO(__file__)
chimera.extension.manager.registerExtension(mm)

# -----------------------------------------------------------------------------
#
import Accelerators
Accelerators.add_accelerator('Ms', 'Toggle move selection mouse mode',
                             mm.toggle_mode)
Accelerators.add_accelerator('um', 'Undo selection move', mm.undo_move)
Accelerators.add_accelerator('rm', 'Redo selection move', mm.redo_move)
