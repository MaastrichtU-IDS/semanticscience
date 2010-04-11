"""Tk 8.5 stuff"""

import Tkinter

class Sizegrip(Tkinter.Widget):
	"""Display sizegrip"""

	def __init__(self, master=None, cnf={}, **kw):
		Tkinter.Widget.__init__(self, master, "::ttk::sizegrip", cnf, kw)
