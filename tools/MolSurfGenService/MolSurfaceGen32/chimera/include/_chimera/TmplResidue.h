#ifndef Chimera_TmplResidue_h
# define Chimera_TmplResidue_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Symbol.h>
# include <otf/WrapPySymbol.h>
# include "_chimera_config.h"
# include "TmplAtom.h"

namespace otf {
class TmplResidue;
}

namespace chimera {

// can't use otf::TmplResidue directly because its copy constructor
// is private, which screws up wrappy
class CHIMERA_IMEX TmplResidue : public otf::WrapPyObj
{
	// DON'T CACHE
	TmplResidue(const TmplResidue&);		// disable
	TmplResidue& operator=(const TmplResidue&);	// disable
	const otf::TmplResidue *tmplResidue_;
# ifdef WrapPy
	TmplResidue();
# endif
public:
# ifndef WrapPy
	TmplResidue(const otf::TmplResidue *t);

	virtual PyObject* wpyNew() const;
# endif
	virtual ~TmplResidue();
	long hash() const;
	bool operator==(const TmplResidue &r) const
				{ return r.tmplResidue_ == tmplResidue_; }

	typedef std::map<otf::Symbol, TmplAtom *,
					std::less<otf::Symbol> > AtomsMap;
	// ATTRIBUTE: atomsMap
	const AtomsMap &atomsMap() const;
private:
	mutable AtomsMap *atoms_;
};

} // namespace chimera

#endif
