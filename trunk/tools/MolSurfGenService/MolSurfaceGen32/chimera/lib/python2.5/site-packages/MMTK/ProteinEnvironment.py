# This module defines the environment in which protein definition files
# are executed.

_undocumented = 1

from Proteins import PeptideChain
from Collections import Collection
from PDB import PDBConfiguration
from Units import *
from Scientific.Geometry import Vector
from Scientific.Geometry.Transformation import Translation, Rotation
from copy import copy, deepcopy
