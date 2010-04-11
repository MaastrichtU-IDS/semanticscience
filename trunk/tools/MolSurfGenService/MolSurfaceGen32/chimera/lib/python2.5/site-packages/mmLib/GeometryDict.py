## Copyright 2002 by PyMMLib Development Group (see AUTHORS file)
## This code is part of the PyMMLib distribution and governed by
## its license.  Please see the LICENSE file that should have been
## included as part of this package.
"""Geometry hasing/fast lookup classes.
"""

from __future__ import generators
import random
import math
import itertools


class XYZDict(object):
    """Hash all objects according to their position, allowing spacial
    location of objects quickly.  This is a brain-dead simple implementation,
    but it gets the job done.
    """
    def __init__(self, resolution):
        self.resolution = resolution
        self.geom_dict  = {}

    def calc_geom_key(self, position):
        """Calculates the cube key for the given position.
        """
        res = self.resolution
        
        return ( int(position[0] / res),
                 int(position[1] / res),
                 int(position[2] / res) )
        
    def add(self, position, item):
        """Add a item.
        """
        res = self.resolution
        
        geom_key = ( int(position[0] / res),
                     int(position[1] / res),
                     int(position[2] / res) )

        geom_tuple = (position, item)

        if self.geom_dict.has_key(geom_key):
            self.geom_dict[geom_key].append(geom_tuple)
        else:
            self.geom_dict[geom_key] = [geom_tuple]

    def remove(self, position, item):
        """Remove an item.
        """
        geom_key   = self.calc_geom_key(position)

        try:
            geom_list = self.geom_dict[geom_key]
        except KeyError:
            pass
        else:
            for geom_tuple in geom_list:
                if geom_tuple[1]==item:
                    geom_list.remove(geom_tuple)
                    return

        raise ValueError, "GeometryDict.remove(x) x not in GeometryDict"

    def iter_all(self):
        """Iter all items
        """
        for geom_list in self.geom_dict.values():
            for geom_tuple in geom_list:
                yield geom_tuple

    def iter_cube_intersection(self, position, radius):
        """Iterate all objects which intersect the cube in no particular
        order.
        """
        center_geom_key = self.calc_geom_key(position)
        bounding_cube_blocks = int(radius / self.resolution) + 1

        for i in xrange(-bounding_cube_blocks, bounding_cube_blocks+1):
            for j in xrange(-bounding_cube_blocks, bounding_cube_blocks+1):
                for k in xrange(-bounding_cube_blocks, bounding_cube_blocks+1):

                    geom_key = ( center_geom_key[0] + i,
                                 center_geom_key[1] + j,
                                 center_geom_key[2] + k )
                    
                    try:
                        geom_list = self.geom_dict[geom_key]
                    except KeyError:
                        continue

                    for geom_tuple in geom_list:
                        yield geom_tuple

    def iter_sphere_intersection(self, position, radius):
        """Iterate all objects which intersect the cube in no particular
        order.
        """
        for geom_tuple in self.iter_cube_intersection(position, radius):
            ipos = geom_tuple[0]

            x = ipos[0] - position[0]
            y = ipos[1] - position[1]
            z = ipos[2] - position[2]
            d = math.sqrt(x*x + y*y + z*z)

            if d <= radius:
                yield geom_tuple
        
    def iter_contact_distance(self, distance):
        """Iterates all items within a given contact distance.
        """
        visited = {}

        for geom_tuple1 in self.iter_all():
            visited[geom_tuple1[1]] = True

            for geom_tuple2 in self.iter_cube_intersection(
                geom_tuple1[0], distance):

                if visited.has_key(geom_tuple2[1]):
                    continue

                p1 = geom_tuple1[0]
                p2 = geom_tuple2[0]

                d = math.sqrt((p1[0]-p2[0])**2 + \
                              (p1[1]-p2[1])**2 + \
                              (p1[2]-p2[2])**2)

                if d>distance:
                    continue

                yield geom_tuple1, geom_tuple2, d
                

### <testing>
def test_module():
    import sys
    import FileIO
    
    struct = FileIO.LoadStructure(fil=sys.argv[1])

    print "Structure Loaded"

    gdict = XYZDict(2.0)

    cnt = 0
    for atm in struct.iter_atoms():
        gdict.add(atm.position, atm)
        cnt += 1

    print "Hashed %d Atoms" % (cnt)

    cnt = 0
    for (p1, atm1),(p2,atm2), dist in gdict.iter_contact_distance(1.9):
        cnt += 1
        #d = math.sqrt((p1[0]-p2[0])**2 + (p1[1]-p2[1])**2 + (p1[2]-p2[2])**2)
        #print atm1, atm2, "%6.2f" % (d)

    print "%d Bonds" % (cnt)
                
if __name__=="__main__":
    test_module()
### <testing>
