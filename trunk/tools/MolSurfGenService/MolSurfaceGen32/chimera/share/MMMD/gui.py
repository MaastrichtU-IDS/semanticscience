# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera
from chimera.baseDialog import ModelessDialog

class mmmdDialog(ModelessDialog):
	name = "Minimize Structure"
	help = "ContributedSoftware/minimize/minimize.html"
	buttons = ("Minimize", "Close")
	keepShown = "Minimize"

	def fillInUI(self, parent):
		import Tkinter
		from chimera.widgets import MoleculeScrolledListBox
		self.molList = MoleculeScrolledListBox(parent,
						listbox_selectmode="extended")
		self.molList.pack(expand=True, fill="both")
		self.minimizeOptions = MinimizeOptions(parent)
		self.minimizeOptions.pack(expand=False, fill="both")

	def Apply(self):
		molecules = self.molList.getvalue()
		if not molecules:
			from chimera import UserError
			raise UserError("Please select a molecule to minimize")
		import base
		base.Minimizer(molecules, callback=self.run)

	def run(self, minimizer):
		self.minimizeOptions.setOptions(minimizer)
		minimizer.run()

	def Dynamics(self):
		raise chimera.LimitationError("MD is unimplemented")


from chimera.tkoptions import EnumOption
import base
class FreezeOption(EnumOption):
	values = (base.FreezeNone, base.FreezeSelected, base.FreezeUnselected)

import Tkinter
class MinimizeOptions(Tkinter.Frame):

	def __init__(self, parent):
		from chimera.tkoptions import IntOption, FloatOption
		Tkinter.Frame.__init__(self, parent)
		self.nsteps = IntOption(self, 0, "Steps", 100, None)
		self.stepsize = FloatOption(self, 1, "Step size (A)",
						0.02, None,
						min=0.0001, max=1.0)
		self.interval = IntOption(self, 2, "Update interval", 10, None)
		self.freeze = FreezeOption(self, 3, "Fixed atoms",
						base.FreezeNone, None)

	def setOptions(self, minimizer):
		minimizer.nsteps = self.nsteps.get()
		minimizer.stepsize = self.stepsize.get()
		minimizer.interval = self.interval.get()
		minimizer.freeze = self.freeze.get()

from chimera import dialogs
dialogs.register(mmmdDialog.name, mmmdDialog)
