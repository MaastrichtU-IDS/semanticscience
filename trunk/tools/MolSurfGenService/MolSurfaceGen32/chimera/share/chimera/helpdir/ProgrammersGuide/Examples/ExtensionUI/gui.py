#    Import the standard modules used by this example.
import os
import Tkinter

#    Import the Chimera modules and classes used by this example.
import chimera
from chimera.baseDialog import ModelessDialog

#    Import the package for which the graphical user interface
#    is designed.  In this case, the package is named 'ExtensionUI'.
import ExtensionUI

#     Define two module variables:
#    'atomMode' and 'bondMode' are Tk variables that keep track of
#    the last selected display representations. These variables are
#    initialized to be 'None', and are set to usable values when
#    the GUI is created.
atomMode = None
bondMode = None

#    Define two dictionaries that map string names into Chimera
#    enumerated constant values. The two variables 'atomMode' and
#    'bondMode' keep track of the representations as strings because
#    they are displayed directly in the user interface. However,
#    the 'mainchain' function in the main package expects Chimera
#    constants as its arguments. The dictionaries 'atomModeMap' and
#    'bondModeMap' provides the translation from string to enumerated
#    constants.
atomModeMap = {
    'Dot': chimera.Atom.Dot,
    'Sphere': chimera.Atom.Sphere,
    'EndCap': chimera.Atom.EndCap,
    'Ball': chimera.Atom.Ball
}
bondModeMap = {
    'Wire': chimera.Bond.Wire,
    'Stick': chimera.Bond.Stick
}

#    Chimera offers two base classes to somewhat simplify the task of
#    creating user interfaces: ModalDialog and ModelessDialog.  The
#    former is designed for situations when information or response
#    is required of the user immediately; the dialog stays in front
#    of other Chimera windows until dismissed and prevents input from
#    going to other Chimera windows.  The latter dialog type is designed
#    for "ongoing" interfaces; it allows input focus to go to other
#    windows, and other windows can obscure it.
#
#    Here we declare a class that derives from ModelessDialog and
#    customize it for the specific needs of this extension.
class MainchainDialog(ModelessDialog):

    #    Chimera dialogs can either be *named* or *nameless*.  Named
    #    dialogs are displayed using the 'display(name)' function
    #    of the chimera.dialogs module.  The *name* that should be used
    #    as an argument to the 'display' function is given by the class
    #    variable 'name'.  Using a named dialog is appropriate when
    #    it might be desirable to invoke the dialog from other extensions
    #    or from Chimera itself.
    #
    #    A nameless dialog is intended for use only in the extension that
    #    defines the dialog.  A nameless dialog is typically created and
    #    displayed by calling its constructor.  Once created, a nameless
    #    dialog can be redisplayed (if it was withdrawn by clicking its
    #    'Cancel' button for example) by calling its 'enter()' method.
    #
    #    For demonstration purposes, we use a named dialog here.  A
    #    nameless dialog is used in the "Color and Color Wells" example.
    #
    #    .. "Color and Color Wells" Main_ColorWellUI.html
    name = "extension ui"

    #    The buttons displayed at the bottom of the dialog are given
    #    in the class variable 'buttons'.  For modeless dialogs, a
    #    help button will automatically be added to the button list
    #    (the help button will be grayed out if no help information
    #    is provided).  For buttons other than 'Help', clicking on
    #    them will invoke a class method of the same name.
    #
    #    Both dialog base classes provide appropriate methods for
    #    'Close', so we won't provide a 'Close' method in this
    #    subclass.  The ModelessDialog base class also provides a
    #    stub method for 'Apply', but we will override it with our
    #    own 'Apply' method later in the class definition.
    buttons = ("Apply", "Close")

    #    A help file or URL can be specified with the 'help' class
    #    variable.  A URL would be specified as a string (typically
    #    starting with "http://...").  A file would be specified as
    #    a 2-tuple of file name followed by a package.  The file
    #    would then be looked for in the 'helpdir' subdirectory of
    #    the package.  A dialog of Chimera itself (rather than of an
    #    imported package) might only give a filename as the class
    #    help variable.  That file would be looked for in
    #    /usr/local/chimera/share/chimera/helpdir.
    help = ("ExtensionUI.html", ExtensionUI)

    #    The title displayed in the dialog window's title bar is set
    #    via the class variable 'title'.
    title = "Set Backbone Representation"

    #    Both ModelessDialog and ModalDialog, in their __init__
    #    functions, set up the standard parts of the dialog interface
    #    (top-level window, bottom-row buttons, etc.) and then call
    #    a function named 'fillInUI' so that the subclass can fill
    #    in the parts of the interface specific to the dialog.  As
    #    an argument to the function, a Tkinter Frame is provided
    #    that should be the parent to the subclass-provided interface
    #    elements.
    def fillInUI(self, parent):

        #    Declare that, in 'fillInUI', the names 'atomMode' and
        #    'bondMode' refer to the global variables defined above.
        global atomMode, bondMode

        #    Create and initialize 'atomMode' and 'bondMode', the
        #    two  global Tk string variables that keep track of the
        #    currently selected display representation.
        atomMode = Tkinter.StringVar(parent)
        atomMode.set('Dot')
        bondMode = Tkinter.StringVar(parent)
        bondMode.set('Wire')

        #    Create the label and option menu for selecting atom
        #    display representation. First create the label 'Atom
        #    Representation' and place it on the left-hand side of
        #    the top row in the GUI window.
        atomLabel = Tkinter.Label(parent, text='Atom Representation')
        atomLabel.grid(column=0, row=0)
        #    Create the menu button and the option menu that it brings up.
        atomButton = Tkinter.Menubutton(parent, indicatoron=1,
                                        textvariable=atomMode, width=6,
                                        relief=Tkinter.RAISED, borderwidth=2)
        atomButton.grid(column=1, row=0)
        atomMenu = Tkinter.Menu(atomButton, tearoff=0)
        #    Add radio buttons for all possible choices to the menu.
        #    The list of choices is obtained from the keys of the
        #    string-to-enumeration dictionary, and the radio button
        #    for each choice is programmed to update the 'atomMode'
        #    variable when selected.
        for mode in atomModeMap.keys():
            atomMenu.add_radiobutton(label=mode, variable=atomMode, value=mode)
        #    Assigns the option menu to the menu button.
        atomButton['menu'] = atomMenu

        #    The lines below do the same thing for bond representation
        #    as the lines above do for atom representation.
        bondLabel = Tkinter.Label(parent, text='Bond Representation')
        bondLabel.grid(column=0, row=1)
        bondButton = Tkinter.Menubutton(parent, indicatoron=1,
                                        textvariable=bondMode, width=6,
                                        relief=Tkinter.RAISED, borderwidth=2)
        bondButton.grid(column=1, row=1)
        bondMenu = Tkinter.Menu(bondButton, tearoff=0)
        for mode in bondModeMap.keys():
            bondMenu.add_radiobutton(label=mode, variable=bondMode, value=mode)
        bondButton['menu'] = bondMenu

    #    Define the method that is invoked when the 'Apply' button
    #    is clicked. The function simply converts the currently
    #    selected representations from strings to enumerated constants,
    #    using the 'atomModeMap' and 'bondModeMap' dictionaries, and
    #    invokes the main package function 'mainchain'.
    def Apply(self):
        ExtensionUI.mainchain(atomModeMap[atomMode.get()],
                              bondModeMap[bondMode.get()])

#   Now we register the above dialog with Chimera, so that it may be 
#   invoked via the 'display(name)' method of the chimera.dialogs module.
#   Here the class itself is registered, but since it is a named dialog
#   deriving from ModalDialog/ModelessDialog, the instance will automatically
#   reregister itself when first created.  This allows the 'dialogs.find()'
#   function to return the instance instead of the class.
chimera.dialogs.register(MainchainDialog.name, MainchainDialog)

#    Create the Chimera toolbar button that displays the dialog when
#    pressed.  Note that since the package is not normally searched for
#    icons, we have to prepend the path of this package to the icon's
#    file name.
dir, file = os.path.split(__file__)
icon = os.path.join(dir, 'ExtensionUI.tiff')
chimera.tkgui.app.toolbar.add(icon, lambda d=chimera.dialogs.display, n=MainchainDialog.name: d(n), 'Set Main Chain Representation', None)
