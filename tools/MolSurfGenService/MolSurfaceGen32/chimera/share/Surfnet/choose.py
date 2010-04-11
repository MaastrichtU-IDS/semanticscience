# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import Tkinter
import Pmw

import chimera
from chimera import tkoptions
from chimera.baseDialog import ModelessDialog
import base
from chimera import replyobj

class SurfnetOptions:

	def setupOptions(self, f, row=0):
		class ReprOption(tkoptions.EnumOption):
			values = ('Mesh', 'Surface')
		self.reprType = ReprOption(f, row, 'Representation',
						ReprOption.values[0], None)

		class DensityOption(tkoptions.EnumOption):
			values = ('Gaussian', 'Quadratic')
		self.density = DensityOption(f, row + 1, 'Density',
						DensityOption.values[0], None)

		self.gridInterval = tkoptions.FloatOption(f, row + 2,
						'Grid Interval', 1.0, None)
		self.cutoff = tkoptions.FloatOption(f, row + 3,
						'Distance Cutoff', 10.0, None)
		self.color = tkoptions.ColorOption(f, row + 4,
						'Color', None, None)

class SelectionSurfnetCB(ModelessDialog, SurfnetOptions):

	title = 'Surfnet Selection'
	help = 'ContributedSoftware/surfnet/surfnet.html'

	def fillInUI(self, parent):
		if not chimera.openModels.list():
			print 'No models opened'
			return
		self.selection = tkoptions.StringOption(parent, 0,
						'Midas Selection', '', None)
		self.setupOptions(parent, row=1)

	def Apply(self):
		sel = self.selection.get()
		if sel == '':
			replyobj.error('Midas selection is empty')
			return
		error = base.atoms_surfnet(sel,
					useMesh=self.reprType.get() == 'Mesh',
					cutoff=self.cutoff.get(),
					density=self.density.get(),
					interval=self.gridInterval.get(),
					color=self.color.get())
		if error:
			replyobj.error(error)

class InterfaceSurfnetCB(SelectionSurfnetCB):

	title = 'Surfnet Interface'
	help = 'ContributedSoftware/surfnet/surfnet.html'

	def fillInUI(self, parent):
		self.receptor = tkoptions.StringOption(parent, 0, 'Receptor',
							'', None)
		self.ligands = tkoptions.StringOption(parent, 1, 'Ligands',
							'', None)
		self.setupOptions(parent, row=2)

	def Apply(self):
		receptor = self.receptor.get()
		if receptor == '':
			replyobj.error('Receptor selection is empty')
			return
		ligands = self.ligands.get()
		if ligands == '':
			replyobj.error('Ligands selection is empty')
			return
		error = base.interface_surfnet(receptor, ligands,
					useMesh=self.reprType.get() == 'Mesh',
					cutoff=self.cutoff.get(),
					density=self.density.get(),
					interval=self.gridInterval.get(),
					color=self.color.get())
		if error:
			replyobj.error(error)
