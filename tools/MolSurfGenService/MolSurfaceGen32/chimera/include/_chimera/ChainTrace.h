#ifndef chimera_ChainTrace_h
#define	chimera_ChainTrace_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <functional>

namespace chimera {

class PseudoBondMgr;

class CHIMERA_IMEX ChainTrace: public PseudoBondGroup  {
	friend class PseudoBondMgr;
public:
		virtual ~ChainTrace();
public:
	inline bool		trackMolecule() const;
	void		setTrackMolecule(bool);

	virtual PyObject* wpyNew() const;
private:
	bool		trackMolecule_;
	ChainTrace(PseudoBondMgr *, otf::Symbol category);
};

} // namespace chimera

#endif
