#ifndef chimera_PseudoBondMgr_h
#define	chimera_PseudoBondMgr_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <map>
#include <vector>
#include <otf/Symbol.h>
#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <otf/WrapPy2.h>
#include "_chimera_config.h"
namespace chimera { class CoordSet; }
#include "PseudoBondGroup.h"
#include "ChainTrace.h"

namespace chimera {

class CHIMERA_IMEX PseudoBondMgr: public otf::WrapPyObj  {
	CoordSet	*CoordSet_;
	std::map<otf::Symbol, PseudoBondGroup *>	PseudoBondGroups_;
public:
		virtual ~PseudoBondMgr();
	CoordSet	*coordSet() const;
	PseudoBondGroup	*newPseudoBondGroup(otf::Symbol category);
	ChainTrace	*newChainTrace(otf::Symbol category);
	void	deletePseudoBondGroup(PseudoBondGroup *element);
	typedef std::vector<PseudoBondGroup *> PseudoBondGroups;
	inline PseudoBondGroups pseudoBondGroups() const;
	typedef std::map<otf::Symbol, PseudoBondGroup *> PseudoBondGroupsMap;
	inline const PseudoBondGroupsMap	&pseudoBondGroupsMap() const;
	typedef std::vector<otf::Symbol> PseudoBondGroupKeys;
	inline PseudoBondGroupKeys	categories() const;
	PseudoBondGroup	*findPseudoBondGroup(otf::Symbol) const;
public:
	// a single PseudoBondMgr manages all PseudoBonds for Molecules
	// with single coordinate sets (i.e. non-trajectories).  This
	// singleton manager is accessed with the mgr() class member
	// function, below
	static PseudoBondMgr 	*mgr(); // singleton instance of PseudoBondMgr
private:
	static PseudoBondMgr *_mgr;
public:
	virtual PyObject* wpyNew() const;
private:
	PseudoBondMgr();
	PseudoBondMgr(const PseudoBondMgr&);		// disable
	PseudoBondMgr& operator=(const PseudoBondMgr&);	// disable
public:
	PseudoBondMgr(CoordSet *);
};

} // namespace chimera

#endif
