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

class ParamGUI:
	"""subclass expected to provide self.formatName"""
	labels = ["PSF", "DCD"]

	def __init__(self, parent):
		from Trajectory.prefs import prefs, INPUT_FILES
		inputPrefs = prefs[INPUT_FILES].setdefault(self.formatName, {})
		self.options = []
		for i in range(len(self.labels)):
			label = self.labels[i]
			self.options.append(InputFileOption(parent, i, 
				label, inputPrefs.get(label, True),
				None, title="Choose %s File" % label,
				historyID="%s %s" % (self.formatName, label)))
		parent.columnconfigure(1, weight=1)
		f = Tkinter.Frame(parent)
		f.grid(row=len(self.labels), column=0, columnspan=2)
		Tkinter.Label(f, text="PSF/DCD support courtesy of"
				).grid(row=0, column=0, sticky='e')
		from chimera import help
		Tkinter.Button(f, text="MDTools", padx=0, pady=0,
				command=lambda: help.display(
				"http://www.ks.uiuc.edu/~jim/mdtools/")
				).grid(row=0, column=1, sticky='w')

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
			inputPrefs[self.formatName][label] = path
			args.append(path)
		prefs[INPUT_FILES] = inputPrefs

		loadEnsemble(args, startFrame, endFrame, callback)

def loadEnsemble(inputs, startFrame, endFrame, callback, relativeTo=None):
	from DCD import DCD
	if relativeTo:
		import os.path
		for i, f in enumerate(inputs):
			if not isinstance(f, basestring) or os.path.isabs(f):
				continue
			inputs[i] = os.path.join(relativeTo, f)
	ensemble = DCD(*tuple(inputs + [startFrame, endFrame]))
	from chimera import replyobj
	replyobj.status("Creating interface\n", blankAfter=0)
	try:
		callback(ensemble)
	finally:
		replyobj.status("Interface created\n")
