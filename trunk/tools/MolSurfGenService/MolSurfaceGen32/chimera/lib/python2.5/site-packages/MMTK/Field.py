# This module defines scalar and vector fields in molecular systems
#
# Written by Konrad Hinsen
# last revision: 2007-5-22
#

"""This module defines field objects that are useful in the analysis
and visualization of collective motions in molecular systems. Atomic
quantities characterizing collective motions vary slowly in space, and
can be considered functions of position instead of values per atom.
Functions of position are called fields, and mathematical techniques
for the analysis of fields have proven useful in many branches of
physics. Fields can be described numerically by values on a
regular grid. In addition to permitting the application of vector
analysis methods to atomic quantities, the introduction of
fields is a valuable visualization aid, because information defined on
a coarse regular grid can be added to a picture of a molecular system
without overloading it. See also the example
Example:Miscellaneous:vector_field.py.
"""

import Collections, ParticleProperties, Visualization
from Scientific.Visualization import Color
from Scientific.Geometry import Vector, TensorAnalysis
from Scientific import N as Numeric

class AtomicField:

    """A field whose values are determined by atomic quantities

    This is an Glossary:abstract-base-class. To create field objects,
    use one of its subclasses.
    """

    def __init__(self, system, grid_size, values):
        self.system = system
        if type(grid_size) == type(()):
            self.box, self.field, self.points, self.colors = grid_size
        else:
            if values.data_rank != 1:
                raise TypeError("data not a particle variable")
            self.box = Collections.PartitionedAtomCollection(grid_size, system)
            self._setField(values)

    def _setField(self, data):
        points = []
        values = []
        colors = []
        default_color = Color.ColorByName('black')
        for min, max, atoms in self.box.partitions():
            center = 0.5*(min+max)
            points.append(center.array)
            v = data.zero()
            total_weight = 0.
            color = default_color
            for a in atoms:
                d = a.position()-center
                weight = Numeric.exp(-d*d/self.box.partition_size**2)
                v = v + weight*data[a]
                total_weight = total_weight + weight
                c = default_color
                try: c = a.color
                except AttributeError: pass
                if type(c) == type(''):
                    c = Color.ColorByName(c)
                color = color + c
            values.append(v/total_weight)
            colors.append(color)
        min = Numeric.minimum.reduce(points)
        max = Numeric.maximum.reduce(points)
        axes = (Numeric.arange(min[0], max[0]+1, self.box.partition_size),
                Numeric.arange(min[1], max[1]+1, self.box.partition_size),
                Numeric.arange(min[2], max[2]+1, self.box.partition_size))
        array = Numeric.zeros(tuple(map(len, axes)) + data.value_rank*(3,),
                              Numeric.Float)
        inside = Numeric.zeros(tuple(map(len, axes)), Numeric.Float)
        for p, v in zip(points, values):
            indices = Numeric.floor((p-min)/self.box.partition_size+0.5)
            indices = tuple(indices.astype(Numeric.Int))
            array[indices] = v
            inside[indices] = 1.
        self.field = self.field_class(axes, array, data.zero())
        inside = TensorAnalysis.ScalarField(axes, inside).gradient().length()
        self.points = []
        self.colors = []
        for i in range(len(points)):
            p = points[i]
            test = 0
            try:
                test = apply(inside, tuple(p)) > 1.e-10
            except ValueError: pass
            if test:
                self.points.append(p)
                self.colors.append(colors[i])

    def __call__(self, point):
        return self.field(point)

    def particleValues(self):
        """Returns the values of the field at the positions of the
        atoms in an appropriate subclass of
        Class:MMTK.ParticleProperties.ParticleProperty."""
        universe = self.system.universe()
        rank = self.field.rank
        if rank == 0:
            v = ParticleProperties.ParticleScalar(universe)
        elif rank == 1:
            v = ParticleProperties.ParticleVector(universe)
        else:
            raise ValueError("no appropriate return type")
        for a in self.system.atomList():
            v[a] = self.field(a.position())
        return v

    def writeToFile(self, filename, scale = 1., color = None):
        """Writes a graphical representation of the field
        to the VRML file named by |filename|, multiplying
        all values by |scale|. |color| permits the choice
        of a color for the graphics objects."""
        from Scientific.Visualization import VRML
        objects = self.graphicsObjects(scale=scale, color=color,
                                       graphics_module=VRML)
        VRML.Scene(objects).writeToFile(filename)

    def view(self, scale = 1., color = None):
        """Shows a graphical representation of the field using
        a VRML viewer. All values are multiplied by |scale|. |color|
        permits the choice of a color for the graphics objects."""
        from Scientific.Visualization import VRML
        objects = self.graphicsObjects(scale=scale, color=color,
                                       graphics_module=VRML)
        VRML.Scene(objects).view()


class AtomicScalarField(AtomicField, Visualization.Viewable):

    """Scalar field defined by atomic quantities

    A Glossary:Subclass of Class:MMTK.Field.AtomicField and
    Class:MMTK.Visualization.Viewable.

    Constructor: AtomicScalarField(|system|, |grid_size|, |values|)

    Arguments:

    |system| -- any subset of a molecular system

    |grid_size| -- the spacing of a cubic grid on which the field values
                   are stored

    |values| -- an object of class Class:MMTK.ParticleScalar containing
                the atomic values that define the field

    The field values are obtained by averaging the atomic quantities
    over all atoms in a cube of edge length |grid_size| surrounding
    each grid point.

    The method graphicsObjects, defined in class
    Class:MMTK.Visualization.Viewable, returns a small cube for each
    grid point, whose color indicates the field's value on a symmetric
    red-to-green color scale defined by the range of the field values.
    Additional keyword options are:

    -- |scale|=factor, to multiply all field values by a factor

    -- |range|=(min, max), to eliminate graphics objects for values
       that are smaller than min or larger than max
    """

    def __init__(self, system, grid_size, values):
        if values is not None and values.value_rank != 0:
            raise TypeError("data not a vector field")
        self.field_class = TensorAnalysis.ScalarField
        AtomicField.__init__(self, system, grid_size, values)

    def gradient(self):
        """Returns an Class:MMTK.Field.AtomicVectorField object representing
        the gradient of the field."""
        field = self.field.gradient()
        return AtomicVectorField(self.system, (self.box, field,
                                               self.points, self.colors), None)

    def laplacian(self):
        """Returns an Class:MMTK.Field.AtomicScalarField object representing
        the laplacian of the field."""
        field = self.field.laplacian()
        return AtomicScalarField(self.system, (self.box, field,
                                               self.points, self.colors), None)

    def _graphics(self, conf, distance_fn, model, module, options):
        scale = options.get('scale', 1.)
        range = options.get('range', (None, None))

        lower, upper = range
        size = self.box.partition_size/10.
        objects = []
        color_scale = module.SymmetricColorScale(1.)
        for p, c in zip(self.points, self.colors):
            p = tuple(p)
            v = apply(self.field, p)
            if (lower is None or v > lower) and (upper is None or v < upper):
                p = apply(Vector, p)
                v = scale*v
                if v < -1. or v > 1.:
                    m = module.DiffuseMaterial('black')
                else:
                    m = module.Material(diffuse_color = color_scale(scale*v))
                objects.append(module.Cube(p, size, material = m))
        return objects


class AtomicVectorField(AtomicField, Visualization.Viewable):

    """Vector field defined by atomic quantities

    A Glossary:Subclass of Class:MMTK.Field.AtomicField and
    Class:MMTK.Visualization.Viewable.

    Constructor: AtomicVectorField(|system|, |grid_size|, |values|)

    Arguments:

    |system| -- any subset of a molecular system

    |grid_size| -- the spacing of a cubic grid on which the field values
                   are stored

    |values| -- an object of class Class:MMTK.ParticleVector containing
                the atomic values that define the field

    The field values are obtained by averaging the atomic quantities
    over all atoms in a cube of edge length |grid_size| surrounding
    each grid point.

    The method graphicsObjects, defined in class
    Class:MMTK.Visualization.Viewable, returns a small arrow for each
    grid point. The arrow starts at the grid point and represents
    the vector value at that point.
    Additional keyword options are:

    -- |scale|=factor, to multiply all field values by a factor

    -- |diameter|=number, to define the diameter of the arrow
       objects (default: 1.)

    -- |range|=(min, max), to eliminate graphics objects for values
       whose lengths are smaller than min or larger than max

    -- |color|=string, to define the color of the arrows
    """

    def __init__(self, system, grid_size, values):
        if values is not None and values.value_rank != 1:
            raise TypeError("data not a vector field")
        self.field_class = TensorAnalysis.VectorField
        AtomicField.__init__(self, system, grid_size, values)

    def length(self):
        """Returns an Class:MMTK.Field.AtomicScalarField object representing
        the length of the field vectors."""
        field = self.field.length()
        return AtomicScalarField(self.system, (self.box, field,
                                               self.points, self.colors), None)

    def divergence(self):
        """Returns an Class:MMTK.Field.AtomicScalarField object representing
        the divergence of the field."""
        field = self.field.divergence()
        return AtomicScalarField(self.system, (self.box, field,
                                               self.points, self.colors), None)

    def curl(self):
        """Returns an Class:MMTK.Field.AtomicVectorField object representing
        the curl of the field."""
        field = self.field.curl()
        return AtomicVectorField(self.system, (self.box, field,
                                               self.points, self.colors), None)

    def laplacian(self):
        """Returns an Class:MMTK.Field.AtomicVectorField object representing
        the laplacian of the field."""
        field = self.field.curl()
        return AtomicVectorField(self.system, (self.box, field,
                                               self.points, self.colors), None)

    def _graphics(self, conf, distance_fn, model, module, options):
        scale = options.get('scale', 1.)
        diameter = options.get('diameter', 1.)
        color = options.get('color', None)
        range = options.get('range', (None, None))

        lower, upper = range
        size = diameter*self.box.partition_size/50.
        if color is not None:
            color = module.ColorByName(color)
        objects = []
        materials = {}
        for p, c in zip(self.points, self.colors):
            p = tuple(p)
            v = apply(self.field, p)
            lv = v.length()
            if (lower is None or lv > lower) and (upper is None or lv < upper):
                p = apply(Vector, p)
                if color is not None:
                    c = color
                try: m = materials[c]
                except KeyError: m = module.Material(diffuse_color = c)
                materials[c] = m
                objects.append(module.Arrow(p, p+scale*v, size, material = m))
        return objects
