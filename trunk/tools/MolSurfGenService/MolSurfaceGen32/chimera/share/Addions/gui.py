import chimera
from chimera.baseDialog import ModelessDialog, ModalDialog

import Pmw
import Tkinter
from CGLtk import Hybrid

from prefs import prefs, SOLVENT_MODEL



class NoChgsDialog(ModalDialog):
	title = "No Chargess..."
	help = "UsersGuide/midas/addcharge.html#needH"
	buttons = ('Abort', 'Add Charges', 'Continue Anyway')
	default = 'Add Charges'
	oneshot = True

	def __init__(self, msg):
		self.msg = msg
		ModalDialog.__init__(self)

	def fillInUI(self, parent):
		import Tkinter
		message = Tkinter.Label(parent, text=self.msg)
		message.grid(sticky='nsew')

	def Abort(self):
		self.Cancel("cancel")

	def AddCharges(self):
		self.Cancel("add charges")

	def ContinueAnyway(self):
		self.Cancel("continue")



class AddionsDialog(ModelessDialog):
	name = "addions"
	title = "Addions"
	#help = "ContributedSoftware/addcharge/addcharge.html"

	def fillInUI(self, parent):
		from chimera.widgets import MoleculeScrolledListBox
		self.molList = MoleculeScrolledListBox(parent, labelpos='w',
						listbox_selectmode="extended",
						label_text="Add ions : ")
		self.molList.grid(row=0, column=0, sticky="nsew")

		rcf1 = Tkinter.Frame(parent)
		rcf1.grid(row=2, column=0, sticky="nsew")
	
		from Addions import ValidIontypes
		self.iontype = "Cl-"
		self.iontypeOption = Pmw.OptionMenu(rcf1, label_text=
			"Ion types:", labelpos = 'w', items=ValidIontypes,
			initialitem=self.iontype, command=self.changeIontype)
		self.iontypeOption.grid(row=0, column=0)

		rcf2 = Tkinter.Frame(parent)
		rcf2.grid(row=3, column=0)
		rcf2.columnconfigure(2, weight=1)

		self.numionOption = Pmw.RadioSelect(rcf2,
				buttontype='radiobutton', command=self.changeNumion,
				labelpos='w', label_text="# of ions:")
		self.numionOption.add("neutralize")
		self.numionOption.add("specific number:")
		self.numionOption.setvalue( "neutralize" )
		self.numionOption.grid( row=0, column=0)
		self.numion = "neutralize"

		self.numionValue = Hybrid.StringVariable(rcf2)
		self.numionEntry = Tkinter.Entry(rcf2, width=5, textvariable=self.numionValue.tk_variable, state='disabled')
		self.numionEntry.grid( row=0, column=1 )


		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)

	def changeIontype(self, state):
		self.iontype= state

	def changeNumion(self, state):
		if state=="neutralize":
			self.numion = "neutralize"
			self.numionEntry.config( state="disabled" )
		else:
			self.numion = "specific" 
		    	self.numionEntry.config( state="normal" )


	def Apply(self):
		from chimera import UserError, replyobj
		if self.iontype=="":
			self.enter()
			raise UserError("No ion type chosen.")

		if self.numion =="specific":
			self.numion = self.numionValue.get()
			if self.numion=="":
				self.enter()
				raise UserError(" number of ion is not given." )

		else:
			assert self.numion=="neutralize"

		from Addions import initiateAddions
		mols = self.molList.getvalue()
		from AddCharge.gui import checkNoCharges
		checkNoCharges(mols, lambda ur, ua, mols=mols: initiateAddions(
			mols, self.iontype, self.numion, replyobj.status),
			"ion addition")

from chimera import dialogs
dialogs.register(AddionsDialog.name, AddionsDialog)

