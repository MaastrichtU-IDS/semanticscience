# This module implements the base classes for proteins and
# nucleic acid chains.
#
# Written by Konrad Hinsen
# last revision: 2007-4-18
#

import Bonds, ChemicalObjects, Collections, Database, PDB
import string

class Residue(ChemicalObjects.Group):

    def __setstate__(self, state):
        for attr, value in state.items():
            self.__dict__[attr] = value
        try:
            self.model = self.hydrogens
        except AttributeError:
            pass
        self._init()

    def _init(self):
        # construct PDB map and alternative names
        type = self.type
        if not hasattr(type, 'pdbmap'):
            pdb_dict = {}
            type.pdbmap = [(type.symbol, pdb_dict)]
            offset = 0
            for g in type.groups:
                for name, atom in g.pdbmap[0][1].items():
                    pdb_dict[name] = Database.AtomReference(atom.number + \
                                                            offset)
                offset = offset + len(g.atoms)
        if not hasattr(type, 'pdb_alternative'):
            alt_dict = {}
            for g in type.groups:
                if hasattr(g, 'pdb_alternative'):
                    for key, value in g.pdb_alternative.items():
                        alt_dict[key] = value
            setattr(type, 'pdb_alternative', alt_dict)


class ResidueChain(ChemicalObjects.Molecule):

    """A chain of residues

    A Glossary:Subclass of Class:MMTK.Molecule.

    This is an Glossary:AbstractBaseClass that defines operations
    common to peptide chains and nucleic acid chains.
    """
    
    is_chain = 1

    def _setupChain(self, circular, properties, conf):
        self.atoms = []
        self.bonds = []
        for g in self.groups:
            self.atoms = self.atoms + g.atoms
            self.bonds = self.bonds + g.bonds
        for i in range(len(self.groups)-1):
            link1 = self.groups[i].chain_links[1]
            link2 = self.groups[i+1].chain_links[0]
            self.bonds.append(Bonds.Bond((link1, link2)))
        if circular:
            link1 = self.groups[-1].chain_links[1]
            link2 = self.groups[0].chain_links[0]
            self.bonds.append(Bonds.Bond((link1, link2)))
        self.bonds = Bonds.BondList(self.bonds)
        self.parent = None
        self.type = None
        self.configurations = {}
        try:
            self.name = properties['name']
            del properties['name']
        except KeyError:
            self.name = ''
        if conf:
            conf.applyTo(self)
        if properties.has_key('position'):
            self.translateTo(properties['position'])
            del properties['position']
        self.addProperties(properties)

    def __len__(self):
        return len(self.groups)

    def __getitem__(self, item):
        return self.groups[item]

    def __setitem__(self, item, value):
        self.replaceResidue(self.groups[item], value)

    def residuesOfType(self, *types):
        """Returns a collection that contains all residues whose type
        (residue code) is contained in |types|."""
        types = map(string.lower, types)
        rlist = []
        for r in self.groups:
            if string.lower(r.type.symbol) in types:
                rlist.append(r)
        return Collections.Collection(rlist)

    def residues(self):
        "Returns a collection containing all residues."
        return Collections.Collection(self.groups)

    def sequence(self):
        "Returns the sequence as a list of residue code."
        return map(lambda r: string.lower(r.type.symbol), self.groups)

#
# Find the full name of a residue
#
def _fullName(residue):
    return _residue_names[string.lower(residue)]

_residue_names = {'ala': 'alanine',          'a': 'alanine',
                  'arg': 'arginine',         'r': 'arginine',
                  'asn': 'asparagine',       'n': 'asparagine',
                  'asp': 'aspartic_acid',    'd': 'aspartic_acid',
                  'cys': 'cysteine',         'c': 'cysteine',
                  'gln': 'glutamine',        'q': 'glutamine',
                  'glu': 'glutamic_acid',    'e': 'glutamic_acid',
                  'gly': 'glycine',          'g': 'glycine',
                  'his': 'histidine',        'h': 'histidine',
                  'ile': 'isoleucine',       'i': 'isoleucine',
                  'leu': 'leucine',          'l': 'leucine',
                  'lys': 'lysine',           'k': 'lysine',
                  'met': 'methionine',       'm': 'methionine',
                  'phe': 'phenylalanine',    'f': 'phenylalanine',
                  'pro': 'proline',          'p': 'proline',
                  'ser': 'serine',           's': 'serine',
                  'thr': 'threonine',        't': 'threonine',
                  'trp': 'tryptophan',       'w': 'tryptophan',
                  'tyr': 'tyrosine',         'y': 'tyrosine',
                  'val': 'valine',           'v': 'valine',
                  'cyx': 'cystine_ss',
                  'cym': 'cysteine_with_negative_charge',
                  'app': 'aspartic_acid_neutral',
                  'glp': 'glutamic_acid_neutral',
                  'hsd': 'histidine_deltah', 'hse': 'histidine_epsilonh',
                  'hsp': 'histidine_plus',
                  'hid': 'histidine_deltah', 'hie': 'histidine_epsilonh',
                  'hip': 'histidine_plus',
                  'lyp': 'lysine_neutral',
                  'ace': 'ace_beginning',    'nme': 'nmethyl',
                  'nhe': 'amide',

                  'da': 'd-adenosine',
                  'da5': 'd-adenosine_5ter',
                  'da3': 'd-adenosine_3ter',
                  'dan': 'd-adenosine_5ter_3ter',
                  'dc': 'd-cytosine',
                  'dc5': 'd-cytosine_5ter',
                  'dc3': 'd-cytosine_3ter',
                  'dcn': 'd-cytosine_5ter_3ter',
                  'dg': 'd-guanosine',
                  'dg5': 'd-guanosine_5ter',
                  'dg3': 'd-guanosine_3ter',
                  'dgn': 'd-guanosine_5ter_3ter',
                  'dt': 'd-thymine',
                  'dt5': 'd-thymine_5ter',
                  'dt3': 'd-thymine_3ter',
                  'dtn': 'd-thymine_5ter_3ter',
                  'ra': 'r-adenosine',
                  'ra5': 'r-adenosine_5ter',
                  'ra3': 'r-adenosine_3ter',
                  'ran': 'r-adenosine_5ter_3ter',
                  'rc': 'r-cytosine',
                  'rc5': 'r-cytosine_5ter',
                  'rc3': 'r-cytosine_3ter',
                  'rcn': 'r-cytosine_5ter_3ter',
                  'rg': 'r-guanosine',
                  'rg5': 'r-guanosine_5ter',
                  'rg3': 'r-guanosine_3ter',
                  'rgn': 'r-guanosine_5ter_3ter',
                  'ru': 'r-uracil',
                  'ru5': 'r-uracil_5ter',
                  'ru3': 'r-uracil_3ter',
                  'run': 'r-uracil_5ter_3ter',
                  }

#
# Add a residue to the residue list
#
def defineAminoAcidResidue(full_name, code3, code1 = None):
    """Adds a non-standard amino acid residue to the residue table.
    The definition of the residue must be accesible by |full_name|
    in the chemical database. The three-letter code is specified
    by |code3|, and an optional one-letter code can be specified by
    |code1|.

    Once added to the residue table, the new residue can be used
    like any of the standard residues in the creation of peptide chains.
    """
    code3 = string.lower(code3)
    if code1 is not None:
        code1 = string.lower(code1)
    if _residue_names.has_key(code3):
        raise ValueError("residue name " + code3 + " already used")
    if _residue_names.has_key(code1):
        raise ValueError("residue name " + code1 + " already used")
    _residue_names[code3] = full_name
    if code1 is not None:
        _residue_names[code1] = full_name
    import Scientific.IO.PDB
    Scientific.IO.PDB.defineAminoAcidResidue(code3)

def defineNucleicAcidResidue(full_name, code):
    """Adds a non-standard nucleic acid residue to the residue table.
    The definition of the residue must be accesible by |full_name|
    in the chemical database. The residue code is specified
    by |code|.

    Once added to the residue table, the new residue can be used
    like any of the standard residues in the creation of nucleotide
    chains.
    """
    if _residue_names.has_key(code):
        raise ValueError("residue name " + code + " already used")
    _residue_names[code] = full_name
    import Scientific.IO.PDB
    Scientific.IO.PDB.defineNucleicAcidResidue(code)
