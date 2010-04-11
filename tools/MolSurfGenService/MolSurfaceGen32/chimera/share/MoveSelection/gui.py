# -----------------------------------------------------------------------------
# Dialog for altering movement mouse modes to move parts of structures.
#

import chimera
from chimera.baseDialog import ModelessDialog

# -----------------------------------------------------------------------------
#
class Movement_Mouse_Mode_Dialog(ModelessDialog):

  title = 'Movement Mouse Mode'
  name = 'movement mouse mode'
  buttons = ('Undo Move', 'Redo Move', 'Close',)
  help = 'ContributedSoftware/movemode/movemode.html'
  
  def fillInUI(self, parent):

    self.toplevel_widget = parent.winfo_toplevel()
    self.toplevel_widget.withdraw()

    parent.columnconfigure(0, weight = 1)
    
    row = 0

    from CGLtk import Hybrid

    self.NORMAL_MOVEMENT = 'Normal'
    self.MOVE_SELECTION = 'Move selection'
    self.MOVE_MOLECULE = 'Move molecule'
    self.MOVE_CHAIN = 'Move chain'
    self.MOVE_SECONDARY_STRUCTURE = 'Move helix, strand, or turn'
    modes = (self.NORMAL_MOVEMENT, self.MOVE_SELECTION, self.MOVE_MOLECULE,
             self.MOVE_CHAIN, self.MOVE_SECONDARY_STRUCTURE)

    mm = Hybrid.Option_Menu(parent, 'Movement mouse mode ', *modes)
    mm.frame.grid(row = row, column = 0, sticky = 'w')
    self.mode = mm.variable
    mm.add_callback(self.mode_changed_cb)

  # ---------------------------------------------------------------------------
  #
  def UndoMove(self):

    import move
    move.undo_move()

  # ---------------------------------------------------------------------------
  #
  def RedoMove(self):

    import move
    move.redo_move()

  # ---------------------------------------------------------------------------
  #
  def mode_changed_cb(self):

    from move import Selection_Mover as m
    mmap = {self.NORMAL_MOVEMENT: m.NORMAL_MOVEMENT,
            self.MOVE_SELECTION: m.MOVE_SELECTION,
            self.MOVE_MOLECULE: m.MOVE_MOLECULE,
            self.MOVE_CHAIN: m.MOVE_CHAIN,
            self.MOVE_SECONDARY_STRUCTURE: m.MOVE_SECONDARY_STRUCTURE
            }
    import move
    move.set_mouse_mode(mmap[self.mode.get()])

# -----------------------------------------------------------------------------
#
def movement_mode_dialog(create = 0):

  from chimera import dialogs
  return dialogs.find(Movement_Mouse_Mode_Dialog.name, create=create)
  
# -----------------------------------------------------------------------------
#
def show_movement_mode_dialog():

  from chimera import dialogs
  return dialogs.display(Movement_Mouse_Mode_Dialog.name)

# -----------------------------------------------------------------------------
#
from chimera import dialogs
dialogs.register(Movement_Mouse_Mode_Dialog.name,
                 Movement_Mouse_Mode_Dialog, replace = 1)
