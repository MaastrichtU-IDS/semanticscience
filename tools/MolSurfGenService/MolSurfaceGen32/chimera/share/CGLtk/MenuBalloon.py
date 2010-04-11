# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---
#
# $Id: MenuBalloon.py 26655 2009-01-07 22:02:30Z gregc $

import os
import Tkinter
import Pmw

class MenuBalloon(Pmw.MegaToplevel):
    def __init__(self, menu, parent = None, **kw):

	# Define the megawidget options.
	optiondefs = (
	    ('initwait',          500,            None), # milliseconds
	    ('label_background',  'lightyellow',  None),
	    ('label_foreground',  'black',        None),
	    ('label_justify',     'left',         None),
            ('master',            'parent',       None),
            ('relmouse',          'both',         self._relmouse),
	    ('state',             'both',         self._state),
	    ('statuscommand',     None,           None),
	    ('xoffset',           20,             None), # pixels
	    ('yoffset',           1,              None), # pixels
	)
	self.defineoptions(kw, optiondefs)

	# Initialise the base class (after defining the options).
	Pmw.MegaToplevel.__init__(self, parent)

	self.withdraw()
	self.overrideredirect(1)

	# Create the components.
	interior = self.interior()
	self._label = self.createcomponent('label',
		(), None,
		Tkinter.Label, (interior,))
	self._label.pack()

        # This gives a black border around the balloon, but avoids a
        # black 'flash' when the balloon is deiconified, before the
        # text appears.
	self.configure(
                hull_highlightthickness = 1,
                hull_highlightbackground = 'black',
                hull_background = self._label.cget('background'),
        )

	# Initialise instance variables.
	self._timer = None
	self._menu = menu
	self._bindings = {}
	self._tearoffMap = {}
	
	# Check keywords and initialise options.
	self.initialiseoptions(MenuBalloon)

    def clear(self):
	for menu in self._bindings.keys():
	    # since we're not explicitly unbinding events, if the main menu
	    # is in _bindings (and therefore has event handlers bound), just
	    # reset the dictionary instead of deleting it entirely (so new
	    # event handlers won't get bound later)
	    if menu == self._menu:
		self._bindings[menu] = {}
	    else:
		del self._bindings[menu]
	
    def destroy(self):
	if self._timer is not None:
	    self.after_cancel(self._timer)
	    self._timer = None
	Pmw.MegaToplevel.destroy(self)

    def bind(self, menuPath, balloonHelp, statusHelp = None):
	curMenu = self._menu
	for pathComp in menuPath[:-1]:
	    curMenu = curMenu.nametowidget(curMenu.entrycget(pathComp, "menu"))
	if not self._bindings.has_key(curMenu):
	    self._bindings[curMenu] = {}
	    curMenu.bind('<Enter>', self._enter)
	    curMenu.bind('<Motion>', self._motion)
	    curMenu.bind('<Leave>', self._leave)
	    curMenu.config(tearoffcommand=self._tearoffCB)

	menuItem = menuPath[-1]
	if balloonHelp is None and statusHelp is None:
	    try:
	        del self._bindings[curMenu][menuItem]
	    except:
		pass
	    return

	if statusHelp is None:
	    statusHelp = balloonHelp
	
	self._bindings[curMenu][menuItem] = (balloonHelp, statusHelp)

    def showstatus(self, statusHelp):
	if self['state'] in ('status', 'both'):
	    cmd = self['statuscommand']
	    if callable(cmd):
		cmd(statusHelp)

    def clearstatus(self):
        self.showstatus(None)

    def _state(self):
	if self['state'] not in ('both', 'balloon', 'status', 'none'):
	    raise ValueError, 'bad state option ' + repr(self['state']) + \
		': should be one of \'both\', \'balloon\', ' + \
		'\'status\' or \'none\''

    def _relmouse(self):
	if self['relmouse'] not in ('both', 'x', 'y', 'none'):
	    raise ValueError, 'bad relmouse option ' + repr(self['relmouse'])+ \
		': should be one of \'both\', \'x\', ' + '\'y\' or \'none\''

    def _enter(self, event):
	if self._timer is not None:
	    self.after_cancel(self._timer)
	    self._timer = None

	menu = self._getMenuFromEvent(event)
	if not menu or menu.type('@%d' % event.y) not in ('menu', 'command'):
	    self._curEntry = None
	    return
	self._curEntry = menu.entrycget('@%d' % event.y, 'label')

	if not self._bindings[menu].has_key(self._curEntry):
	    return

	balloonHelp, statusHelp = self._bindings[menu][self._curEntry]
	if balloonHelp is not None and self['state'] in ('balloon', 'both'):
	    self._timer = self.after(self['initwait'], 
		    lambda self = self, widget = menu, help = balloonHelp:
		    self._showBalloon(widget, help))

	self.showstatus(statusHelp)

    def _leave(self, event):
	if self._timer is not None:
	    self.after_cancel(self._timer)
	    self._timer = None
	self.withdraw()
	self.clearstatus()

    def _motion(self, event):
	menu = self._getMenuFromEvent(event)
	if not menu or menu.type('@%d' % event.y) not in ('menu', 'command'):
	    curEntry = None
	else:
	    curEntry = menu.entrycget('@%d' % event.y, 'label')
	if curEntry == self._curEntry:
		return
	self._curEntry = curEntry

	self._leave(event)

	if not self._bindings[menu].has_key(self._curEntry):
	    return

	balloonHelp, statusHelp = self._bindings[menu][self._curEntry]
	if balloonHelp is not None and self['state'] in ('balloon', 'both'):
	    self._timer = self.after(self['initwait'], 
		    lambda self = self, widget = menu, help = balloonHelp:
		    self._showBalloon(widget, help))

	self.showstatus(statusHelp)

    def _showBalloon(self, widget, balloonHelp):

	self._label.configure(text = balloonHelp)

        # First, display the balloon offscreen to get dimensions.
        screenWidth = self.winfo_screenwidth()
        screenHeight = self.winfo_screenheight()
        self.geometry('+%d+0' % (screenWidth + 1))
        self.update_idletasks()

	leftrel = 0
        toprel = 0
	bottomrel = widget.winfo_height()

        xpointer, ypointer = widget.winfo_pointerxy()   # -1 if off screen

        if xpointer >= 0 and self['relmouse'] in ('both', 'x'):
            x = xpointer
        else:
            x = leftrel + widget.winfo_rootx()
        x = x + self['xoffset']

        if ypointer >= 0 and self['relmouse'] in ('both', 'y'):
            y = ypointer
        else:
            y = bottomrel + widget.winfo_rooty()
        y = y + self['yoffset']

        highlightthickness = self.cget('hull_highlightthickness')
        if x + self._label.winfo_reqwidth() > screenWidth:
            x = screenWidth - self._label.winfo_reqwidth() - highlightthickness

        if y + self._label.winfo_reqheight() > screenHeight:
            if ypointer >= 0 and self['relmouse'] in ('both', 'y'):
                y = ypointer
            else:
                y = toprel + widget.winfo_rooty()
            y = y - self._label.winfo_reqheight() - self['yoffset'] - \
                    highlightthickness

        Pmw.setgeometryanddeiconify(self, '+%d+%d' % (x, y))

    def _tearoffCB(self, origMenu, tearoffMenu):
	try:
		self._tearoffMap[tearoffMenu] = self._menu.nametowidget(
								origMenu)
	except KeyError:
		# nametowidget() failed; maybe the origMenu is a 
		# tearoff -- try again with mangled name
		try:
			mangled = origMenu[origMenu.rindex('.') + 1:]
			self._tearoffMap[tearoffMenu] = self._menu.nametowidget(
				mangled.replace('##', '.#'))
		except KeyError:
			print "Can't set up mapping from orig menu",\
				origMenu,"to tearoff",tearoffMenu

    def _getMenuFromEvent(self, event):
	menu = event.widget
	if isinstance(menu, basestring):
		# Hope to God it's a tearoff that we've registered...
		try:
			menu = self._tearoffMap[menu]
		except KeyError:
			return None
		# compensate for tearoff separator
		event.y = event.y + menu.yposition(1)
	return menu
