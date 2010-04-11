#ifndef chimera_PseudoBond_h
#define	chimera_PseudoBond_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <otf/Array.h>
#include <otf/Geom3d.h>
#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <otf/WrapPy2.h>
#include "_chimera_config.h"
#include "Selectable.h"
#include "Color.h"
#include "Bond.h"
#include "TrackChanges.h"
#include <functional>
namespace chimera { class Atom; }
namespace chimera { class PseudoBondGroup; }

namespace chimera {
class Atom;
class PseudoBondGroup;

class CHIMERA_IMEX PseudoBond: public Selectable  {
	friend class Atom;
	friend class PseudoBondGroup;
	void	operator=(const PseudoBond &);	// disable
		PseudoBond(const PseudoBond &);	// disable
		virtual ~PseudoBond();
	otf::Array<Atom *, 2>	Atoms_;
	PseudoBondGroup	*PseudoBondGroup_;
public:
	typedef otf::Array<Atom *, 2> Atoms;
	inline const Atoms	&atoms() const;
	Atom	*findAtom(int) const;
	PseudoBondGroup	*pseudoBondGroup() const;
public:
	inline Atom		*otherAtom(const Atom *a) const;
	inline bool		contains(const Atom *) const;
private:
	void		basicInitWithAtoms(Atom *, Atom *);
public:
        inline otf::Symbol     category(void) const;
	inline otf::Geom3d::Real
			length() const;
	inline otf::Geom3d::Real
			sqlength() const;
public:
	typedef Bond::DrawMode DrawMode;
	inline const Color	*color() const;
	void		setColor(/*NULL_OK*/ const Color *);
	inline DrawMode	drawMode() const;
	void		setDrawMode(DrawMode);
	typedef Bond::DisplayMode DisplayMode;
	inline DisplayMode	display() const;
	void		setDisplay(DisplayMode);
	bool		shown() const;
	inline float		radius() const;
	void		setRadius(float);
	inline bool		halfbond() const;
	void		setHalfbond(bool);
	inline const std::string &
			label() const;
	void		setLabel(const std::string &s);
	inline const Vector	&labelOffset() const;
	void		setLabelOffset(const Vector &offset);
	inline const Color	*labelColor() const;
	void		setLabelColor(/*NULL_OK*/ const Color *);
	Point		labelCoord() const;
	Vector		currentLabelOffset() const;
	std::string	oslIdent(Selector start = SelDefault,
					Selector end = SelDefault) const;
	Selectable::Selectables oslChildren() const;
	Selectable::Selectables oslParents() const;
	bool		oslTestAbbr(OSLAbbreviation *a) const;
	inline Selector	oslLevel() const;
	static const Selector	selLevel = SelBond;

	void		reuse(Atom *a0, Atom *A1);

	virtual PyObject* wpyNew() const;
private:
	const Color	*color_;
	DrawMode	drawMode_;
	DisplayMode	display_;
	bool		halfbond_;
	float		radius_;
	std::string	label_;
	Vector		labelOffset_;
	const Color	*labelColor_;
	static TrackChanges::Changes *const
			changes;
	inline void		setMajorChange();
public:
	virtual void	wpyAssociate(PyObject* o) const;

	void		trackReason(const NotifierReason &reason) const;
	static Bond::Reason PSEUDOBOND_REUSED;
private:
	PseudoBond(PseudoBondGroup *, Atom *a1, Atom *a2);
};

} // namespace chimera

#endif
