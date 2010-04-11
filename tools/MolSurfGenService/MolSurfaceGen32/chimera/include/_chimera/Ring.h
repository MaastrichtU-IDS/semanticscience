#ifndef chimera_Ring_h
#define	chimera_Ring_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <set>
#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <functional>
namespace chimera { class Bond; }

namespace chimera {

class CHIMERA_IMEX Ring {
	std::set<Bond *>	Bonds_;
public:
		~Ring();
	void	addBond(Bond *element);
	void	removeBond(Bond *element);
	typedef std::set<Bond *> Bonds;
	inline const Bonds	&bonds() const;
public:
	bool operator<(const Ring &) const;
	bool operator==(const Ring &) const;

	// Only bonds, not atoms, are stored "naturally" in the ring.
	// Nonetheless, it is convenient to get the atoms easily...
	typedef std::set<Atom *> Atoms;
	const Atoms &atoms() const;

	// atoms()/bonds() don't return their values in ring order;
	// these do...
	const std::vector<Bond *> orderedBonds() const;
	const std::vector<Atom *> orderedAtoms() const;

	// determine plane equation Ax+By+Cz+D=0 using algorithm in
	// Foley and van Damm 2nd edition, pp. 476-477
	// avgErr is average distance from plane to ring vertex,
	// maxErr is the largest such distance
	void planarity(double planeCoeffs[4], double *avgErr = 0,
	  double *maxErr = 0) const;
private:
	mutable Atoms Atoms_;

	Bonds::iterator mg_containsExactlyOne(Bonds *) const;
	friend class Molecule;
	// would like to be a friend to just Molecule::rings(),
	// but there doesn't seem to be a genlib incantation for
	// getting the include files in the right order
public:
	bool aromatic() const;
public:
	long hash() const;
public:
	Ring(std::set<Bond *> &ringBonds);
};

} // namespace chimera

#endif
