#ifndef Mol_h
#define	Mol_h

#include "Atom.h"
#include "Bond.h"
#include "ChainTrace.h"
#include "Coord.h"
#include "CoordSet.h"
#include "Mol2io.h"
#include "Molecule.h"
#include "PDBio.h"
#include "PseudoBond.h"
#include "PseudoBondGroup.h"
#include "PseudoBondMgr.h"
#include "ReadGaussianFCF.h"
#include "Residue.h"
#include "RibbonData.h"
#include "RibbonResidue.h"
#include "RibbonStyle.h"
#include "RibbonStyleFixed.h"
#include "RibbonStyleTapered.h"
#include "RibbonStyleWorm.h"
#include "RibbonXSection.h"
#include "Ring.h"
#include "Root.h"

namespace chimera {

inline Atom::Bonds
Atom::bonds() const
{
	std::vector<Bond *> result;
	result.reserve(Bonds_.size());
	for (std::map<Atom*, Bond *>::const_iterator i = Bonds_.begin(); i != Bonds_.end(); ++i)
		result.push_back(i->second);
	return result;
}
inline const Atom::BondsMap &
Atom::bondsMap() const
{
	return Bonds_;
}
inline Atom::BondKeys
Atom::neighbors() const
{
	std::vector<Atom*> result;
	result.reserve(Bonds_.size());
	for (std::map<Atom*, Bond *>::const_iterator i = Bonds_.begin(); i != Bonds_.end(); ++i)
		result.push_back(i->first);
	return result;
}
inline const Atom::PseudoBonds &
Atom::pseudoBonds() const
{
	return PseudoBonds_;
}
inline Atom *Atom::rootAtom(bool ignoreBreakPoints) const {
	molecule()->mg_validateRoots();
	if (ignoreBreakPoints) {
		return molecule()->rootForAtom(this, false)->superRoot->atom();
	}
	return mg_Root;
}
inline Atom *Atom::traverseFrom(bool ignoreBreakPoints) const {
	molecule()->mg_validateRoots();
	if (!ignoreBreakPoints && mg_From != NULL
	  && connectsTo(mg_From)->getBreakPoint() == mg_From)
	  	return NULL;
	return mg_From;
}

// returns pointer to Bond that connects this atom to other.
// if unconnected, returns NULL
inline Bond *Atom::connectsTo(Atom *other) const
{
	BondsMap::const_iterator found = bondsMap().find(other);
	return found == bondsMap().end() ? NULL : (*found).second;
}
inline char
Atom::altLoc() const
{
	return alternateLocation;
}
inline void
Atom::setAltLoc(char al)
{
	if (al == ' ')
		al = 0;
	alternateLocation = al;
	trackReason(ALTLOC_CHANGED);
}
inline otf::Symbol
Atom::name() const
{
	return name_;
}
inline otf::Element
Atom::element() const
{
	return element_;
}
inline otf::Symbol
Atom::idatmType() const {
	if (!explicitIdatmType_.empty())
		return explicitIdatmType_;
	if (!Molecule_->idatmValid())
		Molecule_->computeIdatmTypes();
	return computedIdatmType_;
}
inline void
Atom::setIdatmType(otf::Symbol idatmType) {
	std::vector<Atom *> locs = allLocations();
	for (std::vector<Atom *>::iterator li = locs.begin(); li != locs.end();
	++li)
		(*li)->explicitIdatmType_ = idatmType;
	trackReason(IDATM_TYPE_CHANGED);
}
inline void
Atom::setIdatmType(const char *idatmType) {
	setIdatmType(otf::Symbol(idatmType));
}
inline void
Atom::setIdatmType(const std::string &idatmType) {
	setIdatmType(otf::Symbol(idatmType));
}
inline void
Atom::setComputedIdatmType(const char *ct) {
	std::vector<Atom *> locs = allLocations();
	for (std::vector<Atom *>::iterator li = locs.begin(); li != locs.end();
	++li)
		(*li)->computedIdatmType_ = otf::Symbol(ct);
}
inline bool
Atom::idatmIsExplicit() const {
	return !explicitIdatmType_.empty();
}
inline unsigned int
Atom::coordIndex() const
{
	return index_;
}
inline const Color *
Atom::color() const
{
	return color_;
}
inline Atom::DrawMode
Atom::drawMode() const
{
	return drawMode_;
}
inline bool
Atom::display() const
{
	return display_;
}
inline bool
Atom::shown() const
{
	return display_ && Molecule_->display();
}
inline bool
Atom::hide() const
{
	return hide_;
}
inline bool
Atom::vdw() const
{
	return vdw_;
}
inline const Color *
Atom::vdwColor() const
{
	return vdwColor_;
}
inline const std::string &
Atom::label() const
{
	return label_;
}
inline const Vector &
Atom::labelOffset() const
{
	return labelOffset_;
}
inline const Color *
Atom::labelColor() const
{
	return labelColor_;
}
inline const Color *
Atom::surfaceColor() const
{
	return surfaceColor_;
}
inline float
Atom::surfaceOpacity() const
{
	return surfaceOpacity_;
}
inline bool
Atom::surfaceDisplay() const
{
	return surfaceDisplay_;
}
inline otf::Symbol
Atom::surfaceCategory() const
{
	return surfaceCategory_;
}
inline void
Atom::setMajorChange()
{
	molecule()->setMajorChange();
}
inline void
Atom::setMinorSurfaceChange()
{
	molecule()->setMinorSurfaceChange();
}
inline void
Atom::setMajorSurfaceChange()
{
	molecule()->setMajorSurfaceChange();
}
inline Selector
Atom::oslLevel() const
{
	return selLevel;
}
inline float
Atom::lastSize() const
{
	return lastSize_;
}
inline const Bond::Atoms &
Bond::atoms() const
{
	return Atoms_;
}
inline Atom *Bond::otherAtom(const Atom *a) const {
	if (a == findAtom(0))
		return findAtom(1);
	else if (a == findAtom(1))
		return findAtom(0);
	else {
		throw std::invalid_argument(
		  "Atom argument to otherAtom() not member of bond.");
	}
}
inline bool Bond::contains(const Atom *a) const {
	return (a == findAtom(0) || a == findAtom(1));
}
inline Atom *Bond::getBreakPoint() const {
	return mg_BreakPoint;
}
inline Bond *Bond::traverseFrom(bool ignoreBreakPoints) const {
	findAtom(0)->molecule()->mg_validateRoots();
	if (!ignoreBreakPoints && mg_From != NULL
	  && mg_BreakPoint != NULL && mg_From->contains(mg_BreakPoint))
	  	return NULL;
	return mg_From;
}
inline void Bond::clearBreakPoint() {
	if (mg_BreakPoint != NULL) {
		mg_BreakPoint->molecule()->mg_setRootsInvalid();
		mg_BreakPoint = NULL;
	}
}
inline otf::Geom3d::Real
Bond::length() const
{
	return otf::distance(findAtom(1)->coord(), findAtom(0)->coord());
}
inline otf::Geom3d::Real
Bond::sqlength() const
{
	return otf::sqdistance(findAtom(1)->coord(), findAtom(0)->coord());
}
inline const Color *
Bond::color() const
{
	return color_;
}
inline Bond::DrawMode
Bond::drawMode() const
{
	return drawMode_;
}
inline Bond::DisplayMode
Bond::display() const
{
	return display_;
}
inline bool
Bond::halfbond() const
{
	return halfbond_;
}
inline float
Bond::radius() const
{
	return radius_;
}
inline const std::string &
Bond::label() const
{
	return label_;
}
inline const Vector &
Bond::labelOffset() const
{
	return labelOffset_;
}
inline const Color *
Bond::labelColor() const
{
	return labelColor_;
}
inline Molecule *
Bond::molecule() const
{
	return atoms()[0]->molecule();
}
inline void
Bond::setMajorChange()
{
	molecule()->setMajorChange();
}
inline Selector
Bond::oslLevel() const
{
	return selLevel;
}
inline bool
ChainTrace::trackMolecule() const
{
	return trackMolecule_;
}
inline const CoordSet::Coords &
CoordSet::coords() const
{
	return Coords_;
}
inline int
CoordSet::id() const
{
	return csid;
}
inline bool
Mol2io::ok()
{
	return ioErr.empty();
}
inline std::string
Mol2io::error()
{
	return ioErr;
}
inline Atom *
Mol2io::atomWithId(int id) const
{
	std::map<int, Atom *, std::less<int> >::const_iterator i = asn.find(id);
	if (i == asn.end())
		return NULL;
	return (*i).second;
}
inline void
Mol2io::clearAtomIdMap()
{
	asn.clear();
}
inline void
Mol2io::addAtomToSubst(int substId, const std::string &name, Atom *a)
{
	sam[substId].push_back(a);
	snm[substId] = name;
}
inline std::vector<Atom *>
Mol2io::extractAtomsInSubst(int substId)
{
	SAMap::iterator i = sam.find(substId);
	if (i == sam.end())
		throw std::invalid_argument("no such substructure");
	std::vector<Atom *> atoms = (*i).second;
	sam.erase(i);
	return atoms;
}
inline std::vector<int>
Mol2io::substIds()
{
	std::vector<int> ids;
	for (SAMap::iterator i = sam.begin(); i != sam.end(); ++i)
		ids.push_back((*i).first);
	return ids;
}
inline std::string &
Mol2io::substIdToName(int i)
{
	return snm[i];
}
inline void
Mol2io::clearSAMap()
{
	sam.clear();
	snm.clear();
}
inline const Molecule::Atoms &
Molecule::atoms() const
{
	return Atoms_;
}
inline const Molecule::Bonds &
Molecule::bonds() const
{
	return Bonds_;
}
inline const Molecule::CoordSets &
Molecule::coordSets() const
{
	return CoordSets_;
}
inline const Molecule::Residues &
Molecule::residues() const
{
	return Residues_;
}
inline const Molecule::Roots &Molecule::roots(bool ignoreBreakPoints) {
	mg_validateRoots();
	return ignoreBreakPoints ? mg_SuperRoots : mg_BaseRoots;
}
inline void Molecule::mg_validateRoots() {
	if (mg_RecomputeRoots)
		mg_traversalOrganize();
}
inline void Molecule::mg_setRootsInvalid() {
	mg_RecomputeRoots = true;
}
inline void
Molecule::setIdatmValid(bool v) {
	idatmValid_ = v;
}
inline bool
Molecule::idatmValid() const {
	return idatmValid_;
}
inline CoordSet *
Molecule::activeCoordSet() const
{
	return activeCS;
}
inline bool
Molecule::structureAssigned() const
{
	return structureAssigned_;
}
inline void
Molecule::setStructureAssigned(bool b)
{
	structureAssigned_ = b;
}
inline void
Molecule::setPDBHeader(const Molecule::PDBHKeyType &key,
						Molecule::PDBHValueType value)
{
	pdbHeaders[key].swap(value);
}
inline void
Molecule::addPDBHeader(const Molecule::PDBHKeyType &key,
						const std::string &header)
{
	pdbHeaders[key].push_back(header);
}
inline void
Molecule::setAllPDBHeaders(Molecule::PDBHeadersType newHeaders)
{
	pdbHeaders.swap(newHeaders);
}
inline void
Molecule::computeSecondaryStructure(float energyCutoff, int minHelixLength,
						int minStrandLength)
{
	Molecule::computeSecondaryStructure(NULL, energyCutoff,
					minHelixLength, minStrandLength);
}
inline const Molecule::AtomsMoved &
Molecule::atomsMoved() const
{
	return atomsMoved_;
}
inline void
Molecule::addSurfaceNotification(const void *tag, const Notifier *n)
{
	surfNL.addNotification(tag, n);
}
inline void
Molecule::removeSurfaceNotification(const void *tag)
{
	surfNL.removeNotification(tag);
}
inline bool
Molecule::showStubBonds() const
{
	return showStubBonds_;
}
inline float
Molecule::lineWidth() const
{
	return lineWidth_;
}
inline float
Molecule::stickScale() const
{
	return stickScale_;
}
inline float
Molecule::pointSize() const
{
	return pointSize_;
}
inline float
Molecule::ballScale() const
{
	return ballScale_;
}
inline float
Molecule::vdwDensity() const
{
	return vdwDensity_;
}
inline LineType
Molecule::lineType() const
{
	return lineType_;
}
inline void
Molecule::wireStipple(int *factor, int *pattern) const
{
	*factor = stipple[0];
	*pattern = stipple[1];
}
inline bool
Molecule::autochain() const
{
	return autochain_;
}
inline bool
Molecule::aromaticDisplay() const
{
	return aromaticDisplay_;
}
inline LineType
Molecule::aromaticLineType() const
{
	return aromaticLineType_;
}
inline Color *
Molecule::aromaticColor() const
{
	return aromaticColor_;
}
inline Molecule::AromaticMode
Molecule::aromaticMode() const
{
	return aromaticMode_;
}
inline const Color *
Molecule::surfaceColor() const
{
	return surfaceColor_;
}
inline float
Molecule::surfaceOpacity() const
{
	return surfaceOpacity_;
}
inline void
Molecule::setMinorSurfaceChange()
{
	minorSurfaceChange = true;
}
inline void
Molecule::setMajorSurfaceChange()
{
	majorSurfaceChange = true;
}
inline void
Molecule::setAtomMoved(Atom *a)
{
	atomsMoved_.insert(a);
}
inline const Molecule::Rings &
Molecule::minimumRings(bool crossResidues)
{
	return rings(crossResidues, 0);
}
inline const Molecule::Rings &
Molecule::allRings(bool crossResidues, int size)
{
	return rings(crossResidues, size);
}
inline int
Molecule::numHyds() const
{
	return numHyds_;
}
inline bool
Molecule::hasValidRibbonData() const
{
	return ribbonDataValid_;
}
inline void
Molecule::invalidateRibbonData()
{
	ribbonDataValid_ = false;
}
inline void
Molecule::clearRibbonData()
{
	for (Residues::iterator i = Residues_.begin();
						i != Residues_.end(); ++i)
		(*i)->setRibbonData(NULL);
	for (RibbonDataList::iterator i = ribbonDataList_.begin();
						i != ribbonDataList_.end(); ++i)
		delete *i;
	ribbonDataList_.clear();
	for (RibbonStyleSet::iterator i = ribbonStyleSet_.begin();
					i != ribbonStyleSet_.end(); ++i) {
		RibbonStyle *rs = *i;
		rs->removeNotification(this);
	}
	ribbonStyleSet_.clear();
	for (RibbonXSectionSet::iterator i = ribbonXSectionSet_.begin();
					i != ribbonXSectionSet_.end(); ++i) {
		RibbonXSection *xs = *i;
		xs->removeNotification(this);
	}
	ribbonXSectionSet_.clear();
	acMap.clear();
}
inline void
Molecule::ribbonAtomMoved(const Atom *a)
{
	// Check if we need to invalidate ribbon data because
	// a guide atom moved
	if (!hasValidRibbonData())
		return;
	Residue *r = a->residue();
	RibbonData *rd = r->ribbonData();
	if (rd == NULL)
		return;
	if (rd->guide() == a) {
		setMajorChange();
		invalidateRibbonData();
	}
}
inline bool
Molecule::ribbonHidesMainchain() const
{
	return ribbonHidesMainchain_;
}
inline void
Molecule::setRibbonHidesMainchain(bool b)
{
	if (ribbonHidesMainchain_ == b)
		return;
	ribbonHidesMainchain_ = b;
	setMajorChange();
	invalidateRibbonData();
	trackReason(RIBBON_HIDES_MAINCHAIN_CHANGED);
}
inline const Color *
Molecule::ribbonInsideColor() const
{
	return ribbonInsideColor_;
}
inline void
Molecule::setRibbonInsideColor(const Color *c)
{
	if (ribbonInsideColor_ == c)
		return;
	ribbonInsideColor_ = c;
	setMajorChange();
	trackReason(RIBBON_INSIDE_COLOR_CHANGED);
}
inline bool Molecule::inDestructor() { return inDestructor_; }
inline otf::Geom3d::Real
PDBio::bondLengthTolerance()
{
	return tolerance;
}
inline void
PDBio::setBondLengthTolerance(otf::Geom3d::Real t)
{
	tolerance = t;
}
inline bool
PDBio::ok()
{
	return ioErr.empty();
}
inline std::string
PDBio::error()
{
	return ioErr;
}
inline bool
PDBio::explodeNMR()
{
	return explode;
}
inline void
PDBio::setExplodeNMR(bool b)
{
	explode = b;
}
inline const std::vector<std::string> &PDBio::getRecordOrder()
{
	return recordOrder;
}
inline const PseudoBond::Atoms &
PseudoBond::atoms() const
{
	return Atoms_;
}
inline Atom *PseudoBond::otherAtom(const Atom *a) const {
	if (a == findAtom(0))
		return findAtom(1);
	else if (a == findAtom(1))
		return findAtom(0);
	else {
		throw std::invalid_argument(
		  "Atom argument to otherAtom() not member of bond.");
	}
}
inline bool PseudoBond::contains(const Atom *a) const {
	return (a == findAtom(0) || a == findAtom(1));
}
inline otf::Symbol PseudoBond::category(void) const {
        return pseudoBondGroup()->category();
}
inline otf::Geom3d::Real
PseudoBond::length() const
{
	return findAtom(1)->xformCoord().distance(findAtom(0)->xformCoord());
}
inline otf::Geom3d::Real
PseudoBond::sqlength() const
{
	return atoms()[1]->xformCoord().sqdistance(atoms()[0]->xformCoord());
}
inline const Color *
PseudoBond::color() const
{
	return color_;
}
inline PseudoBond::DrawMode
PseudoBond::drawMode() const
{
	return drawMode_;
}
inline PseudoBond::DisplayMode
PseudoBond::display() const
{
	return display_;
}
inline bool
PseudoBond::halfbond() const
{
	return halfbond_;
}
inline float
PseudoBond::radius() const
{
	return radius_;
}
inline const std::string &
PseudoBond::label() const
{
	return label_;
}
inline const Vector &
PseudoBond::labelOffset() const
{
	return labelOffset_;
}
inline const Color *
PseudoBond::labelColor() const
{
	return labelColor_;
}
inline void
PseudoBond::setMajorChange()
{
	pseudoBondGroup()->setMajorChange();
}
inline Selector
PseudoBond::oslLevel() const
{
	return selLevel;
}
inline const PseudoBondGroup::PseudoBonds &
PseudoBondGroup::pseudoBonds() const
{
	return PseudoBonds_;
}
inline otf::Symbol PseudoBondGroup:: category() const {
	return _category;
}
inline bool
PseudoBondGroup::showStubBonds() const
{
	return showStubBonds_;
}
inline float
PseudoBondGroup::lineWidth() const
{
	return lineWidth_;
}
inline float
PseudoBondGroup::stickScale() const
{
	return stickScale_;
}
inline LineType
PseudoBondGroup::lineType() const
{
	return lineType_;
}
inline void
PseudoBondGroup::wireStipple(int *factor, int *pattern) const
{
	*factor = stipple[0];
	*pattern = stipple[1];
}
inline PseudoBondMgr::PseudoBondGroups
PseudoBondMgr::pseudoBondGroups() const
{
	std::vector<PseudoBondGroup *> result;
	result.reserve(PseudoBondGroups_.size());
	for (std::map<otf::Symbol, PseudoBondGroup *>::const_iterator i = PseudoBondGroups_.begin(); i != PseudoBondGroups_.end(); ++i)
		result.push_back(i->second);
	return result;
}
inline const PseudoBondMgr::PseudoBondGroupsMap &
PseudoBondMgr::pseudoBondGroupsMap() const
{
	return PseudoBondGroups_;
}
inline PseudoBondMgr::PseudoBondGroupKeys
PseudoBondMgr::categories() const
{
	std::vector<otf::Symbol> result;
	result.reserve(PseudoBondGroups_.size());
	for (std::map<otf::Symbol, PseudoBondGroup *>::const_iterator i = PseudoBondGroups_.begin(); i != PseudoBondGroups_.end(); ++i)
		result.push_back(i->first);
	return result;
}
inline bool
ReadGaussianFCF::ok() const
{
	return error_.empty();
}
inline std::string
ReadGaussianFCF::error() const
{
	return error_;
}
inline Residue::Atoms
Residue::atoms() const
{
	std::vector<Atom *> result;
	result.reserve(Atoms_.size());
	for (std::multimap<otf::Symbol, Atom *>::const_iterator i = Atoms_.begin(); i != Atoms_.end(); ++i)
		result.push_back(i->second);
	return result;
}
inline const Residue::AtomsMap &
Residue::atomsMap() const
{
	return Atoms_;
}
inline Residue::AtomKeys
Residue::atomNames() const
{
	std::set<otf::Symbol> result;
	//result.reserve(Atoms_.size());
	for (std::multimap<otf::Symbol, Atom *>::const_iterator i = Atoms_.begin(); i != Atoms_.end(); ++i)
		result.insert(i->first);
	return result;
}
inline otf::Symbol
Residue::type() const
{
	return type_;
}
inline void
Residue::setType(otf::Symbol t)
{
	type_ = t;
	trackReason(TYPE_CHANGED);
}
inline const otf::MolResId &
Residue::id() const
{
	return rid;
}
inline bool
Residue::operator==(const Residue &r) const
{
	// only equal if they are the same residue
	return this == &r;
}
inline bool
Residue::operator<(const Residue &r) const
{
	return rid < r.rid;
}
inline bool
Residue::isHelix() const
{
	return isHelix_;
}
inline bool
Residue::isSheet() const
{
	return isSheet_;
}
inline bool
Residue::isStrand() const
{
	return isSheet();
}
inline bool
Residue::isTurn() const
{
	return isTurn_;
}
inline int
Residue::ssId() const
{
	return ssId_;
}
inline void
Residue::setSsId(int id)
{
	ssId_ = id;
}
inline bool
Residue::isHet() const
{
	return isHet_;
}
inline void
Residue::setIsHet(bool ih)
{
	isHet_ = ih;
	trackReason(HET_CHANGED);
}
inline const std::string &
Residue::label() const
{
	return label_;
}
inline const Vector &
Residue::labelOffset() const
{
	return labelOffset_;
}
inline const Color *
Residue::labelColor() const
{
	return labelColor_;
}
inline bool
Residue::fillDisplay() const
{
	return fillDisplay_;
}
inline Residue::FillMode
Residue::fillMode() const
{
	return fillMode_;
}
inline const Color *
Residue::fillColor() const
{
	return fillColor_;
}
inline int
Residue::numAtoms() const
{
	return Atoms_.size();
}
inline void
Residue::setMajorChange()
{
	molecule()->setMajorChange();
}
inline Selector
Residue::oslLevel() const
{
	return selLevel;
}
inline const Color *
Residue::ribbonColor() const
{
	return ribbonColor_;
}
inline Residue::RibbonDrawMode
Residue::ribbonDrawMode() const
{
	return ribbonDrawMode_;
}
inline bool
Residue::ribbonDisplay() const
{
	return ribbonDisplay_;
}
inline RibbonXSection *
Residue::ribbonXSection() const
{
	return ribbonXSection_;
}
inline RibbonStyle *
Residue::ribbonStyle() const
{
	return ribbonStyle_;
}
inline RibbonData *
Residue::ribbonData() const
{
	return ribbonData_;
}
inline const otf::Geom3d::Point &
RibbonData::center() const
{
	return center_;
}
inline void
RibbonData::setCenter(const otf::Geom3d::Point &c)
{
	center_ = c;
}
inline const otf::Geom3d::Vector &
RibbonData::normal() const
{
	return normal_;
}
inline void
RibbonData::setNormal(const otf::Geom3d::Vector &n)
{
	normal_ = n;
}
inline const otf::Geom3d::Vector &
RibbonData::binormal() const
{
	return binormal_;
}
inline void
RibbonData::setBinormal(const otf::Geom3d::Vector &bn)
{
	binormal_ = bn;
}
inline void
RibbonData::flipNormals()
{
	normal_ = normal_ * -1;
	binormal_ = binormal_ * -1;
	flipped_ = !flipped_;
}
inline bool
RibbonData::flipped() const
{
	return flipped_;
}
inline RibbonData *
RibbonData::next() const
{
	return next_;
}
inline void
RibbonData::setNext(RibbonData *n)
{
	next_ = n;
}
inline RibbonData *
RibbonData::prev() const
{
	return prev_;
}
inline void
RibbonData::setPrev(RibbonData *p)
{
	prev_ = p;
}
inline Residue *
RibbonData::prevResidue() const
{
	return prevResidue_;
}
inline void
RibbonData::setPrevResidue(Residue *r)
{
	prevResidue_ = r;
}
inline Residue *
RibbonData::nextResidue() const
{
	return nextResidue_;
}
inline void
RibbonData::setNextResidue(Residue *r)
{
	nextResidue_ = r;
}
inline Atom *
RibbonData::guide() const
{
	return guide_;
}
inline void
RibbonData::setGuide(Atom *a)
{
	guide_ = a;
}
inline float
RibbonStyleWorm::thickness(float t) const
{
	return width(t);
}
inline const std::vector<std::pair<float, float> > &
RibbonXSection::outline() const
{
	return outline_;
}
inline void
RibbonXSection::setOutline(const std::vector<std::pair<float, float> > &o)
{
	outline_ = o;
	notify(RibbonXSection::OUTLINE_CHANGED);
}
inline void
RibbonXSection::addOutlineVertex(float x, float y)
{
	outline_.push_back(std::pair<float, float>(x, y));
}
inline bool
RibbonXSection::smoothWidth() const
{
	return smoothWidth_;
}
inline void
RibbonXSection::setSmoothWidth(bool sw)
{
	if (smoothWidth_ == sw)
		return;
	smoothWidth_ = sw;
	notify(RibbonXSection::SMOOTH_WIDTH_CHANGED);
}
inline bool
RibbonXSection::smoothLength() const
{
	return smoothLength_;
}
inline void
RibbonXSection::setSmoothLength(bool sl)
{
	if (smoothLength_ == sl)
		return;
	smoothLength_ = sl;
	notify(RibbonXSection::SMOOTH_LENGTH_CHANGED);
}
inline bool
RibbonXSection::closed() const
{
	return closed_;
}
inline void
RibbonXSection::setClosed(bool c)
{
	if (closed_ == c)
		return;
	closed_ = c;
	notify(RibbonXSection::CLOSED_CHANGED);
}
inline const Ring::Bonds &
Ring::bonds() const
{
	return Bonds_;
}

} // namespace chimera

#endif
