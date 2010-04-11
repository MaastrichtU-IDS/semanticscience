## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
from Numeric import *
import LinearAlgebra as linalg

_typeMap = {
    float: Float,
}

NumericArray = array
def array(data, dataType):
    return NumericArray(data, _typeMap[dataType])

NumericIdentity = identity
def identity(data, dataType):
    return NumericIdentity(data, _typeMap[dataType])
