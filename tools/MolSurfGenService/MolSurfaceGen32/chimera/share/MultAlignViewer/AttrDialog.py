# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: AttrDialog.py 27541 2009-05-11 20:30:48Z pett $

import chimera
from chimera.baseDialog import ModelessDialog
import Pmw, Tkinter

class AlignmentAttrDialog(ModelessDialog):
	title = "Alignment Annotations"
	provideStatus = True
	statusPosition = "left"
	buttons = ('New', 'Delete', 'Close')
	help = "ContributedSoftware/multalignviewer/multalignviewer.html#anno-ali"

	def __init__(self, fileAttrs, mavStatus):
		self.fileAttrs = fileAttrs
		self.mavStatus = mavStatus
		self.reminder = "Annotations only saved in Stockholm format\n"\
			"Comments saved in RSF and Stockholm formats\n"
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		parent.columnconfigure(0, weight=1)
		parent.rowconfigure(0, weight=1)
		parent.rowconfigure(1, weight=2)
		self.attrFrame = Pmw.ScrolledFrame(parent, horizflex='expand',
							hscrollmode='none')
		self.attrFrame.grid(row=0, column=0, sticky='nsew')
		interior = self.attrFrame.interior()
		interior.columnconfigure(1, weight=1)

		attrNames = self.fileAttrs.keys()
		attrNames.sort(lambda a, b: cmp(a.lower(), b.lower()))
		self.attrWidgets = {}
		for name in attrNames:
			if name == "comments":
				continue
			self._addAttrWidgets(name)

		self.comments = Pmw.ScrolledText(parent, labelpos='nw',
			label_text="Comments", text_width=80, text_height=15)
		self.comments.grid(row=1, column=0, sticky='nsew')
		if "comments" in self.fileAttrs:
			self.comments.setvalue(self.fileAttrs["comments"])
		text = self.comments.component('text')
		text.bind('<KeyRelease>', lambda e, gv=self.comments.getvalue:
				self._attrModCB("comments", gv()), add=True)
		self.newDialog = self.deleteDialog = None
		self.status(self.reminder)
			
	def _addAttrWidgets(self, name, val=None):
		interior = self.attrFrame.interior()
		cols, rows = interior.grid_size()
		label = self._createAttrLabel(name)
		label.grid(row=rows, column=0, sticky='e')

		text = self._createAttrText(name, val)
		text.grid(row=rows, column=1, sticky='nsew')
		self.attrWidgets[name] = (label, text)

	def Close(self):
		self.mavStatus(self.reminder)
		ModelessDialog.Close(self)

	def Delete(self):
		if not self.deleteDialog:
			if self.newDialog:
				self.newDialog.Cancel()
			class DeleteAnnotationDialog(ModelessDialog):
				title = "Delete Annotation"
				buttons = ('OK', 'Cancel')
				help = "ContributedSoftware/multalignviewer/multalignviewer.html#anno-ali"

				def __init__(self, noteDialog):
					self.noteDialog = noteDialog
					ModelessDialog.__init__(self)

				def fillInUI(self, parent):
					self.menu = Pmw.OptionMenu(parent,
						labelpos='w', label_text=
						"Annotation to delete:")
					self.menu.grid()

				def Apply(self):
					name = self.menu.getvalue()
					if name in self.noteDialog.fileAttrs:
						del self.noteDialog.fileAttrs[	
									name]
					for widget in self.noteDialog.\
							attrWidgets[name]:
						widget.grid_forget()
					del self.noteDialog.attrWidgets[name]

				def delete(self):
					self.noteDialog = None
					ModelessDialog.delete(self)

				def map(self, event=None):
					names = self.noteDialog.attrWidgets\
									.keys()
					names.sort(lambda a, b: cmp(a.lower(),
								b.lower()))
					self.menu.setitems(names)
			self.deleteDialog = DeleteAnnotationDialog(self)
		self.deleteDialog.enter()

	def destroy(self):
		self.mavStatus = self.fileAttrs = None
		for dialog in [self.newDialog, self.deleteDialog]:
			if dialog:
				dialog.destroy()
		ModelessDialog.destroy(self)

	def New(self):
		if self.deleteDialog:
			self.deleteDialog.Cancel()
		if not self.newDialog:
			class NewAnnotationDialog(ModelessDialog):
				title = "New Annotation"
				buttons = ('OK', 'Cancel')
				default = 'OK'
				help = "ContributedSoftware/multalignviewer/multalignviewer.html#anno-ali"

				def __init__(self, noteDialog):
					self.noteDialog = noteDialog
					ModelessDialog.__init__(self)

				def fillInUI(self, parent):
					from chimera.tkoptions \
							import StringOption
					self.noteOption = StringOption(parent,
						0, "New annotation name", "",
						None)

				def Apply(self):
					name = self.noteOption.get().strip()
					if not name:
						self.enter()
						from chimera import UserError
						raise UserError("No annotation"
							" name specified")
					self.noteDialog._addAttrWidgets(name,"")
					self.uiMaster().update_idletasks()
					top, bottom = self.noteDialog.attrFrame\
									.yview()
					if bottom < 1.0:
						newTop = top + 1.0 - bottom
						self.noteDialog.attrFrame.yview(
								mode='moveto',
								value=newTop)
					self.noteDialog.attrWidgets[name][1]\
									.focus()
				def destroy(self):
					self.noteDialog = None
					ModelessDialog.destroy(self)
			self.newDialog = NewAnnotationDialog(self)

		self.newDialog.enter()

	def _attrModCB(self, name, val):
		val = val.strip()
		if not val:
			if name in self.fileAttrs:
				del self.fileAttrs[name]
		else:
			self.fileAttrs[name] = val

	def _createAttrLabel(self, name):
		return Tkinter.Label(self.attrFrame.interior(),
						text=name, wraplength='40c')

	def _createAttrText(self, name, value):
		if value is None:
			value = self.fileAttrs[name]
		text = Tkinter.Text(self.attrFrame.interior(),
				height=value.count('\n')+1, wrap='word',
				width=min(80, max(map(len, value.split('\n')))))
		text.insert('end', value)
		text.bind('<KeyRelease>', lambda e, n=name, t=text:
			self._attrModCB(n, t.get("0.0", 'end')), add=True)
		return text
