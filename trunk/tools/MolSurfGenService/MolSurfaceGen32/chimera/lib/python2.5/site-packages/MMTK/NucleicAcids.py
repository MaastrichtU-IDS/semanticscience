# This module implements classes for nucleotide chains.
#
# Written by Konrad Hinsen
# last revision: 2006-8-18
#

import Biopolymers, Bonds, ChemicalObjects, Collections, ConfigIO, Database
import Universe, Utility
from Scientific.Geometry import Vector
import operator, string

from Biopolymers import defineNucleicAcidResidue

#
# Nucleotides are special groups
#
class Nucleotide(Biopolymers.Residue):

    """Nucleic acid residue

    A subclass of Class:MMTK.ChemicalObjects.Group.

    Nucleotides are a special kind of group. Like any other
    group, they are defined in the chemical database. Each residue
    has two or three subgroups ('sugar' and 'base', plus 'phosphate'
    except for 5'-terminal residues) and is usually
    connected to other residues to form a nucleotide chain. The database
    contains three variants of each residue (5'-terminal, 3'-terminal,
    non-terminal).

    Constructor: Nucleotide(|kind|, |model|="all")

    Arguments:

    |kind| -- the name of the nucleotide in the chemical database. This
              is the full name of the residue plus the suffix
              "_5ter" or "_3ter" for the terminal variants.

    |model| -- one of "all" (all-atom), "none" (no hydrogens),
               "polar" (united-atom with only polar hydrogens),
               "polar_charmm" (like "polar", but defining
               polar hydrogens like in the CHARMM force field).
               Currently the database has definitions only for "all".
    """

    def __init__(self, name = None, model = 'all'):
	if name is not None:
	    blueprint = _residueBlueprint(name, model)
	    ChemicalObjects.Group.__init__(self, blueprint)
	    self.model = model
	    self._init()

    def backbone(self):
        "Returns the sugar and phosphate groups."
        bb = self.sugar
        if hasattr(self, 'phosphate'):
            bb = Collections.Collection([bb, self.phosphate])
        return bb

    def bases(self):
        "Returns the base group."
        return self.base


def _residueBlueprint(name, model):
    try:
	blueprint = _residue_blueprints[(name, model)]
    except KeyError:
	if model == 'polar':
	    name = name + '_uni'
	elif model == 'polar_charmm':
	    name = name + '_uni2'
	elif model == 'none':
	    name = name + '_noh'
	blueprint = Database.BlueprintGroup(name)
	_residue_blueprints[(name, model)] = blueprint
    return blueprint

_residue_blueprints = {}

#
# Nucleotide chains are molecules with added features.
#
class NucleotideChain(Biopolymers.ResidueChain):

    """Nucleotide chain

    A Glossary:Subclass of Class:MMTK.Biopolymers.ResidueChain.

    Nucleotide chains consist of nucleotides that are linked together.
    They are a special kind of molecule, i.e. all molecule operations
    are available.

    Constructor: NucleotideChain(|sequence|, **|properties|)

    Arguments:

    |sequence| -- the nucleotide sequence. This can be a list
                  of two-letter codes (a "d" or "r" for the type of
                  sugar, and the one-letter base code), or a
                  PDBNucleotideChain object.
                  If a PDBNucleotideChain object is supplied, the atomic
                  positions it contains are assigned to the atoms
                  of the newly generated nucleotide chain, otherwise the
                  positions of all atoms are undefined.

    |properties| -- optional keyword properties:

    - model: one of "all" (all-atom), "no_hydrogens" or "none" (no hydrogens),
             "polar_hydrogens" or "polar" (united-atom with only polar
             hydrogens), "polar_charmm" (like "polar", but defining
             polar hydrogens like in the CHARMM force field). Default
             is "all". Currently the database contains definitions only
             for "all".

    - terminus_5: 1 if the first nucleotide should be constructed using the
                  5'-terminal variant, 0 if the non-terminal version should
                  be used. Default is 1.

    - terminus_3: 1 if the last residue should be constructed using the
                  3'-terminal variant, 0 if the non-terminal version should
                  be used. Default is 1.

    - circular: 1 if a bond should be constructed between the first
                and the last residue. Default is 0.

    - name: a name for the chain (a string)


    Nucleotide chains act as sequences of residues. If 'n' is a NucleotideChain
    object, then

    - 'len(n)' yields the number of nucleotides

    - 'n[i]' yields nucleotide number 'i' (counting from zero)

    - 'n[i:j]' yields the subchain from nucleotide number 'i' up to but
               excluding nucleotide number 'j'
    """

    def __init__(self, sequence, **properties):
	if sequence is not None:
	    hydrogens = self.binaryProperty(properties, 'hydrogens', 'all')
	    if hydrogens == 1:
		hydrogens = 'all'
	    elif hydrogens == 0:
		hydrogens = 'none'
	    term5 = self.binaryProperty(properties, 'terminus_5', 1)
	    term3 = self.binaryProperty(properties, 'terminus_3', 1)
	    circular = self.binaryProperty(properties, 'circular', 0)
	    try:
		model = string.lower(properties['model'])
	    except KeyError:
		model = hydrogens
	    self.version_spec = {'hydrogens': hydrogens,
				 'terminus_5': term5,
				 'terminus_3': term3,
				 'model': model,
                                 'circular': circular}
	    if type(sequence[0]) == type(''):
		conf = None
	    else:
		conf = sequence
		sequence = map(lambda r: r.name, sequence)
	    sequence = map(Biopolymers._fullName, sequence)
            if term5:
                if string.find(sequence[0], '5ter') == -1:
                    sequence[0] = sequence[0] + '_5ter'
            if term3:
                if string.find(sequence[-1], '3ter') == -1:
                    sequence[-1] = sequence[-1] + '_3ter'

            self.groups = []
            n = 0
            for residue in sequence:
                n = n + 1
                r = Nucleotide(residue, model)
                r.name = r.symbol + '_' + `n`
                r.sequence_number = n
                r.parent = self
                self.groups.append(r)

            self._setupChain(circular, properties, conf)

    is_nucleotide_chain = 1

    def __getslice__(self, first, last):
	return NucleotideSubChain(self, self.groups[first:last])

    def backbone(self):
        """Returns a collection containing the sugar and phosphate groups
        of all nucleotides."""
        bb = Collections.Collection([])
        for residue in self.groups:
            try:
                bb.addObject(residue.phosphate)
            except AttributeError:
                pass
            bb.addObject(residue.sugar)
        return bb

    def bases(self):
        "Returns a collection containing the base groups of all nucleotides."
	return Collections.Collection(map(lambda r: r.base, self.groups))

    def _descriptionSpec(self):
	kwargs = ''
	for name, value in self.version_spec.items():
	    kwargs = kwargs + name + '=' + `value` + ','
	return "N", kwargs[:-1]

    def _typeName(self):
        ljust3 = lambda s, n=3: string.ljust(s, n)
        seq = map(ljust3, self.sequence())
	return reduce(operator.add, seq)

    def _graphics(self, conf, distance_fn, model, module, options):
	if model != 'backbone':
	    return ChemicalObjects.Molecule._graphics(self, conf,
						      distance_fn, model,
						      module, options)
	color = options.get('color', 'black')
	material = module.EmissiveMaterial(color)
	objects = []
	for i in range(1, len(self.groups)-1):
	    a1 = self.groups[i].phosphate.P
	    a2 = self.groups[i+1].phosphate.P
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
class NucleotideSubChain(NucleotideChain):

    """A contiguous part of a nucleotide chain

    NucleotideSubChain objects are the result of slicing operations on
    NucleotideChain objects. They cannot be created directly.
    NucleotideSubChain objects permit all operations of NucleotideChain
    objects, but cannot be added to a universe.
    """

    def __init__(self, chain, groups, name = ''):
	self.groups = groups
	self.atoms = []
	self.bonds = []
	for g in self.groups:
	    self.atoms = self.atoms + g.atoms
	    self.bonds = self.bonds + g.bonds
        for i in range(len(self.groups)-1):
            self.bonds.append(Bonds.Bond((self.groups[i].sugar.O_3,
                                          self.groups[i+1].phosphate.P)))
	self.bonds = Bonds.BondList(self.bonds)
	self.name = name
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


#
# Type check functions
#
def isNucleotideChain(x):
    "Returns 1 if |x| is a NucleotideChain."
    return hasattr(x, 'is_nucleotide_chain')
