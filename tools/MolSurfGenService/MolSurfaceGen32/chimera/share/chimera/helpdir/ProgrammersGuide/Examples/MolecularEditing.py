#    Import system modules used in this example.
import re

# Import Chimera modules used in this example.
import chimera

#    Define a regular expression for matching the names of protein
#    backbone atoms (we do not include the carbonyl oxygens because
#    they tend to clutter up the graphics display without adding
#    much information).
MAINCHAIN = re.compile("^(N|CA|C)$", re.I)

#    Do the actual work of setting the display status of atoms and
#    bonds.  The following 'for' statement iterates over molecules.
#    The function call
#    'chimera.openModels.list(modelTypes=[chimera.Molecule])'
#    returns a list of all open molecules; non-molecular models such
#    as surfaces and graphics objects will not appear in the list.
#    The loop variable 'm' refers to each model successively.
for m in chimera.openModels.list(modelTypes=[chimera.Molecule]):

    #    The following 'for' statement iterates over atoms. The
    #    attribute reference 'm.atoms' returns a list of all atoms
    #    in model 'm', in no particular order.  The loop variable
    #    'a' refers to each atom successively.
    for a in m.atoms:
        #    Set the display status of atom 'a'.  First, we match
	#    the atom name, 'a.name', against the backbone atom
	#    name regular expression, 'MAINCHAIN'. The function
	#    call 'MAINCHAIN.match(a.name)' returns an 're.Match'
	#    object if the atom name matches the regular expression
	#    or 'None' otherwise.  The display status of the atom
	#    is set to true if there is a match (return value is not
	#    'None') and false otherwise.
        a.display = MAINCHAIN.match(a.name) != None

    #    By default, bonds are displayed if and only if both endpoint
    #    atoms are displayed, so therefore we don't have to explicitly
    #    set bond display modes; they will automatically "work right".
