#ifndef chimera_Atom_h
#define	chimera_Atom_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <map>
#include <vector>
#include <vector>
#include <algorithm>
#include "ringfwddecl.h"
#include <otf/Symbol.h>
#include <otf/molkit/Element.h>
#include <otf/Symbol.h>
#include <string>
#include <map>
#include <otf/molkit/TAexcept.h>
#include "CoordSet.h"
#include "resDistConn.h"
#include <otf/WrapPy2.h>
#include "_chimera_config.h"
#include "Selectable.h"
#include "Color.h"
#include "TrackChanges.h"
#include "RibbonSpline.h"
#include <functional>
namespace chimera { class Bond; }
namespace chimera { class Molecule; }
namespace chimera { class PseudoBond; }
namespace chimera { class Residue; }

namespace chimera {
class Molecule;
class Residue;

class CHIMERA_IMEX Atom: public Selectable  {
	friend class Molecule;
	friend class Residue;
	void	operator=(const Atom &);	// disable
		Atom(const Atom &);	// disable
		virtual ~Atom();
	std::map<Atom*, Bond *>	Bonds_;
	Molecule	*Molecule_;
	std::vector<PseudoBond *>	PseudoBonds_;
	Residue	*Residue_;
public:
	void	addBond(Bond *element);
	void	removeBond(Bond *element);
	typedef std::vector<Bond *> Bonds;
	inline Bonds bonds() const;
	typedef std::map<Atom*, Bond *> BondsMap;
	inline const BondsMap	&bondsMap() const;
	typedef std::vector<Atom*> BondKeys;
	inline BondKeys	neighbors() const;
	Bond	*findBond(Atom*) const;
	Molecule	*molecule() const;
	void	addPseudoBond(PseudoBond *element);
	void	removePseudoBond(PseudoBond *element);
	typedef std::vector<PseudoBond *> PseudoBonds;
	inline const PseudoBonds	&pseudoBonds() const;
	PseudoBond	*findPseudoBond(int) const;
	Residue	*residue() const;
public:
public:
	inline Bond		*connectsTo(Atom *a) const;
public:
	inline Atom		*rootAtom(bool ignoreBreakPoints) const;
	inline Atom		*traverseFrom(bool ignoreBreakPoints) const;
private:
	mutable Atom	*mg_Root, *mg_From;
          // Root = corresponding root for traversal _not_ ignoring breakpoints
          // From = previous node in that traversal

	friend class Bond;
public:
	// Is this atom connected to "otherAtom" with a Bond/PseudoBond
	// of type "category" (possibly considering the current trajectory
	// frame)?
	bool	associated(const Atom *otherAtom, otf::Symbol category) const;

	// How many Bonds/PseudoBonds of type "category" link this atom
	// to "otherAtom" (if specified, otherwise any atom), given the
	// trajectory frame (if applicable)?
	std::vector<PseudoBond *>	associations(otf::Symbol category,
					  const Atom *otherAtom = NULL) const;
public:
	typedef std::vector<const Ring *> Rings;
	const Rings &rings(bool crossResidues = false, unsigned int allSizeThreshold = 0) const;
private:
	Rings mg_Rings;
public:
	inline char	altLoc() const;
	inline void	setAltLoc(char al);

	std::vector<Atom *>	allLocations() const;
	std::vector<Bond *>	primaryBonds() const;
	std::vector<Atom *>	primaryNeighbors() const;
private:
	char	alternateLocation;
public:
	inline otf::Symbol	name() const;
	void		setName(otf::Symbol s);
	inline otf::Element	element() const;
	void		setElement(otf::Element e);
	// Atom_idatm overrides setElement, so using "old-fashioned" inlining
	// to work around the fact that wrappy isn't smart enough not to
	// elide the following implementations
	void		setElement(int e) { setElement(otf::Element(e)); };
	void		setElement(const char *e) { setElement(otf::Element(e)); };


private:
	otf::Symbol	name_;
	otf::Element	element_;
public:
	inline otf::Symbol	idatmType() const;
	inline void		setIdatmType(otf::Symbol);
	inline void		setIdatmType(const char *);
	inline void		setIdatmType(const std::string &);
	inline bool		idatmIsExplicit() const;
	enum IdatmGeometry {
		Ion=0, Single=1, Linear=2, Planar=3, Tetrahedral=4
	};
	struct IdatmInfo {
		IdatmGeometry	geometry;
		int		substituents;
		std::string	description;
	};
	typedef std::map<std::string, IdatmInfo> IdatmInfoMap;
	static const IdatmInfoMap &getIdatmInfoMap();
private:
	otf::Symbol		explicitIdatmType_;
	mutable otf::Symbol	computedIdatmType_;
	inline void			setComputedIdatmType(const char *);
	static IdatmInfoMap	*_idatmMap;
	static struct IdatmTable {
		const char *idatmType;
		IdatmInfo info;
	} idatmInfos[];
public:
	static const unsigned int UNASSIGNED = ~0u;
	inline unsigned int	coordIndex() const;
	const Coord	&coord() const;
	const Coord	&coord(const CoordSet *cs) const;
	void		setCoord(const Coord &c);
	void		setCoord(const Coord &c, CoordSet *cs);
private:
	mutable unsigned int
		index_;
	int	newCoord(const Coord &c) const;
public:
public:
	bool	registerField(otf::Symbol field, int value);
	bool	registerField(otf::Symbol field, double value);
	bool	registerField(otf::Symbol field, const std::string &value);
	bool	getRegField(otf::Symbol field, int *value) const;
	bool	getRegField(otf::Symbol field, double *value) const;
	bool	getRegField(otf::Symbol field, std::string *value) const;
public:
	enum DrawMode { Dot, Sphere, EndCap, Ball };
	inline const Color	*color() const;
	void		setColor(/*NULL_OK*/ const Color *);
	inline DrawMode	drawMode() const;
	void		setDrawMode(DrawMode);
	inline bool		display() const;
	void		setDisplay(bool);
	inline bool		shown() const;
	inline bool		hide() const;
	void		setHide(bool);
	float		radius() const;
	void		setRadius(float);
	inline bool		vdw() const;
	void		setVdw(bool);
	float		defaultRadius() const;
	void		revertDefaultRadius();
	int		coordination(int valueIfUnknown = 0) const;
	void		clearVdwPoints();
	typedef std::pair<Point, Vector> VDWPoint;
	const std::vector<VDWPoint>	&vdwPoints();
	inline const Color	*vdwColor() const;
	void		setVdwColor(/*NULL_OK*/ const Color *color);
	inline const std::string &
			label() const;
	void		setLabel(const std::string &s);
	inline const Vector	&labelOffset() const;
	void		setLabelOffset(const Vector &offset);
	const Point	&labelCoord() const;
	Vector		currentLabelOffset() const;
	inline const Color	*labelColor() const;
	void		setLabelColor(/*NULL_OK*/ const Color *color);
	inline const Color	*surfaceColor() const;
	void		setSurfaceColor(/*NULL_OK*/ const Color *color);
	inline float		surfaceOpacity() const;
	void		setSurfaceOpacity(float opacity);
	inline bool		surfaceDisplay() const;
	void		setSurfaceDisplay(bool display);
	inline otf::Symbol	surfaceCategory() const;
	void		setSurfaceCategory(otf::Symbol category);
	std::string	oslIdent(Selector start = SelDefault, Selector end = SelDefault) const;
	Selectable::Selectables oslChildren() const;
	Selectable::Selectables oslParents() const;
	bool		oslTestAbbr(OSLAbbreviation *a) const;
	inline Selector	oslLevel() const;
	static const Selector	selLevel = SelAtom;
	Coord		xformCoord() const;
	Coord		xformCoord(const CoordSet *cs) const;
	// return vector of Rings (instead of Ring *) to make wrappy happy
	std::vector<Ring>	minimumRings(bool crossResidues = false) const;
	std::vector<Ring>	allRings(bool crossResidues = false, int sizeThreshold = 0) const;

	virtual PyObject* wpyNew() const;
private:
	friend class	PseudoBondGroup;
	const Color	*color_;
	DrawMode	drawMode_;
	bool		display_;
	bool		hide_;
	bool		vdw_;
	bool		vdwValid_;
	bool		surfaceDisplay_;
	std::vector<VDWPoint>	vdwPoints_;
	float		radius_;
	const Color	*vdwColor_;
	std::string	label_;
	Vector		labelOffset_;
	const Color	*labelColor_;
	const Color	*surfaceColor_;
	float		surfaceOpacity_;
	otf::Symbol	surfaceCategory_;
	static TrackChanges::Changes *const
			changes;
	friend class MoleculeLensModel;
	mutable float	lastSize_;
	inline void		setMajorChange();
	inline void		setMinorSurfaceChange();
	inline void		setMajorSurfaceChange();
public:
	inline float		lastSize() const;	// last depicted size
	virtual void	wpyAssociate(PyObject* o) const;

	void		trackReason(const NotifierReason &reason) const;
	struct Reason: public NotifierReason {
                Reason(const char *r): NotifierReason(r) {}
        };
	static Reason		ALTLOC_CHANGED;
	static Reason		NAME_CHANGED;
	static Reason		ELEMENT_CHANGED;
	static Reason		IDATM_TYPE_CHANGED;
	static Reason		COLOR_CHANGED;
	static Reason		DRAW_MODE_CHANGED;
	static Reason		DISPLAY_CHANGED;
	static Reason		HIDE_CHANGED;
	static Reason		RADIUS_CHANGED;
	static Reason		VDW_CHANGED;
	static Reason		VDW_POINTS_CHANGED;
	static Reason		VDW_COLOR_CHANGED;
	static Reason		LABEL_CHANGED;
	static Reason		LABEL_OFFSET_CHANGED;
	static Reason		LABEL_COLOR_CHANGED;
	static Reason		SURFACE_COLOR_CHANGED;
	static Reason		SURFACE_OPACITY_CHANGED;
	static Reason		SURFACE_DISPLAY_CHANGED;
	static Reason		SURFACE_CATEGORY_CHANGED;
public:
	bool		bondedToMainchain(RibbonResidueClass *rrc);
private:
	Atom(Molecule *, otf::Symbol n, otf::Element e);
};

} // namespace chimera

#endif
