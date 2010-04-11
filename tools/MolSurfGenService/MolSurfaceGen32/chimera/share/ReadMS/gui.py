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

import Tkinter
from chimera.widgets import MoleculeScrolledListBox
from chimera.tkoptions import RGBAOption
from prefs import prefs, COLOR

class AttrFrame(Tkinter.Frame):
	def __init__(self, master, **kw):
		Tkinter.Frame.__init__(self, master, **kw)
		
		self.rgbaOpt = RGBAOption(self, 1, 'Color', prefs[COLOR],
						None, noneOkay=False)
		self.associateVar = Tkinter.IntVar(self)
		self.associateVar.set(0)
		Tkinter.Checkbutton(self, command=self.modelsActivity,
			text="Associate with...", variable=self.associateVar
			).grid(row=2, column=0, sticky='e')

		self.moleculeList = MoleculeScrolledListBox(self,
				autoselect='single', listbox_state='disabled')
		self.moleculeList.grid(row=2, column=1, sticky='w')

	def modelsActivity(self):
		if self.associateVar.get():
			self.moleculeList.component('listbox').config(
							state='normal')
		else:
			self.moleculeList.component('listbox').config(
							state='disabled')


from genVRML import generateVRML
class ApplyAttrBase:
	help = "UsersGuide/dms.html"
	def Apply(self, okayed=True):
		if not okayed:
			return
		rgba = self.attrFrame.rgbaOpt.get()
		prefs[COLOR] = rgba
		sameAs = None
		if self.attrFrame.associateVar.get():
			sameAs = self.attrFrame.moleculeList.getvalue()
		generateVRML(self.fileName(), rgb=rgba[:3], sameAs=sameAs)

from chimera.baseDialog import ModelessDialog
class PostChimeraOpenDialog(ApplyAttrBase, ModelessDialog):
	buttons = ('Open', 'Cancel')
	default = 'Open'
	oneshot = True
	def __init__(self, fileName):
		self._fileName = fileName
		self.title = "Open %s" % fileName
		self.Open = self.OK
		ModelessDialog.__init__(self)

	def fileName(self):
		return self._fileName

	def fillInUI(self, parent):
		self.attrFrame = AttrFrame(parent)
		self.attrFrame.grid()
		
from OpenSave import OpenModeless
class ReadMsDialog(ApplyAttrBase, OpenModeless):
	oneshot = True
	def __init__(self):
		from fileInfo import fileType, suffixes
		OpenModeless.__init__(self, clientPos='s',
			defaultFilter=fileType,
			filters=[(fileType, ['*'+suf for suf in suffixes])])

	def fileName(self):
		paths = self.getPaths()
		if not paths:
			from chimera import replyobj
			replyobj.error("No file selected\n")
			return
		return paths[0]

	def fillInUI(self, parent):
		OpenModeless.fillInUI(self, parent)
		self.attrFrame = AttrFrame(self.clientArea)
		self.attrFrame.grid()
