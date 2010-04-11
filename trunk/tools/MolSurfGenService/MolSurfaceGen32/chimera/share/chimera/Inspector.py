#!/usr/local/bin/python

# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: Inspector.py 26655 2009-01-07 22:02:30Z gregc $

import sys
import Tkinter
from Tkconstants import YES, NO
from Tkconstants import X, Y, BOTH
from Tkconstants import LEFT, RIGHT, BOTTOM, TOP
from Tkconstants import E, W, N, S
from Tkconstants import END
from Tkconstants import RAISED, SUNKEN, GROOVE
from Tkconstants import DISABLED, NORMAL

# names to use in menu instead of raw class names
displayClass = {}

class Inspector:
	"""Semi-automated selection inspector

	Inspector(master) => widget

	The inspector provides an option menu that lets the user specify
	what class of objects he wants to inspect.  All registered classes
	are listed in the option menu, with classes having no associated
	instances in the selection being grayed out.
	Each class of objects is presented in its own Frame, with each
	registered attribute presented using instances from UI classes
	such as BooleanOption, StringOption or EnumOption.
	"""

	def __init__(self, master):
		self.frame = Tkinter.Frame(master, bd=2, relief=GROOVE)
		self.frame.pack(expand=YES, fill=BOTH, ipadx=2, ipady=2)
		self.classList = []
		self.classFrame = {}
		self.itemInfo = {}
		self.menuFrame = Tkinter.Frame(self.frame)
		self.menuFrame.pack(side=TOP, fill=X)
		bar = Tkinter.Frame(self.frame, height=2, bd=2, relief=GROOVE)
		bar.pack(side=TOP, fill=X, pady=2)
		l = Tkinter.Label(self.menuFrame, text='Inspect')
		l.pack(side=LEFT, fill=X)
		self.menubutton = Tkinter.Menubutton(self.menuFrame,
							bd=2, relief=RAISED,
							indicatoron=YES)
		self.menubutton.pack(side=LEFT, expand=YES, fill=X)
		self.menubutton['state'] = DISABLED
		self.menu = Tkinter.Menu(self.menubutton, tearoff=0)
		self.menuVar = Tkinter.StringVar(self.menu)
		self.currentClass = None
		self.menubutton['textvariable'] = self.menuVar
		self.menubutton['menu'] = self.menu
		self.updateClasses()
		self.updateItems([])

	def updateClasses(self):
		self.menu.delete(0, END)
		if len(self.classList) == 0:
			self.menuVar.set('No items')
			self.menubutton['state'] = DISABLED
		else:
			for klass in self.classList:
				try:
					name = displayClass[klass]
				except KeyError:
					name = klass.__name__
				cmd = lambda s=self, k=klass: s.inspect(k)
				state = self.itemInfo.has_key(klass) \
						and NORMAL or DISABLED
				self.menu.add_command(label=name,
							command=cmd,
							state=state)
			if len(self.itemInfo) > 0:
				self.menubutton['state'] = NORMAL
			else:
				self.menubutton['state'] = DISABLED

	def updateItems(self, items):
		self.itemInfo = {}
		for klass in self.classFrame.keys():
			for item in items:
				if isinstance(item, klass):
					if klass in self.itemInfo:
						self.itemInfo[klass].append(item)
					else:
						self.itemInfo[klass] = [ item ]
		for klass in self.classFrame.keys():
			try:
				name = displayClass[klass]
			except KeyError:
				name = klass.__name__
			state = self.itemInfo.has_key(klass) and NORMAL \
					or DISABLED
			entry = self.menu.entryconfigure(name, state=state)
		self.updateCurrentClass()

	def updateCurrentClass(self):
		if len(self.itemInfo) == 0:
			self._setCurrentClass(None)
			self.menuVar.set('No items')
			self.menubutton['state'] = DISABLED
			return
		if self.itemInfo.has_key(self.currentClass):
			klass = self.currentClass
		else:
			klass = None
			for k in self.classList:
				if self.itemInfo.has_key(k):
					klass = k
					break
		self._setCurrentClass(klass)

	def _setCurrentClass(self, klass):
		if klass is self.currentClass:
			if klass is not None:
				self.classFrame[klass].show(self.itemInfo[klass])
			return
		try:
			self.classFrame[self.currentClass].hide()
		except KeyError:
			# Class might be None or have been deregistered
			pass
		self.currentClass = klass
		if klass:
			try:
				name = displayClass[klass]
			except KeyError:
				name = klass.__name__
			self.menuVar.set(name)
			self.menubutton['state'] = NORMAL
			self.classFrame[klass].show(self.itemInfo[klass])
		else:
			self.menuVar.set('No items')
			self.menubutton['state'] = DISABLED

	def inspect(self, klass):
		try:
			name = displayClass[klass]
		except KeyError:
			name = klass.__name__
		self.menuVar.set(name)
		self._setCurrentClass(klass)

	def attrUpdate(self, klass, field):
		attr = field.attribute
		value = field.get()
		setA = field.setAttribute
		if '.' not in attr:
			for item in self.itemInfo[klass]:
				setA(item, attr, value)
		else:
			attrs = attr.split('.')
			for item in self.itemInfo[klass]:
				for a in attrs[:-1]:
					item = getattr(item, a)
				setA(item, attrs[-1], value)
		field.finish(self.itemInfo[klass])

	def register(self, klass, attr, fieldClass, displayAttr=None, **fieldKw):
		try:
			frame = self.classFrame[klass]
		except KeyError:
			frame = ClassFrame(self, self.frame, klass)
			self.classFrame[klass] = frame
			if klass not in self.classList:
				self.classList.append(klass)
		frame.addAttr(attr, fieldClass, displayAttr, **fieldKw)
		self.updateClasses()
		self.updateCurrentClass()

	def deregister(self, klass, attr):
		try:
			frame = self.classFrame[klass]
		except KeyError:
			return
		try:
			frame.deleteAttr(attr)
		except KeyError:
			return
		if frame.attrCount() == 0:
			del self.classFrame[klass]
			self.classList.remove(klass)
			try:
				del self.itemInfo[klass]
			except KeyError:
				pass
		self.updateClasses()
		self.updateCurrentClass()

class ClassFrame:
	"Frame for displaying class attributes in Inspector"

	def __init__(self, inspector, master, klass):
		self.inspector = inspector
		self.master = master
		self.klass = klass
		self.frame = Tkinter.Frame(master, bd=2, relief=SUNKEN)
		self.frame.grid_columnconfigure(1, weight=1)
		self.attrDict = {}
		self.attrList = []

	def __del__(self):
		for f in self.attrDict.values():
			f.destroy()
		self.frame.destroy()

	def addAttr(self, attr, fieldClass, displayName, **fieldKw):
		if self.attrDict.has_key(attr):
			raise ValueError, \
				'Attribute %s already registered' % attr
		n = len(self.attrList)
		self.attrList.append(attr)
		if not displayName:
			displayName = attr
		self.attrDict[attr] = fieldClass(
			self.frame, n, displayName, None,
			lambda f, s=self: s.inspector.attrUpdate(s.klass, f),
			attribute=attr, **fieldKw)

	def deleteAttr(self, attr):
		del self.attrDict[attr]
		self.attrList.remove(attr)
		# TODO: Remove attribute tk presence from frame

	def attrCount(self):
		return len(self.attrDict)

	def show(self, items):
		for ui in self.attrDict.values():
			ui.display(items)
		self.frame.pack(side=TOP, expand=YES, fill=BOTH)

	def hide(self):
		from tkoptions import ColorOption
		for option in self.attrDict.values():
			if isinstance(option, ColorOption):
				option.deactivate()
		self.frame.forget()

if __name__ == '__main__':
	import tkoptions
	class A:
		def __init__(self, s='testing', c='this'):
			self.hello = s
			self.choice = c
	class B:
		def __init__(self):
			self.world = 'what?'
	top = Tkinter.Frame()
	top.pack(fill=BOTH, expand=YES)
	inspector = Inspector(top)
	a = A()
	a1 = A(s='hello', c='that')
	b = B()
	inspector.register(A, 'hello', tkoptions.StringOption)
	class ThisThatOption(tkoptions.EnumOption):
		values=('this', 'that')
	inspector.register(A, 'choice', ThisThatOption)
	inspector.register(B, 'world', tkoptions.BooleanOption)
	button = Tkinter.Button(text='Test A',
				command=lambda i=inspector, a=a, a1=a1:
				i.updateItems([a, a1]))
	button.pack(side=TOP, fill=X)
	button = Tkinter.Button(text='Test B',
				command=lambda i=inspector, a=a, b=b:
				i.updateItems([b]))
	button.pack(side=TOP, fill=X)
	button = Tkinter.Button(text='Test A and B',
				command=lambda i=inspector, a=a, b=b:
				i.updateItems([a, b]))
	button.pack(side=TOP, fill=X)
	button = Tkinter.Button(text='Deregister A',
				command=lambda i=inspector, A=A:
				i.deregister(A, 'hello'))
	button.pack(side=TOP, fill=X)
	top.mainloop()
