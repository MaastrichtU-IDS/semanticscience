# This module deals with input and output of configurations.
#
# Written by Konrad Hinsen
# last revision: 2006-11-27
#

_undocumented = 1

import ChemicalObjects, PDB, Units, Universe, Utility
from Scientific.Geometry.Objects3D import Sphere, Cone, Plane, Line, \
                                          rotatePoint
from Scientific.Geometry import Vector
from Scientific.Visualization import VRML
from Scientific import N as Numeric
import os, string

#
# This class represents a Z-Matrix. Z-Matrix data consists of a list
# with one element for each atom being defined. Each entry is a
# list containing the data defining the atom.
#
class ZMatrix:

    """Z-Matrix specification of a molecule conformation

    ZMatrix objects can be used in chemical database entries
    to specify molecule conformations by internal coordinates.
    With the exception of the three first atoms, each atom is
    defined relative to three previously atoms by a distance,
    an angle, and a dihedral angle.

    Constructor: ZMatrix(|data|)

    Arguments:

    |data| -- a list of atom definitions. Each atom definition (except
              for the first three ones) is a list containing seven elements:

              - the atom to be defined

              - a previously defined atom and the distance to it

              - another previously defined atom and the angle to it

              - a third previously defined atom and the dihedral angle to it

              The definition of the first atom contains only the first
              element, the second atom needs the first three elements,
              and the third atom is defined by the first five elements.
    """

    def __init__(self, data):
        self.data = data
        self.coordinates = {}

    substitute = 1

    def findPositions(self):
        # First atom at origin
        self.coordinates[self.data[0][0]] = Vector(0,0,0)
        # Second atom along x-axis
        self.coordinates[self.data[1][0]] = Vector(self.data[1][2],0,0)
        # Third atom in xy-plane
        try:
            pos1 = self.coordinates[self.data[2][1]]
        except KeyError:
            raise ValueError("atom %d has no defined position"
                              % self.data[2][1].number)
        try:
            pos2 = self.coordinates[self.data[2][3]]
        except KeyError:
            raise ValueError("atom %d has no defined position"
                              % self.data[2][3].number)
        sphere = Sphere(pos1, self.data[2][2])
        cone = Cone(pos1, pos2-pos1, self.data[2][4])
        plane = Plane(Vector(0,0,0), Vector(0,0,1))
        points = sphere.intersectWith(cone).intersectWith(plane)
        self.coordinates[self.data[2][0]] = points[0]
        # All following atoms defined by distance + angle + dihedral
        for entry in self.data[3:]:
            try:
                pos1 = self.coordinates[entry[1]]
            except KeyError:
                raise ValueError("atom %d has no defined position"
                                  % entry[1].number)
            try:
                pos2 = self.coordinates[entry[3]]
            except KeyError:
                raise ValueError("atom %d has no defined position"
                                  % entry[3].number)
            try:
                pos3 = self.coordinates[entry[5]]
            except KeyError:
                raise ValueError("atom %d has no defined position"
                                  % entry[5].number)
            distance = entry[2]
            angle = entry[4]
            dihedral = entry[6]
            sphere = Sphere(pos1, distance)
            cone = Cone(pos1, pos2-pos1, angle)
            plane123 = Plane(pos3, pos2, pos1)
            points = sphere.intersectWith(cone).intersectWith(plane123)
            for p in points:
                if Plane(pos2, pos1, p).normal * plane123.normal > 0:
                    break
            p = rotatePoint(p, Line(pos1, pos2-pos1), dihedral)
            self.coordinates[entry[0]] = p

    def applyTo(self, object):
        """Define the positions of the atoms in |object| by the
        internal coordinates of the Z-Matrix."""
        if not len(self.coordinates):
            self.findPositions()
        for entry in self.coordinates.items():
            object.setPosition(entry[0], entry[1])
        object.normalizePosition()

#
# This class represents a dictionary of Cartesian positions
#
class Cartesian:

    """Cartesian specification of a molecule conformation

    Cartesian objects can be used in chemical database entries
    to specify molecule conformations by Cartesian coordinates.

    Constructor: Cartesian(|data|)

    Arguments:

    |data| -- a dictionary mapping atoms to tuples of length three
              that define its Cartesian coordinates
    """
    
    def __init__(self, dict):
        self.dict = dict

    substitute = 1

    def applyTo(self, object):
        """Define the positions of the atoms in |object| by the
        stored coordinates."""
        for a, r in self.dict.items():
            object.setPosition(a, Vector(r[0], r[1], r[2]))

#
# VRML output
#
class VRMLWireframeFile(VRML.VRMLFile):

    def __init__(self, filename, color_values = None):
        VRML.VRMLFile.__init__(self, filename, 'w')
        self.warning = 0
        self.color_values = color_values
        if self.color_values is not None:
            lower = Numeric.minimum.reduce(color_values.array)
            upper = Numeric.maximum.reduce(color_values.array)
            self.color_scale = VRML.ColorScale((lower, upper))

    def write(self, object, configuration = None, distance = None):
        if distance is None:
            try:
                distance = object.universe().distanceVector
            except AttributeError:
                distance = Universe.InfiniteUniverse().distanceVector
        if not ChemicalObjects.isChemicalObject(object):
            for o in object:
                self.write(o, configuration, distance)
        else:
            for bu in object.bondedUnits():
                for a in bu.atomList():
                    self.writeAtom(a, configuration)
                if hasattr(bu, 'bonds'):
                    for b in bu.bonds:
                        self.writeBond(b, configuration, distance)

    def close(self):
        VRML.VRMLFile.close(self)
        if self.warning:
            Utility.warning('Some atoms are missing in the output file ' + \
                            'because their positions are undefined.')
            self.warning = 0

    def atomColor(self, atom):
        if self.color_values is None:
            return atom.color
        else:
            return self.color_scale(self.color_values[atom])

    def writeAtom(self, atom, configuration):
        pass

    def writeBond(self, bond, configuration, distance):
        p1 = bond.a1.position(configuration)
        p2 = bond.a2.position(configuration)
        if p1 is not None and p2 is not None:
            bond_vector = 0.5*distance(bond.a1, bond.a2, configuration)
            cut = bond_vector != 0.5*(p2-p1)
            color1 = self.atomColor(bond.a1)
            color2 = self.atomColor(bond.a2)
            material1 = VRML.EmissiveMaterial(color1)
            material2 = VRML.EmissiveMaterial(color2)
            if color1 == color2 and not cut:
                c = VRML.Line(p1, p2, material = material1)
                c.writeToFile(self)
            else:
                c = VRML.Line(p1, p1+bond_vector, material = material1)
                c.writeToFile(self)
                c = VRML.Line(p2, p2-bond_vector, material = material2)
                c.writeToFile(self)


class VRMLHighlight(VRMLWireframeFile):

    def writeAtom(self, atom, configuration):
        try:
            highlight = atom.highlight
        except AttributeError:
            highlight = 0
        if highlight:
            p = atom.position(configuration)
            if p is None:
                self.warning = 1
            else:
                s = VRML.Sphere(p, 0.1*Units.Ang,
                                material = VRML.DiffuseMaterial(atom.color),
                                reuse = 1)
                s.writeToFile(self)


class VRMLBallAndStickFile(VRMLWireframeFile):

    def writeAtom(self, atom, configuration):
        p = atom.position(configuration)
        if p is None:
            self.warning = 1
        else:
            color = self.atomColor(atom)
            s = VRML.Sphere(p, 0.1*Units.Ang,
                            material = VRML.DiffuseMaterial(color),
                            reuse = 1)
            s.writeToFile(self)

    def writeBond(self, bond, configuration, distance):
        p1 = bond.a1.position(configuration)
        p2 = bond.a2.position(configuration)
        if p1 is not None and p2 is not None:
            bond_vector = 0.5*distance(bond.a1, bond.a2, configuration)
            cut = bond_vector != 0.5*(p2-p1)
            color1 = self.atomColor(bond.a1)
            color2 = self.atomColor(bond.a2)
            material1 = VRML.EmissiveMaterial(color1)
            material2 = VRML.EmissiveMaterial(color2)
            if color1 == color2 and not cut:
                c = VRML.Cylinder(p1, p2, 0.03*Units.Ang,
                                  material = material1)
                c.writeToFile(self)
            else:
                c = VRML.Cylinder(p1, p1+bond_vector, 0.03*Units.Ang,
                                  material = material1)
                c.writeToFile(self)
                c = VRML.Cylinder(p2, p2-bond_vector, 0.03*Units.Ang,
                                  material = material2)
                c.writeToFile(self)


class VRMLChargeFile(VRMLWireframeFile):

    color_scale = VRML.SymmetricColorScale(1.)

    def writeAtom(self, atom, configuration):
        p = atom.position(configuration)
        c = atom.charge()
        c = max(min(c, 1.), -1.)
        if p is None:
            self.warning = 1
        else:
            s = VRML.Sphere(p, 0.1*Units.Ang,
                            material = VRML.Material(diffuse_color =
                                                     self.color_scale(c)))
            s.writeToFile(self)

    bond_material = VRML.DiffuseMaterial('black')

    def writeBond(self, bond, configuration, distance):
        p1 = bond.a1.position(configuration)
        p2 = bond.a2.position(configuration)
        if p1 is not None and p2 is not None:
            bond_vector = 0.5*distance(bond.a1, bond.a2, configuration)
            cut = bond_vector != 0.5*(p2-p1)
            if not cut:
                c = VRML.Line(p1, p2, material = self.bond_material)
                c.writeToFile(self)
            else:
                c = VRML.Line(p1, p1+bond_vector, material = self.bond_material)
                c.writeToFile(self)
                c = VRML.Line(p2, p2-bond_vector, material = self.bond_material)
                c.writeToFile(self)

VRMLFile = VRMLWireframeFile

#
# Recognize some standard file types by their extensions
#
def fileFormatFromExtension(filename):
    filename, ext = os.path.splitext(filename)
    if ext in _file_compressions:
        filename, ext = os.path.splitext(filename)
    try:
        return _file_formats[ext]
    except KeyError:
        raise IOError('Unknown file format')

_file_formats = {'.pdb': 'pdb', '.wrl': 'vrml'}
_file_compressions = ['.gz', '.Z']

#
# Output file for a specified format
#
def OutputFile(filename, format = None):
    if format is None:
        format = fileFormatFromExtension(filename)
    format = tuple(string.split(format, '.'))
    try:
        return _file_types[format](filename)
    except KeyError:
        if len(format) == 1:
            return _file_types[format[0]](filename)
        else:
            _file_types[format[0]](filename, format[1])

_file_types = {'pdb': PDB.PDBOutputFile,
               ('vrml',): VRMLFile,
               ('vrml', 'wireframe'): VRMLWireframeFile,
               ('vrml', 'highlight'): VRMLHighlight,
               ('vrml', 'ball_and_stick'): VRMLBallAndStickFile,
               ('vrml', 'charge'): VRMLChargeFile}
