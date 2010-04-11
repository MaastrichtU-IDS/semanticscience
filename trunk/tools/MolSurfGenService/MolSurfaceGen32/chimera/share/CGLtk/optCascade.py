# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: optCascade.py 26655 2009-01-07 22:02:30Z gregc $

import Pmw
import Tkinter
import MenuBalloon

class CascadeOptionMenu(Pmw.OptionMenu):
	
    def __init__(self, parent = None, **kw):
	self.__balloon = None
	self.__val = None
	self.__legalVals = []
	if 'buttonStyle' in kw:
		self.buttonStyle = kw['buttonStyle']
		del kw['buttonStyle']
	else:
		self.buttonStyle = "arrow"
		# the other choice is "final"
	apply(Pmw.OptionMenu.__init__, (self, parent), kw)

	self.__balloon = self.createcomponent('balloon', (), None,
		MenuBalloon.MenuBalloon, (self._menu,))

    def setitems(self, items, index = None):

	# Set the items in the menu component.
        self._menu.delete(0, 'end')
	if self.__balloon:
		self.__balloon.clear()
	self.__legalVals = []
	self._itemList = self._fillMenu(self._menu, [], items)

	# Set the currently selected value.
	var = self._menubutton.cget('textvariable')

	if index is None:
	    if var != '':
		# None means do not change text variable.
		return
	    if len(items) == 0:
		menuText = buttonText = ''
	    else:
		menuText = buttonText = items[0]
	elif isinstance(index, list):
	    if index not in self.__legalVals:
		raise ValueError, "initial value not in items list"
	    menuText = index[0]

	    if self.buttonStyle == "arrow":
	 	buttonText = "->".join(index)
	    else:
	 	buttonText = index[-1]
	    self.__val = index
	else:
	    index = self.index(index)
	    menuText = buttonText = self._itemList[index]

	if var == '':
	    self._menubutton.configure(text = buttonText)
	else:
	    self._menu.tk.globalsetvar(var, menuText)

    def getvalue(self):
    	return self.__val

    def invoke(self, index = Pmw.SELECT):
	if index is None:
		return
	if isinstance(index, list):
	    if index not in self.__legalVals:
		raise ValueError, repr(index) + " not in menu"
	    commandArg = index
	    menuText = index[0]
	    if self.buttonStyle == "arrow":
	 	buttonText = "->".join(index)
	    else:
	 	buttonText = index[-1]
	    self.__val = index
	else:
	    index = self.index(index)
	    text = self._itemList[index]
	    commandArg = [text]
	    buttonText = menuText = text
	    self.__val = index

	var = self._menubutton.cget('textvariable')
	if var == '':
	    self._menubutton.configure(text = buttonText)
	else:
	    self._menu.tk.globalsetvar(var, menuText)

	command = self['command']
	if callable(command):
	    return command(commandArg)
    
    def _fillMenu(self, menu, prevMenuPath, items):
	itemList = []
        for item in items:
	    if isinstance(item, basestring):
		invokeArg = prevMenuPath + [item]
		menu.add_command(label = item, command =
		    lambda self = self, arg = invokeArg: self.invoke(arg))
		itemList.append(item)
		self.__legalVals.append(invokeArg)
	    else:
		badItemMsg = 'menu item must be sequence of length 2 or string'
		try:
		    if len(item) != 2:
			raise TypeError, badItemMsg
		except:
		    raise TypeError, badItemMsg
		
		menu.add_cascade(label = item[0], menu =
		    self._makeCascade(menu, prevMenuPath + [item[0]], item[1]))
		itemList.append(item[0])
	return itemList

    def _makeCascade(self, parentMenu, prevMenuPath, items):
	cascade = Tkinter.Menu(parentMenu, tearoff=0)
	self._fillMenu(cascade, prevMenuPath, items)
	return cascade
		
