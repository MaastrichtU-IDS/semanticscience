#ifndef chimera_Root_h
#define	chimera_Root_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <otf/WrapPy2.h>
#include "_chimera_config.h"
#include <functional>
namespace chimera { class Atom; }

namespace chimera {

class CHIMERA_IMEX Root: public otf::WrapPyObj  {
	Atom	*Atom_;
public:
		virtual ~Root();
	Atom	*atom() const;
public:
	struct GraphSize { int numBonds; int numAtoms; };
	int		bondIndex;
	int		atomIndex;
	GraphSize	size;
	Root		*superRoot;
private:
	Root();  // private constructor
	Root(const Root&);		// disable
	Root& operator=(const Root&);	// disable
	
	friend class Molecule;
public:
	virtual PyObject* wpyNew() const;
public:
};

} // namespace chimera

#endif
