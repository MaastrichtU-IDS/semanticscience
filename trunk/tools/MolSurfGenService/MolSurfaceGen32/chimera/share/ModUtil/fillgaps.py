# --- UCSF Chimera Copyright ---
# Copyright (c) 2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

import Tkinter as Tk

import chimera
from chimera.baseDialog import ModelessDialog

_singleton = None
def gui():
	global _singleton
	if not  _singleton:
		_singleton = Interface()
	_singleton.enter()

class Interface(ModelessDialog):

	title = "Fill Gaps with Modeller"

	def __init__(self, *args, **kw):
		ModelessDialog.__init__(self, *args, **kw)
		# TODO: initialize instance variables

	def fillInUI(self, parent):
		from chimera.widgets import MoleculeOptionMenu
		from chimera.tkoptions import IntOption, BooleanOption, \
				InputFileOption, StringOption
		import itertools
		info = Tk.Label(parent, justify=Tk.LEFT, wraplength=300, text=
				"Select a molecule with gaps")
		info.pack(ipadx=2, ipady=2)
		options = Tk.Frame(parent)
		options.columnconfigure(0, pad=2)
		options.columnconfigure(1, pad=2)
		row = itertools.count()
		molRow = row.next()
		text = Tk.Label(options,
				text="Restrict selections to molecule:")
		text.grid(row=molRow, column=0)
		self.molecules = MoleculeOptionMenu(options,
				command=self.updateMolecule)
		self.molecules.grid(row=molRow, column=1, sticky=Tk.W)
		self.turnsOnly = BooleanOption(options, row.next(),
				"Skip gaps at ends of chains", False, None)
		self.hetatms = BooleanOption(options, row.next(),
				"Include HETATM residues", False, None)
		#self.waters = BooleanOption(options, row.next(),
		#		"Include waters", False, None)
		self.nucleic = BooleanOption(options, row.next(),
				"Include nucleic acids", False, None)
		self.nucleic.disable()
		hr = Tk.Frame(options, relief=Tk.GROOVE, borderwidth=1, height=2)
		hr.grid(row=row.next(), columnspan=2, sticky='ew')
		# modeller location
		self.modeller = InputFileOption(options, row.next(),
				"Modeller location", "mod8v2", None)
		# temporary prefix -- TODO: add unique id
		#self.tempdir = StringOption(options, row.next(),
		#		"Temporary file prefix", "modtmp", None)
		options.pack()

	def updateMolecule(self, *args, **kw):
		print 'updateMolecule', args, kw
		# TODO: look for gaps

	def Apply(self):
		from chimera import selection
		molecule = [self.molecules.getvalue()]
		# TODO: use fillin
		#  write out Modeller input file
		#  run Modeller -- warn that this will take a long time
		#    (could monitor directory for output files)
