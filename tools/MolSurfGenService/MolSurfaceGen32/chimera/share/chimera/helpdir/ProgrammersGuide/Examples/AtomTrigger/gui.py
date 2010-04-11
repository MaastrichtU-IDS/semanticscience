#    The code here is very similar to the code in "Colors
#    and Color Wells" and only differences from that code
#    will be described.
#
#    .. "Colors and Color Wells" Main_ColorWellUI.html

import os
import Tkinter

import chimera
from chimera.baseDialog import ModelessDialog
from chimera.tkoptions import ColorOption
import ColorWellUI

class ColorWellDialog(ModelessDialog):

    title = 'Set Backbone Color'

    #    Need to override '__init__' to initialize our extra state.
    def __init__(self, *args, **kw):

	#    Whereas in the "Colors and Color Wells" example 'coloropt'
	#    was a local variable, here the 'coloropt' variable is stored
	#    in the instance because the trigger handler (which has access
	#    to the instance) needs to update the color well contained in
	#    the ColorOption.  A new variable, 'handlerId', is created to
	#    keep track of whether a handler is currently registered.  The
	#    handler is only created when needed.  See 'map' and 'unmap'
	#    below.  (Note that the instance variables must be set before
	#    calling the base __init__ method since the dialog may be mapped
	#    during initialization, depending on which window system is used.)
	#
	#    .. "Colors and Color Wells" Main_ColorWellUI.html
	self.colorOpt = None
	self.handlerId = None

	#    Call the parent-class '__init__'.
	apply(ModelessDialog.__init__, (self,) + args, kw)

    def fillInUI(self, master):
	#    Save ColorOption in instance.
	self.coloropt = ColorOption(master, 0, 'Backbone Color', None, self._setBackboneColor, balloon='Protein backbone color')

	self._updateBackboneColor()

    def _updateBackboneColor(self):
	for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
	    for a in m.atoms:
		if ColorWellUI.MAINCHAIN.match(a.name):
		    try:
			if a.color != theColor:
			    self.coloropt.setMultiple()
			    return
		    except NameError:
			theColor = a.color

	try:
	    self.coloropt.set(theColor)
	except NameError:
	    self.coloropt.set(None)

    def _setBackboneColor(self, coloroption):
	ColorWellUI.mainchain(coloroption.get())

    #    Register a trigger handler to monitor changes in the
    #    backbone atom list when we're make visible.  We ignore
    #    the event argument.
    def map(self, *ignore):
	#    Synchronize with well color.
        self._updateBackboneColor()

	#    If no handler is currently registered, register one.
	if self.handlerId is None:
	    #    Registration occurs when the 'chimera.triggers' object
	    #    is requested to add a handler. *Registration requires
	    #    three arguments*:
	    #      - the name of the trigger,
	    #      - the handler function to be invoked when the
	    #        trigger fires, and
	    #      - an additional argument to be passed to the handler
	    #        function when it is invoked.
	    #    In this case, the trigger name is the same as the name
	    #    of the class of objects being monitored, "Atom".
	    #    The handler function is '_handler', defined below.
	    #    And the additional argument is empty (None) -- it could
	    #    have been the ColorOption instance ('coloropt') but that
	    #    is accessible via the instance.  The return value from
	    #    the registration is a unique handler identifier for
	    #    the handler/argument combination.  This identifier is
	    #    required for deregistering the handler.
	    #
	    #    *The handler function is always invoked by the trigger
	    #    with three arguments*:
	    #      - the name of the trigger,
	    #      - the additional argument passed in at registration
	    #        time, and
	    #      - an instance with three attributes
	    #	    - created: set of created objects
	    #	    - deleted: set of deleted objects
	    #	    - modified: set of modified objects
	    #    Note that with a newly opened model, objects will just
	    #    appear in both the 'created' set and not in the 'modified'
	    #    set, even though the newly created objects will normally have
	    #    various of their default attributes modified by later
	    #    code sections.
	    self.handlerId = chimera.triggers.addHandler('Atom', self._handler, None)

    #    The '_handler' function is the trigger handler invoked when
    #    attributes of 'Atom' instances change.
    def _handler(self, trigger, additional, atomChanges):
	#    Check through modified atoms for backbone atoms.
	for a in atomChanges.modified:
	    #    If any of the changed atoms is a backbone atom, call
	    #    '_updateBackboneColor' to synchronize the well color
	    #     with backbone atom colors.
	    if ColorWellUI.MAINCHAIN.match(a.name):
		self._updateBackboneColor()
		return

    #    'unmap' is called when the dialog disappears.  We ignore the
    #    event argument.
    def unmap(self, *ignore):
	#    Check whether a handler is currently registered (*i.e.*, the
	#    handler identifier, 'handlerId', is not 'None') and
	#    deregister it if necessary.
	if self.handlerId is not None:

	    #    Deregistration requires two arguments: the name of the
	    #    trigger and the unique handler identifier returned by
	    #    the registration call.
	    chimera.triggers.deleteHandler('Atom', self.handlerId)

	    #    Set the unique handler identifier to 'None' to indicate
	    #    that no handler is currently registered.
	    self.handlerId = None

#    Define the module variable 'dialog', which tracks the dialog instance.
#    It is initialized to 'None', and is assigned a usable value when the
#    dialog is created.
dialog = None

#    Define 'showColorWellUI', which is invoked when the Chimera
#    toolbar button is pressed.
def showColorWellUI():
    global dialog
    if dialog is not None:
	dialog.enter()
        return

    dialog = ColorWellDialog()

dir, file = os.path.split(__file__)
icon = os.path.join(dir, 'AtomTrigger.tiff')
chimera.tkgui.app.toolbar.add(icon, showColorWellUI, 'Set Main Chain Color', None)
