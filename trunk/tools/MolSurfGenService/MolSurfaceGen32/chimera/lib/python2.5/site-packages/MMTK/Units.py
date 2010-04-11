# Define unit conversion factors and physical constants
#
# Written by Konrad Hinsen
# last revision: 2007-9-11
#

"""This module defines constants and prefactors that convert between
MMTK's internal unit system and other units. There are also some
common physical constants.

SI Prefixes: ato, femto, pico, nano, micro, milli, centi, deci, deca,
hecto, kilo, mega, giga, tera, peta

Length units: m, cm, mm, nm, pm, fm, Ang, Bohr

Angle units: rad, deg

Volume units: l

Time units: s, ns, ps, fs

Frequency units: Hz, invcm (wavenumbers)

Mass units: amu, g, kg

Quantity-of-matter units: mol

Energy units:
J, kJ, cal, kcal, Hartree

Temperature units:
K

Pressure units:
Pa, bar, atm

Electrostatic units:
C, A, V, D, eV, e


Physical constants:
c (speed of light),
Nav (Avogadro number),
h = (Planck constant),
hbar = (Planck constant divided by 2*Pi),
k_B = (Boltzmann constant),
eps0 = (permittivity of vacuum),
me = (electron mass)
"""

from Scientific import N as Numeric

# Prefixes

ato   = 1.0e-18
femto = 1.0e-15
pico  = 1.0e-12
nano  = 1.0e-9
micro = 1.0e-6
milli = 1.0e-3
centi = 1.0e-2
deci  = 1.0e-1
deca  = 1.0e1
hecto = 1.0e2
kilo  = 1.0e3
mega  = 1.0e6
giga  = 1.0e9
tera  = 1.0e12
peta  = 1.0e15

# Angles
# internal unit: radian

rad = 1.
deg = (Numeric.pi/180.)*rad

# Length units
# internal unit: nm

m = 1./nano                 # Meter (SI)
cm = centi*m
mm = milli*m
nm = nano*m
pm = pico*m
fm = femto*m
Ang = 1.e-10*m              # Angstrom

# Volume units

l = (deci*m)**3             # liter

# Time units
# internal unit: ps

s = 1./pico                 # Second (SI)
ns = nano*s
ps = pico*s
fs = femto*s

# Speed of light

c = 299792458.*m/s

# Frequency units
# internal unit: THz (1./ps)

Hz = 1./s
invcm = c/cm

# Avogadro number

Nav = 6.0221367e23

# Mass units
# internal unit: amu (= g/mol)

amu = 1                     # Atomic mass unit
g = Nav*amu
kg = kilo*g                 # Kilogram (SI)

# Quantity of matter
# internal unit: number

mol = Nav

# Energy units
# internal unit: kJ/mol

J = mol/kilo                # Joule (SI)
kJ = kilo*J
cal = 4.184*J               # Thermochemical calorie
kcal = kilo*cal

# Force units
# internal unit: kJ/mol/nm

N = J/m
dyn = 1.e-5*N

# Electrostatic units
# internal unit: charge in e

e = 1.
C = 6.24150636309e18*e      # Coulomb (SI)
A = C/s                     # Ampere (SI)
D = 1.e-15*C/c              # Debye
V = J/C                     # Volt
eV = e*V                    # electron volt

# Temperature units
# internal unit: K

K = 1                       # Kelvin

# Pressure units
# internal unit: kJ/mol/nm**3

Pa = J/m**3                 # Pascal
MPa = mega*Pa
GPa = giga*Pa
bar = 1.e5*Pa               # bar
kbar = kilo*bar
atm = 101325*Pa             # atmosphere

# Constants

h = 6.626176e-34*J*s
hbar = h/(2.*Numeric.pi)
k_B = 1.3806513e-23*J/K
eps0 = 1./(4.e-7*Numeric.pi)*A**2*m/J/c**2

me = 0.51099906*mega*eV/c**2

electrostatic_energy = 1/(4.*Numeric.pi*eps0)

# CHARMM time unit
akma_time = Numeric.sqrt(Ang**2/(kcal/mol))

# "Atomic" units
Bohr = 4.*Numeric.pi*eps0*hbar**2/(me*e**2)
Hartree = hbar**2/(me*Bohr**2)

# Remove symbol "Numeric"
del Numeric
