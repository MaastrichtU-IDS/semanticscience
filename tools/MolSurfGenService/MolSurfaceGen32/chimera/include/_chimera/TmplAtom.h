#ifndef Chimera_TmplAtom_h
# define Chimera_TmplAtom_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Symbol.h>
# include <otf/WrapPySymbol.h>
# include <otf/molkit/Element.h>
# include "_chimera_config.h"
# include <otf/Geom3d.h>

namespace otf {
class TmplAtom;
}

namespace chimera {

class TmplBond;
typedef otf::Geom3d::Point TmplCoord;

class CHIMERA_IMEX TmplAtom : public otf::WrapPyObj
{
	// DON'T CACHE
	TmplAtom(const TmplAtom&);		// disable
	TmplAtom& operator=(const TmplAtom&);	// disable
private:
	const otf::TmplAtom *tmplAtom_;
# ifdef WrapPy
			TmplAtom();
# endif
public:
# ifndef WrapPy
	TmplAtom(const otf::TmplAtom *a);

	virtual PyObject* wpyNew() const;
# endif
	virtual ~TmplAtom();
	long hash() const;
	bool operator==(const TmplAtom &a) const;
	typedef std::map<TmplAtom*, TmplBond *, std::less<TmplAtom*> > BondsMap;
	// ATTRIBUTE: bondsMap
	const BondsMap	&bondsMap() const;
	const TmplCoord	&coord() const;
	// ATTRIBUTE: name
	otf::Symbol	name() const;
	// ATTRIBUTE: element
	otf::Element	element() const;
	// ATTRIBUTE: idatmType
	otf::Symbol	idatmType() const;
private:
	mutable BondsMap *bonds_;
	mutable TmplCoord *coord_;
};

} // namespace chimera

#endif
