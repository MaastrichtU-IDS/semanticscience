# --- UCSF Chimera Copyright ---
# Copyright (c) 2000-2006 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: gui.py 26655 2009-01-07 22:02:30Z gregc $

import chimera
from chimera.baseDialog import ModelessDialog

from prefs import prefs, PRESETS

class AnisoDialog(ModelessDialog):
	title = "Thermal Ellipsoids"
	name = "anisotropic ellipsoids"
	buttons = ("Show Ellipsoids", "Hide Ellipsoids", "Close")
	help = "ContributedSoftware/thermal/thermal.html"

	builtinPresets = [
			("Simple ellipsoid", {}),
			("Principal axes", {"ellipsoid": False, "axisFactor": 1.0}),
			("Principal ellipses", {"ellipsoid": False, "ellipseFactor": 1.0}),
			("Ellipsoid and principal axes", {"axisFactor": 1.5}),
			("Octant lines",
				{"ellipseFactor": 1.01, "ellipseColor": (0,0,0,1)}),
			("Snow globe axes",
				{"ellipsoidColor": (1,1,1,1), "transparency": 50.0,
				"axisFactor": 0.99}),
			("Snow globe ellipses",
				{"ellipsoidColor": (1,1,1,1), "transparency": 50.0,
				"ellipseFactor": 0.99})
	]
	def fillInUI(self, parent):
		import Pmw, Tkinter
		top = parent.winfo_toplevel()
		menubar = Tkinter.Menu(top, type="menubar", tearoff=False)
		top.config(menu=menubar)

		self.presetsMenu = Tkinter.Menu(menubar)
		menubar.add_cascade(label="Presets", menu=self.presetsMenu)
		presets = self.builtinPresets + prefs[PRESETS]
		for label, kw in presets:
			self.presetsMenu.add_command(label=label,
								command=lambda kw=kw: self.preset(**kw))
		self.presetsMenu.add_separator()
		self.presetsMenu.add_command(label="Preset from current settings...",
								command=self.startDefinePreset)
		self.presetsMenu.add_command(label="Delete user preset...",
								command=self.startDeletePreset)
		from chimera.tkgui import aquaMenuBar
		row = aquaMenuBar(menubar, parent, row=0, columnspan=2)

		parent.columnconfigure(0, weight=1)
		parent.columnconfigure(1, weight=1)

		self._modFromCalc = False
		self.scaling = Pmw.EntryField(parent, labelpos='w', value='1',
			label_text="Scale factor:", entry_width=5,
			validate={'validator': 'real', 'min': 0.0},
			modifiedcommand=self._scaleTypingCB,
			command=self.ShowEllipsoids)
		self.scaling.grid(row=row, column=0)

		self.smoothing = Pmw.EntryField(parent, labelpos='w',
			label_text="Smoothing level:",
			validate={'validator': 'numeric', 'min': 1, 'max': 100},
			value='3', entry_width=2, command=self.ShowEllipsoids)
		self.smoothing.grid(row=row, column=1)
		row += 1

		self.calculator = Pmw.EntryField(parent, labelpos='w', label_text=
			"Set scale factor for probability (%):",
			entry_width=4, command=self._prob2scaling)
		self.calculator.grid(row=row, column=0, columnspan=2)
		row += 1

		from chimera.tkoptions import SymbolicEnumOption, \
										FloatOption, RGBAOption
		self.showEllipsoidVar = Tkinter.IntVar(parent)
		self.showEllipsoidVar.set(True)
		ellipsoidGroup = Pmw.Group(parent, tag_pyclass=Tkinter.Checkbutton,
			tag_text="Depict ellipsoids", tag_variable=self.showEllipsoidVar)
		ellipsoidGroup.grid(row=row, column=0, columnspan=2, sticky="ew")
		row += 1
		inside = ellipsoidGroup.interior()
		inside.columnconfigure(0, weight=1, uniform=1)
		inside.columnconfigure(1, weight=1, uniform=1)
		self.ellipsoidColorOpt = RGBAOption(inside, 0, 'Color', None, None,
			noneOkay=True, balloon='"No color" means use atom colors')
		class TransparencyOption(SymbolicEnumOption):
			values = [None, 0.0, 10.0, 20.0, 30.0, 40.0, 50.0,
						60.0, 70.0, 80.0, 90.0, 100.0]
			labels = ["same as color", "0%", "10%", "20%", "30%", "40%", "50%",
						"60%", "70%", "80%", "90%", "100%"]
		self.transparencyOpt = TransparencyOption(inside, 1,
										"Transparency", None, None)

		self.showAxesVar = Tkinter.IntVar(parent)
		self.showAxesVar.set(False)
		axesGroup = Pmw.Group(parent, tag_pyclass=Tkinter.Checkbutton,
			tag_text="Depict principal axes", tag_variable=self.showAxesVar)
		axesGroup.grid(row=row, column=0, columnspan=2, sticky="ew")
		row += 1
		inside = axesGroup.interior()
		inside.columnconfigure(0, weight=1, uniform=1)
		inside.columnconfigure(1, weight=1, uniform=1)
		self.axisColorOpt = RGBAOption(inside, 0, 'Color', None, None,
			noneOkay=True, balloon='"No color" means use atom colors')
		self.axisFactorOpt = FloatOption(inside, 1, "Length factor", 1.5,
			self.ShowEllipsoids, balloon="relative to ellipsoids", sticky="w")
		self.axisThicknessOpt = FloatOption(inside, 2, "Thickness",
										0.01, self.ShowEllipsoids, sticky="w")

		self.showEllipsesVar = Tkinter.IntVar(parent)
		self.showEllipsesVar.set(False)
		ellipsesGroup = Pmw.Group(parent, tag_pyclass=Tkinter.Checkbutton,
			tag_text="Depict principal ellipses",
			tag_variable=self.showEllipsesVar)
		ellipsesGroup.grid(row=row, column=0, columnspan=2, sticky="ew")
		row += 1
		inside = ellipsesGroup.interior()
		inside.columnconfigure(0, weight=1, uniform=1)
		inside.columnconfigure(1, weight=1, uniform=1)
		self.ellipseColorOpt = RGBAOption(inside, 0, 'Color', None, None,
			noneOkay=True, balloon='"No color" means use atom colors')
		self.ellipseFactorOpt = FloatOption(inside, 1, "Size factor", 1.0,
			self.ShowEllipsoids, balloon="relative to ellipsoids", sticky="w")
		self.ellipseThicknessOpt = FloatOption(inside, 2, "Thickness",
										0.02, self.ShowEllipsoids, sticky="w")

		self.selRestrictVar = Tkinter.IntVar(parent)
		self.selRestrictVar.set(False)
		Tkinter.Checkbutton(parent, text="Restrict Show/Hide to current"
			" selection, if any", variable=self.selRestrictVar).grid(
			row=row, column=0, columnspan=2)
		row += 1

	def ShowEllipsoids(self, *args):
		if self.showAxesVar.get():
			axisFactor = self.axisFactorOpt.get()
		else:
			axisFactor = None
		if self.showEllipsesVar.get():
			ellipseFactor = self.ellipseFactorOpt.get()
		else:
			ellipseFactor = None
		kw = {'color': self.ellipsoidColorOpt.get(),
			'smoothing': int(self.smoothing.getvalue()),
			'scale': float(self.scaling.getvalue()),
			'showEllipsoid': self.showEllipsoidVar.get(),
			'transparency': self.transparencyOpt.get(),
			'axisFactor': axisFactor,
			'axisColor': self.axisColorOpt.get(),
			'axisThickness': self.axisThicknessOpt.get(),
			'ellipseFactor': ellipseFactor,
			'ellipseColor': self.ellipseColorOpt.get(),
			'ellipseThickness': self.ellipseThicknessOpt.get()}
		if self.selRestrictVar.get():
			from chimera.selection import currentAtoms
			selAtoms = currentAtoms()
			if selAtoms:
				kw['targets'] = selAtoms
		from Aniso import aniso
		from Midas import MidasError
		try:
			aniso(**kw)
		except MidasError:
			from chimera import UserError
			raise UserError("No atoms chosen had anisotropic"
				" information")

	def HideEllipsoids(self):
		kw = {}
		if self.selRestrictVar.get():
			from chimera.selection import currentAtoms
			selAtoms = currentAtoms()
			if selAtoms:
				kw['targets'] = selAtoms
		from Aniso import unaniso
		unaniso(**kw)

	def preset(self, ellipsoid=True, ellipsoidColor=None, transparency=None,
				axisFactor=None, axisColor=None, axisThickness=0.01,
				ellipseFactor=None, ellipseColor=None, ellipseThickness=0.02):
		self.showEllipsoidVar.set(ellipsoid)
		if ellipsoid:
			self.ellipsoidColorOpt.set(ellipsoidColor)
			self.transparencyOpt.set(transparency)
		if axisFactor:
			self.showAxesVar.set(True)
			self.axisFactorOpt.set(axisFactor)
			self.axisColorOpt.set(axisColor)
			self.axisThicknessOpt.set(axisThickness)
		else:
			self.showAxesVar.set(False)
		if ellipseFactor:
			self.showEllipsesVar.set(True)
			self.ellipseFactorOpt.set(ellipseFactor)
			self.ellipseColorOpt.set(ellipseColor)
			self.ellipseThicknessOpt.set(ellipseThickness)
		else:
			self.showEllipsesVar.set(False)
		self.ShowEllipsoids()
			
	def startDefinePreset(self):
		if not hasattr(self, "_presetNameDialog"):
			import Pmw
			self._presetNameDialog = Pmw.PromptDialog(self.uiMaster(),
				title="Preset Name", label_text="Preset name:",
				entryfield_labelpos='w', defaultbutton=0,
				buttons=('OK', 'Cancel'), command=self._definePresetCB)
		self._presetNameDialog.show()

	def startDeletePreset(self):
		if not prefs[PRESETS]:
			from chimera import UserError
			raise UserError("No user presets have been defined")
		if not hasattr(self, "_presetDeleteDialog"):
			import Pmw
			self._presetDeleteDialog = Pmw.SelectionDialog(self.uiMaster(),
				title="Delete Preset", label_text="Preset name:",
				scrolledlist_labelpos='n', defaultbutton=0,
				scrolledlist_items=[ps[0] for ps in prefs[PRESETS]],
				buttons=('OK', 'Cancel'), command=self._deletePresetCB)
		self._presetDeleteDialog.show()

	def _definePresetCB(self, button):
		self._presetNameDialog.withdraw()
		if button is None or button == 'Cancel':
			return
		name = self._presetNameDialog.get().strip()
		if not name:
			self._presetNameDialog.show()
			from chimera import UserError
			UserError("Must provide preset name")
		if name in [x[0] for x in self.builtinPresets]:
			self._presetNameDialog.show()
			from chimera import UserError
			UserError("Cannot redefine builtin preset")
		
		anisoKw = {}
		anisoKw['ellipsoid'] = self.showEllipsoidVar.get()
		if anisoKw['ellipsoid']:
			anisoKw['ellipsoidColor'] = self.ellipsoidColorOpt.get()
			anisoKw['transparency'] = self.transparencyOpt.get()
		if self.showAxesVar.get():
			anisoKw['axisFactor'] = self.axisFactorOpt.get()
			anisoKw['axisColor'] = self.axisColorOpt.get()
			anisoKw['axisThickness'] = self.axisThicknessOpt.get()
		if self.showEllipsesVar.get():
			anisoKw['ellipseFactor'] = self.ellipseFactorOpt.get()
			anisoKw['ellipseColor'] = self.ellipseColorOpt.get()
			anisoKw['ellipseThickness'] = self.ellipseThicknessOpt.get()

		newPreset = (name, anisoKw)
		customPresets = prefs[PRESETS][:]
		for info in customPresets:
			if info[0] == name:
				# changing _contents_ of kw dictionary means we don't
				# have to redefine the menu command action
				info[1].clear()
				info[1].update(anisoKw)
				break
		else:
			customPresets.append(newPreset)
			self.presetsMenu.insert_command(len(self.builtinPresets)
				+ len(customPresets), label=name,
				command=lambda kw=anisoKw: self.preset(**kw))
		prefs[PRESETS] = customPresets

	def _deletePresetCB(self, result):
		self._presetDeleteDialog.withdraw()
		if result is None or result == 'Cancel':
			self._presetDeleteDialog.destroy()
			delattr(self, '_presetDeleteDialog')
			return
		deletions = self._presetDeleteDialog.getvalue()
		remaining = [ps for ps in prefs[PRESETS] if ps[0] not in deletions]
		prefs[PRESETS] = remaining
		for name in deletions:
			self.presetsMenu.delete(name)
		self._presetDeleteDialog.destroy()
		delattr(self, '_presetDeleteDialog')

	def _prob2scaling(self):
		try:
			prob = float(self.calculator.getvalue()) / 100.0
			if prob < 0.0 or prob >= 1.0:
				raise ValueError("bad prob")
		except ValueError:
			from chimera import UserError
			raise UserError("Probability must be >= 0 and < 100")
		from Aniso import prob2scale
		self._modFromCalc = True
		self.scaling.setvalue("%g" % prob2scale(prob))
		self._modFromCalc = False

	def _scaleTypingCB(self):
		if not self._modFromCalc:
			self.calculator.setvalue("")

from chimera import dialogs
dialogs.register(AnisoDialog.name, AnisoDialog)
