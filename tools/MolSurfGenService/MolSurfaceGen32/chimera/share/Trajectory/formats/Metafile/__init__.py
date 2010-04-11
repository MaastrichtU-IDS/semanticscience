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

formatName = "metafile"

class ParamGUI:
	labels = ["Movie metafile"]

	def __init__(self, parent):
		from Trajectory.prefs import prefs, INPUT_FILES
		inputPrefs = prefs[INPUT_FILES].setdefault('metafile', {})
		self.options = []
		for i in range(len(self.labels)):
			label = self.labels[i]
			self.options.append(InputFileOption(parent, i, 
				label, inputPrefs.get(label, True),
				None, title="Choose %s" % label,
				historyID="Movie metafile %s" % label))
		parent.columnconfigure(1, weight=1)

	def loadEnsemble(self, startFrame, endFrame, callback):
		args = []
		from Trajectory.prefs import prefs, INPUT_FILES
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
			inputPrefs['metafile'][label] = path
			args.append(path)
		prefs[INPUT_FILES] = inputPrefs

		loadEnsemble(args, startFrame, endFrame, callback)

	def setpath(self, movieFile):
		self.options[0].set(movieFile)

def loadEnsemble(inputs, startFrame, endFrame, callback, relativeTo=None):
	from Trajectory.EnsembleLoader import loadEnsemble
	movieFile = inputs[0]
	import os.path
	if relativeTo and not os.path.isabs(movieFile):
		movieFile = os.path.join(relativeTo, movieFile)
	loadEnsemble(callback, movieFile=movieFile,
					start=startFrame, end=endFrame)
