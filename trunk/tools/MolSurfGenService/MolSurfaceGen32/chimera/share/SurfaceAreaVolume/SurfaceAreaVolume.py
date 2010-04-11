import Pmw, Tkinter
import chimera
from chimera.baseDialog import ModelessDialog
from chimera.widgets import MoleculeScrolledListBox
from chimera.widgets import MoleculeChainScrolledListBox
import StrucTools

NameFirstChar = "_abcdefghijklmnopqrstuvwxyzABCDEFGHIJKLMNOPQRSTUVWXYZ"
NameChar = NameFirstChar + "0123456789"

class Interface(ModelessDialog):

	title = "Compute Surface Area and Volume"
	help = "ContributedSoftware/surfvol/surfvol.html"

	def fillInUI(self, parent):
		self.notebook = Pmw.NoteBook(parent)
		self.notebook.pack(fill="both", expand=True)
		page = self.notebook.add("Molecules")
		self.molChooser = MoleculeScrolledListBox(page,
					listbox_selectmode="extended",
					autoselect="single")
		self.molChooser.pack(fill="both", expand=True)
		page = self.notebook.add("Chains")
		self.chainChooser = MoleculeChainScrolledListBox(page,
					listbox_selectmode="extended",
					autoselect="single")
		self.chainChooser.pack(fill="both", expand=True)
		titles = self.Servers.keys()
		titles.sort()
		self.serverChooser = Pmw.OptionMenu(parent,
					labelpos="w",
					label_text="Compute:",
					items=titles,
					command=self._changeServer)
		self.serverChooser.pack(fill="x", expand=False)
		self.paramHolder = Tkinter.Frame(parent, padx=10, pady=2)
		self.paramHolder.pack(fill="x", expand=False)
		self.paramFrames = {}
		for name, val in self.Servers.iteritems():
			self.paramFrames[name] = val[2](self, self.paramHolder)
		self.propertyName = Pmw.EntryField(parent,
					labelpos="w",
					label_text="As attribute:",
					value=self.Servers[titles[0]][0],
					validate=self._validatePropName)
		self.propertyName.pack(fill="x", expand=False)
		self.outputOptions = Pmw.RadioSelect(parent,
					pady=0,
					buttontype="checkbutton",
					orient="vertical")
		self.outputOptions.pack(fill="x", expand=False)
		self.outputOptions.add("rba",
					text="Open Render/Select by Attribute")
		self.outputOptions.add("save",
					text="Save server output to file")
		self.outputOptions.add("show",
					text="Show server output in browser")
		self.outputOptions.setvalue(["rba"])
		self._changeServer(titles[0])

	def _changeServer(self, name):
		self.propertyName.setvalue(self.Servers[name][0])
		for n, (frame, parts) in self.paramFrames.iteritems():
			if n == name:
				frame.pack(fill="x", expand=True)
			else:
				frame.forget()

	def _validatePropName(self, text):
		if len(text) == 0:
			return Pmw.PARTIAL
		if text[0] not in NameFirstChar:
			return Pmw.ERROR
		for c in text[1:]:
			if c not in NameChar:
				return Pmw.ERROR
		return Pmw.OK

	def Apply(self):
		if not self.propertyName.valid():
			raise chimera.UserError(
					"Please enter valid attribute name")
		propName = self.propertyName.getvalue()
		pageName = self.notebook.getcurselection()
		if pageName == "Molecules":
			target = self.molChooser.getvalue()
		elif pageName == "Chains":
			target = self.chainChooser.getvalue()
		if not target:
			raise chimera.UserError(
					"Please select molecule or chain")
		opts = self.outputOptions.getvalue()
		rba = "rba" in opts
		save = "save" in opts
		show = "show" in opts
		serverName = self.serverChooser.getcurselection()
		f = self.Servers[serverName][1]
		parts = self.paramFrames[serverName][1]
		opts = self.Servers[serverName][3](self, parts)
		output = f(target, opts, propName, rba)
		if save:
			_save(output, show)
		elif show:
			# create temporary file and invoke browser
			from OpenSave import osTemporaryFile
			filename = osTemporaryFile(suffix=".html")
			f = open(filename, "w")
			f.write(output)
			f.close()
			import urllib
			from chimera import help
			help.display("file:" + urllib.pathname2url(filename))

	_paramMsmsParams = [
		(	"Surface probe size:",
			"msms_probe",
			( ( "1.3", "1.3" ),
			  ( "1.4", "1.4" ),
			  ( "1.5", "1.5" ),
			  ( "1.6", "1.6" ) ),
			"1.5"
		),
		(	"Atoms to use:",
			"msms_atoms",
			( ( "No Hetatms", "HETATM" ),
			  ( "Atoms + Hetatms", "ZZZZZZ" ),
			  ( "All atoms except waters", "HOH" ) ),
			"No Hetatms"
		),
	]
	_paramGersteinSurfaceParams = [
		(	"Surface probe size:",
			"surf_Gerstein_probe",
			( ( "1.3", "1.3" ),
			  ( "1.4", "1.4" ),
			  ( "1.5", "1.5" ),
			  ( "1.6", "1.6" ) ),
			"1.4"
		),
		(	"Atoms to use:",
			"surf_Gerstein_atoms",
			( ( "No Hetatms", "HETATM" ),
			  ( "Atoms + Hetatms", "ZZZZZZ" ),
			  ( "All atoms except waters", "HOH" ) ),
			"All atoms except waters"
		),
	]
	_paramGersteinVolumeParams = [
		(	"Method:",
			"vol_Gerstein_method",
			( ( "Normal Voronoi", "1" ),
			  ( "Method B", "2" ),
			  ( "Radical Plane", "3" ),
			  ( "Modified Method B", "4" ) ),
			"Method B"
		),
		(	"Radii:",
			"vol_Gerstein_radii",
			( ( "Chothia Radii", "" ),
			  ( "Richards Radii", "-RichardsRadii" ) ),
			"Chothia Radii"
		),
		(	"Atoms to use:",
			"vol_Gerstein_atoms",
			( ( "No Hetatms", "HETATM" ),
			  ( "Atoms + Hetatms", "ZZZZZZ" ),
			  ( "All atoms except waters", "HOH" ) ),
			"No Hetatms"
		),
	]
	def _paramMakeMsms(self, group):
		return self._paramMake(group, self._paramMsmsParams)
	def _paramGetMsms(self, parts):
		return self._paramGet(parts, self._paramMsmsParams)
	def _paramMakeGersteinSurface(self, group):
		return self._paramMake(group, self._paramGersteinSurfaceParams)
	def _paramGetGersteinSurface(self, parts):
		return self._paramGet(parts, self._paramGersteinSurfaceParams)
	def _paramMakeGersteinVolume(self, group):
		return self._paramMake(group, self._paramGersteinVolumeParams)
	def _paramGetGersteinVolume(self, parts):
		return self._paramGet(parts, self._paramGersteinVolumeParams)

	def _paramMake(self, parent, params):
		g = Pmw.Group(parent, tag_text="Parameters")
		parts = []
		for label, cgiTag, items, default in params:
			m = Pmw.OptionMenu(g.interior(),
					labelpos="w",
					label_text=label,
					items=[ item[0] for item in items ])
			m.setvalue(default)
			m.pack(fill="x", expand=False)
			parts.append(m)
		Pmw.alignlabels(parts)
		return g, parts
	def _paramGet(self, parts, params):
		args = []
		for i, m in enumerate(parts):
			sel = m.getvalue()
			label, cgiTag, items, default = params[i]
			for name, value in items:
				if name == sel:
					args.append((cgiTag, None, value))
					break
			else:
				raise ChimeraError("unexpected option value")
		return args

	Servers = {
		"Surface Area (MSMS)":
			(	"msmsArea",
				StrucTools.msms,
				_paramMakeMsms,
				_paramGetMsms,
			),
		"Accessible Surface (Gerstein)":
			(	"accessibleSurface",
				StrucTools.surface,
				_paramMakeGersteinSurface,
				_paramGetGersteinSurface,
			),
		"Voronoi Volume (Gerstein)":
			(	"voronoiVolume",
				StrucTools.volume,
				_paramMakeGersteinVolume,
				_paramGetGersteinVolume,
			),
	}

_saveDialog = None
def _save(output, show):
	global _saveDialog
	if not _saveDialog:
		from OpenSave import SaveModeless
		_saveDialog = SaveModeless(
				title="Choose Surface Area/Volume Save File",
				command=_fileChosen,
				initialfile="output.html",
				historyID="Surface Area/Volume Output")
	else:
		_saveDialog.enter()
	_saveDialog._output = output
	_saveDialog._show = show

def _fileChosen(okayed, dialog):
	if okayed:
		paths = dialog.getPaths()
		if paths:
			filename = paths[0]
			from OpenSave import osOpen
			outFile = osOpen(filename, "w")
			outFile.write(dialog._output)
			outFile.close()
			if dialog._show:
				import urllib
				from chimera import help
				help.display(urllib.pathname2url(filename))
	delattr(dialog, "_output")
	delattr(dialog, "_show")
		
singleton = None

def run():
	global singleton
	if not singleton:
		singleton = Interface()
	singleton.enter()
