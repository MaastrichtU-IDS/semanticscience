# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: SaveHeaderDialog.py 27660 2009-05-27 00:25:39Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
from OpenSave import SaveModeless
from chimera import replyobj
import Pmw, Tkinter
import os.path

class SaveHeaderDialog(SaveModeless):
	"""Dialog to allow the user to header lines"""

	def __init__(self, mav):
		self.mav = mav
		self.title = "Save Header of %s" % mav.title
		defaultFile = os.path.splitext(self.mav.title or "alignment")[0]
		SaveModeless.__init__(self, initialfile=defaultFile+".hdr",
							clientPos='s')

	def fillInUI(self, parent):
		SaveModeless.fillInUI(self, parent)
		from chimera.tkoptions import SymbolicEnumOption
		self.headerChoice = SymbolicEnumOption(self.clientArea,
							0, "Save", None, None)
		self.omitNoValueVar = Tkinter.IntVar(self.clientArea)
		self.omitNoValueVar.set(True)
		frame = Tkinter.Frame(self.clientArea)
		frame.grid(row=1, column=0, columnspan=2)
		ckb = Tkinter.Checkbutton(frame, variable=self.omitNoValueVar,
						text="Omit no-value positions")
		ckb.grid()
		chimera.help.register(ckb, balloon=
				"If on, conservations positions without\n"
				"values will not have lines in the output file")
		self._populateMenu()
		from MAViewer import SHOW_HEADERS, HIDE_HEADERS
		for trig in [SHOW_HEADERS, HIDE_HEADERS]:
			self.mav.triggers.addHandler(trig,
						self._populateMenu, None)
	def destroy(self):
		self.mav = None
		ModelessDialog.destroy(self)

	def Apply(self):
		if not self.getPaths():
			replyobj.error("No header save file specified.\n")
			self.enter()
			return
		self.mav.saveHeader(self.getPaths()[0], self.headerChoice.get(),
					omitNoValue=self.omitNoValueVar.get())

	def _populateMenu(self, *args):
		shown = [hd for hd in self.mav.seqCanvas.headerDisplayOrder()
			if len(self.mav.seqs) > 1 or hd.singleSequenceRelevant]
		default = None
		if shown:
			if self.headerChoice.values:
				default = self.headerChoice.get()
				if not default:
					default = self.headerChoice.values[0]
			elif self.mav.seqCanvas.conservation in shown:
				default = self.mav.seqCanvas.conservation
		self.headerChoice.labels = [s.name for s in shown]
		self.headerChoice.values = shown
		self.headerChoice.remakeMenu()
		if default is not None:
			self.headerChoice.set(default)
