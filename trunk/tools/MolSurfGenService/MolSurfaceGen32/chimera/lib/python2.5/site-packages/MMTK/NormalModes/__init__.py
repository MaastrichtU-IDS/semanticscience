# Normal modes package

from MMTK.NormalModes.EnergeticModes import EnergeticModes
from MMTK.NormalModes.VibrationalModes import VibrationalModes
from MMTK.NormalModes.BrownianModes import BrownianModes

# Backwards compatibility

NormalModes = VibrationalModes

class SubspaceNormalModes(VibrationalModes):
    def __init__(self, universe=None, basis=None, temperature=300.):
        VibrationalModes.__init__(self, universe, temperature, basis)

class FiniteDifferenceSubspaceNormalModes(VibrationalModes):
    def __init__(self, universe=None, basis=None, delta=0.0001,
                 temperature=300.):
        VibrationalModes.__init__(self, universe, temperature,
                                  basis, delta)
                                  
class SparseMatrixNormalModes(VibrationalModes):
    def __init__(self, universe=None, nmodes=None, temperature=300):
        VibrationalModes.__init__(self, universe, temperature, nmodes,
                                  None, True)

class SparseMatrixSubspaceNormalModes(VibrationalModes):
    def __init__(self, universe=None, basis=None, temperature=300.):
        VibrationalModes.__init__(self, universe, temperature, basis,
                                  None, True)

