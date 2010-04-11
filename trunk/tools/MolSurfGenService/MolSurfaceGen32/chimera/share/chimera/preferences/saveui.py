import Tkinter, Pmw

class SaveUI:

	def __init__(self, frame, client):
		self.client = client
		self.presetItems = []
		self.userItems = []
		self.currentItem = None
		self.itemChanged = False
		self.nameChanged = False
		self.frame = frame
		l = client.saveui_label()
		if l:
			tag_text = l
		else:
			tag_text = None
		g = Pmw.Group(frame, tag_text=tag_text)
		g.pack(fill=Tkinter.BOTH)
		inside = g.interior()
		kw = {
			"selectioncommand": self._selectCB,
			"history": 0,
			"dropdown": 1,
			"entryfield_command": self._entryCB,
			"entryfield_modifiedcommand": self._nameChangeCB,
		}
		self.combo = Pmw.ComboBox(inside, **kw)
		self.combo.pack(side=Tkinter.TOP, fill=Tkinter.X)
		self.entryfield = self.combo.component("entryfield")
		self.buttons = Pmw.ButtonBox(inside, padx=0, pady=0)
		self.buttons.pack(side=Tkinter.TOP, fill=Tkinter.X)
		pad = 0
		from chimera import tkgui
		if tkgui.windowSystem == 'aqua':
			pad = None	# Avoid clipping Save As... button text
		self.saveButton = self.buttons.add("Save", padx=pad,
							command=self._saveCB)
		self.saveAsButton = self.buttons.add("Save As...", padx=pad,
							command=self._saveAsCB)
		self.deleteButton = self.buttons.add("Delete", padx=pad,
							command=self._deleteCB)
		self.saveButton.config(default="disabled")
		self.saveAsButton.config(default="disabled")
		self.deleteButton.config(default="disabled")
		self.buttons.alignbuttons()
		try:
			if not callable(client.saveui_setDefaultItem):
				# Not callable == not present
				raise AttribueError
			self.startup = Pmw.OptionMenu(inside,
						labelpos="w",
						label_text="start-up setting",
						command=self._setDefaultCB)
			self.startup.pack(side=Tkinter.TOP, fill=Tkinter.X)
		except AttributeError:
			self.startup = None
		try:
			self.currentItem = self.client.saveui_defaultItem()
			self.defaultItem = self.currentItem
		except AttributeError:
			self.currentItem = None
			self.defaultItem = None
		self.updateComboList(True)

	def updateComboList(self, selectCurrent=True):
		self.presetItems = self.client.saveui_presetItems()
		self.userItems = self.client.saveui_userItems()
		l = self.presetItems + self.userItems
		l.sort()
		self.combo.setlist(l)
		if selectCurrent:
			if self.currentItem:
				self.entryfield.setvalue(self.currentItem)
			else:
				self.entryfield.setvalue("")
		self.updateState()
		if self.startup:
			self.startup.setitems(l, index=self.defaultItem)

	def updateState(self):
		name = self.entryfield.getvalue().strip()
		if self._canSave(name):
			saveState = Tkinter.NORMAL
		else:
			saveState = Tkinter.DISABLED
		if name in self.userItems:
			deleteState = Tkinter.NORMAL
		else:
			deleteState = Tkinter.DISABLED
		self.saveButton.config(state=saveState)
		self.deleteButton.config(state=deleteState)

	def setItemChanged(self, changed):
		self.itemChanged = changed
		self.updateState()

	def saveAs(self, name, confirm=True):
		if not name:
			from chimera import replyobj
			replyobj.error("Please enter a non-empty name")
			return
		if name in self.presetItems:
			from chimera import replyobj
			replyobj.error("\"%s\" is a preset name" % name)
			return
		elif confirm and name in self.userItems:
			if not self._confirmReplace(name):
				return
		selectCurrent = True
		if self.client.saveui_save(name) is None:
			selectCurrent = False
		else:
			self.nameChanged = False
			self.setItemChanged(False)
			self.currentItem = name
		self.updateComboList(selectCurrent)

	def _confirmReplace(self, name):
		type = self.client.saveui_label()
		d = ReplaceDialog(name, type, master=self.frame)
		return d.run(self.frame)

	def _entryCB(self):
		self._selectCB(self.entryfield.getvalue().strip())

	def _nameChangeCB(self):
		self.nameChanged = True
		self.updateState()

	def _selectCB(self, item):
		if item not in self.userItems and item not in self.presetItems:
			return
		self.client.saveui_select(item)
		self.currentItem = item
		self.nameChanged = False
		self.setItemChanged(False)

	def _saveCB(self):
		name = self.entryfield.getvalue().strip()
		if name != self.currentItem:
			self.saveAs(name)
		else:
			selectCurrent = True
			if self.client.saveui_save(name) is None:
				selectCurrent = False
			else:
				self.nameChanged = False
				self.setItemChanged(False)
				self.currentItem = name
			self.updateComboList(selectCurrent)

	def _saveAsCB(self):
		label = self.client.saveui_label()
		title = "Save %s As..." % label
		items = self.presetItems + self.userItems
		items.sort()
		d = SaveAsDialog(self.frame, title, label, items, self.saveAs)
		d.enter()

	def _deleteCB(self):
		name = self.entryfield.getvalue().strip()
		selectCurrent = True
		if self.client.saveui_delete(name) is None:
			selectCurrent = False
		else:
			self.currentItem = ""
			if name == self.defaultItem:
				self.defaultItem = self.client.saveui_defaultItem()
		self.updateComboList(selectCurrent)

	def _setDefaultCB(self, name):
		if self.client.saveui_setDefaultItem(name) is None:
			return
		self.defaultItem = name
		self.startup.setvalue(name)

	def _canSave(self, name):
		if name and name not in self.presetItems:
			return True
		else:
			return False

from chimera.baseDialog import ModelessDialog
class SaveAsDialog(ModelessDialog):
	buttons = ("OK", "Cancel")
	default = "OK"
	oneshot = 1

	def __init__(self, master, title, label, items, cb):
		self.title = title
		self.label = label
		self.items = items
		self.callback = cb
		ModelessDialog.__init__(self, master=master)

	def fillInUI(self, parent):
		kw = {
			"dropdown": 1,
			"history": 0,
		}
		if self.label:
			kw["label_text"] = self.label
			kw["labelpos"] = "w"
		self.combo = Pmw.ComboBox(parent, **kw)
		self.combo.setlist(self.items)
		self.combo.pack(fill=Tkinter.X)
		self.entryfield = self.combo.component("entryfield")

	def enter(self):
		ModelessDialog.enter(self)
		self.entryfield.component("entry").focus_set()

	def Apply(self):
		self.callback(self.entryfield.getvalue().strip())
		ModelessDialog.Apply(self)

from chimera.baseDialog import ModalDialog
class ReplaceDialog(ModalDialog):
	buttons = ("Replace", "Cancel")
	default = "Replace"
	oneshot = 1

	def __init__(self, name, type, **kw):
		self.itemName = name
		self.itemType = type
		ModalDialog.__init__(self, **kw)

	def fillInUI(self, parent):
		l = Tkinter.Label(parent, text="%s \"%s\" already exists.\n"
					"Do you want to replace it?"
					% (self.itemType, self.itemName))
		l.pack()

	def Replace(self):
		self.Cancel(1)

class Test:

	def __init__(self):
		self.app = Tkinter.Toplevel()
		self.app.wm_title("Hello")
		self.saveui = SaveUI(self.app, self)

	def run(self):
		self.app.mainloop()

	def saveui_label(self):
		return "Test"

	def saveui_presetItems(self):
		return [ "Defaults" ]

	def saveui_userItems(self):
		return [ "Hello", "xyzzy", "plugh" ]

	def saveui_defaultItem(self):
		return "Defaults"

	def saveui_select(self, name):
		print "Test.saveui_select", name

	def saveui_save(self, name):
		print "Test.saveui_save", name
		return 1		# Successful save

	def saveui_delete(self, name):
		print "Test.saveui_delete", name
		return 1		# Successful delete

def test():
	Test().run()
