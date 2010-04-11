#ifndef Chimera_TmplBond_h
# define Chimera_TmplBond_h

# if defined(_MSC_VER) && (_MSC_VER >= 1020)
#  pragma once
# endif

# include <otf/WrapPy2.h>
# include <otf/Geom3d.h>
# include "_chimera_config.h"

namespace otf {
class TmplBond;
}

namespace chimera {

class CHIMERA_IMEX TmplBond : public otf::WrapPyObj
{
	// DON'T CACHE
	TmplBond(const TmplBond&);		// disable
	TmplBond& operator=(const TmplBond&);	// disable
private:
	const otf::TmplBond *tmplBond_;
# ifdef WrapPy
	TmplBond();
# endif
public:
# ifndef WrapPy
	TmplBond(const otf::TmplBond *b);

	virtual PyObject* wpyNew() const;
# endif
	virtual ~TmplBond();
	long hash() const;
	bool operator==(const TmplBond &b) const;
	otf::Geom3d::Real length() const;
	otf::Geom3d::Real sqlength() const;
};

} // namespace chimera

#endif
