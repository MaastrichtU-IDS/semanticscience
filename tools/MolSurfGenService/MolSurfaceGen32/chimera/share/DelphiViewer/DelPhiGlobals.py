# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
File:		DelPhiGlobals.py
Date:		06.12.2000
Description:	Contains global classes, variables, and methods that DelPhi*
		modules can use and abuse.

Imports:	- tempfile
		- Tkinter
		- tkFileDialog
		- Pmw
		- chimera
		- chooseModels from ModelBrowser.ModelPicker
		- * from DelPhiHelp

Classes:	- DelPhiOption
		- BooleanOption(DelPhiOption)
		- ScalarOption(DelPhiOption)
		- IntegerScalarOption(DelPhiOption)
		- RealScalarOption(DelPhiOption)
		- MenuOption(DelPhiOption)
		- FileOption(DelPhiOption)
		- InputFileOption(FileOption)
		- ExecFileOption(InputFileOption)
		- OutputFileOption(FileOption)
		- BoundaryConditionOption(MenuOption)
		- EnergyOption
		- MoleculeInputOption(DelPhiOption)

Caveats:	

Last modified:	06.19.2000 - Added.
		07.07.2000 - Organized and such.
		12.12.2006 - Added ExecFileOption.
"""

# general modules
import tempfile
import os

# GUI modules
import Tkinter
import tkFileDialog
import Pmw

# chimera-related modules
import chimera
from chimera import replyobj, help
from ModelBrowser.ModelPicker import chooseModels
from DelPhiHelp import *

class DelPhiOption:

	def __init__(self, name, statement, default, help='<See DelPhi Documentation>'):
		self.name = name
		self.statement = statement
		self.default = default
		self.help = help
		self.label = None
		self.var = None

	def addWidgets(self, parent):
		label = Tkinter.Label(parent, text=self.name)
		label.grid(column=0, padx=5, pady=1, sticky='e')
		self.label = label
		help.register(self.label, balloon=self.help)
		return label.grid_info()['row']

	def getLabel(self, parent):
		return self.label

	def delPhiStatement(self, file):
		if self.var:
			file.write("%s = %s" % (self.statement, self.var.get()))
			file.write("\n")

	def setToDefault(self):
		self.var.set(self.default)

	def checkError(self):
		return None


class BooleanOption(DelPhiOption):

	def __init__(self, name, statement, default=0, help=None):
		DelPhiOption.__init__(self, name, statement, default, help)
		
	def addWidgets(self, parent):
		row = DelPhiOption.addWidgets(self, parent)
		self.var = Tkinter.BooleanVar(parent)
		self.setToDefault()
		cbutton = Tkinter.Checkbutton(parent, highlightthickness=0,
					      onvalue=1, offvalue=0,
					      variable=self.var)
		cbutton.grid(column=1, columnspan=2, row=row, sticky='w')

	def delPhiStatement(self, file):
		if self.var:
			varstring = ['false', 'true'][self.var.get()]
			file.write("%s = %s" % (self.statement, varstring))
			file.write('\n')

class ScalarOption(DelPhiOption):

	def __init__(self, name, statement, dataType, low, high, default, increment, help=None):
		DelPhiOption.__init__(self, name, statement, default, help)
		self.dataType = dataType
		self.low = low
		self.high = high
		self.increment = increment

	def addWidgets(self, parent):
		row = DelPhiOption.addWidgets(self, parent)
		keywords = self.setupCounter(parent)
		self.counter = apply(Pmw.Counter, (parent,), keywords)
		self.counter.grid(column=1, columnspan=2, row=row, sticky='w')

	def setupCounter(self, parent):
		self.var = Tkinter.StringVar(parent)
		self.setToDefault()
		keywords = {}
		keywords['entryfield_entry_textvariable'] = self.var
		keywords['entryfield_validate'] = {
			'validator'	:	self.dataType,
			'minstrict'	:	0,
			'min'		:	str(self.low),
			'max'		:	str(self.high)
		}
		keywords['datatype'] = self.dataType
		keywords['increment'] = self.increment
		keywords['entryfield_entry_highlightthickness'] = 0
		keywords['downarrow_highlightthickness'] = 0
		keywords['uparrow_highlightthickness'] = 0
		return keywords

	def checkError(self):
		if not self.counter.valid():
			return '%s: invalid scalar value\n' % self.name
		return DelPhiOption.checkError(self)

class IntegerScalarOption(ScalarOption):

	def __init__(self, name, statement, low, high, default, increment=1, help=None):
		ScalarOption.__init__(self, name, statement, 'integer', low, high, default, increment, help)
		
class RealScalarOption(ScalarOption):

	def __init__(self, name, statement, low, high, default, increment=0.1, help=None):
		ScalarOption.__init__(self, name, statement, 'real', low, high, default, increment, help)

class MenuOption(DelPhiOption):

	def __init__(self, name, statement, items, default, help=None):
		DelPhiOption.__init__(self, name, statement, default, help)
		self.items = items
	
	def addWidgets(self, parent):
		row = DelPhiOption.addWidgets(self, parent)
		keywords = self.setupMenu(parent)
		menu = apply(Pmw.OptionMenu, (parent,), keywords)
		menu.grid(column=1, columnspan=2, row=row, sticky='w')
		
	def setupMenu(self, parent):
		self.var = Tkinter.StringVar(parent)
		self.setToDefault()
		keywords = {}
		keywords['menubutton_textvariable'] = self.var
		keywords['items'] = self.items
		keywords['menubutton_width'] = max(map(len, self.items))
		keywords['menubutton_highlightthickness'] = 0
		return keywords

class FileOption(DelPhiOption):
	
	def __init__(self, name, statement, default=None, help=None,
			initialdir=None, required=0, compressed=False):
		DelPhiOption.__init__(self, name, statement, default, help)
		self.initialdir = initialdir
		self.required = required
		self.compressed = compressed

	def addWidgets(self, parent):
		row = DelPhiOption.addWidgets(self, parent)
		self.var = Tkinter.StringVar(parent)
		self.var.set(self.default)
		entry = Tkinter.Entry(parent, textvariable=self.var,
				      highlightthickness=0)
		entry.grid(column=1, row=row, sticky='ew')
		browse_cb = lambda s=self : s.browse()
		button = Tkinter.Button(parent, text='Browse...',
					command=browse_cb, highlightthickness=0)
		button.grid(column=2, row=row, padx=5, sticky='e')

class InputFileOption(FileOption):

	def __init__(self, *args, **kw):
		if kw.has_key('filetypes'):
			self.filetypes = kw['filetypes']
			del kw['filetypes']
		else:
			self.filetypes = None
		apply(FileOption.__init__, (self,) + args, kw)

	def browse(self):
		from OpenSave import OpenModeless
		if hasattr(self, '_openDialog'):
			self._openDialog.enter()
			return
		filters = []
		addAll = 0
		if self.filetypes:
			for name, glob in self.filetypes:
				if glob == '*':
					addAll = 1
					continue
				if glob[0] == '.':
					glob = '*' + glob
				filters.append((name, glob))
		if self.default:
			initialfile = self.default
		else:
			initialfile = None
		self._openDialog = OpenModeless(command=self._openCB,
			initialfile=initialfile, title='Select %s' % self.name,
			filters=filters, initialdir=self.startLocation(),
			defaultFilter=0, multiple=0, addAll=addAll,
			historyID="Delphi input %s" % self.name,
			compressed=self.compressed)

	def _openCB(self, okayed, dialog):
		if not okayed:
			return
		for path in dialog.getPaths():
			self.var.set(path)

	def delPhiStatement(self, file, filename=None):
		if filename is None and self.var:
			filename = self.var.get()
		if filename:
			file.write("in(%s, file=\"%s\")\n" % (self.statement,
								filename))

	def startLocation(self):
		if not self.initialdir:
			return None
		if not self.filetypes:
			return self.initialdir
		files = os.listdir('.')
		for file in files:
			ext = os.path.splitext(file)[1]
			for kind, pat in self.filetypes:
				if pat == ext:
					return '.'
		return self.initialdir

	def checkError(self):
		if self.required:
			if not self.var or not self.var.get() \
			or not os.path.isfile(self.var.get()):
				return '%s: invalid file name\n' % self.name
		return FileOption.checkError(self)

class ExecFileOption(InputFileOption):

	def delPhiStatement(self, file):
		return

class OutputFileOption(FileOption):

	def __init__(self, *args, **kw):
		if kw.has_key('defaultextension'):
			self.defaultextension = kw['defaultextension']
			del kw['filetypes']
		else:
			self.defaultextension = None
		apply(FileOption.__init__, (self,) + args, kw)

	def browse(self):
		if hasattr(self, '_saveDialog'):
			self._saveDialog.enter()
			return
		from OpenSave import SaveModeless
		self._saveDialog = SaveModeless(command=self._saveCB,
			historyID='Delphi output %s' % self.name,
			title='Save %s' % self.name, initialfile=self.default,
			filters=[(self.name, '*', self.defaultextension)],
			compressed=self.compressed)

	def _saveCB(self, okayed, dialog):
		if not okayed:
			return
		for path in dialog.getPaths():
			self.var.set(path)

	def delPhiStatement(self, file, filename=None):
		if filename is None and self.var:
			filename = self.var.get()
		if filename:
			file.write("out(%s, file=\"%s\")\n" % (self.statement,
								filename))

	def checkError(self):
		if self.required:
			if not self.var or not self.var.get():
				return '%s: missing file name\n' % self.name
		return FileOption.checkError(self)

# More DelPhi specific options

class BoundaryConditionOption(MenuOption):

	menuoptions = [
		'Zero',
		'Debye-Huckel Dipole',
		'Focussing',
		'Debye-Huckel Total'
	]

	def __init__(self, help=None):
		self.items = self.menuoptions
		MenuOption.__init__(self, 'Boundary Conditions', 'BC', self.items, 'Debye-Huckel Total', help)

	def delPhiStatement(self, file):
		if self.var:
			varstring = self.items.index(self.var.get()) + 1
			file.write("%s = %d" % (self.statement, varstring))
			file.write('\n')

class EnergyOptions(DelPhiOption):
	
	def __init__(self):
		DelPhiOption.__init__(self, 'Energy', 'energy', None, None)
		self.options = [
			BooleanOption('Total Grid', 'G', 0, 
					help=OutputOptionsHelp['G']),
			BooleanOption('Reaction Field', 'S', 0, 
					help=OutputOptionsHelp['S']),
			BooleanOption('Coulombic', 'C', 0,
					help=OutputOptionsHelp['C'])
		]

	def addWidgets(self, parent):
		for option in self.options:
			option.addWidgets(parent)

	def delPhiStatement(self, file):
		for option in self.options:
			if option.var.get():
				break
		else:
			return
		temp = "energy("
		needtostrip = None
		for option in self.options:
			if option.var.get():
				temp = temp + option.statement + ', '
				needtostrip = 1
		# strip the last ', ' and add a ) in its place
		if needtostrip:
			file.write(temp[:-2] + ')')
			file.write('\n')

class MoleculeInputOption(DelPhiOption):

	menuoptions = [
		'Chimera Model',
		'PDB File'
	]

	def __init__(self, name='Molecule Input Data', statement='pdb', default=menuoptions[0], help=None):
		DelPhiOption.__init__(self, name, statement, default, help)
		self.menuOption = MenuOption(None, None, self.menuoptions, self.default, help)
		self.inputFileOption = InputFileOption(None, self.statement, None, None)
		self.needRemove = 0

	def __del__(self):
		if self.needRemove:
			try:
				os.remove(self.var.get())
			except os.error:
				pass

	def addWidgets(self, parent):
		self.parent = parent
		keywords = self.menuOption.setupMenu(parent)
		menu = apply(Pmw.OptionMenu, (parent,), keywords)
		menu.grid(column=0, padx=5, sticky='e')
		row = menu.grid_info()['row']
		self.var  = Tkinter.StringVar(parent)
		self.displayVar  = Tkinter.StringVar(parent)
		self.selectedMolecules = []
		entry = Tkinter.Entry(parent, textvariable=self.displayVar,
					highlightthickness=0)
		entry.grid(column=1, row=row, sticky='ew')
		button = Tkinter.Button(parent, text='Browse...',
					command=self.browse,
					highlightthickness=0)
		button.grid(column=2, row=row, padx=5, sticky='e')
		chimera.openModels.addRemoveHandler(self._moleculeClose, None)
		chimera.openModels.addAddHandler(self._moleculeOpen, None)
		self._checkForSingleModel()

	def _checkForSingleModel(self):
		# Help out the user if there is only one model open
		if self.menuOption.var.get() == self.menuoptions[0]:
			modellist = chimera.openModels.list(
					modelTypes=[chimera.Molecule])
			if len(modellist) == 1:
				self.browse()

	def _moleculeClose(self, trigger, data, mols):
		for m in self.selectedMolecules:
			if m in mols:
				break
		else:
			return
		self._removeTempFile()
		self.var.set("")
		self.displayVar.set("")
		self.selectedMolecule = []
		self._checkForSingleModel()

	def _moleculeOpen(self, trigger, data, mols):
		self._checkForSingleModel()

	def _removeTempFile(self):
		if self.needRemove:
			import os
			try:
				os.remove(self.var.get())
			except os.error:
				pass
			self.var.set("")
			self.needRemove = False

	def _writeTempFile(self, modellist):
		filename = tempfile.mktemp()
		#print 'file name', filename
		PDBio = chimera.PDBio()
		f = open(filename, "w")
		try:
			PDBio.writePDBstream(modellist, f, filename)
		finally:
			f.close()
		#print 'wrote file...'
		self.selectedMolecules = modellist
		self.needRemove = True
		return filename

	def browse(self):
		if self.menuOption.var.get() == self.menuoptions[0]:
			modellist = chimera.openModels.list(
					modelTypes=[chimera.Molecule])
			# if no molecules (and i mean MOLECULES)
			# are open in chimera...
			if not modellist:
				replyobj.error('There are no molecules open')
				return
			if len(modellist) > 1:
				modellist = chooseModels(self.parent,
						modelTypes=[chimera.Molecule])
			if modellist:
				#print 'writing pdb to file...'
				# make a pdb file for the model
				self._removeTempFile()
				self.var.set(self._writeTempFile(modellist))
				self.displayVar.set(modellist[0].name)
				#print 'set file name.'
		else:
			if hasattr(self, '_openDialog'):
				self._openDialog.enter()
				return
			from OpenSave import OpenModeless
			self._openDialog = OpenModeless(command=self._openCB,
				title='Select %s' % self.name, multiple=0,
				historyID="Delphi PDB", compressed=False) 

	def _openCB(self, okayed, dialog):
		if not okayed:
			return
		for path in dialog.getPaths():
			self._removeTempFile()
			self.var.set(path)
			self.displayVar.set(path)

	def delPhiStatement(self, file, filename=None):
		if filename is None and self.var:
			filename = self.var.get()
		if filename:
			file.write('in(%s, file=\"%s\")\n' % (self.statement,
								filename))

	def checkError(self):
		if not self.displayVar or not self.displayVar.get() \
		or (self.menuOption.var.get() == self.menuoptions[1]
		and not os.path.isfile(self.displayVar.get())):
			return '%s: no molecule selected\n' % self.name
		return DelPhiOption.checkError(self)

if __name__ == '__main__':

	optionlist = [
		BooleanOption('TestBool', 'bo'),
		IntegerScalarOption('TestIntScal', 'so', 0, 10, 5, 1),
		RealScalarOption('TestRealScal', 'fo', 0, 1, 0.2),
		BoundaryConditionOption(),
		InputFileOption('Input File', 'ifo', 'in.file'),
		OutputFileOption('Output File', 'ofo', 'out.file'),
		EnergyOptions(),
		MoleculeInputOption()
	]
	
	root = Tkinter.Tk()
	for option in optionlist:
		option.addWidgets(root)
	root.mainloop()
	
	import sys
	for option in optionlist:
		option.delPhiStatement(sys.stdout)
		print
