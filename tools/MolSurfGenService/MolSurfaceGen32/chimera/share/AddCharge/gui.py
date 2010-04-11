import chimera
from chimera.baseDialog import ModelessDialog, ModalDialog

from prefs import prefs, CHARGE_METHOD

class AddChargesDialog(ModelessDialog):
	name = "add charges"
	title = "Add Charges"
	help = "ContributedSoftware/addcharge/addcharge.html"
	default = 'OK'

	def __init__(self, process=None, models=None, chargeModel=None,
								cb=None, **kw):
		if process:
			self.title = "Assign Charges for %s" % process.title()
		else:
			from AddCharge import process
		self.process = process
		self.cb = cb
		self.startModels = models
		if not chargeModel:
			from AddCharge import defaultChargeModel
			chargeModel = defaultChargeModel
		self.initialChargeModel = chargeModel
		ModelessDialog.__init__(self, **kw)

	def fillInUI(self, parent):
		from chimera.widgets import MoleculeScrolledListBox
		self.molList = MoleculeScrolledListBox(parent, labelpos='w',
						listbox_selectmode="extended",
						label_text='Add charges to:')
		if self.startModels:
			self.molList.setvalue(self.startModels)
		self.molList.grid(row=0, column=0, sticky="nsew")
		parent.rowconfigure(0, weight=1)
		parent.columnconfigure(0, weight=1)

		import Pmw
		from AddCharge import knownChargeModels, defaultChargeModel
		self.chargeModel = Pmw.OptionMenu(parent, labelpos='w',
					label_text="Standard residues:",
					items=knownChargeModels,
					initialitem=self.initialChargeModel)
		self.chargeModel.grid(row=1, column=0)

		self.chargeMethod = ChargeMethodOption(parent,
						label="Other residues:")
		self.chargeMethod.grid(row=2, column=0)

		import Tkinter
		labelFrame = Tkinter.Frame(parent)
		labelFrame.grid(row=3, column=0)
		Tkinter.Label(labelFrame, text="Add labels showing charges"
			" to atoms in:").grid(row=0, column=0, rowspan=2)
		self.labelNonstandardVar = Tkinter.IntVar(parent)
		self.labelNonstandardVar.set(False)
		Tkinter.Checkbutton(labelFrame, text="nonstandard residues",
			variable=self.labelNonstandardVar).grid(row=0, column=1, sticky='w')
		self.labelStandardVar = Tkinter.IntVar(parent)
		self.labelStandardVar.set(False)
		Tkinter.Checkbutton(labelFrame, text="standard residues",
			variable=self.labelStandardVar).grid(row=1, column=1, sticky='w')

	def Apply(self):
		from AddCharge import initiateAddCharges
		from AddH.gui import checkNoHyds
		mols = self.molList.getvalue()
		chargeModel = self.chargeModel.getvalue()
		chargeMethod = self.chargeMethod.getvalue()
		checkNoHyds(mols, lambda mols=mols: initiateAddCharges(
			cb=self.cb, models=mols, chargeModel=chargeModel,
			method=chargeMethod, status=chimera.replyobj.status,
			labelStandard=self.labelStandardVar.get(),
			labelNonstandard=self.labelNonstandardVar.get()),
			self.process)

from chimera import dialogs
dialogs.register(AddChargesDialog.name, AddChargesDialog)

class NonstandardChargeDialog(ModelessDialog):
	title = "Specify Net Charges"
	help = "ContributedSoftware/addcharge/addcharge.html#antechamber"
	buttons = ('OK', 'Cancel')
	oneshot = True

	def __init__(self, cb, unchargedResidues, unchargedAtoms,
						method, status, gaffType, showCharges=False):
		self.cb = cb
		self.unchargedResidues = unchargedResidues
		self.unchargedAtoms = unchargedAtoms
		self.status = status
		self.method = method
		self.gaffType = gaffType
		self.showCharges = showCharges
		ModelessDialog.__init__(self)

	def fillInUI(self, parent):
		import Tkinter
		outline = Tkinter.Frame(parent, bd=1, bg='black')
		outline.grid(row=0, column=0)
		tableFrame = Tkinter.Frame(outline)
		tableFrame.grid()
		Tkinter.Label(tableFrame, text="Residue", relief='ridge',
			borderwidth=3).grid(row=0, column=0)
		Tkinter.Label(tableFrame, text="Net Charge", relief='ridge',
			borderwidth=3).grid(row=0, column=1)
		import Pmw

		from AddCharge import estimateNetCharge
		self.options = {}
		resNames = self.unchargedResidues.keys()
		resNames.sort()
		for i, resName in enumerate(resNames):
			Tkinter.Label(tableFrame, text=resName).grid(row=i+1,
								column=0)
			estCharge = estimateNetCharge(
				self.unchargedResidues[resName][0].atoms)
			lowCharge = min(-9, estCharge-5)
			highCharge = max(9, estCharge+5)
			self.options[resName] = Pmw.OptionMenu(tableFrame,
				initialitem="%+d" % estCharge, items=["%+d"
				% v for v in range(lowCharge, highCharge+1)])
			self.options[resName].grid(row=i+1, column=1)
		Tkinter.Label(parent, text="Please specify the net"
			" charges for the above residues\nso that their"
			" atomic partial charges can be computed.").grid(
			row=1, column=0)

		self.chargeMethod = ChargeMethodOption(parent,
							method=self.method)
		self.chargeMethod.grid(row=2, column=0)

		from CGLtk.Citation import Citation
		Citation(parent, "Wang, J., Wang, W., Kollman, P.A., and"
			" Case, D.A. (2006)\n"
			"Automatic atom type and bond type perception in"
			" molecular mechanical calculations\n"
			"Journal of Molecular Graphics and Modelling, 25,"
			" 247-260.",
			prefix="Charges are computed using ANTECHAMBER.\n"
			"Publications using ANTECHAMBER charges should cite:"
			).grid(row=3, column=0)

	def Apply(self):
		from AddCharge import addNonstandardResCharges, ChargeError
		prefs[CHARGE_METHOD] = self.chargeMethod.getvalue()
		for resName, opt in self.options.items():
			try:
				addNonstandardResCharges(
					self.unchargedResidues[resName],
					int(opt.getvalue()), status=self.status,
					method=prefs[CHARGE_METHOD].lower(),
					gaffType=self.gaffType, showCharges=self.showCharges)
			except ChargeError, v:
				from chimera import NonChimeraError
				raise NonChimeraError(v)
			del self.unchargedResidues[resName]
		if self.cb:
			self.cb(self.unchargedResidues, self.unchargedAtoms)

class PhosphorylateDialog(ModalDialog):
	title = "Delete 5' phosphates?"
	buttons = ('Yes', 'No')
	default = 'Yes'
	oneshot = True
	help = "ContributedSoftware/addcharge/addcharge.html#terminalP"

	def fillInUI(self, parent):
		import Tkinter
		text = \
"""Delete 5' terminal phosphates from nucleic acid chains?
The AMBER charge set lacks parameters for 5' terminal phosphates,
and if retained, atoms in such groups will be assigned charges of zero."""
		message = Tkinter.Label(parent, text=text)
		message.grid(sticky='nsew')

	def No(self):
		self.Cancel(False)

	def Yes(self):
		self.Cancel(True)

class NoChargesDialog(ModalDialog):
	title = "No Charges..."
	buttons = ('Abort', 'Assign Charges', 'Continue Anyway')
	default = 'Assign Charges'
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

	def AssignCharges(self):
		self.Cancel("assign charges")

	def ContinueAnyway(self):
		self.Cancel("continue")

def checkNoCharges(items, cb, process, chargeModel=None):
	noCharges = []
	chargeModelOkay = True
	if type(items[0]) == chimera.Atom:
		for a in items:
			if chargeModel and (not hasattr(a.molecule,
					"chargeModel") or a.molecule.chargeModel
					!= chargeModel):
				chargeModelOkay = False
				noCharges.append(a)
			elif not hasattr(a, 'charge'):
				noCharges.append(a)
	else:
		for item in items:
			if chargeModel:
				try:
					mol = item.molecule
				except AttributeError:
					mol = item
				if not hasattr(mol, "chargeModel") \
				or mol.chargeModel != chargeModel:
					chargeModelOkay = False
					noCharges.append(item)
					continue
			for a in item.atoms:
				if not hasattr(a, 'charge') \
				or (chargeModel and not hasattr(a, 'gaffType')):
					break
			else:
				continue
			noCharges.append(item)
	if not noCharges:
		cb(None, None)
		return
	from chimera.baseDialog import AskYesNoDialog
	if chargeModelOkay:
		msg = "Partial atomic charges must be completely assigned for" \
			" %s to work correctly.\n" % process
		missingPhrase = "have missing charges"
		assignPhrase = "assign charges"
	else:
		msg = "%s%s requires %s charge model assignments.\n" % (
				process[0].upper(), process[1:], chargeModel)
		missingPhrase = "have charges that are either missing or inconsistent with %s" % chargeModel
		assignPhrase = "make such assignments"
	if type(items[0]) == chimera.Atom:
		objDesc = "atom"
		attrName = "name"
		noChargeModels = list(set([a.molecule for a in noCharges]))
	elif type(items[0]) == chimera.Residue:
		objDesc = "residue"
		attrName = "type"
		noChargeModels = list(set([r.molecule for r in noCharges]))
	else:
		objDesc = "model"
		attrName = "name"
		noChargeModels = noCharges
	if len(items) == len(noCharges):
		msg += "All %ss %s.\n" % (objDesc, missingPhrase)
	else:
		msg += "The following %ss %s:\n" % (objDesc, missingPhrase)
		for nc in noCharges:
			msg += "\t%s (%s)\n" % (getattr(nc, attrName),
								nc.oslIdent())
	msg += "You can %s using the Add Charge tool.\n" % assignPhrase
	msg += "What would you like to do?"
	userChoice = NoChargesDialog(msg).run(chimera.tkgui.app)
	if userChoice == "assign charges":
		AddChargesDialog(models=noChargeModels, oneshot=True, cb=cb,
						chargeModel=chargeModel)
	elif userChoice == "continue":
		cb(None, None)
import Pmw
class ChargeMethodOption(Pmw.RadioSelect):
	def __init__(self, parent, label="Charge method:", method=None):
		Pmw.RadioSelect.__init__(self, parent, buttontype='radiobutton',
					labelpos='w', label_text=label)
		self.add("AM1-BCC")
		self.add("Gasteiger")
		if method is None:
			self.setvalue(prefs[CHARGE_METHOD])
		else:
			if method.lower()[:3] == "am1":
				self.setvalue("AM1-BCC")
			else:
				self.setvalue("Gasteiger")
