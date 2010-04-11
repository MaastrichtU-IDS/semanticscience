#
# Copyright 2000 by Peter McCluskey (pcm@rahul.net).
# You may do anything you want with it, provided this notice is kept intact.
#

_undocumented = 1

"""
surface_atoms(atoms, solvent_radius = 0., point_density = 258, ret_fmt = 0)

point_density must be 2**(2*N) + 2, where N > 1 (258 and 1026 seem best).
Returns a dictionary with an item for each input atom.
These choices for ret_fmt specify what the dictionary will hold for each atom:
 1: area
 2: (area, volume)
 3: (area, volume, points)
 4: (area, volume, points, dir_tuple)

 points is a list of 3-tuples describing coordinates of points on a
solvent-accesible surface (zero to point_density points per atom).

 dir_tuple is a 3-tuple giving crude estimate of the direction which is
locally "up", i.e. normal to the surface. It is calculated by comparing
the atom's position with the average position of an atom's accesible surface
points.

 The algorithm used is based on the method described in this paper:
 Eisenhaber, Frank, et al. "The Double Cubic Lattice Method: Efficient
Approaches to Numerical Integration of Surface Area and Volume and to
Dot Surface Contouring of Molecular Assemblies", Journal of Computational
Chemistry, Vol. 16, pp 273-284 (1995).
 I have taken a few shortcuts which probably make it a bit less accurate
than what the paper describes (in particular, I used a simple tesselation
algorithm without fully understanding the one described in the paper).

"""
import sys, math

try:
    import MMTK_surface
    have_c_code = 1
except ImportError, msg:
    import tess
    have_c_code = 0

class NeighborList:

    """
    This class is designed to efficiently find lists of atoms which are
    within a distance "radius" of each other.

    Constructor: NeighborList(|atoms|, |radius|, |atom_data|)

    Arguments:

    |atoms| - list of MMTK Atom
    |radius| - max distance between neighboring atoms
    |atom_data| - data returned from get_atom_data
    """

    def __init__(self, atoms, radius, atom_data):
        boxes = {}
        self.box_size = 2*radius
        for i in range(len(atoms)):
            f = self.box_size
            pos = atom_data[i]
            key = '%d %d %d' % (int(math.floor(pos[0]/f)),
                                int(math.floor(pos[1]/f)),
                                int(math.floor(pos[2]/f)))
            if boxes.has_key(key):
                boxes[key].append(i)
            else:
                boxes[key] = [i]
        self.boxes = boxes
        self.atoms = atoms
        self.atom_data = atom_data

    def __len__(self):
        return len(self.atoms)

    def __getitem__(self, i):
        """Returns a list of tuples describing the neighbors of the ith atom
        in the atom list. Each tuple has the index of the atom which neighbors
        atom i, followed by the square of the distance between atoms.
        """
        boxes = self.boxes
        if have_c_code:
            return MMTK_surface.FindNeighborsOfAtom(self.atoms, i, boxes,
                                                    self.box_size,
                                                    self.atom_data)
        max_dist_2 = self.box_size**2
        pos1 = self.atom_data[i]
        f = self.box_size
        key_tup = (int(math.floor(pos1[0]/f)),
                   int(math.floor(pos1[1]/f)),
                   int(math.floor(pos1[2]/f)))
        nlist = []
        for x in (-1, 0, 1):
            for y in (-1, 0, 1):
                for z in (-1, 0, 1):
                    key2 = '%d %d %d' % (key_tup[0]+x, key_tup[1]+y, key_tup[2]+z)
                    if boxes.has_key(key2):
                        for i2 in boxes[key2]:
                            if i2 != i:
                                apos = self.atom_data[i2]
                                vaax = apos[0] - pos1[0]
                                vaay = apos[1] - pos1[1]
                                vaaz = apos[2] - pos1[2]
                                d2 = vaax*vaax + vaay*vaay + vaaz*vaaz
                                if d2 > max_dist_2:
                                    continue
                                nlist.append((i2, d2))
        return nlist

def get_atom_data(atoms, solvent_radius):
    atom_data = [None] * len(atoms)
    max_rad = 0
    sumx = 0
    sumy = 0
    sumz = 0
    for i in range(len(atoms)):
        a = atoms[i]
        vdw = a.vdW_radius
        pos1 = a.position()
        atom_data[i] = (pos1[0], pos1[1], pos1[2], vdw + solvent_radius)
        sumx = sumx + atom_data[i][0]
        sumy = sumy + atom_data[i][1]
        sumz = sumz + atom_data[i][2]
        max_rad = max(max_rad, vdw + solvent_radius)
    return (max_rad, atom_data,
            (sumx/len(atoms), sumy/len(atoms), sumz/len(atoms)))

def _xlate_results(points1, points_unit, point_density, tot_rad, pos1,
                   ret_fmt, cent):
    area = 4*math.pi*(tot_rad**2)*len(points1)/point_density
    if 0:
        print 'area %6.1f %5.1f %5.3f' \
          % (area/(Units.Ang**2), tot_rad/Units.Ang,
             len(points1)/float(point_density))
    if ret_fmt >= 2:
        sumx = 0
        sumy = 0
        sumz = 0
        for p in points_unit:
            sumx = sumx + p[0]
            sumy = sumy + p[1]
            sumz = sumz + p[2]
        n = max(1, len(points1))
        vconst = 4/3.0*math.pi/point_density
        dotp1 = (pos1[0] - cent[0])*sumx + (pos1[1] - cent[1])*sumy \
                + (pos1[2] - cent[2])*sumz
        volume = vconst*((tot_rad**2)*dotp1 + (tot_rad**3)*len(points1))
        if ret_fmt == 2:
            return (area, volume)
        if ret_fmt == 4:
            grad = (sumx/n, sumy/n, sumz/n)
            return (area, volume, points1, grad)
        return (area, volume, points1)
    else:
        return area

def atom_surf(nbors, i, atom_data, pos1, tot_rad, point_density, tess1, \
              ret_unit_points = 1):
    if have_c_code:
        return MMTK_surface.surface1atom(nbors, i, atom_data, pos1, tot_rad, \
                                         point_density, ret_unit_points)
    else:
        rad1sq = tot_rad*tot_rad
        rad1_2 = 2*tot_rad
        data = []
        for (index, d2) in nbors[i]:
            apos = atom_data[index]
            vaax = apos[0] - pos1[0]
            vaay = apos[1] - pos1[1]
            vaaz = apos[2] - pos1[2]
            thresh = (d2 + rad1sq - (apos[3]**2)) / rad1_2
            data.append((vaax, vaay, vaaz, thresh))
        points_unit = []
        points1 = []
        for pt1 in tess1:
            buried = 0
            for (vx, vy, vz, thresh) in data:
                if vx*pt1[0] + vy*pt1[1] + vz*pt1[2] > thresh:
                    buried = 1
                    break
            if buried == 0:
                points1.append((tot_rad*pt1[0] + pos1[0],
                                tot_rad*pt1[1] + pos1[1],
                                tot_rad*pt1[2] + pos1[2]))
                points_unit.append(pt1)
    return (points1, points_unit)

def surface_atoms(atoms, solvent_radius = 0., point_density = 258, ret_fmt = 0):
    surf_points = {}
    (max_rad, atom_data, cent) = get_atom_data(atoms, solvent_radius)
    if have_c_code:
        tess1 = None
    else:
        tess1 = tess.tesselate(point_density)
        if len(tess1) != point_density:
            raise ValueError('point_density invalid, must be 2**(2*N) + 2, ' +
                              'where N > 1')
    nbors = NeighborList(atoms, solvent_radius + max_rad, atom_data)
    for i in range(len(atoms)):
        a1 = atoms[i]
        pos1 = atom_data[i]
        tot_rad = pos1[3]
        (points1, points_unit) = atom_surf(nbors, i, atom_data, pos1,
                                           tot_rad, point_density, tess1,
                                           ret_fmt >= 2)
        surf_points[a1] = _xlate_results(points1, points_unit, point_density,
                                         tot_rad, pos1, ret_fmt, cent)
    return surf_points

if __name__ == '__main__':
    from MMTK.PDB import PDBConfiguration
    from MMTK import Units
    import profile
    # Load the PDB sequences
    target_filename = sys.argv[1]
    pdb_conf1 = PDBConfiguration(target_filename)
    molecule_names = []
    if 0:               # enable to include all molecules in file
        for (key, mol) in pdb_conf1.molecules.items():
            for o in mol:
                molecule_names.append(o.name)
    target = pdb_conf1.createAll(molecule_names = molecule_names)
    atoms = []
    for a in target.atomList():
        if a.symbol != 'H':
            atoms.append(a)
            if a.index is None:
                a.index = len(atoms)
    point_density = 1026
    s = surface_atoms(atoms, solvent_radius = 1.4*Units.Ang,
                      point_density = point_density, ret_fmt = 4)
    tot_a = 0
    tot_v = 0
    for i in range(len(atoms)):
        atom_data = s[atoms[i]]
        if type(atom_data) is type(()):
            tot_a = tot_a + atom_data[0]
            tot_v = tot_v + atom_data[1]
            grad = atom_data[3]
            npts = len(atom_data[2])*100.0/point_density
            if 0:
              print '%5d %5d %-14.14s %3.0f a %6.2f v %6.1f  %4.1f %4.1f %4.1f' \
                    % (i+1, atoms[i].index, str(atoms[i])[-14:], npts,
                       atom_data[0]/(Units.Ang**2), atom_data[1]/(Units.Ang**3),
                       grad[0]/Units.Ang, grad[1]/Units.Ang, grad[2]/Units.Ang)
    print 'tot area %9.1f volume %9.1f' \
          % (tot_a/(Units.Ang**2), tot_v/(Units.Ang**3))
