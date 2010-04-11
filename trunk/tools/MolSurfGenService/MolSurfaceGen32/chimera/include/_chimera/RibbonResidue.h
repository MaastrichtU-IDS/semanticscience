#ifndef chimera_RibbonResidue_h
#define	chimera_RibbonResidue_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <functional>

namespace chimera {

class CHIMERA_IMEX RibbonResidue {
public:
		~RibbonResidue();
public:
private:
	RibbonResidue& operator=(const RibbonResidue&);	// disable
	//RibbonResidue(const RibbonResidue& r); // allow in std::map by value
private:
public:
	Atom			*guide;
	Atom			*plane;
	Residue			*prev;
	Residue			*next;
	otf::Geom3d::Vector	curvatureProjection;
	otf::Geom3d::Vector	localCurvature;
	otf::Geom3d::Vector	normal;
	otf::Geom3d::Vector	binormal;
public:
	RibbonResidue();
};

} // namespace chimera

#endif
