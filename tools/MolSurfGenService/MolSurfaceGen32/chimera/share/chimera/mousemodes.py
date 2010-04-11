#!/usr/local/bin/python
# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: mousemodes.py 28700 2009-08-29 01:38:45Z gregc $

import Tkinter
Tk = Tkinter
import help
from baseDialog import ModelessDialog

AUTOSPIN = "autospin"

autospin = False

_mouseCategory = None

usedButtons = ("1", "2", "3")
usedMods = ("Ctrl",)

_funcDict = {}
_functionOrder = []
def addFunction(name, callables, icon=None):
	"""Add a named mouse function with callback functions + optional icon

	   The 3 (or 5) callbacks are invoked on: mouse press, mouse motion,
	   and mouse release and optionallly mouse double press and mouse
	   double release.  The callbacks take two arguments: viewer and
	   event.  The callbacks will be called from tkgui.py.
	   
	   An optional icon can be supplied.  If not, then an icon will be
	   looked up (using the function name with '.png' appended) via
	   chimage.get()"""

	if not _funcDict.has_key(name):
		_functionOrder.append(name)
	_funcDict[name] = callables
	if icon:
		imageDict[name] = icon
	if _mouseCategory:
		_mouseCategory.addFunc(name, callables)

def functionCallables(name):
	if name in _funcDict:
		return _funcDict[name]
	return None

_butFuncDict = {}
_defButFuncDict = {}
def setButtonFunction(button, modifiers, function, isDefault=False):
	b = expandButton(button, modifiers)
	if isDefault:
		_defButFuncDict[b] = function
	if _mouseCategory:
		_mouseCategory.setButton(b, function)
		# _butFuncDict[b] is set by "setButton"
	else:
		_butFuncDict[b] = function

def getFuncName(button, modifiers):
	return _mouseCategory.getFuncName(expandButton(button, modifiers))

def getCallables(button, modifiers):
	try:
		return _funcDict[getFuncName(button, modifiers)]
	except KeyError:
		return None

def getDefault(button, modifiers):
	return _defButFuncDict.get(expandButton(button, modifiers), None)

#
# Functions for manipulating button and modifier names
#
def _buildModifierList(l, prefix, remainder):
	if len(remainder) == 0:
		l.append(prefix)
		return
	m = remainder[0]
	_buildModifierList(l, prefix, remainder[1:])
	_buildModifierList(l, '%s%s-' % (prefix, m), remainder[1:])

def expandModifiers(modifiers):
	mList = []
	_buildModifierList(mList, '', modifiers)
	return mList

def expandButton(button, modifiers):
	modList = list(modifiers)
	modList.sort()
	prefix = ''
	for m in modList:
		prefix = '%s%s-' % (prefix, m)
	return prefix + button

#
# Function for finding and keeping a reference to images
#
imageDict = {}

def getImage(name, master):
	if imageDict.has_key(name):
		return imageDict[name]
	try:
		# TODO: Do we need to handle other extensions?
		icon_name = name.replace(' ', '_') + '.png'
		import chimage
		img = chimage.get(icon_name, master)
	except IOError, v:
		from extension.TextIcon import TextIcon
		bg = master["background"]		# could be color name
		bg = master.winfo_rgb(bg)		# convert to RGB
		bg = tuple(int(x / 256) for x in bg)	# PIL wants 0-255
		fg = master["foreground"]		# could be color name
		fg = master.winfo_rgb(fg)		# convert to RGB
		fg = tuple(int(x / 256) for x in fg)	# PIL wants 0-255
		img = TextIcon(master, name, compress=1, imageSize=(32, 32),
				bg=bg, fg=fg)
	imageDict[name] = img
	return img

#
# Class displaying and tracking mouse modes as a category under preferences
#
import preferences
import tkoptions
class MouseCategory(preferences.Category):
	"Mouse modes category has its own interface"

	def __init__(self, *args, **kw):
		preferences.Category.__init__(self, *args, **kw)
		self.__regularOptions = {AUTOSPIN: False}
			
		global _mouseCategory
		_mouseCategory = self

		self.__autospin = None

		self.__defaultOptions = self._save(saveAll=1)
		self.__savedOptions = {}

	def ui(self, master, rebuild=False):
		if self._ui and not rebuild:
			return self._ui
		import Tkinter
		if not self._ui or not rebuild:
			self._ui = Tkinter.Frame(master)
		elif rebuild:
			for slave in self._ui.grid_slaves():
				slave.grid_forget()
				slave.destroy()
		t = Tk.Label(self._ui, font='Helvetica',
				text="Note: Shift button may modify action.")
		t.grid(row=1, column=0, columnspan=2, sticky="w")

		frame = Tk.Frame(self._ui)
		frame.grid(row=0, column=0, columnspan=2, sticky="nsew")

		frame.columnconfigure(0, weight=1)
		l = Tk.Label(frame, text='Button')
		l.grid(row=0, column=0, sticky='ews')
		for f in _functionOrder:
			img = getImage(f, l)
			l = Tk.Label(frame, image=img, bd=2, relief=Tk.GROOVE)
			help.register(l, balloon=f)
			n = _functionOrder.index(f) + 1
			l.grid(row=0, column=n, sticky='news')
			frame.columnconfigure(n, weight=1)

		frame.rowconfigure(0, weight=1)
		row = 1
		self._varDict = {}
		for m in expandModifiers(usedMods):
			for b in usedButtons:
				mb = m + b
				l = Tk.Label(frame, text=mb, bd=2,
							relief=Tk.GROOVE)
				l.grid(row=row, column=0, sticky='news')
				frame.rowconfigure(row, weight=1)
				v = Tkinter.StringVar(frame)
				if _butFuncDict.has_key(mb):
					v.set(_butFuncDict[mb])
				else:
					v.set('not assigned')
				self._varDict[mb] = v
				for f in _functionOrder:
					fn = _functionOrder.index(f) + 1
					button = Tk.Radiobutton(frame,
						variable=v, value=f, text='',
						bd=2, relief=Tk.SUNKEN,
						command=lambda s=self, mb=mb,
							func=f:
							s.setButton(mb, func))
					button.grid(row=row, column=fn,
								sticky='news')
				row = row + 1
		ro = self.__regularOptions
		val = ro[AUTOSPIN]
		self.__autospin = tkoptions.BooleanOption(self._ui, 2,
				"Continue rotation after mousing", val,
				lambda o, s=self: s._autospinCB(o.get()))
		return self._ui

	def load(self, optDict, notifyUI=True, updateSaved=1):
		ro = self.__regularOptions
		for info, f in optDict.items():
			try:
				b, m = info
			except ValueError:
				ro[info] = f
				continue
			setButtonFunction(b, m, f)
		if not self.__autospin is None:
			self.__autospin.set(ro[AUTOSPIN])
		self._autospinCB(ro[AUTOSPIN])
		if notifyUI:
			self._pref.notifyUI()
		if updateSaved:
			self.__savedOptions = self._save(saveAll=0)

	def makeCurrentSaved(self):
		self.__savedOptions = self._save(saveAll=0)

	def save(self):
		return self.__savedOptions

	def _save(self, saveAll=0):
		optDict = {}
		for b in usedButtons:
			self._saveButton(optDict, b, (), usedMods, saveAll)

		ro = self.__regularOptions
		if self.__autospin is None:
			autospin = ro.get(AUTOSPIN, False)
		else:
			autospin = self.__autospin.get()
		if not autospin is None:
			optDict[AUTOSPIN] = autospin
		return optDict

	def _autospinCB(self, value):
		global autospin
		autospin = value

	def _saveButton(self, optDict, button, modifiers, remainder, saveAll=0):
		if not remainder:
			f = getFuncName(button, modifiers)
			df = getDefault(button, modifiers)
			if saveAll or f != df:
				optDict[(button, modifiers)] = f
			return
		self._saveButton(optDict, button, modifiers, remainder[1:],
							saveAll)
		self._saveButton(optDict, button, modifiers + (remainder[0],),
							remainder[1:], saveAll)
	def addFunc(self, name, funcs):
		if self._ui:
			self.ui(None, rebuild=True)
	
	def setButton(self, b, func):
		_butFuncDict[b] = func
		if self._ui:
			self._varDict[b].set(func)
	
	def getFuncName(self, b):
		try:
			return _butFuncDict[b]
		except KeyError:
			return 'not assigned'

	def restoreValues(self):
		self.load(self.__defaultOptions, updateSaved=0)
		self.load(self.__savedOptions, updateSaved=0)

	def resetValues(self):
		self.load(self.__defaultOptions, updateSaved=0)
