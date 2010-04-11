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

formatName = "PDB"

class ParamGUI:
	single = "File"
	multiStart = "First file"
	multiEnd = "Last file"
	def __init__(self, parent):
		from Trajectory.prefs import prefs, INPUT_FILES, PDB_STYLE
		inputPrefs = prefs[INPUT_FILES].setdefault(formatName, {})
		class PdbStyleOption(EnumOption):
			values = ["single file", "multiple files"]
		self.style = PdbStyleOption(parent, 0,
				"PDB frames contained in", prefs[PDB_STYLE],
				self._styleChangeCB)
		self.options = {}
		globs = []
		for ext in chimera.fileInfo.extensions("PDB"):
			globs.append("*" + ext)
		filters = [("PDB", globs)]
		self.singleFrame = Tkinter.Frame(parent)
		self.singleFrame.columnconfigure(1, weight=1)
		self.options[self.single] = InputFileOption(self.singleFrame,
			0, self.single, inputPrefs.get(self.single, True), None,
			filters=filters, title="Choose Multi-model PDB File",
			defaultFilter="PDB", historyID="PDB traj multi-model")
		self.multiFrame = Tkinter.Frame(parent)
		self.multiFrame.columnconfigure(1, weight=1)
		self.options[self.multiStart] = InputFileOption(
			self.multiFrame, 0, self.multiStart,
			inputPrefs.get(self.multiStart, True), None,
			title="Choose First PDB File", defaultFilter="PDB",
			filters=filters, historyID="PDB traj multi start")
		self.options[self.multiEnd] = InputFileOption(self.multiFrame,
			1, self.multiEnd, inputPrefs.get(self.multiEnd, True),
			None, title="Choose Last PDB File", defaultFilter="PDB",
			filters=filters, historyID="PDB traj multi end")
		parent.columnconfigure(1, weight=1)
		self._styleChangeCB(self.style)

	def loadEnsemble(self, startFrame, endFrame, callback):
		from Trajectory.prefs import prefs, INPUT_FILES, PDB_STYLE
		style = self.style.get()
		prefs[PDB_STYLE] = style
		args = [style]
		# need to change a _copy_ of the dictionary, otherwise
		# when we try to save the "original" dictionary will also
		# have our changes and no save will occur
		from copy import deepcopy
		inputPrefs = deepcopy(prefs[INPUT_FILES])
		if style == "single file":
			relevant = [self.single]
		else:
			relevant = [self.multiStart, self.multiEnd]
		for prefName in relevant:
			option = self.options[prefName]
			path = option.get()
			if not os.path.exists(path):
				raise ValueError, \
					"%s file '%s' does not exist!" % (
								prefName, path)
			inputPrefs['PDB'][prefName] = path
			args.append(path)
		prefs[INPUT_FILES] = inputPrefs

		loadEnsemble(args, startFrame, endFrame, callback)

	def _styleChangeCB(self, opt):
		if opt.get() == "single file":
			self.multiFrame.grid_forget()
			self.singleFrame.grid(row=1, columnspan=2, sticky="ew")
		else:
			self.singleFrame.grid_forget()
			self.multiFrame.grid(row=1, columnspan=2, sticky="ew")

def loadEnsemble(inputs, startFrame, endFrame, callback, relativeTo=None):
	from chimera import replyobj
	style = inputs[0]
	files = inputs[1:]
	if relativeTo:
		for i, f in enumerate(files):
			if not isinstance(f, basestring) or os.path.isabs(f):
				continue
			files[i] = os.path.join(relativeTo, f)
	if style.lower().startswith("multiple"):
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
		replyobj.status("Collating PDB files\n", blankAfter=0)
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
		addMODEL = True
		sf = file(startFile, "r")
		for line in sf:
			if line.startswith("MODEL"):
				addMODEL = False
				break
			if line.strip() == "END":
				raise ValueError("PDB files must not contain"
								" END records")
		sf.close()
		from tempfile import mkstemp
		(handle, trajFile) = mkstemp(suffix=".pdb")
		os.close(handle)
		collation = open(trajFile, "w")
		zeroPad = len(startFile) == len(endFile)
		for f in range(startFrame, endFrame+1):
			if addMODEL:
				print>>collation, "MODEL %8d" % f
			if zeroPad:
				fname = prefix + "%0*d" % (startSuffixIndex
					- prefixIndex, f-offset) + suffix
			else:
				fname = prefix + "%d" % (f-offset) + suffix
			replyobj.status("Collating file %s\n" % fname,
								blankAfter=0)
			try:
				frameFile = open(fname, "r")
			except IOError:
				collation.close()
				os.unlink(trajFile)
				raise
			collation.write(frameFile.read())
			frameFile.close()
			if addMODEL:
				print>>collation, "ENDMDL"
		collation.close()
			
		replyobj.status("Done collating PDB files\n")
	else:
		trajFile = files[0]
	class PdbTraj:
		def __len__(self):
			return len(self.molecule.coordSets)
	ensemble = PdbTraj()
	ensemble.name = "PDB trajectory from %s" % os.path.basename(files[0])
	ensemble.startFrame = startFrame
	ensemble.endFrame = endFrame
	from chimera import PDBio
	pdbio = PDBio()
	pdbio.explodeNMR = False
	replyobj.status("Reading PDB trajectory\n", blankAfter=0)
	# allow for compression...
	from OpenSave import osOpen
	pdbStream = osOpen(trajFile)
	traj, lineNum = pdbio.readPDBstream(pdbStream, trajFile, 0)
	pdbStream.close()
	replyobj.status("Done reading PDB trajectory\n")
	if style == "multiple files":
		os.unlink(trajFile)
		ensemble.name += "..."
	if not pdbio.ok():
		raise ValueError(pdbio.error())
	elif not traj:
		raise ValueError("No structures in the PDB file!")
	else:
		traj = traj[0]
	if len(traj.coordSets) < 2:
		raise ValueError("The PDB file contains only one structure")
			
	ensemble.molecule = traj
	traj.name = os.path.basename(files[0])
	replyobj.status("Creating interface\n", blankAfter=0)
	try:
		callback(ensemble)
	finally:
		replyobj.status("Interface created\n")
