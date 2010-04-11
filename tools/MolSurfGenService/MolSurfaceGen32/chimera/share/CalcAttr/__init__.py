import Pmw, Tkinter
import chimera
from chimera import selection
from chimera.baseDialog import ModelessDialog
import attrdef

NameFirstChar = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
NameChar = NameFirstChar + "0123456789"

class Interface(ModelessDialog):

	title = "Attribute Calculator"
	help = "ContributedSoftware/calculator/calculator.html"

	def fillInUI(self, parent):
		f = Tkinter.Frame(parent)
		f.pack(side="top", fill="x")
		self.attrName = Pmw.EntryField(f,
					labelpos="w",
					label_text="Calculate attribute ",
					value="attributeName",
					validate=self._validateAttrName)
		self.attrName.pack(side="left")
		self.applyTo = Tkinter.Label(f, text="for")
		self.applyTo.pack(side="left")
		self.forClass = Pmw.OptionMenu(f,
					items=["atoms", "residues", "models" ])
		self.forClass.pack(side="left")
		self.formula = Pmw.ScrolledText(parent,
					labelpos="nw",
					label_text="Formula",
					text_height=4,
					text_width=50)
		self.formula.pack(fill="both", expand=True)
		self.options = Pmw.RadioSelect(parent,
					pady=0,
					buttontype="checkbutton",
					orient="vertical")
		self.options.pack(fill="x", expand=False)
		self.options.add("assignsel",
					text="Restrict attribute assignment to "
					"current selection, if any")
		self.options.add("usesel",
					text="Restrict formula domain to "
					"current selection, if any")
		self.options.add("rba",
					text="Open Render/Select by Attribute")
		self.options.add("show",
					text="Show calculation results "
						"in Reply Log")
		self.options.add("save",
					text="Save calculation results to file")
		self.options.setvalue(["assignsel", "rba"])

	def _validateAttrName(self, text):
		if len(text) == 0:
			return Pmw.PARTIAL
		if text[0] not in NameFirstChar:
			return Pmw.ERROR
		for c in text[1:]:
			if c not in NameChar:
				return Pmw.ERROR
		return Pmw.OK

	def Apply(self):
		if not self.attrName.valid():
			raise chimera.UserError(
					"Please enter valid attribute name")
		name = self.attrName.getvalue()

		formula = self.formula.getvalue()
		try:
			tokenList = attrdef.Scanner().tokenize(formula)
		except ValueError, s:
			raise chimera.UserError(
					"Formula tokenizing error: %s" % str(s))
		if not tokenList:
			raise chimera.UserError("You must specify a formula")
		parser = attrdef.Parser()
		try:
			ast = attrdef.Parser().parse(tokenList)
		except SyntaxError, s:
			raise chimera.UserError(
					"Formula parsing error: %s" % str(s))
		ev = attrdef.Evaluator(ast)

		opts = self.options.getvalue()
		klass = self.forClass.getvalue()
		selection.addImpliedCurrent()
		restrict = {}
		assignsel = "assignsel" in opts
		usesel = "usesel" in opts
		if usesel:
			assignsel = True
		if klass == "atoms":
			target = self._getAtoms(assignsel, usesel, restrict)
			attrsOf = "atoms"
			m = {}
			for a in target:
				m[a.molecule] = True
			modelList = m.keys()
			wrapper = AtomDataWrapper
		elif klass == "residues":
			target = self._getResidues(assignsel, usesel, restrict)
			attrsOf = "residues"
			m = {}
			for r in target:
				m[r.molecule] = True
			modelList = m.keys()
			wrapper = ResidueDataWrapper
		elif klass == "models":
			target = self._getMolecules(assignsel, usesel, restrict)
			attrsOf = "models"
			modelList = target
			wrapper = MoleculeDataWrapper

		good = 0
		bad = 0
		for t in target:
			try:
				v = ev.evaluate(wrapper(t, restrict))
			except (ValueError, TypeError), s:
				raise chimera.UserError(
					"Formula evaluation error: %s" % str(s))
			else:
				setattr(t, name, v)
				if v is not None:
					good += 1
				else:
					bad += 1
		if not ev.errors:
			warning = ""
		else:
			errorList = [ "Problems encountered in calculation:\n" ]
			for msg, count in ev.errors.iteritems():
				errorList.append("  [%d] %s\n" % (count, msg))
			warning = ''.join(errorList)
		if good == 0:
			chimera.replyobj.warning("%sUnable to calculate "
						"attribute for any %s.\n"
						% (warning, klass))
			return
		elif bad > 0:
			if bad == 1:
				count = "one"
				item = klass[:-1]
			else:
				count = str(bad)
				item = klass
			chimera.replyobj.warning("%sUnable to calculate "
						"attribute for %s %s.\n"
						% (warning, count, item))
		elif warning:
			chimera.replyobj.warning(warning)
		if "rba" in opts:
			try:
				from ShowAttr import ShowAttrDialog
			except ImportError:
				pass
			else:
				from chimera import dialogs
				d = dialogs.display(ShowAttrDialog.name)
				d.configure(models=modelList, attrsOf=attrsOf,
						attrName=None)
				d.refreshAttrs()
				d.configure(models=modelList, attrsOf=attrsOf,
						attrName=name)
		if "save" in opts or "show" in opts:
			text = self._saveText(target, name, klass)
			if "show" in opts:
				chimera.replyobj.message(text)
				from chimera import dialogs, tkgui
				dialogs.display(tkgui._ReplyDialog.name)
			if "save" in opts:
				_save(text)

	def _getAtoms(self, assignsel, usesel, restrict):
		if assignsel or usesel:
			sel = selection.currentAtoms()
			if usesel:
				for m in selection.currentMolecules():
					restrict[m] = True
				for r in selection.currentResidues():
					restrict[r] = True
				for a in sel:
					restrict[a] = True
		if assignsel:
			atoms = sel
		else:
			atoms = []
		if not atoms:
			atoms = []
			for m in chimera.openModels.list(
					modelTypes=[chimera.Molecule]):
				atoms += m.atoms
		return atoms

	def _getResidues(self, assignsel, usesel, restrict):
		if assignsel or usesel:
			sel = selection.currentResidues()
			if usesel:
				for m in selection.currentMolecules():
					restrict[m] = True
				for r in sel:
					restrict[r] = True
				for a in selection.currentAtoms():
					restrict[a] = True
		if assignsel:
			residues = sel
		else:
			residues = []
		if not residues:
			residues = []
			for m in chimera.openModels.list(
					modelTypes=[chimera.Molecule]):
				residues += m.residues
		return residues

	def _getMolecules(self, assignsel, usesel, restrict):
		if assignsel or usesel:
			sel = selection.currentMolecules()
			if usesel:
				for r in selection.currentResidues():
					restrict[r] = True
				for a in selection.currentAtoms():
					restrict[a] = True
				for m in sel:
					restrict[m] = True
		if assignsel:
			molecules = sel
		else:
			molecules = []
		if not molecules:
			molecules = chimera.openModels.list(
					modelTypes=[chimera.Molecule])
		return molecules

	def _saveText(self, target, name, klass):
		text = []
		text.append("attribute: %s\n" % name)
		text.append("match mode: 1-to-1\n")
		text.append("recipient: %s\n" % klass)
		for t in target:
			v = getattr(t, name, None)
			if v is not None:
				text.append("\t%s\t%s\n"
						% (t.oslIdent(), str(v)))
		return ''.join(text)

class DataWrapper:
	# Abstract base class.  Should not be instantiated directly.
	def __init__(self, data, restrict):
		self.data = data
		self.restrict = restrict

	def getAttribute(self, scope, attr):
		try:
			value = self._getAttr(scope, attr)
		except ValueError:
			return None
		else:
			def convert(v):
				try:
					return float(v)
				except (TypeError, ValueError):
					return v
			if type(value) is type([]):
				return [ convert(v) for v in value ]
			else:
				return convert(value)

	def _getAttr(self, scope, attr):
		if scope == attrdef.S_ATOM:
			return self.getAtomAttr(attr)
		elif scope == attrdef.S_RESIDUE:
			return self.getResidueAttr(attr)
		elif scope == attrdef.S_MOLECULE:
			return self.getMoleculeAttr(attr)
		else:
			raise ValueError, "unknown scope %s" % str(scope)

class AtomDataWrapper(DataWrapper):
	def getAtomAttr(self, attr):
		return getattr(self.data, attr, None)
	def getResidueAttr(self, attr):
		return getattr(self.data.residue, attr, None)
	def getMoleculeAttr(self, attr):
		return getattr(self.data.molecule, attr, None)

class ResidueDataWrapper(DataWrapper):
	def getAtomAttr(self, attr):
		if self.restrict:
			atomList = [ a for a in self.data.atoms
					if self.restrict.has_key(a) ]
		else:
			atomList = self.data.atoms
		return [ getattr(a, attr, None) for a in atomList ]
	def getResidueAttr(self, attr):
		return getattr(self.data, attr, None)
	def getMoleculeAttr(self, attr):
		return getattr(self.data.molecule, attr, None)

class MoleculeDataWrapper(DataWrapper):
	def getAtomAttr(self, attr):
		if self.restrict:
			atomList = [ a for a in self.data.atoms
					if self.restrict.has_key(a) ]
		else:
			atomList = self.data.atoms
		return [ getattr(a, attr, None) for a in atomList ]
	def getResidueAttr(self, attr):
		if self.restrict:
			residueList = [ r for r in self.data.residues
					if self.restrict.has_key(r) ]
		else:
			residueList = self.data.residues
		return [ getattr(r, attr, None) for r in residueList ]
	def getMoleculeAttr(self, attr):
		return getattr(self, attr, None)

_saveDialog = None
def _save(text):
	global _saveDialog
	if not _saveDialog:
		from OpenSave import SaveModeless
		_saveDialog = SaveModeless(
				title="Choose Attribute Calculator Save File",
				command=_fileChosen,
				initialfile="attrcalc.txt",
				historyID="Attribute Calculator Output")
	else:
		_saveDialog.enter()
	_saveDialog._text = text
def _fileChosen(okayed, dialog):
	if okayed:
		paths = dialog.getPaths()
		if paths:
			filename = paths[0]
			from OpenSave import osOpen
			outFile = osOpen(filename, "w")
			outFile.write(dialog._text)
			outFile.close()
	delattr(dialog, "_text")

singleton = None
def run():
	global singleton
	if not singleton:
		singleton = Interface()
	singleton.enter()
