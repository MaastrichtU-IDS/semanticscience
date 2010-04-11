#ifndef Chimera_BoundSphere_h
# define Chimera_BoundSphere_h

# include <stdio.h>
# include <math.h>
# include "sphere.h"
# include "MinSphere.h"

namespace chimera {

#ifndef WrapPy

template <class Iter> bool
find_minimum_bounding_sphere(Iter first, Iter last, /*OUT*/ Sphere *sphere)
{
	// find the minimum volume bounding sphere
	if (first == last)
		return false;

	Wml::Sphere3 s;
	Wml::MinSphere3(first, last, s);
	sphere->setCenter(s.Center());
	sphere->setRadius(s.Radius());
	return true;
}

template <class Iter> bool
find_bounding_sphere(Iter first, Iter last, /*OUT*/ Sphere *sphere)
{
	// This bounding sphere shares the same center as the
	// axis-aligned bounding box.
	if (first == last)
		return false;

	typedef otf::Geom3d::Real Real;
	typedef otf::Geom3d::Point Point;
	typedef otf::Geom3d::BBox BBox;

	// find AABB to compute center
	BBox box;
	box.llf = box.urb = *first;
	for (Iter i = first + 1; i != last; ++i) {
		const Point &pt = *i;
		for (int j = 0; j != 3; ++j)
			if (box.llf[j] > pt[j])
				box.llf[j] = pt[j];
			else if (box.urb[j] < pt[j])
				box.urb[j] = pt[j];
	}
	sphere->setCenter(otf::lerp(box.llf, box.urb, .5));

	// find farthest point from center to use for the radius
	Real radius_sq = 0;
	for (Iter i = first; i != last; ++i) {
		const Point &pt = *i;
		Real dist_sq = (pt - sphere->center()).sqlength();
		if (dist_sq > radius_sq)
			radius_sq = dist_sq;
	}
	sphere->setRadiusSq(radius_sq);
	return true;
}

#else
extern bool find_bounding_sphere(const std::vector<Point> &pts, /*OUT*/ Sphere *sphere);
extern bool find_minimum_bounding_sphere(const std::vector<Point> &pts, /*OUT*/ Sphere *sphere);
#endif /* ifndef WrapPy */

} // namespace chimera

#endif
