"""dialog for writing models as prmtop files"""

from OpenSave import SaveModeless
from chimera import UserError

class WritePrmtopDialog(SaveModeless):
	keepShown = SaveModeless.default
	name = "write prmtop"
	help = "UsersGuide/savemodel.html#prmtop"

	def __init__(self):
		SaveModeless.__init__(self, clientPos='s', clientSticky='ewns',
			filters=[("Prmtop", "*.prmtop", ".prmtop")])

	def configure(self, model=None, refreshList=True):
		if model:
			self._toplevel.title(
				"Save %s as prmtop File" % model.name)
			if refreshList:
				self.modelMenu.setvalue(model)

	def fillInUI(self, parent):
		import Pmw, Tkinter
		SaveModeless.fillInUI(self, parent)
		row = 0

		from chimera.widgets import MoleculeOptionMenu
		self.modelMenu = MoleculeOptionMenu(self.clientArea,
			labelpos='w', label_text="Save model:",
			command=lambda m: self.configure(
			self.modelMenu.getvalue(), refreshList=False))
		self.modelMenu.grid(row=row, column=0, sticky='w')
		row += 1

		from AddCharge import knownChargeModels, defaultChargeModel

		from chimera import dialogs
		self.parmsetOption = Pmw.OptionMenu(self.clientArea,
			labelpos='w', label_text="Select force field type: ",
			initialitem=defaultChargeModel, items=knownChargeModels)
		# not always shown; remember row number
		self._msmRow = row
		self.parmsetOption.grid(row=row, column=0, sticky='w')
		row += 1

	def Apply(self):
		paths = self.getPaths()
		path = paths[0]
		model = self.modelMenu.getvalue()
		if not model:
			self.enter()
			raise UserError("No model chosen to save.")
			
		from WritePrmtop import writePrmtop
		from AddCharge.gui import checkNoCharges
		chargeModel = self.parmsetOption.getvalue()
		checkNoCharges([model], lambda ur, ua, model=model,
			path=paths[0], parmset=chargeModel[6:]:
			writePrmtop(model, path, parmset, unchargedAtoms=ua),
			"prmtop output", chargeModel=chargeModel)

from chimera.dialogs import register
register(WritePrmtopDialog.name, WritePrmtopDialog)
