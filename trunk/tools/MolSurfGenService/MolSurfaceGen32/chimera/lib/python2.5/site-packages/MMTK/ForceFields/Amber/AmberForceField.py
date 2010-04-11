# This file provides the Amber force field, using Amber parameter files.
#
# Written by Konrad Hinsen
# last revision: 2007-6-10
#

_undocumented = 1

from MMTK.ForceFields import MMForceField
import AmberData
import os

#
# Read parameter files
#
Amber99 = None
Amber94 = None
Amber91 = None
OPLS = None

this_directory = os.path.split(__file__)[0]

def fullModFilePath(modfile):
    if not isinstance(modfile, str):
        return modfile
    if os.path.exists(modfile):
        return modfile
    return os.path.join(this_directory, os.path.basename(modfile))

def readAmber94(main_file = None, mod_files = None):
    global Amber94
    if main_file is None and mod_files is None:
        if Amber94 is None:
            paramfile = os.path.join(this_directory, "amber_parm94")
            modfile = os.path.join(this_directory, "amber_parm94.heme")
            Amber94 = AmberData.AmberParameters(paramfile, [(modfile, 'MOD4')])
            Amber94.lennard_jones_1_4 = 0.5
            Amber94.electrostatic_1_4 = 1./1.2
            Amber94.default_ljpar_set = Amber94.ljpar_sets['MOD4']
            Amber94.atom_type_property = 'amber_atom_type'
            Amber94.charge_property = 'amber_charge'
        return Amber94
    else:
        if main_file is None:
            main_file = os.path.join(this_directory, "amber_parm94")
        mod_files = map(lambda mf: (fullModFilePath(mf), 'MOD4'), mod_files)
        params = AmberData.AmberParameters(main_file, mod_files)
        params.lennard_jones_1_4 = 0.5
        params.electrostatic_1_4 = 1./1.2
        params.default_ljpar_set = params.ljpar_sets['MOD4']
        params.atom_type_property = 'amber_atom_type'
        params.charge_property = 'amber_charge'
        return params

def readAmber99(main_file = None, mod_files = None):
    global Amber99
    if main_file is None and mod_files is None:
        if Amber99 is None:
            paramfile = os.path.join(this_directory, "amber_parm99")
            Amber99 = AmberData.AmberParameters(paramfile)
            Amber99.lennard_jones_1_4 = 0.5
            Amber99.electrostatic_1_4 = 1./1.2
            Amber99.default_ljpar_set = Amber99.ljpar_sets['MOD4']
            Amber99.atom_type_property = 'amber_atom_type'
            Amber99.charge_property = 'amber_charge'
        return Amber99
    else:
        if main_file is None:
            main_file = os.path.join(this_directory, "amber_parm99")
        mod_files = map(lambda mf: (fullModFilePath(mf), 'MOD4'), mod_files)
        params = AmberData.AmberParameters(main_file, mod_files)
        params.lennard_jones_1_4 = 0.5
        params.electrostatic_1_4 = 1./1.2
        params.default_ljpar_set = params.ljpar_sets['MOD4']
        params.atom_type_property = 'amber_atom_type'
        params.charge_property = 'amber_charge'
        return params


def readAmber91():
    global Amber91
    if Amber91 is None:
        Amber91 = AmberData.AmberParameters(os.path.join(this_directory,
                                                         "amber_parm91"))
        Amber91.lennard_jones_1_4 = 0.5
        Amber91.electrostatic_1_4 = 0.5
        Amber91.default_ljpar_set = Amber91.ljpar_sets['STDA']
        Amber91.atom_type_property = 'amber91_atom_type'
        Amber91.charge_property = 'amber91_charge'

def readOPLS(main_file = None, mod_files = None):
    global OPLS
    if main_file is None and mod_files is None:
        if OPLS is None:
            paramfile = os.path.join(this_directory, "opls_parm")
            OPLS = AmberData.AmberParameters(paramfile)
            OPLS.lennard_jones_1_4 = 0.125
            OPLS.electrostatic_1_4 = 0.5
            OPLS.default_ljpar_set = OPLS.ljpar_sets['OPLS']
            OPLS.atom_type_property = 'opls_atom_type'
            OPLS.charge_property = 'opls_charge'
        return OPLS
    else:
        if main_file is None:
            main_file = os.path.join(this_directory, "opls_parm")
        mod_files = map(lambda mf: (fullModFilePath(mf), 'OPLS'), mod_files)
        params = AmberData.AmberParameters(main_file, mod_files)
        params.lennard_jones_1_4 = 0.125
        params.electrostatic_1_4 = 0.5
        params.default_ljpar_set = params.ljpar_sets['OPLS']
        params.atom_type_property = 'opls_atom_type'
        params.charge_property = 'opls_charge'
        return params

#
# The total force field
#
class Amber94ForceField(MMForceField.MMForceField):

    """Amber 94 force field

    Constructor: Amber94ForceField(|lennard_jones_options|,
                                   |electrostatic_options|,
                                   |mod_files| = [])

    Arguments:

    |lennard_jones_options| -- parameters for Lennard-Jones interactions;
                               one of:

      * a number, specifying the cutoff
      * 'None', meaning the default method (no cutoff; inclusion of all
        pairs, using the minimum-image conventions for periodic universes)
      * a dictionary with an entry "method" which specifies the
        calculation method as either "direct" (all pair terms)
        or "cutoff", with the cutoff specified by the dictionary
        entry "cutoff".

    |electrostatic_options| -- parameters for electrostatic interactions;
                               one of:

      * a number, specifying the cutoff
      * 'None', meaning the default method (all pairs without cutoff for
        non-periodic system, Ewald summation for periodic systems)
      * a dictionary with an entry "method" which specifies the
        calculation method as either "direct" (all pair terms),
        "cutoff" (with the cutoff specified by the dictionary
        entry "cutoff"), "ewald" (Ewald summation, only for periodic
        universes), "screened" (see below),
        or "multipole" (fast-multipole method).

    |mod_files| -- a list of parameter modification files. The file
                   format is the one defined by AMBER. Each item
                   in the list can be either a file object
                   or a filename, filenames are looked up
                   first relative to the current directory and then
                   relative to the directory containing MMTK's
                   AMBER parameter files.

    Pair interactions in periodic systems are calculated using the
    minimum-image convention; the cutoff should therefore never be
    larger than half the smallest edge length of the elementary
    cell.

    For Lennard-Jones interactions, all terms for pairs whose distance
    exceeds the cutoff are set to zero, without any form of correction.
    For electrostatic interactions, a charge-neutralizing surface charge
    density is added around the cutoff sphere in order to reduce
    cutoff effects [Article:Wolf1999].

    For Ewald summation, there are some additional parameters that can
    be specified by dictionary entries:

    - "beta" specifies the Ewald screening parameter
    - "real_cutoff" specifies the cutoff for the real-space sum.
      It should be significantly larger than 1/beta to ensure that
      the neglected terms are small.
    - "reciprocal_cutoff" specifies the cutoff for the reciprocal-space sum.
      Note that, like the real-space cutoff, this is a distance; it describes
      the smallest wavelength of plane waves to take into account.
      Consequently, a smaller value means a more precise (and more expensive)
      calculation.

    MMTK provides default values for these parameter which are calculated
    as a function of the system size. However, these parameters are
    exaggerated in most cases of practical interest and can lead to excessive
    calculation times for large systems. It is preferable to determine
    suitable values empirically for the specific system to be simulated.

    The method "screened" uses the real-space part of the Ewald sum
    with a charge-neutralizing surface charge density around the
    cutoff sphere, and no reciprocal sum [Article:Wolf1999]. It requires
    the specification of the dictionary entries "cutoff" and "beta".

    The fast-multipole method uses the DPMTA library [Article:DPMTA].
    Note that this method provides only energy and forces, but no
    second-derivative matrix. There are several optional dictionary
    entries for this method, all of which are set to reasonable default
    values. The entries are "spatial_decomposition_levels",
    "multipole_expansion_terms", "use_fft", "fft_blocking_factor",
    "macroscopic_expansion_terms", and "multipole_acceptance".
    For an explanation of these options, refer to the
    DPMTA manual [Article:DPMTA].
    """

    def __init__(self, lj_options = None, es_options = None,
                 bonded_scale_factor = 1., **kwargs):
        main_file = kwargs.get('parameter_file', None)
        mod_files = kwargs.get('mod_files', None)
        parameters = readAmber94(main_file, mod_files)
        MMForceField.MMForceField.__init__(self, 'Amber94', parameters,
                                           lj_options, es_options,
                                           bonded_scale_factor)
        self.arguments = (lj_options, es_options, bonded_scale_factor)

AmberForceField = Amber94ForceField


class Amber99ForceField(MMForceField.MMForceField):

    """Amber 99 force field

    Constructor: Amber99ForceField(|lennard_jones_options|,
                                   |electrostatic_options|,
                                   |mod_files| = [])

    Arguments:

    |lennard_jones_options| -- parameters for Lennard-Jones interactions;
                               one of:

      * a number, specifying the cutoff
      * 'None', meaning the default method (no cutoff; inclusion of all
        pairs, using the minimum-image conventions for periodic universes)
      * a dictionary with an entry "method" which specifies the
        calculation method as either "direct" (all pair terms)
        or "cutoff", with the cutoff specified by the dictionary
        entry "cutoff".

    |electrostatic_options| -- parameters for electrostatic interactions;
                               one of:

      * a number, specifying the cutoff
      * 'None', meaning the default method (all pairs without cutoff for
        non-periodic system, Ewald summation for periodic systems)
      * a dictionary with an entry "method" which specifies the
        calculation method as either "direct" (all pair terms),
        "cutoff" (with the cutoff specified by the dictionary
        entry "cutoff"), "ewald" (Ewald summation, only for periodic
        universes), "screened" (see below),
        or "multipole" (fast-multipole method).

    |mod_files| -- a list of parameter modification files. The file
                   format is the one defined by AMBER. Each item
                   in the list can be either a file object
                   or a filename, filenames are looked up
                   first relative to the current directory and then
                   relative to the directory containing MMTK's
                   AMBER parameter files.

    Pair interactions in periodic systems are calculated using the
    minimum-image convention; the cutoff should therefore never be
    larger than half the smallest edge length of the elementary
    cell.

    For Lennard-Jones interactions, all terms for pairs whose distance
    exceeds the cutoff are set to zero, without any form of correction.
    For electrostatic interactions, a charge-neutralizing surface charge
    density is added around the cutoff sphere in order to reduce
    cutoff effects [Article:Wolf1999].

    For Ewald summation, there are some additional parameters that can
    be specified by dictionary entries:

    - "beta" specifies the Ewald screening parameter
    - "real_cutoff" specifies the cutoff for the real-space sum.
      It should be significantly larger than 1/beta to ensure that
      the neglected terms are small.
    - "reciprocal_cutoff" specifies the cutoff for the reciprocal-space sum.
      Note that, like the real-space cutoff, this is a distance; it describes
      the smallest wavelength of plane waves to take into account.
      Consequently, a smaller value means a more precise (and more expensive)
      calculation.

    MMTK provides default values for these parameter which are calculated
    as a function of the system size. However, these parameters are
    exaggerated in most cases of practical interest and can lead to excessive
    calculation times for large systems. It is preferable to determine
    suitable values empirically for the specific system to be simulated.

    The method "screened" uses the real-space part of the Ewald sum
    with a charge-neutralizing surface charge density around the
    cutoff sphere, and no reciprocal sum [Article:Wolf1999]. It requires
    the specification of the dictionary entries "cutoff" and "beta".

    The fast-multipole method uses the DPMTA library [Article:DPMTA].
    Note that this method provides only energy and forces, but no
    second-derivative matrix. There are several optional dictionary
    entries for this method, all of which are set to reasonable default
    values. The entries are "spatial_decomposition_levels",
    "multipole_expansion_terms", "use_fft", "fft_blocking_factor",
    "macroscopic_expansion_terms", and "multipole_acceptance".
    For an explanation of these options, refer to the
    DPMTA manual [Article:DPMTA].
    """

    def __init__(self, lj_options = None, es_options = None,
                 bonded_scale_factor = 1., **kwargs):
        main_file = kwargs.get('parameter_file', None)
        mod_files = kwargs.get('mod_files', None)
        parameters = readAmber99(main_file, mod_files)
        MMForceField.MMForceField.__init__(self, 'Amber99', parameters,
                                           lj_options, es_options,
                                           bonded_scale_factor)
        self.arguments = (lj_options, es_options, bonded_scale_factor)


class Amber91ForceField(MMForceField.MMForceField):

    def __init__(self, lj_options = None, es_options = None,
                 bonded_scale_factor=1., **kwargs):
        readAmber91()
        MMForceField.MMForceField.__init__(self, 'Amber91', Amber91,
                                           lj_options, es_options,
                                           bonded_scale_factor)
        self.arguments = (lj_options, es_options, bonded_scale_factor)

class OPLSForceField(MMForceField.MMForceField):

    def __init__(self, lj_options = None, es_options = None,
                 bonded_scale_factor = 1., **kwargs):
        main_file = kwargs.get('parameter_file', None)
        mod_files = kwargs.get('mod_files', None)
        parameters = readOPLS(main_file, mod_files)
        MMForceField.MMForceField.__init__(self, 'OPLS', parameters,
                                           lj_options, es_options,
                                           bonded_scale_factor)
        self.arguments = (lj_options, es_options, bonded_scale_factor)

#
# The following classes provides access to individual terms of the
# Amber force field. They are not used normally, but can be useful
# for testing.
#

#
# Bonded interactions
#
class AmberBondedForceField(MMForceField.MMBondedForceField):

    def __init__(self):
        readAmber94()
        MMForceField.MMBondedForceField.__init__(self, 'Amber_bonded', Amber94)
        self.arguments = ()

#
# Nonbonded interactions
#
class AmberLJForceField(MMForceField.MMLJForceField):

    def __init__(self, cutoff = None):
        readAmber94()
        MMForceField.MMLJForceField.__init__(self, 'Amber_LJ', Amber94, cutoff)
        self.arguments = (cutoff,)

class AmberESForceField(MMForceField.MMESForceField):

    def __init__(self, cutoff = None):
        readAmber94()
        MMForceField.MMESForceField.__init__(self, 'Amber_ES', Amber94, cutoff)
        self.arguments = (cutoff,)

class AmberEwaldESForceField(MMForceField.MMEwaldESForceField):

    def __init__(self, options = {}):
        readAmber94()
        MMForceField.MMEwaldForceESField.__init__(self, 'Amber_ES',
                                                  Amber94, options)
        self.arguments = (options,)

class AmberMPESForceField(MMForceField.MMMPESForceField):

    def __init__(self, options = {}):
        readAmber94()
        MMForceField.MMMPESForceField.__init__(self, 'Amber_ES',
                                               Amber94, options)
        self.arguments = (options,)

class AmberNonbondedForceField(MMForceField.MMNonbondedForceField):

    def __init__(self, lj_options = None, es_options = None):
        readAmber94()
        MMForceField.MMNonbondedForceField.__init__(self, 'Amber_NB', Amber94,
                                                    lj_options, es_options)
        self.arguments = (lj_options, es_options)
