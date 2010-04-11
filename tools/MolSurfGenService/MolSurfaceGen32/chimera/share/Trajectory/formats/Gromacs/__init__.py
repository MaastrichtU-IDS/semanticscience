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
from chimera.tkoptions import InputFileOption

formatName = "GROMACS"

class ParamGUI:
	def __init__(self, parent):
		from Trajectory.prefs import prefs, INPUT_FILES
		inputPrefs = prefs[INPUT_FILES].setdefault('Gromacs', {})
		self.topologyOption = InputFileOption(parent, 1,
				"Run input (.tpr)",
				inputPrefs.get('Topology', True),
				None, filters=[("Topology", ["*.tpr"])],
				title="Choose .tpr File",
				entryWidth=20, historyID="GromacsTop")
		
		self.trajectoryOption = InputFileOption(parent, 2,
			"Trajectory (.trr)",
			inputPrefs.get('Trajectory', True), None,
			entryWidth=20, title="Choose Trajectory File",
			filters=[("Portable trajectory", ["*.trr"])],
			defaultFilter=0, historyID="GromacsTrajectory")
		parent.columnconfigure(1, weight=1)

	def loadEnsemble(self, startFrame, endFrame, callback):
		topology = self.topologyOption.get()
		trajectory = self.trajectoryOption.get()
		if not os.path.exists(topology):
			raise ValueError("Topology file does not exist!")
		if not os.path.exists(trajectory):
			raise ValueError("Trajectory file does not exist!")
		from Trajectory.prefs import prefs, INPUT_FILES
		# need to change a _copy_ of the dictionary, otherwise
		# when we try to save the "original" dictionary will also
		# have our changes and no save will occur
		from copy import deepcopy
		inputPrefs = deepcopy(prefs[INPUT_FILES])
		inputPrefs['Gromacs']['Topology'] = topology
		inputPrefs['Gromacs']['Trajectory'] = trajectory
		prefs[INPUT_FILES] = inputPrefs

		loadEnsemble((topology, trajectory),
						startFrame, endFrame, callback)

def loadEnsemble(inputs, startFrame, endFrame, callback, relativeTo=None):
	from Gromacs import Gromacs
	if relativeTo:
		import os.path
		for i, f in enumerate(inputs):
			if os.path.isabs(f):
				continue
			inputs[i] = os.path.join(relativeTo, f)
	topology, trajectory = inputs
	ensemble = Gromacs(topology, trajectory, startFrame, endFrame)
	from chimera import replyobj
	replyobj.status("Creating interface\n", blankAfter=0)
	try:
		callback(ensemble)
	finally:
		replyobj.status("Interface created\n")
