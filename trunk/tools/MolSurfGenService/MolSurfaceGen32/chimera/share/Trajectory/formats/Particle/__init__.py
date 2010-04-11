# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: __init__.py 27295 2009-04-02 21:43:33Z pett $

import os
import os.path
import Tkinter
import chimera
from chimera.tkoptions import InputFileOption

formatName = "particle"

class ParamGUI:
	labels = ["Particle"]

	def __init__(self, parent):
		from Trajectory.prefs import prefs, INPUT_FILES
		inputPrefs = prefs[INPUT_FILES].setdefault(formatName, {})
		self.options = []
		globs = ["*.ptrj"]
		for ext in chimera.fileInfo.extensions("NetCDF generic array"):
			globs.append("*" + ext)
		filters = [("Particle trajectory", globs)]
		for i, label in enumerate(self.labels):
			self.options.append(InputFileOption(parent, i, label,
				inputPrefs.get(label, True), None,
				title="Choose %s File" % label,
				filters=filters, historyID="Particle %s" % label))
		parent.columnconfigure(1, weight=1)

	def loadEnsemble(self, startFrame, endFrame, callback):
		from Trajectory.prefs import prefs, INPUT_FILES
		args = []
		# need to change a _copy_ of the dictionary, otherwise
		# when we try to save the "original" dictionary will also
		# have our changes and no save will occur
		from copy import deepcopy
		inputPrefs = deepcopy(prefs[INPUT_FILES])
		for i, label in enumerate(self.labels):
			path = self.options[i].get()
			if not os.path.exists(path):
				raise ValueError("%s file '%s' does not exist!" % (
								label, path))
			inputPrefs[formatName][label] = path
			args.append(path)
		prefs[INPUT_FILES] = inputPrefs

		loadEnsemble(args, startFrame, endFrame, callback)

def loadEnsemble(inputs, startFrame, endFrame, callback, relativeTo=None):
	from chimera import replyobj
	files = inputs[:]
	if relativeTo:
		for i, f in enumerate(files):
			if not isinstance(f, basestring) or os.path.isabs(f):
				continue
			files[i] = os.path.join(relativeTo, f)
	replyobj.status("Reading %s file\n" % formatName, blankAfter=0)
	if startFrame is None:
		startFrame = 1
	if endFrame is not None and startFrame > endFrame:
		raise ValueError("Start frame > end frame")
	from Scientific.IO import NetCDF
	fileName = files[0]
	ncInfo = NetCDF.NetCDFFile(fileName, 'r')
	replyobj.status("Done reading %s file\n" % formatName)
	if getattr(ncInfo, 'Conventions', None) != "CCD":
		raise ValueError("%s is not a particle trajectory file" % fileName)
	numParticles = ncInfo.dimensions['particle']
	if endFrame is not None and endFrame > numParticles:
		raise ValueError("End frame (%d) > number of particles in file (%d)"
			% (endFrame, numParticles))

	from Particle import ParticleTraj
	replyobj.status("Creating trajectory\n", blankAfter=0)
	try:
		ensemble = ParticleTraj(os.path.basename(fileName), ncInfo)
	except:
		replyobj.status("Error creating trajectory\n")
		raise
	ensemble.startFrame = startFrame
	ensemble.endFrame = endFrame
	replyobj.status("Creating interface\n", blankAfter=0)
	try:
		callback(ensemble)
	finally:
		replyobj.status("Interface created\n")
