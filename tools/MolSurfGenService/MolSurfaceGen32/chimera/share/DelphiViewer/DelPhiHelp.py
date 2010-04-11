# --- UCSF Chimera Copyright ---
# Copyright (c) 2000 Regents of the University of California.
# All rights reserved.  This software provided pursuant to a
# license agreement containing restrictions on its disclosure,
# duplication and use.  This notice must be embedded in or
# attached to all copies, including partial copies, of the
# software or any revisions or derivations thereof.
# --- UCSF Chimera Copyright ---

"""
File:		DelPhiHelp.py
Date:		06.16.2000
Description:	Contains global help dictionaries for the chimera DelPhi
		extension.

Imports:	(N/A)

Classes:	(N/A)

Globals:	- InputOptionsHelp
		- ParameterOptionsHelp
		- OutputOptionsHelp
"""

InputOptionsHelp = {
	'exe'	:
"""Specifies the DelPhi executable file""",
	'prm'	:
"""Specifies a file that contains all
necessary input, parameter and output data
for DelPhi.""",
	'siz'	:
"""Specifies a file that contains the 
atomic radii of all atoms in the selected
molecules.""",
	'crg'	:
"""Specifies a file that contains the
atomic charge of all atoms in the selected
molecules.""",
	'pdb'	:
"""Specifies a PDB file that contains the
molecule of interest."""
}

ParameterOptionsHelp = {
	'AC':
"""The program by default will
automatically calculate the number of
iterations needed to attain convergence.""",
	'BC':
"""Integer flag specifying the type of
boundary condition imposed on the edge
of the lattice allowed options: 
1== potential is zero. 
2== Approximated by the Debye-Huckel
    potential of the equivalent dipole
    to the molecular charge distribution, 
3== focussing, where a potential map
    from a previous calculation is read
    in on unit 18, and values for the
    potential at the lattice edge are
    interpolated from this map
4== Approximated by the sum of Debye-Huckel
    potentials of all the charges.""",
	'PF':
"""Percentage of the lattice that the
largest of the x,y or z linear dimensions
of the molecule will fill. This along with
grid resolution will determine the number
of grids needed for the solver. The
percentage fill of the lattice will
depend on the application.""",
	'CS':
"""When set to true, outputs a GRASP
viewable surface file in the name grasp.srf.""",
	'ID':
"""Dielectric constants for the molecule.""",
	'ED':
"""Dielectric constants for the surrounding solvent.""",
	'FC':
"""Normally set to false indicating a
linear cubical interpolation of charges to
grid points; set to true this turns on a
spherical charge distribution.""",
	'PX':
"""Logical flag for periodic boundary conditions
for the X edges of the lattice. Note that periodic
boundary conditions will override other boundary
conditions on edges to which they are applied.""",
	'PY':
"""Logical flag for periodic boundary conditions
for the Y edges of the lattice. Note that periodic
boundary conditions will override other boundary
conditions on edges to which they are applied.""",
	'PZ':
"""Logical flag for periodic boundary conditions
for the Z edges of the lattice. Note that periodic
boundary conditions will override other boundary
conditions on edges to which they are applied.""",
	'SP':
"""Normally DelPhi will invoke the
Poisson-Boltzman solver but if you are
interested in using DelPhi for other
things such as calculating surface area
or producing a GRASP viewable surface
file, you can turn off the solver
using this option.""",
	'SC':
"""Expressed in no. grids/Angstrom this indicates
the lattice spacing; this is used along with the
Box Fill parameter to determine the number of grids
in each dimension required to enclose the molecule.""",
	'GC':
"""When set to a fractional value, the iteration
continues till two successive 10 iterations result
in grid energies that are within GC.""",
	'IS':
"""Ionic strenght of solvent in moles/litre.""",
	'IR':
"""Thickness of the ion exclusion layer
around molecule (in Angstroms)""",
	'LG':
"""Log file convergence. ? ? ? """,
	'LP':
"""Log file potentials. ? ? ?""",
	'MD':
"""Membrane data. ? ? ?""",
	'NI':
"""Integer number of non-linear iterations.""",
	'PR':
"""Radius of the solvent probe molecule
that will define solvent excluded surface in
Lee and Richard's sense (in Angstroms 0.0)."""
}

OutputOptionsHelp = {
	'LOG':
"""Output log file.""",
	'PHI':
"""Grid potential file.""",
	'EPS':
"""Site potential file.""",
	'FRC':
"""Dielectric map file.""",
	'PDB':
"""This option produces a modified PDB file
written on named output file, containing the
radius and charge assigned to each atom written
after the coordinates, in the fields used for
occupancy and B factor. It is recommended that
this option be set initially so that you can
check that all the radius and charge assignments
are correct. An additional check on the charge
assignment can be made by looking at the total
charge written to the log file.""",
	'G':
"""The TOTAL ENERGY (formerly called the
grid energy) is that obtained from the potential
at each charge WITHIN the grid, multiplying by
that charge, and summing over all such sites.
It contains all the real electrostatic energy
terms, plus the self energy of the grid.  This
latter is not a meaningful number in itself, but
can be subtracted out to yield meaningful
quantities such as solvation energies etc.""",
	'S':
"""The REACTION FIELD ENERGY term (formerly
called the solvation energy term) is obtained by 
calculating the induced surface charge at each
surface point within the box, then using these
charges to calculate the potential at every
charge, not just those in the box.  If the
molecule lies entirely within the box, and there
is no salt present, this corresponds to the
energy of taking the molecule from a solvent of 
dielectric equal to that of the interior, to
that of the exterior.  Depending on the physical
process, this may be the required solvation
energy, but in general the solvation energy is
obtained by taking the difference in reaction
field energies between suitable final and initial
reference states that define the required process-
hence the name change.""",
	'C':
"""Coulombic energy""",
	'AS':
"""Analytical surface energy""",
	'AG':
"""Analytical grid energy"""
}
