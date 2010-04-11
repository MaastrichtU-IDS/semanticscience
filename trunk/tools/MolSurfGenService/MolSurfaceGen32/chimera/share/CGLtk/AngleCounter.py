# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: AngleCounter.py 26655 2009-01-07 22:02:30Z gregc $

"""Specialization of Pmw.Counter for angles"""

import Pmw
from CGLtk.AngleDial import AngleDial
import math

class AngleCounter(Pmw.MegaWidget):

	def __init__(self, parent = None, **kw):

		# Define the megawidget options
		optiondefs = (
			('angle',	0.0,	self._angleCB),
			('command',	None,	None),
			('dialpos',	'w',	Pmw.INITOPT),
			('labelmargin',	0,	Pmw.INITOPT),
			('labelpos',	None,	Pmw.INITOPT),
			('minangle',	-180.0,	Pmw.INITOPT),
		)
		self.defineoptions(kw, optiondefs)

		# Initialise base class (after defining options)
		Pmw.MegaWidget.__init__(self, parent)

		# Create the components
		interior = self.interior()

		# Create the dial component, maybe
		dialpos = self['dialpos']
		if dialpos is not None:
			self.dial = self.createcomponent('dial', (), None,
				AngleDial, (interior,),
				command=self._dialChange)
			if dialpos == 'w':
				dialRow, dialColumn = (2, 2)
				counterRow, counterColumn = (2, 3)
				childRows, childCols = (1, 2)
			elif dialpos == 'n':
				dialRow, dialColumn = (2, 2)
				counterRow, counterColumn = (3, 2)
				childRows, childCols = (2, 1)
			elif dialpos == 'e':
				dialRow, dialColumn = (2, 3)
				counterRow, counterColumn = (2, 2)
				childRows, childCols = (1, 2)
			else:
				dialRow, dialColumn = (3, 2)
				counterRow, counterColumn = (2, 2)
				childRows, childCols = (2, 1)
			self.dial.grid(row=dialRow, column=dialColumn, 
								sticky='nsew')
			interior.rowconfigure(dialRow, weight=1)
			interior.columnconfigure(dialColumn, weight=1)
		else:
			counterRow, counterColumn = (2, 2)
			childRows, childCols = (1, 1)
			interior.rowconfigure(2, weight=1)
			interior.columnconfigure(2, weight=1)
		
		# Create the counter component
		self.counter = self.createcomponent('counter', (), None,
			Pmw.Counter, (interior,), datatype=self._incrCounter,
			entryfield_command=self._counterChange, entry_width=8)
		if self.counter['orient'] == 'horizontal':
			sticky='ew'
		else:
			sticky='nsew'
		self.counter.grid(row=counterRow, column=counterColumn,
								sticky=sticky)
		
		# Optionally create the label component
		self.createlabel(interior, childRows=childRows,
							childCols=childCols)
		 
		# Check keywords and initialise options
		self.initialiseoptions(AngleCounter)
	
	def _angleCB(self):
		if hasattr(self, '_inAngleCB') and self._inAngleCB:
			return
		self._inAngleCB = 1
		self['angle'] = self.normalize(self['angle'])
		if self['dialpos'] is not None:
			self.dial.configure(angle=self['angle'])
		self.counter.setentry(str(self['angle']))
		self._inAngleCB = 0
	
	def _counterChange(self):
		"""callback from counter entryfield"""

		degrees = float(self.counter.component('entry').get())
		degrees = self.normalize(degrees)
		if self['dialpos'] is not None:
			# setting dial will result in callback to counter
			self.dial.configure(angle=degrees)
		else:
			self._mkCmdCB(degrees)

	def _dialChange(self, degrees):
		"""callback from dial"""

		degrees = self.normalize(degrees)
		self.counter.setentry(str(degrees))
		self._mkCmdCB(degrees)

	def _incrCounter(self, cur, upDown, incr, **kw):
		degrees = float(cur)
		if upDown > 0:
			degrees = degrees + incr
		else:
			degrees = degrees - incr
		if incr >= 1.0:
			degrees = math.floor(degrees + 0.5)
		degrees = self.normalize(degrees)
		if self['dialpos'] is not None:
			self.dial.configure(angle=degrees)
		else:
			self._mkCmdCB(degrees)
		return str(degrees)

	def _mkCmdCB(self, degrees):
		if self['command']:
			if not hasattr(self, '_inAngleCB') \
			or not self._inAngleCB:
				self['command'](degrees)
	
	def normalize(self, degrees):
		"""return angle given constraint of self['minangle']"""

		if self['minangle'] is None:
			return degrees
		
		minangle = self['minangle']
		while degrees < minangle:
			degrees = degrees + 360
		while degrees >= minangle + 360:
			degrees = degrees - 360
		return degrees

Pmw.forwardmethods(AngleCounter, Pmw.Counter, 'counter')
