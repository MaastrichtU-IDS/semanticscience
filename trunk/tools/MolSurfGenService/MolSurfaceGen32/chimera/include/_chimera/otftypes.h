#ifndef Chimera_otftypes_h
# define Chimera_otftypes_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/Geom3d.h>
# include <otf/molkit/Element.h>
# include <otf/molkit/MolResId.h>
# include <otf/PathFinder.h>

namespace chimera {

using otf::Geom3d::Point;
using otf::Geom3d::Vector;
using otf::Geom3d::BBox;
using otf::Geom3d::Xform;
using otf::Geom3d::Real;
using otf::Element;
using otf::MolResId;
using otf::PathFinder;

}

#endif
