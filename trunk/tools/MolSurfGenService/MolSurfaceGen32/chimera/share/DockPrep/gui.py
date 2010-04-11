# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 27494 2009-05-04 23:59:41Z pett $

from chimera.baseDialog import ModelessDialog
from chimera import dialogs
from prefs import prefs, defaults, INCOMPLETE_SC

class DockPrepDialog(ModelessDialog):
	name = "dock prep dialog"
	title = "Dock Prep"
	buttons = ('OK', 'Cancel')
	default = 'OK'
	help = "ContributedSoftware/dockprep/dockprep.html"

	def fillInUI(self, parent):
		import Tkinter, Pmw
		row=0
		from chimera.widgets import MoleculeScrolledListBox
		self.molListBox = MoleculeScrolledListBox(parent,
			labelpos="nw", label_text="Molecules to prep:",
			listbox_selectmode="extended")
		self.molListBox.grid(row=row, sticky='ew')
		row += 1

		Tkinter.Label(parent, text="\nFor chosen molecules,"
			" do the following:").grid(row=row, sticky='w')
		row += 1

		self.delSolventVar = Tkinter.IntVar(parent)
		self.delSolventVar.set(True)
		Tkinter.Checkbutton(parent, variable=self.delSolventVar, text=
			"Delete solvent").grid(row=row, sticky='w')
		row += 1

		self.delIonsVar = Tkinter.IntVar(parent)
		self.delIonsVar.set(False)
		Tkinter.Checkbutton(parent, variable=self.delIonsVar, text=
			"Delete non-complexed ions").grid(row=row, sticky='w')
		row += 1

		self.delAltLocsVar = Tkinter.IntVar(parent)
		self.delAltLocsVar.set(True)
		Tkinter.Checkbutton(parent, variable=self.delAltLocsVar, text=
			"If alternate locations, keep only highest occupancy",
			).grid(row=row, sticky='w')
		row += 1

		f = Tkinter.Frame(parent)
		f.grid(row=row, sticky='w')
		Tkinter.Label(f, text="Change:").grid(
						row=0, column=0, rowspan=4)
		self.mutMseVar = Tkinter.IntVar(parent)
		self.mutMseVar.set(True)
		Tkinter.Checkbutton(f, variable=self.mutMseVar, text=
			"selenomethionine (MSE) to methionine (MET)"
			).grid(row=0, column=1, sticky='w')
		self.mut5buVar = Tkinter.IntVar(parent)
		self.mut5buVar.set(True)
		Tkinter.Checkbutton(f, variable=self.mut5buVar, text=
			"bromo-UMP (5BU) to UMP (U)"
			).grid(row=1, column=1, sticky='w')
		self.mutUmsVar = Tkinter.IntVar(parent)
		self.mutUmsVar.set(True)
		Tkinter.Checkbutton(f, variable=self.mutUmsVar, text=
			"methylselenyl-dUMP (UMS) to UMP (U)"
			).grid(row=2, column=1, sticky='w')
		self.mutCslVar = Tkinter.IntVar(parent)
		self.mutCslVar.set(True)
		Tkinter.Checkbutton(f, variable=self.mutCslVar, text=
			"methylselenyl-dCMP (CSL) to CMP (C)"
			).grid(row=3, column=1, sticky='w')
		row += 1

		self.incompleteVar = Tkinter.IntVar(parent)
		self.incompleteVar.set(True)
		f = Tkinter.Frame(parent)
		Tkinter.Checkbutton(f, variable=self.incompleteVar,
			text="Incomplete side chains:",
			command=self._incompleteCB).grid(row=0, column=0)
		from Rotamers import libraries
		libraries.sort(lambda a, b: cmp(a.displayName, b.displayName))
		from chimera.tkoptions import SymbolicEnumOption
		labels = ["Replace using %s rotamer library" % lib.displayName
							for lib in libraries]
		labels.append("Mutate residues to ALA (if CB present) or GLY")
		values = libraries + ["gly/ala"]
		class IncompleteSCOption(SymbolicEnumOption):
			pass
		IncompleteSCOption.labels = labels
		IncompleteSCOption.values = values
		for possibleDefault in (prefs[INCOMPLETE_SC],
						defaults[INCOMPLETE_SC]):
			for val in IncompleteSCOption.values:
				if type(val) == str:
					if val == possibleDefault:
						default = possibleDefault
						break
				elif val.importName == possibleDefault:
					default = val
					break
			else:
				continue
			break
		self.incompleteOpt = IncompleteSCOption(f, 0, "", default,
							self._incompleteCB)
		f.grid(row=row, sticky='w')
		row += 1

		self.addHydVar = Tkinter.IntVar(parent)
		self.addHydVar.set(True)
		Tkinter.Checkbutton(parent, variable=self.addHydVar,
			text="Add hydrogens").grid(row=row, sticky='w')
		row += 1

		self.addChargesVar = Tkinter.IntVar(parent)
		self.addChargesVar.set(True)
		Tkinter.Checkbutton(parent, variable=self.addChargesVar,
			text="Add charges").grid(row=row, sticky='w')
		row += 1

		self.writeMol2Var = Tkinter.IntVar(parent)
		self.writeMol2Var.set(True)
		Tkinter.Checkbutton(parent, variable=self.writeMol2Var,
			text="Write Mol2 file").grid(row=row, sticky='w')
		row += 1
		self.applyKeywords = {}
		self.citationWidgets = {}
		self.citationRow = row
		self._incompleteCB()

	def Apply(self):
		from DockPrep import prep
		if self.addHydVar.get():
			import AddH
			addHFunc = AddH.hbondAddHydrogens
		else:
			addHFunc = None
		kw = self.applyKeywords
		self.applyKeywords = {}
		rotamerLib = rotamerPreserve = None
		if self.incompleteVar.get():
			incompleteVal = self.incompleteOpt.get()
			if type(incompleteVal) != str:
				rotamerLib = incompleteVal.importName
				rotamerPreserve = True
				incompleteVal = "rotamers"
			prefs[INCOMPLETE_SC] = incompleteVal
		else:
			incompleteVal = None
		prep(self.molListBox.getvalue(), addHFunc=addHFunc,
			addCharges=self.addChargesVar.get(),
			runSaveMol2Dialog=self.writeMol2Var.get(),
			mutateMSE=self.mutMseVar.get(),
			mutate5BU=self.mut5buVar.get(),
			mutateUMS=self.mutUmsVar.get(),
			mutateCSL=self.mutCslVar.get(),
			delSolvent=self.delSolventVar.get(),
			delIons=self.delIonsVar.get(),
			delAltLocs=self.delAltLocsVar.get(),
			incompleteSideChains=incompleteVal,
			rotamerLib=rotamerLib,
			rotamerPreserve=rotamerPreserve, **kw)

	def _incompleteCB(self, *args):
		if 'showing' in self.citationWidgets:
			self.citationWidgets['showing'].grid_forget()
			del self.citationWidgets['showing']
		if not self.incompleteVar.get():
			return
		lib = self.incompleteOpt.get()
		if type(lib) == str:
			return
		if lib not in self.citationWidgets:
			if lib.citation:
				from CGLtk.Citation import Citation
				citationWidget = Citation(self.uiMaster(),
					lib.citation, prefix="Publications"
					" using %s rotamers should cite:"
					% lib.citeName)
			else:
				citationWidget = None
			self.citationWidgets[lib] = citationWidget
		else:
			citationWidget = self.citationWidgets[lib]
		if citationWidget:
			citationWidget.grid(row=self.citationRow, column=0)
			self.citationWidgets['showing'] = citationWidget
			
dialogs.register(DockPrepDialog.name, DockPrepDialog)
