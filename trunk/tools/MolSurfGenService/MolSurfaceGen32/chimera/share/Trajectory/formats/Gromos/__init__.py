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
from chimera.tkoptions import InputFileOption, FloatOption

formatName = "GROMOS"

class ParamGUI:
	labels = ["Topology", "Coordinates", "PROMD"]

	def __init__(self, parent):
		from Trajectory.prefs import prefs, INPUT_FILES, GROMOS_SCALING
		inputPrefs = prefs[INPUT_FILES].setdefault('Gromos', {})
		self.options = []
		for i in range(len(self.labels)):
			label = self.labels[i]
			self.options.append(InputFileOption(parent, i,
				label, inputPrefs.get(label, True),
				None, title="Choose %s File" % label,
				historyID="Gromos %s" % label))
		self.scalingOption = FloatOption(parent, len(self.labels),
			"Angstrom conversion", prefs[GROMOS_SCALING], None,
			balloon="scale factor to convert trajectory\n"
			"coordinates to angstroms", width=4, sticky='w')
		parent.columnconfigure(1, weight=1)

	def loadEnsemble(self, startFrame, endFrame, callback):
		args = []
		from Trajectory.prefs import prefs, INPUT_FILES, GROMOS_SCALING
		# need to change a _copy_ of the dictionary, otherwise
		# when we try to save the "original" dictionary will also
		# have our changes and no save will occur
		from copy import deepcopy
		inputPrefs = deepcopy(prefs[INPUT_FILES])
		for i in range(len(self.labels)):
			path = self.options[i].get()
			label = self.labels[i]
			if not os.path.exists(path):
				raise ValueError, \
					"%s file '%s' does not exist!" % (
								label, path)
			inputPrefs['Gromos'][label] = path
			args.append(path)
		prefs[INPUT_FILES] = inputPrefs
		scale = self.scalingOption.get()
		prefs[GROMOS_SCALING] = scale
		args.append(scale)

		loadEnsemble(args, startFrame, endFrame, callback)

def loadEnsemble(inputs, startFrame, endFrame, callback, relativeTo=None):
	from Gromos import Gromos
	if relativeTo:
		import os.path
		for i, f in enumerate(inputs[:-1]):
			if not isinstance(f, basestring) or os.path.isabs(f):
				continue
			inputs[i] = os.path.join(relativeTo, f)
	ensemble = Gromos(*tuple(inputs + [startFrame, endFrame]))
	from chimera import replyobj
	replyobj.status("Creating interface\n", blankAfter=0)
	try:
		callback(ensemble)
	finally:
		replyobj.status("Interface created\n")
