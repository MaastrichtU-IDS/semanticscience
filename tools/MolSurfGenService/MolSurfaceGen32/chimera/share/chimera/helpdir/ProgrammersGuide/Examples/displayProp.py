import chimera

#    open up a molecule to work with:
opened = chimera.openModels.open('3fx2', type="PDB")
mol    = opened[0]

#    Molecule Display Properties
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    the 'color' attribute represents the model-level color.
#    This color can be controlled by the midas command 'modelcolor'.
#    The 'color' assigned to a newly opened model is determined by a configurable preference (see discussion above).
#    Programmatically, the model 
#    color can be changed by simply assigning a 'MaterialColor' to 'molecule.color'. Molecules also have a
#    'display' attribute, where a value of 'True' corresponds to being displayed, and a value of 'False'
#     means the molecule is not displayed.
#     So to make sure the molecule is shown (it is by default when first opened):
mol.display = True

#     To color the molecule red,
#     get a reference to Chimera's notion of the color red (returns a 'MaterialColor' object)
from chimera.colorTable import getColorByName
red = getColorByName('red')

#     and assign it to 'mol.color'. 
mol.color = red
#     Note that the model will appear red at this point because all the atoms/bonds/residues
#     'color' attributes are set to 'None'

#    Atom Display Properties
#    ~~~~~~~~~~~~~~~~~~~~~~~
#
#    Each atom in a molecule has its own individual color,
#    accessible by the 'color' attribute. Upon opening a molecule, each atom's 'color' is set to 'None'; 
#    it can be changed by assigning a new 'MaterialColor' to 'atom.color'.
#    So, if we wanted to color all the alpha-carbon atoms blue, and all the rest yellow,
#    get references to the colors:
blue    = getColorByName('blue')
yellow  = getColorByName('yellow')

#    get a list of all the atoms in the molecule
ATOMS = mol.atoms
for at in ATOMS:
    #    check to see if this atom is an alpha-carbon
    if at.name == 'CA':
        at.color = yellow
    else:
        at.color = blue

#    Now, even though 'mol.color' is set to red, the molecule will appear to be blue and yellow. This is because each individual
#    atom's 'color' is visible over 'mol.color'.

#     Like molecules, atoms also have a 'display' attribute that controls whether or not the atom is shown.
#     While 'atom.display' controls whether the atom can be seen at all, 'atom.drawMode' controls its visual representation.
#     The value of 'drawMode' can be one of four constants, defined in the 'Atom' class.
#     Acceptable values for 'drawMode'
#     are 'chimera.Atom.Dot' (dot representation), 'chimera.Atom.Sphere' (sphere representation),
#     'chimera.Atom.EndCap' (endcap representation), or 'chimera.Atom.Ball' (ball representation).
#     So, to represent all the atoms in the molecule as "balls":
for at in ATOMS:
    at.drawMode = chimera.Atom.Ball
        

#    Bond Display Properties
#    ~~~~~~~~~~~~~~~~~~~~~~~
#
#    Bonds also contain 'color', and 'drawMode' attributes. They serve the same purposes here as they do
#    in atoms ('color' is the color specific to that bond, and 'drawMode' dictates
#    how the bond is represented). 'drawMode' for bonds can be either 'chimera.Bond.Wire' (wire representation)
#    or 'chimera.Bond.Stick' (stick representation).
#    The 'bond.display' attribute accepts slightly different values than that of other objects.
#    While other objects' 'display' can be set to either 'False' (not displayed)
#    or 'True' (displayed), 'bond.display' can be assigned a value of 'chimera.Bond.Never' (same as 'False' - bond is not
#    displayed), 'chimera.Bond.Always' (same as 'True' - bond is displayed), or 'chimera.Bond.Smart' which means that the
#    bond will only be
#    displayed if both the atoms it connects to are displayed. If not, the bond will not be displayed. 
#    The heuristic that determines bond color is also a little more complicated than for atoms.
#    Bonds have an attribute called 'halfbond'
#    that determines the source of the bond's color. If 'halfbond' is set to 'True', then the
#    bond derives its color from the atoms which 
#    it connects, and ignores whatever 'bond.color' is. If both those atoms are the same color (blue, for instance),
#    then the bond will appear blue. If the bonds atoms are different colors, then each half of the bond will correspond to the color
#    of the atom on that side. However, if 'bond.halfbond' is set to 'False', then that bond's color
#    will be be derived from its 'color' attribute, regardless of the 'color's of the atoms which it connects (except in the case
#    'bond.color' is 'None', the bond will derive its color from one of the atoms to which it connects).
#    To set each bond's display mode to "smart", represent it as a stick, and turn halfbond mode on,
#    get a list of all bonds in the molecule
BONDS = mol.bonds
for b in BONDS:
    b.display  = chimera.Bond.Smart
    b.drawMode = chimera.Bond.Stick
    b.halfbond = True
    


#    Residue Display Properties
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    Residues are not "displayed" in the same manner that atoms and bonds are. When residues are displayed, they are
#    in the form of ribbons, and the attributes that control the visual details of the residues are named accordingly:
#    'ribbonDisplay', 'ribbonColor', 'ribbonDrawMode'. The values for 'ribbonDrawMode' can be 'chimera.Residue.Ribbon_2D' (flat ribbon),
#    'chimera.Residue.Ribbon_Edged' (sharp ribbon), or 'chimera.Residue.Ribbon_Round' (round/smooth ribbon).
#    If a residue's 'ribbonDisplay' value is set to 'False', it doesn't matter what 'ribbonDrawMode'
#    is - the ribbon still won't be displayed!
#    Residues have three attributes that control how the ribbon is drawn. 'isTurn', 'isHelix', and  'isSheet' (same as 'isStrand') are
#    set to either 'True' or 'False' based on secondary structure information contained in the source file (if available).
#    For any residue, only one of these can be set to 'True'. 
#    So, to display only the residues which are part of an alpha-helix, as a smooth ribbon,
#    get a list of all the residues in the molecule
RESIDUES = mol.residues
for r in RESIDUES:
    #    only for residues that are part of an alpha-helix
    if r.isHelix:
        r.ribbonDisplay  = True
        r.ribbonDrawMode = chimera.Residue.Ribbon_Round



