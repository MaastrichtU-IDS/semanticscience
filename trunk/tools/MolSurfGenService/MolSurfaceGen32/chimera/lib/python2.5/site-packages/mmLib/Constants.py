## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
import math

PI       = math.pi
PI2      = math.pi**2
PI3      = math.pi**3

RAD2DEG  = 180.0 / PI
DEG2RAD  = PI / 180.0
RAD2DEG2 = RAD2DEG**2
DEG2RAD2 = DEG2RAD**2

## converting between U (angstrom^2) temp factor values and B temp
## factor values
U2B = 8.0 * PI2
B2U = 1.0 / (8.0 * PI2)
