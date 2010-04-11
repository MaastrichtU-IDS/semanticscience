# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: VolumeDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog

class VolumeDialog(ModelessDialog):
	title = "Volume Map Selection"
	buttons = ("OK", "Apply", "Close")
	help = "ContributedSoftware/rotamers/rotamers.html#density"

	def __init__(self, rotDialog):
		self.rotDialog = rotDialog
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		import Tkinter
		row = 0
		from VolumeViewer import Volume_Menu
		self.volumeMenu = Volume_Menu(parent, 'Volume data',
							open_button=True)
		self.volumeMenu.frame.grid(row=row, columnspan=2)
		row += 1

		from chimera.tkoptions import StringOption
		self.nameOption = StringOption(parent, row, 'Column name',
						'Density', None, width=10)
		row += 1

	def Apply(self):
		from chimera import UserError
		dr = self.volumeMenu.data_region()
		if not dr:
			self.enter()
			raise UserError("No volume chosen")
		name = self.nameOption.get().strip()
		if not name:
			self.enter()
			raise UserError("Column name must not be blank")
		self.rotDialog.addVolumeColumn(name, dr)

	def destroy(self):
		self.rotDialog = None
		ModelessDialog.destroy(self)
