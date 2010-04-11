#    This file is identical to the "ColorWellUI/__init__.py"
#    in the "Colors and Color Wells" example.
#
#    .. "ColorWellUI/__init__.py" ColorWellUI/__init__.py
#    .. "Colors and Color Wells" Main_ColorWellUI.html
import chimera
import re

MAINCHAIN = re.compile("^(N|CA|C)$", re.I)
def mainchain(color):
    for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
        for a in m.atoms:
            if MAINCHAIN.match(a.name):
                a.color = color
