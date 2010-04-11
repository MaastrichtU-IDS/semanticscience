# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: VolumeDialog.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter, Pmw
from chimera.baseDialog import ModelessDialog
from prefs import prefs, VOLUME_CUTOFF, VOLUME_RESOLUTION
import chimera

class VolumeDialog(ModelessDialog):
	title = "Calculate Atomic Occupancy"
	help = "ContributedSoftware/movie/movie.html#occupancy"
	provideStatus = True
	statusPosition = "left"
	buttons = ('OK', 'Close')
	default= 'OK'

	def __init__(self, movie):
		self.movie = movie
		movie.subdialogs.append(self)
		ModelessDialog.__init__(self)

	def map(self, e=None):
		if not self.movie.holdingSteady:
			self.status("No atoms being held steady -- see Help",
							color="red")
	def fillInUI(self, parent):
		Tkinter.Label(parent, text="Collect positions of selected"
			" atoms over trajectory", relief="ridge", bd=4).grid(
			row=0, column=0, columnspan=2, sticky="ew")

		startFrame = self.movie.startFrame
		endFrame = self.movie.endFrame
		from chimera.tkoptions import IntOption, BooleanOption, \
						FloatOption, StringOption
		self.startFrame = IntOption(parent, 1, "Starting frame",
			startFrame, None, min=startFrame, max=endFrame, width=6)

		numFrames = endFrame - startFrame + 1
		defStride = 1 + int(numFrames/300)
		self.stride = IntOption(parent, 2, "Step size", defStride,
			None, min=1, max=numFrames, width=3)

		self.endFrame = IntOption(parent, 3, "Ending frame", endFrame,
			None, min=startFrame, max=endFrame, width=6)

		self.doCutoff = BooleanOption(parent, 4, 'Limit data collection'
			' to within cutoff distance of any "held steady" atoms',
			True, None)

		self.cutoff = FloatOption(parent, 5, "Cutoff distance",
				prefs[VOLUME_CUTOFF], None, width=4)
		self.resolution = FloatOption(parent, 6, "Volume grid spacing",
			prefs[VOLUME_RESOLUTION], None, min=0.0001, width=4)
		self.volumeName = StringOption(parent, 7, "Volume data name",
			self.movie.ensemble.name, None, width=20)
		self.byAtomType = BooleanOption(parent, 8, "Collect data"
			" separately for each atom type in selection",
			True, None, balloon="Create a volume data set for"
			" each type of atom type\n(sp2 oxygen, aromatic carbon,"
			" etc.) in current selection")

	def Apply(self):
		from chimera import UserError
		atoms = chimera.selection.currentAtoms()
		if not atoms:
			self.enter()
			raise UserError("No atoms selected")
		startFrame = self.startFrame.get()
		endFrame = self.endFrame.get()
		if endFrame <= startFrame:
			self.enter()
			raise UserError("Start frame must be less"
							" than end frame")
		if startFrame < self.movie.startFrame \
		or endFrame > self.movie.endFrame:
			self.enter()
			raise UserError("Start or end frame outside"
							" of trajectory")
		if self.doCutoff.get():
			bound = prefs[VOLUME_CUTOFF] = self.cutoff.get()
		else:
			bound = None
		prefs[VOLUME_RESOLUTION] = self.resolution.get()
		step = self.stride.get()
		spacing = self.resolution.get()
		name = self.volumeName.get()
		atomTypes = {}
		if self.byAtomType.get():
			for a in atoms:
				atomTypes.setdefault(a.idatmType, []).append(a)
		if len(atomTypes) > 1:
			for atomType, atAtoms in atomTypes.items():
				self.movie.computeVolume(atAtoms,
					startFrame=startFrame,
					endFrame=endFrame, step=step,
					bound=bound, spacing=spacing,
					volumeName=name+" ["+atomType+"]")
		else:
			self.movie.computeVolume(atoms, startFrame=startFrame,
				endFrame=endFrame, step=step, bound=bound,
				spacing=spacing, volumeName=name)
