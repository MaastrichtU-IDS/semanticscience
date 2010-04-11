#ifndef chimera_Molecule_h
#define	chimera_Molecule_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <vector>
#include <algorithm>
#include <map>
#include <vector>
#include <otf/Symbol.h>
#include <list>
#include "Root.h"
#include <set>
#include <vector>
#include "Ring.h"
#include <list>
#include <map>
#include <list>
#include <otf/molkit/TAexcept.h>
#include "resDistConn.h"
#include <otf/Symbol.h>
#include <sstream>
#include <list>
#include <otf/Geom3d.h>
#include <utility>
#include <otf/WrapPy2.h>
#include "_chimera_config.h"
#include "Selectable.h"
#include "Model.h"
#include "Color.h"
#include "LineType.h"
#include "br.h"
#include "Atom.h"
#include "Bond.h"
#include "CoordSet.h"
#include "Residue.h"

namespace chimera {

class CHIMERA_IMEX Molecule: public Model  {
	std::vector<Atom *>	Atoms_;
	std::vector<Bond *>	Bonds_;
	std::map<int, CoordSet *>	CoordSets_;
	std::vector<Residue *>	Residues_;
public:
		virtual ~Molecule();
	Atom	*newAtom(otf::Symbol n, otf::Element e);
	void	deleteAtom(Atom *element);
	typedef std::vector<Atom *> Atoms;
	inline const Atoms	&atoms() const;
	Atom	*findAtom(int) const;
	Bond	*newBond(Atom *a0, Atom *a1);
	Bond	*newBond(Atom *a[2]);
	void	deleteBond(Bond *element);
	typedef std::vector<Bond *> Bonds;
	inline const Bonds	&bonds() const;
	Bond	*findBond(int) const;
	CoordSet	*newCoordSet(int key);
	CoordSet	*newCoordSet(int key, int size);
	void	deleteCoordSet(CoordSet *element);
	typedef std::map<int, CoordSet *> CoordSets;
	inline const CoordSets	&coordSets() const;
	CoordSet	*findCoordSet(int) const;
	Residue	*newResidue(otf::Symbol t, otf::MolResId rid,
			Residue *neighbor=NULL, bool after=true);
	Residue	*newResidue(otf::Symbol t, otf::Symbol chain, int pos, char insert,
			Residue *neighbor=NULL, bool after=true);
	void	deleteResidue(Residue *element);
	typedef std::vector<Residue *> Residues;
	inline const Residues	&residues() const;
	Residue	*findResidue(int) const;
public:
	typedef std::vector<Root *> Roots;
	inline const Roots 	&roots(bool ignoreBreakPoints);
	Root		*rootForAtom(const Atom *,
			  bool ignoreBreakPoints);
	void		useAsRoot(Atom *newRoot);
	
	typedef std::pair<Bonds::const_iterator, Bonds::const_iterator>
	  TraverseBonds;
	TraverseBonds	traverseBonds(Root *root);
	
	typedef std::pair<Atoms::const_iterator, Atoms::const_iterator>
	  TraverseAtoms;
	TraverseAtoms	traverseAtoms(Root *root);
private:
	friend class Atom; // these friend declarations needed due to hokey way
	friend class Bond; // their destructors mark the traversal list dirty
	
	mutable Roots		mg_BaseRoots, mg_SuperRoots;
	// "base" roots consider breakpoints, "super" roots ignore breakpoints

	Atoms				mg_travAtoms;
	Bonds				mg_travBonds;
	bool				mg_RecomputeRoots;
	
	void				mg_deleteRoots();
	inline void 				mg_validateRoots();
	void 				mg_traversalOrganize();
	Root::GraphSize 		mg_traverse(Atom *root, Bond *from,
						std::map<Atom *, bool> &atomVisited,
						std::map<Bond *, bool> &bondVisited,
						std::list<std::pair<Atom *, Bond *> > &breakAtoms,
						std::list<std::pair<Bond *, Atom *> > &breakBonds);
	
	// so Bonds can get Roots recomputed when graph breakpoints get set
	inline void				mg_setRootsInvalid();
public:
	typedef std::vector<Atom *> AtomGroup;
	typedef std::vector<AtomGroup> AtomGroups;
	void atomGroups(AtomGroups *atomGroups, int numAtoms) const;
private:
	void 		mg_findAtomGroups(std::vector<Atom *> *workingGroup,
				std::vector<std::vector<Atom *> > *groups,
				int groupSize, int remainingSize,
				std::map<Atom*, bool> &checkedAsEndNode,
				std::map<Atom*, bool> &inCurrentGroup) const;
public:
	// PseudoBonds for trajectories are handled on a per-CoordSet basis;
	// pseudoBondMgr() returns the PseudoBondMgr appropriate for the given
	// CoordSet (which, if it isn't in a trajectory, is the global singleton
	// PseudoBondMgr).  The CoordSet argument defaults to the current
	// coordinate set.
	PseudoBondMgr *pseudoBondMgr(CoordSet *cs = NULL) const;
public:
	// find rings: 'crossResidues' regulates whether or not to look for
	//	rings crossing residue boundaries; 'allSizeThreshold', if
	//	requests an exhaustive listing of rings no larger than the
	//	given size (larger minimal rings will still be returned)
	typedef std::set<Ring> Rings;
	const Rings &rings(bool crossResidues = false, unsigned int allSizeThreshold = 0);
private:
	bool		mg_LastCrossResidues;
	unsigned int	mg_LastAllSizeThreshold;
	Rings		mg_Rings;
public:
	bool		mg_RecomputeRings;
public:
private:
	void mg_cullAltLocs();
public:
	std::vector<Atom *>	primaryAtoms() const;
public:
	inline void		setIdatmValid(bool);
	inline bool		idatmValid() const;
private:
public:
	void	computeIdatmTypes();
	enum BondOrder { AMBIGUOUS, SINGLE, DOUBLE }; // need SINGLE==1, DOUBLE==2
private:
	bool	idatmValid_;
	void invertUncertains(std::vector<Atom *> &, std::map<Atom *, Bond *> &,
		std::map<Bond *, BondOrder> *);
	void uncertainAssign(std::vector<Atom *> &, std::map<Atom *, Bond *> &,
		std::set<Bond *> &, std::map<Bond *, BondOrder> &,
		std::vector<std::map<Bond *, int> > *,
		std::vector<std::vector<Atom *> > *, bool allowCharged=false);
	void flipAssign(std::vector<Bond *> &, std::set<Atom *> &,
		std::set<Bond *> &, std::map<Bond *, BondOrder> &,
		std::vector<std::map<Bond *, int> > *, bool allowCharged=false);
public:
	void		setActiveCoordSet(const CoordSet *a);
	inline CoordSet	*activeCoordSet() const;
private:
	CoordSet	*activeCS;
public:
	inline bool			structureAssigned() const;
	inline void			setStructureAssigned(bool b);
private:
	bool	structureAssigned_;
public:
	typedef std::string PDBHKeyType;
	typedef std::vector<std::string> PDBHValueType;
	typedef std::map<PDBHKeyType, PDBHValueType> PDBHeadersType;
	PDBHeadersType pdbHeaders;
	inline void	addPDBHeader(const PDBHKeyType &, const std::string &);
	inline void	setPDBHeader(const PDBHKeyType &, PDBHValueType);
	inline void	setAllPDBHeaders(PDBHeadersType);
	bool	asterisksTranslated;
public:
	Residue			*findResidue(const otf::MolResId&, const char *type = NULL) const;
	void			moveResAfter(const Residue *from, const Residue *to);
public:
	void	pruneShortBonds();
public:
	bool	lowerCaseChains;
public:
	std::vector<std::string> mol2comments, mol2data;
public:
public:
	bool	registerField(otf::Symbol field, int value);
	bool	registerField(otf::Symbol field, double value);
	bool	registerField(otf::Symbol field, const std::string &value);
	bool	getRegField(otf::Symbol field, int *value) const;
	bool	getRegField(otf::Symbol field, double *value) const;
	bool	getRegField(otf::Symbol field, std::string *value) const;
public:
	void		computeSecondaryStructure(
				std::ostringstream *info = NULL,
				float	energyCutoff = -0.5,
				int	minHelixLength = 3,
				int	minStrandLength = 3);
	void		computeSecondaryStructure(
				float	energyCutoff = -0.5,
				int	minHelixLength = 3,
				int	minStrandLength = 3);
private:
	void	ksdssp_addImideHydrogens() const;
	void	ksdssp_findHBonds() const;
	void	ksdssp_findTurns(int) const;
	void	ksdssp_markHelices(int) const;
	void	ksdssp_findHelices() const;
	void	ksdssp_findBridges() const;
	void	ksdssp_makeSummary(std::ostringstream *) const;
	void	ksdssp_computeChain(std::ostringstream *);

public:
	enum {
		KSDSSP_3DONOR		= 0x0001,
		KSDSSP_3ACCEPTOR	= 0x0002,
		KSDSSP_3GAP		= 0x0004,
		KSDSSP_3HELIX		= 0x0008,
		KSDSSP_4DONOR		= 0x0010,
		KSDSSP_4ACCEPTOR	= 0x0020,
		KSDSSP_4GAP		= 0x0040,
		KSDSSP_4HELIX		= 0x0080,
		KSDSSP_5DONOR		= 0x0100,
		KSDSSP_5ACCEPTOR	= 0x0200,
		KSDSSP_5GAP		= 0x0400,
		KSDSSP_5HELIX		= 0x0800,
		KSDSSP_PBRIDGE		= 0x1000,
		KSDSSP_ABRIDGE		= 0x2000,

		KSDSSP_PARA		= 1,
		KSDSSP_ANTI		= 2
	};

	struct Ksdssp_coords {
		const Coord	*c, *n, *ca, *o, *h;
	};

private:
	bool	ksdssp_hBondedTo(Ksdssp_coords *, Ksdssp_coords *) const;
	Coord *	ksdssp_addImideHydrogen(Ksdssp_coords *, Ksdssp_coords *) const;
public:
	inline bool		showStubBonds() const;
	void		setShowStubBonds(bool show);
	inline float		lineWidth() const;
	void		setLineWidth(float lw);
	inline float		stickScale() const;
	void		setStickScale(float ss);
	inline float		pointSize() const;
	void		setPointSize(float ps);
	inline float		ballScale() const;
	void		setBallScale(float bs);
	inline float		vdwDensity() const;
	void		setVdwDensity(float dens);
	inline LineType	lineType() const;
	void		setLineType(LineType linetype);
	inline void		wireStipple(/*OUT*/ int *factor, /*OUT*/ int *pattern) const;
	void		setWireStipple(int factor, int pattern);
	inline bool		autochain() const;
	void		setAutochain(bool yes);
	inline const Color	*surfaceColor() const;
	void		setSurfaceColor(/*NULL_OK*/ const Color *c);
	inline float		surfaceOpacity() const;
	void		setSurfaceOpacity(float opacity);
	void		incrHyds();
	void		decrHyds();
	inline int		numHyds() const;
	inline bool		aromaticDisplay() const;
	void		setAromaticDisplay(bool d);
	inline LineType	aromaticLineType() const;
	void		setAromaticLineType(LineType lt);
	inline Color		*aromaticColor() const;
	void		setAromaticColor(/*NULL_OK*/ Color *color);
	enum AromaticMode { Circle, Disk };
	inline AromaticMode	aromaticMode() const;
	void		setAromaticMode(AromaticMode mode);

	// virtual functions from Model
	virtual bool	computeBounds(/*OUT*/ Sphere *s, /*OUT*/ BBox *box) const;
	virtual bool	frontPoint(const Point &p1, const Point &p2, /*OUT*/ float *frac) const;
	// virtual functions from Selectable
	Selectable::Selectables oslChildren() const;
	Selectable::Selectables oslParents() const;

	void		surfaceCheck();
	inline void		addSurfaceNotification(const void *tag, const Notifier *n);
	inline void		removeSurfaceNotification(const void *tag);

	struct SurfaceReason: public NotifierReason {
		SurfaceReason(const char *r): NotifierReason(r) {}
	};
	// notifier reasons
	static SurfaceReason SURFACE_MINOR;	// don't recompute surface verts
	static SurfaceReason SURFACE_MAJOR;	// recompute surface vertices

	inline void		setMinorSurfaceChange();
	inline void		setMajorSurfaceChange();
	static Reason	ATOMS_MOVED;	// some atoms moved
	inline void		setAtomMoved(Atom *);
	typedef std::set<Atom *> AtomsMoved;
	inline const AtomsMoved &atomsMoved() const;
	inline const Rings	&minimumRings(bool crossResidues = false);
	inline const Rings	&allRings(bool, int);

	virtual PyObject* wpyNew() const;
private:
	Molecule(const Molecule&);		// disable
	Molecule& operator=(const Molecule&);	// disable
private:
	// virtual functions from Model
	virtual LensModel *
			newLensModel(Lens *);
	float		lineWidth_;
	float		stickScale_;
	float		pointSize_;
	float		ballScale_;
	float		vdwDensity_;
	LineType	lineType_;
	int		stipple[2];
	const Color	*surfaceColor_;
	float		surfaceOpacity_;
	AtomsMoved	atomsMoved_;
	bool		showStubBonds_;
	bool		autochain_;
	bool		minorSurfaceChange;
	bool		majorSurfaceChange;
	NotifierList	surfNL;
	static TrackChanges::Changes *const
			changes;
	virtual void	trackReason(const NotifierReason &reason) const;
	int		numHyds_;
	bool		aromaticDisplay_;
	LineType	aromaticLineType_;
	Color		*aromaticColor_;
	AromaticMode	aromaticMode_;
public:
	static const float
			DefaultBondRadius;	// = 0.2f
	static const double
			DefaultOffset;		// use default offset
	virtual void	updateCheck(const NotifierReason &reason);
	virtual void	wpyAssociate(PyObject* o) const;
	virtual void    setColor(const Color *c);

	static Reason	LINE_WIDTH_CHANGED;
	static Reason	STICK_SCALE_CHANGED;
	static Reason	POINT_SIZE_CHANGED;
	static Reason	BALL_SCALE_CHANGED;
	static Reason	VDW_DENSITY_CHANGED;
	static Reason	LINE_TYPE_CHANGED;
	static Reason	WIRE_STIPPLE_CHANGED;
	static Reason	SURFACE_COLOR_CHANGED;
	static Reason	SURFACE_OPACITY_CHANGED;
	static Reason	SHOW_STUB_BONDS_CHANGED;
	static Reason	AUTOCHAIN_CHANGED;
	static Reason	ACTIVE_COORD_SET_CHANGED;
	static Reason	AROMATIC_DISPLAY_CHANGED;
	static Reason	AROMATIC_LINE_TYPE_CHANGED;
	static Reason	AROMATIC_COLOR_CHANGED;
	static Reason	AROMATIC_MODE_CHANGED;
public:
	inline bool		ribbonHidesMainchain() const;
	inline void		setRibbonHidesMainchain(bool b);
	inline const Color	*ribbonInsideColor() const;
	inline void		setRibbonInsideColor(/*NULL_OK*/ const Color *);
	bool		updateRibbonData();
	inline void		ribbonAtomMoved(const Atom *a);
	Residue		*residueAfter(const Residue *r) const;
	Residue		*residueBefore(const Residue *r) const;
	const otf::Geom3d::Point
			&ribbonCoordinates(const Atom *a) const;
private:
	bool		ribbonHidesMainchain_;
	bool		ribbonDataValid_;
	const Color *	ribbonInsideColor_;
	typedef std::vector<RibbonData *> RibbonDataList;
	RibbonDataList	ribbonDataList_;
	inline void		clearRibbonData();

	typedef std::set<RibbonStyle *>	RibbonStyleSet;
	RibbonStyleSet	ribbonStyleSet_;
	class RibbonStyleNotifier : public Notifier {
	public:
                void update(const void *tag, void *style,
                                        const NotifierReason &reason) const;
	}		ribbonStyleNotifier;
	void 		updateRibbonStyle(RibbonStyle *s,
							const NotifierReason &);
	friend class RibbonStyleNotifier;

	typedef std::set<RibbonXSection *> RibbonXSectionSet;
	RibbonXSectionSet	ribbonXSectionSet_;
	class RibbonXSectionNotifier : public Notifier {
	public:
                void update(const void *tag, void *xsection,
                                        const NotifierReason &reason) const;
	}		ribbonXSectionNotifier;
	void 		updateRibbonXSection(RibbonXSection *xs,
							const NotifierReason &);
	friend class RibbonXSectionNotifier;

	static Reason	RIBBON_HIDES_MAINCHAIN_CHANGED;
	static Reason	RIBBON_INSIDE_COLOR_CHANGED;

	typedef std::map<const Atom *, otf::Geom3d::Point> ACMap;
	mutable ACMap	acMap;
public:
	void		updateRibbonAtoms();
	inline void		invalidateRibbonData();
	inline bool		hasValidRibbonData() const;
private:
public:
	Component	*getComponent(Atom *atom, bool create);
	const Link	*findLink(Bond *bond) const;
	void		removeComponent(Component *atom);
private:
	friend class Component;
	friend class Link;
	friend class BondRot;
	void		removeLink(Link *link);		// bookkeeping
	void		addBondLink(Bond *b, Link *l);	// bookkeeping
	void		removeBondLink(Bond *b);	// bookkeeping
	typedef std::map<Atom *, Component *> Components;
	Components	components;
	typedef std::map<Bond *, Link *> BondLinks;
	BondLinks	bondLinks;
	bool		dirtyComponentRoots;
	void		rerootComponents();
	bool		inDestructor_;
public:
	void		printComponent(Component *c, int indent);
	void		printComponents();
	inline bool		inDestructor();
public:
	Molecule();
};

} // namespace chimera

#endif
