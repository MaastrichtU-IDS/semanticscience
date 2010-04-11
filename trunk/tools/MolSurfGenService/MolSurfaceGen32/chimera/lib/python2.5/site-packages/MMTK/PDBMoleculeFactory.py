# This module constructs molecules and universes corresponding exactly
# to the contents of a PDB file, using residue and atom names as
# given in the file.
#
# Written by Konrad Hinsen
# last revision: 2007-12-13
#

"""
This module permits the construction of molecular objects that correspond
exactly to the contents of a PDB file. It is used for working with
experimental data. Note that most force fields cannot be applied to the
systems generated in this way.
"""

import MMTK
from MMTK.MoleculeFactory import MoleculeFactory
from Scientific.Geometry import Vector, delta
from Scientific import N
import copy

class PDBMoleculeFactory(MoleculeFactory):

    """
    A PDBMoleculeFactory generates molecules and universes from the
    contents of a PDBConfiguration. Nothing is added or left out
    (except as defined by the optional residue and atom filters), and
    the atom and residue names are exactly those of the original PDB
    file.
    """

    def __init__(self, pdb_conf, residue_filter=None, atom_filter=None):
        """
        @param pdb_conf: a PDBConfiguration
        @type pdb_conf: L{MMTK.PDB.PDBConfiguration}
        @param residue_filter: a function taking a residue object
                               (as defined in Scientific.IO.PDB)
                               and returning True if that residue is
                               to be kept in the molecule factory
        @type residue_filter: callable
        @param atom_filter: a function taking a residue object and an
                            atom object (as defined in Scientific.IO.PDB)     
                            and returning True if that atom is 
                            to be kept in the molecule factory
        @type atom_filter: callable
        """
        MoleculeFactory.__init__(self)

        if residue_filter is None and atom_filter is None:
            self.pdb_conf = pdb_conf
        else:
            self.pdb_conf = copy.deepcopy(pdb_conf)
            for residue in self.pdb_conf.residues:
                delete = []
                for atom in residue:
                    if atom_filter is not None \
                           and not atom_filter(residue, atom):
                        delete.append(atom)
                for atom in delete:
                    residue.deleteAtom(atom)
            delete = []
            for residue in self.pdb_conf.residues:
                if len(residue) == 0 or \
                       (residue_filter is not None
                        and not residue_filter(residue)):
                    delete.append(residue)
            for residue in delete:
                self.pdb_conf.deleteResidue(residue)

        self.peptide_chains = []
        self.nucleotide_chains = []
        self.molecules = {}
        self.makeAll()

    def retrieveMolecules(self):
        """
        Constructs Molecule objects corresponding to the contents of the
        PDBConfiguration. Each peptide or nucleotide chain becomes
        one molecule. For residues that are neither amino acids nor
        nucleic acids, each residue becomes one molecule.

        Chain molecules (peptide and nucleotide chains) can be iterated
        over to retrieve the individual residues. The residues can also
        be accessed as attributes whose names are the three-letter
        residue name (upper case) followed by an underscore and the
        residue number from the PDB file (e.g. 'GLY_34').

        Each object that corresponds to a PDB residue (i.e. each
        residue in a chain and each non-chain molecule) has the
        attributes 'residue_name' and 'residue_number'. Each atom has
        the attributes 'serial_number', 'occupancy' and
        'temperature_factor'. Atoms for which a ANISOU record exists
        also have an attribute 'u' whose value is a tensor object.
        
        @returns: a list of Molecule objects
        @rtype: C{list}
        """
        objects = []
        for chain in self.peptide_chains + self.nucleotide_chains:
            objects.append(self.retrieveMolecule(chain))
        for mollist in self.molecules.values():
            for residue in mollist:
                objects.append(self.retrieveMolecule(residue))
        return objects

    def retrieveUniverse(self):
        """
        Constructs an empty universe (OrthrhombicPeriodicUniverse or
        ParallelepipedicPeriodicUniverse) representing the
        unit cell of the crystal.
        
        @returns: a universe
        @rtype: L{MMTK.Universe.Universe}
        """
        e1 = self.pdb_conf.from_fractional(Vector(1., 0., 0.))
        e2 = self.pdb_conf.from_fractional(Vector(0., 1., 0.))
        e3 = self.pdb_conf.from_fractional(Vector(0., 0., 1.))
        if abs(e1.normal()*Vector(1., 0., 0.)-1.) < 1.e-15 \
               and abs(e2.normal()*Vector(0., 1., 0.)-1.) < 1.e-15 \
               and abs(e3.normal()*Vector(0., 0., 1.)-1.) < 1.e-15:
            universe = \
               MMTK.OrthorhombicPeriodicUniverse((e1.length(),
                                                  e2.length(),
                                                  e3.length()))
        else:
            universe = MMTK.ParallelepipedicPeriodicUniverse((e1, e2, e3))
        return universe

    def retrieveAsymmetricUnit(self):
        """
        Constructs a universe (OrthrhombicPeriodicUniverse or
        ParallelepipedicPeriodicUniverse) representing the
        unit cell of the crystal and adds the molecules representing
        the asymmetric unit.
        
        @returns: a universe
        @rtype: L{MMTK.Universe.Universe}
        """
        universe = self.retrieveUniverse()
        universe.addObject(self.retrieveMolecules())
        return universe

    def retrieveUnitCell(self, compact=True):
        """
        Constructs a universe (OrthrhombicPeriodicUniverse or
        ParallelepipedicPeriodicUniverse) representing the
        unit cell of the crystal and adds all the molecules it
        contains, i.e. the molecules of the asymmetric unit and
        its images obtained by applying the crystallographic
        symmetry operations.

        @param compact: if C{True}, the images are shifted such that
                        their centers of mass lie inside the unit cell.
        @type compact: C{bool}
        @returns: a universe
        @rtype: L{MMTK.Universe.Universe}
        """
        universe = self.retrieveUniverse()
        asu_count = 0
        for symop in self.pdb_conf.cs_transformations:
            transformation = symop.asLinearTransformation()
            rotation = transformation.tensor
            translation = transformation.vector
            is_asu = translation.length() < 1.e-8 and \
                     N.maximum.reduce(N.ravel(N.fabs((rotation
                                                      -delta).array))) < 1.e-8
            if is_asu:
                asu_count += 1
            asu = MMTK.Collection(self.retrieveMolecules())
            for atom in asu.atomList():
                atom.setPosition(symop(atom.position()))
                if hasattr(atom, 'u'):
                    atom.u = rotation.dot(atom.u.dot(rotation.transpose()))
                atom.in_asu = is_asu
            if compact:
                cm = asu.centerOfMass()
                cm_fr = self.pdb_conf.to_fractional(cm)
                cm_fr = Vector(cm_fr[0] % 1., cm_fr[1] % 1., cm_fr[2] % 1.) \
                        - Vector(0.5, 0.5, 0.5)
                cm = self.pdb_conf.from_fractional(cm_fr)
                asu.translateTo(cm)
            universe.addObject(asu)
        assert asu_count == 1
        return universe

    def makeAll(self):
        cystines = []
        for chain in self.pdb_conf.peptide_chains:
            chain_id = chain.chain_id
            if not chain_id:
                chain_id = 'PeptideChain'+str(len(self.peptide_chains)+1)
            for residue in chain:
                if residue.name == 'CYS' and residue.atoms.has_key('SG'):
                    cystines.append((chain_id, residue, residue.atoms['SG']))
            self.makeChain(chain, chain_id)
            self.peptide_chains.append(chain_id)
        for i in range(len(cystines)):
            for j in range(i+1, len(cystines)):
                d = (cystines[i][2].position-cystines[j][2].position).length()
                if d < 0.25:
                    if cystines[i][0] is cystines[j][0]:
                        cys1 = cystines[i][1]
                        cys2 = cystines[j][1]
                        cys1 = cys1.name + '_' + str(cys1.number)
                        cys2 = cys2.name + '_' + str(cys2.number)
                        self.addBond(cystines[i][0], cys1+'.SG', cys2+'.SG')
                    else:
                        raise NotImplemented('Inter-chain disulfide bridges'
                                             ' not yet implemented')
        for chain in self.pdb_conf.nucleotide_chains:
            chain_id = chain.chain_id
            if not chain_id:
                chain_id = 'NucleotideChain'+str(len(self.nucleotide_chains)+1)
            self.makeChain(chain, chain_id)
            self.nucleotide_chains.append(chain_id)
        for molname, mollist in self.pdb_conf.molecules.items():
            self.molecules[molname] = []
            for residue in mollist:
                base_resname = residue.name + '_' + str(residue.number)
                suffix = 1
                resname = base_resname
                done = False
                while not done:
                    try:
                        self.makeResidue(residue, resname)
                        done = True
                    except ValueError, e:
                        if str(e).split()[0] == "redefinition":
                            resname = base_resname + "_" + str(suffix)
                            suffix += 1
                        else:
                            raise
                self.molecules[molname].append(resname)

    def makeChain(self, chain, chain_id):
        groups = []
        for residue in chain:
            resname = chain_id + '_' + residue.name + '_' + str(residue.number)
            groups.append(resname)
            self.makeResidue(residue, resname)
        self.createGroup(chain_id)
        local_resnames = []
        for resname in groups:
            local_resname = '_'.join(resname.split('_')[1:])
            self.addSubgroup(chain_id, local_resname, resname)
            local_resnames.append(local_resname)
        self.setAttribute(chain_id, 'sequence', local_resnames)
        for i in range(1, len(chain)):
            if chain[i-1].number == chain[i].number-1:
                for atom1 in chain[i-1]:
                    for atom2 in chain[i]:
                        if self.assumeBond(atom1.properties['element'],
                                           atom1.position,
                                           atom2.properties['element'],
                                           atom2.position):
                            self.addBond(chain_id,
                                         local_resnames[i-1]+'.'+atom1.name,
                                         local_resnames[i]+'.'+atom2.name)
                       
    def makeResidue(self, residue, group_name):
        self.createGroup(group_name)
        self.setAttribute(group_name, 'residue_name', residue.name)
        self.setAttribute(group_name, 'residue_number', residue.number)
        atoms = []
        for atom in residue:
            atoms.append((atom.name, atom.properties['element'],
                          atom.position))
            self.addAtom(group_name, atom.name, atom.properties['element'])
            self.setPosition(group_name, atom.name, atom.position)
            self.setAttribute(group_name, atom.name+'.temperature_factor',
                              atom.properties['temperature_factor'])
            self.setAttribute(group_name, atom.name+'.occupancy',
                              atom.properties['occupancy'])
            self.setAttribute(group_name, atom.name+'.serial_number',
                              atom.properties['serial_number'])
            if atom.properties.has_key('u'):
                self.setAttribute(group_name, atom.name+'.u',
                                  atom.properties['u'])
        for i in range(len(atoms)):
            atom_i, element_i, pos_i = atoms[i]
            for j in range(i+1, len(atoms)):
                atom_j, element_j, pos_j = atoms[j]
                if self.assumeBond(element_i, pos_i, element_j, pos_j):
                    self.addBond(group_name, atom_i, atom_j)

    def assumeBond(self, element1, pos1, element2, pos2):
        if element1 > element2:
            element1, element2 = element2, element1
        try:
            d = self.bond_lengths[(element1, element2)]
            return (pos1-pos2).length() < d
        except KeyError:
            return False

    bond_lengths = {('C', 'C'): 0.16,
                    ('C', 'H'): 0.115,
                    ('C', 'N'): 0.215,
                    ('C', 'O'): 0.16,
                    ('C', 'P'): 0.2,
                    ('C', 'S'): 0.2,
                    ('H', 'H'): 0.08,
                    ('H', 'N'): 0.115,
                    ('H', 'O'): 0.115,
                    ('H', 'P'): 0.15,
                    ('H', 'S'): 0.14,
                    ('N', 'N'): 0.155,
                    ('N', 'O'): 0.15,
                    ('O', 'O'): 0.16,
                    ('O', 'P'): 0.17,
                    ('O', 'S'): 0.16,
                    ('P', 'S'): 0.2,
                    ('S', 'S'): 0.25,
                    }
