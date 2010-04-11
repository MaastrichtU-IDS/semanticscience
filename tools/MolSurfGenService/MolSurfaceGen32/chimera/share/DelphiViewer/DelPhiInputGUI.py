# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

""" 
File:		DelPhiInputGUI.py 
Date: 		 06.13.2000 
Description:	Allows user to interactively select DelPhi input files,
		parameters and output files via a GUI.

Imports:	- Tkinter module
		- Pmw module
		- All classes from DelPhiGlobals module
			- BooleanOption
			- IntScalarOption
			- RealScalarOption
			- MenuOption
			- BoundaryConditionOption
			- InputFileOption
			- OutputFileOption
			- MoleculeInputOption
			- EnergyOption
		- Dictionaries from DelPhiHelpDicts
			- InputOptionsHelp
			- ParameterOptionsHelp
			- OutputOptionsHelp

Classes:	

Last modified:  06.13.2000 - Addition of option lists for GUI. 
                12.12.2006 - Addition of DelPhi location selector and prefs.
                12.14.2006 - Addition of saving parameter values in
		             hidden preferences category.
"""

# GUI modules
import Tkinter
import Pmw

# delphi/chimera-related modules
from chimera import replyobj
from DelPhiGlobals import *
from DelPhiHelp import *

# preferences
from chimera import preferences
SURF_RGBA_POS = "surf rgba pos"
SURF_RGBA_MID = "surf rgba mid"
SURF_RGBA_NEG = "surf rgba neg"
prefOptions = {
	"executable": "",
	"radii": "",
	"charges": "",
}
prefs = preferences.addCategory("DelphiController",
			preferences.HiddenCategory, optDict=prefOptions)
Executable = prefs["executable"]
if not Executable:
	import os, os.path
	execNames = [ "delphi", "delphi.exe" ]
	path = os.getenv("PATH", os.defpath)
	pathList = path.split(os.pathsep)
	for p in pathList:
		for e in execNames:
			filename = os.path.join(p, e)
			if os.access(filename, os.X_OK):
				Executable = filename
				break
		if Executable:
			break
	import sys
	if not Executable and sys.platform == "win32":
		drive = os.path.splitdrive(sys.executable)[0]
		filename = os.path.join(drive, os.sep, "Program Files",
					"Delphi", "delphi.exe")
		if os.access(filename, os.X_OK):
			Executable = filename
if not Executable:
	Executable = "/usr/local/bin/delphi"
	from chimera import replyobj
	replyobj.warning("Cannot find Delphi executable.  "
			"Please set manually.")


# Option lists for displaying GUI

MoleculeInputOptions = [
	MoleculeInputOption(help=InputOptionsHelp['pdb'])
]

DelPhiInputOptions = [
	# These three are used for saving preferences, so
	# don't change their order unless you change savePrefs()
	ExecFileOption('DelPhi Executable', 'exe', Executable,
			required=1,
			filetypes=[('All Files', '*')],
			help=InputOptionsHelp['exe']),
	InputFileOption('Atomic Radii File', 'siz', prefs["radii"],
			required=1,
			filetypes=[('Radii', '.siz'),
					('All Files', '*')],
			help=InputOptionsHelp['siz']),
	InputFileOption('Atomic Charge File', 'crg', prefs["charges"], 
			required=1,
			filetypes=[('Charge', '.crg'),
					('All Files', '*')],
			help=InputOptionsHelp['crg']),
	InputFileOption('Potential File (for focussing)', 'phi', '',
			filetypes=[('Potential File', '.phi'),
					('All Files', '*')],
			help=None),
	InputFileOption('PDB Input for Site Potentials', 'frc', '',
			filetypes=[('PDB', '.pdb'),
					('PDB', '.ent'),
					('All Files', '*')],
			help=None)
]

DelPhiGroupedInputOptions = [
	# These two are used for saving preferences, so
	# don't change their order unless you change savePrefs()
	('Molecule', MoleculeInputOptions),
	('Other', DelPhiInputOptions) 
]

DelPhiBasicParameterOptions = [
	BooleanOption('Automatic Convergence', 'AC', 1,
			help=ParameterOptionsHelp['AC']),
	BooleanOption('Calculate GRASP Surface', 'CS', 0,
			help=ParameterOptionsHelp['CS']),
#	BooleanOption('Poisson-Boltzmann Solver', 'SP', 1,
#			help=ParameterOptionsHelp['SP']),
	IntegerScalarOption('Box Fill (%)', 'PF', 0, 100, 60,
			help=ParameterOptionsHelp['PF']),
	RealScalarOption('Grid Scale', 'SC', 0.1, 5.0, 1.2,
			help=ParameterOptionsHelp['SC']),
	RealScalarOption('Probe Radius', 'PR', 0.0, 5.0, 1.4,
			help=ParameterOptionsHelp['PR'])
]

DelPhiAdvancedParameterOptions = [
	BooleanOption('Fancy Charge Distribution', 'FC', 0,
			help=ParameterOptionsHelp['FC']),
	BooleanOption('Log File Convergence', 'LG', 0,
			help=ParameterOptionsHelp['LG']),
	BooleanOption('Log File Potentials', 'LP', 0,
			help=ParameterOptionsHelp['LP']),
#	BooleanOption('Membrane Data', 'MD', 0,
#			help=ParameterOptionsHelp['MD']),
	BooleanOption('Periodic Boundary (X)', 'PX', 0,
			help=ParameterOptionsHelp['PX']),
	BooleanOption('Periodic Boundary (Y)', 'PY', 0, 
			help=ParameterOptionsHelp['PY']),
	BooleanOption('Periodic Boundary (Z)', 'PZ', 0, 
			help=ParameterOptionsHelp['PZ']),
	BoundaryConditionOption(help=ParameterOptionsHelp['BC']),
	IntegerScalarOption('Interior Dielectric Constant', 'ID', 1, 10, 2,
			help=ParameterOptionsHelp['ID']),
	IntegerScalarOption('Exterior Dielectric Constant', 'ED', 1, 200, 80,
			help=ParameterOptionsHelp['ED']),
	RealScalarOption('Grid Convergence', 'GC', 0.0, 1.0, 0.0,
			help=ParameterOptionsHelp['GC']),
	RealScalarOption('Ionic Strength', 'IS', 0.0, 10.0, 0.0,
			help=ParameterOptionsHelp['IS']),
	RealScalarOption('Ion Radius', 'IR', 0.0, 10.0, 0.0,
			help=ParameterOptionsHelp['IR']),
	IntegerScalarOption('Non-Linear Iterations', 'NI', 0, 10, 0,
			help=ParameterOptionsHelp['NI'])
]	

DelPhiGroupedParameterOptions = [
	('Basic', DelPhiBasicParameterOptions),
	('Advanced', DelPhiAdvancedParameterOptions)
]

DelPhiFileOutputOptions = [
	OutputFileOption('Potential File (phimap)', 'phi', 'default.phi', 
			required=1,
			help=OutputOptionsHelp['PHI']),
	OutputFileOption('Site Potentials File', 'frc', '',
			help=OutputOptionsHelp['FRC']),
	OutputFileOption('Dieletric Map File', 'eps', '',
			help=OutputOptionsHelp['EPS']),
	OutputFileOption('Modified PDB File', 'modpdb', '',
			help=OutputOptionsHelp['PDB']),
	OutputFileOption('Log File', 'log', 'delphi.out',
			help=OutputOptionsHelp['LOG'])
]

DelPhiGroupedOutputOptions = [
	('Energy', [EnergyOptions()]),
	('To a File', DelPhiFileOutputOptions)
]

DelPhiGroupedOptions = [
	('Input', DelPhiGroupedInputOptions),
	('Parameter', DelPhiGroupedParameterOptions),
	('Output', DelPhiGroupedOutputOptions)
]


# Input GUI class to handle interactive DelPhi input

from chimera.baseDialog import ModelessDialog
class DelPhiInputGUI(ModelessDialog):

	title = "DelPhiController"
	help = "ContributedSoftware/delphicontroller/delphicontroller.html"
	buttons = ( "Run", "Cancel" )
	default = "Run"

	def __init__(self, onRun_cb, onCancel_cb, *args, **kw):
		self.onRun_cb = onRun_cb
		self.onCancel_cb = onCancel_cb
		self.options = DelPhiGroupedOptions
		ModelessDialog.__init__(self, *args, **kw)

	def fillInUI(self, parent):
		# add a notebook to display option lists by "pages"
		self.notebook = Pmw.NoteBook(parent)
		self.notebook.pack(fill='both', expand=1)

		# fill in the pages with groups of options
		for pagetitle, optionsgroup in self.options:
			page = self.notebook.add(pagetitle)
			for grouptitle, optionslist in optionsgroup:
				group = Pmw.Group(page, tag_text=grouptitle)
				group.pack(fill='both', expand=1,
						padx=1, pady=1)
				for option in optionslist:
					option.addWidgets(group.interior())

		# different versions of Pmw size notebooks differently
		try:
			self.notebook.setnaturalsize()
		except AttributeError:
			self.notebook.setnaturalpagesize()
			
		
	def _handleRequest(self, function_cb, check):
		if check:
			# make sure all options are properly filled out
			for pagetitle, optionsgroup in self.options:
				for grouptitle, optionslist in optionsgroup:
					for option in optionslist:
						error = option.checkError()
						if error:
							replyobj.error(error)
							return
		function_cb(self.options)

	def Run(self):
		ModelessDialog.OK(self)
		self._handleRequest(self.onRun_cb, True)

	def Cancel(self):
		ModelessDialog.Cancel(self)
		self._handleRequest(self.onCancel_cb, False)

	def savePrefs(self):
		group = self.options[0][1]
		optList = group[1][1]
		execFile = optList[0].var.get()
		needSave = False
		if execFile and execFile != prefs["executable"]:
			prefs["executable"] = execFile
			needSave = True
		radiiFile = optList[1].var.get()
		if radiiFile and radiiFile != prefs["radii"]:
			prefs["radii"] = radiiFile
			needSave = True
		chargesFile = optList[2].var.get()
		if chargesFile and chargesFile != prefs["charges"]:
			prefs["charges"] = chargesFile
			needSave = True
		if needSave:
			preferences.save()
