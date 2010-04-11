#    Import system modules used in this example.
#    The regular expression module, 're', is used for matching atom names.
#    The operating system module, 'os', is used for constructing the icon
#    file name (see below).
import re
import os

#    Import Chimera modules used in this example.
#    The 'chimera' module is needed to access the molecular data.
import chimera

#    Function 'mainchain' sets the display status of atoms
#    and requires no arguments.  The body of the function is
#    identical to the example described in
#    "Molecular Editing Using Python".
#
#    .. "Molecular Editing Using Python" MolecularEditing.html
def mainchain():
    MAINCHAIN = re.compile("^(N|CA|C)$", re.I)
    for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
        for a in m.atoms:
            a.display = MAINCHAIN.match(a.name) != None

#    Create a button in the toolbar.
#    The first argument to 'chimera.tkgui.app.toolbar.add' is the icon,
#    which is either the path to an image file, or the name of a standard
#    Chimera icon (which is the base name of an image file found in the
#    "share/chimera/images" directory in the Chimera installation directory).
#    In this case, since 'ToolbarButton.tiff' is not an absolute path, the
#    icon will be looked for under that name in both the current directory
#    and in the Chimera images directory.
#    The second argument is the Python function to be called when the button
#    is pressed (a.k.a., the "callback function").
#    The third argument is a short description of what the button does
#    (used typically as balloon help).
#    The fourth argument is the URL to a full description.
#    For this example the icon name is 'ToolbarButton.tiff';
#    the Python function is 'mainchain';
#    the short description is "Show Main Chain";
#    and there is no URL for context help.
chimera.tkgui.app.toolbar.add('ToolbarButton.tiff', mainchain, 'Show Main Chain', None)

