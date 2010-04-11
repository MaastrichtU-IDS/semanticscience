# -----------------------------------------------------------------------------
# Eliminate copies of close transformations from a set of transformations.
#
class Binned_Transforms:

    def __init__(self, angle, translation, bfactor = 10):

        self.angle = angle
        self.translation = translation
        spacing = (angle, translation, translation, translation)
        self.spacing = spacing
        bin_size = map(lambda s: s*bfactor, spacing)
        self.bins = Bins(bin_size)

    # -------------------------------------------------------------------------
    #
    def add_transform(self, tf):

        a = rotation_angle(tf)  # In range 0 to pi
        x,y,z = tf[0][3], tf[1][3], tf[2][3]
        self.bins.add_object((a,x,y,z), tf)

    # -------------------------------------------------------------------------
    #
    def close_transforms(self, tf):

        a = rotation_angle(tf)  # In range 0 to pi
        x,y,z = tf[0][3], tf[1][3], tf[2][3]
        c = (a,x,y,z)

        clist = self.bins.close_objects(c, self.spacing)
        if len(clist) == 0:
            return []

        close = []
        from Matrix import invert_matrix, multiply_matrices
        itf = invert_matrix(tf)
        for ctf in clist:
            dtf = multiply_matrices(ctf, itf)
            x,y,z = dtf[0][3], dtf[1][3], dtf[2][3]
            if (abs(x) < self.translation and
                abs(y) < self.translation and
                abs(z) < self.translation):
                a = rotation_angle(dtf)
                from math import pi
                if a < self.angle:
                    close.append(ctf)

        return close
        
# -----------------------------------------------------------------------------
# In range 0 to pi.
#
def rotation_angle(tf):

    tr = tf[0][0] + tf[1][1] + tf[2][2]
    cosa = .5 * (tr - 1)
    if cosa > 1:
        cosa = 1
    elif cosa < -1:
        cosa = -1
    from math import acos
    a = acos(cosa)
    return a

# -----------------------------------------------------------------------------
# Bin objects in a grid for fast lookup of objects close to a given object.
#
class Bins:

    def __init__(self, bin_size):

        self.bin_size = bin_size
        self.bins = {}

    # -------------------------------------------------------------------------
    #
    def add_object(self, coords, object):

        bc = map(lambda c, bs: c/bs, coords, self.bin_size)
        from math import floor
        b = tuple(map(lambda c: int(floor(c)), bc))
        if b in self.bins:
            self.bins[b].append((coords, object))
        else:
            self.bins[b] = [(coords, object)]

    # -------------------------------------------------------------------------
    #
    def close_objects(self, coords, range):

        bc = map(lambda c, bs: c/bs, coords, self.bin_size)
        br = map(lambda r, bs: r/bs, range, self.bin_size)
        cobjects = {}
        cbins = self.close_bins(bc, br)
        for b in cbins:
            if b in self.bins:
                for c,o in self.bins[b]:
                    if self.are_coordinates_close(c, coords, range):
                        cobjects[o] = 1
        clist = cobjects.keys()
        return clist

    # -------------------------------------------------------------------------
    #
    def close_bins(self, bc, br):

        from math import floor
        rs = map(lambda c, r: range(int(floor(c-r)), int(floor(c+r)) + 1),
                 bc, br)
        cbins = outer_product(rs)
        return cbins

    # -------------------------------------------------------------------------
    #
    def are_coordinates_close(self, c, coords, dist):

        for k in range(len(c)):
            if abs(c[k] - coords[k]) > dist[k]:
                return False
        return True
        
# -----------------------------------------------------------------------------
#
def outer_product(sets):

    if len(sets) == 0:
        op = []
    elif len(sets) == 1:
        op = map(lambda c: (c,), sets[0])
    else:
        op = []
        op1 = outer_product(sets[1:])
        for c in sets[0]:
            for cr in op1:
                op.append((c,) + cr)
    return op
