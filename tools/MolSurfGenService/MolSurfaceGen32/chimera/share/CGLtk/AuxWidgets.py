# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: AuxWidgets.py 26655 2009-01-07 22:02:30Z gregc $

import Tkinter as Tk
from Tkinter import _cnfmerge
import re

def _splitCnf(prefix, cnf):
	pattern = re.compile(prefix + '(.*)')
	prefixCnf = {}
	otherCnf = {}
	for k in cnf.keys():
		match = pattern.match(k)
		if not match:
			otherCnf[k] = cnf[k]
		else:
			prefixCnf[match.group(1)] = cnf[k]
	return prefixCnf, otherCnf

#
# WidgetWrapper is a base class that puts a widget inside a Frame.
# This is useful if you want a class to have the same semantics
# as an existing widget, but have an enhanced appearance.  For
# example, you can create a LabelEntry class which is exactly like an
# Entry, but has a Label next to the Entry (see below).  Note that
# WidgetWrapper must be the first of the base classes because it
# overrides the "pack" method.
#
class WidgetWrapper:
	def __init__(self, master=None, cnf={}, **kw):
		self.super = Tk.Frame(master, cnf, **kw)
	def pack(self, cnf={}, **kw):
		self.super.pack(cnf, **kw)
	def grid(self, cnf={}, **kw):
		self.super.grid(cnf, **kw)

#
# LabelEntry is an Entry with a Label to its left
#
class LabelEntry(WidgetWrapper, Tk.Entry):
	def __init__(self, master=None, cnf={}, **kw):
		labelCnf, cnf = _splitCnf('label_', _cnfmerge((cnf, kw)))
		WidgetWrapper.__init__(self, master)
		self.label = Tk.Label(self.super, labelCnf)
		self.label.pack(side=Tk.LEFT, fill=Tk.Y)
		Tk.Entry.__init__(self, self.super, cnf)
		Tk.Entry.pack(self, side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.TRUE)
	def setTitle(self, title):
		self.label['text'] = title
	def setEnabled(self, enabled):
		if enabled:
			self.label['foreground'] = '#000000'
			self['state'] = Tk.NORMAL
		else:
			self.label['foreground'] = '#808080'
			self['state'] = Tk.DISABLED

#
# LabelText is a Text with a Label to its left
#
class LabelText(WidgetWrapper, Tk.Text):
	def __init__(self, master=None, cnf={}, **kw):
		labelCnf, cnf = _splitCnf('label_', _cnfmerge((cnf, kw)))
		WidgetWrapper.__init__(self, master)
		self.label = Tk.Label(self.super, labelCnf)
		self.label.pack(side=Tk.LEFT, fill=Tk.Y)
		Tk.Text.__init__(self, self.super, cnf)
		Tk.Text.pack(self, side=Tk.RIGHT, fill=Tk.BOTH, expand=Tk.TRUE)
	def setTitle(self, title):
		self.label['text'] = title
	def setEnabled(self, enabled):
		if enabled:
			self.label['foreground'] = '#000000'
			self['state'] = Tk.NORMAL
		else:
			self.label['foreground'] = '#808080'
			self['state'] = Tk.DISABLED

#
# LabelButton is a Button with a Label below it
#
class LabelButton(WidgetWrapper, Tk.Button):
	def __init__(self, master=None, cnf={}, **kw):
		cnf = _cnfmerge((cnf, kw))
		labelCnf, cnf = _splitCnf('label_', _cnfmerge((cnf, kw)))
		WidgetWrapper.__init__(self, master)
		self.label = Tk.Label(self.super, labelCnf)
		self.label.pack(side=Tk.BOTTOM, fill=Tk.X)
		Tk.Button.__init__(self, self.super, cnf)
		Tk.Button.pack(self, side=Tk.TOP, fill=Tk.BOTH, expand=Tk.TRUE)
	def setTitle(self, title):
		self.label['text'] = title
	def setEnabled(self, enabled):
		if enabled:
			self.label['foreground'] = '#000000'
			self['state'] = Tk.NORMAL
		else:
			self.label['foreground'] = '#808080'
			self['state'] = Tk.DISABLED

#
# ScrollingListbox is a Listbox with a Scrollbar to its left
# and optionally a title above
#
class ScrollingListbox(WidgetWrapper, Tk.Listbox):
	def __init__(self, master=None, cnf={}, **kw):
		labelCnf, cnf = _splitCnf('label_', _cnfmerge((cnf, kw)))
		WidgetWrapper.__init__(self, master)
		if len(labelCnf) > 0:
			title = Label(self.super, labelCnf)
			title.pack(side=Tk.TOP, fill=Tk.X)
		scrollCnf, cnf = _splitCnf('scrollbar_', cnf)
		self.scroll = Tk.Scrollbar(self.super, scrollCnf)
		self.scroll.pack(fill=Tk.Y, side=Tk.LEFT)
		Tk.Listbox.__init__(self, self.super, cnf)
		Tk.Listbox.pack(self, fill=Tk.BOTH, expand=Tk.TRUE, side=Tk.RIGHT)
		self['yscrollcommand'] = self.scroll.set
		self.scroll['command'] = self.yview

#
# ScrollingText is a Text with a Scrollbar to its left
#
class ScrollingText(WidgetWrapper, Tk.Text):
	def __init__(self, master=None, cnf={}, **kw):
		WidgetWrapper.__init__(self, master)
		scrollCnf, cnf = _splitCnf('scrollbar_', _cnfmerge((cnf, kw)))
		self.scroll = Tk.Scrollbar(self.super, scrollCnf)
		self.scroll.pack(fill=Tk.Y, side=Tk.LEFT)
		Tk.Text.__init__(self, self.super, cnf)
		Tk.Text.pack(self, fill=Tk.BOTH, expand=Tk.TRUE, side=Tk.RIGHT)
		self['yscrollcommand'] = self.scroll.set
		self.scroll['command'] = self.yview
