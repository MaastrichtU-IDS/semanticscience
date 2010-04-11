# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import chimera
from chimera.baseDialog import ModelessDialog, ModalDialog

class StructureDiagramDialog(ModelessDialog):
	name = "Structure Diagram"
	help = "ContributedSoftware/diagram/diagram.html"
	buttons = ("Apply", "Save", "Close")
	default = "Apply"

	def __init__(self, smiles=None, molecule=None,
			width=200, height=200, scale=0.9,
			*args, **kw):
		self.smiles = None
		self.image = None
		self.png = None
		self.width = width
		self.height = height
		self.scale = scale
		self.saveDialog = None
		ModelessDialog.__init__(self, *args, **kw)
		if smiles:
			self.entry.setvalue(smiles)
			self.updateImageFromSmiles(smiles)
		elif molecule:
			self.molMenu.setvalue(molecule)
			self.updateImageFromMolecule(molecule)

	def fillInUI(self, parent):
		import Pmw, Tkinter
		from PIL import Image, ImageTk
		from chimera.extension import TextIcon
		from chimera.widgets import MoleculeOptionMenu
		l = Tkinter.Label(parent)
		fgColor = tuple([ v >> 8 for v in l.winfo_rgb(l["fg"]) ])
		bgColor = tuple([ v >> 8 for v in l.winfo_rgb(l["bg"]) ])
		size = (self.width, self.height)
		self.blank = TextIcon(parent, "Blank", imageSize=size,
					bg=bgColor, fg=fgColor)
		self.fg = Image.new("RGB", size, fgColor)
		self.bg = Image.new("RGB", size, bgColor)
		del l

		self.notebook = Pmw.NoteBook(parent)
		self.notebook.pack(side=Tkinter.TOP, fill=Tkinter.X)
		page = self.notebook.add("SMILES")
		self.notebook.tab("SMILES").focus_set()
		self.entry = Pmw.EntryField(page, labelpos="w",
						label_text="SMILES:")
		self.entry.pack(side=Tkinter.TOP, fill=Tkinter.X)
		page = self.notebook.add("Molecule")
		self.notebook.setnaturalsize()
		self.molMenu = MoleculeOptionMenu(page, labelpos="w",
						label_text="Molecule:")
		self.molMenu.pack(side=Tkinter.TOP, fill=Tkinter.X)

		self.imageLabel = Tkinter.Label(parent, image=self.blank)
		self.imageLabel.pack(expand=True, fill=Tkinter.BOTH)
		self.imageLabel.bind("<Configure>", self._resized)
		self.app = parent
		self.buttonWidgets["Save"].config(state="disabled")

	def _resized(self, event):
		self.width = event.width
		self.height = event.height

	def updateImageFromSmiles(self, smiles):
		import base
		self.updateImage(base.smiles2image, smiles)
		self.smiles = smiles

	def updateImageFromMolecule(self, m):
		import base
		self.updateImage(base.molecule2image, m)

	def updateImage(self, convert, input):
		try:
			png = convert(input, self.width,
					self.height, self.scale)
		except Exception, s:
			self.png = None
			self.imageLabel.config(image=self.blank)
			self.buttonWidgets["Save"].config(state="disabled")
			from chimera import NonChimeraError
			raise NonChimeraError(s)
		else:
			from PIL import Image, ImageTk
			self.png = png
			if 0:
				# This code is suitable for the image
				# from the Guha web service
				img = Image.composite(self.bg, self.fg,
							png.convert("L"))
				self.image = ImageTk.PhotoImage(img)
			if 1:
				# This code is suitable for the image
				# from the Cactus web service
				self.image = ImageTk.PhotoImage(png)
			self.imageLabel.config(image=self.image)
			self.buttonWidgets["Save"].config(state="normal")

	def Apply(self):
		page = self.notebook.getcurselection()
		if page == "SMILES":
			v = self.entry.getvalue()
			if v == self.smiles:
				return
			self.updateImageFromSmiles(v)
		elif page == "Molecule":
			m = self.molMenu.getvalue()
			if m is None:
				return
			count = len(m.atoms)
			if count > 200:
				d = YesNo(title="Structure Diagram",
					text="There are %d atoms in "
						"this model.\n"
						"Are you sure you want "
						"to continue?" % count,
					master=self.app)
				status = d.run(self.app)
				if status == 'no':
					return
			self.updateImageFromMolecule(m)

	def Save(self):
		if self.saveDialog:
			self.saveDialog.enter()
			return
		from OpenSave import SaveModeless
		self.saveDialog = SaveModeless(
					title="Save Structure Diagram PNG",
					filters=[ ("PNG", "*.png", ".png") ],
					command=self._save)

	def _save(self, save, dialog):
		if not save:
			return
		paths = dialog.getPaths()
		if len(paths) != 1:
			return
		self.png.save(paths[0])

class YesNo(ModalDialog):
	buttons = ( "Yes", "No" )

	def __init__(self, title, text, *args, **kw):
		self.text = text
		self.title = title
		ModalDialog.__init__(self, oneshot=1, *args, **kw)

	def fillInUI(self, parent):
		import Tkinter
		l = Tkinter.Label(parent, text=self.text)
		l.pack()

	def Yes(self):
		ModalDialog.Cancel(self, value="yes")

	def No(self):
		ModalDialog.Cancel(self, value="no")

from chimera import dialogs
dialogs.register(StructureDiagramDialog.name, StructureDiagramDialog)
