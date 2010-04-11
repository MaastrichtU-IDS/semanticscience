# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import Tkinter

class Booleanbutton(Tkinter.Frame):

	def __init__(self, master=None, initState=0, command=None,
			onColor='yellow', offColor=None, enabled=1, **kw):
		param = { 'bd': 2, 'width':16, 'height':16 }
		param.update(kw)
		if param.has_key('borderwidth'):
			del param['bd']
		apply(Tkinter.Frame.__init__, (self, master), param)
		self.onColor = onColor
		if offColor:
			self.offColor = offColor
		else:
			self.offColor = self['bg']
		self.state = not initState
		self.command = None
		self.toggle()
		self.command = command
		self.enabled = enabled
		if enabled:
			self.bind('<ButtonRelease>', self.toggle)

	def toggle(self, event=None):
		self.state = not self.state
		if self.state:
			self.config(bg=self.onColor)
			self.config(relief=Tkinter.SUNKEN)
		else:
			self.config(bg=self.offColor)
			self.config(relief=Tkinter.RAISED)
		if self.command:
			if not callable(self.command):
				print 'command', self.command
			else:
				self.command(self.state)

	def setEnabled(self, on):
		if self.enabled == on:
			return
		self.enabled = on
		if on:
			self.bind('<ButtonRelease>', self.toggle)
		else:
			self.unbind('<ButtonRelease>')

	def setState(self, on):
		if self.state == on:
			return
		self.toggle()

	def state(self):
		return self.state

if __name__ == '__main__':
	app = Booleanbutton()
	app.pack()
	app.mainloop()
