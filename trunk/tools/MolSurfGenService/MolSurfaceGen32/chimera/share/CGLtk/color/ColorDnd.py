# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import Tkdnd

class ColorSource:
	def __init__(self, widget):
		if not hasattr(self, "rgb") and not hasattr(self, "rgba"):
			raise TypeError, \
			"Color source must have 'rgb' or 'rgba' attribute"
		widget.bind("<ButtonPress>", self.cs_dragStart)
		self.__widget = widget

	def cs_dragStart(self, event):
		# start drag
		Tkdnd.dnd_start(self, event)
	
	def dnd_end(self, target, event):
		# we've dropped on a target
		pass
	

class ColorTarget:
	def dnd_accept(self, source, event):
		# as a target, do we accept a drag attempt?
		if hasattr(source, "rgb") or hasattr(source, "rgba"):
			return self
		return None
	
	def dnd_motion(self, source, event):
		# drag motion over us as target
		pass
	
	def dnd_enter(self, source, event):
		# drag enters us as target
		pass
	
	def dnd_leave(self, source, event):
		# drag leaves us as target
		pass
	
	def dnd_commit(self, source, event):
		# drop over us
		if hasattr(source, "rgba"):
			self.showColor(color=source.rgba)
		else:
			self.showColor(color=source.rgb)
