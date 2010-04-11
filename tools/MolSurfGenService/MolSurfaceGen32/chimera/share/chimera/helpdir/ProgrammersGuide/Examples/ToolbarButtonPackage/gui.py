#    The contents of "ToolbarButtonPackage/gui.py" is similar to
#    the last section of code in "Toolbar Buttons", with the
#    exception that the 'mainchain' function is now referenced as
#    'ToolbarButtonPackage.mainchain'. The reason for the change is
#    that 'gui.py' is a submodule, while the 'mainchain' function is in
#    the main package.  Since a submodule cannot directly access items
#    defined in the main package, 'gui.py' must first import the package
#    'import ToolbarButtonPackage' and refer to the function by prepending
#    the package name ('ToolbarButtonPackage.mainchain' in the call to
#    'chimera.tkgui.app.toolbar.add').
#
#    .. "ToolbarButtonPackage/gui.py" ToolbarButtonPackage/gui.py
#    .. "Toolbar Buttons" ToolbarButton.html

import os

import chimera

import ToolbarButtonPackage

dir, file = os.path.split(__file__)
icon = os.path.join(dir, 'ToolbarButton.tiff')
chimera.tkgui.app.toolbar.add(icon, ToolbarButtonPackage.mainchain, 'Show Main Chain', None)
