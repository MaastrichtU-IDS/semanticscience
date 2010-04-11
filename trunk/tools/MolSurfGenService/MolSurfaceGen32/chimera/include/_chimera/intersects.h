#ifndef Chimera_intersects_h
# define	Chimera_intersects_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include "Plane.h"
# include "sphere.h"

namespace chimera {

using otf::Geom3d::BBox;

extern bool intersects(const Plane &p, const BBox &box);
extern bool intersects(const Plane &p, const Sphere &s);

} // namespace chimera

#endif
