import chimera.extension

class Undo_Move_EMO(chimera.extension.EMO):
	def name(self):
		return 'Undo Move'
	def description(self):
		return 'Undo last model rotation and translation.'
	def categories(self):
		return ['Movement']
	def icon(self):
		return None
	def activate(self):
		self.module().undo_move()
		return None
chimera.extension.manager.registerExtension(Undo_Move_EMO(__file__))

class Redo_Move_EMO(chimera.extension.EMO):
	def name(self):
		return 'Redo Move'
	def description(self):
		return 'Redo last undone model rotation and translation.'
	def categories(self):
		return ['Movement']
	def icon(self):
		return None
	def activate(self):
		self.module().redo_move()
		return None
chimera.extension.manager.registerExtension(Redo_Move_EMO(__file__))

import UndoMove
UndoMove.start_recording()
