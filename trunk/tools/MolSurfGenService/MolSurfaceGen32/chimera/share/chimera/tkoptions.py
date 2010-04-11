# Copyright (c) 2000 by the Regents of the University of California.
# All rights reserved.  See http://www.cgl.ucsf.edu/chimera/ for
# license details.
#
# $Id: tkoptions.py 29365 2009-11-18 22:57:39Z pett $

"""
Publishes Option/BooleanOption/StringOption/EnumOption.
"""
import Tkinter as Tk
import Tix
import chimera
from CGLtk.color import ColorWell
import CGLtk.OrderedListOption
from CGLtk.OptionMenu import OptionMenu
from colorTable import getColorByName

def recurse_getattr(obj, attribute):
	attrs = attribute.split('.')
	for a in attrs:
		obj = getattr(obj, a)
	return obj

class Option(object):
	"""Provide common interface for managing options"""
	# instance variables
	# name -- name of option
	# value -- value of option
	# _frame -- frame we're in

	multipleValue = "-- multiple --"
	errorColor = 'red'	# may want pink with dark text
	readOnly = False

	# callback behavior choices (when to call callback)
	CONTINUOUS = 0		# on every key typed
	FOCUSOUT = 1		# only on focus out
	RETURN = 2		# on focus out and when user types <Return>
	RETURN_TAB = 3		# as above, then tab to next GUI element

	def __init__(self, master, row, name, default, callback, startCol=0,
			balloon=None, attribute=None, getAttribute=None,
			cbmode=None, **kw):
		# if row == -1, then pack instead of grid
		if row == -1:
			master = Tk.Frame(master)
		self._master = master
		self._hasFocus = False
		self._outsideClick = None
		# non-empty name overrides any default name
		if name or not hasattr(self, 'name'):
			self.name = name
		if attribute:
			self.attribute = attribute
		else:
			if not hasattr(self, 'attribute'):
				self.attribute = self.name
		self.multiattribute = '.' in self.attribute
		if getAttribute:
			self.get = getAttribute
		elif self.multiattribute:
			self.getAttribute = recurse_getattr
		self._callback = callback
		if cbmode or not hasattr(self, 'cbmode'):
			self.cbmode = cbmode
		if self.name:
			self._label = Tk.Label(master, text=(self.name + ':'),
					       justify=Tk.RIGHT)
		else:
			self._label = None
		self.__row = row
		if row == -1:
			self._addOption(-1, None, **kw)
			if self._label:
				self._label.pack(side=Tk.RIGHT)
			master.pack(fill=Tk.X)
		else:
			if self._label:
				self._label.grid(row=row, column=startCol,
								sticky=Tk.E)
			self._addOption(row, startCol + 1, **kw)
			self.__column = startCol
		if balloon or not hasattr(self, 'balloon'):
			self.balloon = balloon
		commandLine = hasattr(self, 'inClass') \
				and '.' not in self.attribute
		if self.balloon or commandLine:
			if self.balloon:
				balloon = self.balloon
			else:
				balloon = ""
			if commandLine:
				attrBalloon = "attribute name: " \
							+ self.attribute
				attrVals = None
				if hasattr(self, 'attrValuesBalloon'):
					attrBalloon += '\n' \
						+ self.attrValuesBalloon
				elif hasattr(self, 'mapping'):
					attrVals = self.mapping.items()
				elif hasattr(self, 'labels') and hasattr(
							self, 'values'):
					if not isinstance(self, BooleanOption)\
					or self.labels != BooleanOption.labels:
						attrVals = zip(self.values,
								self.labels)
				if attrVals:
					attrBalloon += '\n'
					valsText = "values: "
					for val, vtext in attrVals:

						if valsText != "values: ":
							valsText += ", "
						valsText += str(val)
						valsText += " " + vtext
						if len(valsText) > 32:
							attrBalloon += valsText
							attrBalloon += "\n"
							valsText = ""
					if valsText:
						attrBalloon += valsText
					else:
						attrBalloon = attrBalloon[:-1]
				if balloon:
					balloon += "\n\n"
				balloon += attrBalloon
			if self._label:
				chimera.help.register(self._label,
							balloon=balloon)
			chimera.help.register(self._option, balloon=balloon)
		if default != None or not hasattr(self, 'default'):
			self.default = default
		if self.default != None:
			self.set(self.default)
		if self.cbmode in (Option.RETURN, Option.RETURN_TAB):
			if callback:
				self._bindReturn()
			else:
				self.cbmode = Option.CONTINUOUS

	def _bindReturn(self):
		# override as appropriate
		self._option.bind('<Return>', self._return)

	def _return(self, e=None):
		# override if self._set() takes arguments
		self._set()
		if self.cbmode == Option.RETURN_TAB:
			w = self._option.tk_focusNext()
			if w:
				w.focus()
		return 'break'

	_val_subst_format = ('%d', '%i', '%P', '%s', '%S', '%v', '%V', '%W')
	_val_subst_format_str = " ".join(_val_subst_format)
	def _val_substitute(self, *args):
		"""Internal function for validatecommand."""
		if len(args) != len(self._val_subst_format):
			return args
		d, i, P, s, S, v, V, W = args
		e = {
			'action': int(d),
			'index': int(i),
			'new': P,
			'current': s,
			'change': S,
			'type': v,
			'trigger': V,
			'widget': self._master._nametowidget(W)
		}
		return (e,)

	def _val_register(self, func):
		funcid = self._master._register(func, self._val_substitute, True)
		cmd = '%s %s\n' % (funcid, self._val_subst_format_str)
		return cmd

	def _validate(self, e):
		# When we lose focus, call _set only if we had focus
		# Always return TRUE to keep the validate callback
		if e["trigger"] == "focusin":
			# avoid later focus-out callbacks from unmapped widgets
			if self._option.winfo_ismapped():
				self._hasFocus = True
				if self.cbmode in (Option.RETURN, Option.RETURN_TAB):
					ev = Tk.Event()
					ev.widget = e['widget']
					top = self._option.winfo_toplevel()
					self._outsideClick = top.bind(
						'<ButtonPress>',
						lambda e, ev=ev:
							self._return(ev))
		elif e["trigger"] == "focusout":
			if self._hasFocus:
				self._hasFocus = False
				if self._outsideClick:
					top = self._option.winfo_toplevel()
					top.unbind('<ButtonPress>',
							self._outsideClick)
					self._outsideClick = None
				self._set(e)
		else:
			self._set(e)
		return Tk.TRUE

	def _set(self, e=None):		# May be overridden
		"""Called by GUI to propagate change back to program"""
		if self._callback:
			self._callback(self)

	getAttribute = getattr
	setAttribute = setattr

	def set(self, value):		# Must be overridden
		"""called by program, needs to be shown in GUI"""
		raise RuntimeError, "set method must be overridden"

	def get(self):			# May be overridden
		return self._option.get()

	def setMultiple(self):		# May be overridden 
		"""called by program, needs to be shown in GUI"""
		self.set(self.multipleValue)

	def enable(self):
		self._option.config(state=Tk.NORMAL)
		if self._label:
			self._label.config(state=Tk.NORMAL)

	def disable(self):
		self._option.config(state=Tk.DISABLED)
		if self._label:
			self._label.config(state=Tk.DISABLED)

	def forget(self):
		if self.__row != -1:
			cell = self._master.grid_slaves(row=self.__row,
							column=self.__column+1)
			if not cell:
				return
			self.__optWidget = cell[0]
			self.__optWidgetGridKw = self.__optWidget.grid_info()
			self.__optWidget.grid_forget()
			if self._label:
				self.__labelGridKw = self._label.grid_info()
				self._label.grid_forget()
		else:
			# 'hasattr' doesn't work for '__' attributes
			try:
				masterKw = self.__masterWidgetPackKw
			except AttributeError:
				# only save pack info once
				self.__masterWidgetPackKw = self._master.pack_info()
				self._master.forget()

	def manage(self):
		# 'hasattr' doesn't work for '__' attributes
		if self.__row != -1:
			try:
				optWidget = self.__optWidget
			except AttributeError:
				return
			optWidget.grid(**self.__optWidgetGridKw)
			if self._label:
				self._label.grid(**self.__labelGridKw)
		else:
			try:
				masterKw = self.__masterWidgetPackKw
			except AttributeError:
				return
			del self.__masterWidgetPackKw
			self._master.pack(**masterKw)

	def display(self, items):
		if not items:
			return
		if self.readOnly:
			self.enable()
		value = self.getAttribute(items[0], self.attribute)
		for item in items[1:]:
			v = self.getAttribute(item, self.attribute)
			if v != value:
				self.setMultiple()
				if self.readOnly:
					self.disable()
				return
		self.set(value)
		if self.readOnly:
			self.disable()

	def finish(self, items):
		pass

	# for backwards compatibility
	gridUnmanage = forget
	gridManage = manage

class NumericOption(Option):
	"""specialization base class for numeric options"""
	noneValues = False
	missingValues = False

	def display(self, items):
		if not items:
			return
		ga, attrName = self.getAttribute, self.attribute
		if self.missingValues:
			values = [ga(i, attrName, None) for i in items]
		else:
			values = [ga(i, attrName) for i in items]
		if self.noneValues or self.missingValues:
			values = [i for i in values if i is not None]
			if not values:
				if self.missingValues:
					self.multipleValue = "not assigned"
				else:
					self.multipleValue = "N/A"
				self.setMultiple()
				return
		minVal, maxVal = "%g" % min(values), "%g" % max(values)
		if minVal == maxVal:
			self.set(eval(minVal))
		else:
			self.multipleValue = u"%s \N{LEFT RIGHT ARROW} %s" % (
													minVal, maxVal)
			self.setMultiple()

#class BooleanOption(Option):
#	"""Specialization for boolean values"""
#	varclass = Tk.BooleanVar
#
#	def _addOption(self, row, col, **kw):
#		self._option = Tk.Checkbutton(self._master, indicatoron=Tk.TRUE,
#			relief=Tk.FLAT, highlightthickness=0, command=self._set)
#		if row == -1:
#			self._option.pack(side=Tk.RIGHT)
#		else:
#			self._option.grid(row=row, column=col, sticky=Tk.W)
#
#	def setMultiple(self):
#		# TODO: how to show multiple values with a check button?
#		pass

class StringOption(Option):
	"""Specialization for string values"""

	cbmode = Option.RETURN

	def _addOption(self, row, col, **kw):
		entry_opts = {
			'relief': Tk.SUNKEN,
			'borderwidth': 2
		}
		if self._callback:
			entry_opts['validatecommand'] \
					= self._val_register(self._validate)
			if self.cbmode == Option.CONTINUOUS:
				entry_opts['validate'] = 'key'
			else:
				entry_opts['validate'] = 'focus'
		if self._label:
			entry_opts['width'] = 10
		entry_opts.update(kw)
		self._option = Tk.Entry(self._master, **entry_opts)
		if row == -1:
			if self._label:
				self._option.pack(side=Tk.RIGHT)
			else:
				self._option.pack(fill=Tk.X)
		else:
			self._option.grid(row=row, column=col, sticky='ew')

	def _set(self, e=None):
		if self._option.get() == self.multipleValue:
			return Tk.TRUE
		Option._set(self)
		return Tk.TRUE

	def set(self, value):
		entry = self._option
		validate = entry.cget('validate')
		if validate != Tk.NONE:
			entry.configure(validate=Tk.NONE)
		entry.delete(0, Tk.END)
		entry.insert(Tk.END, value)
		if validate != Tk.NONE:
			entry.configure(validate=validate)

class InfoOption(Option):
	"""Provides read-only attribute information"""

	def _addOption(self, row, col, **kw):
		self._option = Tk.Label(self._master, **kw)
		if row == -1:
			self._option.pack(side=Tk.RIGHT)
		else:
			self._option.grid(row=row, column=col, sticky='w')

	def set(self, value):
		self._option['text'] = str(value)

class EnumOption(Option):
	"""Specialization for enumerated values"""
	values=()

	def _addOption(self, row, col, **kw):
		self._option = OptionMenu(self._master, **kw)
		self.menu = self._option["menu"]  # for easy entryconfigure
		if row == -1:
			self._option.pack(side=Tk.RIGHT)
		else:
			self._option.grid(row=row, column=col, sticky=Tk.W)
		self.remakeMenu()

	def set(self, value):
		self._option.set(value)

	def remakeMenu(self, *args):
		self._option.clear()
		self._option.add_buttons(self.values, command=self._set)

class SymbolicEnumOption(EnumOption):
	"""Specialization for enumerated values with symbolic names"""
	values = []		# should be a list
	labels = []		# should be a list

	def _addOption(self, row, col, **kw):
		self._value = None
		EnumOption._addOption(self, row, col, **kw)

	def _set(self, e=None):
		label = self._option.get()
		i = list(self.labels).index(label)
		self._value = self.values[i]
		EnumOption._set(self)
		return Tk.TRUE

	def set(self, value):
		self._value = value
		self._option.set(self.labels[list(self.values).index(value)])

	def get(self):
		return self._value

	def setMultiple(self):
		self._value = None
		self._option.set(self.multipleValue)

	def remakeMenu(self, *args):
		self._option.clear()
		self._option.add_buttons(self.labels, command=self._set)

class ImageEnumOption(EnumOption):
	"""Specialization for enumerated values with image"""
	values = []		# should be a list
	images = []		# should be a list

	def _addOption(self, row, col, **kw):
		self._value = None
		self._images = [None] * len(self.values)
		variable = Tk.IntVar(self._master)
		EnumOption._addOption(self, row, col, variable=variable, **kw)

	def _set(self, e=None):
		self._value = self._option.get()
		index = list(self.values).index(self._value)
		self._option.config(image=self._images[index])
		EnumOption._set(self)
		return Tk.TRUE

	def set(self, value):
		self._value = value
		self._option.set(value)
		index = list(self.values).index(self._value)
		self._option.config(image=self._images[index])

	def get(self):
		return self._value

	def setMultiple(self):
		self._value = None
		self._option.set(self.multipleValue)

	def remakeMenu(self, *args):
		self._option.clear()
		import chimage, os.path
		for i in range(len(self.values)):
			self._images[i] = chimage.get(self.images[i], self._master)
			self._option.add_button(self.values[i],
				image=self._images[i], command=self._set)
		width = max(i.width() for i in self._images) + 4
		height = max(i.height() for i in self._images) + 4
		font = self._option.cget('font')
		if not font:
		    fheight = 12
		else:
		    fheight = self._option.tk.call('font', 'metrics', font, '-linespace')
		if height < fheight:
		    height = fheight
		self._option.config(width=width, height=height)

class BooleanOption(SymbolicEnumOption):
	values = [0, 1]
	labels = ["false", "true"]

	def set(self, value):
		if value:
			value = 1
		else:
			value = 0
		SymbolicEnumOption.set(self, value)

class IntOption(NumericOption):
	"""Specialization for integer input"""

	min = None
	max = None
	cbmode = Option.RETURN

	def _addOption(self, row, col, min=None, max=None, sticky='ew', **kw):
		if min != None:
			self.min = min
		if max != None:
			self.max = max
		entry_opts = {
			'validatecommand': self._val_register(self._validate),
			'relief': Tk.SUNKEN,
			'borderwidth': 2,
			'width': 8,
			'validate': 'all',
		}
		entry_opts.update(kw)
		self._option = Tk.Entry(self._master, **entry_opts)
		if row == -1:
			self._option.pack(side=Tk.RIGHT)
		else:
			self._option.grid(row=row, column=col, sticky=sticky)
		self.bgcolor = self._option.cget('bg')

	def _set(self, args):
		action = args['action']
		entry = self._option
		# action 0 is deletion
		# action 1 is insertion
		# action -1 is focus, forced, or textvariable
		try:
			value = int(args['new'])
		except ValueError:
			if action != -1:
				entry.configure(bg=self.errorColor)
			else:
				# enter/leave, reset to valid value
				entry.configure(bg=self.bgcolor)
				if self._value:
					self.set(self._value)
			return Tk.TRUE
		entry.configure(bg=self.bgcolor)
		if action == -1:
			if self.min is not None and value < self.min:
				altered = self._value != value
				self.set(self.min)
				if altered:
					Option._set(self)
			elif self.max is not None and value > self.max:
				altered = self._value != value
				self.set(self.max)
				if altered:
					Option._set(self)
			else:
				if self._value != value:
					self._value = value
					Option._set(self)
			return Tk.TRUE
		if (self.min is not None and value < self.min) \
		or (self.max is not None and value > self.max):
			entry.configure(bg=self.errorColor)
			return Tk.TRUE
		if self.cbmode == Option.CONTINUOUS:
			self._value = value
			Option._set(self)
		return Tk.TRUE

	def _return(self, e=None):
		args = {
			'action': -1,
			'new': self._option.get()
		}
		self._set(args)
		if self.cbmode == Option.RETURN_TAB:
			w = self._option.tk_focusNext()
			if w:
				w.focus()
		return 'break'

	def set(self, value):
		value = int(value)
		self._value = value
		entry = self._option
		validate = entry.cget('validate')
		if validate != Tk.NONE:
			entry.configure(validate=Tk.NONE)
		entry.delete(0, Tk.END)
		entry.insert(Tk.END, str(value))
		if validate != Tk.NONE:
			entry.configure(validate=validate)

	def get(self):
		return self._value

	def setMultiple(self):
		self._value = None
		entry = self._option
		validate = entry.cget('validate')
		if validate != Tk.NONE:
			entry.configure(validate=Tk.NONE)
		entry.delete(0, Tk.END)
		entry.insert(Tk.END, self.multipleValue)
		if validate != Tk.NONE:
			entry.configure(validate=validate)

class SliderOption(Option):
	"""Restricted float option"""
	min = 0
	max = 1
	step = 0.01

	def _addOption(self, row, col, min=None, max=None, step=None, **kw):
		if min != None:
			self.min = min
		if max != None:
			self.max = max
		if step != None:
			self.step = step
		self._var = Tk.DoubleVar(self._master)
		entry_opts = {
			'from': self.min, 'to': self.max,
			'resolution': self.step,
			'showvalue': 1, 'variable': self._var,
			'orient': Tk.HORIZONTAL, 'command': self._set
		}
		entry_opts.update(kw)
		self._option = Tk.Scale(self._master, **entry_opts)
		if row == -1:
			if self._label:
				self._option.pack(side=Tk.RIGHT)
			else:
				self._option.pack(fill=Tk.X)
		else:
			self._option.grid(row=row, column=col, sticky='news')

	def get(self):
		return self._var.get()

	def set(self, value):
		self._var.set(value)

class FloatOption(NumericOption):
	"""Specialization for floating point input"""

	min = None
	max = None
	cbmode = Option.RETURN

	def _addOption(self, row, col, min=None, max=None, sticky='ew', **kw):
		if min != None:
			self.min = min
		if max != None:
			self.max = max
		entry_opts = {
			'validatecommand': self._val_register(self._validate),
			'relief': Tk.SUNKEN,
			'borderwidth': 2,
			'width': 8,
			'validate': 'all',
		}
		entry_opts.update(kw)
		self._option = Tk.Entry(self._master, **entry_opts)
		if row == -1:
			self._option.pack(side=Tk.RIGHT)
		else:
			self._option.grid(row=row, column=col, sticky=sticky)
		self.bgcolor = self._option.cget('bg')
		self._value = None

	def _set(self, args):
		action = args['action']
		entry = self._option
		try:
			value = float(args['new'])
		except ValueError, info:
			if action != -1:
				entry.configure(bg=self.errorColor)
			else:
				# enter/leave, reset to value value
				entry.configure(bg=self.bgcolor)
				if self._value:
					self.set(self._value)
			return Tk.TRUE
		entry.configure(bg=self.bgcolor)
		if action == -1:
			if self.min is not None and value < self.min:
				altered = self._value != self.min
				self.set(self.min)
				if altered:
					Option._set(self)
			elif self.max is not None and value > self.max:
				altered = self._value != self.max
				self.set(self.max)
				if altered:
					Option._set(self)
			else:
				if self._value != value:
					self._value = value
					Option._set(self)
			return Tk.TRUE
		if (self.min is not None and value < self.min) \
		or (self.max is not None and value > self.max):
			entry.configure(bg=self.errorColor)
			return Tk.TRUE
		if self.cbmode == Option.CONTINUOUS:
			self._value = value
			Option._set(self)
		return Tk.TRUE

	def _return(self, e=None):
		args = {
			'action': -1,
			'new': self._option.get()
		}
		self._set(args)
		if self.cbmode == Option.RETURN_TAB:
			w = self._option.tk_focusNext()
			if w:
				w.focus()
		return 'break'

	def set(self, value):
		value = float(value)
		self._value = value
		validate = self._option.cget('validate')
		if validate != Tk.NONE:
			self._option.configure(validate=Tk.NONE)
		self._option.delete(0, Tk.END)
		strvalue = '%g' % value
		if '.' not in strvalue:
			strvalue += '.0'
		self._option.insert(Tk.END, strvalue)
		if validate != Tk.NONE:
			self._option.configure(validate=validate)

	def get(self):
		return self._value

	def setMultiple(self):
		self._value = None
		entry = self._option
		validate = entry.cget('validate')
		if validate != Tk.NONE:
			entry.configure(validate=Tk.NONE)
		entry.delete(0, Tk.END)
		entry.insert(Tk.END, self.multipleValue)
		if validate != Tk.NONE:
			entry.configure(validate=validate)

class Float3TupleOption(Option):
	"""Specialization for (x, y, z) input"""

	min = None
	max = None
	cbmode = Option.RETURN

	def _addOption(self, row, col, min=None, max=None, **kw):
		if min != None:
			self.min = min
		if max != None:
			self.max = max
		entry_opts = {
			'validatecommand': self._val_register(self._validate),
			'width': 8,
			'validate': 'all',
		}
		entry_opts.update(kw)
		self._option = Tk.Frame(self._master)
		self.entries = []
		for i in range(3):
			e = Tk.Entry(self._option, **entry_opts)
			e.pack(side=Tk.TOP)
			self.entries.append(e)
		if row == -1:
			self._option.pack(side=Tk.RIGHT)
		else:
			self._option.grid(row=row, column=col, sticky=Tk.W)
		self.bgcolor = self.entries[0].cget('bg')
		self._value = [ None, None, None ]

	def enable(self):
		for e in self.entries:
			e.config(state=Tk.NORMAL)
		if self._label:
			self._label.config(state=Tk.DISABLED)

	def disable(self):
		for e in self.entries:
			e.config(state=Tk.DISABLED)
		if self._label:
			self._label.config(state=Tk.DISABLED)

	def _set(self, args):
		action = args['action']
		entry = args['widget']
		index = self.entries.index(entry)
		try:
			value = float(args['new'])
		except ValueError, info:
			if action != -1:
				entry.configure(bg=self.errorColor)
			else:
				# enter/leave, reset to valid value
				entry.configure(bg=self.bgcolor)
				if self._value[0] is not None \
				and self._value[1] is not None \
				and self._value[2] is not None:
					self.set(self._value)
			return Tk.TRUE
		entry.configure(bg=self.bgcolor)
		if action == -1:
			if self.min is not None and value < self.min:
				altered = self._value[index] != self.min
				self._update_value(self.min, index)
				if altered:
					Option._set(self)
			elif self.max is not None and value > self.max:
				altered = self._value[index] != self.max
				self._update_value(self.max, index)
				if altered:
					Option._set(self)
			else:
				if self._value != value:
					self._value[index] = value
					Option._set(self)
			return Tk.TRUE
		if (self.min is not None and value < self.min) \
		or (self.max is not None and value > self.max):
			entry.configure(bg=self.errorColor)
			return Tk.TRUE
		if self.cbmode == Option.CONTINUOUS:
			self._value[index] = value
			Option._set(self)
		return Tk.TRUE

	def _bindReturn(self):
		# override as appropriate
		for e in self.entries:
			e.bind('<Return>', self._return)

	def _return(self, e=None):
		widget = e.widget
		args = {
			'action': -1,
			'new': widget.get(),
			'widget': widget
		}
		self._set(args)
		if self.cbmode == Option.RETURN_TAB \
		or (self.cbmode == Option.RETURN and widget != self.entries[2]):
			w = widget.tk_focusNext()
			if w:
				w.focus()
		return 'break'
	
	def _update_index(self, value, index):
		self._value[index] = value
		entry = self.entries[index]
		validate = entry.cget('validate')
		if validate != Tk.NONE:
			entry.configure(validate=Tk.NONE)
		entry.delete(0, Tk.END)
		strvalue = '%g' % value
		if '.' not in strvalue:
			strvalue += '.0'
		entry.insert(Tk.END, strvalue)
		if validate != Tk.NONE:
			entry.configure(validate=validate)

	def set(self, value):
		assert(len(value) == 3)
		value = [float(value[0]), float(value[1]), float(value[2])] 
		for index in range(3):
			self._update_index(value[index], index)

	def get(self):
		return self._value

	def setMultiple(self):
		raise RuntimeError, "%s does not implement setMultiple()" % (
							self.__class__.__name__)

# TODO: need to be able to set the font name, size, and style
SANSSERIF = intern("Sans Serif")
SERIF = intern("Serif")
FIXED = intern("Fixed")
#SANSSERIF = intern("Helvetica")
#SERIF = intern("Times")
#FIXED = intern("Courier")

class FontOption(Option):
	"""Specialization of Option Class for fonts"""
	names = (SANSSERIF, SERIF, FIXED)
	styles = ("Normal", "Bold", "Italic", "Bold Italic")
	sizes = (6, 8, 9, 10, 11, 12, 16, 18, 24, 30, 36)

	DEFAULT_SIZE = 16

	def _addOption(self, row, col):
		#self._name = Tk.StringVar(self._master)
		#self._style = Tk.StringVar(self._master)
		self._size = self.DEFAULT_SIZE
		self._option = Tk.Frame(self._master)
		self.bgcolor = self._option.cget('bg')

		#self.fontName = Tix.ComboBox(self._option, editable=Tk.NO,
		#	variable=self._name, command=self._setName,
		#	options="entry.width 9 slistbox.listbox.height 0")
		#self.fontName.pack(side=Tk.LEFT)
		#for n in self.names:
		#	self.fontName.insert(Tk.END, n)
		#self.fontName.slistbox.place(relw=1)

		self._name = OptionMenu(self._option, values=self.names,
							command=self._setName)
		self._name.pack(side=Tk.LEFT)

		#self.fontStyle = Tix.ComboBox(self._option, editable=Tk.NO,
		#	variable=self._style, command=self._setStyle,
		#	options="entry.width 8 slistbox.listbox.height 0")
		#self.fontStyle.pack(side=Tk.LEFT)
		#for n in self.styles:
		#	self.fontStyle.insert(Tk.END, n)
		#self.fontStyle.slistbox.place(relw=1)

		self._style = OptionMenu(self._option, values=self.styles,
							command=self._setStyle)
		self._style.pack(side=Tk.LEFT)

		self.fontSize = Tix.ComboBox(self._option, editable=Tk.YES,
			options="entry.width 3", command=self._SizeReturn)
		self.fontSize.entry.configure(validate='all',
			validatecommand=self._val_register(self._setSize))
		self.fontSize.pack(side=Tk.LEFT)
		for s in self.sizes:
			self.fontSize.insert(Tk.END, s)
		self.fontSize.slistbox.place(relw=1)

		if row == -1:
			self._option.pack(side=Tk.RIGHT)
		else:
			self._option.grid(row=row, column=col, sticky='news')

	def _setName(self, args=None):
		Option._set(self)

	def _setStyle(self, args=None):
		Option._set(self)

	def _setSize(self, args):
		action = args['action']
		entry = self.fontSize.entry
		try:
			value = int(args['new'])
		except ValueError:
			if action != -1:
				entry.configure(bg=self.errorColor)
			else:
				# enter/leave, reset to valid value
				entry.configure(bg=self.bgcolor)
				if self._size:
					self.set((None, None, self._size))
			return Tk.TRUE
		entry.configure(bg=self.bgcolor)
		if action == -1:
			if value < 1:
				if self._size != value:
					self.set((None, None, 1))
					Option._set(self)
			else:
				if self._size != value:
					self._size = value
					Option._set(self)
			return Tk.TRUE
		if value < 1:
			entry.configure(bg=self.errorColor)
			return Tk.TRUE
		if self.cbmode == Option.CONTINUOUS:
			self._size = value
			Option._set(self)
		return Tk.TRUE

	def _SizeReturn(self, e=None):
		args = {
			'action': -1,
			'new': self.fontSize.entry.get()
		}
		self._setSize(args)
		if self.cbmode == Option.RETURN_TAB:
			w = self._option.tk_focusNext()
			if w:
				w.focus()

	def set(self, value):
		assert(len(value) == 3)

		if value[0] is not None:
			self._name.set(str(value[0]))

		if value[1] is not None:
			self._style.set(str(value[1]))

		if value[2] is not None:
			size = int(value[2])
			if value < 1:
				raise ValueError, "font size must be positive"
			self._size = size
			entry = self.fontSize.entry
			validate = entry.cget('validate')
			if validate != Tk.NONE:
				entry.configure(validate=Tk.NONE)
			entry.delete(0, Tk.END)
			entry.insert(Tk.END, str(size))
			if validate != Tk.NONE:
				entry.configure(validate=validate)


	def get(self):
		return (self._name.get(), self._style.get(), self._size)

	def setMultiple(self):
		raise RuntimeError, "%s does not implement setMultiple()" % (
							self.__class__.__name__)

# utility funcs for interfacing colors to preferences save mechanism
def _colorToPref(color):
	try:
		return color.rgba()
	except AttributeError:
		return color
def _prefToColor(pref):
	if isinstance(pref, basestring):
		try:
			return getColorByName(pref)
		except KeyError:
			return None
	if pref is None:
		return None
	return chimera.MaterialColor(*pref)

class ColorOption(Option):
	"""Specialization for color selection
	
	   If value is set to a Color instance, will monitor that Color for
	   internal changes, calling colorChangeCB on such changes.  If set
	   to a non-Color, will use a private Color instance and monitor
	   changes to that.  Non-internal changes will call the normal
	   callback.
	"""

	prefConv = (_colorToPref, _prefToColor)

	def _addOption(self, row, col, noneOkay=True, colorChangeCB=None, **kw):
		self._option = ColorWell.ColorWell(self._master,
					noneOkay=noneOkay, callback=self._set)
		if row == -1:
			self._option.pack(side=Tk.RIGHT)
		else:
			self._option.grid(row=row, column=col, sticky=Tk.W)
		self.__monitorColorHandler = None
		self.value = None
		self.__expectingChange = False
		self.__colorChangeCB = colorChangeCB

	def _set(self, colorOrRgba, makeCallback=True):
		if isinstance(self.value, chimera.Color):
			self.__stopMonitoring()
		if isinstance(colorOrRgba, chimera.Color):
			self.value = colorOrRgba
			self.__startMonitoring()
		elif colorOrRgba is None:
			self.value = None
		else:
			rgba = colorOrRgba
			self.value = chimera.MaterialColor()
			self.value.ambientDiffuse = tuple(rgba[:3])
			self.value.opacity = rgba[3]
			if self.__colorChangeCB:
				self.__colorChangeCB()
			self.__startMonitoring()
			self.__expectingChange = True
		if makeCallback:
			Option._set(self)

	def set(self, c, makeCallback=False):
		if c is None:
			rgba = value = None
		elif isinstance(c, basestring):
			rgba = value = getColorByName(c).rgba()
		elif isinstance(c, tuple):
			if len(c) == 3:
				c = c + (1.0,)
			rgba = value = c
		else:
			value = c
			rgba = c.rgba()
		self._set(value, makeCallback=makeCallback)
		self._option.showColor(rgba, doCallback=False)

	def displayColor(self, c):
		#self._color.ambientDiffuse = c.ambientDiffuse
		self.set(c)

	def get(self):
		return self.value

	def setMultiple(self):
		if isinstance(self.value, chimera.Color):
			self.__stopMonitoring()
		self._option.showColor(multiple=1)

	def enable(self):
		self._option.enable()

	def disable(self):
		self._option.disable()

	def activate(self):
		self._option.activate()

	def deactivate(self):
		self._option.deactivate()

	def __stopMonitoring(self):
		if not self.__monitorColorHandler:
			return
		chimera.triggers.deleteHandler('Color',
						self.__monitorColorHandler)
		self.__monitorColorHandler = None

	def __startMonitoring(self):
		if self.__monitorColorHandler:
			return
		self.__monitorColorHandler = chimera.triggers.addHandler(
						'Color', self.__monitorCB, None)

	def __monitorCB(self, trigName, myData, trigData):
		if self.value not in trigData.modified:
			return
		if self.__expectingChange:
			self.__expectingChange = False
			return
		self._option.showColor(self.value.rgba(), doCallback=0)
		if self.__colorChangeCB:
			self.__colorChangeCB()

class RGBAOption(Option):
	"""Specialization for RGBA selection"""

	def _addOption(self, row, col, noneOkay=1, **kw):
		self._option = ColorWell.ColorWell(self._master,
					noneOkay=noneOkay, callback=self._set)
		if row == -1:
			self._option.pack(side=Tk.RIGHT)
		else:
			self._option.grid(row=row, column=col, sticky=Tk.W)
		self._set(self._option.rgba, makeCallback=0)

	def _set(self, rgba, makeCallback=1):
		self.value = rgba
		if makeCallback:
			Option._set(self)

	def set(self, rgba, makeCallback=0):
		if rgba is None:
			value = None
		elif isinstance(rgba, basestring):
			value = getColorByName(rgba).rgba()
		elif isinstance(rgba, chimera.Color):
			value = rgba.rgba()
		else:
			if len(rgba) == 3:
				rgba = tuple(rgba) + (1,)
			value = rgba
		self._set(value, makeCallback=makeCallback)
		self._option.showColor(value, doCallback=0)

	def get(self):
		if isinstance(self.value, basestring):
			self.value = getColorByName(rgba).rgba()
		return self.value

	def setMultiple(self):
		self._option.showColor(multiple=1)

	def enable(self):
		# TODO
		pass

	def disable(self):
		# TODO
		pass

class _BaseFileOption(Option):
	"""Get a file name.
	
	   Keyword 'entryWidth' controls width of the entry field.
	   Other keyword argments are passed to OpenModeless constructor.

	   Giving a default value of True will cause the entry field to be
	   set to the last used file.
	"""

	cbmode = Option.RETURN

	def _addOption(self, row, col, entryWidth=20, **kw):
		self._dialog = None
		self._dialogKw = kw
		frame = Tk.Frame(self._master)
		if row == -1:
			frame.pack(side=Tk.RIGHT)
		else:
			frame.grid(row=row, column=col, sticky="ew")
		frame.bind('<Unmap>', self._nukeDialog)

		# entry
		frame.columnconfigure(0, weight=1)
		self._option = Tk.Entry(frame, width=entryWidth)
		self._option.grid(row=0, column=0, sticky="ew")

		# browse button
		self._button = Tk.Button(frame, command=self._startDialog,
			pady=0, text="Browse")
		chimera.help.register(self._button,
				balloon="Browse filesystem for file name")
		self._button.grid(row=0, column=1)

	def disable(self):
		self._option.config(state='disabled')
		self._button.config(state='disabled')

	def enable(self):
		self._option.config(state='normal')
		self._button.config(state='normal')

	def set(self, value):
		self._option.delete(0, 'end')
		if not isinstance(value, basestring):
			# set to most recently used file
			try:
				from OpenSave.miller import _prefs
			except ImportError:
				return
			try:
				historyID = self._dialogKw['historyID']
				history = _prefs['fileHistory'][historyID]
			except KeyError:
				return
			if not history:
				return
			value = history[0]
		self._option.insert(0, value)
		width = int(self._option["width"])
		if len(value) > width:
			self._option.xview_scroll(len(value) - width, "units")
		
	def _nukeDialog(self, event=None):
		if self._dialog:
			self._dialog.destroy()
			self._dialog = None

	def _startDialog(self):
		if not self._dialog:
			def setEntry(okayed, dialog, self=self):
				if okayed:
					self.set(dialog.getPaths()[0])
					self._return()
			from OpenSave import OpenBase
			if issubclass(self.dialogType, OpenBase):
				default = 'Set Input Location'
			else:
				default = 'Set Output Location'
			self._dialog = self.dialogType(command=setEntry,
					multiple=False, default=default,
					**self._dialogKw)
		self._dialog.enter()

class InputFileOption(_BaseFileOption):
	"""Get an input file.  See _BaseFileOption for more info."""
	def __init__(self, *args, **kw):
		from OpenSave import OpenModeless
		self.dialogType = OpenModeless
		_BaseFileOption.__init__(self, *args, **kw)

class OutputFileOption(_BaseFileOption):
	"""Get an output file.  See _BaseFileOption for more info."""
	def __init__(self, *args, **kw):
		from OpenSave import SaveModeless
		self.dialogType = SaveModeless
		_BaseFileOption.__init__(self, *args, **kw)

class FileOption(Option):
	"""Get a file name
	
	   Keyword argument 'initVal' is the initial value of the file name
	   (default empty string).
	   Keyword argument 'entryWidth' controls the width of the entry field
	   (default 10).
	"""

	def _addOption(self, row, col, entryWidth=10, **kw):
		self._option = Tix.FileEntry(self._master,
				command=self._set, 
				options="entry.width %d" % entryWidth, **kw)
		if row == -1:
			self._option.pack(side=Tk.RIGHT)
		else:
			self._option.grid(row=row, column=col, sticky=Tk.W)
		chimera.help.register(self._option.button,
				balloon="Browse filesystem for file name")
	
	def get(self, doInvoke=1):
		"""text entered in the entry widget without the Return
		   key being hit is not reflected when the FileEntry widget
		   is queried.  Use invoke() to force an update.  If you are
		   in a callback from this option when calling get(), use the
		   doInvoke=0 keyword option to suppress further invoke()s.
		"""
		if doInvoke:
			self._option.invoke()
		return self._option.cget('value')

	def set(self, value):
		self._option.configure(value=value)

baseOFLOption = CGLtk.OrderedListOption.OrderedFileListOption
class OrderedFileListOption(Option):
	"""Allow CGLtk's OrderedFileListOption to be used as an option"""

	def _addOption(self, row, col, **kw):
		border = Tk.Frame(self._master, relief='ridge', bd=4)
		class OFLoption(baseOFLOption):
			# override 'addItem' and 'removeItem' and 'moveItem'
			# so that _set gets called
			def __init__(self, *args, **kw):
				self.__self = kw['sself']
				del kw['sself']
				baseOFLOption.__init__(self, *args, **kw)
			def addItem(self, name, item):
				baseOFLOption.addItem(self, name, item)
				self.__self._set()
			def delete(self):
				baseOFLOption.delete(self)
				self.__self._set()
			def deleteAll(self):
				baseOFLOption.deleteAll(self)
				self.__self._set()
			def removeItem(self, item):
				baseOFLOption.removeItem(self, item)
				self.__self._set()
			def moveItem(self, item, before):
				baseOFLOption.moveItem(self, item, before)
				self.__self._set()
		import tkgui
		import preferences
		if preferences.get(tkgui.GENERAL,
					tkgui.PATH_STYLE) == tkgui.PATH_NEXT:
			self.pathStyle = 'NeXT'
		else:
			self.pathStyle = 'normal'
				
		kw['pathStyle'] = self.pathStyle
		kw['sself'] = self
		self._option = OFLoption(border, **kw)
		if row == -1:
			border.pack(side=Tk.RIGHT)
		else:
			border.grid(row=row, column=col, sticky="nsew")
			self._master.rowconfigure(row, weight=1)
		self._option.pack(expand=1, fill="both")
	
	def _createVar(self):
		# no explicit tracking of list
		pass
	
	def set(self, value):
		for fileDir, path in self._option.items():
			self._option.removeItem(path)
		
		import os.path
		for filename in value:
			if self.pathStyle == 'normal':
				self._option.addItem(filename, filename)
			else:
				dir, name = os.path.split(filename)
				if not dir:
					dir = "(current directory)"
				self._option.addItem('%s - %s'
							% (name, dir), filename)
	
	def get(self):
		return map(lambda x: x[1], self._option.items())
	
	def setMultiple(self):
		raise RuntimeError, "%s does not implement setMultiple()" % (
							self.__class__.__name__)
	
	def enable(self):
		self._option.outline.unlock()
	
	def disable(self):
		self._option.outline.lock()
	

baseODLOption = CGLtk.OrderedListOption.OrderedDirListOption
class OrderedDirListOption(Option):
	"""Allow CGLtk's OrderedDirListOption to be used as an option"""

	def _addOption(self, row, col, **kw):
		border = Tk.Frame(self._master, relief='ridge', bd=4)
		class ODLoption(baseODLOption):
			# override 'addItem' and 'removeItem' and 'moveItem'
			# so that _set gets called
			def __init__(self, master, *args, **kw):
				self.__self = kw['sself']
				del kw['sself']
				self.master = master
				baseODLOption.__init__(self, master,
								*args, **kw)
			def add(self):
				if not hasattr(self, 'dirPick'):
					from OpenSave import OpenModal
					class SimpleOpenModal(OpenModal):
						def run(self, master):
							return OpenModal.run(
							self, master)[0][0]
					self.dirPick = SimpleOpenModal(
						title=self.dirPrompt,
						initialdir=self.startDir,
						dirsOnly=True)
				baseODLOption.add(self, self.master)
			def addItem(self, name, item):
				baseODLOption.addItem(self, name, item)
				self.__self._set()
			def delete(self):
				baseODLOption.delete(self)
				self.__self._set()
			def deleteAll(self):
				baseODLOption.deleteAll(self)
				self.__self._set()
			def removeItem(self, item):
				baseODLOption.removeItem(self, item)
				self.__self._set()
			def moveItem(self, item, before):
				baseODLOption.moveItem(self, item, before)
				self.__self._set()
				
		kw['sself'] = self
		self._option = ODLoption(border, **kw)
		if row == -1:
			border.pack(side=Tk.RIGHT)
		else:
			border.grid(row=row, column=col, sticky="nsew")
			self._master.rowconfigure(row, weight=1)
		self._option.pack(expand=1, fill="both")
	
	def _createVar(self):
		# no explicit tracking of list
		pass
	
	def set(self, value):
		for item in self._option.items():
			self._option.removeItem(item)
		
		for item in value:
			self._option.addItem(item, item)
	
	def get(self):
		return map(lambda x: x[1], self._option.items())
	
	def setMultiple(self):
		raise RuntimeError, "%s does not implement setMultiple()" % (
							self.__class__.__name__)
	
	def enable(self):
		self._option.outline.unlock()
	
	def disable(self):
		self._option.outline.lock()
	
# bunch of options specific enough that they know what their balloon help,
# name, defaults, etc. should be...
class RibbonXSectionOption(EnumOption):
	name = "ribbon cross section"
	attribute = "ribbonDrawMode"
	default = "rounded"
	inClass = chimera.Residue

	def __init__(self, *args, **kw):
		from RibbonStyleEditor import xsection
		self.values = xsection.listXSections(all=True)
		self.values.sort()
		chimera.triggers.addHandler(xsection.Trigger, self._updateMenu,
						None)
		EnumOption.__init__(self, *args, **kw)

	def _updateMenu(self, *args):
		from RibbonStyleEditor import xsection
		self.values = xsection.listXSections(all=True)
		self.values.sort()
		self.remakeMenu()

	def getAttribute(self, item, attrName):
		from RibbonStyleEditor import xsection
		return xsection.getXSectionName(item)

	def setAttribute(self, item, attrName, value):
		from RibbonStyleEditor import xsection
		return xsection.setXSectionByName(item, value)

class RibbonScalingOption(EnumOption):
	name = "ribbon scaling"
	attribute = "ribbonStyle"
	default = "Chimera default"
	inClass = chimera.Residue

	def __init__(self, *args, **kw):
		from RibbonStyleEditor import scaling
		self.values = scaling.listScalings(all=True)
		self.values.sort()
		chimera.triggers.addHandler(scaling.Trigger, self._updateMenu,
						None)
		EnumOption.__init__(self, *args, **kw)

	def _updateMenu(self, *args):
		from RibbonStyleEditor import scaling
		self.values = scaling.listScalings(all=True)
		self.values.sort()
		self.remakeMenu()

	def getAttribute(self, item, attrName):
		from RibbonStyleEditor import scaling
		return scaling.getScalingName(item)

	def setAttribute(self, item, attrName, value):
		from RibbonStyleEditor import scaling
		return scaling.setScalingByName(item, value)

class RibbonDisplayOption(BooleanOption):
	labels = ["off", "on"]
	name = "ribbon display"
	attribute = "ribbonDisplay"
	default = 0
	inClass = chimera.Residue

class AtomDrawModeOption(SymbolicEnumOption):
	labels = ("dot", "ball", "endcap", "sphere")
	values = (chimera.Atom.Dot, chimera.Atom.Ball,
				chimera.Atom.EndCap, chimera.Atom.Sphere)
	name = "atom style"
	attribute = "drawMode"
	balloon = "How atoms are drawn.\n" \
			"'dot' is used in wireframes.\n" \
			"'ball' is for ball-and-stick.\n" \
			"'endcap' ends sticks for stick only.\n" \
			"'sphere' is for space-filling."
	default = chimera.Atom.Dot
	inClass = chimera.Atom

class BondDrawModeOption(SymbolicEnumOption):
	labels = ("wire", "stick")
	values = (chimera.Bond.Wire, chimera.Bond.Stick)
	name = "bond style"
	attribute = "drawMode"
	balloon = "How bonds are depicted"
	default = chimera.Bond.Wire
	inClass = [chimera.Bond, chimera.PseudoBond]

class MoleculeColorOption(ColorOption):
	name = "color"
	attribute = "color"
	balloon = "Color of model regions where residue\n" \
		"and/or atom colors have not been specified"
	default = "gray"
	inClass = chimera.Molecule

class InsideRibbonColorOption(ColorOption):
	name = "ribbon inside color"
	attribute = "ribbonInsideColor"
	balloon = "Inside color of ribbons of helices"
	inClass = chimera.Molecule

class PseudoBondGroupColorOption(MoleculeColorOption):
	name = "color"
	balloon="Color of pseudobonds in this group\n" \
		"that don't otherwise have a color set\n" \
		"(ignored if halfbond mode is on)"
	inClass = chimera.PseudoBondGroup

class LineWidthOption(FloatOption):
	name = "line width"
	attribute = "lineWidth"
	balloon = "Width of wire-frame bonds (in pixels)"
	default = 1.0
	min = 0.01
	inClass = [chimera.PseudoBondGroup, chimera.Molecule]

class StickScaleOption(FloatOption):
	name = "stick scale"
	attribute = "stickScale"
	balloon = "Size of stick bonds (as fraction of bond radius)"
	default = 1.0
	min = 0.01
	inClass = [chimera.PseudoBondGroup, chimera.Molecule]

class BallScaleOption(FloatOption):
	name = "ball scale"
	attribute = "ballScale"
	balloon = "Size of ball atoms (as fraction of atom radius)"
	default = 0.25
	min = 0.01
	inClass = chimera.Molecule

class AutoChainOption(BooleanOption):
	labels = ["off", "on"]
	name = "auto-chaining"
	attribute = "autochain"
	balloon = "Automatically draw 'bond' between consecutive\n" \
		"connected residues when connecting bonds are hidden"
	default = 1
	inClass = chimera.Molecule

class RibbonHideBackboneOption(BooleanOption):
	name = "ribbon hides backbone atoms"
	attribute = "ribbonHidesMainchain"
	balloon = "Hide backbone atoms when ribbon is displayed"
	default = 1
	inClass = chimera.Molecule

booleanDisplayName = "displayed"
class BondDisplayModeOption(SymbolicEnumOption):
	labels = ["true", "false", "if atoms shown"]
	values = [chimera.Bond.Always, chimera.Bond.Never, chimera.Bond.Smart]
	name = booleanDisplayName
	attribute = "display"
	balloon = "Bond display can be on/off or\n" \
			"set to display only if both\n" \
			"endpoint atoms are displayed"
	default = chimera.Bond.Smart
	inClass = [chimera.Bond, chimera.PseudoBond]

class ModelActiveOption(BooleanOption):
	name = "active"
	attribute = "openState.active"
	balloon = "Model responsive to mouse"
	default = 1
	triggerClass = chimera.OpenState
	reason = 'active change'
	inClass = chimera.Model
	exceptClass = chimera.PseudoBondGroup

class ModelDisplayOption(BooleanOption):
	name = booleanDisplayName
	attribute = "display"
	balloon = "show/hide model"
	default = 1
	inClass = chimera.Model

class AtomDisplayOption(BooleanOption):
	name = booleanDisplayName
	attribute = "display"
	balloon = "show/hide atom"
	default = 1
	inClass = chimera.Atom

class DotSizeOption(FloatOption):
	name = "vdw dot size"
	attribute = "pointSize"
	balloon = "Size of vdw dots (in pixels)"
	default = 1
	min = 0.01
	inClass = chimera.Molecule

class VdwDensityOption(FloatOption):
	name = "vdw density"
	attribute = "vdwDensity"
	balloon = "Density of vdw surface dots\n" \
		"(dots per 0.2 square angstroms)"
	default = 5
	min = 0.01
	inClass = chimera.Molecule

class LineTypeOption(ImageEnumOption):
	name = "line style"
	balloon = "Draw wireframe bonds in given style"
	default = chimera.SolidLine
	values = (chimera.SolidLine, chimera.Dash, chimera.Dot, chimera.DashDot, chimera.DashDotDot)
	images = ('solid.xbm', 'dash.xbm', 'dot.xbm', 'dashdot.xbm', 'dashdotdot.xbm')
	attribute = "lineType"
	attrValuesBalloon = "values: %d solid, %d dashed, %d dotted,\n%d dash-dot, %d dash-dot-dot" % values
	inClass = [chimera.Molecule, chimera.PseudoBondGroup]

class HalfbondOption(SymbolicEnumOption):
	labels = ["on", "off"]
	values = [1, 0]
	name = "halfbond mode"
	attribute = "halfbond"
	balloon = "If halfbond mode is on, bonds are colored in\n" \
		"two halves: each is the color of its endpoint\n" \
		"atom.  Otherwise the bond uses its own color."
	inClass = [chimera.Bond, chimera.PseudoBond]

class SurfaceReprOption(SymbolicEnumOption):
	labels = ["solid", "mesh", "dots"]
	values = [0, 1, 2]
	default = values[0]
	name = "representation"
	attribute = "drawMode"
	balloon = "Representation of MSMS surface:\n" \
		"'solid' draws filled triangles between surface points\n" \
		"'mesh' draws lines between surface points\n" \
		"'dots' draws only the surface points"
	inClass = chimera.MSMSModel

class SurfaceColorSourceOption(SymbolicEnumOption):
	labels = ["model", "atoms", "unknown"]
	values = [ chimera.MSMSModel.ByMolecule,
		   chimera.MSMSModel.ByAtom,
		   chimera.MSMSModel.Custom
		 ]
	default = values[1]
	name = "color source"
	attribute = "colorMode"
	balloon = "Source of surface colors:\n" \
		"'model' means the entire surface\n" \
		"    is the model-level color\n" \
		"'atoms' colors with atom-level colors\n" \
		"'unknown' means the surface is colored with\n"\
		"    a custom color scheme, typically provided\n" \
		"    by an extension (e.g. Delphi)"
	inClass = chimera.MSMSModel

	def display(self, items):
		# disable "unknown" if inapplicable
		SymbolicEnumOption.display(self, items)

		if not hasattr(self, "menu"):
			return

		state = "normal"
		for surf in items:
			if not surf.customColors:
				state = "disabled"
				break
		index = self.labels.index("unknown")
		self.menu.entryconfigure(index, state=state)

class SurfaceProbeRadiusOption(FloatOption):
	name = "probe radius"
	attribute = "probeRadius"
	balloon= "Radius of probe sphere used to\n" \
		"compute surface (in angstroms)"
	min = 0.5
	max = 11.0
	default = 1.4
	inClass = chimera.MSMSModel

class SurfaceDensityOption(FloatOption):
	name = "vertex density"
	attribute = "density"
	balloon="Density of surface vertices\n" \
		" (vertices per square angstrom)"
	# from msms code
	min = 0.3
	max = 100.0
	default = 2.0
	inClass = chimera.MSMSModel

class SurfaceLineWidthOption(LineWidthOption):
	name = "line width"
	attribute = "lineWidth"
	balloon = "Width of mesh line (in pixels)"
	default = 1.0
	inClass = chimera.MSMSModel

class SurfaceDotSizeOption(DotSizeOption):
	name = "dot size"
	attribute = "pointSize"
	balloon = "Size of surface dots (in pixels)"
	default = 1
	inClass = chimera.MSMSModel

class SurfaceDisjointOption(BooleanOption):
	name = "show disjoint surfaces"
	attribute = "allComponents"
	balloon = "select whether disjoint surfaces are shown"
	default = True
	inClass = chimera.MSMSModel
	
class RibbonColorOption(ColorOption):
	name = "ribbon color"
	attribute = "ribbonColor"
	balloon = "color of ribbon depiction"
	inClass = chimera.Residue

class AtomSurfaceDisplayOption(BooleanOption):
	name = "surface displayed"
	attribute = "surfaceDisplay"
	balloon="show/hide surface for this atom"
	inClass = chimera.Atom

class AtomBondRadiusOption(FloatOption):
	name = "radius"
	attribute = "radius"
	balloon = "radius (in angstroms)"
	min = 1e-10
	inClass = [chimera.Atom, chimera.Bond, chimera.PseudoBond]

class AtomBondColorOption(ColorOption):
	name = "color"
	attribute = "color"
	inClass = [chimera.Atom, chimera.Bond, chimera.PseudoBond]

class AtomBondLabel(StringOption):
	name = "label"
	attribute = "label"
	inClass = [chimera.Atom, chimera.Bond,
					chimera.PseudoBond, chimera.Residue]

class AtomBondLabelColor(ColorOption):
	name = "label color"
	attribute = "labelColor"
	inClass = [chimera.Atom, chimera.Bond,
					chimera.PseudoBond, chimera.Residue]

class ResidueHelixOption(BooleanOption):
	name = "in helix"
	attribute = "isHelix"
	balloon = "residue is part of helical secondary structure"
	inClass = chimera.Residue

class ResidueStrandOption(BooleanOption):
	name = "in strand"
	attribute = "isSheet"
	balloon = "residue is part of strand secondary structure"
	inClass = chimera.Residue
	
class PhiOption(FloatOption):
	noneValues = True
	name = "phi angle"
	attribute = "phi"
	balloon = u"amino acid \N{GREEK CAPITAL LETTER PHI} angle"
	inClass = chimera.Residue

class PsiOption(FloatOption):
	noneValues = True
	name = "psi angle"
	attribute = "psi"
	balloon = u"amino acid \N{GREEK CAPITAL LETTER PSI} angle"
	inClass = chimera.Residue

class Chi1Option(FloatOption):
	noneValues = True
	name = "chi1 angle"
	attribute = "chi1"
	balloon = u"amino acid \N{GREEK CAPITAL LETTER CHI}\N{SUBSCRIPT ONE} angle"
	inClass = chimera.Residue

class Chi2Option(FloatOption):
	noneValues = True
	name = "chi2 angle"
	attribute = "chi2"
	balloon = u"amino acid \N{GREEK CAPITAL LETTER CHI}\N{SUBSCRIPT TWO} angle"
	inClass = chimera.Residue

class Chi3Option(FloatOption):
	noneValues = True
	name = "chi3 angle"
	attribute = "chi3"
	balloon = u"amino acid \N{GREEK CAPITAL LETTER CHI}\N{SUBSCRIPT THREE} angle"
	inClass = chimera.Residue

class Chi4Option(FloatOption):
	noneValues = True
	name = "chi4 angle"
	attribute = "chi4"
	balloon = u"amino acid \N{GREEK CAPITAL LETTER CHI}\N{SUBSCRIPT FOUR} angle"
	inClass = chimera.Residue

class RibbonColorOption(ColorOption):
	name = "ribbon color"
	attribute = "ribbonColor"
	balloon = "color of ribbon depiction"
	inClass = chimera.Residue

class AtomMoleculeSurfaceColorOption(ColorOption):
	name = "surface color"
	attribute = "surfaceColor"
	balloon = "color of molecular surface"
	inClass = [chimera.Atom, chimera.Molecule]

class AtomMoleculeSurfaceOpacityOption(FloatOption):
	name = "surface opacity"
	attribute = "surfaceOpacity"
	max = 1.0
	balloon = "Opacity of the surface:\n" \
		"  1.0 is completely opaque\n" \
		"  0.0 is completely transparent\n" \
		"  a negative value means that the opacity value\n" \
		"    of the surface color is used"
	inClass = [chimera.Atom, chimera.Molecule]

class TrackMoleculeOption(BooleanOption):
	name = "track molecule"
	attribute = "trackMolecule"
	balloon = "if true, changes in the molecule's attributes\n" \
		  "automatically cause identical changes in the\n" \
		  "chain's attributes (if applicable)"
	inClass = chimera.ChainTrace

class IdatmTypeOption(EnumOption):
	import idatm
	values = idatm.typeInfo.keys()
	values.sort()

	name = "IDATM type"
	attribute = "idatmType"
	balloon = "atom's type as per IDATM algorithm (e.g. C3 is sp3 carbon)"
	inClass = chimera.Atom

	def __init__(self, *args, **kw):
		EnumOption.__init__(self, *args, **kw)
		self.disable()

class NamingStyleOption(SymbolicEnumOption):
	name = "Naming style"
	labels = ["simple", "command-line specifier", "serial number"]
	values = ["simple", "osl", "serial number"]
	default = "simple"
	balloon = "format atom/residue names in command-line specifier\n" \
		"\tstyle, simple (e.g. ALA 41 CA) style, or just\n" \
		"\twith atom serial number"

class FillRingDisplayOption(BooleanOption):
	name = "filled ring display"
	balloon = "show/display filled rings"
	attribute = "fillDisplay"
	inClass = chimera.Residue

class FillRingModeOption(SymbolicEnumOption):
	name = "filled ring style"
	balloon = "How rings are filled"
	default = chimera.Residue.Thick
	values = (chimera.Residue.Thin, chimera.Residue.Thick)
	labels = ("thin", "thick")
	attribute = "fillMode"
	inClass = chimera.Residue

class AromaticLineTypeOption(LineTypeOption):
	name = "aromatic line style"
	balloon = "draw aromatic ring circles in given style"
	default = chimera.Dash
	attribute = "aromaticLineType"
	inClass = chimera.Molecule

class AromaticColorOption(ColorOption):
	name = "aromatic color"
	balloon = "aromatic ring annotation color"
	attribute = "aromaticColor"
	inClass = chimera.Molecule

class AromaticDisplayOption(BooleanOption):
	name = "aromatic display"
	balloon = "show/display aromatic rings"
	attribute = "aromaticDisplay"
	inClass = chimera.Molecule

class AromaticModeOption(SymbolicEnumOption):
	name = "aromatic ring style"
	balloon = "how aromatic rings are depicted"
	default = chimera.Molecule.Disk
	values = (chimera.Molecule.Circle, chimera.Molecule.Disk)
	labels = ("circle", "disk")
	attribute = "aromaticMode"
	inClass = chimera.Molecule

class CategoryOption(StringOption):
	name = "category"
	balloon = "pseudobond classification"
	default = ""
	attribute = "category"
	inClass = chimera.PseudoBondGroup
	readOnly = True

class InspectionInfo:
	"""class for tracking info used by selection inspector"""
	displayAs = {}
	inspectables = []
	_callbacks = []

	def register(self, klass, displayAs=None):
		"""Register a class with the selection inspector"""
		if not issubclass(klass, chimera.Selectable):
			raise TypeError, "%s must inherit from chimera." \
				"Selectable to be registered as an inspectable"\
				% klass.__name__
		if not chimera.triggers.hasTrigger(klass.__name__):
			raise NameError, "%s must be in chimera.triggers" \
				" to be registered as an inspectable" % (
				klass.__name__)
		self.inspectables.append(klass)
		if displayAs:
			self.displayAs[klass] = displayAs
		for cb in self._callbacks:
			cb(klass)

	def registerCB(self, cb):
		"""register a callback for when an inspectable is registered

		   the callback will be given the inspectable as an argument
		"""
		self._callbacks.append(cb)

	def deregisterCB(self, cb):
		"""deregister a callback previously registered via registerCB"""
		self._callbacks.remove(cb)

	
inspectionInfo = InspectionInfo()

class AttributeHeader(Tk.Frame):
	def __init__(self, master, **kw):
		if 'collapsible' in kw:
			collapsible = kw['collapsible']
			del kw['collapsible']
		else:
			if 'composite' in kw:
				collapsible = kw['composite']
			else:
				collapsible = False
		if collapsible:
			self.widgetClass = Tk.Checkbutton
			self.expandedVar = Tk.IntVar(master)
			if 'collapsed' in kw:
				collapsed = kw['collapsed']
				del kw['collapsed']
			else:
				collapsed = collapsible
			self.expandedVar.set(not collapsed)
			kw['variable'] = self.expandedVar
			kw['command'] = self.collapseChange
			if 'anchor' not in kw:
				kw['anchor'] = 'w'
		else:
			self.widgetClass = Tk.Label
			collapsed = False

		if 'bg' not in kw and 'background' not in kw:
			kw['bg'] = "#8fff80008000"
		if 'relief' not in kw:
			kw['relief'] = 'ridge'
		if 'klass' in kw and 'text' not in kw:
			if isinstance(kw['klass'], basestring):
				className = kw['klass']
			else:
				className = kw['klass'].__name__
			text = className + " Attributes"
			if 'composite' in kw:
				if kw['composite']:
					text = "Component " + text
			kw['text'] = text
			del kw['klass']
		if 'composite' in kw:
			del kw['composite']
		Tk.Frame.__init__(self, master)
		self.columnconfigure(0, weight=1)
		self.header = self.widgetClass(self, **kw)
		self.header.grid(row=0, sticky='ew')
		self.frame = Tk.Frame(self)
		self.frameGridKw = { 'row': 1 }
		if not collapsed:
			self.frame.grid(**self.frameGridKw)
		self.frameRow = 0

	def addOption(self, opt, *args, **kw):
		widget = opt(self.frame, self.frameRow, *args, **kw)
		self.frameRow += 1
		return widget

	def addWidget(self, widgetClass, **kw):
		widget = widgetClass(self.frame, **kw)
		widget.grid(row=self.frameRow, columnspan=2)
		self.frameRow += 1
		return widget

	def collapseChange(self):
		if self.expandedVar.get():
			self.frame.grid(**self.frameGridKw)
		else:
			self.frame.grid_forget()

def optionSortFunc(a, b):
	if hasattr(a, 'sorting'):
		sortA = a.sorting
	else:
		sortA = a.name
	if hasattr(b, 'sorting'):
		sortB = b.sorting
	else:
		sortB = b.name
	return cmp(sortA.lower(), sortB.lower())

_optionCache = {}
_withBasesCache = {}
_registeredOptions = []
def getOptionsForClass(optClass, baseClassOptions=True):
	"""return a list of all the options applicable to 'optClass'

	   if 'baseClassOptions' then include base-class options in the list.
	"""
	from types import ClassType
	global _optionCache, _withBasesCache, _registeredOptions
	if not _optionCache:
		for gv in globals().values():
			if not isinstance(gv, type):
				continue
			if not issubclass(gv, Option):
				continue
			if not hasattr(gv, "inClass"):
				continue
			classes = gv.inClass
			if isinstance(classes, (type, ClassType)):
				classes = [classes]
			for c in classes:
				try:
					options = _optionCache[c]
				except KeyError:
					options = _optionCache[c] = []
				options.append(gv)
		for opts in _optionCache.values():
			opts.sort(optionSortFunc)
	if _registeredOptions:
		_withBasesCache = {}
		needSort = set()
		for ro in _registeredOptions:
			try:
				classes = ro.inClass
			except AttributeError:
				chimera.replyobj.error("Mandatory 'inClass'"
					" attribute missing from Option %s"
					% ro.__class__.__name__)
				continue
			if isinstance(classes, (type, ClassType)):
				classes = [classes]
			for klass in classes:
				if klass in _optionCache:
					options = _optionCache[klass]
				else:
					options = _optionCache[klass] = []
				options.append(ro)
				needSort.add(klass)
		for klass in needSort:
			_optionCache[klass].sort(optionSortFunc)
		_registeredOptions = []
	if baseClassOptions:
		# fold in options from base classes
		if optClass not in _withBasesCache:
			fullOpts = _optionCache.get(optClass, [])[:]
			family = [optClass]
			bases = list(optClass.__bases__)
			family.extend(bases)
			while bases:
				base = bases.pop()
				bases += list(base.__bases__)
				family.extend(list(base.__bases__))
				if base not in _optionCache:
					continue
				for opt in _optionCache[base]:
					if hasattr(opt, 'exceptClass') \
					and opt.exceptClass in family:
						continue
					fullOpts.append(opt)
			fullOpts.sort(optionSortFunc)
			_withBasesCache[optClass] = fullOpts
		return _withBasesCache[optClass][:]
	return _optionCache.get(optClass, [])[:]
	
def registerOptions(options):
	_registeredOptions.extend(options)
