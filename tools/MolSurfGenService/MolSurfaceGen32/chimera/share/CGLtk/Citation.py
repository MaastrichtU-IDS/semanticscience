""" Citation:  show citation for literature reference"""

import Tkinter

class Citation(Tkinter.Frame):
	"""Citation is treated as a Frame
		'cite' is the citation text
		'prefix'/'suffix' is text to precede/follow the citation
	"""
	def __init__(self, master, cite, prefix=None, suffix=None):
		Tkinter.Frame.__init__(self, master, bd=2, relief="raised")
		if prefix is not None:
			Tkinter.Label(self, text=prefix).grid(row=0, column=0)
		Tkinter.Label(self, justify="left", font=("Times", "12"),
			text=cite).grid(row=1, column=0)
		if suffix is not None:
			Tkinter.Label(self, text=suffix).grid(row=2, column=0)
