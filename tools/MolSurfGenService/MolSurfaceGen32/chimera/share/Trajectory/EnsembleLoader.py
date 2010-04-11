# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: EnsembleLoader.py 26655 2009-01-07 22:02:30Z gregc $

import Pmw
import Tkinter
from chimera.baseDialog import ModelessDialog
from chimera import replyobj
from prefs import prefs, FORMAT

class EnsembleLoader(ModelessDialog):
	title = "Get Ensemble Info"
	buttons = ['OK', 'Cancel']
	help = "ContributedSoftware/movie/movie.html#movieinput"

	def __init__(self, callback, movieFile=None):
		self.callback = callback
		self.movieFile = movieFile
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		from formats import formats
		if not formats:
			replyobj.error("No trajectory formats?!?\n")
			self.destroy()
			return

		if self.movieFile:
			initFormat = "metafile"
		elif prefs[FORMAT] in formats:
			initFormat = prefs[FORMAT]
		else:
			initFormat = formats[0]
		self.formatMenu = Pmw.OptionMenu(parent, initialitem=initFormat,
			command=self.showFormat, items=formats, labelpos='w',
			label_text="Trajectory format:")
		self.formatMenu.grid(row=0, column=0, sticky='w')

		self.frames = {}
		self.paramGUIs = {}
		for format in formats:
			exec "from formats.%s import ParamGUI" \
						% format2importable(format)
			self.frames[format] = Tkinter.Frame(parent)
			self.paramGUIs[format] = ParamGUI(self.frames[format])
		parent.columnconfigure(0, weight=1)
		parent.rowconfigure(1, weight=1)
		if self.movieFile:
			self.paramGUIs[initFormat].setpath(self.movieFile)

		self.curFormat = None
		self.showFormat(initFormat)

		rangeFrame = Tkinter.Frame(parent)
		rangeFrame.grid(row=2, column=0)
		self.startRangeEntry = Pmw.EntryField(rangeFrame, labelpos='w',
			label_text='Use frames', value='first', entry_width=5)
		self.startRangeEntry.grid(row=0, column=0, sticky='e')
		self.endRangeEntry = Pmw.EntryField(rangeFrame, labelpos='w',
			label_text='through', value='last', entry_width=5)
		self.endRangeEntry.grid(row=0, column=1, sticky='w')

	def showFormat(self, format):
		if self.curFormat:
			self.frames[self.curFormat].grid_forget()
		self.frames[format].grid(row=1, column=0, sticky='nsew')
		self.curFormat = format

	def Apply(self):
		prefs[FORMAT] = self.curFormat
		try:
			start = int(self.startRangeEntry.getvalue())
		except ValueError:
			start = None
		endval = self.endRangeEntry.getvalue().lower()
		try:
			end = int(endval)
		except ValueError:
			if endval == "pipe":
				end = endval
			else:
				end = None
		try:
			self.paramGUIs[self.curFormat].loadEnsemble(start, end,
								self.callback)
			self.destroy()
		except ValueError, msg:
			# bad input field
			self.enter()
			replyobj.error(str(msg) + '\n')

def loadEnsemble(callback, movieFile=None, start=None, end=None):
	if movieFile is None:
		EnsembleLoader(callback)
		return

	mf = open(movieFile, "rU")
	lines = map(lambda l: l[:-1], mf.readlines())
	mf.close()
	format = lines[0]
	inputs = lines[1:]
	import os.path
	mfDir, fname = os.path.split(movieFile)
	if start is None:
		try:
			format, start, end = format.split()
		except ValueError:
			pass
		else:
			if start != "?":
				start = int(start)
			end = end.lower()
			if end not in ("?", "pipe"):
				end = int(end)
	else:
		format = format.split()[0]
	if start == "?" or end == "?":
		EnsembleLoader(callback, movieFile=movieFile)
		return
			
	exec "from formats.%s import loadEnsemble" % format2importable(format)
	loadEnsemble(inputs, start, end, callback, relativeTo=mfDir)
		
def format2importable(x):
	return "".join(filter(lambda x: x.isalnum(), x)).capitalize()
