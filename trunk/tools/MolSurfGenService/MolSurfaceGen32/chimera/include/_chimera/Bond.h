#ifndef chimera_Bond_h
#define	chimera_Bond_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <otf/Array.h>
#include "ringfwddecl.h"
#include <otf/molkit/TAexcept.h>
#include <otf/Geom3d.h>
#include "resDistConn.h"
#include <otf/WrapPy2.h>
#include "_chimera_config.h"
#include "Selectable.h"
#include "Color.h"
#include "TrackChanges.h"
#include <functional>
namespace chimera { class Atom; }

namespace chimera {
class Atom;
class Molecule;

class CHIMERA_IMEX Bond: public Selectable  {
	friend class Atom;
	friend class Molecule;
	void	operator=(const Bond &);	// disable
		Bond(const Bond &);	// disable
		virtual ~Bond();
	otf::Array<Atom *, 2>	Atoms_;
public:
	typedef otf::Array<Atom *, 2> Atoms;
	inline const Atoms	&atoms() const;
	Atom	*findAtom(int) const;
public:
public:
	inline Atom		*otherAtom(const Atom *a) const;
	inline bool		contains(const Atom *) const;
private:
	void		basicInitWithAtoms(Atom *, Atom *);
public:
	inline Atom		*getBreakPoint() const;
	void		setBreakPoint(Atom *a);
	inline void		clearBreakPoint();

	inline Bond		*traverseFrom(bool ignoreBreakPoints) const;
private:
	Atom		*mg_BreakPoint;
          // NULL if this edge can be crossed during traversals,
          // otherwise set to one of the endpoints (that endpoint
          // will not consider this edge during a traversal)
	
	mutable Bond	*mg_From;
	void			mg_bondInit(Atom *, Atom*);
public:
	typedef std::vector<const Ring *> Rings;
	const Rings &rings(bool crossResidues = false, unsigned int allSizeThreshold = 0) const;
private:
	Rings mg_Rings;
public:
	inline otf::Geom3d::Real
			length() const;
	inline otf::Geom3d::Real
			sqlength() const;
public:
public:
	bool	registerField(otf::Symbol field, int value);
	bool	registerField(otf::Symbol field, double value);
	bool	registerField(otf::Symbol field, const std::string &value);
	bool	getRegField(otf::Symbol field, int *value) const;
	bool	getRegField(otf::Symbol field, double *value) const;
	bool	getRegField(otf::Symbol field, std::string *value) const;
public:
	inline Molecule	*molecule() const;
	inline const Color	*color() const;
	void		setColor(/*NULL_OK*/ const Color *);
	enum DrawMode { Wire, Stick };
	inline DrawMode	drawMode() const;
	void		setDrawMode(DrawMode);
	enum DisplayMode { Never, Always, Smart };
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
	Point		labelCoord() const;
	Vector		currentLabelOffset() const;
	void		setLabelColor(/*NULL_OK*/ const Color *);
	std::string	oslIdent(Selector start = SelDefault,
					Selector end = SelDefault) const;
	Selectable::Selectables oslChildren() const;
	Selectable::Selectables oslParents() const;
	bool		oslTestAbbr(OSLAbbreviation *a) const;
	inline Selector	oslLevel() const;
	static const Selector	selLevel = SelBond;
	// return vector of Rings (instead of Ring *) to make wrappy happy
	std::vector<Ring>	minimumRings(bool crossResidues = false) const;
	std::vector<Ring>	allRings(bool crossResidues = false, int sizeThreshold = 0) const;

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
	struct Reason: public NotifierReason {
                Reason(const char *r): NotifierReason(r) {}
        };
	static Reason		COLOR_CHANGED;
	static Reason		DRAW_MODE_CHANGED;
	static Reason		DISPLAY_CHANGED;
	static Reason		RADIUS_CHANGED;
	static Reason		HALFBOND_CHANGED;
	static Reason		LABEL_CHANGED;
	static Reason		LABEL_OFFSET_CHANGED;
	static Reason		LABEL_COLOR_CHANGED;
private:
	Bond(Molecule *, Atom *a0, Atom *a1);
	Bond(Molecule *, Atom *a[2]);
};

} // namespace chimera

#endif
