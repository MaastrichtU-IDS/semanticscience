# -*- coding: iso8859-1 -*-

# SPCE force field
#
# Written by Konrad Hinsen
# last revision: 2005-2-2
#

from MMTK.ForceFields import MMForceField

class SPCEParameters:

    atom_type_property = 'spce_atom_type'
    charge_property = 'spce_charge'
    lennard_jones_1_4 = 1.
    electrostatic_1_4 = 1.

    def ljParameters(self, type):
        if type == 'O':
            # TIP3: 0.6363936, 0.315075240657
            return (0.650169580819, 0.31655578902, 0)
        elif type == 'H':
            return (0., 0., 0)
        else:
            raise ValueError('Unknown atom type ' + type)

    # Bond and angle parameters from:
    # O. Telemann, B. Jönsson, S. Engström
    # Mol. Phys. 60(1), 193-203 (1987)
    def bondParameters(self, at1, at2):
        if at1 == 'O' or at2 == 'O':
            return (0.1, 463700.)
        else:
            return (0.163298086184, 0.)
    
    def bondAngleParameters(self, at1, at2, at3):
        if at2 == 'O':
            return (1.91061193216, 383.)
        else:
            return (0.615490360716, 0.)
    
    def dihedralParameters(self, at1, at2, at3, at4):
        return [(1, 0., 0.)]
    
    def improperParameters(self, at1, at2, at3, at4):
        return [(1, 0., 0.)]


class SPCEForceField(MMForceField.MMForceField):

    """Force field for water simulations with the SPC/E model

    Constructor: SPCEForceField(|lennard_jones_options|,
                                |electrostatic_options|)

    The meaning of the arguments is the same as for the class
    [Class:MMTK.ForceFields.Amber94ForceField]
    """

    def __init__(self, lj_options=None, es_options=None):
        self.arguments = (lj_options, es_options)
        MMForceField.MMForceField.__init__(self, 'SPCE', SPCEParameters(),
                                           lj_options, es_options)
