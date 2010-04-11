# This module provides the basic mechanism for Molecular-Mechanics-type
# force fields that use the standard terms (bonds, angles, dihedrals,
# Lennard-Jones, electrostatic). An implementation of a specific force
# field (e.g. Amber94) only needs to provide access to its parameters.
#
# The implementation is based on the following assumptions about the
# force field:
#
# - Each atom has an atom type, taken from the database, which determines
#   bonded and Lennard-Jones interactions. The specific force field has
#   to provide the mapping from types to force field parameters.
# - Each atom has a partial charge, taken from the database, which
#   is used for the electrostatic term.
#
# Each specific force field must supply a paramater set object to
# the generic force field classes defined here. This object provides
# method that return the parameters for each force field term.
#
# The only concrete force field that has been implemented is Amber 94;
# implementing other MM force fields will probably require minor
# modifications to this module.
#
# Written by Konrad Hinsen
# last revision: 2006-11-17
#

_undocumented = 1

from BondedInteractions import BondedForceField
from NonBondedInteractions import NonBondedForceField, LJForceField, \
                                  ElectrostaticForceField, \
                                  ESMPForceField, ESEwaldForceField
from ForceField import ForceField, CompoundForceField, ForceFieldData
from MMTK import ParticleProperties
from Scientific.Geometry import Vector
import copy

#
# Mix-in class that ensures availability of atom parameters.
#
class MMAtomParameters:

    def collectAtomTypesAndIndices(self, universe, global_data):
        if not hasattr(global_data, 'atom_type'):
            type = {}
            for o in universe:
                for a in o.atomList():
                    type[a] = o.getAtomProperty(a, self.dataset
                                                           .atom_type_property)
            global_data.atom_type = type

    def collectCharges(self, universe, global_data):
        if not hasattr(global_data, 'charge'):
            charge = {}
            for o in universe:
                for a in o.atomList():
                    charge[a] = o.getAtomProperty(a, self.dataset
                                                              .charge_property)
            global_data.charge = charge

    def _atomType(self, object, atom, global_data):
        return global_data.atom_type[atom]

    def _charge(self, object, atom, global_data):
        return global_data.charge[atom]

    def _ljParameters(self, type, global_data):
        return self.dataset.ljParameters(type)


#
# Bonded interactions
#
class MMBondedForceField(MMAtomParameters, BondedForceField):

    def __init__(self, name, parameters, scale_factor=1.):
        self.dataset = parameters
        self.scale_factor = scale_factor
        BondedForceField.__init__(self, name)

    def evaluatorParameters(self, universe, subset1, subset2, global_data):
        self.collectAtomTypesAndIndices(universe, global_data)
        return BondedForceField.evaluatorParameters(self, universe,
                                                    subset1, subset2,
                                                    global_data)

    def addBondTerm(self, data, bond, object, global_data):
        a1 = bond.a1
        a2 = bond.a2
        i1 = a1.index
        i2 = a2.index
        global_data.add('excluded_pairs', (i1, i2))
        t1 = global_data.atom_type[a1]
        t2 = global_data.atom_type[a2]
        try:
            p = self.dataset.bondParameters(t1, t2)
        except KeyError:
            raise KeyError(('No parameters for bond %s (atom type %s)' +
                            ' - %s (atom type %s)') % (str(a1), t1,
                                                       str(a2), t2))
        if p is not None and p[1] != 0.:
            data.add('bonds', (i1, i2, p[0], p[1]*self.scale_factor))

    def addBondAngleTerm(self, data, angle, object, global_data):
        a1 = angle.a1
        a2 = angle.a2
        ca = angle.ca
        i1 = a1.index
        i2 = a2.index
        ic = ca.index
        global_data.add('excluded_pairs', (i1, i2))
        t1 = global_data.atom_type[a1]
        t2 = global_data.atom_type[a2]
        tc = global_data.atom_type[ca]
        try:
            p = self.dataset.bondAngleParameters(t1, tc, t2)
        except KeyError:
            raise KeyError(('No parameters for angle %s (atom type %s)' +
                            ' - %s (atom type %s) - %s (atom type %s)')
                           % (str(a1), t1, str(ca), tc, str(a2), t2))
        if p is not None and p[1] != 0.:
            data.add('angles', (i1, ic, i2, p[0], p[1]*self.scale_factor))

    def addDihedralTerm(self, data, dihedral, object, global_data):
        a1 = dihedral.a1
        a2 = dihedral.a2
        a3 = dihedral.a3
        a4 = dihedral.a4
        i1 = a1.index
        i2 = a2.index
        i3 = a3.index
        i4 = a4.index
        global_data.add('1_4_pairs', (i1, i4))
        t1 = global_data.atom_type[a1]
        t2 = global_data.atom_type[a2]
        t3 = global_data.atom_type[a3]
        t4 = global_data.atom_type[a4]
        terms = self.dataset.dihedralParameters(t1, t2, t3, t4)
        if terms is not None:
            for p in terms:
                if p[2] != 0.:
                    data.add('dihedrals', (i1, i2, i3, i4,
                                           p[0], p[1], p[2]*self.scale_factor))

    def addImproperTerm(self, data, improper, object, global_data):
        a1 = improper.a1
        a2 = improper.a2
        a3 = improper.a3
        a4 = improper.a4
        i1 = a1.index
        i2 = a2.index
        i3 = a3.index
        i4 = a4.index
        t1 = global_data.atom_type[a1]
        t2 = global_data.atom_type[a2]
        t3 = global_data.atom_type[a3]
        t4 = global_data.atom_type[a4]
        terms = self.dataset.improperParameters(t1, t2, t3, t4)
        if terms is not None:
            atoms = [(t2,i2), (t3,i3), (t4,i4)]
            atoms.sort(_order)
            i2, i3, i4 = tuple(map(lambda t: t[1], atoms))
            for p in terms:
                if p[2] != 0.:
                    data.add('dihedrals', (i1, i2, i3, i4,
                                           p[0], p[1], p[2]*self.scale_factor))

    def bondLengthDatabase(self, universe):
        return MMBondLengthDatabase(self, universe, self.dataset)

    def bonds(self, global_data):
        return self.data.get('bonds')
    def angles(self, global_data):
        return self.data.get('angles')
    def dihedrals(self, global_data):
        return self.data.get('dihedrals')

def _order(a1, a2):
    ret = cmp(a1[0], a2[0])
    if ret == 0:
        ret = cmp(a1[1], a2[1])
    return ret


#
# Nonbonded interactions
#
class MMLJForceField(MMAtomParameters, LJForceField):

    def __init__(self, name, parameters, cutoff, scale_factor=1.):
        self.dataset = parameters
        LJForceField.__init__(self, name, cutoff, scale_factor)
        self.lj_14_factor = self.dataset.lennard_jones_1_4


class MMESForceField(MMAtomParameters, ElectrostaticForceField):

    def __init__(self, name, parameters, cutoff, scale_factor=1.):
        self.dataset = parameters
        ElectrostaticForceField.__init__(self, name, cutoff, scale_factor)
        self.es_14_factor = self.dataset.electrostatic_1_4


class MMEwaldESForceField(MMAtomParameters, ESEwaldForceField):

    def __init__(self, name, parameters, options):
        self.dataset = parameters
        ESEwaldForceField.__init__(self, name, options)
        self.es_14_factor = self.dataset.electrostatic_1_4

    
class MMMPESForceField(MMAtomParameters, ESMPForceField):

    def __init__(self, name, parameters, options):
        self.dataset = parameters
        ESMPForceField.__init__(self, name, options)
        self.es_14_factor = self.dataset.electrostatic_1_4


class MMNonbondedForceField(MMAtomParameters, NonBondedForceField):

    def __init__(self, name, parameters, lj_options, es_options):
        self.name = name
        self.dataset = parameters

        if lj_options is None:
            self.lj_options = {}
        elif type(lj_options) != type({}):
            self.lj_options = {'method': 'cutoff', 'cutoff': lj_options}
        else:
            self.lj_options = copy.copy(lj_options)

        if es_options is None:
            self.es_options = {}
        elif type(es_options) != type({}):
            self.es_options = {'method': 'cutoff', 'cutoff': es_options}
        else:
            self.es_options = copy.copy(es_options)
            
    def charge(self, atoms):
        total = 0.
        for a in atoms.atomList():
            charge = a.topLevelChemicalObject() \
                     .getAtomProperty(a, self.dataset.charge_property)
            total = total + charge
        return total

    def charges(self, universe):
        q = ParticleProperties.ParticleScalar(universe)
        for object in universe:
            for atom in object.atomList():
                q[atom] = object.getAtomProperty(atom,
                                                 self.dataset.charge_property)
        return q
        
    def dipole(self, atoms, reference = None):
        if reference is None:
            reference = atoms.centerOfMass()
        total = Vector(0., 0., 0.)
        for a in atoms.atomList():
            charge = a.topLevelChemicalObject() \
                     .getAtomProperty(a, self.dataset.charge_property)
            total = total + charge*a.position()-reference
        return total

    def _getLJForceField(self, universe):
        lj_method = self.lj_options.get('method', 'direct')
        lj_scale_factor = self.lj_options.get('scale_factor', 1.)
        if lj_method == 'direct':
            return MMLJForceField(self.name, self.dataset,
                                  None, lj_scale_factor)
        elif lj_method == 'cutoff':
            return MMLJForceField(self.name, self.dataset,
                                  self.lj_options['cutoff'], lj_scale_factor)
        else:
            raise ValueError("Unknown LJ method: " + lj_method)

    def _getESForceField(self, universe):
        if universe.is_periodic:
            es_method = 'ewald'
        else:
            es_method = 'direct'
        es_method = self.es_options.get('method', es_method)
        es_scale_factor = self.es_options.get('scale_factor', 1.)
        if es_method == 'ewald':
            return MMEwaldESForceField(self.name, self.dataset,
                                       self.es_options)
        elif es_method == 'screened':
            options = copy.copy(self.es_options)
            options['method'] = 'ewald'
            options['real_cutoff'] = options['cutoff']
            options['no_reciprocal_sum'] = 1
            del options['cutoff']
            return MMEwaldESForceField(self.name, self.dataset, options)
        elif es_method == 'multipole':
            return MMMPESForceField(self.name, self.dataset, self.es_options)
        elif es_method == 'direct':
            return MMESForceField(self.name, self.dataset, None,
                                  es_scale_factor)
        elif es_method == 'cutoff':
            return MMESForceField(self.name, self.dataset,
                                  self.es_options['cutoff'], es_scale_factor)
        else:
            raise ValueError("Unknown electrostatics method: " + es_method)

    def evaluatorParameters(self, universe, subset1, subset2, global_data):
        self.collectAtomTypesAndIndices(universe, global_data)
        self.collectCharges(universe, global_data)
        lj = self._getLJForceField(universe)
        es = self._getESForceField(universe)
        compound = CompoundForceField(lj, es)
        return compound.evaluatorParameters(universe, subset1, subset2,
                                            global_data)

    def evaluatorTerms(self, universe, subset1, subset2, global_data):
        self.collectAtomTypesAndIndices(universe, global_data)
        self.collectCharges(universe, global_data)
        lj = self._getLJForceField(universe)
        es = self._getESForceField(universe)
        compound = CompoundForceField(lj, es)
        return compound.evaluatorTerms(universe, subset1, subset2, global_data)

#
# The total force field
#
class MMForceField(MMAtomParameters, CompoundForceField):

    def __init__(self, name, parameters, lj_options, es_options,
                 bonded_scale_factor = 1.):
        self.dataset = parameters
        self.bonded = MMBondedForceField(name, parameters, bonded_scale_factor)
        self.nonbonded = MMNonbondedForceField(name, parameters,
                                               lj_options, es_options)
        apply(CompoundForceField.__init__, (self, self.bonded, self.nonbonded))

    is_compound_force_field = 0

    def evaluatorParameters(self, universe, subset1, subset2, global_data):
        self.collectAtomTypesAndIndices(universe, global_data)
        return CompoundForceField.evaluatorParameters(self, universe,
                                                      subset1, subset2,
                                                      global_data)

    def charge(self, atoms):
        return self.nonbonded.charge(atoms)

    def charges(self, universe):
        return self.nonbonded.charges(universe)

    def dipole(self, atoms, reference = None):
        return self.nonbonded.dipole(atoms, reference)

    def bondLengthDatabase(self, universe):
        return self.bonded.bondLengthDatabase(universe)

    description = ForceField.description

#
# The bond length database (used for constraining bond lengths)
#
class MMBondLengthDatabase:

    def __init__(self, ff, universe, parameter_set):
        self.data = ForceFieldData()
        ff.collectAtomTypesAndIndices(universe, self.data)
        self.parameters = parameter_set

    def bondLength(self, bond):
        a1 = bond.a1
        a2 = bond.a2
        t1 = self.data.atom_type[a1]
        t2 = self.data.atom_type[a2]
        try:
            return self.parameters.bondParameters(t1, t2)[0]
        except KeyError:
            return None

    def bondAngle(self, angle):
        a1 = angle.a1
        a2 = angle.a2
        ca = angle.ca
        t1 = self.data.atom_type[a1]
        t2 = self.data.atom_type[a2]
        tc = self.data.atom_type[ca]
        try:
            return self.parameters.bondAngleParameters(t1, tc, t2)[0]
        except KeyError:
            return None
