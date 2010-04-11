# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: WriteSelDialog.py 28076 2009-07-13 21:42:53Z pett $

from OpenSave import SaveModeless
import Tkinter
import Pmw
import chimera

classes = [chimera.Atom, chimera.Bond, chimera.PseudoBond,
			chimera.Residue, chimera.Molecule, chimera.Model]

class WriteSelDialog(SaveModeless):
	name = "write selection"
	title = "Write Current Selection"
	keepShown = SaveModeless.default
	extraButtons = ("Log",)
	help = "UsersGuide/menu.html#writespec"

	PREF_NAMING = "naming scheme"

	def __init__(self):
		import preferences
		options = { self.PREF_NAMING: "simple" }
		self.prefs = preferences.addCategory("write selection dialog",
			preferences.HiddenCategory, optDict=options)
		SaveModeless.__init__(self, clientPos='s')

	def fillInUI(self, parent):
		SaveModeless.fillInUI(self, parent)

		self.selUnsel = Pmw.OptionMenu(self.clientArea, items=[
			"selected", "unselected"], labelpos='w', label_text=
			"Write")
		self.selUnsel.grid(row=0, column=0, sticky='e')
		self.classMenu = Pmw.OptionMenu(self.clientArea, items=
			map(lambda c: c.__name__.lower() + "s", classes))
		self.classMenu.grid(row=0, column=1, sticky='w')

		from tkoptions import NamingStyleOption
		if self.prefs[self.PREF_NAMING] in NamingStyleOption.values:
			default = self.prefs[self.PREF_NAMING]
		else:
			default = None
		self.naming = NamingStyleOption(self.clientArea, 1, None,
							default, None)

	def configure(self, klass=None, selected=None):
		if klass is not None and klass in classes:
			self.classMenu.invoke(classes.index(klass))
		if selected is not None:
			if selected:
				self.selUnsel.setvalue("selected")
			else:
				self.selUnsel.setvalue("unselected")

	def Apply(self):
		self._writeSel(self.getPaths()[0])

	def Log(self):
		self.Close()
		self._writeSel("-")
		dialogs.display("reply")

	def _writeSel(self, destination):
		naming = self.naming.get()
		self.prefs[self.PREF_NAMING] = naming

		selected = self.selUnsel.getvalue() == "selected"

		from writeSel import writeSel
		writeSel(destination, namingStyle=naming, selected=selected,
					itemType=classes[self.classMenu.index(
					Pmw.SELECT)].__name__)

import dialogs
dialogs.register(WriteSelDialog.name, WriteSelDialog)
