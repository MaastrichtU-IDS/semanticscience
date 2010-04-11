#    This code is analogous to the code found in the "__init__.py"
#    modules in the "Packaging an Extension" and "Extension-Specific
#    User Interface" examples.  See "Molecular Editing" for a more
#    detailed example on changing molecular attributes. Note that
#    the 'mainchain' function is expecting a color *object* as its
#    argument (because the color is used to set an atomic attribute).
#
#    .. "Packaging an Extension" Main_ExtensionPackage.html
#    .. "Extension-Specific User Interface" Main_ExtensionUI.html
#    .. "Molecular Editing" MolecularEditing.html
import chimera
import re

MAINCHAIN = re.compile("^(N|CA|C)$", re.I)
def mainchain(color):
    for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
        for a in m.atoms:
            if MAINCHAIN.match(a.name):
                a.color = color
