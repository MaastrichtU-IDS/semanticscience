#
# Copyright 2000 by Peter McCluskey (pcm@rahul.net).
# You may do anything you want with it, provided this notice is kept intact.
#

_undocumented = 1

"""
tesselate(num_points)

Returns a list of num_points points spread fairly evenly over the unit sphere.
The points are 3-tuples of floats.
num_points should be 2**(2*N) + 2, where N > 1.

The C code in MMTK_surfacemodule.c does the same thing faster, so this
code should normally be used only by people who can't compile C code.
"""

from math import sqrt, atan2, pi

def _normalize(x, y, z):
    length = sqrt(x*x + y*y + z*z)
    return (x/length, y/length, z/length)

def tess_triangle(pts, npts, r, pt_dict):
    v0 = pts[0]
    v1 = pts[1]
    v2 = pts[2]
    new_pt0 = _normalize(v0[0] + v1[0], v0[1] + v1[1], v0[2] + v1[2])
    new_pt1 = _normalize(v1[0] + v2[0], v1[1] + v2[1], v1[2] + v2[2])
    new_pt2 = _normalize(v2[0] + v0[0], v2[1] + v0[1], v2[2] + v0[2])
    n4 = npts/4
    if n4 <= 3:
                # other 2 points in pts will be created as pts[0] of
                # another triangle, except for top level points
        for p in (pts[0], new_pt0, new_pt1, new_pt2):
            key = '%.6f,%.6f,%.6f' % p
            if not pt_dict.has_key(key):
                pt_dict[key] = p
                r.append(p)
    else:
        tess_triangle((pts[0], new_pt0, new_pt2), n4, r, pt_dict)
        tess_triangle((new_pt0, pts[1], new_pt1), n4, r, pt_dict)
        tess_triangle((new_pt0, new_pt1, new_pt2), n4, r, pt_dict)
        tess_triangle((new_pt1, pts[2], new_pt2), n4, r, pt_dict)

def tesselate(num_points):
    north = (0.0, 0.0, 1.0)
    south = (0.0, 0.0, -1.0)
    noon  = (1.0, 0.0, 0.0)
    night = (-1.0, 0.0, 0.0)
    dawn  = (0.0, 1.0, 0.0)
    dusk  = (0.0, -1.0, 0.0)
    npts = int((num_points - 2)/4)

    pt_dict = {}
    r = []
    for p in [north, south, noon, night, dusk, dawn]:
        key = '%.6f,%.6f,%.6f' % p
        pt_dict[key] = p
        r.append(p)
    tess_triangle((north, dawn, noon), npts, r, pt_dict)
    tess_triangle((north, noon, dusk), npts, r, pt_dict) 
    tess_triangle((north, dusk, night), npts, r, pt_dict) 
    tess_triangle((north, night, dawn), npts, r, pt_dict) 
    tess_triangle((south, dawn, night), npts, r, pt_dict) 
    tess_triangle((south, night, dusk), npts, r, pt_dict) 
    tess_triangle((south, dusk, noon), npts, r, pt_dict) 
    tess_triangle((south, noon, dawn), npts, r, pt_dict)
    return r

if __name__ == '__main__':
    r = tesselate(1026)
    print len(r), 'points'
    if len(r) < 1000:
        for pt in r:
            print '%6.1f %6.1f %6.1f' % (pt[0], pt[1], pt[2])

