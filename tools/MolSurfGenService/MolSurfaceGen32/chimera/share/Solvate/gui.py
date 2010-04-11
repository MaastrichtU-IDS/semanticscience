import chimera
from chimera.baseDialog import ModelessDialog

import Pmw
import Tkinter
from CGLtk import Hybrid

from prefs import prefs, SOLVENT_MODEL

class SolvateDialog(ModelessDialog):
	name = "solvate"
	title = "Solvate"
	#help = "ContributedSoftware/addcharge/addcharge.html"

	def fillInUI(self, parent):
		from chimera.widgets import MoleculeScrolledListBox
		self.molList = MoleculeScrolledListBox(parent, labelpos='w',
						listbox_selectmode="extended",
						label_text="Solvate:    ")
		self.molList.grid(row=0, column=0, sticky="nsew")
		self.solvateMethod = Pmw.RadioSelect(parent,
				buttontype='radiobutton', command=self.changeMethod,
				labelpos='w', label_text="Solvate method:")
		self.solvateMethod.add("Box")
		self.solvateMethod.add("Cap")
		self.solvateMethod.add("Oct")
		self.solvateMethod.add("Shell")
		self.solvateMethod.setvalue("Box")
		self.solvateMethod.grid(row=1, column=0, sticky="nsew")
                self.method = "Box"
		rcf1 = Tkinter.Frame(parent)
		rcf1.grid(row=2, column=0, sticky="nsew")
		self.solvent = prefs[SOLVENT_MODEL]

		from Solvate import ValidSolventModels
		self.solventModel = Pmw.OptionMenu(rcf1, label_text=
			"Solvent Model:", labelpos = 'w', items=ValidSolventModels,
			initialitem=self.solvent, command=self.changeSolvent)
		self.solventModel.grid(row=0, column=0)

		rcf2 = Tkinter.Frame(rcf1)
		rcf2.grid(row=0, column=1)
		rcf1.columnconfigure(1, weight=1)
		self.extentLabel = Tkinter.Label(rcf2, text="Box size:" )
		self.extentLabel.grid(row=0, column=0)
		
		self.extentValue = Hybrid.StringVariable(rcf2)
		ev = Tkinter.Entry( rcf2, width=5, textvariable=self.extentValue.tk_variable)
		ev.grid( row=0, column=1 )

		rcf3 = Tkinter.Frame(parent)
		rcf3.grid(row=3, column=0)
		self.centerLabel = Tkinter.Label(rcf3, text="Cap center (in ambmask):", state='disabled' )
		self.centerLabel.grid(row=0, column=0)
		
		self.centerValue = Hybrid.StringVariable(rcf3)
		self.centerEntry = Tkinter.Entry( rcf3, width=5, textvariable=self.centerValue.tk_variable, state='disabled')
		self.centerEntry.grid( row=0, column=1 )

		self.removeExisting = Hybrid.Checkbutton(parent,
					"Remove existing ions/solvent", True)
		self.removeExisting.button.grid(row=4, column=0)


		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)

	def changeMethod(self, state):
		self.method = state
		if state=="Box":
		    self.extentLabel.config( text="Box size: " )
		    self.centerLabel.config( state='disabled' )
		    self.centerEntry.config( state='disabled' )
		elif state=="Cap":
		    self.extentLabel.config( text="Cap Radius: " )
		    self.centerLabel.config( state='normal' )
		    self.centerEntry.config( state='normal' )
		elif state=="Oct":
		    self.extentLabel.config( text="Oct size: " )
		    self.centerLabel.config( state='disabled' )
		    self.centerEntry.config( state='disabled' )
		else:
		    assert state=="Shell"
		    self.extentLabel.config( text="Shell extent: " )
		    self.centerLabel.config( state='disabled' )
		    self.centerEntry.config( state='disabled' )

	def changeSolvent(self, solvent):
		self.solvent = solvent

	def Apply(self):
		from chimera import UserError
		if self.solvent=="":
			self.enter()
			raise UserError("No solvent model chosen.")

		if self.extentValue.get()=="":
			self.enter()
			raise UserError(self.method + " size is not given." )

		if self.method=="Cap" and self.centerValue.get()=="":
			self.enter()
			raise UserError("Center of cap is not given.")

		prefs[SOLVENT_MODEL] = self.solvent

		from Solvate import initiateSolvate
		mols = self.molList.getvalue()
		if self.removeExisting.variable.get():
			from Midas import deleteAtomsBonds
			deleteAtomsBonds(atoms=[a for m in mols
				for a in m.atoms
				if a.surfaceCategory in ["solvent", "ions"]])
			# in case any models were _all_ solvent/ions...
			mols = [m for m in mols if not m.__destroyed__]
		noHyds = []
		for mol in mols:
			for a in mol.atoms:
				if a.element.number == 1:
					break
			else:
				noHyds.append(mol)
		if noHyds:
			from chimera.baseDialog import AskYesNoDialog
			msg = "Hydrogens must be present for" \
				" solvation to work correctly.\n"
			if len(mols) == len(noHyds):
				msg += "No models have hydrogens.\n"
			else:
				msg += "The following models have no" \
						" hydrogens:\n"
				for nh in noHyds:
					msg += "\t%s (%s)\n" % (nh.name,
								nh.oslIdent())
			msg += "You can add hydrogens using the AddH tool.\n"
			msg += "What would you like to do?"
			from AddH.gui import NoHydsDialog
			userChoice = NoHydsDialog(msg).run(chimera.tkgui.app)
			if userChoice == "cancel":
				return
			elif userChoice == "add hydrogens":
				from AddH.gui import AddHDialog
				AddHDialog(title="Add Hydrogens for Solvate",
					models=noHyds, useHBonds=True,
					oneshot=True, cb=lambda mols=mols:
					initiateSolvate(mols,self.method, self.solvent,
					self.extentValue.get(), self.centerValue.get(),
					chimera.replyobj.status))
				return


		initiateSolvate(mols, self.method, self.solvent, self.extentValue.get(), self.centerValue.get(), chimera.replyobj.status)

from chimera import dialogs
dialogs.register(SolvateDialog.name, SolvateDialog)

