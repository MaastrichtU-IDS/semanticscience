"""dialog for writing models as Mol2 files"""

from OpenSave import SaveModeless
from chimera import replyobj, preferences, selection, openModels, Molecule

class WriteMol2Dialog(SaveModeless):
	keepShown = SaveModeless.default
	name = "write Mol2"
	help = "UsersGuide/savemodel.html#mol2"

	def __init__(self):
		self.prefs = preferences.addCategory("write Mol2 dialog",
				preferences.HiddenCategory,
				optDict={"multiSaveMol2": "multiple",
					"hydrogen naming": "sybyl",
					"residue numbers": True})
		SaveModeless.__init__(self, clientPos='s', clientSticky='ewns',
			filters=[("Mol2", "*.mol2", ".mol2")])
		openModels.addAddHandler(self._modelsChange, None)
		openModels.addRemoveHandler(self._modelsChange, None)
		self._modelsChange()

	def configure(self, models=None, refreshList=True, selOnly=None):
		if models is not None:
			if len(models) > 1:
				name = "Multiple Models "
			elif models:
				name = models[0].name + " "
			else:
				name = ""
			self._toplevel.title("Save %sas Mol2 File" % name)
			if refreshList:
				self.modelList.setvalue(models)

			if len(models) > 1:
				self.multiSaveMenu.grid(row=self._msmRow,
						column=0, sticky='w')
			else:
				self.multiSaveMenu.grid_forget()

	def fillInUI(self, parent):
		import Pmw, Tkinter
		SaveModeless.fillInUI(self, parent)
		row = 0

		from chimera.widgets import MoleculeScrolledListBox, \
							ModelOptionMenu
		self.modelList = MoleculeScrolledListBox(self.clientArea,
			labelpos='w', label_text="Save models:",
			listbox_selectmode='extended',
			selectioncommand=lambda: self.configure(
			self.modelList.getvalue(), refreshList=False))
		self.modelList.grid(row=row, column=0, sticky='nsew')
		self.clientArea.rowconfigure(row, weight=1)
		self.clientArea.columnconfigure(0, weight=1)
		row += 1

		from chimera import dialogs
		self.labelMap = {
			"individual":
				"a single file [individual @MOLECULE sections]",
			"combined":
				"a single file [combined @MOLECULE section]",
			"multiple":
				"multiple files [appending model number]"
		}
		preferred = self.labelMap[self.prefs["multiSaveMol2"]]
		self.multiSaveMenu = Pmw.OptionMenu(self.clientArea,
			labelpos='w', label_text="Save multiple models in",
			initialitem=preferred, items=self.labelMap.values())
		# not always shown; remember row number
		self._msmRow = row
		row += 1

		self.saveRelativeVar = Tkinter.IntVar(self.clientArea)
		self.saveRelativeVar.set(False)
		self.relativeFrame = f = Tkinter.Frame(self.clientArea)
		Tkinter.Checkbutton(f, variable=self.saveRelativeVar,
			text="Save relative to model:").grid(row=0,
			column=0, sticky='e')
		self.relModelMenu = ModelOptionMenu(f)
		self.relModelMenu.grid(row=0, column=1, sticky='w')
		self.saveUntransformedVar = Tkinter.IntVar(parent)
		self.saveUntransformedVar.set(True)
		self.untransformedButton = Tkinter.Checkbutton(self.clientArea,
					variable=self.saveUntransformedVar,
					text="Use untransformed coordinates")
		self._rfRow = row
		row += 1

		self.sybylHydNamesVar = Tkinter.IntVar(self.clientArea)
		self.sybylHydNamesVar.set(
				self.prefs["hydrogen naming"] == "sybyl")
		Tkinter.Checkbutton(self.clientArea,
			variable=self.sybylHydNamesVar,
			text="Use Sybyl-style hydrogen naming (e.g. HE12"
			" rather than 2HE1)").grid(row=row, column=0,
			sticky="w")
		row += 1

		self.resNumsVar = Tkinter.IntVar(self.clientArea)
		self.resNumsVar.set(self.prefs["residue numbers"])
		Tkinter.Checkbutton(self.clientArea, variable=self.resNumsVar,
			text="Include residue sequence numbers in substructure"
			" names").grid(row=row, column=0, sticky='w')
		row += 1

		self.writeGaffVar = Tkinter.IntVar(self.clientArea)
		self.resNumsVar.set(False)
		Tkinter.Checkbutton(self.clientArea, variable=self.writeGaffVar,
			text="Write Amber/GAFF atom types instead of Sybyl atom types"
			).grid(row=row, column=0, sticky='w')
		row += 1

		self.rigidVar = Tkinter.IntVar(self.clientArea)
		self.rigidVar.set(False)
		Tkinter.Checkbutton(self.clientArea, variable=self.rigidVar,
			text="Write current selection to @SETS section of file"
			).grid(row=row, column=0, sticky="w")
		row += 1

	def Apply(self):
		from chimera import dialogs
		kw = {'status': replyobj.status}

		paths = self.getPaths()
		if not paths:
			replyobj.error('No save location chosen.\n')
			return
		path = paths[0]
		models = self.modelList.getvalue()
		if not models:
			replyobj.error("No models chosen to save.\n")
			return
		if float(self.modelList.size()) > 1.5:
			if self.saveRelativeVar.get():
				kw['relModel'] = self.relModelMenu.getvalue()
		else:
			if self.saveUntransformedVar.get():
				kw['relModel'] = models[0]
			
		if self.writeGaffVar.get():
			kw['gaffType'] = True
		from chimera import UserError
		kw['gaffFailError'] = UserError

		if self.rigidVar.get():
			sel = selection.copyCurrent()
			sel.addImplied()
			selAtoms = sel.atoms()
			selBonds = sel.bonds()
			if selAtoms and selBonds:
				kw['anchor'] = sel
		sybylHydNaming = self.sybylHydNamesVar.get()
		if sybylHydNaming:
			self.prefs["hydrogen naming"] = "sybyl"
		else:
			self.prefs["hydrogen naming"] = "pdb"
		kw['hydNamingStyle'] = self.prefs["hydrogen naming"]

		kw['resNum'] = self.resNumsVar.get()
			
		from WriteMol2 import writeMol2
		if len(models) < 2:
			replyobj.status("Writing %s to %s\n" %
							(models[0].name, path))
			writeMol2(models, path, **kw)
			replyobj.status("Wrote %s to %s\n" %
							(models[0].name, path))
			return

		saveOpt = self.multiSaveMenu.getvalue()
		for key, value in self.labelMap.items():
			if saveOpt == value:
				break
		self.prefs["multiSaveMol2"] = key

		# write multiple models to multiple files
		if key == "multiple":
			if path.endswith(".mol2"):
				start, end = path[:-4], ".mol2"
			else:
				start, end = path, ""
			for m in models:
				modelPath = start + m.oslIdent()[1:] + end
				replyobj.status("Writing %s (%s) to %s\n" %
					(m.name, m.oslIdent(), modelPath))
				writeMol2(m, modelPath, **kw)
				replyobj.status("Wrote %s (%s) to %s\n" %
					(m.name, m.oslIdent(), modelPath))
			return
		kw["multimodelHandling"] = key

		# write multiple models to single file
		replyobj.status("Writing multiple models to %s\n" % path)
		writeMol2(models, path, **kw)
		replyobj.status("Wrote multiple models to %s\n" % path)

	def _modelsChange(self, *args):
		if len(openModels.listIds()) > 1:
			self.untransformedButton.grid_forget()
			self.relativeFrame.grid(row=self._rfRow,
						column=0, sticky='w')
		else:
			self.relativeFrame.grid_forget()
			self.untransformedButton.grid(row=self._rfRow,
						column=0, sticky='w')
	
from chimera.dialogs import register
register(WriteMol2Dialog.name, WriteMol2Dialog)
