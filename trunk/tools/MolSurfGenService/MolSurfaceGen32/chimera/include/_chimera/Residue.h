#ifndef chimera_Residue_h
#define	chimera_Residue_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <map>
#include <set>
#include <vector>
#include <otf/Symbol.h>
#include <otf/molkit/MolResId.h>
#include <otf/molkit/TAexcept.h>
#include "Residue_template.h"
#include <vector>
#include "PDBio.h"
#include <otf/molkit/MolResId.h>
#include "resDistConn.h"
#include <otf/WrapPy2.h>
#include "_chimera_config.h"
#include "Selectable.h"
#include "Color.h"
#include "TrackChanges.h"
#include "Spline.h"
#include "RibbonXSection.h"
#include "RibbonStyle.h"
#include "RibbonData.h"
#include "RibbonSpline.h"
#include <functional>
namespace chimera { class Atom; }
namespace chimera { class Molecule; }

namespace chimera {
class Molecule;

class CHIMERA_IMEX Residue: public Selectable  {
	friend class Molecule;
	void	operator=(const Residue &);	// disable
		Residue(const Residue &);	// disable
		virtual ~Residue();
	std::multimap<otf::Symbol, Atom *>	Atoms_;
	Molecule	*Molecule_;
public:
	void	addAtom(Atom *element);
	void	removeAtom(Atom *element);
	typedef std::vector<Atom *> Atoms;
	inline Atoms atoms() const;
	typedef std::multimap<otf::Symbol, Atom *> AtomsMap;
	inline const AtomsMap	&atomsMap() const;
	typedef std::set<otf::Symbol> AtomKeys;
	inline AtomKeys	atomNames() const;
	Atom	*findAtom(otf::Symbol) const;
	typedef std::pair<AtomsMap::const_iterator, AtomsMap::const_iterator>	RangeAtoms;
	RangeAtoms	findRangeAtoms(otf::Symbol) const;
	Molecule	*molecule() const;
public:
	inline otf::Symbol		type() const;
	inline void			setType(otf::Symbol t);
	inline const otf::MolResId	&id() const;
	inline bool			operator==(const Residue &r) const;
	inline bool			operator<(const Residue &r) const;
private:
	otf::Symbol	type_;
	otf::MolResId	rid;
public:
	// return atoms that received assignments from the template
	std::vector<Atom *>	templateAssign(
				  void (*assignFunc)(Atom *, const char *),
				  const char *app,
				  const char *templateDir,
				  const char *extension
				) const;
	std::vector<Atom *>	templateAssign(
				  void (Atom::*assignFunc)(const char *),
				  const char *app,
				  const char *templateDir,
				  const char *extension
				) const;
	std::vector<Atom *>	templateAssign(assigner, 
				  const char *app,
				  const char *templateDir,
				  const char *extension
				) const;
public:
	inline bool			isHelix() const;
	void			setIsHelix(bool b);
	inline bool			isSheet() const;
	void			setIsSheet(bool b);
	inline bool			isStrand() const;
	void			setIsStrand(bool b);
	inline bool			isTurn() const;
	void			setIsTurn(bool b);
	inline int			ssId() const;
	inline void			setSsId(int id);
private:
	bool	isHelix_;
	bool	isSheet_;
	bool	isTurn_;
	int	ssId_;
public:
	Atom	*findAtom(otf::Symbol name, char altLoc) const;
	inline bool	isHet() const;
	inline void	setIsHet(bool);
private:
	bool	isHet_;

	// need to be able to change MolResIds
	friend class PDBio;
public:
public:
	bool	registerField(otf::Symbol field, int value);
	bool	registerField(otf::Symbol field, double value);
	bool	registerField(otf::Symbol field, const std::string &value);
	bool	getRegField(otf::Symbol field, int *value) const;
	bool	getRegField(otf::Symbol field, double *value) const;
	bool	getRegField(otf::Symbol field, std::string *value) const;
public:
	std::string	oslIdent(Selector start = SelDefault, Selector end = SelDefault) const;
	Selectable::Selectables oslChildren() const;
	Selectable::Selectables oslParents() const;
	bool		oslTestAbbr(OSLAbbreviation *a) const;
	inline Selector	oslLevel() const;
	static const Selector	selLevel = SelResidue;
	inline int		numAtoms() const;
	PyObject	*kdHydrophobicity() const;

	virtual PyObject* wpyNew() const;

	inline const std::string &
			label() const;
	void		setLabel(const std::string &);
	inline const Vector	&labelOffset() const;
	void		setLabelOffset(const Vector &offset);
	inline const Color	*labelColor() const;
	void		setLabelColor(/*NULL_OK*/ const Color *color);
	Point		labelCoord() const;
	Vector		currentLabelOffset() const;
	inline bool		fillDisplay() const;
	void		setFillDisplay(bool d);
	enum FillMode { Thin, Thick };
	inline FillMode	fillMode() const;
	void		setFillMode(FillMode mode);
	inline const Color	*fillColor() const;
	void		setFillColor(/*NULL_OK*/ const Color *color);
private:
	static TrackChanges::Changes *const
			changes;
	inline void		setMajorChange();
	typedef std::map<std::string, double> hpInfoMap;
	static hpInfoMap kdHpMap;
	std::string	label_;
	Vector		labelOffset_;
	const Color	*labelColor_;
	bool		fillDisplay_;
	FillMode	fillMode_;
	const Color	*fillColor_;
public:
	virtual void	wpyAssociate(PyObject* o) const;

	void		trackReason(const NotifierReason &reason) const;
	struct Reason: public NotifierReason {
                Reason(const char *r): NotifierReason(r) {}
        };
	static Reason	RESIDUE_CHANGED;
	static Reason	TYPE_CHANGED;
	static Reason	HELIX_CHANGED;
	static Reason	SHEET_CHANGED;
	static Reason	STRAND_CHANGED;
	static Reason	TURN_CHANGED;
	static Reason	HET_CHANGED;
	static Reason	LABEL_CHANGED;
	static Reason	LABEL_OFFSET_CHANGED;
	static Reason	LABEL_COLOR_CHANGED;
	static Reason	FILL_DISPLAY_CHANGED;
	static Reason	FILL_MODE_CHANGED;
	static Reason	FILL_COLOR_CHANGED;
public:
	enum RibbonDrawMode { Ribbon_2D, Ribbon_Edged, Ribbon_Round, Ribbon_Custom };
	inline bool		ribbonDisplay() const;
	void		setRibbonDisplay(bool display);
	inline const Color	*ribbonColor() const;
	void		setRibbonColor(/*NULL_OK*/ const Color *);
	inline RibbonDrawMode	ribbonDrawMode() const;
	void		setRibbonDrawMode(RibbonDrawMode);
	inline RibbonXSection	*ribbonXSection() const;
	void		setRibbonXSection(/*NULL_OK*/ RibbonXSection *xs);
	inline RibbonStyle	*ribbonStyle() const;
	void		setRibbonStyle(/*NULL_OK*/ RibbonStyle *s);
	inline RibbonData	*ribbonData() const;
	void		setRibbonData(/*NULL_OK*/ RibbonData *d);
	RibbonResidueClass	*ribbonResidueClass() const;
	void		setRibbonResidueClass(/*NULL_OK*/ RibbonResidueClass *c);
	bool		hasRibbon() const;

	enum RS { RS_TURN, RS_HELIX, RS_SHEET, RS_ARROW, RS_NUCLEIC };
	RibbonXSection	*ribbonFindXSection(RibbonDrawMode mode) const;
	RS		ribbonFindStyleType() const;
	RibbonStyle	*ribbonFindStyle() const;
	GeometryVector	ribbonCenters() const;
	GeometryVector	ribbonNormals() const;
	GeometryVector	ribbonBinormals() const;
	bool		bondedTo(const Residue *r, bool checkNever=false) const;

	static RibbonStyle	*getDefaultRibbonStyle(int ss);
private:
	const Color	*ribbonColor_;
	RibbonDrawMode	ribbonDrawMode_;
	bool		ribbonDisplay_;
	RibbonXSection	*ribbonXSection_;
	RibbonStyle	*ribbonStyle_;
	RibbonData	*ribbonData_;
	mutable RibbonResidueClass
			*ribbonResidueClass_;
	void		assignRibbonResidueClass() const;
public:
	static Reason	RIBBON_DISPLAY_CHANGED;
	static Reason	RIBBON_COLOR_CHANGED;
	static Reason	RIBBON_DRAWMODE_CHANGED;
	static Reason	RIBBON_XSECTION_CHANGED;
	static Reason	RIBBON_STYLE_CHANGED;
	static Reason	RIBBON_DATA_CHANGED;
	static Reason	RIBBON_RESIDUE_CLASS_CHANGED;
private:
	Residue(Molecule *, otf::Symbol t, otf::MolResId rid);
	Residue(Molecule *, otf::Symbol t, otf::Symbol chain, int pos, char insert);
};

} // namespace chimera

#endif
