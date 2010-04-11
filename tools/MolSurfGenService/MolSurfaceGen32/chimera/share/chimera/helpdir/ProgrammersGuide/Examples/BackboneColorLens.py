#    Import the standard Python modules used by this example.
import Tkinter
import re

#    Import the Chimera modules used by this example. The 'tkoptions'
#    module defines some user interface elements; for this example,
#    the 'ColorOption' class provides a simple interface to a labeled
#    color well. The 'lenses' module contains the required lens base
#    class, 'BaseLens'. The 'LensInspector' module contains the lens
#    class registration function, 'registerAddFunc'.
import chimera.tkoptions
import chimera.lenses
import chimera.LensInspector

#    Define a regular expression for matching the names of protein
#    backbone atoms (we do not include the carbonyl oxygens because
#    they tend to clutter up the graphics display without adding
#    much information).
MAINCHAIN = re.compile("^(N|CA|C)$", re.I)

#    Define the 'BackboneColorLens' class whose instances will manage
#    lens areas in the graphics window.  The derivation of
#    'BackboneColorLens' from base class 'chimera.lenses.BaseLens'
#    is *mandatory*.
class BackboneColorLens(chimera.lenses.BaseLens):

    #    Define the constructor for 'BackboneColorLens' instances.
    #    Declare that the constructor should be called with the
    #    instance itself and the parent lens in which the new lens
    #    will reside.
    def __init__(self, parent):
	#    Invoke the base class constructor, specifying that
	#    'BackboneColorLens' are opaque lenses, i.e., the
	#    content of the lens will <em>replace</em> the
	#    background lens image; the alternative to
	#    'chimera.Lens.Opaque' is 'chimera.Lens.Overlay',
	#    which indicates that the content of the lens is drawn
	#    on top of the background lens image.  The parent
	#    argument is for maintaining the lens hierarchy
	#    information needed by the Lens Inspector.
        chimera.lenses.BaseLens.__init__(self, chimera.Lens.Opaque, parent=parent)
	#    Initialize instance variables that will refer to the
	#    inspector frame and the color well option; the variables
	#    are initialized to 'None' to indicate that the user
	#    interface has not been created yet.
        self.inspector = None
        self.option = None
	#    Declare the instance variable that will keep track of
	#    all backbone atoms in the Chimera session.
        self._atoms = []
	#    Register trigger handlers for opening and closing of models;
	#    these handlers update the list of backbone atoms.
        self._addHandlerId = chimera.openModels.addAddHandler(
                                        self._checkModels, None)
        self._removeHandlerId = chimera.openModels.addRemoveHandler(
                                        self._checkModels, None)
	#    Invoke 'self._update' to immediately update the backbone
	#    atom list for the currently open models.
        self._update()

    #    Define the "destructor" for 'BackboneColorLens' instances.
    #    We extend the chimera.lenses.BaseLens 'destroy' method to
    #    unregister our triggers and remove references to the handlers.
    #    We don't use the '__del__' method since that only gets called
    #    when there are no more references to the instance.  Since the
    #    trigger handlers have embedded references to the instance, 
    #    '__del__' will never get called until those handlers are
    #    deregistered.
    def destroy(self):
	chimera.lenses.BaseLens.destroy(self)
        chimera.openModels.deleteAddHandler(self._addHandlerId)
        chimera.openModels.deleteRemoveHandler(self._removeHandlerId)
	self._addHandlerId = None
	self._removeHandlerId = None

    #    Define 'showInspector', which is called by the Lens Inspector
    #    when the user inspects the lens. The instance method is invoked
    #    with a an argument, 'master', which is the Tk widget in which
    #    the user interface should appear.
    def showInspector(self, master):
        #    Check whether the user interface has already been created.
        if self.inspector is None:
            #    If not, create the frame in which all other user
	    #    interface element will appear; having a single frame
	    #    containing all elements makes it easier to display or
	    #    hide the entire user interface.
            self.inspector = Tkinter.Frame(master)
            #    Create an user interface element, 'ColorOption',
	    #    defined by Chimera.  A 'ColorOption' is simply a color
	    #    well with a text label on its left.  The constructor
	    #    to a 'ColorOption' instance takes five arguments:
	    #    the frame in which it appears, the row in the frame
	    #    that the option occupies, the text for the label,
	    #    the default color to display, and the function to call
	    #    when the user changes the color in the well.
	    #    The constructor also accepts an optional keyword
	    #    argument ('balloon=') to specify a balloon-help message.
            self.option = chimera.tkoptions.ColorOption(
                    self.inspector,        # parent frame
                    0,                     # row number
                    'Backbone Color',      # label
                    None,                  # default value
                    self._setColor,        # callback
		    balloon='Protein backbone color')
        #    Once the inspector user interface exists, add it into the
	#    master widget supplied by the Lens Inspector for display.
        self.inspector.pack(expand=1, fill=Tkinter.BOTH)

    #    Define 'hideInspector', which is called by the Lens Inspector
    #    when ther user stops inspecting the lens.
    def hideInspector(self):
        #    Simply hide the inspector frame (created by 'showInspector')
	#    by removing it from its master widget.
        self.inspector.forget()

    #    Define '_checkModels', which is the trigger handler registered
    #    by the constructor and is invoked whenever models are opened
    #    or closed. Trigger handlers are called with the trigger name,
    #    an argument supplied at registration time, and the list of
    #    objects that caused the handler invocation.  For '_checkModels',
    #    the list consists of models that were opened or closed.
    def _checkModels(self, trigger, arg, models):
        #    Check whether any of the models are molecules; if so,
	#    call '_update' to recompute the backbone atom list.
        for m in models:
            if isinstance(m, chimera.Molecule):
                self._update()
                return

    #    Define '_update', which extracts the list of backbone atoms
    #    in the currently open models.  '_update' is called by the
    #    constructor when the lens is first created, and by the
    #    trigger handler when models are opened or closed.
    def _update(self):
        #    Start with an empty list of atoms.
        atoms = []
        #    Iterate over all models, adding backbone atoms in molecules
	#    to atom list.
        for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
            for a in m.atoms:
                if MAINCHAIN.match(a.name):
                    atoms.append(a)
        #    Save the list as an instance variable.
        self._atoms = atoms
        #    Invoke '_setColor' to update the lens information using
	#    the new list of atoms.
        self._setColor(self.option)

    #    Define '_setColor', which contains the heart of lens
    #    functionality. _setColor is registered as the callback
    #    function for 'ColorOption', which means it will receive
    #    the option as its argument.  _setColor is also called by
    #    '_update' when the list of backbone atoms is changed;
    #    however, the inspector user interface may not exist when
    #    the '_update' is called and _setColor will then receive
    #    an option of 'None'.
    def _setColor(self, option):
        #    Make sure that no action is taken when the color
	#    option (user interface) does not exist.
        if not self.option:
            return
        #    Fetch the current color displayed in the color option.
        color = option.get()
        #    Iterate over the list of backbone atoms and update the
	#    atom color within the lens. Unlike molecular editing,
	#    where one directly sets the atom attribute, the graphical
	#    attributes of an atom inside a lens is stored in the
	#    lens instance.
        for a in self._atoms:
            #    Fetch the graphical attributes dictionary,
	    #    'ga', for atom 'a'.
            ga = self.gfxAttr(a)
            #    Either define the color in the dictionary if the
	    #    current color is not 'None', or delete the color
	    #    value from the dictionary. The dictionary key that
	    #    is used for a graphics attribute is the string
	    #    containing the name of the attribute; in this case,
	    #    the key is 'color'.
            if color is None:
                try:
                    del ga['color']
                except KeyError:
                    pass
            else:
                ga['color'] = color
        #    Finally, call 'invalidateCache' to force Chimera to
	#    recompute the lens graphical display.
        self.invalidateCache()


#    Register the 'BackboneColorLens' class with the
#    'chimera.LensInspector' module for inclusion in the list
#    of available lens classes when the user is adding a lens.
chimera.LensInspector.registerAddFunc('Backbone Color', BackboneColorLens)
