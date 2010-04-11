#ifndef RESDISTCONN_H
#define RESDISTCONN_H

#include <set>
#include <otf/Geom3d.h>

namespace chimera {

class Residue;
class Atom;

void connectResidueByDistance(Residue *, std::set<Atom *> *,
	otf::Geom3d::Real bondRatio = 1, otf::Geom3d::Real bondTolerance = 0.4);

otf::Geom3d::Real bondedDist(Atom *a, Atom *b,
	otf::Geom3d::Real bondRatio = 1, otf::Geom3d::Real bondTolerance = 0.4);

}

#endif
