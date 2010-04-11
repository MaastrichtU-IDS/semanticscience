# This module implements classes for peptide chains and proteins.
#
# Written by Konrad Hinsen
# last revision: 2007-5-25
#

import Biopolymers, Bonds, ChemicalObjects, Collections, ConfigIO, Database
import Units, Universe, Utility
from Scientific.Geometry import Vector
import operator, string

from Biopolymers import defineAminoAcidResidue

#
# Residues are special groups
#
class Residue(Biopolymers.Residue):

    """Amino acid residue

    A Glossary:Subclass of Class:MMTK.ChemicalObjects.Group.

    Amino acid residues are a special kind of group. Like any other
    group, they are defined in the chemical database. Each residue
    has two subgroups ('peptide' and 'sidechain') and is usually
    connected to other residues to form a peptide chain. The database
    contains three variants of each residue (N-terminal, C-terminal,
    non-terminal) and various models (all-atom, united-atom,
    C_alpha).

    Constructor: Residue(|kind|, |model|="all")

    Arguments:

    |kind| -- the name of the residue in the chemical database. This
              is the full name of the residue plus the suffix
              "_nt" or "_ct" for the terminal variants.

    |model| -- one of "all" (all-atom), "none" (no hydrogens),
               "polar" (united-atom with only polar hydrogens),
               "polar_charmm" (like "polar", but defining
               polar hydrogens like in the CHARMM force field),
               "polar_opls" (like "polar", but defining
               polar hydrogens like in the latest OPLS force field),
               "calpha" (only the C_alpha atom)
    """

    def __init__(self, name = None, model = 'all'):
        if name is not None:
            blueprint = _residueBlueprint(name, model)
            ChemicalObjects.Group.__init__(self, blueprint)
            self.model = model
            self._init()

    def _init(self):
        Biopolymers.Residue._init(self)
        # create peptide attribute for calpha model
        if self.model == 'calpha':
            self.peptide = self

    def _makeCystine(self):
        if self.model == 'calpha':
            return self
        if string.lower(self.symbol) != 'cys':
            raise ValueError(`self` + " is not cysteine.")
        new_residue = 'cystine_ss'
        if hasattr(self.peptide, 'H_3'):
            new_residue = new_residue + '_nt'
        elif hasattr(self.peptide, 'O_2'):
            new_residue = new_residue + '_ct'
        new_residue = Residue(new_residue, self.model)
        for g in ['peptide', 'sidechain']:
            g_old = getattr(self, g)
            g_new = getattr(new_residue, g)
            atoms = map(lambda a: a.name, getattr(g_new, 'atoms'))
            for a in atoms:
                set_method = getattr(getattr(g_new, a), 'setPosition')
                set_method(getattr(getattr(g_old, a), 'position')())
        return new_residue

    def isSubsetModel(self):
        return self.model == 'calpha'

    def backbone(self):
        "Returns the peptide group."
        return self.peptide

    def sidechains(self):
        "Returns the sidechain group."
        return self.sidechain

    def phiPsi(self, conf = None):
        "Returns the values of the backbone dihedral angles phi and psi."
        universe = self.universe()
        if universe is None:
            universe = Universe.InfiniteUniverse()
        C = None
        for a in self.peptide.N.bondedTo():
            if a.parent.parent != self:
                C = a
                break
        if C is None:
            phi = None
        else:
            phi = universe.dihedral(self.peptide.C, self.peptide.C_alpha,
                                    self.peptide.N, C, conf)
        N = None
        for a in self.peptide.C.bondedTo():
            if a.parent.parent != self:
                N = a
                break
        if N is None:
            psi = None
        else:
            psi = universe.dihedral(N, self.peptide.C, self.peptide.C_alpha,
                                    self.peptide.N, conf)
        return phi, psi

    def phiAngle(self):
        """Returns a Class:MMTK.InternalCoordinates.DihedralAngle object
        representing the phi angle."""
        from MMTK.InternalCoordinates import DihedralAngle
        C = None
        for a in self.peptide.N.bondedTo():
            if a.parent.parent != self:
                C = a
                break
        if C is None:
            raise ValueError("residue is N-terminus")
        return DihedralAngle(self.peptide.C, self.peptide.C_alpha,
                             self.peptide.N, C)

    def psiAngle(self):
        """Returns a Class:MMTK.InternalCoordinates.DihedralAngle object
        representing the psi angle."""
        from MMTK.InternalCoordinates import DihedralAngle
        N = None
        for a in self.peptide.C.bondedTo():
            if a.parent.parent != self:
                N = a
                break
        if N is None:
            raise ValueError("residue is C-terminus")
        return DihedralAngle(N, self.peptide.C, self.peptide.C_alpha,
                             self.peptide.N)

    def chiAngle(self):
        """Returns a Class:MMTK.InternalCoordinates.DihedralAngle object
        representing the chi angle."""
        from MMTK.InternalCoordinates import DihedralAngle
        try:
            C_beta = self.sidechain.C_beta
        except AttributeError:
            raise ValueError("no C_beta in sidechain")
        X = None
        for atom_name in ['C_gamma', 'C_gamma_1', 'S_gamma',
                          'O_gamma', 'O_gamma_1', 'H_beta_1']:
            try:
                X = getattr(self.sidechain, atom_name)
                break
            except AttributeError:
                pass
        if X is None:
            raise ValueError("no sidechain reference atom found")
        return DihedralAngle(self.peptide.N, self.peptide.C_alpha,
                             C_beta, X)


def _residueBlueprint(name, model):
    try:
        blueprint = _residue_blueprints[(name, model)]
    except KeyError:
        if model == 'polar':
            name = name + '_uni'
        elif model == 'polar_charmm':
            name = name + '_uni2'
        elif model == 'polar_oldopls':
            name = name + '_uni3'
        elif model == 'none':
            name = name + '_noh'
        elif model == 'calpha':
            name = name + '_calpha'
        blueprint = Database.BlueprintGroup(name)
        _residue_blueprints[(name, model)] = blueprint
    return blueprint

_residue_blueprints = {}

#
# Peptide chains are molecules with added features.
#
class PeptideChain(Biopolymers.ResidueChain):

    """Peptide chain

    A Glossary:Subclass of Class:MMTK.Biopolymers.ResidueChain.

    Peptide chains consist of amino acid residues that are linked
    by peptide bonds. They are a special kind of molecule, i.e.
    all molecule operations are available.

    Constructor: PeptideChain(|sequence|, **|properties|)

    Arguments:

    |sequence| -- the amino acid sequence. This can be a string
                  containing the one-letter codes, or a list
                  of three-letter codes, or a PDBPeptideChain object.
                  If a PDBPeptideChain object is supplied, the atomic
                  positions it contains are assigned to the atoms
                  of the newly generated peptide chain, otherwise the
                  positions of all atoms are undefined.

    |properties| -- optional keyword properties:

    - model: one of "all" (all-atom), "no_hydrogens" or "none" (no hydrogens),
             "polar_hydrogens" or "polar" (united-atom with only polar
             hydrogens), "polar_charmm" (like "polar", but defining
             polar hydrogens like in the CHARMM force field),
             "polar_opls" (like "polar", but defining
             polar hydrogens like in the latest OPLS force field),
             "calpha" (only the C_alpha atom of each residue). Default
             is "all".

    - n_terminus: 1 if the first residue should be constructed using the
                  N-terminal variant, 0 if the non-terminal version should
                  be used. Default is 1.

    - c_terminus: 1 if the last residue should be constructed using the
                  C-terminal variant, 0 if the non-terminal version should
                  be used. Default is 1.

    - circular: 1 if a peptide bond should be constructed between the first
                and the last residue. Default is 0.

    - name: a name for the chain (a string)


    Peptide chains act as sequences of residues. If 'p' is a PeptideChain
    object, then

    - 'len(p)' yields the number of residues

    - 'p[i]' yields residue number 'i' (counting from zero)

    - 'p[i:j]' yields the subchain from residue number 'i' up to but excluding
               residue number 'j'
    """

    def __init__(self, sequence, **properties):
        if sequence is not None:
            model = 'all'
            if properties.has_key('model'):
                model = string.lower(properties['model'])
            elif properties.has_key('hydrogens'):
                model = properties['hydrogens']
                if model == 1: model = 'all'
                elif model == 0: model = 'none'
                else: model = string.lower(model)
            if model == 'no_hydrogens':
                model = 'none'
            elif model == 'polar_hydrogens':
                model = 'polar'
            n_term = self.binaryProperty(properties, 'n_terminus', 1)
            c_term = self.binaryProperty(properties, 'c_terminus', 1)
            circular = self.binaryProperty(properties, 'circular', 0)
            self.version_spec = {'n_terminus': n_term,
                                 'c_terminus': c_term,
                                 'model': model,
                                 'circular': circular}
            if type(sequence[0]) == type(''):
                conf = None
                numbers = range(len(sequence))
            else:
                conf = sequence
                sequence = conf.sequence()
                numbers = [r.number for r in conf]
            sequence = map(Biopolymers._fullName, sequence)
            if model != 'calpha':
                if n_term:
                    sequence[0] = sequence[0] + '_nt'
                if c_term:
                    sequence[-1] = sequence[-1] + '_ct'

            self.groups = []
            n = 0
            for residue, number in zip(sequence, numbers):
                n = n + 1
                r = Residue(residue, model)
                r.name = r.symbol + str(number)
                r.sequence_number = n
                r.parent = self
                self.groups.append(r)

            self._setupChain(circular, properties, conf)

    is_peptide_chain = 1

    def __getslice__(self, first, last):
        return SubChain(self, self.groups[first:last])

    def sequence(self):
        """Returns the primary sequence as a list of three-letter residue
        codes."""
        return map(lambda r: r.symbol, self.groups)

    def backbone(self):
        "Returns a collection containing the peptide groups of all residues."
        backbone = Collections.Collection()
        for r in self.groups:
            try:
                backbone.addObject(r.peptide)
            except AttributeError:
                pass
        return backbone
    
    def sidechains(self):
        "Returns a collection containing the sidechain groups of all residues."
        sidechains = Collections.Collection()
        for r in self.groups:
            try:
                sidechains.addObject(r.sidechain)
            except AttributeError:
                pass
        return sidechains

    def phiPsi(self, conf = None):
        """Returns a list of the (phi, psi) backbone angle pairs
        for each residue."""
        universe = self.universe()
        if universe is None:
            universe = Universe.InfiniteUniverse()
        angles = []
        for i in range(len(self)):
            r = self[i]
            if i == 0:
                phi = None
            else:
                phi = universe.dihedral(r.peptide.C, r.peptide.C_alpha,
                                        r.peptide.N,
                                        self[i-1].peptide.C, conf)
            if i == len(self)-1:
                psi = None
            else:
                psi = universe.dihedral(self[i+1].peptide.N,
                                        r.peptide.C, r.peptide.C_alpha,
                                        r.peptide.N, conf)
            angles.append((phi, psi))
        return angles

    def replaceResidue(self, r_old, r_new):
        """Replaces residue |r_old|, which must be a residue object that
        is part of the chain, by the residue object |r_new|."""
        n = self.groups.index(r_old)
        for a in r_old.atoms:
            self.atoms.remove(a)
        obsolete_bonds = []
        for b in self.bonds:
            if b.a1 in r_old.atoms or b.a2 in r_old.atoms:
                obsolete_bonds.append(b)
        for b in obsolete_bonds:
            self.bonds.remove(b)
        r_old.parent = None
        self.atoms.extend(r_new.atoms)
        self.bonds.extend(r_new.bonds)
        r_new.sequence_number = n+1
        r_new.name = r_new.symbol+`n+1`
        r_new.parent = self
        self.groups[n] = r_new
        if n > 0:
            peptide_old = self.bonds.bondsOf(r_old.peptide.N)
            if peptide_old:
                self.bonds.remove(peptide_old[0])
            self.bonds.append(Bonds.Bond((self.groups[n-1].peptide.C,
                                          self.groups[n].peptide.N)))
        if n < len(self.groups)-1:
            peptide_old = self.bonds.bondsOf(r_old.peptide.C)
            if peptide_old:
                self.bonds.remove(peptide_old[0])
            self.bonds.append(Bonds.Bond((self.groups[n].peptide.C,
                                          self.groups[n+1].peptide.N)))
        if isinstance(self.parent, ChemicalObjects.Complex):
            self.parent.recreateAtomList()
        universe = self.universe()
        if universe is not None:
            universe._changed(True)

    # add sulfur bridges between cysteine residues
    def _addSSBridges(self, bonds):
        for b in bonds:
            cys1 = b[0]
            if string.lower(cys1.symbol) == 'cyx':
                cys_ss1 = cys1
            else:
                cys_ss1 = cys1._makeCystine()
                self.replaceResidue(cys1, cys_ss1)
            cys2 = b[1]
            if string.lower(cys2.symbol) == 'cyx':
                cys_ss2 = cys2
            else:
                cys_ss2 = cys2._makeCystine()
                self.replaceResidue(cys2, cys_ss2)
            self.bonds.append(Bonds.Bond((cys_ss1.sidechain.S_gamma,
                                          cys_ss2.sidechain.S_gamma)))

    def _descriptionSpec(self):
        kwargs = ''
        for name, value in self.version_spec.items():
            kwargs = kwargs + name + '=' + `value` + ','
        return "S", kwargs[:-1]

    def _typeName(self):
        return reduce(operator.add, self.sequence())

    def _graphics(self, conf, distance_fn, model, module, options):
        if model != 'backbone':
            return ChemicalObjects.Molecule._graphics(self, conf,
                                                      distance_fn, model,
                                                      module, options)
        color = options.get('color', 'black')
        material = module.EmissiveMaterial(color)
        objects = []
        for i in range(len(self.groups)-1):
            a1 = self.groups[i].peptide.C_alpha
            a2 = self.groups[i+1].peptide.C_alpha
            p1 = a1.position(conf)
            p2 = a2.position(conf)
            if p1 is not None and p2 is not None:
                bond_vector = 0.5*distance_fn(a1, a2, conf)
                cut = bond_vector != 0.5*(p2-p1)
                if not cut:
                    objects.append(module.Line(p1, p2, material = material))
                else:
                    objects.append(module.Line(p1, p1+bond_vector,
                                               material = material))
                    objects.append(module.Line(p2, p2-bond_vector,
                                               material = material))
        return objects

#
# Subchains are created by slicing chains or extracting a chain from
# a group of connected chains.
#
class SubChain(PeptideChain):

    """A contiguous part of a peptide chain

    SubChain objects are the result of slicing operations on
    PeptideChain objects. They cannot be created directly.
    SubChain objects permit all operations of PeptideChain
    objects, but cannot be added to a universe.
    """

    def __init__(self, chain=None, groups=None, name = ''):
        if chain is not None:
            self.groups = groups
            self.atoms = []
            self.bonds = []
            for g in self.groups:
                self.atoms.extend(g.atoms)
                self.bonds.extend(g.bonds)
            for i in range(len(self.groups)-1):
                link1 = self.groups[i].chain_links[1]
                link2 = self.groups[i+1].chain_links[0]
                self.bonds.append(Bonds.Bond((link1, link2)))
            self.bonds = Bonds.BondList(self.bonds)
            self.name = name
            self.model = chain.model
            self.parent = chain.parent
            self.type = None
            self.configurations = {}
            self.part_of = chain

    is_incomplete = 1

    def __repr__(self):
        if self.name == '':
            return 'SubChain of ' + repr(self.part_of)
        else:
            return ChemicalObjects.Molecule.__repr__(self)
    __str__ = __repr__

    def replaceResidue(self, r_old, r_new):
        for a in r_old.atoms:
            self.atoms.remove(a)
        obsolete_bonds = []
        for b in self.bonds:
            if b.a1 in r_old.atoms or b.a2 in r_old.atoms:
                obsolete_bonds.append(b)
        for b in obsolete_bonds:
            self.bonds.remove(b)
        n = self.groups.index(r_old)
        if n > 0:
            peptide_old = self.bonds.bondsOf(r_old.peptide.N)
            self.bonds.remove(peptide_old[0])
        if n < len(self.groups)-1:
            peptide_old = self.bonds.bondsOf(r_old.peptide.C)
            self.bonds.remove(peptide_old[0])
        PeptideChain.replaceResidue(self.part_of, r_old, r_new)
        self.groups[n] = r_new
        self.atoms.extend(r_new.atoms)
        self.bonds.extend(r_new.bonds)
        if n > 0:
            self.bonds.append(Bonds.Bond((self.groups[n-1].peptide.C,
                                          self.groups[n].peptide.N)))
        if n < len(self.groups)-1:
            self.bonds.append(Bonds.Bond((self.groups[n].peptide.C,
                                          self.groups[n+1].peptide.N)))

#
# Connected chains are collections of peptide chains connected by s-s bridges.
#
class ConnectedChains(PeptideChain):

    # Peptide chains connected by sulfur bridges
    #
    # A group of peptide chains connected by sulfur bridges must be considered
    # a single molecule due to the presence of chemical bonds. Such a molecule
    # is represented by a ConnectedChains object. These objects are created
    # automatically when a Protein object is assembled. They are normally
    # not used directly by application programs. When a chain with sulfur
    # bridges to other chains is extracted from a Protein object, the
    # return value is a SubChain object that indirectly refers to a
    # ConnectedChains object.

    def __init__(self, chains=None):
        if chains is not None:
            self.chains = []
            self.groups = []
            self.atoms = []
            self.bonds = Bonds.BondList([])
            self.chain_names = []
            self.model = chains[0].model
            version_spec = chains[0].version_spec
            for c in chains:
                if c.version_spec['model'] != version_spec['model']:
                    raise ValueError("mixing chains of different model: " +
                                      c.version_spec['model'] + "/" +
                                      version_spec['model'])
                ng = len(self.groups)
                self.chains.append((c.name, ng, ng+len(c.groups),
                                    c.version_spec))
                self.groups.extend(c.groups)
                self.atoms.extend(c.atoms)
                self.bonds.extend(c.bonds)
                try: name = c.name
                except AttributeError: name = ''
                self.chain_names.append(name)
            for g in self.groups:
                g.parent = self
            self.name = ''
            self.parent = None
            self.type = None
            self.configurations = {}
            for i in range(len(self.chains)):
                c = self.chains[i]
                sub_chain = SubChain(self, self.groups[c[1]:c[2]], c[0])
                sub_chain.version_spec = c[3]
                for g in sub_chain.groups:
                    g.parent = sub_chain
                self.chains[i] = sub_chain
    is_connected_chains = 1

    def __len__(self):
        return len(self.chains)

    def __getitem__(self, item):
        return self.chains[item]

    def __getslice__(self, first, last):
        raise TypeError("Can't slice connected chains")

    def _graphics(self, conf, distance_fn, model, module, options):
        if model != 'backbone':
            return ChemicalObjects.Molecule._graphics(self, conf,
                                                      distance_fn, model,
                                                      module, options)
        objects = []
        for chain in self:
            objects = objects + chain._graphics(conf, distance_fn,
                                                model, module, options)
        return objects

#
# Proteins are complexes of peptide chains, connected peptide chains,
# and possibly other things.
#
class Protein(ChemicalObjects.Complex):

    """Protein

    A Glossary:Subclass of Class:MMTK.Complex.

    A Protein object is a special kind of a Complex object which
    is made up of peptide chains.

    Constructor: Protein(|specification|, **|properties|)

    Arguments:

    |specification| -- one of:

    - a list of peptide chain objects

    - a string, which is interpreted as the name of a database definition
      for a protein. If that definition does not exist, the string
      is taken to be the name of a PDB file, from which all peptide chains
      are constructed and assembled into a protein.

    |properties| -- optional keyword properties:

    - model: one of "all" (all-atom), "no_hydrogens" or "none" (no hydrogens),
             "polar_hydrogens" or "polar" (united-atom with only polar
             hydrogens), "polar_charmm" (like "polar", but defining
             polar hydrogens like in the CHARMM force field),
             "polar_opls" (like "polar", but defining
             polar hydrogens like in the latest OPLS force field),
             "calpha" (only the C_alpha atom of each residue). Default
             is "all".

    - position: the center-of-mass position of the protein (a vector)

    - name: a name for the protein (a string)

    If the atoms in the peptide chains that make up a protein have
    defined positions, sulfur bridges within chains and between
    chains will be constructed automatically during protein generation
    based on a distance criterion between cystein sidechains.


    Proteins act as sequences of chains. If 'p' is a Protein object, then

    - 'len(p)' yields the number of chains

    - 'p[i]' yields chain number 'i' (counting from zero)
    """

    def __init__(self, *items, **properties):
        if items == (None,):
            return
        self.name = ''
        if len(items) == 1 and type(items[0]) == type(''):
            try:
                filename = Database.databasePath(items[0], 'Proteins')
                found = 1
            except IOError:
                found = 0
            if found:
                blueprint = Database.BlueprintProtein(items[0])
                items = blueprint.chains
                for attr, value in vars(blueprint).items():
                    if attr not in ['type', 'chains']:
                        setattr(self, attr, value)
            else:
                import PDB
                conf = PDB.PDBConfiguration(items[0])
                model = properties.get('model', 'all')
                items = conf.createPeptideChains(model)
        molecules = []
        for i in items:
            if ChemicalObjects.isChemicalObject(i):
                molecules.append(i)
            else:
                molecules = molecules + list(i)
        for m, i in zip(molecules, range(len(molecules))):
            m._numbers = [i]
            if not m.name:
                m.name = 'chain'+`i`
        ss = self._findSSBridges(molecules)
        new_mol = {}
        for m in molecules:
            new_mol[m] = ([m],[])
        for bond in ss:
            m1 = new_mol[bond[0].topLevelChemicalObject()]
            m2 = new_mol[bond[1].topLevelChemicalObject()]
            if m1 == m2:
                m1[1].append(bond)
            else:
                combined = (m1[0] + m2[0], m1[1] + m2[1] + [bond])
                for m in combined[0]:
                    new_mol[m] = combined
        self.molecules = []
        while new_mol:
            m = new_mol.values()[0]
            for i in m[0]:
                del new_mol[i]
            bonds = m[1]
            if len(m[0]) == 1:
                m = m[0][0]
            else:
                numbers = reduce(operator.add, map(lambda i: i._numbers, m[0]))
                m = ConnectedChains(m[0])
                m._numbers = numbers
                for c in m:
                    c.parent = self
            m._addSSBridges(bonds)
            m.parent = self
            self.molecules.append(m)

        self.atoms = []
        self.chains = []
        for m in self.molecules:
            self.atoms.extend(m.atoms)
            if hasattr(m, 'is_connected_chains'):
                for c, name, i in zip(range(len(m)),
                                   m.chain_names, m._numbers):
                    self.chains.append((m, c, name, i))
            else:
                try: name = m.name
                except AttributeError: name = ''
                self.chains.append((m, None, name, m._numbers[0]))
        self.chains.sort(lambda c1, c2: cmp(c1[3], c2[3]))
        self.chains = map(lambda c: c[:3], self.chains)

        self.parent = None
        self.type = None
        self.configurations = {}
        try:
            self.name = properties['name']
            del properties['name']
        except KeyError: pass
        if properties.has_key('position'):
            self.translateTo(properties['position'])
            del properties['position']
        self.addProperties(properties)

        undefined = 0
        for a in self.atoms:
            if a.position() is None:
                undefined = undefined + 1
        if undefined > 0 and undefined != len(self.atoms):
            Utility.warning('Some atoms in a protein ' +
                            'have undefined positions.')

    is_protein = 1

    def __len__(self):
        return len(self.chains)

    def __getitem__(self, item):
        if isinstance(item, int):
            m, c, name = self.chains[item]
        else:
            for m, c, name in self.chains:
                if name == item:
                    break
            if name != item:
                raise ValueError('No chain with name ' + item)
        if c is None:
            return m
        else:
            return m[c]

    def residuesOfType(self, *types):
        """Returns a collection that contains all residues whose type
        (one- or three-letter code) is contained in |types|."""
        rlist = Collections.Collection([])
        for m in self.molecules:
            if isPeptideChain(m):
                rlist = rlist + apply(m.residuesOfType, types)
        return rlist

    def backbone(self):
        """Returns a collection containing the peptide groups of all residues
        in all chains."""
        rlist = Collections.Collection([])
        for m in self.molecules:
            if isPeptideChain(m):
                rlist = rlist + m.backbone()
        return rlist

    def sidechains(self):
        """Returns a collection containing the sidechain groups of all
        residues in all chains."""
        rlist = Collections.Collection([])
        for m in self.molecules:
            if isPeptideChain(m):
                rlist = rlist + m.sidechains()
        return rlist

    def residues(self):
        "Returns a collection containing all residues in all chains."
        rlist = Collections.Collection([])
        for m in self.molecules:
            if isPeptideChain(m):
                rlist = rlist + m.residues()
        return rlist

    def phiPsi(self, conf = None):
        """Returns a list containing the phi/psi backbone dihedrals for
        all chains."""
        angles = []
        for chain in self:
            angles.append(chain.phiPsi(conf))
        return angles

    _ss_bond_max = 0.25*Units.nm

    def _findSSBridges(self, molecules):
        molecules = filter(lambda m: hasattr(m, 'is_peptide_chain'), molecules)
        cys = Collections.Collection([])
        for m in molecules:
            if m.version_spec['model'] != 'calpha':
                cys = cys + m.residuesOfType('cys') + m.residuesOfType('cyx')
        s = cys.map(lambda r: r.sidechain.S_gamma)
        ns = len(s)
        ss = []
        for i in xrange(ns-1):
            for j in xrange(i+1,ns):
                r1 = s[i].position()
                r2 = s[j].position()
                if r1 and r2 and (r1-r2).length() < self._ss_bond_max:
                    ss.append((cys[i], cys[j]))
        return ss

    def _subunits(self):
        return list(self)

    def _description(self, tag, index_map, toplevel):
        if not toplevel:
            raise ValueError
        return 'l(' + `self.__class__.__name__` + ',' + `self.name` + ',[' + \
               reduce(operator.add,
                      map(lambda o, t=tag, m=index_map:
                                 o._description(t, m, 1)+',',
                          self)) + '])'

    def _graphics(self, conf, distance_fn, model, module, options):
        if model != 'backbone':
            return ChemicalObjects.Complex._graphics(self, conf, distance_fn,
                                                     model, module, options)
        objects = []
        for chain in self:
            objects = objects + chain._graphics(conf, distance_fn,
                                                model, module, options)
        return objects

#
# Type check functions
#
def isPeptideChain(x):
    "Returns 1 f |x| is a peptide chain."
    return hasattr(x, 'is_peptide_chain')

def isProtein(x):
    "Returns 1 f |x| is a protein."
    return hasattr(x, 'is_protein')
