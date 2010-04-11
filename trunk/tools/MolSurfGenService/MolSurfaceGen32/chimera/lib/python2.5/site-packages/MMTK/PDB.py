# This module deals with input and output of configurations in PDB format.
#
# Written by Konrad Hinsen
# last revision: 2007-8-7
#

"""This module provides classes that represent molecules in PDB file.
They permit various manipulations and the creation of MMTK objects.
Note that the classes defined in this module are specializations
of classed defined in Scientific.IO.PDB; the methods defined in
that module are also available.
"""

import ChemicalObjects, Collections, Database, Units, Universe, Utility
from Scientific.Geometry import Vector
import Scientific.IO.PDB
import os, string

#
# The chain classes from Scientific.IO.PDB are extended by methods
# that construct MMTK objects and set configurations.
#
class PDBChain:

    def applyTo(self, chain, map = 'pdbmap', alt = 'pdb_alternative',
                atom_map = None):
        if len(chain) != len(self):
            raise ValueError("chain lengths do not match")
        for i in range(len(chain)):
            residue = chain[i]
            pdbmap = getattr(residue, map)
            try: altmap = getattr(residue, alt)
            except AttributeError: altmap = {}
            setResidueConfiguration(residue, self[i], pdbmap[0], altmap,
                                    atom_map)
    
class PDBPeptideChain(Scientific.IO.PDB.PeptideChain, PDBChain):

    """Peptide chain in a PDB file

    A Glossary:Subclass of Scientific.IO.PDB.PeptideChain.
    See the description of that class for the constructor and
    additional methods. In MMTK, PDBPeptideChain objects
    are usually obtained from a PDBConfiguration object
    via its attribute peptide_chains (see the documentation
    of Scientific.IO.PDB.Structure).
    """

    def createPeptideChain(self, model = 'all',
                           n_terminus=None, c_terminus=None):
        """Returns a PeptideChain object corresponding to the
        peptide chain in the PDB file. The parameter |model|
        has the same meaning as for the PeptideChain constructor."""
        self.identifyProtonation()
        import Proteins
        properties = {'model': model}
        if self.segment_id != '':
            properties['name'] = self.segment_id
        elif self.chain_id != '':
            properties['name'] = self.chain_id
        if c_terminus is None:
            properties['c_terminus'] = self.isTerminated()
        else:
            properties['c_terminus'] = c_terminus
        if n_terminus is not None:
            properties['n_terminus'] = n_terminus
        chain = apply(Proteins.PeptideChain, (self,), properties)
        if model != 'no_hydrogens':
            chain.findHydrogenPositions()
        return chain

    def identifyProtonation(self):
        for residue in self.residues:
            if residue.name == 'HIS':
                count_hd = 0
                count_he = 0
                for atom in residue:
                    if 'HD' in atom.name:
                        count_hd += 1
                    if 'HE' in atom.name:
                        count_he += 1
                if count_he == 2:
                    if count_hd == 2:
                        residue.name = 'HIP'
                    else:
                        residue.name = 'HIE'
                else:
                    residue.name = 'HID'
            elif residue.name == 'GLU':
                for atom in residue:
                    if 'HE' in atom.name:
                        residue.name = 'GLP'
                        break
            elif residue.name == 'ASP':
                for atom in residue:
                    if 'HD' in atom.name:
                        residue.name = 'APP'
                        break
            elif residue.name == 'LYS':
                count_hz = 0
                for atom in residue:
                    if 'HZ' in atom.name:
                        count_hz += 1
                if count_hz < 3:
                    residue.name = 'LYP'

class PDBNucleotideChain(Scientific.IO.PDB.NucleotideChain, PDBChain):

    """Nucleotide chain in a PDB file

    A Glossary:Subclass of Scientific.IO.PDB.NucleotideChain. See
    the description of that class for the constructor and
    additional methods. In MMTK, PDBNucleotideChain objects
    are usually obtained from a PDBConfiguration object
    via its attribute nucleotide_chains (see the documentation
    of Scientific.IO.PDB.Structure).
    """

    def createNucleotideChain(self, model='all'):
        """Returns a NucleotideChain object corresponding to the
        nucleotide chain in the PDB file. The parameter |model|
        has the same meaning as for the NucleotideChain constructor."""
        import NucleicAcids
        properties = {'model': model}
        if self.segment_id != '':
            properties['name'] = self.segment_id
        if self[0].hasPhosphate():
            properties['terminus_5'] = 0
        chain = apply(NucleicAcids.NucleotideChain, (self,), properties)
        if model != 'no_hydrogens':
            chain.findHydrogenPositions()
        return chain

class PDBMolecule(Scientific.IO.PDB.Molecule):

    """Molecule in a PDB file

    A Glossary:Subclass of Scientific.IO.PDB.Molecule. See
    the description of that class for the constructor and
    additional methods. In MMTK, PDBMolecule objects
    are usually obtained from a PDBConfiguration object
    via its attribute molecules (see the documentation
    of Scientific.IO.PDB.Structure). A molecule is by definition
    any residue in a PDB file that is not an amino acid or
    nucleotide residue.
    """

    def applyTo(self, molecule, map = 'pdbmap', alt = 'pdb_alternative',
                atom_map = None):
        pdbmap = getattr(molecule, map)
        try: altmap = getattr(molecule, alt)
        except AttributeError: altmap = {}
        setResidueConfiguration(molecule, self, pdbmap[0], altmap, atom_map)

    def createMolecule(self, name=None):
        """Returns a Molecule object corresponding to the molecule
        in the PDB file. The parameter |name| specifies the molecule
        name as defined in the chemical database. It can be left out
        for known molecules (currently only water)."""
        if name is None:
            name = molecule_names[self.name]
        m = ChemicalObjects.Molecule(name)
        setConfiguration(m, [self])
        return m

#
# The structure class from Scientific.IO.PDB is extended by methods
# that construct MMTK objects and set configurations.
#
class PDBConfiguration(Scientific.IO.PDB.Structure):

    """Everything in a PDB file

    A PDBConfiguration object represents the full contents of a PDB
    file. It can be used to create MMTK objects for all or part
    of the molecules, or to change the configuration of an existing
    system.

    Constructor: PDBConfiguration(|filename|, |model|='0',
                                  |alternate_code|='"A"')

    Arguments:

    |filename| -- the name of a PDB file

    |model| -- the number of the model to be used from a multiple model file

    |alternate_code| -- the alternate code to be used for atoms that have
                        alternate positions
    """
    
    def __init__(self, filename, model = 0, alternate_code = 'A'):
        filename = Database.PDBPath(filename)
        Scientific.IO.PDB.Structure.__init__(self, filename,
                                             model, alternate_code)
        self._numberAtoms()
        self._convertUnits()

    peptide_chain_constructor = PDBPeptideChain
    nucleotide_chain_constructor = PDBNucleotideChain
    molecule_constructor = PDBMolecule

    def _numberAtoms(self):
        n = 1
        for residue in self.residues:
            for atom in residue:
                atom.number = n
                n += 1

    def _convertUnits(self):
        for residue in self.residues:
            for atom in residue:
                atom.position = atom.position*Units.Ang
                try:
                    b = atom.properties['temperature_factor']
                    atom.properties['temperature_factor'] = b*Units.Ang**2
                except KeyError:
                    pass
                try:
                    u = atom.properties['u']
                    atom.properties['u'] = u*Units.Ang**2
                except KeyError:
                    pass

        # All these attributes exist only if ScientificPython >= 2.7.5 is used.
        # The Scaling transformation was introduced with the same version,
        # so if it exists, the rest should work as well.
        try:
            from Scientific.Geometry.Transformation import Scaling
        except ImportError:
            return
        for attribute in ['a', 'b', 'c']:
            value = getattr(self, attribute)
            if value is not None:
                setattr(self, attribute, value*Units.Ang)
        for attribute in ['alpha', 'beta', 'gamma']:
            value = getattr(self, attribute)
            if value is not None:
                setattr(self, attribute, value*Units.deg)
        if self.to_fractional is not None:
            self.to_fractional = self.to_fractional*Scaling(1./Units.Ang)
            v1 = self.to_fractional(Vector(1., 0., 0.))
            v2 = self.to_fractional(Vector(0., 1., 0.))
            v3 = self.to_fractional(Vector(0., 0., 1.))
            self.reciprocal_basis = (Vector(v1[0], v2[0], v3[0]),
                                     Vector(v1[1], v2[1], v3[1]),
                                     Vector(v1[2], v2[2], v3[2]))
        else:
            self.reciprocal_basis = None
        if self.from_fractional is not None:
            self.from_fractional = Scaling(Units.Ang)*self.from_fractional
            self.basis = (self.from_fractional(Vector(1., 0., 0.)),
                          self.from_fractional(Vector(0., 1., 0.)),
                          self.from_fractional(Vector(0., 0., 1.)))
        else:
            self.basis = None
        for i in range(len(self.ncs_transformations)):
            tr = self.ncs_transformations[i]
            tr_new = Scaling(Units.Ang)*tr*Scaling(1./Units.Ang)
            tr_new.given = tr.given
            tr_new.serial = tr.serial
            self.ncs_transformations[i] = tr_new
        for i in range(len(self.cs_transformations)):
            tr = self.cs_transformations[i]
            tr_new = Scaling(Units.Ang)*tr*Scaling(1./Units.Ang)
            self.cs_transformations[i] = tr_new

    def createPeptideChains(self, model='all'):
        """Returns a list of PeptideChain objects, one for each
        peptide chain in the PDB file. The parameter |model|
        has the same meaning as for the PeptideChain constructor."""
        return [chain.createPeptideChain(model)
                for chain in self.peptide_chains]

    def createNucleotideChains(self, model='all'):
        """Returns a list of NucleotideChain objects, one for each
        nucleotide chain in the PDB file. The parameter |model|
        has the same meaning as for the NucleotideChain constructor."""
        return [chain.createNucleotideChain(model)
                for chain in self.nucleotide_chains]

    def createMolecules(self, names = None, permit_undefined=1):
        """Returns a collection of Molecule objects, one for each
        molecule in the PDB file. Each PDB residue not describing
        an amino acid or nucleotide residue is considered a molecule.

        The parameter |names| allows the selective construction of
        certain molecule types and the construction of unknown
        molecules. If its value is a list of molecule names
        (as defined in the chemical database) and/or PDB residue
        names, only molecules mentioned in this list will be
        constructed. If its value is a dictionary, it is used
        to map PDB residue names to molecule names. By default only
        water molecules are recognizes (under various common PDB residue
        names); for all other molecules a molecule name must be provided
        by the user.

        The parameter |permit_undefined| determines how PDB residues
        without a corresponding molecule name are handled. A value
        of 0 causes an exception to be raised. A value of 1 causes
        an AtomCluster object to be created for each unknown residue.
        """
        collection = Collections.Collection()
        mol_dicts = [molecule_names]
        if type(names) == type({}):
            mol_dicts.append(names)
            names = None
        for name in self.molecules.keys():
            full_name = None
            for dict in mol_dicts:
                full_name = dict.get(name, None)
            if names is None or name in names or full_name in names:
                if full_name is None and not permit_undefined:
                    raise ValueError("no definition for molecule " + name)
                for molecule in self.molecules[name]:
                    if full_name:
                        m = ChemicalObjects.Molecule(full_name)
                        setConfiguration(m, [molecule])
                    else:
                        pdbdict = {}
                        atoms = []
                        i = 0
                        for atom in molecule:
                            aname = atom.name
                            while aname[0] in string.digits:
                                aname = aname[1:] + aname[0]
                            try:
                                element = atom['element']
                                a = ChemicalObjects.Atom(element, name = aname)
                            except KeyError:
                                try:
                                    a = ChemicalObjects.Atom(aname[:2],
                                                             name = aname)
                                except IOError:
                                    a = ChemicalObjects.Atom(aname[:1],
                                                             name = aname)
                            a.setPosition(atom.position)
                            atoms.append(a)
                            pdbdict[atom.name] = Database.AtomReference(i)
                            i = i + 1
                        m = ChemicalObjects.AtomCluster(atoms, name = name)
                        if len(pdbdict) == len(molecule):
                            # pdbmap is correct only if the AtomCluster has
                            # unique atom names
                            m.pdbmap = [(name, pdbdict)]
                    collection.addObject(m)
        return collection

    def createGroups(self, mapping):
        groups = []
        for name in self.molecules.keys():
            full_name = mapping.get(name, None)
            if full_name is not None:
                for molecule in self.molecules[name]:
                    g = ChemicalObjects.Group(full_name)
                    setConfiguration(g, [molecule], toplevel=0)
                    groups.append(g)
        return groups

    def createAll(self, molecule_names = None, permit_undefined=1):
        """Returns a collection containing all objects contained in
        the PDB file, i.e. the combination of the objects returned
        by createPeptideChains(), createNucleotideChains(), and
        createMolecules(). The parameters have the same meaning
        as for createMolecules()."""
        collection = Collections.Collection()
        peptide_chains = self.createPeptideChains()
        if peptide_chains:
            import Proteins
            collection.addObject(Proteins.Protein(peptide_chains))
        nucleotide_chains = self.createNucleotideChains()
        collection.addObject(nucleotide_chains)
        molecules = self.createMolecules(molecule_names, permit_undefined)
        collection.addObject(molecules)
        return collection

    def applyTo(self, object, atom_map=None):
        """Sets the configuration of |object| from the coordinates in the
        PDB file. The object must be compatible with the PDB file, i.e.
        contain the same subobjects and in the same order. This is usually
        only guaranteed if the object was created by the method
        createAll() from a PDB file with the same layout."""
        setConfiguration(object, self.residues, atom_map=atom_map)

#
# An alternative name for compatibility in Database files.
#
PDBFile = PDBConfiguration

#
# Set atom coordinates from PDB configuration.
#
def setResidueConfiguration(object, pdb_residue, pdbmap, altmap,
                            atom_map = None):
    defined = 0
    for atom in pdb_residue:
        name = atom.name
        try: name = altmap[name]
        except KeyError: pass
        try:
            pdbname = pdbmap[1][name]
        except KeyError:
            pdbname = None
            if not object.isSubsetModel():
                raise IOError('Atom '+atom.name+' of PDB residue ' +
                               pdb_residue.name+' not found in residue ' +
                               pdbmap[0] + ' of object ' + object.fullName())
        if pdbname:
            object.setPosition(pdbname, atom.position)
            try:
                object.setIndex(pdbname, atom.number-1)
            except ValueError:
                pass
            if atom_map is not None:
                atom_map[object.getAtom(pdbname)] = atom
            defined = defined + 1
    return defined

def setConfiguration(object, pdb_residues,
                     map = 'pdbmap', alt = 'pdb_alternative',
                     atom_map = None, toplevel = 1):
    defined = 0
    if hasattr(object, 'is_protein'):
        i = 0
        for chain in object:
            l = len(chain)
            defined = defined + setConfiguration(chain, pdb_residues[i:i+l],
                                                 map, alt, atom_map, 0)
            i = i + l
    elif hasattr(object, 'is_chain'):
        for i in range(len(object)):
            defined = defined + setConfiguration(object[i],
                                                 pdb_residues[i:i+1],
                                                 map, alt, atom_map, 0)
    elif hasattr(object, map):
        pdbmap = getattr(object, map)
        try: altmap = getattr(object, alt)
        except AttributeError: altmap = {}
        nres = len(pdb_residues)
        if len(pdbmap) != nres:
            raise IOError('PDB configuration does not match object ' +
                           object.fullName())
        for i in range(nres):
            defined = defined + setResidueConfiguration(object,
                                                        pdb_residues[i],
                                                        pdbmap[i], altmap,
                                                        atom_map)
    elif Collections.isCollection(object):
        nres = len(pdb_residues)
        if len(object) != nres:
            raise IOError('PDB configuration does not match object ' +
                           object.fullName())
        for i in range(nres):
            defined = defined + setConfiguration(object[i], [pdb_residues[i]],
                                                 map, alt, atom_map, 0)
    else:
        try:
            name = object.fullName()
        except AttributeError:
            try:
                name = object.name
            except AttributeError:
                name = '???'
        raise IOError('PDB configuration does not match object ' + name)
              
    if toplevel and defined < object.numberOfAtoms():
        name = '[unnamed object]'
        try:
            name = object.fullName()
        except: pass
        if name: name = ' in ' + name
        Utility.warning(`object.numberOfAtoms()-defined` + ' atom(s)' + name +
                        ' were not assigned (new) positions.')
    return defined


#
# Create objects from a PDB configuration.
#
molecule_names = {'HOH': 'water', 'TIP': 'water', 'TIP3': 'water',
                  'WAT': 'water', 'HEM': 'heme'}

def defineMolecule(code, name):
    if molecule_names.has_key(code):
        raise ValueError("PDB code " + code + " already used")
    molecule_names[code] = name

#
# This object represents a PDB file for output.
#
class PDBOutputFile:

    """PDB file for output

    Constructor: PDBOutputFile(|filename|, |subformat|='None')

    Arguments:

    |filename| -- the name of the PDB file that is created

    |subformat| -- a variant of the PDB format; these subformats
                   are defined in module Scientific.IO.PDB. The
                   default is the standard PDB format.
    """

    def __init__(self, filename, subformat= None):
        self.file = Scientific.IO.PDB.PDBFile(filename, 'w', subformat)
        self.warning = 0
        self.atom_sequence = []
        self.model_number = None

    def nextModel(self):
        "Start a new model"
        if self.model_number is None:
            self.model_number = 1
        else:
            self.file.writeLine('ENDMDL', '')
            self.model_number = self.model_number + 1
        self.file.writeLine('MODEL', {'serial_number': self.model_number})
        
    def write(self, object, configuration = None, tag = None):
        """Writes |object| to the file, using coordinates from
        |configuration| (defaults to the current configuration).
        The parameter |tag| is reserved for internal use."""
        if not ChemicalObjects.isChemicalObject(object):
            for o in object:
                self.write(o, configuration)
        else:
            toplevel = tag is None
            if toplevel:
                tag = Utility.uniqueAttribute()
            if hasattr(object, 'pdbmap'):
                for residue in object.pdbmap:
                    self.file.nextResidue(residue[0], )
                    sorted_atoms = residue[1].items()
                    sorted_atoms.sort(lambda x, y:
                                      cmp(x[1].number, y[1].number))
                    for atom_name, atom in sorted_atoms:
                        atom = object.getAtom(atom)
                        p = atom.position(configuration)
                        if Utility.isDefinedPosition(p):
                            try: occ = atom.occupancy
                            except AttributeError: occ = 0.
                            try: temp = atom.temperature_factor
                            except AttributeError: temp = 0.
                            self.file.writeAtom(atom_name, p/Units.Ang,
                                                occ, temp, atom.type.symbol)
                            self.atom_sequence.append(atom)
                        else:
                            self.warning = 1
                        setattr(atom, tag, None)
            else:
                if hasattr(object, 'is_protein'):
                    for chain in object:                    
                        self.write(chain, configuration, tag)
                elif hasattr(object, 'is_chain'):
                        self.file.nextChain(None, object.name)
                        for residue in object:
                            self.write(residue, configuration, tag)
                        self.file.terminateChain()
                elif hasattr(object, 'molecules'):
                    for m in object.molecules:
                        self.write(m, configuration, tag)
                elif hasattr(object, 'groups'):
                    for g in object.groups:
                        self.write(g, configuration, tag)
            if toplevel:
                for a in object.atomList():
                    if not hasattr(a, tag):
                        self.write(a, configuration, tag)
                    delattr(a, tag)

    def close(self):
        "Closes the file. Must be called in order to prevent data loss."
        if self.model_number is not None:
            self.file.writeLine('ENDMDL', '')
        self.file.close()
        if self.warning:
            Utility.warning('Some atoms are missing in the output file ' + \
                            'because their positions are undefined.')
            self.warning = 0
