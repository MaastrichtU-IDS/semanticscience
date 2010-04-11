#    Import Chimera modules used in this example.
import chimera

#    First, we'll open up a model to work with. This molecule (4fun) is very small,
#    comprised of just a couple residues, but it is perfect for illustrating
#    some important components of Chimera's object model.
#    For more information on how to open/close models in Chimera, see the
#    "Basic Model Manipulation" Example in the Programmer's Guide (coming soon). For now,
#    just understand that this code opens up any molecules stored in the file
#    "4fun.pdb" and returns a list of references to opened models.
#
#    .. "4fun.pdb" 4fun.pdb
opened = chimera.openModels.open('4fun.pdb')

#    Because only one molecule was opened, 'opened' is a list with just one element.
#    Get a reference to that element (which is a 'Molecule'
#    instance) and store it in 'mol'
mol = opened[0]


#    Now that we have a molecule to work with, an excellent way of examining its data structures is to flatten it out and write
#    it to a file. We'll write this file in the 'mol2' format, a free-format ascii file that describes molecular structure.
#    It is not necessary to have any prior knowledge of the 'mol2' format to understand this example, just a basic
#    comprehension of file formats that use coordinate data. Check out the "finished product".
#    It should serve as a good reference while you're going through the example.
#    Get a reference to a file to write to:
#
#    .. "finished product" 4fun.mol2
f = open("4fun.mol2", 'w')


#    mol2 uses a series of Record Type Indicators (RTI), that indicate the type of structure that will be described in
#    the following lines.
#    An RTI is simply an ASCII string which starts with an asterisk ('@'), followed by a string of characters,
#    and is terminated by a new line.
#    Here, we define some RTI's that we will use througout the file to describe the various parts of our model:

MOLECULE_HEADER = "@<TRIPOS>MOLECULE"
ATOM_HEADER     = "@<TRIPOS>ATOM"
BOND_HEADER     = "@<TRIPOS>BOND"
SUBSTR_HEADER   = "@<TRIPOS>SUBSTRUCTURE"


#    The 'chimera2sybyl' dictionary is used to map Chimera atom types
#    to Sybyl atom types.  See section below on writing out per-atom
#    information.
chimera2sybyl = {
	'C3'  : 'C.3',     'C2'  : 'C.2',     'Car' : 'C.ar',    'Cac' : 'C.2',
	'C1'  : 'C.1',     'N3+' : 'N.4',     'N3'  : 'N.3',     'N2'  : 'N.2',
	'Npl' : 'N.pl3',   'Ng+' : 'N.pl3',   'Ntr' : 'N.2',     'Nox' : 'N.4',
	'N1+' : 'N.1',     'N1'  : 'N.1',     'O3'  : 'O.3',     'O2'  : 'O.2',
	'Oar' : 'O.2',     'O3-' : 'O.co2',   'O2-' : 'O.co2',   'S3+' : 'S.3',
	'S3'  : 'S.3',     'S2'  : 'S.2',     'Sac' : 'S.O2',    'Son' : 'S.O2',
	'Sxd' : 'S.O',     'Pac' : 'P.3',     'Pox' : 'P.3',     'P3+' : 'P.3',
	'HC'  : 'H',       'H'   : 'H',       'DC'  : 'H',       'D'   : 'H',
	'P'   : 'P.3',     'S'   : 'S.3',     'Sar' : 'S.2',     'N2+' : 'N.2'
}

#    Writing Out per-Molecule Information
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    The "<TRIPOS>MOLECULE" RTI indicates that the next couple of lines will contain information relevant
#    to the molecule as a whole. First, write out the Record Type Indicator (RTI):
f.write("%s\n" % MOLECULE_HEADER)

#    The next line contains the name of the molecule. This can be accessed through the 'mol.name' attribute.
#    (Remember, 'mol' is a reference to the molecule we opened). If the model you open came from a pdb file, 'name' will most
#    often be the name of the file (without the '.pdb' extension).  For this example, 'mol.name' is "4fun".
f.write("%s\n" % mol.name)

#    Next, we need to write out the number of atoms, number of bonds, and number of substructures in the model (substructures
#    can be several different things; for the sake of simplicity, the only substructures we'll worry about here are residues).
#    This data is accessible through attributes of a molecule object: 'mol.atoms', 'mol.bonds', and 'mol.residues' all contain
#    lists of their respective components. We can determine how many atoms, bonds, or residues this
#    molecule has by taking the 'len' of the appropriate list.
#    save the list of references to all the atoms in 'mol':
ATOM_LIST = mol.atoms
#    save the list of references to all the bonds in 'mol':
BOND_LIST = mol.bonds
#    save the list of references to all the residues in 'mol':
RES_LIST  = mol.residues

f.write("%d %d %d\n" % ( len(ATOM_LIST), len(BOND_LIST), len(RES_LIST)) )

#    type of molecule
f.write("PROTEIN\n")

#    indicate that no charge-related information is available
f.write("NO_CHARGES\n")

f.write("\n\n")


#    Writing Out per-Atom Information
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    Next, write out atom-related information. In order to indicate this, we must first write out the
#    atom RTI:
f.write("%s\n" % ATOM_HEADER)

#   Each line under the 'ATOM' RTI consists of information pertaining to a single atom. The following information about each
#   atom is required: an arbitrary atom id number, atom name, x coordinate, y coordinate, z coordinate, atom type, id of the
#   substructure to which the atom belongs , name of the substructure to which the atom belongs.

#    You can look at each atom in the molecule by looping through its 'atoms' attribute.
#    Remember, 'ATOM_LIST' is the list of atoms stored in 'mol.atoms.' It's more efficient
#    to get the list once, and assign it to a variable, then to repeatedly ask for 'mol.atoms'.
for atom in ATOM_LIST:
    #    Now that we have a reference to an atom, we can write out all the necessary information to the file.
    #    The first field is an arbitrary id number. We'll just use that atom's index within the 'mol.atoms' list. 
    f.write("%d " % ATOM_LIST.index(atom) )

    #    Next, we need the name of the atom, which is accessible via the 'name' attribute.
    f.write("%s " % atom.name)

    #    Now for the x, y, and z coordinate data.
    #    Get the atom's 'xformCoord' object. This is essentially a wrapper that holds information about the 
    #    coordinate position (x,y,z) of that atom. 'xformCoord.x', 'xformCoord.y', and 'xformCoord.z' store the x, y,
    #    and z coordinates,
    #    respectively, as floating point integers. This information comes from the coordinates given for each atom
    #    specification in the input file
    coord = atom.xformCoord()
    f.write("%g %g %g " % (coord.x, coord.y, coord.z) )

    #    The next field in this atom entry is the atom type. This is a string which stores information about the
    #    chemical properties of the atom. It is accessible through the 'idatmType' attribute of an atom object.
    #    Because Chimera uses slightly different atom types than SYBYL (the modeling program for which .mol2 is the primary
    #    input format), use a dictionary called chimera2sybyl (defined above) that converts Chimera's atom types to
    #    the corresponding SYBYL version of the atom's type. 
    f.write("%s " % chimera2sybyl[atom.idatmType])

    #    The last two fields in an atom entry pertain to any substructures to which the atom may belong.
    #    As previously noted, we are only interested in residues for this example.
    #    Every atom object has a 'residue' attribute, which is a reference to the residue to which that atom belongs.
    res   = atom.residue

    #    Here, we'll use 'res.id' for the substructure id field. 'res.id' is a string which represents a unique id
    #    for that residue (a string representation of a number, i.e. "1" , which are sequential, for all the
    #    residues in a molecule).
    f.write("%s " % res.id)

    #    The last field to write is substructure name. Here, we'll use the 'type' attribute of 'res'. the 'type' attribute contains
    #    a string representation of the residue type (e.g. "HIS", "PHE", "SER"...).  Concatenate onto this the residue's 'id'
    #    to make a unique name for this substructure (because it is possible, and probable, to have more than one
    #    "HIS" residue in a molecule. This way, the substructure name will be "HIS6" or "HIS28")
    f.write("%s%s\n" % (res.type, res.id) )

f.write("\n\n")


#    Writing Out per-Bond Information
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    Now for the bonds. The bond RTI says that the following lines will contain information about bonds.
f.write("%s\n" % BOND_HEADER)


#    Each line after the bond RTI contains information about one bond in the molecule.
#    As noted earlier, you can access all the bonds in a molecule through the 'bonds' attribute,
#    which contains a list of bonds. 
for bond in BOND_LIST:

    #    each bond object has an 'atoms' attribute, which is list of length 2, where each item in the list is
    #    a reference to one of the atoms to which the bond connects.
    a1, a2 = bond.atoms
    
    #    The first field in a mol2 bond entry is an arbitrary bond id. Once again, we'll just use that
    #    bond's  index in the 'mol.bonds' list
    f.write("%d " % BOND_LIST.index(bond) )

    #    The next two fields are the ids of the atoms which the bond connects. Since we have a reference to both these
    #    atoms (stored in 'a1' and 'a2'), we can just get the index of those objects in the 'mol.atoms' list:
    f.write("%s %s " % (ATOM_LIST.index(a1), ATOM_LIST.index(a2)) )

    #    The last field in this bond entry is the bond order. Chimera doesn't currently calcuate bond orders,
    #    but for our educational purposes here, this won't be a problem.    
    #    The mol2 format expects bond order as a string: "1" (first-order), "2" (second-order), etc.,  so
    #    just write out "1" here (even though this may not be correct).
    f.write("1\n")

f.write("\n\n")


#    Writing Out per-Residue Information
#    ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~
#
#    Almost done!!! The last section contains information about the substructures (i.e. residues for this example)
#    You know the drill:
f.write("%s\n" % SUBSTR_HEADER)

#    We've already covered some of these items (see above):
for res in RES_LIST:
    #    residue id field
    f.write("%s " % res.id )

    #    residue name field
    f.write("%s%s " % (res.type, res.id) )

    #    the next field specifies the id of the root atom of the substructure. For the case of residues,
    #    we'll use the alpha-carbon as the root.
    #    Each residue has an 'atomsMap' attribute which is a dictionary. The keys in this dictionary are
    #    atom names (e.g. 'C', 'N', 'CA'), and the values are lists of references to atoms in the residue that have that
    #    name. So, to get the alpha-carbon of this residue:
    alpha_carbon = res.atomsMap['CA'][0]

    #    and get the id of 'alpha_carbon' from the 'mol.atoms' list
    f.write("%d " % ATOM_LIST.index(alpha_carbon) )


    #    The final field of this substructure entry is a string which specifies what type of substructure it is:
    f.write("RESIDUE\n")

f.write("\n\n")
f.close()

#    And that's it! Don't worry if you didn't quite understand all the ins and outs of the mol2 file format.
#    The purpose of this exercise was to familiarize yourself with Chimera's object model; writing out a mol2 file
#    was just a convenient way to do that. The important thing was to gain an understanding of how Chimera's atoms,
#    bonds, residues, and molecules all fit together.
