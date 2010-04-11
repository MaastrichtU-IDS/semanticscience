# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from OpenSave import OpenModeless
from chimera.tkoptions import ColorOption
from chimera import replyobj
from chimera.tkoptions import FileOption, StringOption, BooleanOption, \
				IntOption, LineWidthOption
import Tkinter
import Tix
from base import readPBinfo
import Pmw

ui = None

def showUI():
	global ui

	if not ui:
		ui = PBreaderDialog()
	ui.enter()

from chimera import preferences

options = { "line width": 1.0 }
prefs = preferences.addCategory("pseudobond reader", preferences.HiddenCategory,
							optDict=options)

class PBreaderDialog(OpenModeless):
	title = "Pseudobond Reader"
	help = "ContributedSoftware/pbreader/pbreader.html"

	def __init__(self):
		OpenModeless.__init__(self, title="Pseudobond File to Read",
				historyID="PBReader open", clientPos='s')

	def fillInUI(self, parent):
		OpenModeless.fillInUI(self, parent)

		group = Pmw.Group(self.clientArea, tag_text='Further info')
		group.grid(row=0, column=0, sticky='nsew')
		self.catName = StringOption(group.interior(), 0,
			"group name", None, None)
		class PBLineWidthOption(LineWidthOption):
			default = prefs["line width"]
			balloon = "Width of pseudobonds (in pixels)"
		self.lineWidth = PBLineWidthOption(group.interior(), 1, None,
								None, None)
		self.clearCat = BooleanOption(group.interior(), 2,
			"clear group of previous pseudobonds", 1, None)
		self.leftModel = IntOption(group.interior(), 3,
			"first column specifiers default to model", 0, None)
		self.rightModel = IntOption(group.interior(), 4,
			"second column specifiers default to model", 0, None)

	def Apply(self):
		if not self.getPaths():
			replyobj.error("No pseudobond file chosen\n")
		lineWidth = self.lineWidth.get()
		prefs["line width"] = lineWidth
		for path in self.getPaths():
			readPBinfo(path, category=self.catName.get(),
				clearCategory=self.clearCat.get(),
				lineWidth=lineWidth, drawMode=None,
				leftModel=str(self.leftModel.get()),
				rightModel=str(self.rightModel.get()),
				defColor=None)
