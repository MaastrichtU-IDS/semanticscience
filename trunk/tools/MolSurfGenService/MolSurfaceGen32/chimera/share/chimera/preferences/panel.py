import Tkinter
import Pmw

from chimera.baseDialog import ModelessDialog
from chimera import help, replyobj

class PreferencesPanel(ModelessDialog):
	"Create preferences dialog."
	name = "preferences"
	title = "Preferences"
	buttons = ("Reset", "Restore", "Save", "Close",)
	help = "UsersGuide/preferences.html"
	provideStatus  = True
	statusPosition = "above"

	def __init__(self, pref, master=None, *args, **kw):
		self._pref = pref
		apply(ModelessDialog.__init__, (self, master) + args, kw)
		help.register(self.buttonWidgets["Save"],
				balloon="Save category")
		help.register(self.buttonWidgets["Restore"],
				balloon="Restore category to saved defaults")
		help.register(self.buttonWidgets["Reset"],
				balloon="Reset category to factory defaults")

	def fillInUI(self, master):
		"Fill in user interface."

		self.curUI = None
		self.frame = Tkinter.Frame(master)
		self.frame.pack(expand=Tkinter.TRUE, fill=Tkinter.BOTH)
		f = Tkinter.Frame(self.frame)
		f.pack(side=Tkinter.TOP, fill=Tkinter.X)
		self.menu = Pmw.OptionMenu(f, labelpos=Tkinter.W,
						label_text='Category:',
						command=self.setCategory,
						items=['empty'])
		self.menu.pack(side=Tkinter.LEFT)
	
		hr = Tkinter.Frame(self.frame, relief=Tkinter.GROOVE,
						borderwidth=1, height=2)
		hr.pack(side=Tkinter.TOP, fill=Tkinter.X, pady=1)

		self.categoriesChanged()
		if 'General' in self._pref.categories():
			self.menu.invoke(index='General')
		else:
			self.setCategory(self.menu.getcurselection())
		self._pref.setUIPanel(self)

	def setCategory(self, category):
		"Set currently displayed category."

		# don't constrain to user's last resize
		self.frame.winfo_toplevel().geometry("")

		if self.curUI:
			self.curUI.forget()
			self.curUI = None
		try:
			ui = self._pref.ui(category, master=self.frame)
		except KeyError:
			return
		ui.pack(side=Tkinter.BOTTOM, expand=Tkinter.TRUE,
				fill=Tkinter.BOTH)
		self.curUI = ui

		self.status("")

	def setCategoryMenu(self, category):
		"""Set currently displayed menu category
		
		This invokes the menu callback and sets the category as well.
		"""

		self.menu.invoke(index=category)

	def categoriesChanged(self):
		"Called by Preferences when list of categories changes."

		cList = self._pref.categories()
		cList.sort()
		self.menu.setitems(cList)
		for category in cList:
			ui = self._pref.ui(category, self.frame)
			if not ui:
				continue
			help.register(ui,
				"UsersGuide/preferences.html#%s" % category)

	def Reset(self):
		category = self.menu.getvalue()
		self._pref.resetValues(category)
		self.status("Category '%s' has been reset" % category, color="blue", blankAfter=10)

	def Restore(self):
		category = self.menu.getvalue()
		self._pref.restoreValues(category)
		self.status("Category '%s' has been restored" % category, color="blue", blankAfter=10)

	def Save(self):
		category = self.menu.getvalue()
		if self._pref.isReadonly():
			from chimera import UserError
			raise UserError("Preference file \"%s\" is read-only."
					% self._pref.filename())
		self._pref.makeCurrentSaved(category)
		self._pref.save()
		self.status("Category '%s' has been saved" % category, color="blue", blankAfter=10)

	
	def Help(self):
		# implement our own help, since we want different
		# URLs depending on the current preferences category
		nameTag = self.menu.getcurselection()
		help.display("UsersGuide/preferences.html#%s" % nameTag)

	def ResetAll(self):
		for category in self._pref.categories():
			self._pref.resetValues(category)
		self.status("All categories have been reset to defaults", color="blue", blankAfter=10)

	def RestoreAll(self):
		for category in self._pref.categories():
			self._pref.restoreValues(category)
		self.status("All categories have been restored to last save", color="blue", blankAfter=10)	

	def SaveAll(self):
		if self._pref.isReadonly():
			from chimera import UserError
			raise UserError("Preference file \"%s\" is read-only."
					% self._pref.filename())
		for category in self._pref.categories():
			self._pref.makeCurrentSaved(category)
		self._pref.save()
		self.status("All categories have been saved", color="blue", blankAfter=10)
