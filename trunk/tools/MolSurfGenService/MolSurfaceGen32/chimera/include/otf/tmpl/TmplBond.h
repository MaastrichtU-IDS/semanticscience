#ifndef otf_TmplBond_h
#define	otf_TmplBond_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <otf/Array.h>
#include <otf/Geom3d.h>
#include <otf/molkit/TAexcept.h>
#include <otf/config.h>
#include <functional>
namespace otf { class TmplAtom; }

namespace otf {
class TmplAtom;
class TmplMolecule;

class OTF_IMEX TmplBond {
	friend class TmplAtom;
	friend class TmplMolecule;
	void	operator=(const TmplBond &);	// disable
		TmplBond(const TmplBond &);	// disable
		~TmplBond();
	otf::Array<TmplAtom *, 2>	Atoms_;
public:
	typedef otf::Array<TmplAtom *, 2> Atoms;
	inline const Atoms	&atoms() const;
	TmplAtom	*findAtom(int) const;
public:
	inline TmplAtom		*otherAtom(const TmplAtom *a) const;
public:
	inline otf::Geom3d::Real
			length() const;
	inline otf::Geom3d::Real
			sqlength() const;
private:
	TmplBond(TmplMolecule *, TmplAtom *a0, TmplAtom *a1);
	TmplBond(TmplMolecule *, TmplAtom *a[2]);
};

} // namespace otf

#endif
