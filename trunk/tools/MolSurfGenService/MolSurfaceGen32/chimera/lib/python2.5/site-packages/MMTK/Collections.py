# This module defines collections of chemical objects.
#
# Written by Konrad Hinsen
# last revision: 2008-2-12
#

import ConfigIO, Utility, Units, ParticleProperties, Visualization
from Scientific.Geometry import Vector, Tensor, Objects3D
from Scientific.Geometry import Quaternion, Transformation
from Scientific import N as Numeric
import copy, operator, types

#
# This class defines groups of atoms. It is used as a base class
# for anything containing atoms, including chemical objects, collections,
# universes etc., but it can't be used directly. All its subclasses
# must define a method atomList() that returns a list of all their atoms.
#
class GroupOfAtoms:

    """Anything that consists of atoms

    This class is a Glossary:MixInClass that defines a large set
    of operations which are common to all objects that consist of
    atoms, i.e. any subset of a chemical system. Examples are
    atoms, molecules, collections, or universes.
    """
    
    def numberOfAtoms(self):
        "Returns the number of atoms."
        return len(self.atomList())

    def numberOfPoints(self):
        """Returns the number of geometrical points that define the
        object. It is currently always equal to the number of atoms,
        but could be different e.g. for quantum systems, in which
        each atom is described by a wave function or a path integral."""
        n = 0
        for a in self.atomList():
            n = n + a.numberOfPoints()
        return n

    numberOfCartesianCoordinates = numberOfPoints

    def numberOfFixedAtoms(self):
        "Returns the number of atoms that are fixed, i.e. cannot move."
        n = 0
        for a in self.atomList():
            try:
                if a.fixed: n = n + 1
            except AttributeError: pass
        return n

    def degreesOfFreedom(self):
        "Returns the number of mechanical degrees of freedom."
        return 3*(self.numberOfAtoms()-self.numberOfFixedAtoms())

    def atomCollection(self):
        "Returns a collection containing all atoms in the object."
        return Collection(self.atomList())

    def atomsWithDefinedPositions(self, conf = None):
        "Returns a collection of all atoms that have a definite position."
        return Collection(filter(lambda a, c=conf:
                                 Utility.isDefinedPosition(a.position(c)),
                                 self.atomList()))

    def mass(self):
        "Returns the total mass."
        atoms = self.atomList()
        if atoms:
            return reduce(operator.add, map(lambda a: a._mass, atoms))
        else:
            return 0.

    def centerOfMass(self, conf = None):
        "Returns the center of mass."
        offset = None
        universe = self.universe()
        if universe is not None:
            offset = universe.contiguousObjectOffset([self], conf)
        m = 0.
        mr = Vector(0.,0.,0.)
        if offset is None:
            for a in self.atomList():
                m = m + a._mass
                mr = mr + a._mass * a.position(conf)
        else:
            for a in self.atomList():
                m = m + a._mass
                mr = mr + a._mass * (a.position(conf)+offset[a])
        return mr/m

    position = centerOfMass

    def centerAndMomentOfInertia(self, conf = None):
        "Returns the center of mass and the moment of inertia tensor."
        from Scientific.Geometry import delta
        offset = None
        universe = self.universe()
        if universe is not None:
            offset = universe.contiguousObjectOffset([self], conf)
        m = 0.
        mr = Vector(0.,0.,0.)
        t = Tensor(3*[3*[0.]])
        for a in self.atomList():
            ma = a._mass
            if offset is None:
                r = a.position(conf)
            else:
                r = a.position(conf)+offset[a]
            m = m + ma
            mr = mr + ma*r
            t = t + ma*r.dyadicProduct(r)
        cm = mr/m
        t = t - m*cm.dyadicProduct(cm)
        t = t.trace()*delta - t
        return cm, t

    def rotationalConstants(self, conf=None):
        """Returns a sorted array of rotational constants A, B, C
        in internal units."""
        com, i = self.centerAndMomentOfInertia(conf)
        pmi = i.eigenvalues()
        return Numeric.sort(Units.h / (8.*Numeric.pi*Numeric.pi*pmi))[::-1]

    def boundingBox(self, conf = None):
        """Returns two opposite corners of a bounding box around the
        object. The bounding box is the smallest rectangular bounding box
        with edges parallel to the coordinate axes."""
        atoms = self.atomList()
        min = atoms[0].position(conf).array
        max = min
        for a in atoms[1:]:
            r = a.position(conf).array
            min = Numeric.minimum(min, r)
            max = Numeric.maximum(max, r)
        return Vector(min), Vector(max)

    def boundingSphere(self, conf = None):
        """Returns a sphere that contains all atoms in the object.
        This is *not* the minimal bounding sphere, just *some*
        bounding sphere."""
        atoms = self.atomList()
        r = Vector(0., 0., 0.)
        for a in atoms:
            r = r + a.position(conf)
        center = r/len(atoms)
        r = 0.
        for a in self.atomList():
            r = max(r, (a.position(conf)-center).length())
        return Objects3D.Sphere(center, r)

    def rmsDifference(self, conf1, conf2 = None):
        """Returns the RMS (root-mean-square) difference between the
        conformations of the object in two universe configurations, |conf1|
        and |conf2| (the latter defaults to the current configuration)."""
        universe = conf1.universe
        m = 0.
        rms = 0.
        for a in self.atomList():
            ma = a._mass
            dr = universe.distanceVector(a.position(conf1), a.position(conf2))
            m = m + ma
            rms = rms + ma*dr*dr
        return Numeric.sqrt(rms/m)

    def findTransformationAsQuaternion(self, conf1, conf2 = None):
        universe = self.universe()
        if conf1.universe != universe:
            raise ValueError("conformation is for a different universe")
        if conf2 is None:
            conf1, conf2 = conf2, conf1
        else:
            if conf2.universe != universe:
                raise ValueError("conformation is for a different universe")
        ref = conf1
        conf = conf2
        weights = universe.masses()
        weights = weights/self.mass()
        ref_cms = self.centerOfMass(ref).array
        pos = Numeric.zeros((3,), Numeric.Float)
        possq = 0.
        cross = Numeric.zeros((3, 3), Numeric.Float)
        for a in self.atomList():
            r = a.position(conf).array
            r_ref = a.position(ref).array-ref_cms
            w = weights[a]
            pos = pos + w*r
            possq = possq + w*Numeric.add.reduce(r*r) \
                          + w*Numeric.add.reduce(r_ref*r_ref)
            cross = cross + w*r[:, Numeric.NewAxis]*r_ref[Numeric.NewAxis, :]
        k = Numeric.zeros((4, 4), Numeric.Float)
        k[0, 0] = -cross[0, 0]-cross[1, 1]-cross[2, 2]
        k[0, 1] = cross[1, 2]-cross[2, 1]
        k[0, 2] = cross[2, 0]-cross[0, 2]
        k[0, 3] = cross[0, 1]-cross[1, 0]
        k[1, 1] = -cross[0, 0]+cross[1, 1]+cross[2, 2]
        k[1, 2] = -cross[0, 1]-cross[1, 0]
        k[1, 3] = -cross[0, 2]-cross[2, 0]
        k[2, 2] = cross[0, 0]-cross[1, 1]+cross[2, 2]
        k[2, 3] = -cross[1, 2]-cross[2, 1]
        k[3, 3] = cross[0, 0]+cross[1, 1]-cross[2, 2]
        for i in range(1, 4):
            for j in range(i):
                k[i, j] = k[j, i]
        k = 2.*k
        for i in range(4):
            k[i, i] = k[i, i] + possq - Numeric.add.reduce(pos*pos)
        from Scientific import LA
        e, v = LA.eigenvectors(k)
        i = Numeric.argmin(e)
        v = v[i]
        if v[0] < 0: v = -v
        if e[i] <= 0.:
            rms = 0.
        else:
            rms = Numeric.sqrt(e[i])
        return Quaternion.Quaternion(v), Vector(ref_cms), \
               Vector(pos), rms

    def findTransformation(self, conf1, conf2 = None):
        """Returns the linear transformation that, when applied to
        the object in configuration |conf1|, minimizes the RMS distance
        to the conformation in |conf2|, and the minimal RMS distance.
        If |conf2| is 'None', returns the transformation from the
        current configuration to |conf1| and the associated RMS distance.
        The algorithm is described in [Article:Kneller1990]."""
        q, cm1, cm2, rms = self.findTransformationAsQuaternion(conf1, conf2)
        return Transformation.Translation(cm2) * \
               q.asRotation() * \
               Transformation.Translation(-cm1), \
               rms

    def translateBy(self, vector):
        "Translates the object by the displacement |vector|."
        for a in self.atomList():
            a.translateBy(vector)

    def translateTo(self, position):
        "Translates the object such that its center of mass is at |position|."
        self.translateBy(position-self.centerOfMass())

    def normalizePosition(self):
        self.translateTo(Vector(0., 0., 0.))

    def normalizeConfiguration(self, repr=None):
        """Applies a linear transformation such that the coordinate
        origin becomes the center of mass of the object and its
        principal axes of inertia are parallel to the three coordinate
        axes.

        A specific representation can be chosen by setting |repr| to
          Ir    : x y z <--> b c a
          IIr   : x y z <--> c a b
          IIIr  : x y z <--> a b c
          Il    : x y z <--> c b a
          IIl   : x y z <--> a c b
          IIIl  : x y z <--> b a c
        """
        transformation = self.normalizingTransformation(repr)
        self.applyTransformation(transformation)

    def normalizingTransformation(self, repr=None):
        """Returns a linear transformation that shifts the center of mass
        of the object to the coordinate origin and makes its
        principal axes of inertia parallel to the three coordinate
        axes.

        A specific representation can be chosen by setting |repr| to
          Ir    : x y z <--> b c a
          IIr   : x y z <--> c a b
          IIIr  : x y z <--> a b c
          Il    : x y z <--> c b a
          IIl   : x y z <--> a c b
          IIIl  : x y z <--> b a c
        """
        from Scientific.LA import determinant
        cm, inertia = self.centerAndMomentOfInertia()
        ev, diag = inertia.diagonalization()
        if determinant(diag.array) < 0:
            diag.array[0] = -diag.array[0]
        if repr != None:
            seq = Numeric.argsort(ev)
            if repr == 'Ir':
                seq = Numeric.array([seq[1], seq[2], seq[0]])
            elif repr == 'IIr':
                seq = Numeric.array([seq[2], seq[0], seq[1]])
            elif repr == 'Il':
                seq = Numeric.seq[2::-1]
            elif repr == 'IIl':
                seq[1:3] = Numeric.array([seq[2], seq[1]])
            elif repr == 'IIIl':
                seq[0:2] = Numeric.array([seq[1], seq[0]])
            elif repr != 'IIIr':
                print 'unknown representation'
            diag.array = Numeric.take(diag.array, seq)                
        return Transformation.Rotation(diag)*Transformation.Translation(-cm)

    def applyTransformation(self, t):
        "Applies the transformation |t| to the object."
        for a in self.atomList():
            a.setPosition(t(a.position()))

    def displacementUnderTransformation(self, t):
        """Returns the displacement vectors (in a ParticleVector)
        for the atoms in the object that correspond to the
        transformation |t|."""
        d = ParticleProperties.ParticleVector(self.universe())
        for a in self.atomList():
            r = a.position()
            d[a] = t(r)-r
        return d

    def rotateAroundCenter(self, axis_direction, angle):
        """Rotates the object by the given |angle| around an axis
        that passes through its center of mass and has the given
        |direction|."""
        cm = self.centerOfMass()
        t = Transformation.Translation(cm) * \
            Transformation.Rotation(axis_direction, angle) * \
            Transformation.Translation(-cm)
        self.applyTransformation(t)

    def rotateAroundOrigin(self, axis, angle):
        """Rotates the object by the given |angle| around an axis
        that passes through the coordinate origin and has the given
        |direction|."""
        self.applyTransformation(Transformation.Rotation(axis, angle))

    def rotateAroundAxis(self, point1, point2, angle):
        """Rotates the object by the given |angle| around the axis
        that passes through |point1| and |point2|"""
        tr1 = Transformation.Translation(-point1)
        tr2 = Transformation.Rotation(point2-point1, angle)
        tr3 = tr1.inverse()
        self.applyTransformation(tr3*tr2*tr1)

    def writeToFile(self, filename, configuration = None, format = None):
        """Writes a representation of the object in the given
        |configuration| to the file identified by |filename|.
        The |format| can be either "pdb" or "vrml"; if no format is
        specified, it is deduced from the filename. An optional subformat
        specification can be added to the format name, separated
        by a dot. The subformats of "pdb" are defined by the
        module 'Scientific.IO.PDB', the subformats of "vrml" are
        "wireframe" (the default, yielding a wireframe representation),
        "ball_and_stick" (yielding a ball-and-stick representation),
        "highlight" (like wireframe, but with a small sphere for
        all atoms that have an attribute "highlight" with a non-zero value),
        and "charge" (wireframe plus small spheres for the atoms with colors
        from a red-to-green color scale to indicate the charge).
        """
        universe = self.universe()
        if universe is not None:
            configuration = universe.contiguousObjectConfiguration(
                               [self], configuration)
        file = ConfigIO.OutputFile(filename, format)
        file.write(self, configuration)
        file.close()

    def view(self, configuration = None, format = 'pdb'):
        """Starts an external viewer for the object in the given
        |configuration|. The optional parameter |format| indicates
        which format (and hence which viewer) should be used;
        the formats are "pdb" and "vrml". An optional subformat
        specification can be added to the format name, separated
        by a dot. The subformats of "pdb" are defined by the
        module 'Scientific.IO.PDB', the subformats of "vrml" are
        "wireframe" (the default, yielding a wireframe representation),
        "ball_and_stick" (yielding a ball-and-stick representation),
        "highlight" (like wireframe, but with a small sphere for
        all atoms that have an attribute "highlight" with a non-zero value),
        and "charge" (wireframe plus small spheres for the atoms with colors
        from a red-to-green color scale to indicate the charge)."""
        universe = self.universe()
        if universe is not None:
            configuration = universe.contiguousObjectConfiguration([self],
                                                                configuration)
        Visualization.viewConfiguration(self, configuration, format)

    def kineticEnergy(self, velocities = None):
        "Returns the kinetic energy."
        if velocities is None:
            velocities = self.atomList()[0].universe().velocities()
        energy = 0.
        for a in self.atomList():
            v = velocities[a]
            energy = energy + a._mass*(v*v)
        return 0.5*energy

    def temperature(self, velocities = None):
        "Returns the temperature."
        energy = self.kineticEnergy(velocities)
        return 2.*energy/(self.degreesOfFreedom()*Units.k_B)

    def momentum(self, velocities = None):
        "Returns the momentum."
        if velocities is None:
            velocities = self.atomList()[0].universe().velocities()
        p = Vector(0., 0., 0.)
        for a in self.atomList():
            p = p + a._mass*velocities[a]
        return p

    def angularMomentum(self, velocities = None, conf = None):
        "Returns the angular momentum."
        if velocities is None:
            velocities = self.atomList()[0].universe().velocities()
        cm = self.centerOfMass(conf)
        l = Vector(0., 0., 0.)
        for a in self.atomList():
            l = l + a._mass*a.position(conf).cross(velocities[a])
        return l

    def angularVelocity(self, velocities = None, conf = None):
        "Returns the angular velocity."
        if velocities is None:
            velocities = self.atomList()[0].universe().velocities()
        cm, inertia = self.centerAndMomentOfInertia(conf)
        l = Vector(0., 0., 0.)
        for a in self.atomList():
            l = l + a._mass*a.position(conf).cross(velocities[a])
        return inertia.inverse()*l
        
    def universe(self):
        """Returns the universe of which the object is part. For an
        object that is not part of a universe, the result is 'None'."""
        atoms = self.atomList()
        if not atoms:
            return None
        universe = atoms[0].universe()
        for a in atoms[1:]:
            if a.universe() is not universe:
                return None
        return universe

    def charge(self):
        """Returns the total charge of the object. This is defined only
        for objects that are part of a universe with a force field that
        defines charges."""
        return self.universe().forcefield().charge(self)

    def dipole(self, reference = None):
        """Returns the total dipole moment of the object. This is defined only
        for objects that are part of a universe with a force field that
        defines charges."""
        return self.universe().forcefield().dipole(self, reference)

    def booleanMask(self):
        """Returns a ParticleScalar object that contains a value of 1
        for each atom that is in the object and a value of 0 for all
        other atoms in the universe."""
        universe = self.universe()
        if universe is None:
            raise ValueError("object not in a universe")
        array = Numeric.zeros((universe.numberOfAtoms(),), Numeric.Int)
        mask = ParticleProperties.ParticleScalar(universe, array)
        for a in self.atomList():
            mask[a] = 1
        return mask

#
# This class defines a general collection that can contain
# chemical objects and other collections.
#
import ChemicalObjects

class Collection(GroupOfAtoms, Visualization.Viewable):

    """Collection of chemical objects

    A Glossary:Subclass of Class:MMTK.Collections.GroupOfAtoms
    and Class:MMTK.Visualization.Viewable.

    Collections permit the grouping of arbitrary chemical objects
    (atoms, molecules, etc.) into one object for the purpose of analysis
    or manipulation.

    Constructor: Collection(|objects|=None)

    Arguments:

    |objects| -- a chemical object or a sequence of chemical objects that
                 define the initial content of the collection.

    Collections permit length inquiry, item extraction by indexing,
    and iteration, like any Python sequence object. Two collections
    can be added to yield a collection that contains the combined
    elements.
    """

    def __init__(self, *args):
        self.objects = []
        self.addObject(args)

    is_collection = 1

    def addObject(self, object):
        """Adds |object| to the collection. If |object| is another collection
        or a list, all of its elements are added."""
        if ChemicalObjects.isChemicalObject(object):
            self.addChemicalObject(object)
        elif isCollection(object):
            self.addChemicalObjectList(object.objectList())
        elif Utility.isSequenceObject(object):
            if object and ChemicalObjects.isChemicalObject(object[0]):
                self.addChemicalObjectList(list(object))
            else:
                for o in object:
                    self.addObject(o)
        else:
            raise TypeError('Wrong object type in collection')

    def addChemicalObject(self, object):
        self.objects.append(object)

    def addChemicalObjectList(self, list):
        self.objects = self.objects + list

    def removeObject(self, object):
        """Removes |object| from the collection. If |object| is a collection
        or a list, each of its elements is removed. The object to be removed
        must be an element of the collection."""
        if ChemicalObjects.isChemicalObject(object):
            self.removeChemicalObject(object)
        elif isCollection(object) or Utility.isSequenceObject(object):
            for o in object:
                self.removeObject(o)
        else:
            raise ValueError('Object not in this collection')

    def removeChemicalObject(self, object):
        try:
            self.objects.remove(object)
        except ValueError:
            raise ValueError('Object not in this collection')

    def selectShell(self, point, r1, r2=0.):
        """Return a collection of all elements whose
        distance from |point| is between |r1| and |r2|."""
        if r1 > r2:
            r1, r2 = r2, r1
        universe = self.universe()
        in_shell = []
        for o in self.objects:
            for a in o.atomList():
                r =  universe.distance(a.position(), point)
                if r >= r1 and r <= r2:
                    in_shell.append(o)
                    break
        return Collection(in_shell)

    def selectBox(self, p1, p2):
        """Return a collection of all elements that lie
        within a box whose corners are given by |p1| and |p2|."""
        x1 = Numeric.minimum(p1.array, p2.array)
        x2 = Numeric.maximum(p1.array, p2.array)
        in_box = []
        for o in self.objects:
            r = o.position().array
            if Numeric.logical_and.reduce( \
                Numeric.logical_and(Numeric.less_equal(x1, r),
                                    Numeric.less(r, x2))):
                in_box.append(o)
        return Collection(in_box)

    def objectList(self, klass = None):
        """Returns a list of all objects in the collection.
        If |klass| is not None, only objects whose class is equal
        to |klass| are returned."""
        if klass is None:
            return self.objects
        else:
            return filter(lambda o, k=klass: o.__class__ is k,
                          self.objects)

    def atomList(self):
        "Returns a list containing all atoms of all objects in the collection."
        lists = map(lambda o: o.atomList(), self.objectList())
        if lists:
            return reduce(operator.add, lists)
        else:
            return []

    def numberOfAtoms(self):
        "Returns the total number of atoms in the objects of the collection."
        count = map(lambda o: o.numberOfAtoms(), self.objectList())
        if count:
            return reduce(operator.add, count)
        else:
            return 0
    
    def universe(self):
        """Returns the universe of which the objects in the collection
        are part. If no such universe exists, the return value is 'None'."""
        if not self.objects:
            return None
        universe = self.objects[0].universe()
        for o in self.objects[1:]:
            if o.universe() is not universe:
                return None
        return universe

    def __len__(self):
        return len(self.objects)

    def __getitem__(self, item):
        return self.objects[item]

    def __add__(self, other):
        return Collection(self.objectList(), other.objectList())

    def __str__(self):
        return "Collection of %d objects" % len(self.objects)

    def map(self, function):
        """Applies |function| to all objects in the collection and
        returns the list of the results. If the results are chemical
        objects, a Collection object is returned instead of a list."""
        list = map(function, self.objectList())
        if list and ChemicalObjects.isChemicalObject(list[0]):
            return Collection(list)
        else:
            return list

    def bondedUnits(self):
        bu = []
        for o in self.objects:
            bu = bu + o.bondedUnits()
        return bu

    def degreesOfFreedom(self):
        return GroupOfAtoms.degreesOfFreedom(self) \
               - self.numberOfDistanceConstraints()

    def distanceConstraintList(self):
        "Returns the list of distance constraints."
        dc = []
        for o in self.objects:
            dc = dc + o.distanceConstraintList()
        return dc

    def numberOfDistanceConstraints(self):
        "Returns the number of distance constraints."
        n = 0
        for o in self.objects:
            n = n + o.numberOfDistanceConstraints()
        return n

    def setBondConstraints(self, universe=None):
        "Sets distance constraints for all bonds."
        if universe is None:
            universe = self.universe()
        for o in self.objects:
            o.setBondConstraints(universe)

    def removeDistanceConstraints(self, universe=None):
        "Removes all distance constraints."
        if universe is None:
            universe = self.universe()
        for o in self.objects:
            o.removeDistanceConstraints(universe)

    def _graphics(self, conf, distance_fn, model, module, options):
        lists = []
        for o in self.objects:
            lists.append(o._graphics(conf, distance_fn, model,
                                     module, options))
        return reduce(operator.add, lists, [])

    def __copy__(self):
        return self.__class__(copy.copy(self.objects))


# type check for collections

def isCollection(object):
    "Return 1 if |object| is a Collection."
    return hasattr(object, 'is_collection')

#
# This class defines a partitioned collection. Such collections
# divide their objects into cubic boxes according to their positions.
# It is then possible to find potential neighbours much more efficiently.
#
class PartitionedCollection(Collection):

    """Collection with cubic partitions

    A Glossary:Subclass of Class:MMTK.Collection.

    A PartitionedCollection differs from a plain Collection by
    sorting its elements into small cubic cells. This makes adding
    objects slower, but geometrical operations like 
    selectShell become much faster for a large number of
    objects.

    Constructor: PartitionedCollection(|partition_size|, |objects|=None)

    Arguments:
    
    |partition_size| -- the edge length of the cubic cells

    |objects| -- a chemical object or a sequence of chemical objects that
                 define the initial content of the collection.
    """

    def __init__(self, partition_size, *args):
        self.partition_size = 1.*partition_size
        self.undefined = []
        self.partition = {}
        self.addObject(args)

    def addChemicalObject(self, object):
        p = object.position()
        if p is None:
            self.undefined.append(object)
        else:
            index = self.partitionIndex(p)
            try:
                partition = self.partition[index]
            except KeyError:
                partition = []
                self.partition[index] = partition
            partition.append(object)
        self.all = None

    def addChemicalObjectList(self, list):
        for object in list:
            self.addChemicalObject(object)

    def removeChemicalObject(self, object):
        p = object.position()
        if p is None:
            self.undefined.remove(object)
        else:
            index = self.partitionIndex(p)
            try:
                partition = self.partition[index]
            except KeyError:
                raise ValueError('Object not in this collection')
            try:
                partition.remove(object)
            except ValueError:
                raise ValueError('Object not in this collection')
        self.all = None

    def partitionIndex(self, x):
        return (int(Numeric.floor(x[0]/self.partition_size)),
                int(Numeric.floor(x[1]/self.partition_size)),
                int(Numeric.floor(x[2]/self.partition_size)))

    def objectList(self):
        return reduce(operator.add, self.partition.values()+[self.undefined])

    def __len__(self):
        return Numeric.add.reduce(map(len, self.partition.values())) + \
               len(self.undefined)

    def __getitem__(self, item):
        if self.all is None:
            self.all = self.objectList()
        if item >= len(self.all):
            self.all = None
            raise IndexError
        return self.all[item]

    def __copy__(self):
        return self.__class__(self.partition_size,
                              copy.copy(self.objectList()))

    def partitions(self):
        """Returns a list of cubic partitions. Each partition is specified
        by a tuple containing two vectors (describing the diagonally
        opposite corners) and the list of objects in the partition."""
        list = []
        for index, objects in self.partition.items():
            min = Vector(index)*self.partition_size
            max = min + Vector(3*[self.partition_size])
            list.append((min, max, objects))
        return list

    def selectCube(self, point, edge):
        x = int(round(point[0]/self.partition_size))
        y = int(round(point[1]/self.partition_size))
        z = int(round(point[2]/self.partition_size))
        d = (Vector(x, y, z)*self.partition_size-point).length()
        n = int(Numeric.ceil((edge + d)/(2.*self.partition_size)))
        objects = []
        for nx in range(-n, n):
            for ny in range(-n, n):
                for nz in range(-n, n):
                    try:
                        objects.append(self.partition[(nx+x, ny+y, nz+z)])
                    except KeyError: pass
        return Collection(objects)

    def selectShell(self, point, min, max=0):
        if min > max:
            min, max = max, min
        objects = Collection()
        minsq = min**2
        maxsq = max**2
        for index in self.partition.keys():
            d1 = self.partition_size*Numeric.array(index) - point.array
            d2 = d1 + self.partition_size
            dmin = (d1 > 0.)*d1 - (d2 < 0.)*d2
            dminsq = Numeric.add.reduce(dmin**2)
            dmaxsq = Numeric.add.reduce(Numeric.maximum(d1**2, d2**2))
            if dminsq >= minsq and dmaxsq <= maxsq:
                objects.addObject(self.partition[index])
            elif dmaxsq >= minsq and dminsq <= maxsq:
                o = Collection(self.partition[index]).selectShell(point,
                                                                  min, max)
                objects.addObject(o)
        return objects

    def pairsWithinCutoff(self, cutoff):
        """Returns a list containing all pairs of objects in the
        collection whose center-of-mass distance is less than |cutoff|."""
        pairs = []
        positions = {}
        for index, objects in self.partition.items():
            pos = map(lambda o: o.position(), objects)
            positions[index] = pos
            for o1, o2 in Utility.pairs(zip(objects, pos)):
                if (o2[1]-o1[1]).length() <= cutoff:
                    pairs.append((o1[0], o2[0]))
        partition_cutoff = int(Numeric.floor((cutoff/self.partition_size)**2))
        ones = Numeric.array([1,1,1])
        zeros = Numeric.array([0,0,0])
        keys = self.partition.keys()
        for i in range(len(keys)):
            p1 = keys[i]
            for j in range(i+1, len(keys)):
                p2 = keys[j]
                d = Numeric.maximum(abs(Numeric.array(p2)-Numeric.array(p1)) -
                                    ones, zeros)
                if Numeric.add.reduce(d*d) <= partition_cutoff:
                    for o1, pos1 in zip(self.partition[p1],
                                        positions[p1]):
                        for o2, pos2 in zip(self.partition[p2],
                                            positions[p2]):
                            if (pos2-pos1).length() <= cutoff:
                                pairs.append((o1, o2))
        return pairs

#
# A special form of partitioned collection that stores the atoms
# of all objects that are added to it.
#
class PartitionedAtomCollection(PartitionedCollection):

    """Partitioned collection of atoms

    A Glossary:Subclass of Class:MMTK.PartitionedCollection.

    PartitionedAtomCollection objects behave like PartitionedCollection
    atoms, except that they store only atoms. When a composite chemical
    object is added, its atoms are stored instead.

    Constructor: PartitionedAtomCollection(|partition_size|, |objects|=None)

    Arguments:
    
    |partition_size| -- the edge length of the cubic cells

    |objects| -- a chemical object or a sequence of chemical objects that
                 define the initial content of the collection.
    """

    def __init__(*args):
        apply(PartitionedCollection.__init__, args)

    def addChemicalObject(self, object):
        for atom in object.atomList():
            PartitionedCollection.addChemicalObject(self, atom)

    def removeChemicalObject(self, object):
        for atom in object.atomList():
            PartitionedCollection.removeChemicalObject(self, atom)

#
# Test code
#
if __name__ == '__main__':

    from Random import randomPointInBox
    from copy import copy

    box = PartitionedCollection(1.)

    for i in xrange(100):
        x = randomPointInBox(4., 4., 4.)
        box.addObject(ChemicalObjects.Atom('c', position = x))
