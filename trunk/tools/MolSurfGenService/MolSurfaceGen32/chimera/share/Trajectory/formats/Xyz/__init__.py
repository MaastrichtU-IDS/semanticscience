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
from chimera.tkoptions import InputFileOption, EnumOption

formatName = "XYZ"

class ParamGUI:
	multiStart = "First file"
	multiEnd = "Last file"
	def __init__(self, parent):
		from Trajectory.prefs import prefs, INPUT_FILES
		inputPrefs = prefs[INPUT_FILES].setdefault(formatName, {})
		self.options = {}
		globs = []
		for ext in chimera.fileInfo.extensions("XYZ"):
			globs.append("*" + ext)
		filters = [("XYZ", globs)]
		self.multiFrame = Tkinter.Frame(parent)
		self.multiFrame.columnconfigure(1, weight=1)
		self.options[self.multiStart] = InputFileOption(
			self.multiFrame, 0, self.multiStart,
			inputPrefs.get(self.multiStart, True), None,
			title="Choose First XYZ File", defaultFilter="XYZ",
			filters=filters, historyID="XYZ traj multi start")
		self.options[self.multiEnd] = InputFileOption(self.multiFrame,
			1, self.multiEnd, inputPrefs.get(self.multiEnd, True),
			None, title="Choose Last XYZ File", defaultFilter="XYZ",
			filters=filters, historyID="XYZ traj multi end")
		parent.columnconfigure(1, weight=1)
		self.multiFrame.grid(row=1, columnspan=2, sticky="ew")

	def loadEnsemble(self, startFrame, endFrame, callback):
		from Trajectory.prefs import prefs, INPUT_FILES
		args = []
		# need to change a _copy_ of the dictionary, otherwise
		# when we try to save the "original" dictionary will also
		# have our changes and no save will occur
		from copy import deepcopy
		inputPrefs = deepcopy(prefs[INPUT_FILES])
		relevant = [self.multiStart, self.multiEnd]
		for prefName in relevant:
			option = self.options[prefName]
			path = option.get()
			if not os.path.exists(path):
				raise ValueError, \
					"%s file '%s' does not exist!" % (
								prefName, path)
			inputPrefs['XYZ'][prefName] = path
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
	startFile, endFile = files
	errMsg = "Can't determine numeric sequence from starting file name (%s) to ending file name (%s)" % (startFile, endFile)
	for i, c in enumerate(startFile):
		if i >= len(endFile):
			raise ValueError(errMsg)
		if endFile[i] != c:
			break
	else:
		raise ValueError(errMsg)
	# push trailing digits on the prefix back into the number part,
	# otherwise ranges like 1-100 are bug problems
	while i > 0 and startFile[i-1].isdigit():
		i -= 1
	prefixIndex = i
	prefix = startFile[:i]
	while i < len(startFile) and startFile[i].isdigit():
		i += 1
	startSuffixIndex = i
	endSuffixIndex = i + len(endFile) - len(startFile)
	suffix = startFile[startSuffixIndex:]
	replyobj.status("Processing XYZ files\n", blankAfter=0)
	first = int(startFile[prefixIndex:startSuffixIndex])
	if first < 1:
		offset = 1 - first
		first += offset
		replyobj.info("Adjusting frame numbers to start at 1\n")
	else:
		offset = 0
	try:
		last = int(endFile[prefixIndex:endSuffixIndex]) + offset
	except ValueError:
		raise ValueError("Last file name not similar to first"
			" file name\nCan't determine numeric sequence")
	if startFrame is None:
		startFrame = first
	elif startFrame < first:
		replyobj.error("Starting frame (%d) less than first"
			" file's frame (%d); using the latter\n"
			% (startFrame, first))
		startFrame = first
	if endFrame is None:
		endFrame = last
	elif endFrame > last:
		replyobj.error("Ending frame (%d) greater than last"
			" file's frame (%d); using the latter\n"
			% (endFrame, last))
		endFrame = last
	if startFrame > endFrame:
		raise ValueError("Start frame > end frame")
	from ReadXYZ import readXYZ
	try:
		mol = readXYZ(startFile)[0]
	except Exception, v:
		raise ValueError("Problem reading first XYZ file (%s): %s"
			% (startFile, str(v)))
	crdSet1 = mol.activeCoordSet
	natoms = len(mol.atoms)
	zeroPad = len(startFile) == len(endFile)
	for f in range(startFrame+1, endFrame+1):
		if zeroPad:
			fname = prefix + "%0*d" % (startSuffixIndex
				- prefixIndex, f-offset) + suffix
		else:
			fname = prefix + "%d" % (f-offset) + suffix
		replyobj.status("Processing file %s\n" % fname,
							blankAfter=0)
		try:
			m = readXYZ(fname)[0]
		except Exception, v:
			mol.destroy()
			raise ValueError("Problem reading XYZ file %s: %s"
				% (fname, str(v)))
		if len(m.atoms) != natoms:
			mol.destroy()
			raise ValueError("%s does not contain the same number of atoms "
				" as %s" % (fname, startFile))
		setID = crdSet1.id + f - startFrame
		crdSet = mol.newCoordSet(setID)
		for a1, a2 in zip(mol.atoms, m.atoms):
			a1.setCoord(a2.coord(), crdSet)
		m.destroy()
		
	replyobj.status("Done processing XYZ files\n")
	class XyzTraj:
		def __len__(self):
			return len(self.molecule.coordSets)
	ensemble = XyzTraj()
	ensemble.name = "XYZ trajectory from %s..." % os.path.basename(files[0])
	ensemble.startFrame = startFrame
	ensemble.endFrame = endFrame
	ensemble.molecule = mol
	mol.name = os.path.basename(files[0])
	replyobj.status("Creating interface\n", blankAfter=0)
	try:
		callback(ensemble)
	finally:
		replyobj.status("Interface created\n")
