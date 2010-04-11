# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: AngleDial.py 26655 2009-01-07 22:02:30Z gregc $

# Dial widget that shows a turnable knob for setting an angle.
#
import math
import Tkinter
import Pmw

# Radius is in any Tk-acceptable format.
# Command callback takes an angle argument (degrees).
#
class AngleDial(Pmw.MegaWidget):

	def __init__(self, parent=None, **kw):
	
		# Define the megawidget options
		optiondefs = (
			('angle',	0.0,		self._angleCB),
			('command',	None,		None),
			('fill',	'light gray',	self._fillCB),
			('line',	'black',	self._lineCB),
			('outline',	'black',	self._outlineCB),
			('radius',	'.5i',		self._radiusCB),
			('labelmargin',	0,			Pmw.INITOPT),
			('labelpos',	None,			Pmw.INITOPT),
			('rotDir',	'counterclockwise',	Pmw.INITOPT),
			('zeroAxis',	'x',			Pmw.INITOPT),
		)
		self.defineoptions(kw, optiondefs)

		# Initialise base class (after defining options)
		Pmw.MegaWidget.__init__(self, parent)

		# Create the components
		interior = self.interior()

		# Create the canvas component
		self.canvas = self.createcomponent('canvas', (), None,
			Tkinter.Canvas, (interior,))
		self.canvas.grid(row=1, column=1)
		interior.rowconfigure(1, weight=1)
		interior.columnconfigure(1, weight=1)
		self.canvas.bind('<Button1-Motion>', self.pointer_drag_cb)
		self.canvas.bind('<ButtonRelease-1>', self.button_release_cb)
		self.oval = None
		self.line = None
		self.lineMul = 1.2 # line length as multiple of radius

		# Optionally create the label component
		self.createlabel(interior)

		# Check keywords and initialise options
		self._initializing = 1
		self.initialiseoptions(AngleDial)
		self._initializing = 0
		self._drawDial()

	def _angleCB(self):
		if self._initializing:
			return
		self._drawDial()
		if self['command']:
			self['command'](self['angle'])

	def _fillCB(self):
		if self._initializing:
			return
		self.canvas.itemconfigure(self.oval, fill=self['fill'])

	def _lineCB(self):
		if self._initializing:
			return
		self.canvas.itemconfigure(self.line, fill=self['line'])

	def _outlineCB(self):
		if self._initializing:
			return
		self.canvas.itemconfigure(self.oval, outline=self['outline'])

	def _radiusCB(self):
		if self.oval:
			self.canvas.delete(self.oval)
		if self.line:
			self.canvas.delete(self.line)
		
		self.radius = self.canvas.winfo_pixels(self['radius'])
		bump_size = (self.lineMul - 1) * self.radius

		s = int(2 * (self.radius + bump_size))
		self.canvas.configure(width=s, height=s)

		c = bump_size + self.radius
		kw = {
			'fill': self['fill'],
			'outline': self['outline']
		}
		self.oval = apply(self.canvas.create_oval, (c-self.radius,
			c-self.radius, c+self.radius, c+self.radius), kw)
		
		kw = {'fill': self['line']}
		self.line = apply(self.canvas.create_line, (c, c, 0, 0), kw)
		self._drawDial()

	def pointer_drag_cb(self, event):
		try:
			a = self.event_angle(event)
		except ValueError:
			pass
		else:
			self.configure(angle=a)

	def button_release_cb(self, event):
		try:
			a = self.event_angle(event)
		except ValueError:
			pass
		else:
			self.configure(angle=a)

	def event_angle(self, event):
		# math.atan2 may raise ValueError if dx and dy are zero.
		(x, y) = self.canvas_coordinates(self.canvas, event)
		cx = cy = self.lineMul * self.radius
		(dx, dy) = (x - cx, cy - y)
		rad = math.atan2(dy, dx)
		deg = 180 * rad / math.pi
		if self['zeroAxis'] in ['y','n']:
			deg = deg + 270
		elif self['zeroAxis'] in ['-x','w']:
			deg = deg + 180
		elif self['zeroAxis'] in ['-y','s']:
			deg = deg + 90

		if self['rotDir'] == 'clockwise':
			deg = 360 - deg

		while deg > 180.0:
			deg = deg - 360
		while deg <= -180.0:
			deg = deg + 360
		return deg

	def _drawDial(self):
		cx = cy = d = self.radius * self.lineMul
		cartesian = self['angle']
		if self['rotDir'] == 'clockwise':
			cartesian = 360 - cartesian
		if self['zeroAxis'] in ['y','n']:
			cartesian = cartesian + 90
		elif self['zeroAxis'] in ['-x','w']:
			cartesian = cartesian + 180
		elif self['zeroAxis'] in ['-y','s']:
			cartesian = cartesian + 270
		while cartesian > 180.0:
			cartesian = cartesian - 360
		while cartesian <= -180.0:
			cartesian = cartesian + 360
		rad = math.pi * cartesian / 180.0
		ox = d * math.cos(rad)
		oy = d * math.sin(rad)
		self.canvas.coords(self.line, cx, cy, cx + ox, cy - oy)

	def canvas_coordinates(self, canvas, event):
		return (canvas.canvasx(event.x), canvas.canvasy(event.y))
