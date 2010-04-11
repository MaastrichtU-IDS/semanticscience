# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: base.py 26655 2009-01-07 22:02:30Z gregc $

import sys
import os.path
import Tkinter
import tkMessageBox
import Tix

import chimera
from chimera import preferences, help
from CGLtk.OrderedListOption import OrderedListOption
from TixScrolledGrid import ScrolledGrid
from TextIcon import TextIcon

class EMO:
	"""EMO stands for Extension Management Object

	This class defines the protocol used by the Extension Manager to
	communicate with tools and should be the base class for all
	package tools.

	Extension names are assumed to be unique and may present in more
	than one category.
	"""

	def __init__(self, path):
		self.__path = os.path.dirname(path)
		self.__pkgName = os.path.basename(self.__path)
		self.toolbarButton = None

	def name(self):
		"Return unique display name for this tool"
		return "ExtensionManagementObject%d" % id(self)

	def icon(self):
		"Return image or file/URL to represent tool"
		return TextIcon(chimera.tkgui.app.toolbar, self.name(),
				compress=1)

	def categories(self):
		"Return list of category names in which this tool belongs"
		return []

	def description(self):
		"Return short description (appropriate for balloon help)"
		return "Base class for package tools"

	def categoryDescriptions(self):
		"""Return a dictionary of categories and descriptions.

		When available, this method will be used in preference
		to "categories".  Descriptions from this dictionary will
		be used for balloon help text in the Tools menu (but tool
		bar help will always be from "description" method). """
		raise AttributeError

	def documentation(self):
		"Return full documention URL"
		return None

	def hasUI(self):
		"Return whether tool activation starts a UI"
		return 1

	def activate(self):
		"Activate tool and return an instance (if appropriate)"
		print "Activate", self.name()

	def menuActivate(self, cat):
		"Activate tool from menu"
		if manager.confirmStart(cat, self):
			from chimera.baseDialog import ModalDialog
			class ynDialog(ModalDialog):
				buttons = ('Yes', 'No')
				default = 'Yes'
				title = "Invoke Tool"
				def fillInUI(self, parent, name=self.name()):
					Tkinter.Label(parent, text=
						'Invoke Tool "%s"?' % name
						).grid()
				def Yes(self):
					self.Cancel(True)
				def No(self):
					self.Cancel(False)
			if not ynDialog().run(chimera.tkgui.app.graphics):
				return None
		self.activate()

	def packageName(self):
		"Return the name of the package that this EMO came from"

		return self.__pkgName

	def path(self, file=None):
		"Return the path to a file in the package"

		if not file:
			return self.__path
		else:
			return os.path.join(self.__path, file)

	def module(self, modName=None):
		"Return a module in the package (empty name -> package itself)"

		if not modName:
			fullName = self.__pkgName
		else:
			fullName = "%s.%s" % (self.__pkgName, modName)
		mod = __import__(fullName)
		if modName:
			components = modName.split('.')
			for comp in components:
				mod = getattr(mod, comp)
			return mod
		return mod

	def saveSession(self):
		"Save tool as session XML object"
		return None

	def restoreSession(self, xmlObj):
		"Restore tool from session XML object"
		pass

	def showOnToolbar(self):
		if self.toolbarButton:
			return
		icon = self.icon()
		if not icon:
			icon = EMO.icon(self)
		self.toolbarButton = chimera.tkgui.app.toolbar.add(icon,
					self.activate, self.description())

	def removeFromToolbar(self):
		if not self.toolbarButton:
			return
		chimera.tkgui.app.toolbar.remove(self.toolbarButton)
		self.toolbarButton = None


class Category:

	def __init__(self, name):
		self._name = name
		self._entryList = []

	def name(self):
		return self._name

	def entries(self):
		return self._entryList

	def addEntry(self, emo):
		self._entryList.append(emo)

	def sortedEntries(self):
		order = self._getSortOrder()
		l = []
		for emo in self._entryList:
			name = emo.name()
			try:
				index = order.index(name)
			except ValueError:
				index = -1
			l.append((index, name, emo))
		l.sort()
		return [ item[2] for item in l ]

	def _getSortOrder(self):
		from SortOrder import ToolOrder
		return ToolOrder.get(self._name, [])


class ExtensionKey:

	def __init__(self, rawKey):
		self.extName = rawKey

	def matches(self, emo):
		if self.extName != emo.name():
			return False
		return True

	def prefKey(self):
		return self.extName

extensionKeyCache = {}
def makeExtensionKey(rawKey):
	try:
		return extensionKeyCache[rawKey]
	except KeyError:
		key = ExtensionKey(rawKey)
		extensionKeyCache[key.prefKey()] = key
		return key


class Manager:
	"""Manager singleton keeps track of available tools"""

	Suffixes = [ ".pyc", ".py", ".pyo" ]

	def __init__(self, *args, **kw):
		"Initialize manager with no tools"

		self.categories = {}
		self.categoryChanged = {}
		self.newCategoryAdded = 0
		self.settingsMap = {}
		self.settingsCount = 0
		self.directories = []
		self.autoStart = {}
		self.onToolbar = {}
		import StdTools
		self.inFavorites = StdTools.StdFavorites.copy()
		self.confirmOnStart = {}

		self.menu = None		# Tools menu
		self.favorites = None		# Favorites Menu
		self.instanceEntry = None
		self.instances = []
		self.instMenu = {}
		self.catMenu = {}
		self.settingsGrid = None
		self.settingsButtons = {}
		self.dirList = None

		self.AUTO_START = 1
		self.ON_TOOLBAR = 2
		self.IN_FAVORITES = 3
		self.CONFIRM_ON_START = 4
		self.settings = {
			# Key is column number
			# Value is (label, display, callback) tuple
			# Column 0 is reserved for tool names
			self.AUTO_START: ( "Auto Start",
						self._setAutoStart,
						self._autoStart ),
			self.ON_TOOLBAR: ( "On Toolbar",
						self._setOnToolbar,
						self._onToolbar ),
			self.IN_FAVORITES: ( "In Favorites",
						self._setInFavorites,
						self._inFavorites ),
			self.CONFIRM_ON_START: ( "Confirm on Start",
						self._setConfirmOnStart,
						self._confirmOnStart ),
		}

	def findCategory(self, catName):
		return self.categories[catName]

	def addCategory(self, cat):
		self.categories[cat.name()] = cat

	def sortedCategories(self):
		l = []
		order = self._getSortOrder()
		for name, cat in self.categories.iteritems():
			try:
				index = order.index(name)
			except ValueError:
				index = -1
			l.append((index, name, cat))
		l.sort()
		return [ item[2] for item in l ]

	def _getSortOrder(self):
		from SortOrder import CategoryOrder
		return CategoryOrder

	def addDirectory(self, path, savePreferences=False):
		"Add a directory to preferences and load extension from it"

		if path not in self.directories:
			self.directories.append(path)
			if self.loadDirectory(path) and self.settingsGrid:
				self.remakeSettings()
			if savePreferences:
				preferences.makeCurrentSaved("Tools")
				preferences.save()
		else:
			from chimera import replyobj
			replyobj.error("Tools directory \"%s\" "
					"already loaded\n" % path)

	def loadDirectory(self, path, basename="Chimera"):
		"Search a path for package Python tools"

		from chimera.misc import stringToAttr
		if path not in sys.path:
			sys.path.append(path)
		self.categoryChanged = {}
		self.newCategoryAdded = 0
		module = basename + "Extension"
		try:
			files = os.listdir(path)
		except OSError:
			from chimera import replyobj
			replyobj.warning("Cannot load tools directory "
						"\"%s\"\n" % path)
			return 0
		for f in os.listdir(path):
			if stringToAttr(f) != f:
				# Skip anything that isn't a legal Python
				# identifier since it can't be used for
				# imports anyway
				continue
			emoPath = os.path.join(path, f, module)
			for s in self.Suffixes:
				if os.path.isfile(emoPath + s):
					break
			else:
				# No ChimeraExtension.py*
				continue
			if self.findExtensionPackage(f):
				from chimera import replyobj
				replyobj.warning("Package \"%s\" "
					"already exists and tool(s) in "
					"it will not be loaded\n" % f)
				continue
			self._importExtension(path, f, module)
		if self.menu:
			if self.newCategoryAdded:
				self.remakeToolsMenu()
			elif self.categoryChanged:
				for cat in self.categoryChanged.iterkeys():
					self.remakeCategoryMenu(cat)
		return self.categoryChanged or self.newCategoryAdded

	def _importExtension(self, path, pkgName, module):
		"""Import tool at given path
		
		Import process should cause tool to register
		itself via registerExtension"""

		sys.path.insert(0, os.path.join(path, pkgName))
		try:
			try:
				# When "module" is imported, it should register
				# itself.  Then we delete the module from
				# sys.modules so that the same name may be
				# used when importing another tool.
				try:
					__import__(module)
				except ImportError:
					pass
				try:
					del sys.modules[module]
				except KeyError:
					pass
			finally:
				del sys.path[0]
		except:
			# need to give some indication of what module the
			# error is occuring in, so prepend info to error
			from chimera import replyobj
			import traceback
			replyobj.pushMode(replyobj.ERROR)
			replyobj.message("Error while importing %s from %s:\n"
							% (pkgName, path))
			s = apply(traceback.format_exception,
					sys.exc_info())
			replyobj.message(''.join(s))
			replyobj.popMode()

	def updateDirectories(self, dirList):
		self.directories = dirList

	def registerExtension(self, emo):
		"Add tool into categories in manager"

		try:
			cList = emo.categoryDescriptions().iterkeys()
		except AttributeError:
			cList = emo.categories()
		for c in cList:
			self.addExtension(c, emo)

	def addExtension(self, catName, emo):
		"Add a tool into a single category"

		try:
			cat = self.findCategory(catName)
			self.categoryChanged[cat] = 1
		except KeyError:
			self.newCategoryAdded = 1
			cat = Category(catName)
			self.addCategory(cat)
		cat.addEntry(emo)

	def findExtensionPackage(self, name, catName=None):
		"Find a tool by package name"

		if catName:
			try:
				cat = self.findCategory(catName)
				return self._findPackage(name)
			except KeyError:
				return None
		else:
			for cat in self.categories.itervalues():
				ext = self._findPackage(cat, name)
				if ext:
					return ext
		return None

	def _findPackage(self, cat, name):
		for e in cat.entries():
			if e.packageName() == name:
				return e
		return None

	def registerInstance(self, inst):
		"Register an instance of a tool"

		if inst in self.instances:
			return
		self.instances.append(inst)
		self.remakeInstanceMenu()

	def deregisterInstance(self, inst):
		"Deregister an instance of a tool"

		try:
			self.instances.remove(inst)
		except ValueError:
			return
		self.remakeInstanceMenu()

	def createMenu(self):
		"Create Tools and Favorites menu items on menu bar"

		from chimera import help
		from chimera.tkgui import app, MENU_TOOLS, MENU_FAVORITES
		from CGLtk.MenuBalloon import MenuBalloon
		menu = Tkinter.Menu(app.menubar, title="Tools")
		balloon = MenuBalloon(menu)
		app.menubar.entryconfigure(MENU_TOOLS, menu=menu)
		help.register(menu, "UsersGuide/menu.html#menutools")
		favorites = Tkinter.Menu(app.menubar, title="Favorites")
		app.menubar.entryconfigure(MENU_FAVORITES, menu=favorites)
		help.register(menu, "UsersGuide/menu.html#menufavorites")
		from chimera.tkgui import updateAquaMenuBar
		updateAquaMenuBar(app.menubar)

		self.menu = menu
		self.menuBalloon = balloon
		self.remakeToolsMenu()
		self.favorites = favorites
		self.remakeFavorites()

	def remakeToolsMenu(self):
		self.menuBalloon.clear()
		self.menu.delete(0, Tkinter.END)
		for menu in self.catMenu.itervalues():
			menu.destroy()
		self.catMenu = {}
		for menu in self.instMenu.itervalues():
			menu.destroy()
		self.instMenu = {}
		self.instanceEntry = None
		for cat in self.sortedCategories():
			menu = Tkinter.Menu(self.menu, title=cat.name())
			self.catMenu[cat.name()] = menu
			self.menu.add_cascade(label=cat.name(), menu=menu)
			self.remakeCategoryMenu(cat)

	def remakeCategoryMenu(self, cat):
		menu = self.catMenu[cat.name()]
		menu.delete(0, Tkinter.END)
		for e in cat.sortedEntries():
			def activate(e=e, cat=cat):
				e.menuActivate(cat)
			menu.add_command(label=e.name(), command=activate)
			try:
				desc = e.categoryDescriptions()[cat.name()]
			except AttributeError:
				desc = e.description()
			self.menuBalloon.bind([ cat.name(), e.name() ], desc)

	def remakeInstanceMenu(self):
		if self.instanceEntry:
			self.menu.delete(self.instanceEntry, Tkinter.END)
			for menu in self.instMenu.itervalues():
				menu.destroy()
			self.instMenu = {}
			self.instanceEntry = None
		if not self.instances:
			return
		self.menu.add_separator()
		self.instanceEntry = self.menu.index(Tkinter.END)
		for inst in self.instances:
			try:
				name = inst.emName()
			except:
				name = inst.__class__.__name__
			if len(name) > 20:
				name = "%s..." % name[:20]
			self.menu.add_cascade(label=name)
			index = self.menu.index(Tkinter.END)
			menu = Tkinter.Menu(self.menu, title=name)
			for f in ["Raise", "Hide", "Quit"]:
				try:
					method = getattr(inst, "em" + f)
					if not callable(method):
						method = None
				except AttributeError:
					method = None
				if method:
					menu.add_command(label=f,
							command=method)
				else:
					menu.add_command(label=f,
							state=Tkinter.DISABLED)
			self.menu.entryconfigure(index, menu=menu)
			self.instMenu[inst] = menu

	def remakeFavorites(self):
		from chimera import dialogs
		m = self.favorites
		if not m:
			return
		m.delete(0, Tkinter.END)
		toolList = []
		alreadyFound = set([])
		for cat in self.categories.itervalues():
			for emo in cat.entries(): 
				key = makeExtensionKey(emo.name())
				if self.inFavorites.has_key(key):
					if key in alreadyFound:
						continue
					toolList.append((self.inFavorites[key],
							emo))
					alreadyFound.add(key)
		toolList.sort()
		for order, emo in toolList:
			def activate(e=emo, cat=cat):
				e.menuActivate(cat)
			m.add_command(label=emo.name(), command=activate)
		m.add_separator()
		m.add_command(label="Add to Favorites/Toolbar...", underline=0,
			command=self.showToolPreferences)
		m.add_command(label="Preferences...", underline=0,
			command=lambda f=dialogs.display: f("preferences"))

	def showToolPreferences(self):
		from chimera import dialogs
		d = dialogs.display("preferences")
		d.setCategoryMenu("Tools")

	def createUI(self, master):
		import Pmw
		w = Pmw.Group(master, tag_text="Settings")
		w.pack(side=Tkinter.TOP, expand=Tkinter.TRUE, fill=Tkinter.BOTH)
		g = ScrolledGrid(w.interior(), bd=0)
		g.pack(fill=Tkinter.BOTH, expand=Tkinter.TRUE)
		grid = g.tixGrid
		self.settingsGrid = grid
		grid.config(formatcmd=self.formatGrid)
		w = Pmw.Group(master, tag_text="Locations")
		w.pack(side=Tkinter.TOP, fill=Tkinter.BOTH)
		self.dirList = OrderedDirList(self, w.interior())
		self.dirList.pack(fill=Tkinter.BOTH)
		self.imageUnchecked = grid.tk.call("tix", "getimage", "ck_off")
		self.imageChecked = grid.tk.call("tix", "getimage", "ck_on")
		self.settingsStyle = Tix.DisplayStyle("window",
							refwindow=grid,
							anchor="center")
		self.remakeSettings()
		self.remakeLocations()

	def formatGrid(self, area, x1, y1, x2, y2):
		x1 = int(x1)
		x2 = int(x2)
		y1 = int(y1)
		y2 = int(y2)
		if x1 > len(self.settings) or y1 >= self.settingsCount:
			return
		if x2 > len(self.settings):
			x2 = len(self.settings)
		if y2 >= self.settingsCount:
			y2 = self.settingsCount - 1
		grid = self.settingsGrid
		if area == "main":
			# inside
			for y in range(y1, y2 + 1):
				if self.settingsMap.has_key(y):
					a = Tkinter.SE
				else:
					a = Tkinter.S
				grid.format("grid", x1, y, x2, y, anchor=a,
					relief="solid", bd=1, filled=1,
					xon=1, yon=1, xoff=0, yoff=0)
		elif area == "x-margin":
			# top side
			bg = grid.getvar('::tk::Palette(selectBackground)')
			grid.format("border", x1, y1, x2, y2,
					relief="raised", bd=1,
					filled=1, bg=bg)
		elif area == "y-margin":
			# left side
			for y in range(y1, y2 + 1):
				if self.settingsMap.has_key(y):
					bg = grid.cget('bg')
				else:
					bg = grid.getvar('::tk::Palette(selectBackground)')
				grid.format("grid", x1, y, x2, y,
						relief="solid", bd=1,
						filled=1, bg=bg)
		elif area == "s-margin":
			# top-left corner
			grid.format("border", x1, y1, x2, y2,
					relief="raise", bd=1, fill=1)

	def remakeSettings(self):
		grid = self.settingsGrid
		if self.settingsCount > 0:
			grid.delete("row", 0, self.settingsCount)
		grid.set(0, 0, itemtype="text", text="Tool")
		grid.size("col", 0, size="auto")
		for col in self.settings.iterkeys():
			label = self.settings[col][0]
			grid.set(col, 0, itemtype="text", text=label)
			grid.size("col", col, size="auto")
		# Make an exceptionally wide default column width
		# If the widget is resized to be much wider
		# than all the columns combined, then (hopefully)
		# only one extra blank column is displayed.
		# We don't bother with the rows since we expect
		# to have many more rows than are displayable.
		grid.size("col", "default", size="1000char")

		from chimera.tkgui import windowSystem
		if windowSystem == 'aqua':
			# Blank text entries with Aqua Tk 8.5.2 without this.
			grid.size("row", "default", size="1.3char")

		self.settingsMap = {}
		row = 1
		for cat in self.sortedCategories():
			grid.set(0, row, itemtype="text", text=cat.name())
			row += 1
			for emo in cat.sortedEntries():
				label = " " + emo.name()
				grid.set(0, row, text=label)
				for col in self.settings.iterkeys():
					b = self._getEMOButton(cat, emo, grid,
								row, col)
					grid.set(col, row,
						itemtype="window", window=b,
						style=self.settingsStyle)
					set = self.settings[col][1]
					set(cat, emo, b)
				self.settingsMap[row] = (cat, emo)
				row += 1
		self.settingsCount = row

	def _getEMOButton(self, cat, emo, grid, row, col):
		try:
			b = self.settingsButtons[(cat, emo, col)]
		except KeyError:
			cb = self.settings[col][2]
			def cmd(cb=cb, cat=cat, emo=emo):
				cb(cat, emo)
			b = Tkinter.Checkbutton(grid, indicatoron=0,
						image=self.imageUnchecked,
						selectimage=self.imageChecked,
						highlightthickness=0, bd=0,
						command=cmd)
			self.settingsButtons[(cat, emo, col)] = b
		return b

	def remakeLocations(self):
		# Clear out all items
		for desc, dir in self.dirList.items():
			self.dirList.removeItem(desc)
		for d in self.directories:
			self.dirList.addItem(d)

	def _setAutoStart(self, cat, emo, button):
		key = makeExtensionKey(emo.name())
		try:
			isOn = self.autoStart[key]
		except KeyError:
			button.deselect()
		else:
			button.select()

	def _autoStart(self, cat, emo):
		isOn = self._getButtonState(cat, emo, self.AUTO_START)
		key = makeExtensionKey(emo.name())
		wasOn = self.autoStart.has_key(key)
		if isOn == wasOn:
			return
		if isOn:
			self.autoStart[key] = 1
		else:
			del self.autoStart[key]
		self._resetButtonState(emo, self.AUTO_START)

	def _setOnToolbar(self, cat, emo, button):
		key = makeExtensionKey(emo.name())
		try:
			isOn = self.onToolbar[key]
		except KeyError:
			button.deselect()
		else:
			button.select()

	def _onToolbar(self, cat, emo):
		isOn = self._getButtonState(cat, emo, self.ON_TOOLBAR)
		key = makeExtensionKey(emo.name())
		wasOn = self.onToolbar.has_key(key)
		if isOn == wasOn:
			return
		if isOn:
			try:
				place = max(self.onToolbar.itervalues()) + 1
			except ValueError:
				place = 1
			emo.showOnToolbar()
			self.onToolbar[key] = place
		else:
			emo.removeFromToolbar()
			del self.onToolbar[key]
		self._resetButtonState(emo, self.ON_TOOLBAR)

	def _setInFavorites(self, cat, emo, button):
		key = makeExtensionKey(emo.name())
		try:
			isOn = self.inFavorites[key]
		except KeyError:
			button.deselect()
		else:
			button.select()

	def _inFavorites(self, cat, emo):
		isOn = self._getButtonState(cat, emo, self.IN_FAVORITES)
		key = makeExtensionKey(emo.name())
		wasOn = self.inFavorites.has_key(key)
		if isOn == wasOn:
			return
		if isOn:
			try:
				place = max(self.inFavorites.itervalues()) + 1
			except ValueError:
				place = 1
			self.inFavorites[key] = place
		else:
			del self.inFavorites[key]
		self.remakeFavorites()
		self._resetButtonState(emo, self.IN_FAVORITES)

	def _setConfirmOnStart(self, cat, emo, button):
		key = makeExtensionKey(emo.name())
		try:
			isOn = self.confirmOnStart[key]
		except KeyError:
			if not emo.hasUI():
				button.select()
			else:
				button.deselect()
		else:
			button.select()

	def _confirmOnStart(self, cat, emo):
		isOn = self._getButtonState(cat, emo, self.CONFIRM_ON_START)
		key = makeExtensionKey(emo.name())
		wasOn = self.confirmOnStart.has_key(key)
		if isOn == wasOn:
			return
		if isOn:
			self.confirmOnStart[key] = 1
		else:
			del self.confirmOnStart[key]
		self._resetButtonState(emo, self.CONFIRM_ON_START)

	def _getButtonState(self, cat, emo, col):
		b = self.settingsButtons[(cat, emo, col)]
		return int(b.tk.globalgetvar(b.cget("variable")))

	def _resetButtonState(self, changedEMO, col):
		for cat in self.categories.itervalues():
			for emo in cat.entries(): 
				if emo != changedEMO:
					continue
				b = self.settingsButtons[(cat, emo, col)]
				set = self.settings[col][1]
				set(cat, emo, b)

	def showToolbarButtons(self):
		toolDict = {}
		for cat in self.categories.itervalues():
			for emo in cat.entries(): 
				key = makeExtensionKey(emo.name())
				if self.onToolbar.has_key(key):
					toolDict[emo] = self.onToolbar[key]
				else:
					emo.removeFromToolbar()
		toolList = [ (v, k) for k, v in toolDict.iteritems() ]
		toolList.sort()
		for order, emo in toolList:
			try:
				emo.showOnToolbar()
			except:
				pass

	def confirmStart(self, cat, emo):
		key = makeExtensionKey(emo.name())
		try:
			return self.confirmOnStart[key]
		except KeyError:
			return not emo.hasUI()

	def preferencesReset(self, optdict):
		import StdTools
		self.inFavorites = StdTools.StdFavorites.copy()
		self.autoStart = {}
		self.confirmOnStart = {}
		self.onToolbar = {}
		self.directories = []
		self.preferencesLoad(optdict, loadDir=False)

	def preferencesLoad(self, optDict, loadDir=True):
		"Restore state from preferences dictionary"

		if optDict.has_key("dirList"):
			# Make a copy so we won't modify preferences
			# list when directories are added and removed
			self.directories = optDict["dirList"][:]
			if loadDir:
				for d in self.directories:
					self.loadDirectory(d)
		if optDict.has_key("autoStart"):
			self.autoStart = self._prefLoad(optDict["autoStart"])
		if optDict.has_key("onToolbar"):
			self.onToolbar = self._prefLoad(optDict["onToolbar"])
		if optDict.has_key("inFavorites"):
			self.inFavorites = \
				self._prefLoad(optDict["inFavorites"])
		if optDict.has_key("confirmOnStart"):
			self.confirmOnStart = \
				self._prefLoad(optDict["confirmOnStart"])

		if chimera.nogui:
			return
		self.showToolbarButtons()
		self.remakeFavorites()
		if self.settingsGrid:
			self.remakeSettings()
		if self.dirList:
			self.remakeLocations()

	def _prefLoad(self, d):
		# Convert from old style (category, extension)
		# to new style extension-only key
		nd = {}
		for k, v in d.iteritems():
			if isinstance(k, tuple) and len(k) == 2:
				k = k[1]
			nd[makeExtensionKey(k)] = v
		return nd

	def preferencesSave(self):
		"Return dictionary of state for saving in preferences"

		optDict = {}
		# make a copy of "directories" list so that later
		# modifications will not affect preferences state
		optDict["dirList"] = self.directories[:]
		optDict["autoStart"] = self._prefDict(self.autoStart)
		optDict["onToolbar"] = self._prefDict(self.onToolbar)
		optDict["inFavorites"] = self._prefDict(self.inFavorites)
		optDict["confirmOnStart"] = self._prefDict(self.confirmOnStart)
		return optDict

	def _prefDict(self, d):
		pd = {}
		for k, v in d.iteritems():
			pd[k.prefKey()] = v
		return pd

	def autostartTools(self, names):
		# 'names' is a list of tools to start that were 
		# specified on the command line.  Tools that
		# start successfully should be removed from 'names'
		if not self.autoStart and not names:
			return
		#
		# Convert old "Midas Emulator" name into
		# new "Command Line" name
		#
		cmdLine = "Command Line"
		oldMidasExtName = "Midas Emulator"
		for k, v in self.autoStart.iteritems():
			if k.extName == oldMidasExtName:
				key = makeExtensionKey(cmdLine)
				self.autoStart[key] = v
				del self.autoStart[k]
				break
		try:
			n = names.index(oldMidasExtName)
		except ValueError:
			pass
		else:
			names[n] = cmdLine
		#
		# Loop through all emos and find those that appear
		# either in autoStart or names.  Keep the hits
		# in a dictionary so that an emo is only started
		# at most once.
		# Special case the Command Line so it is done first,
		# because it modifies the main window and we want to
		# guarantee that the other tool dialogs to pop up
		# over it.
		#
		cmdLineEMO = None
		emoDict = {}
		bad = {}
		for name in names:
			bad[name] = 1
		for cat in self.categories.itervalues():
			catName = cat.name()
			for emo in cat.entries(): 
				emoName = emo.name()
				try:
					del bad[emoName]
				except KeyError:
					pass
				if self._shouldAutoStart(emo) \
				or emoName in names:
					if emoName == cmdLine:
						cmdLineEMO = emo
					else:
						emoDict[emo] = 1
		#
		# Assume all extensions will start correctly and
		# remove all but extensions that were not found.
		# If activating the extension fails, then add
		# the extension name back into the names list.
		#
		del names[:]
		for name in bad.iterkeys():
			names.append(name)
		if cmdLineEMO:
			try:
				cmdLineEMO.activate()
				chimera.tkgui.app.update_idletasks()
			except:
				if chimera.debug:
					raise
				names.append(cmdLineEMO.name())
		for emo in emoDict.iterkeys():
			try:
				emo.activate()
			except:
				if chimera.debug:
					raise
				names.append(emo.name())

	def _shouldAutoStart(self, emo):
		for key in self.autoStart.iterkeys():
			if key.matches(emo):
				return True
		return False


class OrderedDirList(OrderedListOption):
	"""OrderedListOption keeps track of an ordered list of file names"""

	def __init__(self, manager, master=None, *args, **kw):
		from chimera.tkgui import app
		apply(OrderedListOption.__init__, (self, master) + args, kw)
		self.manager = manager
		self._addDialog = None

	def addItem(self, dir):
		from chimera import tkgui
		if preferences.get(tkgui.GENERAL,
					tkgui.PATH_STYLE) == tkgui.PATH_NEXT:
			path, name = os.path.split(dir)
			OrderedListOption.addItem(self,
						"%s - %s" % (name, path), dir)
		else:
			OrderedListOption.addItem(self, dir, dir)

	# Override default add/delete behavior
	def add(self):
		if self._addDialog is None:
			import OpenSave
			self._addDialog = OpenSave.OpenModeless(
						title="Add Extension Directory",
						command=self.openDirectory,
						dirsOnly=1,
						clientPos='s')
		self._addDialog.enter()

	def delete(self):
		OrderedListOption.delete(self)
		self.manager.updateDirectories(
			[ obj for desc, obj in self.items() ])

	# Callback invoked when user selects a directory
	def openDirectory(self, okay, dialog):
		if not okay:
			return
		dirList = dialog.getPaths()
		if not dirList:
			return
		self.manager.addDirectory(dirList[0])
		self.addItem(dirList[0])


class ToolsCategory(preferences.Category):
	"ToolsCategory saves tool settings in preferences"

	def __init__(self, pref, manager=None):
		self.manager = manager
		self._savedState = {}
		preferences.Category.__init__(self, pref)
		self.frame = None

	def ui(self, master=None):
		if self.frame is None:
			self.frame = Tkinter.Frame(master)
			self.manager.createUI(self.frame)
		return self.frame

	def load(self, optDict, notifyUI=1):
		self.manager.preferencesLoad(optDict)
		self._savedState = optDict.copy()
		if notifyUI:
			self._pref.notifyUI()

	def save(self):
		return self._savedState

	def makeCurrentSaved(self):
		self._savedState = self.manager.preferencesSave()

	def resetValues(self):
		self.manager.preferencesReset({})

	def restoreValues(self):
		self.manager.preferencesReset(self._savedState)

manager = Manager()		# Create singleton

def startup(extNames):
	"""If a tool is started out of the list of tool names,
	then it is removed from the list."""
	manager.autostartTools(extNames)

def setup():
	import StdTools
	preferences.addCategory("Tools", ToolsCategory, aliases=["Extensions"],
				manager=manager)
	manager.loadDirectory(chimera.pathFinder().dataRoot)
	StdTools.registerStandardTools()
	if chimera.nogui:
		return
	manager.createMenu()
	manager.showToolbarButtons()
