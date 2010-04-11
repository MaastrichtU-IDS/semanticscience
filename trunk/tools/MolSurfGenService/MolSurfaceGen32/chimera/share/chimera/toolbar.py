# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: toolbar.py 26655 2009-01-07 22:02:30Z gregc $

"""
	Toolbar interface
"""
# TODO: don't show scroll bar tools are all visible

__all__ = ("Toolbar", "YES", "NO", "AUTO")

import Tkinter
Tk = Tkinter
import chimage

# visibility arguments
YES = "yes"
NO = "no"
AUTO = "auto"

SCROLLBAR_WIDTH = 7

def _guard(func):
	"""Protect against faulty callback functions."""
	try:
		func()
	except (SystemExit, KeyboardInterrupt):
		raise
	except Exception:
		import replyobj
		replyobj.reportException('Error in toolbar callback')

class Toolbar(Tk.Frame):
	"""A Toolbar widget.

	Toolbar(master, side=Tk.LEFT) => widget

	A Toolbar is a frame that contains a scrollable list of tool
	buttons and one work widget that is always visible.  The work
	widget is created by the caller as a child of the toolbar, and
	then the setWork method must be called with that widget.  The
	optional side argument may be one of LEFT, RIGHT, TOP, or BOTTOM.

	Example:
		from toolbar import Toolbar
		tb = Toolbar(application)
		tb.pack()
		graphics = Canvas(tb)
		tb.setWork(graphics)
	"""
	# implementation:
	#    work widget is at grid (2, 2)
	#    the scrollbar and toolbox locations are kept in _geom
	#    (boxrow, boxcol, scrollrow, scrollcol, sticky)

	def __init__(self, master, side=Tk.LEFT):
		Tk.Frame.__init__(self, master)
		self.grid_columnconfigure(2, weight=1)
		self.grid_rowconfigure(2, weight=1)
		self._visible = AUTO
		self._side = side
		self._work = None
		# use Helvetica -48 instead of Courier because its 0 is
		# closer to half the 48 pixel width
		self._toolbox = Tk.Text(self, width=2, height=1,
				font=("Helvetica", -48), state=Tk.DISABLED,
				padx=0, pady=0, cursor="left_ptr")
		# need two scrollbars because scrollbars stop working
		# when switching from horizontal to vertical
		self._scrollbar = Tk.Scrollbar(self, width=SCROLLBAR_WIDTH)
		self._updateSideParameters(side)

	def setWork(self, w):
		"""Set work widget.

		toolbar.setWork(widget) => None

		See Toolbar class description for more details.
		"""
		if self._work == w:
			return
		reset = (self._work is None or w is None)
		self._work = w
		if self._work:
			self._work.grid(row=2, column=2, sticky=Tk.NSEW)
		if reset:
			self._updateSideParameters(self._side)
			visible = self._visible
			self._visible = None
			self.setVisible(visible)

	def _autoscroll_set(self, first, last):
		if not self._toolbox.winfo_ismapped():
			return
		if float(first) <= 0 and float(last) >= 1:
			self._scrollbar.grid_forget()
		elif not self._scrollbar.winfo_ismapped():
			brow, bcol, srow, scol, sticky = self._geom
			self._scrollbar.grid(row=srow, column=scol, sticky=sticky)
			# need to update_idletasks so scrollbar behaves
			self._scrollbar.update_idletasks()
		self._scrollbar.set(first, last)

	def _updateSideParameters(self, side):
		# only call this
		if self._work == None or side == Tk.TOP:
			orient = Tk.HORIZONTAL
			self._geom = (1, 2, 0, 2, Tk.EW)
		elif side == Tk.BOTTOM:
			# Tk.BOTTOM
			orient = Tk.HORIZONTAL
			self._geom = (3, 2, 4, 2, Tk.EW)
		elif side == Tk.LEFT:
			orient = Tk.VERTICAL
			self._geom = (2, 1, 2, 0, Tk.NS)
		elif side == Tk.RIGHT:
			orient = Tk.VERTICAL
			self._geom = (2, 4, 2, 3, Tk.NS)
		if orient == Tk.VERTICAL:
			self._toolbox.config(width=2, height=1, wrap=Tk.CHAR,
				xscrollcommand="{}",
				yscrollcommand=self._autoscroll_set)
			self._scrollbar.config(orient=orient,
					command=self._toolbox.yview)
		else:
			self._toolbox.config(width=2, height=1, wrap=Tk.NONE,
				xscrollcommand=self._autoscroll_set,
				yscrollcommand="{}")
			self._scrollbar.config(orient=orient,
					command=self._toolbox.xview)

	def setSide(self, side):
		"""Set which side of the frame to place the toolbar.

		toolbar.setSide(side) => None

		side can be one of Tk constants LEFT, RIGHT TOP or BOTTOM.
		"""
		if self._side == side:
			return
		self._side = side
		self._updateSideParameters(side)
		if self._visible == YES \
		or (self._visible == AUTO and self.count() > 0):
			brow, bcol, srow, scol, sticky = self._geom
			self._toolbox.grid(row=brow, column=bcol, sticky=sticky)
			self._scrollbar.grid(row=srow, column=scol, sticky=sticky)
			if self._work:
				self._work.grid(row=2, column=2)

	def setVisible(self, visibility):
		"""Turn on and off the toolbar.

		toolbar.setVisible(visibility) => None
		"""
		if self._visible == visibility:
			return
		self._visible = visibility
		if visibility == AUTO:
			if self.count() > 0:
				visibility = YES
			else:
				visibility = NO
		if visibility == NO:
			self._scrollbar.grid_forget()
			self._toolbox.grid_forget()
		elif visibility == YES:
			brow, bcol, srow, scol, sticky = self._geom
			self._toolbox.grid(row=brow, column=bcol, sticky=sticky)
			self._scrollbar.grid(row=srow, column=scol, sticky=sticky)
			if self._work:
				self._work.grid(row=2, column=2)
		else:
			raise TypeError, "visibility must be 'yes', 'no', or 'auto'"

	def add(self, image, callback, balloon, helpURL=None):
		"""Add button to toolbar.

		toolbar.add(image, callback, balloon, helpURL) => None

		Create a button for a tool with the given image, callback
		function, balloon help string, and URL for context sensitive
		help.  The image may be a filename or an Image instance.
		The callback function should take no arguments.  Balloon help
		should be a short string.
		"""

		button = Tk.Button(self._toolbox,
				command=lambda func=callback: _guard(func))
		import help
		help.register(button, helpURL, balloon)

		imtk = chimage.get(image, button, allowRelativePath=True)
		button.config(image=imtk)
		# need to keep reference to Tk image or else it is destroyed
		# and the button stops working
		button._image = imtk
		if self._side == Tk.LEFT or self._side == Tk.RIGHT:
			button.pack(side=Tk.TOP)
		else:
			button.pack(side=Tk.LEFT)
		self._toolbox.window_create(Tk.END, window=button,
						align=Tk.TOP, padx=0, pady=0)
		if self._visible == AUTO and self.count() == 1:
			self._visible = NO
			self.setVisible(AUTO)
		return button

	def remove(self, button):
		"""Remove button from toolbar.

		toolbar.remove(button) => None

		Remove a button created by "add"."""

		button.destroy()
		if self._visible == AUTO and self.count() == 0:
			self._visible = YES
			self.setVisible(AUTO)

	def clear(self):
		"""Remove all buttons from toolbar"""
		self._toolbox['state'] = 'normal'
		self._toolbox.delete('1.0', Tk.END)
		self._toolbox['state'] = 'disabled'

	def count(self):
		return len(self._toolbox.window_names())

if __name__ == "__main__":
	def pressed(what):
		print what
	app = Tk.Frame(Tk.Tk())
	app.pack(expand=Tk.YES, fill=Tk.BOTH)
	tb = Toolbar(app, side=Tk.LEFT)
	tb.pack(expand=Tk.YES, fill=Tk.BOTH)
	work = Tk.Canvas(tb, background="#600")
	tb.setWork(work)
	work.bind('<ButtonRelease-1>', lambda e, t=tb: t.setVisible(YES))
	tb.add('images/avacado.png', lambda: tb.setSide(Tk.LEFT), 'fruit', "avacado.html")
	tb.add('images/Palette.png', lambda: tb.setSide(Tk.RIGHT), 'color palette', "palette.html")
	tb.add('images/avacado.png', lambda: tb.setSide(Tk.BOTTOM), 'fruit', "avacado.html")
	tb.add('images/Palette.png', lambda: tb.setSide(Tk.TOP), 'color palette', "palette.html")
	tb.add('images/CowboyHat3.png', lambda: tb.setVisible(NO), 'cowboy', "cowboy.html")
	app.mainloop()
