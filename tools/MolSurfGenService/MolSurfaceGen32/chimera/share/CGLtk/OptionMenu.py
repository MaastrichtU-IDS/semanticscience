# TODO: merge with Pmw.OptionMenu and CGLtk.CascadeOptionMenu uses.
import Tkinter as Tk

class OptionMenu(Tk.Menubutton):
	"""Like Tkinter's OptionMenu, with major differences.  (1) The
	values are given as a list, and may be nested -- first item is the
	name of the submenu (except for the first list).  (2) A value with
	a single dash becomes a menu separator, and a value with a single
	| becomes a column break.  (3) The menu may be made incrementally,
	so individual entries can have images.  (4) The variable is optional,
	so get and set methods are provided."""

	def __init__(self, master, values=[], variable=None, command=None, **kw):
		if kw:
			raise Tk.TclError('unknown option -' + kw.keys()[0])
		if command is not None:
			kw['command'] = command
		if variable is None:
			variable = Tk.StringVar(master)
		# defaults from tk8.5/library/optMenu.tcl
		defaults = {
			'anchor': 'c',
			'direction': 'flush',
			'highlightthickness': 1,
			'indicatoron': 1,
			'relief': Tk.RAISED,
			'textvariable': variable,
		}
		Tk.Widget.__init__(self, master, "menubutton", defaults)
		menu = self.__menu = Tk.Menu(self, name="menu", tearoff=0)
		self["menu"] = menu
		self.__var = variable
		self.add_buttons(values, **kw)

	def __getitem__(self, name):
		if name == 'menu':
			return self.__menu
		return Tk.Widget.__getitem__(self, name)

	def destroy(self):
		"""Destroy this widget and the associated menu."""
		Tk.Menubutton.destroy(self)
		self.__menu = None

	def clear(self):
		self.__menu.delete(0, Tk.END)

	def get(self):
		return self.__var.get()

	def set(self, value):
		return self.__var.set(value)

	def add_buttons(self, values=[], menu=None, **kw):
		for v in values:
			if isinstance(v, basestring):
				if v == '-':
					self.add_separator(menu=menu, **kw)
				elif v == '|':
					self.add_column(menu=menu, **kw)
				else:
					self.add_button(v, menu=menu, **kw)
			elif hasattr(v, '__iter__'):
				cascade = self.add_cascade(v[0], menu=menu, **kw)
				self.add_buttons(values=v[1:], menu=cascade, **kw)
			else:
				self.add_button(str(v), menu=menu, **kw)

	def add_column(self, menu=None, **kw):
		if menu is None:
			menu = self.__menu
		menu.entryconfigure(Tk.END, columnbreak=1, **kw)

	def add_separator(self, menu=None, **kw):
		if menu is None:
			menu = self.__menu
		menu.add_separator(**kw)

	def add_cascade(self, name, menu=None, **kw):
		if menu is None:
			menu = self.__menu
		defaults = {
			'label': name,
			'tearoff': 0,
		}
		defaults.update(kw)
		menu.add_cascade(**defaults)

	def add_button(self, value, menu=None, **kw):
		if not self.__var.get():
			self.__var.set(value)
		defaults = {
			'label': value,
			'selectcolor': 'black',
			'variable': self.__var,
		}
		defaults.update(kw)
		self.__menu.add_radiobutton(**defaults)

################

## optMenu.tcl --
#
#proc ::tk_optionMenu {w varName firstValue args} {
#    upvar #0 $varName var
#
#    if {![info exists var]} {
#	set var $firstValue
#    }
#    menubutton $w -textvariable $varName -indicatoron 1 -menu $w.menu \
#	    -relief raised -highlightthickness 1 -anchor c \
#	    -direction flush
#    menu $w.menu -tearoff 0
#    $w.menu add radiobutton -label $firstValue -variable $varName
#    foreach i $args {
#    	$w.menu add radiobutton -label $i -variable $varName
#    }
#    return $w.menu
#}
