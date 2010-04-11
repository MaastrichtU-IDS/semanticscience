# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: output.py 27369 2009-04-22 22:56:49Z pett $

import os
import formatters
from chimera import replyobj
from OpenSave import SaveModeless, SaveModal

saverFunc = {}
extensions = {}
fileGlobs = {}
for saverFile in os.listdir(formatters.__file__[:-12]):
	if saverFile[:4] != "save" \
	or saverFile[-3:] != ".py":
		continue
	saverType = saverFile[4:-3]
	try:
		exec \
		"from formatters.%s import extension, globs, save, fileType" \
						% saverFile[:-3]
	except ImportError:
		replyobj.error("Formatter for %s multi-sequence file "
			"does not contain default file-name extension, "
			"list of acceptable file name patterns, "
			"file type description, and/or save() "
			" function\n" % saverType)
		continue
	except:
		replyobj.reportException("Error in %s formatter" % saverType)
		continue
	saverFunc[fileType] = save
	extensions[fileType] = extension
	fileGlobs[fileType] = globs

if not saverFunc:
	raise ImportError, "No working multi-sequence file formatters found."

def saveFile(mav, modal=False):
	filters = []
	for fileType in saverFunc.keys():
		filters.append([fileType, fileGlobs[fileType],
							extensions[fileType]])
	filters.sort()

	kw = {
		'title': "Save %s" % mav.title,
		'dialogKw': {'oneshot': True},
		'clientPos': 's',
		'filters': filters,
		'historyID': "MAV file save"
	}
	if modal:
		d = _SaveModalDialog(mav, **kw)
	else:
		kw['command'] = _saveCB
		d = _SaveModelessDialog(mav, **kw)
	if modal:
		pathInfo = d.run(mav.uiMaster().winfo_toplevel())
		if pathInfo != None:
			_saveCB(True, d, pathInfo=pathInfo)

def _omitGapColumns(seqs, markups):
	nonGaps = []
	for pos in range(len(seqs[0])):
		allGap = True
		for seq in seqs:
			if seq[pos].isalnum():
				allGap = False
				break
		if not allGap:
			nonGaps.append(pos)
	if len(nonGaps) < len(seqs[0]):
		return filterColumns(seqs, nonGaps, seqs, markups)
	return seqs, markups

def _appendNumberings(inSeqs, doCopy):
	from copy import copy
	outSeqs = []
	for inSeq in inSeqs:
		if doCopy:
			outSeq = copy(inSeq)
		else:
			outSeq = inSeq
		outSeq.name = inSeq.name + "/%d-%d" % (inSeq.numberingStart,
			inSeq.numberingStart + len(inSeq.ungapped()) - 1)
		outSeqs.append(outSeq)
		if hasattr(inSeq, 'matchMaps'):
			outSeq.matchMaps = inSeq.matchMaps
	return outSeqs

def _saveCB(okay, dialog, pathInfo=None):
	mav = dialog.mav

	if not okay:
		return

	if dialog.saveRegion.get():
		try:
			saveSeqs, saveFileMarkups = _verifySaveRegion(mav)
		except:
			dialog.enter()
			raise
	else:
		saveSeqs = mav.seqs
		saveFileMarkups = mav.fileMarkups
	if dialog.omitGaps.get():
		saveSeqs, saveFileMarkups = _omitGapColumns(saveSeqs,
							saveFileMarkups)
	if dialog.appendNumberings.get():
		saveSeqs = _appendNumberings(saveSeqs,
						doCopy=(saveSeqs == mav.seqs))
	if pathInfo is None:
		pathInfo = dialog.getPathsAndTypes()
	if not pathInfo:
		dialog.enter()
		raise ValueError, "No filename specified"
	from OpenSave import osOpen
	for path, fileType in pathInfo:
		f = osOpen(path, "w")
		saverFunc[fileType](f, mav, saveSeqs, saveFileMarkups)
		f.close()
		mav.status("Saved %s\n" % path)
	mav._edited = False
	
def _verifySaveRegion(mav):
	region = mav.currentRegion()
	if region is None:
		raise ValueError, "No active region"
	checkList = {}
	for s1, s2, p1, p2 in region.blocks:
		prange = range(p1, p2+1)
		try:
			i1 = mav.seqs.index(s1)
		except ValueError:
			# in header sequences
			i1 = 0
		try:
			i2 = mav.seqs.index(s2)
		except ValueError:
			# in header sequences
			continue
		for si in range(i1, i2+1):
			seq = mav.seqs[si]
			if seq not in checkList:
				checks = {}
				checkList[seq] = checks
			else:
				checks = checkList[seq]
			for p in prange:
				checks[p] = True
	if not checkList:
		raise ValueError, "No alignment sequences in active region"
	standard = checkList[seq].keys()
	standard.sort()
	for checks in checkList.values():
		compare = checks.keys()
		compare.sort()
		if compare != standard:
			raise ValueError, "All sequences in active region must comprise same columns"
	return filterColumns(checkList, standard, mav.seqs, mav.fileMarkups)

def filterColumns(keepSeqs, keepCols, seqs, fileMarkups):
	from copy import copy
	saveSeqs = []
	for seq in seqs:
		if seq not in keepSeqs:
			continue
		saveSeq = copy(seq)
		saveSeq[:] = [seq[i] for i in keepCols]
		saveSeqs.append(saveSeq)
		for k, v in saveSeq.markups.items():
			saveSeq.markups[k] = "".join([v[i] for i in keepCols])
		if hasattr(seq, 'matchMaps') \
		and len(saveSeq.ungapped()) == len(seq.ungapped()):
			saveSeq.matchMaps = seq.matchMaps
	saveFileMarkups = {}
	for k, v in fileMarkups.items():
		saveFileMarkups[k] = "".join([v[i] for i in keepCols])
	return saveSeqs, saveFileMarkups

class _SaveDialog:
	def __init__(self, mav, **kw):
		self.mav = mav
		if isinstance(self, SaveModeless):
			SaveModeless.__init__(self, **kw)
		else:
			SaveModal.__init__(self, **kw)

	def map(self, *args, **kw):
		self.appendNumberings.set(self.mav.leftNumberingVar.get()
					or self.mav.rightNumberingVar.get())
	def fillInUI(self, *args):
		if isinstance(self, SaveModeless):
			SaveModeless.fillInUI(self, *args)
		else:
			SaveModal.fillInUI(self, *args)
		import Tkinter
		self.saveRegion = Tkinter.IntVar(self.clientArea)
		self.saveRegion.set(False)
		Tkinter.Checkbutton(self.clientArea, variable=self.saveRegion,
			text="Restrict save to active region").grid(row=0,
			sticky='w')
		self.omitGaps = Tkinter.IntVar(self.clientArea)
		self.omitGaps.set(True)
		Tkinter.Checkbutton(self.clientArea, variable=self.omitGaps,
			text="Omit all-gap columns").grid(row=1, sticky='w')
		self.appendNumberings = Tkinter.IntVar(self.clientArea)
		Tkinter.Checkbutton(self.clientArea,
			variable=self.appendNumberings, text="Append sequence"
			" numberings to sequence names").grid(row=2, sticky='w')

class _SaveModalDialog(_SaveDialog, SaveModal):
	pass
class _SaveModelessDialog(_SaveDialog, SaveModeless):
	pass
