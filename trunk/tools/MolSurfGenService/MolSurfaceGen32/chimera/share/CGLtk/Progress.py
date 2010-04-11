"""
Tk Progress bar

This code is in the public domain.
"""

__all__ = ['Progress']

import Tkinter

_firstTime = True

class Progress:
	"""Progress bar based on Tcl version by Donal K. Fellows
	<http://www.man.ac.uk/~zzcgudf/tcl/mwidx.html#progress>.
	Options are based on Tile (aka Tk 8.5) progress bar arguments
	to simplify converting.
	"""

	undoneForeground = "black"
	undoneBackground = "white"
	doneForeground = "white"
	doneBackground = "blue2"
	borderWidth = 1
	relief = Tkinter.SUNKEN

	Default_options = (
		('*Progress.undoneForeground', 'black', 'widgetDefault'),
		('*Progress.undoneBackground', 'white', 'widgetDefault'),
		('*Progress.doneForeground', 'white', 'widgetDefault'),
		('*Progress.doneBackground', 'blue2', 'widgetDefault'),
		('*Progress.borderWidth', '2', 'widgetDefault'),
		('*Progress.relief', 'sunken', 'widgetDefault'),
		)

	def __init__(self, master, orient=Tkinter.HORIZONTAL, length=0,
					maximum=100, value=0, variable=None):
		if not 'horizontal'.startswith(orient):
			raise RuntimeError, "only horizontal progress bars are supported for now"
		if variable:
			self.textvar = variable
		else:
			self.textvar = Tkinter.StringVar(master)
		self.maximum = maximum

		global _firstTime
		if _firstTime:
			_firstTime = False
			for pattern, v, priority in self.Default_options:
				master.option_add(pattern, v, priority)

		self.hull = Tkinter.Frame(master, class_='Progress')
		for attr in [x[0].split('.')[-1] for x in self.Default_options]:
			v = self.hull.option_get(attr, attr.capitalize())
			if v:
				setattr(self, attr, v)

		self.undone = Tkinter.Frame(self.hull, borderwidth=0,
				background=self.undoneBackground)
		if length:
			self.undone.configure(width=length)
		self.right = Tkinter.Label(self.undone,
				textvariable=self.textvar, borderwidth=0,
				foreground=self.undoneForeground,
				background=self.undoneBackground)
		self.undone.configure(height=self.right.winfo_reqheight() + 2)
		self.done = Tkinter.Frame(self.undone,
				background=self.doneBackground)
		self.left = Tkinter.Label(self.done, textvariable=self.textvar,
				borderwidth=0, foreground=self.doneForeground,
				background=self.doneBackground)

		self.undone.bind('<Configure>', self._configure)
		self.undone.pack(fill=Tkinter.BOTH, expand=1)
		self.right.place(relx=0.5, rely=0.5, anchor=Tkinter.CENTER)
		self.done.place(x=0, y=0, relheight=1, relwidth=0)
		self.left.place(x=0, rely=0.5, anchor=Tkinter.CENTER)

		self.set(value)

	def pack(self, *args, **kw):
		self.hull.pack(*args, **kw)

	def grid(self, *args, **kw):
		self.hull.grid(*args, **kw)

	def place(self, *args, **kw):
		self.hull.place(*args, **kw)

	def set(self, value):
		relwidth = value / float(self.maximum)
		progress = int(100 * relwidth)
		newText = "%g%%" % progress
		oldText = self.textvar.get()
		if newText != oldText:
			self.done.place_configure(relwidth=relwidth)
			self.textvar.set(newText)

	def _configure(self, event):
		self.left.place_configure(x=int(event.width / 2))
