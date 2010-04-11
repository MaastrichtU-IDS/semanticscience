#
# Copyright 2000 by Peter McCluskey (pcm@rahul.net).
# You may do anything you want with it, provided this notice is kept intact.
#

# This module is in part a replacement for the MolecularSurface MMTK module
# that uses the NSC code. It has a less restrictive license than the NSC code,
# and is mostly more flexible, but is probably slower and somewhat less
# accurate. It can run (slowly) without any of the C code. It has an
# additional routine surfacePointsAndGradients, which returns area, an
# "up" vector, and surface points for each atom.


# Minor modifications by Konrad Hinsen <hinsen@cnrs-orleans.fr>:
# - Replaced tabs by spaces
# - Added/adapted docstrings to MMTK conventions
# - Removed assignment of methods to class GroupOfAtoms
# - Use vectors in the return value of surfacePointsAndGradients
# - Replaced "math" module by "Numeric"
# - Renamed module _surface to MMTK_surface

"""This module provides functions that calculate molecular surfaces
and volumes.
"""


import surfm
from MMTK.Collections import GroupOfAtoms, Collection
from MMTK import Vector
from Scientific import N as Numeric

def surfaceAndVolume(self, probe_radius = 0.):
    """Returns the molecular surface and volume of |object|,
    defining the surface at a distance of |probe_radius| from
    the van-der-Waals surfaces of the atoms."""
    atoms = self.atomList()
    smap = surfm.surface_atoms(atoms, probe_radius, ret_fmt = 2)
    tot_a = 0
    tot_v = 0
    for a in atoms:
        atom_data = smap[a]
        tot_a = tot_a + atom_data[0]
        tot_v = tot_v + atom_data[1]
    return (tot_a, tot_v)

#GroupOfAtoms.surfaceAndVolume = surfaceAndVolume

def surfaceAtoms(self, probe_radius = 0.):
    """Returns a dictionary that maps the surface atoms to their
    exposed surface areas."""
    atoms = self.atomList()
    smap = surfm.surface_atoms(atoms, probe_radius, ret_fmt = 1)
    surface_atoms = {}
    for a in atoms:
        area = smap[a]
        if area > 0.:
            # we have a surface atom
            surface_atoms[a] = area
    return surface_atoms

#GroupOfAtoms.surfaceAtoms = surfaceAtoms

def surfacePointsAndGradients(self, probe_radius = 0., point_density = 258):
    """Returns a dictionary that maps the surface atoms to a tuple
    containing three surface-related quantities: the exposed surface
    are, a list of points in the exposed surface, and a gradient vector
    pointing outward from the surface."""
    atoms = self.atomList()
    smap = surfm.surface_atoms(atoms, probe_radius, ret_fmt = 4,
                               point_density = point_density)
    surface_data = {}
    for a in atoms:
        (area, volume, points1, grad) = smap[a]
        if area > 0.:
            # we have a surface atom
            surface_data[a] = (area, map(Vector, points1), Vector(grad))
    return surface_data

#GroupOfAtoms.surfacePointsAndGradients = surfacePointsAndGradients


class Contact:

    def __init__(self, a1, a2, dist = None):
        self.a1 = a1
        self.a2 = a2
        if dist is None:
            self.dist = (a1.position() - a2.position()).length()
        else:
            self.dist = dist

    def __getitem__(self, index):
        return (self.a1, self.a2)[index]

    def __cmp__(a, b):
        return cmp(a.dist, b.dist)

    def __hash__(self):
        return (self.a1, self.a2)

    def __repr__(self):
        return 'Contact(%s, %s)' % (self.a1, self.a2)

    __str__ = __repr__

def findContacts(object1, object2, contact_factor = 1.0, cutoff = 0.0):
    """Returns a list of MMTK.MolecularSurface.Contact objects
    that describe atomic contacts between |object1| and |object2|.
    A contact is defined as a pair of atoms whose distance is less than
    |contact_factor|*(r1+r2+|cutoff|) where r1 and r2 are the atomic
    van-der-Waals radii."""
    max_object1 = len(object1.atomList())
    atoms = object1.atomList() + object2.atomList()
    tup = surfm.get_atom_data(atoms, 0.0)
    max_rad = tup[0]                    # max vdW_radius
    atom_data = tup[1]
    nbors = surfm.NeighborList(atoms, contact_factor*(2*max_rad+cutoff),
                               atom_data)
    clist = []
    done = {}
    for index1 in range(len(atoms)):
        for (index2, dist2) in nbors[index1]:
            if (index1 < max_object1) != (index2 < max_object1):
                if index1 < index2:
                    a1 = atoms[index1]
                    a2 = atoms[index2]
                else:
                    a1 = atoms[index2]
                    a2 = atoms[index1]
                dist = Numeric.sqrt(dist2)
                if dist >= contact_factor*(a1.vdW_radius + a2.vdW_radius + cutoff):
                    continue
                if not done.has_key((index1, index2)):
                    clist.append(Contact(a1, a2, dist))
                    done[(index1, index2)] = 1
    return clist

if __name__ == '__main__':
    
    from MMTK.PDB import PDBConfiguration
    from MMTK import Units
    import sys

    target_filename = sys.argv[2]
    pdb_conf1 = PDBConfiguration(target_filename)
    if sys.argv[1][:2] == '-f':
        chains = pdb_conf1.createNucleotideChains()
        molecule_names = []
        if len(chains) >= 2:
            clist = findContacts(chains[0], chains[1])
        else:
            molecule_names = []
            for (key, mol) in pdb_conf1.molecules.items():
                for o in mol:
                    molecule_names.append(o.name)
            targets = pdb_conf1.createAll(molecule_names = molecule_names)
            if len(molecule_names) > 1:
                clist = findContacts(targets[0], targets[1])
            else:
                atoms = targets.atomList()
                mid = len(atoms)/2
                clist = findContacts(Collection(atoms[:mid]),
                                     Collection(atoms[mid:]))
        print len(clist), 'contacts'
        for c in clist[:8]:
            print '%-64s %6.2f' % (c, c.dist/Units.Ang)
    else:
        target = pdb_conf1.createAll()
        if sys.argv[1][:2] == '-v':
            (a, v) = target.surfaceAndVolume()
            print 'surface area %.2f volume %.2f' \
                  % (a/(Units.Ang**2), v/(Units.Ang**3))
        elif sys.argv[1][:2] == '-a':
            smap = target.surfaceAtoms(probe_radius = 1.4*Units.Ang)
            print len(smap.keys()),'of',len(target.atomList()),'atoms on surface'
        elif sys.argv[1][:2] == '-p':
            smap = target.surfacePointsAndGradients(probe_radius = 1.4*Units.Ang)
            for (a, tup) in smap.items():
                print '%-40.40s %6.2f %5d %5.1f %5.1f %5.1f' \
                      % (a.fullName(), tup[0]/(Units.Ang**2), len(tup[1]),
                         tup[2][0], tup[2][1], tup[2][2])
