#ifndef otf_TmplAtom_h
#define	otf_TmplAtom_h
#if defined(_MSC_VER) && (_MSC_VER >= 1020)
#pragma once
#endif

#include <map>
#include <vector>
#include <otf/Symbol.h>
#include <otf/molkit/Element.h>
#include "TmplCoordSet.h"
#include <otf/molkit/TAexcept.h>
#include <otf/config.h>
#include <functional>
namespace otf { class TmplBond; }
namespace otf { class TmplMolecule; }
namespace otf { class TmplResidue; }

namespace otf {
class TmplMolecule;
class TmplResidue;

class OTF_IMEX TmplAtom {
	friend class TmplMolecule;
	friend class TmplResidue;
	void	operator=(const TmplAtom &);	// disable
		TmplAtom(const TmplAtom &);	// disable
		~TmplAtom();
	std::map<TmplAtom*, TmplBond *>	Bonds_;
	TmplMolecule	*Molecule_;
	TmplResidue	*Residue_;
public:
	void	addBond(TmplBond *element);
	void	removeBond(TmplBond *element);
	typedef std::vector<TmplBond *> Bonds;
	inline Bonds bonds() const;
	typedef std::map<TmplAtom*, TmplBond *> BondsMap;
	inline const BondsMap	&bondsMap() const;
	typedef std::vector<TmplAtom*> BondKeys;
	inline BondKeys	neighbors() const;
	TmplBond	*findBond(TmplAtom*) const;
	TmplMolecule	*molecule() const;
	TmplResidue	*residue() const;
public:
private:
public:
	inline TmplBond		*connectsTo(TmplAtom *a) const;
public:
	inline otf::Symbol	name() const;
	inline void		setName(otf::Symbol s);
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
	static const unsigned int UNASSIGNED = ~0u;
	inline unsigned int	coordIndex() const;
	const TmplCoord	&coord() const;
	const TmplCoord	&coord(const TmplCoordSet *cs) const;
	void		setCoord(const TmplCoord &c);
	void		setCoord(const TmplCoord &c, TmplCoordSet *cs);
private:
	mutable unsigned int
		index_;
	int	newCoord(const TmplCoord &c) const;
private:
private:
	otf::Symbol     idatmType_;
public:
	otf::Symbol     idatmType() const { return idatmType_; }
	void		setIdatmType(const char *i) {
				idatmType_ = (otf::Symbol) i;
			}
private:
	TmplAtom(TmplMolecule *, otf::Symbol n, otf::Element e);
};

} // namespace otf

#endif
