#ifndef chimera_RibbonData_h
#define	chimera_RibbonData_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <otf/WrapPy2.h>
#include <otf/Geom3d.h>
#include <functional>

namespace chimera {

class CHIMERA_IMEX RibbonData: public otf::WrapPyObj  {
public:
		~RibbonData();
public:
	friend class Residue;
	friend class Atom;
	inline const otf::Geom3d::Point &
			center() const;
	inline void		setCenter(const otf::Geom3d::Point &c);
	inline const otf::Geom3d::Vector &
			normal() const;
	inline void		setNormal(const otf::Geom3d::Vector &n);
	inline const otf::Geom3d::Vector &
			binormal() const;
	inline void		setBinormal(const otf::Geom3d::Vector &bn);
	inline void		flipNormals();
	inline bool		flipped() const;
	inline RibbonData	*prev() const;
	inline void		setPrev(/*NULL_OK*/ RibbonData *p);
	inline RibbonData	*next() const;
	inline void		setNext(/*NULL_OK*/ RibbonData *n);
	inline Residue		*prevResidue() const;
	inline void		setPrevResidue(/*NULL_OK*/ Residue *r);
	inline Residue		*nextResidue() const;
	inline void		setNextResidue(/*NULL_OK*/ Residue *r);
	inline Atom		*guide() const;
	inline void		setGuide(/*NULL_OK*/ Atom *a);

	virtual PyObject* wpyNew() const;
private:
	RibbonData(const RibbonData&);			// disable
	RibbonData& operator=(const RibbonData&);	// disable
private:
	otf::Geom3d::Point	center_;
	otf::Geom3d::Vector	normal_;
	otf::Geom3d::Vector	binormal_;
	RibbonData		*next_;
	RibbonData		*prev_;
	Residue			*nextResidue_;
	Residue			*prevResidue_;
	Atom			*guide_;
	bool			flipped_;
public:
	RibbonData();
};

} // namespace chimera

#endif
