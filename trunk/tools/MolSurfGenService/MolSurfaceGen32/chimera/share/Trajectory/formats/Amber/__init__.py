# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 26655 2009-01-07 22:02:30Z gregc $

import os.path
import Tkinter
import chimera
from chimera.tkoptions import InputFileOption, OrderedFileListOption

class ParamGUI:
	def __init__(self, parent):
		from Trajectory.prefs import prefs, INPUT_FILES
		inputPrefs = prefs[INPUT_FILES].setdefault('Amber', {})
		self.prmtopOption = InputFileOption(parent, 0, "Prmtop",
				inputPrefs.get('Prmtop', True),
				None, filters=[("Prmtop", ["*.top"])],
				title="Choose Prmtop File",
				entryWidth=20, historyID="AmberPrmtop")
		
		defaultTrajs = inputPrefs.get('Trajectories', None)
		if defaultTrajs is None and 'Trajectory' in inputPrefs:
			defaultTrajs = [inputPrefs['Trajectory']]
		from Amber import Amber
		self.trajectoriesOption = OrderedFileListOption(parent, 1,
						"Trajectory", defaultTrajs,
						None, addKw=Amber.AddTrajKw)
		parent.columnconfigure(1, weight=1)
		parent.rowconfigure(1, weight=1)

	def loadEnsemble(self, startFrame, endFrame, callback):
		prmtop = self.prmtopOption.get()
		trajectories = self.trajectoriesOption.get()
		from chimera import UserError
		if not os.path.exists(prmtop):
			raise UserError("Parmtop file does not exist!")
		if not trajectories:
			raise UserError("No trajectory files specified")
		for traj in trajectories:
			if not os.path.exists(traj):
				raise UserError("Trajectory coordinate file"
					" (%s) does not exist!" % traj)
		from Trajectory.prefs import prefs, INPUT_FILES
		# need to change a _copy_ of the dictionary, otherwise
		# when we try to save the "original" dictionary will also
		# have our changes and no save will occur
		from copy import deepcopy
		inputPrefs = deepcopy(prefs[INPUT_FILES])
		inputPrefs['Amber']['Prmtop'] = prmtop
		inputPrefs['Amber']['Trajectories'] = trajectories
		prefs[INPUT_FILES] = inputPrefs

		loadEnsemble([prmtop] + trajectories, startFrame, endFrame,
								callback)

def loadEnsemble(inputs, startFrame, endFrame, callback, relativeTo=None):
	# don't import until now so that Amber-specific PDBio changes
	# don't occur until needed
	from Amber import Amber
	if relativeTo:
		import os.path
		for i, f in enumerate(inputs):
			if os.path.isabs(f):
				continue
			inputs[i] = os.path.join(relativeTo, f)
	prmtop, trajectory = inputs[:2]
	ensemble = Amber(prmtop, trajectory, startFrame, endFrame)
	for traj in inputs[2:]:
		ensemble.addTraj(traj)
	from chimera import replyobj
	replyobj.status("Creating interface\n", blankAfter=0)
	try:
		callback(ensemble)
	finally:
		replyobj.status("Interface created\n")
