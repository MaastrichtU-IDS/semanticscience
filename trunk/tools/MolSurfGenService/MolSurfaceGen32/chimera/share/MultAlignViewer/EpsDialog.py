# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: EpsDialog.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog
from OpenSave import SaveModeless
from chimera import replyobj
import Pmw, Tkinter
import os.path
from MAViewer import DISPLAY_TREE

class EpsDialog(SaveModeless):
	"""Dialog to allow the user to save alignment as EPS"""

	def __init__(self, mav):
		self.mav = mav
		self.title = "Save EPS of %s" % mav.title
		defaultFile = os.path.splitext(self.mav.title or "alignment")[0]
		SaveModeless.__init__(self, clientPos='s',
					initialfile=defaultFile,
					filters=[("EPS", "*.eps", ".eps")])

	def fillInUI(self, parent):
		SaveModeless.fillInUI(self, parent)
		from chimera.tkoptions import SymbolicEnumOption, BooleanOption
		class ColorModeOption(SymbolicEnumOption):
			values = ["color", "gray", "mono"]
			labels = ["color", "grayscale", "black & white"]
		self.colorMode = ColorModeOption(self.clientArea, 0,
						"color mode", "color", None,
						balloon="output color range")
		self.orientation = BooleanOption(self.clientArea, 1,
			"rotate 90", False, None,
			balloon="If true, output will be rotated 90 degrees\n"
				"(i.e. landscape mode)")
		class ExtentOption(SymbolicEnumOption):
			values = ["visible", "all"]
			labels = ["visible region", "entire alignment"]
		self.extent = ExtentOption(self.clientArea, 2,
			"extent", "visible", None, balloon=
			"save the entire alignment or just the visible part")
		self.hideNodes = BooleanOption(self.clientArea, 3,
			"hide tree control nodes", True, None,
			balloon="Hide square boxes used as controls for tree")
		if not self.mav.seqCanvas.treeShown:
			self.hideNodes.forget()
		self._nodesHandler = self.mav.triggers.addHandler(DISPLAY_TREE,
						self._treeDispCB, None)

	def destroy(self):
		self.mav.triggers.deleteHandler(DISPLAY_TREE,
							self._nodesHandler)
		self.mav = None
		ModelessDialog.destroy(self)

	def Apply(self):
		if not self.getPaths():
			replyobj.error("No EPS save file specified.\n")
			self.enter()
			return
		self.mav.saveEPS(self.getPaths()[0],
					colorMode=self.colorMode.get(),
					rotate=self.orientation.get(),
					extent=self.extent.get(),
					hideNodes=self.hideNodes.get())

	def _treeDispCB(self, trigName, myData, tree):
		if tree:
			self.hideNodes.manage()
		else:
			self.hideNodes.forget()
