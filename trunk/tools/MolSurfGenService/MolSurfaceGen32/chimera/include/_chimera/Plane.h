#ifndef Chimera_Plane_h
# define Chimera_Plane_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/Geom3d.h>
# include "_chimera_config.h"

namespace chimera {

using otf::Geom3d::Real;
using otf::Geom3d::Point;
using otf::Geom3d::Vector;
using otf::Geom3d::Xform;

class CHIMERA_IMEX Plane
{
	// The plane normal points in the direction that is visible,
	// i.e., not clipped.
	// IMPLICIT COPY CONSTRUCTOR
public:
	Plane();	// degenerate with zero normal
	Plane(const Point &origin, const Vector &normal);
#ifndef WrapPy
	template <class pointIterator>
			Plane(pointIterator ptStart, pointIterator ptStop);
#else
	Plane(const std::vector<Point*> &points);
#endif

	const Point	&origin() const;
	void		setOrigin(const Point &origin);
	const Vector	&normal() const;
	void		setNormal(const Vector &normal);
	Real		offset() const;

	Real		distance(const Point &pt) const;
	Point		nearest(const Point &pt) const;
	bool		intersection(const Plane &p, /*OUT*/ Point *pt,
						/*OUT*/ Vector *v) const;
	void		equation(/*OUT*/ Real abcd[4]) const;

	void		xformNormal(const Xform &xf);
	void		moveOrigin(Real distance);
	void		applyXform(const Xform &xf);
private:
	void		computeOffset();
	Vector	n;
	Point	o;
	Real	offset_;
};

#ifndef WrapPy

inline const Vector &
Plane::normal() const
{
	return n;
}

inline const Point &
Plane::origin() const
{
	return o;
}

inline Real
Plane::offset() const
{
	return offset_;
}

template <class pointIterator>
Plane::Plane(pointIterator ptStart, pointIterator ptStop)
{
	if (std::distance(ptStart, ptStop) < 3)
		throw std::runtime_error("need at least 3 points");

	//
	// Constructor when given a set of points
	// Implementation of Newell's algorithm
	// See Foley, van Dam, Feiner, and Hughes (pp. 476-477)
	// Implementation copied from Filippo Tampieri from Graphics Gems
	//

	otf::Geom3d::PointAdd pa;
	Real A = 0, B = 0, C = 0;
	for (pointIterator i = ptStart; i != ptStop; ++i) {
		pointIterator j = i;
		++j;
		if (j == ptStop)
			j = ptStart;
		const Point &u = *i;
		const Point &v = *j;
		A += (u.y() - v.y()) * (u.z() + v.z());
		B += (u.z() - v.z()) * (u.x() + v.x());
		C += (u.x() - v.x()) * (u.y() + v.y());
		pa.add(u);
	}
	n = Vector(A, B, C);
	n.normalize();
	o = pa.point();
	computeOffset();
}

#endif /* ndef WrapPy */

} // namespace chimera

#endif
