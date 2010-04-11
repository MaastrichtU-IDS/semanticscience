# MMTK initialization
#
# Written by Konrad Hinsen
# last revision: 2007-4-23
#

"""MMTK is the base module of the Molecular Modelling Toolkit.
It contains the most common objects and all submodules. As a convenience
to the user, it also imports some commonly used objects from other
libraries:

- 'Vector' from 'Scientific.Geometry'
- 'Translation' and 'Rotation' from 'Scientific.Geometry.Transformation'
- 'copy' and 'deepcopy' from 'copy'
- 'stdin', 'stdout', and 'stderr' from 'sys'
"""

#
# Package information
#
from __pkginfo__ import __version__

#
# Add shared library path to sys.path
#
import os, sys
sys.path.append(os.path.join(os.path.split(__file__)[0], sys.platform))
del os
del sys


#
# General library modules, for convenience
#
from Scientific.Geometry import Vector
from Scientific.Geometry.Transformation import Translation, Rotation
from copy import copy, deepcopy
from sys import stdin, stdout, stderr

#
# MMTK core modules
#
from ThreadManager import activeThreads, waitForThreads
from Universe import InfiniteUniverse, OrthorhombicPeriodicUniverse, \
                     CubicPeriodicUniverse, ParallelepipedicPeriodicUniverse
from ParticleProperties import ParticleScalar, ParticleVector, \
                               ParticleTensor, SymmetricPairTensor, \
                               Configuration
from ChemicalObjects import Atom, Molecule, Complex, AtomCluster
from Collections import Collection, PartitionedCollection, \
                        PartitionedAtomCollection
from Utility import save, load
import Units

# Pretend that certain object are defined here for documentation purposes

import sys
if sys.modules.has_key('pythondoc'):

    InfiniteUniverse.__module__ = 'MMTK'
    OrthorhombicPeriodicUniverse.__module__ = 'MMTK'
    CubicPeriodicUniverse.__module__ = 'MMTK'
    ParticleScalar.__module__ = 'MMTK'
    ParticleVector.__module__ = 'MMTK'
    ParticleTensor.__module__ = 'MMTK'
    SymmetricPairTensor.__module__ = 'MMTK'
    Configuration.__module__ = 'MMTK'
    Atom.__module__ = 'MMTK'
    Molecule.__module__ = 'MMTK'
    Complex.__module__ = 'MMTK'
    AtomCluster.__module__ = 'MMTK'
    Collection.__module__ = 'MMTK'
    PartitionedCollection.__module__ = 'MMTK'
    PartitionedAtomCollection.__module__ = 'MMTK'
    Units.__module__ = 'MMTK'
    save.func_globals['__name__'] = 'MMTK'
    load.func_globals['__name__'] = 'MMTK'

del sys
save.func_globals['virtual_module'] = 'MMTK'
load.func_globals['virtual_module'] = 'MMTK'

##  import string
##  load.func_globals['__file__'] = string.replace(load.func_globals['__file__'],
##                                                 'Utility', '__init__')
##  save.func_globals['__file__'] = string.replace(load.func_globals['__file__'],
##                                                 'Utility', '__init__')
##  del string

# Execute user-defined initialization code

import os, sys
filename = os.path.expanduser('~/.mmtk/init.py')
if os.path.exists(filename):
    definitions = {}
    execfile(filename, globals(), definitions)
    if definitions.has_key('export'):
        mod = sys.modules['MMTK']
        for name, value in definitions['export'].items():
            setattr(mod, name, value)
del filename
del os
del sys
