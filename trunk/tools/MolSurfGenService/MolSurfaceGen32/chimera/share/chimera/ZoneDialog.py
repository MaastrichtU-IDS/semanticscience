# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: ZoneDialog.py 26655 2009-01-07 22:02:30Z gregc $

from baseDialog import ModelessDialog
import Tkinter
import Pmw

class ZoneDialog(ModelessDialog):
	name="zone specifier"
	title="Select Zone Parameters"
	buttons=('OK','Cancel')
	default='OK'
	help='UsersGuide/selection.html#selectzone'

	def fillInUI(self, parent):
		self.callback = None
		Tkinter.Label(parent, text='Select all atoms/bonds that'
			' meet all the chosen criteria below:').grid(row=10,
						column=1, columnspan=2)
		self.doCloser = Tkinter.IntVar(parent)
		self.doCloser.set(1)
		Tkinter.Checkbutton(parent, var=self.doCloser, takefocus=0
					).grid(row=20, column=1, sticky='e')
		closerFrame = Tkinter.Frame(parent)
		closerFrame.grid(row=20, column=2, sticky='w')
		self.closerEntry = Pmw.EntryField(closerFrame, labelpos='w',
			validate={'validator': 'real', 'min': 0.0},
			value='5.0', label_text='<', entry_width=5)
		self.closerEntry.component('entry').focus_set()
		self.closerEntry.component('entry').selection_range(0, 'end')
		self.closerEntry.grid(row=10, column=1, sticky='e')
		Tkinter.Label(closerFrame, text='angstroms from currently'
			' selected atoms').grid(row=10, column=2, sticky='w')
		
		self.doFurther = Tkinter.IntVar(parent)
		self.doFurther.set(0)
		Tkinter.Checkbutton(parent, var=self.doFurther, takefocus=0
					).grid(row=30, column=1, sticky='e')
		furtherFrame = Tkinter.Frame(parent)
		furtherFrame.grid(row=30, column=2, sticky='w')
		self.furtherEntry = Pmw.EntryField(furtherFrame, labelpos='w',
			validate={'validator': 'real', 'min': 0.0},
			value='5.0', label_text='>', entry_width=5)
		self.furtherEntry.grid(row=10, column=1, sticky='e')
		self.furtherEntry.component('entry').focus_set()
		Tkinter.Label(furtherFrame, text='angstroms from currently'
			' selected atoms').grid(row=10, column=2, sticky='w')
		
		self.doResidues = Tkinter.IntVar(parent)
		self.doResidues.set(0)
		Tkinter.Checkbutton(parent, var=self.doResidues, takefocus=0
					).grid(row=40, column=1, sticky='e')
		Tkinter.Label(parent, text='Select all atoms/bonds of any'
			' residue in selection zone').grid(row=40, column=2,
								sticky='w')

		for b in self.buttonWidgets.values():
			b.config(takefocus=0)


	def Apply(self):
		if self.callback:
			self.callback(self)
import dialogs
dialogs.register(ZoneDialog.name, ZoneDialog)
