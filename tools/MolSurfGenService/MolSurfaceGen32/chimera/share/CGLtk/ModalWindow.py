# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: ModalWindow.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter

class ModalWindow(Tkinter.Toplevel):
	"""
	ModalWindow is used to present a window that grabs input focus
	when activated.  Its "end" method is used to terminate the grab
	and remove the window from view.
	Code shamelessly stolen from SimpleDialog.
	"""

	def __init__(self, master=None, resizable=Tkinter.FALSE, *args, **kw):
		apply(Tkinter.Toplevel.__init__, (self, master) + args, kw)
		self.withdraw()
		if not resizable:
			self.resizable(Tkinter.FALSE, Tkinter.FALSE)
		self.protocol('WM_DELETE_WINDOW', self.end)

	def run(self, master=None):
		self.transient(master)
		self.returnValue = None
		self.update_idletasks()
		if self.master.winfo_ismapped():
			x = self.master.winfo_rootx() \
				+ self.master.winfo_width() / 2 \
				- self.winfo_reqwidth() / 2
			y = self.master.winfo_rooty() \
				+ self.master.winfo_height() / 2 \
				- self.winfo_reqheight() / 2
		else:
			x = self.master.winfo_screenwidth() / 2 \
				- self.winfo_reqwidth() / 2
			y = self.master.winfo_screenheight() / 2 \
				- self.winfo_reqheight() / 2
		self.geometry('+%d+%d' % (x, y))
		self.grab_set()
		self.deiconify()
		self.mainloop()
		self.withdraw()
		self.grab_release()
		return self.returnValue

	def end(self, value=None):
		self.returnValue = value
		self.quit()
