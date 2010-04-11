#    Import the standard modules used in this example.
import re

#    Import the Chimera modules used in this example.
import chimera

#    Define a regular expression for matching the names of protein backbone
#    atoms (we do not include the carbonyl oxygens because they tend to
#    clutter up the graphics display without adding much information).
MAINCHAIN = re.compile("^(N|CA|C)$", re.I)

#    Define 'mainchain' function for setting the display representation
#    of protein backbone atoms and bonds.  See "Molecular Editing" for a
#    more detailed example on changing molecular attributes.
#
#    .. "Molecular Editing" MolecularEditing.html
def mainchain(atomMode, bondMode):
    for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):
        for a in m.atoms:
            if MAINCHAIN.match(a.name):
                a.drawMode = atomMode
        for b in m.bonds:
            ends = b.atoms
            if MAINCHAIN.match(ends[0].name) \
            and MAINCHAIN.match(ends[1].name):
                b.drawMode = bondMode
