#    The contents of "ToolbarButtonPackage/__init__.py" is
#    identical to the first section of code in "Toolbar Buttons",
#    with the exception that module 'os' is not imported.
#
#    .. "ToolbarButtonPackage/__init__.py" ToolbarButtonPackage/__init__.py
#    .. "Toolbar Buttons" ToolbarButton.html

import re

import chimera

def mainchain():
    MAINCHAIN = re.compile("^(N|CA|C)$", re.I)
    for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
        for a in m.atoms:
            a.display = MAINCHAIN.match(a.name) != None
